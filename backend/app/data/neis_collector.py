"""NEIS Open API 클라이언트.

엔드포인트 문서: https://open.neis.go.kr/portal/data/service/selectServicePage.do
응답 구조: {<service>: [{"head": [...]}, {"row": [...]}]}
  - 성공: head[1]["RESULT"]["CODE"] == "INFO-000"
  - 데이터 없음: 최상위에 "RESULT"만 옴 (CODE == "INFO-200")
"""
from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from app.core.config import settings

NEIS_BASE = "https://open.neis.go.kr/hub"


class NEISClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.neis_api_key
        self.client = httpx.AsyncClient(timeout=20.0)

    async def _get(self, path: str, params: dict[str, Any]) -> list[dict]:
        params = {"KEY": self.api_key, "Type": "json", "pIndex": 1, "pSize": 1000, **params}
        r = await self.client.get(f"{NEIS_BASE}/{path}", params=params)
        r.raise_for_status()
        data = r.json()
        # 데이터 없음(INFO-200) 등은 {"RESULT": {...}} 형태 → 빈 리스트
        if path not in data:
            return []
        rows = data[path]
        if len(rows) < 2:
            return []
        return rows[1].get("row", [])

    async def search_school(self, name: str) -> list[dict]:
        return await self._get("schoolInfo", {"SCHUL_NM": name})

    async def get_meals(
        self,
        edu_office_code: str,
        school_code: str,
        from_date: date,
        to_date: date,
    ) -> list[dict]:
        return await self._get(
            "mealServiceDietInfo",
            {
                "ATPT_OFCDC_SC_CODE": edu_office_code,
                "SD_SCHUL_CODE": school_code,
                "MLSV_FROM_YMD": from_date.strftime("%Y%m%d"),
                "MLSV_TO_YMD": to_date.strftime("%Y%m%d"),
            },
        )

    async def get_schedule(
        self,
        edu_office_code: str,
        school_code: str,
        from_date: date,
        to_date: date,
    ) -> list[dict]:
        return await self._get(
            "SchoolSchedule",
            {
                "ATPT_OFCDC_SC_CODE": edu_office_code,
                "SD_SCHUL_CODE": school_code,
                "AA_FROM_YMD": from_date.strftime("%Y%m%d"),
                "AA_TO_YMD": to_date.strftime("%Y%m%d"),
            },
        )

    async def get_timetable_elementary(
        self,
        edu_office_code: str,
        school_code: str,
        from_date: date,
        to_date: date,
    ) -> list[dict]:
        return await self._get(
            "elsTimetable",
            {
                "ATPT_OFCDC_SC_CODE": edu_office_code,
                "SD_SCHUL_CODE": school_code,
                "TI_FROM_YMD": from_date.strftime("%Y%m%d"),
                "TI_TO_YMD": to_date.strftime("%Y%m%d"),
            },
        )

    async def close(self):
        await self.client.aclose()


# 알레르기 코드 매핑 (NEIS 표준 19종)
ALLERGY_CODES: dict[str, str] = {
    "1": "난류",
    "2": "우유",
    "3": "메밀",
    "4": "땅콩",
    "5": "대두",
    "6": "밀",
    "7": "고등어",
    "8": "게",
    "9": "새우",
    "10": "돼지고기",
    "11": "복숭아",
    "12": "토마토",
    "13": "아황산류",
    "14": "호두",
    "15": "닭고기",
    "16": "쇠고기",
    "17": "오징어",
    "18": "조개류",
    "19": "잣",
}


def parse_allergy_string(meal_dish: str) -> list[str]:
    """급식 메뉴 문자열에서 알레르기 코드 추출.

    예: "오징어덮밥 (1.5.9)" → ["1", "5", "9"]
    """
    import re

    codes: set[str] = set()
    for match in re.findall(r"\(([\d.\s]+)\)", meal_dish):
        for num in match.split("."):
            num = num.strip()
            if num and num in ALLERGY_CODES:
                codes.add(num)
    return sorted(codes, key=int)
