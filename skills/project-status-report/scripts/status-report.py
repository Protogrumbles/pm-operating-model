#!/usr/bin/env python3
"""Generate a weekly status report (Markdown) from milestones + RAID.

RAG status is derived from rules, not vibes — see `derive_rag` below.

Usage:
    python3 status-report.py [input.json] [--md out.md]

Input JSON:
    {
      "program": "Vendor Onboarding Redesign",
      "week": "Week of 2026-11-16",
      "week_ending": "2026-11-20",
      "prepared_by": "Priya Nair",
      "milestones": [
        {"name": "New intake form drafted", "due": "2026-11-13",
         "status": "Complete", "note": "Signed off by Legal"}
      ],
      "raid_summary": {"open_critical": 1, "open_high": 2,
                       "open_medium": 1, "open_low": 0},
      "accomplishments": ["Mapped the current onboarding flow"],
      "next_steps": ["Start the five-vendor pilot"]
    }

RAG rules (in order — the first match wins):
  - 🔴 Red: any milestone is Overdue, or any milestone whose due date
    is before `week_ending` and is not Complete (derived overdue), or
    `open_critical` > 0.
  - 🟡 Amber: any milestone is At risk, or `open_high` > 0.
  - 🟢 Green: none of the above.

Valid milestone statuses: Complete, On track, At risk, Overdue,
Not started. Anything else is an error.

Rules enforced (invalid input exits non-zero with a clear error):
  - `program` and `week` must be non-empty strings.
  - every milestone needs a non-empty `name`, a valid YYYY-MM-DD
    `due` date, and a valid `status`.
  - `raid_summary` counts, when present, must be integers >= 0.

With no --md flag, Markdown goes to stdout.
"""

import argparse
import json
import sys
from datetime import date

MILESTONE_STATUSES = {"Complete", "On track", "At risk", "Overdue",
                      "Not started"}
RAID_COUNT_KEYS = ("open_critical", "open_high", "open_medium", "open_low",
                   "total_open")


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def _non_empty_str(value):
    return isinstance(value, str) and value.strip() != ""


def validate(data):
    """Return (errors, week_ending). Errors empty = valid."""
    errors = []
    if not isinstance(data, dict):
        return ["Input must be a JSON object."], None
    if not _non_empty_str(data.get("program")):
        errors.append("`program` is required and must be a non-empty string.")
    if not _non_empty_str(data.get("week")):
        errors.append("`week` is required and must be a non-empty string.")
    week_ending = None
    if "week_ending" in data and data["week_ending"] is not None:
        try:
            week_ending = date.fromisoformat(data["week_ending"])
        except (ValueError, TypeError):
            errors.append(f"`week_ending` '{data['week_ending']}' is not a "
                          "valid YYYY-MM-DD date.")
    milestones = data.get("milestones")
    if not isinstance(milestones, list):
        errors.append("`milestones` must be a list (use [] if none).")
    else:
        for m in milestones:
            label = m.get("name", "?") if isinstance(m, dict) else "?"
            if not isinstance(m, dict):
                errors.append("Every milestone must be a JSON object.")
                continue
            if not _non_empty_str(m.get("name")):
                errors.append("Every milestone needs a non-empty `name`.")
            if "due" not in m:
                errors.append(f"Milestone '{label}': `due` date is required.")
            else:
                try:
                    date.fromisoformat(m["due"])
                except (ValueError, TypeError):
                    errors.append(f"Milestone '{label}': `due` "
                                  f"'{m['due']}' is not a valid YYYY-MM-DD "
                                  "date.")
            if m.get("status") not in MILESTONE_STATUSES:
                errors.append(
                    f"Milestone '{label}': `status` must be one of "
                    f"{', '.join(sorted(MILESTONE_STATUSES))} (got "
                    f"'{m.get('status')}').")
    raid = data.get("raid_summary", {})
    if not isinstance(raid, dict):
        errors.append("`raid_summary` must be an object of counts.")
    else:
        for key, value in raid.items():
            if key not in RAID_COUNT_KEYS:
                errors.append(f"`raid_summary` has unknown key '{key}' "
                              f"(expected one of "
                              f"{', '.join(RAID_COUNT_KEYS)}).")
            elif not isinstance(value, int) or isinstance(value, bool) \
                    or value < 0:
                errors.append(f"`raid_summary.{key}` must be an integer >= 0.")
    for field in ("accomplishments", "next_steps"):
        if field in data:
            if not isinstance(data[field], list) or \
                    any(not _non_empty_str(x) for x in data[field]):
                errors.append(f"`{field}` must be a list of non-empty "
                              "strings.")
    return errors, week_ending


