"""학교알리미 OpenAPI 클라이언트.

API 안내: https://www.schoolinfo.go.kr/ng/go/pnnggo_a01_l0.do

⚠️ 2026-05-26 라이브 검증 결과 / 보류 상태:
  - base/파라미터 구조는 확인됨: GET openApi.do?apiKey&apiType&pbanYr&schulKndCode&schulCode
  - 필수 파라미터 순서대로 요구됨: pbanYr(공시년도) → schulKndCode(학교종류 02초/03중/04고) → ...
  - 그러나 apiType 코드를 못 맞춤. 추측한 코드 전부
    "선택하신 항목은 해당 연도에 공시되지 않은 항목으로 제공이 불가합니다." 반환.
  - 정확한 apiType 코드 목록 = 학교알리미 OpenAPI '활용가이드'(등록 시 제공)에 있음.
  - 또한 학교알리미 schulCode 체계는 NEIS SD_SCHUL_CODE와 다름(별도 매핑 필요).
  - → 가이드 확보 후 apiType + schulCode 매핑 채우면 동작. 보조 데이터라 우선순위 낮음.
"""
from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings

SCHOOLINFO_BASE = "https://www.schoolinfo.go.kr/openApi.do"


class SchoolInfoClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.schoolinfo_api_key
        self.client = httpx.AsyncClient(timeout=20.0)

    async def _call(self, api_type: str, school_code: str, **extra) -> dict:
        """raw JSON 응답을 그대로 반환(구조 검증 단계용)."""
        params: dict[str, Any] = {
            "apiKey": self.api_key,
            "apiType": api_type,
            "schulCode": school_code,
            **extra,
        }
        r = await self.client.get(SCHOOLINFO_BASE, params=params)
        r.raise_for_status()
        return r.json()

    async def get_basic_info(self, school_code: str) -> dict:
        return await self._call("00_TY01_001", school_code)

    async def close(self):
        await self.client.aclose()
