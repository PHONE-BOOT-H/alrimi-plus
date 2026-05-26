"""질문에서 날짜 의도와 급식 의도를 파싱.

목적: "오늘/내일/이번 주/5월 27일 급식" 같은 질문에서 날짜를 추출해
벡터 검색만으로는 못 집는 정확한 날짜의 급식 청크를 직접 조회하기 위함.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

_KST = ZoneInfo("Asia/Seoul")


def today_kst() -> date:
    """한국 표준시 기준 오늘. (서버가 UTC라도 한국 사용자 기준으로 '오늘' 계산)"""
    return datetime.now(_KST).date()


_MEAL_HINTS = ("급식", "메뉴", "점심", "중식", "조식", "석식", "밥", "식단", "먹", "반찬")
_WEEKDAYS = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}


def is_meal_query(q: str) -> bool:
    return any(h in q for h in _MEAL_HINTS)


def _week_start(d: date) -> date:
    """그 주의 월요일."""
    return d - timedelta(days=d.weekday())


def parse_date_range(q: str, today: date) -> tuple[date, date] | None:
    """질문에서 날짜(범위)를 추출. 없으면 None.

    반환: (start, end) 두 날짜 모두 포함.
    """
    # 1) 명시적 'M월 D일'
    m = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", q)
    if m:
        mo, da = int(m.group(1)), int(m.group(2))
        try:
            d = date(today.year, mo, da)
            return (d, d)
        except ValueError:
            pass

    # 2) 상대 표현
    if "모레" in q:
        d = today + timedelta(days=2)
        return (d, d)
    if "내일" in q:
        d = today + timedelta(days=1)
        return (d, d)
    if "어제" in q:
        d = today - timedelta(days=1)
        return (d, d)
    if "오늘" in q:
        return (today, today)

    if "다음" in q and "주" in q:
        ws = _week_start(today) + timedelta(days=7)
        return (ws, ws + timedelta(days=4))  # 다음 주 월~금
    if ("지난" in q or "저번" in q) and "주" in q:
        ws = _week_start(today) - timedelta(days=7)
        return (ws, ws + timedelta(days=4))
    if "이번" in q and "주" in q or "금주" in q:
        ws = _week_start(today)
        return (ws, ws + timedelta(days=4))  # 이번 주 월~금

    # 3) 요일 ('월요일 급식' 등) → 이번 주 해당 요일
    wm = re.search(r"([월화수목금토일])\s*요일", q)
    if wm:
        wd = _WEEKDAYS[wm.group(1)]
        d = _week_start(today) + timedelta(days=wd)
        return (d, d)

    # 4) 'D일'만 (월 생략) → 이번 달 그 날
    dm = re.search(r"(?<!\d)(\d{1,2})\s*일", q)
    if dm:
        da = int(dm.group(1))
        try:
            d = date(today.year, today.month, da)
            return (d, d)
        except ValueError:
            pass

    return None
