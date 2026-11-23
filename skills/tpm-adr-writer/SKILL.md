# tpm-adr-writer

Write an architecture decision record (ADR) — the decision, the context,
the alternatives you rejected, and what follows from it — as numbered
Markdown.

## When to use it

- A technical decision is about to be made and the reasoning will be
  forgotten in six months if it isn't written down now.
- Two teams disagree about an approach and the argument keeps restarting.
- You're inheriting a system and need to know *why* it looks the way it
  does, not just what it does.
- A decision is being reversed or superseded and the old record needs a
  clean status change, not a silent edit.

## Rules the writer enforces

- **Status must be one of `Proposed`, `Accepted`, `Deprecated`,
  `Superseded`.** Anything else fails with a clear error. An ADR with a
  made-up status is a note, not a record.
- **At least one alternative must be considered.** An ADR with zero
  alternatives fails — if nothing else was weighed, no decision was made.
- **Every alternative needs a title and at least one pro or con.** An
  alternative with neither was not actually considered.
- **Title, context, decision, and consequences must be non-empty.** An
  ADR that records a decision without its consequences is a press release.
- Optional: `number` (zero-padded to 4 digits in the heading, e.g.
  `ADR-0012`), `date`, `supersedes`, `superseded_by`.

## Input format

```json
{
  "number": 12,
  "title": "Adopt event-driven ingestion for the Creator Analytics pipeline",
  "status": "Accepted",
  "date": "2026-11-20",
  "context": "Creators see yesterday's numbers at best; batch windows are getting longer as the catalog grows.",
  "decision": "Producers publish schema-versioned events to a central event bus; the pipeline consumes them in near real time.",
  "alternatives": [
    {
      "title": "Keep nightly batch ingestion",
      "pros": ["No new infrastructure"],
      "cons": ["Data lands up to 6 hours late"]
    }
  ],
  "consequences": ["Producers must publish schema-versioned events."]
}
```

## Usage

```bash
python3 scripts/adr.py examples/input.json --md out/adr-0012.md
# or: cat examples/input.json | python3 scripts/adr.py
```

Output is a numbered ADR in Markdown: status and date, context, decision,
each alternative with its pros and cons, then consequences. Invalid input
fails with an error on stderr and a non-zero exit code — no ADR is written.

## Design notes

The rule that matters most is the alternatives rule. In practice the
decision itself is rarely the hard part; the hard part is that six months
later nobody remembers what was rejected or why, so the rejected option
gets proposed again as if it were new. One honest paragraph per rejected
alternative is the cheapest insurance a technical program has. Record the
consequences you can already see — especially the new on-call surface and
the backfill path — because those are the costs the decision actually
carries.
