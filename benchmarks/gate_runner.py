"""Run the repository's non-suite gates and print one pass/fail summary.

This is deliberately not a test runner. It invokes the existing ``--check``
entry points in subprocesses, preserves each command's own output and exit
status, and fails if any one of them fails. It runs no engine cell and writes
no file.

    python -m benchmarks.gate_runner            # run every gate, one summary
    python -m benchmarks.gate_runner --list     # show the commands, run none

The gate set is the engine pin, D3-1 through D3-4, D2's pre-flight, the presence/assertion audit,
the presence-to-assertion ladder, the presence-cap preregistration, the research registry,
research accountability and the decision graph. D2 is checked
with ``--require-pass`` so a consistent page that records a blocked campaign fails the gate.
D3-4 is checked with ``--check`` against its completed run artifact, and so are the audit's
stamped artifact and page and the ladder trace.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: (display name, module, arguments). Keep this ordered: the summary follows it.
GATES = (
    ("engine pin", "benchmarks.engine_pin", ("--check",)),
    ("D3-1 persistence prereg", "benchmarks.d3_persistence_prereg", ("--check",)),
    ("D3-2 seed-varying record", "benchmarks.d3_persistence_seed_varying", ("--check",)),
    ("D3-3 engine replication record", "benchmarks.d3_persistence_engine_replication",
     ("--check",)),
    ("D3-4 G1 recalibrated run", "benchmarks.d3_persistence_g1_recalibrated",
     ("--check",)),
    ("D2 pre-flight", "benchmarks.tier1_preflight", ("--check", "--require-pass")),
    ("presence/assertion audit", "benchmarks.presence_assertion_audit", ("--check",)),
    ("presence->assertion ladder", "benchmarks.presence_assertion_ladder", ("--check",)),
    ("presence cap prereg", "benchmarks.presence_cap_experiment", ("--check-prereg",)),
    ("research registry", "benchmarks.research_registry", ("--check",)),
    ("research accountability", "benchmarks.research_accountability", ("--check",)),
    ("decision graph", "benchmarks.decision_graph", ("--check",)),
)


def command(module: str, args: tuple[str, ...]) -> list[str]:
    """The executable command for one gate, run from the repository root."""
    return [sys.executable, "-m", module, *args]


def run_gate(gate, timeout: float = 180.0) -> dict:
    """Run one gate in its own process and return its status and output."""
    name, module, args = gate
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            command(module, args),
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout, stderr = proc.stdout or "", proc.stderr or ""
        returncode = proc.returncode
        error = None
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        returncode = None
        error = "timed out after %.0fs" % timeout
    except OSError as exc:
        stdout, stderr = "", str(exc)
        returncode = None
        error = "could not start the gate"
    return {
        "name": name,
        "module": module,
        "args": args,
        "passed": returncode == 0,
        "returncode": returncode,
        "seconds": time.perf_counter() - started,
        "stdout": stdout,
        "stderr": stderr,
        "error": error,
    }


def show(result: dict) -> None:
    """Print one gate's own output, without rewriting its verdict."""
    print("\n" + "=" * 78)
    print("%s  %s  (%.2fs)" % (
        "PASS" if result["passed"] else "FAIL", result["name"], result["seconds"]))
    if result["error"]:
        print(result["error"])
    if result["stdout"].strip():
        print(result["stdout"].rstrip())
    if result["stderr"].strip():
        print("stderr:")
        print(result["stderr"].rstrip())


def summarize(results: list[dict]) -> int:
    """Print the single overall verdict and return the runner's exit code."""
    failed = [result for result in results if not result["passed"]]
    print("\n" + "=" * 78)
    print("GATE SUMMARY")
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        detail = ""
        if not result["passed"]:
            if result["returncode"] is not None:
                detail = " (exit %d)" % result["returncode"]
            elif result["error"]:
                detail = " (%s)" % result["error"]
        print("  %-4s %s%s" % (status, result["name"], detail))
    print("\n%d of %d gates passed." % (len(results) - len(failed), len(results)))
    print("RESULT: %s" % ("PASS" if not failed else "FAIL"))
    return 0 if not failed else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true",
                        help="show the gate commands without running them")
    parser.add_argument("--timeout", type=float, default=180.0,
                        help="per-gate timeout in seconds (default: 180)")
    args = parser.parse_args(argv)

    if args.list:
        for name, module, gate_args in GATES:
            print("%-30s %s" % (name, " ".join(command(module, gate_args))))
        return 0

    results = [run_gate(gate, args.timeout) for gate in GATES]
    for result in results:
        show(result)
    return summarize(results)


if __name__ == "__main__":
    raise SystemExit(main())
