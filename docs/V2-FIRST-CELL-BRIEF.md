# Signing the first V2 cell — one-page brief

**For the owner's signature.** The decision is [`DECISION-V2-FIRST-CELL`](DECISION-V2-FIRST-CELL.md), status
**PENDING**. The protocol is [`V2-FIRST-EXPERIMENT-PREREGISTRATION`](V2-FIRST-EXPERIMENT-PREREGISTRATION.md),
signed 2026-11-16. This brief adds no evidence; it collects what the diagnostics measured.

## What you are authorising

One cell, on the already-declared block, with the already-built readout:

| | |
|---|---|
| Seeds | **10**, `20910101`–`20910110`, held and unspent |
| World | compositional, 120 blocks; train blocks `0–95` (96 blocks), calibration `80–95`, held out `96–119` |
| Arms | A pair counts, B frozen membership, C maintained membership |
| Endpoint | mean paired difference in held-out next-edge log-loss, C − A |
| Rule | 99% paired bootstrap over seeds, 10,000 resamples, directional since Amendment 2 |
| Gates | `A1`–`A5` before any arm; any failure is `VOID` |
| Stop | one report; the charter closes, pass or fail |

Signing spends the seed block, authorises no engine change, no second report and no promotion. The readout adapter exists and
is pinned; nothing has run.

## What the diagnostics say

**The rule's false-pass rate is zero.** On 20 structureless worlds, the interval **included zero in
57** of 1,000 ten-seed cells
(0.0570) and excluded it in 943
— all of them **above** zero, where C is worse. Under the original two-sided wording that would have counted as a pass, which
is why Amendment 2 made the criterion directional: pass only when the interval lies entirely below zero. Under that rule the
false-pass rate is **0.0000** (0 of
1,000).

**The power is known, and it is not generous.** At the same measured noise (mean `d` **0.000847**,
sd **0.000645**), a ten-seed cell detects a gross benefit of **0.001399** nats
at 80% power, **0.001449** at 90% and **0.001478** at 95%. Because the null carries a
handicap, that corresponds to an observed mean difference of **−0.000602** nats at 90% power.

**The handicap is the treatment's price, not a bug.** Frozen membership's β pseudo-counts cost
**+0.001312** nats on a world with nothing to learn; the revision rule gives back
**-0.000465** by pruning member edges, for a net of **+0.000847**. The
revision-only arm is exactly the baseline on every seed (`D − A = 0.000000`), so the effect is
β-dependent and there is no implementation asymmetry. No non-trivial readout is unbiased on a structureless world; the
handicap is already inside the power numbers above.

## The single remaining action

**Sign [`DECISION-V2-FIRST-CELL`](DECISION-V2-FIRST-CELL.md).** Nothing else is open: the protocol is signed, the readout is
built and pinned, the 10 seeds are held, the gates are written, and the three diagnostics are recorded. The
signature is the only step between the protocol and a run.

## Where the evidence lives

[`V2-FIRST-CELL-NULL`](V2-FIRST-CELL-NULL.md) · [`V2-FIRST-CELL-POWER`](V2-FIRST-CELL-POWER.md) ·
[`V2-FIRST-CELL-HANDICAP`](V2-FIRST-CELL-HANDICAP.md) · [`v2_first_cell_scorer_pin.json`](v2_first_cell_scorer_pin.json) ·
[`v2_first_cell_seeds.json`](v2_first_cell_seeds.json)
