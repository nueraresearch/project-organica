"""The action plan's figures must be the artifacts' figures.

The plan is prose, but every number in it is a restatement of a measured record. This is the
same defect rule 27 names: a document that restates an artifact is a new claim and needs a
mechanical check against it. `missing()` is that check, and the second test proves it can fail.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs/ACTION-PLAN.md"
PREFLIGHT = ROOT / "docs/tier1_preflight.json"
SURVIVAL = ROOT / "docs/question_survival.json"
PRUNING = ROOT / "docs/pruning_by_type.json"
RERUN = ROOT / "docs/RERUN-CAMPAIGN-PLAN.md"


def _fragments():
    pre = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    sur = json.loads(SURVIVAL.read_text(encoding="utf-8"))
    pru = json.loads(PRUNING.read_text(encoding="utf-8"))
    engine = pru["arms"]["engine"]
    witness = pre["witness"]
    persistence = pre["persistence"]
    older = [r for r in sur["questions"] if r["state"] == "answered-older-build"]
    held = [r for r in sur["questions"] if r["state"] == "governance-held"]
    gated = [r for r in sur["questions"] if r["state"] == "prerequisite"]
    open_ev = [r for r in sur["questions"] if r["state"] == "open-with-evidence"]
    at_pin = [r for r in sur["questions"] if r["state"] == "answered-at-pin"]
    first_zero = ("first zero at cycle %d" % persistence["first_zero_cycle"]
                  if persistence["first_zero_cycle"] is not None else "no first zero")
    return [
        "%d of %d cycles" % (witness["reference_theory_cycles"], witness["cycles"]),
        "%d of %d" % (sur["evidence"]["named_build"], sur["evidence"]["json_refs"]),
        first_zero,
        "%d-cycle horizon" % persistence["horizon"],
        "%d open + %d future = %d" % (sur["populations"]["open"],
                                      sur["populations"]["future"],
                                      sur["populations"]["reviewed"]),
        "%d carry an answer" % len(older),
        "%d are governance-held" % len(held),
        "%d are prerequisite-gated" % len(gated),
        "%d are open with evidence" % len(open_ev),
        "%d are answered at the pin" % len(at_pin),
        "%d peak edges" % engine["peak_edges"],
        "%d end in a pruned terminal" % engine["terminal"]["pruned"],
        "{:,} prediction candidates".format(
            engine["retired_by_type"]["prediction_candidate"]),
        "12 re-derivations",
        "12 of 12 name a preregistration",
    ]


def _flat(text):
    """Strip emphasis and thousands separators so a figure is compared, not its styling."""
    return text.replace("*", "").replace("`", "").replace(",", "")


def missing(text=None):
    """The plan fragments the artifacts do not support. Empty means every figure traces."""
    text = PLAN.read_text(encoding="utf-8") if text is None else text
    flat = _flat(text)
    return [fragment for fragment in _fragments() if _flat(fragment) not in flat]


def test_the_plan_restates_only_figures_the_artifacts_hold():
    problems = missing()
    assert problems == [], "the action plan states figures the artifacts do not support: %r" % (
        problems,)


def test_the_check_can_fail():
    text = PLAN.read_text(encoding="utf-8").replace("105 peak edges", "106 peak edges")
    assert "106 peak edges" in text
    assert missing(text)


def test_the_plan_states_the_measured_population():
    text = PLAN.read_text(encoding="utf-8")
    survival = json.loads(SURVIVAL.read_text(encoding="utf-8"))
    assert "%d open" % survival["populations"]["open"] in _flat(text)
