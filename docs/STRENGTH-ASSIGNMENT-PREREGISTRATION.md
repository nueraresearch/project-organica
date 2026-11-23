# Strength assignment — pre-registration

**Status: draft, committed before any cell of this study has run.** §1–§9 are the protocol. §10 is
where the design audit will be recorded; it is empty on purpose. **No confirmatory seed has been
read, and none may be until the design block passes every gate in §7.**

This is a **new** study. It does not reopen the closed structural-contribution study
(`docs/STRUCTURAL-CONTRIBUTION-PREREGISTRATION.md`, closed at its design gate — S3b failed on all
five design seeds), it does not re-read any of its numbers, and it does not touch the frozen
functional-structure study or the closed reusable-knowledge study.

**Why it exists, in one sentence:** the structural-contribution study asked whether *which edge is
where* matters, and its control could not be identified — the graph is dense enough that a
degree-preserving rewiring leaves 95–96 % of the pairs in place — so the question was asked at a
resolution the graph cannot support, not answered negatively.

**Supersedes one earlier decision, explicitly.** On 2026-11-02 the owner declined the weight-level
substitute and closed the structural-contribution study on its density finding. This document is a
different and later decision by the same owner: the strength-assignment study is authorised as a
**separate** study with its own protocol, its own seeds and its own question. The closed study's
records stand unchanged.

## 1. Question

> Does the **assignment of strengths** to the existing source–target pairs carry predictive
> information — that is, on the withheld-relation window, does the readout score better with the
> weights where the organism put them than with the same weights on the same edges, redistributed
> among each source's existing targets?

The unit is a held-out transition; the score is the frozen study's mean per-cell log-loss in nats
(§11.2 of `docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md`), with `exclude_self=True` and the
source-equals-target cell kept in the denominator at label zero.

**The window is the full held-out window** (cycles 150–200).

*That is not the closed study's choice, and the difference is the whole point (Amendment A1, §9).*
The closed study scored the **withheld-relation** window, where the counting baseline has no counts.
This study asks a different question — whether the *weights the organism put on its existing pairs*
carry information — and on the withheld window the readout has almost no weights at all: the relations
were deliberately withheld from formation, so a formed edge from the source to the observed target is
rare there. The design block measured it: **6 of 372** realised cells (**1.6 %**) carry such an edge
on the withheld window, against **1230 of 1596** (**77.1 %**) on the full window, on the first design
seed. A weight permutation cannot move a cell whose probability is the backoff, so on the withheld
window this intervention would have been measured on noise it cannot reach.

The withheld window is still reported, as a **secondary diagnostic that gates nothing**, with its
coverage share printed beside it — and the coverage figure is itself gated (§7 S2).

## 2. What this is not

- **Not a topology test.** Topology is held *exactly* fixed: every node, every edge, every
  out-degree, every in-degree and every row total is identical to the original. A result here says
  nothing about whether having edges at all helps, and nothing about whether the *pairing* is right.
  It is strictly narrower than the closed study's question, and the narrower question is the one
  this graph can answer.
- **Not a transfer test.** The provenance measure cannot certify transfer on relations withheld from
  formation; no transfer claim is made in either direction.
- **Not a claim about the world's law.** The edge table is the organism's, so it may carry
  engine-vocabulary relations as well as world ones.

## 3. The arms

One formation stream per seed, three arms, all scored on the identical cells.

| Arm | Readout | What it isolates |
|---|---|---|
| **Full** | the frozen readout `p(b\|a) = (w(a,b) + alpha·m(b)) / (W(a) + alpha)`, `alpha = 256.0` | the strengths as the organism assigned them |
| **Strength-shuffled** | the same function on the same rows with each source's weights permuted among that row's existing targets (§4) | the contribution of **which strength sits on which target**, at identical topology, degrees and row totals |
| **Tuned bigram** | the closed protocol's comparator sweep, best configuration on the tuning split, refit on all 110 cycles | whether any of it beats the strongest simple learner |

