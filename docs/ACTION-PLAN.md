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
| D1 / D2 | Implemented; the campaign is gated on the persistence pre-flight | `docs/tier1_preflight.json` |
| Q053 mechanism | Ran; `MECHANISM DID NOT OPERATE` (M1 0.00 against 0.25); capability unread; closed | `docs/Q053-MECHANISM-RESULT.md` |
| Q021 transfer | Ran; `NO_TRANSFER_ADVANTAGE` (TR 1.0, 0/10 paired seeds); v1 3.2 not re-derived | `docs/Q021-TRANSFER-RE-DERIVATION-RESULTS.md` |
| Q006 admission | Ran; `NO GAIN ON THIS LAYER` (coverage gain -0.069197, 0/8 seeds positive); historical answer survives; Q006 closed | `docs/Q006-ADMISSION-RE-DERIVATION-RESULT.md` |
| Half A triage | 11 re-runnable, Q017 decision-only; 0 needs-harness, 0 prose-only | `docs/RERUN-CAMPAIGN-PLAN.md` §3 |
| D3 persistence | Frozen 24-cell block run; `PERSISTENCE REPAIRED` on one deterministic trajectory (all six seeds identical, effective n = 1); adoption pending | `docs/d3_persistence_run.json` |
| Pruning | Reachability and by-type attribution recorded; `PRUNING_PARTIAL` | `docs/pruning_by_type.json` |
| Question survival | Mechanical pass generated; semantic dispositions remain | `docs/question_survival.json` |

**Q002 needs no review.** It closed on 2026-11-09 and C003 was promoted; it is no longer a
dependency, and keeping it in the queue would re-open a settled question.

## 2. The active blocker — persistence

The campaign is blocked for one measured reason, not three:

- The witness is alive: the reference arm forms a theory in **39 of 40 cycles**, peak 6, and both
  negative controls record zero across the trace.
- The campaign stimulus dies: `L1_hub1_t3_disjoint` records its **first zero at cycle 39** against
  the campaign's **3000-cycle horizon**.
- The pre-flight therefore returns `CAMPAIGN_NOT_MEASURABLE`, and the horizon is not shortened.

The causal chain is now: live witness -> campaign stimulus -> persistence collapse -> D3 block.
The frozen block ran and returned **`PERSISTENCE REPAIRED`**: the control's first zero is cycle 60
on every seed, the treatment has no first zero through 3000, and the early-recall median gap is
0.0 against the -0.01 bar. But **all six seeds are byte-identical**, so this is one deterministic
trajectory repeated, effective n = 1. The pass is a real single-world result; it does not clear
D2's gate for the campaign. A seed-varying confirmation is required before adoption. The engine
is unchanged; the treatment is an in-process subclass.

## 3. Half A — the actual runnable set

`docs/RERUN-CAMPAIGN-PLAN.md` §3 now triages the **12 re-derivations**. The inherited slogan
was "14 reruns"; Q006 and Q021 have closed and the measured set is 12. **12 of 12 name a preregistration**;
11 also have a JSON comparator and an existing harness module, and Q017 is a decision-only
protocol with no cell. Q006's result is `docs/Q006-ADMISSION-RE-DERIVATION-RESULT.md`; Q021's is
`docs/Q021-TRANSFER-RE-DERIVATION-RESULTS.md`; Q017's protocol is
`docs/Q017-ADMISSION-DECISION-PREREGISTRATION.md`.

**Runnable means the three pieces exist.** Q006 and Q021 have run and closed; the eleven runnable rows
below have not run on 0.13.0. The endpoint modules are present, not all proved live.

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

**The comparator gap remains the real risk.** Only 4 of 53 cited JSON artifacts name any build,
and all four name 0.13.0. The old number's build is carried by prose, which is why Half A's
protocol names the comparator explicitly and reuses the endpoint rather than rewriting it.

Q006 and Q021 have run and closed on this engine. Q017 is read after Q024; it is not a cell.

## 4. The reviewed population, and the one correction

- Reviewed: **30 open + 5 future = 35**.
- **15 carry an answer** whose own `why_open` says it predates a later build.
- **2 are governance-held**: Q004 and Q005 cite the PENDING `DECISION-DENSITY-EXCLUSION`.
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

The two halves are measured separately: **112 of 112** world edges are present in raw temporal
memory on all six seeds at 0.13.0, while asserted coverage is **0.2500-0.3214** at cap 40.
Presence is not assertion, and C003's scope says so.

This is a re-reading before it is a campaign. The existing per-seed artifacts are asked: what
makes a stored relation asserted; what prevents assertion; how long presence survives without
it; what predicts it across seeds. No engine change is authorised. If the re-reading names a
lever, it gets its own preregistration.

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
- No D3 promotion before a seed-varying confirmation and a recorded owner decision; promotion would need an engine re-pin.

## 9. Execution queue

1. **Resolve D3's seed axis.** The 24-cell block has run and passed its frozen criteria, but all
   six seeds are identical. A seed-varying confirmation is the next measurement; do not launch
   Tier-1 on the degenerate block and do not promote the arm on it.
2. **Run Half A in the order above.** Q024 first (Q006 is closed), then Q004/Q005, the decay cluster,
   Q044, Q043, Q051. Q017 is read after Q024 and Q006's closing result; it is not a cell.
3. **Finish the semantic question dispositions.**
4. **Re-read presence against assertion.**
5. **Run the survivor analysis.**
6. **Role abstraction** after the items above; it stays blocked behind Q012.

## 10. What would change this plan

- A D3 pass at the horizon clears D2's gate only when the seed axis varies; this block's pass does not, because all six seeds are identical.
- A seed-varying D3 confirmation would turn the single-world pass into a campaign-clearing result; a failure would keep the campaign blocked and move the question to the denominator-versus-numerator split.
- A Half A result that reverses a recorded answer would move that question's follow-up up.
- An assertion predictor in the existing artifacts would replace the re-reading with a targeted
  experiment.
- A survivor feature that predicts persistence would replace the D3 guess with a targeted change.

Until one of those happens, the order is the D3 block, then Half A, then the question review,
then presence/assertion, then persistence, then role abstraction.
