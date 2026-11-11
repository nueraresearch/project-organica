# Decision brief — the Layer-1 prediction cap

**Status: BRIEFING FOR AN OWNER DECISION (2026-11-10). No decision is taken by this document, and nothing here is in force.**
**Decision owner:** the project owner, alone. **Required by:** `AGENTS.md` rule 2 (a cognition change needs an explicit
recorded decision) and rule 30 (a diagnostic is worth its cost only if a named decision follows from its outcome).
**Record:** `docs/presence_cap_prereg.json` (`PRESENCE-CAP-1`, `FROZEN, RUN`, verdict `CAP LIMITING`, licensed 2026-11-10).
**Evidence:** `docs/presence_cap_run.json` (24 cells plus the witness) and `docs/PRESENCE-CAP-RESULT.md`. Every figure below
is produced from that artifact by the script that wrote this page, and `tests/test_cap_decision_brief.py` fails if one drifts.

---

## 1. Two questions, not one

The block was registered to answer one question. The Q4 diagnosis of the observer showed that it is really two, and that
they can be decided separately:

| # | Question | State |
| --- | --- | --- |
| 1 | **What should the constant mean?** Today one integer is both the total budget and the rule that splits it. | Not decided. §2 sets out the split. |
| 2 | **What should the budget be?** 40, 80 or 112. | Not decided. §4–§6 lay out the evidence and the trade. |

Collapsing the two is what produced the Q3 defect: an instrument read the *name*, assumed "at most N served", lifted the
value, and changed the composition of what was served instead of only its length. A name that hides an allocation rule will
keep producing that error, whichever level is chosen.

## 2. The first question: the constant is misnamed

`MAX_PREDICTIONS` is read twice inside one function. `half_cap = MAX_PREDICTIONS // 2` fixes the guaranteed transition
floor; the remainder, `MAX_PREDICTIONS - len(selected_transitions)`, becomes the cooccurrence budget; and the same value is
the final cut. The floor is not a fixed allocation: if cooccurrence candidates do not fill the remainder, the engine
backfills the unused slots with further transitions. At 40 the engine guarantees 20 transitions and seats up to 20
cooccurrences; at 112 it guarantees 56 transitions and seats up to 56 cooccurrences, and the band arm's 112 cells actually
served 64-69 transitions. The constant is therefore not "how many predictions" — it is a **selection-budget policy**:
total budget and a transition floor in a single integer.

**Reconciliation, 2026-11-11.** The 56 is a guaranteed floor, not the served transition count. BAND-1 observed 64-69
transitions at 112, and its exact-56 gate was a gate defect; BAND-2 freezes the corrected `>= 56` condition. This changes
no cap, no Q2 verdict, and no measured row in this brief.

Two consequences follow. A change to the number changes *which kinds* of candidates occupy the budget, not only how many
are returned. And nobody — reader, instrument or protocol — can change the total without also changing the split.

**Option E — split the constant, values linked.** Introduce explicit names for the returned-prediction budget and the two
allocation budgets, initialised so the shipped behaviour is bit-identical (returned 40, transitions 20, cooccurrences 20 at
the shipped setting, or 80/40/40 under option B, and so on). This changes no behaviour at linked values and makes the
coupling explicit, nameable and testable. It does not require choosing a level, and choosing a level does not require it.

**What a split would require.** It is an engine edit under rules 2 and 12: a package version bump, a changelog entry, a
re-pin of `docs/engine_pin.json`, and a **behaviour-preserving proof**. The block canaries added on 2026-11-10 are the
vehicle: a split that changes no behaviour must leave all four recorded digests unchanged, including the cap and construct
cells that exercise the allocation. That is the same standard `tests/test_substrate_equivalence.py` sets for substrate
changes.

**Why split before raising.** Today a cap change moves total budget, transition allocation, cooccurrence allocation,
candidate composition and downstream assertion in one step. Splitting first isolates the total from the split, so a later
level study is interpretable rather than confounded with a rename.

## 3. What the verdict is, and what it is not

