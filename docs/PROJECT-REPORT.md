# Project report — status, evidence and research timeline

**Status: synthesis, not a result.** This page adds no measurement and changes no verdict. The
cited artifacts and `docs/RESEARCH-FINDINGS.md` are authoritative. It is dated **2026-11-13**;
figures are read from the committed records on that date.

## 1. One-paragraph status

Organica demonstrably develops structure through experience, but it has not yet demonstrated that
those structures confer a measurable external advantage. The positive half is measured: structure
forms, history and curriculum matter, lineage is grounded, and persistence changes what reaches
candidate formation. The negative half is also measured: six external task families are negative,
the acquisition campaign stopped at its own asserted-structure gate, and no positive transfer has
been demonstrated. The current frontier is therefore not "can development occur?" but "which
mechanism determines which internally developed structures become behaviorally active?"

## 2. Repository age and experimental-cycle timeline

The repository's first commit is **`15149cb`**, dated **2026-10-20 09:04 -06:00** ("initial commit
of Project Organica developmental stack (Gen 0 - Gen 8)"). As of **2026-11-13**, the recorded
repository history is **24 days old**, with **503 commits through `d2ab04a`** and **seven tags**.

| Date | Day | Record |
| --- | ---: | --- |
| 2026-10-20 | 0 | First commit: the Gen 0–8 stack, manifesto, papers and reproduction material |
| 2026-10-23 | 3 | `v0.6.0` and `v0.7.0` |
| 2026-10-24 | 4 | `v0.8.0` and `v0.9.0`; `v0.9.0` becomes the archival Organica 1 reference |
| 2026-10-29 | 9 | `audit-trace-v1`; the audit instrumentation is frozen |
| 2026-10-31 | 11 | `v0.10.0` |
| 2026-11-06 | 17 | `v0.12.0` deposit |
| 2026-11-13 | 24 | `b173ad6`; the retention, presence and provenance blocks |

**Repository age is not project age.** The initial commit already contains the Gen 0–8 architecture,
the papers and the research chronicle, so the intellectual work may predate the first commit. What
is measured here is the age of the **recorded repository history**, not the age of the ideas.

The same distinction applies to the "90-day" longitudinal study. It is a designed horizon and a
cycle count, not 90 days of wall-clock elapsed time. The live study reached **5,396 sleep cycles**
before it was paused; the last daemon session completed **1,032 continuous-run cycles**.

### Multiple clocks

Calendar age, repository activity and experimental exposure measure different things. They must
not be added together into a single "developmental age."

| Clock | Measured value | What it counts | What it does not mean |
| --- | ---: | --- | --- |
| Calendar age | **24 days** (2026-10-20 to 2026-11-13) | Elapsed recorded repository history | The age of the ideas or the architecture |
| Commit clock | **503 commits** through `d2ab04a` | Recorded changes to the repository | Independent experiments or replications |
| Test clock | **2,274 passed, 19 skipped, 0 failed of 2,293** | Suite assertions on 2026-11-13 | Scientific confirmation of the claims under test |
| Live developmental clock | **5,396 sleep cycles** | One paused longitudinal run against one preserved database | Aggregate experience across all colonies or worlds |
| Tier-1 campaign clock | **18,000 colony-cycles** | Six colonies × 3,000 cycles in the matrix | One organism's continuous lifetime |

The live cycles and the campaign cycles are both real exposure, but they are **separate runs on
separate substrates**. The correct aggregate statement is "thousands of experimental cycles across
multiple campaigns," not "one system has lived for thousands of cycles." That distinction matters
when the negative results are interpreted: the project has more experimental exposure than its
calendar age suggests, but less continuous developmental history than the raw cycle total suggests.

Experimental exposure is therefore substantial even though the calendar is short:

| Record | Measured exposure |
| --- | --- |
| Live longitudinal study | **5,396** sleep cycles; paused, database and log preserved |
| Tier-1 matrix | six colonies × **3,000** cycles = **18,000** colony-cycles |
| Acquisition campaign | **0–3 of 112** world edges asserted against **112/112** present in raw memory; the 600-cell factorial did not run |
| Original never-served block | **180** never-served edges; **26** asserted; **18** identity / **8** alternate carriers |
| Fresh provenance block | **212** never-served edges; **26** asserted; **24** identity / **2** alternate; verdict **`DIRECTIONAL ONLY`** |
| Loop-only block | **177** loop-forming never-served edges; **77** asserted events |
| Formation-anchored retention | **172** eligible edges; **70** asserted events; early OR **2.09** (1.36–3.23), reverse late OR **32.83** (8.66–124.44) |
| Test suite | **2,274 passed, 19 skipped, 0 failed of 2,293** on 2026-11-13 |

