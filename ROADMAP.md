# Project Organica: Research Roadmap

**Planning record — 2026-11-13.** This roadmap replaces the earlier phase plan as the project's
forward-looking plan. It changes no verdict, gate, seed allocation, result or frozen record. The
synthesis of what the evidence supports is [`docs/PROJECT-REPORT.md`](docs/PROJECT-REPORT.md); the
evidence artifacts remain authoritative.

## How to read this roadmap

This is a roadmap of **decisions**, not themes or calendar commitments. Every active item states:

- the question it addresses,
- the current evidence and its limits,
- the gate that must be passed before the next item,
- what each outcome would license.

Two rules govern the whole document:

1. **Scientific status and audit status are different currencies.** Scientific claims use
   *supported within the tested scope*, *not established* or *untested*. Record-keeping uses
   *verified*, *registered*, *unresolved* or *operationally closed*. An audit improvement is never
   evidence for a scientific claim.
2. **Uncertainty must be narrow enough to discriminate.** A study earns its cost only if its
   possible outcomes map differently onto the surviving explanations. More description of the same
   correlation is not progress.

No calendar dates are assigned. Available research hours are unknown, and the dependencies below
are the real constraints.

## Current position

- Development, history dependence, persistence effects, admission anomalies and carrier enrichment
  are supported within their tested scopes.
- Carrier **causation** is untested. Positive transfer and external advantage are not established.
- The live longitudinal study is **paused** at **5,396 sleep cycles**. V2 is not cut; V2–V5 have not
  run.
- The full suite is green: **2,274 passed, 19 skipped, 0 failed of 2,293**.
- The seed-freshness repair registered intentional downstream reuse. It changed no verdict, cell,
  seed allocation or artifact outcome, and did not independently validate the reused analyses.
- Cap-112 run-authorisation provenance is **unresolved**. The numerical results stand as recorded.
- Eight manuscript files exist; **none is published**. Papers 01 and 02 have complete submission
  packages and await the owner's deposit.
- `PRESENCE-CONVERSION-2` is **`FROZEN, RUN`**. `PRESENCE-CAP-LADDER-1` and
  `CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1` are **`FROZEN, NOT RUN`**, with no grant and no cells.

---

## Track A — Scientific discrimination

Track A is sequential. A0 characterizes the selection problem; A1 is the first test that can
discriminate among the carrier explanations; A3 is only meaningful after a mechanism survives.

### A0. Carrier formation — descriptive, current

**Question.** What forms and selects the loop and workflow carriers behind asserted never-served
edges, and why does the direct edge never become a final prediction source?

**Current evidence.** On the original block, **26/26** asserted never-served edges have a loop
carrier. The fresh matched block has **25** loop carriers and **1** workflow-only carrier, with
**24 identity / 2 alternate** paths and a **`DIRECTIONAL ONLY`** replication verdict. Both fresh
alternate paths concentrate on seed `20613106`. This is enrichment, not causation.

**A0 result (2026-11-13).** The read-only analysis in
[`docs/CARRIER-FORMATION-A0.md`](docs/CARRIER-FORMATION-A0.md) returns
**`NO SINGLE UPSTREAM SELECTION STAGE IDENTIFIED`**. Admission excludes the direct edge: **672**
present, **671** constructed, **179** never served, **26** asserted but never served, and **0** of
the 26 inside the served transition budget. Candidate formation creates the carrier: **26/26** rows,
cycles **37–117**, median first formation **76**. The carrier exists at or before the best recorded
rank in **17** rows and after it in **9**. Admission and carrier formation are parallel paths to
assertion, not one upstream chain.

**Work.** Classify carrier formation timing, source diversity, schema priority, persistence and
final readout. Explain the direct-edge exclusion and the seed concentration. Distinguish
loop-carried paths from workflow-only paths. Pre-register a fresh confirmatory block before making
any general claim.

**Exit gate.** A written formation account that names the selection stages it measured, plus a
pre-registered fresh design if the result is to be generalized beyond the observed blocks. **The
stage-identification part is not passed:** A0 found no single upstream stage, so A1 is blocked as
written.

