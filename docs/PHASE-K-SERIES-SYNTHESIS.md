# The K series — collation and reading (2026-11-19)

> **What this document is.** One place that collects every K-series record,
> separates what is admissible from what is not, and states the development
> decisions the data supports. It adds no evidence, runs no cell, changes no
> engine, and does not re-score the campaign. The Phase K verdict stands in
> [`phase_k_results.md`](phase_k_results.md); the K2 block status stands in
> [`K2-BLOCK-RESULT.md`](K2-BLOCK-RESULT.md). Where this document and a run
> record disagree, the run record wins.

**Status: SYNTHESIS. No new experiment. No architecture change. No V2.**

---

## 1. The answer in one paragraph

The K series is finished as a search. Phase K ruled out three task families
against the strongest simple baseline, with clean intervals and empty
mechanism ablations; that verdict is admissible and unchanged. The one K2
intervention block built afterwards is **VOID** — its own validity gate fired
on every seed — so it contributes no evidence and cannot confirm, refute or
retire the constraint. The open question is therefore not *what does the block
show* but *is a repaired block worth running*, and the registered arithmetic
says no: even a pass under the rule written before the block leaves a large
loss to the baseline, so neither a pass nor a fail changes the architecture.
Recommendation: close the K search, retire the K2 constraint row without a
second block, adopt a same-build rule for registered comparators, and spend
the next development cycle on the already-authorised V2 path rather than on a
seventh task family.

---

## 2. What exists

| Record | Date | Build | What it contributes | Admissible as evidence? |
|---|---|---|---|---|
| Phase K campaign [`phase_k_results.json`](phase_k_results.json) | 2026-10-24 | engine `0.9.0`, tree `25d9e50` | K0 control, endpoint ceiling audit, and K1/K2/K3 over ten seeds each | **Yes** — the three family verdicts and the control |
| Mechanism erratum [`PHASE-K-MECHANISM-ERRATUM.md`](PHASE-K-MECHANISM-ERRATUM.md) | 2026-11-16 | document and code only | the frozen artifact's `mechanism_implicated` field is inverted; intervals and prose govern | correction, not evidence |
| K3 root cause [`phase_k_diagnose.py`](../benchmarks/phase_k_diagnose.py) | campaign-era | engine `0.9.0` | per-cycle check, under-read check, and the arrival-order × strength 2×2 | **Yes** — a diagnostic of the zero |
| K2 build passport [`K2-BUILD-PASSPORT.md`](K2-BUILD-PASSPORT.md) | 2026-11-17 | none | the frozen build contract and refusal matrix; no cell | n/a |
| K2 block [`phase_k_k2_results.json`](phase_k_k2_results.json) | 2026-11-18 | engine `0.15.0`, tree `d4eeefc` | K1 + K2 over ten seeds, 300 cycles | **No** — `VOID`, no criterion read |

The campaign artifact is frozen and included in the V1 freeze; its provenance
is recorded separately in [`PHASE-K-PROVENANCE.md`](PHASE-K-PROVENANCE.md).
The block is a separate, later build and is not a replication of the campaign
on the same bytes — that distinction is the subject of §4.

---

## 3. The campaign verdict, and what it does and does not rest on

<!-- BEGIN K SUMMARY: generated from docs/phase_k_results.json by benchmarks/k_series_collate.py; do not edit by hand -->
| Family | Organica | Best simple baseline | Paired difference | 98.33% interval | Verdict |
|---|---:|---:|---:|---|---|
| **K1** — incremental world modeling | 0.5923 | 0.9360 | -0.3437 | [-0.3773, -0.3123] | **REVERSED** |
| **K2** — belief revision | 0.4111 | 0.9846 | -0.5735 | [-0.6162, -0.5309] | **REVERSED** |
| **K3** — longitudinal integration | 0.0000 | 0.8578 | -0.8578 | [-0.8598, -0.8571] | **REVERSED** |
<!-- END K SUMMARY -->

The instrument audits passed before the campaign ran: the K0 control
reproduced Organica's known loss on the Phase H held-out task, and the
endpoint ceiling check scored a synthetic perfect model at 1.0 on all three
families. The verdicts survive eight alternative bootstrap seeds and both
leave-one-out checks; none is an artifact of the published interval's
bootstrap seed.

### 3.1 The matched ablations

<!-- BEGIN K ABLATION: generated from docs/phase_k_results.json by benchmarks/k_series_collate.py; do not edit by hand -->
| Ablation | Ablated arm (mean) | Organica − ablation | Read |
|---|---:|---|---|
| `NO_QUESTIONS` (K1) | 0.6018 | -0.0095 [-0.0328, +0.0140] | contains zero — not established |
| `NO_FALSIFICATION` (K2) | 0.3870 | +0.0241 [-0.0048, +0.0495] | contains zero — not established |
| `NO_DREAMS` (K3) | 0.0000 | +0.0000 [+0.0000, +0.0000] | contains zero — not established |
<!-- END K ABLATION -->

