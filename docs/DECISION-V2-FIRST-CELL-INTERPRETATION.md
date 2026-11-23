# `DECISION-V2-FIRST-CELL-INTERPRETATION` — what each cell outcome authorises, fixed before the cell

**Status:** `ADOPTED 2026-11-16 — THE FOUR READINGS ARE FIXED BEFORE THE CELL; NO CELL IS AUTHORISED`

**Decision ID:** `DECISION-V2-FIRST-CELL-INTERPRETATION-1` · **Date:** 2026-11-16

**Instruction:** record the pre-cell interpretation commitment (owner, 2026-11-16).

**Narrows:** nothing. [`V2-FIRST-EXPERIMENT-PREREGISTRATION`](V2-FIRST-EXPERIMENT-PREREGISTRATION.md) already fixes the
endpoint, the interval, the failure rule and the seed block; this decision fixes what each outcome **authorises** once that
rule reports. **Leaves untouched:** the signed protocol, the scorer pin, every diagnostic artifact, and
[`DECISION-V2-FIRST-CELL`](DECISION-V2-FIRST-CELL.md), which remains unsigned and is still the only act that starts the cell.

## 1. Why this exists before the cell

A pre-registration fixes what counts as a pass. It does not, by itself, fix what a pass licenses, what a tie closes, or what
a reversal forbids saying. Those are the sentences most easily written after the interval is seen, and a reading chosen then
is not a reading; it is a rescue.

This document was written on 2026-11-16 with **no cell run**: the ten declared seeds `20910101`–`20910110` are held and
unspent in [`a1_seed_reservations.json`](a1_seed_reservations.json), the readout adapter is built and pinned, and no cell
result artifact exists. It fixes the four readings and the scope of each before the first number exists. It is not edited
after a result; a correction is an amendment that keeps this text readable.

## 2. The commitment, in five sentences

1. A cell outcome is read by one of four labels fixed here before the cell runs: PASS when the interval lies entirely below
   zero, BOOKKEEPING when it includes zero, REVERSAL when it lies entirely above zero, and VOID when no admissible interval
   was produced.
2. PASS authorises one report that the primitive earned held-out prediction beyond the counts on the measured world family,
   and no build, promotion or attribution of the gain to maintained selection.
3. BOOKKEEPING authorises the report that the primitive is bookkeeping and the charter fails at its first experiment, and no
   feature, rescore or second run of the same block.
4. REVERSAL authorises the report that maintained membership cost held-out prediction, which is a failure and is not
   evidence that selection found signal with the wrong sign.
5. VOID authorises no effect estimate and no scientific reading at all, because a failure to produce an admissible
   comparison is not a negative result and a further attempt needs a new pre-registration, a fresh seed block and a new
   dated grant.

## 3. The four readings

| Label | Interval on `d = L_C − L_A` | What it says | Disposition |
|---|---|---|---|
| **PASS** | entirely below zero | the addressed primitive predicted held-out edges better than the counts, on this world family | the charter passes; one report |
| **BOOKKEEPING** | includes zero | the primitive added nothing measurable; the preregistration's bookkeeping failure | the charter fails at its first experiment; one report |
| **REVERSAL** | entirely above zero | maintained membership was reliably **worse** than the counts | the charter fails; one report that states the cost |
| **VOID** | none was produced | no admissible comparison exists | nothing is read; not a result |

A gate failure is not a fifth scientific outcome. It is the absence of one, and it stops interpretation before any effect is
quoted — the discipline [`DECISION-A1-VOID-ACCEPTED`](DECISION-A1-VOID-ACCEPTED.md) already applied to A1.

## 4. What PASS authorises

**Authorises.** Exactly one report of the pre-registered cell: ten seeds, the paired mean, the 99% interval, each arm's
selected `β`, every exclusion, and `d_B` beside `d_C`. On that report the charter's first experiment passes: the primitive
earned held-out prediction beyond the counts on the measured world family.

**Does not authorise.** A V2 build, a module, an engine change, a version or tag, a promotion, a capability, transfer or
G4 claim, or a second experiment. The charter's requirement 5 closes it after one report; what follows a pass is a question
to the owner and a new decision, not an automatic build.

