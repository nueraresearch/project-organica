# D3 persistence seed-varying result

Generated from `docs/d3_persistence_seed_varying_run.json` by
`python -m benchmarks.d3_persistence_seed_varying --finish`. Do not edit by hand.

Protocol: `docs/D3-PERSISTENCE-SEED-VARYING-PREREGISTRATION.md`. Treatment: `MatchedFrequencySleepService`, in process only; the engine is unchanged.

**Verdict: `PERSISTENCE REPAIRED`**

## Seed axis is live

The six seeds produced **6 distinct preflight treatment trajectories**; the treatment's world digest is distinct for every seed. The block is no longer a single trajectory repeated under six labels.

| Criterion | Result |
| --- | --- |
| W1 witness | 6 of 6 seeds held 39/40 cycles and peak 6 |
| P1 persistence | 6 of 6 seeds alive at the horizon |
| C1 early cost | median gap 0.0 (bar -0.01) |

| Stage | Seed | Arm | World | Cycles | Theory cycles | Peak | First zero | Early recall@5 | Early predictions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| witness | 20611101 | control | 4d84cd9bee31c256 | 40 | 39 | 6 | none | 1.0 | 663 |
| witness | 20611101 | treatment | 4d84cd9bee31c256 | 40 | 39 | 6 | none | 1.0 | 663 |
| witness | 20611102 | control | 6ffd4ea043270454 | 40 | 39 | 6 | none | 1.0 | 680 |
| witness | 20611102 | treatment | 6ffd4ea043270454 | 40 | 39 | 6 | none | 1.0 | 680 |
| witness | 20611103 | control | 93fc55f3605415d9 | 40 | 39 | 6 | none | 1.0 | 666 |
| witness | 20611103 | treatment | 93fc55f3605415d9 | 40 | 39 | 6 | none | 1.0 | 666 |
| witness | 20611104 | control | 3cd7dccebd225bb8 | 40 | 39 | 6 | none | 1.0 | 650 |
| witness | 20611104 | treatment | 3cd7dccebd225bb8 | 40 | 39 | 6 | none | 1.0 | 650 |
| witness | 20611105 | control | 33c0d590dff5282d | 40 | 39 | 6 | none | 1.0 | 652 |
| witness | 20611105 | treatment | 33c0d590dff5282d | 40 | 39 | 6 | none | 1.0 | 652 |
| witness | 20611106 | control | f066137841e2c9fe | 40 | 39 | 6 | none | 1.0 | 656 |
| witness | 20611106 | treatment | f066137841e2c9fe | 40 | 39 | 6 | none | 1.0 | 656 |
| preflight | 20611101 | control | 792b6a1ef93f2fdc | 59 | 57 | 7 | 59 | 0.953125 | 783 |
| preflight | 20611101 | treatment | 792b6a1ef93f2fdc | 3000 | 2999 | 7 | none | 0.953125 | 783 |
| preflight | 20611102 | control | fb585a6262a402b7 | 59 | 57 | 7 | 59 | 0.927734 | 785 |
| preflight | 20611102 | treatment | fb585a6262a402b7 | 3000 | 2999 | 7 | none | 0.927734 | 785 |
| preflight | 20611103 | control | c708da14ce7c6609 | 60 | 58 | 7 | 60 | 0.898438 | 776 |
| preflight | 20611103 | treatment | c708da14ce7c6609 | 3000 | 2999 | 7 | none | 0.898438 | 776 |
| preflight | 20611104 | control | b25fddd5d2a92335 | 60 | 58 | 7 | 60 | 0.912109 | 763 |
| preflight | 20611104 | treatment | b25fddd5d2a92335 | 3000 | 2999 | 7 | none | 0.912109 | 763 |
| preflight | 20611105 | control | b6451c563dc4c114 | 60 | 58 | 7 | 60 | 0.947266 | 766 |
| preflight | 20611105 | treatment | b6451c563dc4c114 | 3000 | 2999 | 7 | none | 0.947266 | 766 |
| preflight | 20611106 | control | d2d4af94402179cb | 58 | 56 | 7 | 58 | 0.933594 | 767 |
| preflight | 20611106 | treatment | d2d4af94402179cb | 3000 | 2999 | 7 | none | 0.933594 | 767 |

The control's preflight death is the G1 baseline gate; the treatment's full 3,000-cycle trace is the P1 reading. Both negative controls are at zero across the witness.

**Scope.** One engine, two designs, six seed-determined schedules. A pass licenses no adoption; promotion is an owner decision, and the Tier-1 campaign still requires its own run.