`K = 25` independent shuffles per seed; the seeded arm's loss is the **mean** over the 25, with min,
median and max reported beside it. The mean is pre-specified and the best draw is never used.

The bigram is the only arm that is tuned, and it is tuned exactly as the frozen study tunes it: the
other two are the same readout on two row tables, so neither can be handicapped by construction.

## 4. The intervention, fixed in advance

For each source row independently, permute the row's weight values among the row's existing
targets.

```python
def shuffle_once(rows, seed, draw):
    rng = random.Random(seed * 1013 + draw)      # 1013: this study's draw multiplier
    out = {}
    for a in sorted(rows):
        targets = sorted(rows[a])
        weights = [float(rows[a][b]) for b in targets]
        rng.shuffle(weights)                     # Fisher–Yates, in place
        out[a] = dict(zip(targets, weights))
    return out
```

**Preserved exactly, and asserted on every draw (gate S1):**

- the node set and the set of `(source, target)` pairs — topology is untouched;
- every source's out-degree and every target's in-degree;
- every row's **weight multiset**, and therefore every row's total weight `W(a)`;
- the global total weight.

**Changed:** which target inside a row carries which weight. That is the whole intervention, and it
is the only thing that changes.

**Why this is identifiable where rewiring was not.** The closed study's null required the graph to
change while its degrees stayed fixed, and at this density the two requirements are mutually
unsatisfiable for most pairs. A row-wise permutation needs no swap to be admissible: it is always
available, it never re-pairs a source with a new target, and its "unchanged" case is only the
identity permutation of a row.

**Honest limit of that.** For a row with two targets, a random permutation is the identity half the
time; for a row with three, one time in six. Aggregate movement is therefore reported per draw
(`moved_share`: the fraction of edges whose weight differs from the original), and gate S3 requires
the median draw to move **at least half** of the edges. A draw that moved almost nothing is a draw
that tests almost nothing, and it must not be averaged in unremarked.

## 5. The decision rule, fixed now

- `d_shuffled = loss(full) − mean_k loss(shuffled_k)` on the **full window**; positive means the
  organism's assignment scored better, which is the direction this study exists to detect.
- `d_bigram = loss(full) − loss(bigram)`; reported beside the primary and **not part of it**.
- **Primary criterion:** the **lower** bound of the 98.33 % interval on `d_shuffled` is **strictly
  above zero**. (The structural-contribution study asked for an upper bound below zero because its
  contrasts were defined the other way round; the direction is flipped here and stated so that it
  cannot be read as a re-scored bar. 98.33 % is the three-arm Bonferroni level: `0.05 / 3`.)
- Interval: percentile bootstrap, 10,000 cluster resamples over seeds, paired by seed, bootstrap seed
  `20261102`, `PYTHONHASHSEED=0`.
- 15 confirmatory seeds, run once.

## 6. The outcome table, before any number exists

| `d_shuffled` lower bound > 0 | `d_bigram` lower bound > 0 | Reported outcome |
|---|---|---|
| yes | yes | **Strength assignment contributes, and the readout beats the tuned bigram** |
| yes | no | **Strength assignment contributes; not enough for an advantage over the simple baseline** |
| no | yes | **The readout's advantage does not depend on which weight is where** |
| no | no | **No detectable contribution of the strength assignment on this window** |

The third row is the one to watch: it is the pattern that would mean the frozen study's favourable
withheld-relation margin is carried by something a strength permutation preserves — the row totals,
the degree sequence, or the mere presence of mass on the right source — rather than by the
assignment. It is written here, in advance, because it is the row most tempting to explain away
afterwards.

## 7. Gates — the design block must pass every one

Each gate can fail, and a failure stops the study rather than shrinking it.

- **S1 structural invariance.** On every draw and every seed: node set, edge-pair set, out-degree,
  in-degree, per-row weight multiset, per-row total and global total identical to the original.
  A permutation that breaks an invariant is a bug, not a result.
