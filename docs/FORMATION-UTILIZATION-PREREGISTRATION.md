# Formation vs. Utilization — Preregistration

**Date:** 2026-10-30
**Status:** committed **before any cell of this experiment has run**. No result exists yet.
**Amendment 1:** appended 2026-10-30 (§12), after the one-seed timing pass and before any
confirmatory seed. It fixes Layer 1's temporal basis at arm B's for the admission arms, adds
audit A8, and narrows what a C result can claim. Sections 1–11 stand as committed and are not
re-scored; §12 supersedes §3.3's "same counts" and §4's arm-table description of arm C's
substrate, and says what the amendment leaves in place.
**Engine:** Organica 1, frozen at `v0.9.0`; no engine file may change for this study.
**Parents:** `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` (world, tasks, limbs, readout,
calibration), `docs/GATE13-PAIRED-CAPACITY-TEST.md` (the cap-1,000 treatment),
`docs/GATE13-RANKING-CRITERION.md` (coverage and precision), `docs/ORGANICA-V2-DESIGN-BRIEF.md`
§11 (what a V2 may target).

---

## 1. The question, and the claim it can support

> **Given that the world's relation can be held at all, does holding it predict better than
> the strongest data-only learner — on retention, on transfer, and on revision?**

This is the cell the record does not have. Gate 13 established that the frozen engine
**cannot form** the world's relations at `MAX_PREDICTIONS = 20` (asserted coverage 0.0 %–2.7 %
against 100 % raw). The paired capacity test established that raising only that cap to 1,000
**does form** them (98.2 %–100 % on five diagnostic seeds, downstream selection does not
discard them). Neither scored the three limbs. Phase K's three REVERSED families are
**system-level** losses: they say the organism lost to strong baselines, not that it formed
the structure and failed to use it.

**What a result here can support:** a statement about **where the defect is** — formation and
selection, or use — and therefore which part of a future V2 would be aimed at the measured
gap. **What it cannot support:** that V2 is authorised, that the architecture is general, or
that the frozen engine can discover the law. Arm C is *given* the law's edges; it measures
utilization, not discovery.

This experiment **does not re-open** the acquisition study. Its P × E factorial remains
unrun and is not addressed here. The world, tasks, limbs, readout and calibration are reused
so the numbers are comparable; the cell matrix is new.

---

## 2. What is already known — design inputs, not predictions

