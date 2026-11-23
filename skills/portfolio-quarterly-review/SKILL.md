# portfolio-quarterly-review

Generate a quarterly portfolio review pack from wins, at-risk items,
and decisions needed — the one document the review meeting actually
runs from.

## When to use it

- The quarterly portfolio review is coming up and the pack is
  currently five decks and a spreadsheet.
- Leadership needs to see what shipped, what is at risk, and what
  they need to decide — on one page each, not buried in status
  updates.
- You want the review to end with decisions, not with "let's take
  that offline."

## Rules the generator enforces

- **Every at-risk item must name a mitigation.** An at-risk item
  with no mitigation (missing or blank) is rejected with a clear
  error. A risk without a plan is not a review item — it is a
  surprise waiting to happen.
- **Every decision needed must name an owner and a due date.** A
  decision with no owner is rejected; a decision nobody owns is a
  decision nobody makes.

## Input format

```json
{
  "portfolio": "Northlight Studios (sample data — fictional)",
  "quarter": "Q3 2026",
  "wins": ["Shipped the unified asset pipeline on time."],
  "at_risk": [
    {"project": "Live events platform",
     "reason": "Streaming vendor delivery slipped two weeks.",
     "mitigation": "Stand up a fallback streaming vendor by Oct 15."}
  ],
  "decisions_needed": [
    {"decision": "Approve the Q4 live events budget",
     "owner": "Dana Kim", "due": "2026-10-20"}
  ]
}
```

## Usage

```bash
python3 scripts/review.py examples/input.json --md out/review.md
# or: cat examples/input.json | python3 scripts/review.py
```

Output is a Markdown review pack: a wins list, an at-risk table
(project, reason, mitigation), and a decisions-needed table
(decision, owner, due date), plus a summary count of each.

## Design notes

A review pack works when it is short enough to read before the
meeting and structured enough to run the meeting from. Wins go
first so the review opens on evidence, not anxiety. At-risk items
are paired with their mitigation in the same row, so nobody has to
ask "so what are we doing about it?" Decisions are the last section
because they are the point of the meeting: each one leaves with an
owner and a date, or it was not a decision.
