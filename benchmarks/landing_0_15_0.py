"""The 0.15.0 landing: what the checklist required, and the build it produced.

The checklist is a procedure, not a result. It was written before the landing and is now the
record of one: it quotes both the state it departed from and the state it produced, and every
figure is derived from the pin, the canary record, the version declarations and the three
cap-112 records. A drift in any of them turns this check red rather than leaving a stale
procedure looking current.

    ./.venv/bin/python -m benchmarks.landing_0_15_0 --check
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "LANDING-0.15.0.md"
PIN = ROOT / "docs" / "engine_pin.json"
CANARIES = ROOT / "docs" / "block_canaries.json"
DRAFTS = ("presence_comparator_112_prereg.json", "presence_construct_1_112_prereg.json",
          "presence_cap_1_112_prereg.json")
REQUIRED = ("## Preconditions", "## 1. Bump", "## 2. Change the cap", "## 3. Re-pin",
            "## 4. Re-record", "## 5. Attribute", "## 6. Bring the frozen", "## 7. Verify",
            "## Stop conditions", "## Rollback", "## What this does not do")
COMMANDS = ("benchmarks.engine_pin", "benchmarks.block_canaries --write", "pytest tests",
            "benchmarks.engine_lineage --check", "benchmarks.presence_cap112_prereg --check",
            "benchmarks.test_count")
# The 0.14.0 digests the checklist quoted before it ran. They are preserved here on purpose:
# docs/block_canaries.json now holds the 0.15.0 rows, so this is the only record of the departure.
PRE_LANDING = {
    "PRESENCE-CAP-1": "a32ae3bc3d00dd4fc54a39f3a5629d1f237b900944c9a96e32a2685ad2b70f8d",
    "PRESENCE-CONSTRUCT-1": "c2388cfe9e784bc24fbc851acd62b6301fb1c1a2af2ec3c593a8d6b251ba73ad",
    "PRESENCE-CONVERSION-1": "87c6af27aec428c60587894667d16bad9a3e8d910d9f11189149b85bc9f95739",
    "PRESENCE-CONVERSION-2": "f8ead12b63221c9db5b261b7969f8797b4ceb4ad1b44d67cce415b8036972aca",
}


def state() -> dict:
    from organica import __version__
    from organica.sleep import SleepService
    pin = json.loads(PIN.read_text(encoding="utf-8"))
    canaries = json.loads(CANARIES.read_text(encoding="utf-8"))
    drafts = [json.loads((ROOT / "docs" / name).read_text(encoding="utf-8")) for name in DRAFTS]
    return {"version": __version__, "cap": int(SleepService.MAX_PREDICTIONS), "pin": pin,
            "canaries": canaries, "drafts": drafts}


def problems(text: str | None = None, live: dict | None = None) -> list[str]:
    text = DOC.read_text(encoding="utf-8") if text is None else text
    live = state() if live is None else live
    found: list[str] = []
    if "**Status: LANDED**" not in text:
        found.append("the checklist does not record the landing as landed")
    for heading in REQUIRED:
        if heading not in text:
            found.append("missing section: %s" % heading)
    for command in COMMANDS:
        if command not in text:
            found.append("the checklist does not name `%s`" % command)
    for module in set(re.findall(r"benchmarks\.([a-z0-9_]+)", text)):
        if not (ROOT / "benchmarks" / (module + ".py")).exists():
            found.append("the checklist names a missing module: benchmarks.%s" % module)
    if live["version"] != "0.15.0" or live["cap"] != 112:
        found.append("the landed state is no longer the one this record describes: version %r, "
                     "cap %r" % (live["version"], live["cap"]))
    if str(live["pin"].get("version")) != "0.15.0" or len(live["pin"]["files"]) != 14:
        found.append("the pin is not the landed 0.15.0 pin of 14 files")
    if live["canaries"].get("engine_version") != "0.15.0":
        found.append("the canary record is not from 0.15.0")
    for block, cell in live["canaries"]["cells"].items():
        if cell["digest"] not in text:
            found.append("the landed %s digest is not quoted" % block)
    for block, digest in PRE_LANDING.items():
        if digest not in text:
            found.append("the pre-landing %s digest is not preserved" % block)
    for draft in live["drafts"]:
        name = draft["prereg"]
        if draft["status"] == "FROZEN, RUN":
            result = draft.get("result") or {}
            artifact = result.get("artifact")
            if draft.get("no_cells_run") is not False or not artifact or not (
                    ROOT / artifact).exists() or not result.get("verdict"):
                found.append("%s claims a run with no complete result" % name)
        elif draft["status"] == "FROZEN, NOT RUN":
            if draft.get("result") is not None:
                found.append("%s carries a result while unrun" % name)
        else:
            found.append("%s is not frozen" % name)
        if not draft["authorisation"]["granted"]:
            found.append("%s carries no grant" % name)
        if draft["runner"]["status"] != "built":
            found.append("%s does not record its built runner" % name)
        elif not draft["runner"].get("module") or not (
                ROOT / draft["runner"]["module"]).exists():
            found.append("%s names a runner module that does not exist" % name)
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args(argv)
    found = problems()
    for problem in found:
        print("FAIL:", problem)
    if found:
        return 1
    print("landing 0.15.0: landed, quotes both builds, names live commands")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
