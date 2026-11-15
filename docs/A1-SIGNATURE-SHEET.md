# A1's three pending decisions — one sheet, three signatures

**ID:** `A1-SIGNATURE-SHEET-1`
**Date:** 2026-11-15
**Status:** `ALL THREE ADOPTED 2026-11-15; THE N=20 ACT SIGNED; NOTHING GRANTED, NOTHING RUN`

This sheet is an index, not a binding record. The binding text is each decision file; signing means filling its
**Decision owner** and **Signature and date** lines and replacing its `Status:` line. Withdrawing means writing
`WITHDRAWN` there with a date and a one-line reason, which the research registry already accepts as an outcome. This
sheet exists so all three can be dealt with in one pass instead of three.

| # | Record | Signing commits you to | Cost | If you decline |
| --- | --- | --- | --- | --- |
| D1 | [`DECISION-A1-C1-CEILING`](DECISION-A1-C1-CEILING.md) | the `>64` clause governs the candidate-plan count it names, not the recorded cell row | one clause of one binding record amended by dated note | five of six seeds read `VOID — design inconsistency` before retention is looked at |
| D2 | [`DECISION-A1-C8-SELECTION`](DECISION-A1-C8-SELECTION.md) | the implemented selection procedure becomes binding (S1–S7) | nothing measurable moves; code already behaves this way | the acts cite a draft that cannot bind, or restate the procedure and drift |
| D3 | [`DECISION-A1-COMPETENT-ESTIMAND`](DECISION-A1-COMPETENT-ESTIMAND-1) ([file](DECISION-A1-COMPETENT-ESTIMAND.md)) | targets come from the baseline-competent population; the estimand becomes conditional | the claim narrows to a conditioned population; two seeds get zero C8 tolerance | every seed is C2-VOID before any treatment effect is read |

---

## D1 — The C1 ceiling is the preplanned universe, not the number 64

**Record:** `DECISION-A1-C1-CEILING` · **Status:** `ADOPTED BY OWNER 2026-11-15`

**What you commit to.** The `>64` clause in `A1-PATH-A-C1-RULE-1` is narrowed to the quantity its own table names — the
63–64 **candidate-plan count** — and stops governing the recorded cell row. The top of the band is then carried by a
comparison, not a constant: the scored denominator must equal the preplanned universe, restated from the pre-treatment
baseline artifact before either act is signed.

**Why it is needed.** `DECISION-A1-C1-DENOMINATOR-1`, adopted a day later, changed the denominator's unit to *every
recorded paired-control row* and left the ceiling on the old scale. Measured on the adopted block, the observed minima
are **79 / 64 / 79 / 74 / 72 / 74** against a ceiling of 64: read literally, five seeds are VOID before anything is
scored. No row was added — the universe was 112 edges per seed all along.

**Cost.** One clause of one binding record, amended by dated note rather than deletion. The threshold (0.95), the 60-row
floor, the three-loss band and the C4 ceiling are untouched. Nothing is re-scored.

**If you decline.** Five of six seeds are `VOID — design inconsistency` on arrival, and the C1 branch stays closed at the
bottom only (floor at 60) with no honest top. It also has to be restated in the N=20 act, which is where a competent
block can live.

**Independent of D2 and D3.** The universe is selection-invariant: C1 counts every recorded row of the cell stream,
targets included, so 79 / 64 / 79 / 74 / 72 / 74 is a property of the 112-row universe and the competent selection
reproduces it exactly.

**Signed 2026-11-15.** Status line: `ADOPTED BY OWNER 2026-11-15 — THE 63–64 CLAUSE GOVERNS THE CANDIDATE-PLAN
COUNT; THE CEILING IS THE PREPLANNED UNIVERSE; IN FORCE`.

---

## D2 — The selection procedure is binding, not drafted

**Record:** `DECISION-A1-C8-SELECTION` · **Status:** `ADOPTED BY OWNER 2026-11-15`

**What you commit to.** Seven clauses on **how** C8's rows are chosen: the pool is the competent pool (S1); pool, block
and constructor identity are recorded in the act before any cell (S2); no fallback row to reach a size (S3); no
re-filtering after the outcome (S4); the unfiltered selection is disclosed beside the filtered one (S5); a breach of
S2–S4 voids the block (S6); and nothing measurable moves (S7).

**Why it is needed.** `DECISION-A1-C8-NMIN` bound the *adjudication* half of the competence rule and said nothing about
selection. The clauses exist only in `A1-C2-C8-COMPETENCE-RULE`, whose status line reads `DRAFT — NOT IN FORCE`, and the
implemented selector already follows them. So a run would follow a procedure that nothing in force requires, and the
acts cannot cite a draft as binding language.

