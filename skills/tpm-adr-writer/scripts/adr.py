#!/usr/bin/env python3
"""Write an architecture decision record (ADR) in Markdown from JSON input.

Usage:
    python3 adr.py [input.json] [--md out.md]

Input JSON:
    {
      "number": 12,
      "title": "Adopt event-driven ingestion for the Creator Analytics pipeline",
      "status": "Accepted",
      "date": "2026-11-20",
      "context": "Why the decision is needed.",
      "decision": "What was decided.",
      "alternatives": [
        {"title": "Keep batch ingestion",
         "pros": ["No new infrastructure"],
         "cons": ["Data lands up to 6 hours late"]}
      ],
      "consequences": ["Producers must publish a schema-versioned event."]
    }

Rules enforced (validation failure: clear error on stderr, exit code 1):
  - status must be one of Proposed, Accepted, Deprecated, Superseded
  - at least one alternative must be considered
  - every alternative needs a title and at least one pro or con
  - title, context, decision, and consequences must be non-empty

With no --md flag, Markdown goes to stdout.
"""

import argparse
import json
import sys

STATUSES = {"Proposed", "Accepted", "Deprecated", "Superseded"}


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def validate(data):
    """Return a list of error strings; empty means the ADR is writable."""
    errors = []
    if not str(data.get("title", "")).strip():
        errors.append("title must be a non-empty string.")
    status = data.get("status")
    if status not in STATUSES:
        errors.append(
            f"status '{status}' is not valid — use one of "
            f"{', '.join(sorted(STATUSES))}."
        )
    if not str(data.get("context", "")).strip():
        errors.append("context must be a non-empty string.")
    if not str(data.get("decision", "")).strip():
        errors.append("decision must be a non-empty string.")
    alternatives = data.get("alternatives")
    if not isinstance(alternatives, list) or not alternatives:
        errors.append(
            "alternatives must be a non-empty list — an ADR with zero "
            "alternatives considered is not a decision, it is a decree."
        )
    else:
        for i, alt in enumerate(alternatives, 1):
            if not isinstance(alt, dict) or not str(alt.get("title", "")).strip():
                errors.append(f"alternatives[{i}]: each alternative needs a title.")
                continue
            pros = alt.get("pros", [])
            cons = alt.get("cons", [])
            if not isinstance(pros, list) or not isinstance(cons, list):
                errors.append(
                    f"alternatives[{i}] ({alt.get('title')}): pros and cons "
                    "must be lists."
                )
            elif not pros and not cons:
                errors.append(
                    f"alternatives[{i}] ({alt.get('title')}): list at least "
                    "one pro or one con — an alternative with neither was "
                    "not actually considered."
                )
    consequences = data.get("consequences")
    if not isinstance(consequences, list) or not consequences:
        errors.append("consequences must be a non-empty list.")
    elif any(not str(c).strip() for c in consequences):
        errors.append("consequences must not contain empty entries.")
    number = data.get("number")
    if number is not None and (not isinstance(number, int) or number < 0):
        errors.append("number, when given, must be a non-negative integer.")
    return errors


def to_markdown(data):
    number = data.get("number")
    heading = (
        f"# ADR-{number:04d}: {data['title']}"
        if isinstance(number, int)
        else f"# ADR: {data['title']}"
    )
    lines = [heading, ""]
    lines.append(f"**Status:** {data['status']}")
    if data.get("date"):
        lines.append(f"**Date:** {data['date']}")
    if data.get("supersedes"):
        lines.append(f"**Supersedes:** {data['supersedes']}")
    if data.get("superseded_by"):
        lines.append(f"**Superseded by:** {data['superseded_by']}")
    lines.append("")
    lines.append("## Context")
    lines.append("")
    lines.append(data["context"])
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(data["decision"])
    lines.append("")
    lines.append("## Alternatives considered")
    lines.append("")
    for alt in data["alternatives"]:
        lines.append(f"### {alt['title']}")
        lines.append("")
        for pro in alt.get("pros", []):
            lines.append(f"- ✅ Pro: {pro}")
        for con in alt.get("cons", []):
            lines.append(f"- ⚠️ Con: {con}")
        lines.append("")
    lines.append("## Consequences")
    lines.append("")
    for c in data["consequences"]:
        lines.append(f"- {c}")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Write an architecture decision record.")
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

    errors = validate(data)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1

    md = to_markdown(data)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
