"""골든 질문을 라이브 HF 엔드포인트에 돌려 검증. python -m scripts.run_golden_live"""
from __future__ import annotations

import json
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import httpx

from scripts.run_golden import judge
from tests.golden_questions import GOLDEN

BASE = "https://HANANHAN-alrimi-plus-backend.hf.space"


def ask(q: str, code: str):
    with httpx.stream("POST", f"{BASE}/api/chat", json={"school_code": code, "question": q}, timeout=90) as r:
        ans = ""
        nsrc = 0
        err = None
        for line in r.iter_lines():
            if not line.strip():
                continue
            ev = json.loads(line)
            t = ev.get("type")
            if t == "sources":
                nsrc = len(ev["sources"])
            elif t == "delta":
                ans += ev["text"]
            elif t == "error":
                err = ev["message"]
    return ans, nsrc, err


def main():
    passed = 0
    print(f"[LIVE] 골든 {len(GOLDEN)}개 @ {BASE}\n" + "=" * 56)
    for i, (q, code, cat) in enumerate(GOLDEN, 1):
        ans, nsrc, err = ask(q, code)
        ok, note = judge(cat, ans, nsrc, err)
        passed += ok
        print(f"{'✅' if ok else '❌'} [{i}] ({cat}) {q[:34]} → {note}")
        time.sleep(1.2)
    print("=" * 56 + f"\n[LIVE] 결과: {passed}/{len(GOLDEN)} 통과")


if __name__ == "__main__":
    main()
