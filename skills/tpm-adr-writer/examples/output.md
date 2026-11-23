# ADR-0012: Adopt event-driven ingestion for the Creator Analytics pipeline

**Status:** Accepted
**Date:** 2026-11-20

## Context

Northlight Studios (sample data — fictional) runs a Creator Analytics pipeline that ingests playback and payout events in nightly batches. Creators see yesterday's numbers at best, and support gets the same question every morning: "where are my numbers?" Batch windows are also getting longer as the catalog grows, so the 6-hour lag is trending worse, not better.

## Decision

Move ingestion to an event-driven model: producers publish schema-versioned events to a central event bus, and the analytics pipeline consumes them in near real time. Batch ingestion stays as a backfill path only.

## Alternatives considered

### Keep nightly batch ingestion

- ✅ Pro: No new infrastructure
- ✅ Pro: Team already knows how to operate it
- ⚠️ Con: Data lands up to 6 hours late
- ⚠️ Con: Batch window grows with the catalog

### Hourly micro-batches

- ✅ Pro: Small change from current design
- ✅ Pro: Cuts lag from 6 hours to 1
- ⚠️ Con: Still not real time
- ⚠️ Con: Adds scheduler complexity without solving the trend

### Buy a third-party analytics ingestion service

- ✅ Pro: Fastest to ship
- ✅ Pro: Vendor operates the pipeline
- ⚠️ Con: Recurring cost scales with event volume
- ⚠️ Con: Creator data leaves our boundary

## Consequences

- Producers must publish schema-versioned events; breaking schema changes require a new version, not an edit.
- The team owns and operates an event bus — new on-call surface, with runbooks before launch.
- Batch ingestion is retained as a backfill path, so both paths must be tested on every schema change.
- Creators see numbers within minutes, which raises the bar on data-quality monitoring.