| Fact | Value | Source |
|---|---|---|
| World edges that carry the law (T1) | **112** cross-cell edges | `docs/GATE13-RANKING-CRITERION.md` |
| Asserted coverage at cap 20 | **0.0 %–2.7 %** (0–3 of 112), five seeds | `docs/GATE13-PAIRED-CAPACITY-TEST.md` |
| Asserted coverage at cap 1,000 | **98.2 %–100 %**, five seeds, 110 cycles | same |
| Downstream selection discards cross-cell predictions? | **No** — they persist to the final store | same |
| Precision of the asserted set at any budget | **never above 0.3443**; per-source allocation does not help | `docs/GATE13-RANKING-CRITERION.md` |
| Readout | backoff-smoothed conditional, α = **256.0**, calibrated on seed `20261099` | `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §4.3, §6.4 |
| Readout's span on the compositional task | **0.978** of the achievable span; not the limiter | same, §4.3 |
| Seeds | **20261101–20261130**, 30 independent worlds, no raising n | same, §6.1 |
| Limbs and windows | retention 110–149, transfer 150–199, revision 200–249, revision held-out 250–299 | same, §4.4 |

**These are inputs. None of them is a prediction of this experiment's outcome.** In
particular, the 0.3443 precision ceiling is a *premise check* (A3), not a threshold on the
result.

---

## 3. Definitions, fixed in advance

**3.1 The world's support (the oracle set).** The set of transitions the task's **generator**
permits — its full non-zero transition support, materialized from the generator's own
parameters **before** any arm runs. It is not derived from the organism's state, from the
observed data, or from any scoring window. The **112 cross-cell edges** are a subset of it and
remain the numerator of the Gate 13 coverage metric; the support also contains the law's
self-recurrence, which §4.3 of the acquisition preregistration established is law-governed
and is counted by the endpoint.

**3.2 Coverage and precision.** As in `docs/GATE13-RANKING-CRITERION.md`:
`coverage = |asserted ∩ world edges| / |world edges|`,
`precision = |asserted ∩ world edges| / |asserted|`. Both are measured on the **final
acquisition store**, not on the readout.

**3.3 Oracle admission.** An in-process filter applied when Layer-1 prediction candidates are
built: a candidate whose `(source, target)` pair is **not** in the generator's support is not
stored. Nothing else changes — same engine, same stream, same counts, same thresholds, same
readout. The filter lives in the harness, never in `organica/`; when it is off, the substrate
is byte-identical to the unfiltered arm (proved by a substrate-equivalence test).

**3.4 The three scored limbs.** Exactly as `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`
§4.4: retention, transfer, revision, plus the revision-held-out window as a co-primary. Each
is scored per seed; each learner contributes one score per metric per seed.

**3.5 The endpoint.** The pinned prediction endpoint of §4.3: log-loss over
`|contexts| × |vocabulary|`, fixed denominator, the same labels for every learner, vocabulary
fixed from the acquisition phase, house shape primary and self-cell shape co-primary. A
result that flips between the two shapes is reported as flipping.

---

## 4. The arms, and what each one leaves behind

| Arm | `MAX_PREDICTIONS` | Admission filter | What it is | What it leaves behind |
|---|---|---|---|---|
| **A — control** | 20 | none | the frozen engine as published | the published failure: 0–3 of 112 asserted |
| **B — raw formation** | 1,000 | none | the Gate 13 treatment, run to the limbs | 98–100 % coverage at precision ≤ 0.3443; **no state change beyond the cap** |
| **C — oracle admission** | 1,000 | only the generator's support enters Layer 1 | utilization **given** correct structure | Layer-1 prediction candidates are exactly the world's permitted transitions; all other layers and all counts are untouched |

**What arm C is not.** It is not a learner competing with the baselines — it receives the
world's law at admission, which no data-only learner receives. Its score is a **ceiling on
utilization**, not a discovery claim, and it must never be headlined as "the organism learned
the law".

**What arm C does not clean.** The readout accumulates evidence over **all six structure
types** (§4.3). The oracle controls Layer-1 predictions only; concepts, loops, phrases,
meta-concepts and hypotheses still contribute whatever they hold. §7's audit **A7** measures
that share, and a failure with a non-trivial uncontrolled share is reported as **not
attributable to utilization** rather than as a utilization result.

**Observer-side decomposition (diagnostic, not an arm).** For B and C, the readout's evidence
is decomposed by structure type and by oracle membership, and reported. This is an
*observer-side* analysis and is labeled as such; per AGENTS rule 22 it may never be reported
as a mechanism result.

---

## 5. World, tasks, windows, seeds

- **Tasks:** T1 (the transition world) and T2 (the compositional world), exactly as
  `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §4.1–§4.2 defines them, including the
  withheld combinations and the discriminativeness gate already passed.
- **Cycles:** acquisition 0–109, then the four scored windows of §3.4.
- **Seeds:** `20261101`–`20261130`, **30**, paired by seed and by task. There is **no
  post-hoc raising of n**; the honest remedy for a wide interval here is to say the interval
  is wide.
- **Calibration:** all hyperparameters are frozen from seed `20261099` — Organica's
  α = 256.0, Replay `(1, None, 0.5)`, Statistical `(0.1, None, None)`. **No parameter is
  selected on a scoring window or a confirmatory seed.**
- **Compute:** 3 arms × 2 tasks × 30 seeds = **180 engine runs**, plus 2 comparison learners ×
  2 tasks × 30 seeds = **120 learner runs**. A **one-seed timing run precedes the campaign**,
  and the full campaign does not start until its cost is reported.

---

## 6. Comparators

| Comparator | What it answers | Status |
|---|---|---|
| **Replay** — stores episodes verbatim, retrieves, no model | can storing and retrieving account for the score? | tuned on `20261099`, grid declared in the acquisition preregistration §6.3 |
| **Best statistical learner** — first-order Markov and recency-decayed, swept over a declared grid, **best** configuration used | can transition counting do the task? | same; AGENTS rule 11 — no baseline is handicapped |
| **Base rate** | the "knows nothing" reference | computed, not a competitor |
| **Bayes ceiling** (T2) | how much room exists at all | computed, not a competitor |

The bar is the **best** of Replay and the statistical learner, per limb, chosen on the
calibration seed — never on a scoring window. Arm C is compared to the same bar; it is a
ceiling, so beating it is not required for the baselines.

---

## 7. The decision rule, pre-committed

