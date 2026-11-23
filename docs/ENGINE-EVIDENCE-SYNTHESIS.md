# What the engine's evidence base says — by build (2026-11-19)

> **What this document is.** A reading of every judged block the project has run,
> organised by the build it ran on, and stated as what it does and does not say
> about **the engine that ships today**. It is not a campaign, not a
> preregistration, and not a re-score. Every measurement it mentions is quoted
> by the page it links; this page states no measurement of its own.
>
> The question is not *"what have we measured?"* — the dashboards answer that.
> It is *"what do we actually know about the current engine, and what does that
> license?"*

**Status: SYNTHESIS. No new experiment. No architecture change. No V2 design.**

---

## 1. The answer in one paragraph

The evidence base is large and **mostly build-bound**. The six negative task
families, the Tier-1 mechanism verdicts and Phase L were all measured before
the 0.10 rebuild — Phase K and Phase L on the frozen `0.9.0` tag, Phase H, I
and J earlier still — and the engine has taken **22 commits** since that tag. The
`0.15.0` corpus — the current engine — is almost entirely about **pipeline
mechanics**: whether the world's edges are present, selected, served, asserted
and carried. Until 2026-11-19 it contained exactly **one** attempt at an
external task family, the K2 block, and that attempt is `VOID`. That gap is now
closed for three families: the frozen Phase K protocol was re-run on `0.15.0`
and all three families are `REVERSED` again, with intervals wholly below zero
(§3.4). So the honest answer to *"what do we know about this engine?"* is: **we
know how its pipeline moves edges, and on the only three task families measured
on it, it loses to a simple baseline by a wide margin.** The through-line across
every build is that levers reliably move **coverage** and have never been shown
to move **behaviour**. Development should stop buying pipeline diagnostics: the
long-missing behavioural measurement now exists, and it confirms the loss.

---

## 2. The build spine

Build attribution below is what the artifacts themselves record. Several blocks
— the density A2 block and the rank-ordering block among them — record **no
engine version**; the density block's claim is marked `unreproducible` in the
claim ledger for exactly that reason. That is a property of the record, not a
detail to skip.

### 2.1 Every judged block

A **judged block** is one run whose protocol fixed a decision rule and whose
record returns a verdict. Instrument audits (K0, endpoint ceilings),
calibrations, pre-run design gates and post-hoc diagnostics are not blocks, and
the question dashboard indexes those. `unrecorded` means the artifact carries
no engine version; the checker verifies that absence rather than inferring a
build. Where a block's record is a results page rather than a machine verdict
field, the quoted sentence is checked and the label in the Verdict column is
this synthesis's classification of that sentence.

