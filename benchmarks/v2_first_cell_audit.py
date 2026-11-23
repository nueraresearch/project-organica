"""Read-only audit of a completed first V2 cell result.

This module deliberately does not import the runner, the readout adapter or the
engine.  It first requires the run marker to be `COMPLETED`, then reads the
result, the raw per-seed log, the committed gate record and the declared seed
list, and recomputes the 99% percentile bootstrap from the result's per-seed
differences.  A `STARTED` marker, a missing marker or any other non-completed
status is refused before the result is audited: a partial result left by a VOID
attempt is not a result.  No world is replayed and no event is scored.

    python -m benchmarks.v2_first_cell_audit --audit [RESULT.json] [--marker RUN.json]
    python -m benchmarks.v2_first_cell_audit --check

The recomputation uses the protocol's fixed bootstrap PRNG seed (20261116), the
same resample count (10,000) and the same percentile-index rule as the readout.
The result is allowed to differ from the raw recomputation only by its declared
six-decimal rounding.  The auditor also requires the label to agree with both
the reported bounds and the recomputed bounds, so a boundary crossing cannot be
hidden by rounding.

`--check` runs synthetic fixtures only.  Neither mode writes a file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RESULT = REPO / "docs" / "v2_first_cell_result.json"
RAW_LOG = REPO / "docs" / "v2_first_cell_run_log.json"
GATES = REPO / "docs" / "v2_first_cell_gates.json"
SEEDS = REPO / "docs" / "v2_first_cell_seeds.json"
RUN = REPO / "docs" / "v2_first_cell_run.json"

BOOTSTRAP_SEED = 20261116
LEVEL = 0.99
RESAMPLES = 10_000
DECIMALS = 6
ROUNDING = 0.5 * 10 ** -DECIMALS
ROUNDING_EPSILON = ROUNDING + 1e-9
BETA_GRID = (1, 2, 4, 8)
ARMS = ("A", "B", "C")
GATE_IDS = ("A1", "A2", "A3", "A4", "A5")
GATE_CODES = {
    "A1": "A1_CANONICALISATION",
    "A2": "A2_IDENTIFIER",
    "A3": "A3_MUTATION",
    "A4": "A4_COST",
    "A5": "A5_DETERMINISM",
}
VOID_CODES = tuple(GATE_CODES.values()) + (
    "SEEDS_MEASURABLE",
    "PARTS_INCOMPLETE",
    "SCORER_PIN",
    "GATES_NOT_RUN",
    "M1_CONTROL",
)
LABELS = ("PASS", "BOOKKEEPING", "REVERSAL", "VOID")
MIN_MEASURABLE = 8


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_num(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_seed(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _finite(value) -> bool:
    return _is_num(value) and math.isfinite(float(value))


def _close(left: float, right: float, tolerance: float = ROUNDING_EPSILON) -> bool:
    return abs(float(left) - float(right)) <= tolerance + 1e-15


def _is_sha256(value) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-fA-F]{64}", value))


def derive_label(lo: float, hi: float) -> str:
    """The protocol's directional label: below zero passes, above zero reverses."""
    if hi < 0:
        return "PASS"
    if lo > 0:
        return "REVERSAL"
    return "BOOKKEEPING"


def bootstrap_interval(values: list[float], level: float = LEVEL,
                       resamples: int = RESAMPLES) -> dict:
    """Recompute the protocol's paired percentile bootstrap.

    This is intentionally a separate implementation from the readout adapter.
    It uses the same fixed PRNG seed and percentile-index rule, because those are
    part of the protocol rather than implementation details.
    """
    values = [float(value) for value in values]
    if not values:
        raise ValueError("no per-seed differences to resample")
    rng = random.Random(BOOTSTRAP_SEED)
    means = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(len(values)):
            total += values[rng.randrange(len(values))]
        means.append(total / len(values))
    means.sort()
    lo_index = int(round((1 - level) / 2 * (resamples - 1)))
    hi_index = int(round((1 + level) / 2 * (resamples - 1)))
    return {
        "mean": sum(values) / len(values),
        "lo": means[lo_index],
        "hi": means[hi_index],
    }


