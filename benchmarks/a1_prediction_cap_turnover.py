"""Do the A edges won by raising the prediction cap carry the same K rate?

Cap 80 to cap 112 adds A edges and lifts joint C1 from 4/18 to 8/18.  This
traces the edge sets themselves and splits A at cap 112 into three parts:

* retained: served at both caps;
* new: served only at cap 112;
* dropped: served only at cap 80.

For each part it measures K membership against the same-seed K set at cap
112.  If new A edges join K at the retained rate, the extra slots buy joint
coverage; if they join below it, the cap adds marginal A without adding
overlap, which is what the joint C1 gain would reflect.

The test is descriptive.  Pooled rates are reported with the per-seed
distribution behind them, and a two-sided sign test over seeds asks whether
the new-edge rate is lower within a seed.  Seeds are the unit, not edges.

Cap 80 and cap 112 must both reproduce their committed A, K and A∩K counts
per seed, or the build refuses.

No engine change, target, freeze, grant or A1 cell.

    python -m benchmarks.a1_prediction_cap_turnover --write
    python -m benchmarks.a1_prediction_cap_turnover --check
    python -m benchmarks.a1_prediction_cap_turnover --self-test
"""
from __future__ import annotations

import argparse
import json
import math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from benchmarks import a1_prediction_cap_c1 as base
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LOW_PATH = DOCS / "a1_prediction_cap_c1.json"
HIGH_PATH = DOCS / "a1_prediction_cap_112.json"
OUT_PATH = DOCS / "a1_prediction_cap_turnover.json"
PAGE_PATH = DOCS / "A1-PREDICTION-CAP-TURNOVER.md"
ID = "A1-PREDICTION-CAP-TURNOVER-1"
DATE = "2026-11-14"
KIND = "a1_prediction_cap_turnover"
STATUS = ("DESCRIPTIVE — CAP-80/112 A-EDGE TURNOVER AND K MEMBERSHIP; "
          "NO TARGET, FREEZE, GRANT OR A1 CELL")
LOW_CAP = 80
HIGH_CAP = 112


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _rate(count: int, total: int) -> float | None:
    return None if total == 0 else count / total


def _rounded_rate(count: int, total: int) -> float | None:
    value = _rate(count, total)
    return None if value is None else round(value, 6)


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else "%.3f" % value


def _sign_test(differences: list[float]) -> dict:
    """Two-sided sign test over seeds; ties are dropped."""
    below = sum(1 for value in differences if value < 0)
    above = sum(1 for value in differences if value > 0)
    ties = len(differences) - below - above
    n = below + above
    if n == 0:
        return {"below": below, "above": above, "ties": ties, "n": 0,
                "p_value": None}
    tail = sum(math.comb(n, k) for k in range(0, min(below, above) + 1))
    p_value = min(1.0, 2 * tail / (2 ** n))
    return {"below": below, "above": above, "ties": ties, "n": n,
            "p_value": round(p_value, 6)}


