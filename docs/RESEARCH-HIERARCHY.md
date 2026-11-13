# Research hierarchy — selection, persistence and assertion

**Status:** durable synthesis, **not a result**. Last updated 2026-11-13.

**Authority.** The cited artifacts and `docs/RESEARCH-FINDINGS.md` are authoritative. If this page disagrees with either, the artifact or registry wins. This page exists so the current reading does not depend on chat history, a context window or memory.

**Scope.** Never-served world edges in the compositional world family, at 120 cycles and the recorded caps. It covers construction, admission, service, loop formation, loop persistence and final assertion. It does **not** cover capability, transfer, belief revision, a general engine property or human-like cognition. A block that is `VOID` or `FROZEN, NOT RUN` is not evidence, and a `POST-HOC` block is not confirmatory.

**Claim statuses.** This page uses the project's four statuses: **supported within the tested scope**, **mixed / context-limited**, **reversed**, and **not established / not measured**. `VOID`, `POST-HOC` and `FROZEN, NOT RUN` are block states, not synonyms for a scientific status.

## 1. One-paragraph reading

The evidence now supports a layered selection account, not a frequency account. Candidate structures are abundant. Persistence acts first at **candidate formation**: when carried support never reaches the floor, no candidate exists and the downstream stages never see the edge. Separately, the **26 asserted-but-never-served edges** are construction-present, above the floor, and excluded at ranking and allocation, so they are an **admission** failure rather than a formation failure. Admission is entropy-first, while the assertion models do not show a rank effect among never-served edges; service ranking and assertion are therefore partially decoupled. Loop formation is strongly enriched among asserted never-served edges, but it is necessary-not-sufficient in the blocks that measured it. The newest, post-hoc result is that **retention survives count, rank, strength and first-formation timing**, and that the raw count association reverses once persistence is measured. That makes count a poor independent signal, but it does not establish the causal chain, the dominance of strength, or a mechanism.

## 2. The hierarchy

### Tier 1 — supported within the tested scope

1. **Persistence affects eligibility at candidate formation.**
   T1b's persistence-off arm reduced served and asserted world edges: shipped `S_ever` values **101, 95, 100, 103, 98, 99** against persistence-off **0, 1, 0, 3, 0, 3**, mean paired difference **98.167**, 95% interval **[96, 100]**, all seven gates passing. On the five zero cells, within-cycle counts stay at **1-4**, never reach the floor of **5**, and no world-edge candidate is formed. This localizes the failure before ranking or assertion; it does not identify the cause of the short support. See `docs/t1b_persistence_off_run.json`, `docs/T1B-PERSISTENCE-OFF-RESULT.md`, `docs/persistence_zero_served_diagnostic.json` and `docs/PERSISTENCE-ZERO-SERVED-NOTE.md`.

2. **The 26 asserted-but-never-served edges are construction-present and rank/allocation-excluded.**
   On the original Q4 block, all **26** are transitions. Their best recorded rank spans **22-127**: **0** in ranks 1-20, **10** in 21-40, **10** in 41-80, **4** in 81-112 and **2** at 113 or worse. **10** sit inside the cap, but **0** sat inside the transitions actually served in the cycle that ranked them, and the closest in-cap miss was **2** ranks short. The direct temporal count is **23-47**, far above the prediction floor of **5**. This is a location, not a cause. See `docs/never_served_assertion_model.json`, `docs/NEVER-SERVED-ASSERTION-MODEL-RESULT.md`, `docs/assertion_provenance.json`, `docs/ASSERTION-PROVENANCE.md`, `docs/assertion_carrier_trace.json` and `docs/ASSERTION-CARRIER-TRACE.md`.

3. **Admission is entropy-first, and no variance-share figure is established.**
   The shipped transition order is schema tier, then entropy ascending, then transition probability, then temporal count, then source and target. The engine stores the entropy under the name `target_entropy`, but computes it from `source_entropy[tag_from]`, the entropy of the source's outgoing target distribution; this page calls it entropy-first rather than target entropy. The order is established. A claim that entropy explains a specific share of rank variance is **not established here**: no cited artifact carries that decomposition, so no percentage is used. See `organica/sleep_extraction.py`, `docs/SCHEMA-PRIORITY-GATE.md` and `docs/LANDING-0.15.0.md`.

