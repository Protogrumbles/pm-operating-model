#!/usr/bin/env python3
"""Generate a quarterly portfolio review pack: wins, at-risk items, and
decisions needed.

Usage:
    python3 review.py [input.json] [--md out.md]

Input JSON:
    {
      "portfolio": "Portfolio name",
      "quarter": "Q3 2026",
      "wins": ["Shipped the unified asset pipeline on time."],
      "at_risk": [
        {"project": "Live events platform",
         "reason": "Vendor delivery slipped two weeks.",
         "mitigation": "Stand up a fallback streaming vendor by Oct 15."}
      ],
      "decisions_needed": [
        {"decision": "Approve the Q4 events budget",
         "owner": "Dana Kim", "due": "2026-10-20"}
      ]
    }

Rules enforced (exit code 2 with a clear error):
  - every at-risk item must name a mitigation — an at-risk item with no
    mitigation (missing or blank) is rejected. A risk without a plan is
    not a review item, it is a surprise waiting to happen.
  - every decision needed must name an owner — a decision with no owner
    is rejected

With no --md flag, Markdown goes to stdout.
"""

import argparse
import json
import sys


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def validate(data):
    """Return a list of error strings; empty means the input is clean."""
    errors = []
    if not data.get("quarter"):
        errors.append("quarter: a quarter label (e.g. 'Q3 2026') is required.")
    for item in data.get("at_risk", []):
        proj = item.get("project", "?")
        if not item.get("reason"):
            errors.append(f"{proj}: at-risk item needs a 'reason'.")
        mitigation = item.get("mitigation")
        if not mitigation or not str(mitigation).strip():
            errors.append(
                f"{proj}: at-risk item has no mitigation — every at-risk "
                f"item must name a mitigation."
            )
    for d in data.get("decisions_needed", []):
        dec = d.get("decision", "?")
        if not d.get("owner") or not str(d.get("owner")).strip():
            errors.append(
                f"Decision '{dec}': no owner — every decision needed must "
                f"name an owner."
            )
        if not d.get("due"):
            errors.append(f"Decision '{dec}': no due date.")
    return errors


def to_markdown(data):
    lines = [f"# Quarterly Portfolio Review — "
             f"{data.get('portfolio', 'Untitled Portfolio')} "
             f"({data.get('quarter', '')})", ""]
    wins = data.get("wins", [])
    lines.append("## Wins")
    lines.append("")
    if wins:
        for w in wins:
            lines.append(f"- {w}")
    else:
        lines.append("_(No wins recorded this quarter.)_")
    lines.append("")
    lines.append("## At-risk items")
    lines.append("")
    at_risk = data.get("at_risk", [])
    if at_risk:
        lines.append("| Project | Reason | Mitigation |")
        lines.append("| --- | --- | --- |")
        for item in at_risk:
            lines.append("| " + " | ".join([
                item.get("project", ""), item.get("reason", ""),
                item.get("mitigation", ""),
            ]) + " |")
    else:
        lines.append("_(Nothing at risk this quarter.)_")
    lines.append("")
    lines.append("## Decisions needed")
    lines.append("")
    decisions = data.get("decisions_needed", [])
    if decisions:
        lines.append("| Decision | Owner | Due |")
        lines.append("| --- | --- | --- |")
        for d in decisions:
            lines.append("| " + " | ".join([
                d.get("decision", ""), d.get("owner", ""),
                d.get("due", ""),
            ]) + " |")
    else:
        lines.append("_(No decisions pending.)_")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Wins: {len(wins)}")
    lines.append(f"- At-risk items: {len(at_risk)}")
    lines.append(f"- Decisions needed: {len(decisions)}")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(
        description="Generate a quarterly portfolio review pack.")
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

    md = to_markdown(data)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
