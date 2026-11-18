"""The Phase K summary, and the campaign's reader of its own live recording.

The resume tests invoke ``run_campaign``'s non-cell path with the per-seed job
replaced by a fake, so no world is built and no cycle is executed.  They assert
the property a resumed run needs: one record per cell, and a recording that
cannot be read is never appended to.
"""
from __future__ import annotations
LAYER = "dry-run"  # benchmarks/test_layers.py: the harness's resume path, no cell

import json
from pathlib import Path

import pytest

from benchmarks import phase_k_campaign as campaign

SEEDS = list(range(20910101, 20910111))
RESUME_SEEDS = [20910201, 20910202, 20910203]


def _records() -> list[dict]:
    """Ten paired records whose ablation is identical to Organica."""
    return [
        {
            "seed": seed,
            "organica": 0.5,
            "best_simple_baseline": {"primary": 0.9},
            "all_models": [
                {"model": "organica"},
                {"model": "organica_NO_FALSIFICATION"},
            ],
            "ablation": 0.5,
        }
        for seed in SEEDS
    ]


def test_a_null_ablation_interval_does_not_implicate_the_mechanism():
    summary = campaign.summarize(_records(), "K2")
    ablation = summary["matched_ablation"]
    paired = ablation["paired_organica_minus_ablation"]

    assert paired["interval"] == [0.0, 0.0], paired
    assert ablation["mechanism_implicated"] is False, (
        "a null Organica-minus-ablation interval must not be labelled a mechanism effect")


def test_a_positive_ablation_interval_implicates_the_mechanism():
    records = _records()
    for record in records:
        record["organica"] = 0.6
    summary = campaign.summarize(records, "K2")
    ablation = summary["matched_ablation"]
    paired = ablation["paired_organica_minus_ablation"]

    assert paired["interval"] == [0.1, 0.1], paired
    assert ablation["mechanism_implicated"] is True


def test_a_crossing_ablation_interval_does_not_implicate_the_mechanism():
    records = _records()
    for i, record in enumerate(records):
        record["organica"] = 0.6 if i % 2 == 0 else 0.4
    summary = campaign.summarize(records, "K2")
    ablation = summary["matched_ablation"]
    paired = ablation["paired_organica_minus_ablation"]

    assert paired["interval"][0] < 0.0 < paired["interval"][1], paired
    assert ablation["mechanism_implicated"] is False, (
        "an Organica-minus-ablation interval crossing zero must not be labelled a mechanism effect")


# ==================================================================
# The campaign's resume path: one reader, one record per cell
# ==================================================================

def _record(seed: int, organica: float = 0.50, family: str = "K1") -> dict:
    """One per-seed record in the shape ``_run_one`` writes."""
    return {
        "family": family,
        "seed": seed,
        "organica": organica,
        "ablation": organica - 0.10,
        "best_simple_baseline": {"model": "temporal_graph", "primary": 0.90,
                                 "config": {"lookback": 3, "min_count": 3}},
        "all_models": [{"model": "organica", "primary": organica},
                       {"model": "organica_NO_FALSIFICATION",
                        "primary": organica - 0.10}],
        "manipulation": None,
        "protocol": {"switch_cycle": 200},
    }


def _row(seed: int, **kwargs) -> str:
    return json.dumps(_record(seed, **kwargs))


def _write(path: Path, lines: list[str], *, torn_tail: bool = False) -> Path:
    """Write one line per element; a torn tail is written without its newline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + ("" if torn_tail else "\n"),
                    encoding="utf-8")
    return path


class _FakeJob:
    """The campaign's per-seed job, replaced: no world is built, no cycle runs."""

    def __init__(self) -> None:
        self.seeds: list[int] = []

    def __call__(self, job):
        family, seed, _scale, _factory = job
        self.seeds.append(seed)
        return _record(seed, family=family)


def _resume(tmp_path: Path, monkeypatch, fake: _FakeJob):
    monkeypatch.setattr(campaign, "_run_one", fake)
    out = tmp_path / "phase_k_results.json"
    result = campaign.run_campaign(["K1"], list(RESUME_SEEDS), 1,
                                   out_path=out, resume=True)
    return result, out, out.with_suffix(".ndjson")


