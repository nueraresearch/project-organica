# Decision: the selection procedure for C8 is binding, not drafted

**ID:** `DECISION-A1-C8-SELECTION`

**Date:** 2026-11-15

**Status:** `ADOPTED BY OWNER 2026-11-15 — THE SELECTION PROCEDURE IS BINDING; S1–S7 IN FORCE; NOTHING FROZEN, NOTHING RUN`

**Decision owner:** Owner

**Signature and date:** 2026-11-15, adoption instructed in session; no personal name is recorded in this repository

**Scope:** the procedure by which C8's rows are chosen, and what happens when it is violated. It changes no threshold,
no denominator, no floor, no gate, no engine file and no seed; it freezes no manifest and authorises no cell. The floor,
the threshold and the endpoint cap are those adopted in [`DECISION-A1-C8-NMIN`](DECISION-A1-C8-NMIN.md) and are **not
restated here**.

---

## 1. The gap this closes

[`DECISION-A1-C8-NMIN`](DECISION-A1-C8-NMIN.md) made the *adjudication* half of the competence rule binding: which row is
scored, what makes it competent, the floor, the threshold and the cap. It says nothing about how rows are **chosen**.

Those clauses exist in [`A1-C2-C8-COMPETENCE-RULE`](A1-C2-C8-COMPETENCE-RULE.md), whose status line reads `DRAFT — FOR
OWNER DECISION; NOT IN FORCE`. The implemented selector,
[`benchmarks/a1_c8_target_selection_competent.py`](../benchmarks/a1_c8_target_selection_competent.py), follows them.

So the repository is currently in this state: **the procedure a run would follow is implemented and drafted, and nothing
in force requires either.** A future change to the selector would contradict a draft. The freeze acts cannot cite a
draft as binding language. That is the gap; it is recorded on the reading page
[`A1-COMPETENCE-RULE-IN-FORCE`](A1-COMPETENCE-RULE-IN-FORCE.md) under *What does not bind yet*.

## 2. What is adopted by this decision

**S1 — The pool.** Every C8 row is drawn from the competent pool. Competence is read at the recorded no-arm baseline,
per the *Unit* row of [`DECISION-A1-C8-NMIN`](DECISION-A1-C8-NMIN.md); no other predicate may be substituted at selection
time.

**S2 — The record, before the run.** The pool and the selected block are written into the freeze act, together with the
identity of the constructor that produced the block, before any cell runs. A block that exists only in a run log is not
selected; it is discovered.

**S3 — No fallback.** A row that fails competence is never added to reach a size. A seed that cannot field the floor under
the adopted cap is `VOID` under [`DECISION-A1-C8-NMIN`](DECISION-A1-C8-NMIN.md), not patched with a weaker row.

**S4 — No re-filtering.** After a run, the pool, the block, the competence predicate or the constructor may not be
re-derived to fit an observed outcome. Any such change voids C8 for that block.

**S5 — Disclosure.** The unfiltered selection is reported beside the filtered block, so the filter's effect is visible
rather than baked in. The observed row count per seed is reported with the result.

**S6 — Violation.** A breach of S2, S3 or S4 voids the block for C8 and is recorded as VOID with the breach named. It is
not a pass, not a warning, and not a reason to re-run until the procedure is satisfied by chance.

**S7 — What this changes.** This decision changes no engine file, threshold, floor, gate, seed or cell. Nothing
measurable moves. The
implemented selector already behaves this way; adoption makes the behaviour binding instead of customary, and gives the
freeze acts something in force to cite.

## 3. Why now, and not at the freeze

A freeze act is a checklist of what is fixed. If the selection procedure is not in force when the act is signed, the act
either cites a draft — which cannot bind — or restates the procedure in its own words, which creates a second place where
it is written. Both failures are already visible in this corpus, and the second is the one that produces drift. Adopting
the procedure now means each act cites one record.

## 4. Rejected alternatives

- **Leave it in the draft and cite the draft from the acts.** A draft marked NOT IN FORCE cannot make anything binding;
  citing it gives the appearance of a rule without the effect, which is worse than an acknowledged gap.
- **Restate the clauses inside each freeze act.** The acts would then define the procedure, and two acts could define it
  differently while both claiming to implement one rule.
- **Put the clauses into DECISION-A1-C8-NMIN by amendment.** That record is signed and about what is adjudicated, not how
  rows are chosen; amending it makes its status quote describe less than the document contains.
- **Treat the implementation as the rule.** Code is what runs, not what was agreed: a rule that lives only in code can be
  changed by a commit nobody reviewed as a decision.

## 5. What stays open

- Whether the constructor's *search* strategy — exact where feasible, bounded otherwise — belongs in force too. It is
  recorded in [`A1-C8-TARGET-SELECTION-COMPETENT`](A1-C8-TARGET-SELECTION-COMPETENT.md) and pinned by
  [`a1_c8_target_selection_competent.json`](a1_c8_target_selection_competent.json); this decision binds the *use* of its
  output, not its internal search.
- The freeze acts themselves, which remain unsigned and are the owner's separate act. They now carry the field list
  S2 needs, in `§2a` of [`A1-TARGET-FREEZE-ACT`](A1-TARGET-FREEZE-ACT.md) and
  [`A1-TARGET-FREEZE-ACT-N20`](A1-TARGET-FREEZE-ACT-N20.md). The N=20 act's rows are generated from the selection
  artifact, which records the pool's members as well as its size, and its S5 row points at
  [`A1-C8-SELECTION-DISCLOSURE`](A1-C8-SELECTION-DISCLOSURE.md), which reports the unfiltered block beside the
  competent one. **All ten rows are recorded**, so the act is complete apart from the owner's signature.

  **Note (measured 2026-11-15).** The C2-viability blocker (0/6 seeds on the unfiltered block) does not apply
  to the block this decision selects: [`A1-VIABILITY-LEVERS`](A1-VIABILITY-LEVERS.md) screens it at **0 failures in
  115 rows** against the same baseline, because the filter requires both an `A` carrier and a `K` path — which is what
  C2 needs to observe. That is a restatement of the filter's definition, not independent corroboration, and what it
  costs is the estimand: *representative eligible edges* become *baseline-competent edges*. Adopting this decision is
  therefore also the act that dissolves the 0/6 blocker, at that price. The N=4 act's
  rows are unrecorded because its block is not produced by the competence constructor.
- The C1 ceiling clause, [`DECISION-A1-C1-CEILING`](DECISION-A1-C1-CEILING.md), still pending.

## 6. How this record is checked

```bash
python -m benchmarks.a1_board --check          # its board row reads from this record's status line
python -m benchmarks.decision_graph --check    # the index, the counts and DISCOVERY are generated
python -m pytest tests/test_a1_freeze_fields.py -q   # S2's fields, held to one list across both acts
```

**Adopted 2026-11-15.** Its status line changed, the board row closed and the reading page's gap section lost this
entry, which is what the reading page's test checks. Nothing else follows: no threshold, floor, cap, seed or cell
moved, and no manifest is frozen.
