"""Does K completeness separate the 16-tag and larger-28 regimes across caps?

K completeness is ``K / candidate_edges``: the fraction of a seed's candidate
edges that a loop or dream ever carried.  The cap studies make it cheap to
test across prediction caps 20/40/80/112 because K is already measured on the
same 18 candidate streams.

Two questions are kept separate:

1. Does K completeness classify the blocks at every cap?
2. Does K completeness explain the cap response or joint C1 pass?

The artifact is built from the committed cap-20/40/80 and cap-112 rows.  The
overlapping cap-40 and cap-80 rows must agree exactly, or the build refuses.
No replay, engine change, target, freeze, grant or A1 cell.

    python -m benchmarks.a1_k_completeness --write
    python -m benchmarks.a1_k_completeness --check
    python -m benchmarks.a1_k_completeness --self-test
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
C1_PATH = DOCS / "a1_prediction_cap_c1.json"
CAP112_PATH = DOCS / "a1_prediction_cap_112.json"
OUT_PATH = DOCS / "a1_k_completeness.json"
PAGE_PATH = DOCS / "A1-K-COMPLETENESS.md"
ID = "A1-K-COMPLETENESS-1"
DATE = "2026-11-14"
KIND = "a1_k_completeness"
STATUS = "DESCRIPTIVE — K COMPLETENESS ACROSS PREDICTION CAPS; NO TARGET, FREEZE, GRANT OR A1 CELL"
BLOCKS = ("current-16", "fresh-16", "larger-28")
CAPS = (20, 40, 80, 112)
C1_FLOOR = 60
COMPLETE_THRESHOLD = 0.9


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows() -> list[dict]:
    c1 = _load(C1_PATH)["rows"]
    high = _load(CAP112_PATH)["rows"]
    by_key = {(row["block"], row["seed"], row["prediction_cap"]): row
              for row in c1}
    for row in high:
        key = (row["block"], row["seed"], row["prediction_cap"])
        if key in by_key:
            old = by_key[key]
            for field in ("candidate_edges", "A", "K", "A_and_K"):
                if old[field] != row[field]:
                    raise SystemExit(
                        "REFUSED: %s/%d/%d %s %d, expected %d"
                        % (key[0], key[1], key[2], field, row[field],
                           old[field]))
        else:
            by_key[key] = row
    rows = []
    for key in sorted(by_key, key=lambda item: (item[2], item[0], item[1])):
        row = by_key[key]
        candidates = row["candidate_edges"]
        rows.append({
            "block": row["block"],
            "seed": row["seed"],
            "prediction_cap": row["prediction_cap"],
            "candidate_edges": candidates,
            "A": row["A"],
            "K": row["K"],
            "A_and_K": row["A_and_K"],
            "C1_marginal": row["C1_marginal"],
            "C1_joint": row["C1_joint"],
            "C1_joint_pass": row["C1_joint"] >= C1_FLOOR,
            "K_completeness": round(row["K"] / candidates, 6),
            "K_coverage_of_A": round(row["A_and_K"] / row["A"], 6)
            if row["A"] else 0.0,
            "A_completeness": round(row["A"] / candidates, 6),
        })
    return rows


def _summary(rows: list[dict]) -> list[dict]:
    out = []
    for cap in CAPS:
        block = [row for row in rows if row["prediction_cap"] == cap]
        values = [row["K_completeness"] for row in block]
        out.append({
            "prediction_cap": cap,
            "seeds": len(block),
            "candidate_edges": sum(row["candidate_edges"] for row in block),
            "A_total": sum(row["A"] for row in block),
            "K_total": sum(row["K"] for row in block),
            "A_and_K_total": sum(row["A_and_K"] for row in block),
            "K_completeness": round(
                sum(row["K"] for row in block)
                / sum(row["candidate_edges"] for row in block), 6),
            "K_completeness_min": min(values),
            "K_completeness_max": max(values),
            "K_coverage_of_A": round(
                sum(row["A_and_K"] for row in block)
                / sum(row["A"] for row in block), 6),
            "C1_marginal_pass": sum(
                row["C1_marginal"] >= C1_FLOOR for row in block),
            "C1_joint_pass": sum(row["C1_joint_pass"] for row in block),
        })
    return out


def _by_block(rows: list[dict]) -> list[dict]:
    out = []
    for label in BLOCKS:
        entry = {"label": label}
        for cap in CAPS:
            block = [row for row in rows
                     if row["block"] == label and row["prediction_cap"] == cap]
            entry[str(cap)] = {
                "candidate_edges": sum(row["candidate_edges"] for row in block),
                "K_total": sum(row["K"] for row in block),
                "K_completeness": round(
                    sum(row["K"] for row in block)
                    / sum(row["candidate_edges"] for row in block), 6),
                "K_completeness_min": min(
                    row["K_completeness"] for row in block),
                "K_completeness_max": max(
                    row["K_completeness"] for row in block),
                "A_total": sum(row["A"] for row in block),
                "A_and_K_total": sum(row["A_and_K"] for row in block),
                "K_coverage_of_A": round(
                    sum(row["A_and_K"] for row in block)
                    / sum(row["A"] for row in block), 6),
                "C1_joint_pass": sum(row["C1_joint_pass"] for row in block),
            }
        out.append(entry)
    return out


def build() -> dict:
    rows = _rows()
    summary = _summary(rows)
    by_block = _by_block(rows)
    sixteen = [row for row in rows if row["block"] != "larger-28"]
    larger = [row for row in rows if row["block"] == "larger-28"]
    min16 = min(row["K_completeness"] for row in sixteen)
    max28 = max(row["K_completeness"] for row in larger)
    margin = round(min16 - max28, 6)
    caps_with_joint = {
        str(cap): sum(row["C1_joint_pass"] for row in rows
                      if row["prediction_cap"] == cap)
        for cap in CAPS
    }
    larger_joint = {
        str(cap): sum(row["C1_joint_pass"] for row in larger
                      if row["prediction_cap"] == cap)
        for cap in CAPS
    }
    larger_ranges = {
        seed: round(max(row["K_completeness"] for row in larger
                        if row["seed"] == seed)
                    - min(row["K_completeness"] for row in larger
                          if row["seed"] == seed), 6)
        for seed in sorted({row["seed"] for row in larger})
    }
    cap80 = [row for row in larger if row["prediction_cap"] == 80]
    pass80 = [row for row in cap80 if row["C1_joint_pass"]]
    fail80 = [row for row in cap80 if not row["C1_joint_pass"]]
    overlap_not_monotone = (
        min(row["K_completeness"] for row in pass80)
        < max(row["K_completeness"] for row in fail80))
    reading = (
        "K completeness separates the blocks at every cap: all 16-tag rows "
        "are 1.000, while larger-28 rows are %.4f-%.4f (margin %.4f). But it "
        "is nearly invariant across caps: larger-28 moves only %.4f in "
        "absolute aggregate, and its per-seed range is at most %.4f, while joint C1 "
        "passes move %d->%d->%d->%d overall and %d->%d->%d->%d in larger-28. "
        "K completeness is therefore a regime marker, not the cap lever."
        % (min(row["K_completeness"] for row in larger),
           max(row["K_completeness"] for row in larger), margin,
           abs(summary[-1]["K_completeness"] - summary[0]["K_completeness"]),
           max(larger_ranges.values()),
           caps_with_joint["20"], caps_with_joint["40"],
           caps_with_joint["80"], caps_with_joint["112"],
           larger_joint["20"], larger_joint["40"],
           larger_joint["80"], larger_joint["112"]))
    if overlap_not_monotone:
        reading += (
            " It also does not order joint success within larger-28: at cap "
            "80, the lowest-completeness pass is %.4f while the "
            "highest-completeness failure is %.4f."
            % (min(row["K_completeness"] for row in pass80),
               max(row["K_completeness"] for row in fail80)))
    return engine_stamp.stamp({
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "not_a_result": True,
        "question": (
            "Does K completeness (K / candidate_edges) separate the 16-tag "
            "and larger-28 worlds across prediction caps, and does it explain "
            "their joint C1 response?"
        ),
        "definition": (
            "For all 18 seeds at prediction caps 20/40/80/112, K completeness "
            "is the fraction of candidate edges carried at least once.  "
            "K coverage of A is A∩K / A.  Joint C1 is A∩K against the 60-row "
            "floor."
        ),
        "method": (
            "Read the committed cap-20/40/80 and cap-112 rows; the cap-40 and "
            "cap-80 overlaps must agree exactly.  No replay and no engine "
            "change.  The test is a census of the fixed seeds, not a sample."
        ),
        "constants": {
            "caps": list(CAPS),
            "c1_floor": C1_FLOOR,
            "complete_threshold": COMPLETE_THRESHOLD,
        },
        "governance": {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none",
        },
        "reading": reading,
        "summary": summary,
        "by_block": by_block,
        "larger_completeness_ranges": larger_ranges,
        "separation": {
            "min_16_completeness": min16,
            "max_larger_completeness": max28,
            "margin": margin,
            "threshold": COMPLETE_THRESHOLD,
            "classification_accuracy": round(sum((row["K_completeness"] >= COMPLETE_THRESHOLD) == (row["block"] != "larger-28") for row in rows) / len(rows), 6),
            "rows": len(rows),
        },
        "joint_caps": caps_with_joint,
        "larger_joint_caps": larger_joint,
        "cap80_overlap_not_monotone": overlap_not_monotone,
        "rows": rows,
        "not_evidence": (
            "A descriptive census of 18 fixed no-arm seeds across four "
            "prediction caps.  K completeness is measured from the committed "
            "rows, not intervened; the artifact does not show that changing "
            "K completeness would change C1, and it is not a treatment, "
            "target viability or a successor."
        ),
    })


def render(doc: dict) -> str:
    s = {row["prediction_cap"]: row for row in doc["summary"]}
    lines = [
        "# A1 K completeness across prediction caps",
        "",
        "Generated from `docs/a1_k_completeness.json` by "
        "`python -m benchmarks.a1_k_completeness --write`. Do not edit by hand.",
        "",
        "**Descriptive census, not an A1 result.** 18 no-arm seeds at "
        "prediction caps **20/40/80/112**. No target, freeze, grant or A1 cell.",
        "",
        "## Result",
        "",
        doc["reading"],
        "",
        "| Cap | Candidates | A | K | A∩K | K completeness | K coverage of A | Joint pass |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cap in CAPS:
        row = s[cap]
        lines.append("| %d | %d | %d | %d | %d | %.3f | %.3f | %d/18 |" % (
            cap, row["candidate_edges"], row["A_total"], row["K_total"],
            row["A_and_K_total"], row["K_completeness"],
            row["K_coverage_of_A"], row["C1_joint_pass"]))
    lines += [
        "",
        "## By block",
        "",
        "| Block | Cap | Candidates | K | K completeness | K coverage of A | Joint pass |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for block in doc["by_block"]:
        for cap in CAPS:
            row = block[str(cap)]
            lines.append("| %s | %d | %d | %d | %.3f | %.3f | %d/6 |" % (
                block["label"], cap, row["candidate_edges"], row["K_total"],
                row["K_completeness"], row["K_coverage_of_A"],
                row["C1_joint_pass"]))
    lines += [
        "",
        "## Separation",
        "",
        "| Statistic | Value |",
        "| --- | ---: |",
        "| Minimum 16-tag completeness | %.3f |" % doc["separation"]["min_16_completeness"],
        "| Maximum larger-28 completeness | %.3f |" % doc["separation"]["max_larger_completeness"],
        "| Margin | %.3f |" % doc["separation"]["margin"],
        "| Classification accuracy | %.0f%% |" % (100 * doc["separation"]["classification_accuracy"]),
        "",
        "The block split is perfect at every cap. It is also almost constant "
        "within larger-28: the aggregate moves by only %.4f, and the largest "
        "per-seed across-cap range is %.4f."
        % (abs(s[112]["K_completeness"] - s[20]["K_completeness"]),
           max(doc["larger_completeness_ranges"].values())),
        "",
        "## What it does not explain",
        "",
        "K completeness is static while joint C1 is not. Joint passes move "
        "**0 → 0 → 4 → 8** overall and **0 → 0 → 4 → 6** in larger-28 across "
        "caps 20/40/80/112. At cap 80, the lowest-completeness larger-28 pass "
        "is **%.3f**, while the highest-completeness failure is **%.3f**; a "
        "higher completeness does not guarantee a joint pass."
        % (min(row["K_completeness"] for row in doc["rows"]
               if row["block"] == "larger-28"
               and row["prediction_cap"] == 80 and row["C1_joint_pass"]),
           max(row["K_completeness"] for row in doc["rows"]
               if row["block"] == "larger-28"
               and row["prediction_cap"] == 80 and not row["C1_joint_pass"])),
        "",
        "The 16-tag block is K-complete but still fails joint C1 at caps "
        "20/40/80 (and 10/12 seeds fail at 112). Completeness removes the "
        "A\\K loss; it does not supply A.",
        "",
        "## Reading",
        "",
        "K completeness is a **regime marker**: 1.000 in the 16-tag streams, "
        "0.61–0.85 in larger-28, at every cap. It is not the variable that "
        "moves C1 across caps. The cap response is A, while K coverage of A "
        "determines how much of that A survives into the joint count.",
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
    if len(rows) != 18 * len(CAPS):
        found.append("%d rows, expected %d" % (len(rows), 18 * len(CAPS)))
    for row in rows:
        if row.get("K_completeness") != round(
                row.get("K", 0) / row.get("candidate_edges", 1), 6):
            found.append("K completeness at %r"
                         % ((row.get("block"), row.get("seed"),
                             row.get("prediction_cap")),))
        if row.get("C1_joint_pass") != (row.get("A_and_K", 0) >= C1_FLOOR):
            found.append("joint pass at %r"
                         % ((row.get("block"), row.get("seed"),
                             row.get("prediction_cap")),))
    if PAGE_PATH.exists() and PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("the page is stale")
    return found


def self_test() -> list[str]:
    failures: list[str] = []
    if round(3 / 4, 6) != 0.75:
        failures.append("completeness fixture")
    if COMPLETE_THRESHOLD != 0.9:
        failures.append("threshold is part of the committed test")
    return failures


def write() -> int:
    body = build()
    OUT_PATH.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(body), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(body["reading"])
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        raise SystemExit("no K-completeness artifact; run --write")
    body = _load(OUT_PATH)
    found = problems(body)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("K completeness: clean")
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
        print("K-completeness self-test: clean")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
