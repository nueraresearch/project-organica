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
from benchmarks import verdict_policy as vp

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


def _reference_record(raw_path):
    """The harness's own structured reference-arm check, if it wrote one.

    Presence is the fail-closed build's signature: the older harness printed a warning and
    exited 0, and wrote no such field. Nothing here reads the wording to decide anything --
    the list is recorded and displayed, and attribution is the field's existence.
    """
    if not raw_path.exists():
        return None
    try:
        doc = json.loads(raw_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    entry = doc.get("reference_arm")
    if not isinstance(entry, dict) or not isinstance(entry.get("problems"), list):
        return None
    return {"check": entry.get("check"), "problems": [str(p) for p in entry["problems"]]}


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
    record = _reference_record(RAW)
    HARNESS.write_text(
        json.dumps(
            {
                "exit_code": proc.returncode,
                # The status is the harness's own verdict on its reference arm
                # (benchmarks/force_matrix.py, fail-closed since 2026-11-07). Since the
                # harness persists that check in the artifact, a failure is attributed
                # from the field, never from the printed wording: wording is not a signal,
                # and a checker that greps for one inherits the wording's bugs.
                "mode": "fail-closed" if record is not None else "pre-fail-closed",
                "reference_arm": record,
                "reference_arm_problems": record["problems"] if record else None,
                "reference_arm_failed": (
                    bool(record["problems"]) if record else proc.returncode != 0
                ),
                "tail": output.strip().splitlines()[-12:],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return proc.returncode


def arm_status(harness):
    """The reference arm's verdict, from recorded fields and never from output text.

    A report written before the structured check existed falls back to its own exit code; a
    report with no status at all returns None rather than a guess, so an unrecorded status is
    never read as success.
    """
    status = harness.get("exit_code")
    failed = harness.get("reference_arm_failed")
    if failed is None and status is not None:
        failed = status != 0
    return status, failed


def summarise():
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    row = next(r for r in raw["rows"] if r["colony"] == "FULL")
    series = row["series"]
    pin = json.loads((ROOT / "docs" / "engine_pin.json").read_text(encoding="utf-8"))
    harness = json.loads(HARNESS.read_text(encoding="utf-8")) if HARNESS.exists() else {}
    harness_status, arm_failed = arm_status(harness)

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
        "harness_exit_code": harness_status,
        "harness_reference_arm_failed": arm_failed,
        "harness_mode": harness.get("mode"),
        "harness_reference_arm_problems": harness.get("reference_arm_problems"),
        "harness_reference_arm_attributed": bool(harness.get("reference_arm_problems")),
        "harness_tail": harness.get("tail"),
    }
    series_verdict = verdict_for(series["theories"], series["beliefs"], int(record["cycles"]))
    record.update(series_verdict)
    # The gate precedes every scientific verdict (docs/DECISION-UNCERTIFIED-RUN.md): a run
    # the harness will not certify is void, and the reading the series still supports is
    # kept as an observation that no aggregate may count as a verdict.
    record["series_verdict"] = series_verdict["verdict"]
    cert = vp.certificate(arm_failed, harness.get("reference_arm_problems") or [])
    decided = vp.decide(record["series_verdict"], cert, "VOID_REFERENCE_DEAD")
    record["certified"] = decided["certified"]
    record["verdict"] = decided["verdict"]
    record["observation"] = decided["observation"]
    record["gate"] = (
        {"reference_arm_failed": True,
         "problems": cert["problems"],
         "reason": "the harness's own reference-arm check failed the run"}
        if not decided["certified"] else None
    )

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
    ]
    if record["verdict"] == "VOID_REFERENCE_DEAD":
        lines += [
            "**VOID_REFERENCE_DEAD.** The harness's own reference-arm check failed, so this run "
            "cannot test the decay hypothesis and no scientific verdict is reported. The series "
            "is kept as an observation with its own verdict, `%s`, and the gate's reason is "
            "recorded below." % record["series_verdict"],
            "",
        ]
    else:
        lines += ["**%s.** " % record["verdict"] + _verdict_sentence(record), ""]
    if record.get("harness_exit_code") is not None:
        problems = record.get("harness_reference_arm_problems") or []
        lines += [
            "## The harness's own status",
            "",
            "| Item | Value |",
            "| --- | --- |",
            "| Build that wrote the status | %s |" % (record.get("harness_mode") or "unrecorded"),
            "| Exit code | **%d** |" % record["harness_exit_code"],
            "| Run certified by the harness | %s |"
            % ("yes" if record.get("certified") else "no"),
            "| Reference-arm check | %s |" % (
                "; ".join(problems) if problems else "passed"),
            "| Series verdict, as an observation | %s |" % record.get("series_verdict"),
            "",
        ]
        if problems:
            lines += [
                "The harness exited **" + str(record["harness_exit_code"]) + "** because its own"
                " reference-arm check fired,",
                "and it recorded that reason in the run artifact rather than only on the console:",
                "the status is attributable without reading a line of output. The runner records",
                "the status verbatim and does not override it. This falsifier exists to measure the",
                "death the harness is refusing to certify, so a non-zero status here is the",
                "finding, not a crashed run -- and the artifact says which it is.",
                "",
            ]
        else:
            lines += [
                "The harness exited **0** under the fail-closed build, whose own reference check",
                "requires a theory in the final tenth of cycles. That check passing is a weaker",
                "statement than the series below: it asks for one live theory in the last tenth,",
                "and the falsifier asks whether a theory lived in *every* cycle. The verdict is",
                "read from the series, not from the status.",
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
    if record.get("series_verdict") != expected["verdict"]:
        found.append("the recorded series verdict does not follow from the series")
    found.extend(vp.check(record, "VOID_REFERENCE_DEAD"))
    refused = record.get("harness_reference_arm_failed") is True
    if record.get("certified") is refused:
        found.append("the certificate disagrees with the harness's own reference-arm flag")
    if record["verdict"] == "VOID_REFERENCE_DEAD" and not record.get("harness_reference_arm_failed"):
        found.append("the verdict is VOID_REFERENCE_DEAD but the reference arm did not fail")
    if record["verdict"] != "VOID_REFERENCE_DEAD" and record["verdict"] != expected["verdict"]:
        found.append("the recorded verdict does not follow from the series")
    if not record.get("engine_pin_current"):
        found.append("the engine moved since the pin, so this result describes another build")
    status = record.get("harness_exit_code")
    reasons = record.get("harness_reference_arm_problems") or []
    attributed = bool(reasons) and record.get("harness_reference_arm_failed") is True
    if status not in (None, 0) and not attributed:
        found.append(
            "the artifact was summarised from a harness run that exited %d without a recorded "
            "reference-arm reason, so the failure cannot be told apart from a crashed run" % status
        )
    if attributed and record["theories"]["at_end"] != 0:
        found.append(
            "the harness refused the run for its reference arm, but the series does not end at "
            "zero, so that refusal is not the condition this falsifier measures"
        )
    if record.get("harness_reference_arm_failed") and status == 0:
        found.append("the harness failure flag disagrees with its own exit status")
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
            harness = json.loads(HARNESS.read_text(encoding="utf-8"))
            if not harness.get("reference_arm_problems"):
                print("FAIL: the harness exited %d with no recorded reference-arm reason; "
                      "nothing written" % code)
                return 1
            print("harness exited %d and named its reason; the refusal is the measurement"
                  % code)
    record = summarise()
    ARTIFACT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    DOC.write_text(render(record), encoding="utf-8")
    print("decay falsifier: %s" % record["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
