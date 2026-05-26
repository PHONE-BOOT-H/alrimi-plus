"""애플리케이션 설정.

로컬에서는 backend/.env, HF Spaces에서는 Repository secrets에서 환경변수를 읽는다.
.env 키 이름과 코드 속성명이 다른 경우(SUPABASE_SERVICE_ROLE_KEY 등)는 alias로 흡수한다.
"""
from __future__ import annotations

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 공공데이터 API
    neis_api_key: str
    schoolinfo_api_key: str

    # LLM / 임베딩
    anthropic_api_key: str
    voyage_api_key: str

    # Supabase
    supabase_url: str
    # .env에는 SUPABASE_SERVICE_ROLE_KEY로 저장돼 있어 두 이름 모두 허용
    supabase_service_key: str = Field(
        validation_alias=AliasChoices("SUPABASE_SERVICE_KEY", "SUPABASE_SERVICE_ROLE_KEY")
    )
    supabase_anon_key: str

    # 모델 설정 (기본값; .env의 ANTHROPIC_MODEL_* 와는 이름이 달라 충돌 없음)
    claude_model_default: str = "claude-haiku-4-5-20251001"
    claude_model_complex: str = "claude-sonnet-4-6"
    voyage_model: str = "voyage-multilingual-2"

    # CORS — 콤마 구분 문자열로 받는다(list 타입이면 pydantic-settings가 JSON 디코드를
    # 시도해 실패함). 실제 리스트는 cors_origins 프로퍼티로 노출.
    cors_origins_raw: str = Field(
        default="http://localhost:3000,https://alrimi-plus.vercel.app",
        validation_alias="CORS_ORIGINS",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]


settings = Settings()
