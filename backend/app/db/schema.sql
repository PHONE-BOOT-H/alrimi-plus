-- ============================================================
-- 알리미+ Supabase 스키마
-- Supabase Dashboard → SQL Editor → New query → 전체 붙여넣기 → Run
-- 오류 시 한 블록씩 분리 실행
-- ============================================================

-- 확장: pgvector(벡터검색) + pg_trgm(학교명 유사검색)
-- ⚠️ pg_trgm은 아래 idx_schools_name(gin_trgm_ops)보다 먼저 활성화되어야 함
create extension if not exists vector;
create extension if not exists pg_trgm;

-- 1. 학교 마스터 테이블
create table if not exists schools (
    school_code text primary key,           -- NEIS 학교 코드 (SD_SCHUL_CODE)
    edu_office_code text not null,          -- 시도교육청 코드 (ATPT_OFCDC_SC_CODE)
    school_name text not null,
    school_type text,                       -- 초/중/고
    region text,
    address text,
    last_synced_at timestamptz default now(),
    created_at timestamptz default now()
);

create index if not exists idx_schools_name on schools using gin (school_name gin_trgm_ops);

-- 2. 학교 문서 청크 (RAG 본체)
create table if not exists school_documents (
    id bigserial primary key,
    school_code text not null references schools(school_code) on delete cascade,
    source_type text not null,              -- 'neis_meal' | 'neis_schedule' | 'neis_timetable' | 'schoolinfo' | 'homepage'
    source_url text,                        -- 원본 API/URL
    title text,
    content text not null,                  -- 청크 본문
    metadata jsonb default '{}'::jsonb,     -- 날짜, 학년 등 부가 정보
    embedding vector(1024),                 -- Voyage multilingual-2 = 1024 차원
    fetched_at timestamptz default now(),
    valid_from date,
    valid_to date
);

create index if not exists idx_school_docs_school on school_documents(school_code);
create index if not exists idx_school_docs_source on school_documents(source_type);
create index if not exists idx_school_docs_embedding on school_documents
    using ivfflat (embedding vector_cosine_ops) with (lists = 100);

-- 3. 사용자 자녀 (Supabase Auth와 연동)
create table if not exists user_children (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    nickname text not null,                 -- 자녀 별명 (실명 X)
    school_code text references schools(school_code),
    grade integer,                          -- 1~6 (초), 1~3 (중·고)
    allergies text[] default '{}',          -- 알레르기 코드 배열
    created_at timestamptz default now()
);

alter table user_children enable row level security;

drop policy if exists "users see only their children" on user_children;
create policy "users see only their children"
    on user_children for all
    using (auth.uid() = user_id);

-- 4. 채팅 로그 (피드백 수집용)
create table if not exists chat_logs (
    id bigserial primary key,
    user_id uuid references auth.users(id) on delete set null,
    session_id text,
    school_code text references schools(school_code),
    question text not null,
    answer text not null,
    sources jsonb default '[]'::jsonb,
    feedback smallint,                      -- -1, 0, 1
    language text default 'ko',
    created_at timestamptz default now()
);

-- 5. pgvector 유사도 검색 함수
create or replace function match_documents(
    query_embedding vector(1024),
    p_school_code text,
    match_count int default 6
) returns table (
    id bigint,
    school_code text,
    source_type text,
    title text,
    content text,
    metadata jsonb,
    source_url text,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        d.id,
        d.school_code,
        d.source_type,
        d.title,
        d.content,
        d.metadata,
        d.source_url,
        1 - (d.embedding <=> query_embedding) as similarity
    from school_documents d
    where d.school_code = p_school_code
    order by d.embedding <=> query_embedding
    limit match_count;
end;
$$;
