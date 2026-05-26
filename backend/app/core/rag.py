"""RAG 파이프라인: 쿼리 임베딩 → pgvector 검색 → Claude 답변 생성(스트리밍)."""
from __future__ import annotations

from datetime import date
from typing import AsyncIterator

from app.core.embedding import embed_query
from app.core.llm import get_client, route_model
from app.core.prompts import SYSTEM_PROMPT, build_context
from app.db.supabase_client import get_supabase_admin

MATCH_COUNT = 6
MAX_TOKENS = 1024


async def retrieve(school_code: str, question: str, match_count: int = MATCH_COUNT) -> list[dict]:
    """질문을 임베딩해 해당 학교의 유사 문서 Top-K를 가져온다."""
    emb = await embed_query(question)
    sb = get_supabase_admin()
    res = sb.rpc(
        "match_documents",
        {"query_embedding": emb, "p_school_code": school_code, "match_count": match_count},
    ).execute()
    return res.data or []


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
) -> AsyncIterator[str]:
    """검색된 문서를 컨텍스트로 Claude 답변을 토큰 단위로 스트리밍."""
    model = model or route_model(question)
    context = build_context(docs)
    lang_note = "한국어" if language == "ko" else ("English" if language == "en" else language)
    today = date.today().isoformat()

    user_content = (
        f"오늘 날짜는 {today}야. '오늘/내일/이번 주' 같은 표현은 이 날짜를 기준으로 해석해.\n\n"
        f"{context}\n\n"
        f"위 <참고자료>만 근거로, 다음 질문에 {lang_note}로 답해줘. "
        f"사용한 자료 번호를 [1],[2]처럼 표기하고, 자료에 없으면 모른다고 해줘.\n\n"
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
