# tpm-sev-review

Build a blameless post-incident (Sev) review from an incident id,
severity, timeline, impact, root cause, and action items — as Markdown
with a timeline table, an impact summary, and the open action items
called out.

## When to use it

- An incident is resolved and the review is due before the details fade.
- The timeline exists in three different chat threads and nobody agrees
  what happened first.
- Action items from the last review never got tracked because they were
  never written down with an owner and a due date.
- A review draft is drifting toward naming who "caused" it instead of
  what the system did.

## Rules the review builder enforces

- **Severity must be one of `Sev-1`, `Sev-2`, `Sev-3`, `Sev-4`.**
  Anything else fails with a clear error.
- **Timeline events must be in chronological order.** An event dated
  before the one before it fails — a timeline that runs backwards is not
  a timeline.
- **Timeline times must be valid ISO 8601 timestamps** (e.g.
  `2027-03-02T14:05:00Z`).
- **Action-item status must be one of `Open`, `In Progress`, `Done`.**
- **`incident_id`, `title`, `impact`, and `root_cause` must be
  non-empty.** A review without an impact statement or a root cause is
  a status update, not a review.

## Blameless by design

The output names systems and decisions, never people as causes. Timeline
actors are roles (On-call, Platform Engineering, Incident Commander), not
blame targets, and the review carries an explicit blameless note at the
top. If a draft sentence blames a person, rewrite it to name the missing
guardrail instead — the fix is almost always a control the system didn't
have, not a person who failed.

## Input format

```json
{
  "incident_id": "INC-2041",
  "severity": "Sev-2",
  "title": "Creator payouts delayed by 6 hours",
  "detected_at": "2027-03-02T14:05:00Z",
  "resolved_at": "2027-03-02T20:40:00Z",
  "impact": "Payouts for 1,200 creators delayed by up to 6 hours. No payouts lost or duplicated.",
  "root_cause": "A partial queue outage caused workers to retry aggressively; the retry storm saturated the queue and there was no circuit breaker on retry volume.",
  "timeline": [
    {"time": "2027-03-02T14:05:00Z", "actor": "On-call", "action": "Paged on payout queue-depth alert."}
  ],
  "action_items": [
    {"id": "AI-1", "description": "Add a circuit breaker that caps retry volume when queue depth rises", "owner": "Priya Nair", "due": "2027-03-16", "status": "Open"}
  ]
}
```

## Usage

```bash
python3 scripts/sev.py examples/input.json --md out/sev-2041.md
# or: cat examples/input.json | python3 scripts/sev.py
```

Output is a Markdown review: severity and title, impact, timeline table,
root cause, and action items with the open ones listed separately.
Invalid input fails with an error on stderr and a non-zero exit code —
no review is written.

## Design notes

A Sev review has exactly two jobs: establish what happened in order, and
produce action items that someone owns with a due date. Everything else
is commentary. The timeline rule exists because the most common review
failure is a shuffled timeline — and once the order is wrong, the causal
story is wrong too. The open-action-items section exists because the
second most common failure is action items that dissolve into the meeting
notes; an item with an owner, a due date, and a status is trackable, and
the next review should open by checking the previous one's open items.
