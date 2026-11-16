"""The one-page brief for the signature that starts the first cell.

Every number is read from the artifact that measured it: the null calibration,
the power curve, the handicap decomposition, the seed declaration and the
decision index. Nothing is typed twice, so the brief cannot drift from the
evidence it summarises.

    python -m benchmarks.v2_first_cell_brief --check
    python -m benchmarks.v2_first_cell_brief --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

PAGE = Path("docs/V2-FIRST-CELL-BRIEF.md")
NULL = Path("docs/v2_first_cell_null.json")
POWER = Path("docs/v2_first_cell_power.json")
HANDICAP = Path("docs/v2_first_cell_handicap.json")
SEEDS = Path("docs/v2_first_cell_seeds.json")
DECISIONS = Path("docs/decisions.json")
RESERVATIONS = Path("docs/a1_seed_reservations.json")
DRY = Path("docs/v2_first_cell_dry_run.json")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render() -> str:
    null = _load(NULL)
    power = _load(POWER)
    handicap = _load(HANDICAP)
    seeds = _load(SEEDS)
    decisions = _load(DECISIONS)
    reservations = _load(RESERVATIONS)
    dry = _load(DRY)
    decision = [row for row in decisions["decisions"]
                if row["decision_id"] == "DECISION-V2-FIRST-CELL"][0]
    block = seeds["seed_block"]
    held = [row for row in reservations["reservations"]
            if row["owner"] == "docs/v2_first_cell_seeds.json"][0]
    calibration = null["calibration"]
    decomposition = handicap["decomposition"]
    factorial = handicap["factorial"]
    effects = factorial["effects"]
    return f"""# Signing the first V2 cell — one-page brief

**For the owner's signature.** The decision is [`DECISION-V2-FIRST-CELL`](DECISION-V2-FIRST-CELL.md), status
**{decision['status']}**. The protocol is [`V2-FIRST-EXPERIMENT-PREREGISTRATION`](V2-FIRST-EXPERIMENT-PREREGISTRATION.md),
signed 2026-11-16. This brief adds no evidence; it collects what the diagnostics measured.

## What you are authorising

One cell, on the already-declared block, with the already-built readout:

| | |
|---|---|
| Seeds | **{seeds['n']}**, `{block['lo']}`–`{block['hi']}`, held and {'unspent' if not held['spent'] else 'spent'} |
| World | compositional, {null['null_world']['cycles']} blocks; train blocks `0–{dry['train_blocks'] - 1}` ({dry['train_blocks']} blocks), calibration `{dry['calibration'][0]}–{dry['calibration'][1] - 1}`, held out `{dry['holdout'][0]}–{dry['holdout'][1] - 1}` |
| Arms | A pair counts, B frozen membership, C maintained membership |
| Endpoint | mean paired difference in held-out next-edge log-loss, C − A |
| Rule | {power['method']['level']:.0%} paired bootstrap over seeds, 10,000 resamples, directional since Amendment 2 |
| Gates | `A1`–`A5` before any arm; any failure is `VOID` |
| Stop | one report; the charter closes, pass or fail |

Signing spends the seed block, authorises no engine change, no second report and no promotion. The readout adapter exists and
is pinned; nothing has run.

## What the diagnostics say

**The rule's false-pass rate is zero.** On {null['summary']['n']} structureless worlds, the interval **included zero in
{round(calibration['includes_zero_rate'] * calibration['cells'])}** of {calibration['cells']:,} ten-seed cells
({calibration['includes_zero_rate']:.4f}) and excluded it in {calibration['excludes_above_zero'] + calibration['excludes_below_zero']}
— all of them **above** zero, where C is worse. Under the original two-sided wording that would have counted as a pass, which
is why Amendment 2 made the criterion directional: pass only when the interval lies entirely below zero. Under that rule the
false-pass rate is **{calibration['directional_false_pass_rate']:.4f}** ({calibration['excludes_below_zero']} of
{calibration['cells']:,}).

**The power is known, and it is not generous.** At the same measured noise (mean `d` **{power['source']['null_mean_d']:.6f}**,
sd **{power['source']['null_sd_d']:.6f}**), a ten-seed cell detects a gross benefit of **{power['mde']['0.8']:.6f}** nats
at 80% power, **{power['mde']['0.9']:.6f}** at 90% and **{power['mde']['0.95']:.6f}** at 95%. Because the null carries a
handicap, that corresponds to an observed mean difference of **{('%.6f' % power['required_mean_d']['0.9']).replace('-', '−')}** nats at 90% power.

**The handicap is the treatment's price, not a bug.** Frozen membership's β pseudo-counts cost
**+{decomposition['beta_only_mean']:.6f}** nats on a world with nothing to learn; the revision rule gives back
**{decomposition['revision_mean']:.6f}** by pruning member edges, for a net of **+{decomposition['net_mean']:.6f}**. The
revision-only arm is exactly the baseline on every seed (`D − A = {factorial['arms']['D']['mean_d']:.6f}`), so the effect is
β-dependent and there is no implementation asymmetry. No non-trivial readout is unbiased on a structureless world; the
handicap is already inside the power numbers above.

## The single remaining action

**Sign [`DECISION-V2-FIRST-CELL`](DECISION-V2-FIRST-CELL.md).** Nothing else is open: the protocol is signed, the readout is
built and pinned, the {seeds['n']} seeds are held, the gates are written, and the three diagnostics are recorded. The
signature is the only step between the protocol and a run.

## Where the evidence lives

[`V2-FIRST-CELL-NULL`](V2-FIRST-CELL-NULL.md) · [`V2-FIRST-CELL-POWER`](V2-FIRST-CELL-POWER.md) ·
[`V2-FIRST-CELL-HANDICAP`](V2-FIRST-CELL-HANDICAP.md) · [`v2_first_cell_scorer_pin.json`](v2_first_cell_scorer_pin.json) ·
[`v2_first_cell_seeds.json`](v2_first_cell_seeds.json)
"""


def check() -> None:
    if render() != PAGE.read_text(encoding="utf-8"):
        raise SystemExit("brief is stale; rebuild with --write")
    decision = [row for row in _load(DECISIONS)["decisions"]
                if row["decision_id"] == "DECISION-V2-FIRST-CELL"][0]
    if decision["status"] != "PENDING":
        raise SystemExit("the brief is for signing, but the decision is no longer pending")
    print("check: brief is fresh and the decision is still pending")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the brief is fresh")
    parser.add_argument("--write", action="store_true", help="render the brief from the artifacts")
    args = parser.parse_args()
    if args.check:
        check()
        return 0
    if args.write:
        PAGE.write_text(render(), encoding="utf-8")
        print("wrote", PAGE)
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