`CAP LIMITING`: raising only the Layer-1 prediction cap adds asserted world edges at the declared bar. World, presence and
every non-cap parameter were held fixed, so the reading is about **selection capacity**, not about the organism.

It is **not** a capability, transfer or generalization claim. It is **not** a claim that 112 is optimal. It is **not** a
retention, revision or prediction-quality result: no cell scored behaviour.

## 4. The evidence

Six fresh seeds, 120 cycles each (seed 20611405 ran 89 windows), the Gate-13 compositional world with 112 derivable edges,
engine 0.14.0 unchanged, one manipulated variable. Asserted world edges by cap:

| Seed | cap 40 | cap 80 | cap 112 | uncapped | gain 40 → 112 |
| --- | --- | --- | --- | --- | --- |
| 20611401 | 38 | 42 | 52 | 112 | +14 |
| 20611402 | 48 | 51 | 63 | 112 | +15 |
| 20611403 | 32 | 44 | 62 | 112 | +30 |
| 20611404 | 48 | 48 | 62 | 112 | +14 |
| 20611405 | 29 | 30 | 43 | 112 | +14 |
| 20611406 | 43 | 44 | 51 | 112 | +8 |

- mean paired gain at 112: **15.833333** asserted world edges
- 95% paired lower bound: **8.081175**, against a pre-committed bar of **10** — the bar is cleared
- seeds with a positive gain: **6 of 6**; flat seeds: **0**; seeds where reach changed: **6 of 6**
- reach-limited ceiling: **28.5**; gain over the ceiling: **0.555556**
- witness, seed 20261100 at cap 40: 112 present, 40 asserted, witness fingerprint: **db2b1a46db2f4b7f** — the cap-40 arm reproduces the published audit row, so it *is* the shipped engine

**The midpoint was measured, not judged:** at cap 80 the mean asserted world edges over the cap-40 arm is 3.50,
positive on 5 of 6 seeds; at cap 112 it is 15.83. The pre-committed bar and the paired interval belong to
112 — the record names 112 as the adoptable comparison level — and no interval was registered for 80. The 80 arm's figure is
therefore descriptive: usable for choosing, not a passed criterion.

The uncapped arm asserts every present world edge, so the gain is bounded by reach once the cap exceeds the world's size —
which is why 112, not the ceiling, is the adoptable level. The gain is also uneven (seed 20611403 gains
30, seed 20611406 gains 8), which is why the decision rests on a paired lower bound
rather than on the mean.

## 5. Beneficial is not necessary — 112 against 80

- **112 is the scientifically clean choice.** It is the level the protocol fixed in advance, it cleared the pre-committed
  bar (mean 15.833, lower bound 8.081 against 10), it matches the world's edge
  count, and it is the easiest to defend later because nothing about it was chosen after the data arrived.
- **80 is the engineering choice.** It preserves the doubling ladder the engine has actually moved along (20 → 40 → 80),
  it is a smaller cognition jump, and it buys operational experience before a larger one. Its measured mean gain is
  3.50 asserted world edges, roughly a fifth of 112's.
- **What the block proved is that 112 is beneficial and sufficient to clear its bar — not that 112 is necessary.** Necessity
  would require a criterion judged at 80 that 80 fails and 112 passes; this block has no such criterion, and inventing one
  now would be scoring the protocol after the fact.
- So the level is a judgement about risk and interpretability, not an evidence gap. Whichever is chosen, say which one it
  is buying: the pre-registered comparison, or the ladder step.

## 6. What raising the budget would actually change

At 40 the guarantee is 20 transitions plus up to 20 cooccurrences; at 80 it is 40 plus up to 40; at 112 it is 56 plus up
to 56, with transition backfill when cooccurrences are scarce (the band arm observed 64-69 transitions at 112). Any of B
or C therefore changes composition as well as length — which is the treatment the block measured, and the reason option E
exists.

Consequences of choosing B or C:

- **It is a cognition change.** Frozen engine files (rule 12) need a version bump, a changelog entry under that version and
  a re-pin, with `python -m benchmarks.engine_pin --check` and `tests/test_versioning.py` green. A passing block never
  promotes itself.
