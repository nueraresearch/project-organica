# Action plan — the reality-based execution queue

**Status: planning document.** It runs nothing and freezes nothing. Every figure below is read
from the artifact named beside it, and `tests/test_action_plan.py` fails when this page and those
artifacts disagree. The queue lists only work that is still undone; completed work is recorded so
it is not re-decided.

## 1. Completed — do not re-open

| Item | State | Record |
| --- | --- | --- |
| Q002 / C003 | Q002 closed `SUPPORTED`; C003 `SUPPORTED` inside its presence scope | `docs/question_survival.json`, `docs/CLAIM-LEDGER.md` |
| G1 witness | Re-based on `L3_hub1_t3_mixed`; failure condition unchanged | `docs/DECISION-G1-WITNESS.md` |
| D1 / D2 | Implemented; the promoted build's pre-flight returns `PASSES`; Tier-1 campaign ran on 0.14.0 | `docs/tier1_preflight.json`, `docs/force_matrix_0.14.0.json` |
| Q053 mechanism | Ran; `MECHANISM DID NOT OPERATE` (M1 0.00 against 0.25); capability unread; closed | `docs/Q053-MECHANISM-RESULT.md` |
| Q021 transfer | Ran; `NO_TRANSFER_ADVANTAGE` (TR 1.0, 0/10 paired seeds); v1 3.2 not re-derived | `docs/Q021-TRANSFER-RE-DERIVATION-RESULTS.md` |
| Q006 admission | Ran; `NO GAIN ON THIS LAYER` (coverage gain -0.069197, 0/8 seeds positive); historical answer survives; Q006 closed | `docs/Q006-ADMISSION-RE-DERIVATION-RESULT.md` |
| Half A triage | 11 re-runnable, Q017 decision-only; 0 needs-harness, 0 prose-only | `docs/RERUN-CAMPAIGN-PLAN.md` §3 |
| D3 persistence | Promoted into the engine at 0.14.0 under the dated owner decision; D2 pre-flight `PASSES` on the promoted build | `docs/tier1_preflight.json`, `docs/DECISION-G1-WITNESS.md` |
| Tier-1 0.14.0 | Ran; six colonies × 3,000 cycles; stamped 0.14.0; prediction buckets not re-scored | `docs/force_matrix_0.14.0.json`, `docs/FORCE-MATRIX-0.14.0-RESULTS.md` |
| D3 engine replication | Ran on 0.14.0; `VOID` at G1 (control first zero 58–61 against the 60-cycle bound); treatment alive 6/6; no persistence claim | `docs/D3-PERSISTENCE-ENGINE-REPLICATION-RESULT.md`, `docs/d3_persistence_engine_replication_run.json` |
| Pruning | Reachability and by-type attribution recorded; `PRUNING_PARTIAL` | `docs/pruning_by_type.json` |
| Question survival | Mechanical pass generated; semantic dispositions remain | `docs/question_survival.json` |

**Q002 needs no review.** It closed on 2026-11-09 and C003 was promoted; it is no longer a
dependency, and keeping it in the queue would re-open a settled question.

## 2. The persistence blocker is cleared

The campaign's pre-flight now returns **`PASSES`** on the promoted engine:

- The witness is alive: the reference arm forms a theory in **39 of 40 cycles**, peak 6, and both
  negative controls record zero across the trace.
- The campaign stimulus stays alive: `L1_hub1_t3_disjoint` has **no first zero** through the
  campaign's **3000-cycle horizon**, peak 6.
- D3's matched-frequency persistence repair is promoted into the engine at **0.14.0** under the
  dated owner decision; the seed-varying confirmation had six distinct treatment trajectories and
  effective n = 6.
- The prior single-world `D3-PERSISTENCE-1` result remains caveated; the engine change is recorded,
  re-pinned, and the pre-flight is the promoted build's own run.

