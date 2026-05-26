"""/api/chat — RAG 챗봇 엔드포인트.

NDJSON 스트리밍 프로토콜(한 줄 = 한 JSON):
  {"type":"sources","sources":[...]}   ← 검색된 출처 (가장 먼저 1회)
  {"type":"delta","text":"..."}         ← 답변 토큰 (여러 번)
  {"type":"done","model":"..."}         ← 종료 + 사용 모델
  {"type":"error","message":"..."}      ← 오류
"""
from __future__ import annotations

import json
import time
from collections import defaultdict
from typing import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.llm import route_model
from app.core.rag import format_sources, retrieve, stream_answer

router = APIRouter(prefix="/api", tags=["chat"])

# abuse 방어 (무인증 공개 엔드포인트). HF 재시작 시 초기화되는 소프트 가드.
#  - per-IP: best-effort (XFF는 스푸핑 가능하므로 신뢰하지 않음, 보조 신호로만)
#  - GLOBAL: 전체 합산 상한 = IP 스푸핑으로 못 뚫는 진짜 backstop
#  - 진짜 최종 backstop은 Anthropic 콘솔의 월 사용량 캡(코드 밖)
_RATE_WINDOW_SEC = 600  # 10분
_RATE_MAX_PER_IP = 30  # IP당 10분 30회
_RATE_MAX_GLOBAL = 200  # 전체 10분 200회 (스푸핑 무관 상한)
_rate_hits: dict[str, list[float]] = defaultdict(list)
_global_hits: list[float] = []

# 명백한 프롬프트 인젝션 마커 (정상 학교 질문엔 절대 안 나오는 표현만 → 오거부 위험 없음)
_INJECTION_MARKERS = (
    "이전 지시",
    "이전의 지시",
    "위 지시",
    "시스템 프롬프트",
    "system prompt",
    "ignore previous",
    "ignore all previous",
    "너는 이제부터",
    "you are now",
    "disregard",
)


def _client_ip(request: Request) -> str:
    # XFF는 신뢰하지 않음(스푸핑 가능). 보조 식별자로만 사용.
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()[:64]
    return request.client.host if request.client else "unknown"


def _prune(ts: list[float], now: float) -> list[float]:
    return [t for t in ts if now - t < _RATE_WINDOW_SEC]


def _rate_ok(ip: str) -> bool:
    global _global_hits, _rate_hits
    now = time.time()
    # 1) 전역 상한 — IP 스푸핑으로 우회 불가
    _global_hits = _prune(_global_hits, now)
    if len(_global_hits) >= _RATE_MAX_GLOBAL:
        return False
    # 2) per-IP 상한 (보조)
    hits = _prune(_rate_hits.get(ip, []), now)
    if len(hits) >= _RATE_MAX_PER_IP:
        _rate_hits[ip] = hits
        return False
    hits.append(now)
    _global_hits.append(now)
    _rate_hits[ip] = hits
    # 3) 오래된 빈 버킷 청소 (메모리 누수 방지)
    if len(_rate_hits) > 2000:
        _rate_hits = {k: _prune(v, now) for k, v in _rate_hits.items()}
        _rate_hits = defaultdict(list, {k: v for k, v in _rate_hits.items() if v})
    return True


def _is_injection(q: str) -> bool:
    ql = q.lower()
    return any(m in ql for m in _INJECTION_MARKERS)


class ChatRequest(BaseModel):
    school_code: str = Field(..., description="NEIS 학교 코드")
    question: str = Field(..., min_length=1, max_length=500)
    language: str = Field(default="ko")


def _ndjson(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False) + "\n"


@router.post("/chat")
async def chat(req: ChatRequest, request: Request):
    if not _rate_ok(_client_ip(request)):
        async def limited() -> AsyncIterator[str]:
            yield _ndjson(
                {"type": "error", "message": "잠시 후 다시 시도해 주세요. (짧은 시간에 너무 많이 요청했어요 🙏)"}
            )

        return StreamingResponse(limited(), media_type="application/x-ndjson")

    # 명백한 인젝션은 임베딩·LLM 호출 전에 즉시 차단 (비용 절감 + 방어)
    if _is_injection(req.question):
        async def guarded() -> AsyncIterator[str]:
            yield _ndjson({"type": "sources", "sources": []})
            yield _ndjson(
                {
                    "type": "delta",
                    "text": "저는 학교 정보(급식·학사일정·공지 등)에 대해서만 답해드릴 수 있어요. 😊",
                }
            )
            yield _ndjson({"type": "done", "model": "guard"})

        return StreamingResponse(guarded(), media_type="application/x-ndjson")

    async def generate() -> AsyncIterator[str]:
        try:
            docs = await retrieve(req.school_code, req.question)
            yield _ndjson({"type": "sources", "sources": format_sources(docs)})

            model = route_model(req.question)
            async for delta in stream_answer(req.question, docs, req.language, model):
                yield _ndjson({"type": "delta", "text": delta})

            yield _ndjson({"type": "done", "model": model})
        except Exception as e:  # noqa: BLE001 — 스트림 중 오류를 클라이언트에 전달
            name = type(e).__name__
            text = str(e)
            if "RateLimit" in name or "rate limit" in text.lower() or "429" in text:
                msg = "지금 요청이 몰려서 잠시 후(약 1분 뒤) 다시 시도해 주세요. 🙏"
            elif "credit balance" in text.lower():
                msg = "일시적으로 답변 생성이 어려워요. 잠시 후 다시 시도해 주세요."
            else:
                msg = f"답변 중 오류가 발생했어요. 잠시 후 다시 시도해 주세요. ({name})"
            yield _ndjson({"type": "error", "message": msg})

    return StreamingResponse(generate(), media_type="application/x-ndjson")
