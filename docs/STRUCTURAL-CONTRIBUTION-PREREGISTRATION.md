# Structural contribution — pre-registration

**Status: committed 2026-11-02 (v1) — and stopped at the design block.** The harness exists
(`benchmarks/structural_contribution.py` and `benchmarks/structural_contribution_harness.py`) and
the design block ran on `20270301`–`20270305`: **it failed gate S3b on all five seeds** (§12). §10's
stop rule applies, so **no confirmatory seed has been read, no contrast has been formed, and the
study is closed at the design gate** — the owner's decision of 2026-11-02 (§12.6) keeps
§1–§10 unchanged, declines the weight-level substitute, and makes the density finding the
result. No further work happens under this preregistration.

The question, arms, rewiring rule, bar, outcome table and seeds below are the ones committed before
the harness existed. Nothing in §1–§10 changed after the audit; §11 and §12 were added by it.

It is a **new** study. It does not reopen the functional-structure study, whose result is frozen
(`docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md` §10.4), and it does not touch the closed
reusable-knowledge study or the provenance study.

Related: `docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md` (the frozen study whose readout, windows,
scoring and constants this one reuses unchanged), `docs/V1-FREEZE.md`, and
`docs/AUDIT-TRACE-SPEC.md` (the parent/lineage instrument this study does not need).

## 1. Question

> Does the **content** of the edge structure Organica forms improve log-loss on the relations it
> was never shown, over the same readout with that content destroyed in two different ways?

The unit is a held-out transition; the score is mean per-cell log-loss in nats, adopted unchanged
from the frozen study's §11.2, with `exclude_self=True` and the source-equals-target cell kept in
the denominator at label zero.

**The window is the withheld-relation window** — the relations withheld from every formation
exposure in the frozen study's world. It is the window where the strongest simple baseline has no
counts to learn from, so an improvement there is not ordinary transition counting. The full window
(cycles 150–200) is reported as a secondary diagnostic and **does not gate anything**.

## 2. What this is not

**This is a structural-contribution test, not a transfer test.** The frozen study's provenance
measure cannot certify a transfer claim on relations that were withheld from formation, because
those relations cannot carry world-source support (its §10.2 records that as structural). This
study does not use that measure and does not make a transfer claim. It asks a narrower and
answerable question: *given that the readout is better on those relations, is the advantage carried
by the learned pairings, or by something a statistic-matched graph would also produce?*

Attribution here is by **ablation**, not by source row: the same readout, scored on the same cells,
with its content removed in a declared way. That is why the question is answerable without the
provenance measure.

## 3. The four arms

Every arm is fitted on the identical 110-cycle formation stream; nothing is tuned except the bigram
arm, which is tuned exactly as the frozen study tunes it.

| Arm | Readout | What it isolates |
|---|---|---|
| **Full** | the frozen readout: `p(b\|a) = (w(a,b) + alpha·m(b)) / (W(a) + alpha)`, `alpha = 256.0` | the formed structure, as scored before |
| **Edge-removed** | the same function with an empty edge table, so `p(b\|a) = m(b)` | the contribution of having edges **at all**, at identical smoothing |
| **Rewired** | the same function on a degree-preserving rewiring of the same edge table (§4) | the contribution of **which** edge is where, at identical degrees and weights |
| **Tuned bigram** | the closed protocol's comparator sweep, best configuration chosen on the tuning split, refit on all 110 cycles | whether any of it beats the strongest simple learner |

The edge-removed arm is exactly the base-rate backoff: with an empty row, `W(a) = 0` and
`p(b|a) = alpha·m(b)/alpha = m(b)`. Gate S3 checks that identity to 1e-12 rather than assuming it.

The two controls are **ablations of the subject, not handicapping of a baseline.** AGENTS rule 11
forbids giving a baseline less than its best; here the edge-removed and rewired arms are deliberately
weaker by construction, and the arm that must not be handicapped is the bigram, which is tuned on a
split excluded from its fits exactly as in the frozen study.

## 4. The rewiring rule, fixed in advance

