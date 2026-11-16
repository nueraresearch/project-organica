"""The independent cell auditor recomputes the result and touches no seed."""
LAYER = "dry-run"  # benchmarks/test_layers.py: the auditor's non-cell paths only

import ast
import copy
import inspect
import json

from benchmarks import v2_first_cell_audit as audit
from benchmarks import v2_first_cell_readout as readout
from benchmarks import v2_first_cell_report as report
from benchmarks import v2_first_cell_runner as runner

SEEDS = list(range(20910101, 20910111))


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
    assert audit.audit(result, raw, gates, seeds) == []
    assert (result, raw, gates) == before
    assert audit.main(["--check"]) == 0


def test_a_result_assembled_by_the_runner_passes_the_audit():
    result, raw, gates, seeds = _fixture()
    assembled = runner.assemble(result["per_seed"], gates["gates"], result["control"],
                                date="2026-11-16")
    assert audit.audit(assembled, raw, gates, seeds) == []


def test_a_label_that_contradicts_the_recomputed_interval_is_refused():
    result, raw, gates, seeds = _fixture()
    result["outcome"] = "BOOKKEEPING"
    errors = audit.audit(result, raw, gates, seeds)
    assert any("outcome" in error for error in errors), errors


def test_reported_bounds_must_match_the_independent_bootstrap():
    result, raw, gates, seeds = _fixture()
    result["interval"]["hi"] += 0.001
    errors = audit.audit(result, raw, gates, seeds)
    assert any("interval hi" in error for error in errors), errors


def test_gates_are_checked_against_the_committed_record_and_void_rule():
    result, raw, gates, seeds = _fixture()
    result["gates"]["A3"]["status"] = "FAIL"
    errors = audit.audit(result, raw, gates, seeds)
    assert any("failed gate requires VOID" in error for error in errors), errors

    result, raw, gates, seeds = _fixture()
    gates["gates"]["A3"]["status"] = "FAIL"
    errors = audit.audit(result, raw, gates, seeds)
    assert any("gate A3 is PASS" in error and "committed record" in error for error in errors), errors


def test_betas_are_in_the_grid_and_match_the_raw_log():
    result, raw, gates, seeds = _fixture()
    result["per_seed"][0]["beta"]["C"] = 8
    errors = audit.audit(result, raw, gates, seeds)
    assert any("arm C beta" in error and "disagrees" in error for error in errors), errors

    result, raw, gates, seeds = _fixture()
    raw["seeds"][0]["arms"]["C"]["beta"] = 0
    errors = audit.audit(result, raw, gates, seeds)
    assert any("outside the grid" in error for error in errors), errors


def test_a_moved_bystander_or_an_unvoided_m1_failure_is_refused():
    result, raw, gates, seeds = _fixture()
    result["control"]["bystander_delta"] = 0.0001
    errors = audit.audit(result, raw, gates, seeds)
    assert any("contradicts bystander_delta" in error for error in errors), errors

    result, raw, gates, seeds = _fixture()
    result["control"]["status"] = "FAIL"
    errors = audit.audit(result, raw, gates, seeds)
    assert any("requires VOID" in error for error in errors), errors


def test_the_result_differences_must_match_the_raw_arm_losses():
    result, raw, gates, seeds = _fixture()
    raw["seeds"][0]["arms"]["C"]["log_loss"] += 0.001
    errors = audit.audit(result, raw, gates, seeds)
    assert any("raw C-A difference" in error for error in errors), errors


def test_a_missing_raw_log_is_reported_not_ignored():
    result, _, gates, seeds = _fixture()
    errors = audit.audit(result, {}, gates, seeds)
    assert any("raw log" in error for error in errors), errors


def test_a_malformed_difference_is_reported_without_crashing():
    result, raw, gates, seeds = _fixture()
    result["per_seed"][0]["d"] = None
    errors = audit.audit(result, raw, gates, seeds)
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
    assert audit.audit(result, raw, gates, seeds) == []


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
    result, raw, gates, seeds = _fixture()
    result_path = tmp_path / "result.json"
    raw_path = tmp_path / "run-log.json"
    gates_path = tmp_path / "gates.json"
    seeds_path = tmp_path / "seeds.json"
    result_path.write_text(json.dumps(result), encoding="utf-8")
    raw_path.write_text(json.dumps(raw), encoding="utf-8")
    gates_path.write_text(json.dumps(gates), encoding="utf-8")
    seeds_path.write_text(json.dumps({"seed_block": {"seeds": seeds}}), encoding="utf-8")
    before = {path: path.read_bytes() for path in (result_path, raw_path, gates_path, seeds_path)}

    assert audit.main(["--audit", str(result_path), "--raw-log", str(raw_path),
                       "--gates", str(gates_path), "--seeds", str(seeds_path)]) == 0
    assert {path: path.read_bytes() for path in before} == before
