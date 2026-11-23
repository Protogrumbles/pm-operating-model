# TPM lane — Technical Program

The technical program lane of the pm-operating-model skill pack: four
skills for the parts of technical program management that live in
documents, not dashboards — the decision, the rollout, the cutover, and
the incident review.

## Skills

| Skill | What it does | CLI |
|---|---|---|
| [tpm-adr-writer](tpm-adr-writer/SKILL.md) | Writes a numbered architecture decision record: context, decision, alternatives with pros/cons, consequences | `scripts/adr.py` |
| [tpm-rollout-planner](tpm-rollout-planner/SKILL.md) | Builds a phased API/platform rollout plan with cumulative traffic, computed end dates, rollback criteria, and comms | `scripts/rollout.py` |
| [tpm-cutover-checklist](tpm-cutover-checklist/SKILL.md) | Migration cutover checklist with go/no-go gates and a mechanical GO/NO-GO verdict | `scripts/cutover.py` |
| [tpm-sev-review](tpm-sev-review/SKILL.md) | Blameless post-incident review: timeline table, impact, root cause, tracked action items | `scripts/sev.py` |

## How the lane fits together

A technical program usually runs in this order, and the skills follow it:

1. **Decide** (`tpm-adr-writer`) — record the decision and what was
   rejected, while the reasoning is still fresh.
2. **Roll out** (`tpm-rollout-planner`) — phase the change to real
   traffic with written rollback triggers.
3. **Cut over** (`tpm-cutover-checklist`) — verify the migration
   checklist and let the gates decide GO or NO-GO.
4. **Review** (`tpm-sev-review`) — when something goes wrong anyway,
   establish the timeline in order and track the fixes.

Each skill is a dependency-free Python 3 CLI (standard library only),
reads JSON from a file or stdin, and writes Markdown to stdout or a
file. Invalid input fails with a clear error and a non-zero exit code —
no output is written.

## Companion: security review

Technical decisions, rollouts, and cutovers all need a security pass
before they ship. The companion skill for that is
[RAILGUARD](https://github.com/Protogrumbles/Rail-Guard) — a security
review framework for agentic coding, not a scanner. It structures the
security review of what an agent built; it does not scan code for
vulnerabilities, and it does not replace a scanner or a human security
review. Use it alongside this lane when a decision, rollout, or cutover
touches code an agent wrote.

## Example commands

```bash
# Architecture decision record
python3 skills/tpm-adr-writer/scripts/adr.py \
  skills/tpm-adr-writer/examples/input.json \
  --md out/adr-0012.md

# Phased rollout plan
python3 skills/tpm-rollout-planner/scripts/rollout.py \
  skills/tpm-rollout-planner/examples/input.json \
  --md out/rollout.md

# Cutover checklist with go/no-go verdict
python3 skills/tpm-cutover-checklist/scripts/cutover.py \
  skills/tpm-cutover-checklist/examples/input.json \
  --md out/cutover.md

# Blameless Sev review
python3 skills/tpm-sev-review/scripts/sev.py \
  skills/tpm-sev-review/examples/input.json \
  --md out/sev-2041.md
```

## Honest scope

- Design and reporting aids, not a PMIS. No Jira/Asana integration.
- Deterministic CLIs: same input, same output. No APIs, no learning
  from your data.
- Verdicts and validations are mechanical: the ADR writer requires at
  least one alternative, the rollout planner enforces traffic and date
  order, the cutover checklist computes GO/NO-GO from required items
  and gates, and the Sev review requires a chronological timeline.
  If a rule is wrong for your org, change the input — or fork the
  script; it's yours to edit.
- All sample data is fictional (Northlight Studios). Do not quote the
  example numbers as results.
