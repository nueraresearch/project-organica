# A planted composite signal — the readout's positive control

**Status:** `POSITIVE-CONTROL DIAGNOSTIC — A PLANTED-SIGNAL WORLD, NOT A CELL AND NOT A VERDICT`

**Question:** the null worlds show the readout is slower than pair counts when there is nothing to learn. Can it
gain when the composite is the **only** evidence for the held-out transition?

## 1. What is planted

`training repeats five three-tag motifs a->b->c, 51 times each; the held-out stream asks for a->c, the motif closure read forwards, 19 times per motif`. Training shows `c -> a` and never `a -> c`; the held-out stream asks for
`a -> c`. The pair-count arm therefore has zero support for the scored transition and is left with its smoothing
floor. The admitted motif `{a,b,c}` contains the undirected member edge `{a,c}` — read from the `c -> a`
occurrence — so the membership term can raise `c` when it sees `a`. This is the readout's best case, built
deliberately: the composite is the only binding between the two tags.

## 2. Per-seed result

`d = L_C − L_A`; a negative value means the primitive beat the pair counts. `closure` is the share of admitted
member edges that are the planted motif's closure pair.

| Seed | A | B | C | `d` C−A | `d` B−A | `d` C−B | closure |
|---|---|---|---|---|---|---|---|
| `20930102` | 0.243242 | 0.191727 | 0.191567 | -0.051675 | -0.051515 | -0.000160 | 0.3448 |
| `20930103` | 0.243242 | 0.191727 | 0.191553 | -0.051689 | -0.051515 | -0.000174 | 0.3448 |
| `20930104` | 0.243242 | 0.191727 | 0.191553 | -0.051689 | -0.051515 | -0.000174 | 0.3448 |
| `20930105` | 0.243242 | 0.191727 | 0.191567 | -0.051675 | -0.051515 | -0.000160 | 0.3448 |
| `20930106` | 0.243242 | 0.191727 | 0.191567 | -0.051675 | -0.051515 | -0.000160 | 0.3448 |
| `20930107` | 0.243242 | 0.191727 | 0.191553 | -0.051689 | -0.051515 | -0.000174 | 0.3448 |
| `20930108` | 0.243242 | 0.191727 | 0.191553 | -0.051689 | -0.051515 | -0.000174 | 0.3448 |
| `20930109` | 0.243242 | 0.191727 | 0.191553 | -0.051689 | -0.051515 | -0.000174 | 0.3448 |
| `20930110` | 0.243242 | 0.191727 | 0.191553 | -0.051689 | -0.051515 | -0.000174 | 0.3448 |
| `20930111` | 0.243242 | 0.191727 | 0.191553 | -0.051689 | -0.051515 | -0.000174 | 0.3448 |

## 3. Summary and comparison

Across 10 planted worlds: mean `d` = **-0.051685**, sd `0.000007`, range
`[-0.051689, -0.051675]`; negative in 10 of 10. The
99% interval is `[-0.051689, -0.051679]` around `-0.051685`.

| Quantity | Value |
|---|---|
| Mean gain (`−d`) | **0.051685** nats |
| Null handicap (measured on structureless worlds) | 0.000847 |
| Gain as a multiple of the handicap | **61.02×** |
| Required observed mean `d` for 90% power | -0.000602 |
| Interval clears the handicap (`hi < −handicap`) | **True** |
| Interval clears the power bar (`hi < required`) | **True** |
| Revision's share of the gain (`|C−B| / |C−A|`) | 0.003 |

**Verdict: GAIN CLEARS THE NULL HANDICAP.** the planted composite is the only evidence for the held-out transition; a gain that clears the handicap shows the readout can express it, and says nothing about whether the first cell's world contains such a motif.

## 4. What this does and does not establish

**It establishes that the readout can express a composite gain above the null handicap.** The gain is
**0.051685** nats against a handicap of **0.000847**, so the
handicap is a cost the composite term can overcome when the signal is real.

**It also shows the gain is not revision's.** The frozen arm B reaches `-0.051515` and
maintenance adds `-0.000170`; revision accounts for
0.3% of the gain. This world has stable motifs, so there is nothing for the
maintenance rule to discover. It is a positive control for the **composite term**, not for mutation.

**The interval's scope is narrow.** The ten seeds vary only the tag-to-role mapping; the planted structure is
identical, so the interval measures mapping variation, not a population of worlds. The magnitude does not depend on
that distinction, but its width should not be read as a between-world estimate.

**It tests a binding, not a conjunction.** The composite term is a set of undirected member edges, so the
control shows that an admitted motif can carry a directed transition training never showed. It does not show that
the term represents `a` and `b` jointly — the readout never conditions on the conjunction, only on the edge.

**It does not establish that the first cell's world contains such a motif.** The held-out transition was chosen
to be absent from training and bound only by the composite; no natural world is guaranteed to have that shape. The
cell remains the test of whether the primitive earns its handicap on the pre-registered world, and this diagnostic
does not change the pre-registration or spend the cell's seeds.

## 5. Reproduction

```bash
python -m benchmarks.v2_first_cell_planted --smoke   # the declared smoke seed, not scored
python -m benchmarks.v2_first_cell_planted --write   # ten measurement seeds, artifact and page
python -m benchmarks.v2_first_cell_planted --check   # freshness, determinism, declared block
```

Artifact: [`v2_first_cell_planted.json`](v2_first_cell_planted.json). Seeds:
[`v2_first_cell_planted_seeds.json`](v2_first_cell_planted_seeds.json).
