# A1 engine-side join

Generated from `docs/a1_engine_side_join.json` by `python -m benchmarks.a1_engine_side_join --write`. Do not edit by hand.

**Descriptive join over committed artifacts, not an A1 result.**

## Result

**`mean_rank_fraction_served`** tracks the level among the 17 behavioural quantities: pooled within-block r **-0.8743** with block correlations **-0.901** and **-0.870**, permutation p **0.0026** against a Bonferroni threshold of **2.94e-03**, and **-0.9628** once the served count is partialed out. The loop-window family contributes 0 trackers and the ordering family 1, so the loop budget, its saturation, the entropy, the transition probability, the count and the probability mass of what the engine served and cut all fail the rule. What does track is where in the engine's own final ordering the served edges sit — a description of the selection itself, not an independent engine parameter, so this locates the level inside the selection step without naming a separate term that sets it. The join is falsifiable and passes its controls: the served edge count tracks the level at pooled r **0.8322** — as it must, because the level is an average over the served set — while the candidate count, which the two blocks hold at 63.8 apiece, gives **0.4209** with permutation p **0.1810**. Every correlation here is computed inside a block, so a block-level offset cannot produce it, and the null shuffles levels within blocks so it preserves each block's mean exactly.

## Quantities against the level

| Quantity | Family | Pooled r | current-16 | fresh-16 | p | Tracks |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| served | control | 0.8322 | 0.848 | 0.832 | 0.0044 | no |
| candidates | control | 0.4209 | -0.154 | 0.907 | 0.1810 | no |
| rank_fraction_expected | control | 0.8254 | 0.911 | 0.802 | 0.0047 | no |
| loops_at_15 | loop window | 0.2403 | 0.222 | 0.265 | 0.5078 | no |
| loops_at_120 | loop window | 0.2308 | 0.208 | 0.258 | 0.5291 | no |
| selected_loops | loop window | 0.2403 | 0.222 | 0.265 | 0.5078 | no |
| possible_loops | loop window | 0.1639 | 0.121 | 0.195 | 0.6767 | no |
| loop_slot_share | loop window | 0.3071 | 0.390 | 0.274 | 0.3659 | no |
| cap_pressure | loop window | 0.2511 | 0.223 | 0.285 | 0.4821 | no |
| saturation_cycle | loop window | 0.1938 | -0.182 | 0.351 | 0.6210 | no |
| mean_selected_loops | loop window | 0.2403 | 0.222 | 0.265 | 0.5078 | no |
| candidate_coverage | loop window | 0.3054 | 0.128 | 0.524 | 0.3027 | no |
| mean_entropy_served | prediction ordering | 0.3801 | 0.724 | 0.140 | 0.1817 | no |
| mean_probability_served | prediction ordering | -0.5221 | -0.765 | -0.414 | 0.0636 | no |
| mean_count_served | prediction ordering | 0.4708 | 0.478 | 0.545 | 0.1083 | no |
| mean_rank_fraction_served | prediction ordering | -0.8743 | -0.901 | -0.870 | 0.0026 | yes |
| transition_share | prediction ordering | -0.3357 | -0.655 | — | 0.1654 | no |
| probability_mass_served | prediction ordering | -0.1662 | -0.698 | 0.192 | 0.6126 | no |
| mass_fraction_served | prediction ordering | 0.7371 | 0.729 | 0.741 | 0.0250 | no |
| unserved_mean_probability | prediction ordering | -0.1799 | -0.326 | -0.104 | 0.6092 | no |

Threshold: |pooled r| >= 0.6, same sign in both blocks, permutation p <= 2.94e-03.

## Per-seed join

| Block | Seed | Level | Served | Candidates | Loops 120 | Slot share | Mean entropy | Mean probability |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | 20630101 | 0.3782 | 57 | 64 | 13130 | 0.0273 | 2.9521 | 0.1120 |
| current-16 | 20630102 | 0.4057 | 57 | 63 | 13122 | 0.0264 | 3.1181 | 0.0936 |
| current-16 | 20630103 | 0.4836 | 60 | 64 | 13157 | 0.0287 | 3.2817 | 0.0875 |
| current-16 | 20630104 | 0.3586 | 55 | 64 | 9358 | 0.0278 | 2.9644 | 0.1154 |
| current-16 | 20630105 | 0.4407 | 59 | 64 | 13184 | 0.0264 | 3.2839 | 0.0872 |
| current-16 | 20630106 | 0.4533 | 57 | 63 | 9094 | 0.0284 | 3.0016 | 0.1049 |
| fresh-16 | 20650101 | 0.4407 | 59 | 64 | 13142 | 0.0263 | 3.3275 | 0.0770 |
| fresh-16 | 20650102 | 0.3938 | 56 | 64 | 9313 | 0.0277 | 3.0754 | 0.0936 |
| fresh-16 | 20650103 | 0.4915 | 59 | 64 | 9405 | 0.0285 | 3.1142 | 0.0871 |
| fresh-16 | 20650104 | 0.4446 | 63 | 64 | 13106 | 0.0259 | 3.2295 | 0.0921 |
| fresh-16 | 20650105 | 0.2589 | 52 | 63 | 9936 | 0.0267 | 3.1647 | 0.0947 |
| fresh-16 | 20650106 | 0.4094 | 57 | 64 | 13126 | 0.0268 | 3.2247 | 0.1004 |

## Limits

- Six seeds per block: a correlation this small is not distinguishable from chance at any useful resolution, so a null result excludes these aggregates as carriers, not the engine as a cause.
- Every quantity is a per-seed aggregate over cycles; a quantity that varies within a seed is averaged away before the join.
- Loops at cap 15 and loops selected are the same numbers at these seeds, and mean loops selected per cycle is that series divided by the cycle count, so the loop family carries seven distinct series in nine registered quantities; the join records exact duplicate groups under found.identical_series.
- Partial correlations rest on twelve seeds and a covariate (the served count) that is itself close to the level; a partial r of -0.96 is a description, not a mechanism, and it is unstable at this n.
- The level is a fitted coverage offset, so a quantity that reproduces it arithmetically (the served count) is a control, not a finding.
- Two blocks: sign consistency across blocks is a weak filter, and a quantity that tracks in one block only is not reported as tracking.

## What this does not claim

A descriptive join over committed artifacts. It runs no engine, opens no database, and is not a treatment, target, freeze, grant or A1 cell.
