# A1 C2/C8 target-competence rule — draft for owner decision

**Date:** 2026-11-15

**Status:** `DRAFT — FOR OWNER DECISION; NOT IN FORCE; NO CELL RUN`

**Scope:** target selection for C8 and for the C2 cells that ride on the same rows. This document freezes no manifest, assigns no seed, changes no threshold, authorises no cell and measures no treatment effect. Nothing in it is in force until the owner chooses one of the three options below.

## Why this document exists

The A1 pre-freeze checklist records C2/C8 target competence as **unowned**: the viability record calls competence *conditional* and asks for "an owner rule", and no rule has been written. C8 needs a declared number of rows per seed on which an A−K− double block can actually be observed; C2 needs all four of its cells on a target. If a target's baseline A or K path is absent, its row cannot exercise those cells, and the gate has nothing to score.

This is a draft rule with measured consequences, not a decision. The decision is the owner's and is one of the three options in the last section.

## The competence reading, stated as an assumption

A row is treated as **competent** when both of its baseline paths (A and K) are present at the recorded no-arm baseline. Under that reading, a row lacking baseline A or K cannot support all of C2's cells and cannot test a genuine A−K− double block.

Two limits are part of the reading, not caveats bolted on afterwards:

- **C2 is a treatment gate, not a no-arm gate.** The baseline cannot show that a missing path stays missing under A− or K+ treatment. If an unblocked arm can induce the absent path, exact C2 is unmeasured by this rule rather than decided by it.
- **Absence at baseline is not treatment failure.** The counts below are a target-selection incompatibility, not a proof that C2 or C8 must fail.

## What is measured

On the **2063** block (recorded in `docs/a1_design_viability.json`):

- selected N=4 rows competent per seed: **2, 3, 3, 1, 2, 1** — at most **3 of 4**;
- selected N=20 rows competent per seed: **5–12** of 20;
- candidate pool that is A- and K-available: **23–36** edges per seed.

On the **adopted 2074** block, computed 2026-11-15 from the committed availability and selection artifacts (the query is reproduced below; this computation is not yet its own registered artifact, so it is a computation here, not a record):

- selected N=4 rows competent per seed: **3, 0, 3, 2, 2, 2** — **12 of 24**, at most **3 of 4**;
- selected N=20 rows competent per seed: **10, 7, 11, 13, 10, 7** — **58 of 120**, at most **13 of 20**;
- candidate pool that is A- and K-available: **27–40** edges per seed.

The two blocks agree on the shape of the finding: **no seed supplies a clean C8 block under the current selection, and the supply is not the constraint** — 27–40 competent edges exist per seed and a 20-row block needs 20. The current N20 selection, not the pool, is the C2/C8 problem.

## The rule, as drafted

1. **Row unit.** One target edge. A row is competent if and only if both baseline paths A and K are present for that directed edge in the recorded no-arm baseline. Competence is a property of the row at selection time; it carries no claim about treatment.
2. **Block rule.** A C8 block is adjudicable only if **every** one of its declared N rows is competent. A block containing even one non-competent row is **VOID — not adjudicable**, not "scored on the rest". A ratio over the rows that happened to be exercisable is not measurable and may not be reported as a rate, a pass or a zero.
3. **Selection rule.** C8 rows are selected only from the competent pool, by a declared rule, and the pool is recorded **before** the freeze. The filter is part of the pre-outcome design.
4. **Pre-registration.** The rule, the pool and the block are recorded in the freeze. Changing any of them after a run voids C8 for that block; the block may not be re-filtered to fit an outcome.
5. **Disclosure.** Report the unfiltered selection beside the filtered block — what the current rule would have produced, and what the competence filter changes — so the filter's effect is visible rather than silently baked in.

## Three options for the owner

**Option A — adopt the filter.** C8 rows are re-selected from the A- and K-available pool under a declared rule. The pool is sufficient on both blocks (2063: 23–36, 2074: 27–40 against 20 required). Cost: both target tables are regenerated, the freeze acts' recorded target sets change, and the estimand moves from *any selected edge* to *competent selected edge* — which must be recorded as a design change, not slipped in as a selection detail. This is the only option under which C8 becomes adjudicable.

**Option B — declare C8 not adjudicable.** Keep the current selections and record on the act that C8 cannot be scored on them. Cost: nothing today, and C8 never becomes measurable under this design. It is the honest option only if the owner intends never to score C8 on this universe.

**Option C — redesign the universe** to raise A∩K per seed. Cost: the largest, and it contradicts what is already known about K (window-limited, and the loop cap moved it only sublinearly). It is listed because it is the alternative that could make competence abundant rather than merely sufficient.

**A recommendation, marked as one:** Option A. It is the only option that costs a selection rule and a regenerated table rather than a measurement or a permanent hole in the gate, and the pool is large enough on both blocks that the filter does not create a new supply problem.

## What this rule does not decide

- Whether an absent baseline path can be induced by the unblocked arm. C2 remains treatment-gated, and no no-arm rule can settle it.
- Whether C1's floor is reachable. That turns on the row-versus-relation convention recorded in `docs/A1-DESIGN-VIABILITY.md`, which is a separate open definition.
- Any threshold. The C2, C4 and C8 thresholds are unchanged by this document, and no arm is run under it.

## What would change this

A measurement showing that baseline-absent paths are inducible by an unblocked arm would make competence irrelevant to C2 and force this rule to be re-drafted rather than adopted. An owner decision to run C8 on a declared filtered block closes it in the other direction.

## Closure

The owner selects A, B or C. This document is then re-issued with the choice recorded: under A it gains the declared selection rule and the regenerated block; under B it becomes the recorded limitation on the freeze act; under C it becomes the specification for a new universe. Until then the checklist row stays **unowned and undecided**, and no C8 block is adjudicable.

## Reproduce the adopted-block figures

```bash
python - <<'PY'
import json
from pathlib import Path
av = json.loads(Path("docs/a1_baseline_availability_adopted.json").read_text())
n4 = json.loads(Path("docs/a1_target_selection.json").read_text())
n20 = json.loads(Path("docs/a1_c8_target_selection.json").read_text())
for row in av["per_seed"]:
    seed = str(row["seed"])
    flags = {r["edge"]: (r["A"], r["K"]) for r in row["rows"]}
    ok = lambda e: flags.get(e, (False, False))[0] and flags.get(e, (False, False))[1]
    print(seed,
          sum(ok(e) for e in n4["per_seed"][seed]["selected"]), "of 4 |",
          sum(ok(e) for e in n20["per_seed"][seed]["selected"]), "of 20")
PY
```
