"""인사이트 차트 생성 (기획서·영상용). python -m scripts.make_charts

급식 데이터를 집계해 2개 차트를 14_제출본에 PNG로 저장.
"""
from __future__ import annotations

import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.db.supabase_client import get_supabase_admin

# 한글 폰트 (Windows)
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

OUTDIR = r"C:\Users\hanta\Desktop\한태영\대외활동\공모전\교육공공데이터활용대회\14_제출본"
NAVY = "#1e293b"
RED = "#dc2626"


def main():
    sb = get_supabase_admin()
    rows = (
        sb.table("school_documents")
        .select("metadata")
        .eq("source_type", "neis_meal")
        .limit(5000)
        .execute()
        .data
    )
    total = len(rows)
    allergen = Counter()
    profiles = {"우유+밀": {"2", "6"}, "우유+대두+밀": {"2", "5", "6"}, "난류+우유": {"1", "2"}, "우유": {"2"}, "땅콩+호두(견과)": {"4", "14"}}
    profile_warn = Counter()
    for r in rows:
        meta = r.get("metadata") or {}
        codes = set(meta.get("allergy_codes") or [])
        for nm in meta.get("allergy_names") or []:
            allergen[nm] += 1
        for pn, pc in profiles.items():
            if codes & pc:
                profile_warn[pn] += 1

    # 차트 1: 알레르기 출현 빈도 (상위 12)
    top = allergen.most_common(12)
    names = [n for n, _ in top][::-1]
    pcts = [c / total * 100 for _, c in top][::-1]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(names, pcts, color=NAVY)
    ax.set_xlabel("급식 중 출현 비율 (%)")
    ax.set_title(f"급식 알레르기 유발 식품 출현 빈도 (시범 10개교 · 급식 {total}끼)", fontsize=12, fontweight="bold")
    ax.set_xlim(0, 105)
    for b, p in zip(bars, pcts):
        ax.text(p + 1, b.get_y() + b.get_height() / 2, f"{p:.0f}%", va="center", fontsize=9)
    fig.tight_layout()
    f1 = f"{OUTDIR}\\차트1_알레르기_출현빈도.png"
    fig.savefig(f1, dpi=150)
    plt.close(fig)

    # 차트 2: 프로필별 경고 필요 급식 비율
    items = sorted(profile_warn.items(), key=lambda x: -x[1])
    pnames = [n for n, _ in items]
    ppcts = [c / total * 100 for _, c in items]
    colors = [RED if p >= 50 else "#f59e0b" for p in ppcts]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(pnames, ppcts, color=colors)
    ax.set_ylabel("경고 필요 급식 비율 (%)")
    ax.set_title("알레르기 프로필별 '경고가 필요한 급식' 비율", fontsize=12, fontweight="bold")
    ax.set_ylim(0, 110)
    for b, p in zip(bars, ppcts):
        ax.text(b.get_x() + b.get_width() / 2, p + 2, f"{p:.0f}%", ha="center", fontsize=10, fontweight="bold")
    plt.xticks(rotation=15)
    fig.tight_layout()
    f2 = f"{OUTDIR}\\차트2_프로필별_경고비율.png"
    fig.savefig(f2, dpi=150)
    plt.close(fig)

    print("저장 완료:")
    print(" -", f1)
    print(" -", f2)


if __name__ == "__main__":
    main()
