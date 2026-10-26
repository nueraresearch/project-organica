# Changelog

All notable changes to Project Organica are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning 2.0.0](https://semver.org/).

## Versioning in this repository — three separate namespaces

The words "v1" and "v2" appear in this project in three different senses.
They are deliberately distinct, and they are what the version number
*does not* refer to.

| Namespace | Form | Meaning | Current |
|---|---|---|---|
| **Package version** | `0.x.y` (SemVer 2) | the released, installable, citable artifact | **0.9.0** (unreleased) · 0.8.0 is the latest tag |
| **Architecture generation** | *Organica 1*, *Organica 2* | a generation of the eight-layer engine. Organica 1 is frozen; Organica 2 is planned | **Organica 1** |
| **Research campaign** | *Ablation Study 1*, *Ablation Study 2* | the experimental series. Study 1 is the eleven-condition ablation; Study 2 is the six-colony Tier-1 matrix | **Study 2 in flight** |

The package version is **pre-1.0**, which is the honest state: the public
API is not declared stable, and the MINOR/PATCH numbers carry the
meaning instead. `tests/test_versioning.py` asserts that the three
declarations — `organica.__version__`, `pyproject.toml` and `CITATION.cff`
— never drift apart, and that the version describes *this* commit: if a
tag for the version exists, it must point here. A version whose changelog
entry is marked `(unreleased)` is allowed to have no tag yet, because
there is nothing to check out.

---

## [0.10.0] — (unreleased)

**Organica 1 is frozen, and Phase L opens as a measurement phase rather than
another benchmark hunt.**

### Result — Phase L primary axis (V1): a reproducible crossing, and a criterion that did not pass

The Phase L campaign ran its primary axis to completion: **80 of 80 cells**,
8,057.8 s wall clock, 10 seeds per sweep point, `PYTHONHASHSEED=0` pinned and
recorded as the *actual* value, 99.00% decision interval, 10,000 bootstrap
replicates, against the frozen `v0.9.0` engine (verified unchanged by the
freeze test). **All four instrument audits passed on the live run**, and **no
cell was unmeasurable** — nothing was excluded and nothing was zeroed.

**Verdict: `H3-L — INCONCLUSIVE`.** The protocol's remedy for that verdict is
*raise n; conclude nothing*, and **no Phase L outcome authorises a V2** — the
secondary arms V2–V5 were deliberately not run.

| Label | DI (sd) | PI (sd) | DS | Latency | Seeds reaching DI > 0.5 |
|---|---|---|---|---|---|
| 1:4 | 0.000 (0.000) | 0.789 (0.078) | −0.789 | — | 0/10 |
| 1:3 | 0.000 (0.000) | 0.794 (0.070) | −0.794 | — | 0/10 |
| 1:2 | 0.000 (0.000) | 0.783 (0.096) | −0.783 | — | 0/10 |
| 1:1 | 0.000 (0.000) | 0.728 (0.055) | −0.728 | — | 0/10 |
| 2:1 | 0.283 (0.124) | 0.600 (0.122) | −0.317 | — | 0/10 |
| 3:1 | 0.722 (0.037) | 0.022 (0.039) | +0.700 | 347 | 10/10 |
| 4:1 | 0.739 (0.064) | 0.000 (0.000) | +0.739 | 285 | 10/10 |
| 6:1 | 0.750 (0.029) | 0.000 (0.000) | +0.750 | 236 | 10/10 |

**Three of the four pre-committed criteria are met.** DI is monotone increasing
with range 0.750; the curves cross at **3:1**, interior to the sweep; and the
crossing is reproducible under a paired bootstrap over seeds — interval
**[5.0, 5.0]**, **10,000 of 10,000** replicates finding a crossing, eight
alternative bootstrap seeds all `INTERIOR`, leave-one-seed-out 3:1 in **10 of
10** folds.

**Criterion 2 — *PI is monotone decreasing* — was not met.** Mean PI rises
0.789 → 0.794 between 1:4 and 1:3 (+0.005, against a per-point standard
deviation of 0.070) before falling monotonically through the rest of the
sweep. The criterion has no noise clause: it is evaluated on the mean curve,
and the mean curve rises. It was evaluated once by the committed code and it
failed; it was **not** re-read, relaxed, or reinterpreted afterwards, and the
stable RT was not allowed to stand in for the criterion that failed.

**A wording defect in the protocol is recorded rather than exploited.** The
`H3-L` bucket is described as *"intervals too wide to place RT"*, which is not
what happened — the RT interval is the narrowest possible and criterion 4
passed comfortably. The verdict is INCONCLUSIVE because criterion 2 failed, not
because the threshold could not be located. The next phase must say what
"inconclusive" means when the interval is narrow and a different criterion
failed.

**Established:** the instrument works and the pilot's flat line was an
artefact; the organism sits at the preservation pole (DI exactly 0.000, PI ≈
0.79) under low displacement pressure; on this axis DI and PI cross at 3:1 and
the crossing is highly reproducible. **Not established:** a boundary in the
`H2-L` sense, PI's monotone decrease, anything about capability, and anything
about the support ratio being *the* operative variable beyond this axis on
this engine.

Added `docs/phase_l_results.md` and the artifacts `docs/phase_l_results.json`
and `docs/phase_l_results.ndjson`. Journal §38, facts sheet §X, manual §8.10
and finding 15.

### Result — Phase L raise-n (n=30): the verdict stands, and the reason is now visible

The raise-n campaign finished: **240 of 240 cells**, 30 seeds per point,
12,738.1 s, `PYTHONHASHSEED=0` pinned and recorded as the actual value,
99.00% decision interval, against the frozen `v0.9.0` engine. All four
instrument audits passed on the live run and **no cell was unmeasurable**. It
is a strict **superset** of the n=10 run — the original ten seeds are the
first ten of the new list, so the 80 original cells were **reused, not
recomputed** — and the reuse was verified: all 80 are byte-identical in the
merged file.

**Verdict: `H3-L — INCONCLUSIVE`, unchanged — and now with TWO of the four
criteria unmet.**

| Criterion | n = 10 | n = 30 |
|---|---|---|
| 1. DI monotone increasing | **met** | **not met** |
| 2. PI monotone decreasing | not met | not met |
| 3. DI range ≥ 0.25, crossing interior | met | met |
| 4. RT interval excludes both endpoints | met | met |

**The Revision Threshold did not move:** still 3:1, interval **[5.0, 5.0]**,
**10,000 of 10,000** replicates finding a crossing, eight alternative
bootstrap seeds all `INTERIOR`, leave-one-seed-out at 3:1 in **30 of 30**
folds. Tripling n did not move the one quantity the phase set out to locate.

**The curve is a step function, not a ramp.** DI is **exactly 0.000** at
1:4–1:1 for all 30 seeds; **PI is exactly 0.000** at 4:1 and 6:1; DI ≈ 0.71
across the top; two sharp transitions in between. Revision latency goes from
**0/30** seeds reaching DI > 0.5 at 2:1 to **30/30** at 3:1 (mean 356 cycles,
median 351).

**Both failing criteria fail on steps whose 99% paired interval contains
zero** — +0.011 [−0.026, +0.044] at 1:4 → 1:3, and −0.007 [−0.037, +0.022] at
4:1 → 6:1 — while every step whose interval excludes zero is a real
transition. **A criterion that flips when n changes is measuring the draw,
not the organism:** resampling the 30 measured seeds, criteria 3 and 3b hold
in **100%** of random subsets, criterion 1 in 19.3% / 16.1% / 0%, criterion 2
in 12.0% / 6.6% / 0%, and **all four together in 2.9% / 1.2% / 0%**. Strict
monotonicity is not a property this organism's displacement curve has at any
practical n, and more seeds cannot turn a plateau into a ramp — so "raise n"
is exhausted as a route to satisfying criteria 1 and 2. **This does not
re-score the protocol:** the verdict stands, no boundary is claimed, and the
four criteria stand as written.

**The added seeds moved the curve more than resampling should allow** — DI at
6:1 0.750 → 0.697 (p = 0.0022) and DI at 2:1 0.283 → 0.164 (p = 0.0103)
against random 10-vs-20 splits — so a **seed-exchangeability audit** with 30
fresh, non-consecutive, pre-declared seeds was run to tell non-exchangeability
from an unlucky draw. It is an instrument audit and produces no experimental
claim. **The seeds are exchangeable**: the fresh scattered set gave DI 0.7241
at 6:1 against the campaign's own 0.7148 (30 seeds) and 0.7500 (its original
ten) — a difference of +0.0093, **p = 0.60** against random 30/30 splits of
all 60 measured values — and its own arbitrary half-split gap of **−0.0407**
has the opposite sign to the campaign's +0.0528 at similar magnitude. **The
original ten seeds were an unlucky high draw, not a seed-block artefact**, so
the paired bootstrap over seeds is sound.

