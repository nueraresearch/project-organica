# A1 loop-cap counterfactual

Generated from `docs/a1_loop_cap_counterfactual.json` by `python -m benchmarks.a1_loop_cap_counterfactual --write`. Do not edit by hand.

**Counterfactual diagnostic, not an A1 result.** The same 18 worlds and candidate streams at loop caps **15/30/60/120**. Only `MAX_LOOPS` is overridden on the service instance; no engine file, target, freeze, grant or A1 cell changes.

## Result

**MIXED — the cap raises candidate K, with reshuffling losses**

Raising the loop cap from 15 to 120 raises unique candidate K from 714 to 1498 (+784, 109.8%), while 10 edges are lost against the control. The direction is window-limited, but the response is strongly sublinear and is not a fixed K quota.

The strict rule is: clean window-limited only if the top-cap total is higher, totals are nondecreasing, and no edge is lost against the control. The small reshuffling losses keep the label at **MIXED**.

| Loop cap | Candidate K | Δ vs control | Gained | Lost | All directed K | Mean K/seed | Range |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 15 | 714 | +0 | 0 | 0 | 3548 | 39.67 | 23-55 |
| 30 | 1001 | +287 | 292 | 5 | 4693 | 55.61 | 43-85 |
| 60 | 1294 | +580 | 583 | 3 | 5832 | 71.89 | 54-115 |
| 120 | 1498 | +784 | 786 | 2 | 6608 | 83.22 | 63-138 |

The control at cap **15** reproduces the committed candidate-K set on every seed. The **gained** and **lost** columns are relative to that control; a cap increase is not treated as monotone by assumption. At cap **120** the two 16-tag blocks reach **382/383** candidate K, while the 28-tag block reaches **733/1,000**: the window is still binding in the larger world.

## Per block

| Block | Candidates | K at 15 | K at 30 | K at 60 | K at 120 | All K at 15 | All K at 120 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current-16 | 382 | 228 | 302 | 362 | 382 | 980 | 1522 |
| fresh-16 | 383 | 242 | 303 | 360 | 383 | 1031 | 1529 |
| larger-28 | 1000 | 244 | 396 | 572 | 733 | 1537 | 3557 |

## Reading

A counterfactual diagnostic on 18 no-arm seeds and one build. It changes only the loop output cap; it runs no A1 cell, selects no target and makes no causal claim about capability, retention or transfer. Raising a cap can reshuffle which loops are stored, so the gained and lost columns are part of the result.

The paper's candidate-K ceiling is a candidate-stream count, not the engine's total directed carrier count. `all_K` is shown separately so a cap effect cannot be confused with the full carrier population.

## Per-seed rows

