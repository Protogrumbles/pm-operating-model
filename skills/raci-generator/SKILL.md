# raci-generator

Build a RACI matrix for a program from its decisions and its people.

## When to use it

- A program is starting and nobody can say who decides what.
- Two teams both think they own the same decision (or neither does).
- You're redesigning an operating model and need the decision rights
  written down before the org chart changes.

## Rules the generator enforces

- **Exactly one Accountable per decision.** Zero or two+ is flagged as an
  error in the output, not silently accepted. This is the single most
  common operating-model failure: a decision with no owner, or two.
- **At least one Responsible per decision.** A decision nobody executes
  is a wish.
- **Consulted and Informed are optional**, but a decision with no
  Consulted and no Informed usually means nobody knows it happened.
- Valid roles: `R` (Responsible — does the work), `A` (Accountable —
  owns the outcome, exactly one), `C` (Consulted — input before the
  decision), `I` (Informed — told after the decision).

## Input format

```json
{
  "program": "Vendor Onboarding Redesign",
  "people": [
    {"name": "Priya Nair", "role": "Program Manager"},
    {"name": "Marcus Chen", "role": "Procurement Lead"}
  ],
  "decisions": [
    {
      "id": "D1",
      "title": "Approve a new vendor",
      "assignments": {"Priya Nair": "A", "Marcus Chen": "R"}
    }
  ]
}
```

- `people[].name` must match the keys in `decisions[].assignments`
  exactly; unknown names are reported as errors.
- `assignments` values must be one of `R`, `A`, `C`, `I` (a person can
  hold only one letter per decision).

## Usage

```bash
python3 scripts/raci.py examples/input.json --md out/raci.md --csv out/raci.csv
# or: cat examples/input.json | python3 scripts/raci.py
```

Output is a Markdown table plus a CSV with the same matrix, followed by
a validation section listing any decisions that break the rules above.

## Design notes

This pattern comes from a 180-person operating-model redesign where the
first deliverable was not a new org chart but a decision-rights map:
every recurring decision, one accountable owner, named explicitly.
The org chart followed the decisions, not the other way around.
