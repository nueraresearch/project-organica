"""The K2 one-block runner: grant refusal, one lease, one marker, resume.

The block has not run.  These are dry-run checks: the campaign is replaced by a
fake that writes synthetic per-seed records to the checkpoint, so no database is
opened and no sleep cycle is executed.  The fake exercises the runner's own
paths -- grant, lease, marker, assembly, validation and resume -- which is the
part the build was missing.
"""
from __future__ import annotations

LAYER = "dry-run"  # benchmarks/test_layers.py: no cell is executed

import hashlib
import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from benchmarks import k2_block as block
from benchmarks import k2_gate as gate
from benchmarks import phase_k_campaign as campaign
from benchmarks.k2_pre_switch_retention import ASSOCIATION_TYPES, empty_evidence


# ==================================================================
# Synthetic campaign output
# ==================================================================

def _manipulation(demoted: int, before: float, after: float) -> dict:
    evidence = empty_evidence(200 if demoted else None)
    evidence.update({
        "association_types": list(ASSOCIATION_TYPES),
        "cycles_observed": 300,
        "pre_boundary_key_count": 4,
        "post_boundary_target_count": demoted,
        "demoted_count": demoted,
        "priority_before_sum": before,
        "priority_after_sum": after,
        "mean_priority_delta": (round((after - before) / demoted, 6)
                                if demoted else None),
        "min_priority_delta": round(after - before, 6) if demoted else None,
        "max_priority_delta": round(after - before, 6) if demoted else None,
        "target_type_counts": {
            "loop_candidate": demoted,
            "prediction_candidate": 0,
            "hypothesis": 0,
        },
        "sample_keys": ["loop:alpha"] if demoted else [],
    })
    return evidence


def _records() -> list[dict]:
    """Twenty gate-shaped campaign records: ten K2 and ten K1."""
    rows: list[dict] = []
    for seed in gate.K2_SEEDS:
        rows.append({
            "family": "K2",
            "seed": seed,
            "organica": 0.60,
            "ablation": 0.41,
            "best_simple_baseline": {"model": "temporal_graph",
                                     "primary": 0.97},
            "all_models": [{"model": "organica"},
                           {"model": "organica_NO_FALSIFICATION"}],
            "manipulation": _manipulation(2, 1.0, 0.5),
            "protocol": {"switch_cycle": 200},
        })
    for seed in gate.K2_SEEDS:
        rows.append({
            "family": "K1",
            "seed": seed,
            "organica": 0.60,
            "ablation": 0.55,
            "best_simple_baseline": {"model": "cooccurrence",
                                     "primary": 0.94},
            "all_models": [{"model": "organica"},
                           {"model": "organica_NO_QUESTIONS"}],
            "manipulation": _manipulation(0, 0.0, 0.0),
            "protocol": {"late_entity_cycle": 150},
        })
    return rows