### What the timeline means

**The velocity is unusually high.** Five hundred commits and a large artifact trail in 24 days is
not a normal research cadence. It is also not the same thing as time-separated replication: most
of the work sits on one engine line, one synthetic world family and a small number of reused seed
blocks.

**The youth argument cuts both ways.** At 24 days, the absence of a positive external result is not
alarming. But the negative results are also 24 days old. They are strong enough to constrain the
next experiment; they are not old enough to be a final verdict on the architecture.

**Auditability substitutes for elapsed time.** When documentation is compressed this tightly, the
audit trail is what keeps the record checkable. That is why seed freshness, provenance, frozen
records and the distinction between confirmatory and post-hoc blocks carry more weight here than
they would in a slower program.

## 3. What is established

- Development is a real phenomenon: internal epistemic structure forms without pretrained domain
  knowledge, and the recorded lineage is grounded.
- History and curriculum matter. The curriculum experiments changed inventory from **74** to
  **128** across the recorded ladder; strict order dependence remains untested.
- Persistence affects candidate eligibility. Shipped `S_ever` values **101, 95, 100, 103, 98, 99**
  against persistence-off **0, 1, 0, 3, 0, 3**, mean paired difference **98.167**, 95% interval
  **[96, 100]**.
- The 26 asserted-but-never-served edges are construction-present and excluded at admission, not
  lost at construction or by a recording gap.
- **A0 stage analysis (2026-11-13, a re-reading rather than a new measurement): no single upstream
  selection stage is identified.** Admission excludes the direct edge — **672** present, **671**
  constructed, **179** never served, **26** asserted but never served, **0** of the 26 inside the
  served transition budget — while loop construction creates the carrier: **26/26** rows, cycles
  **37–117**, median first formation **76**. The carrier exists at or before the best recorded rank
  in **17** rows and after it in **9**. The two are parallel paths to assertion, so the 2×2
  discrimination design is **`NOT IDENTIFIED`** as written. The replacement is a registered two-path
  design — admission × carrier availability, with an assertion-blockade arm and a double-block
  positive control — but it is design-only, with no seeds, runner or grant. The **C1–C9 preflight**
  classified **0 satisfied, 9 requiring instrumentation, 0 unsatisfiable**: the 26-row slice is
  entirely `A−K+`, no artifact records an assertion cycle, and none of the interventions exists. A1
  is therefore not admissible yet, but no condition has been shown impossible. This blocks A1 as
  written; it does not show that no selection process exists.
- Loops are strongly enriched among asserted never-served edges: **26/26** cases against **13/26**
  matched controls on the original block; **29/29** against **11/29** on the fresh matched block.
- Count is not an independent positive signal once retention and strength are measured.
- Retention is associated with assertion but the temporal order is unresolved; the
  formation-anchored block is **`CONFIRMED, TEMPORALLY AMBIGUOUS`**.

## 4. What is not established

- Positive transfer, external task advantage or a capability claim.
- That loop or workflow carriers **cause** assertion, as opposed to marking it.
- That early retention precedes assertion.
- That strength dominates the carrier relationship, or that count is downstream.
- That entropy explains a fixed share of rank variance.
- That the core+band admission rule works; that block is **`VOID`**.
- That the cap ladder prices the bands; it is **`FROZEN, NOT RUN`**.
- That the entry-transition retention block has a result; it is **`FROZEN, NOT RUN`**, with no grant.
- Generality beyond the tested world family, or independent replication by another laboratory.

## 5. Conservative current-status restatement

**This is a status boundary, not an empirical finding.** It restates the scope of the evidence in
one place and adds no measurement. It is deliberately separate from the established findings above.

> Developmental structure formation is supported within the tested scope. Persistence effects are
> supported. Admission anomalies are supported. Carrier enrichment is supported. Carrier causation
> is untested. Positive transfer and external advantage remain unestablished. Audit consistency has
> improved through explicit treatment of downstream seed reuse, but the underlying scientific claims
> rest on the same experimental evidence as before.

The repair changes what the record can say about itself, not what the experiments established:

