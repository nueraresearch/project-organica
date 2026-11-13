# C6-TIMING-1 — fresh six-seed timing block

**Status: FROZEN, RUN. Frozen 2026-11-13 before any seed in this block was run; run 2026-11-13.**

The completed block returned `C6 ORDER VARIATION CONFIRMED`; see
[`C6-TIMING-BLOCK.md`](C6-TIMING-BLOCK.md) and `docs/c6_timing_block.json`. The criteria below were
not changed after the outcome.

This is the preregistration for the C6 timing block. It is not a result and it authorises no
intervention.

## 1. Question

Across a fresh six-seed block, does the non-carrier assertion readout `Y_ind` exist, and does the
`K`/`Y_ind` order vary in both directions?

This is a measurement question. It does not select a causal mechanism and does not test carrier
causation.

## 2. Design

| | |
|---|---|
| Seeds | **20621101–20621106** (six fresh seeds) |
| Cycles | **120** |
| Cap | **40** |
| World | `generate_compositional_world(seed=, cycles=120)`, deterministic |
| Acquisition | `PHASE_ACQUISITION`, `env_acq` inside the window |
| Arms | `off` and `on` on every seed |
| Cells | **12** |
| Preflight seed | **20611601**, excluded from this block |
| Seed collision scan | empty at freeze time for 20621101–20621106 |

The preflight seed is excluded because its order counts were already seen. This block is fresh.

## 3. Readouts

- `Y_full` — assertion from all candidate types.
- `Y_ind` — assertion from all candidate types except `loop_candidate` and `dream`.
- `K` — assertion from `loop_candidate` and `dream` only.

`C6` is read only from `Y_ind`. `Y_full` is a parity readout.

## 4. Ordering classes

| Class | Condition |
|---|---|
| `K_BEFORE_Y_IND` | `first_k < first_y_ind` |
| `Y_IND_BEFORE_K` | `first_y_ind < first_k` |
| `SAME_CYCLE` | `first_k == first_y_ind` |
| `NO_K` | `K` never observed |
| `NO_Y_IND` | `Y_ind` never observed |

`SAME_CYCLE`, `NO_K` and `NO_Y_IND` are reported separately and are never folded into a direction.

## 5. Gates and minimums

`N1_neutrality` and `N3_parity` must pass on every seed. The engine pin must pass.

**Minimum per-order count:** at least **10** `K_BEFORE_Y_IND` edges and at least **10**
`Y_IND_BEFORE_K` edges on **each** seed.

**Coverage:** both orders must occur on at least **5 of 6** seeds.

There are no optional seeds and no seed replacement. The first six seeds are the block.

The committed block is checked by `benchmarks/c6_timing_guard.py`, which recomputes these
floors and gates before accepting the `C6 ORDER VARIATION CONFIRMED` outcome. The guard does not
change any rule above; it only refuses a label the committed evidence does not support.

## 6. Outcomes

| Outcome | Rule |
|---|---|
| `C6 ORDER VARIATION CONFIRMED` | `N1`/`N3` pass on all six; every seed meets both 10-edge floors; both orders occur on at least 5/6 seeds |
| `C6 NOT SEPARATED` | Gates pass, but a per-order floor or the 5/6 coverage rule fails |
| `C6 NOT MEASURABLE` | Any seed has no edge with `Y_ind` |
| `VOID` | Any `N1`, `N3` or engine-pin gate fails |

The primary report is the per-seed counts and the aggregate. No p-value is attached to the
order counts, and no mechanism verdict follows from this block.

## 7. Falsifiers

- A seed with zero `Y_ind` edges makes C6 not measurable for the block.
- A seed with only one order means the block does not establish order variation.
- An `N1` or `N3` failure voids the block.
- A changed engine pin voids the block.

## 8. Not authorised

This block does not authorise `A−`, `K−`, `Y−`, an engine edit, a version bump, a causal claim or V2
work.

## 9. Record

- Machine record: `docs/c6_timing_prereg.json`
- Authorisation: `docs/AUTHORISATION-C6-TIMING.md`
- Design: `docs/C6-ASSERTION-TIMING-INSTRUMENTATION.md`
- Runner: `benchmarks.c6_timing_observer.run_one_seed`
- Result: `docs/C6-TIMING-BLOCK.md`, `docs/c6_timing_block.json`