class _Campaign:
    """A stand-in for ``phase_k_campaign.run_campaign``; it runs no cell."""

    def __init__(self, records=None, *, write: int | None = None,
                 fail: bool = False):
        self.records = _records() if records is None else records
        self.write = len(self.records) if write is None else write
        self.fail = fail
        self.calls: list[dict] = []

    def __call__(self, **kwargs) -> dict:
        self.calls.append(kwargs)
        path = Path(kwargs["checkpoint_path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as handle:
            for row in self.records[:self.write]:
                handle.write(json.dumps(row) + "\n")
        if self.fail:
            raise RuntimeError("simulated interruption")
        return {"records": self.write}


# ==================================================================
# Paths and the grant
# ==================================================================

def _grant(tmp_path: Path, **overrides) -> Path:
    body = {
        "kind": block.GRANT_KIND,
        "grant_id": "K2-BLOCK-TEST",
        "granted_on": date.today().isoformat(),
        "granted_by": "owner",
        "authorizes": block.GRANT_AUTHORIZES,
        "block": {
            "families": ["K1", "K2"],
            "seeds": list(gate.K2_SEEDS),
            "cycles": gate.K2_CYCLES,
            "scale": 1,
            "workers": 1,
        },
    }
    body.update(overrides)
    path = tmp_path / "K2-BLOCK-GRANT.json"
    path.write_text(json.dumps(body), encoding="utf-8")
    return path


def _run(tmp_path: Path, **overrides) -> dict:
    out = tmp_path / "phase_k_k2_results.json"
    grant = tmp_path / "K2-BLOCK-GRANT.json"
    if not grant.exists():
        # A test that forges a grant keeps it; this only supplies the default.
        grant = _grant(tmp_path)
    kwargs = {
        "grant_path": grant,
        "out_path": out,
        "checkpoint_path": tmp_path / "phase_k_k2_results.ndjson",
        "lease_path": tmp_path / "phase_k_k2_block_lease.json",
        "marker_path": tmp_path / "phase_k_k2_attempt.json",
        "env": {"PYTHONHASHSEED": "0"},
        "allowed_outputs": [out],
    }
    kwargs.update(overrides)
    return kwargs


def _lease(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "phase_k_k2_block_lease.json").read_text(
        encoding="utf-8"))


def _marker(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "phase_k_k2_attempt.json").read_text(
        encoding="utf-8"))


def _nothing_written(tmp_path: Path) -> bool:
    return not any((tmp_path / name).exists() for name in (
        "phase_k_k2_results.json",
        "phase_k_k2_results.ndjson",
        "phase_k_k2_block_lease.json",
        "phase_k_k2_attempt.json",
    ))


def test_a_missing_grant_refuses_before_anything_is_written(tmp_path):
    campaign = _Campaign()
    receipt = block.run_block(**_run(
        tmp_path, grant_path=tmp_path / "no-such-grant.json",
        campaign_runner=campaign))

    assert receipt["state"] == "REFUSED"
    assert receipt["stage"] == "grant"
    assert receipt["refusal_code"] == "GRANT_MISSING"
    assert receipt["exit_code"] == 2
    assert receipt["result_written"] is False
    assert receipt["cells_started"] == 0
    assert receipt["lease"]["state"] == "NOT_ACQUIRED"
    assert receipt["attempt"]["state"] == "NOT_WRITTEN"
    assert _nothing_written(tmp_path)
    assert campaign.calls == []


def test_an_undated_or_future_grant_is_refused(tmp_path):
    out = tmp_path / "phase_k_k2_results.json"

    undated = _grant(tmp_path)
    body = json.loads(undated.read_text(encoding="utf-8"))
    del body["granted_on"]
    undated.write_text(json.dumps(body), encoding="utf-8")
    receipt = block.run_block(**_run(tmp_path))
    assert receipt["refusal_code"] == "GRANT_UNDATED"
    assert _nothing_written(tmp_path)

    _grant(tmp_path, granted_on="17-11-2026")
    assert block.run_block(**_run(tmp_path))["refusal_code"] == "GRANT_UNDATED"

    future = (date.today() + timedelta(days=1)).isoformat()
    _grant(tmp_path, granted_on=future)
    assert (block.run_block(**_run(tmp_path))["refusal_code"]
            == "GRANT_NOT_YET_VALID")
    assert not out.exists()


def test_a_grant_for_another_block_is_refused(tmp_path):
    _grant(tmp_path, kind="k1_block_grant")
    assert (block.run_block(**_run(tmp_path))["refusal_code"]
            == "GRANT_BLOCK_MISMATCH")

    _grant(tmp_path)
    body = json.loads((tmp_path / "K2-BLOCK-GRANT.json").read_text(
        encoding="utf-8"))
    body["block"]["seeds"] = list(gate.K2_SEEDS[:-1])
    (tmp_path / "K2-BLOCK-GRANT.json").write_text(
        json.dumps(body), encoding="utf-8")
    receipt = block.run_block(**_run(tmp_path))
    assert receipt["refusal_code"] == "GRANT_BLOCK_MISMATCH"
    assert receipt["checks"]["observed_block"]["seeds"] == list(
        gate.K2_SEEDS[:-1])
    assert _nothing_written(tmp_path)


