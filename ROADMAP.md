# Project Organica: Research Roadmap

**Planning record — 2026-11-14.** This roadmap replaces the earlier phase plan as the project's
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

No calendar dates are assigned to phases. Available research hours are unknown, and the
dependencies below are the real constraints; the one dated item is the planning decision below.

## Dated roadmap decision — V2 reservation (2026-11-14)

**Status:** ADOPTED — a planning decision, not a result and not a new V2 design.

**Decision.** **V2 is reserved for a mechanism-driven architectural redesign.** The current work —
instrumentation, governance, preregistration, measurement, audit and record repair, including A1,
M1 and the G9/activation framing — is **0.x work**. It must not be named, versioned or scoped as
V2.

**When V2 becomes eligible.** V2 may be proposed only after **M1 routes a mechanism-bearing branch**
(M1-C, M1-A, M1-CC or M1-RO) and **G4** is passed with a named architectural target. M1-X and M1-V
license no V2. A0/A1 diagnostics, an audit improvement, a green suite, a governance decision or a
record repair do not satisfy this condition, individually or together.

**What this decision does not do.** It creates no V2 design, version, feature, claim, seed, cell,
grant or result. It does not move the package beyond 0.x and does not re-score any existing verdict.
Package **0.15.0** remains the current 0.x build.

**Rejected alternatives.**

- **Call the current instrumentation and governance work V2.** Rejected: V2 is reserved for a
  mechanism-driven architectural redesign, not for measurement or record work.
- **Design V2 from the A0/A1 diagnostics without an M1 mechanism branch.** Rejected: A0/A1 locate
  and discriminate paths; they do not name an architectural mechanism to redesign.
- **Treat the next 0.x capability increment as V2 by relabelling it.** Rejected: a version label is
  not a mechanism, and relabelling would make the record claim a redesign it did not perform.

## 0.x engineering charter (adopted 2026-11-14)

**Status:** ADOPTED — IN FORCE (2026-11-14). See [`docs/DECISION-0X-ENGINEERING-CHARTER.md`](docs/DECISION-0X-ENGINEERING-CHARTER.md).

[`docs/0X-ENGINEERING-CHARTER.md`](docs/0X-ENGINEERING-CHARTER.md) fixes the allowed 0.x change
categories (record, test/CI, instrumentation, engine behavior, packaging, publication), the version
boundary and the stop conditions. It keeps A1 target selection and grant as separate experimental
acts, forbids V2 and G9 work, refuses post-outcome retuning, and does not pre-allocate 0.16–0.20.
It creates no version, engine change, seed, cell, grant or claim; it is now in force as an engineering
boundary and does not authorise any A1 act.

## Current position

- Development, history dependence, persistence effects, admission anomalies and carrier enrichment
  are supported within their tested scopes.
- Carrier **causation** is untested. Positive transfer and external advantage are not established.
- **Progression beyond G8 is gated on activation/use, not on a G9 design.** The next objective is to
  determine what makes a developed, admitted or asserted structure behaviourally active, and whether
  that activation produces an external advantage. Generation 9 remains locked. See
  [`docs/DECISION-PROGRESSION-BEYOND-G8.md`](docs/DECISION-PROGRESSION-BEYOND-G8.md). The
  outcome criteria, six-class stage ledger and activation ladder are in
  [`docs/G9-ACTIVATION-DESIGN.md`](docs/G9-ACTIVATION-DESIGN.md); all remain design-only.
- The live longitudinal study is **paused** at **5,396 sleep cycles**. **V2 is reserved for a
  mechanism-driven architectural redesign (decision 2026-11-14); current work is 0.x.** V2 has not
  been designed or cut, and V2–V5 have not run.
- The full suite is green: **2,276 passed, 19 skipped, 0 failed of 2,295**.
- The seed-freshness repair registered intentional downstream reuse. It changed no verdict, cell,
  seed allocation or artifact outcome, and did not independently validate the reused analyses.
- Cap-112 run-authorisation provenance is **resolved by explicit reclassification (2026-11-14)**:
  the two executed runs are **provisional and not owner-authorised**. Their numerical results and
  gates stand as recorded, but they are not confirmatory. See
  [`docs/CAP-112-PROVENANCE-DISPOSITION.md`](docs/CAP-112-PROVENANCE-DISPOSITION.md).
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

**Reading.** A0 narrowed the admissible design space. It did not narrow the biological hypothesis
space. The next step must either widen that space with instrumentation or close the carrier branch
as not identifiable.

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