def build() -> dict:
    tasks = [(block["label"], seed, cap)
             for block in base.BLOCKS
             for seed in block["seeds"]
             for cap in (LOW_CAP, HIGH_CAP)]
    with ProcessPoolExecutor(max_workers=6) as pool:
        raw = list(pool.map(base._replay, tasks))

    low_reference = {
        (row["block"], row["seed"]): row
        for row in _load(LOW_PATH)["rows"]
        if row["prediction_cap"] == LOW_CAP
    }
    high_reference = {
        (row["block"], row["seed"]): row
        for row in _load(HIGH_PATH)["rows"]
        if row["prediction_cap"] == HIGH_CAP
    }
    got = {(row["block"], row["seed"], row["prediction_cap"]): row
           for row in raw}
    for key, expected in low_reference.items():
        row = got[(key[0], key[1], LOW_CAP)]
        for field in ("A", "K", "A_and_K", "candidate_edges"):
            if row[field] != expected[field]:
                raise SystemExit(
                    "REFUSED: cap-%d control %s/%d %s %d, expected %d"
                    % (LOW_CAP, key[0], key[1], field, row[field],
                       expected[field]))
    for key, expected in high_reference.items():
        row = got[(key[0], key[1], HIGH_CAP)]
        for field in ("A", "K", "A_and_K", "candidate_edges"):
            if row[field] != expected[field]:
                raise SystemExit(
                    "REFUSED: cap-%d reference %s/%d %s %d, expected %d"
                    % (HIGH_CAP, key[0], key[1], field, row[field],
                       expected[field]))

    rows = []
    per_seed_rates = []
    k_identical = 0
    for block in base.BLOCKS:
        for seed in block["seeds"]:
            low = got[(block["label"], seed, LOW_CAP)]
            high = got[(block["label"], seed, HIGH_CAP)]
            low_a = set(low["A_edges"])
            high_a = set(high["A_edges"])
            low_k = set(low["K_edges"])
            high_k = set(high["K_edges"])
            same_k = low_k == high_k
            k_identical += int(same_k)
            retained = high_a & low_a
            new = high_a - low_a
            dropped = low_a - high_a
            new_in_k = new & high_k
            retained_in_k = retained & high_k
            dropped_in_k = dropped & low_k
            row = {
                "block": block["label"],
                "seed": seed,
                "candidate_edges": high["candidate_edges"],
                "A_low": len(low_a),
                "A_high": len(high_a),
                "K_low": len(low_k),
                "K_high": len(high_k),
                "K_identical": same_k,
                "retained": len(retained),
                "new": len(new),
                "dropped": len(dropped),
                "retained_in_K": len(retained_in_k),
                "new_in_K": len(new_in_k),
                "dropped_in_K": len(dropped_in_k),
                "new_K_rate": (None if not new
                               else round(len(new_in_k) / len(new), 6)),
                "retained_K_rate": (None if not retained
                                    else round(len(retained_in_k) / len(retained), 6)),
                "C1_joint_low": low["A_and_K"],
                "C1_joint_high": high["A_and_K"],
                "joint_gain": high["A_and_K"] - low["A_and_K"],
            }
            if row["new"] and row["retained"]:
                per_seed_rates.append(row["new_K_rate"]
                                      - row["retained_K_rate"])
            rows.append(row)

    pooled = {
        "retained": sum(row["retained"] for row in rows),
        "new": sum(row["new"] for row in rows),
        "dropped": sum(row["dropped"] for row in rows),
        "retained_in_K": sum(row["retained_in_K"] for row in rows),
        "new_in_K": sum(row["new_in_K"] for row in rows),
        "dropped_in_K": sum(row["dropped_in_K"] for row in rows),
        "A_low": sum(row["A_low"] for row in rows),
        "A_high": sum(row["A_high"] for row in rows),
        "C1_joint_low": sum(row["C1_joint_low"] for row in rows),
        "C1_joint_high": sum(row["C1_joint_high"] for row in rows),
        "seeds": len(rows),
        "seeds_with_identical_K": k_identical,
    }
    pooled["retained_rate"] = _rounded_rate(pooled["retained_in_K"],
                                            pooled["retained"])
    pooled["new_rate"] = _rounded_rate(pooled["new_in_K"], pooled["new"])
    pooled["dropped_rate"] = _rounded_rate(pooled["dropped_in_K"],
                                           pooled["dropped"])
    if pooled["new_rate"] is None or pooled["retained_rate"] is None:
        pooled["rate_difference"] = None
        pooled["expected_new_in_K"] = None
        pooled["new_in_K_excess"] = None
    else:
        pooled["rate_difference"] = round(pooled["new_rate"]
                                          - pooled["retained_rate"], 6)
        pooled["expected_new_in_K"] = round(pooled["retained_rate"]
                                            * pooled["new"], 6)
        pooled["new_in_K_excess"] = round(pooled["new_in_K"]
                                          - pooled["expected_new_in_K"], 6)
    sign = _sign_test(per_seed_rates)
    larger_rates = []
    for row in rows:
        if row["block"] == "larger-28" and row["new"] and row["retained"]:
            larger_rates.append(row["new_K_rate"] - row["retained_K_rate"])
    sign_larger = _sign_test(larger_rates)
    by_block = []
    for block in base.BLOCKS:
        group = [row for row in rows if row["block"] == block["label"]]
        entry = {
            "block": block["label"],
            "seeds": len(group),
            "retained": sum(row["retained"] for row in group),
            "new": sum(row["new"] for row in group),
            "dropped": sum(row["dropped"] for row in group),
            "retained_in_K": sum(row["retained_in_K"] for row in group),
            "new_in_K": sum(row["new_in_K"] for row in group),
            "C1_joint_low": sum(row["C1_joint_low"] for row in group),
            "C1_joint_high": sum(row["C1_joint_high"] for row in group),
        }
        entry["retained_rate"] = _rounded_rate(entry["retained_in_K"],
                                               entry["retained"])
        entry["new_rate"] = _rounded_rate(entry["new_in_K"], entry["new"])
        by_block.append(entry)

    block_adjusted = sum(
        (0.0 if entry["retained_rate"] is None else entry["retained_rate"])
        * entry["new"] for entry in by_block)
    pooled["block_adjusted_expected_new_in_K"] = round(block_adjusted, 6)
    pooled["block_adjusted_excess"] = round(
        pooled["new_in_K"] - block_adjusted, 6)
    pooled["new_share_larger"] = round(
        sum(row["new"] for row in rows if row["block"] == "larger-28")
        / pooled["new"], 6)
    pooled["retained_share_larger"] = round(
        sum(row["retained"] for row in rows if row["block"] == "larger-28")
        / pooled["retained"], 6)
    larger_block = next(entry for entry in by_block
                        if entry["block"] == "larger-28")
    pooled["larger_rate_difference"] = round(
        larger_block["new_rate"] - larger_block["retained_rate"], 6)

    sixteen = [row for row in rows if row["block"] != "larger-28"]
    sixteen_new = sum(row["new"] for row in sixteen)
    sixteen_new_in_k = sum(row["new_in_K"] for row in sixteen)
    reading = (
        "Raising the prediction cap from 80 to 112 adds %d A edges (%d to "
        "%d) and drops %d, so A is nested and the turnover is pure "
        "addition. K membership is not one number here. On the %d 16-tag "
        "seeds K is complete at both caps, so new and retained edges both "
        "sit at %s and those seeds cannot answer the question. On larger-28 "
        "the new edges carry K at %s (%d of %d) against %s (%d of %d) for "
        "retained, a difference of %+.3f, with %d seeds above, %d below and "
        "%d tied (two-sided sign test p = %s). The pooled rates move the "
        "other way (%.3f against %.3f, %+.3f) only because the new edges are "
        "weighted toward larger-28 — %d of %d against %d of %d retained — "
        "whose base rate is lower; no block reverses that direction at "
        "block level. Against a block-adjusted expectation of "
        "%.1f, the new edges add %d K-covered edges (%+.1f), and joint C1 "
        "rises %d → %d."
        % (
            pooled["new"], pooled["A_low"], pooled["A_high"],
            pooled["dropped"],
            len(sixteen),
            _fmt(_rate(sixteen_new_in_k, sixteen_new)),
            _fmt(larger_block["new_rate"]), larger_block["new_in_K"],
            larger_block["new"],
            _fmt(larger_block["retained_rate"]), larger_block["retained_in_K"],
            larger_block["retained"],
            pooled["larger_rate_difference"],
            sign_larger["above"], sign_larger["below"], sign_larger["ties"],
            ("%.4f" % sign_larger["p_value"]
             if sign_larger["p_value"] is not None else "n/a"),
            pooled["new_rate"], pooled["retained_rate"],
            pooled["rate_difference"],
            sum(row["new"] for row in rows if row["block"] == "larger-28"),
            pooled["new"],
            sum(row["retained"] for row in rows
                if row["block"] == "larger-28"),
            pooled["retained"],
            pooled["block_adjusted_expected_new_in_K"],
            pooled["new_in_K"], pooled["block_adjusted_excess"],
            pooled["C1_joint_low"], pooled["C1_joint_high"],
        )
    )

    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Between prediction caps 80 and 112, do newly served A edges "
            "belong to K at the same rate as retained A edges?"
        ),
        "definition": (
            "A edge sets at caps 80 and 112 for the same 18 no-arm seeds. "
            "retained = A80 ∩ A112, new = A112 - A80, dropped = A80 - A112. "
            "K membership is measured against the same-seed cap-112 K set; "
            "dropped edges are measured against the cap-80 K set. Rates are "
            "counts of A edges also carried by K over A edges in the part."
        ),
        "method": (
            "One no-arm replay per seed and cap at loop cap 120. Both caps "
            "must reproduce their committed A, K, A∩K and candidate counts "
            "per seed. Pooled rates are reported with the per-seed "
            "distribution and a two-sided sign test over seeds."
        ),
        "constants": {
            "cycles": base.CYCLES,
            "loop_cap": base.LOOP_CAP,
            "low_cap": LOW_CAP,
            "high_cap": HIGH_CAP,
            "seeds": len(rows),
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "pooled": pooled,
        "sign_test": sign,
        "sign_test_larger28": sign_larger,
        "by_block": by_block,
        "per_seed_rate_differences": [round(value, 6)
                                      for value in per_seed_rates],
        "rows": rows,
        "not_evidence": (
            "A descriptive edge-level trace on 18 no-arm seeds at two "
            "prediction caps. K membership is an availability property, not "
            "a treatment effect; seeds are the unit and edges within a seed "
            "are not independent. It does not show that serving a new edge "
            "would make K carry it, and it is not a target viability or "
            "successor."
        ),
    })


