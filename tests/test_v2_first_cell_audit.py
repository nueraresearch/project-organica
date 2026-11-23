"""The independent cell auditor recomputes the result and touches no seed."""
LAYER = "dry-run"  # benchmarks/test_layers.py: the auditor's non-cell paths only

import ast
import copy
import hashlib
import inspect
import json

from benchmarks import v2_first_cell_audit as audit
from benchmarks import v2_first_cell_readout as readout
from benchmarks import v2_first_cell_report as report
from benchmarks import v2_first_cell_runner as runner

SEEDS = list(range(20910101, 20910111))
MARKER = {"kind": "v2_first_cell_run", "status": "COMPLETED"}


def _fixture():
    differences = [round(-0.0010 - index * 0.0001, audit.DECIMALS)
                   for index in range(len(SEEDS))]
    interval = readout.paired_interval(differences)
    reported = {field: round(interval[field], audit.DECIMALS)
                for field in ("mean", "lo", "hi")}
    gates = {gate: {"status": "PASS", "evidence": "audit fixture"} for gate in audit.GATE_IDS}
    rows = [
        {
            "seed": seed,
            "measurable": True,
            "d": difference,
            "d_B": round(difference - 0.0005, audit.DECIMALS),
            "beta": {"B": 1, "C": 2},
        }
        for seed, difference in zip(SEEDS, differences)
    ]
    result = {
        "kind": "v2_first_cell_result",
        "outcome": audit.derive_label(reported["lo"], reported["hi"]),
        "scorer_pin_ok": True,
        "gates": copy.deepcopy(gates),
        "per_seed": copy.deepcopy(rows),
        "interval": dict(reported, level=audit.LEVEL, resamples=audit.RESAMPLES),
        "control": {
            "status": "PASS",
            "seed": SEEDS[0],
            "intervention": "remove_member",
            "composite_id": "c-000001",
            "removed_member": "a->b",
            "bystander_id": "c-000002",
            "metric": "resolved member count",
            "member_delta": 1.0,
            "bystander_delta": 0.0,
            "detail": "the target lost one member; the bystander did not move",
        },
        "void": None,
    }
    raw = {
        "kind": "v2_first_cell_run_log",
        "seeds": [
            {
                "seed": row["seed"],
                "measurable": True,
                "arms": {
                    "A": {"beta": None, "log_loss": 0.5},
                    "B": {"beta": 1, "log_loss": 0.5 + row["d_B"]},
                    "C": {"beta": 2, "log_loss": 0.5 + row["d"]},
                },
            }
            for row in rows
        ],
    }
    return result, raw, {"gates": gates}, list(SEEDS)


def test_the_independent_bootstrap_matches_the_protocol_readout():
    for values in (
        [-0.0010, -0.0009, -0.0008, -0.0007, -0.0006, -0.0005],
        [-0.002, 0.0, 0.001, 0.002],
        [0.0] * 10,
        [0.0001] * 9 + [-0.0001],
    ):
        expected = readout.paired_interval(values)
        got = audit.bootstrap_interval(values)
        for field in ("mean", "lo", "hi"):
            assert got[field] == expected[field], (field, got, expected)
    assert audit.BOOTSTRAP_SEED == readout.BOOTSTRAP_SEED
    assert audit.LEVEL == report.LEVEL
    assert audit.RESAMPLES == report.RESAMPLES
    assert audit.BETA_GRID == report.BETA_GRID
    assert audit.GATE_IDS == report.GATE_IDS


def test_a_valid_result_passes_and_the_check_is_read_only():
    result, raw, gates, seeds = _fixture()
    before = copy.deepcopy((result, raw, gates))
    assert audit.audit(result, raw, gates, seeds, MARKER) == []
    assert (result, raw, gates) == before
    assert audit.main(["--check"]) == 0


def test_a_result_assembled_by_the_runner_passes_the_audit():
    result, raw, gates, seeds = _fixture()
    assembled = runner.assemble(result["per_seed"], gates["gates"], result["control"],
                                date="2026-11-16")
    assert audit.audit(assembled, raw, gates, seeds, MARKER) == []


