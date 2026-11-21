"""Regenerate and check the pressure test's figures against the Phase K artifact.

The pressure-test page, the withdrawn draft and the manual rows that quote the test all
restate figures from ``docs/phase_k_results_0.15.0.json``.  Rule 27 applies: a figure
transcribed from an artifact is a new claim, so the page's table is generated here and
``--check`` re-derives every figure.  A quoted six-decimal number must be either an
aggregate this module derives or a figure that one artifact row carries together with
the other figures quoted beside it, a range must be one the artifact derives as a pair,
and the ledger's ``baseline_gap`` must equal the mean gap derived here.  ``--self-test``
proves each refusal can fire.

The module opens no database, runs no sleep cycle and writes no research result.

Usage::

    python -m benchmarks.assertion_provenance_pressure_test --write
    python -m benchmarks.assertion_provenance_pressure_test --check
    python -m benchmarks.assertion_provenance_pressure_test --self-test
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "phase_k_results_0.15.0.json"
PAGE = ROOT / "docs" / "ASSERTION-PROVENANCE-PRESSURE-TEST.md"
DRAFT = ROOT / "docs" / "constraint_registrations" / "assertion-provenance.json"
MANUAL = ROOT / "docs" / "USER-MANUAL.md"
LEDGER = ROOT / "docs" / "bottleneck_map.json"

BLOCK_BEGIN = ("<!-- BEGIN PRESSURE TEST FIGURES: generated from "
               "docs/phase_k_results_0.15.0.json by "
               "benchmarks/assertion_provenance_pressure_test.py; do not edit by hand -->")
BLOCK_END = "<!-- END PRESSURE TEST FIGURES -->"

# C(4, 2) x 3 entities: the denominator behind every K1 precision and recall.
GOLD_PAIRS = 18
# The draft's pass bar is the 0.15.0 mean plus this much, as registered.
PASS_MIN_IMPROVEMENT = 0.10
LONG_WINDOWS = ("all", 300, 150)
FIGURE = re.compile(r"\d\.\d{6}")
DECIMAL = re.compile(r"\d\.\d{4,}")
RANGE = re.compile(r"(\d\.\d{6})[-\u2013\u2014\u2212](\d\.\d{6})")
DASHES = ("\u2013", "\u2014", "\u2212")
REQUIRED = ("0.312011", "0.935972", "0.623961")


def _fmt(value: float) -> str:
    return "%.6f" % value


def _range(values) -> str:
    low, high = min(values), max(values)
    return _fmt(low) if low == high else "%s-%s" % (_fmt(low), _fmt(high))


def figures(document: dict) -> dict:
    """Every figure the pressure test rests on, derived from the artifact."""
    rows = [record for record in document.get("per_model_detail") or []
            if record.get("family") == "K1"]
    if not rows:
        raise ValueError("the artifact carries no K1 rows")
    organica, best, distinct, gains = [], [], [], []
    long_coincide = ties = 0
    configs = Counter()
    grid_sizes, long_defaults = [], []
    for record in rows:
        seed = record.get("seed")
        models = record.get("models") or []
        primary = next((m for m in models if m.get("model") == "organica"), None)
        if primary is None:
            raise ValueError("K1 seed %s has no organica row" % seed)
        cooc = [m for m in models if m.get("model") == "cooccurrence"]
        if not cooc:
            raise ValueError("K1 seed %s has no cooccurrence row" % seed)
        organica.append(primary)
        top = max(cooc, key=lambda m: m["primary"])
        best.append(top)
        winners = [m for m in cooc if m["primary"] == top["primary"]]
        for winner in winners:
            configs["window %s / floor %s"
                    % (winner["config"]["window"], winner["config"]["min_count"])] += 1
        if len(winners) > 1:
            ties += 1
        distinct.append(len({(m["primary"], m["precision"], m["recall"]) for m in cooc}))
        grid_sizes.append(len(cooc))
        long_rows = [m for m in cooc if m["config"]["window"] in LONG_WINDOWS]
        if len({(m["primary"], m["precision"], m["recall"]) for m in long_rows}) == 1:
            long_coincide += 1
        default = min(long_rows, key=lambda m: (str(m["config"]["window"]),
                                                m["config"]["min_count"]))
        long_defaults.append(default["primary"])
        gains.append(top["primary"] - default["primary"])
    organica_mean = sum(m["primary"] for m in organica) / len(organica)
    best_mean = sum(m["primary"] for m in best) / len(best)
    pairs = [round(GOLD_PAIRS / m["precision"]) for m in best]
    return {
        "seeds": len(rows),
        "organica_precision": _range([m["precision"] for m in organica]),
        "organica_recall": _range([m["recall"] for m in organica]),
        "organica_f1": _range([m["primary"] for m in organica]),
        "organica_mean": _fmt(organica_mean),
        "best_precision": _range([m["precision"] for m in best]),
        "best_recall": _range([m["recall"] for m in best]),
        "best_f1": _range([m["primary"] for m in best]),
        "best_mean": _fmt(best_mean),
        "gap": _fmt(organica_mean - best_mean),
        "pairs": "%d-%d" % (min(pairs), max(pairs)),
        "grid": min(grid_sizes),
        "distinct": "%d-%d" % (min(distinct), max(distinct)),
        "long_coincide": "%d of %d" % (long_coincide, len(rows)),
        "long_f1": _range(long_defaults),
        "gain": _range(gains),
        "ties": ties,
        "winner_configs": ", ".join(sorted(configs)),
        "bar": _fmt(organica_mean + PASS_MIN_IMPROVEMENT),
        "margin": _fmt(best_mean - (organica_mean + PASS_MIN_IMPROVEMENT)),
    }


def render(fig: dict) -> str:
    rows = (
        ("K1 seeds", str(fig["seeds"])),
        ("Organica precision", fig["organica_precision"]),
        ("Organica recall", fig["organica_recall"]),
        ("Organica F1", fig["organica_f1"]),
        ("Organica mean F1", fig["organica_mean"]),
        ("Best-of-grid precision", fig["best_precision"]),
        ("Best-of-grid recall", fig["best_recall"]),
        ("Best-of-grid F1", fig["best_f1"]),
        ("Best-of-grid mean F1", fig["best_mean"]),
        ("Mean gap (Organica minus best)", fig["gap"]),
        ("Emitted pairs behind the eighteen true ones", fig["pairs"]),
        ("Cooccurrence grid", "%d configurations per seed" % fig["grid"]),
        ("Distinct results per seed", fig["distinct"]),
        ("Seeds whose nine long-window configurations coincide", fig["long_coincide"]),
        ("That collapsed point's F1", fig["long_f1"]),
        ("Gain of the best configuration over it", fig["gain"]),
        ("Seeds whose maximum is tied", str(fig["ties"])),
        ("Configurations that ever win", fig["winner_configs"]),
        ("Draft pass bar", fig["bar"]),
        ("Pass bar below the best-of-grid mean", fig["margin"]),
    )
    lines = ["| Quantity | Value |", "|---|---|"]
    lines += ["| %s | %s |" % (name, value) for name, value in rows]
    return "\n".join(lines)


def _normalise(text: str) -> str:
    """Fold the en/em dashes and typographic minus the prose uses onto ASCII."""
    for mark in DASHES:
        text = text.replace(mark, "-")
    return text


def _figures_in(text: str) -> set[str]:
    return {match.group(0) for match in FIGURE.finditer(text)}


def _derived(fig: dict) -> tuple[set[str], set[str]]:
    """The aggregates, split into ranges that must be quoted whole and scalars."""
    ranges, scalars = set(), set()
    for value in fig.values():
        text = _normalise(str(value))
        pairs = RANGE.findall(text)
        if pairs:
            ranges |= {"%s-%s" % (low, high) for low, high in pairs}
        else:
            scalars |= _figures_in(text)
    return ranges, scalars


def _row_values(document: dict) -> list[set[str]]:
    """The figure triple each K1 row carries; a per-seed quote must fit one row."""
    rows = []
    for record in document.get("per_model_detail") or []:
        if record.get("family") != "K1":
            continue
        for model in record.get("models") or []:
            values = set()
            for key in ("precision", "recall", "primary"):
                value = model.get(key)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    values.add(_fmt(float(value)))
            if values:
                rows.append(values)
    return rows


def _quoted_problems(where: str, text: str, ranges: set[str], scalars: set[str],
                     rows: list[set[str]]) -> list[str]:
    """A quote is supported by a derived aggregate or by the one row it sits on."""
    problems = []
    text = _normalise(text)
    ends = set()
    for low, high in RANGE.findall(text):
        ends |= {low, high}
        pair = "%s-%s" % (low, high)
        if pair not in ranges:
            problems.append("%s quotes %s, which is not a range the artifact derives as a pair"
                            % (where, pair))
    singles = sorted(_figures_in(text) - ends)
    per_row = [token for token in singles if token not in scalars]
    if per_row and not any(set(per_row) <= values for values in rows):
        problems.append("%s quotes %s, and no single K1 row carries those figures together"
                        % (where, ", ".join(per_row)))
    return problems


def _strings(value, path: str = ""):
    """Every string leaf of a record, with a dotted path for the message."""
    if isinstance(value, str):
        yield path or "<record>", value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _strings(item, "%s.%s" % (path, key) if path else str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _strings(item, "%s[%d]" % (path, index))


def _ledger_rows(ledger_text: str) -> list[dict]:
    ledger = json.loads(ledger_text)
    return [row for row in ((ledger.get("constraint_ledger") or {}).get("rows") or [])
            if str(row.get("constraint") or "").startswith("K1")]


def _declared_gap(relative: str):
    """The baseline_gap a registration declares, or None when it cannot be read."""
    try:
        record = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return (record.get("threshold_values") or {}).get("baseline_gap")


def _compare_gap(label: str, declared, gap: float, fig: dict) -> list[str]:
    if not isinstance(declared, (int, float)) or isinstance(declared, bool):
        return ["%s records no readable numeric baseline_gap" % label]
    if round(float(declared), 6) != gap:
        return ["%s records baseline_gap %s, but the K1 rows give a mean gap of %s "
                "(Organica %s minus best-of-grid %s)"
                % (label, _fmt(float(declared)), _fmt(gap), fig["organica_mean"], fig["best_mean"])]
    return []


def _gap_problems(fig: dict, ledger_text: str, draft_text: str) -> list[str]:
    """The page's central claim: the ledger's baseline_gap is the derived mean gap."""
    gap = round(float(fig["gap"]), 6)
    problems = []
    try:
        rows = _ledger_rows(ledger_text)
    except ValueError as exc:
        return ["the ledger is not JSON: %s" % exc]
    if not rows:
        problems.append("the ledger carries no K1 row, so its baseline_gap is not checked "
                        "against the artifact")
    for row in rows:
        relative = row.get("registration")
        if not relative:
            problems.append("the ledger's K1 row names no registration")
            continue
        problems += _compare_gap("the ledger's %s" % relative,
                                 _declared_gap(str(relative)), gap, fig)
    declared = (json.loads(draft_text).get("threshold_values") or {}).get("baseline_gap")
    problems += _compare_gap("the draft's threshold_values", declared, gap, fig)
    return problems


def _block_of(text: str) -> str:
    start = text.find(BLOCK_BEGIN)
    end = text.find(BLOCK_END)
    if start < 0 or end < start:
        raise ValueError("the page carries no figures block")
    return text[start + len(BLOCK_BEGIN):end].strip("\n")


def check(document: dict | None = None, *, page: str | None = None,
          draft: str | None = None, manual: str | None = None,
          ledger: str | None = None) -> list[str]:
    document = document if document is not None else json.loads(
        ARTIFACT.read_text(encoding="utf-8"))
    page = page if page is not None else PAGE.read_text(encoding="utf-8")
    draft = draft if draft is not None else DRAFT.read_text(encoding="utf-8")
    manual = manual if manual is not None else MANUAL.read_text(encoding="utf-8")
    ledger = ledger if ledger is not None else LEDGER.read_text(encoding="utf-8")

    fig = figures(document)
    problems = []

    expected = render(fig)
    if _block_of(page) != expected:
        problems.append("the page's figures block does not match the artifact; run --write")

    prose = page.replace(_block_of(page), "")
    stray = sorted(DECIMAL.findall(prose))
    if stray:
        problems.append("the page quotes figures outside its generated block: %s"
                        % ", ".join(stray))

    ranges, scalars = _derived(fig)
    rows = _row_values(document)
    for path, text in _strings(figures_payload(draft), "pressure_test"):
        problems += _quoted_problems("the draft's %s" % path, text, ranges, scalars, rows)

    manual_quoted = set()
    for number, line in enumerate(manual.splitlines(), 1):
        if "assertion-provenance" not in line.lower():
            continue
        manual_quoted |= _figures_in(line)
        problems += _quoted_problems("manual line %d" % number, line, ranges, scalars, rows)
    quoted = _figures_in(json.dumps(figures_payload(draft), ensure_ascii=False))
    for token in REQUIRED:
        if token not in manual_quoted:
            problems.append("the manual rows no longer quote the required figure %s" % token)
        if token not in quoted:
            problems.append("the draft no longer quotes the required figure %s" % token)
    problems += _gap_problems(fig, ledger, draft)
    return problems


def figures_payload(draft_text: str) -> dict:
    return json.loads(draft_text).get("pressure_test") or {}


def write(page: str | None = None) -> str:
    document = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    page = page if page is not None else PAGE.read_text(encoding="utf-8")
    body = render(figures(document))
    start, end = page.index(BLOCK_BEGIN) + len(BLOCK_BEGIN), page.index(BLOCK_END)
    return page[:start] + "\n" + body + "\n" + page[end:]


def self_test() -> list[str]:
    """The checker must fail on a stale, borrowed or moved figure and pass when clean."""
    document = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    draft_text = DRAFT.read_text(encoding="utf-8")
    ledger = LEDGER.read_text(encoding="utf-8")
    failures = []
    if check(document):
        failures.append("the committed files already fail the check")
    bumped = copy.deepcopy(document)
    for record in bumped["per_model_detail"]:
        if record.get("family") == "K1":
            for model in record["models"]:
                if model.get("model") == "organica":
                    model["primary"] = round(model["primary"] + 0.01, 6)
            break
    page = PAGE.read_text(encoding="utf-8")
    if not check(bumped, page=page):
        failures.append("a changed artifact did not fail the page check")
    doctored = page.replace(BLOCK_END, "0.999999\n" + BLOCK_END, 1)
    if not check(document, page=doctored):
        failures.append("an unsupported figure in the prose did not fail the check")
    draft = draft_text.replace("0.935972", "0.935973", 1)
    if not check(document, draft=draft):
        failures.append("an unsupported figure in the draft did not fail the check")
    borrowed = draft_text.replace("the engine reaches 0.313043 at precision 0.185567",
                                  "the engine reaches 0.307692 at precision 0.185567", 1)
    if borrowed == draft_text:
        failures.append("the self-test could not find the per-seed quote it doctors")
    elif not check(document, draft=borrowed):
        failures.append("a figure borrowed from another K1 row did not fail the check")
    stitched = draft_text.replace("F1 0.878049-0.972973", "F1 0.878049-0.947368", 1)
    if stitched == draft_text:
        failures.append("the self-test could not find the range it stitches")
    elif not check(document, draft=stitched):
        failures.append("a stitched range did not fail the check")
    moved = draft_text.replace('"baseline_gap": -0.623961', '"baseline_gap": -0.623960', 1)
    if moved == draft_text:
        failures.append("the self-test could not find the draft baseline_gap it moves")
    elif not check(document, draft=moved):
        failures.append("a draft baseline_gap that disagrees with the artifact did not fail")
    doctored = json.loads(ledger)
    k1_rows = [row for row in doctored["constraint_ledger"]["rows"]
               if str(row.get("constraint") or "").startswith("K1")]
    if not k1_rows:
        failures.append("the ledger no longer carries a K1 row to doctor")
    else:
        for row in k1_rows:
            row["registration"] = "docs/constraint_registrations/K2-belief-revision.json"
        if not check(document, ledger=json.dumps(doctored)):
            failures.append("a ledger baseline_gap that disagrees with the artifact did not fail")
    return failures


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="render the figures block")
    parser.add_argument("--check", action="store_true", help="verify against the artifact")
    parser.add_argument("--self-test", action="store_true", help="prove the checker fails")
    args = parser.parse_args(argv)

    if args.write:
        PAGE.write_text(write(), encoding="utf-8")
        print("pressure test: figures block written from the artifact")
        return 0
    if args.self_test:
        failures = self_test()
        if failures:
            for failure in failures:
                print("FAIL:", failure)
            return 1
        print("self-test ok: the checker rejects a moved artifact, a stray prose figure, "
              "a mistyped draft figure, a figure borrowed from another K1 row, a stitched "
              "range, and a draft or ledger baseline_gap that disagrees with the artifact")
        return 0
    problems = check()
    if problems:
        for problem in problems:
            print("FAIL:", problem)
        return 1
    fig = figures(json.loads(ARTIFACT.read_text(encoding="utf-8")))
    print("pressure test: page, draft, manual and ledger match the artifact "
          "(%d seeds, gap %s = ledger baseline_gap, grid %d configurations)"
          % (fig["seeds"], fig["gap"], fig["grid"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
