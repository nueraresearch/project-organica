# Assertion provenance for the 26 never-served edges

Generated from `docs/assertion_provenance.json` by `python -m benchmarks.assertion_provenance --write`. Do not edit by hand.

**Not a result artifact.** It labels the provenance of a committed readout. The replay is accepted only if each seed reproduces the stored asserted fingerprint and the committed served-world set; it adds no seed, arm, cap or treatment.

## The four buckets

| Category | Edges | What the evidence shows |
| --- | ---: | --- |
| Recording gap | 0 | the replay served the direct edge but the committed N3 record did not |
| Identity mismatch | 18 | the direct edge was not served, but its reverse orientation was |
| Alternate assertion path | 8 | neither orientation was served; a non-prediction structure carries the edge |
| Genuine assertion without service | 0 | only a prediction candidate carries the edge and neither orientation was served |

The categories are mutually exclusive by the declared order. An identity mismatch can also have an alternate structural carrier; that is recorded in `cofactors` on the row, not used to double-count the headline.

## Per seed

| Seed | Unexplained | Recording gap | Identity mismatch | Alternate path | Prediction residual | Asserted fingerprint | Served sets match |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 20611601 | 4 | 0 | 2 | 2 | 0 | `870dfcc70f9bcad6` | yes |
| 20611602 | 4 | 0 | 4 | 0 | 0 | `e7807c59774cc135` | yes |
| 20611603 | 9 | 0 | 5 | 4 | 0 | `1236b18abf56753c` | yes |
| 20611604 | 2 | 0 | 0 | 2 | 0 | `e8475dd16f9698e7` | yes |
| 20611605 | 3 | 0 | 3 | 0 | 0 | `79f5979592b76711` | yes |
| 20611606 | 4 | 0 | 4 | 0 | 0 | `6fc0f21cf1811b80` | yes |

## Every edge

| Seed | Edge | Rank | Band | Category | Direct / reverse served | Assertion sources | Cofactors |
| ---: | --- | ---: | --- | --- | ---: | --- | --- |
| 20611601 | `olive>umber` | 31 | 21-40 | identity mismatch | 0 / 1 | loop_candidate=1 | alternate_assertion_path |
| 20611601 | `olive>willow` | 39 | 21-40 | alternate assertion path | 0 / 0 | loop_candidate=1 | none |
| 20611601 | `willow>olive` | 127 | 113+ | alternate assertion path | 0 / 0 | loop_candidate=1 | none |
| 20611601 | `willow>teal` | 124 | 113+ | identity mismatch | 0 / 46 | loop_candidate=5 | alternate_assertion_path |
| 20611602 | `amber>umber` | 61 | 41-80 | identity mismatch | 0 / 55 | loop_candidate=1 | alternate_assertion_path |
| 20611602 | `indigo>umber` | 52 | 41-80 | identity mismatch | 0 / 56 | loop_candidate=3 | alternate_assertion_path |
| 20611602 | `sable>slate` | 26 | 21-40 | identity mismatch | 0 / 3 | loop_candidate=1 | alternate_assertion_path |
| 20611602 | `willow>umber` | 54 | 41-80 | identity mismatch | 0 / 55 | dream=1, loop_candidate=7 | alternate_assertion_path |
| 20611603 | `sable>yarrow` | 111 | 81-112 | alternate assertion path | 0 / 0 | loop_candidate=1 | none |
| 20611603 | `slate>umber` | 27 | 21-40 | identity mismatch | 0 / 3 | loop_candidate=1 | alternate_assertion_path |
| 20611603 | `slate>yarrow` | 26 | 21-40 | alternate assertion path | 0 / 0 | loop_candidate=1 | none |
| 20611603 | `umber>teal` | 28 | 21-40 | identity mismatch | 0 / 26 | loop_candidate=3 | alternate_assertion_path |
| 20611603 | `willow>verdant` | 41 | 41-80 | identity mismatch | 0 / 41 | loop_candidate=1 | alternate_assertion_path |
| 20611603 | `yarrow>indigo` | 80 | 41-80 | identity mismatch | 0 / 10 | loop_candidate=2 | alternate_assertion_path |
| 20611603 | `yarrow>sable` | 79 | 41-80 | alternate assertion path | 0 / 0 | loop_candidate=1 | none |
| 20611603 | `yarrow>slate` | 81 | 81-112 | alternate assertion path | 0 / 0 | loop_candidate=1 | none |
| 20611603 | `yarrow>verdant` | 77 | 41-80 | identity mismatch | 0 / 41 | loop_candidate=9 | alternate_assertion_path |
| 20611604 | `amber>maple` | 35 | 21-40 | alternate assertion path | 0 / 0 | loop_candidate=1 | none |
| 20611604 | `maple>amber` | 41 | 41-80 | alternate assertion path | 0 / 0 | loop_candidate=1 | none |
| 20611605 | `amber>birch` | 22 | 21-40 | identity mismatch | 0 / 23 | loop_candidate=3 | alternate_assertion_path |
| 20611605 | `sable>birch` | 31 | 21-40 | identity mismatch | 0 / 24 | loop_candidate=7 | alternate_assertion_path |
| 20611605 | `sable>teal` | 81 | 81-112 | identity mismatch | 0 / 68 | loop_candidate=5 | alternate_assertion_path |
| 20611606 | `crimson>teal` | 27 | 21-40 | identity mismatch | 0 / 4 | loop_candidate=1 | alternate_assertion_path |
| 20611606 | `ochre>amber` | 82 | 81-112 | identity mismatch | 0 / 27 | loop_candidate=1 | alternate_assertion_path |
| 20611606 | `teal>amber` | 51 | 41-80 | identity mismatch | 0 / 28 | loop_candidate=4 | alternate_assertion_path |
| 20611606 | `teal>willow` | 50 | 41-80 | identity mismatch | 0 / 2 | loop_candidate=1 | alternate_assertion_path |

## What the trace found

- **No recording gaps.** Every seed's replay served-world set equals its committed N3 set, and all 26 direct edges have zero direct service in both records.
- **18 identity mismatches.** Their endpoint pair was served only in the reverse orientation; the reverse is also a world edge, so this is an orientation mismatch in the direct record, not evidence that the directed edge was served. The loop/dream readout is symmetric, so the direct edge is asserted from the opposite orientation.
- **8 alternate paths.** Neither orientation was served; loop/dream structures carry the edge independently of the prediction window.
- **0 genuine residuals.** No edge is carried only by a prediction candidate, so the prediction path does not supply an assertion that service failed to provide.

## Controls

| Control | Expected category | Fired |
| --- | --- | --- |
| recording_gap_control | recording gap | yes |
| identity_mismatch_control | identity mismatch | yes |
| alternate_path_control | alternate assertion path | yes |
| prediction_residual_control | genuine assertion without service | yes |

## What this does not claim

A provenance classification of one readout on six seeds, one world family, one build and one cap. It does not show why loop/dream structures carry these pairs, whether serving them would change A_W, or that any engine change is warranted. The reverse-orientation bucket is a record-identity description, not an engine defect.