The campaign has now run on 0.14.0. Its six colonies completed 3,000 cycles each; the
engine-stamped artifact is `docs/force_matrix_0.14.0.json`, and the raw result is recorded in
`docs/FORCE-MATRIX-0.14.0-RESULTS.md`. The historical five prediction buckets were not
re-scored against a noise floor measured on an earlier engine.

## 3. Half A — the actual runnable set

`docs/RERUN-CAMPAIGN-PLAN.md` §3 now triages the **12 re-derivations**. The inherited slogan
was "14 reruns"; Q006 and Q021 have closed and the measured set is 12. **12 of 12 name a preregistration**;
11 also have a JSON comparator and an existing harness module, and Q017 is a decision-only
protocol with no cell. Q006's result is `docs/Q006-ADMISSION-RE-DERIVATION-RESULT.md`; Q021's is
`docs/Q021-TRANSFER-RE-DERIVATION-RESULTS.md`; Q017's protocol is
`docs/Q017-ADMISSION-DECISION-PREREGISTRATION.md`.

**Runnable means the three pieces exist.** Q006 and Q021 have run and closed; the eleven runnable rows
below have not run on the promoted engine. The endpoint modules are present, not all proved live.

| ID | Question | Endpoint / harness | Comparator | Status |
| --- | --- | --- | --- | --- |
| **Q024** | Does diversity-first admission improve the real engine? | `run_ranking_admission.py`, `score_ranking_admission.py` | `admission_two_arm_result.json` | Runnable |
| **Q004** | Does excluding intra-cell rows buy precision at a fixed cap? | `run_density_interaction.py`, `score_density_interaction_a2.py` | `density_interaction_a2_result.json` | Runnable |
| **Q005** | Does the partial final pass explain the ladder's non-monotonicity? | `density_padding.py` | `density_padding_result.json` | Runnable |
| **Q029** | Why do the 35-edge degree-12 structures disappear? | `decay_attribution.py` | `decay_attribution.json` | Runnable |
| **Q030** | Is temporal edge decay the removal mechanism? | `decay_attribution.py` | `decay_attribution.json` | Runnable |
| **Q031** | When does the fall begin and how long does it take? | `decay_attribution.py` | `decay_attribution.json` | Runnable |
| **Q032** | Do theories die before the edges? | `decay_attribution.py` | `decay_attribution.json` | Runnable |
| **Q036** | What is the peak structure's half-life? | `decay_attribution.py` | `decay_attribution.json` | Runnable |
| **Q044** | Is a missed re-emission an admission loss or a slot loss? | `decay_admission_slot.py` | `decay_admission_slot.json` | Runnable |
| **Q043** | Does the engine need a store-time role record? | `store_time_role_durability.py` | `store_time_role_durability.json` | Runnable |
| **Q051** | Does 0.9925 rank late better than 0.95 without an early cost? | `long_delay_capability_confirm.py` | `long_delay_capability_confirm.json` | Runnable |
| **Q017** | Should further admission variants be tried? | decision-only; no cell | Q006/Q024 results | Decision-only |

**Execution order:** Q024, Q004, Q005, Q029, Q030, Q031, Q032, Q036, Q044, Q043, Q051.
Admission and density first because they share a comparator and carry the acquisition-bound and
Gate 13 traps; decay follows in causal order; Q044 extends it; Q043 is independent; Q051 is last
because its endpoint rests on Q024 and Q044.

**The comparator gap remains the real risk.** Only 9 of 60 cited JSON artifacts name any build,
and all named artifacts name 0.13.0, 0.14.0 or 0.15.0. The old number's build is carried by prose, which is why Half A's
protocol names the comparator explicitly and reuses the endpoint rather than rewriting it.

Q006 and Q021 have run and closed on 0.13.0; their records are historical. Q017 is read after Q024; it is not a cell.

## 4. The reviewed population, and the one correction

- Reviewed: **31 open + 5 future = 36**.
- **14 carry an answer** whose own `why_open` says it predates a later build.
- **4 are governance-held**: Q003 cites the PENDING `DECISION-CAP-LEVEL`, and Q004 and Q005 cite the PENDING `DECISION-DENSITY-EXCLUSION`.
- **5 are prerequisite-gated**: the future questions behind Q012.
- **13 are open with evidence** and no answer.
- **0 are answered at the pin.**

