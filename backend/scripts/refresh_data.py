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

SLEEP_SEC = 35  # Voyage 무료 등급 TPM 회피용 학교 간 대기
DAYS = 60


async def main():
    sb = get_supabase_admin()
    schools = (
        sb.table("schools")
        .select("school_code, edu_office_code, school_name")
        .execute()
        .data
    )
    print(f"대상 학교 {len(schools)}개 (days={DAYS}, sleep={SLEEP_SEC}s)")
    total = 0
    failed: list[str] = []
    for i, s in enumerate(schools):
        print(f"\n[{i+1}/{len(schools)}] 📚 {s['school_name']}")
        try:
            n = await ingest_school_neis(s["school_code"], s["edu_office_code"], days=DAYS)
            total += n
        except Exception as e:
            print(f"  ❌ 실패: {type(e).__name__}: {str(e)[:120]}")
            failed.append(s["school_name"])
        if i < len(schools) - 1:
            await asyncio.sleep(SLEEP_SEC)
    print(f"\n🎉 총 {total}개 청크 적재 완료")
    if failed:
        print(f"⚠️ 실패한 학교 {len(failed)}개: {', '.join(failed)} (재실행하면 이어서 채워짐)")


if __name__ == "__main__":
    asyncio.run(main())