**Status: REGISTERED DESIGN — NOT FROZEN, NOT RUN, NO GRANT.** **Program disposition (2026-11-14): COMMITTED TO TARGET RESOLUTION — NO RUN AUTHORISED.** [`docs/DECISION-A1-DISPOSITION.md`](docs/DECISION-A1-DISPOSITION.md) commits A1 to a pre-outcome target-selection protocol, fixed per-seed targets, a freeze and a separate dated grant decision; it does not freeze the manifest, reserve the seeds or authorise a cell. If no target-selection protocol and dated grant decision are recorded by **2026-12-14**, the disposition lapses to **A1 PARKED**. A0 blocked the single-stage 2×2;
the replacement is
[`docs/TWO-PATH-ADMISSION-CARRIER-DESIGN.md`](docs/TWO-PATH-ADMISSION-CARRIER-DESIGN.md). It treats
admission and carrier availability as parallel factors, adds an assertion-blockade ordering arm and
uses `A−K−` as a positive control. The design assigns no seeds; the separate dry-run manifest
proposes candidate seeds **20630101–20630106** but freezes and reserves none. The A−/K−/Y− treatments
are implemented in `benchmarks/a1_arms.py`, but the target edges are unresolved, the manifest is not
frozen and no cell is authorised. **Target-selection protocol (implemented, 2026-11-14):**
[`docs/A1-TARGET-SELECTION-PROTOCOL.md`](docs/A1-TARGET-SELECTION-PROTOCOL.md) fixes the
per-seed selection rule and the cycle-36 `U` sampling point. The corrected sampler captures `U`
before `run_sleep_cycle()` and retains it only when the report cycle is 36. The no-arm pass
formed four disjoint targets for all six provisional seeds in
[`docs/a1_target_selection.json`](docs/a1_target_selection.json). The targets are not entered in
the manifest, no seed is reserved, nothing is frozen and no cell is authorised; blindness checks,
the power review and C4 non-target rows remain open.

**Preflight (2026-11-13): `NOT ADMISSIBLE` — 0/9 satisfied, 9 requiring instrumentation, 0
unsatisfiable.** [`docs/C1-C9-PREFLIGHT.md`](docs/C1-C9-PREFLIGHT.md) found the design blocked by
missing instrumentation, not by a demonstrated impossibility. The 26-row A0 slice is entirely `A−K+`,
so it cannot establish positivity. `C6` was the timing gap; the six-seed block below now satisfies
it. C1–C5 and C7–C9 remain uncleared, so the design is still not admissible. **Readiness
(2026-11-14):** those eight gates now have executable contracts and synthetic controls in
[`docs/A1-GATE-READINESS.md`](docs/A1-GATE-READINESS.md); all eight remain `CONTRACT BUILT, NOT RUN`.
The C1/C4/C7 thresholds and C8 ceiling were precommitted on 2026-11-14 in
[`docs/A1-PRECOMMITTED-THRESHOLDS.md`](docs/A1-PRECOMMITTED-THRESHOLDS.md), before any cell; no cell has
run and no grant exists. Each open gate has **one attempt** and a terminal failure disposition: a
failed or unmeasurable gate closes A1 and requires a new registered design, not another
instrumentation round.

**C6 observer:** [`docs/C6-ASSERTION-TIMING-INSTRUMENTATION.md`](docs/C6-ASSERTION-TIMING-INSTRUMENTATION.md)
is built, and the self-test passes neutrality, mutation and parity. It reads `Y_ind` — assertion from
non-carrier structures — because the full readout `Y_full` is simultaneous with a loop carrier by construction.
A one-seed preflight (20611601) found both orders and passed `N1`/`N3`. A frozen fresh six-seed block
(20621101–20621106, 120 cycles, cap 40) then confirmed **183 K-before, 294 Y-before, 58 same-cycle,
51 no-K and 67 no-Y-ind** across 653 edge rows; the smallest per-seed counts were 22 and 35, all six
seeds met the 10-per-order floor, and `N1`–`N7` pass. **`C6 ORDER VARIATION CONFIRMED`.** The C6
timing requirement is cleared; the two-path admission-by-carrier design remains unrun, and no causal
claim follows. See [`docs/C6-TIMING-BLOCK.md`](docs/C6-TIMING-BLOCK.md).

