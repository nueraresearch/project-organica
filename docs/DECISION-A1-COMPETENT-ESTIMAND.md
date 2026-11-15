# Decision: Path A targets are drawn from the baseline-competent population

**ID:** `DECISION-A1-COMPETENT-ESTIMAND-1`

**Date:** 2026-11-15

**Status:** `PENDING — FOR OWNER ADOPTION; NOT IN FORCE; NO FREEZE, NO GRANT, NO RUN`

**Decision owner:** ____________________

**Signature and date:** ____________________

**Scope:** the target population, the estimand's wording, and the C4 multiplicity restatement that follows from the
row counts. Changes no threshold, no endpoint cap, no gate and no seed. Freezes nothing and runs nothing.

---

## 1. The question

Path A's estimand is recorded in both freeze acts as *"the representative eligible pre-37 cycle-membership
directed-edge effect"*. `DECISION-A1-C8-NMIN-1` adopted a **competent directed target row** as C8's unit — "both
baseline paths A and K present, no-arm A+K+ replay" — while its scope was C8's rule alone. The two cannot both hold
of one target set, and the tree has now measured what that costs:

| Design | Targets | Competent | Seeds with a clean block |
| --- | ---: | ---: | ---: |
| N=4 | 24 | 12 | **0 of 6** |
| N=20 | 120 | 58 | **0 of 6** |

Under C8's adopted rule a block containing any non-competent row is VOID rather than partial-scored, so the current
selections would VOID on every seed — not for anything the treatment did, but because the selection rule never asked
whether either path was present. The pool is not the constraint: **27–40 competent rows per seed** against 20 needed.

## 2. Decision

**The target population is baseline-competent.** An edge is an admissible target only when the no-arm A+K+ replay
records both an `A` carrier and a `K` path for it. Selection is otherwise unchanged: the same 36-cycle candidate
universe, the same positive-strength and cycle-membership eligibility, the same hash order, and the same endpoint cap
of 3 edges per tag.

**The estimand becomes conditional.** Path A estimates *the pre-37 cycle-membership directed-edge effect, conditional
on both paths being present in the no-arm baseline.* The unconditional, representative-eligible wording is retired
from the freeze acts and from any record that restates it.

**This amends one sentence of `A1-PATH-A-C1-RULE-1`, and nothing else in it.** That record fixes the estimand *and*
the C1 acceptance rule; its §1 states the estimand as "the representative eligible pre-37 cycle-membership
directed-edge effect". Adopting this decision replaces that sentence with the conditional wording above, as a dated
amendment note in that record rather than a deletion, while its C1 acceptance rule, its 60-row floor and its other
clauses remain binding. The index cannot express a partial supersession — `superseded_by` names a whole record — so
the amendment is carried here, in that record's note, and on the checklist.

**Operative sizes are the ones `DECISION-A1-C8-NMIN-1` already adopted.** Exactly 20 rows per seed where the declared
construction finds them, otherwise the largest block it finds, provided it reaches `N_min = 17`: **20, 17, 20, 20,
18, 20**. There is no fallback to non-competent rows. A seed that cannot reach 17 supplies no block, and the block is
VOID.

**The selection artifact must be re-derived before any act is signed.** `a1_c8_target_selection.json` records a
*representative* twenty per seed and does not satisfy this decision; signing an act against it would freeze exactly
the rows the measurement found non-competent. The re-derivation now exists:
[`a1_c8_target_selection_competent.json`](a1_c8_target_selection_competent.json) forms **20 / 17 / 20 / 20 / 18 / 20**
under this rule, with every block the largest that exists at the unchanged endpoint cap of three: 20, 19 and 18 are
proved impossible on `20740102`, and 20 and 19 on `20740105`, by exhaustion rather than by a failed search. The freeze
act must point at that artifact rather than at the representative one.

**C4's clause 1 is restated to match the row counts.** `A1-C4-POSTURE-1` declares the veto as the maximum
over 324 deltas per seed and 1,944 across the block. Those figures are 108 non-target rows × 3 paths × 6 seeds — the
N=4 design. Under the operative sizes the non-target stream is 112 − N per seed:

