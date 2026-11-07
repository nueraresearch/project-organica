# Decay operability — next-step proposal (2026-11-07)

**Status: a proposal. Not a pre-registration, not a decision, and not a run.**
No engine file is changed, `v0.12.0` stays immutable, and no cell is spent until
the owner sets the three open decisions in §3 and authorises or declines a build.

## 1. What the evidence settles, and what it leaves open

* **Settled: no threshold on the pre-registered grid passes for either arm.**
  448 calibration cells, degrees 2/4/6/12, seven thresholds, eight seeds; the
  transition arm and the ratio control both recorded *no global threshold clears
  all degree regimes* (`docs/DECAY-FIX-CONFIRMATION-PREREGISTRATION.md` §18), and
  no held-out cell was run.
* **Not settled: that every continuous value would fail.** Nothing here measures
  that, and there is no reason to investigate it by tuning the grid — the
  conflict is bracketed by adjacent grid points (§18), so a finer grid would land
  on the same wall.
* **Settled: `0.12.0` cannot sustain the protocol.** The reference arm dies by
  cycle 112 (`docs/RERUN-0.12.0.md`).
* **Settled: decay-off stays live for the matrix's full 3,000-cycle horizon.** The protocol
  run holds theories and beliefs through its final tenth, and its edge mass grows
  1,819 -> 197,753 (section 4). That is liveness at one horizon.
* **Not settled: whether decay belongs in a supported engine, and whether decay-off is
  resource-sound.** The growth curve has no pre-committed bound, so it cannot certify
  soundness (section 4, rule 19).

## 2. Direction recorded from the owner (2026-11-07, recommendation only)

1. **Decide whether temporal decay belongs in the supported engine.** If the
   priority is a usable engine, the pragmatic route is a new version with decay
   disabled by default, keeping `0.12.0` immutable, and checking long-run
   liveness and edge growth before calling the restoration release-ready.
2. **Keep the decay question separate from the build comparison.** The existing
   `0.9.0` versus `0.12.0` pre-registration asks whether the builds differ
   overall; it does not isolate decay. "Does decay help?" needs a matched
   decay-on/off comparison with the rest of the engine held fixed. A new engine
   version would also require amending that comparison protocol **before** cells.
3. **Return to the central science only on a live, supported build.** The
   structure-to-behavior design still requires the independent review before any
   seed is allocated.

## 3. What a restoration check has to measure, and what stays the owner's call

The counterfactual in `docs/RERUN-0.12.0.md`: with decay disabled the run held
21 stable predictions, 10 processes and 5 theories for all 80 cycles, while edge
mass grew 1,819 -> 6,981 — a factor of about 3.8 over 80 cycles, with no long-run bound measured. It has since been run to the matrix's
3,000-cycle horizon; section 4 records that result and why it still certifies no bound. Twenty-one and five are the *start* of the question, not
the answer to it: an engine whose edge mass grows without bound is not
"restored" merely because it is alive.

A check should therefore report, per horizon and per declared seed: liveness of
theories and beliefs in the final tenth of the run, stable predictions,
processes, edge mass and its growth per cycle, and the cycle at which any series
first empties. The horizons the repository already uses are 300, 1,000 and 3,000
cycles.
Implemented in `benchmarks/decay_operability.py`, which runs both arms on
the matrix's own settings and writes the report described here.

**Three decisions are the owner's and are deliberately left unset here:**

* **the seed block** for the check;
* **which horizons are actually spent**, given the cost on the owner's machine;
* **the edge-growth criterion** that counts as sound — no measured bound exists,
  and one chosen after seeing the growth curve would be taken from the run it
  judges (rule 19). The check must state its bar before cells, or report the
  curve and decline to certify restoration. The 3,000-cycle curve is now in hand
  (section 4), and that changes nothing here: a bar read off it is still taken from the
  run it judges. An a priori rate, or a bound calibrated on a run that is not the one it
  judges, remains the only honest route.

## 4. The 3,000-cycle operational measurement (2026-11-07)

