# stakeholder-report

A weekly stakeholder update that takes 15 minutes to write and 2 minutes
to read.

## When to use it

- Your status update is a wall of text nobody reads.
- Different stakeholders ask you the same three questions every week.
- You need a paper trail of decisions and risks, not just vibes.

## The format

One page, five sections, in this order:

1. **TL;DR** — one or two sentences: are we on track, yes or no, and
   the single most important thing this week.
2. **Progress** — what shipped or moved, with numbers. No adjectives
   without evidence.
3. **Risks & blockers** — each with an owner and a next step. A risk
   with no owner is a complaint.
4. **Decisions needed** — the decision, the options, your
   recommendation, and the date you need it by. Stakeholders decide
   faster when you recommend.
5. **Next week** — the 2–3 things that will happen, so the next update
   writes itself.

## Rules

- Lead with the verdict, not the activity. "On track" or "At risk"
  comes first; the detail justifies it.
- Every number gets a comparison: vs. last week, vs. target, or vs.
  baseline. A number without a comparison is trivia.
- If there is no decision needed this week, say so explicitly — it
  signals that silence is not indecision.
- Keep it to one page. If it doesn't fit, you're reporting activity,
  not status.

## Files

- `templates/template.md` — the blank template, with prompts in each
  section.
- `templates/example.md` — a worked example with fictional sample
  data, showing the format filled in.

## Design notes

This is the reporting half of the operating-model pattern in this pack:
the RACI says who decides, the escalation tiers say where issues go,
the OKR tracker says whether it's working, telemetry says whether
people are using it — and this template is how all four get reported
upward in one page.
