# The use-path diagnostic — pre-registration

**Status: FROZEN.** Version 1.0, 2026-10-30. The protocol hash and the freeze commit are recorded in
`docs/use_path_diagnostic_freeze.json`; the runner refuses to start if the file's SHA-256 differs
from that record. Nothing in this document may be edited to match a result. If it is found wrong,
amend it, disclose the amendment, and re-freeze before any cell is run.

This is a **diagnostic**, not a V2 design and not a V2 build. It is the mechanism step that
`docs/ORGANICA-V2-DESIGN-BRIEF.md` gate 5 asks for after the formation-utilization campaign.

---

## 0. The record claim this protocol serves

> The formation-utilization campaign established that weak transfer despite correct internal
> structure is an observed ceiling condition and selected the use path as the target of
> investigation. It did not identify the binding component of that path and therefore did not, by
> itself, satisfy the mechanism requirement for a V2 build authorization.

The campaign is the source of the observation and of the target. It is not the source of a
mechanism, and it is not a build authorisation.

---

## 1. What the campaign established, and what it did not

The campaign ran 30 confirmatory seeds (`20261101`–`20261130`) on two tasks. Arm C held the
generator's full non-zero transition support at admission (cap 1,000, Layer 1 only) and read arm
B's fixed temporal graph at every cycle (Amendment 1). It therefore had **correct internal
structure at fixed evidence**. It still lost transfer on both tasks against the frozen bar:
T1 `d = −0.0262`, T2 `d = −0.0227` (98.33 % paired intervals, `d = bar − arm`). It lost retention
too (T1 −0.0267, T2 −0.0230), and won revision on T1 (+0.1002) while tying it on T2 (+0.0007).
B also lost transfer on both tasks (T1 −0.0296, T2 −0.0795), so the pre-committed "both lose"
cell fired.

Three limits are part of the record and are not repaired by this protocol:

1. C is a **counterfactual trajectory on B's temporal evidence**, not an independent organism.
2. C is **given** the structure; B is the discovery arm. The campaign is not a discovery result.
3. The campaign does **not** localise the defect inside the use path. "Retrieval / activation /
   readout" is a path, not a mechanism.

The campaign's T2 bar is the cell-level latent-state counter, which is granted the latent cell
structure; the protocol named the family "data-only" and that name is corrected in the record.
The verdict survives the strongest strictly data-only comparator (C loses T2 transfer to Replay by
0.0208 and to the bigram by 0.0187, and loses T1 transfer to Replay by 0.0262), so this diagnostic
inherits the verdict, not the naming defect.

---

## 2. The question, in the order it must be asked

**First:** at the evidence the campaign actually had, is there **measurable room** in the use path
— that is, could any predictor on the same contexts score better than the pinned readout, with the
ceiling as the upper bound? **Second, and only if the answer is yes:** which component of the use
path — retrieval/provenance, activation/aggregation, or the readout form — accounts for part of
that room?

The order is not rhetorical. Classifying a component before confirming that room exists is how a
diagnostic manufactures a mechanism. The dependency is:

```
D0 reproduction  →  room estimate  →  mechanism mapping
```

No stage may be interpreted out of order. A decomposition of the wrong object cannot produce a
mechanism, and a mechanism cannot be classified before the room is known.

---

## 3. The D0 validity gate

**D0 must reproduce the campaign's arm-C scores for all 30 seeds and all three scored limbs
(retention, transfer, revision) within `1e-4` absolute.** This is a validity gate, not a control:
a failed denominator check invalidates a variant; a failed D0 check invalidates the **object being
analysed**.

- The reference is `docs/formation_utilization.json`, the campaign artifact: for each
  `(task, seed)`, arm C's `scores[limb]["house_shape"]["log_loss"]`.
- The diagnostic re-runs B and C on the same seed, task, support, cap and fixed temporal basis as
  the campaign, and compares the re-run C scores with the artifact.
- The tolerance is `1e-4`, which is ten times the largest previously observed re-run drift
  (`1.4e-5`) and is still far below any effect the diagnostic treats as meaningful (`0.01` nats).
- If **any** seed or limb fails, the run is `status = audit_required`,
  `variants_interpretable = false`, and no room estimate or mechanism mapping is reported. The
  result document is titled **AUDIT REQUIRED** and contains no mechanism section.
