# escalation-designer

Design a tiered escalation workflow: who handles what, how fast, and
when it moves up.

## When to use it

- Escalations currently land wherever — Slack, email, hallway — with no
  owner and no clock.
- A new program or platform is launching and the support model is "we'll
  figure it out."
- Escalation volume is climbing and you need to show where the tiers
  leak.

## Design principles

1. **Every tier has one owner role and one SLA.** A tier with no owner
   is a dead letter; a tier with no SLA is a queue with no clock.
2. **Escalation is a handoff, not a re-explanation.** Each tier's entry
   criteria state exactly what must already be tried, so the customer
   (internal or external) doesn't repeat themselves.
3. **Tiers get narrower as they go up.** Tier 1 handles volume, the top
   tier handles judgment. If the top tier is handling volume, the lower
   tiers are broken.
4. **SLAs tighten as severity rises, not as tier rises.** A Sev-1 at
   Tier 3 still gets the Sev-1 clock.

## Input format

```json
{
  "program": "Risk Platform Support (sample data — fictional)",
  "severities": ["Sev-1", "Sev-2", "Sev-3"],
  "tiers": [
    {
      "name": "Tier 1 — Help Desk",
      "owner": "Support Lead",
      "handles": "Password resets, how-to questions, known issues",
      "entry_criteria": "Issue reported via intake form or chat",
      "sla": {"Sev-1": "30m first response", "Sev-2": "4h", "Sev-3": "1 business day"},
      "escalates_to": "Tier 2 — Product Ops",
      "escalate_when": "Not resolved in 4h, or unknown root cause"
    }
  ]
}
```

- `sla` keys should match `severities`; missing keys are flagged.
- The last tier's `escalates_to` should be `null` (or omitted) — it is
  the top of the chain.

## Usage

```bash
python3 scripts/escalation.py examples/input.json --md out/escalation.md
# or: cat examples/input.json | python3 scripts/escalation.py
```

Output is a Markdown workflow table plus a Mermaid flowchart you can
paste into any Markdown renderer (GitHub, Notion, Confluence with the
Mermaid macro).

## Design notes

The pattern here comes from a risk platform rolled out across 57
productions in ~8 weeks, where the escalation model was designed before
launch: tiered ownership with explicit SLAs meant the platform team
didn't become the help desk for 57 productions on day one. In that
rollout, escalations fell ~25% and first-contact resolution improved
~65–70% once the tiers and their entry criteria were explicit.