**What it licenses.** The variables and contrasts for A1. It does **not** license a causal claim,
and it does not by itself justify V2.

### A1. Carrier intervention — central discrimination test

**Status: REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT.** A0 blocked the single-stage 2×2;
the replacement is
[`docs/TWO-PATH-ADMISSION-CARRIER-DESIGN.md`](docs/TWO-PATH-ADMISSION-CARRIER-DESIGN.md). It treats
admission and carrier availability as parallel factors, adds an assertion-blockade ordering arm and
uses `A−K−` as a positive control. It assigns no seeds, implements no runner and authorises no cell.

**Question.** Do admission and carrier availability each contribute to assertion independently, and
is the carrier–assertion association causal, a shared-cause association, an admission-only
association, or a readout of assertion?

**Design requirements.** The registered design is two-path, not a single-stage 2×2.

- Four cells: admission allowed/blocked × carrier available/blocked (`A± K±`). `A−K−` is a positive
  control: assertion surviving both blocks is `THIRD ROUTE PRESENT`.
- `A−` blocks served-window availability; `K−` blocks carrier-to-readout availability; each must
  leave the other path intact. `Y−` blocks assertion and measures carrier survival.
- `U` — pre-treatment temporal count, reverse count and strength — is measured and used for
  stratification, not as a post-treatment covariate.
- Precommit the prediction table before running. Separate observer-side reconstruction from
  subject-side manipulation. Use matched controls and fresh seeds.

**What the outcomes mean.**

- **`CARRIER CAUSAL`:** carrier availability contributes to assertion at `A−`, the association
  survives within `U`, and assertion blockade does not remove the carrier.
- **`ADMISSION ONLY`:** the carrier effect is null and the association vanishes given admission.
- **`SHARED CAUSE`:** the carrier effect is null and the association vanishes within `U`.
- **`READOUT`:** the carrier effect is null and assertion blockade reduces the carrier.
- **`THIRD ROUTE PRESENT` / `SHARED CAUSE / READOUT NOT SEPARATED` / `MIXED`:** no model is selected;
  the named structural failure is the result.

**Exit gate.** At least one model is eliminated by the precommitted predictions, or a structural
verdict (`THIRD ROUTE PRESENT`, `SHARED CAUSE / READOUT NOT SEPARATED`, `MIXED`, `VOID`) is recorded
with no causal claim.

**What it licenses.** A causal carrier result licenses a carrier-targeted A3 and V2 discussion; an
admission-only result targets admission; a shared-cause result targets `U`; a readout result demotes
the carrier. A structural failure licenses no A3 and no V2 design.

### M1. Mechanism branch — after A1

M1 is a routing gate, not a second intervention. It reads A1's precommitted signature and decides
which mechanism, if any, A3 may target. A surviving explanation is not the same as a
mechanism-bearing result: common cause and readout both preserve the carrier's association while
denying it causal status.

| Branch | A1 signature | M1 status | A3 target | V2 implication |
| --- | --- | --- | --- | --- |
| **M1-C — Causal carrier** | Carrier effect at `A−`; association survives within `U`; carrier precedes assertion; `Y−` does not remove carrier | **PASS — carrier mechanism** | Carrier → external | Carrier-targeted V2 eligible |
| **M1-A — Admission only** | No carrier effect at `A−`; association vanishes given admission; admission effect positive | **PASS — admission mechanism** | Admission → external | Admission-targeted V2 eligible; no carrier V2 |
| **M1-CC — Shared cause** | No carrier effect; association persists given admission but vanishes within `U`; `Y−` does not remove carrier | **PASS — shared-cause target** | `U` → external | Shared-cause V2 eligible; no carrier V2 |
| **M1-RO — Readout only** | No carrier effect; `Y−` reduces carrier; assertion precedes carrier | **PASS — readout target; carrier demoted** | Assertion or admission → external, never carrier | No carrier-targeted V2 |
| **M1-X — Not identified** | Signatures conflict, `THIRD ROUTE PRESENT`, or shared cause and readout are not separated | **FAIL — no mechanism branch** | None | None; redesign only with a named defect |
| **M1-V — Void** | A manipulation, independence, pairing or determinism gate fails | **VOID** | None until the instrument is fixed | None |

