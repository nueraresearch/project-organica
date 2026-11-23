"""Design the test that separates the selection step from the served count.

`A1-ENGINE-SIDE-JOIN-1` found exactly one engine-side tracker of the 16-tag
level: the mean engine-rank fraction of the served transitions, which is the
selection described rather than an independent parameter, and it survives
partialing out the served count.  Everything else — the loop window, the
entropy, the transition probability, the count and the probability mass —
fails.  So the open question is now narrow and sharp: **does the identity of
the served edges matter, over and above how many of them are served?**

No committed artifact can answer that, because the level is a fitted coverage
offset produced by a run: which edges were served and how many were served
arrive together in every existing cell.  This module specifies the run that
would separate them, and prices it from committed artifacts only.

The design is a **fixed-count exchange**:

* **Arm I (identity control)** — the committed configuration, re-run.  It must
  reproduce the committed level to the artifact's precision or the harness is
  not deterministic and the block is void.
* **Arm S (swap)** — the same seed, the same world, the same prediction cap and
  the same candidate set, with the transition ordering replaced by the
  probability-only order.  The slot count is unchanged, so the served **count**
  is fixed by construction; only the **identity** of the served edges moves.
  The committed traces say how far: the two orders disagree on about six of
  every fifty-seven served edges.
* **Arm C (count calibration)** — the cap moved by a small amount, to measure
  in the same conditions what one extra served edge is worth.  This is the
  yardstick that turns a level difference into **edge-equivalents**, and it is
  measured in-run rather than read off the frozen cap curve.

The contrast is arm S minus arm I in edge-equivalents.  A count-only account
predicts zero; a selection account predicts a shift of the size of the swap.
Arm C exists so the answer is reported in units of "served edges", not in the
units of a fitted offset that only this analysis can read.

Everything here is a specification: it runs nothing, opens no database, and
carries no grant.

    python -m benchmarks.a1_selection_identity_spec --write
    python -m benchmarks.a1_selection_identity_spec --check
    python -m benchmarks.a1_selection_identity_spec --self-test
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CURVE_PATH = DOCS / "a1_cap_response_curve.json"
CAP112_PATH = DOCS / "a1_prediction_cap_112.json"
ORDER_PATH = DOCS / "a1_cap112_ordering_term.json"
WITHIN_PATH = DOCS / "a1_within_block_level.json"
OUT_PATH = DOCS / "a1_selection_identity_spec.json"
PAGE_PATH = DOCS / "A1-SELECTION-IDENTITY-SPEC.md"
ID = "A1-SELECTION-IDENTITY-SPEC-1"
DATE = "2026-11-14"
KIND = "a1_selection_identity_spec"
STATUS = ("CANDIDATE SPEC — FIXED-COUNT EXCHANGE TO SEPARATE SELECTION FROM COUNT; "
          "NO ARM, NO RUN, NO TARGET, NO GRANT")
CAP = 112
CAPS = (40, 80, 112)
EFFECTS = (0.5, 1.0, 2.0, 3.0, 6.0)
SIGMAS = ((0.066656, "seed-level LOO RMSE"),
          (0.043410, "current-16 within-block SD"),
          (0.072798, "fresh-16 within-block SD"))
ALPHA = 0.05
POWER = 0.80
SUPPORT = 2.0
REFUTE = 0.5


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _slope(xs: list[float], ys: list[float]) -> float:
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    return sxy / sxx if sxx else 0.0


def _z(p: float) -> float:
    low, high = 0.0, 8.0
    for _ in range(200):
        middle = (low + high) / 2.0
        if 0.5 * math.erfc(-middle / math.sqrt(2.0)) < p:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def _seeds(sigma: float, effect: float) -> int:
    """Seeds per arm and block for a two-sample comparison of the means."""
    if effect <= 0.0:
        raise ValueError("effect must be positive")
    factor = _z(1.0 - ALPHA / 2.0) + _z(POWER)
    return max(2, math.ceil(2.0 * (sigma * factor / effect) ** 2))


def build() -> dict:
    curve = _load(CURVE_PATH)
    cap112 = _load(CAP112_PATH)
    order = _load(ORDER_PATH)
    within = _load(WITHIN_PATH)
    sqrt_coefficient = curve["sqrt_coefficient"]
    if abs(sqrt_coefficient - 0.04698666) > 1e-7:
        raise SystemExit("REFUSED: the committed cap-response slope moved")
    served_by_block_cap: dict[tuple[str, int], list[float]] = defaultdict(list)
    for row in cap112["rows"]:
        served_by_block_cap[(row["block"], row["prediction_cap"])].append(
            float(row["A"]))
    exchange = []
    for block in ("current-16", "fresh-16", "larger-28"):
        caps = [cap for cap in CAPS if (block, cap) in served_by_block_cap]
        if len(caps) < 2:
            raise SystemExit("REFUSED: %s has fewer than two caps" % block)
        xs = [math.sqrt(cap) for cap in caps]
        ys = [statistics.mean(served_by_block_cap[(block, cap)]) for cap in caps]
        slope = _slope(xs, ys)
        if slope <= 0.0:
            raise SystemExit("REFUSED: %s serves fewer edges at higher caps"
                             % block)
        exchange.append({
            "block": block,
            "caps": caps,
            "served_per_cap": [round(value, 4) for value in ys],
            "slope_served_per_sqrt_cap": round(slope, 6),
            "level_per_served_edge": round(sqrt_coefficient / slope, 6),
        })
    sixteen = [row for row in exchange if row["block"] != "larger-28"]
    per_block = [row["level_per_served_edge"] for row in sixteen]
    if not per_block or any(value <= 0.0 for value in per_block):
        raise SystemExit("REFUSED: the exchange rate is not positive")
    edge_value = round(statistics.mean(per_block), 6)
    grouped: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in order["rows"]:
        grouped[(row["block"], row["seed"])].append(row)
    swap = []
    for key in sorted(grouped):
        rows = grouped[key]
        served = {row["edge"] for row in rows if row["inside"]["engine"]}
        alternate = {row["edge"] for row in rows if row["inside"]["probability_only"]}
        changed = len(served ^ alternate) // 2
        swap.append({
            "block": key[0],
            "seed": key[1],
            "served": len(served),
            "alternate_served": len(alternate),
            "swapped": changed,
            "swap_fraction": round(changed / max(1, len(served)), 6),
        })
    if not swap:
        raise SystemExit("REFUSED: no swapped served sets to read")
    mean_swap = statistics.mean(row["swapped"] for row in swap)
    level_sd = next(row["offset_sd"] for row in within["blocks"]
                    if row["label"] == "current-16")
    power = []
    for sigma, source in SIGMAS:
        for effect in EFFECTS:
            power.append({
                "sigma": sigma,
                "sigma_source": source,
                "effect_edges": effect,
                "effect_level": round(effect * edge_value, 6),
                "seeds_per_arm_per_block": _seeds(sigma, effect * edge_value),
            })
    full_swap_effect = round(mean_swap * edge_value, 6)
    found = {
        "cap": CAP,
        "sqrt_coefficient": sqrt_coefficient,
        "exchange": exchange,
        "level_per_served_edge": edge_value,
        "swap_seeds": len(swap),
        "mean_swapped": round(mean_swap, 4),
        "mean_swap_fraction": round(
            statistics.mean(row["swap_fraction"] for row in swap), 6),
        "effect_if_identity_matters": full_swap_effect,
        "effect_in_seed_units": round(full_swap_effect / level_sd, 4),
        "seeds_for_full_swap": _seeds(0.066656, full_swap_effect),
        "seeds_for_refute_threshold": _seeds(0.066656, REFUTE * edge_value),
        "seeds_for_support_threshold": _seeds(0.066656, SUPPORT * edge_value),
        "support_threshold_edges": SUPPORT,
        "refute_threshold_edges": REFUTE,
    }
    reading = (
        "The test is a **fixed-count exchange**: run the committed configuration "
        "twice on the same seeds — once unchanged (**arm I**) and once with the "
        "transition ordering replaced by the probability-only order (**arm S**) "
        "— at the same cap and on the same candidate set, so the served count is "
        "fixed by construction and only the identity of the served edges moves. "
        "A third arm (**arm C**) moves the cap by a few slots to price one served "
        "edge in the same conditions, so the contrast is reported in "
        "**edge-equivalents** rather than in offset units only this analysis can "
        "read. The committed traces already say how big the exchange is: the two "
        "orders disagree on **%(swap).1f** of **%(served)d** served edges per "
        "seed (**%(frac).1f%%**). If identity matters with the same exchange rate "
        "the count has, that is **%(effect).4f** coverage units, or **%(units).2f** "
        "seed standard deviations of the level — **%(seeds)d seeds per arm and "
        "block** to see it at a 5%% two-sided test with 80%% power. The decision "
        "rule is pre-committed in edge-equivalents: selection identity is "
        "**supported** only if the swap moves the level by at least "
        "**%(support).1f** edges' worth with an interval excluding zero, "
        "**refuted** if it moves by less than **%(refute).1f**, and otherwise "
        "undecided. The calibration is the point: arm C makes a one-edge effect "
        "measurable, so a null in arm S says that swapping **%(swap).1f** edges "
        "changed nothing a single edge would have changed, not merely that the "
        "level was noisy. The design is asymmetric and that is its weakness: "
        "**%(refute)d** seeds per arm and block would be needed to refute a "
        "**%(refute_edges).1f**-edge effect, against **%(seeds)d** to see the "
        "full swap, so the test can support the selection account cheaply but "
        "can only fail to find a small identity effect — a null leaves the "
        "question open rather than closing it."
        % {
            "swap": mean_swap,
            "served": round(statistics.mean(row["served"] for row in swap)),
            "frac": 100 * statistics.mean(row["swap_fraction"] for row in swap),
            "effect": full_swap_effect,
            "units": full_swap_effect / level_sd,
            "seeds": _seeds(0.066656, full_swap_effect),
            "refute": _seeds(0.066656, REFUTE * edge_value),
            "support": SUPPORT,
            "refute": REFUTE,
            "refute_edges": REFUTE,
        }
    )
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Does the identity of the served edges move the 16-tag level over "
            "and above how many edges are served?"
        ),
        "definition": (
            "A three-arm fixed-count exchange at the committed cap: identity "
            "control, probability-order swap, and a cap-shift calibration that "
            "prices one served edge, with the contrast reported in "
            "edge-equivalents."
        ),
        "method": (
            "The design and its power are computed from committed artifacts "
            "only: the cap-response slope gives the level per served edge, the "
            "committed cap-112 trace gives the exchange size, and the "
            "within-block SD gives the seed-level noise. No arm is run."
        ),
        "design": {
            "arms": [
                {"id": "I", "role": "identity control",
                 "change": "none — the committed configuration, re-run",
                 "must": "reproduce the committed level for the seed, or the seed is void"},
                {"id": "S", "role": "swap",
                 "change": "transition ordering replaced by the probability-only order",
                 "must": "serve the same number of candidate edges as arm I"},
                {"id": "C", "role": "count calibration",
                 "change": "prediction cap moved by a few transition slots",
                 "must": "move the served count without touching the candidate set"},
            ],
            "fixed": ["seed", "world family", "candidate set", "loop cap",
                      "events per cycle", "acquisition phase"],
            "varied": {"I vs S": "identity of the served edges",
                       "I vs C": "count of the served edges"},
            "refusals": [
                "arm S serves a different number of candidate edges than arm I — the swap leaked into the count and the seed cannot separate them",
                "arm I does not reproduce the committed level for the seed",
                "arm C does not move the served count, so the yardstick is missing",
                "the candidate set differs between arms",
            ],
            "controls": [
                "arm I is the determinism control: an identical configuration must return an identical level",
                "arm C is the yardstick control: a count change of known size must move the level by its edge-equivalent",
                "a sham swap that re-applies the committed order must return the arm I level",
            ],
            "reporting": "contrast in edge-equivalents, with the per-edge rate measured in-run by arm C",
        },
        "decision_rule": {
            "statistic": (
                "level(arm S) minus level(arm I), divided by the level per "
                "served edge measured by arm C, reported in edge-equivalents"
            ),
            "supported": "at least %.1f edge-equivalents with an interval excluding zero" % SUPPORT,
            "refuted": "at most %.1f edge-equivalents" % REFUTE,
            "otherwise": "undecided — the exchange neither separates nor excludes",
            "seed_rule": (
                "a seed contributes only if its arms serve the same count; the "
                "block is void if arm I misses the committed level"
            ),
        },
        "prediction": {
            "count_only": "the swap moves the level by 0 edge-equivalents",
            "selection_identity": (
                "the swap moves the level by the exchanged edges' worth, about "
                "%.1f edges, with the sign of the edges it adds" % mean_swap
            ),
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "found": found,
        "swap": swap,
        "power": power,
        "limits": [
            "The exchange rate is read from the frozen cap curve, which attributes the whole cap slope to the count; the cap also buys window depth, so the per-edge value is an upper proxy until arm C measures it in-run.",
            "Arm S changes the ordering basis, which is an engine-behaviour change: the spec is a proposal that needs a grant, not a thing this analysis may run.",
            "The swap fraction is measured on the committed ordering trace at cap 112 and will not transfer exactly to a block whose candidate pool differs.",
            "Three arms multiply the run cost: the design is only worth mounting if a positive arm-S result would change the selection architecture rather than add another diagnostic.",
        ],
        "not_evidence": (
            "A specification and a design estimate. It runs no arm, opens no "
            "database, measures no level, and is not a treatment, target, freeze, "
            "grant or A1 cell."
        ),
    })


def render(doc: dict) -> str:
    found = doc["found"]
    lines = [
        "# A1 selection-versus-count specification",
        "",
        "Generated from `docs/a1_selection_identity_spec.json` by "
        "`python -m benchmarks.a1_selection_identity_spec --write`. "
        "Do not edit by hand.",
        "",
        "**Specification, not a result. No arm was run.**",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## Exchange rate: level per served edge",
        "",
        "| Block | Caps | Served per sqrt(cap) | Level per served edge |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in found["exchange"]:
        lines.append("| %s | %s | %.4f | %.6f |" % (
            row["block"], "/".join(str(cap) for cap in row["caps"]),
            row["slope_served_per_sqrt_cap"], row["level_per_served_edge"]))
    lines += [
        "",
        "## Exchange size in the committed trace",
        "",
        "| Seeds | Mean served | Mean swapped | Swap fraction | Effect if identity matters |",
        "| ---: | ---: | ---: | ---: | ---: |",
        "| %d | %.1f | %.1f | %.3f | %.4f |" % (
            found["swap_seeds"],
            statistics.mean(row["served"] for row in doc["swap"]),
            found["mean_swapped"], found["mean_swap_fraction"],
            found["effect_if_identity_matters"]),
        "",
        "## Seeds per arm and block",
        "",
        "| Per-seed SD | Source | Effect (edges) | Effect (level) | Seeds |",
        "| ---: | --- | ---: | ---: | ---: |",
    ]
    for row in doc["power"]:
        lines.append("| %.6f | %s | %.1f | %.4f | %d |" % (
            row["sigma"], row["sigma_source"], row["effect_edges"],
            row["effect_level"], row["seeds_per_arm_per_block"]))
    lines += [
        "",
        "## Arms",
        "",
        "| Arm | Role | Change | Requirement |",
        "| --- | --- | --- | --- |",
    ]
    for arm in doc["design"]["arms"]:
        lines.append("| %s | %s | %s | %s |" % (
            arm["id"], arm["role"], arm["change"], arm["must"]))
    lines += ["", "## Decision rule", ""]
    for key, value in doc["decision_rule"].items():
        lines.append("- **%s**: %s" % (key, value))
    lines += ["", "## Limits", ""]
    lines += ["- %s" % limit for limit in doc["limits"]]
    lines += ["", "## What this does not claim", "", doc["not_evidence"], ""]
    return "\n".join(lines)


def problems(doc: dict | None = None) -> list[str]:
    doc = _load(OUT_PATH) if doc is None else doc
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("artifact kind")
    if doc.get("not_a_result") is not True:
        found.append("the artifact does not say it is not a result")
    if engine_stamp.missing(doc):
        found.append("the artifact is not fully stamped")
    if doc.get("governance") != {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none"}:
        found.append("governance changed")
    if doc["found"]["refute_threshold_edges"] >= doc["found"]["support_threshold_edges"]:
        found.append("the refute threshold is not below the support threshold")
    rates = [row["level_per_served_edge"] for row in doc["found"]["exchange"]
             if row["block"] != "larger-28"]
    if len(rates) != 2:
        found.append("the exchange rate does not cover both 16-tag blocks")
    if any(rate <= 0.0 for rate in rates):
        found.append("a block has a non-positive exchange rate")
    if not doc.get("swap"):
        found.append("no swapped served sets")
    for row in doc["swap"]:
        if row["swapped"] < 0 or row["swapped"] > row["served"]:
            found.append("a swap count is impossible")
    for row in doc["power"]:
        if row["seeds_per_arm_per_block"] < 2:
            found.append("a power row asks for fewer than two seeds")
    effects = {row["effect_edges"] for row in doc["power"]}
    if effects != set(EFFECTS):
        found.append("the power table does not cover the registered effects")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    if abs(_z(0.975) - 1.959963984540054) > 1e-6:
        failures.append("normal quantile")
    if abs(_z(0.80) - 0.8416212335729143) > 1e-6:
        failures.append("power quantile")
    if _seeds(0.066656, 0.10) <= _seeds(0.066656, 0.20):
        failures.append("a larger effect does not need fewer seeds")
    if _seeds(0.10, 0.05) <= _seeds(0.07, 0.05):
        failures.append("a larger SD does not need more seeds")
    if _seeds(0.066656, 0.066656 * 1.5) != 7:
        failures.append("a 1.5-sigma effect does not need the textbook count")
    if abs(_slope([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]) - 2.0) > 1e-9:
        failures.append("slope")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    print("found:", body["found"])
    for row in body["power"]:
        print(" ", row["sigma"], row["effect_edges"],
              row["seeds_per_arm_per_block"])
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no selection-identity spec; run --write")
    found = problems(_load(OUT_PATH))
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("selection identity spec: clean")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.self_test:
        found = self_test()
        if found:
            raise SystemExit("FAIL: " + "; ".join(found))
        print("selection identity spec: self-test clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
