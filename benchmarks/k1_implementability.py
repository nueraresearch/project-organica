"""Regenerate and check the K1 implementability review's figures.

The review's table is a transcription of two committed artifacts:
``docs/phase_k_results_0.15.0.json`` (the shipping build) and
``docs/phase_k_results.json`` (the frozen 0.9.0 record).  Rule 27 applies: a
table transcribed from an artifact is a new claim and needs a mechanical
check, so the table is generated here and ``--check`` fails when the document
and the artifacts disagree.

The module opens no database, runs no sleep cycle and writes no research
result.  It reads two artifacts and one page.

Usage::

    python -m benchmarks.k1_implementability --write   # render the table into the page
    python -m benchmarks.k1_implementability --check   # the page matches the artifacts
    python -m benchmarks.k1_implementability --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHIPPED = ROOT / "docs" / "phase_k_results_0.15.0.json"
ARCHIVAL = ROOT / "docs" / "phase_k_results.json"
DOC = ROOT / "docs" / "K1-IMPLEMENTABILITY-REVIEW.md"

PANEL_BEGIN = ("<!-- BEGIN K1 PANEL: generated from the two Phase K artifacts by "
               "benchmarks/k1_implementability.py; do not edit by hand -->")
PANEL_END = "<!-- END K1 PANEL -->"

COLUMNS = ("| Build | Seeds | Recall 1.000 | Recall range | Precision range | "
           "Pairs emitted | Late-group F1 range |",
           "|---|---|---|---|---|---|---|")

# The K1 world is three entities of four features each: C(4, 2) x 3 = 18 gold
# pairs.  Every K1 cell is scored on all three entities' pairs, so this is the
# denominator behind precision and recall, not a value read off the artifact.
GOLD_PAIRS = 18

# What the review asserts, as predicates over the per-seed rows.  Each is a
# claim the page makes, so each is checked rather than typed.
CLAIMS = (
    ("shipped_recall_is_full",
     "on 0.15.0 every K1 seed recalls the whole gold set",
     lambda s: s["recall_min"] == 1.0 and s["recall_max"] == 1.0),
    ("shipped_late_group_nonzero",
     "on 0.15.0 the late-group F1 is positive on every seed",
     lambda s: s["late_min"] > 0.0),
    ("shipped_precision_low",
     "on 0.15.0 precision stays below 0.20",
     lambda s: s["precision_max"] < 0.20),
    ("shipped_emits_wide",
     "on 0.15.0 Organica emits at least five times the gold set",
     lambda s: s["emitted_min"] >= 5 * GOLD_PAIRS),
    ("archival_recall_partial",
     "on 0.9.0 no seed recalls the whole gold set",
     lambda s: s["recall_max"] < 1.0),
    ("archival_late_group_zero",
     "on 0.9.0 the late-group F1 is exactly zero on at least one seed",
     lambda s: s["late_min"] == 0.0),
)


def _read(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _num(value: float) -> str:
    """A measured value, written with the artifact's own precision."""
    return ("%.6f" % value).rstrip("0").rstrip(".")


def k1_rows(document: dict) -> list[dict]:
    """The K1 cells, with the quantities the review reads derived per seed."""
    rows = []
    for record in document.get("per_model_detail") or []:
        if record.get("family") != "K1":
            continue
        models = record.get("models") or []
        primary = next((m for m in models if m.get("model") == "organica"), None)
        if primary is None:
            raise ValueError("K1 seed %s has no organica row" % record.get("seed"))
        precision = float(primary["precision"])
        recall = float(primary["recall"])
        # The strongest simple baseline on this seed, by the campaign's own rule.
        baseline = max(
            (m for m in models if m.get("model") in ("cooccurrence", "temporal_graph")),
            key=lambda m: float(m["primary"]), default=None)
        rows.append({
            "seed": record["seed"],
            "f1": float(primary["primary"]),
            "baseline_f1": float(baseline["primary"]) if baseline else None,
            "precision": precision,
            "recall": recall,
            "late_f1": primary.get("late_f1"),
            # TP / precision, with TP = recall * gold.  Derived, not quoted.
            "emitted": (round(GOLD_PAIRS * recall / precision)
                        if precision else None),
        })
    if not rows:
        raise ValueError("no K1 rows in the document")
    return sorted(rows, key=lambda row: row["seed"])


