# Cross-context reuse, second run — pre-registration

**Date**: 2026-11-07
**Status**: COMMITTED BEFORE ANY CELL. No cell of this protocol has run.
**Campaign**: cross-context reuse, second run (RoleCandidate and SchemaCandidate)
**Licence**: `docs/ccre_question_licensing.json` (Q012 answer, Q022 move, Q028 answer, Q025-Q027 record)
**Supersedes**: nothing. The first run's protocol and its results stay as they were.

This document fixes the comparators, the thresholds, the controls and the decision
rule **before the first cell**, so that the run can fail. Nothing here is computed
from the run it governs (AGENTS rule 19), and no criterion may be re-read after the
results are in (rule 14).

---

## 1. What the record already says

- **The first run** (`docs/CROSS-CONTEXT-REUSE-PREREGISTRATION.md`, artifact
  `docs/cross_context_reuse_benchmark.json`) reported `REUSE_DEMONSTRATED`. That
  verdict is **withdrawn**: its advantage came from a boost that raised a
  one-transition edge past `PREDICTION_MIN_COUNT` (decision D1), and its schema
  identity was not content-bearing (D3), so Context A and the orthogonal control
  produced the same schema.
- **The earned-evidence run** (`docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md`) re-ran
  the design on unboosted evidence at 5 seeds and 40/40 cycles: treatment **3.6**,
  naive **3.4**, pruned **3.4**, orthogonal **3.4** cycles to acquisition, transfer
  ratios **0.944 / 1.0 / 1.0**. Verdict
  `STRUCTURAL_PRIOR_PRESENT_NO_ACQUISITION_ADVANTAGE`. The prior is applied and is
  not inert; it buys no latency.
- **Two defects the earned run named in itself** matter here. The acquisition
  endpoint **saturates** (v1 acquired at cycle 1, the minimum attainable), so an
  endpoint that only counts latency cannot register a rank effect; and the prior
  **reorders candidates**, which the latency endpoint ignores. The target edge's
  rank at acquisition was 7, 5, 4, 20, 7 in treatment.
- **Q028's trace exists and currently resolves nothing**: 14 transfer events, 0
  resolved, all `unresolved_no_role`, and 0 of 14 prior ids shared with Context A
  (`docs/transfer_provenance.json`). That measurement is on the first run's seed and
  is **not** the denominator of this run.

## 2. Questions this run may answer, and only these

| id | tier | what a result may claim |
|---|---|---|
| Q012 | answers | role abstraction removes the orthogonal-context dependence, within this engine and world family |
| Q022 | moves | whether reuse is role-specific or schema-existence-specific; **not** a cross-domain claim |
| Q028 | answers | whether each transfer event resolves to a role satisfaction, with its events and priming |
| Q025-Q027 | records | persistence, survival under selection, the priming-versus-role fraction; no claim made from them |

A refusal in the licensing record stays refused. This protocol adds no question.

## 3. Design

**Arms** (five, all in-process subclasses; the engine is never edited):

| arm | Context A | Context B | what it isolates |
|---|---|---|---|
| `treatment` | structured A | B | the design's intervention |
| `naive` | none | B | acquisition without any prior |
| `pruned` | A, target schema excised | B | the schema's causal contribution |
| `orthogonal` | flat/random C | B | whether any prior helps, not this one |
| `shuffled` | A, prior relabelled to a different relation | B | whether the prior's **content** is doing the work |

**Worlds**: both contexts use the benchmark's own generators (`VOCAB_A`, `VOCAB_B`,
`VOCAB_C`, `generate_world_events`) with disjoint surface vocabularies, so no Tag
from A can appear in B (rule 9: every Tag has at least four letters).

**Budget**: 40 cycles in Context A and 40 in Context B per cell, the earned run's
own cadence. **Cells**: 5 arms x 12 seeds = **60 cells**, **4,800 colony-cycles**.

