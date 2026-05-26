# 알리미+ (Alrimi+)

> 학교알리미가 진짜 **답하는** 시대 — 학교 공공데이터를 활용한 RAG 챗봇 서비스

제8회 교육 공공데이터 AI 활용대회 출품작 (일반부, 한태영)

## 구조
- `frontend/` — Next.js 14 + TypeScript + Tailwind + shadcn/ui + Vercel AI SDK
- `backend/` — FastAPI + LangChain + Anthropic SDK + Voyage AI
- Data: Supabase (PostgreSQL + pgvector + Auth)

## 데이터 소스
- NEIS Open API (급식·학사일정·시간표)
- 학교알리미 OpenAPI (학교 공시정보)
- 학교 홈페이지 범용 크롤러 (공지사항)

## 데모
- Web: https://alrimi-plus.vercel.app (예정)
- Backend API: https://huggingface.co/spaces/HANANHAN/alrimi-plus-backend

## 개발
[Day 1~11 진행 중]
