"""pgvector 유사도 검색(match_documents) 테스트.

네트워크 의존(Voyage + Supabase) + 데이터 선적재 필요:
    python -m scripts.seed_schools && python -m scripts.refresh_data
"""
import pytest

from app.core.embedding import embed_query
from app.db.supabase_client import get_supabase_admin


@pytest.mark.asyncio
async def test_match_documents_meal():
    sb = get_supabase_admin()
    # 청크가 적재된 학교 하나 선택
    docs = (
        sb.table("school_documents")
        .select("school_code")
        .eq("source_type", "neis_meal")
        .limit(1)
        .execute()
        .data
    )
    assert docs, "school_documents 비어있음 — refresh_data 먼저 실행"
    code = docs[0]["school_code"]

    emb = await embed_query("오늘 급식 뭐 나와?")
    res = sb.rpc(
        "match_documents",
        {"query_embedding": emb, "p_school_code": code, "match_count": 3},
    ).execute()
    assert res.data
    # 급식 질문이므로 최상위는 급식 청크여야 함
    assert res.data[0]["source_type"] == "neis_meal"
    assert "메뉴" in res.data[0]["content"]
