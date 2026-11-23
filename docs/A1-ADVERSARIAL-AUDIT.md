# A1 six-seed feasibility and adversarial audit

**Status:** `P0 PASS — SIX-SEED FEASIBILITY AND BLINDNESS`

**This is not an experimental result.** No arm cell was run; no manifest was frozen.

| Seed | Feasibility | Future-blind | Determinism | Selected |
| ---: | --- | --- | --- | --- |
| 20740101 | PASS | PASS | PASS | `indigo>fern`, `teal>slate`, `maple>cedar`, `verdant>umber` |
| 20740102 | PASS | PASS | PASS | `olive>umber`, `willow>yarrow`, `verdant>crimson`, `ochre>slate` |
| 20740103 | PASS | PASS | PASS | `yarrow>teal`, `amber>willow`, `birch>fern`, `verdant>sable` |
| 20740104 | PASS | PASS | PASS | `slate>indigo`, `umber>cedar`, `crimson>sable`, `willow>birch` |
| 20740105 | PASS | PASS | PASS | `ochre>crimson`, `verdant>willow`, `sable>yarrow`, `fern>olive` |
| 20740106 | PASS | PASS | PASS | `indigo>teal`, `birch>ochre`, `amber>yarrow`, `verdant>sable` |

| Check | Result |
| --- | --- |
| P0 protocol compliance | PASS |
| U sampled before cycle-36 sleep | PASS |
| Pre-37 candidate universe | PASS |
| Future-blindness | PASS |
| Determinism | PASS |
| Report-blindness | PASS |
| Sleep-blindness | PASS |
| Selector self-test | PASS |

## Selection representativeness

**Source:** `docs/a1_target_selection.json`.

**Estimand:** representative eligible pre-37 cycle-membership directed-edge population.

| Measurement | Result |
| --- | ---: |
| Selected target observations | 24 |
| Unique target edges | 23 |
| Unselected candidates | 358 |
| Candidates | 382 |
| All candidates eligible | yes |
| Selected mean / median strength | 13.958 / 14.5 |
| Unselected mean / median strength | 15.475 / 16.0 |
| Descriptive permutation p | 0.11235 |

**Conclusion:** The selected targets are a representative eligible pre-37 sample; A1 does not estimate a high-U, hard-edge or carrier-enriched effect.

It is **not** a sample of high-U edges, hard edges, carrier-enriched anomalies.

The permutation p-value is descriptive. Failure to reject a difference is not an equivalence test and does not by itself establish representativeness; the design fact is that every candidate is eligible and the hash order ignores U.

**Not evidence:** A no-arm feasibility and adversarial audit. It selects draft targets, records a descriptive selection-representativeness measurement, but freezes no manifest, authorises no cell and records no A1 result.
