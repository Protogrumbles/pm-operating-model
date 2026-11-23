# Cutover Checklist — Northlight billing database migration (sample data — fictional)

**Cutover date:** 2027-02-14

## Summary

6 items (5 required): 5 Pass, 0 Fail, 1 Pending, 0 Blocked. Required items still open: 0.

## Verdict

### ✅ GO

No required item is Fail/Blocked and no gate has failed.

## Checklist by category

### Data

| ID | Item | Owner | Required | Status |
| --- | --- | --- | :---: | --- |
| C1 | Final snapshot taken and verified restorable | Dana Kim | Yes | **Pass** |
| C2 | Row counts match between source and target | Marcus Chen | Yes | **Pass** |

### Application

| ID | Item | Owner | Required | Status |
| --- | --- | --- | :---: | --- |
| C3 | Billing service pointed at the new database in staging | Priya Nair | Yes | **Pass** |

### Operations

| ID | Item | Owner | Required | Status |
| --- | --- | --- | :---: | --- |
| C4 | Rollback runbook rehearsed end to end | Tom Okafor | Yes | **Pass** |
| C6 | Old database decommission plan drafted | Dana Kim | No | **Pending** |

### Comms

| ID | Item | Owner | Required | Status |
| --- | --- | --- | :---: | --- |
| C5 | Support team briefed on the cutover window | Sofia Reyes | Yes | **Pass** |

## Go / No-Go gates

| Gate | Criterion | Status |
| --- | --- | --- |
| **G1** Data integrity gate | Row counts and spot-check sums match between source and target | **Pass** |
| **G2** Rollback readiness gate | Rollback rehearsed successfully within the last 7 days | **Pass** |
