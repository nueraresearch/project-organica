# Formation provenance — robustness checks (descriptive)

**Generated from [`docs/formation_provenance_robustness.json`](formation_provenance_robustness.json).**
These tables are descriptive. They create no success rule, apply no threshold, and
**do not change the registered verdict or interval** — the endpoint was evaluated once
on the confirmatory seeds and that result stands.

Input: the cached per-candidate records of seeds 20270106–20270120;
no cell was re-run.

## Registered result (unchanged)

Difference +0.2141, interval [0.195886, 0.228119], verdict **association detected**.

## Per seed

| seed | world hits/n | world rate | self hits/n | self rate | difference |
|---|---|---|---|---|---|
| 20270106 | 96/210 | 0.4571 | 96/410 | 0.2341 | +0.2230 |
| 20270107 | 98/212 | 0.4623 | 94/418 | 0.2249 | +0.2374 |
| 20270108 | 141/306 | 0.4608 | 150/636 | 0.2358 | +0.2249 |
| 20270109 | 150/324 | 0.4630 | 135/615 | 0.2195 | +0.2435 |
| 20270110 | 94/206 | 0.4563 | 96/412 | 0.2330 | +0.2233 |
| 20270111 | 127/307 | 0.4137 | 159/612 | 0.2598 | +0.1539 |
| 20270112 | 96/208 | 0.4615 | 100/432 | 0.2315 | +0.2301 |
| 20270113 | 92/210 | 0.4381 | 106/426 | 0.2488 | +0.1893 |
| 20270114 | 288/630 | 0.4571 | 312/1260 | 0.2476 | +0.2095 |
| 20270115 | 90/200 | 0.4500 | 100/434 | 0.2304 | +0.2196 |
| 20270116 | 153/327 | 0.4679 | 135/576 | 0.2344 | +0.2335 |
| 20270117 | 192/424 | 0.4528 | 192/828 | 0.2319 | +0.2209 |
| 20270118 | 84/182 | 0.4615 | 108/446 | 0.2422 | +0.2194 |
| 20270119 | 147/318 | 0.4623 | 141/609 | 0.2315 | +0.2307 |
| 20270120 | 90/216 | 0.4167 | 112/414 | 0.2705 | +0.1461 |

Per-seed differences range +0.1461 to +0.2435; **15 of 15** are positive.

## Leave one seed out

Pooled differences range +0.2117 to +0.2187 when one seed is removed;
**15 of 15** folds stay positive.

## By candidate evidence count (`temporal_count`)

The registered permutation preserved seed and cycle, not evidence count, so this table
asks whether the direction survives at comparable counts.

| stratum | world hits/n | world rate | self hits/n | self rate | difference |
|---|---|---|---|---|---|
| `count=5` | 23/23 | 1.0000 | 32/96 | 0.3333 | +0.6667 |
| `count=6` | 39/44 | 0.8864 | 17/134 | 0.1269 | +0.7595 |
| `count=7` | 49/58 | 0.8448 | 5/149 | 0.0336 | +0.8113 |
| `count=8` | 73/107 | 0.6822 | 11/129 | 0.0853 | +0.5970 |
| `count=9` | 56/103 | 0.5437 | 6/219 | 0.0274 | +0.5163 |
| `count=10` | 115/168 | 0.6845 | 0/130 | 0.0000 | +0.6845 |
| `count=11` | 83/184 | 0.4511 | 0/185 | 0.0000 | +0.4511 |
| `count=12` | 137/256 | 0.5352 | 5/94 | 0.0532 | +0.4820 |
| `count=13` | 90/206 | 0.4369 | 5/89 | 0.0562 | +0.3807 |
| `count=14` | 139/308 | 0.4513 | 0/87 | 0.0000 | +0.4513 |
| `count=15` | 142/315 | 0.4508 | 13/143 | 0.0909 | +0.3599 |
| `count=16` | 127/280 | 0.4536 | 5/118 | 0.0424 | +0.4112 |
| `count=17` | 105/324 | 0.3241 | 3/80 | 0.0375 | +0.2866 |
| `count=18` | 103/253 | 0.4071 | 5/140 | 0.0357 | +0.3714 |
| `count=19` | 114/254 | 0.4488 | 12/94 | 0.1277 | +0.3212 |
| `count=20` | 84/208 | 0.4038 | 6/110 | 0.0545 | +0.3493 |
| `count>=21` | 459/1189 | 0.3860 | 1911/6531 | 0.2926 | +0.0934 |

Stratum-weighted difference: **+0.2384**, over 17 strata holding both arms; the direction is positive in **17 of 17**.

## What these checks do and do not say

They say whether the pooled association is carried by one seed, and whether it survives
when candidates are compared at the same recorded evidence count. A positive
stratum-weighted difference suggests provenance carries information not explained by the
transition count alone. That is still descriptive: these are observational strata, not an
intervention, and nothing here shows the knowledge is useful, that it originated in the
world, or that provenance causes held-out occurrence.
