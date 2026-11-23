# D3 persistence engine replication — result

Generated from `docs/d3_persistence_engine_replication_run.json` by `python -m benchmarks.d3_persistence_engine_replication --finish`. Do not edit by hand.

Protocol: `docs/D3-PERSISTENCE-ENGINE-REPLICATION-PREREGISTRATION.md`. Treatment: shipped `organica.sleep.SleepService` at 0.14.0. Control: pre-repair raw-denominator ablation.

**Verdict: `VOID`**

## Seed axis is live

The six seeds produced **6 distinct preflight treatment trajectories**.

## Gate failure

**G1_baseline_death** failed before any criterion was read.

Control first zero by seed: 20611201=60, 20611202=58, 20611203=61, 20611204=61, 20611205=58, 20611206=59. The G1 bound is 1-60 cycles.

Treatment cells with no first zero: 6 of 6. The treatment survived the horizon, but the block is void and licenses no persistence claim.

| Criterion | Result |
| --- | --- |
| W1 witness | unread (void) |
| P1 persistence | unread (void) |
| C1 early cost | unread (void) |

| Stage | Seed | Arm | World | Cycles | Theory cycles | Peak | First zero | Early recall@5 | Frequency updates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| witness | 20611201 | control | f3a7362b1dcd65ed | 40 | 39 | 6 | none | 1.0 | 0 |
| witness | 20611201 | treatment | f3a7362b1dcd65ed | 40 | 39 | 6 | none | 1.0 | 40 |
| witness | 20611202 | control | 6a4707a2bac5d936 | 40 | 39 | 6 | none | 1.0 | 0 |
| witness | 20611202 | treatment | 6a4707a2bac5d936 | 40 | 39 | 6 | none | 1.0 | 40 |
| witness | 20611203 | control | ae3ced9636262668 | 40 | 39 | 6 | none | 1.0 | 0 |
| witness | 20611203 | treatment | ae3ced9636262668 | 40 | 39 | 6 | none | 1.0 | 40 |
| witness | 20611204 | control | 5bb0454cfa449eba | 40 | 39 | 6 | none | 1.0 | 0 |
| witness | 20611204 | treatment | 5bb0454cfa449eba | 40 | 39 | 6 | none | 1.0 | 40 |
| witness | 20611205 | control | f2f591211dea4e9f | 40 | 39 | 6 | none | 1.0 | 0 |
| witness | 20611205 | treatment | f2f591211dea4e9f | 40 | 39 | 6 | none | 1.0 | 40 |
| witness | 20611206 | control | c1e56844734f64da | 40 | 39 | 6 | none | 1.0 | 0 |
| witness | 20611206 | treatment | c1e56844734f64da | 40 | 39 | 6 | none | 1.0 | 40 |
| preflight | 20611201 | control | f5bdc7746365d67c | 60 | 58 | 7 | 60 | 0.947266 | 0 |
| preflight | 20611201 | treatment | f5bdc7746365d67c | 3000 | 2999 | 7 | none | 0.947266 | 3000 |
| preflight | 20611202 | control | d07c6d69defbce11 | 58 | 56 | 7 | 58 | 0.933594 | 0 |
| preflight | 20611202 | treatment | d07c6d69defbce11 | 3000 | 2999 | 7 | none | 0.933594 | 3000 |
| preflight | 20611203 | control | 040c29b6df155bb2 | 61 | 59 | 7 | 61 | 0.923828 | 0 |
| preflight | 20611203 | treatment | 040c29b6df155bb2 | 3000 | 2999 | 7 | none | 0.923828 | 3000 |
| preflight | 20611204 | control | 92e619f0cffd784a | 61 | 59 | 7 | 61 | 0.900391 | 0 |
| preflight | 20611204 | treatment | 92e619f0cffd784a | 3000 | 2999 | 7 | none | 0.900391 | 3000 |
| preflight | 20611205 | control | 3d96ba1cd8b007ca | 58 | 56 | 7 | 58 | 0.955078 | 0 |
| preflight | 20611205 | treatment | 3d96ba1cd8b007ca | 3000 | 2999 | 7 | none | 0.955078 | 3000 |
| preflight | 20611206 | control | ac3d483212bb893d | 59 | 57 | 7 | 59 | 0.9375 | 0 |
| preflight | 20611206 | treatment | ac3d483212bb893d | 3000 | 2999 | 7 | none | 0.9375 | 3000 |

The control's preflight death is the G1 baseline gate; the treatment's full 3,000-cycle trace is the P1 reading. Both negative controls are at zero.

**Scope.** One promoted engine, two designs, six fresh seed-determined schedules. This is a replication of the promoted behavior, not a new adoption decision.
