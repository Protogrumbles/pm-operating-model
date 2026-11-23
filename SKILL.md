# pm-operating-model

A Claude Code / Codex / Cursor skill pack for people who run projects,
programs, technical programs, and portfolios. Seventeen skills, each
with a working CLI (except `stakeholder-report`, which is templates),
grounded in patterns from a real 600-person operating-model redesign
and a risk platform rolled out across 57 productions in ~8 weeks.

## What this pack is

Most PM tooling helps you track tasks. This pack helps you design the
system the tasks live in — at every altitude:

- **Project:** charter the work, schedule it, track risks and issues,
  report status by rule.
- **Program:** who decides what (RACI), how issues escalate (tiers and
  SLAs), whether the work is actually moving the objective (OKRs),
  whether people are adopting the new way of working (telemetry), and
  how to report all of it to stakeholders without a status-meeting
  death spiral.
- **Technical Program:** decide (ADRs), roll out (phases, cohorts,
  rollback), cut over (go/no-go gates), and review incidents (blameless
  Sev reviews).
- **Portfolio:** score intake, check capacity, roll up ROI, and run the
  quarterly review that decides what gets funded next.

## Skills

### Project lane

| Skill | What it does | CLI |
|---|---|---|
| `project-charter-generator` | Turns a project brief into a signable charter: problem, scope, success criteria, stakeholders, risks | `scripts/charter.py` |
| `project-wbs-scheduler` | Work breakdown + dated schedule from tasks and dependencies, with critical path and milestones | `scripts/wbs-scheduler.py` |
| `project-raid-log` | RAID log with fixed severity/status vocabularies and an open Critical/High summary | `scripts/raid.py` |
| `project-status-report` | Weekly status report with RAG derived by rule from milestones and RAID counts | `scripts/status-report.py` |

### Program lane

| Skill | What it does | CLI |
|---|---|---|
| `raci-generator` | Builds a RACI matrix from a program's decisions and people | `scripts/raci.py` |
| `escalation-designer` | Designs tiered escalation workflows with owners and SLAs | `scripts/escalation.py` |
| `okr-tracker` | Scores objectives and key results with % progress and RAG status | `scripts/okr.py` |
| `adoption-telemetry` | Summarizes weekly adoption, trend, escalations, hours saved | `scripts/telemetry.py` |
| `stakeholder-report` | Weekly stakeholder update template + worked example | `templates/` |

### Technical Program lane

| Skill | What it does | CLI |
|---|---|---|
| `tpm-adr-writer` | Architecture decision records: context, decision, alternatives, consequences | `scripts/adr.py` |
| `tpm-rollout-planner` | API/platform rollout planner: phases, cohorts, rollback criteria, comms | `scripts/rollout.py` |
| `tpm-cutover-checklist` | Migration cutover checklist with go/no-go gates | `scripts/cutover.py` |
| `tpm-sev-review` | Blameless incident/Sev review template + timeline builder | `scripts/sev.py` |

Companion skill: RAILGUARD (github.com/Protogrumbles/Rail-Guard) —
the security-review skill for AI coding assistants; a review
framework, not a scanner. See `skills/tpm-lane-README.md`.

### Portfolio lane

| Skill | What it does | CLI |
|---|---|---|
| `portfolio-intake-scorer` | Scores project intake (strategic fit, ROI, risk, effort) into a ranked Fund / Defer / Reject list | `scripts/scorer.py` |
| `portfolio-capacity-planner` | Capacity vs. demand across teams and quarters, with overload flags | `scripts/capacity.py` |
| `portfolio-roi` | Portfolio ROI roll-up: hours saved, gross/net $/yr, ROI multiple per initiative and in total | `scripts/roi.py` |
| `portfolio-quarterly-review` | Quarterly portfolio review pack: wins, at-risk items, decisions needed | `scripts/review.py` |

## Verified results this pack is grounded in

These are real outcomes from the operating-model work the patterns come
from, anonymized and labeled where they appear. They are not promises —
they are what the pattern produced once, in one context.

- 600-person operating-model redesign, commissioned by a senior director.
- Risk platform built across 57 productions in ~8 weeks — roughly 5–7x
  faster than the prior approach.
- Escalations cut ~25%; first-contact resolution improved ~65–70%.
- $2.5M/yr recovered; ~600 hrs/mo saved.

The portfolio ROI worked example (`skills/portfolio-roi/examples/
verified-example.json`) is a labeled, anonymized illustration of one
team: 600 hrs/mo saved, $1,015,200/yr net, 36.3x ROI. Illustrative,
not a promise.

All other numbers in this pack — every example input, worked example, and
template — are fictional sample data, clearly labeled as such.

## Quick start

```bash
# PROJECT lane
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

# PROGRAM lane
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

# TECHNICAL PROGRAM lane
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

# PORTFOLIO lane
python3 skills/portfolio-intake-scorer/scripts/scorer.py \
  skills/portfolio-intake-scorer/examples/input.json \
  --md out/intake.md

python3 skills/portfolio-capacity-planner/scripts/capacity.py \
  skills/portfolio-capacity-planner/examples/input.json \
  --md out/capacity.md

python3 skills/portfolio-roi/scripts/roi.py \
  skills/portfolio-roi/examples/input.json \
  --md out/portfolio-roi.md

python3 skills/portfolio-quarterly-review/scripts/review.py \
  skills/portfolio-quarterly-review/examples/input.json \
  --md out/quarterly-review.md
```

Every script is dependency-free Python 3 (standard library only) and reads
JSON on stdin or from a file, writing Markdown (and CSV where applicable)
to stdout or a file.

## Honest scope

- These are design and reporting aids, not a PMIS. They do not integrate
  with Jira, Asana, or any ticketing system.
- The CLIs are deterministic: same input, same output. They do not call
  any API and they do not learn from your data.
- RAG statuses, escalation tiers, and intake scores are heuristics you
  configure, not judgments the tool makes for you. If a threshold is
  wrong for your org, change the input, not the tool.
- Sample data is fictional. Do not quote the example numbers as results.

## Install

See [INSTALL.md](INSTALL.md) for Claude Code, Codex, and Cursor setup.