def _rounded(interval: dict) -> dict:
    return {field: round(float(interval[field]), DECIMALS) for field in ("mean", "lo", "hi")}


def _marker_errors(marker) -> list[str]:
    """The run marker must prove the attempt finished before any result is read."""
    if marker is None:
        return ["run marker is missing; a result is auditable only after a COMPLETED run"]
    if not isinstance(marker, dict):
        return ["run marker is not a JSON object; a result is auditable only after a COMPLETED run"]
    status = marker.get("status")
    if status != "COMPLETED":
        return [
            "run marker status is %r, not COMPLETED; a result is auditable only after a "
            "COMPLETED run (a STARTED or VOID attempt is never audited)" % (status,)
        ]
    return []


def _seed_values(record: dict) -> list[int]:
    if not isinstance(record, dict):
        raise ValueError("the seed declaration is not a JSON object")
    block = record.get("seed_block", record.get("seeds"))
    if isinstance(block, dict):
        block = block.get("seeds")
    if not isinstance(block, list) or not all(isinstance(seed, int) and not isinstance(seed, bool)
                                             for seed in block):
        raise ValueError("the seed declaration does not contain a list of integer seeds")
    return list(block)


def _gate_mapping(record: dict) -> dict:
    if not isinstance(record, dict):
        return {}
    gates = record.get("gates", record)
    return gates if isinstance(gates, dict) else {}


def _check_control(control, declared: set[int], is_void: bool, codes: list[str],
                   errors: list[str]) -> bool:
    """Validate the section 8 arm; return whether M1 failed."""
    if not isinstance(control, dict):
        errors.append("control must be an object describing the section 8 arm")
        return False

    status = control.get("status")
    if status not in ("PASS", "FAIL", "NOT RUN"):
        errors.append("control status must be PASS, FAIL or NOT RUN")
    seed = control.get("seed")
    if not _is_seed(seed) or seed not in declared:
        errors.append("control seed %r is not declared" % (seed,))
    intervention = control.get("intervention")
    if intervention not in ("remove_member", "retire"):
        errors.append("control intervention must be remove_member or retire")
    for field in ("composite_id", "bystander_id", "metric"):
        if not isinstance(control.get(field), str) or not control[field].strip():
            errors.append("control %s must be a non-empty string" % field)
    if control.get("composite_id") and control.get("bystander_id"):
        if control["composite_id"] == control["bystander_id"]:
            errors.append("the control's bystander must not be its target composite")
    if intervention == "remove_member":
        if not str(control.get("removed_member") or "").strip():
            errors.append("remove_member needs the removed member")
    elif intervention == "retire" and control.get("removed_member") not in (None, ""):
        errors.append("retire takes no removed_member")

    if status == "NOT RUN":
        if not str(control.get("detail") or "").strip():
            errors.append("a control that did not run needs a reason")
        if "member_delta" in control or "bystander_delta" in control:
            errors.append("a control that did not run carries no deltas")
        return False

    member = control.get("member_delta")
    bystander = control.get("bystander_delta")
    if not _finite(member):
        errors.append("control member_delta must be finite numeric")
    if not _finite(bystander):
        errors.append("control bystander_delta must be finite numeric")

    failed = False
    if _finite(bystander) and status in ("PASS", "FAIL"):
        derived = "PASS" if float(bystander) == 0.0 else "FAIL"
        if status != derived:
            errors.append(
                "control status %s contradicts bystander_delta %.9f: M1 returns %s"
                % (status, float(bystander), derived)
            )
        failed = derived == "FAIL"
    if status == "FAIL":
        failed = True
        if not is_void:
            errors.append("an M1 violation (control FAIL) requires VOID")
        elif "M1_CONTROL" not in codes:
            errors.append("an M1 violation requires the M1_CONTROL code")
    return failed


