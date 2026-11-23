# adoption-telemetry

Turn weekly adoption numbers into a one-page summary: adoption %,
trend, escalations, and hours saved — the numbers that tell you whether
a new operating model is actually landing.

## When to use it

- A new tool, process, or operating model launched and leadership asks
  "is it working?" every week.
- Adoption is flat and you need to show whether it's a training problem,
  a workflow problem, or a "nobody was asked" problem.
- You need a defensible hours-saved figure, not a vibes-based one.

## What it computes

- **Adoption %** per week: `active_users / eligible_users`.
- **Trend**: week-over-week change in adoption, in percentage points.
- **Escalations**: raw count and change vs. the prior week.
- **Hours saved**: `active_users × hours_saved_per_user_per_week`,
  summed across weeks. The per-user figure is an input you supply and
  should come from a time study or a measured before/after — not from
  this tool.
- **Rollout pace**: eligible users onboarded per week, so you can see
  whether slow adoption is a rollout problem or a usage problem.

## Input format

```json
{
  "program": "Risk Platform Rollout (sample data — fictional)",
  "hours_saved_per_user_per_week": 2.5,
  "weeks": [
    {"week": "W1", "eligible_users": 120, "active_users": 48,
     "escalations": 22}
  ]
}
```

## Usage

```bash
python3 scripts/telemetry.py examples/input.json --md out/telemetry.md
# or: cat examples/input.json | python3 scripts/telemetry.py
```

## Anonymized worked example

`examples/verified-example.json` is built from the real operating-model
work this pack is grounded in, with identifying details removed. It is
labeled as such in the file and in the output. The verified outcomes:

- 600-person operating-model redesign; risk platform across 57
  productions in ~8 weeks (5–7x faster than the prior approach).
- Escalations down ~25%; first-contact resolution up ~65–70%.
- $2.5M/yr recovered; ~600 hrs/mo saved.

Run it with:

```bash
python3 scripts/telemetry.py examples/verified-example.json --md out/verified-telemetry.md
```

Treat those numbers as what the pattern produced once, in one context —
not as a forecast for your rollout.
