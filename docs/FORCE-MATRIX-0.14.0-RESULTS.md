# Tier-1 matrix on 0.14.0 — result record

**Status: RAN. 2026-11-10.** This is a new record, not a revision of
[`FORCE-MATRIX-RESULTS.md`](FORCE-MATRIX-RESULTS.md). The historical
`docs/force_matrix.json` was not overwritten; the new campaign is
`docs/force_matrix_0.14.0.json`.

## 1. The run

| | |
|---|---|
| Engine | **0.14.0**, `477aeb2ff34dd2cc857520d139d1b452892ec95a8158aedf72a089e8318f05e2` |
| Engine commit | `8f9d3b71340729d3c61165d5e51ad0db3c2694c3` |
| Colonies | `FULL`, `SALIENCE`, `NO_CONTRADICTIONS`, `NO_QUESTIONS`, `NO_DREAMS`, `ANTI_EIG` |
| Cycles | **3,000 per colony — 18,000 colony-cycles** |
| Stimulus | `lattice_L1` — three disjoint triangles, 9 distinct events, 7 words, experience period 9 cycles |
| Seed | `20261023` |
| `PYTHONHASHSEED` | `0` in all six processes |
| G1 | all six code paths verified distinct before launch |
| D2 | passed; the `L1` reference arm is alive at the 3,000-cycle horizon |
| Colony wall clock | 196.1–204.6 s each, six in parallel |
| Artifact | `docs/force_matrix_0.14.0.json` |

**Launcher note.** The first launch completed all six colonies, but the
per-colony part processes exited 1 because `force_matrix.py` applied the
full-artifact reference-arm check to each part and `FULL` was absent from
the other five parts. The part-mode guard is now `--part`, passed by
`run_matrix.py`; the completed parts were merged through the harness's own
`--merge` path. **No cell was rerun**, and the merge's reference check
reports no problems.

## 2. The result

Four of the nine frozen metrics are sensitive across the six arms:

| Metric | FULL | SALIENCE | NO_CONTRADICTIONS | NO_QUESTIONS | NO_DREAMS | ANTI_EIG |
|---|---:|---:|---:|---:|---:|---:|
| M1 theory duty cycle | 0.9997 | 0.9997 | 0.9997 | 0.9997 | 0.9997 | 0.9997 |
| M2 question duty cycle | 0.9997 | 0.9997 | 0.9997 | **0.0000** | 0.9997 | 0.9997 |
| M3 contradiction density | 193.8038 | 194.5824 | 194.6980 | 194.5824 | 194.5824 | 194.5824 |
| M4 contradiction survival | 0.8824 | 0.8333 | 0.8333 | 0.8333 | 0.8333 | 0.8333 |
| M5 development velocity | 1.667 | 1.733 | 1.733 | 1.167 | 1.400 | 1.733 |
| M6 lineage depth | 8 | 8 | 8 | 8 | 8 | 8 |
| M7 mean hypothesis lifetime | 1,497.500 | 2,997.667 | 2,997.667 | 2,997.667 | 2,997.667 | 2,997.667 |
| M8 population stability | 0.9817 | 0.9817 | 0.9817 | 0.9817 | 0.9817 | 0.9817 |
| M9 cognitive revolutions | 0 | 0 | 0 | 0 | 0 | 0 |

**Sensitive:** M2, M4, M5, M7. **Insensitive:** M1, M3, M6, M8.
**Structurally zero:** M9.

The inventory is lower than the historical 0.13.0 campaign:

| Colony | M5 inventory | New in final 100 cycles |
|---|---:|---:|
| FULL | 50 | 0 |
| SALIENCE | 52 | 0 |
| NO_CONTRADICTIONS | 52 | 0 |
| NO_QUESTIONS | 35 | 0 |
| NO_DREAMS | 42 | 0 |
| ANTI_EIG | 52 | 0 |

All six arms still discover nothing new in their final 100 cycles. The
stimulus remains a closed, repeating nine-event world, so that flat tail is
a property of this world as much as of the organism.

The historical 0.13.0 matrix recorded M3 at 14,031.6–16,028.4 and inventory
at 74–112. The 0.14.0 values are not a like-for-like delta: the engine's
persistence repair changed the temporal substrate, so the two matrices
describe different builds. They are recorded side by side, not pooled.

## 3. What this does not do

- **No prediction bucket is re-scored here.** The five frozen predictions
  depend on a measured noise floor; `docs/process_noise_3000.json` predates
  0.14.0. Applying that floor to this campaign would judge the new engine
  with an old instrument. The raw campaign, metric-sensitivity audit and
  discovery report are recorded; a prediction re-score needs a fresh
  0.14.0 noise-floor calibration and its own disclosed decision.
- **No architecture claim is added.** The campaign measures the six arms on
  one stimulus and one seed. It does not establish that any arm develops
  better, and it does not turn the 0.13.0 verdicts into 0.14.0 verdicts.
- **No historical record is rewritten.** `docs/force_matrix.json`,
  `docs/FORCE-MATRIX-RESULTS.md` and the 0.13.0 verdicts remain as recorded.

## 4. Artifacts

- `docs/force_matrix_0.14.0.json` — stamped campaign, six rows.
- `docs/metric_sensitivity_0.14.0.json` — metric audit for this campaign.
- `docs/discovery_0.14.0.json` — inventory and discovery curves.
- `docs/figure_discovery_0.14.0.svg` — the discovery figure.

Generated from the campaign by `benchmarks/force_matrix.py`,
`benchmarks/metric_sensitivity.py` and `benchmarks/discovery_report.py`.