The proposal asked for liveness and growth per horizon. The matrix's own horizon
has now been run: `benchmarks/decay_operability.py` at 3,000 cycles, the matrix's
world, cadence and hash seed, both arms in one process, stimulus `lattice_L1`.
The figures below are the **owner's, transcribed**; `docs/decay_operability.json`
is the authority and is **not in this worktree**, so nothing here was recomputed
from a per-cycle series, and the table is a new claim that must be checked
against the artifact when it is committed (rule 27).

| Horizon | shipped (`0.95`) | decay disabled (`1.0`) | edge mass | factor |
|---|---|---|---|---|
| 80 cycles (`RERUN-0.12.0.md`) | 12 stable, 3 processes, 0 theories at cycle 79 | 21 stable, 10 processes, 5 theories throughout | 1,819 -> 6,981 | ×3.838 |
| 3,000 cycles (this record) | theories die by cycle 37, beliefs by 112 (matrix arm, same build) | live through cycle 2,999 | 1,819 -> 197,753 | ×108.715 |

"Live" is the harness's own gate, not an impression: at least one theory in every
cycle of the last tenth, and a mean of at least two beliefs across it.

**The mass is accumulated weight, not a row count.** It is `SUM(precedes.count)`
over the `precedes` table, so 197,753 is transition weight and not
197,753 distinct edges — the artifact carries `edges` separately.
Reading the mass as a table size overstates storage by the mean per-pair count,
and it is the kind of unit slip that makes an operable engine look impossible.

**The relation set did not grow.** The run ends on **27 temporal-edge rows**
and a database about **1.55×** its starting size. 197,753 of weight across 27
rows is a mean of roughly **7,324.2 accumulated counts per pair**, which is what
repeated reinforcement of a small, fixed relation set looks like. So the three
figures agree with each other and disagree with the alarming reading: this is
not 200,000 new edges, and it is not a database that grew a hundredfold. The
mass grew because each stored pair was reinforced, not because more pairs were
stored — and a report that gives either the mass as a row count or the growth
as a storage multiplier has the mechanism backwards. Whether the row count was
already 27 at 80 cycles is the owner's reading, not something this table
checked: the shorter run's row count was not reported.

### What the growth does and does not license

Four cautions travel with the ×108.715 factor, and none of them is decoration:

* **No bar existed.** The payload's own `growth_criterion` reads `unset: no bound
  was pre-committed, so growth is reported and not judged` (rule 19), and a bar
  read off this curve is still taken from the run it judges.
* **A mean rate is not a trajectory.** 65.333 mass per cycle is the endpoint
  difference over the span. Whether growth decelerates, stays linear or
  compounds lives in the artifact's decile snapshots, which were not reported
  here — so this record says nothing about the shape, and a reader should not
  infer one (rule 28).
* **One seed, one stimulus, one horizon.** The claim is bounded to this world
  family and this build.
* **Storage did not track mass.** A 1.55× database against a 108.715× mass says
  the exposure here is not file size. Latency and CPU were not reported, so no
  cost estimate is offered — an engine can be live, cheap to store and too slow
  to use, and this run cannot tell those apart.

So the run **certifies liveness at 3,000 cycles for the decay-off arm**, and it
**does not certify resource soundness**: growth is monotone across the measured
horizon, no deceleration was measured, database size is recorded but is not a
growth proxy, and the criterion that would turn either into a verdict is unset.

### What it does not say about decay

It does not show decay is useless. The matched decay-on/off comparison with
everything else held fixed has not run, and this harness differs from the matrix
in its counters, not in its engine. It does not compare `0.9.0` with `0.12.0`.
And a 3,000-cycle live run is not the longitudinal study's horizon, which is
longer: liveness here is a precondition for calling a restoration build
release-ready, not a green light.

## 5. What this proposal does not do

* No threshold calibration, no grid change, no per-degree `tau`.
* No engine edit. A decay-off build would be a new version with its own identity
  record, changelog entry and regression test, and it would leave `0.12.0` and
  its record untouched.
* No amendment to `docs/COMPARISON-0.9-0.12-PREREGISTRATION.md`. That amendment
  is required before cells if a new version is used, and it is a separate act
  from this proposal.
* No claim that decay is useless. The matched comparison is what would speak to
  that, and it has not run.

## 6. Stop condition

This proposal closes when the owner sets the three decisions in §3 and
authorises or declines the decay-off build. Nothing runs before that, and the
existence of this document authorises nothing.