# ==================================================================
# The gate still refuses before the lease
# ==================================================================

def test_a_gate_refusal_acquires_no_lease_and_writes_no_marker(tmp_path, monkeypatch):
    campaign = _Campaign()
    forged = dict(block.k1_noop_evidence())
    forged["noop_hash"] = "not-the-shipped-fixture"
    monkeypatch.setattr(block, "k1_noop_evidence", lambda: forged)

    receipt = block.run_block(**_run(tmp_path, campaign_runner=campaign))

    assert receipt["state"] == "REFUSED"
    assert receipt["refusal_code"] == "K1_NOOP_FIXTURE_MISMATCH"
    assert receipt["lease"]["state"] == "NOT_ACQUIRED"
    assert receipt["attempt"]["state"] == "NOT_WRITTEN"
    assert _nothing_written(tmp_path)
    assert campaign.calls == []


def test_a_leaking_noop_fixture_refuses_before_the_lease(tmp_path, monkeypatch):
    leaking = dict(block.k1_noop_evidence())
    leaking["noop_manipulation"] = dict(
        leaking["noop_manipulation"], demoted_count=1)
    monkeypatch.setattr(block, "k1_noop_evidence", lambda: leaking)

    campaign = _Campaign()
    receipt = block.run_block(**_run(tmp_path, campaign_runner=campaign))

    assert receipt["state"] == "REFUSED"
    assert receipt["refusal_code"] == "K1_NOOP_MANIPULATION_MISMATCH"
    assert "demoted_count" in receipt["checks"]["differing_fields"]
    assert receipt["lease"]["state"] == "NOT_ACQUIRED"
    assert _nothing_written(tmp_path)
    assert campaign.calls == []


# ==================================================================
# The fresh block
# ==================================================================

def test_the_block_acquires_one_lease_one_marker_and_a_validated_result(tmp_path):
    campaign = _Campaign()
    receipt = block.run_block(**_run(tmp_path, campaign_runner=campaign))

    assert receipt["state"] == "VALIDATED", receipt
    assert receipt["gate"]["verdict"] == "PASS", receipt["gate"]
    assert receipt["gate"]["criteria_read"] is True
    assert receipt["exit_code"] == 0

    assert len(campaign.calls) == 1
    call = campaign.calls[0]
    assert call["families"] == ["K1", "K2"]
    assert call["seeds"] == list(gate.K2_SEEDS)
    assert call["scale"] == 1
    assert call["resume"] is False
    assert set(call["primary_factories"]) == {"K1", "K2"}
    assert call["primary_factories"]["K2"].keywords["boundary_cycle"] == (
        gate.K2_BOUNDARY_CYCLE)
    assert call["primary_factories"]["K1"].keywords["boundary_cycle"] is None

    lease = _lease(tmp_path)
    assert lease["state"] == "CLOSED"
    assert lease["outcome"] == "PASS"
    assert lease["cells_completed"] == 20
    assert lease["per_seed_leases"] == 0
    assert lease["attempt_id"] == receipt["attempt_id"]

    marker = _marker(tmp_path)
    assert marker["state"] == "COMPLETE"
    assert marker["attempt_id"] == receipt["attempt_id"]
    assert marker["gate_verdict"] == "PASS"

    assert sorted(p.name for p in tmp_path.glob("*k2*lease*.json")) == [
        "phase_k_k2_block_lease.json"]
    assert sorted(p.name for p in tmp_path.glob("*k2*attempt*.json")) == [
        "phase_k_k2_attempt.json"]

    result = json.loads((tmp_path / "phase_k_k2_results.json").read_text(
        encoding="utf-8"))
    assert len(result["records"]) == 20
    assert result["engine_tree_sha256"] == gate.expected_engine_tree()
    assert result["gate"]["verdict"] == "PASS"
    assert result["arm"]["class_hash"] == gate.class_hash(
        __import__("benchmarks.k2_pre_switch_retention", fromlist=["x"])
        .K2PreSwitchRetentionService)
    assert result["engine_version"] and result["engine_commit"]
    assert result["runner"] == "benchmarks.k2_block"
    assert "verdict" not in result


