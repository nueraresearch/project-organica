# Fresh-seed replication of the reverse-orientation provenance split

Generated from `docs/assertion_provenance_replication.json` by `python -m benchmarks.assertion_provenance_replication --write`. Do not edit by hand.

**Verdict: `DIRECTIONAL ONLY`.** The design was frozen in `docs/assertion_provenance_replication_prereg.json` before the run.

## Design

- Seeds: **20613101, 20613102, 20613103, 20613104, 20613105, 20613106** (six fresh seeds; collision scan empty).
- **120** cycles, cap **40**, PHASE_ACQUISITION schedule, no engine edit.
- Population: every asserted world edge with zero direct served windows.
- One replay per seed. Direct service and recorded service are the same record, so the recording-gap category is structurally zero and is not tested here.

## Result

| Quantity | Original Q4 | Fresh block |
| --- | ---: | ---: |
| Never-served asserted edges | 26 | 26 |
| Identity mismatch | 18 | 24 |
| Alternate assertion path | 8 | 2 |
| Identity share | 0.692 | 0.923 |
| 95% Wilson interval | not recorded | [0.759, 0.979] |

| Criterion | Passes |
| --- | --- |
| R1 identity > alternate | yes |
| R2 original 18/26 inside fresh interval | no |
| R3 both classes present | yes |

`assertion_without_service` residuals: **0**. `recording_gap` rows: **0** (structural for this one-replay design).

## Per seed

| Seed | Asserted world edges | Served world edges | Never served | Identity | Alternate | Residual |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20613101 | 30 | 81 | 1 | 1 | 0 | 0 |
| 20613102 | 49 | 75 | 5 | 5 | 0 | 0 |
| 20613103 | 37 | 79 | 1 | 1 | 0 | 0 |
| 20613104 | 50 | 80 | 8 | 8 | 0 | 0 |
| 20613105 | 23 | 72 | 6 | 6 | 0 | 0 |
| 20613106 | 29 | 73 | 5 | 3 | 2 | 0 |

## Every never-served edge

| Seed | Edge | Direct served | Reverse served | Category | Sources |
| ---: | --- | ---: | ---: | --- | --- |
| 20613101 | `verdant>ochre` | 0 | 77 | identity mismatch | loop_candidate=1 |
| 20613102 | `cedar>indigo` | 0 | 27 | identity mismatch | loop_candidate=3 |
| 20613102 | `crimson>indigo` | 0 | 30 | identity mismatch | loop_candidate=2 |
| 20613102 | `maple>amber` | 0 | 1 | identity mismatch | loop_candidate=1 |
| 20613102 | `maple>indigo` | 0 | 12 | identity mismatch | loop_candidate=1 |
| 20613102 | `willow>maple` | 0 | 4 | identity mismatch | loop_candidate=2 |
| 20613103 | `sable>teal` | 0 | 13 | identity mismatch | loop_candidate=1 |
| 20613104 | `birch>olive` | 0 | 19 | identity mismatch | loop_candidate=1 |
| 20613104 | `birch>verdant` | 0 | 35 | identity mismatch | loop_candidate=4 |
| 20613104 | `teal>cedar` | 0 | 5 | identity mismatch | loop_candidate=1 |
| 20613104 | `teal>olive` | 0 | 16 | identity mismatch | loop_candidate=1 |
| 20613104 | `teal>umber` | 0 | 50 | identity mismatch | loop_candidate=1 |
| 20613104 | `teal>verdant` | 0 | 35 | identity mismatch | loop_candidate=7 |
| 20613104 | `teal>yarrow` | 0 | 16 | identity mismatch | loop_candidate=1 |
| 20613104 | `willow>teal` | 0 | 1 | identity mismatch | loop_candidate=1 |
| 20613105 | `cedar>willow` | 0 | 51 | identity mismatch | loop_candidate=2 |
| 20613105 | `indigo>willow` | 0 | 38 | identity mismatch | loop_candidate=1, workflow_concept=1 |
| 20613105 | `olive>amber` | 0 | 1 | identity mismatch | loop_candidate=1 |
| 20613105 | `olive>teal` | 0 | 77 | identity mismatch | loop_candidate=1 |
| 20613105 | `slate>olive` | 0 | 7 | identity mismatch | loop_candidate=1 |
| 20613105 | `slate>umber` | 0 | 1 | identity mismatch | loop_candidate=1 |
| 20613106 | `birch>teal` | 0 | 0 | alternate assertion path | loop_candidate=1 |
| 20613106 | `cedar>indigo` | 0 | 27 | identity mismatch | workflow_concept=1 |
| 20613106 | `teal>birch` | 0 | 0 | alternate assertion path | loop_candidate=1 |
| 20613106 | `teal>indigo` | 0 | 37 | identity mismatch | loop_candidate=7 |
| 20613106 | `willow>teal` | 0 | 7 | identity mismatch | loop_candidate=1 |

## What this does and does not establish

This is a fresh-block test of whether the **orientation split** repeats. It does not test recording fidelity, because one replay cannot distinguish a direct service record from a replay; it also does not test whether serving the direct edges would change `A_W`, and it is not a capability or engine-effect claim.

A fresh-seed diagnostic of one provenance split. It is not a capability, retention, transfer or engine-effect claim, and it does not show whether serving the direct edges would change A_W.
