"""출품작 제안서 PDF 생성 (HTML→Playwright PDF). python -m scripts.build_deck

요강 반영: 표지 다음 활용데이터 페이지, AI 활용흐름, 검증 매트릭스, 방법론·한계,
비교표, 콜아웃, 증거배지. 식별정보(실명·학교명·지역명) 미기재.
"""
from __future__ import annotations

import base64
import os

from playwright.sync_api import sync_playwright

SUB = r"C:\Users\hanta\Desktop\한태영\대외활동\공모전\교육공공데이터활용대회\14_제출본"
OUT_PDF = os.path.join(SUB, "알리미플러스_출품작.pdf")
OUT_HTML = os.path.join(SUB, "_deck.html")


def b64(name: str) -> str:
    with open(os.path.join(SUB, name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


IMG = {
    "SOL": b64("캡처_솔루션답변.png"),
    "CAP2": b64("캡처2_개인화알레르기.png"),
    "CAP3": b64("캡처3_출처.png"),
    "CAP4": b64("캡처4_영어답변.png"),
    "CH1": b64("차트1_알레르기_출현빈도.png"),
    "CH2": b64("차트2_프로필별_경고비율.png"),
    "ARCH": b64("아키텍처_다이어그램.png"),
}

CSS = """
@page { size:1280px 720px; margin:0; }
* { margin:0; padding:0; box-sizing:border-box; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
body { font-family:'Pretendard','Malgun Gothic',sans-serif; color:#0f172a; }
.page { width:1280px; height:720px; padding:52px 64px; position:relative; page-break-after:always; background:#fff; overflow:hidden; }
.page:last-child { page-break-after:auto; }
.kicker { color:#2563eb; font-weight:800; font-size:17px; letter-spacing:2px; }
.bar { height:7px; width:54px; background:#2563eb; border-radius:4px; margin:10px 0 18px; }
h1 { font-size:58px; font-weight:800; line-height:1.12; letter-spacing:-1px; }
h2 { font-size:38px; font-weight:800; line-height:1.18; margin-bottom:16px; letter-spacing:-1px; }
.sub { font-size:25px; color:#334155; font-weight:600; }
.desc { font-size:18px; color:#64748b; line-height:1.6; }
.big { font-size:140px; font-weight:800; color:#dc2626; line-height:1; letter-spacing:-3px; }
.hl { color:#dc2626; }
.blue { color:#2563eb; }
ul { list-style:none; }
li { font-size:20px; line-height:1.7; padding-left:28px; position:relative; color:#1e293b; margin-bottom:4px; }
li:before { content:"›"; position:absolute; left:4px; color:#2563eb; font-weight:800; }
.foot { position:absolute; bottom:24px; left:64px; right:64px; display:flex; justify-content:space-between; font-size:12px; color:#94a3b8; }
.shot { border:1px solid #e2e8f0; border-radius:12px; box-shadow:0 10px 30px rgba(15,23,42,.12); }
.two { display:flex; gap:42px; align-items:center; height:500px; }
.two .txt { flex:1.05; } .two .vis { flex:.95; display:flex; justify-content:center; align-items:center; height:100%; }
.two .vis img { max-height:498px; max-width:100%; }
.cover { height:100%; display:flex; flex-direction:column; justify-content:center; }
.badge { display:inline-block; border:1px solid #cbd5e1; border-radius:999px; padding:7px 16px; font-size:14px; color:#475569; margin-bottom:24px; width:fit-content; }
.pill { display:inline-block; background:#eff6ff; color:#2563eb; border-radius:999px; padding:6px 15px; font-size:15px; font-weight:700; margin:4px 6px 4px 0; }
.badges { margin-top:30px; }
.badges .b { display:inline-block; background:#0f172a; color:#fff; border-radius:8px; padding:7px 13px; font-size:13px; font-weight:700; margin:4px 6px 4px 0; }
table.t { width:100%; border-collapse:collapse; font-size:16px; }
table.t th { background:#0f172a; color:#fff; padding:10px 12px; text-align:left; font-size:15px; }
table.t td { padding:9px 12px; border-bottom:1px solid #eef2f7; }
table.t td.k { color:#475569; font-weight:700; width:30%; }
table.t .yes { color:#16a34a; font-weight:800; } .t .no { color:#cbd5e1; } .t .star { color:#2563eb; font-weight:800; }
.box { background:#f8fafc; border:1px solid #e8edf3; border-left:4px solid #2563eb; border-radius:8px; padding:14px 18px; font-size:15px; color:#475569; line-height:1.55; }
.callout { background:#eff6ff; border-radius:10px; padding:12px 16px; font-size:16px; margin-bottom:10px; color:#1e3a8a; }
.callout b { color:#2563eb; }
.flow { font-size:18px; line-height:1.5; }
.flow .s { display:flex; gap:12px; margin-bottom:9px; align-items:flex-start; }
.flow .num { background:#2563eb; color:#fff; border-radius:7px; min-width:26px; height:26px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:14px; }
.grid5 { display:flex; gap:14px; margin-top:6px; }
.gcard { flex:1; background:#f8fafc; border:1px solid #e8edf3; border-radius:14px; padding:18px 14px; }
.gcard .n { color:#2563eb; font-weight:800; font-size:14px; } .gcard .t2 { font-weight:800; font-size:18px; margin:6px 0 5px; } .gcard .d { font-size:13px; color:#64748b; line-height:1.45; }
.eq { background:#fff7ed; border:1px solid #fed7aa; border-radius:12px; padding:18px 20px; font-size:19px; line-height:1.7; }
.eq .op { color:#ea580c; font-weight:800; }
.steps { display:flex; gap:14px; margin-top:18px; } .step { flex:1; background:#f8fafc; border-radius:12px; padding:14px; font-size:15px; } .step b { display:block; color:#2563eb; font-size:13px; margin-bottom:5px; }
.jr { font-size:15px; line-height:1.55; }
.jr .old { background:#fef2f2; border-radius:8px; padding:12px 14px; color:#991b1b; margin-bottom:10px; }
.jr .new { background:#ecfdf5; border-radius:8px; padding:12px 14px; color:#065f46; }
.rm { display:flex; gap:12px; margin-top:14px; } .rm div { flex:1; background:#f8fafc; border:1px solid #e8edf3; border-radius:10px; padding:13px; font-size:14px; line-height:1.45; } .rm b { color:#0f172a; }
"""


def foot(n):
    return f'<div class="foot"><span>알리미+ (Alrimi+) · 학교 공공데이터 AI · 팀명 소크라테스의 식판</span><span>{n} / 15</span></div>'


def page(inner, n):
    return f'<div class="page">{inner}{foot(n)}</div>'


P = []

# 1 Cover
P.append(page(f"""
<div class="cover">
  <div class="badge">제8회 교육 공공데이터 AI 활용대회 · 일반부</div>
  <h1>알리미+ <span class="blue">(Alrimi+)</span></h1>
  <div class="sub" style="margin-top:16px">학교 공공데이터를 <span class="blue">출처와 함께</span> 답하는 AI</div>
  <div class="desc" style="margin-top:12px;max-width:840px">모든 학부모를 위한 학교 급식·학사정보 챗봇 — 알레르기 맞춤 안내 · 한국어/영어 지원</div>
  <div class="badges">
    <span class="b">LIVE 배포 완료</span><span class="b">NEIS 10개교·490청크</span><span class="b">출처 인용 RAG</span>
    <span class="b">알레르기 코드 교차계산</span><span class="b">라이브 검증 12/12</span>
  </div>
  <div style="margin-top:22px"><span class="pill">데모 · alrimi-plus.vercel.app</span></div>
</div>""", 1))

# 2 활용 데이터 · AI 활용 요약 (규정 필수: 표지 다음)
P.append(page(f"""
<div class="kicker">DATA & AI</div><div class="bar"></div>
<h2>활용 데이터와 AI 처리 흐름</h2>
<table class="t">
  <tr><td class="k">활용 공공데이터</td><td>NEIS 급식식단정보 · NEIS 학사일정 (교육부 나이스 개방포털)</td></tr>
  <tr><td class="k">주요 필드</td><td>학교·날짜·메뉴·열량/영양·알레르기 코드(1~19)·행사명</td></tr>
  <tr><td class="k">활용 범위</td><td>시범 10개교(초4·중3·고3) · 급식 223끼 · 약 490개 검색 청크</td></tr>
  <tr><td class="k">AI 활용</td><td>Voyage 임베딩 → pgvector 학교별 의미검색 → Claude 답변 생성 → 출처 인용</td></tr>
  <tr><td class="k">비(非)AI 안전로직</td><td>날짜 직접조회 · <b>사용자 알레르기 ∩ NEIS 알레르기 코드 = 경고</b>(코드 계산)</td></tr>
  <tr><td class="k">산출물</td><td>학교별 질의응답 · 출처 원문 · 알레르기 맞춤 경고 · 한/영 응답</td></tr>
  <tr><td class="k">개인정보</td><td>알레르기 설정은 localStorage(기기 저장), 서버 미저장 · 학생 개인정보 미수집</td></tr>
</table>
<div class="box" style="margin-top:14px">생성형 AI는 <b>출처가 있는 답변 생성</b>에만 사용. 알레르기 경고 등 안전 기능은 LLM 추측이 아닌 <b>코드 레벨 교차계산</b>으로 처리.</div>""", 2))

# 3 문제정의 (user journey)
P.append(page("""
<div class="kicker">PROBLEM</div><div class="bar"></div>
<h2>정보는 NEIS에 있다. 그런데 못 찾는다.</h2>
<div class="jr">
  <div class="old"><b>기존 방식</b> · 앱/학교 홈페이지 접속 → 학교 선택 → 급식표 → 알레르기 번호(1~19) 해석 → 우리 아이 항목과 대조</div>
  <div class="new"><b>알리미+</b> · 학교 선택 → "오늘 급식 뭐 나와?" → 메뉴 + 출처 + <b>내 아이 주의 항목</b></div>
</div>
<div class="grid5" style="margin-top:18px">
  <div class="gcard"><div class="t2">일반 학부모</div><div class="d">여러 출처를 오가며 급식·학사일정 확인</div></div>
  <div class="gcard"><div class="t2">알레르기 가정</div><div class="d">매일 급식표의 알레르기 번호를 직접 해독 — 안전 확인 노동</div></div>
  <div class="gcard"><div class="t2">다문화 가정</div><div class="d">한국어 정보 장벽 — 학교생활 파악 어려움</div></div>
</div>""", 3))

# 4 데이터 인사이트 + 방법론/한계
P.append(page(f"""
<div class="kicker">DATA INSIGHT</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <div class="big">100%</div>
    <div class="sub" style="margin-top:12px">시범 10개교 223끼 기준,<br>우유+밀 알레르기 아동은 <span class="hl">모든 급식에 경고 필요</span></div>
    <div class="box" style="margin-top:18px">분석 방법 · NEIS 메뉴별 알레르기 코드(1~19) 수집 → 날짜별 급식 단위 통합 → 사용자 알레르기 프로필과 교차계산<br>한계 · 시범 10개교 표본(전국 일반화 아님), MVP 검증용 분석</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CH2']}"></div>
</div>""", 4))

# 5 솔루션 (chat answer)
P.append(page(f"""
<div class="kicker">SOLUTION</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>학교 고르고, 물어보면,<br>출처와 함께 답한다</h2>
    <div class="steps">
      <div class="step"><b>STEP 1</b>우리 학교 선택</div>
      <div class="step"><b>STEP 2</b>자연어 질문</div>
      <div class="step"><b>STEP 3</b>출처·경고 포함 답변</div>
    </div>
    <div class="callout" style="margin-top:20px"><b>→</b> 표를 뒤지는 게 아니라 대화 한 줄로. 답마다 <b>근거(출처)</b>가 붙는다.</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['SOL']}"></div>
</div>""", 5))

# 6 차별화 비교표
P.append(page("""
<div class="kicker">WHY DIFFERENT</div><div class="bar"></div>
<h2>기존 급식 앱과 무엇이 다른가</h2>
<table class="t">
  <tr><th>기능</th><th>일반 급식앱 / NEIS</th><th>일반 챗봇</th><th>알리미+</th></tr>
  <tr><td class="k">학교별 공공데이터</td><td>있음</td><td class="no">불안정</td><td class="star">있음</td></tr>
  <tr><td class="k">자연어 질문</td><td class="no">약함</td><td>있음</td><td class="star">있음</td></tr>
  <tr><td class="k">출처 인용</td><td class="no">약함</td><td class="no">약함</td><td class="star">답변마다 표시</td></tr>
  <tr><td class="k">날짜 직접조회</td><td>제한적</td><td class="no">자주 틀림</td><td class="star">하이브리드 조회</td></tr>
  <tr><td class="k">개인 알레르기 경고</td><td>수동 확인</td><td class="no">추측 위험</td><td class="star">코드 교차계산</td></tr>
  <tr><td class="k">영어 응답</td><td class="no">제한적</td><td>출처 약함</td><td class="star">출처 유지</td></tr>
</table>
<div class="callout" style="margin-top:16px"><b>핵심</b> · 데이터를 '보여주는' 앱이 아니라, 공공데이터를 <b>사용자 상황에 맞게 해석</b>하는 AI</div>""", 6))

# 7 출처 인용 (callouts)
P.append(page(f"""
<div class="kicker">TRUST</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>지어내지 않습니다.<br>출처를 함께.</h2>
    <div class="callout"><b>여기 →</b> 답변 본문 속 <b>[1] [2]</b> 근거 표기</div>
    <div class="callout"><b>여기 →</b> 하단 <b>출처 원문</b> 카드(날짜·유형)</div>
    <div class="callout"><b>정책 →</b> 검색 결과 없으면 <b>"모른다"</b>고 답(환각 방지)</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CAP3']}" style="max-height:498px"></div>
</div>""", 7))

# 8 개인화 알레르기 (교차계산 수식)
P.append(page(f"""
<div class="kicker">SAFETY</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>우리 아이 기준으로<br>경고합니다</h2>
    <div class="eq">사용자 설정 <b>{{우유, 밀}}</b><br><span class="op">∩</span> NEIS 메뉴 코드 <b>{{우유, 대두, 밀, 새우}}</b><br><span class="op">=</span> <span class="hl">⚠️ 주의: 우유, 밀</span></div>
    <ul style="margin-top:16px">
      <li>안전 기능은 <b>LLM 추측 금지 → 코드 교차계산</b></li>
      <li>알레르기 설정은 <b>이 기기에만 저장</b>(서버 미저장)</li>
    </ul>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CAP2']}" style="max-height:498px"></div>
</div>""", 8))

# 9 다국어
P.append(page(f"""
<div class="kicker">ACCESS</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>영어 질문에도 NEIS 근거와<br>날짜 정확도를 유지</h2>
    <ul>
      <li>영어 질문 → 한국어 NEIS 검색 → <b>영어 답변</b> 생성</li>
      <li>메뉴명·알레르기·<b>출처</b>를 그대로 유지</li>
      <li>다문화 학생 <b>20만 명(전체 4.0%)</b>* 의 정보 접근성</li>
    </ul>
    <div class="desc" style="margin-top:14px">* 한국교육개발원 2025 교육기본통계</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CAP4']}" style="max-height:498px"></div>
</div>""", 9))

# 10 아키텍처 + 처리흐름
P.append(page(f"""
<div class="kicker">HOW IT WORKS</div><div class="bar"></div>
<h2>처리 흐름 — 운영 가능한 RAG 시스템</h2>
<div style="display:flex;gap:36px">
  <div class="flow" style="flex:1.1">
    <div class="s"><span class="num">1</span>학교 선택값으로 검색 범위 제한</div>
    <div class="s"><span class="num">2</span>질문 언어·의도·날짜 표현 파악(오늘/이번주/특정일)</div>
    <div class="s"><span class="num">3</span>급식+날짜면 NEIS <b>날짜 직접조회</b> 병합</div>
    <div class="s"><span class="num">4</span>pgvector <b>의미검색</b>으로 관련 문서</div>
    <div class="s"><span class="num">5</span>Claude가 <b>출처 기반</b> 답변 생성</div>
    <div class="s"><span class="num">6</span>알레르기 경고는 <b>코드 교차계산</b>으로 삽입</div>
    <div class="s"><span class="num">7</span>주제이탈·프롬프트 인젝션 차단</div>
  </div>
  <div style="flex:1;display:flex;align-items:center"><img src="{IMG['ARCH']}" style="max-width:100%;max-height:420px"></div>
</div>
<div class="desc" style="margin-top:8px">Next.js(Vercel) · FastAPI(Hugging Face) · Supabase(pgvector) · Voyage 임베딩 · Anthropic Claude</div>""", 10))

# 11 검증 매트릭스
P.append(page("""
<div class="kicker">VERIFICATION</div><div class="bar"></div>
<h2>라이브 환경 12/12 — 데모가 아니라 동작하는 서비스</h2>
<div style="display:flex;gap:28px">
  <table class="t" style="flex:1.15;font-size:14px">
    <tr><th>테스트</th><th>로컬</th><th>라이브</th></tr>
    <tr><td>오늘/특정일 급식</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
    <tr><td>출처 [1][2]·원문 표시</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
    <tr><td>우유+밀 알레르기 경고</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
    <tr><td>이번 주 학사일정</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
    <tr><td>타 학교 데이터 혼입 방지</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
    <tr><td>영어 질문→영어 답변</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
    <tr><td>주제이탈·인젝션 거절</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
  </table>
  <table class="t" style="flex:1;font-size:14px">
    <tr><th>발견 결함</th><th>수정</th><th>재검증</th></tr>
    <tr><td>타임존(오늘 날짜 오답)</td><td>KST 기준 처리</td><td class="yes">PASS</td></tr>
    <tr><td>레이트리밋 우회</td><td>IP/전역 제한</td><td class="yes">PASS</td></tr>
    <tr><td>동시접속 블로킹</td><td>비동기 보완</td><td class="yes">PASS</td></tr>
    <tr><td>프롬프트 인젝션</td><td>사전 차단</td><td class="yes">PASS</td></tr>
  </table>
</div>
<div class="callout" style="margin-top:14px">골든 질문 12종 · <b>로컬 12/12 + 라이브 12/12</b> · 독립 AI 코드리뷰로 결함 수정 후 재검증</div>""", 11))

# 12 공공데이터 분석 (chart1)
P.append(page(f"""
<div class="kicker">PUBLIC DATA</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>공공데이터를 '조회'가 아니라<br>'판단'으로 전환</h2>
    <ul>
      <li>NEIS 급식식단정보: 메뉴·영양·<b>알레르기 코드</b></li>
      <li>처리: 정규화 → 청킹 → 학교별 메타데이터 → 검색/직접조회</li>
      <li>같은 데이터로 "오늘 메뉴"를 넘어 <b>"내 아이가 조심할 항목"</b>으로</li>
    </ul>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CH1']}"></div>
</div>""", 12))

# 13 활용 가능성 (시나리오)
P.append(page("""
<div class="kicker">USABILITY</div><div class="bar"></div>
<h2>누가, 어떻게 더 빨라지는가</h2>
<table class="t">
  <tr><th>과제</th><th>기존 방식</th><th>알리미+</th></tr>
  <tr><td class="k">오늘 급식 + 우리 아이 알레르기 확인</td><td>앱 열고 메뉴별 번호(1~19) 해석·대조 (여러 단계)</td><td class="star">한 번 질문 → 주의 항목 자동 강조</td></tr>
  <tr><td class="k">이번 주 학사일정 확인</td><td>학교 홈페이지·가정통신문 탐색</td><td class="star">"이번 주 학사일정" 한 줄</td></tr>
  <tr><td class="k">다문화 보호자의 급식 확인</td><td>한국어만 → 어려움</td><td class="star">영어로 질문·답변</td></tr>
</table>
<div class="box" style="margin-top:16px">간이 사용성 테스트(n=3~5) 계획 · 과제별 <b>소요시간·성공률·신뢰도(5점)</b>를 기존 방식과 비교 측정 → 결과는 발표 자료에 반영.</div>""", 13))

# 14 확장·운영 계획
P.append(page("""
<div class="kicker">ROADMAP & OPS</div><div class="bar"></div>
<h2>검증된 MVP에서 운영 서비스로</h2>
<table class="t">
  <tr><th>단계</th><th>범위</th><th>검증할 것</th></tr>
  <tr><td class="k">현재 MVP</td><td>10개교, 급식·학사일정</td><td>RAG 정확도·날짜조회·알레르기 경고</td></tr>
  <tr><td class="k">1차 확장</td><td>학교 수 확대·자동 갱신</td><td>수집 안정성·비용·응답속도</td></tr>
  <tr><td class="k">2차 확장</td><td>학교알리미·홈페이지 공지 연동</td><td>데이터 다변화·최신성</td></tr>
  <tr><td class="k">운영</td><td>피드백·오답 신고</td><td>품질 개선 루프</td></tr>
</table>
<div class="rm">
  <div><b>개인정보 최소화</b><br>알레르기 설정 서버 미저장</div>
  <div><b>비용 통제</b><br>주제 가드·레이트리밋·모델 라우팅</div>
  <div><b>품질 관리</b><br>골든질문 회귀 테스트·출처 없는 답변 제한</div>
</div>""", 14))

# 15 Closing
P.append(page("""
<div class="cover" style="align-items:flex-start">
  <div class="kicker">알리미+ (Alrimi+)</div>
  <h1 style="margin-top:8px">학교 공공데이터를,<br>학부모가 바로 쓸 <span class="blue">답</span>으로.</h1>
  <div class="desc" style="margin-top:22px;font-size:21px">출처 인용 RAG · 알레르기 코드 기반 경고 · 한/영 접근성 · 라이브 검증 12/12</div>
  <div style="margin-top:26px"><span class="pill" style="font-size:19px;padding:10px 20px">alrimi-plus.vercel.app</span></div>
  <div class="desc" style="margin-top:20px">추천 질문 · "오늘 급식 뭐 나와?" / "이번 주 학사일정" / "What's on the lunch menu today?"</div>
</div>""", 15))

html = f"<!doctype html><html><head><meta charset='utf-8'><style>@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css');{CSS}</style></head><body>{''.join(P)}</body></html>"

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

with sync_playwright() as p:
    browser = p.chromium.launch()
    pg = browser.new_page()
    pg.goto("file:///" + OUT_HTML.replace("\\", "/"), wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(1800)
    pg.pdf(path=OUT_PDF, width="1280px", height="720px", print_background=True,
           margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    browser.close()

print("PDF:", OUT_PDF, "|", round(os.path.getsize(OUT_PDF) / 1024 / 1024, 2), "MB")