def test_a_second_attempt_is_refused_and_cannot_overwrite_the_result(tmp_path):
    block.run_block(**_run(tmp_path, campaign_runner=_Campaign()))
    out = tmp_path / "phase_k_k2_results.json"
    before = hashlib.sha256(out.read_bytes()).hexdigest()

    campaign = _Campaign()
    receipt = block.run_block(**_run(tmp_path, campaign_runner=campaign))

    assert receipt["state"] == "REFUSED"
    assert receipt["refusal_code"] == "OUTPUT_EXISTS"
    assert receipt["checks"]["output_before_sha256"] == before
    assert receipt["checks"]["output_after_sha256"] == before
    assert campaign.calls == []
    assert hashlib.sha256(out.read_bytes()).hexdigest() == before


# ==================================================================
# Resume
# ==================================================================

def test_resume_after_an_interrupt_reuses_the_same_lease_and_marker(tmp_path):
    interrupted = _Campaign(write=10, fail=True)
    with pytest.raises(RuntimeError):
        block.run_block(**_run(tmp_path, campaign_runner=interrupted))

    assert not (tmp_path / "phase_k_k2_results.json").exists()
    first_lease = _lease(tmp_path)
    assert first_lease["state"] == "INTERRUPTED"
    assert first_lease["cells_completed"] == 10
    assert first_lease["resume_count"] == 0
    assert _marker(tmp_path)["state"] == "INTERRUPTED"

    resumed = _Campaign()
    receipt = block.run_block(**_run(
        tmp_path, campaign_runner=resumed, resume=True))

    assert receipt["state"] == "VALIDATED", receipt
    assert receipt["gate"]["verdict"] == "PASS"
    assert resumed.calls[0]["resume"] is True
    assert len(resumed.calls) == 1

    lease = _lease(tmp_path)
    assert lease["state"] == "CLOSED"
    assert lease["resume_count"] == 1
    assert lease["acquired_at"] == first_lease["acquired_at"]
    assert lease["attempt_id"] == receipt["attempt_id"]

    marker = _marker(tmp_path)
    assert marker["state"] == "COMPLETE"
    assert marker["resume_count"] == 1
    assert marker["attempt_id"] == receipt["attempt_id"]

    assert sorted(p.name for p in tmp_path.glob("*k2*lease*.json")) == [
        "phase_k_k2_block_lease.json"]
    assert sorted(p.name for p in tmp_path.glob("*k2*attempt*.json")) == [
        "phase_k_k2_attempt.json"]

    result = json.loads((tmp_path / "phase_k_k2_results.json").read_text(
        encoding="utf-8"))
    assert len(result["records"]) == 20
    assert result["gate"]["verdict"] == "PASS"


def test_resume_refuses_a_foreign_attempt_and_leaves_it_alone(tmp_path):
    out = tmp_path / "phase_k_k2_results.json"
    foreign = {
        "attempt_id": "k2-block-foreign",
        "arm_signature": block.arm_signature(),
        "protocol": {"seeds": list(gate.K2_SEEDS)},
    }
    out.write_text(json.dumps(foreign), encoding="utf-8")
    before = out.read_bytes()

    campaign = _Campaign()
    receipt = block.run_block(**_run(
        tmp_path, campaign_runner=campaign, resume=True))

    assert receipt["state"] == "REFUSED"
    assert receipt["refusal_code"] == "RESUME_ARM_MISMATCH"
    assert "attempt_id" in receipt["checks"]["mismatched_fields"]
    assert campaign.calls == []
    assert out.read_bytes() == before
    assert not (tmp_path / "phase_k_k2_block_lease.json").exists()
    assert not (tmp_path / "phase_k_k2_attempt.json").exists()