**Per arm, per limb, per task:** the paired difference `d = score(arm) − score(best baseline)`,
with a **98.33 %** percentile bootstrap over **10,000** replicates, **paired by seed**
(Bonferroni across the three limbs; the same interval Phase K used). **Win:** lower bound
> 0. **Tie:** interval contains 0. **Loss:** upper bound < 0.

**Primary comparison: transfer.** Retention and revision gate the summary claim but do not
replace it.

**The mapping — exactly one of these is reported:**

| | **B wins transfer** | **B ties or loses transfer** |
|---|---|---|
| **C wins transfer** | Both formed arms beat the bar: **utilization works and precision does not bind the endpoint** → V2 targets use/abstraction, not selection. Report the retention and revision limbs beside it. | C wins, B loses: **correct structure is sufficient; the defect is what entered the store** → V2 targets candidate selection/precision. |
| **C loses transfer** | C loses while B wins: **the experiment is invalid** — A2 or A7 must have fired; report the audit, not the score. | Both lose: **utilization fails even with correct structure** → V2 targets the use path (retrieval/activation/readout), and the report names the limb. |

**A summary claim of "utilization works" requires C to win or tie on transfer AND not lose on
retention or revision.** Anything else is reported limb by limb, with the failing limb named.
Every branch publishes; a tie is a tie, and an unmeasurable quantity is reported as **not
measurable and excluded**, never as zero.

---

## 8. Audits — each must be able to fail

The campaign does not report a score until all seven pass. Each audit ships with a test that
**fires**: the test mutates the condition and asserts the audit rejects it.

| # | Audit | Passes when | Fires when |
|---|---|---|---|
| **A1** | **Arm differential** | coverage(A) < 0.50 and coverage(B) ≥ 0.50 and coverage(C) ≥ 0.50, per seed | any arm's coverage sits on the wrong side; then the arms did not differ and the campaign **stops** |
| **A2** | **Oracle exactness** | C's admitted set equals the generator's support, with no extra and no missing pair above the count threshold | a single injected false edge is admitted, or a permitted edge is dropped |
| **A3** | **Precision premise** | B's precision ≤ 0.3443 + 0.01 on every seed; C's admitted precision = 1.0 by construction | B's precision leaves the measured band — the premise changed and the mapping is void |
| **A4** | **Denominators** | every limb has ≥ 1 scored event on every seed; exclusions counted and reported | a limb is empty; that limb is reported **not measurable**, never zero |
| **A5** | **Readout matches construct** | the readout's score on a synthetic world with a known answer recovers that answer | the readout can manufacture a loss (the failure §9.3 records) |
| **A6** | **No leakage** | shuffling the oracle set makes C collapse to B's coverage and precision | C still scores well with a shuffled oracle — the oracle is not doing the work, or the readout is reading ground truth |
| **A7** | **Attribution share** | the oracle-controlled structure types carry the majority of the readout's evidence in C | the majority comes from layers the oracle does not control; the result is **not attributable to utilization** |

---

## 9. What this does not decide

- **It does not authorise a V2 build.** It selects a *target* for one; the build gates in
  `docs/ORGANICA-V2-DESIGN-BRIEF.md` §7 still stand.
- **It does not change the engine.** The oracle filter is harness-side and off by default.
- **It does not test discovery.** Arm C is given the law's support; arm B is the discovery
  arm, and its formation result is already known.
- **It does not re-score Phase K or Phase L**, and it does not reopen the acquisition
  factorial.
- **It does not generalise beyond T1 and T2.** A result here is a result on these worlds.
- **It does not add a fourth arm after seeing a score.** If A7 or A2 fails, the report says
  the experiment is not attributable — it does not add arms until one is.

---

## 10. Stop condition

**The specification is frozen when committed.** The harness may be **fixed** if it is found
wrong, and every fix is disclosed; **no feature may be added** after this document is
committed. One campaign is run. If an audit fails, the campaign stops and reports **not
measurable** with the audit named — never a zero, never a relaxed gate. The artifacts are
`docs/formation_utilization.json` and `docs/formation_utilization.md`, written from the run,
not by hand.

---

## 11. Where every number in this document comes from