def derive_rag(data, week_ending):
    """Return (rag_label, reason). First matching rule wins."""
    milestones = data.get("milestones", [])
    raid = data.get("raid_summary", {})
    overdue = [m for m in milestones if m["status"] == "Overdue"]
    if overdue:
        names = ", ".join(m["name"] for m in overdue)
        return "🔴 Red", f"overdue milestone(s): {names}."
    if week_ending:
        derived = [m for m in milestones
                   if m["status"] != "Complete"
                   and date.fromisoformat(m["due"]) < week_ending]
        if derived:
            names = ", ".join(
                f"{m['name']} (due {m['due']})" for m in derived)
            return "🔴 Red", f"milestone(s) past due as of {week_ending}: " \
                             f"{names}."
    if raid.get("open_critical", 0) > 0:
        n = raid["open_critical"]
        return "🔴 Red", f"{n} open Critical RAID item(s)."
    at_risk = [m for m in milestones if m["status"] == "At risk"]
    if at_risk:
        names = ", ".join(m["name"] for m in at_risk)
        return "🟡 Amber", f"milestone(s) at risk: {names}."
    if raid.get("open_high", 0) > 0:
        n = raid["open_high"]
        return "🟡 Amber", f"{n} open High RAID item(s)."
    return "🟢 Green", "no overdue or at-risk milestones, no open " \
                        "Critical/High RAID items."


def to_markdown(data, rag, reason):
    lines = [f"# Status Report — {data['program']}", ""]
    lines.append("_Sample data — fictional._")
    lines.append("")
    lines.append(f"**Week:** {data['week']}")
    if data.get("week_ending"):
        lines.append(f"**Week ending:** {data['week_ending']}")
    if data.get("prepared_by"):
        lines.append(f"**Prepared by:** {data['prepared_by']}")
    lines.append("")
    lines.append(f"## Overall status: {rag}")
    lines.append("")
    lines.append(f"RAG derived by rule: {reason}")
    lines.append("")
    lines.append("## Milestones")
    lines.append("")
    milestones = data.get("milestones", [])
    if not milestones:
        lines.append("No milestones tracked this week.")
    else:
        lines.append("| Milestone | Due | Status | Note |")
        lines.append("| --- | --- | --- | --- |")
        for m in milestones:
            lines.append(f"| {m['name']} | {m['due']} | {m['status']} | "
                         f"{m.get('note', '—')} |")
    lines.append("")
    raid = data.get("raid_summary", {})
    lines.append("## RAID summary")
    lines.append("")
    lines.append(f"- Open Critical: {raid.get('open_critical', 0)}")
    lines.append(f"- Open High: {raid.get('open_high', 0)}")
    lines.append(f"- Open Medium: {raid.get('open_medium', 0)}")
    lines.append(f"- Open Low: {raid.get('open_low', 0)}")
    if "total_open" in raid:
        lines.append(f"- Total open: {raid['total_open']}")
    lines.append("")
    lines.append("## Accomplishments")
    lines.append("")
    accomplishments = data.get("accomplishments", [])
    if not accomplishments:
        lines.append("None recorded.")
    else:
        for a in accomplishments:
            lines.append(f"- {a}")
    lines.append("")
    lines.append("## Next steps")
    lines.append("")
    next_steps = data.get("next_steps", [])
    if not next_steps:
        lines.append("None recorded.")
    else:
        for n in next_steps:
            lines.append(f"- {n}")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Generate a weekly status report.")
    ap.add_argument("input", nargs="?", help="JSON input file (default: stdin)")
    ap.add_argument("--md", help="Write Markdown output to this file")
    args = ap.parse_args()

    try:
        data = load_input(args.input)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: could not read input: {e}", file=sys.stderr)
        return 2

    errors, week_ending = validate(data)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 2

    rag, reason = derive_rag(data, week_ending)
    md = to_markdown(data, rag, reason)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