**Seeds**: **20272001-20272024** (24 integers). The first **12** are confirmatory
(20272001, 20272002, 20272003, 20272004, 20272005, 20272006, 20272007, 20272008, 20272009, 20272010, 20272011, 20272012); the remaining **12** are reserve (20272013, 20272014, 20272015, 20272016, 20272017, 20272018, 20272019, 20272020, 20272021, 20272022, 20272023, 20272024) and are **never drawn**.
Substitution is prohibited: a cell that fails a control is dropped and reported, and
the analysis reports the n it actually had. The block is disjoint from every seed
recorded in `docs/` at the time of writing, checked mechanically against the same
scan Stage B uses (1829 seeds).

## 4. Comparators, fixed with their grids

Every simple comparator is swept over a **declared grid** and its **best** score is
the number used; a handicapped baseline is not evidence (rule 11).

- **CT1 `naive`** — the design's own baseline: no Context A at all.
- **CT2 `pruned`** — Context A minus the target schema.
- **CT3 `orthogonal`** — a Context C prior of the same volume, flat transitions.
- **CT4 `shuffled`** — Context A's prior with its relation relabelled; same count,
  same application rate, wrong content. **This is the attribution control.**
- **CT5 the strongest simple learner, not an arm**: a **decayed bigram counter over
  Context B's own events**, predicting the same target relation. Grid: decay in
  1.00, 0.99, 0.95 crossed with minimum count in 1, 3, 5; its cycles-to-threshold at
  each setting, and the **best** setting is reported. It learns what this world
  rewards (a first-order Markov law), so it is the comparator that can make the task
  trivial.

## 5. Endpoints and pre-committed thresholds

- **E1 Transfer ratio.** `TR = cycles_to_acquire(naive) / cycles_to_acquire(arm)`,
  measured under the earned-evidence contract: a prediction counts only when its own
  `temporal_count` clears `PREDICTION_MIN_COUNT`; no prior may admit one.
- **E2 Rank at acquisition.** The rank of the target edge among admissible
  candidates in the cycle it is acquired. The earned run showed the prior reorders
  and the latency endpoint is blind to it; this endpoint exists because that run
  said so, and it is fixed here before any new cell.
- **E3 Trace resolution.** Q028's share: transfer events resolved to a role match,
  with the events behind it and the prior that licensed it, over the denominator of
  transfer events, with every unresolved reason counted
  (`benchmarks/transfer_provenance.py`).

**Criteria, all four judged together (rule 14):**

- **P1**: median `TR(treatment)` **at least 1.25**, with the 95 % bootstrap lower
  bound **above 1.00**.
- **P2**: `TR(treatment)` exceeds **both** `TR(orthogonal)` and `TR(shuffled)` by at
  least **0.10**, with lower bounds above zero. A prior that helps because it is a
  prior cannot clear this.
- **P3**: median rank at acquisition in `treatment` is **at least 2 positions lower**
  than in `naive`, with the 95 % interval excluding zero.
- **P4 (trace, rule 18)**: **at least 0.90** of transfer events resolve, **and** no
  transfer is left unresolved without a named reason. **If P4 fails, the protocol
  fails and no transfer claim is licensed, even if P1-P3 pass.**

**Void conditions, fixed now:** if more than **20 %** of cells in any arm acquire at
cycle 1 (the endpoint saturates, as v1 did), the run is `NOT COMPARABLE`; if CT5's
best setting acquires the target at or before the median of every arm, the endpoint
cannot separate structure from counting and the run is `NOT COMPARABLE`.

## 6. Controls that can fail, fixed before the first cell

- **C1 arm distinctness.** The perturbation ladder is run before the campaign and
  must show the five arms differ on their outputs; identical arms void the run.
- **C2 reference-arm liveness, fail-closed.** The campaign's own reference check
  exits non-zero on a dead arm (`benchmarks/force_matrix.py`). A campaign that
  reports success with an empty comparison arm is void.
- **C3 attribution.** `shuffled` must fail to reproduce the treatment advantage. If
  it reproduces it, the verdict is `NOT_ATTRIBUTABLE`, not a pass.
