"""Supabase 클라이언트 팩토리."""
from __future__ import annotations

import httpx
from supabase import Client, create_client

from app.core.config import settings

# 요청마다 새로 만들지 않고 모듈 전역에 캐시 (연결 셋업 비용 절감)
_admin: Client | None = None
_anon: Client | None = None


def execute_with_retry(query_fn, attempts: int = 6):
    """Supabase 호출을 간헐적 transport 오류(HTTP/2 GOAWAY 등 연결 종료) 시 재시도.

    일부 호스팅(예: HF Spaces)→Supabase 경로에서 재사용된 HTTP/2 연결이
    GOAWAY로 끊겨 RemoteProtocolError가 간헐 발생한다. 실패한 연결은 httpx가
    폐기하므로 재시도는 새 연결로 수행되어 대부분 성공한다.
    query_fn: 매 시도마다 쿼리를 새로 만들어 .execute()까지 호출하는 무인자 함수.
    """
    last: Exception | None = None
    for _ in range(attempts):
        try:
            return query_fn()
        except httpx.TransportError as e:  # RemoteProtocolError/ConnectError 등 포함
            last = e
    raise last  # type: ignore[misc]


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
