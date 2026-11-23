"""The loop retention/strength extension stays post hoc and internally current."""
LAYER = "dry-run"

from pathlib import Path

import pytest

from benchmarks import loop_persistence_assertion_model as block


def _missing_captures() -> list[Path]:
    """The gitignored loop captures `--check` recomputes the model from."""
    return [block.CACHE / ("%d.json" % seed) for seed in block.SEEDS
            if not (block.CACHE / ("%d.json" % seed)).exists()]


def _skip_without_captures() -> None:
    missing = _missing_captures()
    if missing:
        pytest.skip(
            "the loop captures are a gitignored .scratch/ run artifact and %d of "
            "%d are absent, starting with %s; collect them with "
            "`python -m benchmarks.loop_persistence_assertion_model --collect`."
            % (len(missing), len(block.SEEDS), missing[0]))


def test_artifact_is_posthoc_and_current():
    _skip_without_captures()
    assert block.main(["--check"]) == 0
    art = block._load(block.ARTIFACT)
    assert art["posthoc"] is True
    assert art["prereg"] is None
    assert art["summary"]["confirmatory_verdict"] is None
    assert all(art["summary"]["integrity"].values())


def test_formation_control_is_present_and_derived_from_loop_onset(monkeypatch, tmp_path):
    art = block._load(block.ARTIFACT)
    assert all(row["formation_cycle"] == min(row["loop_cycles"])
               for row in art["rows"])
    assert all(abs(row["formation_fraction"]
                   - row["formation_cycle"] / float(block.CYCLES)) < 1e-15
               for row in art["rows"])
    assert art["summary"]["integrity"]["formation_finite"] is True
    assert art["summary"]["integrity"]["controlled_converged"] is True
    assert art["summary"]["controlled"]["n"] == 177
    assert art["summary"]["controlled"]["events"] == 77
    assert "formation" in art["summary"]["controlled"]["coefficients"]
    assert art["summary"]["formation_control_readout"]
    assert "Formation-control readout" in block.render(art)
    # The skip above must be able to fire, and must stop firing once the files
    # exist: a predicate that always reported something missing would skip the
    # recomputation in the working tree too.
    monkeypatch.setattr(block, "CACHE", tmp_path / "absent")
    assert len(_missing_captures()) == len(block.SEEDS), (
        "an empty cache directory must report every seed as missing")
    (tmp_path / "absent").mkdir()
    for seed in block.SEEDS:
        (tmp_path / "absent" / ("%d.json" % seed)).write_text("{}", encoding="utf-8")
    assert _missing_captures() == [], "the prerequisite reports a written file as missing"
    monkeypatch.undo()
    assert _missing_captures() in ([], [block.CACHE / ("%d.json" % s)
                                      for s in block.SEEDS])


def test_strength_quartiles_cover_every_row():
    art = block._load(block.ARTIFACT)
    groups = art["summary"]["strength_quartiles"]
    assert sum(group["n"] for group in groups) == len(art["rows"])
    assert sum(group["events"] for group in groups) == art["summary"]["events"]


def test_check_refuses_a_confirmatory_verdict():
    _skip_without_captures()
    art = block._load(block.ARTIFACT)
    art["confirmatory_verdict"] = "CONFIRMED"
    assert "confirmatory verdict present" in block.problems(art)
