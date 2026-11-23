# Post-Incident Review — INC-2041

**Severity:** Sev-2
**Title:** Creator payouts delayed by 6 hours
**Detected:** 2027-03-02T14:05:00Z
**Resolved:** 2027-03-02T20:40:00Z

> Blameless review: this document describes what the system did and what we will change. It does not assign fault to any person.

## Impact

Northlight Studios (sample data — fictional): payouts for 1,200 creators were delayed by up to 6 hours. No payouts were lost or duplicated, and no creator data was affected. Support received 34 contacts about missing payouts during the window.

## Timeline

| Time | Actor | Action |
| --- | --- | --- |
| 2027-03-02T14:05:00Z | On-call | Paged on payout queue-depth alert. |
| 2027-03-02T14:20:00Z | On-call | Confirmed the payout queue backlog and declared Sev-2. |
| 2027-03-02T15:00:00Z | Platform Engineering | Identified retry storm from workers hitting the partial queue outage. |
| 2027-03-02T15:45:00Z | Platform Engineering | Paused retries and drained the queue manually. |
| 2027-03-02T18:30:00Z | Platform Engineering | Queue drained; payouts processing normally again. |
| 2027-03-02T20:40:00Z | Incident Commander | Verified all delayed payouts completed; incident resolved. |

## Root cause

A partial outage in the payout queue caused workers to retry failed jobs aggressively. The retry storm saturated the queue, so new payout jobs waited behind retries for hours. There was no circuit breaker on retry volume, and the queue-depth alert fired 40 minutes after the backlog began because its threshold was set for the old, smaller payout volume.

## Action items

3 action item(s), 3 still open.

| ID | Action | Owner | Due | Status |
| --- | --- | --- | --- | --- |
| AI-1 | Add a circuit breaker that caps retry volume when queue depth rises | Priya Nair | 2027-03-16 | **Open** |
| AI-2 | Retune the queue-depth alert threshold to current payout volume | Marcus Chen | 2027-03-09 | **In Progress** |
| AI-3 | Publish a creator-facing status update template for payout delays | Sofia Reyes | 2027-03-23 | **Open** |

### Open action items

- **AI-1** — Add a circuit breaker that caps retry volume when queue depth rises (Priya Nair, due 2027-03-16, Open)
- **AI-2** — Retune the queue-depth alert threshold to current payout volume (Marcus Chen, due 2027-03-09, In Progress)
- **AI-3** — Publish a creator-facing status update template for payout delays (Sofia Reyes, due 2027-03-23, Open)
