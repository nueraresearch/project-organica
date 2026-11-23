"""Fail CI if the G9 stage-ledger validator step is removed or weakened.

The validator step is part of the test job, not a detached report. A silent edit
that deletes it, comments it out, renames it, skips it with ``if: false`` or lets
it fail with ``continue-on-error: true`` would otherwise leave the workflow
green while the six-class validator stopped running.

    python -m benchmarks.g9_ci_guard --check
    python -m benchmarks.g9_ci_guard --self-test

The guard is intentionally standard-library only. It reads the workflow as
text and matches the YAML step block without importing a YAML parser.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
STEP_NAME = "G9 stage-ledger validator and six-class self-test"
COMMANDS = (
    "python -m benchmarks.g9_stage_ledger --check",
    "python -m benchmarks.g9_stage_ledger --self-test",
)
STEP = re.compile(
    r"^      - name: (?P<name>.+?)\n(?P<body>.*?)(?=^      - name: |\Z)",
    re.MULTILINE | re.DOTALL,
)


def steps(text: str) -> list[tuple[str, str]]:
    """Return ``(name, body)`` for every six-space-indented workflow step."""
    return [(match.group("name").strip(), match.group("body"))
            for match in STEP.finditer(text)]


def validator_problems(text: str) -> list[str]:
    """Why the workflow does not contain one fail-closed G9 validator step."""
    found: list[str] = []
    matches = [body for name, body in steps(text) if name == STEP_NAME]
    if not matches:
        return ["the G9 validator step is missing"]
    if len(matches) > 1:
        found.append("the G9 validator step appears more than once")
    body = matches[0]
    if not re.search(r"^\s+run:\s*(?:\||>)?\s*$", body, re.MULTILINE):
        found.append("the G9 validator step has no run block")
    if re.search(r"^\s+if:\s*(?:false|\$\{\{\s*false\s*\}\})", body,
                 re.MULTILINE | re.IGNORECASE):
        found.append("the G9 validator step is disabled with if: false")
    if re.search(r"^\s+continue-on-error:\s*(?:true|\$\{\{\s*true\s*\}\})\s*$",
                 body, re.MULTILINE | re.IGNORECASE):
        found.append("the G9 validator step permits failure with continue-on-error")
    lines = [line.strip() for line in body.splitlines()]
    for command in COMMANDS:
        if command not in lines:
            found.append("the G9 validator step is missing the exact command %r" % command)
    return found


def self_test() -> list[str]:
    """Prove the guard rejects the silent-removal shapes it claims to catch."""
    found: list[str] = []
    valid = (
        "      - name: Other\n"
        "        run: echo other\n"
        "      - name: %s\n"
        "        run: |\n"
        "          %s\n"
        "          %s\n"
    ) % (STEP_NAME, COMMANDS[0], COMMANDS[1])
    if validator_problems(valid):
        found.append("a valid G9 validator block is rejected: %r"
                     % validator_problems(valid))
    if not validator_problems(valid.replace("      - name: %s\n" % STEP_NAME, "")):
        found.append("a removed G9 validator step is accepted")
    renamed = valid.replace(STEP_NAME, "G9 validator (renamed)")
    if not validator_problems(renamed):
        found.append("a renamed G9 validator step is accepted")
    commented = valid.replace("          " + COMMANDS[0], "          # " + COMMANDS[0])
    if not any("exact command" in problem for problem in validator_problems(commented)):
        found.append("a commented-out G9 command is accepted")
    disabled = valid.replace(
        "      - name: %s\n" % STEP_NAME,
        "      - name: %s\n        if: false\n" % STEP_NAME,
    )
    if not any("if: false" in problem for problem in validator_problems(disabled)):
        found.append("a G9 step disabled with if: false is accepted")
    tolerant = valid.replace(
        "      - name: %s\n" % STEP_NAME,
        "      - name: %s\n        continue-on-error: true\n" % STEP_NAME,
    )
    if not any("continue-on-error" in problem for problem in validator_problems(tolerant)):
        found.append("a G9 step with continue-on-error: true is accepted")
    no_run = valid.replace("        run: |\n", "")
    if not any("no run block" in problem for problem in validator_problems(no_run)):
        found.append("a G9 step without a run block is accepted")
    duplicated = valid + valid.split("      - name: Other\n", 1)[1]
    if not any("more than once" in problem for problem in validator_problems(duplicated)):
        found.append("a duplicated G9 validator step is accepted")
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        found = self_test()
        for problem in found:
            print("FAIL:", problem)
        if not found:
            print("G9 CI guard self-test: pass")
        return 1 if found else 0

    if not WORKFLOW.exists():
        print("FAIL: the workflow is missing: %s" % WORKFLOW)
        return 1
    found = validator_problems(WORKFLOW.read_text(encoding="utf-8"))
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("G9 CI guard: pass; validator step present and fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