The semantic dispositions — `OBSOLETE`, `WORLD_MISMATCH`, `UNREPRODUCIBLE` — still need a read
per question. The derived states do not license those labels. The C003 correction is the model:
the defect was a measurement attached to the wrong object.

## 5. Question generation is not a separate program

The row "0 questions, 8 dreams, 5 experiments, 0 theories" is a dead arm at cycle 40, not a
question-generation defect. Questions stop in the same cycles theories do, because both need two
competing hypotheses for a subject. On `L3` the arm has 4 questions and 4 theories at cycle 40;
on `L1` it has 5 questions through cycle 36 and is dead by 40.

The only surviving version is a **falsifier**: on a live arm, a cycle with theories above zero and
questions at zero would be a real defect. It has not fired. No question-generation program is
queued.

## 6. Presence vs assertion — after D3

The 0.13.0 record measured the two halves separately: **112 of 112** world edges present in raw
temporal memory on all six seeds, while asserted coverage was **0.2500-0.3214** at cap 40.
Presence is not assertion, and C003's scope says so.

**Same-build audit on 0.14.0 (2026-11-10).** Re-running the same six seeds on the current build,
with the shipped 40-slot Layer-1 prediction cap, returns **112 of 112 present** on every seed and
**34-47 of 112 asserted** (**0.3036-0.4196**); the final asserted structure holds **100-132**
edges across all six structure types. Verdict `PRESENCE NOT ASSERTION`. The 40-slot cap is the
prediction-admission budget, not a bound on the final asserted structure. The result is a
construct separation, not a defect; no engine file changed.

This is a re-reading before it is a campaign. The existing per-seed artifacts are asked: what
makes a stored relation asserted; what prevents assertion; how long presence survives without
it; what predicts it across seeds. No further engine change is authorised by this re-reading. If
the re-reading names a lever, it gets its own preregistration.

**Where the loss happens (2026-11-10, exploratory).** The ladder trace asks the next question
directly: for each of the 112 world edges, which of four readings did it reach — present in raw
temporal memory, offered by the ranked Layer-1 candidate list, admitted to the shipped 40-row
window, asserted in the final structure? **No edge is lost before the ranking:** all 112 are
offered on all six seeds once the cap is removed. **68-84** are ever admitted to the 40-row
window, and the **423** present-but-unasserted edges split **171** offered-and-never-admitted
(0.4043) against **252** admitted-and-still-not-asserted (0.5957). Under the rule declared
before the run — a bucket needs a 0.60 pooled share and a majority of seeds — the label is
`MIXED`, and the dominance bar was not moved after the run. The window was full on 72-112 of the
120 cycles, world edges were only 0.2393-0.2782 of admitted rows, and the uncapped list held
225-238 candidates per cycle, so admission is a real constraint and not the whole story; Admission frequency does not separate the two fates either: the admitted-but-unasserted edges held a median of 5-9 window slots against 3-13.5 for the asserted ones, so repetition is not sufficient for assertion. 3-9
asserted edges per seed arrived with no prediction-window admission at all. This is a
description, not a lever: it licenses no engine change and scores no criterion.
`docs/presence_assertion_ladder_0.14.0.json`.

**The cap-only test is preregistered and authorised (2026-11-10).** `PRESENCE-CAP-1` freezes Q2 of the conversion draft as its own block: four cap levels (40, 80, 112, uncapped), six fresh seeds, 24 cells, the cap as the only variable, and `S_cycle` read from the report the engine already returns. The bar is derived from the audit (10 edges, twice its between-seed spread) and the ceiling from the ladder (28.5 never-admitted edges per seed). Every outcome maps to a decision, including `ADMISSION-ONLY BOTTLENECK` and `CAP NOT LIMITING`. It was **authorised and run on 2026-11-10**, and the verdict is **`CAP LIMITING`**: the mean paired gain at cap 112 is 15.83 world edges against the 10-edge bar, the 95% paired lower bound is 8.08, six of six seeds move in the predicted direction, and the gain is 0.56 of the reach-limited ceiling. The result is `docs/PRESENCE-CAP-RESULT.md`; it licenses an owner decision on the cap and no engine change by itself.