### 3.2 Four claims, at the status the record supports

**(a) Organica 1 has no comparative advantage on these three families.**
*Status: reversed, within this engine, world family and support axis.* The
intervals are wholly below zero for all three families, and the losses are
large: K2's baseline reaches 1.000 on eight of ten seeds, K3's 0.857 on nine
of ten. This is not a near-tie that more seeds could flip.

**(b) The three matched mechanisms are not shown to carry their tasks.**
*Status: not established / not measured.* This is deliberately weaker than
"the mechanisms are inert". Each ablation interval contains zero, which
neither establishes nor refutes a mechanism effect at this sample size, and
the matched ablations were run on tasks where the organism was already losing
by 0.34–0.86. A mechanism cannot show an effect when the outcome is dominated
by something else. The frozen artifact's inverted `mechanism_implicated`
field is not usable; read the intervals.

**(c) K3's zero is a priority/capacity exclusion under the frozen
configuration.** *Status: supported within the tested scope.* The late
structure appears in zero of 150 cycles, every candidate type except
`anomaly` mentions zero late tags, and the 2×2 shows the late group is
incorporated only when it is strictly stronger than the group that arrived
first. With the protocol's weight-3 scaffold against weight-1 late entities,
it is never incorporated. This is a result about Organica 1's bounded belief
pool, not about developmental architectures in general.

**(d) The K2 intervention changes the outcome.** *Status: not measured.* The
only attempt is `VOID`. It is not a null result, not a failed replication and
not a confirmation, and no criterion from it may be quoted.

---

## 4. The K2 block: what the week added, and what it did not

The block ran 20 cells under grant `K2-BLOCK-20261118-A`, wrote 20 of 20
checkpoint rows, closed its one lease and completed its one marker on the
pinned `0.15.0` engine. Every structural
check passed. Then the block's own gate returned:

- verdict `VOID`;
- failed gate `G4_no_pre_boundary_demotions`;
- `criteria_read: false`;
- `confirmed_families: []`.

Two build findings are recorded in [`K2-BLOCK-RESULT.md`](K2-BLOCK-RESULT.md):

1. **The gate cannot pass on this build.** The treatment calls the demotion
   helper on every cycle including cycles 1–199, and the helper increments
   `pre_boundary_demotions` for every pre-boundary association it visits even
   though it appends the record unchanged. The counts are 22,007 to 23,837 per
   K2 seed, so G4 fires on every seed. No candidate was actually demoted
   before the boundary; the counter counts the attempt, not the effect.
2. **The K1 comparator is not a same-build measurement.** Its registered
   pre-value is -0.343658; the block's ten K1 cells measured -0.623961, an
   absolute change of 0.280303 against the registration's 0.05 limit. A direct
   rerun of seed 20261023 gave the identical 96-pair set and the same F1 for
   both the shipped `SleepService` and the no-op, so the drift is the engine
   build: the registered values come from the Phase K artifact committed
   2026-10-24, before the `0.15.0` pin.

**What the week bought:** a build defect and a methodological defect. Both are
real and both were found before either could be cited as science. **What it
did not buy:** evidence. Per rule 31, a block that fails its own gate measured
nothing about the engine, and citing it as a failed replication would convert
an inadmissible run into evidence.

**Why the dry run missed it.** The gate suite exercised the helper at the
boundary and a direct pre-boundary fixture call; it never ran the service's
own cycles 1–199. A frozen harness's dry run has to execute the treatment's
own path across the boundary, not only its pure functions. That is a process
finding about this repository, not about K2.

---

## 5. What the K data does and does not license

**It supports:**

- adding K1, K2 and K3 to the negative-results map — three more families
  excluded under the pre-committed H2 outcome;
- the statement that the three tested mechanisms are *not shown* to be
  load-bearing on these endpoints;
- the K3 capacity/priority characterization, within the frozen configuration;
- a same-build requirement for every registered comparator, which is the one
  general lesson the block produced.

**It does not support:**

- any claim for or against the K2 intervention — the block is `VOID`;
- any claim about developmental architectures generally, or about V2;
- any capability, transfer or comparative-advantage claim;
- the statement that the tested mechanisms are inert;
- reopening Phase K's verdicts.

---

## 6. Decisions this supports

These are owner decisions. The recommendation is the reading of the record;
none of it is in force by this document.

