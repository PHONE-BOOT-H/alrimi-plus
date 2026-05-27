"""출품작 제안서 PDF 생성 (HTML→Playwright PDF). python -m scripts.build_deck

14_제출본의 캡처/차트/다이어그램을 base64로 임베드해 16:9 슬라이드 13매 PDF 생성.
식별정보(실명) 미기재. 팀명만 표기.
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
    "CAP1": b64("캡처1_랜딩.png"),
    "CAP2": b64("캡처2_개인화알레르기.png"),
    "CAP3": b64("캡처3_출처.png"),
    "CAP4": b64("캡처4_영어답변.png"),
    "CH1": b64("차트1_알레르기_출현빈도.png"),
    "CH2": b64("차트2_프로필별_경고비율.png"),
    "ARCH": b64("아키텍처_다이어그램.png"),
}

CSS = """
@page { size: 1280px 720px; margin: 0; }
* { margin:0; padding:0; box-sizing:border-box; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
body { font-family:'Pretendard','Malgun Gothic',sans-serif; color:#0f172a; }
.page { width:1280px; height:720px; padding:60px 72px; position:relative; page-break-after:always; background:#ffffff; overflow:hidden; }
.page:last-child { page-break-after:auto; }
.kicker { color:#2563eb; font-weight:800; font-size:18px; letter-spacing:2px; margin-bottom:14px; }
h1 { font-size:60px; font-weight:800; line-height:1.12; letter-spacing:-1px; }
h2 { font-size:42px; font-weight:800; line-height:1.2; margin-bottom:22px; letter-spacing:-1px; }
.sub { font-size:26px; color:#334155; font-weight:600; }
.desc { font-size:19px; color:#64748b; line-height:1.6; }
.big { font-size:150px; font-weight:800; color:#dc2626; line-height:1; letter-spacing:-3px; }
.muted { color:#64748b; }
ul { list-style:none; }
li { font-size:21px; line-height:1.75; padding-left:30px; position:relative; color:#1e293b; }
li:before { content:"›"; position:absolute; left:6px; color:#2563eb; font-weight:800; }
.foot { position:absolute; bottom:26px; left:72px; right:72px; display:flex; justify-content:space-between; font-size:13px; color:#94a3b8; }
.shot { border:1px solid #e2e8f0; border-radius:14px; box-shadow:0 10px 36px rgba(15,23,42,.12); }
.bar { height:8px; width:60px; background:#2563eb; border-radius:4px; margin-bottom:22px; }
.grid5 { display:flex; gap:16px; margin-top:10px; }
.gcard { flex:1; background:#f8fafc; border:1px solid #e8edf3; border-radius:16px; padding:22px 18px; }
.gcard .n { color:#2563eb; font-weight:800; font-size:15px; }
.gcard .t { font-weight:800; font-size:20px; margin:8px 0 6px; }
.gcard .d { font-size:14px; color:#64748b; line-height:1.5; }
.two { display:flex; gap:48px; align-items:center; height:480px; }
.two .txt { flex:1; }
.two .vis { flex:1; display:flex; justify-content:center; align-items:center; height:100%; }
.two .vis img { max-height:480px; max-width:100%; }
.cover { height:100%; display:flex; flex-direction:column; justify-content:center; }
.badge { display:inline-block; border:1px solid #cbd5e1; border-radius:999px; padding:8px 18px; font-size:15px; color:#475569; margin-bottom:28px; width:fit-content; }
.pill { display:inline-block; background:#eff6ff; color:#2563eb; border-radius:999px; padding:6px 16px; font-size:16px; font-weight:700; margin-right:8px; }
.tbl { width:100%; border-collapse:collapse; font-size:18px; margin-top:8px; }
.tbl td { padding:12px 10px; border-bottom:1px solid #eef2f7; }
.tbl td.k { color:#475569; }
.tbl td.v { font-weight:800; text-align:right; }
.hl { color:#dc2626; }
.steps { display:flex; gap:18px; margin-top:22px; }
.step { flex:1; background:#f8fafc; border-radius:14px; padding:18px; font-size:17px; }
.step b { display:block; color:#2563eb; font-size:15px; margin-bottom:6px; }
.rm { display:flex; gap:14px; margin-top:18px; }
.rm div { flex:1; background:#f8fafc; border:1px solid #e8edf3; border-radius:12px; padding:16px; font-size:15px; }
.rm div b { color:#0f172a; }
"""


def foot(n: int) -> str:
    return f'<div class="foot"><span>알리미+ (Alrimi+) · 학교 공공데이터 AI</span><span>{n} / 13</span></div>'


def page(inner: str, n: int) -> str:
    return f'<div class="page">{inner}{foot(n)}</div>'


pages = []

# 1. Cover
pages.append(page(f"""
<div class="cover">
  <div class="badge">제8회 교육 공공데이터 AI 활용대회 · 일반부</div>
  <h1>알리미+ <span style="color:#2563eb">(Alrimi+)</span></h1>
  <div class="sub" style="margin-top:18px">학교 공공데이터를 <span style="color:#2563eb">출처와 함께</span> 답하는 AI</div>
  <div class="desc" style="margin-top:14px;max-width:820px">모든 학부모를 위한 학교 급식·학사정보 챗봇 — 알레르기 맞춤 안내 · 한국어/영어 지원</div>
  <div style="margin-top:40px">
    <span class="pill">팀명 · 소크라테스의 식판</span>
    <span class="pill">데모 · alrimi-plus.vercel.app</span>
  </div>
</div>""", 1))

# 2. Problem
pages.append(page("""
<div class="kicker">PROBLEM</div><div class="bar"></div>
<h2>정보는 NEIS에 있다.<br>그런데 학부모는 못 찾는다.</h2>
<ul style="margin-top:10px">
  <li>급식·학사일정·공지를 보려면 앱·홈페이지·급식표를 매번 오가야 한다.</li>
  <li>정보가 단편적이고, 한국어로만 제공돼 다문화 가정엔 장벽이 크다.</li>
  <li><span class="hl">특히 알레르기 자녀를 둔 가정</span>엔, 같은 확인이 <b>매일의 안전 점검 노동</b>이 된다.</li>
</ul>""", 2))

# 3. Data insight (chart2)
pages.append(page(f"""
<div class="kicker">DATA</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <div class="big">100%</div>
    <div class="sub" style="margin-top:14px">우유+밀 알레르기 아동이<br><span class="hl">경고가 필요한 급식</span>의 비율</div>
    <div class="desc" style="margin-top:18px">시범 10개교 급식 <b>223끼</b>를 NEIS 알레르기코드(19종)로 분석.<br>모든 급식에 알레르기 유발 식품이 1종 이상 포함 — 알레르기 가정은 사실상 <b>매 끼니를 확인</b>해야 한다.</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CH2']}"></div>
</div>""", 3))

# 4. Solution (landing)
pages.append(page(f"""
<div class="kicker">SOLUTION</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>학교 고르고, 물어보면,<br>출처와 함께 답한다</h2>
    <div class="steps">
      <div class="step"><b>STEP 1</b>우리 학교 선택</div>
      <div class="step"><b>STEP 2</b>자연어로 질문</div>
      <div class="step"><b>STEP 3</b>출처 포함 답변</div>
    </div>
    <div class="desc" style="margin-top:22px">표를 뒤지는 게 아니라, 대화 한 줄로. 답마다 근거(출처)가 붙는다.</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CAP1']}" style="max-height:470px"></div>
</div>""", 4))

# 5. Differentiation
pages.append(page("""
<div class="kicker">WHY DIFFERENT</div><div class="bar"></div>
<h2>기존 급식 앱과 무엇이 다른가</h2>
<div class="grid5">
  <div class="gcard"><div class="n">01</div><div class="t">학교 인식</div><div class="d">학교별로 데이터를 분리해 검색. 범용 챗봇 아님</div></div>
  <div class="gcard"><div class="n">02</div><div class="t">출처 인용</div><div class="d">답마다 [1][2] 근거 표기 → 환각 방지·신뢰</div></div>
  <div class="gcard"><div class="n">03</div><div class="t">날짜 인식</div><div class="d">"오늘·이번 주" 급식을 날짜로 정확히 (한·영)</div></div>
  <div class="gcard"><div class="n">04</div><div class="t">개인화 알레르기</div><div class="d">내 아이 기준으로 위험 메뉴만 강조</div></div>
  <div class="gcard"><div class="n">05</div><div class="t">다국어</div><div class="d">영어로 물으면 영어로 답 (다문화)</div></div>
</div>
<div class="desc" style="margin-top:34px">데이터를 <b>'보여주는'</b> 앱을 넘어 — 묻고, 내 아이 기준으로 해석하고, 근거를 보여주는 <span style="color:#2563eb;font-weight:700">AI</span>.</div>""", 5))

# 6. Source citation (cap3)
pages.append(page(f"""
<div class="kicker">TRUST</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>지어내지 않습니다.<br>출처를 함께.</h2>
    <ul>
      <li>모든 답변에 사용한 자료의 <b>출처([1][2])</b>와 원문을 표시.</li>
      <li>자료에 없으면 <b>"모른다"</b>고 정직하게 답한다.</li>
      <li>AI 환각 불신을 해소 — 공공 서비스의 신뢰 기반.</li>
    </ul>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CAP3']}" style="max-height:470px"></div>
</div>""", 6))

# 7. Personalized allergy (cap2)
pages.append(page(f"""
<div class="kicker">SAFETY</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>우리 아이 기준으로<br>경고합니다</h2>
    <ul>
      <li>알레르기 19종 등록 — <b>이 기기에만 저장</b>(서버 미저장, 안전).</li>
      <li>급식에서 겹치는 항목만 <span class="hl">⚠️ 내 아이 주의 항목</span>으로 강조.</li>
      <li>안전 기능이라 LLM 추측이 아닌 <b>코드 교차계산</b>으로 정확도 보장.</li>
    </ul>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CAP2']}" style="max-height:470px"></div>
</div>""", 7))

# 8. Multilingual (cap4)
pages.append(page(f"""
<div class="kicker">ACCESS</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>영어로 물으면,<br>영어로 답합니다</h2>
    <ul>
      <li>초·중등 <b>다문화 학생 20만 명(전체의 4.0%)</b>*.</li>
      <li>한·영 모두 날짜 인식·알레르기·출처 그대로 지원.</li>
      <li>다문화 가정의 학교 정보 접근성을 높인다.</li>
    </ul>
    <div class="desc" style="margin-top:18px">* 한국교육개발원 2025 교육기본통계</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CAP4']}" style="max-height:470px"></div>
</div>""", 8))

# 9. Architecture
pages.append(page(f"""
<div class="kicker">HOW IT WORKS</div><div class="bar"></div>
<h2>시스템 아키텍처</h2>
<div style="display:flex;justify-content:center;margin-top:6px"><img src="{IMG['ARCH']}" style="max-height:430px;max-width:96%"></div>
<div class="desc" style="text-align:center;margin-top:14px">Next.js(Vercel) · FastAPI(Hugging Face) · Supabase(pgvector) · Voyage AI 임베딩 · Anthropic Claude</div>""", 9))

# 10. Public data
pages.append(page(f"""
<div class="kicker">PUBLIC DATA</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>교육 공공데이터(NEIS) 활용</h2>
    <ul>
      <li>NEIS <b>급식식단정보</b>(메뉴·열량·영양 + 알레르기 19종) · <b>학사일정</b>.</li>
      <li>시범 10개교(초4·중3·고3, 6개 시도) 약 490개 청크 적재.</li>
      <li>pgvector 의미검색 + 날짜 직접조회 <b>하이브리드</b>로 정확도 확보.</li>
    </ul>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CH1']}"></div>
</div>""", 10))

# 11. Verification
pages.append(page("""
<div class="kicker">QUALITY</div><div class="bar"></div>
<h2>데모만이 아니라, 검증된 서비스</h2>
<ul style="margin-top:6px">
  <li><b>골든 질문 12종</b> — 로컬 12/12 + <b>라이브(배포 환경) 12/12</b> 통과.<br><span class="desc">급식·날짜·알레르기·학사일정 정확 / 주제이탈·프롬프트 인젝션 거절 / 타 학교 / 영어</span></li>
  <li><b>독립 AI 코드 리뷰</b> → 결함 수정 → 라이브 재검증 (타임존·레이트리밋·동시접속 등).</li>
  <li><b>안전장치</b> — 출처 인용(환각 방지) · 주제 가드 + 인젝션 사전차단 · 호출 제한 · 면책 고지.</li>
</ul>
<div class="desc" style="margin-top:26px">→ 운영 리스크까지 점검된, <b style="color:#2563eb">실제 배포된</b> 풀스택 서비스.</div>""", 11))

# 12. Impact + roadmap
pages.append(page("""
<div class="kicker">IMPACT & ROADMAP</div><div class="bar"></div>
<h2>기대 효과 & 확장</h2>
<ul>
  <li><b>정보 접근시간 단축</b> · <b>알레르기 안전</b> · <b>다문화 접근성</b> · <b>출처로 신뢰</b></li>
</ul>
<div class="rm">
  <div><b>현재 (MVP)</b><br>NEIS 급식·학사 / 10개교 / 출처·개인화알레르기·다국어·날짜검색</div>
  <div><b>단기</b><br>학교알리미 공시정보 / 학교 수 확장</div>
  <div><b>중기</b><br>홈페이지 공지 크롤러 / 자동 갱신 / 피드백</div>
  <div><b>장기</b><br>전국 확대 / 모바일 앱 / 교사용</div>
</div>
<div class="desc" style="margin-top:26px">현재는 NEIS 기반 시범 10개교 — 전국 통합이 아닌, 확장 가능한 구조의 <b>검증된 MVP</b>.</div>""", 12))

# 13. Closing
pages.append(page("""
<div class="cover" style="align-items:flex-start">
  <div class="kicker">알리미+ (Alrimi+)</div>
  <h1 style="margin-top:8px">학교 공공데이터가,<br>진짜 <span style="color:#2563eb">답하는</span> 시대.</h1>
  <div class="desc" style="margin-top:26px;font-size:22px">지금 바로 써보세요 — 학교를 고르고, 물어보세요.</div>
  <div style="margin-top:30px"><span class="pill" style="font-size:20px;padding:10px 22px">alrimi-plus.vercel.app</span></div>
  <div class="desc" style="margin-top:24px">추천 질문 · "오늘 급식 뭐 나와?" / "이번 주 학사일정" / "What's on the lunch menu today?"</div>
</div>""", 13))

html = f"<!doctype html><html><head><meta charset='utf-8'><style>@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css');{CSS}</style></head><body>{''.join(pages)}</body></html>"

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page_ = browser.new_page()
    page_.goto("file:///" + OUT_HTML.replace("\\", "/"), wait_until="networkidle")
    page_.evaluate("document.fonts.ready")
    page_.wait_for_timeout(1800)
    page_.pdf(path=OUT_PDF, width="1280px", height="720px", print_background=True,
              margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    browser.close()

print("PDF:", OUT_PDF)
print("size:", round(os.path.getsize(OUT_PDF) / 1024 / 1024, 2), "MB")
