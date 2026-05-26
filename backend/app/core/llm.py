"""Anthropic Claude 클라이언트 + 모델 라우팅.

확정 사양: Haiku 4.5 기본, 복잡한 질문은 Sonnet 4.6로 라우팅(비용 최적화).
"""
from __future__ import annotations

import anthropic

from app.core.config import settings

_client: anthropic.AsyncAnthropic | None = None

# 복잡/분석형 질문 신호 → Sonnet 라우팅
_COMPLEX_HINTS = (
    "분석", "비교", "왜", "이유", "추천", "요약", "정리해", "차이",
    "추세", "경향", "어떻게 생각", "조언", "설명해줘",
)


def get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


def route_model(question: str) -> str:
    """질문 난이도에 따라 모델 선택. 분석형 신호가 있으면 Sonnet, 아니면 Haiku.

    (긴 질문을 무조건 Sonnet으로 보내면 긴 입력으로 비용을 강제 증폭시킬 수 있어
     길이 기준은 제외하고, 분석형 키워드로만 승급한다.)
    """
    q = question.strip()
    if any(h in q for h in _COMPLEX_HINTS):
        return settings.claude_model_complex
    return settings.claude_model_default