| # | Decision | What the record says | Recommendation | What it needs |
|---|---|---|---|---|
| D1 | **Close the K search.** No K4 or K5 family. | Six task families are negative; the ablations are null; another family would be the seventh entry in a list of losses. | **Yes.** The search's premise — that one of these three mechanisms is load-bearing — was tested and not supported. | an owner record naming H2 as the terminal outcome of the search |
| D2 | **Retire the K2 constraint row without a second block.** | The only attempt is `VOID`, so the intervention has no pass/fail; the campaign's K2 result is a clean family loss. A repaired block's best case under the registered rule is a gap of -0.4735 — still a large loss — so neither PASS nor FAIL changes the architecture. | **Yes, with the basis stated.** Retire as *intervention not worth running*, on the `VOID` attempt plus the campaign's K2 result, and amend the ledger's retirement predicate rather than pretending the rule is met. | one decision record and a ledger validator change; leaving the row `in-test` blocks any new constraint row |
| D3 | **Do not run the remaining K diagnostics now.** K1 forced selection, K3 forced service, and the attribution positive control stay recorded and unrun. | The first two are mechanism probes on families that lost by 0.34 and 0.86; the third would make the null ablations interpretable but changes no engine decision today. | **Yes.** Revisit the positive control only if a future ablation is going to carry an architecture decision. | no run; the rows stay as history |
| D4 | **Adopt a same-build rule for registered comparators.** | The K2 registration's K1 pre-value and baseline gap came from a pre-`0.15.0` artifact; the gate compared declared values to constants and could not see the provenance. | **Yes.** Generalise rule 31's same-build control from engine-effect claims to every pre-registered comparator. | an owner record; a check can follow, but the rule is the decision |
| D5 | **Spend the next development cycle on the authorised V2 path.** | The K data produces no capability lead and no architecture change; the first V2 cell is signed, its seeds are spent, and it has not run. | **Yes.** Do not substitute a seventh K family for the item already authorised. | run the signed cell under `DECISION-V2-FIRST-CELL`; no new K work |

**Why D2 is not merely bookkeeping.** The K2 row was the only `in-test` row in
the constraint ledger, and the build passport states that no new constraint
row may be added until K2's result and architectural decision exist. Leaving
the row open therefore blocks the next constraint from being registered. Some
decision is required regardless of which way it goes; it has since been taken,
and the K1 row is now `in-test`.

---

## 7. If the owner prefers to repair K2 instead

The repair is bounded and known: make the pre-boundary path a genuine no-op
(or count only actual demotions), re-derive the K1 comparator on the same
build, amend the registration, and run one fresh dated block. That is a day of
work plus a governance cycle, and it would produce a readable mechanism
result.

It would still not produce a comparative advantage. The registration's PASS
threshold is an improvement of 0.10 over the -0.5735 baseline gap, so the best
case it can return is a gap of **-0.4735**: the organism would still be far
behind the strongest simple baseline on the family. A PASS would be a
statement about how much of the loss the pre-boundary-priority hypothesis
explains, not a statement that belief revision works. That is why D2
recommends against it: a diagnostic whose best case leaves the development
decision unchanged fails the rule this repository already applies to
diagnostics.

---

## 8. Provenance and how this page is checked

- The two tables in §3 are **generated**, not transcribed, from
  [`phase_k_results.json`](phase_k_results.json) by
  [`benchmarks/k_series_collate.py`](../benchmarks/k_series_collate.py).
- `python -m benchmarks.k_series_collate --check` re-renders both tables and
  fails on any drift; it also checks the block's verdict, failed gate,
  `criteria_read` value, the K1 registered/live/absolute figures, the
  pre-boundary count range and the D2 arithmetic against the artifacts and
  the constraint registration. `--self-test` proves the check can reject a
  tampered copy. `--write` regenerates the two regions.
- It adds no artifact, no seed, no grant and no engine stamp, and it is not a
  result record.
- The build replication is a separate artifact and does not alter this page's
  tables or verdicts: on `0.15.0`, with the same ten seeds, the three families
  returned the same `REVERSED` verdicts
  ([`PHASE-K-REPLICATION-0.15.0-RESULT.md`](PHASE-K-REPLICATION-0.15.0-RESULT.md)).
- The V2 first cell recommended in §6 ran on 2026-11-19 and returned
  `REVERSAL` (maintained membership cost `0.004199` nats); the K disposition
  is unchanged and no V2 build follows.
- The K2 disposition was executed on 2026-11-19: K2 is retired as an invalid
  attempt (untested, not refuted) under
  [`CONSTRAINT-K2-RETIREMENT.md`](CONSTRAINT-K2-RETIREMENT.md), and the K1
  forced-selection arm is the ledger's `in-test` row. No cell has run.
