"""The plan must match the landed state, and must go red when the state or the plan drifts."""
LAYER = "static"  # benchmarks/test_layers.py: reads records, runs no cell

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import cap112_admission_plan as plan  # noqa: E402


def artifact() -> dict:
    return json.loads(plan.ARTIFACT.read_text(encoding="utf-8"))


def test_the_plan_matches_the_landed_state():
    art = artifact()

    assert plan.problems(art) == []
    assert art["not_a_result"] is True
    assert art["build"]["version"] == "0.15.0"
    assert art["build"]["cap"] == 112
    assert art["preflight"] == []
    states = {row["id"]: row["state"] for row in art["steps"]}
    assert states["land"] == "done"
    assert states["frozen-records"] == "done"
    assert states["runner-preflight"] == "done"
    assert states["comparator-112"] in ("ready", "done")
    assert states["admission-arm"] in ("ready", "waiting", "done")
    assert states["band-arm"] == "done"
    assert states["decision"] == "blocked"
    assert art["summary"]["band"] == "done"
    assert states["decision"] == "blocked"
    assert art["summary"]["later_blockers"] == ["the owner's update of the PENDING decision"]
    assert plan.PAGE.read_text(encoding="utf-8") == plan.render(art)


def test_a_pre_landing_build_is_rejected():
    live = copy.deepcopy(plan.live())
    live["version"] = "0.14.0"
    live["cap"] = 40

    assert plan.problems(live_state=live), "a plan for 0.15.0 must fail on the 0.14.0 build"


def test_a_tampered_step_state_is_rejected():
    bad = copy.deepcopy(artifact())
    bad["steps"][0]["state"] = "blocked"

    assert plan.problems(bad), "a step that disagrees with the records must fail"


def test_a_granted_band_record_turns_the_step_ready():
    live = copy.deepcopy(plan.live())
    live["band"] = {"granted": True, "runner": True, "artifact": False}

    row = [item for item in plan.steps(live) if item["id"] == "band-arm"][0]
    assert row["state"] == "ready" and row["blocked_by"] == []
