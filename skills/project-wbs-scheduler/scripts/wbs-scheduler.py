#!/usr/bin/env python3
"""Build a work breakdown + schedule from tasks with dependencies.

Computes start/end dates per task (respecting dependencies), flags
critical-path tasks (zero slack, by the standard earliest/latest
pass), and lists milestones.

Usage:
    python3 wbs-scheduler.py [input.json] [--md out.md]

Input JSON:
    {
      "project": "Vendor Onboarding Redesign",
      "start_date": "2026-11-02",
      "tasks": [
        {"id": "T1", "name": "Map current onboarding flow",
         "duration_days": 5, "dependencies": [], "milestone": false},
        {"id": "T2", "name": "Draft new intake form",
         "duration_days": 5, "dependencies": ["T1"], "milestone": false}
      ]
    }

Dates are calendar days: a 5-day task starting 2026-11-02 ends
2026-11-06, and its successor starts 2026-11-07. Weekends are not
skipped — if your org works business days only, convert durations
before feeding them in.

Rules enforced (invalid input exits non-zero with a clear error):
  - `start_date` must be a valid YYYY-MM-DD date.
  - every task needs a unique non-empty `id`, a non-empty `name`,
    and an integer `duration_days` >= 0.
  - every dependency must name a task that exists.
  - dependencies must be acyclic — a circular dependency is an error,
    not a schedule.

With no --md flag, Markdown goes to stdout.
"""

import argparse
import json
import sys
from datetime import date, timedelta

ONE_DAY = timedelta(days=1)


def load_input(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def _parse_date(value, field, errors):
    if not isinstance(value, str):
        errors.append(f"`{field}` must be a YYYY-MM-DD date string.")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"`{field}` '{value}' is not a valid YYYY-MM-DD date.")
        return None


def validate(data):
    """Return (errors, start_date, tasks-by-id). Errors empty = valid."""
    errors = []
    if not isinstance(data, dict):
        return ["Input must be a JSON object."], None, {}
    if not isinstance(data.get("project"), str) or not data["project"].strip():
        errors.append("`project` is required and must be a non-empty string.")
    start = _parse_date(data.get("start_date"), "start_date", errors)
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("`tasks` must be a non-empty list.")
        return errors, start, {}
    by_id = {}
    for t in tasks:
        if not isinstance(t, dict):
            errors.append("Every task must be a JSON object.")
            continue
        tid = t.get("id")
        if not isinstance(tid, str) or not tid.strip():
            errors.append("Every task needs a non-empty string `id`.")
            continue
        if tid in by_id:
            errors.append(f"Duplicate task id '{tid}'.")
            continue
        by_id[tid] = t
        if not isinstance(t.get("name"), str) or not t["name"].strip():
            errors.append(f"Task {tid}: `name` must be a non-empty string.")
        dur = t.get("duration_days")
        if not isinstance(dur, int) or isinstance(dur, bool) or dur < 0:
            errors.append(f"Task {tid}: `duration_days` must be an integer "
                          ">= 0.")
        deps = t.get("dependencies", [])
        if not isinstance(deps, list):
            errors.append(f"Task {tid}: `dependencies` must be a list.")
        elif tid in deps:
            errors.append(f"Task {tid}: a task cannot depend on itself.")
        if "milestone" in t and not isinstance(t["milestone"], bool):
            errors.append(f"Task {tid}: `milestone` must be true or false.")
    for t in by_id.values():
        for dep in t.get("dependencies", []):
            if dep not in by_id:
                errors.append(f"Task {t['id']}: unknown dependency '{dep}' — "
                              "no task with that id exists.")
    if topo_sort(by_id) is None:
        errors.append("Circular dependency detected: the task graph has "
                      "a cycle, so no valid schedule exists.")
    return errors, start, by_id


def topo_sort(by_id):
    """Kahn's algorithm; returns task ids in dependency order, or None.

    Unknown dependencies are ignored here — they are reported as
    errors by validate(); this function only answers "is there a cycle
    among the tasks that exist?"
    """
    indegree = {tid: 0 for tid in by_id}
    successors = {tid: [] for tid in by_id}
    for tid, t in by_id.items():
        for dep in t.get("dependencies", []):
            if dep not in by_id:
                continue
            successors[dep].append(tid)
            indegree[tid] += 1
    queue = [tid for tid in by_id if indegree[tid] == 0]
    order = []
    while queue:
        tid = queue.pop(0)
        order.append(tid)
        for succ in successors[tid]:
            indegree[succ] -= 1
            if indegree[succ] == 0:
                queue.append(succ)
    return order if len(order) == len(by_id) else None


