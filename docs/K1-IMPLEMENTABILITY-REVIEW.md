# K1 implementability review — the point exists, the effect is already in the build

**Status:** `REVIEW 2026-11-19 — NO GRANT, NO CELL, NO ENGINE EDIT, NO TERM CHANGED`
**Registration under review:** [`constraint_registrations/K1-served-path.json`](constraint_registrations/K1-served-path.json) (`CONSTRAINT-K1-1`, `in-test`)
**Figures regenerated from:** [`phase_k_results_0.15.0.json`](phase_k_results_0.15.0.json) (shipping build) and [`phase_k_results.json`](phase_k_results.json) (frozen 0.9.0 record)
**Checker:** `python -m benchmarks.k1_implementability --check` (regenerates the panel from the two artifacts and fails on any disagreement)
**Superseded by:** [`K1-DISPOSITION-CHOICE`](K1-DISPOSITION-CHOICE.md) — K1 was retired as superseded before any cell on 2026-11-19; this review is kept as the dated record of what it found.

## 1. The answer, before the detail

Three findings, in order of how much they change the decision.

1. **The intervention is implementable without a frozen-engine edit.** The served set is built by
   `SleepService._build_predictions(temporal, freqs, prior_schemas=None)` in
   `organica/sleep_extraction.py`, and a dozen committed benchmarks already override exactly that
   method in-process. No file under `organica/` needs to change, so the engine pin holds.
2. **On the 0.15.0 build there is nothing left to force.** The K1 deficit the registration names —
   incremental structure not reaching the served path — is a **0.9.0** phenomenon. On 0.15.0 the
   late group is **already served**: recall is **1.000 on all ten seeds** and the late-group F1 is
   positive on every seed. The remaining 0.15.0 deficit is **precision**, and forcing more candidates
   into the window can only make precision worse.
3. **The registration's own observability clause is already satisfied in the negative.** It says the
   arm is `VOID` if "the forced-set selection point is not observable on the arm's build". The audit
   trace reconstructs the **Layer-5 hypothesis-retention** contest under `salience`; the forced set is
   the **Layer-1 prediction window**. They are different selection points, so on this build the
   clause fires.

**No grant should be considered until the hypothesis is re-scoped to the deficit 0.15.0 actually
has.** That is an owner act against a pre-registered constraint and this review does not perform it.

## 2. What the two builds' K1 cells actually contain

<!-- BEGIN K1 PANEL: generated from the two Phase K artifacts by benchmarks/k1_implementability.py; do not edit by hand -->
| Build | Seeds | Recall 1.000 | Recall range | Precision range | Pairs emitted | Late-group F1 range |
|---|---|---|---|---|---|---|
| 0.15.0 | 10 | 10 of 10 | 1-1 | 0.181818-0.189474 | 95-99 | 0.129032-0.134831 |
| 0.9.0 | 10 | 0 of 10 | 0.555556-0.666667 | 0.52381-0.578947 | 18-21 | 0-0 |
<!-- END K1 PANEL -->

*Pairs emitted is derived, not quoted: `round(18 x recall / precision)` against the K1 world's
eighteen gold pairs. The panel is generated and checked by
`benchmarks.k1_implementability`; the checker's self-test proves it rejects a tampered panel and a
non-full recall.*

Read the two rows together and the registration's mechanism is visible in the difference.

- **0.9.0 omitted the late group entirely.** Late-group F1 was **exactly 0.000** on all ten seeds,
  recall sat at 0.56-0.67, and Organica emitted **18-21** pairs — against the old
  `MAX_PREDICTIONS = 20` window. Its false positives were few (precision 0.52-0.58), and the late
  entity's pairs were not among what it emitted.
- **0.15.0 serves the late group and over-produces instead.** Recall is **1.000** on every seed, the
  late-group F1 is **0.129-0.135** rather than zero, and Organica emits **95-99** pairs against
  eighteen gold ones (precision **0.182-0.189**). The late structure is in the served set; it arrives
  inside a set roughly five times too large.

`MAX_PREDICTIONS` moved 20 -> 112 in 0.15.0 (`organica/sleep.py`, `DECISION-CAP-LEVEL` option C), so
the transition half of the window is 56 slots. The emission counts are consistent with that: the
0.9.0 cells emitted 18-21 pairs around the old 20-slot cap, the 0.15.0 cells 95-99 against the new
window. **The forced-
selection lever appears to have been spent by the cap raise rather than by any selection rule** — but
that is an inference from counts and the cap, not a measurement. Attributing the recall gain to the
cap would need a cap-matched arm, which this review does not run.

## 3. Why the registration's intervention cannot move this endpoint

`constraint_registration` names the intervention as *"force incremental updates into the served set"*,
and the endpoint as *"paired K1 difference (Organica minus the strongest-of-grid baseline)"*. On
0.15.0 those two do not connect.