4. **Loop formation is strongly enriched among asserted never-served edges.**
   On the original Q4 block, **26/26** cases ever formed a reported loop against **13/26** matched controls, a **+50.0 pp** difference (seed-cluster 95% CI **[34.5, 69.6] pp**, risk ratio **2.00**, exact McNemar **p = 2.40e-04**). On the clean fresh block, **29/29** cases formed a loop against **11/29** controls: **+62.1 pp**, CI **[38.5, 85.2]**, risk ratio **2.64**, exact McNemar **p = 7.63e-06**. The original +50 pp lies inside the fresh interval, so the direction and rough magnitude replicate; this does not establish an exact twofold law. See `docs/matched_carrier_replication_2.json` and `docs/MATCHED-CARRIER-REPLICATION-2.md`.

5. **The raw count association is not robust to loop persistence.**
   In the confirmed loop-only model, count OR is **2.69** (**1.77-4.07**) with rank OR **1.19** (**0.82-1.72**). Adding retention and strength moves count to **0.61** (**0.29-1.27**), a sign reversal and a **150.1%** change in the log-odds coefficient. Adding formation timing moves count to **0.71** (**0.33-1.53**). The supported statement is conditional: **count is not an independent positive signal once retention and strength are measured.** It is not established that count is downstream, or that the reversal is mediation rather than suppression, confounding or collinearity. See `docs/loop_only_assertion_model.json`, `docs/LOOP-ONLY-ASSERTION-MODEL.md`, `docs/loop_persistence_assertion_model.json` and `docs/LOOP-PERSISTENCE-ASSERTION-MODEL.md`.

### Tier 2 — strongly suggested, post hoc

6. **Retention adds information beyond formation, count, rank and strength.**
   In `POSTHOC-LOOP-PERSISTENCE-1`, retention OR is **8.02** per SD (**2.57-25.02**) and strength OR **2031.58** per SD (**38.71-106621.84**; about **2.08** per raw strength unit). Adding first-formation timing moves retention to **14.68** (**3.68-58.64**, p **1.43e-04**), not toward 1. Controlled formation OR is **6.25** (**1.17-33.54**); controlled count OR is **0.71** (**0.33-1.53**); leave-one-seed-out keeps controlled retention at **2.12-4.62** and controlled formation at **1.11-3.69**. This is still one observational sample on reused seeds. A rising point estimate under conditioning is not evidence of a stronger effect, and the interval is wide.

7. **Strength nearly separates the outcome.**
   The lowest strength quartile is **0/44** asserted; the highest is **44/45**. The quartile ranges are **5-10**, **11-20**, **20-26** and **26-51**. This is a real descriptive separation in this sample, not a precise effect: near-separation inflates the Firth coefficient and its interval, and the uppermost quartile is almost a constant outcome. See `docs/LOOP-PERSISTENCE-ASSERTION-MODEL.md`.

8. **Timing and retention are not the same variable in this sample.**
   Asserted loops form later on average (**cycle 47.0** versus **37.0**), persist longer in raw span (**53.6** versus **15.8** cycles) and have higher retention (**0.667** versus **0.198**). They are also stronger (**28.4** versus **13.4**) and higher-count (**35.1** versus **27.0**). The controlled model says formation timing does not explain retention away; it does not say timing is irrelevant, and it does not isolate a pure timing effect.

### Tier 3 — hypotheses, not findings

9. **Strength may be the dominant carrier variable.** The near-separation and the count reversal are compatible with strength and retention being two readouts of one latent loop quality. The data do not distinguish that from strength as an independent cause.
10. **The causal ordering may be count -> strength -> retention -> assertion.** This is one compatible ordering. Reverse causation, a common cause, and a collider are not excluded.
11. **Loops may function like replay, or the graph may function like a cognitive map or successor representation.** These are analogies that generate tests. They are not measured here. An SR test must build the score from an early window and predict a held-out later assertion; a final-graph score would leak the outcome.

## 3. Block ledger

