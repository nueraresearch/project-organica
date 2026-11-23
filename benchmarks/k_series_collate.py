"""Collate the K-series records into one page, and check the page against them.

The K series left five records: the Phase K campaign and its frozen verdicts, a
mechanism erratum, a K3 root-cause diagnostic, a build passport, and one K2
block that returned ``VOID``. Reading them side by side is easy to get wrong in
the direction that matters -- an inadmissible block quoted as a failed
replication, or a null ablation read as a refuted mechanism -- so the page that
collates them is generated from the artifacts and checked against them.

The page is ``docs/PHASE-K-SERIES-SYNTHESIS.md``. Two regions in it are
rendered from ``docs/phase_k_results.json``; everything else is prose.

    python -m benchmarks.k_series_collate --check      # exit 1 on drift
    python -m benchmarks.k_series_collate --write      # regenerate the tables
    python -m benchmarks.k_series_collate --self-test  # prove --check can fail

``--check`` writes nothing. It compares the rendered regions byte for byte and
then verifies the page's non-table facts against the block result, the
constraint registration and the campaign artifact: the verdict, the failed
gate, ``criteria_read``, the K1 registered/live/absolute figures, the
pre-boundary count range, and the arithmetic behind the retirement
recommendation. A page that quotes a number the artifacts do not support fails
rather than reading as a sentence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "PHASE-K-SERIES-SYNTHESIS.md"
CAMPAIGN = ROOT / "docs" / "phase_k_results.json"
BLOCK = ROOT / "docs" / "phase_k_k2_results.json"
REGISTRATION = ROOT / "docs" / "constraint_registrations" / "K2-belief-revision.json"

SUMMARY_BEGIN = (
    "<!-- BEGIN K SUMMARY: generated from docs/phase_k_results.json by "
    "benchmarks/k_series_collate.py; do not edit by hand -->"
)
SUMMARY_END = "<!-- END K SUMMARY -->"
ABLATION_BEGIN = (
    "<!-- BEGIN K ABLATION: generated from docs/phase_k_results.json by "
    "benchmarks/k_series_collate.py; do not edit by hand -->"
)
ABLATION_END = "<!-- END K ABLATION -->"

FAMILIES = ("K1", "K2", "K3")
FAMILY_LABELS = {
    "K1": "incremental world modeling",
    "K2": "belief revision",
    "K3": "longitudinal integration",
}
ABLATION_NAMES = {
    "K1": "NO_QUESTIONS",
    "K2": "NO_FALSIFICATION",
    "K3": "NO_DREAMS",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def summary_table(campaign: dict) -> str:
    """The family verdict table, rendered from the campaign's own summaries."""
    lines = [
        "| Family | Organica | Best simple baseline | Paired difference | 98.33% interval | Verdict |",
        "|---|---:|---:|---:|---|---|",
    ]
    for family in FAMILIES:
        summary = campaign["summaries"][family]
        gap = summary["paired_organica_minus_best_baseline"]
        lines.append(
            "| **{family}** — {label} | {organica:.4f} | {baseline:.4f} | {mean:.4f} | "
            "[{low:.4f}, {high:.4f}] | **{verdict}** |".format(
                family=family,
                label=FAMILY_LABELS[family],
                organica=summary["organica_primary_mean"],
                baseline=summary["best_simple_baseline_primary_mean"],
                mean=gap["mean"],
                low=gap["interval"][0],
                high=gap["interval"][1],
                verdict=summary["verdict"],
            )
        )
    return "\n".join(lines)


def _ablation_read(interval: list[float]) -> str:
    """Three interval shapes, three different readings -- never one label."""
    if interval[0] > 0:
        return "wholly above zero — mechanism implicated"
    if interval[1] < 0:
        return "wholly below zero — mechanism refuted"
    return "contains zero — not established"


def ablation_table(campaign: dict) -> str:
    """The matched-ablation table, with the read derived from the interval."""
    lines = [
        "| Ablation | Ablated arm (mean) | Organica − ablation | Read |",
        "|---|---:|---|---|",
    ]
    for family in FAMILIES:
        ablation = campaign["summaries"][family]["matched_ablation"]
        paired = ablation["paired_organica_minus_ablation"]
        lines.append(
            "| `{name}` ({family}) | {mean:.4f} | {diff:+.4f} [{low:+.4f}, {high:+.4f}] | {read} |".format(
                name=ABLATION_NAMES[family],
                family=family,
                mean=ablation["primary_mean"],
                diff=paired["mean"],
                low=paired["interval"][0],
                high=paired["interval"][1],
                read=_ablation_read(paired["interval"]),
            )
        )
    return "\n".join(lines)


