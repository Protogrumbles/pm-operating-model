# Rollout Plan — Northlight Playback API v2 (sample data — fictional)

| Phase | Cohort | Traffic | Cumulative | Start | End | Duration |
| --- | --- | ---: | ---: | --- | --- | ---: |
| **Canary** | Internal employees | 5% | 5% | 2027-01-05 | 2027-01-12 | 7 days |
| **Early adopters** | Opt-in creator accounts | 20% | 25% | 2027-01-12 | 2027-01-19 | 7 days |
| **General availability** | All accounts | 75% | 100% | 2027-01-19 | 2027-02-02 | 14 days |

**Total traffic at full rollout:** 100%

## Rollback criteria

Roll back immediately if any of these hold:

- Error rate exceeds 1% for 15 consecutive minutes.
- p95 playback-start latency rises more than 20% over the v1 baseline.
- Any Sev-1 or Sev-2 incident attributed to v2 during a phase.

## Comms plan

| Audience | Channel | Message |
| --- | --- | --- |
| Support | #support | Canary starts Jan 5 for employees only; no customer-facing change expected. |
| Creator partners | Email + status page | Opt-in early access opens Jan 12; v2 playback starts faster, no action needed. |
| All customers | Status page + in-app banner | Playback API v2 rolls out to everyone Jan 19; v1 stays available until Feb 28. |
