"""The two missing Half-A registrations must exist, resolve, and keep their commitments."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Q021 = ROOT / "docs/Q021-TRANSFER-RE-DERIVATION-PREREGISTRATION.md"
Q017 = ROOT / "docs/Q017-ADMISSION-DECISION-PREREGISTRATION.md"
Q021_RESULTS = ROOT / "docs/Q021-TRANSFER-RE-DERIVATION-RESULTS.md"
REGISTRY = ROOT / "docs/research_question_registry.json"


def test_q021_names_its_fresh_block_bar_and_controls():
    text = Q021.read_text(encoding="utf-8")
    assert "FROZEN, NOT RUN" in text
    assert "20262101" in text and "20262110" in text
    assert "40 (4 arms x 10 seeds = 40 cells)" in text
    for arm in ("treatment", "control_naive", "control_pruned", "control_orthogonal"):
        assert arm in text
    assert "1.25" in text and "0.10" in text
    assert "NO_TRANSFER_ADVANTAGE" in text


def test_q021_seed_block_is_not_reused_elsewhere():
    for path in (ROOT / "docs").glob("*.md"):
        if path in (Q021, Q021_RESULTS):
            continue
        assert "20262101" not in path.read_text(encoding="utf-8"), path


def test_q017_is_decision_only_and_cannot_run_a_cell():
    text = Q017.read_text(encoding="utf-8")
    assert "DECISION-ONLY, NO CELL" in text
    assert "RETIRE_NO_FURTHER_VARIANTS" in text
    assert "BUILD_REQUIRED_VARIANT" in text
    assert "UNREAD" in text
    assert "runs no engine" in text


def test_the_registry_links_both_records():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in registry["questions"]}
    for qid, path in (("Q017", Q017), ("Q021", Q021)):
        assert any((ROOT / raw).resolve() == path.resolve()
                   for raw in by_id[qid]["preregistrations"]), qid
