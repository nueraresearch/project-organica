# The interval's power at the measured null noise — a protocol diagnostic

**Status:** `PROTOCOL DIAGNOSTIC — POWER AT THE MEASURED NULL NOISE, NOT A CELL AND NOT A VERDICT`

**Question:** the directional criterion passes only when the ten-seed interval lies entirely below zero. How large must
the primitive's held-out benefit be for that to happen reliably? A rule that cannot see a benefit it is meant to detect is
as uninformative as one that manufactures a benefit that is not there — and the null calibration already showed the rule is
sensitive enough to resolve a handicap of 0.000847 nats.

## 1. The injection

A structureless world cannot contain a benefit, so the benefit is injected as a **known shift**: if arm C were better than
the baseline by `b` nats on a seed, that seed's `d = L_C − L_A` would be its measured null value minus `b`. The shift is
exact for the interval — the percentile bootstrap of the mean moves every resampled mean by `−b`, so the upper bound at
benefit `b` is the null upper bound minus `b`. A cell passes when `hi − b < 0`, i.e. when `b > hi`; power is therefore the
fraction of cells whose measured null upper bound lies below `b`.

Source: [`v2_first_cell_null.json`](v2_first_cell_null.json), 20 structureless worlds, mean `d` =
**0.000847**, sd **0.000645**. `1000` ten-seed cells,
2,000 resamples each, level 99%.

**Assumption, stated:** the treatment shifts the mean of `d` without changing its seed-to-seed variance. A benefit that
varies across seeds would need to be larger for the same power.

## 2. The answer

| Target power | Smallest detectable benefit (nats) | Required mean `d = L_C − L_A` |
|---|---|---|
| 80% | **0.001399** | -0.000552 |
| 90% | **0.001449** | -0.000602 |
| 95% | **0.001478** | -0.000631 |

The second column is the benefit relative to the seed's null value; the third is the difference a cell would actually
observe. Because the null mean is **+0.000847**, a benefit of 0.001449 nats is what it
takes for the *observed* mean to sit at -0.000602 — the handicap has to be overcome before any
benefit shows.

The upper-bound distribution across cells: min `0.000878`, median
`0.001292`, p80 `0.001399`, p90
`0.001449`, p95 `0.001478`, max
`0.001557`. Power at the null's own mean benefit (0.000847) is
0.000: that is the case where a true benefit exactly cancels the handicap, so the true mean
difference is zero and the pass rate should match the null's directional false-pass rate — and it does.

| Injected benefit (nats) | Power |
|---|---|
| 0.0000 | 0.000 |
| 0.0005 | 0.000 |
| 0.0010 | 0.025 |
| 0.0015 | 0.976 |
| 0.0020 | 1.000 |
| 0.0025 | 1.000 |
| 0.0030 | 1.000 |
| 0.0035 | 1.000 |

## 3. What this establishes, and what it does not

**Establishes:** at the noise measured on 20 structureless worlds, a ten-seed cell detects a true
benefit of **0.001399** nats 80% of the time, **0.001449** 90%, and
**0.001478** 95%. Those are properties of the rule at this noise, computed from the same interval code the
cell will run.

**Does not establish:** the size of any real effect. The null worlds are structureless; a real world's seed-to-seed
variance may be larger, which would raise every number in the table. Nor does it establish the probability of the charter's
other error — a null verdict when the primitive works — beyond the power curve above, which is exactly that error under the
constant-shift model.

**Convergence check:** the protocol uses 10,000 resamples; the calibration used 2,000. On the
first 100 cells the two agree to a maximum upper-bound difference of
0.00005130 nats.

## 4. Reproduction

```bash
python -m benchmarks.v2_first_cell_power --write    # artifact and this page
python -m benchmarks.v2_first_cell_power --check    # page freshness, a small recomputation, and interval sanity
```

Artifact: [`v2_first_cell_power.json`](v2_first_cell_power.json).