- **S2 the intervention changes the intended variable, and there is something to change.** Three
  quantities, all reported: **(a)** the share of realised cells whose source row has an edge to the
  observed target — the cells where the readout's weights live — must be **at least 0.50** on the
  primary window; **(b)** the **median** draw's largest change across realised cells must exceed
  1e-12; **(c)** the median draw must move at least half of the edges (§4). The per-draw minimum is
  reported and **not** gated: a permutation is a random draw whose distribution includes
  near-identity outcomes, so with few informative cells some draw legitimately leaves the one
  informative weight where it was. *(Amended by A1 from "on every draw": the strict reading failed
  the first design block on chance alone — 3 of 25 draws — while pointing at the real problem, which
  is (a).)*
- **S3 positive planted control.** A synthetic row with a concentrated true successor and a closed
  observation set that observes only that successor: shuffling must **increase** the expected loss
  by a substantial margin. If it does not, the harness cannot detect information that is present.
- **S4 negative planted control — and it must be exchangeable, not merely constant.** Two fixtures:
  **(a)** nonconstant weights with an observation set **closed under the permutation** (every target
  in the row observed) — the loss must change by **exactly zero**, to 1e-12, because the loss then
  depends only on the multiset of probabilities; **(b)** the previously used weak fixture, constant
  weights, which is exchangeable under *any* observation set. (a) is the one that matters: it
  demonstrates that the null can be reached with unequal weights, so a zero result cannot be
  explained as "the weights were all equal anyway".
- **S5 reproducibility.** Shuffling a seed twice in one process and in a fresh process must yield
  the identical 25 graphs; the gate compares them by value, per draw.
- **S6 identical denominators.** Every arm is scored on the same cells — same pairs, same
  vocabulary, same count — reported per arm and equal by construction. A zero denominator is
  reported **not measurable**, never as a score of zero.
- **S7 end-to-end integration.** The seeded arm must be formed by the same engine run, the same
  formation stream, the same readout constants and the same comparator sweep as the full arm —
  asserted by comparing the full arm against a readout rebuilt from the same rows, not by
  construction alone.

## 8. Seeds

Fresh, disjoint from every seed this repository has used:

| Block | Seeds | Use |
|---|---|---|
| design | `20270401`–`20270405` | harness audit, liveness, denominators, invariants, planted controls; **no contrast formed, no outcome label read** |
| confirmatory | `20270406`–`20270420` (n = 15) | §5's interval, run once. **Not read.** |

Blocks that must not be touched: the closed structural-contribution study's `20270301`–`20270320`;
the frozen study's `20270201`–`20270220`; the provenance study's `20270101`–`20270120`; the
acquisition study's `20261100`–`20261130`; Phase K and L's `20261023`–`20261052`; the closed study's
`20261201`–`20261226`; and `20261099`, the alpha calibration world.

## 9. Stop rules

- **One build, one stop condition.** The build is complete when §3–§7 are implemented and every gate
  can fire. A defect may be fixed and is disclosed; no feature may be added afterwards.
- **No endpoint on the design block.** Per-cell losses are computed because the gates need them and
  are labelled endpoint-derived diagnostics; the pooled contrasts and the §6 label are **not**
  formed.
- **One confirmatory run**, no seed added, dropped or re-drawn, and no parameter changed after a
  number is seen.
- **A design failure stops the study.** It does not become a reason to lower a gate.
- **The closed study stays closed.** Nothing here revises its §10.4 finding.

## Amendment A1 — 2026-11-02, pre-outcome: the primary window and the S2 statistic

**When.** After the first design block (`20270401`–`20270405`) failed gate S2, and **before any
confirmatory seed existed**. No endpoint was formed and no §6 label was read: the design artifact
carries `deltas: null` and the reason beside it.

