"""NEIS 수집기 테스트. 네트워크(NEIS API) 의존 — .env에 NEIS_API_KEY 필요."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.data.neis_collector import ALLERGY_CODES, NEISClient, parse_allergy_string

SAMPLE_SCHOOL = "서울대학교사범대학부설초등학교"


@pytest.mark.asyncio
async def test_search_school():
    client = NEISClient()
    try:
        rows = await client.search_school(SAMPLE_SCHOOL)
    finally:
        await client.close()
    assert len(rows) > 0
    assert "SD_SCHUL_CODE" in rows[0]
    assert "ATPT_OFCDC_SC_CODE" in rows[0]


@pytest.mark.asyncio
async def test_get_meals_returns_list():
    client = NEISClient()
    try:
        rows = await client.search_school(SAMPLE_SCHOOL)
        assert rows
        edu = rows[0]["ATPT_OFCDC_SC_CODE"]
        sc = rows[0]["SD_SCHUL_CODE"]
        today = date.today()
        meals = await client.get_meals(edu, sc, today - timedelta(days=30), today + timedelta(days=30))
    finally:
        await client.close()
    assert isinstance(meals, list)
    if meals:
        assert "DDISH_NM" in meals[0]


def test_parse_allergy():
    assert parse_allergy_string("오징어덮밥 (1.5.9)") == ["1", "5", "9"]
    assert parse_allergy_string("국 (2)") == ["2"]
    assert parse_allergy_string("물") == []
    # 코드 순서는 숫자 정렬
    assert parse_allergy_string("볶음 (10.2.5)") == ["2", "5", "10"]


def test_allergy_codes_complete():
    assert len(ALLERGY_CODES) == 19
    assert ALLERGY_CODES["1"] == "난류"
    assert ALLERGY_CODES["19"] == "잣"