def audit(result: dict, raw_log: dict, committed_gates: dict, seeds: list[int],
          marker: dict | None = None) -> list[str]:
    """Return every audit finding; an empty list means the result verified.

    The marker is required and must say `COMPLETED`.  The check happens before
    any result field is read, so a STARTED attempt's partial output cannot be
    presented as an audited result.
    """
    marker_errors = _marker_errors(marker)
    if marker_errors:
        return marker_errors

    errors: list[str] = []
    declared = set(seeds)

    if not isinstance(result, dict):
        return ["result is not a JSON object"]
    if result.get("kind") != "v2_first_cell_result":
        errors.append("kind must be v2_first_cell_result")

    outcome = result.get("outcome")
    if outcome not in LABELS:
        errors.append("outcome must be one of %s" % ", ".join(LABELS))
    declared_void = outcome == "VOID"
    void = result.get("void")
    is_void = declared_void or void is not None
    codes: list[str] = []
    if void is not None:
        if not isinstance(void, dict):
            errors.append("void must be an object with codes and detail")
        else:
            value = void.get("codes")
            if not isinstance(value, list) or not value:
                errors.append("a VOID needs at least one reason code")
            else:
                codes = [code for code in value if isinstance(code, str)]
                if len(codes) != len(value):
                    errors.append("VOID codes must be strings")
                unknown = sorted(set(codes) - set(VOID_CODES))
                if unknown:
                    errors.append("unknown VOID codes: %s" % ", ".join(unknown))
            if not str(void.get("detail") or "").strip():
                errors.append("a VOID needs a detail sentence")
        if not declared_void:
            errors.append("a result with a void object must use the VOID outcome")
    if declared_void and void is None:
        errors.append("the VOID outcome needs a void object with codes and detail")

    pin_ok = result.get("scorer_pin_ok")
    if pin_ok not in (True, False):
        errors.append("scorer_pin_ok must be true or false")
    if pin_ok is not True and not is_void:
        errors.append("a stale scorer pin requires VOID")
    if pin_ok is not True and is_void and "SCORER_PIN" not in codes:
        errors.append("a stale scorer pin requires the SCORER_PIN code")

    # Result gates: shape, status, evidence, and the conditions that require VOID.
    result_gates = result.get("gates")
    failed_gates: list[str] = []
    not_run_gates: list[str] = []
    if not isinstance(result_gates, dict) or set(result_gates) != set(GATE_IDS):
        errors.append("gates must name exactly A1-A5")
        result_gates = result_gates if isinstance(result_gates, dict) else {}
    for gate in GATE_IDS:
        row = result_gates.get(gate)
        if not isinstance(row, dict):
            errors.append("gate %s is missing" % gate)
            continue
        status = row.get("status")
        if status not in ("PASS", "FAIL", "NOT RUN"):
            errors.append("gate %s status must be PASS, FAIL or NOT RUN" % gate)
        elif not str(row.get("evidence") or "").strip():
            errors.append("gate %s needs its evidence" % gate)
        if status == "FAIL":
            failed_gates.append(gate)
        elif status == "NOT RUN":
            not_run_gates.append(gate)
    if not is_void and failed_gates:
        errors.append("a failed gate requires VOID: %s" % ", ".join(failed_gates))
    if not is_void and not_run_gates:
        errors.append("a gate that did not run requires VOID: %s" % ", ".join(not_run_gates))

    # The committed gate record is the independent source for the result's gate block.
    committed = _gate_mapping(committed_gates)
    if not committed:
        errors.append("the committed gate record is missing or unreadable")
    elif set(committed) != set(GATE_IDS):
        errors.append("the committed gate record must name exactly A1-A5")
    for gate in GATE_IDS:
        result_row = result_gates.get(gate)
        committed_row = committed.get(gate)
        if not isinstance(result_row, dict) or not isinstance(committed_row, dict):
            continue
        result_status = result_row.get("status")
        committed_status = committed_row.get("status")
        if committed_status not in ("PASS", "FAIL", "NOT RUN"):
            errors.append("committed gate %s has an invalid status" % gate)
            continue
        if result_status == committed_status:
            continue
        if gate == "A1" and is_void and committed_status == "PASS" and result_status in (
                "FAIL", "NOT RUN") and (
                "A1_CANONICALISATION" in codes or "GATES_NOT_RUN" in codes):
            continue
        errors.append(
            "result gate %s is %s but the committed record says %s"
            % (gate, result_status, committed_status)
        )

    # Result rows and their beta declarations.
    rows = result.get("per_seed")
    if not isinstance(rows, list) or not rows:
        errors.append("per_seed must be a non-empty list")
        rows = []
    seen: set[int] = set()
    measurable: list[dict] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append("per_seed[%d] is not an object" % index)
            continue
        seed = row.get("seed")
        if not _is_seed(seed) or seed not in declared:
            errors.append("per_seed[%d]: seed %r is not declared" % (index, seed))
            continue
        if seed in seen:
            errors.append("per_seed[%d]: seed %r is duplicated" % (index, seed))
            continue
        seen.add(seed)
        flag = row.get("measurable")
        if flag is True:
            measurable.append(row)
            if not _finite(row.get("d")):
                errors.append("seed %d: a measurable seed needs finite d" % seed)
            if not _finite(row.get("d_B")):
                errors.append("seed %d: a measurable seed needs finite d_B" % seed)
            beta = row.get("beta")
            if not isinstance(beta, dict) or set(beta) != {"B", "C"}:
                errors.append("seed %d: beta must name B and C only; arm A selects no beta" % seed)
            else:
                for arm in ("B", "C"):
                    if beta[arm] not in BETA_GRID:
                        errors.append(
                            "seed %d: beta %s must be one of %s"
                            % (seed, arm, ", ".join(str(value) for value in BETA_GRID))
                        )
        elif flag is False:
            if not str(row.get("exclusion") or "").strip():
                errors.append("seed %d: an unmeasured seed needs an exclusion reason" % seed)
            if "d" in row or "d_B" in row or "beta" in row:
                errors.append("seed %d: an unmeasured seed must not carry d, d_B or beta" % seed)
        else:
            errors.append("seed %d: measurable must be true or false" % seed)

    missing = declared - seen
    if missing and not is_void:
        errors.append("declared seeds missing: %s" % ", ".join(str(seed) for seed in sorted(missing)))
    if missing and is_void and "PARTS_INCOMPLETE" not in codes:
        errors.append("missing declared seeds require the PARTS_INCOMPLETE code")
    if len(measurable) < MIN_MEASURABLE:
        if not is_void:
            errors.append("fewer than %d measurable seeds requires VOID" % MIN_MEASURABLE)
        elif "SEEDS_MEASURABLE" not in codes:
            errors.append("fewer than %d measurable seeds requires the SEEDS_MEASURABLE code" % MIN_MEASURABLE)

    # Raw-log linkage: every result seed must be present, and every measurable
    # loss and beta must agree with the result within its six-decimal rounding.
    raw_rows = raw_log.get("seeds") if isinstance(raw_log, dict) else None
    raw_by_seed: dict[int, dict] = {}
    if not isinstance(raw_log, dict) or raw_log.get("kind") != "v2_first_cell_run_log":
        errors.append("raw log is missing or is not a v2_first_cell_run_log")
    if not isinstance(raw_rows, list) or not raw_rows:
        errors.append("raw log must carry a non-empty per-seed list")
        raw_rows = []
    for index, row in enumerate(raw_rows):
        if not isinstance(row, dict) or not _is_seed(row.get("seed")):
            errors.append("raw log row %d has no integer seed" % index)
            continue
        seed = row["seed"]
        if seed in raw_by_seed:
            errors.append("raw log seed %d is duplicated" % seed)
        else:
            raw_by_seed[seed] = row
    if set(raw_by_seed) != declared:
        errors.append("raw log seeds do not exactly match the declared block")

    for row in rows:
        if not isinstance(row, dict):
            continue
        seed = row.get("seed")
        if not _is_seed(seed) or seed not in declared:
            continue
        raw = raw_by_seed.get(seed)
        if raw is None:
            errors.append("seed %d is missing from the raw log" % seed)
            continue
        flag = row.get("measurable")
        if raw.get("measurable") is not flag:
            errors.append("seed %d: raw log measurability disagrees with the result" % seed)
        if flag is False:
            if raw.get("exclusion") != row.get("exclusion"):
                errors.append("seed %d: raw log exclusion disagrees with the result" % seed)
            continue
        if flag is not True:
            continue
        arms = raw.get("arms")
        if not isinstance(arms, dict) or set(arms) != set(ARMS):
            errors.append("seed %d: raw log must carry arms A, B and C" % seed)
            continue
        losses: dict[str, float] = {}
        result_beta = row.get("beta") if isinstance(row.get("beta"), dict) else {}
        for arm in ARMS:
            record = arms.get(arm)
            if not isinstance(record, dict):
                errors.append("seed %d: raw log arm %s is missing" % (seed, arm))
                continue
            loss = record.get("log_loss")
            if not _finite(loss):
                errors.append("seed %d: raw log arm %s has no finite log_loss" % (seed, arm))
            else:
                losses[arm] = float(loss)
            beta = record.get("beta")
            if arm == "A":
                if beta is not None:
                    errors.append("seed %d: raw log arm A must not select a beta" % seed)
            else:
                if beta not in BETA_GRID:
                    errors.append("seed %d: raw log arm %s beta is outside the grid" % (seed, arm))
                if beta != result_beta.get(arm):
                    errors.append(
                        "seed %d: raw log arm %s beta %r disagrees with the result %r"
                        % (seed, arm, beta, result_beta.get(arm))
                    )
        if set(losses) == set(ARMS):
            raw_d = losses["C"] - losses["A"]
            raw_d_b = losses["B"] - losses["A"]
            if _finite(row.get("d")) and not _close(raw_d, row["d"]):
                errors.append(
                    "seed %d: result d %.9f is not the raw C-A difference %.9f"
                    % (seed, float(row["d"]), raw_d)
                )
            if _finite(row.get("d_B")) and not _close(raw_d_b, row["d_B"]):
                errors.append(
                    "seed %d: result d_B %.9f is not the raw B-A difference %.9f"
                    % (seed, float(row["d_B"]), raw_d_b)
                )

    # The interval and label are derived here, not read from the result.
    interval = result.get("interval")
    if declared_void:
        if interval is not None:
            errors.append("a VOID report carries no interval")
    elif not isinstance(interval, dict):
        errors.append("a non-VOID result needs an interval")
    else:
        for field in ("mean", "lo", "hi"):
            if not _finite(interval.get(field)):
                errors.append("interval %s must be finite numeric" % field)
        if interval.get("level") != LEVEL:
            errors.append("interval level must be %.2f" % LEVEL)
        if interval.get("resamples") != RESAMPLES:
            errors.append("interval resamples must be %d" % RESAMPLES)
        if all(_finite(interval.get(field)) for field in ("mean", "lo", "hi")):
            if interval["lo"] > interval["hi"]:
                errors.append("interval lo is above hi")
            if len(measurable) >= MIN_MEASURABLE and all(
                    _finite(row.get("d")) for row in measurable):
                values = [float(row["d"]) for row in measurable]
                recomputed = bootstrap_interval(values)
                expected = _rounded(recomputed)
                for field in ("mean", "lo", "hi"):
                    if not _close(interval[field], expected[field]):
                        errors.append(
                            "interval %s %.9f disagrees with the independent recomputation %.9f"
                            % (field, float(interval[field]), expected[field])
                        )
                reported_label = derive_label(interval["lo"], interval["hi"])
                recomputed_label = derive_label(recomputed["lo"], recomputed["hi"])
                if outcome != reported_label:
                    errors.append(
                        "outcome %s contradicts reported interval [%.9f, %.9f]: the rule returns %s"
                        % (outcome, interval["lo"], interval["hi"], reported_label)
                    )
                if outcome != recomputed_label:
                    errors.append(
                        "outcome %s contradicts recomputed interval [%.9f, %.9f]: the rule returns %s"
                        % (outcome, recomputed["lo"], recomputed["hi"], recomputed_label)
                    )
                if reported_label != recomputed_label:
                    errors.append(
                        "the reported and recomputed intervals fall on opposite sides of zero "
                        "(%s vs %s); the label cannot be audited"
                        % (reported_label, recomputed_label)
                    )

    control_failed = _check_control(result.get("control"), declared, is_void, codes, errors)

    if void is not None:
        conditions: set[str] = set(GATE_CODES[gate] for gate in failed_gates)
        if not_run_gates:
            conditions.add("GATES_NOT_RUN")
        if len(measurable) < MIN_MEASURABLE:
            conditions.add("SEEDS_MEASURABLE")
        if missing:
            conditions.add("PARTS_INCOMPLETE")
        if pin_ok is not True:
            conditions.add("SCORER_PIN")
        if control_failed:
            conditions.add("M1_CONTROL")
        if not conditions:
            errors.append("a VOID names no condition this result shows")
        elif codes and not (conditions & set(codes)):
            errors.append("the VOID codes name no condition this result shows")
        for gate in failed_gates:
            if GATE_CODES[gate] not in codes:
                errors.append("failed gate %s requires code %s" % (gate, GATE_CODES[gate]))
        if not_run_gates and "GATES_NOT_RUN" not in codes:
            errors.append("a gate that did not run requires the GATES_NOT_RUN code")
        if len(measurable) < MIN_MEASURABLE and "SEEDS_MEASURABLE" not in codes:
            errors.append("fewer than %d measurable seeds requires the SEEDS_MEASURABLE code" % MIN_MEASURABLE)
        if missing and "PARTS_INCOMPLETE" not in codes:
            errors.append("missing declared seeds require the PARTS_INCOMPLETE code")
        if pin_ok is not True and "SCORER_PIN" not in codes:
            errors.append("a stale scorer pin requires the SCORER_PIN code")
        if control_failed and "M1_CONTROL" not in codes:
            errors.append("an M1 violation requires the M1_CONTROL code")

    return errors