- **The canaries must agree.** A deliberate level change re-records `docs/block_canaries.json`; an *unintended* digest change
  fails the suite.
- **It is not a behaviour result.** No prediction, retention or transfer claim may be attached to the new cap without its
  own pre-registered cells.
- **Downstream measurements move.** Artifacts that quote cap 40 as shipped — the Stage B scan, the audit row, the conversion
  blocks — need rebuilding under the new pin. That cost is real and belongs in the decision, not in a later surprise.
- **The uncapped arm must not ship.** It is a control, and it removes the cooccurrence half of the split entirely.

## 7. What the decision does not cover

One world family, six seeds, 120 cycles, one endpoint (`A_W`), one engine build. It says nothing about worlds of other sizes,
about whether 112 generalizes, or about the rate at which admitted edges assert. It cannot be pooled with Q1 or Q3 and does
not re-score Gate 13, the ladder or the audit.

## 8. What would withdraw the reading

Per the record: the cap-40 witness stops reproducing the audit row; the treatment class gains a second override; the engine
pin moves without a version bump; or a later block finds the cap-40 control was not the shipped build. A withdrawn reading is
recorded, not deleted.

## 9. The decision

Two decisions, which may be taken in either order but should be recorded separately:

**Question 1 — the constant's semantics.**
- **E0 — leave it as one integer.** The coupling stays implicit and the name keeps misleading instruments.
- **E1 — split it, values linked** (behaviour-identical; proven by unchanged canary digests; **in force, landed in 0.14.0** through `docs/engine_lineage.json`).

**Question 2 — the budget.**
- **A — keep 40.** **B — raise to 80.** **C — raise to 112 (chosen 2026-11-11; see `docs/DECISION-CAP-LEVEL.md`).** **D — something else**, which needs its own preregistration.

### Sequencing E1 and a level change

The two decisions are separable, but they cannot be *proven* together, and the difference matters:

- **E1 at the shipped values** (returned 40, transitions 20, cooccurrences 20) is behaviour-preserving. Its acceptance
  test is that all four canary digests in `docs/block_canaries.json` stay unchanged — the split renamed and structured the
  policy without moving a single served row.
- **A level change re-records those digests.** That is correct and deliberate, but it destroys the split's proof: once the
  digest moves, nothing in the record distinguishes "the split changed behaviour" from "the level did".
- So an owner who wants both should record **E1 first**, land it with the digests unchanged, then record the level as its
  own decision and re-record the digests, attributing the change to the level. The reverse order is not equivalent:
  raising first and splitting afterwards leaves the split unproven for the same reason.
- Recording "E1+B" as one decision, with one version bump, and describing the result as behaviour-preserving would be the
  error this rule exists to prevent. Behaviour-preserving is a claim about one change at a time.

Recording a choice requires the option, the date, a one-line rationale, and the version the change lands in. Both questions
now have that sentence: Question 1 is in force in 0.14.0, carried to the shipped engine by `docs/engine_lineage.json`
without restamping a frozen block, and Question 2 is decided for 0.15.0 but not yet in force, because the cap-40
comparator and the three frozen blocks cannot run under 112.

| Decision | Date | Rationale | Lands in version |
| --- | --- | --- | --- |
| E1 — split the constant, values linked | 2026-11-10 | The Q3 `OBSERVER NOT NEUTRAL` verdict arose from the design: the name described a capacity while the engine spent an allocation, so an instrument reading it literally served a different window. The split is behaviour-identical, and the four block-canary digests staying unchanged is the proof. | in force in 0.14.0 (unreleased), carried to the shipped engine by `docs/engine_lineage.json` |
| C — raise to 112 | 2026-11-11 | `CAP LIMITING` licenses a cap change, and 112 is the level the protocol fixed in advance: mean paired gain 15.833333, 95% lower bound 8.081175 against a bar of 10, positive on 6 of 6 seeds, matching the world's 112 edges. Beneficial, not necessary, and chosen for the pre-registered comparison rather than the ladder step. | 0.15.0 (unreleased), not in force — the cap-40 comparator and the three frozen blocks must be re-registered under 112 and need an owner grant |
