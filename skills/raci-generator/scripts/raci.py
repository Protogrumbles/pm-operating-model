#!/usr/bin/env python3
"""Generate a RACI matrix (Markdown + CSV) from a JSON program definition.

Usage:
    python3 raci.py [input.json] [--md out.md] [--csv out.csv]

Input JSON:
    {
      "program": "Program name",
      "people": [{"name": "Ada", "role": "Program Manager"}, ...],
      "decisions": [
        {"id": "D1", "title": "Approve a vendor",
         "assignments": {"Ada": "A", "Ben": "R", "Cleo": "C"}}
      ]
    }

Rules enforced (reported in the validation section, exit code 1 if broken):
  - exactly one Accountable (A) per decision
  - at least one Responsible (R) per decision
  - every assigned name must appear in `people`
  - every assignment letter must be one of R, A, C, I

With no --md/--csv flags, Markdown goes to stdout.
"""

import argparse
import csv
import io
import json
import sys

VALID = {"R", "A", "C", "I"}


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def validate(data):
    """Return a list of error strings; empty means the matrix is clean."""
    errors = []
    known = {p["name"] for p in data.get("people", [])}
    for d in data.get("decisions", []):
        did = d.get("id", "?")
        title = d.get("title", "")
        assigns = d.get("assignments", {})
        for name, letter in assigns.items():
            if name not in known:
                errors.append(
                    f"{did} ({title}): '{name}' is not listed in people."
                )
            if letter not in VALID:
                errors.append(
                    f"{did} ({title}): '{letter}' for {name} is not a "
                    f"valid RACI letter (use R, A, C, I)."
                )
        accountable = [n for n, l in assigns.items() if l == "A"]
        responsible = [n for n, l in assigns.items() if l == "R"]
        if len(accountable) == 0:
            errors.append(f"{did} ({title}): no Accountable (A) assigned.")
        elif len(accountable) > 1:
            errors.append(
                f"{did} ({title}): {len(accountable)} Accountable "
                f"({', '.join(accountable)}) — exactly one required."
            )
        if not responsible:
            errors.append(f"{did} ({title}): no Responsible (R) assigned.")
    return errors


def build_matrix(data):
    people = [p["name"] for p in data.get("people", [])]
    rows = []
    for d in data.get("decisions", []):
        assigns = d.get("assignments", {})
        rows.append(
            [d.get("id", ""), d.get("title", "")]
            + [assigns.get(name, "—") for name in people]
        )
    return people, rows


def to_markdown(data, people, rows, errors):
    lines = [f"# RACI Matrix — {data.get('program', 'Untitled Program')}", ""]
    header = "| Decision | " + " | ".join(people) + " |"
    lines.append(header)
    lines.append("| " + " | ".join(["---"] * (len(people) + 1)) + " |")
    for r in rows:
        lines.append(
            "| " + " | ".join([f"**{r[0]}** {r[1]}"] + r[2:]) + " |"
        )
    lines.append("")
    lines.append("**Legend:** R = Responsible (does the work) · "
                 "A = Accountable (owns the outcome, exactly one) · "
                 "C = Consulted (input before) · I = Informed (told after)")
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    if not errors:
        lines.append("✅ All decisions have exactly one Accountable and "
                     "at least one Responsible.")
    else:
        lines.append(f"⚠️ {len(errors)} issue(s) found:")
        lines.append("")
        for e in errors:
            lines.append(f"- {e}")
    lines.append("")
    return "\n".join(lines)


def to_csv(people, rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Decision ID", "Decision"] + people)
    w.writerows(rows)
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser(description="Generate a RACI matrix.")
    ap.add_argument("input", nargs="?", help="JSON input file (default: stdin)")
    ap.add_argument("--md", help="Write Markdown output to this file")
    ap.add_argument("--csv", help="Write CSV output to this file")
    args = ap.parse_args()

    try:
        data = load_input(args.input)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: could not read input: {e}", file=sys.stderr)
        return 2

    errors = validate(data)
    people, rows = build_matrix(data)
    md = to_markdown(data, people, rows, errors)
    csv_text = to_csv(people, rows)

    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    if args.csv:
        with open(args.csv, "w", encoding="utf-8", newline="") as f:
            f.write(csv_text)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