- The gate is evaluated before any variant is interpreted. The runner writes `d0_reproduction` as
  the first field of the artifact; the analysis module raises `AuditRequired` if it is asked to
  map a mechanism when the gate failed; the result generator refuses to emit a mechanism section.

The gate is deliberately strict. A diagnostic that decomposes a different object than the one that
produced the ceiling result is not a diagnostic of that result.

---

## 4. The arms

All arms are scored on the same contexts and vocabulary as the campaign: retention `110–149`,
transfer `150–199`, revision `250–299` (cycles; the learning window `200–249` is where the revision
is acquired, not where it is scored). The support, the world, the base rate and the fixed temporal
basis are the campaign's.

| Arm | Isolates | Manipulation |
|---|---|---|
| **D0** pinned | reproduction | the campaign readout: full asserted structure, `α = 256` |
| **D1** Layer-1 only | retrieval / provenance | the asserted graph restricted to `prediction_candidate` edges |
| **D2** type-weighted | activation / aggregation | the full asserted graph with **declared constants**: Layer 1 `= 1.0`, every other structure type `= 0.5` |
| **D3** α sweep | activation / smoothing | the full asserted graph with `α` selected on the calibration seed from `{16, 64, 256, 1024}` |
| **D4** direct | readout form | a direct first-order conditional fitted on the exposure rows with a declared add-one constant (`1.0`), no backoff |
| **D5** ceiling | room | the generator's true conditional on the same contexts: regime 0 for retention and transfer, regime 1 for revision |

**D0** is the pinned readout. It is not "the engine"; it is the campaign's readout on C's asserted
structure. **D1** removes every non-Layer-1 contribution, which is the provenance question the
campaign's A7 measured at 94.0–97.7 % of edge weight. **D2** re-weights the same edges by type; it
does not change which edges are present and it does not re-fit anything. **D3** changes only the
smoothing of the same rows. **D4** changes the readout form: a direct conditional with no backoff,
which is the simplest alternative to the pinned backoff. **D5** is the upper bound: no predictor of
the same world can beat the true conditional in expectation.

D5 is a **ceiling**, not a learner. It is granted the world's law. A result from it is never a
capability claim.

---

## 5. D2 is constants-only

The D2 weights are **fixed constants written into this protocol**, not estimated, selected,
calibrated or fitted:

```
w(prediction_candidate) = 1.0
w(any other structure type) = 0.5
```

There is no selection step, no calibration on `20261099`, no reading of the campaign artifact, and
no code path from any score to these numbers. The code asserts the constants; a test proves they
are not derived from the 30 diagnostic seeds; a proof-of-firing test shows that changing a constant
changes the score. If the constants are changed after any score is seen, D2 is disqualified and the
result document says so.

The reason is not fussiness. A type-weighted readout whose weights were chosen by looking at the
campaign's seeds would be a tuned retrospective analysis wearing a diagnostic's name. The arm is
worth running only as a **constant** contrast: does moving weight from the uncontrolled layers to
Layer 1 help, at the values declared before the run?

---

## 6. Calibration

Only the D3 smoothing α is selected, and only on **seed `20261099`**, the calibration seed the
campaign already used for its comparator and α selection. For each task:

1. Build the calibration world and support.
2. Run B, then C with B's fixed temporal basis.
3. Score C's full asserted structure under each `α ∈ {16, 64, 256, 1024}` on the **transfer**
   window.
4. Select the α with the lowest transfer log-loss. Record every α's score and the selected value.

No confirmatory seed (`20261101`–`20261130`) takes part in this selection. D0 and D2 do **not** use
the calibration; their constants are fixed above. D4's add-one constant is fixed above. D5 uses the
generator's law, not a fitted parameter.

If the calibration seed's C arm fails to reproduce (for example, its support is not regime
invariant), the calibration is `not measurable` and D3 is reported as not measurable; the other
arms still run.

---

## 7. Scoring, orientation and uncertainty

- The score is the house pairwise log-loss (`evaluate_shapes(...)["house_shape"]["log_loss"]`),
  rounded to six decimals for reporting; the comparison uses the unrounded values.
