# Intake Scores — Northlight Studios — Q1 intake (sample data — fictional)

## Scoring formula

All inputs are scored 1–5. Fit and ROI count positively; risk and effort count negatively by entering inverted (6 − value), so a riskier or heavier project scores lower:

```
score = w_fit × fit + w_roi × roi
      + w_risk × (6 − risk) + w_effort × (6 − effort)
```

Weights: strategic_fit 0.35, roi_estimate 0.30, risk 0.20, effort 0.15 (sum 1.00)

Thresholds: Fund ≥ 3.5 · Defer ≥ 2.5 · below 2.5 Reject

| Rank | Project | Fit | ROI | Risk | Effort | Score | Recommendation |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Unified asset pipeline | 5 | 5 | 2 | 3 | 4.50 | **Fund** |
| 2 | Creator payout automation | 4 | 4 | 3 | 2 | 3.80 | **Fund** |
| 3 | AI-assisted tagging | 3 | 4 | 2 | 2 | 3.65 | **Fund** |
| 4 | Live events platform | 4 | 3 | 4 | 5 | 2.85 | **Defer** |
| 5 | Legacy CMS migration | 2 | 2 | 4 | 4 | 2.00 | **Reject** |

## Summary

- Candidates scored: 5
- Fund: 3 · Defer: 1 · Reject: 1