| Block | Seeds and design | Population and result | Status | Artifact |
| --- | --- | --- | --- | --- |
| `T1b-PERSISTENCE-OFF-1` | Twelve cells plus rerun, shipped versus persistence-off | Mean paired difference **98.167**, 95% interval **[96, 100]**; five zero cells localized to candidate formation | Supported within scope; not a mechanism | `docs/t1b_persistence_off_run.json` |
| `NEVER-SERVED-ASSERTION-MODEL-1` | Six Q4 seeds, 120 cycles, cap 40 | **180** never-served, **179** complete, **26** asserted; loop **26/35**, no-loop **0/118** | Fit; observational, quasi-separated | `docs/never_served_assertion_model.json` |
| `ASSERTION-CARRIER-TRACE-1` | Same six Q4 seeds, behaviour-neutral replay | **26/26** loop carriers; **61** loop occurrences, **58** 3-cycles and **3** 2-cycles; counts **23-47**; first formation **37-117**, median **78.5** | Provenance classification; not a mechanism | `docs/assertion_carrier_trace.json` |
| `NEVER-SERVED-ASSERTION-MODEL-REPLICATION-1` | Six fresh seeds `20613101-20613106`, 120 cycles, cap 40 | **212** never-served, **26** asserted; loop **26/62**, no-loop **0/124**; min rank **22-116**; counts **21-49** | `REPLICATED`; same-family observational; not a new independent draw from Q4 | `docs/never_served_assertion_model_replication.json` |
| `MATCHED-CARRIER-REPLICATION-2` | Six fresh seeds `20615201-20615206`, 1:1 count match | **29/29** cases loop versus **11/29** controls; **+62.1 pp**, CI **[38.5, 85.2]**, RR **2.64**, McNemar **7.63e-06** | `REPLICATED`; not a retention or causal claim | `docs/matched_carrier_replication_2.json` |
| `CONFIRMATORY-LOOP-ONLY-ASSERTION-1` | Twelve fresh seeds `20616101-20616112`, 120 cycles, cap 40 | **177** loop-forming never-served edges, **77** asserted; count OR **2.69**, rank OR **1.19**, AUC **0.801** | `CONFIRMED` for the count association; subgroup only | `docs/loop_only_assertion_model.json` |
| `POSTHOC-LOOP-PERSISTENCE-1` | Same twelve seeds, replay of the 177 loop edges | Count OR **0.61** after retention and strength; retention **8.02**, strength **2031.58**; formation control retention **14.68**, formation **6.25** | `POST-HOC`; no confirmatory verdict | `docs/loop_persistence_assertion_model.json` |
| `POST-HOC-SCHEMA-PRIORITY-GATE-1` | Six consumed schema-prime seeds, cached ranking features | **111,275** rows, **1,816** schema rows, **701** cycles, **13,604** seats; gate 10 gives **1,400** schema seats, **1,039** priority, **0** weak priority, **0** strong lost | Candidate ordering only; no engine cell | `docs/schema_priority_gate.json` |
| `POST-HOC-STORED-FIELD-TIEBREAK-1` | Same cached ranking features | **0** seats, windows or edge-seed pairs changed; **12** windows reorder **37** positions; **120/701** cutoff ties, all equal stored strength | Candidate ordering only; no engine cell | `docs/stored_field_tiebreak.json` |
| `POST-HOC-SOURCE-DIVERSIFIED-TOP20-1` | Six-seed replication cache | Uncapped **18/26**; cap 3 **19/26**, displacing **8** non-asserted seats and adding **1** asserted; gain confined to seed `20613101` **0/1 -> 1/1** | Post-hoc diagnostic; no engine cell | `docs/source_diversified_top20.json` |
| `BAND-5` | Six seeds `20612601-20612606`, 12 cells at 40 and 112 | **89/89** rank-21-40 edges served at 112 and **0** at 40; B1-B8 pass | Class-level confirmed; does **not** validate BAND-1's 62 named edges | `docs/presence_band_rank_5_run.json` |
| `CORE-BAND-ADMISSION-1` | Six fresh seeds `20617101-20617106`, 12 cells, cap 112 | Both arms cover **22,753/22,753** tier slots, **0** replacements, identical window digests; false-admission **0.701599** both, difference **0.0** | **`VOID`**: C3 and C4 fail on cold-start cycles; descriptive non-binding only | `docs/core_band_admission.json` |
| `PRESENCE-CAP-LADDER-1` | Six seeds `20614101-20614106`, 24 cells at 40, 56, 80, 112 | **0** cells run; no grant | `FROZEN, NOT RUN`; not evidence | `docs/presence_cap_ladder_prereg.json` |
| `CONFIRMATORY-RETENTION-INCREMENTAL-1` | Twelve fresh seeds `20618101-20618112`, 120 cycles, cap 40, cycle-60 landmark | **399** never-served, **181** loop-forming, **103** eligible; **0** asserted events; **16** late assertions all formed after 60 | **`VOID`**: M1 population fails; no coefficient read | `docs/retention_incremental.json` |
| `CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1` | Twelve fresh seeds `20619101-20619112`, 120 cycles, cap 40, per-edge 20-cycle window, formation <= 90, follow-up as the single horizon control | **434** never-served, **180** loop-forming, **172** eligible, **70** asserted events; **36** late edges, **18** late events; early OR **2.09** (1.36-3.23), reverse late OR **32.83** (8.66-124.44) | **`CONFIRMED, TEMPORALLY AMBIGUOUS`**: P1-P3 pass, R1 fails; no temporal-order claim | `docs/retention_formation_anchored.json` |

