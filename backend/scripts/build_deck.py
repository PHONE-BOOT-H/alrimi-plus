"""출품작 제안서 PDF 생성 (HTML→Playwright PDF). python -m scripts.build_deck

밀도 높은 15쪽 제안서. QR(라이브 데모) 포함. 식별정보 미기재(팀명·vercel URL만).
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


IMG = {k: b64(v) for k, v in {
    "SOL": "캡처_솔루션답변.png", "CAP2": "캡처2_개인화알레르기.png", "CAP3": "캡처3_출처.png",
    "CAP4": "캡처4_영어답변.png", "CH1": "차트1_알레르기_출현빈도.png", "CH2": "차트2_프로필별_경고비율.png",
    "ARCH": "아키텍처_다이어그램.png", "QR": "_qr.png",
}.items()}

CSS = """
@page { size:1280px 720px; margin:0; }
* { margin:0; padding:0; box-sizing:border-box; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
body { font-family:'Pretendard','Malgun Gothic',sans-serif; color:#0f172a; }
.page { width:1280px; height:720px; padding:46px 58px; position:relative; page-break-after:always; background:#fff; overflow:hidden; }
.page:last-child { page-break-after:auto; }
.kicker { color:#2563eb; font-weight:800; font-size:15px; letter-spacing:2px; }
.bar { height:6px; width:48px; background:#2563eb; border-radius:4px; margin:8px 0 14px; }
h1 { font-size:54px; font-weight:800; line-height:1.1; letter-spacing:-1px; }
h2 { font-size:33px; font-weight:800; line-height:1.18; margin-bottom:12px; letter-spacing:-1px; }
.sub { font-size:22px; color:#334155; font-weight:600; }
.desc { font-size:16px; color:#64748b; line-height:1.55; }
.big { font-size:120px; font-weight:800; color:#dc2626; line-height:.95; letter-spacing:-3px; }
.hl { color:#dc2626; } .blue { color:#2563eb; } .grn { color:#16a34a; }
ul { list-style:none; } li { font-size:17px; line-height:1.55; padding-left:24px; position:relative; color:#1e293b; margin-bottom:5px; }
li:before { content:"›"; position:absolute; left:3px; color:#2563eb; font-weight:800; }
.foot { position:absolute; bottom:20px; left:58px; right:58px; display:flex; justify-content:space-between; font-size:11px; color:#94a3b8; }
.shot { border:1px solid #e2e8f0; border-radius:11px; box-shadow:0 8px 26px rgba(15,23,42,.12); }
.two { display:flex; gap:34px; align-items:center; height:548px; }
.two .txt { flex:1.12; } .two .vis { flex:.88; display:flex; justify-content:center; align-items:center; height:100%; }
.two .vis img { max-height:528px; max-width:100%; }
.ex { background:#f8fafc; border:1px solid #e8edf3; border-radius:9px; padding:10px 14px; font-size:12.5px; line-height:1.6; color:#475569; } .ex b { color:#0f172a; }
.cover { height:100%; display:flex; flex-direction:column; justify-content:center; }
.badge { display:inline-block; border:1px solid #cbd5e1; border-radius:999px; padding:6px 14px; font-size:13px; color:#475569; margin-bottom:20px; width:fit-content; }
.pill { display:inline-block; background:#eff6ff; color:#2563eb; border-radius:999px; padding:6px 14px; font-size:14px; font-weight:700; margin:3px 6px 3px 0; }
.b { display:inline-block; background:#0f172a; color:#fff; border-radius:7px; padding:6px 11px; font-size:12px; font-weight:700; margin:3px 5px 3px 0; }
table.t { width:100%; border-collapse:collapse; font-size:15px; }
table.t th { background:#0f172a; color:#fff; padding:8px 11px; text-align:left; font-size:13.5px; }
table.t td { padding:7px 11px; border-bottom:1px solid #eef2f7; }
table.t td.k { color:#475569; font-weight:700; }
.t .yes { color:#16a34a; font-weight:800; } .t .no { color:#cbd5e1; } .t .star { color:#2563eb; font-weight:800; }
.box { background:#f8fafc; border:1px solid #e8edf3; border-left:4px solid #2563eb; border-radius:8px; padding:11px 15px; font-size:13.5px; color:#475569; line-height:1.5; }
.callout { background:#eff6ff; border-radius:9px; padding:9px 13px; font-size:15px; margin-bottom:8px; color:#1e3a8a; } .callout b { color:#2563eb; }
.flow .s { display:flex; gap:10px; margin-bottom:7px; align-items:flex-start; font-size:15.5px; line-height:1.4; }
.flow .num { background:#2563eb; color:#fff; border-radius:6px; min-width:24px; height:24px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:13px; flex-shrink:0; }
.grid3 { display:flex; gap:12px; } .gcard { flex:1; background:#f8fafc; border:1px solid #e8edf3; border-radius:12px; padding:14px; } .gcard .t2 { font-weight:800; font-size:17px; margin-bottom:5px; } .gcard .d { font-size:13.5px; color:#64748b; line-height:1.5; }
.eq { background:#fff7ed; border:1px solid #fed7aa; border-radius:11px; padding:15px 18px; font-size:17px; line-height:1.65; } .eq .op { color:#ea580c; font-weight:800; }
.steps { display:flex; gap:11px; } .step { flex:1; background:#f8fafc; border-radius:11px; padding:12px; font-size:14px; } .step b { display:block; color:#2563eb; font-size:12px; margin-bottom:4px; }
.jr { font-size:14.5px; line-height:1.45; } .jr .old { background:#fef2f2; border-radius:8px; padding:10px 13px; color:#991b1b; margin-bottom:8px; } .jr .new { background:#ecfdf5; border-radius:8px; padding:10px 13px; color:#065f46; }
.rm { display:flex; gap:11px; } .rm div { flex:1; background:#f8fafc; border:1px solid #e8edf3; border-radius:10px; padding:11px; font-size:13px; line-height:1.4; } .rm b { color:#0f172a; }
.statrow { display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; } .stat { background:#f1f5f9; border-radius:8px; padding:7px 11px; font-size:14px; font-weight:700; color:#0f172a; } .stat span { color:#dc2626; }
.qrbox { display:flex; align-items:center; gap:14px; margin-top:10px; } .qrbox img { width:104px; height:104px; border:1px solid #e2e8f0; border-radius:8px; padding:5px; background:#fff; }
"""


def foot(n):
    return f'<div class="foot"><span>알리미+ (Alrimi+) · 학교 공공데이터 AI · 팀명 소크라테스의 식판</span><span>{n} / 15</span></div>'


def pg(inner, n):
    return f'<div class="page">{inner}{foot(n)}</div>'


P = []

P.append(pg(f"""
<div class="cover">
  <div class="badge">제8회 교육 공공데이터 AI 활용대회 · 일반부</div>
  <h1>알리미+ <span class="blue">(Alrimi+)</span></h1>
  <div class="sub" style="margin-top:14px">학교 공공데이터를 <span class="blue">출처와 함께</span> 답하는 AI</div>
  <div class="desc" style="margin-top:10px;max-width:780px">모든 학부모를 위한 학교 급식·학사정보 챗봇 — 알레르기 맞춤 안내 · 한국어/영어 지원</div>
  <div style="margin-top:22px">
    <span class="b">LIVE 배포 완료</span><span class="b">NEIS 10개교·490청크</span><span class="b">출처 인용 RAG</span><span class="b">알레르기 코드 교차계산</span><span class="b">라이브 검증 12/12</span>
  </div>
  <div class="qrbox"><img src="{IMG['QR']}"><div><div class="pill" style="font-size:16px;padding:8px 16px">alrimi-plus.vercel.app</div><div class="desc" style="margin-top:6px">QR 스캔 → 지금 바로 사용 가능</div></div></div>
</div>""", 1))

P.append(pg(f"""
<div class="kicker">DATA & AI</div><div class="bar"></div>
<h2>활용 데이터와 AI 처리 흐름</h2>
<table class="t">
  <tr><td class="k" style="width:22%">활용 공공데이터</td><td>NEIS 급식식단정보 · NEIS 학사일정 (교육부 나이스 개방포털)</td></tr>
  <tr><td class="k">주요 필드</td><td>학교 · 날짜 · 메뉴 · 열량/영양 · <b>알레르기 코드(1~19)</b> · 행사명</td></tr>
  <tr><td class="k">활용 범위</td><td>시범 10개교(초4·중3·고3, 6개 시도) · 급식 223끼 · 약 490개 검색 청크</td></tr>
  <tr><td class="k">AI 활용</td><td>Voyage 임베딩(1024차원) → pgvector 학교별 의미검색 → Claude(Haiku/Sonnet) 답변 생성 → 출처 인용</td></tr>
  <tr><td class="k">비(非)AI 안전로직</td><td>날짜 직접조회 · <b>사용자 알레르기 ∩ NEIS 알레르기 코드 = 경고</b> (코드 계산)</td></tr>
  <tr><td class="k">산출물</td><td>학교별 질의응답 · 출처 원문 · 알레르기 맞춤 경고 · 한/영 응답</td></tr>
  <tr><td class="k">개인정보</td><td>알레르기 설정 localStorage(기기 저장) · 서버 미저장 · 학생 개인정보 미수집</td></tr>
</table>
<div class="box" style="margin-top:11px">데이터 파이프라인 · 수집 → 정규화 → 청킹 → 학교별 메타데이터 → (검색 / 날짜 직접조회). 생성형 AI는 <b>출처 기반 답변 생성</b>에만, 안전 기능(알레르기)은 <b>코드 교차계산</b>으로 분리.</div>""", 2))

P.append(pg("""
<div class="kicker">PROBLEM</div><div class="bar"></div>
<h2>정보는 NEIS에 있다. 그런데 학부모는 못 찾는다.</h2>
<div class="jr">
  <div class="old"><b>기존</b> · 앱/홈페이지 접속 → 학교 선택 → 급식표 → 알레르기 번호(1~19) 해석 → 우리 아이 항목 대조 <b>(여러 단계, 매일 반복)</b></div>
  <div class="new"><b>알리미+</b> · 학교 선택 → "오늘 급식 뭐 나와?" → 메뉴 + 출처 + <b>내 아이 주의 항목</b> (한 줄)</div>
</div>
<div class="grid3" style="margin-top:14px">
  <div class="gcard"><div class="t2">일반 학부모</div><div class="d">급식·학사일정·공지를 여러 출처 오가며 확인 — 번거로움</div></div>
  <div class="gcard"><div class="t2">알레르기 가정</div><div class="d">매일 급식표의 알레르기 번호를 직접 해독 — <b>안전 확인 노동</b></div></div>
  <div class="gcard"><div class="t2">다문화 가정</div><div class="d">한국어 정보 장벽 — 자녀 학교생활 파악 어려움 (학생 20만명)</div></div>
</div>
<div class="callout" style="margin-top:13px"><b>→</b> 같은 공공데이터인데, 누구에게는 단순 불편, 누구에게는 매일의 부담.</div>
<div style="margin-top:16px;display:flex;align-items:center;gap:9px">
  <div style="font-size:13px;color:#94a3b8;font-weight:800;min-width:54px">현재</div>
  <div class="stat" style="background:#f1f5f9">NEIS·교육청 앱</div><div class="stat" style="background:#f1f5f9">학교 홈페이지</div><div class="stat" style="background:#f1f5f9">가정통신문</div><div class="stat" style="background:#f1f5f9">급식표(번호 1~19)</div>
  <div style="color:#cbd5e1;font-weight:800;font-size:20px">→</div>
  <div class="stat" style="background:#eff6ff;color:#2563eb;border:1px solid #bfdbfe">알리미+ 하나로</div>
</div>""", 3))

P.append(pg(f"""
<div class="kicker">DATA INSIGHT</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <div class="big">100%</div>
    <div class="sub" style="margin-top:8px">시범 10개교 223끼 기준,<br>우유+밀 알레르기 아동은 <span class="hl">모든 급식에 경고 필요</span></div>
    <div class="statrow">
      <div class="stat">밀 <span>100%</span></div><div class="stat">대두 <span>99.6%</span></div><div class="stat">새우 <span>97.8%</span></div><div class="stat">우유 <span>85.2%</span></div><div class="stat">난류 <span>77.1%</span></div>
    </div>
    <div class="box" style="margin-top:12px">분석 방법 · NEIS 메뉴별 알레르기 코드(1~19) 수집 → 날짜별 급식 단위 통합 → 사용자 프로필과 교차계산<br>한계 · 시범 10개교 표본(전국 일반화 아님), MVP 검증용 분석</div>
    <div style="margin-top:10px;font-size:13.5px;color:#475569;line-height:1.55"><b style="color:#0f172a">조합 분석</b> · 우유 단독 85.2% · 난류+우유 95.1% · 견과류(땅콩·호두) 4.9%(드물지만 치명적) → 흔한 알레르기일수록 회피 노동↑</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CH2']}"></div>
</div>""", 4))

P.append(pg(f"""
<div class="kicker">SOLUTION</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>학교 고르고, 물어보면,<br>출처와 함께 답한다</h2>
    <div class="steps"><div class="step"><b>STEP 1</b>우리 학교 선택</div><div class="step"><b>STEP 2</b>자연어 질문</div><div class="step"><b>STEP 3</b>출처·경고 포함 답변</div></div>
    <div style="margin-top:14px;font-size:14.5px;color:#475569;line-height:1.6"><b style="color:#0f172a">답변 구성</b> · 메뉴/영양 · 알레르기 유발 식품 · <b>내 아이 주의 항목</b> · 출처 [1][2] 원문 · (한/영)</div>
    <div class="callout" style="margin-top:13px"><b>→</b> 표를 뒤지는 게 아니라 대화 한 줄로. 답마다 근거(출처)가 붙는다.</div>
    <div class="ex" style="margin-top:12px"><b>실제 질의 예시</b><br>"오늘 급식 뭐 나와?" → 메뉴·영양 + ⚠️ 주의 항목 + 출처[1]<br>"이번 주 학사일정?" → 날짜별 행사 목록 + 출처<br>"파이썬 코드 짜줘" → "학교 정보에 대해서만 답해드려요" (악용 차단)</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['SOL']}"></div>
</div>""", 5))

P.append(pg("""
<div class="kicker">WHY DIFFERENT</div><div class="bar"></div>
<h2>기존 급식 앱과 무엇이 다른가</h2>
<table class="t">
  <tr><th>기능</th><th>일반 급식앱 / NEIS</th><th>일반 챗봇</th><th>알리미+</th></tr>
  <tr><td class="k">학교별 공공데이터</td><td>있음</td><td class="no">불안정</td><td class="star">있음</td></tr>
  <tr><td class="k">자연어 질문</td><td class="no">약함</td><td>있음</td><td class="star">있음</td></tr>
  <tr><td class="k">출처 인용(근거 제시)</td><td class="no">약함</td><td class="no">약함</td><td class="star">답변마다 표시</td></tr>
  <tr><td class="k">날짜 직접조회</td><td>제한적</td><td class="no">자주 틀림</td><td class="star">하이브리드 조회</td></tr>
  <tr><td class="k">개인 알레르기 경고</td><td>수동 확인</td><td class="no">추측 위험</td><td class="star">코드 교차계산</td></tr>
  <tr><td class="k">영어 응답(출처 유지)</td><td class="no">제한적</td><td>출처 약함</td><td class="star">출처 유지</td></tr>
</table>
<div class="callout" style="margin-top:13px"><b>핵심</b> · 데이터를 '보여주는' 앱이 아니라, 공공데이터를 <b>사용자 상황에 맞게 해석</b>하는 AI. 새 기술이 아니라 <b>문제 재정의</b>가 차별점.</div>
<div class="grid3" style="margin-top:15px">
  <div class="gcard"><div class="t2" style="color:#2563eb">출처 인용</div><div class="d">답변마다 [1][2] + 하단 원문 카드. 근거 없는 문장은 생성하지 않음 → 환각 방지.</div></div>
  <div class="gcard"><div class="t2" style="color:#2563eb">코드 기반 알레르기</div><div class="d">LLM 추측이 아닌 집합 교차계산. 안전 기능은 결정론적으로 동작.</div></div>
  <div class="gcard"><div class="t2" style="color:#2563eb">하이브리드 날짜검색</div><div class="d">의미검색 + 날짜 직접조회 병합 → "오늘/이번주 급식"을 정확히.</div></div>
</div>""", 6))

P.append(pg(f"""
<div class="kicker">TRUST</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>지어내지 않습니다.<br>출처를 함께.</h2>
    <div class="callout"><b>여기 →</b> 답변 본문 속 <b>[1] [2]</b> 근거 표기</div>
    <div class="callout"><b>여기 →</b> 하단 <b>출처 원문</b> 카드(날짜·유형)</div>
    <div class="callout"><b>정책 →</b> 검색 결과 없으면 <b>"모른다"</b>고 답</div>
    <ul style="margin-top:10px">
      <li>출처 카드에 <b>날짜·데이터 유형</b> 표기 → 원본 추적 가능</li>
      <li>여러 항목은 <b>[1] [2]로 분리</b>해 각각 인용</li>
    </ul>
    <div class="box" style="margin-top:11px">RAG 설계 원칙 · 검색된 공공데이터 청크에 <b>근거가 있는 문장만</b> 생성. 환각 방지 + AI 불신 해소.</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CAP3']}" style="max-height:516px"></div>
</div>""", 7))

P.append(pg(f"""
<div class="kicker">SAFETY</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>우리 아이 기준으로<br>경고합니다</h2>
    <div class="eq">사용자 설정 <b>{{우유, 밀}}</b><br><span class="op">∩</span> NEIS 메뉴 코드 <b>{{우유, 대두, 밀, 새우}}</b><br><span class="op">=</span> <span class="hl">⚠️ 주의: 우유, 밀</span></div>
    <ul style="margin-top:12px">
      <li>안전 기능은 <b>LLM 추측 금지 → 코드 교차계산</b> (오답=위험)</li>
      <li>알레르기 설정은 <b>이 기기에만 저장</b>(서버 미저장)</li>
      <li>알레르기 19종 + 등록 외 포함 식품도 함께 안내</li>
    </ul>
    <div class="box" style="margin-top:11px;border-left-color:#ea580c;background:#fff7ed;border-color:#fed7aa;color:#9a3412;font-size:12px;line-height:1.5">NEIS 알레르기 19종 — 난류1·우유2·메밀3·땅콩4·대두5·밀6·고등어7·게8·새우9·돼지고기10·복숭아11·토마토12·아황산류13·호두14·닭고기15·쇠고기16·오징어17·조개18·잣19</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CAP2']}" style="max-height:516px"></div>
</div>""", 8))

P.append(pg(f"""
<div class="kicker">ACCESS</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>영어 질문에도 NEIS 근거와<br>날짜 정확도를 유지</h2>
    <ul>
      <li>영어 질문 → 한국어 NEIS 검색 → <b>영어 답변</b> 생성</li>
      <li>메뉴명·알레르기·<b>출처</b>를 그대로 유지</li>
      <li>"today / this week / tomorrow" 등 <b>영어 날짜도 인식</b></li>
      <li>다문화 학생 <b>20만 명(전체 4.0%)</b>* 의 정보 접근성</li>
    </ul>
    <div class="ex" style="margin-top:11px">Q. "What's on the lunch menu today?"<br>A. "Today's lunch includes ... Allergens: milk, soy, wheat, shrimp ... [1]"</div>
    <div class="desc" style="margin-top:9px">* 한국교육개발원 2025 교육기본통계</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CAP4']}" style="max-height:516px"></div>
</div>""", 9))

P.append(pg(f"""
<div class="kicker">HOW IT WORKS</div><div class="bar"></div>
<h2>처리 흐름 — 운영 가능한 RAG 시스템</h2>
<div style="display:flex;gap:30px">
  <div class="flow" style="flex:1.05">
    <div class="s"><span class="num">1</span>학교 선택값으로 검색 범위 제한</div>
    <div class="s"><span class="num">2</span>질문 언어·의도·날짜 표현 파악(오늘/이번주/특정일, 한·영)</div>
    <div class="s"><span class="num">3</span>급식+날짜면 NEIS <b>날짜 직접조회</b> 병합</div>
    <div class="s"><span class="num">4</span>pgvector <b>의미검색</b>으로 관련 문서</div>
    <div class="s"><span class="num">5</span>Claude가 <b>출처 기반</b> 답변 생성·스트리밍</div>
    <div class="s"><span class="num">6</span>알레르기 경고는 <b>코드 교차계산</b>으로 삽입</div>
    <div class="s"><span class="num">7</span>주제이탈·프롬프트 인젝션 차단 · 호출 제한</div>
  </div>
  <div style="flex:1;display:flex;align-items:center"><img src="{IMG['ARCH']}" style="max-width:100%;max-height:340px"></div>
</div>
<div class="desc" style="margin-top:2px;margin-bottom:11px">Next.js(Vercel) · FastAPI(Hugging Face) · Supabase(pgvector) · Voyage 임베딩 · Anthropic Claude</div>
<div class="grid3">
  <div class="gcard"><div class="t2" style="font-size:16px">호출 안전</div><div class="d">IP·전역 레이트리밋 + 일일 캡으로 비용·남용 방어</div></div>
  <div class="gcard"><div class="t2" style="font-size:16px">주제·인젝션 가드</div><div class="d">학교 무관 질문·프롬프트 인젝션 사전 차단(키 도용 방지)</div></div>
  <div class="gcard"><div class="t2" style="font-size:16px">모델 라우팅</div><div class="d">기본 Haiku 4.5, 복잡 질문만 Sonnet 4.6 → 품질·비용 균형</div></div>
</div>""", 10))

P.append(pg("""
<div class="kicker">VERIFICATION</div><div class="bar"></div>
<h2>라이브 환경 12/12 — 데모가 아니라 동작하는 서비스</h2>
<div style="display:flex;gap:24px">
  <table class="t" style="flex:1.1">
    <tr><th>테스트</th><th>로컬</th><th>라이브</th></tr>
    <tr><td>오늘/특정일 급식</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
    <tr><td>출처 [1][2]·원문 표시</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
    <tr><td>우유+밀 알레르기 경고</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
    <tr><td>이번 주 학사일정</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
    <tr><td>타 학교 데이터 혼입 방지</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
    <tr><td>영어 질문→영어 답변</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
    <tr><td>주제이탈·인젝션 거절</td><td class="yes">PASS</td><td class="yes">PASS</td></tr>
  </table>
  <table class="t" style="flex:1">
    <tr><th>발견 결함</th><th>수정</th><th>재검증</th></tr>
    <tr><td>타임존(날짜 오답)</td><td>KST 처리</td><td class="yes">PASS</td></tr>
    <tr><td>레이트리밋 우회</td><td>IP/전역 제한</td><td class="yes">PASS</td></tr>
    <tr><td>동시접속 블로킹</td><td>비동기 보완</td><td class="yes">PASS</td></tr>
    <tr><td>프롬프트 인젝션</td><td>사전 차단</td><td class="yes">PASS</td></tr>
    <tr><td>영어 날짜 미인식</td><td>다국어 파서</td><td class="yes">PASS</td></tr>
  </table>
</div>
<div class="callout" style="margin-top:12px">골든 질문 12종 · <b>로컬 12/12 + 라이브 12/12</b> · 독립 AI 코드리뷰로 결함 발견→수정→재검증</div>""", 11))

P.append(pg(f"""
<div class="kicker">PUBLIC DATA</div><div class="bar"></div>
<div class="two">
  <div class="txt">
    <h2>공공데이터를 '조회'가 아니라<br>'판단'으로 전환</h2>
    <ul>
      <li>NEIS 급식식단정보: 일자별 메뉴·열량·영양 + <b>요리별 알레르기 코드 19종</b></li>
      <li>NEIS 학사일정: 날짜·행사명</li>
      <li>학교·교육청 코드로 <b>학교별 분리</b> 적재 → 타 학교 혼입 방지</li>
      <li>처리: 정규화 → 청킹 → 메타데이터 → 검색/날짜 직접조회</li>
      <li>같은 데이터로 "오늘 메뉴"를 넘어 <b>"내 아이가 조심할 항목"</b>으로</li>
    </ul>
    <div class="statrow" style="margin-top:10px"><div class="stat">시범 10개교</div><div class="stat">초4·중3·고3</div><div class="stat">6개 시도</div><div class="stat">급식 223끼</div><div class="stat">약 490 청크</div></div>
    <div class="box" style="margin-top:10px">차트 · 시범 10개교 급식에서 알레르기 유발 식품 출현 빈도. 흔한 알레르기일수록 회피 부담이 큼을 정량화.</div>
  </div>
  <div class="vis"><img class="shot" src="{IMG['CH1']}"></div>
</div>""", 12))

P.append(pg("""
<div class="kicker">USABILITY</div><div class="bar"></div>
<h2>누가, 어떻게 더 빨라지는가</h2>
<table class="t">
  <tr><th>과제</th><th>기존 방식</th><th>알리미+</th></tr>
  <tr><td class="k">오늘 급식 + 우리 아이 알레르기 확인</td><td>앱 열고 메뉴별 번호(1~19) 해석·대조 (여러 단계)</td><td class="star">한 번 질문 → 주의 항목 자동 강조</td></tr>
  <tr><td class="k">이번 주 학사일정 확인</td><td>학교 홈페이지·가정통신문 탐색</td><td class="star">"이번 주 학사일정" 한 줄</td></tr>
  <tr><td class="k">다문화 보호자의 급식 확인</td><td>한국어만 → 어려움</td><td class="star">영어로 질문·답변</td></tr>
  <tr><td class="k">특정 식이 항목(예: 돼지고기) 확인</td><td>메뉴를 하나씩 확인</td><td class="star">질문으로 해당 항목만 추출</td></tr>
</table>
<div class="box" style="margin-top:13px">간이 사용성 테스트(n=3~5) 계획 · 과제별 <b>소요시간 · 성공률 · 신뢰도(5점)</b>를 기존 방식과 비교 측정 → 발표 자료에 반영.</div>
<div class="grid3" style="margin-top:15px">
  <div class="gcard"><div class="t2">확인 시간 단축</div><div class="d">여러 출처를 오가던 확인을 <b>대화 한 줄</b>로</div></div>
  <div class="gcard"><div class="t2">안전 확인 노동 ↓</div><div class="d">매일 급식표 번호 해독을 <b>자동 경고</b>로 대체</div></div>
  <div class="gcard"><div class="t2">다문화 접근성</div><div class="d">한국어 장벽 없이 <b>영어로</b> 학교 정보 확인</div></div>
</div>""", 13))

P.append(pg("""
<div class="kicker">ROADMAP & OPS</div><div class="bar"></div>
<h2>검증된 MVP에서 운영 서비스로</h2>
<table class="t">
  <tr><th>단계</th><th>범위</th><th>검증할 것</th></tr>
  <tr><td class="k">현재 MVP</td><td>10개교 · 급식·학사일정</td><td>RAG 정확도 · 날짜조회 · 알레르기 경고</td></tr>
  <tr><td class="k">1차 확장</td><td>학교 수 확대 · 자동 갱신</td><td>수집 안정성 · 비용 · 응답속도</td></tr>
  <tr><td class="k">2차 확장</td><td>학교알리미 공시 · 홈페이지 공지 연동</td><td>데이터 다변화 · 최신성</td></tr>
  <tr><td class="k">운영</td><td>피드백 · 오답 신고</td><td>품질 개선 루프</td></tr>
</table>
<div class="rm" style="margin-top:13px">
  <div><b>개인정보 최소화</b><br>알레르기 설정 서버 미저장</div>
  <div><b>비용 통제</b><br>주제 가드·레이트리밋·모델 라우팅</div>
  <div><b>품질 관리</b><br>골든질문 회귀 테스트·출처 없는 답변 제한</div>
</div>
<div class="callout" style="margin-top:15px"><b>→</b> 지금도 라이브로 동작하는 서비스. 확장은 '가능성'이 아니라 검증된 구조 위의 <b>다음 단계</b>.</div>""", 14))

P.append(pg(f"""
<div class="cover" style="align-items:flex-start">
  <div class="kicker">알리미+ (Alrimi+)</div>
  <h1 style="margin-top:6px">학교 공공데이터를,<br>학부모가 바로 쓸 <span class="blue">답</span>으로.</h1>
  <div class="desc" style="margin-top:16px;font-size:19px">출처 인용 RAG · 알레르기 코드 기반 경고 · 한/영 접근성 · 라이브 검증 12/12</div>
  <div class="qrbox" style="margin-top:22px"><img src="{IMG['QR']}" style="width:128px;height:128px"><div><div class="pill" style="font-size:18px;padding:9px 18px">alrimi-plus.vercel.app</div><div class="desc" style="margin-top:8px">QR 스캔 → 직접 사용 · 추천 질문: "오늘 급식 뭐 나와?" / "이번 주 학사일정" / "What's on the lunch menu today?"</div></div></div>
</div>""", 15))

html = f"<!doctype html><html><head><meta charset='utf-8'><style>@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css');{CSS}</style></head><body>{''.join(P)}</body></html>"
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

with sync_playwright() as p:
    br = p.chromium.launch(); pgg = br.new_page()
    pgg.goto("file:///" + OUT_HTML.replace("\\", "/"), wait_until="networkidle")
    pgg.evaluate("document.fonts.ready"); pgg.wait_for_timeout(1800)
    pgg.pdf(path=OUT_PDF, width="1280px", height="720px", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    br.close()
print("PDF:", round(os.path.getsize(OUT_PDF) / 1024 / 1024, 2), "MB")
