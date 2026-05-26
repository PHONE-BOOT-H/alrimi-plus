"""시범 학교를 NEIS에서 검색해 schools 테이블에 적재.

실행: (backend 디렉터리에서)
    python -m scripts.seed_schools

다양성 기준: 초등 4 / 중등 3 / 고등 3, 지역·유형 분산.
"""
from __future__ import annotations

import asyncio
import sys

# Windows 콘솔(cp949)에서도 한글/이모지 출력이 깨지거나 죽지 않도록
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from app.data.neis_collector import NEISClient
from app.db.supabase_client import get_supabase_admin

SEED_SCHOOLS = [
    "서울대학교사범대학부설초등학교",
    "남춘천초등학교",
    "제주북초등학교",
    "분당초등학교",
    "역삼중학교",
    "강릉중학교",
    "곡성중학교",
    "휘문고등학교",
    "한국애니메이션고등학교",
    "포항제철고등학교",
]


async def main():
    sb = get_supabase_admin()
    client = NEISClient()
    inserted = 0
    try:
        for name in SEED_SCHOOLS:
            rows = await client.search_school(name)
            if not rows:
                print(f"❌ {name}: not found")
                continue
            row = rows[0]
            record = {
                "school_code": row["SD_SCHUL_CODE"],
                "edu_office_code": row["ATPT_OFCDC_SC_CODE"],
                "school_name": row["SCHUL_NM"],
                "school_type": row.get("SCHUL_KND_SC_NM"),
                "region": row.get("LCTN_SC_NM"),
                "address": row.get("ORG_RDNMA"),
            }
            sb.table("schools").upsert(record).execute()
            print(f"✅ {row['SCHUL_NM']} → {row['SD_SCHUL_CODE']} ({row.get('LCTN_SC_NM','')})")
            inserted += 1
    finally:
        await client.close()
    print(f"\n총 {inserted}/{len(SEED_SCHOOLS)} 학교 적재 완료")


if __name__ == "__main__":
    asyncio.run(main())