def schedule(by_id, start):
    """Return {id: (start, end, slack_days, critical)} and topo order."""
    order = topo_sort(by_id)
    successors = {tid: [] for tid in by_id}
    for tid, t in by_id.items():
        for dep in t.get("dependencies", []):
            successors[dep].append(tid)
    earliest_start, earliest_end = {}, {}
    for tid in order:
        t = by_id[tid]
        deps = t.get("dependencies", [])
        s = start if not deps else max(earliest_end[d] for d in deps) + ONE_DAY
        dur = t["duration_days"]
        e = s + timedelta(days=dur - 1) if dur > 0 else s
        earliest_start[tid] = s
        earliest_end[tid] = e
    project_end = max(earliest_end.values())
    latest_end, latest_start = {}, {}
    for tid in reversed(order):
        t = by_id[tid]
        succs = successors[tid]
        e = project_end if not succs else min(latest_start[s] for s in succs) - ONE_DAY
        dur = t["duration_days"]
        s = e - timedelta(days=dur - 1) if dur > 0 else e
        latest_end[tid] = e
        latest_start[tid] = s
    result = {}
    for tid in by_id:
        slack = (latest_start[tid] - earliest_start[tid]).days
        result[tid] = (earliest_start[tid], earliest_end[tid], slack,
                       slack == 0)
    return result, order, project_end


def to_markdown(data, start, sched, order, project_end):
    by_id = {t["id"]: t for t in data["tasks"]}
    total_days = (project_end - start).days + 1
    lines = [f"# WBS & Schedule — {data['project']}", ""]
    lines.append("_Sample data — fictional._")
    lines.append("")
    lines.append(f"**Start:** {start.isoformat()} · **End:** "
                 f"{project_end.isoformat()} · **Duration:** {total_days} "
                 "calendar days")
    lines.append("")
    lines.append("| ID | Task | Start | End | Days | Depends on | "
                 "Milestone | Critical |")
    lines.append("| --- | --- | --- | --- | ---: | --- | --- | --- |")
    for tid in order:
        t = by_id[tid]
        s, e, slack, critical = sched[tid]
        deps = ", ".join(t.get("dependencies", [])) or "—"
        lines.append(f"| **{tid}** | {t['name']} | {s.isoformat()} | "
                     f"{e.isoformat()} | {t['duration_days']} | {deps} | "
                     f"{'✅' if t.get('milestone') else '—'} | "
                     f"{'⭐ Yes' if critical else 'No'} |")
    lines.append("")
    critical_path = [tid for tid in order if sched[tid][3]]
    lines.append("## Critical path")
    lines.append("")
    lines.append("Tasks with zero slack — any slip here moves the end date:")
    lines.append("")
    lines.append(" → ".join(
        f"**{tid}** {by_id[tid]['name']}" for tid in critical_path))
    lines.append("")
    lines.append("## Milestones")
    lines.append("")
    milestones = [tid for tid in order if by_id[tid].get("milestone")]
    if not milestones:
        lines.append("No milestones defined.")
    else:
        for tid in milestones:
            s, e, _, _ = sched[tid]
            lines.append(f"- **{by_id[tid]['name']}** ({tid}) — "
                         f"{s.isoformat()}")
    lines.append("")
    non_critical = [(tid, sched[tid][2]) for tid in order
                    if not sched[tid][3]]
    if non_critical:
        lines.append("## Slack")
        lines.append("")
        for tid, slack in non_critical:
            lines.append(f"- {tid} {by_id[tid]['name']}: {slack} day(s) "
                         "of slack.")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(
        description="Build a work breakdown and schedule.")
    ap.add_argument("input", nargs="?", help="JSON input file (default: stdin)")
    ap.add_argument("--md", help="Write Markdown output to this file")
    args = ap.parse_args()

    try:
        data = load_input(args.input)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: could not read input: {e}", file=sys.stderr)
        return 2

    errors, start, by_id = validate(data)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 2

    sched, order, project_end = schedule(by_id, start)
    md = to_markdown(data, start, sched, order, project_end)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