## 4. Block-specific loop numbers

These numbers are **not interchangeable**. The population, seed block and definition change between rows.

| Quantity | Original Q4 | Fresh provenance | Fresh matched controls | Loop-only / persistence |
| --- | ---: | ---: | ---: | ---: |
| Seeds | `20611601-20611606` | `20613101-20613106` | `20615201-20615206` | `20616101-20616112` |
| Never-served population | **180** | **212** | 29 case-control pairs | **177** loop-forming edges |
| Asserted | **26** | **26** | **29** cases | **77** events |
| Loop-formed, asserted | **26/26** | **26/62** loop cell | **29/29** cases | **77** in the loop-only population |
| Loop-formed, not asserted | **35** | **36** | **11/29** controls | **100** |
| No-loop, asserted | **0/118** | **0/124** | — | — |
| Direct count range | **23-47** | **21-49** | matched on final count | **7-55** |
| Best rank range | **22-127** | **22-116** | — | **21-175** |

Two distinctions are easy to lose:

- **Formation is not carrier provenance.** The fresh provenance block has **25** loop carriers and **one workflow-only carrier**. The never-served model still records `ever_loop = true` for all 26, because it measures whether a loop formed anywhere, not whether a loop was the final assertion source. The carrier trace's `loop_carrier` field is the provenance variable; `ever_loop` is the formation variable.
- **The 26 are not one universal population.** The original block has **180** never-served edges; the fresh provenance block has **212**; the loop-only block has **177** loop-forming edges. The number 26 recurs because it is the asserted count in the first two blocks, not because the populations are the same.

## 5. Two failure classes

**Formation / floor failure.** The reset leaves within-cycle world-edge counts at **1-4**; no edge reaches floor **5**; no world-edge candidate exists; `S_ever` is **0**. This is the T1b zero-cell class. Downstream ranking never receives the edge.

**Admission / allocation failure.** The edge is present in the temporal graph at count **23-47** and has a candidate; it ranks **22-127** and does not enter the served transition window. This is the 26 class. It is not a floor miss and not a recording gap: the provenance replay found **0** recording gaps, **18** reverse-orientation identity mismatches and **8** alternate loop/dream paths on the original block.

The two classes can coexist in one run, but a result about one is not a result about the other.

## 6. Tensions that remain

1. **Loop formation is necessary but not sufficient.** In the 177-edge loop-only population, **100** loop-forming edges are not asserted. In the fresh provenance block, **36** of 62 loop-cell edges are not asserted. In the original block, **35** loop-formed edges are not asserted. The "35" is original-block-specific, not a universal count.
2. **Admission and assertion are partially decoupled.** Entropy-first ordering is strong at admission. Rank adds little in the never-served assertion models, and the loop-only model finds rank null. The clean statement is: **entropy orders admission; the assertion models do not establish an entropy or rank effect among never-served edges.** The mechanism that would connect the two is not measured.
3. **Reverse timing is untested.** Assertion is measured at the end; retention is accumulated across the run. If asserted edges are preferentially retained after assertion, the association is partly reverse. No block records the first assertion cycle.
4. **The count reversal is not a causal identification.** A sign reversal is compatible with mediation, confounding, collider structure, or a noisier proxy for the same latent loop quality. The data support "count is not robust conditional on persistence," not "count is downstream."
5. **Carrier provenance and loop formation differ.** The fresh block has one workflow-only assertion carrier even though the edge also has `ever_loop = true`. "All asserted never-served edges have loops" is true for the original carrier trace and for `ever_loop` in both model blocks; it is **not** true as a statement about assertion carriers in the fresh block.