def _region(text: str, begin: str, end: str) -> str:
    if text.count(begin) != 1 or text.count(end) != 1:
        raise ValueError("expected exactly one %r ... %r region" % (begin, end))
    start = text.index(begin) + len(begin)
    stop = text.index(end)
    if stop < start:
        raise ValueError("the regions are out of order")
    return text[start:stop]


def _replace_region(text: str, begin: str, end: str, body: str) -> str:
    _region(text, begin, end)
    start = text.index(begin) + len(begin)
    stop = text.index(end)
    return text[:start] + "\n" + body + "\n" + text[stop:]


def _expected_regions(campaign: dict) -> dict[str, tuple[str, tuple[str, str]]]:
    return {
        "summary": ("\n" + summary_table(campaign) + "\n", (SUMMARY_BEGIN, SUMMARY_END)),
        "ablation": ("\n" + ablation_table(campaign) + "\n", (ABLATION_BEGIN, ABLATION_END)),
    }


def required_facts(block: dict, registration: dict) -> list[str]:
    """Non-table facts the page states, each derived from a record.

    A transcription is a claim; these are the strings the page must contain and
    the records that produce them. Formatting is fixed here so a change in an
    artifact surfaces as a failing check rather than a stale sentence.
    """
    gate = block["gate"]
    k1 = block["k1"]
    pre = [
        record["manipulation"]["pre_boundary_demotions"]
        for record in block["records"]
        if record.get("family") == "K2"
    ]
    baseline_gap = registration["threshold_values"]["baseline_gap"]
    pass_improvement = registration["threshold_values"]["pass_min_improvement"]
    best_case = baseline_gap + pass_improvement
    return [
        gate["verdict"],
        gate["failed_gates"][0],
        "criteria_read: false" if gate["criteria_read"] is False else "criteria_read: true",
        block["engine_version"],
        block["engine_tree_sha256"][:7],
        block["protocol"]["grant_id"],
        "%.6f" % k1["pre_value"],
        "%.6f" % k1["post_value"],
        "%.6f" % k1["abs_change"],
        "{:,}".format(min(pre)),
        "{:,}".format(max(pre)),
        "%.4f" % best_case,
    ]


def problems(text: str, campaign: dict, block: dict, registration: dict) -> list[str]:
    """Everything wrong with the page, as sentences, without writing anything."""
    found: list[str] = []
    for name, (expected, (begin, end)) in _expected_regions(campaign).items():
        try:
            current = _region(text, begin, end)
        except ValueError as exc:
            found.append("%s: %s" % (name, exc))
            continue
        if current != expected:
            found.append(
                "%s table is stale; run python -m benchmarks.k_series_collate --write"
                % name
            )
    for fact in required_facts(block, registration):
        if fact not in text:
            found.append("the page does not state %r, which its records require" % fact)
    if campaign.get("confirmed_families"):
        found.append(
            "the campaign now names confirmed families; this page's H2 reading is stale"
        )
    return found


def write(text: str, campaign: dict) -> str:
    for _name, (body, (begin, end)) in _expected_regions(campaign).items():
        text = _replace_region(text, begin, end, body.strip("\n"))
    return text


def self_test(text: str, campaign: dict, block: dict, registration: dict) -> list[str]:
    """Prove --check rejects a page that states a number the artifact does not."""
    failures: list[str] = []
    if problems(text, campaign, block, registration):
        failures.append("the committed page does not pass its own check")
    tampered = text.replace("**REVERSED**", "**SUPPORTED**", 1)
    if tampered == text:
        failures.append("could not build a tampered page to test the check")
    elif not problems(tampered, campaign, block, registration):
        failures.append("the check accepted a tampered verdict")
    return failures


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="verify the page; writes nothing")
    group.add_argument("--write", action="store_true", help="regenerate the two tables")
    group.add_argument("--self-test", action="store_true", help="prove the check can fail")
    args = parser.parse_args(argv)

    campaign = _load(CAMPAIGN)
    block = _load(BLOCK)
    registration = _load(REGISTRATION)
    text = DOC.read_text(encoding="utf-8")

    if args.write:
        DOC.write_text(write(text, campaign), encoding="utf-8")
        print("wrote the generated regions of", DOC.relative_to(ROOT))
        return 0

    if args.self_test:
        failures = self_test(text, campaign, block, registration)
        for failure in failures:
            print("FAIL:", failure)
        if failures:
            return 1
        print("self-test: the check accepts the page and rejects a tampered verdict")
        return 0

    failures = problems(text, campaign, block, registration)
    for failure in failures:
        print("FAIL:", failure)
    if failures:
        return 1
    print("K-series synthesis: tables and facts match their artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
