#!/usr/bin/env python3
"""Build a migration cutover checklist with go/no-go gates, in Markdown.

Usage:
    python3 cutover.py [input.json] [--md out.md]

Input JSON:
    {
      "migration": "Billing database migration",
      "cutover_date": "2027-02-14",
      "items": [
        {"id": "C1", "description": "Final snapshot verified",
         "owner": "Dana Kim", "category": "Data",
         "required": true, "status": "Pass"}
      ],
      "gates": [
        {"id": "G1", "name": "Data integrity gate",
         "criterion": "Row counts match between source and target",
         "status": "Pass"}
      ]
    }

Rules enforced (validation failure: clear error on stderr, exit code 1):
  - item status must be one of Pass, Fail, Pending, Blocked
  - gate status must be one of Pass, Fail, Pending
  - item and gate ids must be unique within their own lists
  - required must be a boolean

Verdict (reported in the output; exit code 1 on NO-GO, 0 on GO):
  - NO-GO if any required item is Fail or Blocked, or any gate is Fail.
  - A Pending gate does not by itself force NO-GO, but it is flagged
    prominently — do not cut over with an uncleared gate.

With no --md flag, Markdown goes to stdout.
"""

import argparse
import json
import sys
from collections import OrderedDict

ITEM_STATUSES = {"Pass", "Fail", "Pending", "Blocked"}
GATE_STATUSES = {"Pass", "Fail", "Pending"}


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def validate(data):
    """Return a list of error strings; empty means the checklist is usable."""
    errors = []
    if not str(data.get("migration", "")).strip():
        errors.append("migration must be a non-empty string.")
    items = data.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty list.")
        items = []
    seen_ids = set()
    for i, item in enumerate(items, 1):
        where = f"items[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where}: each item must be an object.")
            continue
        iid = item.get("id", "?")
        if iid in seen_ids:
            errors.append(f"items: duplicate item id '{iid}'.")
        seen_ids.add(iid)
        if not str(item.get("description", "")).strip():
            errors.append(f"{iid}: description must be a non-empty string.")
        if not str(item.get("owner", "")).strip():
            errors.append(f"{iid}: owner must be a non-empty string.")
        if not isinstance(item.get("required"), bool):
            errors.append(f"{iid}: required must be true or false.")
        status = item.get("status")
        if status not in ITEM_STATUSES:
            errors.append(
                f"{iid}: status '{status}' is not valid — use one of "
                f"{', '.join(sorted(ITEM_STATUSES))}."
            )
    gates = data.get("gates", [])
    if not isinstance(gates, list):
        errors.append("gates must be a list.")
        gates = []
    seen_gates = set()
    for i, gate in enumerate(gates, 1):
        where = f"gates[{i}]"
        if not isinstance(gate, dict):
            errors.append(f"{where}: each gate must be an object.")
            continue
        gid = gate.get("id", "?")
        if gid in seen_gates:
            errors.append(f"gates: duplicate gate id '{gid}'.")
        seen_gates.add(gid)
        if not str(gate.get("name", "")).strip():
            errors.append(f"{gid}: name must be a non-empty string.")
        status = gate.get("status")
        if status not in GATE_STATUSES:
            errors.append(
                f"{gid}: status '{status}' is not valid — use one of "
                f"{', '.join(sorted(GATE_STATUSES))}."
            )
    return errors


def verdict(data):
    """Return (is_go, blocking_reasons, pending_gate_names)."""
    blocking = []
    for item in data.get("items", []):
        if item.get("required") and item.get("status") in ("Fail", "Blocked"):
            blocking.append(
                f"Required item {item.get('id')} ({item.get('description')}) "
                f"is {item.get('status')}."
            )
    for gate in data.get("gates", []):
        if gate.get("status") == "Fail":
            blocking.append(
                f"Gate {gate.get('id')} ({gate.get('name')}) failed."
            )
    pending_gates = [
        g.get("name") for g in data.get("gates", []) if g.get("status") == "Pending"
    ]
    return (not blocking), blocking, pending_gates


def to_markdown(data, is_go, blocking, pending_gates):
    lines = [f"# Cutover Checklist — {data.get('migration', 'Untitled Migration')}", ""]
    if data.get("cutover_date"):
        lines.append(f"**Cutover date:** {data['cutover_date']}")
        lines.append("")
    items = data.get("items", [])
    total = len(items)
    counts = {s: sum(1 for i in items if i.get("status") == s) for s in ITEM_STATUSES}
    required = [i for i in items if i.get("required")]
    required_open = sum(
        1 for i in required if i.get("status") in ("Fail", "Pending", "Blocked")
    )
    lines.append("## Summary")
    lines.append("")
    lines.append(
        f"{total} items ({len(required)} required): "
        + ", ".join(f"{counts[s]} {s}" for s in ("Pass", "Fail", "Pending", "Blocked"))
        + f". Required items still open: {required_open}."
    )
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    if is_go:
        lines.append("### ✅ GO")
        lines.append("")
        lines.append("No required item is Fail/Blocked and no gate has failed.")
    else:
        lines.append("### 🛑 NO-GO")
        lines.append("")
        lines.append("Do not cut over. Blocking issues:")
        lines.append("")
        for b in blocking:
            lines.append(f"- {b}")
    if pending_gates:
        lines.append("")
        lines.append(
            "⚠️ Gates not yet cleared: " + ", ".join(pending_gates) + "."
        )
    lines.append("")
    grouped = OrderedDict()
    for item in items:
        grouped.setdefault(item.get("category", "Uncategorized"), []).append(item)
    lines.append("## Checklist by category")
    lines.append("")
    for category, cat_items in grouped.items():
        lines.append(f"### {category}")
        lines.append("")
        lines.append("| ID | Item | Owner | Required | Status |")
        lines.append("| --- | --- | --- | :---: | --- |")
        for item in cat_items:
            req = "Yes" if item.get("required") else "No"
            lines.append(
                f"| {item.get('id', '')} | {item.get('description', '')} | "
                f"{item.get('owner', '')} | {req} | **{item.get('status', '')}** |"
            )
        lines.append("")
    gates = data.get("gates", [])
    if gates:
        lines.append("## Go / No-Go gates")
        lines.append("")
        lines.append("| Gate | Criterion | Status |")
        lines.append("| --- | --- | --- |")
        for gate in gates:
            lines.append(
                f"| **{gate.get('id', '')}** {gate.get('name', '')} | "
                f"{gate.get('criterion', '')} | **{gate.get('status', '')}** |"
            )
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Build a cutover checklist.")
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

    is_go, blocking, pending_gates = verdict(data)
    md = to_markdown(data, is_go, blocking, pending_gates)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0 if is_go else 1


if __name__ == "__main__":
    sys.exit(main())
