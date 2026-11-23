"""Check the T2 frontier figures against the Phase K artifact.

The build page's T2 section and the (a)+T1 memo quote one frontier: across all K1
cooccurrence rows, the best F1, the rows at precision 1.000000 and what they cost in
recall, and the false pairs the best full-recall point carries.  Rule 27 applies: a
figure transcribed from an artifact is a new claim, so this module derives every one
of them from ``docs/phase_k_results_0.15.0.json``, fails when either document
disagrees, and ``--self-test`` proves the check can fail.

The module opens no database, runs no sleep cycle and writes no research result.

Usage::

    python -m benchmarks.cooccurrence_frontier_check --check
    python -m benchmarks.cooccurrence_frontier_check --self-test
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "phase_k_results_0.15.0.json"
PAGE = ROOT / "docs" / "COOCCURRENCE-SELECTION-BUILD.md"
MEMO = ROOT / "docs" / "COOCCURRENCE-A-T1-MEMO.md"

GOLD_PAIRS = 18
WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18,
}
DASHES = ("\u2013", "\u2014", "\u2212")


def _fmt(value: float) -> str:
    return "%.6f" % value


def _count(token: str) -> int:
    return int(token) if token.isdigit() else WORDS[token]


def _normalise(text: str) -> str:
    """Drop emphasis and code markers, fold the prose dashes, collapse whitespace."""
    for mark in ("*", "`"):
        text = text.replace(mark, "")
    for mark in DASHES:
        text = text.replace(mark, "-")
    return " ".join(text.split())


def figures(document: dict) -> dict:
    """The frontier, derived from every K1 cooccurrence row."""
    seeds: dict = {}
    rows = []
    for record in document.get("per_model_detail") or []:
        if record.get("family") != "K1":
            continue
        for model in record.get("models") or []:
            if model.get("model") != "cooccurrence":
                continue
            rows.append(model)
            seeds.setdefault(record.get("seed"), []).append(model)
    if not rows:
        raise ValueError("the artifact carries no K1 cooccurrence rows")
    perfect = [m for m in rows if abs(float(m["precision"]) - 1.0) < 1e-12]
    if not perfect:
        raise ValueError("no K1 cooccurrence row reaches precision 1.000000")
    perfect_configs = {(str(m["config"]["window"]), str(m["config"]["min_count"]))
                       for m in perfect}
    if len(perfect_configs) != 1:
        raise ValueError("the precision-1.000000 rows do not share one configuration")
    all_configs = {(str(m["config"]["window"]), str(m["config"]["min_count"]))
                   for m in rows}
    best = [max(models, key=lambda m: m["primary"]) for models in seeds.values()]
    for model in best:
        if abs(float(model["recall"]) - 1.0) > 1e-9:
            raise ValueError("a best row is not full-recall; the false-pair arithmetic does not apply")
    false = [round(GOLD_PAIRS / float(m["precision"])) - GOLD_PAIRS for m in best]
    recalls = [float(m["recall"]) for m in perfect]
    true = [round(value * GOLD_PAIRS) for value in recalls]
    window, floor = next(iter(perfect_configs))
    return {
        "rows": len(rows),
        "seeds": len(seeds),
        "configs": len(all_configs),
        "max_f1": _fmt(max(float(m["primary"]) for m in rows)),
        "perfect_rows": len(perfect),
        "perfect_window": window,
        "perfect_floor": floor,
        "recall_low": _fmt(min(recalls)),
        "recall_high": _fmt(max(recalls)),
        "true_low": min(true),
        "true_high": max(true),
        "false_low": min(false),
        "false_high": max(false),
    }


def _section(text: str, start: str, end: str, label: str) -> str:
    head = text.find(start)
    tail = text.find(end, head + 1) if head >= 0 else -1
    if head < 0 or tail <= head:
        raise ValueError("%s no longer carries its %r to %r section" % (label, start, end))
    return text[head + len(start):tail]


def _claims(label: str, text: str, fig: dict) -> list[str]:
    """Every frontier claim in one section, checked against the derived figures."""
    text = _normalise(text)
    problems = []

    def report(message: str) -> None:
        problems.append(message)

    match = re.search(r"Across all (\d+) cooccurrence rows", text)
    if not match:
        report("%s no longer states the cooccurrence row count" % label)
    elif int(match.group(1)) != fig["rows"]:
        report("%s says %s cooccurrence rows; the artifact has %d"
               % (label, match.group(1), fig["rows"]))

    match = re.search(r"(\w+) seeds by (\w+) configurations", text)
    if not match:
        report("%s no longer states the seeds-by-configurations shape" % label)
    else:
        try:
            seeds, configs = _count(match.group(1)), _count(match.group(2))
        except KeyError as exc:
            report("%s uses an unreadable count %s" % (label, exc))
        else:
            if seeds != fig["seeds"] or configs != fig["configs"]:
                report("%s says %d seeds by %d configurations; the artifact has %d by %d"
                       % (label, seeds, configs, fig["seeds"], fig["configs"]))

    match = re.search(r"best F1 anywhere is (\d+\.\d{6})", text)
    if not match:
        report("%s no longer states the best F1" % label)
    elif _fmt(float(match.group(1))) != fig["max_f1"]:
        report("%s says the best F1 is %s; the artifact's is %s"
               % (label, match.group(1), fig["max_f1"]))

    match = re.search(
        r"Precision (\d+\.\d{6}) appears in (\w+) rows, all(?: of them)? window (\d+) / floor (\d+)",
        text)
    if not match:
        report("%s no longer states the precision-1.000000 rows and their configuration" % label)
    else:
        try:
            count = _count(match.group(2))
        except KeyError:
            report("%s uses an unreadable row count %s" % (label, match.group(2)))
            count = -1
        if _fmt(float(match.group(1))) != "1.000000":
            report("%s says precision %s; the claim is about 1.000000" % (label, match.group(1)))
        if count != fig["perfect_rows"]:
            report("%s says %d rows at precision 1.000000; the artifact has %d"
                   % (label, count, fig["perfect_rows"]))
        if match.group(3) != fig["perfect_window"] or match.group(4) != fig["perfect_floor"]:
            report("%s says window %s / floor %s; the artifact's perfect rows are window %s / floor %s"
                   % (label, match.group(3), match.group(4),
                      fig["perfect_window"], fig["perfect_floor"]))

    match = re.search(
        r"recall: (\d+\.\d{6})(?: to |-)(\d+\.\d{6}), or (\w+) to (\w+) of the eighteen", text)
    if not match:
        report("%s no longer states the recall range and the true-positive count" % label)
    else:
        try:
            low, high = _count(match.group(3)), _count(match.group(4))
        except KeyError:
            report("%s uses an unreadable true-positive count" % label)
        else:
            if (_fmt(float(match.group(1))), _fmt(float(match.group(2)))) != (
                    fig["recall_low"], fig["recall_high"]):
                report("%s says recall %s-%s; the artifact's perfect rows span %s-%s"
                       % (label, match.group(1), match.group(2),
                          fig["recall_low"], fig["recall_high"]))
            if (low, high) != (fig["true_low"], fig["true_high"]):
                report("%s says %d-%d true positives; the artifact's perfect rows carry %d-%d"
                       % (label, low, high, fig["true_low"], fig["true_high"]))

    match = re.search(r"carries (\w+) to (\w+) false pairs", text)
    if not match:
        report("%s no longer states the false pairs at the best full-recall point" % label)
    else:
        try:
            low, high = _count(match.group(1)), _count(match.group(2))
        except KeyError:
            report("%s uses an unreadable false-pair count" % label)
        else:
            if (low, high) != (fig["false_low"], fig["false_high"]):
                report("%s says %d-%d false pairs; the artifact's best full-recall point carries %d-%d"
                       % (label, low, high, fig["false_low"], fig["false_high"]))
    return problems


def _reproduce(text: str, fig: dict) -> list[str]:
    """The memo's reproduce note restates the same figures and must match them."""
    pattern = (r"(\d+) seeds × (\d+) configurations = (\d+) rows; maximum primary (\d+\.\d{6}); "
               r"the (\w+) rows with precision (\d+\.\d{6}) are window (\d+) / floor (\d+) "
               r"with recall (\d+\.\d{6})-(\d+\.\d{6})")
    match = re.search(pattern, _normalise(text))
    if not match:
        return ["the memo no longer carries its reproduce note"]
    problems = []
    if (int(match.group(1)), int(match.group(2)), int(match.group(3))) != (
            fig["seeds"], fig["configs"], fig["rows"]):
        problems.append("the memo's reproduce note states a different seeds x configurations = rows")
    if _fmt(float(match.group(4))) != fig["max_f1"]:
        problems.append("the memo's reproduce note says max primary %s; the artifact's is %s"
                        % (match.group(4), fig["max_f1"]))
    try:
        count = _count(match.group(5))
    except KeyError:
        problems.append("the memo's reproduce note uses an unreadable row count")
        count = -1
    if count != fig["perfect_rows"]:
        problems.append("the memo's reproduce note says %d precision-1.000000 rows; the artifact has %d"
                        % (count, fig["perfect_rows"]))
    if _fmt(float(match.group(6))) != "1.000000":
        problems.append("the memo's reproduce note says precision %s; the claim is about 1.000000"
                        % match.group(6))
    if match.group(7) != fig["perfect_window"] or match.group(8) != fig["perfect_floor"]:
        problems.append("the memo's reproduce note names window %s / floor %s; the artifact's perfect "
                        "rows are window %s / floor %s"
                        % (match.group(7), match.group(8), fig["perfect_window"], fig["perfect_floor"]))
    if (_fmt(float(match.group(9))), _fmt(float(match.group(10)))) != (
            fig["recall_low"], fig["recall_high"]):
        problems.append("the memo's reproduce note says recall %s-%s; the artifact's perfect rows span %s-%s"
                        % (match.group(9), match.group(10), fig["recall_low"], fig["recall_high"]))
    return problems


