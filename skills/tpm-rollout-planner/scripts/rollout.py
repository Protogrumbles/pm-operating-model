#!/usr/bin/env python3
"""Build a phased API/platform rollout plan in Markdown from JSON input.

Usage:
    python3 rollout.py [input.json] [--md out.md]

Input JSON:
    {
      "service": "Playback API v2",
      "phases": [
        {"name": "Canary", "cohort": "Internal employees",
         "traffic_percent": 5, "start_date": "2027-01-05",
         "duration_days": 7}
      ],
      "rollback_criteria": ["Error rate exceeds 1% for 15 minutes."],
      "comms_plan": [
        {"audience": "Support", "channel": "#support",
         "message": "Canary starts Jan 5; expect no customer-facing change."}
      ]
    }

Rules enforced (validation failure: clear error on stderr, exit code 1):
  - at least one phase
  - each phase's traffic_percent must be > 0
  - cumulative traffic across phases must be <= 100
  - start_date must be YYYY-MM-DD and phases must run in order:
    each phase starts on or after the previous phase's end date
    (start_date + duration_days)
  - duration_days must be a positive integer
  - rollback_criteria must be a non-empty list

With no --md flag, Markdown goes to stdout.
"""

import argparse
import json
import sys
from datetime import date, timedelta


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def parse_date(value, where, errors):
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        errors.append(
            f"{where}: start_date '{value}' is not a valid YYYY-MM-DD date."
        )
        return None


def validate(data):
    """Return (errors, parsed phases) — parsed phases carry start/end dates."""
    errors = []
    if not str(data.get("service", "")).strip():
        errors.append("service must be a non-empty string.")
    phases = data.get("phases")
    if not isinstance(phases, list) or not phases:
        errors.append("phases must be a non-empty list.")
        phases = []
    parsed = []
    cumulative = 0
    prev_end = None
    for i, ph in enumerate(phases, 1):
        name = ph.get("name", f"Phase {i}") if isinstance(ph, dict) else f"Phase {i}"
        if not isinstance(ph, dict):
            errors.append(f"phases[{i}]: each phase must be an object.")
            continue
        pct = ph.get("traffic_percent")
        if not isinstance(pct, (int, float)) or isinstance(pct, bool) or pct <= 0:
            errors.append(
                f"{name}: traffic_percent must be a number greater than 0 "
                f"(got {pct!r})."
            )
        else:
            cumulative += pct
            if cumulative > 100:
                errors.append(
                    f"{name}: cumulative traffic reaches {cumulative:g}% — "
                    "phases must sum to at most 100%."
                )
        duration = ph.get("duration_days")
        if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
            errors.append(
                f"{name}: duration_days must be a positive integer "
                f"(got {duration!r})."
            )
            duration = None
        start = parse_date(ph.get("start_date"), name, errors)
        end = None
        if start is not None and duration is not None:
            end = start + timedelta(days=duration)
            if prev_end is not None and start < prev_end:
                errors.append(
                    f"{name}: starts {start.isoformat()} but the previous "
                    f"phase runs until {prev_end.isoformat()} — phases "
                    "must run in order, with no overlap."
                )
            prev_end = end
        parsed.append({**ph, "_start": start, "_end": end})
    rollback = data.get("rollback_criteria")
    if not isinstance(rollback, list) or not rollback:
        errors.append("rollback_criteria must be a non-empty list.")
    elif any(not str(c).strip() for c in rollback):
        errors.append("rollback_criteria must not contain empty entries.")
    comms = data.get("comms_plan", [])
    if not isinstance(comms, list):
        errors.append("comms_plan must be a list.")
    else:
        for i, msg in enumerate(comms, 1):
            if not isinstance(msg, dict) or not str(msg.get("audience", "")).strip():
                errors.append(f"comms_plan[{i}]: each entry needs an audience.")
    return errors, parsed


def to_markdown(data, parsed):
    lines = [f"# Rollout Plan — {data.get('service', 'Untitled Service')}", ""]
    lines.append("| Phase | Cohort | Traffic | Cumulative | Start | End | Duration |")
    lines.append("| --- | --- | ---: | ---: | --- | --- | ---: |")
    cumulative = 0
    for ph in parsed:
        cumulative += ph.get("traffic_percent", 0)
        start = ph["_start"].isoformat() if ph["_start"] else str(ph.get("start_date", ""))
        end = ph["_end"].isoformat() if ph["_end"] else "—"
        duration = ph.get("duration_days", "—")
        lines.append(
            f"| **{ph.get('name', '')}** | {ph.get('cohort', '')} | "
            f"{ph.get('traffic_percent', '')}% | {cumulative:g}% | "
            f"{start} | {end} | {duration} days |"
        )
    lines.append("")
    lines.append(f"**Total traffic at full rollout:** {cumulative:g}%")
    lines.append("")
    lines.append("## Rollback criteria")
    lines.append("")
    lines.append("Roll back immediately if any of these hold:")
    lines.append("")
    for c in data["rollback_criteria"]:
        lines.append(f"- {c}")
    lines.append("")
    comms = data.get("comms_plan", [])
    if comms:
        lines.append("## Comms plan")
        lines.append("")
        lines.append("| Audience | Channel | Message |")
        lines.append("| --- | --- | --- |")
        for msg in comms:
            lines.append(
                f"| {msg.get('audience', '')} | {msg.get('channel', '')} | "
                f"{msg.get('message', '')} |"
            )
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Build a phased rollout plan.")
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

    errors, parsed = validate(data)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1

    md = to_markdown(data, parsed)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