**Manifest (2026-11-14).** [`docs/A1-TWO-PATH-MANIFEST.md`](docs/A1-TWO-PATH-MANIFEST.md) fixes the
dry-run cell manifest: six seeds × six cells (`A+K+`, `A+K-`, `A-K+`, `A-K-`, `Y−` at `A+K+` and
`A−K+`) plus one determinism control. `--cell` and `--measure` call `refuse()` before a database is
opened; the gate checks a dated grant document and quote, the shipped build, the planned cells, U,
the object fingerprint and seed freshness. The A-/K-/Y- treatments are implemented in
`benchmarks/a1_arms.py`; the target edges remain unresolved, the manifest is not frozen and no grant
exists, so no cell may open a database.

**C6 stop condition.** The observer, edge extractor and neutrality/mutation harness are built. The
one-seed preflight found both orders, so the frozen six-seed block was run and stopped at its
preregistered size. No optional seeds were added after the outcome. Do not add instrumentation
after the build closes; a new requirement goes to the wish-list.

**Question.** Do admission and carrier availability each contribute to assertion independently, and
is the carrier–assertion association causal, a shared-cause association, no carrier relation, or a
readout of assertion?

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
- **`NO CARRIER RELATION`:** the carrier effect is null and the association vanishes given admission.
- **`SHARED CAUSE`:** the carrier effect is null and the association vanishes within `U`.
- **`READOUT`:** the carrier effect is null and assertion blockade reduces the carrier.
- **`THIRD ROUTE PRESENT` / `SHARED CAUSE / READOUT NOT SEPARATED` / `MIXED`:** no model is selected;
  the named structural failure is the result.

**Exit gate.** At least one model is eliminated by the precommitted predictions, or a structural
verdict (`THIRD ROUTE PRESENT`, `SHARED CAUSE / READOUT NOT SEPARATED`, `MIXED`, `VOID`) is recorded
with no causal claim.

**What it licenses.** A causal carrier result licenses a carrier-targeted A3 and a V2 **eligibility**
discussion (not a V2 design); a no-carrier-relation result targets admission; a shared-cause result
targets `U`; a readout result demotes the carrier. A structural failure licenses no A3 and no V2
design.

### M1. Mechanism branch — after A1

M1 is a routing gate, not a second intervention. It reads A1's precommitted signature and decides
which mechanism, if any, A3 may target. A surviving explanation is not the same as a
mechanism-bearing result: common cause and readout both preserve the carrier's association while
denying it causal status.

| Branch | A1 signature | M1 status | A3 target | V2 implication |
| --- | --- | --- | --- | --- |
| **M1-C — Causal carrier** | Carrier effect at `A−`; association survives within `U`; carrier precedes assertion; `Y−` does not remove carrier | **PASS — carrier mechanism** | Carrier → external | Carrier-targeted V2 eligible |
| **M1-A — No carrier relation** | No carrier effect at `A−`; association vanishes given admission; admission effect positive | **PASS — no carrier relation; admission target** | Admission → external | Admission-targeted V2 eligible; no carrier V2 |
| **M1-CC — Shared cause** | No carrier effect; association persists given admission but vanishes within `U`; `Y−` does not remove carrier | **PASS — shared-cause target** | `U` → external | Shared-cause V2 eligible; no carrier V2 |
| **M1-RO — Readout only** | No carrier effect; `Y−` reduces carrier; assertion precedes carrier | **PASS — readout target; carrier demoted** | Assertion or admission → external, never carrier | No carrier-targeted V2 |
| **M1-X — Not identified** | Signatures conflict, `THIRD ROUTE PRESENT`, or shared cause and readout are not separated | **FAIL — no mechanism branch** | None | None; redesign only with a named defect |
| **M1-V — Void** | A manipulation, independence, pairing or determinism gate fails | **VOID** | None until the instrument is fixed | None |

Scientific verdicts are graph-level statements about `K` and `Y`: `CARRIER CAUSAL`, `NO CARRIER
RELATION`, `SHARED CAUSE` and `READOUT`. The `M1-*` labels are routing labels that map a verdict to an
A3 target; they are not a second taxonomy.

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
only to internal assertion? **Activation is the endpoint:** an external score difference is not
enough unless removing or blocking the selected structure removes the advantage. The G9 outcome
criteria and stage ledger are [`docs/G9-ACTIVATION-DESIGN.md`](docs/G9-ACTIVATION-DESIGN.md); they
do not authorise a G9 design.

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

### B0. Close cap-112 authorisation provenance — **CLOSED 2026-11-14**

**Issue.** The cap-112 run records cite a preparation-only quote: *"Write the dated cap-112
authorisation document for the comparator, Q1 and Q2…"* That is not a run authorisation. The
numerical results stand as recorded; their authorisation provenance does not.

