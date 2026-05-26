"""RAG 파이프라인: 쿼리 임베딩 → pgvector 검색 → Claude 답변 생성(스트리밍)."""
from __future__ import annotations

import asyncio
from datetime import date
from typing import AsyncIterator

from app.core.date_intent import is_meal_query, parse_date_range, today_kst
from app.core.embedding import embed_query
from app.core.llm import get_client, route_model
from app.core.prompts import SYSTEM_PROMPT, build_context
from app.db.supabase_client import get_supabase_admin

MATCH_COUNT = 6
MAX_TOKENS = 1536
_DOC_COLS = "id, school_code, source_type, title, content, metadata, source_url"


def _fetch_meals_by_date(sb, school_code: str, start: date, end: date) -> list[dict]:
    """특정 날짜(범위)의 급식 청크를 직접 조회 (벡터검색이 못 집는 정확한 날짜용)."""
    res = (
        sb.table("school_documents")
        .select(_DOC_COLS)
        .eq("school_code", school_code)
        .eq("source_type", "neis_meal")
        .gte("valid_from", start.isoformat())
        .lte("valid_from", end.isoformat())
        .order("valid_from")
        .limit(12)
        .execute()
    )
    return [{**d, "similarity": 1.0} for d in (res.data or [])]


def _vector_search(sb, school_code: str, emb: list[float], match_count: int) -> list[dict]:
    return (
        sb.rpc(
            "match_documents",
            {"query_embedding": emb, "p_school_code": school_code, "match_count": match_count},
        )
        .execute()
        .data
        or []
    )


async def retrieve(school_code: str, question: str, match_count: int = MATCH_COUNT) -> list[dict]:
    """하이브리드 검색: (급식+날짜 질문이면) 해당 날짜 급식 직접조회 + 벡터검색 Top-K, 중복 제거.

    동기 supabase 호출은 to_thread로 감싸 이벤트 루프 블로킹을 피한다(동시 요청 처리).
    """
    emb = await embed_query(question)
    sb = get_supabase_admin()
    vector_docs = await asyncio.to_thread(_vector_search, sb, school_code, emb, match_count)

    date_docs: list[dict] = []
    rng = parse_date_range(question, today_kst())
    if rng and is_meal_query(question):
        date_docs = await asyncio.to_thread(_fetch_meals_by_date, sb, school_code, rng[0], rng[1])

    # 날짜 직접조회 결과를 앞에, 벡터검색을 뒤에. id 기준 중복 제거.
    seen: set[int] = set()
    merged: list[dict] = []
    for d in [*date_docs, *vector_docs]:
        if d["id"] in seen:
            continue
        seen.add(d["id"])
        merged.append(d)
    # 날짜 청크는 모두 유지하고, 전체는 너무 길지 않게 제한
    cap = max(match_count, len(date_docs))
    return merged[:cap]


def format_sources(docs: list[dict]) -> list[dict]:
    """프론트 표시용 출처 메타데이터(번호 포함)."""
    return [
        {
            "n": i,
            "title": d.get("title"),
            "source_type": d.get("source_type"),
            "source_url": d.get("source_url"),
            "similarity": round(float(d.get("similarity", 0)), 3),
        }
        for i, d in enumerate(docs, start=1)
    ]


async def stream_answer(
    question: str,
    docs: list[dict],
    language: str = "ko",
    model: str | None = None,
    allergies: list[str] | None = None,
) -> AsyncIterator[str]:
    """검색된 문서를 컨텍스트로 Claude 답변을 토큰 단위로 스트리밍.

    allergies: 사용자가 등록한 알레르기명 목록(예: ["우유","밀"]). 급식 답변에서 개인화 경고.
    """
    model = model or route_model(question)
    context = build_context(docs)
    today = today_kst().isoformat()
    # 기본은 '질문과 같은 언어'로 답(다국어). language를 명시(en/ko)하면 그 언어로 강제.
    if language == "en":
        lang_rule = "Answer in English."
    elif language == "ko":
        lang_rule = "질문과 같은 언어로 답해줘(한국어 질문이면 한국어, 영어 질문이면 영어)."
    else:
        lang_rule = f"Answer in {language}."

    # 개인화 알레르기: LLM에 맡기지 않고 코드로 정확히 교차 계산(안전 기능 — false negative 금지)
    allergy_rule = ""
    if allergies:
        per_date: list[str] = []
        for d in docs:
            if d.get("source_type") != "neis_meal":
                continue
            meta = d.get("metadata") or {}
            names = set(meta.get("allergy_names") or [])
            hit = [a for a in allergies if a in names]
            label = meta.get("date") or (d.get("title") or "")
            per_date.append(
                f"- {label}: ⚠️ 주의 항목 = {', '.join(hit)}" if hit else f"- {label}: ✅ 등록 알레르기 없음"
            )
        calc = "\n".join(per_date) if per_date else "(급식 메뉴 자료 없음)"
        allergy_rule = (
            f"\n\n[개인화 알레르기 분석 — 코드가 계산한 사실이므로 그대로 반영]\n"
            f"등록 알레르기: {', '.join(allergies)}\n{calc}\n"
            f"급식 답변이면 위 계산 결과를 그대로 써서, 날짜별로 메뉴 앞에 "
            f"'⚠️ 내 아이 주의 항목: …' 또는 '✅ 등록 알레르기 없음'을 굵게 표기해. "
            f"위 계산과 다르게 말하지 마. (급식이 아닌 질문이면 무시)"
        )

    user_content = (
        f"오늘 날짜는 {today}야. '오늘/내일/이번 주' 같은 표현은 이 날짜를 기준으로 해석해.\n\n"
        f"{context}\n\n"
        f"위 <참고자료>만 근거로 다음 질문에 답해줘. {lang_rule} "
        f"사용한 자료 번호를 [1],[2]처럼 표기하고, 자료에 없으면 모른다고 해줘."
        f"{allergy_rule}\n\n"
        f"질문: {question}"
    )

    client = get_client()
    async with client.messages.stream(
        model=model,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