def test_an_active_lease_needs_reclaim_and_the_matching_attempt(tmp_path):
    grant = block.load_grant(_grant(tmp_path))
    attempt_id = block.attempt_id_for(grant)
    lease_path = tmp_path / "phase_k_k2_block_lease.json"
    lease_path.write_text(json.dumps({
        "state": "ACTIVE", "attempt_id": attempt_id, "pid": 999999,
        "acquired_at": "2026-11-17",
    }), encoding="utf-8")

    assert (block.run_block(**_run(tmp_path))["refusal_code"]
            == "K2_BLOCK_LEASE_HELD")

    receipt = block.run_block(**_run(
        tmp_path, resume=True, reclaim=True, campaign_runner=_Campaign(),
        pid_alive=lambda pid: True))
    assert receipt["refusal_code"] == "K2_LEASE_NOT_RECLAIMABLE"
    assert lease_path.exists()

    lease_path.write_text(json.dumps({
        "state": "ACTIVE", "attempt_id": "k2-block-foreign", "pid": 999999,
        "acquired_at": "2026-11-17",
    }), encoding="utf-8")
    assert (block.run_block(**_run(tmp_path, resume=True, reclaim=True,
                                   pid_alive=lambda pid: False))["refusal_code"]
            == "K2_LEASE_NOT_RECLAIMABLE")

    lease_path.write_text(json.dumps({
        "state": "ACTIVE", "attempt_id": attempt_id, "pid": 999999,
        "acquired_at": "2026-11-17",
    }), encoding="utf-8")
    receipt = block.run_block(**_run(
        tmp_path, resume=True, reclaim=True, campaign_runner=_Campaign(),
        pid_alive=lambda pid: False))
    assert receipt["state"] == "VALIDATED", receipt
    assert receipt["gate"]["verdict"] == "PASS"
    lease = _lease(tmp_path)
    assert lease["state"] == "CLOSED"
    assert lease["reclaimed_from_pid"] == 999999
    assert lease["attempt_id"] == attempt_id


# ==================================================================
# The checkpoint reader: resume and result assembly both read this file
# ==================================================================

def _checkpoint_row(family: str = "K2", seed: int | None = None,
                    **overrides) -> dict:
    row = {
        "family": family,
        "seed": gate.K2_SEEDS[0] if seed is None else seed,
        "organica": 0.60,
        "ablation": 0.41,
        "best_simple_baseline": {"model": "temporal_graph", "primary": 0.97},
        "all_models": [{"model": "organica"}],
        "manipulation": None,
        "protocol": {"switch_cycle": 200},
    }
    row.update(overrides)
    return row