`docs/phase_l_results.md` is rewritten for the raise-n result; journal §39,
facts sheet §Y, manual §8.11 and finding 16.

### Result — Phase L characterisation: regime behaviour, and a verdict that did not move

The raise-n result has been read and **published as a characterisation**:
[`docs/PHASE-L-SYNTHESIS.md`](docs/PHASE-L-SYNTHESIS.md). The protocol verdict
is **unchanged** — `H3-L — INCONCLUSIVE` — and the two are deliberately kept
as separate artefacts, the measurement record and the synthesis, neither
re-scoring the other.

> *Organica 1 does not appear to exhibit a continuous coherence–plasticity
> trade-off. It appears to exhibit regime behaviour separated by a
> reproducible transition region.*

**What survived increasing n:** the preservation plateau (**DI exactly 0.000**
for all 30 seeds across 1:4–1:1), the transition region, the crossing at
**3:1**, the reproducible RT (**[5.0, 5.0]**, 10,000/10,000 replicates,
leave-one-seed-out 3:1 in **30 of 30**), and the abrupt latency shift
(**0/30 → 30/30** seeds reaching DI > 0.5 between 2:1 and 3:1). **What did not
survive:** strict monotonicity, which got *weaker* as n grew — exactly as
expected if it was never a property of the organism.

**Raising n is exhausted on this axis and will not be repeated.** The reason to
raise n was to distinguish *the tiny PI reversal is noise around an otherwise
monotone curve* from *the curve is genuinely step-shaped* — worlds that predict
differently. n=30 distinguished them: the low-end steps are each consistent
with zero, the plateaus are exact across all 30 seeds, and the monotonicity
criteria fail *more* firmly. The campaign was not failing for want of
precision; it was failing because the curve is not the curve the protocol
expected.

**The dangerous question, answered.** *A stable, reproducible threshold at 3:1
— that is a boundary, isn't it?* **It is not.** A threshold divides a continuum
only if the trade-off is a continuum; here the curve is flat on both sides of
the crossing, and the crossing is stable because the organism **switches
regimes**. That is a real property of the measured system, and it is not the
property the protocol asked for.

**What comes next.** **V2–V5 remain unrun** — no Phase L outcome authorises a
V2. The secondary axes are now a more specific question than the one Phase L
was written to ask: not *which variable moves a smooth boundary*, but **why is
the curve step-shaped** — what sets the width and location of the transition
region.

Added `docs/PHASE-L-SYNTHESIS.md`; manual §8.12 and finding 17; facts sheet
§Z; journal §40.

### Added — the development audit trace specification (Phase M groundwork)

The specification for a **developmental auditability** record: the artifact
that would let an investigator reconstruct *why* a structure survived — what
evidence was used, how the claim was formed, what the competing candidates were
— **without asking the system**. Written against the frozen engine's **actual**
report fields and persistence limits, source-read on 2026-10-25.

**Level 1 (provenance) is available.** `get_ancestry()` reads parent links that
are already stored; the limits are depth 7 and the 4,000-event window, and a
parent outside the window means *not found in window*, never *no parent*.

