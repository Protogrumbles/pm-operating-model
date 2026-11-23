# tpm-rollout-planner

Build a phased rollout plan for an API or platform change: cohorts,
traffic percentages, dates, rollback criteria, and the comms plan — as
Markdown with cumulative traffic computed, not asserted.

## When to use it

- An API or platform change is going to real traffic and "just ship it"
  is not a plan.
- You need to say, in writing, who gets the change when and what sends
  it back.
- A rollout slipped and nobody can reconstruct which cohort was live
  when the errors started.
- Leadership asks for the rollout schedule and you want the dates,
  percentages, and rollback triggers in one page.

## Rules the planner enforces

- **Each phase's `traffic_percent` must be greater than 0.** A phase
  that ships to nobody is a phase that doesn't exist.
- **Cumulative traffic across phases must be at most 100%.** A plan
  that rolls out to 120% of traffic fails with a clear error.
- **Phases must run in order.** Each phase starts on or after the
  previous phase's end date (`start_date` + `duration_days`); overlapping
  or out-of-order dates fail.
- **`start_date` must be a valid `YYYY-MM-DD` date** and
  `duration_days` a positive integer.
- **`rollback_criteria` must be a non-empty list.** A rollout without a
  written rollback trigger is a hope, not a plan.

## Input format

```json
{
  "service": "Playback API v2",
  "phases": [
    {
      "name": "Canary",
      "cohort": "Internal employees",
      "traffic_percent": 5,
      "start_date": "2027-01-05",
      "duration_days": 7
    },
    {
      "name": "Early adopters",
      "cohort": "Opt-in creator accounts",
      "traffic_percent": 20,
      "start_date": "2027-01-12",
      "duration_days": 7
    }
  ],
  "rollback_criteria": ["Error rate exceeds 1% for 15 consecutive minutes."],
  "comms_plan": [
    {"audience": "Support", "channel": "#support", "message": "Canary starts Jan 5; no customer-facing change expected."}
  ]
}
```

## Usage

```bash
python3 scripts/rollout.py examples/input.json --md out/rollout.md
# or: cat examples/input.json | python3 scripts/rollout.py
```

Output is a Markdown plan: a phases table with per-phase traffic,
cumulative traffic, and computed end dates, followed by the rollback
criteria and the comms plan. Invalid input fails with an error on stderr
and a non-zero exit code — no plan is written.

## Design notes

The two numbers that get fudged in rollout plans are cumulative traffic
and phase dates, so the planner computes both from the input instead of
trusting them: cumulative traffic is a running sum, and end dates are
`start_date + duration_days`. If the plan says 5% then 20% then 75%, the
output says 5%, 25%, 100% — and if it says 110%, it fails loudly rather
than shipping a plan nobody can execute. Write rollback criteria as
observable thresholds (error rate, latency, a Sev attributed to the
change), not as vibes: "it feels wrong" is not a trigger anyone can act
on at 2am.