**Work.** Choose and record one disposition: a corrected authorisation record, a disclosed
amendment, or an explicit reclassification. Do not rewrite the numerical results.

**Disposition (2026-11-14).** No run-authorising owner quote is recorded in the repository, and
none was invented. [`docs/CAP-112-PROVENANCE-DISPOSITION.md`](docs/CAP-112-PROVENANCE-DISPOSITION.md)
reclassifies `PRESENCE-COMPARATOR-112` (7 cells) and `PRESENCE-CAP-1-112` (25 cells) as
**provisional and not owner-authorised**. Their numbers, gates, statuses, seeds and artifacts are
unchanged; they are not confirmatory and may not be cited as owner-authorised results. The shared
grant document is annotated, the stale `not_evidence` text is replaced, and
`PRESENCE-CONSTRUCT-1-112` remains unrun under the preparation-only quote.

**Guard status.** `python -m benchmarks.authorisation_guard --check` still reports the two records.
That is intentional: the disposition is the roadmap's explicit-disposition branch, not a clean
guard. Making the guard accept a preparation-only quote would hide the defect it exists to catch.

**Exit gate — satisfied by the second branch.** The records carry an explicit, dated disposition
that explains the exception.

**What it licenses.** A clean provenance basis for any new confirmatory claim, subject to the
provisional label. It does not validate the underlying result and does not make the runs
confirmatory.

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
| V2 engineering | Only after M1 routes a mechanism branch: M1-C targets the carrier, M1-A targets admission, M1-CC targets `U`, and M1-RO targets assertion or admission. M1-X and M1-V license no V2. Current instrumentation, governance and measurement work remains 0.x; do not label it V2 or design V2 against a guessed mechanism. |
| Long-duration soak testing | Not active while the live study is paused. Requires an explicit restart decision. |
| Generation 9 self-modeling | Remains locked and unimplemented. Not a current roadmap item. Eligible only after X1 and **G9-A–D** all pass; passing them still requires a separate G9 design and owner decision. See [`docs/G9-ACTIVATION-DESIGN.md`](docs/G9-ACTIVATION-DESIGN.md). |

---

## Gates and recommended order

| Gate | Passes when | If it does not pass |
| --- | --- | --- |
| **G0 — Record** | Cap-112 provenance has a disposition and the suite is green | No new confirmatory claim; publication can still proceed |
| **G1 — Paths** | A0 is complete and the design uses admission and carrier as separately manipulable paths, with cross-path checks | A1 stays blocked; a design that cannot block either path returns `NOT IDENTIFIED` |
| **G2 — Discrimination** | A1 eliminates at least one of causal / common-cause / readout | No carrier claim; do not start V2 |
| **M1 — Mechanism branch** | A1's signature routes to M1-C, M1-CC or M1-RO | M1-X or M1-V: no A3, no V2; redesign only with a named defect |
| **G3 — External link** | A3 measures an endpoint against the M1-selected target | External advantage remains unestablished |
| **X1 — External activation** | A3 measures an external endpoint, ablation removes the advantage, and independent replication holds; G9-A–D remain separate conjunctive criteria | `EXTERNAL ACTIVATION NOT ESTABLISHED`; no G9 design |
| **G4 — V2** | M1 routes a mechanism-bearing branch and the target is named | Keep V2 deferred; continue 0.x work and do not substitute another diagnostic |
| **P1 — Publication** | Papers 01 and 02 have public deposits and DOIs | External value is delayed, not a scientific failure |

**Recommended order.**

1. **Now, in parallel:** A0 is complete and B0 is closed by the 2026-11-14 disposition; B1/B2
   (deposit and publish the existing record) remain.
2. **After A0:** the two-path design is registered. Implement and preregister its four cells, `Y−`
   arm and `U` strata before running any carrier intervention; an owner grant is still required.
3. **If granted:** run A2 in parallel or after A1; accept `VOID` as closure.
4. **After M1:** design A3 around the routed target. M1-CC and M1-RO never target the carrier.
5. **After A3:** read **X1**. If activation is not established, close the G8 → G9 path for the
   tested scope; do not design G9. If X1 passes, a G9 question still needs its own registered design
   and owner decision.
6. **Only after M1 and G4:** discuss V2 engineering, with the same target discipline. Until then,
   all current work remains 0.x.
7. **Opportunistically, with a decision rule:** short-group topology. Otherwise leave it deferred.

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
