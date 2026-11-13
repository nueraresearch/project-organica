# Gated schema priority — post hoc diagnostic

Generated from `docs/schema_priority_gate.json` by `python -m benchmarks.schema_priority_gate --write`. Do not edit by hand.

**Verdict: `GATE REMOVES WEAK PRIORITY, RETAINS ALL STRONG SCHEMA SEATS`.** This is a diagnostic, not a confirmatory result and not evidence that gated priority improves downstream behavior.

## Design

- Six consumed seeds (`20611601, 20611602, 20611603, 20611604, 20611605, 20611606`), 120 cycles each, **111275** ranked rows.
- **701** nonempty cycles and **13604** top-20 seats; 19 cycles have no candidates.
- **1816** schema rows.
- The gate is **temporal count >= 10**, twice the engine's admission floor of 5.
- A gated-out schema row is **not removed**. It loses the priority flag and ranks on target entropy, transition probability, count and edge like every other transition.
- A **priority seat** is a schema edge in the policy top 20 that is not in the same cycle's no-priority top 20.

## Top-20 composition

| Policy | Schema seats | Share of seats | Priority seats | Weak priority | Weak schema in top 20 | Strong priority |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| No schema priority | 382 | 2.81% | 0 | 0 | 168 | 0 |
| Ungated schema priority | 1816 | 13.35% | 1434 | 395 | 563 | 1039 |
| Gated at count >= 10 | 1400 | 10.29% | 1039 | 0 | 147 | 1039 |

Every ungated schema row is in the top 20: **1816** schema rows and **1816** schema seats.

## What the gate changes

- **395 weak priority seats** are removed; every weak schema edge with count below 10 loses the priority flag.
- **1039 strong priority seats** are retained and **0** strong schema seats are lost.
- **416** weak schema seats leave the top 20; **147** remain because they were already in the no-priority top 20 on their own ordering. Of the 416 that leave, **395** were priority seats and **21** were ordinary seats displaced when strong schema edges moved up.
- **416** non-schema seats are returned.
- **832** seats change across **135** cycles.
- Mean top-20 count changes by **+0.13** and mean probability by **+0.0007**.

## Threshold sweep

The gate at 5 reproduces ungated priority; the gate at 999 disables priority. Both controls reproduce their target top-20 lists exactly.

| Gate count | Schema seats | Share | Priority seats | Weak priority | Weak schema in top 20 | Strong priority |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 1816 | 13.35% | 1434 | 395 | 563 | 1039 |
| 8 | 1563 | 11.49% | 1206 | 167 | 310 | 1039 |
| 10 | 1400 | 10.29% | 1039 | 0 | 147 | 1039 |
| 12 | 1252 | 9.20% | 885 | 0 | 154 | 885 |
| 15 | 1072 | 7.88% | 703 | 0 | 155 | 703 |
| 20 | 809 | 5.95% | 435 | 0 | 163 | 435 |
| 999 | 382 | 2.81% | 0 | 0 | 168 | 0 |

## Per seed

| Seed | Schema rows | Ungated schema seats | Ungated priority | Gated schema seats | Gated priority |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20611601 | 103 | 103 | 91 | 41 | 29 |
| 20611602 | 156 | 156 | 129 | 137 | 110 |
| 20611603 | 613 | 613 | 426 | 493 | 321 |
| 20611604 | 216 | 216 | 171 | 136 | 93 |
| 20611605 | 588 | 588 | 500 | 507 | 423 |
| 20611606 | 140 | 140 | 117 | 86 | 63 |

## Checks

| Check | Passes |
| --- | --- |
| `all_cycles_present` | yes |
| `all_schema_rows_in_ungated_top20` | yes |
| `gate_at_floor_reproduces_ungated` | yes |
| `gate_disabled_reproduces_no_priority` | yes |
| `gated_has_no_weak_priority` | yes |
| `gate_removes_weak_priority` | yes |
| `all_strong_priority_retained` | yes |
| `remaining_weak_on_merit_only` | yes |

## What this does and does not establish

The gate is a ranking rule: it decides whether a schema edge may jump the queue, not whether the edge is admissible. Weak schema edges can still reach the top 20 on their own entropy and probability, and all 147 that do here were already there without schema priority.

The result is about candidate ordering only. It does not measure served predictions, asserted edges, downstream acquisition, transfer or capability, and the six seeds are reused. No engine file changed.

A post-hoc diagnostic on six already-consumed seeds and cached candidate rankings. It measures top-20 ordering, not served or asserted behavior, and it does not establish that gated priority improves downstream prediction, transfer or capability.
