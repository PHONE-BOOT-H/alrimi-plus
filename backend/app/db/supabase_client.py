"""Supabase 클라이언트 팩토리."""
from __future__ import annotations

from supabase import Client, create_client

from app.core.config import settings


def get_supabase_admin() -> Client:
    """Service role — 백엔드 전용, RLS 우회."""
    return create_client(settings.supabase_url, settings.supabase_service_key)


def get_supabase_anon() -> Client:
    """Anon key — 사용자 컨텍스트 기반 호출용."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)