| Cap | Block | Seed | Candidate edges | Candidate K | New | Lost | All K |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 15 | current-16 | 20630101 | 64 | 44 | 0 | 0 | 183 |
| 15 | current-16 | 20630102 | 63 | 31 | 0 | 0 | 151 |
| 15 | current-16 | 20630103 | 64 | 39 | 0 | 0 | 155 |
| 15 | current-16 | 20630104 | 64 | 35 | 0 | 0 | 147 |
| 15 | current-16 | 20630105 | 64 | 43 | 0 | 0 | 171 |
| 15 | current-16 | 20630106 | 63 | 36 | 0 | 0 | 173 |
| 15 | fresh-16 | 20650101 | 64 | 40 | 0 | 0 | 161 |
| 15 | fresh-16 | 20650102 | 64 | 37 | 0 | 0 | 164 |
| 15 | fresh-16 | 20650103 | 64 | 46 | 0 | 0 | 193 |
| 15 | fresh-16 | 20650104 | 64 | 42 | 0 | 0 | 184 |
| 15 | fresh-16 | 20650105 | 63 | 39 | 0 | 0 | 178 |
| 15 | fresh-16 | 20650106 | 64 | 38 | 0 | 0 | 151 |
| 15 | larger-28 | 20660101 | 169 | 23 | 0 | 0 | 174 |
| 15 | larger-28 | 20660102 | 167 | 40 | 0 | 0 | 268 |
| 15 | larger-28 | 20660103 | 172 | 42 | 0 | 0 | 254 |
| 15 | larger-28 | 20660104 | 165 | 55 | 0 | 0 | 277 |
| 15 | larger-28 | 20660105 | 169 | 47 | 0 | 0 | 303 |
| 15 | larger-28 | 20660106 | 158 | 37 | 0 | 0 | 261 |
| 30 | current-16 | 20630101 | 64 | 55 | 11 | 0 | 219 |
| 30 | current-16 | 20630102 | 63 | 44 | 13 | 0 | 191 |
| 30 | current-16 | 20630103 | 64 | 49 | 11 | 1 | 209 |
| 30 | current-16 | 20630104 | 64 | 48 | 13 | 0 | 192 |
| 30 | current-16 | 20630105 | 64 | 57 | 14 | 0 | 223 |
| 30 | current-16 | 20630106 | 63 | 49 | 13 | 0 | 208 |
| 30 | fresh-16 | 20650101 | 64 | 53 | 14 | 1 | 211 |
| 30 | fresh-16 | 20650102 | 64 | 43 | 6 | 0 | 201 |
| 30 | fresh-16 | 20650103 | 64 | 57 | 11 | 0 | 238 |
| 30 | fresh-16 | 20650104 | 64 | 53 | 11 | 0 | 221 |
| 30 | fresh-16 | 20650105 | 63 | 47 | 8 | 0 | 206 |
| 30 | fresh-16 | 20650106 | 64 | 50 | 12 | 0 | 199 |
| 30 | larger-28 | 20660101 | 169 | 45 | 22 | 0 | 270 |
| 30 | larger-28 | 20660102 | 167 | 63 | 26 | 3 | 364 |
| 30 | larger-28 | 20660103 | 172 | 67 | 25 | 0 | 376 |
| 30 | larger-28 | 20660104 | 165 | 85 | 30 | 0 | 403 |
| 30 | larger-28 | 20660105 | 169 | 68 | 21 | 0 | 373 |
| 30 | larger-28 | 20660106 | 158 | 68 | 31 | 0 | 389 |
| 60 | current-16 | 20630101 | 64 | 61 | 17 | 0 | 240 |
| 60 | current-16 | 20630102 | 63 | 54 | 23 | 0 | 225 |
| 60 | current-16 | 20630103 | 64 | 60 | 21 | 0 | 246 |
| 60 | current-16 | 20630104 | 64 | 61 | 26 | 0 | 241 |
| 60 | current-16 | 20630105 | 64 | 64 | 21 | 0 | 255 |
| 60 | current-16 | 20630106 | 63 | 62 | 26 | 0 | 244 |
| 60 | fresh-16 | 20650101 | 64 | 64 | 24 | 0 | 254 |
| 60 | fresh-16 | 20650102 | 64 | 55 | 18 | 0 | 234 |
| 60 | fresh-16 | 20650103 | 64 | 63 | 17 | 0 | 254 |
| 60 | fresh-16 | 20650104 | 64 | 62 | 21 | 1 | 251 |
| 60 | fresh-16 | 20650105 | 63 | 61 | 22 | 0 | 248 |
| 60 | fresh-16 | 20650106 | 64 | 55 | 17 | 0 | 231 |
| 60 | larger-28 | 20660101 | 169 | 83 | 60 | 0 | 437 |
| 60 | larger-28 | 20660102 | 167 | 91 | 53 | 2 | 484 |
| 60 | larger-28 | 20660103 | 172 | 85 | 43 | 0 | 456 |
| 60 | larger-28 | 20660104 | 165 | 115 | 60 | 0 | 533 |
| 60 | larger-28 | 20660105 | 169 | 91 | 44 | 0 | 455 |
| 60 | larger-28 | 20660106 | 158 | 107 | 70 | 0 | 544 |
| 120 | current-16 | 20630101 | 64 | 64 | 20 | 0 | 254 |
| 120 | current-16 | 20630102 | 63 | 63 | 32 | 0 | 255 |
| 120 | current-16 | 20630103 | 64 | 64 | 25 | 0 | 256 |
| 120 | current-16 | 20630104 | 64 | 64 | 29 | 0 | 251 |
| 120 | current-16 | 20630105 | 64 | 64 | 21 | 0 | 254 |
| 120 | current-16 | 20630106 | 63 | 63 | 27 | 0 | 252 |
| 120 | fresh-16 | 20650101 | 64 | 64 | 24 | 0 | 255 |
| 120 | fresh-16 | 20650102 | 64 | 64 | 27 | 0 | 256 |
| 120 | fresh-16 | 20650103 | 64 | 64 | 18 | 0 | 255 |
| 120 | fresh-16 | 20650104 | 64 | 64 | 22 | 0 | 255 |
| 120 | fresh-16 | 20650105 | 63 | 63 | 24 | 0 | 256 |
| 120 | fresh-16 | 20650106 | 64 | 64 | 26 | 0 | 252 |
| 120 | larger-28 | 20660101 | 169 | 111 | 88 | 0 | 541 |
| 120 | larger-28 | 20660102 | 167 | 125 | 87 | 2 | 622 |
| 120 | larger-28 | 20660103 | 172 | 105 | 63 | 0 | 526 |
| 120 | larger-28 | 20660104 | 165 | 138 | 83 | 0 | 640 |
| 120 | larger-28 | 20660105 | 169 | 121 | 74 | 0 | 580 |
| 120 | larger-28 | 20660106 | 158 | 133 | 96 | 0 | 648 |

## Reproduce

```bash
python -m benchmarks.a1_loop_cap_counterfactual --check
python -m benchmarks.a1_loop_cap_counterfactual --self-test
```