A draft of that protocol is [`docs/PRESENCE-ASSERTION-CONVERSION-PREREGISTRATION.md`](PRESENCE-ASSERTION-CONVERSION-PREREGISTRATION.md). It is **DRAFT — not frozen as one program and not run**, though each of its three questions now has its own frozen record, and all three have run: `PRESENCE-CONSTRUCT-1` (Q1), `PRESENCE-CAP-1` (Q2) and `PRESENCE-CONVERSION-1` (Q3). It separates construct, cap-sweep and full-conversion questions; tracks `W -> P -> C -> E -> R -> S -> A -> U` where observable; names the Layer-1 prediction cap as the one manipulated variable; and requires positive and negative witnesses before any defect claim.

## 7. Survivor persistence — after D3

Pruning is measured: **105 peak edges**, of which **96 end in a pruned terminal** and 9 are
withdrawn without pruning, with 0 alive; **2,478 prediction candidates** retired. All four
pruning gates pass; the label is `PRUNING_PARTIAL`.

The complement is the next question: why does anything survive? The per-cycle ledgers already
exist in `docs/pruning_by_type.json` and `docs/decay_attribution.json`, so this is a re-reading,
not a new campaign. The deliverable is survivor-focused: longest-lived edges and candidate
classes, and the features that separate survivors from losses.

## 8. What not to do

- No new memory system, ranking rewrite, temporal rewrite or architecture change.
- No Q053 retry without a new preregistration aimed at the prior-decay path.
- No re-scoring a criterion, no shortening the campaign horizon, no pooling `burst_L1`.
- No more attribution or ledger work unless a measurement changes.
- No further D3 promotion without a new recorded owner decision; the 2026-11-10 promotion is already recorded and re-pinned.

## 9. Execution queue

1. **Tier-1 has run on the promoted engine and its result is recorded.** The seed-varying
   24-cell confirmation passed on six distinct trajectories (`PERSISTENCE REPAIRED`, effective
   n = 6), D2's pre-flight returns `PASSES`, and the six-colony campaign completed 3,000 cycles
   each on 0.14.0. The raw artifact is `docs/force_matrix_0.14.0.json`; the historical prediction
   buckets were not re-scored.
2. **Run Half A in the order above.** Q024 first (Q006 is closed), then Q004/Q005, the decay cluster,
   Q044, Q043, Q051. Q017 is read after Q024 and Q006's closing result; it is not a cell.
3. **Finish the semantic question dispositions.**
4. **Presence vs assertion has been re-read on 0.14.0.** The same-build audit returns 112/112 present and 34-47/112 asserted at the 40-slot Layer-1 cap; the verdict is `PRESENCE NOT ASSERTION`, a construct separation rather than a defect. The ladder trace then places the loss: every world edge is offered by the ranking, 68-84 are ever admitted, and the misses split 171 at admission against 252 after it (`MIXED` under a rule declared before the run). Any lever still needs its own preregistration, and the cap-only half is preregistered and authorised as `PRESENCE-CAP-1`.
5. **Run the survivor analysis.**
6. **Role abstraction** after the items above; it stays blocked behind Q012.