| Number | Source |
|---|---|
| 112 world edges | `docs/GATE13-RANKING-CRITERION.md` |
| 0.0–2.7 % / 98.2–100 % coverage | `docs/GATE13-PAIRED-CAPACITY-TEST.md` |
| 0.3443 precision ceiling | `docs/GATE13-RANKING-CRITERION.md` |
| α = 256.0; Replay `(1, None, 0.5)`; Statistical `(0.1, None, None)` | `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §6.4; `docs/acquisition_alpha_calibration.json`; `docs/acquisition_baseline_calibration.json` |
| 0.978 of span | `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md` §4.3 |
| Windows 110–149 / 150–199 / 200–249 / 250–299 | same, §4.4 |
| 30 seeds, 20261101–20261130 | same, §6.1 |
| 98.33 % interval, 10,000 replicates, paired by seed | Phase K precedent, `docs/PHASE-K-PREREGISTRATION.md`; Phase L Amendment 3 for the pairing |

---

## 12. Amendment 1 — the temporal basis is fixed at arm B's (2026-10-30)

**Status:** appended after the one-seed timing pass
(`docs/formation_utilization_timing_pre_amendment.json`) and before any
confirmatory seed. It is a recorded amendment, not a re-scoring: no criterion in
§7 or §8 is relaxed, and the pre-amendment scores are not carried forward as a
result. The owner's instruction of 2026-10-30 is the decision.

### 12.1 What the timing pass found

The arms do not share a temporal graph. The pre-amendment pass measured, at the
end of acquisition:

| Task | Edges (B vs C, acquisition end) | Symmetric difference | Cycles differing | Missing / extra |
|---|---|---|---|---|
| T2 | 374 vs 380 | 32 | 59 of 131 (first at cycle 6) | 248 / 172 |
| T1 | 362 vs 351 | 21 | 107 of 160 (first at cycle 40) | 274 / 120 |

The mechanism is `organica/memory.py::_record_temporal_edges`. It is called
only for world events — `store()` skips it when `event_type == "sleep"` — but
its window is `SELECT tags FROM events ORDER BY time DESC LIMIT 3`, and sleep
rows are rows of `events`. A sleep row is therefore never an edge source, but
it **occupies a window slot** for the first world events of the next cycle, and
its extracted tags become `tag_from` values for those events. The number and
content of sleep rows differ between arms by construction: A truncates at 20, B
at 1,000, C admits only the generator's support and S a shuffled set. The next
cycle's `precedes` counts therefore differ, and with them the Layer-1
candidates. B versus C was not "the same evidence with different admission"; it
was different evidence.

The arm table's "all other layers and all counts are untouched" was false for
this engine. This is the defect the diagnosis names; the amendment below is the
response.

### 12.2 The amendment

Arm C and the shuffled-oracle arm S read **arm B's per-cycle temporal graph**
instead of their own:

- **B is run first and is unchanged.** At the start of each sleep cycle, before
  any of that cycle's sleep rows are stored, the graph `_load_temporal()`
  returns is recorded. B is the published formation arm and the basis on which
  A1's coverage premise and A3's precision band were measured; changing B's
  graph would have invalidated both.
- **C and S are run with `_load_temporal()` returning that recorded graph for
  the same cycle index.** Each run asserts it consumed exactly as many graphs
  as B produced; a length mismatch stops the run.
- **A is unchanged.** It is the cap control, not part of the B/C contrast.
- **`organica/` is not edited.** The engine still writes each arm's own
  `precedes` table; under the amendment the sleep service does not read C's or
  S's.

The filter itself is unchanged: C's admitted set is the graph's
count-threshold-eligible pairs intersected with the generator's support, applied
before the cap; S uses the size-matched shuffled set.

**Why not make every arm sleep-blind instead.** That would change B, and with
it the calibration this protocol committed: A1's 98–100 % premise and A3's
0.3443 band were measured on B as shipped, and re-measuring either on the
campaign's own data is forbidden by AGENTS rule 19. It would also change what
A measures. Holding B fixed and giving the admission arms B's evidence fixes
the contrast without re-opening the calibration.

### 12.3 What the amendment fixes

The feedback path is closed at the layer that reads it. At every cycle C and S
receive the same `(source, target, count)` mapping B received, and therefore the
same eligible candidate pairs and the same per-pair evidence. The new audit
**A8** checks this at the resolution of the graph and the candidate stream:

- per cycle, the graph each admission arm **actually read** must equal B's (the
  service records what it returned, not what the harness meant to pass);
- per cycle, the eligible pair set must equal B's;
- evidence is compared on the pairs both lists carry, which catches a divergent
  frequency denominator;
- the two arms' logs must cover the same cycles; the run separately asserts the
  graph list is consumed exactly once per sleep cycle.

A8 is a **gate**. It ships with tests that fire on a differing graph, a
differing candidate stream, a cycle-count mismatch and differing evidence, and
with a test that the substitution is load-bearing — a deliberately perturbed
graph changes the store, and with the filter off the fixed-basis run reproduces
the captured arm's store and candidate dump (wall-clock fields normalized). A8
does **not** require the engine's own `precedes`
tables to agree: C's table is still written from C's own sleep rows, and its
symmetric difference is reported as a footnote so a reader can see the channel
exists and that Layer 1 no longer reads it.

### 12.4 What the amendment does not fix

- **B's graph still contains B's self-sourced edges.** B is the shipped engine;
  its own sleep rows occupy slots in its window. The amendment does not make the
  engine sleep-blind, so this study still cannot attribute anything to removing
  self-sourcing (the audit trace's D2; AGENTS rule 18).
- **C's own output still differs.** C admits fewer pairs; its sleep payload, its
  prior candidates and the structures built from them differ from B's. That is
  the treatment, not a confound: what is held fixed is the evidence the filter
  acts on, not the organism's subsequent state.
- **A and B remain closed-loop runs.** Only the two admission arms are given a
  fixed graph.
- **C is a counterfactual trajectory, not an independent organism.** It is the
  engine run on B's temporal evidence with a restricted admission. It is not a
  candidate deployable configuration, and its score is a ceiling conditional on
  B's evidence.
- **It does not test the filter inside the closed loop.** That would need either
  an engine-level change to the lookback (forbidden by the freeze) or a
  sleep-blind substrate for all arms (which would invalidate A3's band). The
  closed-loop question is left to a future protocol that can calibrate on data
  it does not judge.

### 12.5 What it changes about the claim

The primary B-versus-C contrast is now: *given the temporal evidence the
unfiltered arm actually had, what does restricting admission to the generator's
support do to retention, transfer and revision?* It is a paired, controlled
contrast — and it is narrower than "a filter inside the organism":

- A C win is evidence that **admission precision at fixed evidence** does not
  bind the endpoint; a C tie is evidence that any effect is below the
  resolution of this design. Neither is evidence that installing this filter in
  the shipped engine would reproduce the result, because the shipped engine's
  filter would change its evidence — the defect this amendment exists to
  remove.
- A C loss is evidence that correct structure at fixed evidence is not enough
  for the use path, with the same caveat.
- The result says nothing about self-sourced support: B's graph contains it and
  C inherits it. The study cannot use C to argue that self-sourcing was or was
  not the cause of anything.
- The protocol's question — does holding the relation predict better than the
  strongest data-only learner — is still answered by B (unchanged) and C (the
  conditional ceiling). The mapping of §7 is unchanged. A C result must carry
  the conditioning clause in the same sentence: *given B's temporal evidence*.

**No pre-amendment score is a result of this design.** The pre-amendment
artifact is preserved. Its C and S cells were measured under the confound, may
not be compared with the amended C as if the amendment were an improvement, and
are carried forward only as the diagnosis. B's cells are the reproducibility
check between the two passes, at the artifact's four-decimal precision: the
amended pass and the pre-amendment pass agree there, while at full precision the
untouched A arm also moves in the fifth decimal (up to 1.4 × 10⁻⁵). The check is
therefore reproducibility to about 10⁻⁵, not bit-identity — a property of the
engine and the readout, not of the amendment.

### 12.6 Audits and readiness

The audit set is now **eight**: A1–A7 as committed, plus A8. The campaign does
not report a score until all eight pass. A8 is gated on both tasks. The one-seed
timing pass is re-run under this amendment; its measured cost and A8 result are
recorded in `docs/formation_utilization_timing.json` / `.md`, not in this
document.

The amendment adds one audit because the fix has to be checked at the
resolution it claims. It adds no arm, no world, no metric and no hypothesis;
§10's stop condition is why the change is written as an amendment with a
recorded owner decision rather than as a silent harness change.

### 12.7 Provenance

- Pre-amendment timing artifact: `docs/formation_utilization_timing_pre_amendment.json`
  (seed `20261100`, 2026-10-30). The D1 table above is checked against it by
  `tests/test_formation_utilization.py::test_amendment_table_matches_the_pre_amendment_artifact`.
- Amendment decision: the owner's instruction of 2026-10-30, recorded before any
  confirmatory seed.
- Implementation: `benchmarks/formation_utilization.py` —
  `_AdmissionSleepService._load_temporal`, `audit_temporal_input`, and the
  B-first order in `run_task_seed`.
- Tests: `tests/test_formation_utilization.py` (A8 proof-of-firing, the fixed
  basis's equivalence and load-bearing checks, and the table check above).
