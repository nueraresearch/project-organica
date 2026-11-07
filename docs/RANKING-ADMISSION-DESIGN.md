# The admission change the ordering run licenses (2026-11-07)

**Status: a specified architectural change, not an experiment.** This record names what
`ORDERING SUPPORTED` licenses — the admission rule and its budget floor — and what it does not. It
allocates nothing: no seed, no cell, no threshold, no bar. The numbers are in
`docs/ranking_admission_design.json`, and the evidence it cites is in
`docs/rank_ordering_run.json` and `docs/rank_ordering_result.json`.

The completed block returned the positive branch of its decision table: M1 passed with a mean
coverage delta of **0.1615** at the sparsest density, 95% interval **[0.1094, 0.2031]** against the
declared **0.15** bar, all nine gates green. That licenses one thing — the ordering basis is the
lever at the sparsest density, so the admission rule is the next architectural object. It does not
license a behavioural gain, a general density law, or a larger budget.

## 1. The change

**Admission.** Global count-ranked admission is replaced by **diversity-first admission over the
source side**: each slot takes the eligible candidate whose left-hand tag has the fewest
already-admitted outgoing edges, with **count as the tie-break**. The rule changes *which eligible
candidate occupies a budget slot*. Eligibility, the scoring function and the admission window are
unchanged, and the primary term counts already-admitted edges sharing a source rather than the
candidate's own frequency — the difference that keeps this from being a frequency variant.

**Budget.** The budget rule is a **floor**, not an increase: **the cap must be at least the number
of eligible source tags** (16 in this world family), because below that the diversity order has at
most one slot per source and degenerates toward count order. For the adoption test **the cap stays
at the engine's own value**. Nothing here raises it.

## 2. Why the budget is not the change

The budget route was already measured, and it was measured out. At Gate 13, coverage needs
**240–244** asserted edges — about **twelve times the budget** — precision never exceeded **0.3438**
under either frequency allocation rule, and a per-source allocation rule did worse than the global
one at the same budget. So **a larger budget buys noise**, and mixing an increase with the ordering
change would confound the one variable the completed run measured. The only budget change this
verdict licenses is the floor that makes the ordering rule expressible.

## 3. What would be decided

The estimand is Delta = diversity coverage minus count coverage at cap 20, read at the sparsest and
the densest declared densities on a fresh seed block. The **primary** reading is **the sparsest
density at cap 20**, where the completed run measured its effect. The densest density is a **guard
that voids adoption, not a second criterion to score**: an adoption that gains where the world is
sparse and loses where it is dense is a trade, and a trade must be priced rather than adopted.

Three outcomes, and none of them is "run it again":

- **Both ends pass** — the admission rule replaces count ranking in the next engine version. That
  is a cognition change under the repository's own rule, so it needs its recorded decision; the
  frozen engine is untouched and `0.12.0` is immutable.
- **The sparse end fails** — ordering is closed at this cap and world family, the line moves to the
  candidate space (which candidates exist at all), and this record **may not be followed by another
  admission variant**.
- **The dense end fails** — the rule is a trade, and the trade is written as its own record; nothing
  is adopted on the strength of the sparse end alone.

## 4. Checks that must be able to fail

- **Admission overlap** at the sparsest density must be below 1.0, or the manipulation did not
  occur. Identical admissions are **an unrun experiment, not a null result**.
- **The budget floor must bind.** A cell whose cap is below the source count is void, not a result,
  because at that cap the rule has degenerated to the control.
- **Presence must be 1.0** in every pool, so a cell tests ranking rather than memory.
- **The change is applied in-process to a copy.** The frozen engine files are untouched, `0.12.0`
  is immutable, and the change exists only as a specification until the decision is recorded.

## 5. Falsifiers

- The diversity advantage does not reproduce on fresh seeds: the ordering result was a property of
  those eight seeds.
- The rule loses more at the dense end than it gains at the sparse end: the change is a trade, not
  a fix.
- The arms' admissions are identical at the sparsest density: an unrun experiment.
- The budget floor is the only active difference: then the change is a budget change and must be
  relabelled before adoption.

## 6. Stop condition, and what this record may not become

The scope is one world family, cap 20 primary and cap 40 secondary, the sparsest and densest
declared densities, fresh seeds fixed by a pre-registration, one horizon and one exposure scheme.
The record stops on adoption, on a closed ordering line, or on a priced trade. **No admission
variant may be added to this record after the run**; it may be fixed if it is found wrong, and it
may not grow.

**What stays untested.** Coverage is not behaviour. The completed run measured which world edges a
selection surfaces, not whether surfacing them improves prediction, revision or retention. The
bottleneck map's selection row keeps its "effect on behavior untested" half, and this record adds no
row to that map.

**Allocation: zero.** This record allocates nothing; the confirmatory pre-registration fixes the bar,
the seeds and the cells. Its bar may be calibrated on the completed ordering run, which is not the
block being judged — the rule that a threshold must not be computed from the run it judges.