- `d = D0 − arm`: **positive favours the variant**, because lower log-loss is better.
- For the room, `room = D5 − D0`: **positive means the ceiling is above the pinned readout**,
  i.e. there is room between the readout and the best possible score.
- Intervals are 98.33 % percentile bootstraps over **10,000** replicates, **paired by seed**. The
  bootstrap is `formation_utilization.paired_bootstrap`, which is already the committed
  implementation and refuses fewer than two seeds.
- An effect is a **win** only when the lower bound is above zero **and** the mean is at least
  `0.01` nats. A negative mean whose interval is wholly below zero is a **loss**. Everything else
  is a tie or not measurable. The 0.01 floor is declared before the run because the campaign's
  re-run drift is `1e-5`-scale and a 0.001-nat "win" would be indistinguishable from scheduling
  noise; 0.01 is also the scale below which the campaign's own C-vs-B differences were treated as
  not decisive.

The **primary limb is transfer**, because that is the limb the campaign lost and the limb the
use-path question is about. Retention and revision are reported as secondary; a variant that helps
transfer but loses retention or revision is reported as **partial**, not as a clean mechanism.

---

## 8. The pre-committed mapping

`helps(task, arm)` = transfer `d = D0 − arm` has lower bound > 0 and mean ≥ 0.01.
`loses(arm, limb)` = the paired interval for that limb lies wholly below zero.

| Outcome | Condition | What follows |
|---|---|---|
| **AUDIT REQUIRED** | any D0 seed/limb differs by more than `1e-4` | Stop. Diagnose the object; no room estimate and no mechanism mapping. |
| **EVIDENCE-LIMITED** | `room_mean < 0.01` on both tasks and no arm helps on either | The use path has no measurable room at this evidence. Redirect upstream to formation / estimation / evidence quality. Do **not** draft a use-path V2. |
| **MECHANISM CANDIDATE — retrieval/activation** | `room_mean ≥ 0.01` on both tasks and D1 or D2 helps on both | Draft a component-targeted V2 brief around retrieval/activation. If both help, name the larger transfer effect and report the other. |
| **MECHANISM CANDIDATE — readout form** | `room_mean ≥ 0.01` on both tasks and D3 or D4 helps on both, D1/D2 do not | Draft a component-targeted V2 brief around the readout form. |
| **UNKNOWN USE-PATH MECHANISM** | `room_mean ≥ 0.01` on both tasks and no arm helps on either | Room exists but the tested family cannot reach it. Investigate a different use-path family; do not redirect to formation and do not tune the same readout. |
| **TASK-DEPENDENT** | room or a helping arm differs between T2 and T1, and the difference is not explained by the pre-declared primary task | Report both; propose a two-target protocol, not a single-target V2. |
| **AUDIT ANOMALY** | a variant helps while `room_mean < 0.01`, or `room_mean < −0.05` | The ceiling and the readout disagree about the same object. Report the anomaly; do not claim evidence-limited or a mechanism until it is explained. |

A **partial** mechanism candidate is a candidate that helps transfer on both tasks but loses
retention or revision on either. It is reported with the losing limb named, and it does not become
a clean component claim.

The mapping is applied to T2 first (the primary task) and then checked against T1. If T2 and T1
disagree, the result is task-dependent unless the pre-declared primary task rule resolves it; the
protocol does not allow the better-looking task to be chosen after the fact.

---

## 9. Controls, each able to fail

1. **D0 reproduction** — the validity gate in §3. A 2e-4 perturbation must fail it; the test
   injects one.
2. **Known-answer** — each readout variant must recover a known deterministic relation on a toy
   world; a variant that cannot is disqualified.
3. **Shuffled evidence** — each variant must collapse towards the base rate when the evidence is
   shuffled; the test uses a size-matched shuffled rows table and asserts the score moves toward
   the base-rate score.
4. **Denominators** — every scored limb must have events and cells; a limb with a zero denominator
   is `not measurable`, never `0.0`.
5. **Attribution** — the per-type edge weights must reconcile to the full asserted structure; a
   mismatch fails the run, because the variants would be decomposing a different graph.
6. **Calibration isolation** — the α selection must use only `20261099`; the test asserts the
   diagnostic seeds are not in the calibration record.
7. **D2 constants** — the constants are asserted, not read; a proof-of-firing test changes one and
   watches the score move.
