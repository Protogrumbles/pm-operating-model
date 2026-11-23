# pm-operating-model

A skill pack for people who run projects, programs, technical programs,
and portfolios — not just one of them. Seventeen skills, each with a
working CLI, for Claude Code, Codex, and Cursor, in four lanes:

- **Project** — run one project end to end: charter, schedule, RAID log,
  status report.
- **Program** — run the operating model: RACI, escalation, OKRs, adoption
  telemetry, stakeholder reporting.
- **Technical Program** — decide, roll out, cut over, review: ADRs,
  rollout plans, cutover gates, Sev reviews.
- **Portfolio** — decide what to fund: intake scoring, capacity,
  ROI roll-up, quarterly review.

Grounded in patterns from a real 600-person operating-model redesign
and a risk platform rolled out across 57 productions in ~8 weeks.

## The skills

### Project lane

| Skill | What it does |
|---|---|
| [project-charter-generator](skills/project-charter-generator/SKILL.md) | Turns a project brief into a signable charter: problem, scope in/out, success criteria, stakeholders, risks |
| [project-wbs-scheduler](skills/project-wbs-scheduler/SKILL.md) | Work breakdown + dated schedule from tasks and dependencies, with critical path and milestones |
| [project-raid-log](skills/project-raid-log/SKILL.md) | RAID log (Risks, Assumptions, Issues, Dependencies) with fixed severity/status vocabularies and an open Critical/High summary |
| [project-status-report](skills/project-status-report/SKILL.md) | Weekly status report with RAG derived by rule from milestones and RAID counts |

### Program lane

| Skill | What it does |
|---|---|
| [raci-generator](skills/raci-generator/SKILL.md) | Builds a RACI matrix from decisions and people; flags decisions with zero or two+ Accountable owners |
| [escalation-designer](skills/escalation-designer/SKILL.md) | Designs tiered escalation workflows with owners, SLAs, and a Mermaid flowchart |
| [okr-tracker](skills/okr-tracker/SKILL.md) | Scores OKRs — % progress and RAG status computed against time elapsed, not vibes |
| [adoption-telemetry](skills/adoption-telemetry/SKILL.md) | Weekly adoption summary: adoption %, trend, escalations, hours saved |
| [stakeholder-report](skills/stakeholder-report/SKILL.md) | One-page weekly stakeholder update template + worked example |

### Technical Program lane

| Skill | What it does |
|---|---|
| [tpm-adr-writer](skills/tpm-adr-writer/SKILL.md) | Architecture decision records: context, decision, alternatives, consequences |
| [tpm-rollout-planner](skills/tpm-rollout-planner/SKILL.md) | API/platform rollout planner: phases, cohorts, rollback criteria, comms |
| [tpm-cutover-checklist](skills/tpm-cutover-checklist/SKILL.md) | Migration cutover checklist with go/no-go gates |
| [tpm-sev-review](skills/tpm-sev-review/SKILL.md) | Blameless incident/Sev review template + timeline builder |

Companion skill: [RAILGUARD](https://github.com/Protogrumbles/Rail-Guard)
— the security-review skill for AI coding assistants. It is a review
framework, not a scanner; see
[skills/tpm-lane-README.md](skills/tpm-lane-README.md).

### Portfolio lane

| Skill | What it does |
|---|---|
| [portfolio-intake-scorer](skills/portfolio-intake-scorer/SKILL.md) | Scores project intake (strategic fit, ROI, risk, effort) into a ranked Fund / Defer / Reject list |
| [portfolio-capacity-planner](skills/portfolio-capacity-planner/SKILL.md) | Capacity vs. demand across teams and quarters, with overload flags |
| [portfolio-roi](skills/portfolio-roi/SKILL.md) | Portfolio ROI roll-up: hours saved, gross/net $/yr, ROI multiple per initiative and in total |
| [portfolio-quarterly-review](skills/portfolio-quarterly-review/SKILL.md) | Quarterly portfolio review pack: wins, at-risk items, decisions needed |

## What it's grounded in

The patterns in this pack come from real operating-model work: a
600-person operating-model redesign commissioned by a senior director,
and a risk platform built across 57 productions in ~8 weeks (roughly
5–7x faster than the prior approach). Verified outcomes from that work:

- Escalations cut ~25%; first-contact resolution improved ~65–70%
- $2.5M/yr recovered; ~600 hrs/mo saved

Those numbers appear only where labeled as verified outcomes. Every
example input, worked example, and template in this pack uses fictional
sample data, except the labeled anonymized ROI worked example in
`skills/portfolio-roi/examples/verified-example.json` (one team,
600 hrs/mo saved, $1,015,200/yr net, 36.3x ROI — illustrative, not a
promise).

## Install

See [INSTALL.md](INSTALL.md). Short version: copy `skills/*` into your
tool's skills folder (`~/.claude/skills/`, `~/.codex/skills/`, or
`.cursor/skills/`). No dependencies beyond Python 3.8+.