## 7. What this page does not license

- **"Organica is cognition-like."** The evidence supports selection and persistence patterns that are cognition-relevant; it does not establish a cognitive capacity.
- **"Loops cause assertion."** The loop contrast is an enrichment, and the persistence model is observational.
- **"Count is downstream."** Count's conditional association reverses; the direction is not identified.
- **"Strength dominates."** The separation is real; the coefficient is near-separated and not a precise effect.
- **"All loops matter."** Most loop-forming edges are not asserted.
- **"The 26 are universal."** The asserted count is 26 in two blocks, but the populations are 180 and 212, and the loop-only block has 177 with 77 asserted.
- **"Entropy explains a fixed share of rank variance."** No cited artifact carries that decomposition.
- **"Core+band confirms the admission rule."** The block is `VOID`; its identical arms are descriptive only.
- **"The cap ladder prices the bands."** It has no grant and no cells.
- **"The retention landmark confirms pre-assertion retention."** It is `VOID`: the 60-cycle landmark leaves 103 eligible edges and 0 asserted events, so no coefficient is read.
- **"The cap-112 runs are owner-authorised on their records."** `PRESENCE-COMPARATOR-112` and `PRESENCE-CAP-1-112` are `FROZEN, RUN`, but both cite a preparation-only quote ("Write the dated cap-112 authorisation document ..."). Their gates and numbers stand; the run authorisation itself is not recorded. See `docs/AUTHORISATION-PROVENANCE-AUDIT.md`.

## 8. Priority

1. **The next retention block tests a distinct structure-entry transition, not post-landmark persistence.** `CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1` is `FROZEN, NOT RUN` in `docs/retention_entry_transition_prereg.json` / `docs/RETENTION-ENTRY-TRANSITION-PREREGISTRATION.md`: 24 fresh seeds, a structure-free interval through `f + 39`, and a sustained first entry at `f + 40` or later, with early and proximal retention both measured before the outcome and gates D1-D10. The runner is built behind the grant check; no grant or cell exists. Its feasibility gate may return `VOID`, and it does not re-score the prior block.
2. **The formation-anchored retention follow-up is confirmed but temporally ambiguous.** `CONFIRMATORY-RETENTION-FORMATION-ANCHORED-1` used fresh seeds `20619101-20619112` and a per-edge 20-cycle window from formation through `formation + 19`, admitting never-served loop edges formed by cycle 90. The corrected post-landmark onset found **172** eligible edges and **70** asserted events; the late cohort had **36** edges and **18** events, and all nine gates pass. Early retention OR is **2.09** (1.36-3.23); reverse post-landmark retention OR is **32.83** (8.66-124.44). P1-P3 pass and R1 fails, so the block cannot establish that early retention precedes assertion. The reverse-model audit finds no material late-retention/follow-up collinearity (pairwise VIF **1.10**, late OR **33.50** without the follow-up control), but the reverse OR is a boundary contrast: **11/11** edges at late retention **1.0** are asserted, **58/100** in between, against **1/55** at **0.0**. See `docs/RETENTION-FORMATION-ANCHORED.md` and `docs/RETENTION-REVERSE-OVERLAP-AUDIT.md`.
3. **The retention landmark ran and is `VOID`.** `CONFIRMATORY-RETENTION-INCREMENTAL-1` used fresh seeds `20618101-20618112`, a cycle-60 landmark and a reverse-time late-retention diagnostic. It found **103** eligible loop-forming never-served edges but **0** asserted events: every late assertion formed after cycle 60. M1 fails, no coefficient is read, and the block does not enter Tier 1. See `docs/RETENTION-INCREMENTAL.md`. The next retention question needs a different design, not a re-score.
4. **Early-window successor-representation diagnostic.** Build the graph score from an early window, predict a held-out later assertion, and compare against count, rank, retention and strength. This is a separate diagnostic, not a paper claim.
5. **The cap ladder**, if a dated grant is recorded. It is already frozen at 24 cells and has a runner; it is not evidence until it runs.
6. **A corrected core+band block**, only under a new preregistration and a new grant. The current block is `VOID`; do not re-score it or reuse its seeds.

