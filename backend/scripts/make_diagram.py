"""아키텍처 다이어그램 PNG 생성. python -m scripts.make_diagram"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

OUT = r"C:\Users\hanta\Desktop\한태영\대외활동\공모전\교육공공데이터활용대회\14_제출본\아키텍처_다이어그램.png"


def box(ax, x, y, w, h, title, sub, fc, tc="white"):
    ax.add_patch(
        FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                       linewidth=0, facecolor=fc)
    )
    ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center", fontsize=11, fontweight="bold", color=tc)
    ax.text(x + w / 2, y + h * 0.27, sub, ha="center", va="center", fontsize=8.5, color=tc)


def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
                                 linewidth=1.6, color="#64748b"))


def main():
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.2)
    ax.axis("off")

    box(ax, 0.3, 2.0, 2.3, 1.2, "사용자 (브라우저)", "Next.js 14 · Vercel\n학교 선택 + 질문", "#0f172a")
    box(ax, 3.2, 2.0, 2.5, 1.2, "백엔드 API", "FastAPI · HF Spaces\n/api/chat (스트리밍)", "#2563eb")
    # 3개 데이터/AI 컴포넌트
    box(ax, 6.4, 3.5, 2.2, 1.0, "Voyage AI", "질문 임베딩\n(1024차원)", "#7c3aed")
    box(ax, 6.4, 2.05, 2.2, 1.0, "Supabase", "pgvector 유사도검색\n+ 날짜 직접조회", "#059669")
    box(ax, 6.4, 0.6, 2.2, 1.0, "Claude", "Haiku 4.5 / Sonnet 4.6\n출처인용 답변", "#ea580c")
    box(ax, 9.0, 2.05, 1.7, 1.0, "NEIS\nOpen API", "급식·학사일정", "#475569")

    arrow(ax, 2.6, 2.6, 3.2, 2.6)
    arrow(ax, 5.7, 2.75, 6.4, 4.0)   # → Voyage
    arrow(ax, 5.7, 2.6, 6.4, 2.55)   # → Supabase
    arrow(ax, 5.7, 2.45, 6.4, 1.1)   # → Claude
    arrow(ax, 9.0, 2.4, 8.6, 2.5)    # NEIS → Supabase (적재)
    # 응답 화살표(역방향)
    ax.add_patch(FancyArrowPatch((3.2, 2.35), (2.6, 2.35), arrowstyle="-|>", mutation_scale=14,
                                 linewidth=1.4, color="#94a3b8", linestyle=(0, (4, 3))))
    ax.text(2.9, 2.05, "출처+알레르기\n답변 스트리밍", ha="center", va="top", fontsize=7.5, color="#64748b")

    ax.text(5.5, 4.9, "알리미+ 시스템 아키텍처", ha="center", fontsize=14, fontweight="bold", color="#0f172a")
    ax.text(5.5, 0.2, "RAG: 학교 공공데이터(NEIS) → 임베딩·검색 → Claude가 출처 인용하며 답변",
            ha="center", fontsize=8.5, color="#64748b")

    fig.tight_layout()
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("저장:", OUT)


if __name__ == "__main__":
    main()
