# WBS & Schedule — Vendor Onboarding Redesign

_Sample data — fictional._

**Start:** 2026-11-02 · **End:** 2026-12-01 · **Duration:** 30 calendar days

| ID | Task | Start | End | Days | Depends on | Milestone | Critical |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| **T1** | Map current onboarding flow | 2026-11-02 | 2026-11-06 | 5 | — | — | ⭐ Yes |
| **T2** | Draft new intake form and handoff steps | 2026-11-07 | 2026-11-11 | 5 | T1 | — | ⭐ Yes |
| **T3** | Legal review of new form | 2026-11-12 | 2026-11-14 | 3 | T2 | — | No |
| **T4** | Finance payment-setup checklist | 2026-11-12 | 2026-11-14 | 3 | T2 | — | No |
| **T5** | Build pilot tracker | 2026-11-12 | 2026-11-15 | 4 | T2 | — | ⭐ Yes |
| **T6** | Pilot with five new vendors | 2026-11-16 | 2026-11-25 | 10 | T3, T4, T5 | — | ⭐ Yes |
| **T7** | Pilot complete | 2026-11-26 | 2026-11-26 | 0 | T6 | ✅ | ⭐ Yes |
| **T8** | Roll out redesigned flow and run retro | 2026-11-27 | 2026-12-01 | 5 | T7 | — | ⭐ Yes |

## Critical path

Tasks with zero slack — any slip here moves the end date:

**T1** Map current onboarding flow → **T2** Draft new intake form and handoff steps → **T5** Build pilot tracker → **T6** Pilot with five new vendors → **T7** Pilot complete → **T8** Roll out redesigned flow and run retro

## Milestones

- **Pilot complete** (T7) — 2026-11-26

## Slack

- T3 Legal review of new form: 1 day(s) of slack.
- T4 Finance payment-setup checklist: 1 day(s) of slack.
