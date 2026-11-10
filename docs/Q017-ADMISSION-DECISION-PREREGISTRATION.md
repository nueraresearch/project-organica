# Q017 admission decision: a protocol with no cell

**Status: DECISION-ONLY, NO CELL.** This record resolves a judgment question; it does not run an
experiment and it cannot make Q017 a re-derivation. No engine file changes.

**Question.** Should further Layer-1 admission variants be tried?

**Why there is no experiment to register.** Q017 is not a measurement of a mechanism. Its answer
is a policy choice about whether to spend another build on a layer that two measurements already
closed. The evidence is Q006's admission comparison and Q024's ranking-admission comparison. A
new admission variant would need its own mechanism, comparator and harness before it could be a
cell; this record only decides whether that build is warranted.

## 1. Inputs

| Input | Artifact | What it must be |
| --- | --- | --- |
| Q006 | `docs/admission_two_arm_result.json` | a result from the 0.13.0 rerun under `docs/ADMISSION-TWO-ARM-PREREGISTRATION.md`, with all gates passed |
| Q024 | `docs/ranking_admission_result.json` | a result from the 0.13.0 rerun under `docs/RANKING-ADMISSION-PREREGISTRATION.md`, with all gates passed |

A result that is void, underpowered, or measured on another build is **not an input**. Q017 stays
unread; it is not retired on an invalid comparison.

## 2. What counts as a positive admission effect

A positive effect is the input protocol's own pre-committed gain conjunction, judged whole:

- the mean paired coverage gain is at or above that protocol's frozen bar;
- its 95% interval lower bound is above zero;
- the protocol's seed-count requirement is met; and
- the protocol's precision guard passes.

A headline mean above zero is not enough, and a gain bought with a precision loss is a priced
trade, not a positive effect. No new threshold is computed here; this record imports each input's
own bar and guard.

## 3. Decision rule

| Condition | Verdict | What follows |
| --- | --- | --- |
| both inputs are valid and neither is positive | `RETIRE_NO_FURTHER_VARIANTS` | Q017 is retired on 0.13.0: the layer is closed to this family of variants, and no further admission variant is scheduled |
| both inputs are valid and at least one is positive | `BUILD_REQUIRED_VARIANT` | Q017 stays open, but the next step is a **new** variant protocol with its own mechanism, comparator and harness; nothing is run by this record |
| either input is void or underpowered | `UNREAD` | no decision; wait for a valid rerun of that input, and do not add a variant in the meantime |

`BUILD_REQUIRED_VARIANT` is not an adoption. It licenses a preregistration, not a cell, and a
variant that repeats the layer without naming what is different is refused by its own protocol.

## 4. Gates

| Gate | Requirement |
| --- | --- |
| G1_inputs_valid | both input artifacts exist, are stamped with 0.13.0, and their protocols' gates passed |
| G2_no_reclassification | the decision reads each input's recorded verdict; it does not re-score a criterion, pool seeds or recompute a bar |
| G3_no_cell | this record runs no engine, opens no world and produces no cell; a decision that requires a cell is outside this protocol |

A failed gate leaves Q017 `UNREAD`; it does not become a negative result.

## 5. What this does not claim

- It does not show that no admission variant could ever help; it closes the variants that repeat
  the measured layer on this engine and world family.
- It does not revive the withdrawn diversity-first rule or the pooled-table gain.
- It does not make Q017 a runnable Half-A row. It removes the document-shaped blocker by naming
  the decision and its inputs, not by inventing a harness.

## 6. Stop condition

One decision, read once after Q006 and Q024 have valid 0.13.0 results. No admission variant may be
added under this record; a new variant needs its own preregistration and its own harness. The
record may be fixed if it is found wrong, but it may not grow into an experiment.
