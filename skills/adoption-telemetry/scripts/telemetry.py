#!/usr/bin/env python3
"""Summarize weekly adoption telemetry: adoption %, trend, escalations,
hours saved.

Usage:
    python3 telemetry.py [input.json] [--md out.md]

Input JSON:
    {
      "program": "Program name",
      "hours_saved_per_user_per_week": 2.5,
      "weeks": [
        {"week": "W1", "eligible_users": 120, "active_users": 48,
         "escalations": 22}
      ]
    }

Output: Markdown summary table + totals. Hours saved per week =
active_users * hours_saved_per_user_per_week; totals sum across weeks.
"""

import argparse
import json
import sys


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def _fmt_delta(new, old, suffix="pts", invert=False):
    if old is None:
        return "—"
    d = new - old
    if invert:
        d = -d
    sign = "+" if d >= 0 else "−"
    return f"{sign}{abs(d):.1f} {suffix}".strip()


def _fmt_count_delta(new, old):
    """Raw-count change, e.g. -4 / +2. Down is good for escalations."""
    if old is None:
        return "—"
    d = new - old
    sign = "+" if d > 0 else "−" if d < 0 else "±"
    return f"{sign}{abs(d)}" if d else "±0"


def summarize(data):
    weeks = data.get("weeks", [])
    hpu = data.get("hours_saved_per_user_per_week", 0)
    rows = []
    prev_adoption = None
    prev_esc = None
    for w in weeks:
        eligible = w.get("eligible_users", 0)
        active = w.get("active_users", 0)
        esc = w.get("escalations", 0)
        adoption = (active / eligible * 100) if eligible else 0.0
        hours = active * hpu
        rows.append({
            "week": w.get("week", ""),
            "eligible": eligible,
            "active": active,
            "adoption": adoption,
            "adoption_delta": _fmt_delta(adoption, prev_adoption),
            "escalations": esc,
            "esc_delta": _fmt_count_delta(esc, prev_esc),
            "hours": hours,
        })
        prev_adoption = adoption
        prev_esc = esc
    total_hours = sum(r["hours"] for r in rows)
    total_esc = sum(r["escalations"] for r in rows)
    latest = rows[-1] if rows else None
    first = rows[0] if rows else None
    return rows, {
        "total_hours": total_hours,
        "total_escalations": total_esc,
        "latest_adoption": latest["adoption"] if latest else 0.0,
        "adoption_change": (
            latest["adoption"] - first["adoption"]
            if latest and first else 0.0
        ),
        "weeks": len(rows),
    }


def to_markdown(data, rows, totals):
    label = data.get("label", "")
    lines = [f"# Adoption Telemetry — {data.get('program', 'Untitled Program')}"]
    if label:
        lines.append("")
        lines.append(f"*{label}*")
    lines.append("")
    lines.append("| Week | Eligible | Active | Adoption | Δ vs prior wk | "
                 "Escalations | Esc Δ | Hours saved |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in rows:
        lines.append(
            "| " + " | ".join([
                r["week"], str(r["eligible"]), str(r["active"]),
                f"{r['adoption']:.1f}%", r["adoption_delta"],
                str(r["escalations"]), r["esc_delta"], f"{r['hours']:.0f}",
            ]) + " |"
        )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Weeks tracked: {totals['weeks']}")
    lines.append(
        f"- Latest adoption: {totals['latest_adoption']:.1f}% "
        f"({totals['adoption_change']:+.1f} pts since week 1)"
    )
    lines.append(f"- Total escalations: {totals['total_escalations']}")
    lines.append(
        f"- Total hours saved: {totals['total_hours']:.0f} "
        f"(at {data.get('hours_saved_per_user_per_week', 0)} hrs per "
        f"active user per week)"
    )
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Summarize adoption telemetry.")
    ap.add_argument("input", nargs="?", help="JSON input file (default: stdin)")
    ap.add_argument("--md", help="Write Markdown output to this file")
    args = ap.parse_args()

    try:
        data = load_input(args.input)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: could not read input: {e}", file=sys.stderr)
        return 2

    rows, totals = summarize(data)
    md = to_markdown(data, rows, totals)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