def audit_files(result_path: Path = RESULT, raw_log_path: Path = RAW_LOG,
                gates_path: Path = GATES, seeds_path: Path = SEEDS,
                marker_path: Path = RUN) -> list[str]:
    """Read the run marker and the four artifacts, and audit them; never writes.

    A COMPLETED marker must bind the exact result bytes through `result_sha256`.
    The digest is checked before the result is parsed, so an edited or truncated
    result cannot pass by being self-consistent with the raw log.
    """
    try:
        marker = _load(marker_path)
    except (OSError, ValueError) as error:
        return [
            "cannot read run marker %s: %s; a result is auditable only after a COMPLETED run"
            % (marker_path, error)
        ]
    marker_errors = _marker_errors(marker)
    if marker_errors:
        return marker_errors
    recorded = marker.get("result_sha256")
    if not _is_sha256(recorded):
        return ["run marker has no valid result_sha256; a COMPLETED run must bind its result file"]
    try:
        result_bytes = result_path.read_bytes()
    except OSError as error:
        return ["cannot read result %s: %s" % (result_path, error)]
    actual = hashlib.sha256(result_bytes).hexdigest()
    if actual != recorded.lower():
        return [
            "result file %s does not match the COMPLETED run marker's result_sha256 "
            "(recorded %s, actual %s)" % (result_path, recorded, actual)
        ]
    try:
        result = json.loads(result_bytes.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        return ["cannot read result %s: %s" % (result_path, error)]
    try:
        raw_log = _load(raw_log_path)
    except (OSError, ValueError) as error:
        return ["cannot read raw log %s: %s" % (raw_log_path, error)]
    try:
        gates = _load(gates_path)
    except (OSError, ValueError) as error:
        return ["cannot read gate record %s: %s" % (gates_path, error)]
    try:
        seeds = _seed_values(_load(seeds_path))
    except (OSError, ValueError) as error:
        return ["cannot read seed declaration %s: %s" % (seeds_path, error)]
    return audit(result, raw_log, gates, seeds, marker)


def _fixture():
    """An in-memory result used by --check; no world is touched."""
    seeds = list(range(20910101, 20910111))
    differences = [round(-0.0010 - index * 0.0001, DECIMALS)
                   for index in range(len(seeds))]
    interval = bootstrap_interval(differences)
    reported = _rounded(interval)
    result = {
        "kind": "v2_first_cell_result",
        "outcome": derive_label(reported["lo"], reported["hi"]),
        "scorer_pin_ok": True,
        "gates": {gate: {"status": "PASS", "evidence": "audit fixture"} for gate in GATE_IDS},
        "per_seed": [
            {
                "seed": seed,
                "measurable": True,
                "d": round(value, DECIMALS),
                "d_B": round(value - 0.0005, DECIMALS),
                "beta": {"B": 1, "C": 2},
            }
            for seed, value in zip(seeds, differences)
        ],
        "interval": dict(reported, level=LEVEL, resamples=RESAMPLES),
        "control": {
            "status": "PASS",
            "seed": seeds[0],
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
            for row in result["per_seed"]
        ],
    }
    gates = {"gates": result["gates"]}
    return result, raw, gates, seeds


def _check() -> int:
    result, raw, gates, seeds = _fixture()
    marker = {"kind": "v2_first_cell_run", "status": "COMPLETED"}
    if audit(result, raw, gates, seeds, marker):
        raise SystemExit("the audit fixture does not verify: %s"
                         % "; ".join(audit(result, raw, gates, seeds, marker)))
    broken = json.loads(json.dumps(result))
    broken["outcome"] = "BOOKKEEPING"
    if not any("outcome" in error for error in audit(broken, raw, gates, seeds, marker)):
        raise SystemExit("the audit accepted a label that contradicts its interval")
    if not any("STARTED" in error for error in audit(
            result, raw, gates, seeds, {"kind": "v2_first_cell_run", "status": "STARTED"})):
        raise SystemExit("the audit accepted a STARTED run marker")
    print("check: bootstrap recomputes; a completed result verifies; a contradictory label "
          "and a STARTED marker are refused")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="run synthetic audit fixtures")
    group.add_argument("--audit", nargs="?", const=str(RESULT), metavar="RESULT",
                       help="audit a result (default: docs/v2_first_cell_result.json)")
    parser.add_argument("--raw-log", metavar="PATH", default=str(RAW_LOG),
                        help="raw per-seed log (default: docs/v2_first_cell_run_log.json)")
    parser.add_argument("--gates", metavar="PATH", default=str(GATES),
                        help="committed gate record (default: docs/v2_first_cell_gates.json)")
    parser.add_argument("--seeds", metavar="PATH", default=str(SEEDS),
                        help="seed declaration (default: docs/v2_first_cell_seeds.json)")
    parser.add_argument("--marker", metavar="PATH", default=str(RUN),
                        help="run marker (default: docs/v2_first_cell_run.json); it must be COMPLETED")
    args = parser.parse_args(argv)

    if args.check:
        return _check()
    if args.audit is None:
        parser.print_help()
        return 2
    errors = audit_files(Path(args.audit), Path(args.raw_log), Path(args.gates), Path(args.seeds),
                         Path(args.marker))
    if errors:
        print("audit: FAIL (%d finding(s))" % len(errors), file=sys.stderr)
        for error in errors:
            print("  - %s" % error, file=sys.stderr)
        return 1
    print("audit: PASS — result, raw log, gate record and independent bootstrap agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
