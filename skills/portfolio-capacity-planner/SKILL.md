# portfolio-capacity-planner

Compare capacity vs demand per team per quarter, and flag overload
and underuse before they become missed dates or idle teams.

## When to use it

- The intake list is approved and you need to know whether the teams
  can actually absorb it this quarter.
- A team keeps missing dates and nobody can say whether it is
  overcommitted or just unlucky.
- You are sequencing work across quarters and need to see where the
  slack is.

## Rules the planner enforces

- **Demand must reference a known team.** A demand item naming a
  team not listed in `teams` is rejected with a clear error — a typo
  in a team name must not silently drop work from the plan.
- **Hours must be non-negative.** Negative hours are rejected.
- **Capacity must be a positive number** per team per quarter.

## What it computes

Per team per quarter:

- **Capacity** (hrs) — from the `teams` list.
- **Demand** (hrs) — demand items summed for that team and quarter.
- **Utilisation %** — demand ÷ capacity × 100.
- **Flag** — `⚠️ OVERLOAD` when utilisation is over 100% (demand
  exceeds capacity), `ℹ️ UNDERUSED` when it is under 50% (less than
  half the team's capacity is spoken for), otherwise `OK`.

Every team is shown for every quarter that appears in the demand
list, including quarters with zero demand — a team with nothing
scheduled is underused, not invisible.

## Input format

```json
{
  "portfolio": "Northlight Studios — capacity plan (sample data — fictional)",
  "teams": [
    {"name": "Platform", "capacity_hours_per_quarter": 480}
  ],
  "demand": [
    {"project": "Unified asset pipeline", "team": "Platform",
     "quarter": "Q1", "hours": 300}
  ]
}
```

## Usage

```bash
python3 scripts/capacity.py examples/input.json --md out/capacity.md
# or: cat examples/input.json | python3 scripts/capacity.py
```

Output is a Markdown table per team per quarter with capacity,
demand, utilisation, and flag, plus a summary count of overloaded
and underused team-quarters.

## Design notes

Capacity planning is a sequencing tool, not a hiring plan. An
OVERLOAD flag means the quarter's demand does not fit the team as
staffed — the fix is to defer, descope, or move work, and the table
shows exactly which quarter to move it to. An UNDERUSED flag is
equally useful: it is where deferred work can land without a fight.
