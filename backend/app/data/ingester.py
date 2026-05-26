"""NEIS 데이터를 청크로 만들어 임베딩 후 school_documents에 적재."""
from __future__ import annotations

from datetime import date, timedelta

from app.core.embedding import embed_documents
from app.data.neis_collector import ALLERGY_CODES, NEISClient, parse_allergy_string
from app.db.supabase_client import get_supabase_admin


def _format_meal_chunk(meal: dict) -> tuple[str, str, dict]:
    """급식 1건 → (title, content, metadata)."""
    ymd = meal.get("MLSV_YMD", "")
    formatted_date = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}" if len(ymd) == 8 else ymd
    school_name = meal.get("SCHUL_NM", "")
    meal_type = meal.get("MMEAL_SC_NM", "")  # 조식/중식/석식
    dishes_raw = meal.get("DDISH_NM", "").replace("<br/>", " / ")
    cal = meal.get("CAL_INFO", "")
    ntr_info = meal.get("NTR_INFO", "")

    allergies = parse_allergy_string(dishes_raw)
    allergy_names = [ALLERGY_CODES[c] for c in allergies if c in ALLERGY_CODES]

    title = f"{formatted_date} {school_name} {meal_type}"
    content = (
        f"{title}\n"
        f"메뉴: {dishes_raw}\n"
        f"열량: {cal}\n"
        f"영양정보: {ntr_info}\n"
        f"알레르기 유발 식품: {', '.join(allergy_names) if allergy_names else '없음'}"
    )
    metadata = {
        "date": formatted_date,
        "meal_type": meal_type,
        "allergy_codes": allergies,
        "allergy_names": allergy_names,
    }
    return title, content, metadata


def _format_schedule_chunk(item: dict) -> tuple[str, str, dict]:
    ymd = item.get("AA_YMD", "")
    formatted = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}" if len(ymd) == 8 else ymd
    title = f"{formatted} {item.get('SCHUL_NM','')} 학사일정"
    content = (
        f"{title}\n"
        f"행사명: {item.get('EVENT_NM','')}\n"
        f"내용: {item.get('EVENT_CNTNT','')}\n"
        f"수업공휴일: {item.get('SBTR_DD_SC_NM','')}"
    )
    return title, content, {"date": formatted}


async def ingest_school_neis(school_code: str, edu_office_code: str, days: int = 60) -> int:
    """한 학교의 NEIS 데이터(급식·학사)를 청크·임베딩·적재. days: 오늘 기준 ±N일."""
    sb = get_supabase_admin()
    client = NEISClient()
    today = date.today()
    start = today - timedelta(days=days // 2)
    end = today + timedelta(days=days // 2)

    chunks: list[dict] = []
    try:
        meals = await client.get_meals(edu_office_code, school_code, start, end)
        for meal in meals:
            title, content, meta = _format_meal_chunk(meal)
            chunks.append(
                {
                    "school_code": school_code,
                    "source_type": "neis_meal",
                    "source_url": "NEIS Open API - mealServiceDietInfo",
                    "title": title,
                    "content": content,
                    "metadata": meta,
                    "valid_from": meta["date"],
                    "valid_to": meta["date"],
                }
            )

        schedules = await client.get_schedule(edu_office_code, school_code, start, end)
        for item in schedules:
            title, content, meta = _format_schedule_chunk(item)
            chunks.append(
                {
                    "school_code": school_code,
                    "source_type": "neis_schedule",
                    "source_url": "NEIS Open API - SchoolSchedule",
                    "title": title,
                    "content": content,
                    "metadata": meta,
                    "valid_from": meta["date"],
                    "valid_to": meta["date"],
                }
            )
    finally:
        await client.close()

    if not chunks:
        print(f"  ⚠️ {school_code}: 청크 0개 — 데이터 없음")
        return 0

    # 임베딩 (pgvector는 '[...]' 문자열 입력을 받음 → str로 변환해 삽입)
    embeddings = await embed_documents([c["content"] for c in chunks])
    for c, emb in zip(chunks, embeddings):
        c["embedding"] = str(emb)

    # 기존 동일 출처 청크 삭제 후 재삽입(= upsert 효과)
    sb.table("school_documents").delete().eq("school_code", school_code).in_(
        "source_type", ["neis_meal", "neis_schedule"]
    ).execute()
    BATCH = 100
    for i in range(0, len(chunks), BATCH):
        sb.table("school_documents").insert(chunks[i : i + BATCH]).execute()

    print(f"  ✅ {school_code}: {len(chunks)}개 청크 적재")
    return len(chunks)
