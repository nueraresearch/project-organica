# `DECISION-V2-PRIMITIVE-RESOLUTIONS` — adopt the primitive's four resolutions

**Status:** `ADOPTED 2026-11-16 — THE FOUR RESOLUTIONS ARE THE CHARTER'S REQUIREMENT 6; NO BUILD IS AUTHORISED`

**Decision ID:** `DECISION-V2-PRIMITIVE-RESOLUTIONS` · **Date:** 2026-11-15 · **Adopted:** 2026-11-16
**Instruction:** adopt the four resolutions as the content of the charter's requirement 6 (owner, 2026-11-16).

**Tallied by:** Q057 — the charter question. This is content *for* that charter, so it is one more decision resting on the
same question rather than a new question of its own.

**Narrows:** nothing in [`DECISION-V2-SCOPE`](DECISION-V2-SCOPE.md). D1 was already narrowed by
[`DECISION-V2-CHARTER`](DECISION-V2-CHARTER.md); this record only fixes the content of that charter's requirement 6.
**Leaves untouched:** D2 and the G13-D diagnostic, every frozen engine file, every published artifact, every verdict, and
the planning-only status of [`ORGANICA-V2-DESIGN-BRIEF`](ORGANICA-V2-DESIGN-BRIEF.md).

## 1. The decision

Adopt, as the content of the V2 charter's mutable-identity requirement, the four argued resolutions in V2-MUTABLE-IDENTITY-SPEC §10 — edges as members and tags as the key, homogeneous typed levels with level 1 built first and level 2 permitted but unbuilt, per-kind canonicalisation, reference-count reclamation that never frees an id, a key or a tombstone, and registration admitted on total appearances — with none of them in force until the charter is signed and a build is separately authorised, and none of them authorising a build by themselves.

The specification it adopts is [`V2-MUTABLE-IDENTITY-SPEC`](V2-MUTABLE-IDENTITY-SPEC.md) (§10–§11).

## 2. The four resolutions it adopts

| # | Question | Adopted answer | The measurement that constrains it |
|---|---|---|---|
| 1 | members: atoms or carriers? | edges as members, tags as the key; homogeneous typed members; level 1 built first, level 2 permitted but unbuilt | a tag triple with a missing third edge is not a carrier; the baseline is a table of pair counts, so the member must be the counted unit |
| 2 | which normalisation? | per kind: sorted triple for `cycle3`, least rotation/reflection for `cycle_n`, order preserved for open paths | 177 directed paths over 158 node sets; a direction-free key must not merge two different node sets |
| 3 | how is it compacted? | reference-count references; reclaim unreferenced atoms; never reclaim ids, keys or tombstones | atoms are immutable values and rebuildable from the pair graph, so the only non-reconstructible part is identity |
| 4 | is registration cheap enough? | admit on total appearances `m`; candidates carry no id | about eleven detections per cycle; direction flips would defeat a streak rule |

## 3. Why this is one decision and not four

They are not independent. Membership decides what canonicalisation normalises; canonicalisation decides whether the
registry can merge two detections at all; reclamation is only safe because members are immutable values; and admission is
only meaningful because registration is content-free. Adopting three of them would leave a specification that contradicts
itself — for example, a streak-based admission rule on a direction-free key would reject stable objects by construction.

Bundling also keeps the owner's act single: one sentence to sign or reject, rather than four that could be accepted in
incompatible combinations.

## 4. What this authorises

Nothing buildable. The record adopts specification content, not a change: no module, no cell, no table, no engine edit, no
threshold, no freeze. `tests/test_v2_mutable_identity_spec.py` enforces that the specification is not imported by the engine
and that no mutable-identity decision is `ADOPTED` without the charter.

## 5. The four alternatives it rejects

- **Tags as members.** A tag triple with a missing third edge would count as a carrier, and the baseline the primitive must beat counts pairs.
- **Atoms-only membership.** It would make a theory-level composite unrepresentable by schema, deciding a substantive question by accident.
- **One global canonicalisation rule.** Too coarse merges distinct cycles that share a node set; too fine never merges the two directions of one cycle.
- **Register on first detection or on consecutive streaks.** First detection makes the object population an artifact of thresholds, and direction flips would make a streak rule reject a stable object.

## 6. What would reopen it

- **Resolution 1** reopens if the first experiment requires a theory-level object: level 2 would then be built before the
  test, and the ordering clause changes while the homogeneity clause stands.
- **Resolution 2** reopens when a structure kind with semantically distinct orientations is introduced; that kind keeps its
  order and the direction-free key does not apply.
- **Resolution 3** reopens if compaction is shown to change a resolution, or if retired composites' members are dropped and
  the control arm can no longer cite them.
- **Resolution 4** reopens if admission by stability biases the population toward structures the pair-count baseline
  predicts well; the threshold would then be lowered, or the arm run over candidates too.

## 7. What a rejection does

A rejection leaves the specification planning-only and its §10 explicitly unanswered, so the charter's requirement 6 has no
content to be signed against — the charter can still be signed, but not with a primitive it has defined. Rejection is
therefore a decision to keep the question open, not a decision to build something else.

## 8. Evidence update — 2026-11-16

Resolution 2's canonicalisation is no longer only argued. The offline re-keying study was replicated on a second world, and
in both worlds a direction-free key merges the two orientations of one cycle without merging anything else:

| | Seed 20740101 | Seed 20900101 |
|---|---|---|
| Directed paths → direction-free identities | 177 → 158 | 138 → 125 |
| Retirement rows | 186 → 170 | 128 → 117 |
| Orientation flips converted into reinforcements | 55 | 18 |
| Store validation (identities, retirement rows) | pass | pass |

The 19 and 13 identities removed are exactly the both-direction node sets, and `distinct_node_sets` equals the direction-free
identity count in each world, so the sorted triple does not collapse two different node sets. This is what resolution 2 says
the key must do, measured rather than asserted, in two worlds ([`V1-REKEYING-TWO-SEEDS`](V1-REKEYING-TWO-SEEDS.md);
[`V1-REKEYING-STUDY`](V1-REKEYING-STUDY.md); [`V1-REKEYING-STUDY-20900101`](V1-REKEYING-STUDY-20900101.md)).

The 55 and 18 flips are also direct support for resolution 4's reason: a rule that requires consecutive detections would
reject a stable object that alternates orientation, and the flips are measured, not hypothetical.

**What this does not settle.** Two seeds replicate a direction, not a magnitude, so no spread or interval is claimed. The
reclamation answer (resolution 3) still rests on the storage accounting, not on a measurement of forgetting — the boundary
measurement in [`V1-CARRIER-FORGETTING`](V1-CARRIER-FORGETTING.md) found the engine never forgets a live carrier, which
removes a suspected failure mode but does not by itself justify the reclamation rule. And the decision still authorises no
build: the sentence in §1, the four answers and the rejected alternatives are unchanged. The record was `PENDING` when this
evidence was added; it was adopted with the charter on 2026-11-16.

## 9. Signature

| | |
|---|---|
| **Owner** | owner |
| **Adopt / reject** | `ADOPTED` |
| **Date** | 2026-11-16 |
| **Note** | One sentence above; the four alternatives and their reasons are in the decision index. |
