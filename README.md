# pm-operating-model

A skill pack for program managers who run operating models, not just
projects. Five skills, each with a working CLI, for Claude Code, Codex,
and Cursor.

## The skills

| Skill | What it does |
|---|---|
| [raci-generator](skills/raci-generator/SKILL.md) | Builds a RACI matrix from decisions and people; flags decisions with zero or two+ Accountable owners |
| [escalation-designer](skills/escalation-designer/SKILL.md) | Designs tiered escalation workflows with owners, SLAs, and a Mermaid flowchart |
| [okr-tracker](skills/okr-tracker/SKILL.md) | Scores OKRs — % progress and RAG status computed against time elapsed, not vibes |
| [adoption-telemetry](skills/adoption-telemetry/SKILL.md) | Weekly adoption summary: adoption %, trend, escalations, hours saved |
| [stakeholder-report](skills/stakeholder-report/SKILL.md) | One-page weekly stakeholder update template + worked example |

## What it's grounded in

The patterns in this pack come from real operating-model work: a
600-person operating-model redesign commissioned by a senior director,
and a risk platform built across 57 productions in ~8 weeks (roughly
5–7x faster than the prior approach). Verified outcomes from that work:

- Escalations cut ~25%; first-contact resolution improved ~65–70%
- $2.5M/yr recovered; ~600 hrs/mo saved

Those numbers appear only where labeled as verified outcomes. Every
example input, worked example, and template in this pack uses fictional
sample data.

## Install

See [INSTALL.md](INSTALL.md). Short version: copy `skills/*` into your
tool's skills folder (`~/.claude/skills/`, `~/.codex/skills/`, or
`.cursor/skills/`). No dependencies beyond Python 3.8+.

## Example commands

```bash
# RACI matrix — Markdown + CSV
python3 skills/raci-generator/scripts/raci.py \
  skills/raci-generator/examples/input.json \
  --md out/raci.md --csv out/raci.csv

# Escalation workflow with Mermaid diagram
python3 skills/escalation-designer/scripts/escalation.py \
  skills/escalation-designer/examples/input.json \
  --md out/escalation.md

# OKR tracker
python3 skills/okr-tracker/scripts/okr.py \
  skills/okr-tracker/examples/input.json \
  --md out/okrs.md

# Adoption telemetry — fictional sample
python3 skills/adoption-telemetry/scripts/telemetry.py \
  skills/adoption-telemetry/examples/input.json \
  --md out/telemetry.md

# Adoption telemetry — anonymized worked example from the verified rollout
python3 skills/adoption-telemetry/scripts/telemetry.py \
  skills/adoption-telemetry/examples/verified-example.json \
  --md out/verified-telemetry.md
```

Every script also reads JSON from stdin and writes Markdown to stdout
when no output path is given. Run any script with `--help` for flags.

## Honest scope

- Design and reporting aids, not a PMIS. No Jira/Asana integration.
- Deterministic CLIs: same input, same output. No APIs, no learning
  from your data.
- RAG statuses and escalation tiers are heuristics you configure.
  If a threshold is wrong for your org, change the input.
- Sample data is fictional. Do not quote the example numbers as results.

## Layout

```
pm-operating-model/
├── SKILL.md                      # Pack overview (this file's parent doc)
├── README.md                     # This file
├── INSTALL.md                    # Claude Code / Codex / Cursor setup
├── .claude-plugin/plugin.json    # Plugin manifest
└── skills/
    ├── raci-generator/           # SKILL.md, scripts/raci.py, examples/
    ├── escalation-designer/      # SKILL.md, scripts/escalation.py, examples/
    ├── okr-tracker/              # SKILL.md, scripts/okr.py, examples/
    ├── adoption-telemetry/       # SKILL.md, scripts/telemetry.py, examples/
    └── stakeholder-report/       # SKILL.md, templates/template.md, templates/example.md
```

## Author

Sean Steuer — Senior Program Manager, AI Strategy & Operational
Transformation at Netflix. [seansteuer.com](https://seansteuer.com)
