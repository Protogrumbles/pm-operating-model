#!/usr/bin/env python3
"""Roll up portfolio ROI: per-initiative and portfolio-total hours saved,
gross value, net value, and ROI multiple.

Usage:
    python3 roi.py [input.json] [--md out.md]

Input JSON:
    {
      "portfolio": "Portfolio name",
      "initiatives": [
        {"name": "Support copilot rollout",
         "hours_saved_per_month": 180,
         "loaded_hourly_cost": 120,
         "ai_tool_spend_per_month": 900}
      ]
    }

Formulas (same shape as the AI Adoption ROI Calculator):
    gross $/yr = hours_saved_per_month * loaded_hourly_cost * 12
    net $/yr   = gross $/yr - ai_tool_spend_per_month * 12
    ROI        = gross $/yr / (ai_tool_spend_per_month * 12)
                 ("n/a" when spend is zero — no cost to divide by)

Rules enforced (exit code 2 with a clear error):
  - hours_saved_per_month, loaded_hourly_cost, and
    ai_tool_spend_per_month must be non-negative numbers;
    negative hours or spend are rejected
  - at least one initiative is required

With no --md flag, Markdown goes to stdout.
"""

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP

FIELDS = ("hours_saved_per_month", "loaded_hourly_cost",
          "ai_tool_spend_per_month")


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def validate(data):
    """Return a list of error strings; empty means the input is clean."""
    errors = []
    initiatives = data.get("initiatives", [])
    if not initiatives:
        errors.append("initiatives: at least one initiative is required.")
    for it in initiatives:
        name = it.get("name", "?")
        for field in FIELDS:
            v = it.get(field)
            if v is None:
                errors.append(f"{name}: missing '{field}'.")
            elif isinstance(v, bool) or not isinstance(v, (int, float)) \
                    or v < 0:
                errors.append(
                    f"{name}: '{field}' must be a non-negative number, "
                    f"got {v!r}."
                )
    return errors


def compute(it):
    hours = it["hours_saved_per_month"]
    cost = it["loaded_hourly_cost"]
    spend = it["ai_tool_spend_per_month"]
    gross = hours * cost * 12
    net = gross - spend * 12
    roi = (gross / (spend * 12)) if spend > 0 else None
    return {"name": it["name"], "hours": hours, "cost": cost,
            "spend": spend, "gross": gross, "net": net, "roi": roi}


def _money(n):
    return f"${n:,.0f}"


def _roi(roi):
    # Round half-up so an exact 36.25x prints as 36.3x (Python's
    # round-half-even formatting would print 36.2x).
    if roi is None:
        return "n/a (no spend)"
    return f"{Decimal(str(roi)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}x"


def to_markdown(data, rows):
    label = data.get("label", "")
    lines = [f"# Portfolio ROI — {data.get('portfolio', 'Untitled Portfolio')}"]
    if label:
        lines.append("")
        lines.append(f"*{label}*")
    lines.append("")
    lines.append("Gross $/yr = hours saved/mo × loaded hourly cost × 12. "
                 "Net $/yr = gross − tool spend/mo × 12. "
                 "ROI = gross ÷ annual tool spend.")
    lines.append("")
    lines.append("| Initiative | Hrs saved/mo | Gross $/yr | Net $/yr | ROI |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for r in rows:
        lines.append("| " + " | ".join([
            r["name"], f"{r['hours']:g}",
            _money(r["gross"]), _money(r["net"]), _roi(r["roi"]),
        ]) + " |")
    total_hours = sum(r["hours"] for r in rows)
    total_gross = sum(r["gross"] for r in rows)
    total_net = sum(r["net"] for r in rows)
    total_spend = sum(r["spend"] * 12 for r in rows)
    total_roi = (total_gross / total_spend) if total_spend > 0 else None
    lines.append("| **Portfolio total** | "
                 f"**{total_hours:g}** | **{_money(total_gross)}** | "
                 f"**{_money(total_net)}** | **{_roi(total_roi)}** |")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Initiatives: {len(rows)}")
    lines.append(f"- Total hours saved: {total_hours:g}/mo")
    lines.append(f"- Total gross value: {_money(total_gross)}/yr")
    lines.append(f"- Total net value: {_money(total_net)}/yr")
    lines.append(f"- Portfolio ROI: {_roi(total_roi)}")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Roll up portfolio ROI.")
    ap.add_argument("input", nargs="?", help="JSON input file (default: stdin)")
    ap.add_argument("--md", help="Write Markdown output to this file")
    args = ap.parse_args()

    try:
        data = load_input(args.input)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: could not read input: {e}", file=sys.stderr)
        return 2

    errors = validate(data)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 2

    rows = [compute(it) for it in data["initiatives"]]
    md = to_markdown(data, rows)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