| Question | After the repair |
| --- | --- |
| Did any verdict change? | No |
| Was any cell rerun? | No |
| Did any artifact outcome change? | No |
| Did the seed reuse become explicit? | Yes — intentional downstream reuse is now registered |
| Did the suite become green? | Yes — **2,274 passed, 19 skipped, 0 failed** |
| Did this validate the underlying replication independently? | No |

The remaining uncertainty is concentrated in three layers, which should not be collapsed into one
question:

1. **Selection:** what determines which internally developed structures become behaviorally active?
2. **Carrier role:** is carrier enrichment causal, a common cause, or a readout of selection that has
   already happened elsewhere?
3. **External link:** can any of this be connected to a measurable external advantage, rather than
   only to internal assertion?

This is a conservative statement because it keeps the audit repair and the empirical claims in
different categories. The repair improved the record; it did not improve the result.

## 6. Integrity state

- The full suite is green after the 2026-11-13 repair: **2,274 passed, 19 skipped, 0 failed**.
- The seed-freshness scans now distinguish intentionally reused downstream analyses from new
  independent draws. No verdict, cell, seed allocation or artifact result was changed by that repair.
- The two cap-112 run records still cite a preparation-only authorisation quote. Their numerical
  results stand as recorded, but their run-authorisation provenance is unresolved.
- `PRESENCE-CONVERSION-2` is **`FROZEN, RUN`**; `PRESENCE-CAP-LADDER-1` and
  `CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1` have no grant and no cells.
- The live study remains paused.

## 7. Roadmap options

| Option | Question | Cost | Main risk |
| --- | --- | ---: | --- |
| **0. Provenance repair** | Are the records internally consistent? | Low | Delays new work |
| **A. Carrier formation** | What forms and selects loop/workflow carriers? | Low | Reused seeds and post-hoc reasoning |
| **B. Carrier intervention** | Does carrier availability cause assertion? | Medium–high | Confounded intervention |
| **C. Entry-transition retention** | Does early retention precede a sustained entry? | Medium | Feasibility may return `VOID`; needs a grant |
| **D. Short-group topology** | Why do reset groups stop at 4–8 events? | Low–medium | Another diagnostic without a decision |
| **E. Publication** | Can the audit method and negative results be made citable? | Low compute | None scientific; owner action |
| **F. V2 engineering** | Can a targeted redesign fix the weakness? | High | Repeating a guessed-mechanism cycle |

**Recommended sequence:** finish provenance repair and publication in parallel; characterize
carrier formation; then implement and preregister the registered two-path design, because A0 found
no single upstream selection stage. A1 remains design-only until it has a granted, runnable block.
Treat A and B as one program: A says where to intervene, B says whether the intervention matters.
Do not start V2 until that result exists.

The decision-gated version of this sequence is [`ROADMAP.md`](../ROADMAP.md), which states each
exit gate, what each outcome licenses, and which items are deferred. This table is the report's
synthesis, not a second plan.

## 8. Evidence index

- Persistence: `docs/t1b_persistence_off_run.json`, `docs/T1B-PERSISTENCE-OFF-RESULT.md`
- Assertion anomaly: `docs/never_served_assertion_model.json`, `docs/NEVER-SERVED-ASSERTION-MODEL-RESULT.md`
- Provenance and carriers: `docs/assertion_provenance.json`, `docs/assertion_carrier_trace.json`,
  `docs/matched_carrier_replication_2.json`
- Carrier A0: `docs/carrier_formation_a0.json`, `docs/CARRIER-FORMATION-A0.md`
- Two-path design: `docs/TWO-PATH-ADMISSION-CARRIER-DESIGN.md`
- C1–C9 preflight: `docs/c1_c9_preflight.json`, `docs/C1-C9-PREFLIGHT.md`
- C6 timing observer: `docs/C6-ASSERTION-TIMING-INSTRUMENTATION.md`, `benchmarks/c6_timing_observer.py`
- Retention: `docs/retention_formation_anchored.json`, `docs/RETENTION-FORMATION-ANCHORED.md`,
  `docs/RETENTION-ENTRY-TRANSITION-PREREGISTRATION.md`
- Acquisition: `docs/ACQUISITION-ENDPOINT-AUDIT.md`, `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`
- Current hierarchy: `docs/RESEARCH-HIERARCHY.md`, `docs/FINDINGS-LEDGER.md`
- Registry and claims: `docs/RESEARCH-FINDINGS.md`, `docs/claim_ledger.json`