**Method: degree-preserving double-edge swap** (the standard Maslov–Sneppen rewiring), applied to
the frozen readout's edge table, where `rows[a][b] = w` is the weight of the edge from source tag
`a` to target tag `b`.

```
def rewire(rows, seed, draw):
    rng = random.Random(seed * 1009 + draw)
    edges = sorted((a, b, w) for a in rows for b, w in rows[a].items())
    for _ in range(10 * len(edges)):          # attempts, not successes
        (a, b, w1), (c, d, w2) = rng.sample(edges, 2)
        if a == d or c == b:                  # would create a self-loop
            continue
        if any(e[:2] == (a, d) for e in edges) or any(e[:2] == (c, b) for e in edges):
            continue                          # would create a duplicate edge
        edges.remove((a, b, w1))
        edges.remove((c, d, w2))
        edges.extend([(a, d, w1), (c, b, w2)])
    return edges_to_rows(edges)
```

Each successful swap exchanges two targets while leaving both sources and both weights in place, so:

- **preserved exactly:** the node set, the edge count, every source's **out-degree**, every target's
  **in-degree**, the multiset of edge **weights**, and the total weight;
- **not preserved:** which target belongs to which source (the content), and therefore each row's
  total weight `W(a)`, which is reported as a diagnostic. The rewired arm's backoff denominator
  legitimately differs, and preserving `W(a)` would require preserving a quantity the readout does
  not declare as a structural statistic.

**Draws.** The rewired arm is one arm but many graphs: `K = 25` independent draws per seed, each
from its own `draw` index, and the seed's rewired loss is the **mean** over the 25. The mean is
pre-specified; the best draw is never used. The draw distribution (min, median, max) is reported
beside it, so a mean cannot hide a bimodal set of graphs.

**Determinism.** The draw seed is `seed * 1009 + draw`; no draw is chosen, and re-running a seed
reproduces every graph. `PYTHONHASHSEED=0` is required, as in the frozen study.

**The control must be able to fail as a control (gate S3b).** If the rewiring leaves the edge set
too close to the original, the comparison is vacuous. Two quantities are reported, and one is gated:

| Quantity | Rule |
|---|---|
| share of edges whose `(source, target)` pair is unchanged | must be **≤ 0.20**, else the rewiring is not a control and the study stops |
| number of successful swaps | reported, not gated |

**One limitation, disclosed.** Rewiring is applied to the readout's edge table, not to the world. It
therefore preserves the graph the organism formed, including any engine-vocabulary edges that are
not world relations; it does not preserve tag-in-cell structure or the world's law. A full-readout
win over this control is evidence that the *pairing* carries information relative to a
degree-matched random graph — not evidence that the organism recovered the world's law in a
semantic sense, and not evidence of transfer (§2).

## 5. Endpoint and bar

Three paired quantities per confirmatory seed, each pooled over the 15 seeds by cells as in the
frozen study (total loss difference over total cells):

- `d_removed = loss(full) − loss(edge_removed)`
- `d_rewired = loss(full) − loss(rewired)`, where the rewired loss is the mean over the 25 draws
- `d_bigram  = loss(full) − loss(tuned bigram)`

Negative means the full readout scored better. **Bar, fixed now:** for each of the three, the
**upper** bound of a 98.33 % percentile interval from 10,000 cluster-bootstrap resamples over seeds
must lie **below zero**. The bootstrap seed is fixed at `20261102`, the same convention as the
frozen study; no interval is recomputed with another seed.

**Primary success criterion:** the upper bounds of **both** `d_removed` and `d_rewired` are below
zero. Only then may the word *content* be used. Beating the bigram is reported beside it and is
**not** part of this criterion, because a tuned bigram can be beaten by a graph statistic as easily
as by a learned relation.

## 6. Outcome table, fixed now

Every combination is named before any number exists, so the result cannot choose its own label.

