"""Supabase 클라이언트 팩토리."""
from __future__ import annotations

from supabase import Client, create_client

from app.core.config import settings

# 요청마다 새로 만들지 않고 모듈 전역에 캐시 (연결 셋업 비용 절감)
_admin: Client | None = None
_anon: Client | None = None


def get_supabase_admin() -> Client:
    """Service role — 백엔드 전용, RLS 우회."""
    global _admin
    if _admin is None:
        _admin = create_client(settings.supabase_url, settings.supabase_service_key)
    return _admin


def get_supabase_anon() -> Client:
    """Anon key — 사용자 컨텍스트 기반 호출용."""
    global _anon
    if _anon is None:
        _anon = create_client(settings.supabase_url, settings.supabase_anon_key)
    return _anon
