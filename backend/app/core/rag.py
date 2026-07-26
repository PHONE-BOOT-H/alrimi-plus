"""RAG 파이프라인: 쿼리 임베딩 → pgvector 검색 → Claude 답변 생성(스트리밍)."""
from __future__ import annotations

import asyncio
from datetime import date
from typing import AsyncIterator

from app.core.date_intent import is_meal_query, parse_date_range, today_kst
from app.core.embedding import embed_query
from app.core.llm import get_client, route_model
from app.core.prompts import SYSTEM_PROMPT, build_context
from app.db.supabase_client import execute_with_retry, get_supabase_admin

MATCH_COUNT = 6
MAX_TOKENS = 1536
_DOC_COLS = "id, school_code, source_type, title, content, metadata, source_url"

_WD_KO = "월화수목금토일"


def _weekday_ko(iso: str) -> str:
    """'YYYY-MM-DD' → '월'/'화'... (모델이 요일을 추측하다 틀리는 것 방지용, 파이썬이 정확 계산)."""
    try:
        y, m, d = (int(x) for x in iso.split("-"))
        return _WD_KO[date(y, m, d).weekday()]
    except Exception:
        return ""


def _fetch_meals_by_date(sb, school_code: str, start: date, end: date) -> list[dict]:
    """특정 날짜(범위)의 급식 청크를 직접 조회 (벡터검색이 못 집는 정확한 날짜용)."""
    res = execute_with_retry(
        lambda: sb.table("school_documents")
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


def _fetch_nearest_meal(sb, school_code: str, start: date, end: date) -> list[dict]:
    """요청 날짜(범위)에 급식이 없을 때 안내용으로 '가장 가까운 급식일' 1건 조회.

    우선 요청일 이후의 첫 급식, 없으면 요청일 이전의 마지막 급식.
    """
    after = execute_with_retry(
        lambda: sb.table("school_documents")
        .select(_DOC_COLS)
        .eq("school_code", school_code)
        .eq("source_type", "neis_meal")
        .gt("valid_from", end.isoformat())
        .order("valid_from")
        .limit(1)
        .execute()
    )
    if after.data:
        return [{**d, "similarity": 1.0} for d in after.data]
    before = execute_with_retry(
        lambda: sb.table("school_documents")
        .select(_DOC_COLS)
        .eq("school_code", school_code)
        .eq("source_type", "neis_meal")
        .lt("valid_from", start.isoformat())
        .order("valid_from", desc=True)
        .limit(1)
        .execute()
    )
    return [{**d, "similarity": 1.0} for d in (before.data or [])]


def _vector_search(sb, school_code: str, emb: list[float], match_count: int) -> list[dict]:
    """pgvector 의미검색(match_documents RPC). 간헐적 연결 종료에 대비해 재시도로 감쌈."""
    return (
        execute_with_retry(
            lambda: sb.rpc(
                "match_documents",
                {"query_embedding": emb, "p_school_code": school_code, "match_count": match_count},
            ).execute()
        ).data
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

        # 날짜를 특정한 급식 질문: 요청 범위 밖의 급식 청크는 출처에서 제외.
        # (벡터검색이 의미만 비슷한 다른 달 급식을 끌어와 출처 패널을 오염시키는 것 방지)
        s_iso, e_iso = rng[0].isoformat(), rng[1].isoformat()
        vector_docs = [
            d
            for d in vector_docs
            if d.get("source_type") != "neis_meal"
            or s_iso <= ((d.get("metadata") or {}).get("date") or "") <= e_iso
        ]
        if not date_docs:
            # 요청 날짜에 급식이 없으면(주말·공휴일 등) '가장 가까운 급식일' 1건만 안내용으로 첨부
            date_docs = await asyncio.to_thread(_fetch_nearest_meal, sb, school_code, rng[0], rng[1])

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
    today_wd = _weekday_ko(today)

    # 자료에 나온 급식/학사 날짜의 정확한 요일표(모델이 요일을 추측하다 틀리는 것 방지).
    doc_dates = sorted({
        (d.get("metadata") or {}).get("date")
        for d in docs
        if d.get("source_type") in ("neis_meal", "neis_schedule")
        and (d.get("metadata") or {}).get("date")
    })
    wday_ref = ""
    if doc_dates:
        _lines = "\n".join(f"- {dt}: {_weekday_ko(dt)}요일" for dt in doc_dates)
        wday_ref = (
            f"\n\n[날짜→요일 정확표 — 아래 <참고자료>에 나온 날짜의 실제 요일이야. "
            f"요일은 반드시 이 표대로만 표기하고 직접 계산·추측하지 마]\n{_lines}"
        )

    # 요청한 날짜에 급식이 실제로 없을 때: 벡터검색이 끌어온 '무관한 다른 날짜'들을
    # 학교의 전체 급식 일정인 양 나열하지 않도록 명시 안내(주말/공휴일/방학 오해 방지).
    date_gap_rule = ""
    if is_meal_query(question):
        rng = parse_date_range(question, today_kst())
        if rng:
            s_iso, e_iso = rng[0].isoformat(), rng[1].isoformat()
            has_meal_in_range = any(
                d.get("source_type") == "neis_meal"
                and s_iso <= ((d.get("metadata") or {}).get("date") or "") <= e_iso
                for d in docs
            )
            if not has_meal_in_range:
                if rng[0] == rng[1]:
                    when = f"{s_iso}({_weekday_ko(s_iso)}요일)"
                    extra = "그 날은 주말이라 급식이 없어. " if rng[0].weekday() >= 5 else ""
                else:
                    when = f"{s_iso}~{e_iso}"
                    extra = ""
                # 첨부된 '가장 가까운 급식일'(범위 밖 급식 청크)이 있으면 안내 허용
                near_dates = sorted(
                    (d.get("metadata") or {}).get("date") or ""
                    for d in docs
                    if d.get("source_type") == "neis_meal"
                )
                near_hint = (
                    f"가장 가까운 급식일은 {near_dates[0]}({_weekday_ko(near_dates[0])}요일)이야 — "
                    f"'가장 가까운 급식일은 ○일이에요'라고 함께 안내해줘. "
                    if near_dates
                    else ""
                )
                date_gap_rule = (
                    f"\n\n[중요 — 반드시 지켜]\n"
                    f"사용자가 요청한 날짜({when})의 급식은 <참고자료>에 없어. {extra}"
                    f"'{when} 급식 정보는 자료에 없어요'라고 솔직히 안내해. {near_hint}"
                    f"그 외 다른 날짜의 메뉴를 요청한 날의 것처럼 답하거나 "
                    f"'학교에 이 날짜들만 있어요'처럼 나열하지 마."
                )
            elif rng[0] != rng[1]:
                # 기간(이번 주/다음 주 등) 질문 + 자료에 급식 있음 → 그 기간의 모든 날을 빠짐없이.
                date_gap_rule = (
                    f"\n\n[안내] 사용자가 기간({s_iso}~{e_iso})의 급식을 물었어. "
                    f"그 기간 안에서 <참고자료>에 있는 급식은 하나도 빠뜨리지 말고 날짜순으로 모두 보여줘. "
                    f"가장 최근 하루만 보여주지 말고, 급식이 없는 날(주말·공휴일 등)은 없다고만 짧게 언급해."
                )

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
        f"오늘 날짜는 {today}({today_wd}요일)야. '오늘/내일/이번 주' 같은 표현은 이 날짜를 기준으로 해석해."
        f"{wday_ref}\n\n"
        f"{context}\n\n"
        f"위 <참고자료>만 근거로 다음 질문에 답해줘. {lang_rule} "
        f"사용한 자료 번호를 [1],[2]처럼 표기하고, 자료에 없으면 모른다고 해줘."
        f"{date_gap_rule}"
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
