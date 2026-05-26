---
title: Alrimi+ Backend
emoji: 🏫
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# 알리미+ Backend

학교 공공데이터(NEIS · 학교알리미 · 학교 홈페이지) 기반 RAG 챗봇 백엔드.

- FastAPI + LangChain + Anthropic SDK + Voyage AI
- Supabase (PostgreSQL + pgvector)
- 배포: Hugging Face Spaces (Docker)

## 엔드포인트
- `GET /` — 헬스체크
- `GET /healthz` — 헬스체크

## 로컬 실행
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
