# Formation provenance — pre-registration (V1)

**Status: committed before any cell has run under it.** The instrument it names is
proven on synthetic controls (`python -m benchmarks.formation_provenance --controls`,
8/8). No study cell has been read, calibration or otherwise, and nothing in this
document has been chosen from a result.

Related: `docs/FORMATION-PROVENANCE-SPEC.md` (the instrument and its limits),
`benchmarks/formation_provenance.py`, `docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md`
§20 (the closed study — closed, and not reopened here).

## 1. Question

> Can a candidate's recorded origins be traced, and does that trace predict
> successful held-out generalization?

Two halves, and only the second is a claim about the organism. The first is a
property of the record: can a prediction's origins be attributed at formation at
all. The second is an association between that attribution and held-out success.

## 2. What is measured, and in what unit

At each sleep cycle, every prediction the engine forms gets a **formation record**:
its id, source, target, the engine's own `temporal_count`, whether it carried
parent ids, and the origin class of its `(source, target)` pair —
`pair_world_attributed`, `pair_mixed`, `pair_self_sourced` or `pair_unattributed`.

- The unit is a **transition** (prior event row, stored event row), never a count
  of "observations".
- `pair_unattributed` is not zero support; a candidate whose pair was never
  recorded is excluded from the comparison and counted, never merged.
- **Held-out success** is binary and declared here: the asserted pair occurs at
  least once in the held-out window, a window the organism is never shown.

The world and the withholding rule are those already fixed in
`docs/REUSABLE-KNOWLEDGE-PREREGISTRATION.md` §15, reused unchanged so the world is
comparable. Reuse of the *world* is not reuse of the *cells*: every seed below is
fresh, and no artifact of the closed study is re-scored.

## 3. Endpoint

**Primary:** the difference in held-out success rate between candidates whose
recorded origin is `pair_world_attributed` and candidates whose origin includes a
self-sourced row (`pair_mixed` or `pair_self_sourced`), over the confirmatory
seeds.

- Reported with a 98.33 % interval (the interval level used elsewhere in this
  project), its n, and both arm rates.
- **The bar is the lower bound of that interval being strictly greater than
  zero.** It is fixed now and may not be re-chosen after any number is seen.
- A difference whose interval contains zero is reported as **no association
  detected**, not as evidence that origins do not matter.

**Control that must fail:** a permutation arm that shuffles origin labels across
candidates within the same cycle and seed. Its interval must include zero. If the
shuffled arm also clears the bar, the primary association is an artefact of
candidate size or cycle and the study reports that, with no primary claim.

## 4. Seeds

Fresh, and disjoint from every seed already used anywhere in this project:

| block | seeds | use |
|---|---|---|
| design | `20270101`–`20270105` | instrument liveness and sample-size gates only; no endpoint is evaluated |
| confirmatory | `20270106`–`20270120` (n = 15) | the endpoint of §3, run once |

`20261201`–`20261205` are the closed study's calibration cells, `20261206` is
burned, and `20261207`–`20261226` are the closed confirmatory set. None of them is
read, extended or re-scored by this study.

## 5. Gates that must pass before the endpoint is evaluated

Each gate can fail, and a failure stops the study rather than shrinking it.

- **G1 liveness.** On every design seed, at least one formed prediction has a
  non-`pair_unattributed` origin. A build that attributes nothing is not measuring
  the question.
- **G2 denominators.** Each comparison arm must hold at least 30 candidates across
  the confirmatory seeds. Below that the study reports **not measurable** and
  stops; a ratio with no denominator is not a zero.
- **G3 permutation control.** The shuffled arm of §3 must fail to clear the bar.
- **G4 instrument neutrality.** The formation hook must reproduce the engine's own
  candidates exactly on the study build, the same comparison the synthetic control
  makes.

## 6. What a positive result would and would not mean

**Would mean:** among the candidates this engine forms on these worlds, the
recorded provenance of a prediction's pair is associated with whether that pair
occurs in a window the organism was not shown.

**Would not mean:**

- that the closed study's transfer failed or passed — its verdict is untouched,
  and this endpoint is not its endpoint;
- that the knowledge is **useful or reusable**: an association between provenance
  and held-out occurrence is not the closed study's margin, and provenance alone
  is never evidence of usefulness;
- that the content *originated* in the world: `pair_world_attributed` says the
  source rows were world events, not that the tags were first learned there;
- anything about observation-level causation. The instrument observes; it does not
  intervene.

## 7. Stop rules

- The instrument is closed: no field may be added to it to make this endpoint
  measurable. If G1 or G2 fails, that is the result.
- No seed may be added, dropped or re-drawn after the design stage is seen.
- The closed study's artifacts, seeds, thresholds and verdict are not touched by
  anything here, and a failure of this study does not reopen it.
- If the instrument's own control (G4) fails, the study does not run at all.