<!-- BEGIN JUDGED BLOCKS: generated from docs/engine_evidence_inventory.json by benchmarks/engine_evidence_inventory.py; do not edit by hand -->
| Block | Build | Verdict | Record |
|---|---|---|---|
| Phase H — next-event prediction | unrecorded | `LOSS` | [V1-SYNTHESIS.md](V1-SYNTHESIS.md) |
| Phase I — regime-shift detection | unrecorded | `NO FAMILY MET THE RULE` | [V1-SYNTHESIS.md](V1-SYNTHESIS.md) |
| Phase J — post-shift adaptation | unrecorded | `NO GATE PASSED` | [V1-SYNTHESIS.md](V1-SYNTHESIS.md) |
| Phase K — K1 incremental world modeling | 0.9.0 | `REVERSED` | [phase_k_results.json](phase_k_results.json) |
| Phase K — K2 belief revision | 0.9.0 | `REVERSED` | [phase_k_results.json](phase_k_results.json) |
| Phase K — K3 longitudinal integration | 0.9.0 | `REVERSED` | [phase_k_results.json](phase_k_results.json) |
| Phase L — plasticity–coherence | 0.9.0 | `INCONCLUSIVE` | [phase_l_results.json](phase_l_results.json) |
| K2 one-block intervention | 0.15.0 | `VOID` | [phase_k_k2_results.json](phase_k_k2_results.json) |
| T1 persistence-off (first block) | 0.15.0 | `VOID` | [t1_persistence_off_run.json](t1_persistence_off_run.json) |
| T1b persistence-off (replication) | 0.15.0 | `PERSISTENCE CONTRIBUTES` | [t1b_persistence_off_run.json](t1b_persistence_off_run.json) |
| Presence cap ladder at 40 | 0.14.0 | `CAP LIMITING` | [presence_cap_run.json](presence_cap_run.json) |
| Presence cap-112 block | 0.15.0 | `CAP LIMITING` | [presence_cap_1_112_run.json](presence_cap_1_112_run.json) |
| Presence comparator at 112 | 0.15.0 | `PRESENCE NOT ASSERTION` | [presence_comparator_112_run.json](presence_comparator_112_run.json) |
| Presence construct audit at 40 | 0.14.0 | `CONSTRUCT VALID` | [presence_construct_audit_run.json](presence_construct_audit_run.json) |
| Presence conversion repair | 0.14.0 | `CONVERSION STAGE MEASURED` | [presence_conversion_repair_run.json](presence_conversion_repair_run.json) |
| Presence conversion observer | 0.14.0 | `OBSERVER NOT NEUTRAL` | [presence_conversion_observer_run.json](presence_conversion_observer_run.json) |
| Presence allocation band, first block | 0.15.0 | `VOID` | [presence_band_rank_run.json](presence_band_rank_run.json) |
| Presence allocation band, fresh-world confirmation | 0.15.0 | `CONFIRMED` | [presence_band_rank_5_run.json](presence_band_rank_5_run.json) |
| Density interaction A2 | unrecorded | `EXCLUSION PAYS AT SPARSE DENSITY AND GROWS WITH DENSITY` | [density_interaction_a2_result.json](density_interaction_a2_result.json) |
| Rank-ordering block | unrecorded | `ORDERING SUPPORTED` | [rank_ordering_result.json](rank_ordering_result.json) |
| Diversity-first admission, two-arm | unrecorded | `NO GAIN ON THIS LAYER` | [admission_two_arm_result.json](admission_two_arm_result.json) |
| Q006 admission re-derivation | 0.13.0 | `NO GAIN ON THIS LAYER` | [q006_admission_rederivation.json](q006_admission_rederivation.json) |
| Q021 transfer re-derivation | 0.13.0 | `NO_TRANSFER_ADVANTAGE` | [q021_transfer_rederivation.json](q021_transfer_rederivation.json) |
| Q053 competition mechanism | 0.13.0 | `MECHANISM DID NOT OPERATE` | [q053_mechanism_run.json](q053_mechanism_run.json) |
| Temporal-decay falsifier | 0.13.0 | `VOID_REFERENCE_DEAD` | [decay_falsifier.json](decay_falsifier.json) |
| Decay-fix confirmation | unrecorded | `NOT CONFIRMED` | [decay_fix_confirm.json](decay_fix_confirm.json) |
| D3 persistence seed block | 0.13.0 | `PERSISTENCE REPAIRED` | [d3_persistence_seed_varying_run.json](d3_persistence_seed_varying_run.json) |
| D3 persistence recalibrated G1 | 0.14.0 | `PERSISTENCE REPAIRED` | [d3_persistence_g1_recalibrated_run.json](d3_persistence_g1_recalibrated_run.json) |
| D3 persistence engine replication | 0.14.0 | `VOID` | [d3_persistence_engine_replication_run.json](d3_persistence_engine_replication_run.json) |
| Gate 13 loop-free block 6 | unrecorded | `VOID / NOT COMPARABLE` | [gate13_loop_free_block6.json](gate13_loop_free_block6.json) |
| Gate 13 loop-free block 7 | unrecorded | `INTERVENTION SUPPORTED` | [gate13_loop_free_block7.json](gate13_loop_free_block7.json) |
| Gate 13 ratio block 2 | unrecorded | `TREATMENT NOT REPRODUCED` | [gate13_ratio_block2.json](gate13_ratio_block2.json) |
| A1 two-path assembly | 0.15.0 | `VOID` | [a1_two_path_result.json](a1_two_path_result.json) |
| Retention incremental confirmatory | 0.15.0 | `VOID` | [retention_incremental.json](retention_incremental.json) |
| Retention formation-anchored confirmatory | 0.15.0 | `CONFIRMED, TEMPORALLY AMBIGUOUS` | [retention_formation_anchored.json](retention_formation_anchored.json) |
| Core-band admission | 0.15.0 | `VOID` | [core_band_admission.json](core_band_admission.json) |
| Q051 long-delay capability confirmation | unrecorded | `INCONCLUSIVE` | [long_delay_capability_confirm.json](long_delay_capability_confirm.json) |
<!-- END JUDGED BLOCKS -->

