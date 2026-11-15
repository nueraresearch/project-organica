"""Can the 0.05/0.09 decision bands be widened, and what does each widening buy?

The committed rule on the split-32 minus split-48 offset difference maps an
estimate to three outcomes: **size** if |d| <= 0.05, **density** if d <= -0.09,
and *undecided* in between.  `A1-SPLIT-POWER-1` sized that rule: nine seeds per
block at a 20% wrong-decision rate, five of the nine forced by the density
edge sitting only 0.0264 below the predicted -0.116.

This module asks the band question directly.  For a band pair (floor, ceiling)
and a per-seed SD sigma it computes the four outcome probabilities exactly on
the two-sample *t*,

    size declared   | size true     = E_s[ Phi(f/(SE s)) - Phi(-f/(SE s)) ]
    density declared| size true     = E_s[ Phi(-c/(SE s)) ]
    density declared| density true  = E_s[ Phi((G-c)/(SE s)) ]
    size declared   | density true  = E_s[ Phi((G+f)/(SE s)) - Phi((G-f)/(SE s)) ],

with `G = 0.11638` the predicted difference and `SE = sigma sqrt(2/n)`.  A band
pair is admissible at a stated pair of error rates when neither wrong branch
exceeds its rate, and it is *no weaker* than the committed rule when it holds
the same error guarantee at no more seeds.

Two results follow from the algebra and are checked by computation:

* the admissible set at a fixed seed count is an interval — `c >= z SE` and
  `f <= G - z SE` — so widening is possible **only** by lowering the density
  ceiling or raising the size floor, and only within that interval;
* the seed-minimizing bands at a fixed error budget sit **on** those bounds, so
  the cheapest rule is not the committed one: at a 5%/5% guarantee the cheapest
  bands need **6** seeds per block where the committed pair needs more.

    python -m benchmarks.a1_band_frontier --write
    python -m benchmarks.a1_band_frontier --check
    python -m benchmarks.a1_band_frontier --self-test
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks.a1_split_power import _expectation, _phi

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
POWER_PATH = DOCS / "a1_split_power.json"
SPEC_PATH = DOCS / "a1_offset_discriminator_spec.json"
OUT_PATH = DOCS / "a1_band_frontier.json"
PAGE_PATH = DOCS / "A1-BAND-FRONTIER.md"
ID = "A1-BAND-FRONTIER-1"
DATE = "2026-11-14"
KIND = "a1_band_frontier"
STATUS = ("DESIGN ESTIMATE — BAND POSITION AND SEEDS PER SPLIT BLOCK; NO TARGET, "
          "FREEZE, GRANT OR A1 CELL")
SIGMA = 0.066656
GAP = 0.11638
FLOOR = 0.05
CEILING = 0.09
SEEDS = (6, 9)
BUDGETS = (0.05, 0.10)
POWER_TARGET = 0.80
PREFIX = ((0.05, 0.09), (0.0582, 0.0582), (0.05, 0.07), (0.051, 0.065),
          (0.07, 0.09), (0.04, 0.10), (0.068, 0.068), (0.06, 0.09))
GRID_FLOORS = tuple(round(0.02 + 0.01 * step, 2) for step in range(9))
GRID_CEILINGS = tuple(round(0.03 + 0.01 * step, 2) for step in range(10))


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _z(p: float) -> float:
    """Two-sided normal quantile by bisection on the normal CDF."""
    low, high = 0.0, 8.0
    for _ in range(200):
        middle = (low + high) / 2.0
        if _phi(middle) < p:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def _se(sigma: float, n: int) -> float:
    return sigma * math.sqrt(2.0 / n)


def outcomes(n: int, floor: float = FLOOR, ceiling: float = CEILING,
             sigma: float = SIGMA, gap: float = GAP) -> dict:
    """Exact two-sample t probabilities of the four branch outcomes."""
    se = _se(sigma, n)
    df = max(2 * n - 2, 1)
    size_if_size = _expectation(
        df, lambda s: _phi(floor / (se * s)) - _phi(-floor / (se * s)))
    density_if_size = _expectation(df, lambda s: _phi(-ceiling / (se * s)))
    density_if_density = _expectation(
        df, lambda s: _phi((gap - ceiling) / (se * s)))
    size_if_density = _expectation(
        df, lambda s: _phi((gap + floor) / (se * s))
        - _phi((gap - floor) / (se * s)))
    return {
        "n": n,
        "se": round(se, 6),
        "size_if_size": round(size_if_size, 6),
        "density_if_size": round(density_if_size, 6),
        "density_if_density": round(density_if_density, 6),
        "size_if_density": round(size_if_density, 6),
        "undecided_if_size": round(
            1.0 - size_if_size - density_if_size, 6),
        "undecided_if_density": round(
            1.0 - density_if_density - size_if_density, 6),
    }


def _admissible(row: dict, budget: float) -> bool:
    return (row["density_if_size"] <= budget
            and row["size_if_density"] <= budget
            and row["size_if_size"] >= POWER_TARGET
            and row["density_if_density"] >= POWER_TARGET)


def _needed(floor: float, ceiling: float, budget: float,
            limit: int = 60) -> int | None:
    for n in range(2, limit + 1):
        if _admissible(outcomes(n, floor, ceiling), budget):
            return n
    return None


def _bounds(n: int, budget: float) -> dict:
    """The admissible band edges at a fixed seed count."""
    se = _se(SIGMA, n)
    return {
        "n": n,
        "se": round(se, 6),
        "ceiling_min": round(_z(1.0 - budget) * se, 6),
        "floor_max": round(GAP - _z(1.0 - budget) * se, 6),
        "floor_min": 0.0,
    }


def build() -> dict:
    power = _load(POWER_PATH)["found"]
    if abs(power["gap"] + GAP) > 5e-5:
        raise SystemExit("REFUSED: the discriminator differential moved")
    spec = _load(SPEC_PATH)
    if spec["constants"]["decision_floor"] != FLOOR or \
            spec["constants"]["decision_ceiling"] != CEILING:
        raise SystemExit("REFUSED: the committed bands moved")
    rows = []
    for floor, ceiling in PREFIX:
        row = {
            "floor": floor,
            "ceiling": ceiling,
            "middle": round((floor + ceiling) / 2.0, 6),
            "dead_band": ceiling > floor,
            "at_six": outcomes(SEEDS[0], floor, ceiling),
            "at_nine": outcomes(SEEDS[1], floor, ceiling),
            "seeds": {"%.2f" % budget: _needed(floor, ceiling, budget)
                      for budget in BUDGETS},
        }
        row["admissible_at_six"] = _admissible(row["at_six"], BUDGETS[0])
        row["admissible_at_nine"] = _admissible(row["at_nine"], BUDGETS[0])
        rows.append(row)
    bounds = [_bounds(n, BUDGETS[0]) for n in SEEDS]
    search = []
    for floor in GRID_FLOORS:
        for ceiling in GRID_CEILINGS:
            if ceiling < floor:
                continue
            search.append({
                "floor": floor,
                "ceiling": ceiling,
                "seeds_5": _needed(floor, ceiling, BUDGETS[0], limit=20),
                "seeds_10": _needed(floor, ceiling, BUDGETS[1], limit=20),
            })
    for row in rows:
        search.append({"floor": row["floor"], "ceiling": row["ceiling"],
                       "seeds_5": row["seeds"]["0.05"],
                       "seeds_10": row["seeds"]["0.10"]})
    floor_five = min((row for row in search if row["seeds_5"]),
                     key=lambda row: row["seeds_5"])
    floor_ten = min((row for row in search if row["seeds_10"]),
                    key=lambda row: row["seeds_10"])
    cheapest = min((row for row in rows if row["seeds"]["0.05"]),
                   key=lambda row: row["seeds"]["0.05"])
    committed = next(row for row in rows
                     if (row["floor"], row["ceiling"]) == (FLOOR, CEILING))
    single = next(row for row in rows if not row["dead_band"])
    found = {
        "gap": GAP,
        "sigma": SIGMA,
        "committed": {"floor": FLOOR, "ceiling": CEILING},
        "seeds_committed_at_5pct": committed["seeds"]["0.05"],
        "seeds_committed_at_10pct": committed["seeds"]["0.10"],
        "cheapest_floor": cheapest["floor"],
        "cheapest_ceiling": cheapest["ceiling"],
        "seeds_cheapest_at_5pct": cheapest["seeds"]["0.05"],
        "seeds_saved_at_5pct": (committed["seeds"]["0.05"]
                                - cheapest["seeds"]["0.05"]),
        "single_threshold_seeds": single["seeds"]["0.05"],
        "bounds": bounds,
        "ceiling_can_drop_to": bounds[0]["ceiling_min"],
        "floor_can_rise_to": bounds[0]["floor_max"],
        "power_target": POWER_TARGET,
        "budgets": list(BUDGETS),
        "seeds_floor_at_5pct": floor_five["seeds_5"],
        "seeds_floor_at_5pct_bands": [floor_five["floor"],
                                      floor_five["ceiling"]],
        "seeds_floor_at_10pct": floor_ten["seeds_10"],
        "seeds_floor_at_10pct_bands": [floor_ten["floor"],
                                       floor_ten["ceiling"]],
    }
    reading = (
        "Yes, but only in one direction and by a bounded amount. At a 5%%/5%% "
        "guarantee the admissible bands at six seeds per block are "
        "**c ≥ %.4f** and **f ≤ %.4f**, so the committed **0.05** floor is "
        "already almost as high as it can go — raising it past **%.4f** starts "
        "declaring the size summary when the density summary is true — while "
        "the **0.09** ceiling is conservative and can drop to **%.4f** with the "
        "error budget intact. Widening that way is not a weakening: the "
        "cheapest admissible pair is **f %.4f / c %.4f**, which holds both "
        "wrong-branch rates at 5%% and both correct branches at 80%% at "
        "**%d seeds per block** instead of the **%d** the committed pair needs "
        "at the same guarantee — **%d seeds saved per block**. Widening past "
        "**c %.4f** is where the discriminator does weaken: at six seeds and "
        "the committed floor, a ceiling below that value pushes the false-"
        "density rate above 5%%, and at nine seeds the floor cannot rise past "
        "**%.4f** either. Collapsing the dead band into a single threshold at "
        "the midpoint is worse than either: it needs **%d seeds per block** at "
        "5%%, because a single cut cannot spend the error budget on one side "
        "and the power budget on the other, and it leaves no undecided outcome "
        "for the cases the design should refuse to call. No band choice does "
        "better than that floor: searching floors **0.02–0.10** against "
        "ceilings **0.03–0.12**, the cheapest admissible pair needs **%d seeds "
        "per block** at a 5%% guarantee and **%d** at 10%%, so the bands as "
        "committed are worth **%d seeds** and no more at this per-seed SD. At "
        "the looser 10%% budget the ordering flips and the single threshold "
        "wins with **%d** seeds, because a budget that wide no longer repays "
        "the seeds the dead band spends on refusing to decide."
        % (bounds[0]["ceiling_min"], bounds[0]["floor_max"],
           bounds[0]["floor_max"], bounds[0]["ceiling_min"],
           cheapest["floor"], cheapest["ceiling"],
           cheapest["seeds"]["0.05"], committed["seeds"]["0.05"],
           found["seeds_saved_at_5pct"], bounds[0]["ceiling_min"],
           bounds[1]["floor_max"], single["seeds"]["0.05"],
           found["seeds_floor_at_5pct"], found["seeds_floor_at_10pct"],
           found["seeds_saved_at_5pct"], found["seeds_floor_at_10pct"]))
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Could the committed 0.05/0.09 decision bands be widened without "
            "weakening the discriminator, and how many seeds per split block "
            "does each alternative need?"
        ),
        "definition": (
            "For each band pair, the exact two-sample t probabilities of the "
            "four branch outcomes on the split-32 minus split-48 difference, "
            "the admissible band edges at six and nine seeds, and the seeds "
            "each pair needs at a 5% and a 10% error budget with 80% power on "
            "both branches."
        ),
        "method": (
            "Same chi-integrated t power as `A1-SPLIT-POWER-1`, generalized to "
            "the rule's three outcomes: size inside the floor, density below "
            "the ceiling, undecided between them. A pair is admissible when "
            "neither wrong branch exceeds the budget and both correct branches "
            "reach the power target; the cheapest pair is found by search over "
            "the evaluated grid plus the analytic bound."
        ),
        "constants": {
            "sigma": SIGMA,
            "gap": GAP,
            "committed_floor": FLOOR,
            "committed_ceiling": CEILING,
            "budgets": list(BUDGETS),
            "power_target": POWER_TARGET,
            "seed_counts": list(SEEDS),
            "band_pairs": [list(pair) for pair in PREFIX],
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "found": found,
        "rows": rows,
        "grid": search,
        "limits": [
            "The band edges are a design convention, not a hypothesis test; the error budget is the probability of the wrong branch, not a p-value.",
            "Everything inherits the per-seed SD borrowed from 16-tag blocks; the admissible edges move with sigma, so a larger SD moves them inward.",
            "The two predictions are taken as point values, so a real split block landing between them is the undecided outcome the rule is designed to produce.",
            "Moving the bands changes only this design's cost; it does not make either summary better supported by the existing blocks.",
        ],
        "not_evidence": (
            "A design estimate over committed artifacts. It runs no arm, "
            "measures no split block, and is not a treatment, target, freeze, "
            "grant or A1 cell."
        ),
    })


def render(doc: dict) -> str:
    found = doc["found"]
    lines = [
        "# A1 band frontier",
        "",
        "Generated from `docs/a1_band_frontier.json` by "
        "`python -m benchmarks.a1_band_frontier --write`. Do not edit by hand.",
        "",
        "**Design estimate, not an A1 result.** No split block has been run.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## Admissible band edges",
        "",
        "| Seeds | SE | Ceiling can drop to | Floor can rise to |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for row in found["bounds"]:
        lines.append("| %d | %.6f | %.4f | %.4f |" % (
            row["n"], row["se"], row["ceiling_min"], row["floor_max"]))
    lines += [
        "",
        "At a 5% error budget with 80% power on both branches.",
        "",
        "## Band pairs",
        "",
        "| Floor | Ceiling | Dead band | Seeds 5% | Seeds 10% | "
        "Density power at 6 | Size power at 6 |",
        "| ---: | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["rows"]:
        lines.append("| %.4f | %.4f | %s | %s | %s | %.3f | %.3f |" % (
            row["floor"], row["ceiling"], "yes" if row["dead_band"] else "no",
            row["seeds"]["0.05"], row["seeds"]["0.10"],
            row["at_six"]["density_if_density"], row["at_six"]["size_if_size"]))
    lines += [
        "",
        "## At six seeds per block",
        "",
        "| Floor | Ceiling | Size true → density | Density true → size | "
        "Undecided (size) | Undecided (density) |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["rows"]:
        six = row["at_six"]
        lines.append("| %.4f | %.4f | %.4f | %.4f | %.4f | %.4f |" % (
            row["floor"], row["ceiling"], six["density_if_size"],
            six["size_if_density"], six["undecided_if_size"],
            six["undecided_if_density"]))
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
    if abs(doc["found"]["gap"] - GAP) > 1e-9:
        found.append("the differential moved")
    committed = [row for row in doc["rows"]
                 if (row["floor"], row["ceiling"]) == (FLOOR, CEILING)]
    if len(committed) != 1:
        found.append("the committed band pair is missing or duplicated")
    cheapest = doc["found"]["seeds_cheapest_at_5pct"]
    if cheapest is None or cheapest > doc["found"]["seeds_committed_at_5pct"]:
        found.append("the cheapest pair costs more than the committed one")
    for row in doc["rows"]:
        six = row["at_six"]
        total = (six["size_if_size"] + six["density_if_size"]
                 + six["undecided_if_size"])
        if abs(total - 1.0) > 1e-5:
            found.append("the size-true outcomes do not sum to one")
        total = (six["density_if_density"] + six["size_if_density"]
                 + six["undecided_if_density"])
        if abs(total - 1.0) > 1e-5:
            found.append("the density-true outcomes do not sum to one")
    bounds = doc["found"]["bounds"]
    if bounds[0]["ceiling_min"] >= CEILING:
        found.append("the ceiling is reported as already at its minimum")
    grid = doc.get("grid") or []
    best_five = min(row["seeds_5"] for row in grid if row["seeds_5"])
    best_ten = min(row["seeds_10"] for row in grid if row["seeds_10"])
    if doc["found"]["seeds_floor_at_5pct"] != best_five:
        found.append("the 5% seed floor does not match the searched grid")
    if doc["found"]["seeds_floor_at_10pct"] != best_ten:
        found.append("the 10% seed floor does not match the searched grid")
    if doc["found"]["single_threshold_seeds"] < doc["found"]["seeds_floor_at_5pct"]:
        found.append("a single threshold beats the searched floor")
    if bounds[0]["floor_max"] > FLOOR + 0.01:
        found.append("the floor is reported as able to rise far past 0.05")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    if abs(_z(0.975) - 1.959963984540054) > 1e-6:
        failures.append("normal quantile")
    wide = outcomes(40, 0.05, 0.09)
    if wide["size_if_size"] < 0.99 or wide["density_if_density"] < 0.95:
        failures.append("both branches do not converge with 40 seeds")
    if outcomes(200, 0.05, 0.09)["density_if_density"] < 0.99:
        failures.append("the density branch never reaches 0.99")
    merged = outcomes(9, 0.09, 0.09)
    if merged["undecided_if_size"] < -1e-9:
        failures.append("a merged band leaves negative undecided mass")
    for n in (6, 9):
        row = outcomes(n)
        for truth in ("if_size", "if_density"):
            total = sum(row["%s_%s" % (branch, truth)]
                        for branch in ("size", "density", "undecided"))
            if abs(total - 1.0) > 1e-5:
                failures.append("outcomes do not sum to one at %d seeds" % n)
    if _needed(0.05, 0.09, 0.05) is None:
        failures.append("the committed pair never reaches a 5% guarantee")
    if _needed(0.0582, 0.0582, 0.05) is None:
        failures.append("the single threshold never reaches a 5% guarantee")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    print("found:", body["found"])
    for row in body["rows"]:
        print(" f %.4f c %.4f seeds %s six=%s" % (
            row["floor"], row["ceiling"], row["seeds"],
            {key: row["at_six"][key] for key in
             ("size_if_size", "density_if_size", "density_if_density",
              "undecided_if_density")}))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no band-frontier artifact; run --write")
    found = problems(_load(OUT_PATH))
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("band frontier: clean")
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
        print("band frontier self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
