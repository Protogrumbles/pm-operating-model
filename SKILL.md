# pm-operating-model

A Claude Code / Codex / Cursor skill pack for program managers who run
operating models, not just projects. Five skills, each with a working CLI,
grounded in patterns from a real 600-person operating-model redesign and a
risk platform rolled out across 57 productions in ~8 weeks.

## What this pack is

Most PM tooling helps you track tasks. This pack helps you design the system
the tasks live in: who decides what (RACI), how issues escalate (tiers and
SLAs), whether the work is actually moving the objective (OKRs), whether
people are adopting the new way of working (telemetry), and how to report
all of it to stakeholders without a status-meeting death spiral.

## Skills

| Skill | What it does | CLI |
|---|---|---|
| `raci-generator` | Builds a RACI matrix from a program's decisions and people | `scripts/raci.py` |
| `escalation-designer` | Designs tiered escalation workflows with owners and SLAs | `scripts/escalation.py` |
| `okr-tracker` | Scores objectives and key results with % progress and RAG status | `scripts/okr.py` |
| `adoption-telemetry` | Summarizes weekly adoption, trend, escalations, hours saved | `scripts/telemetry.py` |
| `stakeholder-report` | Weekly stakeholder update template + worked example | `templates/` |

## Verified results this pack is grounded in

These are real outcomes from the operating-model work the patterns come
from, anonymized and labeled where they appear. They are not promises —
they are what the pattern produced once, in one context.

- 600-person operating-model redesign, commissioned by a senior director.
- Risk platform built across 57 productions in ~8 weeks — roughly 5–7x
  faster than the prior approach.
- Escalations cut ~25%; first-contact resolution improved ~65–70%.
- $2.5M/yr recovered; ~600 hrs/mo saved.

All other numbers in this pack — every example input, worked example, and
template — are fictional sample data, clearly labeled as such.

## Quick start

```bash
# RACI matrix from a JSON input
python3 skills/raci-generator/scripts/raci.py \
  skills/raci-generator/examples/input.json \
  --md out/raci.md --csv out/raci.csv

# Escalation workflow
python3 skills/escalation-designer/scripts/escalation.py \
  skills/escalation-designer/examples/input.json \
  --md out/escalation.md

# OKR tracker
python3 skills/okr-tracker/scripts/okr.py \
  skills/okr-tracker/examples/input.json \
  --md out/okrs.md

# Adoption telemetry (includes the anonymized worked example)
python3 skills/adoption-telemetry/scripts/telemetry.py \
  skills/adoption-telemetry/examples/input.json \
  --md out/telemetry.md
```

Every script is dependency-free Python 3 (standard library only) and reads
JSON on stdin or from a file, writing Markdown (and CSV where applicable)
to stdout or a file.

## Honest scope

- These are design and reporting aids, not a PMIS. They do not integrate
  with Jira, Asana, or any ticketing system.
- The CLIs are deterministic: same input, same output. They do not call
  any API and they do not learn from your data.
- RAG statuses and escalation tiers are heuristics you configure, not
  judgments the tool makes for you. If a threshold is wrong for your org,
  change the input, not the tool.
- Sample data is fictional. Do not quote the example numbers as results.

## Install

See [INSTALL.md](INSTALL.md) for Claude Code, Codex, and Cursor setup.