| Build | What ran on it | Status for the current engine |
|---|---|---|
| **`0.9.0`** — frozen 2026-10-24, the archival reference | Phase H, I and J (earlier on the line); the Phase K campaign (K1/K2/K3); Phase L; the ablation study; the Tier-1 force matrix | **historical** — evidence about Organica 1 on the `0.9.x` line, not about the engine that ships |
| **`0.10.0`–`0.12.x`** | formation/utilization; candidate-membership audit; the decay collapse and its rerun plan | **historical** — superseded by later engine changes |
| **`0.13.0`** | Q052/Q053 competition work; the decay repair chain; the audit-trace probes; the Q006 and Q021 re-derivations | **historical**, with the decay findings carried forward only where re-measured |
| **`0.14.0`** — pinned 2026-11-10 | presence at cap 40; construct audit; conversion observer; the cap ladder | **partly superseded** — the cap moved to 112 in `0.15.0` |
| **`0.15.0`** — pinned 2026-11-11, current | presence/comparator at 112; cap-112 ladder (`CAP LIMITING`); T1/T1b persistence; retention, carrier and assertion models; source-diversified ranking; A1 (`VOID`); the K2 block (`VOID`); V2 calibration | **current**, but contains **no external-task result**; the cap-112 construct record is frozen and unrun |

The change map records **22** commits under `organica/` between `v0.9.0` and
HEAD and asks, for each, which recorded failure it could move. Its own audit
finding is the reason this page exists: **no recorded failure was measured on
the engine at HEAD.**

---

## 3. What each corpus established

### 3.1 `0.9.x` — the archival record (frozen at `0.9.0`)

This is the corpus the project quotes most, and it is coherent:

- **Development is real.** Structure forms from the event stream with no
  pretrained weights; the lineage ladder is grounded end to end.
- **Curriculum matters enormously.** Changing the stimulus moved the inventory
  through a chain of falsified ceilings (74 → 91 → 113 → 119 → 128), and the
  1,200-cycle arm still landed below its preregistered band.
- **The internal motivational machinery is not what drives development.** Of
  the five Tier-1 predictions, retention and dreams were supported, while
  contradiction, question generation and EIG were **reversed** — removing them
  *raised* development rather than lowering it.
- **Six task families are negative.** Next-event prediction, latent-structure
  recovery, regime-shift detection, post-shift adaptation, and K1/K2/K3 were
  all losses against baselines given the tuning advantage. The Phase K
  intervals are wholly below zero and survive every robustness check.
- **Phase L was inconclusive, and its characterization is a step function.**
  Structural displacement is real and its transition is reproducible; the
  protocol's criteria were not met, and the verdict was not re-scored.
- **Structure → behaviour was never demonstrated.** Phase L measured
  displacement, not behaviour; the capacity-1,000 confirmatory test found no
  held-out prediction gain, with an interval crossing zero.

**Status: historical.** These are the strongest results the project has, and
they are evidence about the `0.9.x` line. Quoting them as properties of the
current engine is the single easiest overstatement available in this
repository.

