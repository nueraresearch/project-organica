"""The ten-seed runner for the first V2 cell, built but not run.

The runner owns the protocol's order, not its design. It refuses to execute a world
until `DECISION-V2-FIRST-CELL` is signed and the seed block is marked spent; it refuses
to score any arm until a committed A1–A5 gate record is present and every gate is PASS,
because the pre-registration puts those gates before the behavioural cell; and it
assembles the result artifact through the same validator that renders the report, so a
cell cannot be written in a shape the report would reject.

    python -m benchmarks.v2_first_cell_runner --check
    python -m benchmarks.v2_first_cell_runner --run [--gates PATH] [--control PATH] [--out PATH]

`--check` executes no world and writes nothing. `--run` is refused while the
authorisation is pending, which is its state now.

Inputs:

* `docs/v2_first_cell_gates.json` — written by `benchmarks.v2_first_cell_gates`. It
  currently records A1–A5 PASS, so the gate block is cleared; the runner still refuses while
  the authorisation is PENDING.
* `docs/v2_first_cell_control.json` — still absent; the section 8 control is recorded
  NOT RUN with a reason, which is admissible because the arm is secondary.

The `--control` record is the object the report template's section 8 expects.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from benchmarks import engine_stamp, v2_first_cell_readout as readout, v2_first_cell_report as report  # noqa: E402

DECISIONS = REPO / "docs" / "decisions.json"
RESERVATIONS = REPO / "docs" / "a1_seed_reservations.json"
PIN = REPO / "docs" / "v2_first_cell_scorer_pin.json"
GATES = REPO / "docs" / "v2_first_cell_gates.json"
CONTROL = REPO / "docs" / "v2_first_cell_control.json"
OUT = REPO / "docs" / "v2_first_cell_result.json"
AUTHORISATION = "DECISION-V2-FIRST-CELL"
SEED_OWNER = "docs/v2_first_cell_seeds.json"


class GateError(ValueError):
    """The gate record is missing or unusable; no cell can be run under it."""


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def authorisation() -> tuple[bool, str]:
    """Signed decision plus a spent block; either alone is not enough."""
    row = [d for d in _load(DECISIONS)["decisions"] if d["decision_id"] == AUTHORISATION][0]
    if row["status"] != "ADOPTED":
        return False, "%s is %s; the cell is not authorised" % (AUTHORISATION, row["status"])
    block = [r for r in _load(RESERVATIONS)["reservations"] if r["owner"] == SEED_OWNER][0]
    if not block["spent"]:
        return False, "the decision is signed but the seed block is still marked held"
    return True, "authorised"


def pins() -> list[str]:
    """Every digest in the scorer pin, including the adapter's; empty means all match."""
    errors = []
    record = _load(PIN)
    for module, digest in record["modules"].items():
        path = REPO / module
        if not path.exists():
            errors.append("pinned module missing: %s" % module)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append("pinned module changed: %s" % module)
    if record["adapter"]["sha256"] != readout.adapter_sha256():
        errors.append("the readout adapter's digest is stale; re-pin is a reviewed commit")
    return errors


def validate_gates(gates: dict) -> None:
    """The record's structure; a gate that was not run is not a pass."""
    if set(gates) != set(report.GATE_IDS):
        raise GateError("the gate record must name exactly A1-A5")
    for gate in report.GATE_IDS:
        row = gates.get(gate)
        if not isinstance(row, dict):
            raise GateError("gate %s is missing" % gate)
        if row.get("status") not in ("PASS", "FAIL", "NOT RUN"):
            raise GateError("gate %s status must be PASS, FAIL or NOT RUN" % gate)
        if not str(row.get("evidence") or "").strip():
            raise GateError("gate %s needs its evidence" % gate)


def load_gates(path: Path = GATES) -> dict:
    """Read the A1–A5 record, or refuse."""
    if not path.exists():
        raise GateError(
            "no gate record at %s; A1-A5 must run and be committed before the cell" % path
        )
    record = _load(path)
    gates = record.get("gates", record)
    validate_gates(gates)
    return gates