def _write_checkpoint(path: Path, lines: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    return path


def _checkpoint_lines() -> list[str]:
    return [json.dumps(_checkpoint_row(family, seed))
            for family in gate.EXPECTED_FAMILIES for seed in gate.K2_SEEDS]


def test_the_checkpoint_reader_refuses_a_non_cell_row_before_the_last(tmp_path):
    path = tmp_path / "phase_k_k2_results.ndjson"
    first = json.dumps(_checkpoint_row("K2", gate.K2_SEEDS[0]))
    second = json.dumps(_checkpoint_row("K2", gate.K2_SEEDS[1]))

    for corrupt, reason in (
        ("{not json", "unreadable"),
        ('["a list"]', "not_a_cell_row"),
        (json.dumps(_checkpoint_row("K3", gate.K2_SEEDS[0])),
         "not_a_cell_row"),
        (json.dumps(_checkpoint_row("K2", True)), "not_a_cell_row"),
    ):
        _write_checkpoint(path, [first, corrupt, second])
        with pytest.raises(block.CheckpointError) as caught:
            block.read_checkpoint(path)
        assert caught.value.code == "CHECKPOINT_CORRUPT"
        assert caught.value.evidence["line"] == 2
        assert caught.value.evidence["reason"] == reason
        assert caught.value.evidence["rows_read"] == 1

    # A blank line is not a row, and a missing file is an empty recording.
    _write_checkpoint(path, [first, "", second])
    assert len(block.read_checkpoint(path)) == 2
    assert block.read_checkpoint(tmp_path / "absent.ndjson") == []


def test_the_checkpoint_reader_tolerates_and_repairs_a_partial_final_row(tmp_path):
    path = tmp_path / "phase_k_k2_results.ndjson"
    complete = _checkpoint_lines()[:3]
    partial = json.dumps(_checkpoint_row("K2", gate.K2_SEEDS[3]))[:40]
    _write_checkpoint(path, complete + [partial])

    report = block.read_checkpoint_report(path)
    assert len(report["records"]) == 3
    assert report["cells"] == 3
    assert report["partial_final_row"] is True
    assert report["partial_final_line"] == 4
    assert len(block.read_checkpoint(path)) == 3

    repaired = block.repair_partial_final_row(path)
    assert repaired["repaired_partial_row"] is True
    assert repaired["partial_final_row"] is False
    assert len(repaired["records"]) == 3
    assert path.read_text(encoding="utf-8").splitlines() == complete

    # A complete final row without a trailing newline parses, so it is a row.
    path.write_text("\n".join(complete), encoding="utf-8")
    report = block.read_checkpoint_report(path)
    assert len(report["records"]) == 3
    assert report["partial_final_row"] is False


def test_the_checkpoint_reader_keeps_one_row_per_cell_and_agrees_on_repeats(tmp_path):
    path = tmp_path / "phase_k_k2_results.ndjson"
    first = _checkpoint_row("K2", gate.K2_SEEDS[0])
    other = _checkpoint_row("K2", gate.K2_SEEDS[1])

    _write_checkpoint(path, [json.dumps(row)
                             for row in (first, other, first)])
    report = block.read_checkpoint_report(path)
    assert [row["seed"] for row in report["records"]] == [
        gate.K2_SEEDS[0], gate.K2_SEEDS[1]]
    assert report["cells"] == 2
    assert report["rows"] == 3
    assert report["duplicate_rows"] == 1
    assert report["duplicate_cells"] == 1

    # The same seed under the same arm is deterministic, so two rows for one
    # cell that disagree are two measurements of one cell, not a later answer.
    changed = dict(first, organica=0.61)
    _write_checkpoint(path, [json.dumps(first), json.dumps(changed)])
    with pytest.raises(block.CheckpointError) as caught:
        block.read_checkpoint(path)
    assert caught.value.code == "CHECKPOINT_DUPLICATE_DISAGREES"
    assert caught.value.evidence["family"] == "K2"
    assert caught.value.evidence["seed"] == gate.K2_SEEDS[0]
    assert caught.value.evidence["differing_fields"] == ["organica"]
    assert caught.value.evidence["first_line"] == 1
    assert caught.value.evidence["second_line"] == 2


def test_a_corrupt_checkpoint_refuses_before_the_lease(tmp_path):
    checkpoint_path = _write_checkpoint(
        tmp_path / "phase_k_k2_results.ndjson",
        [json.dumps(_checkpoint_row("K2", gate.K2_SEEDS[0])),
         "{not json",
         json.dumps(_checkpoint_row("K2", gate.K2_SEEDS[1]))])

    campaign = _Campaign()
    receipt = block.run_block(**_run(
        tmp_path, campaign_runner=campaign, resume=True))

    assert receipt["state"] == "REFUSED"
    assert receipt["stage"] == "checkpoint"
    assert receipt["refusal_code"] == "CHECKPOINT_CORRUPT"
    assert receipt["exit_code"] == 2
    assert receipt["checks"]["line"] == 2
    assert receipt["lease"]["state"] == "NOT_ACQUIRED"
    assert receipt["attempt"]["state"] == "NOT_WRITTEN"
    assert campaign.calls == []
    assert checkpoint_path.exists()
    assert not (tmp_path / "phase_k_k2_block_lease.json").exists()
    assert not (tmp_path / "phase_k_k2_attempt.json").exists()
    assert not (tmp_path / "phase_k_k2_results.json").exists()


def test_resume_repairs_a_partially_written_row_before_appending(tmp_path):
    interrupted = _Campaign(write=10, fail=True)
    with pytest.raises(RuntimeError):
        block.run_block(**_run(tmp_path, campaign_runner=interrupted))

    checkpoint_path = tmp_path / "phase_k_k2_results.ndjson"
    with open(checkpoint_path, "a", encoding="utf-8") as handle:
        handle.write('{"family": "K2", "seed": 202610')
    assert block.read_checkpoint_report(
        checkpoint_path)["partial_final_row"] is True

    receipt = block.run_block(**_run(
        tmp_path, campaign_runner=_Campaign(), resume=True))

    assert receipt["state"] == "VALIDATED", receipt
    assert receipt["gate"]["verdict"] == "PASS"
    assert receipt["checkpoint"]["partial_final_row"] is False
    assert receipt["checkpoint"]["cells"] == 20
    assert receipt["checkpoint"]["duplicate_cells"] == 10
    assert len(block.read_checkpoint(checkpoint_path)) == 20


# --- the two readers of one file must not disagree --------------------------

PARITY_SEEDS = [20910201, 20910202, 20910203]


def _parity_row(seed: int, **overrides) -> str:
    return json.dumps(_checkpoint_row("K2", seed, **overrides))


def _parity_write(path: Path, lines: list[str], *,
                  torn_tail: bool = False) -> Path:
    """Write one line per element; a torn tail is written without its newline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + ("" if torn_tail else "\n"),
                    encoding="utf-8")
    return path


@pytest.mark.parametrize("case, code", [
    ("unreadable", "CHECKPOINT_CORRUPT"),
    ("not_a_cell", "CHECKPOINT_CORRUPT"),
    ("foreign_family", "CHECKPOINT_CORRUPT"),
    ("disagreeing", "CHECKPOINT_DUPLICATE_DISAGREES"),
])
def test_both_readers_refuse_the_same_corruption(tmp_path, case, code):
    middle = {
        "unreadable": "{not json",
        "not_a_cell": json.dumps({"family": "K2", "seed": True}),
        "foreign_family": json.dumps(_checkpoint_row("K9", PARITY_SEEDS[2])),
        "disagreeing": _parity_row(PARITY_SEEDS[0], organica=0.61),
    }[case]
    path = _parity_write(tmp_path / f"{case}.ndjson",
                         [_parity_row(PARITY_SEEDS[0]), middle,
                          _parity_row(PARITY_SEEDS[1])])

    with pytest.raises(block.CheckpointError) as block_caught:
        block.read_checkpoint(path)
    with pytest.raises(campaign.CheckpointError) as campaign_caught:
        campaign.read_checkpoint(path, families=tuple(campaign.TASKS))
    assert block_caught.value.code == campaign_caught.value.code == code


def test_both_readers_tolerate_only_the_two_writer_states(tmp_path):
    torn = _parity_row(PARITY_SEEDS[2])[:60]
    path = _parity_write(tmp_path / "torn.ndjson",
                         [_parity_row(PARITY_SEEDS[0]),
                          _parity_row(PARITY_SEEDS[1]), torn], torn_tail=True)
    block_report = block.read_checkpoint_report(path)
    campaign_report = campaign.read_checkpoint_report(
        path, families=tuple(campaign.TASKS))
    assert block_report["partial_final_row"] is True
    assert campaign_report["partial_final_row"] is True
    assert block_report["cells"] == campaign_report["cells"] == 2

    path = _parity_write(tmp_path / "repeat.ndjson",
                         [_parity_row(PARITY_SEEDS[0]),
                          _parity_row(PARITY_SEEDS[1]),
                          _parity_row(PARITY_SEEDS[0])])
    block_report = block.read_checkpoint_report(path)
    campaign_report = campaign.read_checkpoint_report(
        path, families=tuple(campaign.TASKS))
    assert block_report["cells"] == campaign_report["cells"] == 2
    assert block_report["duplicate_cells"] == campaign_report["duplicate_cells"] == 1
    assert block_report["records"] == campaign_report["records"]


def test_a_complete_final_row_that_is_not_a_cell_is_corruption(tmp_path):
    """A torn write is a line that does not parse; a parseable bad row is not."""
    path = _parity_write(tmp_path / "final.ndjson",
                         [_parity_row(PARITY_SEEDS[0]),
                          json.dumps({"family": "K2", "seed": True})])
    for reader in (block.read_checkpoint, campaign.read_checkpoint):
        with pytest.raises(campaign.CheckpointError) as caught:
            reader(path)
        assert caught.value.code == "CHECKPOINT_CORRUPT"


# ==================================================================
# The single lease and the K1 no-op fixture
# ==================================================================

def test_lease_acquisition_is_exclusive(tmp_path):
    grant = block.load_grant(_grant(tmp_path))
    path = tmp_path / "phase_k_k2_block_lease.json"
    first = block.acquire_lease(
        path, attempt_id="k2-block-one", grant=grant)

    assert first["state"] == "ACTIVE"
    assert first["per_seed_leases"] == 0
    with pytest.raises(block.GrantRefusal) as caught:
        block.acquire_lease(path, attempt_id="k2-block-two", grant=grant)
    assert caught.value.code == "K2_BLOCK_LEASE_HELD"
    assert len(list(tmp_path.glob("*lease*.json"))) == 1


def test_the_k1_noop_fixture_compares_the_shipped_path(tmp_path):
    evidence = block.k1_noop_evidence()
    assert evidence["fixture_id"] == block.FIXTURE_ID
    assert evidence["fixture_sha256"] == evidence["shipped_fixture_sha256"]
    assert evidence["fixture_sha256"] == evidence["noop_fixture_sha256"]
    assert evidence["shipped_arguments_sha256"] == evidence["noop_arguments_sha256"]
    assert evidence["shipped_hash"] == evidence["noop_hash"]
    assert gate.k1_fixture_selection_detail(evidence) == []
    assert evidence["forwarded_identical"] is True
    assert evidence["shipped_manipulation"] is None
    assert evidence["noop_manipulation"] == empty_evidence(None)
    assert evidence["counterfactual_demoted_count"] > 0
    assert evidence["demoted_count"] == 0
    assert evidence["pre_boundary_demotions"] == 0
    assert evidence["priority_before_sum"] == evidence["priority_after_sum"] == 0.0
    assert evidence["boundary_cycle"] is None

    report = gate.preflight(**{
        "families": list(gate.EXPECTED_FAMILIES),
        "seeds": list(gate.K2_SEEDS),
        "out_path": tmp_path / "phase_k_k2_results.json",
        "checkpoint_path": tmp_path / "phase_k_k2_results.ndjson",
        "lease_path": tmp_path / "phase_k_k2_block_lease.json",
        "marker_path": tmp_path / "phase_k_k2_attempt.json",
        "primary_factory": block.primary_factory(),
        "k1_factory": block.k1_factory(),
        "env": {"PYTHONHASHSEED": "0"},
        "engine_tree_sha256": gate.expected_engine_tree(),
        "bootstrap_seed": gate.stable_bootstrap_seed(),
        "allowed_outputs": [tmp_path / "phase_k_k2_results.json"],
        "k1_noop_evidence": evidence,
    })
    assert report["state"] == "PREFLIGHT_OK"
    assert report["arms"]["k1_boundary_cycle"] is None


def test_the_cli_refuses_without_a_grant_and_writes_nothing(tmp_path, capsys):
    out = tmp_path / "phase_k_k2_results.json"
    code = block.main([
        "--grant", str(tmp_path / "missing-grant.json"),
        "--out", str(out),
        "--checkpoint", str(tmp_path / "phase_k_k2_results.ndjson"),
        "--lease", str(tmp_path / "phase_k_k2_block_lease.json"),
        "--marker", str(tmp_path / "phase_k_k2_attempt.json"),
    ])
    assert code == 2
    assert _nothing_written(tmp_path)
    assert "GRANT_MISSING" in capsys.readouterr().out
