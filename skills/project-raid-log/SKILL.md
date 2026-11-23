# project-raid-log

Keep Risks, Assumptions, Issues, and Dependencies in one log, with
severity and status from a fixed vocabulary — so "high priority" means
the same thing to everyone reading it.

## When to use it

- Risks live in chat threads and nobody can say which are still open.
- A status meeting argues about whether something is an issue or a
  risk instead of what to do about it.
- You need the open Critical and High items on one page before a
  sponsor review.

## Rules the generator enforces

- **Fixed vocabularies, no free text.** `type` must be Risk,
  Assumption, Issue, or Dependency. `severity` must be Critical,
  High, Medium, or Low. `status` must be Open, Monitoring, Mitigated,
  or Closed. Anything else is rejected with a clear error — a
  severity of "Severe" or "urgent!!" doesn't sort, doesn't count, and
  doesn't survive a handoff.
- **Every entry has an owner.** An unowned risk is a risk nobody is
  watching.
- **Every entry has a title.** If it can't be titled, it can't be
  tracked.
- **Open Critical/High items are surfaced first.** The summary leads
  with them, before the grouped log — the point of the log is the
  attention list, not the archive.

## Input format

```json
{
  "project": "Vendor Onboarding Redesign",
  "entries": [
    {"id": "R1", "type": "Risk",
     "title": "Legal review becomes a bottleneck",
     "severity": "High", "owner": "Sofia Reyes", "status": "Open",
     "mitigation": "Pre-agreed review SLA with a backup reviewer"},
    {"id": "A1", "type": "Assumption",
     "title": "Average onboarding time stays at 6 weeks",
     "severity": "Medium", "owner": "Tom Okafor", "status": "Open",
     "note": "If the average rises, revisit the charter criteria"}
  ]
}
```

- `project`: optional, defaults to "Untitled Project".
- `entries`: list of objects. `id` is optional but recommended
  (R1, A1, I1, D1 by type). `title` and `owner` are required.
- `mitigation` (for risks/issues) or `note` (for assumptions/
  dependencies) is optional but expected — the output shows whichever
  is present.
- A bare JSON list of entries is also accepted (no `project` wrapper).

## Usage

```bash
python3 scripts/raid.py examples/input.json --md out/raid.md
# or: cat examples/input.json | python3 scripts/raid.py
```

Invalid input (bad severity, bad status, bad type, missing owner)
exits non-zero with a clear error on stderr and writes no output
file. See `examples/invalid-input.json` (severity "Severe").

## Design notes

RAID only works when the words mean the same thing every week, which
is why the CLI is strict about vocabulary and lenient about nothing
else. The output is grouped by type with counts, and the open
Critical/High items lead — because the log exists to direct attention,
not to record history. It pairs with `project-status-report`, which
takes the open Critical/High counts as its RAG input.

All sample data is fictional (Northlight Studios). Do not quote the
example numbers as results.
