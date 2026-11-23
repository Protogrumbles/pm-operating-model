# tpm-cutover-checklist

Build a migration cutover checklist with go/no-go gates: items grouped by
category, counts, and a GO/NO-GO verdict computed from the items — not
from whoever is most confident in the room.

## When to use it

- A migration cutover is scheduled and "are we ready?" needs an answer
  you can point at.
- The go/no-go meeting is about to become an argument about vibes.
- A cutover failed last time and nobody can say which check was skipped.
- You need a written record of what was verified, by whom, before the
  switch was flipped.

## Rules the checklist enforces

- **Item status must be one of `Pass`, `Fail`, `Pending`, `Blocked`.**
  Anything else fails with a clear error.
- **Gate status must be one of `Pass`, `Fail`, `Pending`.**
- **Item and gate ids must be unique** within their own lists.
- **`required` must be a boolean** — every item is either required or
  it isn't; there is no "sort of required."

## The verdict

- **NO-GO** if any required item is `Fail` or `Blocked`, or any gate is
  `Fail`. The output lists every blocking issue.
- **GO** otherwise — and the checklist still shows the counts, so a GO
  with several optional items pending is visible, not hidden.
- A `Pending` gate does not by itself force NO-GO, but it is flagged
  prominently in the output: do not cut over with an uncleared gate.

Exit code is 0 on GO, 1 on NO-GO, 2 on invalid input. A NO-GO is a
result, not a crash: the Markdown is still written.

## Input format

```json
{
  "migration": "Billing database migration",
  "cutover_date": "2027-02-14",
  "items": [
    {
      "id": "C1",
      "description": "Final snapshot taken and verified restorable",
      "owner": "Dana Kim",
      "category": "Data",
      "required": true,
      "status": "Pass"
    }
  ],
  "gates": [
    {
      "id": "G1",
      "name": "Data integrity gate",
      "criterion": "Row counts match between source and target",
      "status": "Pass"
    }
  ]
}
```

## Usage

```bash
python3 scripts/cutover.py examples/input.json --md out/cutover.md
# or: cat examples/input.json | python3 scripts/cutover.py
```

Output is a Markdown checklist grouped by category, with counts, the
verdict, and the gates. Invalid input fails with an error on stderr and
exit code 2 — no checklist is written.

## Design notes

The failure mode this skill exists to prevent is the cutover that went
ahead because nobody wanted to be the person who said no. The verdict is
mechanical on purpose: required items and gates decide it, and the
meeting's job is to argue about the items, not about whether the verdict
is "fair." Keep the required set small — if everything is required,
nothing is — and put rollback rehearsal in the required set, not the
nice-to-have set. A rollback you have never rehearsed is a rollback you
do not have.
