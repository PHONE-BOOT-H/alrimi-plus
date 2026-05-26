"""Voyage 임베딩 테스트. 네트워크 의존 — .env에 VOYAGE_API_KEY 필요."""
import pytest

from app.core.embedding import embed_documents, embed_query


@pytest.mark.asyncio
async def test_embed_documents():
    embs = await embed_documents(["오늘 급식은 김치찌개입니다.", "내일 시험이 있어요."])
    assert len(embs) == 2
    assert len(embs[0]) == 1024


@pytest.mark.asyncio
async def test_embed_query():
    emb = await embed_query("급식 뭐 나와?")
    assert len(emb) == 1024
