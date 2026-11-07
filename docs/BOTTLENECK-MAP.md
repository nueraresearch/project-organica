# The bottleneck map — what each surviving explanation can claim (2026-11-07)

**Status: a reading of the record, not new evidence.** This document adds no measurement and changes
no verdict. It exists because the same explanations keep being discussed in prose — in letters, in
reviews, in this conversation — and the wording drifts one word at a time until "unresolved" becomes
"not supported" and "constraint on coverage" becomes "demonstrated contributor". The machine-readable
form is `docs/bottleneck_map.json`.

Every row carries one of the four claim statuses from `papers/README.md`, a **map label** that is not
a status, the check behind it, and what the status does **not** say. The scope is part of the status.
No seed, cell, threshold or bar is allocated here.

## 1. Why a map rather than a verdict

A verdict answers one question under one protocol. A map answers "what is the standing of each
candidate explanation, and what would move it?" — the question a reader asks between campaigns, and
the one where overstatement is cheapest. Two rows below were corrected while writing this document,
both because the earlier wording claimed more than the check behind it.

The rows are **not** ordered by promise, and the statuses are **not** probabilities. "Not
established" is not "unpromising"; it is "the record cannot say yet".

## 2. The map

<!-- BEGIN MAP TABLE: generated from docs/bottleneck_map.json by benchmarks/bottleneck_map.py; do not edit by hand -->
| Candidate | Map label | Status | The check behind it |
|---|---|---|---|
| World-edge candidate availability | weakened | Supported within the tested scope | all 112 true world edges were present in memory on the tested worlds, so a shortage of candidates is ruled out there as the constraint on coverage |
| Candidate-generation strategy (broader) | unresolved | Not established / not measured | the candidate space was characterized but no generator was intervened on: the measured defect is its ordering, not the presence of the edges |
| Selection / allocation | demonstrated constraint on coverage; effect on behavior untested | Supported within the tested scope + Not established / not measured | under the engine's own global count-ranked selection the 112 world edges are spread, not clustered: the top 20 recovers 0-1, the top 40 0-2, the top 80 8-16, the top 160 36-55 and the top 320 (about 16x the budget) 106-109; precision never exceeds 0.3438 across 36 measurements under two allocation rules |
| Structure to behavior coupling | unresolved | Not established / not measured | Phase L measured structural displacement, and DI/PI are retention indices; its verdict stands at H3-L - INCONCLUSIVE. The capacity-1,000 confirmatory test found no improvement on held-out prediction, with its interval crossing zero |
| Theory mismatch (motivational reversals) | supported concern | Supported within the tested scope | the architecture's own motivational mechanisms were disabled one at a time and scored on the predicted direction: three of five predictions reversed, including contradiction's weight and question generation |
| Density interaction | preregistered, untested | Not established / not measured | the block is held before the run: a pre-run review ran the harness on five unregistered seeds and found the dense end has no headroom (both arms score precision 1.000 at rho 0.8 under fixed total exposure), so the registered interaction cannot be positive as designed; no judged cell has run |
| Pool-structure moderation | not supported | Not established / not measured | the paired-capacity records found no pool-structure moderation; this artifact does not restate their numbers, and the status is the owner's reading of them |
| Loop-redundancy moderation | not supported | Not established / not measured | the ratio- and temporal-redundancy preregistrations and their block records tested redundancy as a moderator; this artifact does not restate their numbers, and the status is the owner's reading of them |
| Decay necessity for liveness | unresolved | Not established / not measured | two points of the parameter range: 0.95 fails the harness liveness criterion on the matrix stream and horizon, while 1.0 passes it through cycle 2,999 (owner-reported) |
<!-- END MAP TABLE -->
The table is generated from the artifact's `rows` by
`python -m benchmarks.bottleneck_map --write`, and its status column carries each status
verbatim, so a compound status reads as the two statuses joined by `+`. Before the table was
generated it printed the shortened *Not established* where the artifact records *Not established
/ not measured*, which is not one of the four statuses and made the table's own vocabulary claim
false. The check column is held to a 400-character single-sentence budget: a row that grows past
it is a sign the check needs shortening in the artifact, not a reason to widen the table.

## 3. Labels are not statuses

The four statuses are the vocabulary of record. A **label** is the shorter working word for a row,
and it exists because the statuses alone cannot say whether a question was never asked or was asked
and answered with nothing.

<!-- BEGIN LABEL TABLE: generated from docs/bottleneck_map.json by benchmarks/bottleneck_map.py; do not edit by hand -->
| Map label | What it means | Status it maps to |
|---|---|---|
| weakened | evidence bears against the explanation as the dominant one, within the tested scope | Supported within the tested scope |
| demonstrated constraint on coverage; effect on behavior untested | evidence supports a limit within the tested scope, and the wider effect was not measured | Supported within the tested scope + Not established / not measured |
| supported concern | a prediction the explanation makes failed, so the concern is real | Supported within the tested scope |
| not supported | a tested prediction did not materialize, or the evidence did not appear where it would have | Not established / not measured |
| unresolved | the record cannot decide the question | Not established / not measured |
| preregistered, untested | a design is frozen and no runtime evidence exists | Not established / not measured |
<!-- END LABEL TABLE -->
The table above is generated from the artifact by
`python -m benchmarks.bottleneck_map --write`, and it is generated between the markers rather
than typed: `tests/test_bottleneck_map.py` fails when the committed table is not what that
command produces, so adding a label to `label_meanings` without regenerating is a test failure
and not a quiet divergence between the document and the artifact.