### 3.2 `0.10`–`0.14` — the rebuild

The engine moved, and the evidence changed character. The work in this period
is about **which edges reach the served path**:

- presence is not assertion — the world's edges are in memory and are not
  served;
- the construct audit is valid, so the presence instrument measures what it
  says;
- the cap is limiting — raising it raises admission and assertion;
- the conversion stage is measured rather than assumed;
- a diversity-first admission rule **failed** on the engine's own layer and was
  withdrawn;
- the decay layer produced a step-function survival boundary, and the
  competition mechanism tested at `0.13.0` **did not operate**;
- cross-context transfer produced **no advantage** when re-derived on the
  engine's own ordering.

**Status: mostly historical.** The cap-112 work was re-measured on `0.15.0`;
the rest describes earlier builds.

### 3.3 `0.15.0` — the current engine

This is the corpus that matters for a development decision, and it is narrow:

- at cap 112 the cap is still limiting (`CAP LIMITING`);
- presence is still not assertion at 112 — but the cap-112 **construct** record
  is `FROZEN, NOT RUN`, so construct validity at 112 is inherited from the
  `0.14.0` audit rather than re-measured;
- the allocation-law band is confirmed on fresh worlds (BAND-5) — a fresh-world
  confirmation of the allocation law, **not** an adjudication of
  `DECISION-ADMISSION-STEP`'s mechanism question: BAND-5's seeds and measured
  band are not the 62 named Q4 edges, so it neither re-scores that decision nor
  satisfies its specific condition;
- persistence **contributes** at 112 (T1b), after T1 returned `VOID` on its own
  gate;
- the source-diversified ranking returns **no reliable recovery gain**;
- the A1 two-path assembly is `VOID` on `C4_no_interference`;
- the K2 block is `VOID` on `G4_no_pre_boundary_demotions`;
- V2's calibration shows the readout can express a planted composite gain,
  which is a property of the instrument and not of the cell.

**Status: current, and no longer without a behavioural measurement.** Every
result above is about the pipeline or about an instrument; §3.4 is the one
behavioural exception, and it confirms the losses rather than reversing them.

**The one raw observation worth recording, and its limit.** The K2 block's raw
scores sit below the `0.9.0` campaign's on both K1 and K2 (the block records
them; the comparison is not a criterion, and rule 31 forbids citing the block
as evidence). Separately, the K1 comparator's registered pre-value does **not**
reproduce on HEAD — a direct rerun gives the same selections under the shipped
and no-op paths, so the drift is the engine. That second fact *is* admissible,
and it says the engine's behaviour changed between builds. It does not say in
which direction on any task.

### 3.4 The `0.15.0` replication — the missing behavioural measurement

The frozen Phase K protocol ran on this build on **2026-11-19**, with the same
families, the same ten seeds (`20261023`–`20261032`), the same grid and the same
98.33% decision intervals. All three families are `REVERSED` again:

| Family | Organica | Best simple baseline | Paired diff | 98.33% interval |
|---|---|---|---|---|
| K1 incremental world modeling | 0.312011 | 0.935972 | -0.623961 | [-0.646675, -0.599907] |
| K2 belief revision | 0.176471 | 0.984615 | -0.808144 | [-0.823529, -0.785068] |
| K3 longitudinal integration | 0.235788 | 0.857808 | -0.622021 | [-0.630928, -0.611828] |

No sign changed: K1 and K2 widened their gaps and K3 narrowed a structural zero
to 0.2358, still 0.62 behind its baseline; every interval is wholly below zero.
No family was confirmed, so the protocol's terminal outcome repeats — no larger-n
campaign, no V2 designed from these families. The matched no-questions ablation
is a no-op on K1 and K2 (`mechanism_implicated: false`), as on `0.9.0`.