No further count study is warranted except as a control. The count question has been measured enough to show that count is not an independent positive signal in the persistence model; another count-only block would not discriminate the remaining hypotheses.

## 9. Evidence index

- Persistence: `docs/t1b_persistence_off_run.json`, `docs/T1B-PERSISTENCE-OFF-RESULT.md`, `docs/persistence_zero_served_diagnostic.json`, `docs/PERSISTENCE-ZERO-SERVED-NOTE.md`
- Original assertion model: `docs/never_served_assertion_model.json`, `docs/NEVER-SERVED-ASSERTION-MODEL-RESULT.md`
- Provenance and carriers: `docs/assertion_provenance.json`, `docs/ASSERTION-PROVENANCE.md`, `docs/assertion_carrier_trace.json`, `docs/ASSERTION-CARRIER-TRACE.md`
- Replication: `docs/never_served_assertion_model_replication.json`, `docs/NEVER-SERVED-ASSERTION-MODEL-REPLICATION.md`, `docs/assertion_provenance_replication.json`, `docs/ASSERTION-PROVENANCE-REPLICATION.md`
- Matched carrier: `docs/matched_carrier_replication_2_prereg.json`, `docs/matched_carrier_replication_2.json`, `docs/MATCHED-CARRIER-REPLICATION-2.md`
- Loop-only model: `docs/loop_only_assertion_model_prereg.json`, `docs/loop_only_assertion_model.json`, `docs/LOOP-ONLY-ASSERTION-MODEL.md`
- Persistence extension: `docs/loop_persistence_assertion_model.json`, `docs/LOOP-PERSISTENCE-ASSERTION-MODEL.md`
- Ranking diagnostics: `docs/schema_priority_gate.json`, `docs/SCHEMA-PRIORITY-GATE.md`, `docs/stored_field_tiebreak.json`, `docs/STORED-FIELD-TIEBREAK.md`, `docs/source_diversified_top20.json`, `docs/SOURCE-DIVERSIFIED-TOP20.md`
- Bands and caps: `docs/presence_band_rank_5_run.json`, `docs/core_band_admission.json`, `docs/CORE-BAND-ADMISSION.md`, `docs/core_band_admission_prereg.json`, `docs/presence_cap_ladder_prereg.json`
- Retention: `docs/retention_incremental_prereg.json`, `docs/RETENTION-INCREMENTAL-PREREGISTRATION.md`, `docs/AUTHORISATION-RETENTION-INCREMENTAL-1.md`, `docs/retention_incremental.json`, `docs/RETENTION-INCREMENTAL.md`
- Retention runner: `benchmarks/retention_incremental.py` (grant-gated; twelve cells run, `VOID`)
- Retention entry-transition design: `docs/RETENTION-ENTRY-TRANSITION-DESIGN.md` (design rationale)
- Retention entry-transition prereg: `docs/retention_entry_transition_prereg.json` / `docs/RETENTION-ENTRY-TRANSITION-PREREGISTRATION.md` (`FROZEN, NOT RUN`, runner built, no grant, no result)
- Entry-transition runner: `benchmarks/retention_entry_transition.py` (full appearance-cycle capture, D1-D10 adjudication, grant-gated dry-run)
- Reverse-model overlap audit: `docs/RETENTION-REVERSE-OVERLAP-AUDIT.md` (diagnostic of the recorded reverse model; no new cells)
- Authorisation provenance: `docs/AUTHORISATION-PROVENANCE-AUDIT.md` (14 documents, 21 records; the cap-112 run records cite a preparation-only quote)
- Formation-anchored retention: `docs/retention_formation_anchored_prereg.json`, `docs/RETENTION-FORMATION-ANCHORED-PREREGISTRATION.md`, `docs/AUTHORISATION-RETENTION-FORMATION-ANCHORED-1.md`, `docs/retention_formation_anchored.json`, `docs/RETENTION-FORMATION-ANCHORED.md`; runner `benchmarks/retention_formation_anchored.py`
- Registry: `docs/RESEARCH-FINDINGS.md`, `docs/research_question_registry.json`

## How to update this page

Append a dated section when a block changes a claim's scope; do not rewrite an older block's numbers. A new measurement belongs in its own artifact and registry question. If a block is `VOID`, say so and keep it out of the hierarchy. If a block is `POST-HOC`, keep it out of Tier 1 even when its coefficients are large.
