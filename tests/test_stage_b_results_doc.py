"""The Stage B result document restates two artifacts, so check it against them.

Every row is rebuilt from the artifact and asserted to appear verbatim; the document is
not allowed to drift from the numbers it claims to report.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _doc() -> str:
    return (ROOT / "docs" / "stage_b_results.md").read_text(encoding="utf-8")


def _analysis() -> dict:
    return json.loads((ROOT / "docs" / "stage_b_runner.json").read_text(encoding="utf-8"))


def _check() -> dict:
    return json.loads((ROOT / "docs" / "stage_b_rerun_check.json").read_text(encoding="utf-8"))


def test_result_table_matches_the_assembly():
    analysis = _analysis()["analysis"]
    doc = _doc()
    for configuration, value in analysis["by_configuration"].items():
        row = (f"| `{configuration}` | {value['worlds']} | {value['eligible_scored']} | "
               f"{value['ineligible']} | {value['censored']} | {value['onset_median']:g} | "
               f"{value['spearman']:+.4f} | [{value['interval'][0]:.4f}, "
               f"{value['interval'][1]:.4f}] | "
               f"{'yes' if value['predicted_sign_held'] else 'no'} |")
        assert row in doc, row
        assert f"| `{configuration}` | {value['worlds']} |" in doc


def test_verdict_and_aggregation_rule_come_from_the_artifact():
    analysis = _analysis()["analysis"]
    doc = _doc()
    assert f"`{analysis['verdict']}`" in doc
    assert analysis["aggregation_rule"] in doc
    assert str(analysis["replicates"]) in doc.replace(",", "")


def test_reproduction_table_matches_the_check():
    doc = _doc()
    for cell in _check()["cells"]:
        old, new = cell["assembly"], cell["rerun"]
        score_old = "--" if old["outcome"] is None else f"{old['outcome']:.6f}"
        score_new = "--" if new["outcome"] is None else f"{new['outcome']:.6f}"
        row = (f"| `{cell['configuration']}` | {cell['seed']} | {old['onset']} -> {new['onset']} | "
               f"{'yes' if old['eligible'] else 'no'} -> {'yes' if new['eligible'] else 'no'} | "
               f"{score_old} -> {score_new} | "
               f"{cell['comparison']['cycles_differing']} of {old['cycles_run']} |")
        assert row in doc, row


def test_hash_seed_sweep_is_reported_as_measured():
    doc = _doc()
    runs = _check()["hash_seed_sweep"]["runs"]
    assert ", ".join(str(r["onset"]) for r in runs) in doc
    assert ", ".join(r["pythonhashseed"] for r in runs) in doc


def test_two_to_one_is_called_underpowered_not_reversed():
    doc = _doc()
    assert "under-powered, not a reversal" in doc
    assert "is a reversal" not in doc


def test_document_has_no_template_placeholders():
    for line in _doc().splitlines():
        assert not ("{" in line and "}" in line and "`" not in line), line


def test_the_tie_break_is_left_in_the_frozen_engine():
    doc = _doc()
    decisions = (ROOT / "docs" / "DECISION-STAGE-B-SEQUENCE.md").read_text(encoding="utf-8")
    assert "## D15" in decisions and "separately versioned engine change" in decisions
    assert "§D15" in doc
    assert "separately versioned engine change" in doc
    assert "is not regenerated under that" in doc
