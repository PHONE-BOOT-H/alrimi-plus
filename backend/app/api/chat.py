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

# 경량 abuse 방어: IP당 슬라이딩 윈도우 호출 제한 (무인증 공개 엔드포인트 보호).
# HF 재시작 시 초기화되는 소프트 가드. 데모엔 영향 없게 넉넉히.
_RATE_WINDOW_SEC = 600  # 10분
_RATE_MAX = 30  # IP당 10분 30회
_rate_hits: dict[str, list[float]] = defaultdict(list)


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _rate_ok(ip: str) -> bool:
    now = time.time()
    hits = [t for t in _rate_hits[ip] if now - t < _RATE_WINDOW_SEC]
    if len(hits) >= _RATE_MAX:
        _rate_hits[ip] = hits
        return False
    hits.append(now)
    _rate_hits[ip] = hits
    return True


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
