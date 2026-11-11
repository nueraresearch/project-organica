"""The plan from the landed 0.15.0 build to a runnable cap-112 admission arm.

0.15.0 landed on 2026-11-11, so this is not a landing checklist: it is the plan for the arm the
landing was needed for. Each step carries what it needs and what still blocks it, and the states
are derived from the records rather than typed -- a drift in the version, the pin, the canaries,
the three cap-112 records, the runner's preflight or the presence of a result artifact turns the
check red instead of leaving a stale plan looking current.

The plan is a plan. It runs no cell, and the decision it serves stays PENDING until the arm's
verdict exists.

    ./.venv/bin/python -m benchmarks.cap112_admission_plan --write
    ./.venv/bin/python -m benchmarks.cap112_admission_plan --check
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks import presence_cap112_runners as runners

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ARTIFACT = DOCS / "cap112_admission_plan.json"
PAGE = DOCS / "CAP112-ADMISSION-PLAN.md"
PIN = DOCS / "engine_pin.json"
CANARIES = DOCS / "block_canaries.json"
DECISION = DOCS / "DECISION-ADMISSION-STEP.md"
LANDING = DOCS / "LANDING-0.15.0.md"
KIND = "cap112_admission_plan"
TARGET_VERSION = "0.15.0"
TARGET_CAP = 112
PIN_FILES = 14
RECORDS = ("presence_comparator_112_prereg.json", "presence_construct_1_112_prereg.json",
           "presence_cap_1_112_prereg.json")
BAND_RECORD = DOCS / "presence_band_rank_prereg.json"
BAND_RUN = DOCS / "presence_band_rank_run.json"
ARTIFACTS = {
    "comparator": DOCS / "presence_comparator_112_run.json",
    "Q1": DOCS / "presence_construct_1_112_run.json",
    "Q2": DOCS / "presence_cap_1_112_run.json",
}
ACCEPTANCE = "21\u201340 transitions must be served at 112"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def live() -> dict:
    from organica import __version__
    from organica.sleep import SleepService

    pin = load(PIN)
    canaries = load(CANARIES)
    decision = DECISION.read_text(encoding="utf-8")
    landing = LANDING.read_text(encoding="utf-8")
    return {
        "version": __version__,
        "cap": int(SleepService.MAX_PREDICTIONS),
        "pin_version": str(pin.get("version")),
        "pin_files": len(pin.get("files") or {}),
        "canaries_version": canaries.get("engine_version"),
        "records": {
            name: {
                "status": (load(DOCS / name).get("status")),
                "granted": bool((load(DOCS / name).get("authorisation") or {})
                                .get("granted")),
                "runner": (load(DOCS / name).get("runner") or {}).get("status"),
            } for name in RECORDS},
        "preflight": runners.preflight(),
        "artifacts": {name: path.exists() for name, path in ARTIFACTS.items()},
        "band": {"granted": bool((load(BAND_RECORD).get("authorisation") or {}).get("granted")),
                 "runner": bool((load(BAND_RECORD).get("runner") or {}).get("built")),
                 "artifact": BAND_RUN.exists()},
        "decision": {"pending": "PENDING" in decision, "acceptance": ACCEPTANCE in decision},
        "landing": "LANDED" in landing,
    }


def steps(state: dict) -> list[dict]:
    landed = (state["version"] == TARGET_VERSION and state["cap"] == TARGET_CAP
              and state["pin_version"] == TARGET_VERSION and state["pin_files"] == PIN_FILES
              and state["canaries_version"] == TARGET_VERSION and state["landing"])
    frozen = all(record["status"] in {"FROZEN, NOT RUN", "FROZEN, RUN"}
                 and record["granted"]
                 and record["runner"] == "built" for record in state["records"].values())
    runners_ready = state["preflight"] == [] and (ROOT / "benchmarks" /
                                                  "presence_cap112_runners.py").exists()
    comparator_done = state["artifacts"]["comparator"]
    q2_done = state["artifacts"]["Q2"]
    runner_block = [] if runners_ready else ["an empty runner preflight"]
    comparator_blocked = [] if comparator_done else [
        "the comparator-112 rows (Q2's finish reads them for the K gates)"]
    arm_blocked = ([] if q2_done else runner_block + comparator_blocked)
    band = state["band"]
    band_done = band["artifact"]
    band_blocked = [] if band_done or (band["granted"] and band["runner"]) else ["a dated grant for the band arm"]
    return [
        {"id": "land", "state": "done" if landed else "blocked",
         "needs": ("version 0.15.0 in the three declarations; the Layer-1 cap 112; a "
                   "fourteen-file pin at 0.15.0; canaries re-recorded on those bytes"),
         "blocked_by": [] if landed else ["the 0.15.0 landing"]},
        {"id": "frozen-records", "state": "done" if frozen else "blocked",
         "needs": ("the comparator, Q1 and Q2 records FROZEN (RUN or NOT RUN), granted, with their "
                   "runners built"),
         "blocked_by": [] if frozen else ["a frozen, granted record with a built runner"]},
        {"id": "runner-preflight", "state": "done" if runners_ready else "blocked",
         "needs": ("benchmarks/presence_cap112_runners.py, its preflight empty on the installed "
                   "build, and its self-test green"),
         "blocked_by": [] if runners_ready else ["an empty runner preflight"]},
        {"id": "comparator-112", "state": "done" if comparator_done else (
            "blocked" if runner_block else "ready"),
         "needs": ("`--measure --block comparator` on the six audit seeds, then "
                   "`--finish --block comparator`; this is the row Q1's C9 anchors to"),
         "blocked_by": [] if comparator_done else runner_block},
        {"id": "admission-arm", "state": "done" if q2_done else (
            "waiting" if arm_blocked else "ready"),
         "needs": ("`--measure --block Q2` on six seeds \u00d7 four levels (24 cells) plus the "
                   "112 witness, then `--finish --block Q2`; the acceptance condition is that "
                   "the 21\u201340 transitions are served at 112, per seed, with K1\u2013K6 "
                   "passing"),
         "blocked_by": arm_blocked},
        {"id": "verdict", "state": "done" if q2_done else "blocked",
         "needs": ("the arm's 24 cells, its witness and the Q2 verdict rule, read against the "
                   "bar the cap-40 record fixes"),
         "blocked_by": [] if q2_done else ["the admission arm's cells and witness"]},
        {"id": "band-arm", "state": "done" if band_done else ("blocked" if band_blocked else "ready"),
         "needs": ("record a dated grant for PRESENCE-BAND-1, then `--measure` and `--finish`; the "
                   "band arm reads the 62 named rank-21-40 edges at 40 and 112 on Q4's six worlds "
                   "and is the decision's designated test"),
         "blocked_by": [] if band_done else band_blocked},
        {"id": "decision", "state": "blocked",
         "needs": ("the band arm's verdict (recorded: VOID on B5), then the owner updates the "
                   "PENDING admission-step decision with a date and a rationale"),
         "blocked_by": ["the owner's update of the PENDING decision"]},
    ]


def summary(rows: list[dict]) -> dict:
    """What the arm waits on, kept apart from what waits on the arm."""
    arm = rows[4]
    band = next(row for row in rows if row["id"] == "band-arm")
    later = sorted({item for row in rows[5:] for item in row["blocked_by"]})
    return {"landing": "done" if rows[0]["state"] == "done" else "blocked",
            "arm": arm["state"], "arm_blockers": list(arm["blocked_by"]),
            "band": band["state"], "band_blockers": list(band["blocked_by"]),
            "later_blockers": later}


def build(state: dict | None = None) -> dict:
    state = live() if state is None else state
    rows = steps(state)
    return engine_stamp.stamp({
        "kind": KIND,
        "not_a_result": True,
        "question": ("What does the landed 0.15.0 build still need before the cap-112 admission "
                     "arm can run, and what blocks each remaining step?"),
        "build": {"version": state["version"], "cap": state["cap"],
                  "pin_version": state["pin_version"], "pin_files": state["pin_files"],
                  "canaries_version": state["canaries_version"]},
        "records": state["records"],
        "preflight": state["preflight"],
        "decision": {"status": "PENDING" if state["decision"]["pending"] else "CHANGED",
                     "acceptance": ACCEPTANCE},
        "steps": rows,
        "summary": summary(rows),
        "not_evidence": ("A plan is not a run. No cell was started, no verdict is adjudicated, "
                         "and the admission-step decision stays PENDING until the arm's verdict "
                         "exists."),
    })


def problems(art: dict | None = None, live_state: dict | None = None) -> list[str]:
    art = load(ARTIFACT) if art is None else art
    state = live() if live_state is None else live_state
    found: list[str] = []
    if art.get("kind") != KIND:
        found.append("artifact kind")
    if art.get("not_a_result") is not True:
        found.append("the plan does not say it is not a result")
    expected = steps(state)
    got = art.get("steps") or []
    if len(got) != len(expected):
        found.append("the plan has %d steps, the state derives %d" % (len(got), len(expected)))
    for row, want in zip(got, expected):
        if row != want:
            found.append("step %r does not match the landed state: %r"
                         % (want["id"], {key: row.get(key) for key in ("state", "blocked_by")}))
    if art.get("build") != build(state)["build"]:
        found.append("the build block does not match the installed build")
    if art.get("summary") != summary(expected):
        found.append("the summary does not match the derived steps")
    if art.get("decision") != build(state)["decision"]:
        found.append("the decision block does not match the record")
    if not state["decision"]["acceptance"]:
        found.append("the decision does not state the acceptance condition")
    if not state["decision"]["pending"]:
        found.append("the decision is no longer PENDING")
    return found


def render(art: dict) -> str:
    build_row = art["build"]
    lines = [
        "# Plan: the cap-112 admission arm on the landed 0.15.0 build",
        "",
        "Generated from `docs/cap112_admission_plan.json` by "
        "`python -m benchmarks.cap112_admission_plan --write`. Do not edit by hand.",
        "",
        "**Status: %s.** 0.15.0 landed on 2026-11-11, so the landing checklist is a record, not "
        "a to-do list (`docs/LANDING-0.15.0.md`). This plan covers the arm the landing was "
        "needed for: what each remaining step needs, and what still blocks it." % (
            "ARM RUNNABLE" if art["summary"]["arm"] == "ready" else
            "ARM WAITING ON THE COMPARATOR" if art["summary"]["arm"] == "waiting" else
            "ARM DONE" if art["summary"]["arm"] == "done" else "BLOCKED"),
        "",
        "**Not a result.** No cell has run; the decision stays **%s**, and the acceptance "
        "condition is *%s*, per seed, with the block's gates passing." % (
            art["decision"]["status"], art["decision"]["acceptance"]),
        "",
        "## The landed build",
        "",
        "| Item | Value |",
        "| --- | --- |",
        "| Package version | `%s` |" % build_row["version"],
        "| Layer-1 cap | `%d` |" % build_row["cap"],
        "| Pin | `%s` over `%d` files |" % (build_row["pin_version"], build_row["pin_files"]),
        "| Canaries | `%s` |" % build_row["canaries_version"],
        "| Runner preflight | %s |" % ("empty" if not art["preflight"] else
                                       "`%s`" % "; ".join(art["preflight"])),
        "",
        "## Steps, needs and blockers",
        "",
        "| # | Step | State | Needs | Blocked by |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for index, row in enumerate(art["steps"], start=1):
        lines.append("| %d | `%s` | **%s** | %s | %s |" % (
            index, row["id"], row["state"].upper(), row["needs"],
            "; ".join(row["blocked_by"]) if row["blocked_by"] else "nothing"))
    lines += [
        "",
        "`done` is derived from the records; `ready` means its prerequisites hold now; "
        "`waiting` means it can be measured but not finished until the named artifact exists; "
        "`blocked` means it follows a measurement.",
        "",
        "## What still blocks the arm",
        "",
    ]
    if art["summary"]["arm_blockers"]:
        lines.append("The arm itself waits on: %s." % "; ".join(
            art["summary"]["arm_blockers"]))
    else:
        lines.append("**Nothing.** The landing, the frozen records and the runner preflight are "
                     "all satisfied, and the arm's result artifact does not yet exist.")
    lines += ["", "The steps after the arm wait on the recorded verdict, then on the owner: %s." % (
        "; ".join(art["summary"]["later_blockers"]) or "nothing")]
    lines += [
        "",
        "The arm is the **admission** question, not the comparator: Q2 varies only the Layer-1 "
        "cap across 40 / 80 / 112 / uncapped on the same six seeds and worlds, with a witness "
        "at 112. The comparator-112 is a dependency, because Q2's finish reads its rows for the "
        "K gates and Q1's C9 anchors to it; it is not the arm's own test.",
        "",
        "## The decision's designated test",
        "",
        "The acceptance condition is read on `PRESENCE-BAND-1` (`docs/presence_band_rank_prereg.json`), "
        "the 62 named rank-21-40 edges at 40 and 112 on Q4's six worlds. The step is **%s**%s."
        % (art["summary"]["band"].upper(),
           "" if not art["summary"]["band_blockers"] else
           " and waits on " + "; ".join(art["summary"]["band_blockers"])),
        "",
        "## Commands, in order",
        "",
        "```",
        "python -m benchmarks.presence_cap112_runners --check        # preflight, no cell",
        "python -m benchmarks.presence_cap112_runners --self-test     # gates and verdict rules",
        "python -m benchmarks.presence_cap112_runners --measure --block comparator",
        "python -m benchmarks.presence_cap112_runners --finish  --block comparator",
        "python -m benchmarks.presence_cap112_runners --measure --block Q2",
        "python -m benchmarks.presence_cap112_runners --finish  --block Q2",
        "python -m benchmarks.presence_band_rank_arm --check             # preflight, no cell",
        "python -m benchmarks.presence_band_rank_arm --self-test",
        "python -m benchmarks.presence_band_rank_arm --measure           # REFUSED until granted",
        "python -m benchmarks.presence_band_rank_arm --finish",
        "```",
        "",
        "A single cell can be opened with `--cell --block Q2 --seed <seed> --cap <level>`; the "
        "parts are cached, so an interrupted measure resumes without re-running a cell.",
        "",
        "## What this does not do",
        "",
        "- It does not run a cell, adjudicate a verdict or promote the PENDING decision.",
        "- It does not re-derive Q1 or Q2's design, gates, seeds or verdict rules; they are "
        "frozen and cited, not restated as new commitments.",
        "- It does not claim 112 is necessary or optimal: the arm tests whether the 21\u201340 "
        "transitions are served, and a negative result moves the next step to the admission "
        "rule rather than to another level.",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def check() -> int:
    if not ARTIFACT.exists():
        print("FAIL: no artifact; run --write")
        return 1
    art = load(ARTIFACT)
    found = problems(art)
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != render(art):
        found.append("the page is stale against the artifact")
    for problem in found:
        print("FAIL:", problem)
    if not found:
        print("cap-112 admission plan: landing done, arm %s, %d step(s) blocked"
              % (art["summary"]["arm"], sum(1 for row in art["steps"]
                                            if row["state"] in ("blocked", "waiting"))))
    return 1 if found else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        art = build()
        ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
        PAGE.write_text(render(art), encoding="utf-8")
        print("wrote %s and %s" % (ARTIFACT.relative_to(ROOT), PAGE.relative_to(ROOT)))
        return 0
    if args.check or not argv:
        return check()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
