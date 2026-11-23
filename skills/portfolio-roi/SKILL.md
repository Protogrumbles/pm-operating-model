# portfolio-roi

Roll up ROI across a portfolio of initiatives: per-initiative and
portfolio-total hours saved, gross value, net value, and ROI multiple
— the numbers that tell leadership whether the portfolio is paying
for itself.

## When to use it

- Leadership asks "what is all this AI tooling actually returning?"
  and wants one number, not five decks.
- You are deciding whether to renew, expand, or cut an initiative
  and need its net value next to its cost.
- The quarterly review needs a portfolio-total ROI line that adds up.

## What it computes

Same shape as the AI Adoption ROI Calculator, per initiative:

- **Gross $/yr** = hours saved/mo × loaded hourly cost × 12
- **Net $/yr** = gross $/yr − tool spend/mo × 12
- **ROI** = gross $/yr ÷ annual tool spend (shown as "n/a" when
  spend is zero — there is no cost to divide by)

The portfolio total sums hours, gross, and net across initiatives;
portfolio ROI is total gross ÷ total annual spend. A single
initiative's ROI is not averaged — the total is recomputed from the
summed dollars.

## Rules the calculator enforces

- **No negative inputs.** Negative hours saved or negative spend are
  rejected with a clear error — a negative saving is a cost, and it
  belongs in the spend column, not hidden in the hours.
- **At least one initiative is required.**

## Input format

```json
{
  "portfolio": "Northlight Studios — AI initiatives (sample data — fictional)",
  "initiatives": [
    {"name": "Support copilot rollout",
     "hours_saved_per_month": 180,
     "loaded_hourly_cost": 120,
     "ai_tool_spend_per_month": 900}
  ]
}
```

## Usage

```bash
python3 scripts/roi.py examples/input.json --md out/roi.md
# or: cat examples/input.json | python3 scripts/roi.py
```

## Anonymized worked example

`examples/verified-example.json` is built from the labeled,
anonymized anchor for this pack. It is labeled as such in the file
and in the output:

- Anonymized worked example (illustrative, not a promise): one team,
  600 hrs/mo saved, $1,015,200/yr net, 36.3x ROI.

Run it with:

```bash
python3 scripts/roi.py examples/verified-example.json --md out/verified-roi.md
```

Treat those numbers as what the pattern produced once, in one
context — not as a forecast for your portfolio. The hours-saved
figure is an input you supply and should come from a time study or
a measured before/after — not from this tool.
