"""등록된 모든 학교의 NEIS 데이터(급식·학사)를 청크·임베딩·적재.

실행: (backend 디렉터리에서)
    python -m scripts.refresh_data

⚠️ Voyage 무료 등급은 3 RPM / 10K TPM 제한 → 학교 사이 SLEEP_SEC 대기로 스로틀.
   결제수단 등록 시(여전히 무료 토큰 적용) 제한 풀려 빨라짐. 그땐 SLEEP_SEC=0 가능.
"""
from __future__ import annotations

import asyncio
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from app.data.ingester import ingest_school_neis
from app.db.supabase_client import get_supabase_admin

SLEEP_SEC = 60  # Voyage 무료 등급(10K TPM) 회피: 학교당 ~7K토큰이라 1분 1학교로 스로틀
DAYS = 60


def _already_ingested(sb, school_code: str) -> bool:
    r = (
        sb.table("school_documents")
        .select("id", count="exact")
        .eq("school_code", school_code)
        .in_("source_type", ["neis_meal", "neis_schedule"])
        .limit(0)
        .execute()
    )
    return (r.count or 0) > 0


async def main():
    sb = get_supabase_admin()
    schools = (
        sb.table("schools")
        .select("school_code, edu_office_code, school_name")
        .execute()
        .data
    )
    # 이미 적재된 학교는 건너뜀(재실행 시 실패분만 이어서 채움). FORCE=1이면 전체 재적재.
    import os

    force = os.environ.get("FORCE") == "1"
    todo = [s for s in schools if force or not _already_ingested(sb, s["school_code"])]
    print(f"대상 {len(schools)}개 중 적재 필요 {len(todo)}개 (days={DAYS}, sleep={SLEEP_SEC}s, force={force})")

    total = 0
    failed: list[str] = []
    for i, s in enumerate(todo):
        print(f"\n[{i+1}/{len(todo)}] 📚 {s['school_name']}")
        try:
            n = await ingest_school_neis(s["school_code"], s["edu_office_code"], days=DAYS)
            total += n
        except Exception as e:
            print(f"  ❌ 실패: {type(e).__name__}: {str(e)[:120]}")
            failed.append(s["school_name"])
        if i < len(todo) - 1:
            await asyncio.sleep(SLEEP_SEC)
    print(f"\n🎉 이번 실행 {total}개 청크 적재 완료")
    if failed:
        print(f"⚠️ 실패 {len(failed)}개: {', '.join(failed)} (재실행하면 이어서 채워짐)")


if __name__ == "__main__":
    asyncio.run(main())