def test_a_started_marker_is_refused_before_the_result_is_audited():
    result, raw, gates, seeds = _fixture()
    result["outcome"] = "NOT A LABEL"  # this must never be reached
    errors = audit.audit(result, raw, gates, seeds, dict(MARKER, status="STARTED"))
    assert any("STARTED" in error and "COMPLETED" in error for error in errors), errors
    assert not any("outcome" in error for error in errors), errors


def test_the_file_audit_refuses_a_started_marker_before_reading_the_result(tmp_path):
    paths = _write_files(tmp_path)
    paths["marker"].write_text(
        json.dumps(dict(MARKER, status="STARTED")), encoding="utf-8"
    )
    paths["result"].write_text("{not valid json", encoding="utf-8")
    errors = audit.audit_files(
        paths["result"], paths["raw"], paths["gates"], paths["seeds"], paths["marker"]
    )
    assert any("STARTED" in error and "COMPLETED" in error for error in errors), errors
    assert not any("cannot read result" in error for error in errors), errors


def test_a_missing_marker_is_refused():
    result, raw, gates, seeds = _fixture()
    errors = audit.audit(result, raw, gates, seeds)
    assert any("run marker is missing" in error for error in errors), errors


def test_missing_artifact_files_are_refused(tmp_path):
    expected = {
        "result": "cannot read result",
        "raw": "cannot read raw log",
        "gates": "cannot read gate record",
        "seeds": "cannot read seed declaration",
        "marker": "cannot read run marker",
    }
    for missing, phrase in expected.items():
        case = tmp_path / missing
        case.mkdir()
        paths = _write_files(case)
        paths[missing].unlink()
        errors = audit.audit_files(
            paths["result"], paths["raw"], paths["gates"], paths["seeds"], paths["marker"]
        )
        assert any(phrase in error for error in errors), (missing, errors)


def _write_files(directory):
    result, raw, gates, seeds = _fixture()
    paths = {
        "result": directory / "result.json",
        "raw": directory / "run-log.json",
        "gates": directory / "gates.json",
        "seeds": directory / "seeds.json",
        "marker": directory / "run.json",
    }
    result_text = json.dumps(result)
    paths["result"].write_text(result_text, encoding="utf-8")
    paths["raw"].write_text(json.dumps(raw), encoding="utf-8")
    paths["gates"].write_text(json.dumps(gates), encoding="utf-8")
    paths["seeds"].write_text(json.dumps({"seed_block": {"seeds": seeds}}), encoding="utf-8")
    paths["marker"].write_text(
        json.dumps(dict(MARKER,
                        result_sha256=hashlib.sha256(result_text.encode("utf-8")).hexdigest())),
        encoding="utf-8",
    )
    return paths