| `d_removed` | `d_rewired` | `d_bigram` | Reported outcome |
|---|---|---|---|
| below 0 | below 0 | below 0 | **Structural contribution supported within this design**: the pairing carries information both ablations lack, and the readout beats the strongest simple learner |
| below 0 | below 0 | not below 0 | **Structure carries information the ablations destroy, and it is not enough for a predictive advantage over the simple baseline** |
| below 0 | not below 0 | either | **Graph structure helps; its specific content is not established** — the advantage survives removing the edges as a whole but not rewiring them |
| not below 0 | below 0 | either | **Inconsistent, and the current interpretation needs rethinking** — content matters against a rewired graph while edges in general do not help |
| not below 0 | not below 0 | either | **No detectable contribution from the formed edges on this window** |

The fourth row is the one to watch: it is the pattern that would mean the frozen study's favorable
withheld-relation margin was carried by something the rewiring preserves and the removal destroys —
a degree or weight artifact, not a learned relation. It is stated here, in advance, because that is
the interpretation that would be most tempting to explain away afterwards.

## 7. Seeds

Fresh, and disjoint from every seed used in this repository:

| Block | Seeds | Use |
|---|---|---|
| design | `20270301`–`20270305` | harness audit, liveness, denominators, rewiring invariants; **no endpoint read as a result**. **Spent 2026-11-02 (§12)** |
| confirmatory | `20270306`–`20270320` (n = 15) | the three intervals of §5, run once. **Not read.** |

Prior blocks that must not be touched: the frozen study's design `20270201`–`20270205` and
confirmatory `20270206`–`20270220`; the closed study's `20261201`–`20261226`; the provenance
study's `20270101`–`20270120`; the acquisition study's `20261100`–`20261130`; and `20261099`, the
alpha calibration world.

## 8. Gates

Each gate can fail, and a failure stops the study rather than shrinking it.

- **S1 liveness.** On every design seed the full readout must have at least one edge whose source
  tag occurs in the scored window, and at least one realised cell with non-zero support. An empty
  edge table would make the comparison vacuous in the other direction.
- **S2 denominators.** All four arms are scored on the identical cell set: same pairs, same
  vocabulary, same count — reported per arm, and equal by construction. A zero denominator is
  reported **not measurable**, never as a score of zero.
- **S3 the controls can fail.** (a) The edge-removed arm's probability must equal `m(b)` to 1e-12
  on every scored cell; (b) the rewired arm must leave **≤ 0.20** of its `(source, target)` pairs
  unchanged and must differ from the full arm on at least one realised cell; (c) a planted-signal
  control — a synthetic world whose law is known and whose readout is built from the true edges —
  must separate the full arm from both ablations, so the harness is shown able to detect a
  contribution that is there.
- **S4 invariants.** For every draw, the gate asserts that the node set, edge count, per-source
  out-degree, per-target in-degree and the weight multiset are identical to the original, and
  reports the row-total change. A rewiring that breaks an invariant is a bug, not a result.
- **S5 constants pinned.** Capacity 1,000, alpha 256.0, 110 formation cycles, tuning split 15
  cycles, `PYTHONHASHSEED=0`, 25 draws, 10,000 bootstrap resamples, level 98.33 %, bootstrap seed
  `20261102`. Any difference is a different study.
- **S6 reproducibility.** Rewiring a seed twice yields the same 25 graphs, and the gate checks it.

## 9. Run order

The frozen study's ordering applies, because it worked: it found the provenance defect before the
confirmatory block was spent.

1. **Build and commit.** The harness, the rewiring rule and the gates, with S1–S6 firing. No
   confirmatory seed is read.
2. **Design block only — `20270301`–`20270305`.** Instrument audit. Per-cell losses are computed
   (the gates need them) and labelled **endpoint-derived diagnostics**; the pooled `d_removed`,
   `d_rewired` and `d_bigram` are **not formed**, and no design margin is compared with §5's bar.
   **Executed 2026-11-02: the block failed S3b — see §12.**
3. **Confirmatory block, only if the design block passes — `20270306`–`20270320`.** One run, no seed
   added, dropped or re-drawn.

## 10. Stop rules, and what a result would not mean

- **One build, one stop condition.** The build is complete when §3–§8 are implemented and the gates
  can fire. A defect may be fixed and is disclosed; no feature may be added afterwards.