**A forced set has nothing to add.** Recall is at its ceiling of 1.000: every gold pair, including
six late-group pairs, is already asserted by a surviving structure. Injecting late candidates into the
ranked transition list would displace correct early candidates from the same 56 slots and add
already-covered pairs. The pass bar needs F1 to reach 0.412 or better (a 0.10 improvement on
`-0.623961`); the direction a forced set moves precision is down, and F1 moves with it.

**The endpoint is not a channel for this intervention anyway.** `organica_pairs` unions fourteen
structure types and `edges_implied_by_structures` turns eight of them into edges — concepts, phrases,
loops, predictions, hypotheses, processes, workflows, dreams. Predictions are one source of eight.
Even a perfectly successful forced prediction set would be diluted in the aggregate, and there is no
committed field that would let a reader separate the forced edges' contribution from the rest. Rule
17(b) applies: *a trace records what happened; a replay records what would have* — a counterfactual
"was this pair asserted because it was forced" needs its own arm, not a field.

## 4. Harness and hook gaps, each one a build item

The gaps are numbered so a grant can name them. None is a run.

**G1 — no K1 gate.** `benchmarks/k2_gate.py` cannot be reused, and it refuses rather than bending:

| Reused as-is | Refusal |
|---|---|
| `EXPECTED_FAMILIES = ("K1", "K2")` and `preflight` requires exactly that set | `FAMILY_SET_MISMATCH` |
| `BASELINE_GAP = -0.5735` (K2's gap) | `BASELINE_PROVENANCE_DRIFT` when K1's `-0.623961` is passed |
| `K1_PRE_VALUE = -0.343658` (the 0.9.0 value) | `K1_PRE_VALUE_MISSING` / the `0.05` guard |
| `signature_problems` requires `overrides == ["_natural_selection"]` | `K2_SIGNATURE_MULTIPLE_OVERRIDES` for any `_build_predictions` arm |
| `_check_arms` requires a `boundary_cycle` partial and `association_age_source == "treatment_state"` | `ARM_PARAMETER_DRIFT` / `PRE_BOUNDARY_AGE_UNAVAILABLE` |
| `decide()` implements K2's rule | a K1 verdict would be read against the wrong thresholds |

A K1 block needs its own gate module, its own refusal matrix and its own decision function.

**G2 — the K3 guard family cannot run under the arm.** `CONSTRAINT-K1-1`'s PASS requires the K2 and
K3 paired differences to move by at most `0.05` absolute, so both guards must be measured under the
same treatment. `phase_k_campaign.task_k2` accepts a `primary_factory`; **`task_k3(seed, scale=1)`
does not**, and `_score_models` is called for K3 with no factory, so K3 always runs the shipped
engine. The K3 half of the registered guard is unmeasurable without editing the campaign.

**G3 — no treatment class and no evidence schema.** There is no `benchmarks/k1_served_path.py`.
`k2_pre_switch_retention`'s `manipulation` record and `ASSOCIATION_EVIDENCE_FIELDS` are
boundary-specific. A K1 arm needs its own record and a liveness check at the **returned-window**
resolution — proving the forced edges are in the list `_build_predictions` actually returns, not
merely in the pre-slice candidate list (rule 17(d): name the resolution of every check).

**G4 — the observability clause points at a different selection point.** §1 finding 3. Either the
clause is re-worded to name the Layer-1 prediction window, or the trace is extended to reconstruct
it; as written the arm is `VOID` on its own terms whichever way the treatment behaves.

**G5 — the registration does not define "incremental".** It names no cycle boundary, no candidate
rule (formed after cycle N? counts that rose this cycle? edges not in the prior served set?), no
forced-set size, and no displacement rule. Without those the arm is not single-variable, and the
`0.05` guards cannot be attributed.

**G6 — the budget terms in circulation are stale.** `MAX_PREDICTIONS` is 112, so
`transition_budget = returned_budget // 2 = 56`. Any design reasoning that says "the cap is 20" is
describing 0.9.0 and would size a forced set against the wrong window.

**G7 — no cap-matched attribution.** Given §2, the honest test of the registration's mechanism is
whether the **cap** rather than a **selection rule** produced the recall gain. That arm does not
exist, and without it a passing forced-selection block could not be attributed to its intervention.

## 5. What a grantable arm would have to look like

Stated as requirements, not as an authorisation. Each follows from a gap above.

- The hypothesis names the **precision** deficit, or the registration is retired as measuring a
  deficit the build no longer has. That choice is the owner's; this review only establishes that the
  current wording and the current build disagree.
- The endpoint carries a resolution that isolates the intervened channel, or the claim is explicitly
  scoped to the aggregate.
- The three guard families all accept the same factory.
- The liveness check operates on the returned window and can fail.
- The baseline, the pre-value and the thresholds come from one build, and the build is pinned before
  the cells and verified after.

## 6. What this review does not do

It runs no cell, opens no database, allocates no seed, grant, threshold or result, changes no engine
file or pin, and re-scores no verdict. It does not amend the K1 registration's terms —
`docs/constraint_registrations/K1-served-path.json` gains only a pointer to this page. The 0.9.0
artifact is untouched, and the 0.15.0 replication artifact is read, not rewritten.