def check(document: dict | None = None, *, page: str | None = None,
          memo: str | None = None) -> list[str]:
    document = document if document is not None else json.loads(
        ARTIFACT.read_text(encoding="utf-8"))
    page = page if page is not None else PAGE.read_text(encoding="utf-8")
    memo = memo if memo is not None else MEMO.read_text(encoding="utf-8")

    fig = figures(document)
    problems = _claims("the build page's T2 section",
                       _section(page, "### T2", "### The choice", "the build page"), fig)
    problems += _claims("the memo's term-sheet section",
                        _section(memo, "## Why T1", "## What the build is", "the memo"), fig)
    problems += _reproduce(memo, fig)
    return problems


def self_test() -> list[str]:
    """The check must fail on a moved artifact, a doctored page and a doctored memo."""
    document = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    failures = []
    if check(document):
        failures.append("the committed files already fail the check")

    bumped = copy.deepcopy(document)
    rows = [m for r in bumped["per_model_detail"] if r.get("family") == "K1"
            for m in r["models"] if m.get("model") == "cooccurrence"]
    top = max(rows, key=lambda m: m["primary"])
    top["primary"] = round(float(top["primary"]) + 0.001, 6)
    if not check(bumped):
        failures.append("a changed artifact did not fail the check")

    page = PAGE.read_text(encoding="utf-8").replace(
        "best F1 anywhere is **0.972973**", "best F1 anywhere is **0.972974**", 1)
    if not check(page=page):
        failures.append("a doctored best F1 in the page did not fail the check")

    memo = MEMO.read_text(encoding="utf-8").replace("eight rows", "nine rows", 1)
    if not check(memo=memo):
        failures.append("a doctored row count in the memo did not fail the check")

    memo = MEMO.read_text(encoding="utf-8").replace(
        "window 30 / floor 10", "window 75 / floor 10", 1)
    if not check(memo=memo):
        failures.append("a doctored configuration in the memo did not fail the check")
    return failures


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify both documents")
    parser.add_argument("--self-test", action="store_true", help="prove the check fails")
    args = parser.parse_args(argv)

    if args.self_test:
        failures = self_test()
        if failures:
            for failure in failures:
                print("FAIL:", failure)
            return 1
        print("self-test ok: the check rejects a moved artifact, a doctored best F1, "
              "a doctored row count and a doctored configuration")
        return 0
    problems = check()
    if problems:
        for problem in problems:
            print("FAIL:", problem)
        return 1
    fig = figures(json.loads(ARTIFACT.read_text(encoding="utf-8")))
    print("frontier: page and memo match the artifact (%d rows, %d seeds x %d configurations, "
          "best F1 %s, %d perfect rows at recall %s-%s)"
          % (fig["rows"], fig["seeds"], fig["configs"], fig["max_f1"],
             fig["perfect_rows"], fig["recall_low"], fig["recall_high"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
