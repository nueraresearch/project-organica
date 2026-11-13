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
repository history is **24 days old**, with **502 commits** and **seven tags**.

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

## 5. Integrity state

- The full suite is green after the 2026-11-13 repair: **2,274 passed, 19 skipped, 0 failed**.
- The seed-freshness scans now distinguish intentionally reused downstream analyses from new
  independent draws. No verdict, cell, seed allocation or artifact result was changed by that repair.
- The two cap-112 run records still cite a preparation-only authorisation quote. Their numerical
  results stand as recorded, but their run-authorisation provenance is unresolved.
- `PRESENCE-CONVERSION-2` is **`FROZEN, RUN`**; `PRESENCE-CAP-LADDER-1` and
  `CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1` have no grant and no cells.
- The live study remains paused.

## 6. Roadmap options

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
carrier formation; then run one carrier intervention. Treat A and B as one program: A says where to
intervene, B says whether the intervention matters. Do not start V2 until that result exists.

## 7. Evidence index

- Persistence: `docs/t1b_persistence_off_run.json`, `docs/T1B-PERSISTENCE-OFF-RESULT.md`
- Assertion anomaly: `docs/never_served_assertion_model.json`, `docs/NEVER-SERVED-ASSERTION-MODEL-RESULT.md`
- Provenance and carriers: `docs/assertion_provenance.json`, `docs/assertion_carrier_trace.json`,
  `docs/matched_carrier_replication_2.json`
- Retention: `docs/retention_formation_anchored.json`, `docs/RETENTION-FORMATION-ANCHORED.md`,
  `docs/RETENTION-ENTRY-TRANSITION-PREREGISTRATION.md`
- Acquisition: `docs/ACQUISITION-ENDPOINT-AUDIT.md`, `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`
- Current hierarchy: `docs/RESEARCH-HIERARCHY.md`, `docs/FINDINGS-LEDGER.md`
- Registry and claims: `docs/RESEARCH-FINDINGS.md`, `docs/claim_ledger.json`