7. **The engine-effect standard is now an owner decision (2026-11-10).** `DECISION-ENGINE-EFFECT-STANDARD` fixes what an engine-effect claim must rest on: one changed variable measured in process first, a control on the same build the claim names, a reproduction on the shipped build, a live seed axis, and a VOID rule for any block that fails its own gate. The rationale is that an in-process subclass is not the shipped engine, and a chain that spans builds must say so rather than name one of them. The D3 chain is the worked example, including its `VOID` replication arm. `docs/DECISION-ENGINE-EFFECT-STANDARD.md`, `docs/DECISIONS.md`, `AGENTS.md` rule 31.
8. **The Q3 conversion observer is preregistered (2026-11-10).** `PRESENCE-CONVERSION-1` freezes a benchmark-only observer that records candidate construction (`C`), the eligibility reason for each present edge (`E`) and each candidate's rank (`R`), paired with an observer-off control on the same seeds: identical presence, ordered admission windows, admitted union, final assertion and asserted world edges are the admissibility gate, and a divergence is `OBSERVER NOT NEUTRAL`, not a result. It names no mechanism and edits no engine file. It ran on 2026-11-10 and returned **`OBSERVER NOT NEUTRAL`** — the observer-on arm differed from the observer-off arm on every seed — so its stage table is not a conversion target until the instrument is fixed and a new block is registered. `docs/PRESENCE-CONVERSION-OBSERVER-PREREGISTRATION.md`, `AGENTS.md` rule 17(c).

9. **The Q3 conversion observer is frozen, has an authorisation request and now has its runner (2026-11-10).** `docs/AUTHORISATION-PRESENCE-CONVERSION-1.md` asks the owner to authorise the block's thirteen reading runs - twelve design cells (two arms x six fresh seeds) plus the observer-off witness cell - and the `X7` determinism control rerun, at 120 cycles each on the pinned 0.14.0 engine. It names the exact question, the four outcomes and what each licenses. The path is built: `authorisation_problems()` accepts a `granted: true` amendment only when a dated document exists and carries the record's quote verbatim, and `--measure`, `--cell` and `--finish` all refuse while `granted` is false; `--measure` writes one stamped part per cell, `--finish` assembles the artifact and result page, and `--check` recomputes the verdict from them. The owner authorised all three blocks on 2026-11-10 (`Authorize all runs`) and all three ran that day; Q3's verdict is `OBSERVER NOT NEUTRAL`, so this block settled its instrument and no conversion question. `PRESENCE-CAP-1` has its own authorisation record. `docs/PRESENCE-CONVERSION-OBSERVER-PREREGISTRATION.md`, `docs/presence_conversion_observer_prereg.json`.

10. **Q1's construct audit is frozen (2026-11-10).** `PRESENCE-CONSTRUCT-1` fixes the program's construct stage: the audit's own six seeds, the shipped 0.14.0 build and cap, 120 cycles, and gates `C1`–`C9`, with `C9` requiring every cell to reproduce its published audit row and `C8` naming the first seed as the determinism control. It adds no observer and no cap level, discloses that the seed block is reused rather than fresh, and carries the recorded grant; the runner is built (`--measure`, `--cell`, `--finish`, `--check`) and ran under that grant on 2026-11-10: **`CONSTRUCT VALID`**, nine of nine gates, every cell reproducing its published audit row. `docs/PRESENCE-CONSTRUCT-AUDIT-PREREGISTRATION.md`, `docs/presence_construct_audit_prereg.json`. All three questions now have frozen records, and all three are authorised as of 2026-11-10 (`Authorize all runs`). Q1's authorisation record is `docs/AUTHORISATION-PRESENCE-CONSTRUCT-1.md`.

## 10. What would change this plan

- The seed-varying D3 confirmation passed on six distinct worlds, the repair is promoted at 0.14.0, and D2's pre-flight passed; the six-colony campaign has now run and its raw result is recorded, but its historical prediction buckets were not re-scored.
- A later D2 or campaign failure would move the question to the denominator-versus-numerator split; it would not re-open the historical single-world result.
- A Half A result that reverses a recorded answer would move that question's follow-up up.
- An assertion predictor in the existing artifacts would replace the re-reading with a targeted
  experiment.
- A survivor feature that predicts persistence would replace the D3 guess with a targeted change.

With D3 promoted and the campaign unblocked, the order is Half A, then the question review,
then presence/assertion, then persistence, then role abstraction.
