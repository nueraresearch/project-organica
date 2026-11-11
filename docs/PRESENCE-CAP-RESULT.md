# Presence to assertion: the cap-only experiment — result

Generated from `docs/presence_cap_run.json` by `python -m benchmarks.presence_cap_experiment --finish`. Do not edit by hand.

Protocol: `docs/PRESENCE-CAP-PREREGISTRATION.md`. Engine 0.14.0, unchanged; the only manipulated variable is the Layer-1 prediction cap.

**Verdict: `CAP LIMITING`**

| Reading | Value |
| --- | --- |
| bar | 10 |
| mean paired gain at 112 | 15.833333 |
| 95% paired lower bound | 8.081175 |
| reach-limited ceiling | 28.5 |
| gain over ceiling | 0.555556 |

| Seed | Cap | Present | S_ever (world) | A_W | A_pred | A_other | Windows | Cycles at cap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20611401 | 40 | 112 | 86 | 38 | 36 | 2 | 120 | 111 |
| 20611401 | 80 | 112 | 95 | 42 | 40 | 2 | 120 | 107 |
| 20611401 | 112 | 112 | 102 | 52 | 51 | 1 | 120 | 104 |
| 20611401 | 1000000000 | 112 | 112 | 112 | 112 | 0 | 120 | None |
| 20611402 | 40 | 112 | 70 | 48 | 39 | 9 | 120 | 113 |
| 20611402 | 80 | 112 | 95 | 51 | 50 | 1 | 120 | 108 |
| 20611402 | 112 | 112 | 104 | 63 | 62 | 1 | 120 | 104 |
| 20611402 | 1000000000 | 112 | 112 | 112 | 112 | 0 | 120 | None |
| 20611403 | 40 | 112 | 79 | 32 | 29 | 3 | 120 | 113 |
| 20611403 | 80 | 112 | 91 | 44 | 43 | 1 | 120 | 107 |
| 20611403 | 112 | 112 | 104 | 62 | 62 | 0 | 120 | 103 |
| 20611403 | 1000000000 | 112 | 112 | 112 | 112 | 0 | 120 | None |
| 20611404 | 40 | 112 | 73 | 48 | 36 | 12 | 120 | 113 |
| 20611404 | 80 | 112 | 89 | 48 | 40 | 8 | 120 | 107 |
| 20611404 | 112 | 112 | 103 | 62 | 61 | 1 | 120 | 104 |
| 20611404 | 1000000000 | 112 | 112 | 112 | 112 | 0 | 120 | None |
| 20611405 | 40 | 112 | 64 | 29 | 23 | 6 | 89 | 80 |
| 20611405 | 80 | 112 | 88 | 30 | 26 | 4 | 89 | 76 |
| 20611405 | 112 | 112 | 95 | 43 | 40 | 3 | 89 | 73 |
| 20611405 | 1000000000 | 112 | 112 | 112 | 112 | 0 | 89 | None |
| 20611406 | 40 | 112 | 70 | 43 | 34 | 9 | 120 | 112 |
| 20611406 | 80 | 112 | 84 | 44 | 36 | 8 | 120 | 107 |
| 20611406 | 112 | 112 | 96 | 51 | 48 | 3 | 120 | 104 |
| 20611406 | 1000000000 | 112 | 112 | 112 | 112 | 0 | 120 | None |

| Seed | A_W at 40 | A_W at 80 | A_W at 112 | A_W uncapped | Gain at 112 |
| --- | --- | --- | --- | --- | --- |
| 20611401 | 38 | 42 | 52 | 112 | 14 |
| 20611402 | 48 | 51 | 63 | 112 | 15 |
| 20611403 | 32 | 44 | 62 | 112 | 30 |
| 20611404 | 48 | 48 | 62 | 112 | 14 |
| 20611405 | 29 | 30 | 43 | 112 | 14 |
| 20611406 | 43 | 44 | 51 | 112 | 8 |

**What this does not claim.** This record measures admitted and asserted world-edge membership on one world family, one engine build and 120 cycles. It does not show that the cap causes the presence/assertion gap, that the gap is a defect, that any structure type is responsible, or that raising the cap would improve capability. `U`, the readout/use stage, is not measured. The uncapped level is a diagnostic ceiling, not a proposal, and a gain above the reach-limited ceiling is attributable to repetition rather than to reach and is reported as such.