def synthetic_gates(status: str = "PASS", failing: tuple[str, ...] = ()) -> dict:
    """A gate record for `--check` only; never written as a cell's gates."""
    return {
        gate: {
            "status": "FAIL" if gate in failing else status,
            "evidence": "synthetic gate record for --check",
        }
        for gate in report.GATE_IDS
    }


def unmeasured_rows(reason: str) -> list[dict]:
    return [{"seed": seed, "measurable": False, "exclusion": reason} for seed in report.declared_seeds()]


def no_control(reason: str = "no section 8 control record was supplied; the arm is secondary") -> dict:
    seeds = report.declared_seeds()
    return {
        "status": "NOT RUN",
        "seed": seeds[0],
        "intervention": "remove_member",
        "composite_id": "not-run-target",
        "removed_member": "not-run-edge",
        "bystander_id": "not-run-bystander",
        "metric": "not measured",
        "detail": reason,
    }


def assemble(rows: list[dict], gates: dict, control: dict, *, detail: str | None = None,
             date: str | None = None) -> dict:
    """Build the artifact the report shape accepts; the label is derived, never passed in."""
    failed = [g for g in report.GATE_IDS if gates.get(g, {}).get("status") == "FAIL"]
    not_run = [g for g in report.GATE_IDS if gates.get(g, {}).get("status") == "NOT RUN"]
    result = {
        "kind": "v2_first_cell_result",
        "id": "V2-FIRST-CELL-RESULT-1",
        "date": date or datetime.date.today().isoformat(),
        "protocol": "docs/V2-FIRST-EXPERIMENT-PREREGISTRATION.md",
        "scorer_pin": "docs/v2_first_cell_scorer_pin.json",
        "scorer_pin_ok": True,
        "outcome": "VOID",
        "gates": gates,
        "per_seed": rows,
        "interval": None,
        "control": control,
        "void": None,
    }

    if failed or not_run:
        codes = [report.GATE_CODES[gate] for gate in failed]
        if not_run:
            codes.append("GATES_NOT_RUN")
        measurable = [row for row in rows if row.get("measurable") is True]
        if len(measurable) < report.MIN_MEASURABLE:
            codes.append("SEEDS_MEASURABLE")
        what = ", ".join(failed + not_run)
        result["void"] = {
            "codes": codes,
            "detail": detail or "gate(s) %s did not pass before the behavioural arms" % what,
        }
        return _validated(result)

    measurable = [row for row in rows if row.get("measurable") is True]
    if len(measurable) < report.MIN_MEASURABLE:
        result["void"] = {
            "codes": ["SEEDS_MEASURABLE"],
            "detail": detail or "only %d of 10 seeds were measurable" % len(measurable),
        }
        return _validated(result)

    differences = [float(row["d"]) for row in measurable]
    interval = readout.paired_interval(differences, report.LEVEL, report.RESAMPLES)
    result["interval"] = {
        "mean": round(float(interval["mean"]), 6),
        "lo": round(float(interval["lo"]), 6),
        "hi": round(float(interval["hi"]), 6),
        "level": report.LEVEL,
        "resamples": report.RESAMPLES,
    }
    result["outcome"] = report.derive_label(result["interval"]["lo"], result["interval"]["hi"])
    return _validated(result)


def _validated(result: dict) -> dict:
    errors = report.validate(result)
    if errors:
        raise ValueError("the assembled artifact does not fit the report shape:\n" + "\n".join(errors))
    return result


def _seed_row(seed: int, record: dict) -> dict:
    arms = record["arms"]
    losses = {arm: arms[arm].get("log_loss") for arm in ("A", "B", "C")}
    scored = {arm: arms[arm].get("scored") for arm in ("A", "B", "C")}
    finite = all(isinstance(loss, float) and loss == loss for loss in losses.values())
    if not finite or any((count or 0) <= 0 for count in scored.values()):
        return {"seed": seed, "measurable": False,
                "exclusion": "no finite held-out score or no held-out positives"}
    beta = {arm: arms[arm].get("beta") for arm in ("B", "C")}
    if any(beta[arm] not in report.BETA_GRID for arm in ("B", "C")):
        return {"seed": seed, "measurable": False,
                "exclusion": "an arm selected no beta on the calibration band"}
    return {
        "seed": seed,
        "measurable": True,
        "d": round(losses["C"] - losses["A"], 6),
        "d_B": round(losses["B"] - losses["A"], 6),
        "beta": beta,
    }


