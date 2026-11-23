# C6-TIMING-1 — fresh six-seed block result

**Status: RUN, 2026-11-13. Outcome: `C6 ORDER VARIATION CONFIRMED`.**

The block was frozen at `docs/c6_timing_prereg.json` before any seed was run. It uses six fresh seeds,
20621101–20621106, at 120 cycles and cap 40, with observer `off` and `on` on every seed. The one-seed
preflight seed 20611601 is excluded.

## 1. Outcome

Both timing orders occur on every seed, and every seed meets the preregistered floor of **10** edges
per order. The smallest per-seed counts were **22** `K_BEFORE_Y_IND` and **35** `Y_IND_BEFORE_K`.
`N1`–`N7` pass.

The result is checked by `benchmarks/c6_timing_guard.py`. It reads the frozen preregistration,
the six per-seed parts, the determinism rerun and this aggregate, then recomputes the per-order
floors and `N1`–`N7`. It refuses a `C6 ORDER VARIATION CONFIRMED` label unless all of them hold.
The guard passes on this record, and its tamper self-test rejects a lowered floor, a failed gate,
a changed determinism row and a passing block that omits the confirmation.

This clears the **C6 temporal-resolution requirement**: the non-carrier readout `Y_ind` exists and
the `K`/`Y_ind` order is not one-sided. It does **not** clear the two-path admission-by-carrier design,
which still has `A−`, `K−` and `Y−` unbuilt and unrun, and it is not a causal or capability result.

## 2. Per-seed counts

Counts are edge rows that appeared in the observer. `Rows` is the number of world edges with a
`Y_full` observation; `Y_ind` and `K` are the counts with that readout. `Asserted` is the final
live-set intersection with the world, reported separately and not used as the C6 denominator.

| Seed | World | Rows | Asserted | `Y_ind` | `K` | `K_BEFORE` | `Y_IND_BEFORE` | `SAME` | `NO_K` | `NO_Y_IND` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20621101 | 112 | 107 | 69 | 91 | 100 | 22 | 50 | 12 | 7 | 16 |
| 20621102 | 112 | 108 | 66 | 93 | 97 | 31 | 46 | 5 | 11 | 15 |
| 20621103 | 112 | 112 | 82 | 103 | 111 | 33 | 59 | 10 | 1 | 9 |
| 20621104 | 112 | 107 | 68 | 97 | 98 | 42 | 35 | 11 | 9 | 10 |
| 20621105 | 112 | 112 | 75 | 104 | 101 | 23 | 60 | 10 | 11 | 8 |
| 20621106 | 112 | 107 | 82 | 98 | 95 | 32 | 44 | 10 | 12 | 9 |
| **Total** | **672** | **653** | **442** | **586** | **602** | **183** | **294** | **58** | **51** | **67** |

The ordered set is the 535 rows in the three ordered classes. The 51 `NO_K` and 67 `NO_Y_IND` rows are
excluded as not measurable in the relevant readout, not read as zeros.

## 3. Gates

| Gate | Result | Evidence |
|---|---|---|
| `N1_neutrality` | pass on all six | off/on canonical reports identical |
| `N2_mutation` | pass | `--self-test`: `N1=True N2=True N3=True N6=False` on the synthetic no-variation stream |
| `N3_parity` | pass on all six | live-set `Y_full` equals final `structure_edges` |
| `N4_coverage` | pass | all 535 ordered rows have both `first_k` and `first_y_ind` |
| `N5_engine` | pass | `engine pin: 14 files at version 0.15.0`; `tests/test_v1_freeze.py` 12 passed |
| `N6_order_variation` | pass on all six | both `K_BEFORE_Y_IND` and `Y_IND_BEFORE_K` present |
| `N7_determinism` | pass | seed 20621101 fresh-process rerun: rows and counts identical |

## 4. What this does and does not establish

**Does:** on this world family, build and cap, the non-carrier assertion readout exists and the
`K`/`Y_ind` order varies in both directions across a fresh six-seed block, above a preregistered
per-order floor.

**Does not:** identify a mechanism, order the two events inside a cycle, establish carrier causation,
establish a readout-only graph, establish capability or transfer, or clear the two-path design. The
edge counts are not independent observations and no p-value is attached to them. One world family,
one build and one cap limit the scope.

The next two-path step remains blocked on `A−`, `K−` and `Y−`; this block supplies the C6
instrumentation result only.

## 5. Records

- Preregistration: `docs/c6_timing_prereg.json`
- Authorisation: `docs/AUTHORISATION-C6-TIMING.md`
- Machine result: `docs/c6_timing_block.json`
- Per-seed raw: `docs/c6_timing_parts/20621101.json` … `20621106.json`
  (the raw harness parts retain `not_a_result: true`; the block aggregate is the result)
- Determinism raw: `docs/c6_timing_parts/20621101_determinism.json`
- Guard: `benchmarks/c6_timing_guard.py` (`--check`, `--self-test`)
- Design: `docs/C6-ASSERTION-TIMING-INSTRUMENTATION.md`
