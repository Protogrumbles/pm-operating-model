# project-charter-generator

Turn a project brief into a charter a sponsor can actually sign: the
problem, what's in and out of scope, how success is judged, who is
involved, and the risks — on one page.

## When to use it

- A project is starting and the scope lives in three different
  people's heads.
- A sponsor asks "what exactly are we doing?" and there is no
  one-page answer.
- Scope creep has already started and nobody can point at the line
  that was crossed.

## Rules the generator enforces

- **No empty scope.** `scope_in` must be a non-empty list. A charter
  with an empty scope authorizes nothing, so the CLI refuses it.
- **No success criteria, no charter.** `success_criteria` must be a
  non-empty list. If success can't be stated, the project isn't ready
  to start.
- **Scope out is mandatory, even if empty.** Saying what the project
  is *not* doing is half the charter. Use `[]` only when nothing is
  explicitly excluded.
- **Every stakeholder has a name and a role.** A stakeholder list
  without roles is a guest list, not accountability.
- **Every risk has a description.** Impact and mitigation are
  optional in the input but expected in the output — a risk with no
  mitigation is a risk accepted silently.

## Input format

```json
{
  "project": "Vendor Onboarding Redesign",
  "sponsor": "Dana Kim, Operations Director",
  "problem": "Onboarding a new vendor takes six weeks ...",
  "scope_in": ["Redesign the vendor intake form"],
  "scope_out": ["Renegotiating existing contracts"],
  "success_criteria": [
    {"criterion": "Median onboarding time", "measure": "6 weeks to 3 weeks"},
    "Pilot vendors onboarded with no tier-1 escalations"
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
```

- `project`, `problem`: required, non-empty strings.
- `scope_in`, `scope_out`: lists of strings. `scope_in` must be
  non-empty; `scope_out` must be present.
- `success_criteria`: list of strings, or objects with `criterion`
  and an optional `measure`. Must be non-empty.
- `stakeholders`: list of objects with `name` and `role`, plus an
  optional `responsibility`.
- `risks`: list of objects with `risk`, plus optional `impact` and
  `mitigation`.
- `sponsor`, `start_date`, `target_date`: optional metadata shown in
  the charter header.

## Usage

```bash
python3 scripts/charter.py examples/input.json --md out/charter.md
# or: cat examples/input.json | python3 scripts/charter.py
```

Invalid input (empty scope, missing success criteria, missing
stakeholder role) exits non-zero with a clear error on stderr and
writes no output file. See `examples/invalid-input.json`.

## Design notes

A charter is a contract, not a status update: it should fit on one
page and survive being read six months later by someone who wasn't in
the room. That is why the generator is strict about scope and success
criteria and lenient about everything else — the two things a charter
must do are draw the line and define "done". The pattern comes from
operating-model work where the first deliverable was never a plan but
a written agreement about what the work was and wasn't.

All sample data is fictional (Northlight Studios). Do not quote the
example numbers as results.