The K1 gap is `-0.623961`, the exact live comparator value the K2 block recorded
when its registered `-0.343658` failed to reproduce. That independently
cross-checks the block's build-drift finding from a clean, complete campaign; it
does **not** rescue the block, which remains `VOID` and is not evidence. Both
pins held: the engine is `0.15.0` with the pinned file-map digest
`d4eeefcfabe6`, and the harness blob is identical before and after. Full
provenance: [`phase_k_results_0.15.0.provenance.json`](phase_k_results_0.15.0.provenance.json);
result page: [`PHASE-K-REPLICATION-0.15.0-RESULT.md`](PHASE-K-REPLICATION-0.15.0-RESULT.md).

---

## 4. The through-line: coverage is not behaviour

Read across builds, the corpus has one consistent shape.

**What the project can do:** locate, measure and move the pipeline. It can show
where the world's edges are lost (candidate availability, ranking, allocation,
admission, assertion, persistence) and which knobs recover them (cap 112,
intra-cell exclusion, ordering). Those are real, replicated, pre-registered
results.

**What it has never done:** connect a pipeline gain to a behavioural gain. The
one pre-registered bridge, Phase L, measured structural displacement and came
back inconclusive. The capacity confirmatory test found no held-out prediction
gain. The formation→utilization work found **no single upstream selection
stage** to blame. The six external families lost — on `0.9.0`.

**The consequence is structural, not rhetorical.** Every diagnostic the project
is currently equipped to run measures the pipeline. Another one cannot close
the behaviour gap, because the gap is not in the pipeline measurement; it is in
the absence of a behavioural endpoint attached to it. Rule 30 already says a
diagnostic needs two different decisions for its two outcomes. The corpus adds
the missing premise: for pipeline diagnostics, the positive outcome and the
negative outcome both currently lead to *another pipeline diagnostic*.

---

## 5. What this licenses for development

| # | Decision | What the corpus says | Recommendation | Cost / dependency |
|---|---|---|---|---|
| D1 | **Stop adding pipeline diagnostics without a behavioural endpoint.** No new presence, ranking or allocation probe whose two outcomes both lead back to the pipeline. | Every pipeline lever measured so far moved coverage; none was connected to behaviour; the bottleneck map already labels the behaviour half *not established*. | **Yes.** This is the rule-30 test applied to the whole corpus, not just to K2. | an owner rule; no run |
| D2 | **Make the six negative families current-engine evidence.** Re-run the frozen Phase K protocol on `0.15.0` as a **new, build-labelled replication** — new artifact path, never overwriting `docs/phase_k_results.json`. | The negatives are `0.9.0`; the engine has taken 22 commits; the audit says no recorded failure was measured at HEAD; the K1 comparator already fails to reproduce, so the build demonstrably changed behaviour. | **Done (2026-11-19) — all three families `REVERSED` again.** It was the cheapest decision-relevant measurement available: roughly the
original campaign's wall clock at twelve workers, with no engine change and no
new grant mechanism. Confirmation makes the map current (§3.4); reversal would have made that family the lead. | owner authorisation + a build-labelled provenance note; `--out` to a new path. The run must pin **both** the engine (`0.15.0`, `docs/engine_pin.json`, the stamped tree SHA-256) and the harness (`benchmarks/phase_k_campaign.py` blob before and after, recorded in the sidecar); a moved pin is `VOID` for replication. Satisfied: both pins are recorded in `docs/phase_k_results_0.15.0.provenance.json` |
| D3 | **Run the signed V2 first cell as the development path.** | It was the only behavioural measurement of a new build in the queue; it is a different program from Organica 1, not a seventh K family. | **Ran 2026-11-19 — `REVERSAL`.** Maintained membership cost **0.004199** nats against pair counts (99% interval [0.003617, 0.004890]); the charter fails at its first experiment, and no build, feature, promotion or second run is authorised. | done; one report (`V2-FIRST-CELL-REPORT.md`), block spent |
| D4 | **Do not design V2 from the pipeline record.** | `DECISION-V2-SCOPE` D1 still binds: H2 stands, and a pipeline diagnosis is not a V2 mandate. The V2 charter is a design, not a capability result. | **Yes.** The corpus gives no mechanism warrant for a redesign, only a measurement gap. | no run |

