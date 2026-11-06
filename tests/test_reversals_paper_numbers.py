"""Every number in Paper 07's results tables, checked against the artifact it came from.

Paper 07 states the five preregistered architecture verdicts and the Phase K matched ablations. Those are exactly the
kind of values that drift when a manuscript is written by hand (AGENTS.md rule 27), so this module rebuilds each row
from the artifact and compares it to the row the paper prints. It also asserts that the checker can fail.

The effect metric is the one the artifact declares for each prediction (`effect_metric`), falling back to the largest
absolute delta only where the artifact declares none (P1 does not), so a change in the declared metric changes the
expectation.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAPER = "papers/07_architecture_predictions_reversed.md"

# Each header cell identifies exactly one table in the paper.
VERDICT_HEADER = "Effect metric"
FAMILY_HEADER = "Best simple baseline"
ABLATION_HEADER = "Matched ablation"


def load_json(rel: str):
    return json.loads(io.open(REPO / rel, encoding="utf-8").read())


def paper_text() -> str:
    return io.open(REPO / PAPER, encoding="utf-8").read()


def table_rows(header_cell: str) -> list[list[str]]:
    """Split the one table whose header contains `header_cell` into cell lists."""
    lines = paper_text().splitlines()
    starts = [i for i, line in enumerate(lines)
              if line.startswith("|") and header_cell in line]
    assert len(starts) == 1, "expected exactly one table headed %r, found %d" % (header_cell, len(starts))
    rows = []
    for line in lines[starts[0] + 1:]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(set(cell) <= set("-: ") for cell in cells):
            continue  # the |---|---| separator
        rows.append(cells)
    return rows


def interval(cell: str) -> list[float]:
    """Parse a `[a, b]` cell."""
    body = cell.strip()
    assert body.startswith("[") and body.endswith("]"), "not an interval cell: %r" % cell
    low, high = body[1:-1].split(",")
    return [float(low), float(high)]


def expected_verdicts() -> dict[str, dict]:
    """Each prediction's row, resolved on the effect metric the artifact declares."""
    out = {}
    for r in load_json("docs/verdicts.json")["results"]:
        declared = r.get("effect_metric")
        if declared is None:
            mover = max(r["detail"], key=lambda d: abs(d["delta"]))
        else:
            matches = [d for d in r["detail"] if d["metric"] == declared]
            assert len(matches) == 1, "%s declares effect metric %r but the detail has %d rows for it" % (
                r["id"], declared, len(matches))
            mover = matches[0]
        out[r["id"]] = {
            "claim": r["claim"], "colony": r["colony"], "metric": mover["metric"],
            "reference": mover["reference_value"], "colony_value": mover["colony_value"],
            "delta": mover["delta"], "floor": mover["noise_floor"], "verdict": r["verdict"],
        }
    return out


def parsed_verdicts() -> dict[str, dict]:
    out = {}
    for cells in table_rows(VERDICT_HEADER):
        assert len(cells) == 9, "verdict row has %d cells, expected 9: %r" % (len(cells), cells)
        out[cells[0]] = {
            "claim": cells[1], "colony": cells[2], "metric": cells[3],
            "reference": float(cells[4]), "colony_value": float(cells[5]),
            "delta": float(cells[6]), "floor": float(cells[7]), "verdict": cells[8],
        }
    return out


def expected_families() -> dict[str, dict]:
    out = {}
    for name, s in load_json("docs/phase_k_results.json")["summaries"].items():
        d = s["paired_organica_minus_best_baseline"]
        out[name] = {
            "organica": s["organica_primary_mean"],
            "baseline": s["best_simple_baseline_primary_mean"],
            "delta": d["mean"], "interval": d["interval"], "verdict": s["verdict"],
        }
    return out


def parsed_families() -> dict[str, dict]:
    out = {}
    for cells in table_rows(FAMILY_HEADER):
        assert len(cells) == 6, "family row has %d cells, expected 6: %r" % (len(cells), cells)
        out[cells[0]] = {
            "organica": float(cells[1]), "baseline": float(cells[2]), "delta": float(cells[3]),
            "interval": interval(cells[4]), "verdict": cells[5],
        }
    return out


def expected_ablations() -> dict[str, dict]:
    out = {}
    for name, s in load_json("docs/phase_k_results.json")["summaries"].items():
        a = s["matched_ablation"]
        out[name] = {
            "ablation": a["name"], "mean": a["primary_mean"],
            "delta": a["paired_organica_minus_ablation"]["mean"],
            "interval": a["paired_organica_minus_ablation"]["interval"],
        }
    return out


def parsed_ablations() -> dict[str, dict]:
    out = {}
    for cells in table_rows(ABLATION_HEADER):
        assert len(cells) == 5, "ablation row has %d cells, expected 5: %r" % (len(cells), cells)
        out[cells[0]] = {
            "ablation": cells[1], "mean": float(cells[2]), "delta": float(cells[3]),
            "interval": interval(cells[4]),
        }
    return out