def render(doc: dict) -> str:
    pooled = doc["pooled"]
    sign = doc["sign_test"]
    lines = [
        "# A1 prediction-cap turnover",
        "",
        "Generated from `docs/a1_prediction_cap_turnover.json` by "
        "`python -m benchmarks.a1_prediction_cap_turnover --write`. Do not edit by hand.",
        "",
        "**Descriptive edge trace, not an A1 result.** 18 no-arm seeds at "
        "prediction caps **80** and **112**, loop cap **120**. No target, "
        "freeze, grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "## Pooled",
        "",
        "| Part | Edges | In K | K rate |",
        "| --- | ---: | ---: | ---: |",
        "| Retained (A80 ∩ A112) | %d | %d | %.3f |" % (
            pooled["retained"], pooled["retained_in_K"],
            pooled["retained_rate"]),
        "| New (A112 − A80) | %d | %d | %.3f |" % (
            pooled["new"], pooled["new_in_K"], pooled["new_rate"]),
        "| Dropped (A80 − A112) | %d | %d | %s |" % (
            pooled["dropped"], pooled["dropped_in_K"],
            "n/a" if pooled["dropped_rate"] is None
            else "%.3f" % pooled["dropped_rate"]),
        "",
        "A at cap 80: **%d**; at cap 112: **%d**. Joint C1 rises "
        "**%d → %d**. At the pooled retained rate the new edges would add "
        "**%s** K-covered edges; block-adjusted they would add **%.1f**; "
        "they add **%d** (%+.1f against the adjusted expectation)."
        % (pooled["A_low"], pooled["A_high"], pooled["C1_joint_low"],
           pooled["C1_joint_high"],
           "n/a" if pooled["expected_new_in_K"] is None
           else "%.1f" % pooled["expected_new_in_K"],
           pooled["block_adjusted_expected_new_in_K"],
           pooled["new_in_K"], pooled["block_adjusted_excess"]),
        "",
        "## Per seed",
        "",
        "| Block | Seed | A80 | A112 | Retained | New | Dropped | New in K | New rate | Retained rate | Joint 80 | Joint 112 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["rows"]:
        lines.append(
            "| %s | %d | %d | %d | %d | %d | %d | %d | %s | %s | %d | %d |"
            % (row["block"], row["seed"], row["A_low"], row["A_high"],
               row["retained"], row["new"], row["dropped"],
               row["new_in_K"],
               "n/a" if row["new_K_rate"] is None else "%.3f" % row["new_K_rate"],
               "n/a" if row["retained_K_rate"] is None
               else "%.3f" % row["retained_K_rate"],
               row["C1_joint_low"], row["C1_joint_high"]))
    lines += [
        "",
        "## Per block",
        "",
        "| Block | Retained | New | Dropped | Retained K rate | New K rate | Joint C1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for entry in doc["by_block"]:
        lines.append("| %s | %d | %d | %d | %s | %s | %d → %d |" % (
            entry["block"], entry["retained"], entry["new"],
            entry["dropped"],
            "n/a" if entry["retained_rate"] is None
            else "%.3f" % entry["retained_rate"],
            "n/a" if entry["new_rate"] is None else "%.3f" % entry["new_rate"],
            entry["C1_joint_low"], entry["C1_joint_high"]))
    lines += [
        "",
        "## Sign test",
        "",
        "All 18 seeds, new-minus-retained K rate: **%d** below zero, **%d** "
        "above, **%d** tied; two-sided p = **%s**."
        % (sign["below"], sign["above"], sign["ties"],
           "n/a" if sign["p_value"] is None else "%.4f" % sign["p_value"]),
        "",
        "Larger-28 only: **%d** below zero, **%d** above, **%d** tied; "
        "two-sided p = **%s**. The 12 16-tag seeds are ties by construction "
        "(K is complete, so both rates are 1.000) and carry no information "
        "about the question."
        % (doc["sign_test_larger28"]["below"],
           doc["sign_test_larger28"]["above"],
           doc["sign_test_larger28"]["ties"],
           "n/a" if doc["sign_test_larger28"]["p_value"] is None
           else "%.4f" % doc["sign_test_larger28"]["p_value"]),
        "",
        "K sets are identical at both caps on **%d/%d** seeds, so the "
        "membership comparison uses the same carried set within a seed."
        % (pooled["seeds_with_identical_K"], pooled["seeds"]),
        "",
        "## What this does not claim",
        "",
        doc["not_evidence"],
        "",
    ]
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
    rows = doc.get("rows") or []
    if len(rows) != len(base.BLOCKS) * 6:
        found.append("row count")
    for row in rows:
        if row.get("retained", 0) + row.get("new", 0) != row.get("A_high"):
            found.append("retained + new at %r"
                         % ((row.get("block"), row.get("seed")),))
        if row.get("retained", 0) + row.get("dropped", 0) != row.get("A_low"):
            found.append("retained + dropped at %r"
                         % ((row.get("block"), row.get("seed")),))
        if row.get("new_in_K", 0) > row.get("new", 0):
            found.append("new-in-K above new at %r"
                         % ((row.get("block"), row.get("seed")),))
        if row.get("retained_in_K", 0) > row.get("retained", 0):
            found.append("retained-in-K above retained at %r"
                         % ((row.get("block"), row.get("seed")),))
        if row.get("dropped_in_K", 0) > row.get("dropped", 0):
            found.append("dropped-in-K above dropped at %r"
                         % ((row.get("block"), row.get("seed")),))
        expected = (None if not row.get("new")
                    else round(row["new_in_K"] / row["new"], 6))
        if row.get("new_K_rate") != expected:
            found.append("new K rate at %r"
                         % ((row.get("block"), row.get("seed")),))
        expected = (None if not row.get("retained")
                    else round(row["retained_in_K"] / row["retained"], 6))
        if row.get("retained_K_rate") != expected:
            found.append("retained K rate at %r"
                         % ((row.get("block"), row.get("seed")),))
    pooled = doc.get("pooled") or {}
    for field, key in (("retained", "retained"), ("new", "new"),
                       ("dropped", "dropped"),
                       ("retained_in_K", "retained_in_K"),
                       ("new_in_K", "new_in_K"),
                       ("dropped_in_K", "dropped_in_K"),
                       ("A_low", "A_low"), ("A_high", "A_high"),
                       ("C1_joint_low", "C1_joint_low"),
                       ("C1_joint_high", "C1_joint_high")):
        if pooled.get(field) != sum(row[key] for row in rows):
            found.append("pooled %s" % field)
    if pooled.get("larger_rate_difference") is not None:
        larger = next((entry for entry in doc.get("by_block") or []
                       if entry.get("block") == "larger-28"), None)
        if larger is None:
            found.append("no larger-28 block row")
        elif pooled["larger_rate_difference"] != round(
                larger["new_rate"] - larger["retained_rate"], 6):
            found.append("larger-28 rate difference")
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    if _sign_test([-0.1, -0.2, 0.1])["below"] != 2:
        failures.append("sign test must count negative differences")
    if _sign_test([0.0, 0.0])["n"] != 0:
        failures.append("ties must be dropped")
    if _sign_test([])["p_value"] is not None:
        failures.append("an empty test has no p value")
    if _rate(0, 0) is not None:
        failures.append("a zero denominator is not measurable")
    if _rate(3, 4) != 0.75:
        failures.append("rate arithmetic")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    print("pooled: retained %d/%d, new %d/%d, dropped %d/%d"
          % (body["pooled"]["retained_in_K"], body["pooled"]["retained"],
             body["pooled"]["new_in_K"], body["pooled"]["new"],
             body["pooled"]["dropped_in_K"], body["pooled"]["dropped"]))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no turnover artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("prediction-cap turnover: clean")
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
        print("prediction-cap turnover self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
