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
* **Not settled: whether decay belongs in a supported engine, and whether
  decay-off is resource-sound over long runs.** The only counterfactual is 80
  cycles long.

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
mass grew 1,819 -> 6,981 — a factor of about 3.8 over 80 cycles, with no
long-run bound measured. Twenty-one and five are the *start* of the question, not
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
  curve and decline to certify restoration.

## 4. What this proposal does not do

* No threshold calibration, no grid change, no per-degree `tau`.
* No engine edit. A decay-off build would be a new version with its own identity
  record, changelog entry and regression test, and it would leave `0.12.0` and
  its record untouched.
* No amendment to `docs/COMPARISON-0.9-0.12-PREREGISTRATION.md`. That amendment
  is required before cells if a new version is used, and it is a separate act
  from this proposal.
* No claim that decay is useless. The matched comparison is what would speak to
  that, and it has not run.

## 5. Stop condition

This proposal closes when the owner sets the three decisions in §3 and
authorises or declines the decay-off build. Nothing runs before that, and the
existence of this document authorises nothing.