**Why D2 ranks above another K2 repair.** A repaired K2 block would produce a
mechanism reading on a family that lost by a large margin on `0.9.0`, and the
registration's best case still leaves that family far behind its baseline. The
Phase K replication answers a question that covers all three families and the
whole negative map, on the build that ships, for about the same compute.

---

## 6. What would change this reading

This page is falsifiable by four measurements, and nothing else:

1. **A `0.15.0` Phase K replication that confirms the losses.** — **Ran
   2026-11-19: confirmed** (§3.4). The negative map is now current-engine
   evidence for these three families, and the development question moves to V2.
2. **A `0.15.0` replication that reverses a family.** — **Not observed:** no
   family reversed. If it had, that family would be the lead — the first
   positive external result in the project.
3. **A behavioural bridge showing a pipeline gain translates.** Then the
   pipeline work was justified after all, and D1 should be narrowed rather than
   kept.
4. **A V2 first-cell PASS.** — **Not observed: the cell returned `REVERSAL`**
   (2026-11-19). A pass would have meant a new primitive earns prediction
   beyond counts; that is a different program's evidence, not Organica 1's.

None of the four is a diagnostic the project has already run.

---

## 7. What this page does not claim

- It does not claim the `0.9.0` results are wrong. They are correct about that
  build, and they remain the project's strongest measurements.
- It does not claim the `0.15.0` replication settles more than K1/K2/K3 on the
  frozen ten seeds. It is not a seed generalisation, and it neither rescues the
  `VOID` K2 block nor adjudicates the band/admission question.
- It does not claim the current engine is worse. The K2 block is `VOID`; the
  raw scores are recorded, not adjudicated.
- It does not claim the pipeline work was wasted. It produced the only
  replicated, pre-registered results the project has on the current build.
- It does not claim V2 is justified. It says the next development decision
  needs a behavioural measurement, and names the two that exist.
- It does not re-score Phase K, Phase L, A1 or K2. Their verdicts stand.

---

## 8. Sources

- Build and change coverage: [`ENGINE-CHANGE-FAILURE-MAP.md`](ENGINE-CHANGE-FAILURE-MAP.md),
  [`ENGINE-CHANGE-AUDIT.md`](ENGINE-CHANGE-AUDIT.md), [`engine_pin.json`](engine_pin.json).
- `0.9.0` measurement record: [`V1-SYNTHESIS.md`](V1-SYNTHESIS.md),
  [`phase_k_results.md`](phase_k_results.md), [`FORCE-MATRIX-RESULTS.md`](FORCE-MATRIX-RESULTS.md),
  [`PHASE-L-SYNTHESIS.md`](PHASE-L-SYNTHESIS.md).
- Question outcomes and scope: [`RESEARCH-FINDINGS.md`](RESEARCH-FINDINGS.md),
  [`RESEARCH-DASHBOARD.md`](RESEARCH-DASHBOARD.md), [`RESEARCH-QUESTION-REGISTRY.md`](RESEARCH-QUESTION-REGISTRY.md).
- Candidate explanations and the constraint ledger: [`BOTTLENECK-MAP.md`](BOTTLENECK-MAP.md).
- Current-build blocks: [`PRESENCE-CAP-1-112-RESULT.md`](PRESENCE-CAP-1-112-RESULT.md),
  [`T1B-PERSISTENCE-OFF-RESULT.md`](T1B-PERSISTENCE-OFF-RESULT.md),
  [`A1-RUN.md`](A1-RUN.md), [`K2-BLOCK-RESULT.md`](K2-BLOCK-RESULT.md),
  [`V2-FIRST-CELL-BRIEF.md`](V2-FIRST-CELL-BRIEF.md).
- The K-series reading: [`PHASE-K-SERIES-SYNTHESIS.md`](PHASE-K-SERIES-SYNTHESIS.md).
