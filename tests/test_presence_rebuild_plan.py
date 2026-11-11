"""The rebuild plan must state the three verdicts it would re-derive, and the artifacts must agree.

The plan is prose about measurements, so every figure in it is a restatement of a record (rule 27):
the block's current verdict, its seeds, and the verdict set its own decision table can return. This
guard reads those from the artifacts and the frozen pre-registrations, and fails when the plan
drifts from them. Its control proves the comparison can fail.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs/PRESENCE-REBUILD-PLAN.md"
CONSTRUCT_RUN = ROOT / "docs/presence_construct_audit_run.json"
CAP_RUN = ROOT / "docs/presence_cap_run.json"
AUDIT = ROOT / "docs/presence_assertion_audit_0.14.0.json"
CONSTRUCT_PREREG = ROOT / "docs/presence_construct_audit_prereg.json"
CAP_PREREG = ROOT / "docs/presence_cap_prereg.json"

# The comparator's verdict is computed by `presence_assertion_audit._verdict`, whose three returns
# are literals in that module. They are listed here rather than imported so this guard reads only
# records and does not run a harness.
AUDIT_VERDICTS = ("PRESENCE NOT FULL", "PRESENCE NOT ASSERTION", "PRESENCE AND ASSERTION COINCIDE")

# What the plan must say about its own state, because a reader will otherwise assume a run.
STATE = ("no rebuild has run", "not authorised")


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _decisions(path: Path) -> set[str]:
    body = _json(path)
    return {row["verdict"] for row in body["decision_table"]}


def _seeds(prereg: dict) -> list[int]:
    return list(prereg["design"]["seeds"])


def missing(text: str | None = None) -> list[str]:
    """The plan's claims the records do not support. Empty means every figure traces."""
    text = PLAN.read_text(encoding="utf-8") if text is None else text
    found: list[str] = []
    if not PLAN.exists():
        return ["the plan does not exist"]

    for path, verdict in ((CONSTRUCT_RUN, None), (CAP_RUN, None), (AUDIT, None)):
        body = _json(path)
        if body.get("verdict") not in text:
            found.append("%s: the plan does not state its verdict %r"
                         % (path.name, body.get("verdict")))
        if path.name not in text:
            found.append("the plan does not name %s" % path.name)

    for verdict in _decisions(CONSTRUCT_PREREG) | _decisions(CAP_PREREG) | set(AUDIT_VERDICTS):
        if verdict not in text:
            found.append("the plan does not state the reachable verdict %r" % verdict)

    for prereg in (CONSTRUCT_PREREG, CAP_PREREG):
        for seed in _seeds(_json(prereg)):
            if str(seed) not in text:
                found.append("%s: the plan does not name seed %d" % (prereg.name, seed))

    for phrase in STATE:
        if phrase not in text:
            found.append("the plan does not say %r" % phrase)
    if "engine_lineage.json" not in text:
        found.append("the plan does not say the split is already carried by the lineage record")
    return found


def test_the_plan_states_the_verdicts_seeds_and_reachable_sets_the_records_hold():
    problems = missing()
    assert problems == [], "the rebuild plan states figures the records do not support: %r" % (
        problems,)


def test_the_check_can_fail():
    # A seed, not a verdict prefix: "CONSTRUCT VALIDITY" still contains "CONSTRUCT VALID", and a
    # control that cannot trip is the defect it is supposed to catch.
    text = PLAN.read_text(encoding="utf-8").replace("20611406", "20611407")
    assert "20611407" in text
    assert missing(text)
