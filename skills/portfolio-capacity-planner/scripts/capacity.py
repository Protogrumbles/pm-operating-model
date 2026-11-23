#!/usr/bin/env python3
"""Compare capacity vs demand per team per quarter and flag overload
and underuse.

Usage:
    python3 capacity.py [input.json] [--md out.md]

Input JSON:
    {
      "portfolio": "Portfolio name",
      "teams": [
        {"name": "Platform", "capacity_hours_per_quarter": 480}
      ],
      "demand": [
        {"project": "Unified asset pipeline", "team": "Platform",
         "quarter": "Q1", "hours": 300}
      ]
    }

Utilisation = demand / capacity * 100, per team per quarter.
Flags:
    > 100%  -> OVERLOAD (demand exceeds capacity)
    < 50%   -> UNDERUSED (less than half the team's capacity is spoken for)
    else    -> OK

Rules enforced (exit code 2 with a clear error):
  - every demand item must reference a team listed in `teams`
  - hours must be a non-negative number (negative hours are rejected)
  - capacity must be a positive number

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
    teams = {}
    for t in data.get("teams", []):
        name = t.get("name")
        cap = t.get("capacity_hours_per_quarter")
        if not name:
            errors.append("teams: every team needs a 'name'.")
            continue
        if cap is None:
            errors.append(f"{name}: missing 'capacity_hours_per_quarter'.")
        elif isinstance(cap, bool) or not isinstance(cap, (int, float)) \
                or cap <= 0:
            errors.append(
                f"{name}: 'capacity_hours_per_quarter' must be a positive "
                f"number, got {cap!r}."
            )
        teams[name] = cap
    if not teams:
        errors.append("teams: at least one team is required.")
    for d in data.get("demand", []):
        proj = d.get("project", "?")
        team = d.get("team")
        hours = d.get("hours")
        if team not in teams:
            errors.append(
                f"{proj}: team '{team}' is not listed in teams "
                f"(known teams: {', '.join(sorted(teams)) or 'none'})."
            )
        if hours is None:
            errors.append(f"{proj}: missing 'hours'.")
        elif isinstance(hours, bool) or not isinstance(hours, (int, float)) \
                or hours < 0:
            errors.append(
                f"{proj}: 'hours' must be a non-negative number, "
                f"got {hours!r}."
            )
        if not d.get("quarter"):
            errors.append(f"{proj}: missing 'quarter'.")
    return errors


def summarize(data):
    """Return rows of (team, quarter, capacity, demand, utilisation, flag)."""
    capacity = {t["name"]: t["capacity_hours_per_quarter"]
                for t in data.get("teams", [])}
    demand = {}
    for d in data.get("demand", []):
        key = (d["team"], d["quarter"])
        demand[key] = demand.get(key, 0) + d["hours"]
    quarters = sorted({d.get("quarter", "") for d in data.get("demand", [])})
    rows = []
    for team in capacity:
        for q in quarters:
            cap = capacity[team]
            dem = demand.get((team, q), 0)
            util = dem / cap * 100 if cap else 0.0
            if util > 100:
                flag = "⚠️ OVERLOAD"
            elif util < 50:
                flag = "ℹ️ UNDERUSED"
            else:
                flag = "OK"
            rows.append((team, q, cap, dem, util, flag))
    return rows


def to_markdown(data, rows):
    lines = [f"# Capacity vs Demand — {data.get('portfolio', 'Untitled Portfolio')}", ""]
    lines.append("Utilisation = demand ÷ capacity × 100, per team per quarter. "
                 "**OVERLOAD** is over 100%; **UNDERUSED** is under 50%.")
    lines.append("")
    lines.append("| Team | Quarter | Capacity (hrs) | Demand (hrs) | Utilisation | Flag |")
    lines.append("| --- | --- | ---: | ---: | ---: | --- |")
    for team, q, cap, dem, util, flag in rows:
        lines.append("| " + " | ".join([
            team, q, f"{cap:g}", f"{dem:g}", f"{util:.1f}%", flag,
        ]) + " |")
    lines.append("")
    overloads = [r for r in rows if "OVERLOAD" in r[5]]
    underused = [r for r in rows if "UNDERUSED" in r[5]]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Team-quarters assessed: {len(rows)}")
    lines.append(f"- Overloaded: {len(overloads)}"
                 + (f" ({', '.join(f'{t} {q}' for t, q, *_ in overloads)})"
                    if overloads else ""))
    lines.append(f"- Underused: {len(underused)}"
                 + (f" ({', '.join(f'{t} {q}' for t, q, *_ in underused)})"
                    if underused else ""))
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Compare capacity vs demand.")
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

    md = to_markdown(data, summarize(data))
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