def test_a_resume_refuses_an_unreadable_row_and_runs_nothing(tmp_path, monkeypatch):
    recording = _write(tmp_path / "phase_k_results.ndjson",
                       [_row(RESUME_SEEDS[0]), "{not json",
                        _row(RESUME_SEEDS[1])])
    fake = _FakeJob()
    with pytest.raises(campaign.CheckpointError) as caught:
        _resume(tmp_path, monkeypatch, fake)

    assert caught.value.code == "CHECKPOINT_CORRUPT"
    assert caught.value.evidence["line"] == 2
    assert fake.seeds == [], "a recording that cannot be read must not start a cell"
    assert not (tmp_path / "phase_k_results.json").exists()
    assert len(recording.read_text(encoding="utf-8").splitlines()) == 3


def test_a_resume_refuses_two_rows_that_disagree_about_one_cell(tmp_path, monkeypatch):
    _write(tmp_path / "phase_k_results.ndjson",
           [_row(RESUME_SEEDS[0], organica=0.50),
            _row(RESUME_SEEDS[0], organica=0.60),
            _row(RESUME_SEEDS[1])])
    fake = _FakeJob()
    with pytest.raises(campaign.CheckpointError) as caught:
        _resume(tmp_path, monkeypatch, fake)

    assert caught.value.code == "CHECKPOINT_DUPLICATE_DISAGREES"
    assert caught.value.evidence["first_line"] == 1
    assert caught.value.evidence["second_line"] == 2
    assert "organica" in caught.value.evidence["differing_fields"]
    assert fake.seeds == []


def test_a_resume_repairs_a_torn_tail_before_appending(tmp_path, monkeypatch):
    torn = json.dumps(_record(RESUME_SEEDS[2]))[:60]
    _write(tmp_path / "phase_k_results.ndjson",
           [_row(RESUME_SEEDS[0]), _row(RESUME_SEEDS[1]), torn],
           torn_tail=True)
    fake = _FakeJob()
    _, out, recording = _resume(tmp_path, monkeypatch, fake)

    assert fake.seeds == [RESUME_SEEDS[2]], (
        "the two complete cells must be kept and only the missing one re-run")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert [r["seed"] for r in payload["records"]] == RESUME_SEEDS
    lines = recording.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    for line in lines:  # appending past a torn tail must not leave it behind
        json.loads(line)
    assert len(campaign.read_checkpoint(
        recording, families=tuple(campaign.TASKS))) == 3


def test_a_resume_keeps_one_record_for_a_cell_appended_twice(tmp_path, monkeypatch):
    _write(tmp_path / "phase_k_results.ndjson",
           [_row(RESUME_SEEDS[0]), _row(RESUME_SEEDS[1]),
            _row(RESUME_SEEDS[0])])
    fake = _FakeJob()
    result, out, _ = _resume(tmp_path, monkeypatch, fake)

    assert fake.seeds == [RESUME_SEEDS[2]]
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert [r["seed"] for r in payload["records"]] == RESUME_SEEDS
    assert payload["summaries"]["K1"]["n_seeds"] == 3, (
        "a repeated cell must not be counted twice in the summary")
    assert result["summaries"]["K1"]["n_seeds"] == 3


def test_a_k2_row_does_not_refuse_a_k1_only_resume(tmp_path, monkeypatch):
    """The reader's families are all a run can write, not this run's subset.

    A recording left by a run over every family holds rows this invocation is
    not asking for.  They are completed cells, not corruption: the K2 row must
    be kept, and the K1 seed that happens to share its number must still run.
    """
    _write(tmp_path / "phase_k_results.ndjson",
           [_row(RESUME_SEEDS[0]),
            _row(RESUME_SEEDS[0], family="K2"),
            _row(RESUME_SEEDS[1])])
    fake = _FakeJob()
    result, out, _ = _resume(tmp_path, monkeypatch, fake)

    assert fake.seeds == [RESUME_SEEDS[2]], (
        "a K2 row must not refuse the K1-only resume, and a K2 cell must not "
        "mark the K1 cell with the same seed as done")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert [(r["family"], r["seed"]) for r in payload["records"]] == [
        ("K1", RESUME_SEEDS[0]), ("K2", RESUME_SEEDS[0]),
        ("K1", RESUME_SEEDS[1]), ("K1", RESUME_SEEDS[2])]
    assert list(payload["summaries"]) == ["K1"]
    assert payload["summaries"]["K1"]["n_seeds"] == 3
    assert result["summaries"]["K1"]["n_seeds"] == 3