M1 does **not** mean “the carrier is causal.” It means “the surviving mechanism is named.” Under
M1-A, M1-CC and M1-RO the carrier is not the target, and an A3 study that manipulates the carrier
would be testing the wrong object.

### A2. Entry-transition retention — conditional

**Question.** Does early retention precede a sustained structure-entry transition, rather than mere
final presence?

**Status.** `CONFIRMATORY-RETENTION-ENTRY-TRANSITION-1` is designed — 24 fresh seeds, 120 cycles,
structure-free through cycle 59, sustained entry at cycle 60 or later, with D1–D10 gates — but it is
**`FROZEN, NOT RUN`** and has no owner grant.

**Exit gate.** Either the owner grants the block and it runs, or the feasibility gate returns
`VOID`, which is an accepted closure. A positive result strengthens temporal ordering; it remains
observational and does not prove causation.

**What it licenses.** A timing result orthogonal to A1. It does not replace the carrier
intervention and does not establish external advantage.

### A3. External link — gated

**Question.** Can asserted structure be connected to a measurable external advantage rather than
only to internal assertion?

**Status.** Not designed for execution. It becomes actionable only after M1 routes a
mechanism-bearing branch. The target is fixed by that branch: carrier under M1-C, admission under
M1-A, `U` under M1-CC, and assertion or admission under M1-RO. A3 never targets the carrier under
M1-A, M1-CC or M1-RO. A2 is orthogonal and does not route A3 on its own.

**Design requirement.** The endpoint must be external to the internal assertion record, specified
in advance, and compared against the appropriate baseline. Internal coverage, rank or assertion
counts are not substitutes for an external endpoint.

**Exit gate.** A measured external result, positive or negative, under a pre-registered design.

**What it licenses.** A positive result supports a limited external-advantage claim within the
tested task family. A negative result closes that claim for the tested scope. Neither result
supports a general-intelligence claim.

---

## Track B — Publication and record

Track B runs in parallel with Track A and consumes no engine cells. It is not a reward for
finishing the science; it is an independent deliverable.

### B0. Close cap-112 authorisation provenance

**Issue.** The cap-112 run records cite a preparation-only quote: *"Write the dated cap-112
authorisation document for the comparator, Q1 and Q2…"* That is not a run authorisation. The
numerical results stand as recorded; their authorisation provenance does not.

**Work.** Choose and record one disposition: a corrected authorisation record, a disclosed
amendment, or an explicit reclassification. Do not rewrite the numerical results.

**Exit gate.** The authorisation guard reports no unresolved cap-112 violation, or the records carry
an explicit, dated disposition that explains the exception.

**What it licenses.** A clean provenance basis for any new confirmatory claim. It does not validate
the underlying result.

### B1. Deposit Papers 01 and 02

**Status.** Submission packages are complete, including rendered PDFs, checked figures, citations
and reproduction bundles. The remaining step is the owner's upload and DOI creation.

**Exit gate.** Both papers have a public deposit and a DOI.

### B2. Publish the negative-results and auditability record

**Work.** Make the developmental architecture, the reproducible negative-results map and the audit
method public. The claim is methodological and empirical within scope, not a capability claim.

**Exit gate.** A public, citable record that distinguishes supported findings from unresolved ones.

### B3. Independent review and replication

**Work.** Seek review by researchers who did not build the system, and support at least one
independent reconstruction of a central result.

**Exit gate.** External review or replication, recorded separately from internal replication.

---

## Track C — Deferred and conditional

These items are real, but none is authorized to start from the current position.