**Level 2 (evidence) is available, with one correction.** `support_count` counts
**temporal transitions**, and `contradiction_count` is the subject's **competing
flow** — not a count of observations that contradicted the claim. The record
format as first proposed ("12 supporting observations, 4 contradictory
observations") would have put a false claim at the centre of the audit and is
corrected in the spec.

**Level 3 (selection) is available without instrumenting the engine.** The
report contains only survivors, but under the default `salience` policy the
whole contest — including candidates culled by the confidence rule and
candidates that lost on rank — is reconstructible from the report's own Layer-2/3
outputs plus the persisted priors. The plan is therefore **assembly, not
instrumentation**; a labelled observer build is the fallback, and it must prove
that recording the trace leaves the engine's outputs unchanged.

**Counterfactuals live behind a wall.** *"Candidate B would have survived
without A"* is a **replay**, not a trace: a separate run, a separate artifact,
its own label.

**Six acceptance criteria** for the eventual build, each able to fail:
evidence-replay exactness, selection-reconstruction exactness, ancestry honesty,
behaviour invariance, field-honesty, and trace/counterfactual separation.

**Two defects disclosed, neither patched** (Organica 1 is frozen):
`contradiction_count` is easy to misread, and the temporal graph's lookback
window has **no `event_type` filter**, so a supporting transition can originate
from the organism's own previous sleep payload while co-occurrence and
tag-frequency edges are world-scoped.

Added `docs/AUDIT-TRACE-SPEC.md`; manual §8.13 and finding 18; facts sheet §AA;
journal §41; AGENTS.md rule 17.

**And the specification's load-bearing claim was tested.** `benchmarks/audit_trace_probe.py`
is an **instrument probe, not an experiment about the organism**: it runs the frozen engine on
the frozen cause-world generator and, at every cycle, rebuilds the selection contest from
the report and the substrate and compares. **Default arm** (the engine's own belief cap of
15): **120 cycles, 1,412 beliefs checked, A1 evidence replay 0 failures, A2 selection
reconstruction 120/120 cycles.** **Stress arm** (cap 5, so the cap binds): **60 cycles, 290
beliefs checked, A1 0 failures, A2 60/60 cycles, 403 candidates lost on rank.** The default
arm alone was a weak test — its pool peaked at 12 against a cap of 15, so the
*lost-on-rank* branch never fired — which is why the stress arm exists and why the write-up
says so. **The checks can fail:** `tests/test_audit_trace_probe.py` breaks the auditor on
purpose and requires A1 and A2 to go red, and they do. **So the selection contest needs no
hook inside the engine** — assembly, not instrumentation. What is *not* established:
generality, the `stochastic` policy, the four remaining acceptance criteria, or anything
about learning.

Added `benchmarks/audit_trace_probe.py`, `tests/test_audit_trace_probe.py`, and the artifacts
`docs/audit_trace_probe.json` and `docs/audit_trace_probe_stress.json`; spec §10; facts sheet
§AA8.

### Added — the rule that keeps the audit trace from becoming a second inventory

An audit layer is attractive, and attractive things become projects. The trace
could have been built, extended and admired without ever adjudicating a question
the project wanted answered — which would make it a *second* inventory
("how many events resolve?"), and would swap one measurement habit for another.

**So the rule is pre-committed, not aspirational:** the next protocol's success
criteria must contain at least one **trace-derived diagnostic**, and a result
that fails it **fails the protocol even if the headline behaviour is correct.**

**The first instance is a disqualifier: *a predicted-correct result whose
supporting evidence is self-sourced is not a transfer result.*** The trace
reports the world/self split of every belief's support, because the temporal
graph's lookback window has no `event_type` filter and a supporting transition
can originate from the organism's own previous sleep payload (D2). That is
D2's first concrete use, and it turns a disclosed defect into a **live
scientific instrument** — a defect that can defeat a claim is worth more than a
defect that is merely recorded.

**Second guard:** the trace's own metrics — evidence-trace completeness,
lineage completeness, selection reproducibility — are **diagnostics of the
instrument**: reported, never criteria. An audit layer earns its keep by
adjudicating a live question, not by accumulating completeness.

Added spec §11; AGENTS.md rule 18; manual §8.14 and finding 19; facts sheet
§AA9; journal §42.

### Corrected — the audit-trace probe's headline, and three errors in the specification

The probe's first version reconciled the **aggregate** `precedes` table against
the engine's reported support counts. That demonstrates the auditor reproduces
Organica's *counts* and its *selection decisions*; it does **not** demonstrate
that it can identify the individual experiences behind a count. The
specification claimed the stronger thing, and is now corrected to say exactly
what was measured: **aggregate evidence reconciliation and selection
reconstruction passed.** Event-level attribution is now its own acceptance
criterion (**A7**), measured with a passive store-time observer.

**Three corrections to the specification, each verified against the source
before being written down:**

1. A cycle returns **14** candidate lists, not 13.
2. The engine's lookback window **includes the event being stored** —
   `store()` inserts the row before recording edges — so the window is the
   event itself plus two others, and **within-event tag pairs also become
   temporal edges**. The first replay rule was wrong.
3. **A post-hoc replay from the final log cannot reconstruct the window**: the
   engine's query has no `rowid` tiebreak, and sleep-candidate rows are
   pruned. Event-level attribution therefore **requires** a passive
   store-time observer, whose guard must mirror the engine's own
   `event_type != "sleep"` rule.

**Results.** Default arm: A1 1,412 beliefs / 0 failures, A2
120/120 cycles, A7 1,412 beliefs / 0 failures with 244 aggregate
edges reconciling exactly. Stress arm: A1 290, A2 60/60, A7 290, **403 candidates lost on rank**. A4
behaviour invariance passes — observer on and off produce byte-identical
reports apart from `ran_at`.

**D2 is now measured: 53,980 of 307,857 attributed support transitions (17.5%) are
self-sourced** — the prior event was the organism's own sleep payload. Roughly
one belief-support transition in six rests on the organism's own output. That
is the baseline the pre-committed disqualifier is read against.

**The probe found two defects in itself** — an observer that attributed
sleep-event transitions the engine never makes, and an invariance check that
compared a wall-clock timestamp — both caught by the checks rather than by
inspection. The generalisable lesson is now **AGENTS.md rule 17(d): an
aggregate is not an attribution; name the resolution of every check.**

### Corrected — the self-sourced figure's denominator, and the forced-tie arm

The probe's most quoted number — the share of self-sourced support — was
measured against the wrong denominator. It pooled the support of every reported
belief across every cycle in which that belief was reported; because a belief's
support count is **cumulative**, a transition that occurred early is counted
again in every later cycle where the belief survives. That pooled number counts
**support references**, not distinct evidence.

**Three views, kept apart** (default arm): **distinct evidence behind reported
beliefs** 802/4,481 = **17.9%** self-sourced — the disqualifier's figure;
**pooled support references** 53,980/307,857 = 17.5%; **all distinct transitions recorded**
5,436/12,583 = **43.2%**, including edges no reported belief ever rested on. Correcting
the denominator moved the headline only slightly (17.5% → 17.9%), and that agreement is worth
stating — but it surfaced a separate and much larger number: **43.2% of the organism's entire
distinct transition surface is its own sleep output**, against 17.9% of the evidence actually behind its
claims.

**The forced-tie arm is now run.** The engine's lookback query has no
tie-breaker, so the schema does not determine which rows a tied window selects.
The clock is patched so every four consecutive stores share a timestamp,
producing **479 stores with a genuinely tied window**; the observer reproduces the engine's
choice anyway and **A7 stays exact**. The honest statement: the *implementation*
is deterministic for identical queries over identical data, while the *schema*
still does not determine the window under a tie — the observer is the reason,
not a proof about the engine.

Added `docs/audit_trace_probe_tie.json`; the probe gained a `--force-tie` arm
and a distinct-evidence view; a seventh test requires the two views to stay
apart. Recorded in spec §3.3, §6, §10, §11; facts sheet §AA11; journal §44.

### Changed — the figure's population, and the disqualifier as a per-claim rule

**The 17.9% is a share of the union of the unique evidence transitions behind beliefs reported during
the run** — deduplicated, restricted to the edges those beliefs rested on. It is **not** a per-claim
share, and it is **not** evidence that self-sourced support caused an incorrect prediction.

**A run-level share cannot carry a per-claim claim**, so the disqualifier is now written against the
claim itself, in four conditions fixed in advance: report the world/self split for the **claim's own**
support; a **majority** of it must be world-derived; its self-sourced share must be **no higher than the
run's baseline rate** for beliefs; and the comparison is against the claim, never the organism in
general, with a failed condition **failing the protocol even if the prediction was correct**.

**The rule is conservative, and says so.** The contamination is **measured, not shown to be
consequential** — nothing yet shows that a self-sourced transition caused a wrong answer — so the
disqualifier is a statement about *what counts as evidence of transfer*, not a claim that the organism
is damaged by its own output. That is also why it is pre-committed: a criterion that only bites once
the harm is demonstrated would never bite at all. **Whether self-sourced support *hurts* is now a
measurable question**, and the trace is the first instrument that can ask it.

**The observer's window match is an implementation match, not a schema guarantee.** The engine runs
`SELECT tags FROM events ORDER BY time DESC LIMIT 3`; the observer runs the same ordering clause with a
wider projection, so the two are not byte-identical SQL. The match is empirical on the tested SQLite
implementation, and the evidence for it is **A7's exactness** — a window mismatch on any store would
have broken the reconciliation. The 60-cycle forced-tie artifact is committed as
`docs/audit_trace_probe_tie.json` (60 cycles, 479 tied windows, 0 mismatches).

Recorded in spec §3.3, §10, §11; facts sheet §AA12, §AA13; journal §45.

### Added — the acquisition experiment pre-registration, and two diagnostics that changed its questions

The blank-slate question is now **can experience create a structure that
remains useful after the originating experience is gone?** — and **does the
organism carry structure forward, reconstruct it from evidence, or do both
under different conditions?**

**Two read-only diagnostics, run before the design was written, and
quarantined in the pre-registration as design inputs rather than
predictions:**

- A surviving structure's parent set is identical in **94.5%** of 3,883 structure-cycles.
- **But 87.2% of all 8,416 lineage links point at structures re-derived in that same
  cycle** (12.8% carried) — so the lineage is **re-derived, not carried**. This corrects
  an earlier reading of mine that called the identical sets "carried forward"; the
  link-state measurement is the discriminating evidence.

**The engine's survival rule is asymmetric across layers**, and this is the fact the
design rests on: `_natural_selection` (`sleep.py:1752-1802`) decays and prunes **Layer 1
only** — `_candidate_key` returns `""` for every other type — so Layer 1 survives only
if current experience keeps producing its content key, while Layers 2–4 are never
decayed and persist as rows with re-derived edges. **"Persistent reconstruction" is
accurate for Layer 1 and misleading for the rest.**

**The trace shows the present lineage, not the historical one**: a candidate's identity
is a content hash that does **not** include the parent set, and parents are recomputed
each cycle, so the same content identity can carry a different lineage later.

**The design:** six cells (parent {removed, not} × source experiences {removed, not} ×
removal applied to the **observer** or the **organism**, because removing a parent from
the auditor's reconstruction tests the trace and removing it from the organism's state
tests the maintenance mechanism). **Q1 (internal persistence) and Q2 (external
provenance) scored separately.** Three outcomes tracked separately and per cycle, so a
crossover is detectable. **The sharpest prediction is computed from the source, not
fitted**: pruning after `⌈log(0.15/c)/log(0.8)⌉` cycles — 4 from c=0.3, 6 from c=0.5. And
the decisive control is a **replay learner** that stores episodes verbatim and
regenerates nothing: if continuity is reconstruction rather than recall, perfect recall
is the *harder* baseline.

Added `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`; manual §8.16 and finding 22;
facts sheet §AA20–§AA22; journal §48; AGENTS.md rule 22.

### Added — A3: the ancestry measurement, and a correction it forced on the specification

**A3 is met.** An ancestry auditor walks each cycle's reported structures' parent
chains against the engine's own cognition window and classifies every branch
that fails to resolve. **Lineage reachability 1.000** (8,061 of 8,061
structures resolve back to Layer 1 within depth 7), **evidence linkage 1.000**
(1,412 of 1,412 claims resolve to event ids with a world/self split), **zero
honesty errors**, and an empty structure-level truncation split — while the
branch-level count shows **105 aged-out branches**, because every structure
resolves through at least one branch still inside the window. The stress arm
(3,240 structures) and the forced-tie arm (3,988 structures) both return 1.000.

**The correction.** Spec §12 said the window was "the more likely binding
constraint", because it spans only 1.7 cycles. **That was wrong.** Surviving
candidates are re-stored every cycle, so a live ancestor stays in the window
however old it is — **a lineage's depth is bounded by the death of an ancestor,
not by the window's recency.** Measured: the window holds 3,998 candidates, the
oldest last stored 1 cycle ago, content spanning 2 cycles. The correction is
recorded in place, not quietly fixed.

**The answer to A3's key question.** The observer's limit and the architecture's
limit are the same limit: **the engine's cognition window IS its memory.** An
investigator cannot recover more developmental history than Organica retains,
because there is no more to recover. That is good news for the trace and a hard
ceiling on the project's distinguishing property.

**Two sweeps prove the truncation categories are reachable rather than inert:**
the window sweep falls from 1.000 at the engine's window to 0.000 at 25–50
candidates (68 aged out); the depth sweep falls from 1.000 at depth 7 to 0.221
at depth 1 (53 depth-truncated) — so **the engine's depth limit of 7 is not
binding; the chains are shorter than it.**

**Two defects the build caught in itself**, both found by the checks rather than
by inspection: the observer matched `sleep:meta_concept` with a prefix test
that excluded every meta candidate (the engine uses an exact comparison), which
produced spurious "missing record" verdicts; and the window sweep sliced the
wrong end of a newest-first list. Both fixed, and the ordering is now pinned by
a test.

Added `A3_ancestry_honesty` to the probe's artifact; spec §13 and the §12
correction; manual §8.15 and finding 21; facts sheet §AA18–§AA19; journal §47;
AGENTS.md rule 21; `tests/test_audit_ancestry.py` (7 tests, four of them
proof-of-firing).

### Fixed — a threshold that judged its own data, and a window span that was wrong by an order of magnitude

**The transfer rule's reference rate is now frozen.** The third condition read
*"no higher than the run's baseline rate"* — circular, because a threshold
computed on the same data it judges relaxes whenever that run's beliefs happen
to be unusually self-sourced. The reference rate is now **17.9%**, fixed from
the calibration probe, **not recomputed on the evaluated run**, re-calibratable
only on data that is not being judged, and labelled a **provisional calibration
value, not a precise universal cutoff** (one run, one world, one policy).

**The window span was wrong by more than an order of magnitude, and is now
measured.** This project asserted the 4,000-event cognition window spanned
"roughly 40–130 cycles". That was a guess. **Measured: the engine stores 2,374.68 sleep events per
cycle, so the window spans 1.7 cycles.** The correction is recorded rather than quietly fixed. A lineage that keeps
being produced stays inside the window (candidates are re-stored every cycle);
one that stopped being produced is gone within about 1.7 cycles.

**A3's definition is fixed in advance**, reporting three things separately:
*lineage reachability* (extant structures resolving back to Layer 1 within
depth 7), *evidence linkage* (extant claims whose support resolves to event
ids with a world/self split), and a *truncation split* — **aged out** (a
persistence problem) / **depth-truncated** (a representation problem) / *no
parent* / **missing record** (a data defect). Level 1 (developmental lineage)
and Level 2 (evidential linkage) stay separate: **success in one cannot stand
in for success in the other.**

**And the boundary A3 cannot cross: fidelity is not sufficiency.** Reproducing
the implemented rule — exactly, and under a binding cap — does not establish
that the reconstruction is a uniquely correct account of *why* a belief arose.

Added spec §12; facts sheet §AA14–§AA16; journal §46; AGENTS.md rule 19; the
probe now reports `A7_event_level_attribution.cognition_window`.

**Fixed — seven literal template placeholders in the specification.** `{ties}`,
`{t_dist:,}`, `{t_edges}`, `{t_cycles}`, `{t_a1:,}`, `{t_a2}` (committed in the second
and third review rounds) and `{share:.1f}` (introduced by this round's script and
caught before commit) had shipped inside sentences that assert results. Corrected
in place from the artifacts: 479 tied windows, 2,589 distinct transitions, 241
aggregate edges, 60 cycles, 692 A1 beliefs, 60 A2 cycles, 692 A7 beliefs, 17.9%
reference rate. A placeholder is **silent** — it reads as a sentence in a diff —
so it is now caught by a standing guard — `tests/test_doc_placeholders.py` — rather
than by another careful read. Facts sheet §AA17; journal §46; AGENTS.md rule 20.

### Amendment 3 — the raise-n campaign on the primary axis

The n=10 run produced `H3-L — INCONCLUSIVE`, whose protocol-specified remedy
is *"raise n; conclude nothing"*. The owner took that remedy literally and on
the primary axis: **same sweep, same protocol, same criteria, no edits.**
Seeds per point go **10 → 30** (the original 10 plus 20 new), so the campaign
is a strict **superset** — the 80 original cells are reused, not recomputed,
and 160 new cells are added. Sweep points, independent variable, metrics,
decision interval, the four success criteria, the four terminal outcomes and
the frozen engine are **unchanged**; the secondary arms V2–V5 remain unrun.

**A real defect was found while preparing the run.** The preregistration says
criterion 4 is a *paired* bootstrap over seeds, but the implementation paired
by **position in the records list** — and the records arrive in completion
order, which differs from label to label. Position-pairing therefore paired
unrelated seeds across labels: an unpaired resample wearing the word
"paired" on it. Each label now contributes a `{seed: value}` map and every
label is evaluated on the same drawn set of seeds. **The fix does not change
the n=10 result** — RT 3:1, interval `[5.0, 5.0]`, 10,000/10,000 replicates,
eight alternative bootstrap seeds `INTERIOR`, leave-one-seed-out 3:1 in
10/10, the same four criteria, the same verdict — so the n=10 record is kept
as `docs/phase_l_results_n10.json` / `.ndjson`.

**A new diagnostic: the adjacent paired differences.** The monotone criteria
are evaluated on the **mean** curve and therefore test the **sign** of an
adjacent difference; if the underlying curve is flat at one end of the sweep,
that sign is a coin flip at any n. More seeds settle the **effect size**. So
each adjacent pair now reports its paired difference with a 99% paired
interval. It is a diagnostic only — not a metric, not a criterion, in no
verdict.

**The analysis is committed code.** `benchmarks/phase_l_analyze.py` replaces
the uncommitted scratch script that produced the reported numbers.

Amendment 3 was committed **before the raise-n run existed**. 69 tests pass;
the four instrument audits pass.

### The freeze

**Organica 1 is frozen as of the `v0.9.0` tag.** Not abandoned, and not
"no more commits" — **no more architectural modifications to the engine.**
The engine becomes a fixed reference object: everything afterwards *measures*
it, and nothing afterwards *quietly changes* it.

Frozen: `organica/sleep.py`, `memory.py`, `paths.py`, `streams.py`,
`branch_streams.py`, `scale_streams.py`, `ground_truth_worlds.py`, and the
published result artifacts. Still free: benchmarks, harnesses, all
documentation, the action list, and tests for new instrumentation. The one
boundary rule: nothing may change the **behaviour** of the frozen engine.

**The freeze is enforced, not declared.** `tests/test_v1_freeze.py` reads the
frozen files out of the `v0.9.0` tag and compares them against the working
tree, failing and naming the difference if one differs, and skipping honestly
when the tag is not reachable. It was proved to fire by temporarily modifying
a frozen file and watching it fail. See `docs/V1-FREEZE.md`.

### Added — Phase L: Plasticity–Coherence Measurement

Phase L is not a benchmark hunt. Every previous phase asked *"can Organica do
X?"*; this one asks **how much pressure is required for new structure to
displace old structure?**

The protocol is frozen in
[`docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md`](docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md)
and was committed **before any Phase L outcome was generated**.

| | |
|---|---|
| **Hypothesis** | Organica 1 exhibits a measurable coherence–plasticity boundary; revision occurs only after a displacement threshold |
| **Primary axis** | support ratio (late : early), 8 points — the axis the K3 2×2 already located |
| **Secondary axes** | arrival timing, novelty density, belief-cap pressure, contradiction pressure — each swept **one at a time** |
| **Displacement Index** | `late_structure_retained / late_structure_available` |
| **Preservation Index** | `early_structure_retained / early_structure_original` |
| **Revision Threshold** | the pressure at which DI crosses PI — the headline quantity |
| **Success criterion** | a **reproducible displacement curve**, not a win: DI monotone up, PI monotone down, an interior crossing, and a bootstrap interval excluding both endpoints |
| **Terminal outcomes** | four, pre-committed — **none of them authorises a V2** |

The instrument audits are permanent and required. A **discrimination control**
must show that first-seen-wins scores DI ≈ 0 / PI ≈ 1 and last-seen-wins
scores DI ≈ 1 / PI ≈ 0, so the metric can tell "never revises" from
"always revises". An **endpoint ceiling check** must show a perfect model
scoring 1.0 on both indices. A **degeneracy audit** must show the design
itself is live: that every cell has a denominator to measure against, that
the support ratio actually changes the early/late event mix, that the
contradiction arm produces a different world from the plain arm, and that the
density arm actually changes the event count. The campaign does not run if any
of them fails.

**Launch is not run.** The protocol is written, the harness is built and
validated, and the protocol is reviewed before the campaign executes.

### Fixed — four harness defects found by the Phase L pilot

The reduced-scale pilot returned `DI = 0.000` at **every** point of the
support-ratio sweep — a clean-looking negative result that was in fact an
artefact. The support ratio was not varying anything. Four defects, all in
the harness's implementation of the protocol as written:

1. **The late group arrived after the run ended.** The arrival cycle was
   absolute rather than a fraction of the run, so at reduced scale the late
   group never became active and the late structure was never available to
   measure. Arrival is now proportional.
2. **An unmeasurable index was reported as `0.0`.** A ratio with a zero
   denominator was reported as "nothing was retained" for conditions in which
   nothing was available to retain. Undefined ratios are now `None`,
   excluded from the curve, and counted — never zeroed.
3. **The contradiction arm was a no-op.** It shared a feature of the late
   group with itself, producing a byte-identical world with the arm on and
   off. The shared feature now comes from the early group, so the two groups
   actually compete for the same subject.
4. **The density arm fed the engine only part of the world.** The event
   stream was chunked at a fixed rate while the density arm varies it, so at
   density 4.0 the engine saw 7,200 of 28,800 events while the harness
   reported a complete run. The world's own event rate is now used.

Also corrected: the Revision Threshold bootstrap was resampling the DI−PI gap
rather than the **crossing location** that criterion 4 is about, and was
reporting a min/max rather than the preregistered percentile interval. Seeds
are now resampled paired across labels, and "excludes both endpoints" is
tested directly against the sweep.

Recorded as **Amendment 1** in the preregistration, made before any Phase L
outcome existed. No hypothesis, variable, metric, baseline, success criterion
or terminal outcome was changed, and no gate was relaxed — one audit was
added.

### Changed — the Phase L decision interval is 99%, not 98.33%

The Phase L protocol stated a **98.33%** decision interval and glossed it as
"Bonferroni across the arms". Those disagree: across five arms Bonferroni
gives 0.05/5 = 0.01, i.e. a **99%** interval, while 98.33% corresponds to
0.05/3 — Phase K's correction factor, carried over by accident.

**The owner's ruling, made before any Phase L outcome existed: the intent
governs and the stray percentage is the accidental constant.** The procedure
is preserved and the number is corrected to 99%. Phase K's own 98.33%
figures are unaffected — that protocol had three families and 0.05/3 was
correct there. Recorded as **Amendment 2**.

Amendment 2 also adds a plain statement of what success and failure look
like (preregistration §6.1): success is a stable displacement curve with an
interior, reproducible crossing; failure is a flat DI, a flat PI and no
crossing — a characterisation, and a publishable one. **The campaign must be
able to fail.**

### Added — the two preregistered secondary outcomes the harness was missing

The protocol declares three secondary outcomes. The harness computed only
"absolute late incorporation"; **revision latency** and the **knowledge
preservation trajectory** are now computed from a per-cycle DI/PI trace taken
as the engine runs. The trace is per-cycle rather than cumulative, so it
answers *when did the organism start asserting the late structure*; the final
indices are still computed from the last report alone and the trace does not
change them.

### Fixed — a false record in the results file

The results file recorded `"python_hash_seed": "0"` unconditionally, asserting
the pinned value whether or not it was set. It now records the **actual**
value, records whether the pin was met, and warns loudly when it was not.

---

## [0.9.0] — 2026-10-24

**The project question changed: from *can we make a developmental
architecture?* to *what class of problems benefits from one?* Phase K opens
the search for that task.**

### The reasoning

Phases H, I and J were three preregistered attempts to show an external
advantage and all three were negative. That is not the same statement as
*V1 failed*:

> V1 develops interesting internal structure. We do not yet know what
> problem that structure solves.

Three tasks were negative; an infinite number of tasks were not tested. So
**no V2** — the design of a successor architecture cannot be justified while
the advantage it would provide is unknown. Designing V2 first would make V2
guesswork.

### Added — Phase K: Comparative Advantage Search

A **search**, not a test. The question is *what is Organica uniquely good
at?* Three candidate task families, each derived from a mechanism the
project has actually measured, each scored against the strongest simple
baseline that could plausibly solve it.

| Family | Mechanism it targets | The baseline that could beat it |
|---|---|---|
| **K1 — Incremental world modeling** | question generation drives novelty assimilation | online co-occurrence, which won Phase H at 0.8000 vs 0.7041 |
| **K2 — Belief revision** | falsification and contradiction drive revision | change-point detection plus wholesale relearning, with a forgetting window |
| **K3 — Longitudinal knowledge integration** | dreams integrate beliefs into coherent structure (P4, SUPPORTED) | sliding-window co-occurrence, which must trade retention against acquisition |

The protocol is frozen in [`docs/PHASE-K-PREREGISTRATION.md`](docs/PHASE-K-PREREGISTRATION.md)
and was committed **before any Phase K outcome was generated**. Three things
in it keep the phase honest:

1. **The baselines get the tuning advantage.** Every simple baseline is swept
   over a declared grid and its *best* score is the number used. A strawman
   baseline is the most likely way to manufacture a false positive, and it is
   impossible by construction.
2. **The harness is validated before the campaign runs.** The Phase H
   held-out task is rerun through the same code, where Organica's loss is
   already known (0.412605 vs 0.504039). If the harness reports a win
   there, the campaign does not run.
3. **"No family confirmed" is a pre-committed terminal outcome.** Three more
   families ruled out is a publishable result, and it does not authorise a
   V2.

Decision rule: paired percentile bootstrap over ten seeds, **98.33%**
interval (Bonferroni across the three families), SUPPORTED only when the
interval for Organica − best simple baseline lies wholly above zero.
Attribution — whether the hypothesised mechanism is actually implicated — is
reported from a matched within-architecture ablation and is kept separate
from the success criterion.

**The pilot, disclosed.** The harness was run once at one seed and one tenth
of every cycle count before the protocol was frozen. Organica was behind the
baseline in all three families. That is one seed at ten per cent of the
protocol and it is **not evidence**; it is recorded in the preregistration
so it cannot later be mistaken for a result.

### The result — the search failed, and that was pre-committed

The campaign ran to completion: **ten seeds per family**, thirty in total. All
three families came back **REVERSED**.

| Family | Organica | Best simple baseline | Paired difference | 98.33% interval | Verdict |
|---|---|---|---|---|---|
| K1 — incremental world modeling | 0.5923 | 0.9360 | −0.3437 | [−0.3773, −0.3123] | **REVERSED** |
| K2 — belief revision | 0.4111 | 0.9846 | −0.5735 | [−0.6162, −0.5309] | **REVERSED** |
| K3 — longitudinal integration | 0.0000 | 0.8578 | −0.8578 | [−0.8598, −0.8571] | **REVERSED** |

No family is SUPPORTED and none is INCONCLUSIVE: every decision interval lies
wholly below zero, so these are clean losses rather than ambiguous ones. Every
verdict survives eight different bootstrap seeds and both leave-one-out
checks. The **H2** terminal outcome fired exactly as written down before the
run: three more task families are ruled out, the negative-results map grows,
and **no V2 is designed**.

**The ablations came back empty — a negative attribution.** `NO_QUESTIONS`
(K1) −0.0095 [−0.0328, +0.0140]; `NO_FALSIFICATION` (K2) +0.0241 [−0.0048,
+0.0495]; `NO_DREAMS` (K3) +0.0000 [0.0000, 0.0000]. All three intervals
contain zero, so the three mechanisms the families were built around are not
load-bearing for the tasks they were meant to carry. This is within one
implementation on synthetic worlds, and it does not say the mechanisms are
inert in general.

**The K3 zero was root-caused, not assumed.** Organica scored exactly 0.000
on late incorporation on all ten seeds while a trivial co-occurrence counter
reached 0.857, so three artifacts were checked — each capable of failing.
The late structure appears in **zero of 150 cycles**, so it is not an artifact
of reading only the final cycle. Every candidate type except `anomaly` mentions
**zero of 12** late tags, so no late structure was left unread by the edge
extractor. And a 2×2 control across five seeds shows the late group is
incorporated **only when it is strictly stronger** than the group that arrived
first — so the exclusion is a salience/priority competition under a bounded
belief pool, not a blanket inability to learn late structure. This is the risk
§6 of the preregistration named before the run.

### Added

- `docs/V1-SYNTHESIS.md` — **the formal synthesis of V1.** What the project established, what it did not, the distinction between the two goals it could serve, the danger of reading six negative task families as a verdict rather than a map, and the question the evidence leaves open: *what properties must a developmental intelligence have to remain adaptable without losing coherence?* It adds no new evidence — it is a reading of the record, and every claim in it cites a committed artifact.
- `docs/phase_k_results.md` — the Phase K write-up: results, robustness, the
  K3 root cause, and what it changes.
- `docs/phase_k_results.json` — the campaign artifact: protocol block, the K0
  control, the ceiling check, all thirty per-seed records with every model's
  score and configuration, and the per-family summaries.
- `docs/phase_k_results.ndjson` — the live recording, one line per completed
  seed, appended and flushed.
- `benchmarks/phase_k_diagnose.py` — the K3 root-cause diagnostics: the
  per-cycle check, the under-read check, and the arrival-order × strength 2×2
  control.

### Changed

- The package version is **0.9.0**, cut on master; **0.8.0 is the latest
  release**. 0.8.0 was a research-integrity release: corrected clone
  verification, corrected version/tag semantics, the missing campaign
  artifacts regenerated, the cycle-1 fixation claim corrected (journal
  §31), the negative external-validity results recorded, and the
  documentation synchronised with the measurements.
- Journal §32 records the strategic shift and the negative-results map;
  **§33 records the Phase K result**, its robustness, and the K3 root cause.
- Facts sheet **§T** records the result in the one-fact-per-line form.
- The manual's status row for Phase K, its command list, its file map and its
  revision log are updated in the same turn as the change they describe.

---

## [0.8.0] — 2026-10-24

**The external-validity arc: three preregistered campaigns asking whether
Organica's structure buys anything over trivial baselines. The honest
answer recorded here is negative.**

Full detail in research journal §24–§30 and in
`docs/PHASE-H-PREREGISTRATION.md`, `docs/REGIME-SHIFT-PREREGISTRATION.md`,
`docs/PHASE-J-ADAPTATION-PREREGISTRATION.md`.

### Corrected — the structural plateau is dominant, not perfect

**0.7.0 said "the structure is decided on cycle 1" and that every colony
"holds that configuration for 2,999 cycles". The first half is right; the
second was an overstatement, and it is corrected here.**

Regenerating the Tier-1 artifact to produce `docs/discovery.json` meant
checking every published claim against the regenerated file. Measured cycle by
cycle:

| Colony | cycles at 18 beliefs / 7 subjects | of the tail half | last excursion |
|---|---:|---:|---:|
| FULL | 2,964 / 2,999 (98.8%) | 100% | cycle 212 |
| SALIENCE | 2,984 / 2,999 (99.5%) | 100% | cycle 221 |
| NO_CONTRADICTIONS | 2,957 / 2,999 (98.6%) | 100% | cycle 163 |
| **NO_QUESTIONS** | **2,277 / 2,999 (75.9%)** | **95.1%** | **cycle 2,738** |
| NO_DREAMS | 2,984 / 2,999 (99.5%) | 100% | cycle 185 |
| ANTI_EIG | 2,943 / 2,999 (98.1%) | 100% | cycle 539 |

The **retained** belief count is exactly 15 in every one of the 2,999 cycles of
every colony. The **pre-retention pool** is modal, not constant: it dips to 16
beliefs over 6 competing subjects and returns. The excursions are brief — 1–17
cycles in five arms, all over by cycle 539 — and they are real substrate
states, not a recording artifact.

**No launch gate is affected.** G-CS, G-P1, G-SUP and G-EXP hold in 100% of
cycles in all six colonies and G-SUS is 100% in every tail half, re-verified
from the regenerated artifact. G-P1/G-SUP need the pool to *exceed* 15, and 16
does. The verdicts, the noise floor, the inventory totals and the +10,776%
support growth stand as published.

The exception is the interesting part: **`NO_QUESTIONS` is also the arm that
discovers the most** (112 items; 95% of them by cycle 977, 99% by cycle 2,167)
and the only arm still finding new items deep into the run. The five arms
whose structure stops moving are the five that stop discovering; the one arm
that kept discovering kept moving. One arm in one run — a correlation, not a
cause — but it points the same way as H24.

Full record: journal §31, facts sheet §S, `docs/FORCE-MATRIX-RESULTS.md` §2.

### The position this leaves

**No external-validity task tested has produced a win for Organica.** Being
precise about what that means:

- **Held-out prediction** — beaten by both baselines (0.4126 against 0.5040
  and 0.4851).
- **Structure recovery** — beats the temporal-transition-graph baseline in
  the clean and overlapping worlds, **loses to it in the stress world**, and
  loses to plain same-event co-occurrence in all three.
- **Regime-shift detection** — no family met its preregistered success rule;
  the cause-mixture comparison was inconclusive.
- **Post-shift adaptation** — both gates failed in both families, against
  baselines with far lower predictive loss.

That is not the same statement as *the architecture has been shown useless*.
These tasks score next-event prediction, detection delay, structure recovery
and adaptation cost, and none of them is what the eight-layer engine was
designed to win. But it is the honest reading of the evidence so far, and it
is recorded **before** any redesign rather than after one.

### Added — Phase H: external validity (preregistered)

Held-out next-event prediction, F1 on known training tags:

| Model | F1 |
|---|---|
| Organica (Generation-1 prediction candidates) | **0.4126** |
| First-order Markov | **0.5040** |
| Decayed temporal association | **0.4851** |

**Disclosure:** the prediction curriculum is deterministic and identical across
seeds, so Organica's F1 is exactly 0.4126 and the Markov baseline's exactly
0.5040 in all ten seeds. The intervals there are degenerate, and they are
reported as degenerate rather than smoothed into significance.

Structure recovery against hidden cause-pair ground truth, mean F1 over the
ten seeds (range in brackets):

| World | Organica | Same-event co-occurrence | Temporal transition graph |
|---|---|---|---|
| clean | **0.7041** [0.667–0.750] | 0.8000 | 0.1482 |
| overlapping | **0.5469** [0.449–0.628] | 0.7642 | 0.2199 |
| stress | **0.1091** [0.097–0.159] | 0.7959 | 0.2803 |

Organica beats the temporal-graph baseline in the clean and overlapping
worlds and **loses to it in the stress world** — 0.1091 against 0.2803. It
loses to plain same-event co-occurrence in all three. The league is a
three-level stress test, and Organica degrades faster than either baseline
does.

### Added — Phase I: preregistered regime-shift detection

No primary success rule was met in either generator family.

- **cause-mix** — Organica's mean detection delay was **2.55** cycles,
  against **2.80** for the Markov baseline and **4.25** for decayed
  association. The paired advantage for the Markov baseline is 0.25
  cycles, 97.5% CI **[−0.25, 0.75]** — inconclusive. Organica's
  false-alarm rate is **0.0**.
- **mapping-swap** — the baselines are **faster** (Markov **1.25**,
  decayed **1.20**, against Organica **2.65**), and their **15%**
  false-alarm rate breaks the 10% gate while Organica's is **0%**. The
  benchmark is flagged invalid for this family, and the comparison is
  reported with that caveat attached.

### Added — Phase J: gradual post-shift adaptation

Both gates failed in both families.

| Family | Organica adaptation cost | Markov | Decayed |
|---|---|---|---|
| cause-mix | **2.497** | 0.178 | 0.122 |
| mapping-mix | **2.727** | 0.442 | 0.276 |

Final-stable NLL gap: **+4.478** / **+4.500** (cause-mix) and **+3.617** /
**+3.796** (mapping-mix). A clean negative result.

### Added — extended burst horizons, and the scaffold ladder

The burst curriculum was carried to longer horizons:

| Horizon | Baseline inventory | Burst inventory | Bursts delivered | Assimilation efficiency |
|---|---|---|---|---|
| 600 cycles | 91 | **119** | 19 | 1.474 |
| 1,200 cycles | 91 | **128** | 39 | 0.949 |

**Assimilation efficiency decays** — 2.44 → 1.474 → 0.949 items per burst —
so the mechanism's yield falls as the run lengthens even while the
cumulative total still climbs. At 1,200 cycles the burst arm added 8 items
between cycles 601 and 1200 and 2 in its final 100 cycles, reaching 128
against a preregistered 140+ progressive-expansion band. Neither unbounded
expansion nor a stable attractor is established; the reading is recorded as
*intermediate*.

The 300-cycle scaffold ladder, at 91 for the repeating baseline, gives 94 /
93 / 95 for the slow / medium / fast scaffold variants over 24 / 51 / 186
distinct event strings — scaffolding holds the inventory roughly flat
where uniform scaling collapses it.

### Changed

- **The live study is PAUSED** at the owner's direction, after continuous-run
  cycle 1032 (global `sleep_cycle` 5396). The pause marker is in the
  append-only log, the `INTERVAL` override was removed, and there is no
  scheduled restart. The organism did not experience the missing wall-clock
  time, and the write-up says so.
- The package version is **0.8.0**, and this release is the one that
  carries it. Master had drifted past the `v0.7.0` tag while still
  declaring 0.7.0, so the version number was naming a release that master
  was not.

### Fixed

- `tests/test_versioning.py` failed in a **fresh clone**. `clone_check.py`
  clones with `--depth 1`, which fetches only the tags pointing at the
  commit it fetched, so a release tag on an ancestor commit was absent
  locally and the test asserted against an empty tag list. The check now
  consults the remote when the checkout is shallow, and a full checkout
  with no tag still fails exactly as before.
- The version test now also fails when the version describes a commit the
  tag does not cover, which is the drift that let master sit past
  `v0.7.0` while still claiming 0.7.0.
- The local `master` branch had not actually been advanced past the
  overnight merges: a fast-forward had landed on a since-deleted PR branch
  instead, leaving `master` 13 commits behind its remote while the working
  tree still looked current. `master` is fast-forwarded and the three
  orphaned branches are gone.

### Known limitations

- Phase H's **prediction** scores are identical across all ten seeds, because
  the curriculum is deterministic; those intervals carry no information about
  seed variance. The **recovery** task does vary across seeds, and Organica's
  recovery F1 falls to 0.1091 in the stress world, below the temporal-graph
  baseline's 0.2803.
- Phase I and Phase J generalise only to their two predefined synthetic
  generator families, and Phase J's settling time is self-referenced to
  each model's own final stable loss, so it is descriptive, not
  confirmatory.
- Phase I's mapping-swap family has an **invalid benchmark** — the
  baselines' false-alarm rate is above the gate.
- The live study is paused and no restart is scheduled.

---

## [0.7.0] — 2026-10-23

**Ablation Study 2 — the Tier-1 matrix ran, and what it actually measured.**

18,000 colony-cycles: six colonies × 3,000 cycles, on the fixed substrate,
under a protocol whose metrics, gates, noise floor and sensitivity were all
fixed and committed *before* the run. The results are a scientific finding in
their own right and are published in `docs/FORCE-MATRIX-RESULTS.md` and
journal §23.

### The headline

**The structure is decided on cycle 1.** Every colony reaches 18
pre-retention beliefs, 7 competing subjects and 15 retained beliefs on the
first cycle and holds that configuration for 2,999 cycles, while mean support
grows **+10,776%**. All six arms converge to the *same* attractor despite
six different interventions. Structure flat, evidence growing by three orders
of magnitude.

> *Corrected in 0.8.0 — journal §31. "Holds that configuration for 2,999
> cycles" was an overstatement: the retained belief count is exactly 15 in
> every cycle, but the pre-retention pool is modal rather than constant
> (98.1–99.5% of cycles for five arms, 75.9% for `NO_QUESTIONS`). No launch
> gate, verdict, inventory total or noise-floor number changes.*

### The verdicts

**2 SUPPORTED · 3 REVERSED · 0 UNSUPPORTED · 0 NOT INTERPRETABLE**

| # | Prediction | Verdict |
|---|---|---|
| P1 | Retention policy affects development | **SUPPORTED** (M7: 212 vs 2,990 cycles) |
| P2 | Contradiction is developmental fuel | **REVERSED** — removing it *raises* development |
| P3 | Curiosity needs explicit questions | **REVERSED** — removing questions *raises* development |
| P4 | Dreams contribute to trajectory | **SUPPORTED** — removing them lowers it |
| P5 | EIG is orthogonal to development | **REVERSED** — lowest-EIG develops *more* than highest-EIG |

The verdicts are **direction-aware**. A naive "did the metric move?" test
would have scored all five as confirmed.

### A metric that was not a metric

M5 ("development velocity") is `new items ÷ run length`. The reference arm
discovered **74** items over 300 cycles and **74** over 3,000; the rate fell
from 24.667 to 2.467 because the numerator stopped growing. Every colony
discovered **zero** new items in its final 100 cycles. The inventory, broken
down by category, is the interpretable number: FULL 74 (16 beliefs, 11
questions, 36 dreams, 11 experiments) · SALIENCE 78 · NO_CONTRADICTIONS 79 ·
NO_QUESTIONS 112 · NO_DREAMS 44 · ANTI_EIG 85.

### A confound, disclosed

The stimulus **repeats every 9 cycles** — 9 distinct events over 7 distinct
words, seen 333 times. A repertoire cannot grow in a world that does not
change, so the plateau is consistent with *the organism exhausted the
environment*, which is not the same statement as *the organism cannot
develop*. The campaign cannot separate the two.

### The hypothesis this produced

**H24: Organica's apparent developmental plateau is primarily constrained by
environmental information content rather than by architectural inability to
reorganise.** Stated with the evidence on both sides and its falsification
criteria before the experiment that tests it. The next experiment is a
**world-complexity ladder** — a stimulus change, not an architecture change.

### The World-Scale Ladder & Burst Assimilation Findings (2026-10-23)

Immediate experimental testing of H24 during the 0.7.0 cycle revealed three
successive mechanistic insights that redefined the developmental narrative:

1. **Uniform scaling causes dilution collapse**: Multiplying distinct world
   triangles by 16× (3 → 12 → 48) collapsed inventory (91 → 66 → 56) and
   theories (10 → 4) due to frequency dilution in the `MAX_PREDICTIONS = 20`
   window.
2. **Scaffolding prevents collapse**: Maintaining a 3-triangle core scaffold
   prevented multi-layer degradation, preserving theories at 13–14 and
   stabilizing beliefs at 18.
3. **Burst reinforcement enables developmental assimilation**: Novelty requires
   local reinforcement to survive early-stage filters (`PREDICTION_MIN_COUNT = 5`,
   `STABLE_THRESHOLD = 0.3`). Introducing novelty in concentrated bursts
   drove cumulative inventory to **113 items (+24.2%)** across 300 cycles, with
   active discoveries continuing through epochs 2–5 (88, 10, 7, 2, 6, 0).
4. **Conclusion frozen**: *Organica's developmental capacity is not a fixed
   architectural constant. It is strongly dependent on the structure and
   presentation schedule of novelty.* Prior candidate ceilings (74, 91) were
   constrained measurements of environmental bottlenecks rather than hard
   architectural limits.

### Added

- `docs/FORCE-MATRIX-RESULTS.md` — the results, the verdicts, what the
  campaign can and cannot answer, and H24.
- `benchmarks/run_matrix.py` — the campaign launcher. Runs the G1
  verification once, launches the six colonies in parallel with the **same**
  `PYTHONHASHSEED=0`, and records the hash seed, git commit and wall clock
  in the artifact.
- `benchmarks/verdicts.py` — every pre-registered prediction forced into
  SUPPORTED / UNSUPPORTED / REVERSED / NOT INTERPRETABLE, direction-aware.
- `benchmarks/discovery_report.py` — the inventory breakdown and the
  cumulative discovery curves, plus the stimulus's own measured periodicity.
- `benchmarks/process_noise.py` — the process-level noise floor, with a
  parallel sweep and the scale-invariant item-count form.
- `organica/scale_streams.py` — worlds of increasing information content for
  the H24 ladder.
- `benchmarks/scale_ladder.py` — the ladder runner.
- `benchmarks/hub_degree_probe.py` — measures the Layer-1 survival threshold
  against hub degree.
- `docs/force_matrix.json`, `docs/discovery.json`, `docs/verdicts.json`,
  `docs/process_noise_3000.json`, `docs/figure_tier1_matrix.svg`,
  `docs/figure_discovery.svg`.
- Facts sheet §I (matrix results) and §J (H24).
- `docs/ORGANICA-V2-DESIGN-NOTES.md` §7–§10 rewritten with the matrix's
  answers and the new stimulus requirement.

### Changed

- `benchmarks/force_matrix.py` now records the per-cycle **discovery
  history** — new items and cumulative distinct items per category — so the
  inventory can be measured directly rather than inferred from a rate.
- `benchmarks/metric_sensitivity.py` gains the per-metric most-sensitive-
  colony ranking and a **downstream** deviation ranking that excludes each
  colony's own intervention metric.
- `benchmarks/v1_impact.py` excludes `None` metrics rather than zeroing
  them. The harness reports "n/a" for lineage completeness when a condition
  has no lineage; that is *not measurable*, not zero, and zeroing it would
  have been the same class of error as the scope defect the tool documents.
- The README now carries the research findings, the verdicts, and H24.

### Fixed

- `benchmarks/seed_noise.py` overclaimed: it measures the **within-process**
  seed floor (exactly 0.00), not the floor that binds. Disclosed in place.
- `benchmarks/figure_campaign.py` failed with a raw `KeyError` on an
  artifact predating the per-cycle series capture; it now says so.
- `benchmarks/run_matrix.py` and `force_matrix.py` print the G1 header even
  when verification is skipped.
- `organica/scale_streams.py` numbered its leaf tags (`ta0`), and the engine
  only extracts words of **four or more letters** — every leaf was silently
  invisible and the ladder measured nothing. The leaves are now spelled in
  letters.

### Known limitations

- The stimulus's 9-cycle period means the campaign cannot separate
  "exhausted the environment" from "cannot reorganise". H24 is untested.
- M7's spread rests on very few observations: the reference arm's
  212-cycle mean is the mean of **one** belief death. Reported as such.
- `NO_CONTRADICTIONS` removes contradiction's **weight in the confidence
  formula**, not contradictions. M3 is near-invariant for it by
  construction. The colony's name overstates the intervention; disclosed in
  the results document and the facts sheet.

---

## [0.6.0] — 2026-10-23

> **0.6.0 is the first release of this repository to carry a git tag.**
> The versions below were published to this repository without tags, so they
> are recorded here as history but cannot be checked out as named commits.
> The tag convention starts here: releases are tagged `v<version>`, and
> `tests/test_versioning.py` fails the build if the version has no tag.

**Milestone M0.5 — mechanism closure, and a substrate correction.**

This release changes the organism's behaviour. It is a pre-1.0 release
because the public API is not stable, but the behavioural change is
real and is disclosed in full in `research-journal/phase_g_findings_20261021.md`
§21.8 and `docs/USER-MANUAL.md` §8.4.

### Changed — substrate

- **The tag-frequency counter is now scoped to world events.** It was
  maintained over every stored event, including the organism's own sleep
  payloads, while the co-occurrence and temporal graphs it normalises are
  built from world events only. The counter is the *denominator* of the
  Layer-1 edge strength (`ratio = count / source_freq`), so the two sides
  of the ratio measured different populations and the survival filter
  discarded the world's own structure. Measured: 4 surviving edges, 0
  processes, 0 workflows, 0 beliefs.
- A `meta` table records the scope the counters were built with, so a
  database written by an older build rebuilds its counter exactly once
  instead of mixing two populations in one table.

### Added

- `docs/FORCE-MATRIX-PREREGISTRATION.md` — M1–M9 frozen, plus the launch
  gates G-CS, G-P1, G-SUP, G-EXP and G-SUS.
- `docs/ORGANICA-V2-DESIGN-NOTES.md` — planning only: what survived
  scrutiny, what failed, what turned out inert, what turned out essential,
  what became a bottleneck, and the open questions.
- `docs/gate_validation.json`, `docs/mbsd_census.json`,
  `docs/mbsd_census_postfix.json`, `docs/gate_check.json`,
  `docs/freq_scope_probe.json`, `docs/metric_sensitivity.json`,
  `docs/force_matrix_pilot.json`.
- `organica/branch_streams.py` — branch-structured stimuli built from
  triangles, derived from the measured mechanism.
- Benchmarks: `gate_validation.py`, `mbsd_census.py`, `branch_sweep.py`,
  `branch_sweep2.py`, `branch_diag.py`, `branch_diag2.py`,
  `freq_scope_probe.py`, `gate_check.py`, `force_matrix.py`,
  `metric_sensitivity.py`, `seed_noise.py`, `v1_impact.py`,
  `figure_campaign.py`.
- `tests/test_substrate_equivalence.py` — a scope-consistency regression
  test: a sleep payload must change neither the temporal graph nor the
  frequency counter that normalises it.
- `tests/test_versioning.py` — the version declarations must agree, must
  be SemVer 2, must be pre-1.0, and must have a git tag and a changelog
  entry.
- `run_continuous.py` writes `freq_scope=world` in its build marker, so
  the append-only log says which substrate produced which cycles.

### Changed — research findings

- **The proposed Multi-Belief Subject Density gate is structural, not
  predictive.** Layer 5 forms exactly one theory per subject holding ≥ 2
  beliefs; the identity `theories == min(competing_subjects, MAX_THEORIES)`
  holds in 100% of cycles in 9 of the 11 conditions. The gate is restated
  as an absolute count.
- **The `r=4 / r=6 / r=10` "phase transition" was an instrumentation
  artifact.** With the counter scoped correctly, all three repeat counts
  behave identically: a full prediction window, a belief pool of 18, seven
  competing subjects, and 100% of tail cycles passing every gate.
- **"No Falsification freezes the organism" is withdrawn.** Post-fix it is
  the best-supplied condition in the study: 18 beliefs, 6 of 6 subjects
  competing, MBSD 1.000.
- **"The organism is supply-limited, not selection-limited" is withdrawn as
  a general statement.** It was true of the study stream on the old
  substrate; on a branch-structured stimulus the cap binds and the
  retention policy changes the population.
- Facts sheet D8b is **corrected in place**; D8c–D8e are added.

### Fixed

- The G1–G4 perturbation ladder caught a measurement reading the wrong
  report attribute and reporting a working layer as dead (previously
  corrected, recorded here for the release history).
- The campaign runner instantiated the instrument instead of the colony
  subclass, which made every colony run the default service and produced
  a byte-identical FULL and SALIENCE. The runner now asserts G1 — that
  each colony's intervention is in the code path — before running a
  colony.

### Known limitations

- The ablation study in `docs/ablation_study.json` was produced on the
  **pre-fix** substrate. Every condition ran on the same substrate, so
  the comparisons stand, but the absolute densities are not comparable to
  post-fix numbers. `benchmarks/v1_impact.py` produces the before/after
  audit (`docs/v1_impact.json`).
- One seed per colony. Deltas smaller than the measured seed-noise floor
  are reported as *not interpretable*. The floor is measured by
  `benchmarks/seed_noise.py`.

---

## 0.5.0 — 2026-10-21

- Phase G endurance work: monotonic sleep-cycle counter in the database,
  bounded candidate retention, the tag-frequency counter moved from a
  full-table scan to an incremental counter.
- `docs/USER-MANUAL.md` rewritten with 18 sections.
- `docs/FACTS-SHEET.md` — facts with provenance, separated from assumptions.
- `docs/GATE-BOARD.md` — what is demonstrated versus assumed.
- `benchmarks/clone_check.py` and a passing fresh-clone check.

## 0.4.0 — 2026-10-20

- Observation pipeline repaired; `MemoryService.batch()` added after
  profiling found one fsync per candidate dominated the cycle
  (1,023 commits = 3.0 s of a 4.5 s cycle).
- `benchmarks/cold_start.py` — the eight assistance levels.

## 0.3.0 — 2026-10-20

- The eight-layer engine, the four reproduction domains, the reproduction
  pack and the growth benchmarks.

## 0.2.0 — 2026-10-19

- The study daemon, the append-only log format, and the snapshot writers.

## 0.1.0 — 2026-10-19

- First public release of the substrate and the sleep pipeline.

[0.10.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.10.0
[0.9.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.9.0
[0.8.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.8.0
[0.7.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.7.0
[0.6.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.6.0