- **No endpoint on the design block**, in the sense of §9 step 2.
- **One confirmatory run.** No re-run on these seeds, and no parameter changed after a number is
  seen.
- **No threshold movement.** The bar, the outcome table and the rewiring rule are fixed here. A
  failure is reported with the interval that produced it.
- **The frozen study stays frozen.** A result here does not revise its §10.4 finding, and its
  numbers are not re-read.
- **The stop rule has fired once.** Gate S3b failed on every design seed (§12). No threshold, rule
  or arm was adjusted in its light; the two possible amendments are named in §12.4 and are the
  owner's decision, not the audit's.

**A result would not mean:** that Organica transferred anything, that it learned the world's law,
that the pairing it formed corresponds to the world's transitions rather than to the engine's
vocabulary, or that the frozen study's null primary result has changed. It would mean that on this
window, under these ablations, the readout's content does or does not carry information the
ablations lack.

**A null would not mean the edges are contentless.** It would mean that under this scoring rule, at
this capacity, with this rewiring, no contribution from the pairing was detectable — and the
outcome table says which of the four ablations failed to separate, which is the diagnostic value of
running four arms instead of two.

## 11. Second world family, deferred

A result here is a result about **one world family** — the compositional world this protocol shares
with the frozen study. It would not travel past it: the mechanism it could exhibit is "the pairing
the engine formed carries information about relations it never saw", inside one generator, one
vocabulary size (16 scored tags) and one capacity (1,000).

**A broader claim requires a second world family, and that is a separate study.** It would need its
own preregistration — the same four arms and bar, a world whose law differs in cell count,
successor structure and vocabulary size, and, because a second family is a *replication*, an
explicit statement of what would count as a failure to replicate. Until that exists, any sentence
that generalizes past this family is unsupported, and a report may say no more than "in this world
family".

## 12. Design-block audit record (2026-11-02)

### 12.1 What ran

`PYTHONHASHSEED=0 python -m benchmarks.structural_contribution_harness --design`, seeds
`20270301`–`20270305`, **176.2 s**, artifact `docs/structural_contribution_design_audit.json`. No
confirmatory seed was generated, and no contrast or outcome label was formed.

### 12.2 The gates

| Gate | Result |
|---|---|
| S1 liveness | passed on all five seeds |
| S2 denominators | passed on all five seeds — every arm on the identical cell set |
| S3a edge-removed equals the base rate | passed on all five, max abs gap **0.0** |
| **S3b the rewiring changes cells** | **failed on all five** |
| S3c the oracle plant separates the arms | passed on all five |
| S4 invariants, S5 constants, S6 reproducibility | passed on all five |

### 12.3 Why S3b cannot pass on this readout

| Seed | Edges | Source tags | Distinct targets | Possible pairs over vocab | Unchanged share (max of 25 draws) |
|---|---|---|---|---|---|
| `20270301` | 333 | 24 | 17 | 384 | 0.960961 |
| `20270302` | 332 | 24 | 17 | 384 | 0.960843 |
| `20270303` | 329 | 24 | 17 | 384 | 0.957447 |
| `20270304` | 329 | 24 | 17 | 384 | 0.954407 |
| `20270305` | 329 | 23 | 17 | 368 | 0.957447 |

The readout is **dense**: 329–333 edges spread over 23–24 source tags and **17** target tags is
**86–87 %** of every pair those tags could form. Two consequences, both measured:

1. **The swap walk is blocked.** On `20270301`, 1,631 of 2,000 attempts were refused because the
   exchanged pair already existed, 161 because it would be a self-loop, 81 because both edges left
   the same source and 118 because both arrived at the same target; **9 swaps landed**. The graph
   stays where it started.
2. **Even perfect sampling would not help.** An independent degree-matched draw over 17 targets
   retains about `Σ kₐ² / T / edges ≈ 13.9 / 17 ≈ 0.82` of the original pairs — the uniform estimate,
   using the mean out-degree 13.9. A uniform sample from the degree-preserving space is therefore
   also far from the 0.20 the gate requires.

