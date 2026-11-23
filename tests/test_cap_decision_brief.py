"""The cap decision brief's figures must be the Q2 artifact's figures.

The brief exists so a pending owner decision can be taken on the record. A number typed into that
brief would be a new claim, not a restatement (rule 27), so `missing()` compares every quoted figure
against `docs/presence_cap_run.json` and `test_the_check_can_fail` proves it can reject a drift.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRIEF = ROOT / "docs" / "CAP-DECISION-BRIEF.md"
RUN = ROOT / "docs" / "presence_cap_run.json"


def _flat(text: str) -> str:
    return text.replace("*", "").replace("`", "").replace(",", "")


def _fragments() -> list[str]:
    run = json.loads(RUN.read_text(encoding="utf-8"))
    det, wit, gains = run["details"], run["witness"], sorted(run["gains"], key=lambda r: r["seed"])
    found = [
        "mean paired gain at 112: %.6f" % det["mean_gain"],
        "95%% paired lower bound: %.6f" % det["lower_bound"],
        "bar of %d" % det["bar"],
        "reach-limited ceiling: %s" % det["ceiling"],
        "gain over the ceiling: %.6f" % det["ceiling_ratio"],
        "witness fingerprint: %s" % wit["asserted_fingerprint"],
        "at cap 80 the mean asserted world edges over the cap-40 arm is %.2f"
        % (sum(r["80"] - r["40"] for r in gains) / len(gains)),
        "at cap 112 it is %.2f" % (sum(r["112"] - r["40"] for r in gains) / len(gains)),
        "%d of 6" % det["positive_seeds"],
        "%d of 6" % det["reach_changed_seeds"],
    ]
    for row in gains:
        found.append("| %d | %d | %d | %d | %d | +%d |" % (
            row["seed"], row["40"], row["80"], row["112"], row["1000000000"], row["gain_112"]))
    return found


def missing(text: str | None = None) -> list[str]:
    text = BRIEF.read_text(encoding="utf-8") if text is None else text
    flat = _flat(text)
    return [fragment for fragment in _fragments() if _flat(fragment) not in flat]


def test_the_brief_restates_only_figures_the_artifact_holds():
    assert missing() == [], missing()


def test_the_check_can_fail():
    text = BRIEF.read_text(encoding="utf-8").replace("15.833333", "16.833333")
    assert "16.833333" in text
    assert missing(text)


def test_the_recorded_decision_carries_date_rationale_and_version():
    """A decision row without a date, a rationale or a version is not a record, and an empty table is not a decision."""
    text = BRIEF.read_text(encoding="utf-8")
    assert "BRIEFING FOR AN OWNER DECISION" in text
    assert "*(none taken)*" not in text
    row = [line for line in text.splitlines() if line.startswith("| E1 — split the constant")]
    assert len(row) == 1, row
    assert "2026-11-10" in row[0]
    assert "in force" in row[0] and "0.14.0" in row[0]
    assert "engine_lineage.json" in row[0]
    assert "proof" in row[0]
    assert "Question 2 is decided" in text
    level = [line for line in text.splitlines() if line.startswith("| C — raise to 112")]
    assert len(level) == 1, level
    assert "2026-11-11" in level[0]
    assert "0.15.0" in level[0] and "not in force" in level[0]
