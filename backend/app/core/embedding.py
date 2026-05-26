"""Voyage AI 임베딩 모듈.

voyage-multilingual-2 = 1024 차원, 한국어 강함, 무료 200M 토큰.
- 문서(저장용): input_type="document"
- 쿼리(검색용): input_type="query"
"""
from __future__ import annotations

import voyageai

from app.core.config import settings

_client: voyageai.AsyncClient | None = None


def _get_client() -> voyageai.AsyncClient:
    global _client
    if _client is None:
        _client = voyageai.AsyncClient(api_key=settings.voyage_api_key)
    return _client


async def embed_documents(texts: list[str]) -> list[list[float]]:
    """문서 청크 임베딩 (저장용)."""
    client = _get_client()
    result = await client.embed(texts, model=settings.voyage_model, input_type="document")
    return result.embeddings


async def embed_query(text: str) -> list[float]:
    """쿼리 임베딩 (검색용)."""
    client = _get_client()
    result = await client.embed([text], model=settings.voyage_model, input_type="query")
    return result.embeddings[0]