## Example commands

```bash
# PROJECT lane — charter, schedule, RAID log, status report
python3 skills/project-charter-generator/scripts/charter.py \
  skills/project-charter-generator/examples/input.json \
  --md out/charter.md

python3 skills/project-wbs-scheduler/scripts/wbs-scheduler.py \
  skills/project-wbs-scheduler/examples/input.json \
  --md out/wbs.md

python3 skills/project-raid-log/scripts/raid.py \
  skills/project-raid-log/examples/input.json \
  --md out/raid.md

python3 skills/project-status-report/scripts/status-report.py \
  skills/project-status-report/examples/input.json \
  --md out/status.md

# PROGRAM lane — RACI, escalation, OKRs, telemetry
python3 skills/raci-generator/scripts/raci.py \
  skills/raci-generator/examples/input.json \
  --md out/raci.md --csv out/raci.csv

python3 skills/escalation-designer/scripts/escalation.py \
  skills/escalation-designer/examples/input.json \
  --md out/escalation.md

python3 skills/okr-tracker/scripts/okr.py \
  skills/okr-tracker/examples/input.json \
  --md out/okrs.md

python3 skills/adoption-telemetry/scripts/telemetry.py \
  skills/adoption-telemetry/examples/input.json \
  --md out/telemetry.md

# TECHNICAL PROGRAM lane — ADR, rollout, cutover, Sev review
python3 skills/tpm-adr-writer/scripts/adr.py \
  skills/tpm-adr-writer/examples/input.json \
  --md out/adr.md

python3 skills/tpm-rollout-planner/scripts/rollout.py \
  skills/tpm-rollout-planner/examples/input.json \
  --md out/rollout.md

python3 skills/tpm-cutover-checklist/scripts/cutover.py \
  skills/tpm-cutover-checklist/examples/input.json \
  --md out/cutover.md

python3 skills/tpm-sev-review/scripts/sev.py \
  skills/tpm-sev-review/examples/input.json \
  --md out/sev-review.md

# PORTFOLIO lane — intake, capacity, ROI, quarterly review
python3 skills/portfolio-intake-scorer/scripts/scorer.py \
  skills/portfolio-intake-scorer/examples/input.json \
  --md out/intake.md

python3 skills/portfolio-capacity-planner/scripts/capacity.py \
  skills/portfolio-capacity-planner/examples/input.json \
  --md out/capacity.md

python3 skills/portfolio-roi/scripts/roi.py \
  skills/portfolio-roi/examples/input.json \
  --md out/portfolio-roi.md

# Portfolio ROI — anonymized worked example (illustrative, not a promise)
python3 skills/portfolio-roi/scripts/roi.py \
  skills/portfolio-roi/examples/verified-example.json \
  --md out/verified-portfolio-roi.md

python3 skills/portfolio-quarterly-review/scripts/review.py \
  skills/portfolio-quarterly-review/examples/input.json \
  --md out/quarterly-review.md
```

Every script also reads JSON from stdin and writes Markdown to stdout
when no output path is given. Run any script with `--help` for flags.

## Honest scope

- Design and reporting aids, not a PMIS. No Jira/Asana integration.
- Deterministic CLIs: same input, same output. No APIs, no learning
  from your data.
- RAG statuses, escalation tiers, and intake scores are heuristics you
  configure. If a threshold is wrong for your org, change the input.
- Sample data is fictional. Do not quote the example numbers as results.
- The portfolio ROI worked example is anonymized and illustrative. It
  is not a promise of savings.

## Layout

```
pm-operating-model/
├── SKILL.md                      # Pack overview
├── README.md                     # This file
├── INSTALL.md                    # Claude Code / Codex / Cursor setup
├── .claude-plugin/plugin.json    # Plugin manifest (all 17 skills)
└── skills/
    ├── project-charter-generator/
    ├── project-wbs-scheduler/
    ├── project-raid-log/
    ├── project-status-report/
    ├── raci-generator/
    ├── escalation-designer/
    ├── okr-tracker/
    ├── adoption-telemetry/
    ├── stakeholder-report/       # templates/, no CLI
    ├── tpm-adr-writer/
    ├── tpm-rollout-planner/
    ├── tpm-cutover-checklist/
    ├── tpm-sev-review/
    ├── tpm-lane-README.md
    ├── portfolio-intake-scorer/
    ├── portfolio-capacity-planner/
    ├── portfolio-roi/
    └── portfolio-quarterly-review/
```

Each skill folder holds `SKILL.md`, `scripts/<name>.py`, and `examples/`
with `input.json` and CLI-generated `output.md` (plus `verified-example.*`
where a labeled worked example exists).

## Author

Sean Steuer — Senior Program Manager, AI Strategy & Operational
Transformation at Netflix. [seansteuer.com](https://seansteuer.com)
