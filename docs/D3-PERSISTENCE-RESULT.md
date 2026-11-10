# D3 persistence result: matched source-frequency decay

Generated from `docs/d3_persistence_run.json` by
`python -m benchmarks.d3_persistence_run --finish`. Do not edit by hand.

Protocol: `docs/D3-PERSISTENCE-PREREGISTRATION.md` (frozen before any cell). Treatment: `MatchedFrequencySleepService`, in process only; the engine is unchanged.

**Verdict: `PERSISTENCE REPAIRED`**

## Measurement caveat: the seed axis is degenerate

All six world seeds produced identical per-cycle theory traces, early recall and
prediction counts in every stage and arm. The frozen 5/6 rule is therefore met by
**one deterministic trajectory repeated six times**, not by six independent worlds.
Effective n = 1. The within-block criteria stand, but this block cannot support a
seed-robustness claim; that is a design defect in the seed axis, not a repair result.

| Criterion | Result |
| --- | --- |
| W1 witness | read of 6 seeds held 39/40 cycles and peak 6 |
| P1 persistence | 6 of 6 seeds alive at the horizon |
| C1 early cost | median gap 0.0 (bar -0.01) |

| Stage | Seed | Arm | Cycles | Theory cycles | Peak | First zero | Early recall@5 | Early predictions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| witness | 20410301 | control | 40 | 39 | 6 | none | 1.0 | 656 |
| witness | 20410301 | treatment | 40 | 39 | 6 | none | 1.0 | 656 |
| witness | 20410302 | control | 40 | 39 | 6 | none | 1.0 | 656 |
| witness | 20410302 | treatment | 40 | 39 | 6 | none | 1.0 | 656 |
| witness | 20410303 | control | 40 | 39 | 6 | none | 1.0 | 656 |
| witness | 20410303 | treatment | 40 | 39 | 6 | none | 1.0 | 656 |
| witness | 20410304 | control | 40 | 39 | 6 | none | 1.0 | 656 |
| witness | 20410304 | treatment | 40 | 39 | 6 | none | 1.0 | 656 |
| witness | 20410305 | control | 40 | 39 | 6 | none | 1.0 | 656 |
| witness | 20410305 | treatment | 40 | 39 | 6 | none | 1.0 | 656 |
| witness | 20410306 | control | 40 | 39 | 6 | none | 1.0 | 656 |
| witness | 20410306 | treatment | 40 | 39 | 6 | none | 1.0 | 656 |
| preflight | 20410301 | control | 60 | 58 | 7 | 60 | 0.912109 | 763 |
| preflight | 20410301 | treatment | 3000 | 2999 | 7 | none | 0.912109 | 763 |
| preflight | 20410302 | control | 60 | 58 | 7 | 60 | 0.912109 | 763 |
| preflight | 20410302 | treatment | 3000 | 2999 | 7 | none | 0.912109 | 763 |
| preflight | 20410303 | control | 60 | 58 | 7 | 60 | 0.912109 | 763 |
| preflight | 20410303 | treatment | 3000 | 2999 | 7 | none | 0.912109 | 763 |
| preflight | 20410304 | control | 60 | 58 | 7 | 60 | 0.912109 | 763 |
| preflight | 20410304 | treatment | 3000 | 2999 | 7 | none | 0.912109 | 763 |
| preflight | 20410305 | control | 60 | 58 | 7 | 60 | 0.912109 | 763 |
| preflight | 20410305 | treatment | 3000 | 2999 | 7 | none | 0.912109 | 763 |
| preflight | 20410306 | control | 60 | 58 | 7 | 60 | 0.912109 | 763 |
| preflight | 20410306 | treatment | 3000 | 2999 | 7 | none | 0.912109 | 763 |

The control's preflight death is the G1 baseline gate; the treatment's full 3,000-cycle trace is the P1 reading. Both negative controls are at zero across the witness.

**Scope.** One engine, two designs, six seeds. A pass licenses no adoption; promotion is an owner decision, and the Tier-1 campaign still requires its own run.