**The decomposition obligation.** The report must say what the pass does **not** attribute. The largest matched measurement of
the selection channel is `+0.002091` on a deliberately best-case planted world and `−0.000497` on structureless worlds
(§5 below). A pass whose margin is at or below `+0.002091` is compatible with the composite term carrying the gain and
selection contributing little; the report must state the margin against that measured bound and must not describe the pass
as maintained selection finding structure. In the planted world the frozen arm reached `0.051515` of the `0.051685` gain,
so the composite term, not revision, is the channel that carries a planted signal.

## 5. The selection sign reversal, fixed before the cell

The selection channel was measured twice, and its sign depends on whether the world carries signal:

| Quantity | Structureless (20 worlds, reused) | Planted motif (10 worlds) |
|---|---|---|
| maintained arm `d` | `+0.000847` | `−0.051685` |
| Δ at equal total mass | `−0.000460` | `+0.000834`, interval `[−0.000036, +0.002555]` — includes zero |
| Δ at equal mass **and** key count | `−0.000497` | `+0.002091`, interval `[0.000414, 0.003802]` — entirely above zero |

On a world with nothing to learn, maintained selection is worse than a random frozen allocation at the same mass and key
count by `−0.000497`. On the planted world it is better by `+0.002091` — `4.05%` of the `0.051685` planted gain. The null's own handicap is `+0.001312` from the frozen β term, reduced by `-0.000465` when revision holds fewer member edges (`2.571` → `0.783` per composite); the matched controls show the residual is mass, not selection. The sign
reverses, so neither sign may be assumed for the cell.

Four commitments follow, and they bind the report:

1. **A PASS is not a selection result.** The largest measured selection advantage is `+0.002091`, about `4.05%` of the
   planted gain; the composite term carries the rest. A pass establishes that the primitive, as a whole, earned its keep —
   not that revision is the mechanism.
2. **A BOOKKEEPING result is not evidence that selection works while something else failed.** `d_B` and `d_C` are reported
   as a decomposition, as the pre-registration already requires, and neither is promoted to a second criterion.
3. **A REVERSAL is compared with the matched null, not with zero.** The null already reverses at `−0.000497` when mass and
   keys are matched. A cell cost of that order is what no signal looks like under this rule; a larger cost is a penalty the
   mass handicap does not explain. Both are failures, and the comparison is a diagnostic, never a rescue.
4. **VOID is not a weak version of BOOKKEEPING.** BOOKKEEPING is an admissible comparison that says the primitive adds
   nothing; VOID is the failure to produce an admissible comparison. Treating the second as the first converts an
   instrument failure into a finding.

These numbers are restatements of [`V2-FIRST-CELL-MASS-MATCH`](V2-FIRST-CELL-MASS-MATCH.md) and
[`V2-FIRST-CELL-PLANTED-SELECTION`](V2-FIRST-CELL-PLANTED-SELECTION.md); the cell does not re-estimate them and this
document does not update them after a result.

## 6. What BOOKKEEPING authorises

**Authorises.** The report that the primitive is bookkeeping on this test and the charter fails at its first experiment,
with the interval, the null handicap (`+0.000847`, sd `0.000645`) and the fact that power was fixed in advance
(`0.001399` at 80%, `0.001449` at 90%, `0.001478` at 95%; an observed mean of `−0.000602` at 90%). It authorises closing the
charter and recording the negative.

**Does not authorise.** Adding a feature, changing `m`, the `β` grid, the readout, the endpoint or the interval, extending
the block, substituting a seed, re-running the block, relabelling the outcome as underpowered, or promoting a secondary
measure as the headline. A tie is a result: the design's power at the measured noise was declared before the cell, so
"underpowered" is not a reading available after it — the interval is the resolution the design chose, and a null is
reported as a null, not as a suspended verdict.

**Scope.** The block is spent. A further attempt needs a new pre-registration, a fresh seed block and a new dated grant.
The finding is "not found on this world family with this readout", not "addressability is impossible".

## 7. What REVERSAL authorises

**Authorises.** The report that maintained membership cost held-out prediction, with the sign, the magnitude and the
interval. It is a failure of the charter, and it is a stronger negative than BOOKKEEPING: the primitive did not merely fail
to help, it hurt.

**The one diagnostic it permits.** Compare the observed cost with the matched null costs, `−0.000460` at equal mass and
`−0.000497` at equal mass and key count. If the cell's cost is of that order, the result is consistent with the null's
mass handicap operating on a world with nothing to learn; if it is larger, the handicap does not explain it. Either way the
charter fails and no feature is added. The comparison may qualify the sentence; it may not change the verdict.

