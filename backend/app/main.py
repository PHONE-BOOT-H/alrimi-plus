"""알리미+ 백엔드 FastAPI 엔트리포인트."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.core.config import settings

app = FastAPI(title="Alrimi+ Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/")
def health():
    return {"status": "ok", "service": "alrimi-plus-backend"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
