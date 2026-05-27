"""급식 데이터 인사이트 분석 — 기획서 근거용.

10개 시범학교의 NEIS 급식 청크(metadata.allergy_codes)를 집계해
알레르기 출현 빈도·프로필별 경고일·학교급 차이 등 실제 숫자를 산출.
결과를 UTF-8 텍스트로 저장.
실행: python -m scripts.analyze_insights
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from app.data.neis_collector import ALLERGY_CODES
from app.db.supabase_client import get_supabase_admin

OUT = r"C:\Users\hanta\Desktop\한태영\대외활동\공모전\교육공공데이터활용대회\alrimi-plus\insight_report.txt"


def main():
    sb = get_supabase_admin()
    schools = {s["school_code"]: s for s in sb.table("schools").select("*").execute().data}
    # 급식 청크 전부 (페이지네이션 안전하게 넉넉히)
    rows = (
        sb.table("school_documents")
        .select("school_code, metadata, valid_from")
        .eq("source_type", "neis_meal")
        .limit(5000)
        .execute()
        .data
    )

    lines: list[str] = []

    def p(s=""):
        lines.append(s)

    total_meals = len(rows)
    allergen_day_count: Counter = Counter()  # 알레르기명 → 등장 급식수
    by_type_meals: Counter = Counter()  # 학교급 → 급식수
    by_type_allergen: dict = defaultdict(Counter)
    meals_with_any = 0

    # 프로필 시뮬레이션: 코드 집합
    profiles = {
        "우유": {"2"},
        "우유+밀": {"2", "6"},
        "우유+대두+밀": {"2", "5", "6"},
        "땅콩+호두(견과)": {"4", "14"},
        "난류+우유": {"1", "2"},
    }
    profile_warn = Counter()

    for r in rows:
        meta = r.get("metadata") or {}
        codes = set(meta.get("allergy_codes") or [])
        names = meta.get("allergy_names") or [ALLERGY_CODES.get(c) for c in codes]
        stype = (schools.get(r["school_code"], {}) or {}).get("school_type") or "기타"
        by_type_meals[stype] += 1
        if codes:
            meals_with_any += 1
        for nm in names:
            if nm:
                allergen_day_count[nm] += 1
                by_type_allergen[stype][nm] += 1
        for pname, pcodes in profiles.items():
            if codes & pcodes:
                profile_warn[pname] += 1

    p("=" * 60)
    p("알리미+ 급식 데이터 인사이트 리포트")
    p("=" * 60)
    p(f"분석 대상: 시범 {len(schools)}개 학교 / 급식 {total_meals}건(끼니)")
    p(f"알레르기 유발 식품이 1개 이상 포함된 급식: {meals_with_any}건 "
      f"({meals_with_any / total_meals * 100:.1f}%)" if total_meals else "급식 0건")
    p("")
    p("[1] 알레르기 유발 식품 출현 빈도 (급식 건수 기준, 상위)")
    p("-" * 60)
    for nm, c in allergen_day_count.most_common():
        pct = c / total_meals * 100 if total_meals else 0
        bar = "█" * round(pct / 4)
        p(f"  {nm:<8} {c:>4}건 ({pct:>5.1f}%) {bar}")
    p("")
    p("[2] 알레르기 프로필별 '경고 필요 급식 수' (해당 학생이 조심해야 할 끼니)")
    p("-" * 60)
    for pname, c in profile_warn.most_common():
        pct = c / total_meals * 100 if total_meals else 0
        p(f"  {pname:<14} → {c}건 / {total_meals}건 경고 필요 ({pct:.1f}%)")
    p("")
    p("[3] 학교급별 급식 수")
    p("-" * 60)
    for stype, c in by_type_meals.most_common():
        p(f"  {stype:<8} {c}건")
    p("")
    p("[4] 시범 학교 목록 (지역 다양성)")
    p("-" * 60)
    for s in schools.values():
        p(f"  {s['school_name']} | {s.get('school_type')} | {s.get('region')}")
    p("")
    p("※ 데이터: NEIS Open API 급식식단정보(일자별 메뉴+알레르기 코드 19종). 오늘 기준 ±30일 적재.")

    report = "\n".join(lines)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print(f"\n저장: {OUT}")


if __name__ == "__main__":
    main()