def test_a_completed_marker_rejects_a_substituted_or_partial_result(tmp_path):
    paths = _write_files(tmp_path)
    original = paths["result"].read_bytes()

    paths["result"].write_bytes(original.replace(b'"scorer_pin_ok": true',
                                                 b'"scorer_pin_ok": false'))
    errors = audit.audit_files(
        paths["result"], paths["raw"], paths["gates"], paths["seeds"], paths["marker"]
    )
    assert any("result_sha256" in error for error in errors), errors

    paths["result"].write_bytes(original[:len(original) // 2])
    errors = audit.audit_files(
        paths["result"], paths["raw"], paths["gates"], paths["seeds"], paths["marker"]
    )
    assert any("result_sha256" in error for error in errors), errors

    paths["result"].write_bytes(original)
    paths["marker"].write_text(json.dumps(MARKER), encoding="utf-8")
    errors = audit.audit_files(
        paths["result"], paths["raw"], paths["gates"], paths["seeds"], paths["marker"]
    )
    assert any("no valid result_sha256" in error for error in errors), errors


def test_a_label_that_contradicts_the_recomputed_interval_is_refused():
    result, raw, gates, seeds = _fixture()
    result["outcome"] = "BOOKKEEPING"
    errors = audit.audit(result, raw, gates, seeds, MARKER)
    assert any("outcome" in error for error in errors), errors


def test_reported_bounds_must_match_the_independent_bootstrap():
    result, raw, gates, seeds = _fixture()
    result["interval"]["hi"] += 0.001
    errors = audit.audit(result, raw, gates, seeds, MARKER)
    assert any("interval hi" in error for error in errors), errors


def test_gates_are_checked_against_the_committed_record_and_void_rule():
    result, raw, gates, seeds = _fixture()
    result["gates"]["A3"]["status"] = "FAIL"
    errors = audit.audit(result, raw, gates, seeds, MARKER)
    assert any("failed gate requires VOID" in error for error in errors), errors

    result, raw, gates, seeds = _fixture()
    gates["gates"]["A3"]["status"] = "FAIL"
    errors = audit.audit(result, raw, gates, seeds, MARKER)
    assert any("gate A3 is PASS" in error and "committed record" in error for error in errors), errors


def test_betas_are_in_the_grid_and_match_the_raw_log():
    result, raw, gates, seeds = _fixture()
    result["per_seed"][0]["beta"]["C"] = 8
    errors = audit.audit(result, raw, gates, seeds, MARKER)
    assert any("arm C beta" in error and "disagrees" in error for error in errors), errors

    result, raw, gates, seeds = _fixture()
    raw["seeds"][0]["arms"]["C"]["beta"] = 0
    errors = audit.audit(result, raw, gates, seeds, MARKER)
    assert any("outside the grid" in error for error in errors), errors


def test_a_moved_bystander_or_an_unvoided_m1_failure_is_refused():
    result, raw, gates, seeds = _fixture()
    result["control"]["bystander_delta"] = 0.0001
    errors = audit.audit(result, raw, gates, seeds, MARKER)
    assert any("contradicts bystander_delta" in error for error in errors), errors

    result, raw, gates, seeds = _fixture()
    result["control"]["status"] = "FAIL"
    errors = audit.audit(result, raw, gates, seeds, MARKER)
    assert any("requires VOID" in error for error in errors), errors


def test_the_result_differences_must_match_the_raw_arm_losses():
    result, raw, gates, seeds = _fixture()
    raw["seeds"][0]["arms"]["C"]["log_loss"] += 0.001
    errors = audit.audit(result, raw, gates, seeds, MARKER)
    assert any("raw C-A difference" in error for error in errors), errors


def test_a_missing_raw_log_is_reported_not_ignored():
    result, _, gates, seeds = _fixture()
    errors = audit.audit(result, {}, gates, seeds, MARKER)
    assert any("raw log" in error for error in errors), errors


def test_a_malformed_difference_is_reported_without_crashing():
    result, raw, gates, seeds = _fixture()
    result["per_seed"][0]["d"] = None
    errors = audit.audit(result, raw, gates, seeds, MARKER)
    assert any("finite d" in error for error in errors), errors


def test_a_gate_void_with_a_runtime_a1_failure_is_accepted():
    result, raw, gates, seeds = _fixture()
    result["gates"]["A1"]["status"] = "FAIL"
    result["outcome"] = "VOID"
    result["interval"] = None
    result["void"] = {
        "codes": ["A1_CANONICALISATION", "SEEDS_MEASURABLE"],
        "detail": "the A1 cell-stream check failed before the arms",
    }
    result["per_seed"] = [
        {"seed": seed, "measurable": False, "exclusion": "not run: A1 failed"}
        for seed in seeds
    ]
    result["control"] = {
        "status": "NOT RUN",
        "seed": seeds[0],
        "intervention": "remove_member",
        "composite_id": "c-000001",
        "removed_member": "a->b",
        "bystander_id": "c-000002",
        "metric": "resolved member count",
        "detail": "A1 failed before the control arm",
    }
    raw["seeds"] = [
        {"seed": seed, "measurable": False, "exclusion": "not run: A1 failed"}
        for seed in seeds
    ]
    assert audit.audit(result, raw, gates, seeds, MARKER) == []


def test_the_auditor_imports_no_runner_readout_or_engine_module():
    tree = ast.parse(inspect.getsource(audit))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert "benchmarks.v2_first_cell_runner" not in imported
    assert "benchmarks.v2_first_cell_readout" not in imported
    assert "organica" not in imported
    assert not any(name.startswith("organica.") for name in imported)


def test_the_cli_audits_files_without_writing_them(tmp_path):
    paths = _write_files(tmp_path)
    before = {path: path.read_bytes() for path in paths.values()}

    assert audit.main(["--audit", str(paths["result"]), "--raw-log", str(paths["raw"]),
                       "--gates", str(paths["gates"]), "--seeds", str(paths["seeds"]),
                       "--marker", str(paths["marker"])]) == 0
    assert {path: path.read_bytes() for path in before} == before
