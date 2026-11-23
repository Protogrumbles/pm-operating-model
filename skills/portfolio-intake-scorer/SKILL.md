# portfolio-intake-scorer

Score project intake candidates on a common 1–5 scale and rank them
for funding decisions — so the portfolio conversation starts from
numbers, not whoever argued loudest.

## When to use it

- Intake season arrives and ten projects are competing for three slots.
- A sponsor asks "why did this get funded and mine didn't?" and you
  need a defensible answer.
- You want the trade-off between strategic fit, ROI, risk, and effort
  written down before the meeting, not negotiated in it.

## Rules the scorer enforces

- **Every score is a whole number from 1 to 5.** A score outside 1–5
  is rejected with a clear error — a bad input must not silently
  become a bad ranking.
- **Weights must sum to 1.** The default weights are strategic fit
  0.35, ROI 0.30, risk 0.20, effort 0.15; override them in the input
  if your portfolio values the dimensions differently.
- **Risk and effort count against the score.** They enter inverted
  (6 − value), so a riskier or heavier project scores lower even if
  its fit and ROI are strong.
- **Thresholds are explicit inputs**, not hidden in the code:
  Fund ≥ 3.5, Defer ≥ 2.5, below that Reject (defaults; override in
  the input).

## What it computes

```
score = w_fit × fit + w_roi × roi
      + w_risk × (6 − risk) + w_effort × (6 − effort)
```

The score stays on a 1–5 scale. Candidates are ranked highest first,
each with a recommendation: **Fund**, **Defer**, or **Reject**.

## Input format

```json
{
  "portfolio": "Northlight Studios — Q1 intake (sample data — fictional)",
  "weights": {"strategic_fit": 0.35, "roi_estimate": 0.30,
              "risk": 0.20, "effort": 0.15},
  "thresholds": {"fund": 3.5, "defer": 2.5},
  "projects": [
    {"name": "Unified asset pipeline", "strategic_fit": 5,
     "roi_estimate": 5, "risk": 2, "effort": 3}
  ]
}
```

`weights` and `thresholds` are optional — omit them to use the
defaults above. `risk` and `effort` are scored 1–5 where higher means
riskier / more effort.

## Usage

```bash
python3 scripts/scorer.py examples/input.json --md out/intake.md
# or: cat examples/input.json | python3 scripts/scorer.py
```

Output is a ranked Markdown table with the formula, weights, and
thresholds shown, plus a Fund / Defer / Reject count.

## Design notes

Scoring does not make the decision — it makes the decision
explainable. A ranked list with the formula printed on it lets a
sponsor argue with the weights or the inputs instead of with the
program manager. If a project scores low, the table shows whether
it was fit, ROI, risk, or effort that sank it.