8. **One seed is not a test** — the bootstrap refuses fewer than two seeds; the analysis reports a
   single-seed cell as not measurable.

The diagnostic has no engine-side hook. It uses the same in-process subclass the campaign used,
and it adds no field to `organica/`. The behavior-neutrality of the recorder is already proven by
`tests/test_formation_utilization.py`; this protocol does not weaken that proof.

---

## 10. Seeds, tasks, sample size and cost

- Tasks: **T2 (primary)** and **T1 (control)**.
- Seeds: **`20261101`–`20261130`**, the campaign's 30 confirmatory seeds. No new scoring seed is
  added; the diagnostic is a decomposition of the campaign's own units.
- Units: 30 seeds × 2 tasks = **60 units**.
- Engine runs: B and C per unit = **120 runs**. D0–D5 are scored offline from the saved asserted
  structures; they add no engine runs.
- Calibration: 2 tasks × (B + C) = **4 additional runs** on `20261099`.
- Expected cost: the campaign's per-arm time was ~73 s; 124 runs at 10 workers is expected to be
  **15–25 minutes** wall clock, not the campaign's 12.7 worker-hours. The estimate is a planning
  figure, not a claim; the artifact records the actual per-unit seconds.
- A unit that fails to run, fails a denominator, or fails the support/regime checks is recorded as
  **not measurable**, not as a zero. The run does not silently drop a unit; a missing unit is named.

---

## 11. The result document

`docs/USE-PATH-DIAGNOSTIC-RESULTS.md` is generated from `docs/use_path_diagnostic.json` by the
harness's renderer. Its first section is the **D0 validity gate**. If the gate failed, the document
is titled **AUDIT REQUIRED** and contains no room estimate and no mechanism section. If it passed,
the document reports, in order:

1. the D0 gate and the maximum absolute difference;
2. the room estimate (`D5 − D0`) per task and limb;
3. the variant table (`D0 − arm`) with intervals, per task and limb;
4. the mapping and its named component, or the evidence-limited / unknown / task-dependent outcome;
5. the controls and their proof-of-firing status;
6. the limits: observer-side, post hoc, on the campaign's seeds, not a new learner, not discovery,
   not an efficacy claim, not a V2 authorisation.

Every number in the document is substituted from the artifact; no placeholder may survive. The
document is checked by a drift test that regenerates it and compares, and by a tampered-artifact
test that proves a failed gate cannot produce a mechanism section.

---

## 12. What this protocol does not establish

- It does not establish that the use path is the defect in general; it decomposes one world family
  and two tasks.
- It does not establish that a helping variant would help in a **deployable** setting: C is given
  the support and reads B's evidence. A component candidate is a hypothesis for a confirmatory V2
  protocol, not a demonstrated fix.
- It does not establish that the engine can form the structure; B remains the discovery arm and
  the formation limitation is untouched.
- It does not establish causality: the variants are re-scorings of the same asserted graph, not
  interventions on the organism.
- It does not authorise a V2 build. It can, at most, select a component for a V2 **brief**.

---

## 13. Stop condition

The diagnostic stops when one of the mapping outcomes in §8 is assigned and the result document is
written. It does not extend into a V2 design in the same run. A component candidate authorises a
**brief**, not a build. An evidence-limited result authorises a redirection of the V2 target
upstream, not a use-path V2. An audit-required result authorises an audit, not an interpretation.

The owner's build authorisation is a separate decision, recorded with its own date, budget and stop
condition. No result in this document can supply it.

---

## 14. Freeze and provenance

- Protocol version: **1.0**.
- Frozen: **2026-10-30**.
- Protocol SHA-256 and freeze commit: `docs/use_path_diagnostic_freeze.json`. The hash is over
  the **LF-normalized bytes**, so Git's line-ending conversion cannot invalidate the freeze.
- Campaign artifact: `docs/formation_utilization.json`.
- Engine: the frozen V1 engine; no file in `organica/` is changed.
- Runner: `benchmarks/use_path_diagnostic.py`.
- Tests: `tests/test_use_path_diagnostic.py`.
- This protocol was written **before** any diagnostic cell was run. The self-test and the
  calibration run may be executed only after the freeze commit; the confirmatory run may be
  executed only after the same freeze.