| Item | Condition before starting |
| --- | --- |
| Short-group topology | A named architectural decision that both a positive and a negative result would license. Without it, defer. |
| Cap ladder | A dated owner grant. Currently `FROZEN, NOT RUN`; no cells. |
| BAND-2 governance | Keep as record bookkeeping. It is not a scientific priority and does not validate BAND-1. |
| V2 engineering | Only after M1 routes a mechanism branch: M1-C targets the carrier, M1-A targets admission, M1-CC targets `U`, and M1-RO targets assertion or admission. M1-X and M1-V license no V2. Do not design V2 against a guessed mechanism. |
| Long-duration soak testing | Not active while the live study is paused. Requires an explicit restart decision. |
| Generation 9 self-modeling | Remains locked and unimplemented. Not a current roadmap item. |

---

## Gates and recommended order

| Gate | Passes when | If it does not pass |
| --- | --- | --- |
| **G0 — Record** | Cap-112 provenance has a disposition and the suite is green | No new confirmatory claim; publication can still proceed |
| **G1 — Paths** | A0 is complete and the design uses admission and carrier as separately manipulable paths, with cross-path checks | A1 stays blocked; a design that cannot block either path returns `NOT IDENTIFIED` |
| **G2 — Discrimination** | A1 eliminates at least one of causal / common-cause / readout | No carrier claim; do not start V2 |
| **M1 — Mechanism branch** | A1's signature routes to M1-C, M1-CC or M1-RO | M1-X or M1-V: no A3, no V2; redesign only with a named defect |
| **G3 — External link** | A3 measures an endpoint against the M1-selected target | External advantage remains unestablished |
| **G4 — V2** | M1 routes a mechanism-bearing branch and the target is named | Keep V2 deferred; do not substitute another diagnostic |
| **P1 — Publication** | Papers 01 and 02 have public deposits and DOIs | External value is delayed, not a scientific failure |

**Recommended order.**

1. **Now, in parallel:** B0 (cap-112 disposition), A0 (carrier formation), and B1/B2 (deposit and
   publish the existing record).
2. **After A0:** the two-path design is registered. Implement and preregister its four cells, `Y−`
   arm and `U` strata before running any carrier intervention; an owner grant is still required.
3. **If granted:** run A2 in parallel or after A1; accept `VOID` as closure.
4. **After M1:** design A3 around the routed target. M1-CC and M1-RO never target the carrier.
5. **Only after M1 and G4:** discuss V2 engineering, with the same target discipline.
6. **Opportunistically, with a decision rule:** short-group topology. Otherwise leave it deferred.

The pairing of A0 and A1 is deliberate. A0 says where an intervention could act; A1 says whether
acting there matters. Neither is sufficient alone.

---

## Scientific and audit vocabulary

| Ledger | Use these words | Do not use these words for record quality |
| --- | --- | --- |
| Scientific record | supported within the tested scope; not established; untested; not supported | verified, registered, operational |
| Audit and governance record | verified; registered; operational; unresolved; operationally closed | supported, replicated, confirmed |

In particular:

- A repaired classification is **not** a strengthened hypothesis.
- A green suite is **not** evidence for the architecture.
- A registered seed reuse is **not** an independent replication.
- A directional replication is **not** a magnitude replication.

---

## Historical record (not active)

The earlier phase plan is retained here as history, not as current planning:

- **Phase A — Architecture freeze:** completed; Generations 0–8 locked.
- **Phase B — Multi-domain reproduction pack:** completed; four domains.
- **Phase C — Growth benchmark suite:** completed; BM1–BM5.
- **Phase D — Scientific papers:** manuscript set completed; publication remains open.
- **Phase E — Community and ecosystem:** in progress; repository and contribution documents
  published, funding and community engagement open.
- **Phases F/G — Soak and endurance testing:** not run; the live study is paused.
- **Generation 9 — Self-modeling:** locked.

The 2026-11-12 priority banner (carrier formation, then short-group topology, then BAND-2) is
superseded by this roadmap. Its evidence pointer remains valid; its ordering did not include
provenance closure, publication, entry-transition retention or the A1 discrimination gate.