def summarise(rows: list[dict]) -> dict:
    late = [row["late_f1"] for row in rows if row["late_f1"] is not None]
    emitted = [row["emitted"] for row in rows if row["emitted"] is not None]
    baselines = [row["baseline_f1"] for row in rows if row["baseline_f1"] is not None]
    return {
        "seeds": len(rows),
        "gold_pairs": GOLD_PAIRS,
        "baseline_mean": (round(statistics.mean(baselines), 6) if baselines else None),
        "recall_full": sum(1 for row in rows if row["recall"] == 1.0),
        "recall_min": min(row["recall"] for row in rows),
        "recall_max": max(row["recall"] for row in rows),
        "precision_min": min(row["precision"] for row in rows),
        "precision_max": max(row["precision"] for row in rows),
        "emitted_min": min(emitted) if emitted else None,
        "emitted_max": max(emitted) if emitted else None,
        "late_min": min(late) if late else None,
        "late_max": max(late) if late else None,
        "late_zero_seeds": [row["seed"] for row in rows if row["late_f1"] == 0.0],
    }


def panel() -> dict:
    """Both builds' K1 summaries, and every claim checked against them."""
    builds = {
        "0.15.0": summarise(k1_rows(_read(SHIPPED))),
        "0.9.0": summarise(k1_rows(_read(ARCHIVAL))),
    }
    checks = {}
    for name, text, predicate in CLAIMS:
        # Each claim is stated of one build by its name prefix.
        build = "0.9.0" if name.startswith("archival") else "0.15.0"
        checks[name] = {
            "claim": text,
            "build": build,
            "holds": bool(predicate(builds[build])),
        }
    return {"builds": builds, "claims": checks}


def render_table(payload: dict | None = None) -> str:
    payload = panel() if payload is None else payload
    lines = list(COLUMNS)
    for build in ("0.15.0", "0.9.0"):
        s = payload["builds"][build]
        lines.append("| %s | %d | %d of %d | %s-%s | %s-%s | %s-%s | %s-%s |" % (
            build, s["seeds"], s["recall_full"], s["seeds"],
            _num(s["recall_min"]), _num(s["recall_max"]),
            _num(s["precision_min"]), _num(s["precision_max"]),
            s["emitted_min"], s["emitted_max"],
            _num(s["late_min"]), _num(s["late_max"]),
        ))
    return "\n".join(lines)


def _between(text: str, begin: str, end: str) -> str | None:
    start = text.find(begin)
    if start < 0:
        return None
    start += len(begin)
    stop = text.find(end, start)
    if stop < 0:
        return None
    return text[start:stop]


PLACEHOLDER = re.compile(r"\{[A-Za-z_][A-Za-z0-9_:,.!]*\}")


def problems(text: str, payload: dict | None = None) -> list[str]:
    """Every way the page and the artifacts disagree."""
    payload = panel() if payload is None else payload
    found = []
    block = _between(text, PANEL_BEGIN, PANEL_END)
    if block is None:
        return ["the page carries no generated K1 panel"]
    if block.strip() != render_table(payload).strip():
        found.append("the panel is not the table the artifacts produce")
    for name, check in sorted(payload["claims"].items()):
        if not check["holds"]:
            found.append("%s does not hold on %s" % (name, check["build"]))
    for match in PLACEHOLDER.finditer(text):
        found.append("unsubstituted placeholder %s" % match.group(0))
    return found


def write_page(payload: dict | None = None) -> str:
    payload = panel() if payload is None else payload
    text = DOC.read_text(encoding="utf-8")
    block = _between(text, PANEL_BEGIN, PANEL_END)
    if block is None:
        raise SystemExit("the page carries no generated K1 panel")
    updated = text.replace(
        PANEL_BEGIN + block + PANEL_END,
        PANEL_BEGIN + "\n" + render_table(payload) + "\n" + PANEL_END,
    )
    DOC.write_text(updated, encoding="utf-8")
    return render_table(payload)


def self_test(payload: dict | None = None) -> list[str]:
    """Prove the check can fail: tamper with a copied panel and re-check."""
    payload = panel() if payload is None else payload
    text = DOC.read_text(encoding="utf-8")
    if problems(text, payload):
        return problems(text, payload)
    block = _between(text, PANEL_BEGIN, PANEL_END)
    tampered = text.replace(block, block.replace("1 of 10", "0 of 10"), 1)
    if tampered != text and not problems(tampered, payload):
        return ["a tampered panel was accepted"]
    flipped = json.loads(json.dumps(payload))
    flipped["builds"]["0.15.0"]["recall_min"] = 0.5
    if not problems(text, flipped):
        return ["a build whose recall is not full was accepted"]
    return []


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate or check the K1 implementability review.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    payload = panel()

    if args.write:
        print(render_table(payload))
        write_page(payload)
        print("wrote %s" % DOC.relative_to(ROOT))
        return 0
    if args.self_test:
        failures = self_test(payload)
        if failures:
            print("self-test FAILED: " + "; ".join(failures))
            return 1
        print("self-test ok: the checker rejects a tampered panel and a non-full recall")
        return 0
    findings = problems(DOC.read_text(encoding="utf-8"), payload)
    if findings:
        for finding in findings:
            print("FAIL: " + finding)
        return 1
    print("K1 implementability review: panel matches both artifacts, %d claim(s) hold"
          % len(payload["claims"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