- **C4 the trace instrument's own control.** `python -m benchmarks.transfer_provenance
  --self-test` must pass, and must reject a tracer that always answers `resolved`.
  An instrument that cannot fail licenses nothing.
- **C5 the denominator.** Every arm must have a non-zero count of cells reaching
  acquisition; a cell that never acquires is censored and reported, not scored as
  zero (rule 13b).
- **C6 provenance.** `PYTHONHASHSEED=0` in every process, the engine pin re-recorded
  at the run's commit, and the seed block checked against the Stage B scan.
- **C7 the Q028 known zero.** The trace currently resolves 0 of 14 transfers because
  the engine records no role per prediction. That is a precondition, not a result:
  **this run may not start until the trace's role leg resolves on the build being
  used**, and adding a store-time role record is an engine change that needs its own
  recorded decision.

## 7. Decision rule

Evaluated once, by one analysis run, on the 60 cells.

| outcome | conditions | decision it enables |
|---|---|---|
| `TRANSFER_ATTRIBUTABLE` | P1, P2, P3, P4 all pass | role abstraction is the lever; Q022 becomes live and a third run may test the domain clause |
| `PRIOR_REORDERS_WITHOUT_LATENCY` | P2 and P3 pass, P1 fails | the prior's effect is on ranking, so the next build is a readout pathway, not another prior |
| `NOT_ATTRIBUTABLE` | C3 fires, or P2 fails while P1 passes | the advantage is not the relation's content; stop priming work on this engine |
| `PROTOCOL_FAILED` | P4 fails, or a void condition fires | no transfer claim is licensed; the trace becomes the next build, not the run |

The number of criteria satisfied is **not** a score. A run that meets three of four
is a failed protocol with a diagnosis, and the diagnosis is recorded, not promoted.

## 8. Falsifiers

- `shuffled` matching `treatment` falsifies content-sensitive priming.
- `orthogonal` matching `treatment` falsifies role abstraction as the lever (Q012).
- A rank advantage with no latency advantage falsifies the latency endpoint, not the
  prior; that is the `PRIOR_REORDERS_WITHOUT_LATENCY` row.
- A trace share below 0.90 falsifies **attributability**, and does not touch the
  behavioural result, which then cannot be called transfer.

## 9. Preconditions, stop condition, and what may not change

**Preconditions.** (a) C7: the trace's role leg resolves on the build being used.
(b) The engine's reference arm passes its own check (`force_matrix --verify-only`
exits 0) - it does not on 0.13.0, where the decay rule is unfixed, so the campaign is
blocked today. (c) The engine pin is re-recorded at the run's commit.

**Stop condition.** The build is: one analysis script that reads the cells and emits
the four criteria and the verdict bucket, plus the trace wired to the Q028 endpoint.
No feature may be added afterwards; defects may be fixed.

**What may not change after this commit.** The thresholds (1.25, 0.10, 2 positions,
0.90), the grids, the seed block, the arm set, the void conditions and the decision
table. Any change is an amendment, appended and dated, with the reason and what it
would have changed.

## 10. What this run cannot say

- **n = 12 per arm, one world family, 40/40 cycles.** It separates a live prior from
  a dead one and a rank effect from none; it is not an estimate of effect size.
- **Q022 moves, never answers.** The licence asks about transfer across domains; this
  campaign varies context inside one family.
- **No retention claim beyond TP >= 20 cycles**, and none about the superseded-reader
  defect the earned run disclosed.
- **No claim about why a transfer happened** unless P4 passes; that is the whole
  point of making the trace a criterion rather than a diagnostic.

---

## Seed allocation

| use | seeds |
|---|---|
| confirmatory (12) | 20272001, 20272002, 20272003, 20272004, 20272005, 20272006, 20272007, 20272008, 20272009, 20272010, 20272011, 20272012 |
| reserve, never drawn (12) | 20272013, 20272014, 20272015, 20272016, 20272017, 20272018, 20272019, 20272020, 20272021, 20272022, 20272023, 20272024 |

Disjointness is mechanical: the block was chosen against every seed recorded under
`docs/` at commit time, and C6 re-checks it.
