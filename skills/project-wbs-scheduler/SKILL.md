# project-wbs-scheduler

Turn a task list with dependencies into a dated schedule: start and
end per task, the milestones, and the critical path — computed, not
guessed.

## When to use it

- A charter is signed and now someone asks "when will it be done?"
- A plan's dates were set by picking a launch date and working
  backwards from vibes.
- A dependency slips and nobody can say which dates move with it.

## Rules the generator enforces

- **Every dependency must exist.** A task that depends on a task id
  that isn't in the list is an error, not a silent gap.
- **No circular dependencies.** A cycle means no valid schedule
  exists, so the CLI refuses the input and says so.
- **Dates follow dependencies.** A task starts the day after its
  latest-finishing dependency ends (or on the project start date if
  it has none). A task never starts before its dependencies finish.
- **Critical path is computed, not asserted.** A task is critical
  when it has zero slack — the standard earliest/latest pass. Any
  slip on a critical task moves the project end date.
- **Milestones are zero-duration markers.** A milestone task has
  `duration_days: 0` and `milestone: true`; its date is the day its
  dependencies finish.

## Input format

```json
{
  "project": "Vendor Onboarding Redesign",
  "start_date": "2026-11-02",
  "tasks": [
    {"id": "T1", "name": "Map current onboarding flow",
     "duration_days": 5, "dependencies": [], "milestone": false},
    {"id": "T2", "name": "Draft new intake form",
     "duration_days": 5, "dependencies": ["T1"], "milestone": false},
    {"id": "T7", "name": "Pilot complete",
     "duration_days": 0, "dependencies": ["T6"], "milestone": true}
  ]
}
```

- `project`: required, non-empty string.
- `start_date`: required, a valid `YYYY-MM-DD` date.
- `tasks`: non-empty list. Each task needs a unique non-empty `id`,
  a non-empty `name`, an integer `duration_days` >= 0, a
  `dependencies` list of task ids (default `[]`), and `milestone`
  (default `false`).
- Dates are **calendar days**: a 5-day task starting 2026-11-02 ends
  2026-11-06. Weekends are not skipped — if your org works business
  days only, convert durations before feeding them in.

## Usage

```bash
python3 scripts/wbs-scheduler.py examples/input.json --md out/wbs.md
# or: cat examples/input.json | python3 scripts/wbs-scheduler.py
```

Invalid input (circular dependency, unknown dependency, bad date,
duplicate id) exits non-zero with a clear error on stderr and writes
no output file. See `examples/invalid-input.json` (circular dependency
plus an unknown dependency).

## Design notes

The schedule uses the classic critical-path method: a forward pass
for earliest start/end, a backward pass from the project end for
latest start/end, and slack as the difference. A task with zero slack
is on the critical path. That is the whole trick — everything else is
formatting. It comes from the same operating-model work as the rest of
this pack, where the schedule that mattered was the one you could
recompute the morning a dependency slipped.

All sample data is fictional (Northlight Studios). Do not quote the
example numbers as results.
