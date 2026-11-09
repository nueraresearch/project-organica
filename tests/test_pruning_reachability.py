"""The fourth death reason must be reported as unreachable or as measured, never as silence.

`docs/DECAY-ATTRIBUTION.md` printed `pruned | not measurable` beside a 68.97 percent decayed
share, which reads as "pruning does not participate". The branch is unreachable from any edge
the ledger follows, and the engine prunes on the same run. Both halves are checked here, and the
gate that reports them is proved able to fail (AGENTS.md rule 25(c)).
"""

import json
from pathlib import Path

from benchmarks import pruning_reachability as pr

ROOT = Path(__file__).resolve().parent.parent


def test_the_branch_is_unreachable_from_a_stable_edge():
    stable, death = pr.thresholds()
    bound = pr.arithmetic(stable, death, pr.FACTOR)
    assert bound["unreachable_from_a_stable_edge"]
    assert bound["one_step_from_a_threshold_edge"] >= death
    assert bound["input_the_branch_would_need"] < stable
    assert bound["margin_above_the_branch"] > 0


def test_the_branch_fires_once_the_edge_is_followed_below_the_threshold():
    stable, death = pr.thresholds()
    steps = pr.trace(stable, death, pr.FACTOR)
    reasons = [step["reason"] for step in steps]
    assert reasons[0] == "decayed", "a stable edge's first step is a decay, not a prune"
    assert "pruned" in reasons, "the rule must be able to reach the branch at all"
    assert reasons.index("pruned") > 1, "one step must not be enough, or the ledger would see it"


def test_the_ledger_takes_one_step_and_that_step_cannot_be_a_prune():
    stable, death = pr.thresholds()
    first = pr.trace(stable, death, pr.FACTOR)[0]
    assert first["step"] == 1
    assert first["reason"] != "pruned"


def test_the_engine_and_the_ledger_disagree_on_the_same_run():
    artifact = json.loads((ROOT / "docs" / "pruning_reachability.json").read_text(encoding="utf-8"))
    engine = artifact["observed"]["engine"]
    assert engine["engine_candidate_counters"]["pruned"] > 0, "pruning must be live in the engine"
    assert engine["ledger_edge_deaths"].get("pruned", 0) == 0, "the ledger must not see it"
    assert engine["ledger_edge_deaths"], "the ledger must have observed some deaths at all"


def test_the_gates_all_pass_on_the_committed_artifact():
    artifact = json.loads((ROOT / "docs" / "pruning_reachability.json").read_text(encoding="utf-8"))
    assert all(artifact["gates"].values()), artifact["gates"]
    assert artifact["label"] == pr.NO_BRANCH


def test_the_page_is_generated_from_the_artifact():
    artifact = json.loads((ROOT / "docs" / "pruning_reachability.json").read_text(encoding="utf-8"))
    page = (ROOT / "docs" / "PRUNING-REACHABILITY.md").read_text(encoding="utf-8")
    assert page == pr.render(artifact)
    assert "{" not in page and "}" not in page, "a placeholder would be a silent number"


def test_the_check_mode_fails_when_the_artifact_is_tampered(tmp_path, monkeypatch):
    artifact = json.loads((ROOT / "docs" / "pruning_reachability.json").read_text(encoding="utf-8"))
    tampered = dict(artifact, label="MEASURED_ZERO")
    bad = tmp_path / "pruning_reachability.json"
    bad.write_text(json.dumps(tampered, indent=2), encoding="utf-8")
    monkeypatch.setattr(pr, "ARTIFACT", bad)
    assert pr.check() != [], "a label the measurement does not support must be refused"


def test_the_check_mode_passes_on_the_committed_artifact():
    assert pr.check() == []
