#!/usr/bin/env python3
"""Render a RAID log (Risks / Assumptions / Issues / Dependencies).

Reads a JSON list of entries, validates severity and status against
fixed vocabularies, and outputs a Markdown log grouped by type with
counts and a summary of open Critical/High items.

Usage:
    python3 raid.py [input.json] [--md out.md]

Input JSON:
    {
      "project": "Vendor Onboarding Redesign",
      "entries": [
        {"id": "R1", "type": "Risk",
         "title": "Legal review becomes a bottleneck",
         "severity": "High", "owner": "Sofia Reyes",
         "status": "Open",
         "mitigation": "Pre-agreed review SLA with a backup reviewer"}
      ]
    }

Rules enforced (invalid input exits non-zero with a clear error):
  - `type` must be one of Risk, Assumption, Issue, Dependency.
  - `severity` must be one of Critical, High, Medium, Low.
  - `status` must be one of Open, Monitoring, Mitigated, Closed.
  - every entry needs a non-empty `title` and `owner`.

With no --md flag, Markdown goes to stdout.
"""

import argparse
import json
import sys
from collections import Counter

TYPES = ["Risk", "Assumption", "Issue", "Dependency"]
PLURALS = {"Risk": "Risks", "Assumption": "Assumptions",
           "Issue": "Issues", "Dependency": "Dependencies"}
SEVERITIES = {"Critical", "High", "Medium", "Low"}
STATUSES = {"Open", "Monitoring", "Mitigated", "Closed"}
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def validate(data):
    """Return (errors, project, entries). Errors empty = valid."""
    errors = []
    if isinstance(data, list):
        project, entries = "Untitled Project", data
    elif isinstance(data, dict):
        project = data.get("project", "Untitled Project")
        entries = data.get("entries")
        if not isinstance(entries, list):
            return ["`entries` must be a list of RAID entries."], project, []
    else:
        return ["Input must be a JSON object with `entries`, or a bare "
                "JSON list of entries."], "Untitled Project", []
    for i, e in enumerate(entries):
        label = e.get("id", f"entry #{i + 1}") if isinstance(e, dict) else f"entry #{i + 1}"
        if not isinstance(e, dict):
            errors.append(f"{label}: every entry must be a JSON object.")
            continue
        if e.get("type") not in TYPES:
            errors.append(f"{label}: `type` must be one of "
                          f"{', '.join(TYPES)} (got "
                          f"'{e.get('type')}').")
        if e.get("severity") not in SEVERITIES:
            errors.append(f"{label}: `severity` must be one of Critical, "
                          f"High, Medium, Low (got '{e.get('severity')}').")
        if e.get("status") not in STATUSES:
            errors.append(f"{label}: `status` must be one of Open, "
                          f"Monitoring, Mitigated, Closed (got "
                          f"'{e.get('status')}').")
        if not isinstance(e.get("title"), str) or not e["title"].strip():
            errors.append(f"{label}: `title` is required and must be a "
                          "non-empty string.")
        if not isinstance(e.get("owner"), str) or not e["owner"].strip():
            errors.append(f"{label}: `owner` is required and must be a "
                          "non-empty string.")
    return errors, project, entries


def to_markdown(project, entries):
    counts = Counter(e["type"] for e in entries)
    status_counts = Counter(e["status"] for e in entries)
    open_severe = [e for e in entries
                   if e["status"] in ("Open", "Monitoring")
                   and e["severity"] in ("Critical", "High")]
    open_severe.sort(key=lambda e: (SEVERITY_ORDER[e["severity"]], e["id"]
                                    if "id" in e else e["title"]))
    lines = [f"# RAID Log — {project}", ""]
    lines.append("_Sample data — fictional._")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"**Total entries:** {len(entries)}")
    lines.append("")
    for t in TYPES:
        lines.append(f"- {PLURALS[t]}: {counts.get(t, 0)}")
    lines.append("")
    lines.append("By status: " + ", ".join(
        f"{s}: {status_counts.get(s, 0)}" for s in
        ["Open", "Monitoring", "Mitigated", "Closed"]))
    lines.append("")
    lines.append("## Open Critical / High items — needs attention")
    lines.append("")
    if not open_severe:
        lines.append("None. No open Critical or High items.")
    else:
        for e in open_severe:
            lines.append(f"- **[{e['severity']}]** "
                         f"{e.get('id', '')} {e['title']} — "
                         f"owner: {e['owner']}, status: {e['status']}")
    lines.append("")
    for t in TYPES:
        group = [e for e in entries if e["type"] == t]
        if not group:
            continue
        group.sort(key=lambda e: (SEVERITY_ORDER[e["severity"]],
                                  e.get("id", "")))
        lines.append(f"## {PLURALS[t]} ({len(group)})")
        lines.append("")
        lines.append("| ID | Title | Severity | Owner | Status | Mitigation / "
                     "note |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for e in group:
            lines.append(f"| {e.get('id', '—')} | {e['title']} | "
                         f"{e['severity']} | {e['owner']} | {e['status']} | "
                         f"{e.get('mitigation', e.get('note', '—'))} |")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Render a RAID log.")
    ap.add_argument("input", nargs="?", help="JSON input file (default: stdin)")
    ap.add_argument("--md", help="Write Markdown output to this file")
    args = ap.parse_args()

    try:
        data = load_input(args.input)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: could not read input: {e}", file=sys.stderr)
        return 2

    errors, project, entries = validate(data)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 2

    md = to_markdown(project, entries)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