| Seed | `20740101` | `20740102` | `20740103` | `20740104` | `20740105` | `20740106` | Block |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Target rows | 20 | 17 | 20 | 20 | 18 | 20 | 115 |
| Non-target rows | 92 | 95 | 92 | 92 | 94 | 92 | 557 |
| Deltas (×3 paths) | 276 | 285 | 276 | 276 | 282 | 276 | **1,671** |

The veto is therefore **the maximum over 276–285 deltas per seed, 1,671 across the block**. The acceptance itself is
unchanged: fewer comparisons per seed is slightly *less* exposure than the 324 the owner accepted, and the posture's
five clauses stand.

**C1's denominator does not move, and the artifact proves it.** C1 counts every recorded row of the cell stream,
targets included, so its denominator is a property of the 112-row universe and not of which edges are targets. The
competent selection reproduces **79 / 64 / 79 / 74 / 72 / 74** exactly — see the C1 table in
[`a1_c8_target_selection_competent.json`](a1_c8_target_selection_competent.json) — so no re-measurement is required,
and the preplanned universe in [`DECISION-A1-C1-CEILING`](DECISION-A1-C1-CEILING.md) is the same number on either
selection. Only C4's stream moves with the row count, and that is restated above.

**Which act survives this.** The sizes above are the N=20 block's, so adopting this fixes `A1-TARGET-FREEZE-N20-1`'s
block and leaves `A1-TARGET-FREEZE-1` — four targets per seed — unable to support C8 at all, because four rows per seed
can never reach `N_min = 17`. That incompatibility is created by C8's own adopted rule, not by this decision; it means
the N=4 act should not be signed under any outcome of this one.

**C8's tolerance changes with the size, and two seeds lose it entirely.** The adopted rule allows
`floor(0.05 × N)` assertions: one at N=20, and **zero at N=18 and N=17**. So seeds `20740102` (17) and `20740105`
(18) admit no assertion at all, while the four twenty-row seeds admit one. This is the cost of taking `N_min` as the
operative size rather than a floor.

## 3. Rejected alternatives

**Keep the representative-eligible population.** The measurement refuses it: 0 of 6 seeds is C2-viable at both
designs, and under C8's adopted rule that is VOID on every seed before any treatment effect is read.

**Use 17 rows uniformly.** It is constructible everywhere, but it discards rows the construction can reach on four
seeds, it puts C8 at zero tolerance on every seed rather than two, and it shrinks the non-target stream by three rows
per seed for no gain.

**Raise the endpoint cap to 4 so twenty rows exist everywhere.** It works — at cap 4 all six seeds take twenty — but
it changes the registered selection rule, and it concentrates more target edges on fewer tags. Interference between
target edges is what C4 exists to detect, so buying rows by raising the cap buys them in the quantity the experiment
is trying not to create.

**Score only the competent rows of the current selection, post hoc.** That conditions the analysis on a treated run
rather than a pre-treatment baseline, and it silently redefines the population after the rows are known.

## 4. What this does not do

It does not freeze a target, reserve a seed, authorise a cell, issue a grant, or clear any gate. It does not resolve
the C1 ceiling conflict ([`A1-C1-CEILING-CONFLICT`](A1-C1-CEILING-CONFLICT.md)); a separate draft,
[`DECISION-A1-C1-CEILING`](DECISION-A1-C1-CEILING.md), is PENDING for that. C4's completeness detection is no longer
open — it was repaired on 2026-11-15 (see the amendment to [`A1-C1-C4-VOID-GATE`](A1-C1-C4-VOID-GATE.md)): an absent or
short treated stream now VOIDs instead of passing on the control's own rows. It does not make C2 pass: baseline competence is necessary and not sufficient, and only a cell can
score the gate.

## 5. Reproduce the counts

```bash
.venv/bin/python -m pytest tests/test_a1_target_viability_adopted.py -q     # per-path counts and the 17/18/20 frontier
.venv/bin/python -c "
import json
d=json.load(open('docs/a1_baseline_availability_adopted.json'))
rows=[r['candidate_rows'] for r in d['per_seed']]
sizes=[20,17,20,20,18,20]
print([(n, r-n, (r-n)*3) for n, r in zip(sizes, rows)])"
```
