#!/usr/bin/env python3
"""Build a blameless post-incident (Sev) review in Markdown from JSON input.

Usage:
    python3 sev.py [input.json] [--md out.md]

Input JSON:
    {
      "incident_id": "INC-2041",
      "severity": "Sev-2",
      "title": "Creator payouts delayed by 6 hours",
      "detected_at": "2027-03-02T14:05:00Z",
      "resolved_at": "2027-03-02T20:40:00Z",
      "impact": "Payouts for 1,200 creators delayed; no data loss.",
      "root_cause": "A retry storm after a partial queue outage ...",
      "timeline": [
        {"time": "2027-03-02T14:05:00Z", "actor": "On-call",
         "action": "Paged on payout queue depth alert."}
      ],
      "action_items": [
        {"id": "AI-1", "description": "Add queue-depth circuit breaker",
         "owner": "Priya Nair", "due": "2027-03-16", "status": "Open"}
      ]
    }

Rules enforced (validation failure: clear error on stderr, exit code 1):
  - severity must be one of Sev-1, Sev-2, Sev-3, Sev-4
  - timeline events must be in chronological order
  - timeline event times must be valid ISO 8601 timestamps
  - action-item status must be one of Open, In Progress, Done
  - incident_id, title, impact, and root_cause must be non-empty

Blameless by design: the output names systems and decisions, never
people as causes. Timeline actors are roles, not blame targets.

With no --md flag, Markdown goes to stdout.
"""

import argparse
import json
import sys
from datetime import datetime

SEVERITIES = {"Sev-1", "Sev-2", "Sev-3", "Sev-4"}
ACTION_STATUSES = {"Open", "In Progress", "Done"}


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def parse_time(value, where, errors):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        errors.append(
            f"{where}: time '{value}' is not a valid ISO 8601 timestamp."
        )
        return None


def validate(data):
    """Return (errors, parsed timeline)."""
    errors = []
    if not str(data.get("incident_id", "")).strip():
        errors.append("incident_id must be a non-empty string.")
    severity = data.get("severity")
    if severity not in SEVERITIES:
        errors.append(
            f"severity '{severity}' is not valid — use one of "
            f"{', '.join(sorted(SEVERITIES))}."
        )
    if not str(data.get("title", "")).strip():
        errors.append("title must be a non-empty string.")
    if not str(data.get("impact", "")).strip():
        errors.append("impact must be a non-empty string.")
    if not str(data.get("root_cause", "")).strip():
        errors.append("root_cause must be a non-empty string.")
    for field in ("detected_at", "resolved_at"):
        if data.get(field):
            parse_time(data[field], field, errors)
    timeline = data.get("timeline")
    if not isinstance(timeline, list) or not timeline:
        errors.append("timeline must be a non-empty list.")
        timeline = []
    parsed = []
    prev_time = None
    prev_raw = None
    for i, event in enumerate(timeline, 1):
        if not isinstance(event, dict):
            errors.append(f"timeline[{i}]: each event must be an object.")
            continue
        t = parse_time(event.get("time"), f"timeline[{i}]", errors)
        if t is not None:
            if prev_time is not None and t < prev_time:
                errors.append(
                    f"timeline[{i}]: event at {event.get('time')} comes "
                    f"after {prev_raw} — timeline events must be in "
                    "chronological order."
                )
            prev_time = t
            prev_raw = event.get("time")
        if not str(event.get("action", "")).strip():
            errors.append(f"timeline[{i}]: action must be a non-empty string.")
        parsed.append(event)
    actions = data.get("action_items", [])
    if not isinstance(actions, list):
        errors.append("action_items must be a list.")
    else:
        for i, item in enumerate(actions, 1):
            if not isinstance(item, dict):
                errors.append(f"action_items[{i}]: each item must be an object.")
                continue
            if not str(item.get("description", "")).strip():
                errors.append(
                    f"action_items[{i}]: description must be a non-empty string."
                )
            status = item.get("status")
            if status not in ACTION_STATUSES:
                errors.append(
                    f"action_items[{i}] ({item.get('id', '?')}): status "
                    f"'{status}' is not valid — use one of "
                    f"{', '.join(sorted(ACTION_STATUSES))}."
                )
    return errors, parsed


def to_markdown(data, timeline):
    lines = [
        f"# Post-Incident Review — {data.get('incident_id', 'Untitled Incident')}",
        "",
        f"**Severity:** {data.get('severity', '')}",
        f"**Title:** {data.get('title', '')}",
    ]
    if data.get("detected_at"):
        lines.append(f"**Detected:** {data['detected_at']}")
    if data.get("resolved_at"):
        lines.append(f"**Resolved:** {data['resolved_at']}")
    lines.append("")
    lines.append("> Blameless review: this document describes what the "
                 "system did and what we will change. It does not assign "
                 "fault to any person.")
    lines.append("")
    lines.append("## Impact")
    lines.append("")
    lines.append(data["impact"])
    lines.append("")
    lines.append("## Timeline")
    lines.append("")
    lines.append("| Time | Actor | Action |")
    lines.append("| --- | --- | --- |")
    for event in timeline:
        lines.append(
            f"| {event.get('time', '')} | {event.get('actor', '')} | "
            f"{event.get('action', '')} |"
        )
    lines.append("")
    lines.append("## Root cause")
    lines.append("")
    lines.append(data["root_cause"])
    lines.append("")
    actions = data.get("action_items", [])
    if actions:
        open_items = [a for a in actions if a.get("status") != "Done"]
        lines.append("## Action items")
        lines.append("")
        lines.append(
            f"{len(actions)} action item(s), {len(open_items)} still open."
        )
        lines.append("")
        lines.append("| ID | Action | Owner | Due | Status |")
        lines.append("| --- | --- | --- | --- | --- |")
        for item in actions:
            lines.append(
                f"| {item.get('id', '')} | {item.get('description', '')} | "
                f"{item.get('owner', '')} | {item.get('due', '')} | "
                f"**{item.get('status', '')}** |"
            )
        lines.append("")
        if open_items:
            lines.append("### Open action items")
            lines.append("")
            for item in open_items:
                lines.append(
                    f"- **{item.get('id', '')}** — {item.get('description', '')} "
                    f"({item.get('owner', '')}, due {item.get('due', '')}, "
                    f"{item.get('status', '')})"
                )
            lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Build a blameless Sev review.")
    ap.add_argument("input", nargs="?", help="JSON input file (default: stdin)")
    ap.add_argument("--md", help="Write Markdown output to this file")
    args = ap.parse_args()

    try:
        data = load_input(args.input)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: could not read input: {e}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("error: input must be a JSON object.", file=sys.stderr)
        return 2

    errors, timeline = validate(data)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1

    md = to_markdown(data, timeline)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