**The label vocabulary is closed.** `vocabulary.labels` in the artifact is the authoritative
list, not a description of what rows happen to use: a row may carry only a label that is on it,
every label on it must have a meaning in the table above, and adding a label means adding both in
the same change. A label invented inside a row fails the suite instead of entering the record —
the check is run on the rows and then run again on a row carrying an undefined label, so the
guard is shown to fire rather than assumed to.

**A label's mapping is asserted, not just described.** The status column above is checked against the rows: each label must map to exactly the set of statuses its rows carry. When candidate availability was split from candidate-generation strategy, this table was left claiming that `weakened` maps to a compound status, which was true before the split and false after it — the availability row now carries only the supported half while the unresolved half is a separate row. The table was corrected rather than the assertion relaxed, and the check was shown to reject the stale mapping before it was applied.

One gap is recorded rather than absorbed: the repository's vocabulary has **no exact home for "not
supported"**. "Not established / not measured" is right for a question the record cannot decide and
wrong for a test that ran and returned nothing, and treating the two as synonyms is how a null
becomes an ambiguity. The map keeps the label, states the mapping, and flags the gap. Adding a fifth
status is a decision about `papers/README.md` and belongs to the owner, not to this record.

**How rows are drawn.** The rule: a row splits when the claim differs, and keeps a compound status when one
claim is measured on two endpoints. Availability of the world's edges and the strategy that proposes
candidates are different claims, so they are separate rows — one supported, one unresolved. The
selection row stays single because its claim is one: a manipulation of what may occupy the ranking
budget, measured on coverage (supported) and on behavior (not established).

## 4. What each status does not say

| Candidate | What it does not say |
|---|---|
| World-edge candidate availability | that candidates are always available. This is presence of the world's edges in one world family, not availability in general |
| Candidate-generation strategy (broader) | that a different generation strategy cannot help. Nothing that changes which pairs a generator proposes was tested |
| Selection / allocation | that fixing selection fixes behavior. No cell has shown a downstream gain from a better-ranked selection, which is why the first status is scoped to coverage and the second is not established |
| Structure to behavior coupling | that structure fails to transfer. Retention was measured; usability of what is retained was not |
| Theory mismatch (motivational reversals) | that the theory is refuted, or that these reversals cause any downstream failure. The concern is supported; the causal link is not |
| Density interaction | that density matters. No cell has run, and the 448-cell decay null held world geometry fixed and never varied density |
| Pool-structure moderation | that pool structure is refuted. No support in the conditions tested is not evidence of absence |
| Loop-redundancy moderation | that redundancy is refuted |
| Decay necessity for liveness | that decay is unnecessary, or that decay is necessary. Neither direction was tested |

## 5. The two corrections

**Decay necessity: "not supported" became "unresolved".** "Not supported" reads as a tested
hypothesis found against. What ran was two points of the parameter range on one stream and horizon
— 0.95 failing the liveness criterion, 1.0 passing it — and necessity was never tested. The matched
decay-on/off comparison that would estimate the parameter's own effect has not run.

**Selection/allocation: "demonstrated contributor" became "demonstrated constraint on coverage;
effect on behavior untested".** The demonstrated result is that the engine's frequency ranking
cannot surface the world's edges at its budget — 0-1 of 112 in the top 20, 106-109 at about sixteen
times the budget. No cell shows that a better-ranked selection improves a behavioral endpoint. That
second half is exactly what the density study's treatment arm exists to test, so calling it
"demonstrated" would have claimed the answer the study is for.

## 6. Only one row is a specified experiment

Of the 9 rows, **1** is an experiment rather than a
reading: Density interaction. It is the only row with a defined manipulation, an explicit estimand, a
registered direction, falsifiers — and zero allocated seeds. That combination, not the plausibility
of the mechanism, is what makes it the cleanest untested explanation on the board. The zero is
enforced mechanically: `tests/test_bottleneck_map.py` fails if a seed block appears in the density
artifact or if this map acquires one.

A preregistered row outranks nothing. It is untested, and it will be judged by the same rules as
everything above it: an interaction rather than a main effect, a predicted direction that can fail,
and a harness-validity check (`Delta` must go to 0 at density 1) that fails as a defect rather than
as a surprise. Its job is no longer to explain the past; it is to survive the experiment.

## 7. What this map is not

* **Not a likelihood ranking.** Nothing here says which explanation is most likely to be the cause.
* **Not a re-scoring.** `H3-L — INCONCLUSIVE`, the 448-cell calibration null and the Phase K results
  stand exactly as recorded elsewhere.
* **Not a substitute for the records it cites.** 7 of the 9 rows were checked
  against the records named in `evidence` while writing this. The remaining 2 —
  Pool-structure moderation, Loop-redundancy moderation — carry the owner's reading, and the artifact says so rather than restating
  numbers it did not re-read.
* **Not open-ended.** A row is added with a check behind it, never with a story.

## 8. How it is checked

`tests/test_bottleneck_map.py` asserts that every status is drawn from the four-status vocabulary,
that every label is drawn from the closed label set and every label in that set is mapped,
that each label's recorded status mapping is exactly the set of statuses its rows carry — and that
both checks reject the input they exist to reject, that every evidence path exists, that exactly one row is a
specified experiment with zero allocation, that the two corrected rows carry their corrected wording
and not their old wording, that the "not supported" rows refuse refutation, that the vocabulary gap
is named rather than absorbed, that availability and generation strategy are separate rows, and that
this document quotes the artifact rather than the reverse.
