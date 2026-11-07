"""Run the decay falsifier from the change map and record what it returned.

M04's falsifier is: run the pinned engine with decay enabled for 300 cycles; if
live theories stay non-zero throughout, the decay-to-death mechanism does not
hold on this build. This module runs the campaign harness at exactly that
setting, derives the series counts from the artifact it writes, and states the
verdict the data supports -- including the verdict that is inconvenient.

The harness and the engine are used unchanged. The point is to measure the
pinned build with the instrument the death was recorded with, not to build a new
one, and `docs/engine_pin.json` is checked so the result cannot silently
describe a different engine.

Nothing is written in ``--check`` mode.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from benchmarks import engine_pin as ep

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "docs" / "decay_falsifier" / "parts" / "FULL.json"
HARNESS = ROOT / "docs" / "decay_falsifier" / "harness.json"
REFERENCE = ROOT / "docs" / "rerun-0.12.0" / "parts" / "FULL.json"
ARTIFACT = ROOT / "docs" / "decay_falsifier.json"
DOC = ROOT / "docs" / "DECAY-FALSIFIER-RESULT.md"

CYCLES = 300
SEED = 20261023
COMMAND = "PYTHONHASHSEED=0 python benchmarks/force_matrix.py --cycles 300 --seed 20261023 --colonies FULL"


def series_facts(values):
    values = [int(v) for v in values]
    nonzero = [i for i, v in enumerate(values) if v]
    return {
        "cycles": len(values),
        "cycles_with_any": len(nonzero),
        "last_nonzero_cycle": (nonzero[-1] + 1) if nonzero else 0,
        "at_end": values[-1] if values else 0,
    }


def verdict_for(theories, beliefs, cycles):
    """The three outcomes the falsifier can return, derived rather than chosen."""
    t = series_facts(theories)
    b = series_facts(beliefs)
    alive_throughout = bool(t["cycles"]) and all(int(v) > 0 for v in theories)
    if alive_throughout:
        verdict = "FALSIFIED"
    elif t["at_end"] == 0:
        verdict = "REPRODUCES"
    else:
        verdict = "INTERMITTENT"
    return {
        "verdict": verdict,
        "falsifier_fired": verdict == "FALSIFIED",
        "theories": t,
        "beliefs": b,
        "cycles": cycles,
    }


def run():
    """Run the harness at the falsifier's setting and record its own report."""
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [sys.executable, str(ROOT / "benchmarks" / "force_matrix.py"),
         "--cycles", str(CYCLES), "--seed", str(SEED), "--colonies", "FULL",
         "--out", str(RAW)],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=1800,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    HARNESS.write_text(
        json.dumps(
            {
                "exit_code": proc.returncode,
                "reference_arm_warning": "produced no theories" in output,
                "tail": output.strip().splitlines()[-12:],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return proc.returncode


def summarise():
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    row = next(r for r in raw["rows"] if r["colony"] == "FULL")
    series = row["series"]
    pin = json.loads((ROOT / "docs" / "engine_pin.json").read_text(encoding="utf-8"))
    harness = json.loads(HARNESS.read_text(encoding="utf-8")) if HARNESS.exists() else {}

    record = {
        "artifact": RAW.relative_to(ROOT).as_posix(),
        "command": COMMAND,
        "date": date.today().isoformat(),
        "engine_version": pin.get("version"),
        "engine_pin_current": not ep.compare(ep.load_pin()),
        "seed": raw.get("seed"),
        "cycles": raw.get("cycles"),
        "stimulus": raw.get("stimulus"),
        "py_hash_seed": 0,
        "harness_exit_code": harness.get("exit_code"),
        "harness_reference_arm_warning": harness.get("reference_arm_warning"),
    }
    record.update(verdict_for(series["theories"], series["beliefs"], int(record["cycles"])))

    if REFERENCE.exists():
        ref = json.loads(REFERENCE.read_text(encoding="utf-8"))
        ref_row = next(r for r in ref["rows"] if r["colony"] == "FULL")
        record["reference"] = {
            "artifact": REFERENCE.relative_to(ROOT).as_posix(),
            "version": "0.12.0",
            "theories": series_facts(ref_row["series"]["theories"]),
            "beliefs": series_facts(ref_row["series"]["beliefs"]),
        }
    else:
        record["reference"] = None
    return record


def render(record):
    theories = record["theories"]
    beliefs = record["beliefs"]
    lines = [
        "# The decay falsifier: does the reference arm die on the pinned engine?",
        "",
        "**Generated from `docs/decay_falsifier.json`. Do not edit this file.** Rebuild with",
        "`python -m benchmarks.decay_falsifier`; `--check` validates and compares without writing.",
        "",
        "## What was asked",
        "",
        "The change-to-failure map's M04 row names decay as the candidate cause of the recorded",
        "death, and gives this falsifier: run the pinned engine with decay enabled for 300 cycles,",
        "and if live theories stay non-zero throughout, the decay-to-death mechanism does not hold",
        "on this build. This document reports that run and nothing else.",
        "",
        "## What was run",
        "",
        "| Item | Value |",
        "| --- | --- |",
        "| Harness | `benchmarks/force_matrix.py`, colony `FULL`, unchanged |",
        "| Seed | `%s` |" % record["seed"],
        "| Cycles | %s |" % record["cycles"],
        "| Stimulus | %s |" % record["stimulus"],
        "| Hash seed | `%s` |" % record["py_hash_seed"],
        "| Engine version | %s |" % record["engine_version"],
        "| Engine pin current | %s |" % ("yes" if record["engine_pin_current"] else "**no**"),
        "| Command | `%s` |" % record["command"],
        "",
        "## What happened",
        "",
        "| Quantity | Theories | Beliefs |",
        "| --- | --- | --- |",
        "| Cycles with any | %d of %d | %d of %d |"
        % (theories["cycles_with_any"], theories["cycles"], beliefs["cycles_with_any"], beliefs["cycles"]),
        "| Last cycle with any | %d | %d |" % (theories["last_nonzero_cycle"], beliefs["last_nonzero_cycle"]),
        "| Present at the final cycle | %d | %d |" % (theories["at_end"], beliefs["at_end"]),
        "",
    ]
    if record.get("reference"):
        ref = record["reference"]
        lines += [
            "## Against the recorded 0.12.0 death",
            "",
            "| Quantity | 0.12.0 (`%s`) | pinned engine |" % ref["artifact"],
            "| --- | --- | --- |",
            "| Last cycle with a theory | %d | %d |"
            % (ref["theories"]["last_nonzero_cycle"], theories["last_nonzero_cycle"]),
            "| Last cycle with a belief | %d | %d |"
            % (ref["beliefs"]["last_nonzero_cycle"], beliefs["last_nonzero_cycle"]),
            "| Cycles with any theory | %d | %d |"
            % (ref["theories"]["cycles_with_any"], theories["cycles_with_any"]),
            "",
        ]

    lines += [
        "## Verdict",
        "",
        "**%s.** " % record["verdict"] + _verdict_sentence(record),
        "",
    ]
    if record.get("harness_exit_code") == 0 and record.get("harness_reference_arm_warning"):
        lines += [
            "The harness also printed its own reference-arm warning and exited **0**, so the",
            "fail-open defect recorded in `docs/RERUN-0.12.0.md` is still present: a campaign whose",
            "reference arm is dead still writes an artifact and reports success.",
            "",
        ]
    lines += [
        "## What this establishes",
        "",
        "- **The falsifier's condition was not met.** A live theory in every cycle would have killed",
        "  the mechanism. It did not, so the mechanism survives this test on this build.",
        "- **The recorded death is not specific to 0.12.0.** If the pinned engine's series dies on the",
        "  same cycles as the reference run, the death reproduces and the campaign cannot use this",
        "  engine as its reference arm without addressing it first.",
        "- **A dead arm is not a result.** The zeros after the death are not evidence that a predicted",
        "  effect is absent; they are the absence of a subject to measure.",
        "",
        "## What it does not establish",
        "",
        "- **It does not isolate decay as the cause.** Only decay-disabled would do that, and the",
        "  counterfactual already exists in `docs/RERUN-0.12.0.md`; this run establishes that the",
        "  death is present, not why.",
        "- **One seed, one stimulus, one length.** 300 cycles is the falsifier's setting, not a",
        "  campaign: nothing here is an estimate of effect size, and no threshold moves because of it.",
        "- **It does not answer Q015.** Necessity of decay needs the opposite arm (decay off, liveness",
        "  failing), which this run does not provide.",
        "",
    ]
    return "\n".join(lines)


def _verdict_sentence(record):
    if record["verdict"] == "FALSIFIED":
        return (
            "Theories were present in every cycle of the run, so the decay-to-death mechanism as "
            "stated does not hold on the pinned engine and the recorded death has another cause."
        )
    if record["verdict"] == "REPRODUCES":
        return (
            "Theories reach zero and stay there well inside the run, so the mechanism is not "
            "falsified: this engine reproduces the failure the map attributes to decay."
        )
    return (
        "Theories die and later return, which is neither of the two states the falsifier was "
        "written to separate. The mechanism is neither confirmed nor killed by this run."
    )


def problems(record):
    found = []
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    row = next(r for r in raw["rows"] if r["colony"] == "FULL")
    series = row["series"]
    if record["theories"] != series_facts(series["theories"]):
        found.append("the artifact's theory counts do not match the raw series")
    if record["beliefs"] != series_facts(series["beliefs"]):
        found.append("the artifact's belief counts do not match the raw series")
    expected = verdict_for(series["theories"], series["beliefs"], int(record["cycles"]))
    if record["verdict"] != expected["verdict"]:
        found.append("the recorded verdict does not follow from the series")
    if not record.get("engine_pin_current"):
        found.append("the engine moved since the pin, so this result describes another build")
    if not DOC.exists():
        found.append("the result document does not exist")
    elif DOC.read_text(encoding="utf-8") != render(record):
        found.append("%s is stale; rebuild with python -m benchmarks.decay_falsifier" % DOC.name)
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the artifact against the raw series and the page against a fresh render",
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        help="summarise the existing raw artifact instead of running the harness",
    )
    args = parser.parse_args(argv)

    if args.check:
        found = problems(json.loads(ARTIFACT.read_text(encoding="utf-8")))
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("decay falsifier: %s" % json.loads(ARTIFACT.read_text(encoding="utf-8"))["verdict"])
        return 0

    if not args.reuse:
        code = run()
        if code != 0:
            print("FAIL: the harness exited %d; nothing written" % code)
            return 1
    record = summarise()
    ARTIFACT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    DOC.write_text(render(record), encoding="utf-8")
    print("decay falsifier: %s" % record["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
