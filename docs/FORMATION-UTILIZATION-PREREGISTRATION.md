# Formation vs. Utilization — Preregistration

**Date:** 2026-10-30
**Status:** committed **before any cell of this experiment has run**. No result exists yet.
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