**Not permitted.** Reading the reversal as signal found backwards — on structureless worlds the same rule excluded zero
above zero in 943 of 1,000 cells, so a reversal is the modal no-signal outcome, not a discovery with a sign error.
"Near pass", "descriptively supportive", a retune, a feature, or a second run are all excluded.

## 8. What VOID authorises

**Authorises.** Recording the failing gate or gates and their reason codes (`A1`–`A5`, fewer than 8 of 10 measurable seeds,
missing or duplicated parts, a scorer-pin mismatch, an unaccounted exclusion), retaining the parts for instrument
diagnostics, and stopping. Nothing else.

**Does not authorise.** An effect estimate, an interval, a direction, a trend, a "descriptively supportive" reading, a
model, a capability claim, a substitute seed or a repaired denominator under the same registration. A VOID run is **not** a
negative result and is not evidence for or against the primitive; it is not reported as a null finding. The block is spent,
and a further attempt needs a new registered design, a fresh seed block and a new dated grant.

## 9. The floor under every reading

No reading authorises a V2 build, a module, an engine change, a version or tag, or a promotion. No reading lets a V1 result
be cited as V2 evidence, or the reverse. No reading authorises a second report, an extension of the first, or a seed beyond
the declared block. No reading authorises a capability, transfer or G4 claim. A report that names none of the four labels,
or blends two of them, is non-compliant rather than differently interpreted.

## 10. Rejected alternatives

**Choose the reading after seeing the interval.** The reading is what turns an interval into a claim, and choosing it after
the interval is seen is how a failed criterion becomes a rescued one. This document exists so that sentence is not available.

**Treat VOID as a negative result.** A run that produced no admissible comparison is not evidence for or against the
primitive, and reporting it as a null converts an instrument failure into a scientific finding.

**Attribute a PASS to maintained selection.** The matched selection measurement is `+0.002091` on a deliberately best-case
planted world and `−0.000497` on a structureless one, so its sign depends on the world and a pass does not establish the
mechanism.

**Rescore the block after BOOKKEEPING or REVERSAL.** The endpoint, the power and the seed block were fixed before the run, so
a second look at the same block is a new experiment reported as if it were the first.

**Read a REVERSAL as signal found backwards.** On structureless worlds the same rule excluded zero above zero in 943 of
1,000 cells, so a reversal is what no signal looks like, not a signal found in reverse.

## 11. Evidence

- [`V2-FIRST-EXPERIMENT-PREREGISTRATION`](V2-FIRST-EXPERIMENT-PREREGISTRATION.md) — the signed protocol and §3's failure rule.
- [`V2-FIRST-CELL-NULL`](V2-FIRST-CELL-NULL.md) — 1,000 ten-seed cells on 20 structureless worlds: 57 include zero (0.057), 943
  above, 0 below; directional false-pass rate 0 of 1,000.
- [`V2-FIRST-CELL-POWER`](V2-FIRST-CELL-POWER.md) — the declared resolution at that noise.
- [`V2-FIRST-CELL-HANDICAP`](V2-FIRST-CELL-HANDICAP.md) — the `+0.000847` handicap and its mass decomposition.
- [`V2-FIRST-CELL-MASS-MATCH`](V2-FIRST-CELL-MASS-MATCH.md) — the null's matched selection costs.
- [`V2-FIRST-CELL-PLANTED`](V2-FIRST-CELL-PLANTED.md) and [`V2-FIRST-CELL-PLANTED-SELECTION`](V2-FIRST-CELL-PLANTED-SELECTION.md)
  — the planted gain and the reversal.
- [`DECISION-A1-VOID-ACCEPTED`](DECISION-A1-VOID-ACCEPTED.md) — the precedent that a VOID is accepted, not rescored.
- [`v2_first_cell_seeds.json`](v2_first_cell_seeds.json), [`a1_seed_reservations.json`](a1_seed_reservations.json) — the
  held, unspent block.

## 12. Signature

| | | |
|---|---|---|
| **Decision owner** | owner direction, 2026-11-16 | |
| **Status** | `ADOPTED 2026-11-16 — THE FOUR READINGS ARE FIXED BEFORE THE CELL; NO CELL IS AUTHORISED` | |
| **Date** | 2026-11-16 | |
| **Note** | Adoption fixes the reading, not the cell: `DECISION-V2-FIRST-CELL` is still unsigned and the ten seeds are still held. | |