So the committed rule and the committed gate are **not mutually satisfiable at this density**,
whatever algorithm samples the rewiring: with the degrees held fixed, "which target belongs to which
source" has almost no room to vary, because the formed readout is close to the complete bipartite
graph over the tags it touches. The 0.20 limit was written for a sparse graph and this readout is
not one.

**The failure is in the control, not in the measurement.** S3c's oracle plant — a readout built from
the scored window itself — scored **0.378707** against **0.487589** for the edge-removed arm and
**0.443569** for the rewired arm, so the harness does detect a contribution when one is present, and
it detects one through exactly the two ablations that failed to be built here.

### 12.4 What it means, and the two amendments I am not making

**It means** that on this readout the content question is not identifiable with a degree-preserving
null, and that the study cannot be spent as written.

**It does not mean** that the formed edges carry nothing: no contrast was formed, and the arm-level
losses recorded in the artifact are labelled gate diagnostics, not results. It does not revise the
frozen study's §10.4 finding, and it makes no transfer claim in either direction.

Two amendments would have made the question answerable. Both change a rule committed before the
audit and both are disclosed here for the record; **neither was applied**, and the owner's
decision between them is §12.6:

- **(a) A weight-level null.** Keep the formed pairs, keep the weight multiset, keep every
  out-degree, and permute *which pair carries which weight*. That destroys relation strength while
  preserving relation existence, so its gate is different: every realised cell must change, and the
  claim a win supports is about the strength assigned to a relation, not about the relation being
  present.
- **(b) Close the study at the identifiability limit.** Keep §4's rule, report §12.3 as the finding,
  and record that at capacity 1,000 the formed readout is too dense for a degree-preserving control
  to exist — so "the content contributes" is unavailable at this capacity, in this world family.

### 12.5 Corrections made during the audit

Two, both disclosed, neither of which touches a rule or a threshold. The first pass failed S2 on a
harness arithmetic error of mine: the expected cell count used the number of event pairs instead of
the summed context tags, so it was half the true denominator. It was corrected to the frozen
protocol's own formula and the block re-run; no arm loss, seed or gate outcome other than S2's
changed. The artifact's readout block also gained `distinct_targets` and `possible_pairs_over_vocab`,
because §12.3's argument needs the density and the first pass did not record it.

### 12.6 Decision (owner, 2026-11-02): closed at the design gate

**Keep this preregistration unchanged, and close the study at the failed design gate. No
confirmatory run.**

The reasoning, recorded because it is what the closed record rests on:

- **The density finding is the result.** §12.3 is not a defect to be worked around; it is the
  answer this study can give: the formed readout is too close to a complete bipartite graph for the
  preregistered degree-preserving rewiring to produce a sufficiently different control, so the
  topology-level question is not identifiable with this readout at this capacity.
- **The 0.20 limit stays at 0.20.** Relaxing the overlap limit after seeing that the control failed
  would turn a failed control into a different experiment — the threshold would have been chosen by
  the failure it was written to guard. §10's *no threshold movement* rule and the repository's own
  threshold rule both forbid it, and neither admits an exception for an inconvenient gate.
- **The weight-level null is not substituted into this study.** It preserves every formed pair, so it
  tests whether edge **strengths** matter, not whether the learned **pairings** matter. That is a
  different question, it supports a different claim, and it needs its own preregistration and its own
  success criterion. It is named here as a possible future study and it is **not** this one.
  If it is pursued, the owner specified the design: shuffle weights **within each source row**,
  preserving `W(a)` together with the topology, so that the test isolates **which existing pair
  carries which strength** rather than which pairs exist. No protocol for it has been written, and
  this study contributes nothing to it except the readout code in §12.3's harness.

**The clean record:** the structural-contribution study stopped at gate **S3b**; topology-level
contribution is **not identifiable with this readout and remains null**; there is **no confirmatory
result**; and no number computed after this decision changes anything in §1–§12.5. The `--confirmatory`
path refuses to run, and it stays refusing — the campaign is closed, not paused.
