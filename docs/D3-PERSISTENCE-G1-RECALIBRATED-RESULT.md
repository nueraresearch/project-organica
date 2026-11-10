# D3 persistence engine replication (G1 recalibrated) — result

Generated from `docs/d3_persistence_g1_recalibrated_run.json` by `python -m benchmarks.d3_persistence_g1_recalibrated --finish`. Do not edit by hand.

Protocol: `docs/D3-PERSISTENCE-G1-RECALIBRATED-PREREGISTRATION.md`. Treatment: shipped `organica.sleep.SleepService` at 0.14.0. Control: pre-repair raw-denominator ablation.

**Verdict: `PERSISTENCE REPAIRED`**

## Seed axis is live

The six seeds produced **6 distinct preflight treatment trajectories**.

| Criterion | Result |
| --- | --- |
| W1 witness | 6 of 6 seeds held 39/40 cycles and peak 6 |
| P1 persistence | 6 of 6 seeds alive at the horizon |
| C1 early cost | median gap 0.0 (bar -0.01) |

| Stage | Seed | Arm | World | Cycles | Theory cycles | Peak | First zero | Early recall@5 | Frequency updates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| witness | 20611301 | control | 158f57a58e8cc77d | 40 | 39 | 6 | none | 1.0 | 0 |
| witness | 20611301 | treatment | 158f57a58e8cc77d | 40 | 39 | 6 | none | 1.0 | 40 |
| witness | 20611302 | control | c1e56844734f64da | 40 | 39 | 6 | none | 1.0 | 0 |
| witness | 20611302 | treatment | c1e56844734f64da | 40 | 39 | 6 | none | 1.0 | 40 |
| witness | 20611303 | control | f2af41a34d11a146 | 40 | 39 | 6 | none | 1.0 | 0 |
| witness | 20611303 | treatment | f2af41a34d11a146 | 40 | 39 | 6 | none | 1.0 | 40 |
| witness | 20611304 | control | 79e0b991a9011a40 | 40 | 39 | 6 | none | 1.0 | 0 |
| witness | 20611304 | treatment | 79e0b991a9011a40 | 40 | 39 | 6 | none | 1.0 | 40 |
| witness | 20611305 | control | 4d84cd9bee31c256 | 40 | 39 | 6 | none | 1.0 | 0 |
| witness | 20611305 | treatment | 4d84cd9bee31c256 | 40 | 39 | 6 | none | 1.0 | 40 |
| witness | 20611306 | control | 7abc7e3e8d1ebb86 | 40 | 39 | 6 | none | 1.0 | 0 |
| witness | 20611306 | treatment | 7abc7e3e8d1ebb86 | 40 | 39 | 6 | none | 1.0 | 40 |
| preflight | 20611301 | control | 393b38780ff8dbe6 | 58 | 56 | 7 | 58 | 0.958984 | 0 |
| preflight | 20611301 | treatment | 393b38780ff8dbe6 | 3000 | 2999 | 7 | none | 0.958984 | 3000 |
| preflight | 20611302 | control | ac3d483212bb893d | 59 | 57 | 7 | 59 | 0.9375 | 0 |
| preflight | 20611302 | treatment | ac3d483212bb893d | 3000 | 2999 | 7 | none | 0.9375 | 3000 |
| preflight | 20611303 | control | bec27eb00a745371 | 59 | 57 | 6 | 59 | 0.869141 | 0 |
| preflight | 20611303 | treatment | bec27eb00a745371 | 3000 | 2999 | 6 | none | 0.869141 | 3000 |
| preflight | 20611304 | control | bdef6f0133ff0763 | 59 | 57 | 6 | 59 | 0.931641 | 0 |
| preflight | 20611304 | treatment | bdef6f0133ff0763 | 3000 | 2999 | 6 | none | 0.931641 | 3000 |
| preflight | 20611305 | control | 792b6a1ef93f2fdc | 59 | 57 | 7 | 59 | 0.953125 | 0 |
| preflight | 20611305 | treatment | 792b6a1ef93f2fdc | 3000 | 2999 | 7 | none | 0.953125 | 3000 |
| preflight | 20611306 | control | e6bcec5b36b44c93 | 59 | 57 | 7 | 59 | 0.927734 | 0 |
| preflight | 20611306 | treatment | e6bcec5b36b44c93 | 3000 | 2999 | 7 | none | 0.927734 | 3000 |

The control's preflight death is the G1 baseline gate; the treatment's full 3,000-cycle trace is the P1 reading. Both negative controls are at zero.

**Scope.** One promoted engine, two designs, six fresh seed-determined schedules. This is a replication of the promoted behavior, not a new adoption decision.