**Cost.** Nearly none, and that is the point: the selector already behaves this way, and the S5 disclosure already
exists (`A1-C8-SELECTION-DISCLOSURE`, six seeds, generated). Adoption makes behaviour binding instead of customary.
The threshold, floor, cap and seeds are not restated — they stay in `DECISION-A1-C8-NMIN`.

**If you decline.** The acts either cite a draft that cannot bind, or restate the procedure in their own words and
create a second place where the rule is written — the drift failure this corpus has already paid for twice. The
procedure stays changeable by any commit that nobody reviews as a decision.

**Signed 2026-11-15.** Status line: `ADOPTED BY OWNER 2026-11-15 — THE SELECTION PROCEDURE IS BINDING; S1–S7 IN
FORCE; NOTHING FROZEN, NOTHING RUN`.

---

## D3 — Targets are drawn from the baseline-competent population

**Record:** `DECISION-A1-COMPETENT-ESTIMAND` (`DECISION-A1-COMPETENT-ESTIMAND-1`) · **Status:** `ADOPTED BY OWNER 2026-11-15`

**What you commit to.** An edge is an admissible target only if the no-arm A+K+ replay records **both** an `A` carrier and
a `K` path for it. The estimand becomes conditional — *the pre-37 cycle-membership directed-edge effect, conditional on
both paths being present at baseline* — and the representative-eligible wording is retired from the acts and from every
record that restates it. One sentence of `A1-PATH-A-C1-RULE-1` is amended by dated note; its C1 rule and 60-row floor
stand. C4's clause 1 is restated to match the new row counts. Operative sizes are the ones already adopted: **20, 17, 20,
20, 18, 20**.

**Why it is needed.** Under C8's adopted rule a block containing one non-competent row is VOID, not partial-scored. The
current representative selection has **58 of 120** competent rows and **15** with neither path, so **0 of 6** seeds can
satisfy C2. `A1-VIABILITY-LEVERS` prices the alternatives and closes them: raising `N` lowers the chance of a viable
seed, a fresh block needs about 10⁻³⁴, and weakening C2 still fails on those 15 rows.

**Cost — the real one.** The claim narrows. A positive C2 result would be about edges that carried both paths *before*
treatment, not about representative eligible edges, and that cannot be argued back afterwards. Two seeds,
`20740102` (17) and `20740105` (18), get **zero** C8 tolerance, because `floor(0.05 × 17)` and `floor(0.05 × 18)` are
both 0 while the twenty-row seeds admit one. And 177 of 382 eligible rows become ineligible as targets.

**If you decline.** The N=20 act cannot be signed into anything runnable: it would freeze 120 target rows that fail C2
on every seed for reasons that have nothing to do with the treatment. Declining does not keep the experiment
representative — it keeps it unmeasurable.

**What adopting triggers.** The current N=20 act is bound to `a1_c8_target_selection.json` (the representative twenty per
seed), so adopting D3 **invalidates its block**. The act must be re-issued against
`a1_c8_target_selection_competent.json` — tables, digests and the S5 pointer regenerated — before it can be signed. That
re-issue is mechanical and is not a change to any threshold.

**Also settled by either outcome:** the N=4 act should not be signed. Four targets per seed can never reach
`N_min = 17`, and that incompatibility comes from C8's own adopted rule, not from this decision.

**Signed 2026-11-15.** Status line: `ADOPTED BY OWNER 2026-11-15 — PATH A TARGETS ARE BASELINE-COMPETENT; THE
ESTIMAND IS CONDITIONAL; NOT FROZEN, NOT RUN`.

---

## Order, and what a full pass produces

**D1 is independent** and can be signed in any order. **D3 depends on D2 in practice**: D3's filter is only binding if
the procedure that selects with it is in force, so signing D3 while D2 stays a draft leaves the block governed by
custom. The clean order is D1, D2, D3.

A full pass produces: a reconciled C1 band, a binding selection procedure, a conditional estimand, and a **re-issuance
of the N=20 act on the competent block**. After that the act has one remaining act — its signature — and then a grant.
None of the three touches the engine, the threshold, the floor, the seeds or the cap; none freezes a target, issues a
grant or runs a cell.

**My recommendation, if you want one:** D1 and D2 are reconciliation — they write down what is already true, and
declining either leaves a VOID or a draft where a rule should be. D3 is the only one that changes what the experiment
means, and the honest summary is that it trades breadth for measurability. I would sign D1 and D2 without reservation
and sign D3 with the loss stated out loud.

**Not evidence:** An index of three pending records. It decides nothing, freezes nothing, grants nothing and runs no
cell.