**What the first block found.** S2 failed on all five seeds with `readout_changes: false` while the
median draw moved **90 %** of the edges. The cause was not a broken permutation. On the
withheld-relation window the readout is almost entirely backoff: **372** realised cells, of which
**6 (1.6 %)** have a formed edge from the source to the observed target. Only those six cells can
respond to a weight permutation at all, so 3 of 25 draws changed nothing, and the strict
"every draw must differ" reading failed on chance.

**Two changes, both design defects and both disclosed:**

1. **Primary window: full held-out (cycles 150–200).** The withheld window keeps its role as a
   secondary diagnostic and loses its gating role. This was chosen with the coverage numbers above
   in hand — 1.6 % against 77.1 % — which is stated here rather than presented as anticipation.
2. **S2 statistic: median draw, plus a coverage floor.** The floor (**0.50**) is a design
   identifiability floor — below it the readout is mostly backoff and the intervention cannot act —
   and it is not a result threshold. It was also chosen with the design-block numbers in hand.

**What did not change.** The bar (§5: lower bound of the 98.33 % interval on `d_shuffled` strictly
above zero), the direction, the four outcome labels, the intervention, the invariants, the draws,
the seed blocks and the confirmatory count. **A bar may not move after a number is seen; a design
that cannot see its own variable may, and must be said out loud.**

## 10. Design audit record

### 10.1 First run — the gate failed, and it was right to

`PYTHONHASHSEED=0 python -m benchmarks.strength_assignment_harness --design`, seeds
`20270401`–`20270405`, **159.0 s**. Liveness, S1 and S3–S7 passed on all five seeds. **S2 failed on
all five**, with `readout_changes: false` while the median draw moved **90 %** of the edges.

The diagnosis is the one in Amendment A1: on the withheld-relation window the readout is almost
entirely backoff — **372** realised cells, **6 (1.6 %)** with a formed edge from source to observed
target — so only six cells could respond to any permutation, and 3 of 25 draws left the one
informative weight in place by chance. The first run's numbers are preserved in journal §130; its
artifact was superseded by the re-run below.

### 10.2 The amended protocol, re-run

`--design` again, seeds `20270401`–`20270405`, **152.1 s**. Artifact
`docs/strength_assignment_design_audit.json`.

| Seed | Edges | Primary realised cells | With a formed edge | Median Δp | Moved share | Draws that moved nothing |
|---|---|---|---|---|---|---|
| `20270401` | 329 | 1596 | 1230 (**77.1 %**) | 0.0926 | 0.906 | 0 |
| `20270402` | 338 | 1596 | 1259 (**78.9 %**) | 0.1058 | 0.902 | 0 |
| `20270403` | 331 | 1596 | 1244 (**77.9 %**) | 0.1033 | 0.906 | 0 |
| `20270404` | 326 | 1596 | 1299 (**81.4 %**) | 0.1125 | 0.902 | 0 |
| `20270405` | 334 | 1596 | 1232 (**77.2 %**) | 0.0981 | 0.898 | 0 |

**Every gate passed on every seed** — liveness, S1 invariance, S2 movement *and* coverage, S3 the
positive plant, S4 both negative plants plus the proof that the fixture fails when exchangeability
breaks, S5 reproducibility and constants, S6 denominators, S7 end-to-end integration. The layer's
own **11 fixtures** passed. Status: **design block passed; the confirmatory block may run** — and it
has not been run. The artifact carries `deltas: null` with the reason beside it.

### 10.3 What the design block does not say

No direction, no contrast, no §6 label. One diagnostic is worth recording because it is in the
artifact and leaving it out would be selection: on seed `20270401` the full window scored
**0.433694** against a shuffled mean of **0.444691** — the shuffled assignment scored *better* by
0.011 nats on that single seed. **That is one design seed on an unaudited-in-advance window, it is
not the endpoint, and the preregistered test has not been run.** It is recorded, not interpreted; if
it survives the confirmatory block, the §6 table's fourth row is the one it would land in, and that
row was written before this number existed.