def run(gates_path: Path = GATES, control_path: Path = CONTROL, out: Path = OUT) -> int:
    allowed, reason = authorisation()
    if not allowed:
        print("refused: %s" % reason, file=sys.stderr)
        return 1
    pin_errors = pins()
    if pin_errors:
        print("refused:\n  " + "\n  ".join(pin_errors), file=sys.stderr)
        return 1
    try:
        gates = load_gates(gates_path)
    except GateError as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1

    control = _load(control_path) if control_path.exists() else no_control()
    failed = [g for g in report.GATE_IDS if gates[g]["status"] != "PASS"]
    if failed:
        result = assemble(
            unmeasured_rows("not run: gate(s) " + ", ".join(failed) + " did not pass"),
            gates,
            no_control("the gate record did not pass, so the control arm did not run"),
            detail="the cell did not run; gate(s) %s did not pass" % ", ".join(failed),
        )
    else:
        rows = []
        for seed in report.declared_seeds():
            rows.append(_seed_row(seed, readout.run(seed)))
        result = assemble(rows, gates, control)

    result = engine_stamp.stamp(result)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote %s: %s" % (out, result["outcome"]))
    if result["interval"]:
        print("mean d %.6f, 99%% interval [%.6f, %.6f]"
              % (result["interval"]["mean"], result["interval"]["lo"], result["interval"]["hi"]))
    return 0


def check() -> None:
    allowed, reason = authorisation()
    if allowed:
        block = [r for r in _load(RESERVATIONS)["reservations"] if r["owner"] == SEED_OWNER][0]
        if not block["spent"]:
            raise SystemExit("the authorisation is signed but the block is still held")
    elif AUTHORISATION not in reason:
        raise SystemExit("the refusal does not name the authorisation decision")

    pin_errors = pins()
    if pin_errors:
        raise SystemExit("; ".join(pin_errors))

    seeds = report.declared_seeds()
    if seeds != list(range(20910101, 20910111)):
        raise SystemExit("the declared block is not the ten reserved seeds")

    for label in ("PASS", "BOOKKEEPING", "REVERSAL"):
        fixture = report._fixture(label)
        result = assemble(fixture["per_seed"], synthetic_gates(), fixture["control"])
        if result["outcome"] != label:
            raise SystemExit("assembled %s for a %s fixture" % (result["outcome"], label))
        if "**Outcome:** `%s`" % label not in report.render(result):
            raise SystemExit("the report did not render the %s label" % label)

    failed = assemble(unmeasured_rows("not run: gate A3 failed"), synthetic_gates(failing=("A3",)),
                      no_control("the gate record did not pass"))
    if failed["outcome"] != "VOID" or "A3_MUTATION" not in failed["void"]["codes"]:
        raise SystemExit("a failed gate did not assemble as VOID with its code")

    seven = report._fixture("PASS")["per_seed"]
    for row in seven[7:]:
        row["measurable"] = False
        row["exclusion"] = "no held-out positives"
        for field in ("d", "d_B", "beta"):
            row.pop(field)
    short = assemble(seven, synthetic_gates(), report._fixture("PASS")["control"])
    if short["outcome"] != "VOID" or "SEEDS_MEASURABLE" not in short["void"]["codes"]:
        raise SystemExit("seven measurable seeds did not assemble as a measurable VOID")

    print("check: authorisation guard (%s); pins match; ten seeds; "
          "PASS/BOOKKEEPING/REVERSAL assemble; gate and seed VOIDs fire" % reason)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="exercise assembly without running a world")
    group.add_argument("--run", action="store_true", help="run the ten seeds, only when authorised")
    parser.add_argument("--gates", default=str(GATES), help="the A1-A5 gate record")
    parser.add_argument("--control", default=str(CONTROL), help="the section 8 control record")
    parser.add_argument("--out", default=str(OUT), help="where to write the result artifact")
    args = parser.parse_args(argv)

    if args.check:
        check()
        return 0
    return run(Path(args.gates), Path(args.control), Path(args.out))


if __name__ == "__main__":
    raise SystemExit(main())
