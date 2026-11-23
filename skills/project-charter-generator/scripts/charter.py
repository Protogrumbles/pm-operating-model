#!/usr/bin/env python3
"""Generate a project charter (Markdown) from a JSON project brief.

Usage:
    python3 charter.py [input.json] [--md out.md]

Input JSON:
    {
      "project": "Vendor Onboarding Redesign",
      "sponsor": "Dana Kim, Operations Director",
      "problem": "Onboarding a new vendor takes ...",
      "scope_in": ["Redesign the intake form", "..."],
      "scope_out": ["Renegotiating existing contracts"],
      "success_criteria": [
        "Onboarding time cut from 6 weeks to 3 weeks",
        {"criterion": "First-contact resolution", "measure": ">= 70%"}
      ],
      "stakeholders": [
        {"name": "Priya Nair", "role": "Program Manager",
         "responsibility": "Owns delivery"}
      ],
      "risks": [
        {"risk": "Legal review becomes a bottleneck",
         "impact": "High", "mitigation": "Pre-agreed review SLA"}
      ]
    }

Rules enforced (invalid input exits non-zero with a clear error):
  - `project` and `problem` must be non-empty strings.
  - `scope_in` must be a non-empty list (an empty scope is not a charter).
  - `scope_out` must be present as a list.
  - `success_criteria` must be a non-empty list. A charter with no
    definition of success is a wish, not a charter.
  - `stakeholders` must be a non-empty list; each needs a name and role.
  - `risks`, if present, must be a list.

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


def _non_empty_str(value):
    return isinstance(value, str) and value.strip() != ""


def validate(data):
    """Return a list of error strings; empty means the brief is valid."""
    errors = []
    if not isinstance(data, dict):
        return ["Input must be a JSON object."]
    if not _non_empty_str(data.get("project")):
        errors.append("`project` is required and must be a non-empty string.")
    if not _non_empty_str(data.get("problem")):
        errors.append("`problem` is required and must be a non-empty string.")
    scope_in = data.get("scope_in")
    if not isinstance(scope_in, list) or not scope_in:
        errors.append(
            "`scope_in` must be a non-empty list: a charter with an empty "
            "scope authorizes nothing."
        )
    elif any(not _non_empty_str(s) for s in scope_in):
        errors.append("Every entry in `scope_in` must be a non-empty string.")
    if "scope_out" not in data:
        errors.append("`scope_out` is required (use [] if nothing is "
                      "explicitly out of scope).")
    elif not isinstance(data["scope_out"], list):
        errors.append("`scope_out` must be a list.")
    elif any(not _non_empty_str(s) for s in data["scope_out"]):
        errors.append("Every entry in `scope_out` must be a non-empty string.")
    criteria = data.get("success_criteria")
    if not isinstance(criteria, list) or not criteria:
        errors.append(
            "`success_criteria` must be a non-empty list: a charter with no "
            "success criteria cannot be judged done."
        )
    else:
        for c in criteria:
            if isinstance(c, str):
                if not c.strip():
                    errors.append("Every entry in `success_criteria` must be "
                                  "a non-empty string or object.")
            elif isinstance(c, dict):
                if not _non_empty_str(c.get("criterion")):
                    errors.append("Each object in `success_criteria` needs a "
                                  "non-empty `criterion`.")
            else:
                errors.append("Each entry in `success_criteria` must be a "
                              "string or an object with `criterion`.")
    stakeholders = data.get("stakeholders")
    if not isinstance(stakeholders, list) or not stakeholders:
        errors.append("`stakeholders` must be a non-empty list.")
    else:
        for s in stakeholders:
            if not isinstance(s, dict) or not _non_empty_str(s.get("name")) \
                    or not _non_empty_str(s.get("role")):
                errors.append("Each stakeholder needs a non-empty `name` "
                              "and `role`.")
    if "risks" in data and not isinstance(data["risks"], list):
        errors.append("`risks` must be a list.")
    else:
        for r in data.get("risks", []):
            if not isinstance(r, dict) or not _non_empty_str(r.get("risk")):
                errors.append("Each risk needs a non-empty `risk` description.")
    return errors


def _criterion_text(c):
    if isinstance(c, str):
        return c, "—"
    return c.get("criterion", ""), c.get("measure", "—")


def to_markdown(data):
    lines = [f"# Project Charter — {data['project']}", ""]
    lines.append("_Sample data — fictional._")
    lines.append("")
    if data.get("sponsor"):
        lines.append(f"**Sponsor:** {data['sponsor']}")
    if data.get("start_date"):
        lines.append(f"**Start:** {data['start_date']}")
    if data.get("target_date"):
        lines.append(f"**Target completion:** {data['target_date']}")
    if data.get("sponsor") or data.get("start_date") or data.get("target_date"):
        lines.append("")
    lines.append("## Problem")
    lines.append("")
    lines.append(data["problem"])
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("### In scope")
    lines.append("")
    for s in data["scope_in"]:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("### Out of scope")
    lines.append("")
    if data["scope_out"]:
        for s in data["scope_out"]:
            lines.append(f"- {s}")
    else:
        lines.append("- Nothing explicitly excluded.")
    lines.append("")
    lines.append("## Success criteria")
    lines.append("")
    lines.append("The project is done when all of these are true:")
    lines.append("")
    lines.append("| # | Criterion | Measure |")
    lines.append("| --- | --- | --- |")
    for i, c in enumerate(data["success_criteria"], 1):
        text, measure = _criterion_text(c)
        lines.append(f"| {i} | {text} | {measure} |")
    lines.append("")
    lines.append("## Stakeholders")
    lines.append("")
    lines.append("| Name | Role | Responsibility |")
    lines.append("| --- | --- | --- |")
    for s in data["stakeholders"]:
        lines.append(f"| {s['name']} | {s['role']} | "
                     f"{s.get('responsibility', '—')} |")
    lines.append("")
    lines.append("## Risks")
    lines.append("")
    risks = data.get("risks", [])
    if not risks:
        lines.append("No risks recorded yet — add them before kickoff.")
    else:
        lines.append("| Risk | Impact | Mitigation |")
        lines.append("| --- | --- | --- |")
        for r in risks:
            lines.append(f"| {r['risk']} | {r.get('impact', '—')} | "
                         f"{r.get('mitigation', '—')} |")
    lines.append("")
    lines.append("## Approval")
    lines.append("")
    lines.append("Sponsor sign-off: ______________________  Date: __________")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Generate a project charter.")
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
