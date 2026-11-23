#!/usr/bin/env python3
"""Generate an escalation workflow (Markdown + Mermaid) from JSON tiers.

Usage:
    python3 escalation.py [input.json] [--md out.md]

Input JSON:
    {
      "program": "Program name",
      "severities": ["Sev-1", "Sev-2", "Sev-3"],
      "tiers": [
        {"name": "Tier 1 — Help Desk", "owner": "Support Lead",
         "handles": "...", "entry_criteria": "...",
         "sla": {"Sev-1": "30m", "Sev-2": "4h"},
         "escalates_to": "Tier 2 — Product Ops",
         "escalate_when": "Not resolved in 4h"}
      ]
    }

Validation (reported in the output, exit code 1 if broken):
  - every tier has an owner and at least one SLA entry
  - SLA keys match the declared severities
  - escalates_to names an existing tier (except the last, which is null)
  - no escalation cycles
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
    errors = []
    tiers = data.get("tiers", [])
    severities = set(data.get("severities", []))
    names = {t.get("name") for t in tiers}
    for i, t in enumerate(tiers):
        name = t.get("name", f"tier {i + 1}")
        if not t.get("owner"):
            errors.append(f"{name}: no owner role assigned.")
        sla = t.get("sla") or {}
        if not sla:
            errors.append(f"{name}: no SLAs defined.")
        for sev in sla:
            if sev not in severities:
                errors.append(
                    f"{name}: SLA severity '{sev}' is not in severities "
                    f"{sorted(severities)}."
                )
        for sev in sorted(severities):
            if sev not in sla:
                errors.append(f"{name}: missing SLA for {sev}.")
        nxt = t.get("escalates_to")
        if nxt is None:
            if i != len(tiers) - 1:
                errors.append(
                    f"{name}: escalates_to is empty but it is not the "
                    f"last tier — issues would stop here."
                )
        elif nxt not in names:
            errors.append(
                f"{name}: escalates_to '{nxt}' does not match any tier."
            )
    # cycle check: follow the chain from the first tier
    seen, current = set(), tiers[0].get("name") if tiers else None
    by_name = {t.get("name"): t for t in tiers}
    while current and current in by_name:
        if current in seen:
            errors.append(f"Escalation cycle detected at '{current}'.")
            break
        seen.add(current)
        current = by_name[current].get("escalates_to")
    return errors


def _node_id(name, idx):
    return f"T{idx + 1}"


def to_mermaid(data):
    tiers = data.get("tiers", [])
    lines = ["```mermaid", "flowchart TD"]
    for i, t in enumerate(tiers):
        nid = _node_id(t["name"], i)
        owner = t.get("owner", "?")
        label = f"{t['name']}<br/>Owner: {owner}"
        lines.append(f'    {nid}["{label}"]')
    for i, t in enumerate(tiers):
        nxt = t.get("escalates_to")
        if nxt:
            j = next(
                (k for k, x in enumerate(tiers) if x.get("name") == nxt),
                None,
            )
            if j is not None:
                when = (t.get("escalate_when") or "").replace('"', "'")
                lines.append(
                    f'    {_node_id(t["name"], i)} -->|"{when}"| '
                    f'{_node_id(nxt, j)}'
                )
    last = tiers[-1] if tiers else None
    if last:
        lines.append(
            f'    {_node_id(last["name"], len(tiers) - 1)} --> RESOLVED([Resolved])'
        )
    lines.append("```")
    return "\n".join(lines)


def to_markdown(data, errors):
    tiers = data.get("tiers", [])
    severities = data.get("severities", [])
    lines = [
        f"# Escalation Workflow — {data.get('program', 'Untitled Program')}",
        "",
        "## Tiers",
        "",
        "| Tier | Owner | Handles | Entry criteria | Escalate when |",
        "| --- | --- | --- | --- | --- |",
    ]
    for t in tiers:
        lines.append(
            "| " + " | ".join([
                t.get("name", ""),
                t.get("owner", ""),
                t.get("handles", ""),
                t.get("entry_criteria", ""),
                t.get("escalate_when", "— (top tier)"),
            ]) + " |"
        )
    lines.append("")
    lines.append("## SLAs by severity")
    lines.append("")
    lines.append("| Tier | " + " | ".join(severities) + " |")
    lines.append("| " + " | ".join(["---"] * (len(severities) + 1)) + " |")
    for t in tiers:
        sla = t.get("sla") or {}
        lines.append(
            "| " + t.get("name", "") + " | "
            + " | ".join(sla.get(s, "—") for s in severities) + " |"
        )
    lines.append("")
    lines.append("## Flow")
    lines.append("")
    lines.append(to_mermaid(data))
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    if not errors:
        lines.append("✅ Every tier has an owner and a full SLA set; "
                     "the chain reaches a top tier with no cycles.")
    else:
        lines.append(f"⚠️ {len(errors)} issue(s) found:")
        lines.append("")
        for e in errors:
            lines.append(f"- {e}")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Generate an escalation workflow.")
    ap.add_argument("input", nargs="?", help="JSON input file (default: stdin)")
    ap.add_argument("--md", help="Write Markdown output to this file")
    args = ap.parse_args()

    try:
        data = load_input(args.input)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: could not read input: {e}", file=sys.stderr)
        return 2

    errors = validate(data)
    md = to_markdown(data, errors)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