def compare(actual: dict, expected: dict, tol: float = 5e-4) -> list[str]:
    """Numeric cells must agree to `tol`; text cells must agree exactly."""
    problems = []
    for key, want in expected.items():
        have = actual.get(key)
        if have is None:
            problems.append("missing %s" % key)
            continue
        for field, value in want.items():
            if isinstance(value, (int, float)):
                if abs(float(have[field]) - float(value)) > tol:
                    problems.append("%s.%s: paper %r, artifact %r" % (key, field, have[field], value))
            elif isinstance(value, list):
                for i, bound in enumerate(value):
                    if abs(float(have[field][i]) - float(bound)) > tol:
                        problems.append("%s.%s[%d]: paper %r, artifact %r"
                                        % (key, field, i, have[field][i], bound))
            elif str(have[field]).lower() != str(value).lower():
                problems.append("%s.%s: paper %r, artifact %r" % (key, field, have[field], value))
    return problems


class TestTierOneVerdicts:
    def test_every_prediction_is_in_the_paper(self):
        expected, actual = expected_verdicts(), parsed_verdicts()
        assert set(actual) == set(expected), (
            "paper's verdict table must contain exactly the five predictions; found %r" % sorted(actual))

    def test_rows_agree_with_the_artifact(self):
        problems = compare(parsed_verdicts(), expected_verdicts())
        assert not problems, "Paper 07's verdict table disagrees with docs/verdicts.json:\n" + "\n".join(problems)

    def test_the_headline_count_is_three_reversed(self):
        verdicts = [r["verdict"] for r in load_json("docs/verdicts.json")["results"]]
        assert verdicts.count("REVERSED") == 3 and verdicts.count("SUPPORTED") == 2
        assert "Three reversed" in paper_text()


class TestPhaseKTables:
    def test_family_rows_agree_with_the_artifact(self):
        problems = compare(parsed_families(), expected_families())
        assert not problems, "Paper 07's Phase K table disagrees with docs/phase_k_results.json:\n" + "\n".join(problems)

    def test_ablation_rows_agree_with_the_artifact(self):
        problems = compare(parsed_ablations(), expected_ablations())
        assert not problems, "Paper 07's ablation table disagrees with docs/phase_k_results.json:\n" + "\n".join(problems)

    def test_all_three_families_are_reversed(self):
        assert all(s["verdict"] == "REVERSED"
                   for s in load_json("docs/phase_k_results.json")["summaries"].values())


class TestTheCheckCanFail:
    def test_a_wrong_delta_is_rejected(self):
        expected = expected_verdicts()
        actual = parsed_verdicts()
        actual["P2"]["delta"] = actual["P2"]["delta"] + 0.5
        problems = compare(actual, expected)
        assert any("P2.delta" in p for p in problems), "the checker did not notice a fabricated delta"

    def test_a_wrong_interval_is_rejected(self):
        expected = expected_families()
        actual = parsed_families()
        actual["K1"]["interval"][0] = actual["K1"]["interval"][0] - 0.5
        problems = compare(actual, expected)
        assert any("K1.interval" in p for p in problems), "the checker did not notice a fabricated bound"

    def test_a_wrong_verdict_label_is_rejected(self):
        expected = expected_verdicts()
        actual = parsed_verdicts()
        actual["P3"]["verdict"] = "SUPPORTED"
        problems = compare(actual, expected)
        assert any("P3.verdict" in p for p in problems), "the checker did not notice a fabricated verdict"


COMPANION_03 = "papers/03_curiosity_through_contradiction.md"
COMPANION_04 = "papers/04_dream_driven_structural_exploration.md"


def companion_text(rel: str) -> str:
    return io.open(REPO / rel, encoding="utf-8").read()


class TestCompanionPapers:
    """Papers 03 and 04 restate Paper 07's effect sizes; those restatements are checked too."""

    def test_03_quotes_the_reversal_effect_sizes(self):
        text, expected = companion_text(COMPANION_03), expected_verdicts()
        for pid in ("P2", "P3", "P5"):
            quoted = "%+.3f" % expected[pid]["delta"]
            assert quoted in text, "Paper 03 does not quote %s (%s)" % (pid, quoted)
        assert "%.3f" % expected["P2"]["floor"] in text

    def test_04_quotes_the_no_dream_delta(self):
        text, expected = companion_text(COMPANION_04), expected_verdicts()
        quoted = "%+.3f" % expected["P4"]["delta"]
        assert quoted in text, "Paper 04 does not quote P4's delta (%s)" % quoted

    def test_both_papers_cite_paper_07(self):
        for rel in (COMPANION_03, COMPANION_04):
            assert "07_architecture_predictions_reversed.md" in companion_text(rel), rel
