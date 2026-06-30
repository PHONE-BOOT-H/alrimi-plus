"""/api/schools — 등록된 학교 목록 (프론트 드롭다운용).

브라우저 anon 키는 RLS로 schools를 못 읽어서, 백엔드가 service 키로 대신 제공한다.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.db.supabase_client import execute_with_retry, get_supabase_admin

router = APIRouter(prefix="/api", tags=["schools"])


@router.get("/schools")
def list_schools():
    sb = get_supabase_admin()
    r = execute_with_retry(
        lambda: sb.table("schools")
        .select("school_code, school_name, school_type, region")
        .order("school_name")
        .execute()
    )
    return r.data or []
