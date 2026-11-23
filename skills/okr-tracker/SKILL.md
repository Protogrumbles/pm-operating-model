# okr-tracker

Score objectives and key results: % progress against target and a RAG
status you can defend in a review.

## When to use it

- Quarterly planning is done but nobody can say, mid-quarter, whether
  an objective is on track.
- A status update says "on track" for everything, which means it says
  nothing.
- You need one page that shows progress, confidence, and what's blocked.

## Scoring rules

- **% progress** = `(current − baseline) / (target − baseline)`, clamped
  to 0–100%. A key result that moves the wrong direction scores 0%.
  `lower_is_better` flips the math (e.g. escalations, cost).
- **RAG status** is computed from progress *and* the time elapsed in
  the period, not from vibes:
  - 🟢 On track: progress ≥ expected progress for the time elapsed
    (with a 10-point tolerance band).
  - 🟡 At risk: progress is behind expected but within 25 points.
  - 🔴 Off track: progress is more than 25 points behind expected, or
    the key result has regressed below baseline.
- **Objective score** is the mean of its key results' progress.
  An objective is only as green as its weakest key result: if any KR
  is 🔴, the objective is flagged 🔴 in the summary line.

## Input format

```json
{
  "period": "Q3 2026",
  "elapsed_pct": 50,
  "objectives": [
    {
      "title": "Cut escalations by 25%",
      "owner": "Priya Nair",
      "key_results": [
        {
          "title": "Weekly escalations",
          "baseline": 40, "current": 32, "target": 30,
          "lower_is_better": true
        }
      ]
    }
  ]
}
```

- `elapsed_pct`: how far through the period you are (0–100). Used for
  the expected-progress comparison.
- `lower_is_better`: set `true` for metrics you want to decrease
  (escalations, cost, time-to-resolve). Default `false`.

## Usage

```bash
python3 scripts/okr.py examples/input.json --md out/okrs.md
# or: cat examples/input.json | python3 scripts/okr.py
```

## Design notes

RAG without a time reference is fiction — a KR at 40% is fine in week 2
and a fire in week 11. This tracker always compares progress against
elapsed time, and says so in the output. The ~25% escalation reduction
and ~65–70% first-contact-resolution improvement cited in this pack's
root SKILL.md are the verified outcomes from the operating-model work
these patterns come from; the example input here is fictional sample
data.
