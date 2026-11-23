# project-status-report

A weekly status report where the RAG status is derived from rules
over milestones and the RAID log — not from how the week felt.

## When to use it

- Every weekly update says "on track" and nobody believes it.
- A sponsor asks why the status is red and the answer is a shrug.
- Milestones and RAID live in different places and the report has to
  reconcile them.

## RAG rules

The first matching rule wins, and the report states which rule fired:

- 🔴 **Red:** any milestone is `Overdue`, or any milestone whose due
  date is before `week_ending` and is not `Complete` (derived
  overdue), or `open_critical` > 0 in the RAID summary.
- 🟡 **Amber:** any milestone is `At risk`, or `open_high` > 0.
- 🟢 **Green:** none of the above.

The report prints the reason next to the RAG, so a red status is
always defensible in the room.

## Rules the generator enforces

- **Fixed milestone vocabulary.** Status must be one of `Complete`,
  `On track`, `At risk`, `Overdue`, `Not started`. A status of
  "Done" or "almost" is rejected — it doesn't map to a rule.
- **Every milestone has a due date.** A milestone without a date
  can't be overdue, which is exactly how dates get hidden.
- **RAID counts are integers ≥ 0.** The RAG rules read
  `open_critical` and `open_high` from `raid_summary`; negative or
  non-numeric counts are rejected.
- **Derived overdue counts.** A milestone that isn't `Complete` and
  whose due date has passed by `week_ending` is treated as overdue
  even if nobody marked it so.

## Input format

```json
{
  "program": "Vendor Onboarding Redesign",
  "week": "Week of 2026-11-16",
  "week_ending": "2026-11-20",
  "prepared_by": "Priya Nair",
  "milestones": [
    {"name": "New intake form drafted", "due": "2026-11-13",
     "status": "Complete", "note": "Signed off by Legal"}
  ],
  "raid_summary": {"open_critical": 1, "open_high": 3,
                   "open_medium": 2, "open_low": 0, "total_open": 6},
  "accomplishments": ["Mapped the current onboarding flow"],
  "next_steps": ["Resolve the pilot tracker outage"]
}
```

- `program`, `week`: required, non-empty strings.
- `week_ending`: optional `YYYY-MM-DD` date, used for the derived
  overdue check. Omit it and only explicit `Overdue` statuses count.
- `milestones`: list of objects with `name`, `due` (`YYYY-MM-DD`),
  `status`, and an optional `note`.
- `raid_summary`: object of counts — `open_critical`, `open_high`,
  `open_medium`, `open_low`, `total_open`. Only `open_critical` and
  `open_high` drive RAG; the rest are reported. Defaults to 0 when a
  key is absent.
- `accomplishments`, `next_steps`: lists of strings.
- `prepared_by`: optional.

## Usage

```bash
python3 scripts/status-report.py examples/input.json --md out/status.md
# or: cat examples/input.json | python3 scripts/status-report.py
```

Invalid input (bad milestone status, missing due date, negative RAID
count) exits non-zero with a clear error on stderr and writes no
output file. See `examples/invalid-input.json` (status "Done").

## Design notes

RAG without a stated rule is fiction — the same week can be green to
the person writing the update and red to the sponsor reading it. This
report fixes the rule in the open and prints the reason, so the
argument moves from "is it red?" to "do we accept the rule?" It pairs
with `project-raid-log`: feed that log's open Critical/High counts
into `raid_summary` here. The example input's counts match the
`project-raid-log` example for the same fictional program
(1 open Critical, 3 open High).

All sample data is fictional (Northlight Studios). Do not quote the
example numbers as results.
