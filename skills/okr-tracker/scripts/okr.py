#!/usr/bin/env python3
"""Score OKRs: % progress vs target and RAG status vs time elapsed.

Usage:
    python3 okr.py [input.json] [--md out.md]

Input JSON:
    {
      "period": "Q3 2026",
      "elapsed_pct": 50,
      "objectives": [
        {"title": "...", "owner": "...",
         "key_results": [
           {"title": "...", "baseline": 0, "current": 5, "target": 10,
            "lower_is_better": false}]}
      ]
    }

Progress = (current - baseline) / (target - baseline), clamped 0-100%.
lower_is_better flips the direction. RAG compares progress to the
expected progress for the time elapsed (10-pt tolerance, 25-pt red line).
"""

import argparse
import json
import sys

TOLERANCE = 10   # points behind expected progress before yellow
RED_LINE = 25    # points behind expected progress before red


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def progress(kr):
    base = kr.get("baseline", 0)
    cur = kr.get("current", 0)
    tgt = kr.get("target", 0)
    if tgt == base:
        return 100.0 if cur == tgt else 0.0
    if kr.get("lower_is_better"):
        pct = (base - cur) / (base - tgt) * 100
    else:
        pct = (cur - base) / (tgt - base) * 100
    return max(0.0, min(100.0, pct))


def rag(pct, elapsed):
    gap = elapsed - pct
    if gap <= TOLERANCE:
        return "🟢 On track"
    if gap <= RED_LINE:
        return "🟡 At risk"
    return "🔴 Off track"


def score(data):
    elapsed = data.get("elapsed_pct", 0)
    out = []
    for obj in data.get("objectives", []):
        krs = []
        for kr in obj.get("key_results", []):
            pct = progress(kr)
            krs.append({**kr, "pct": pct, "rag": rag(pct, elapsed)})
        avg = sum(k["pct"] for k in krs) / len(krs) if krs else 0.0
        worst = "🔴 Off track" if any(k["rag"].startswith("🔴") for k in krs) \
            else "🟡 At risk" if any(k["rag"].startswith("🟡") for k in krs) \
            else "🟢 On track"
        out.append({**obj, "key_results": krs, "score": avg, "rag": worst})
    return out


def to_markdown(data, scored):
    elapsed = data.get("elapsed_pct", 0)
    lines = [
        f"# OKR Tracker — {data.get('period', 'Untitled Period')}",
        "",
        f"**{elapsed}%** of the period elapsed. RAG compares progress "
        f"against elapsed time (10-pt tolerance, 25-pt red line).",
        "",
    ]
    for obj in scored:
        lines.append(f"## {obj.get('title', '')} — {obj['score']:.0f}% · {obj['rag']}")
        lines.append("")
        lines.append(f"Owner: {obj.get('owner', '—')}")
        lines.append("")
        lines.append("| Key result | Baseline | Current | Target | Progress | Status |")
        lines.append("| --- | ---: | ---: | ---: | ---: | --- |")
        for kr in obj["key_results"]:
            lines.append(
                "| " + " | ".join([
                    kr.get("title", ""),
                    str(kr.get("baseline", "")),
                    str(kr.get("current", "")),
                    str(kr.get("target", "")),
                    f"{kr['pct']:.0f}%",
                    kr["rag"],
                ]) + " |"
            )
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Score OKRs with RAG status.")
    ap.add_argument("input", nargs="?", help="JSON input file (default: stdin)")
    ap.add_argument("--md", help="Write Markdown output to this file")
    args = ap.parse_args()

    try:
        data = load_input(args.input)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: could not read input: {e}", file=sys.stderr)
        return 2

    md = to_markdown(data, score(data))
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
