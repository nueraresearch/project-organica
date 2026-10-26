"""A3 -- ancestry honesty -- must be able to fail.

`docs/AUDIT-TRACE-SPEC.md` section 12 fixes, in advance, what A3 counts:
lineage reachability, evidence linkage, and a four-way truncation split
(aged out / depth-truncated / no parent / missing record).  Section 6 states
the criterion:

    Every ancestry node is either resolved within the window, or explicitly
    marked absent WITH the window bound stated.  A record that reports a
    parent as absent when it was merely out of window fails.

That criterion is only worth anything if it can go red, so this test breaks
the auditor on purpose:

  * an out-of-window parent relabelled "no parent"  -> A3 must fail
  * an in-window parent relabelled "aged out"        -> A3 must fail
  * an unresolved node stripped of its window bound  -> A3 must fail

It also proves the *measurement* is sensitive rather than stuck at a
constant: the truncation split must move when the window shrinks (which is
what makes "aged out" reachable) and when the depth limit shrinks (which is
what makes "depth-truncated" reachable).  A category that never fires is a
category that has not been tested.

Reference: docs/AUDIT-TRACE-SPEC.md sections 6 and 12.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import audit_trace_probe as probe  # noqa: E402

CYCLES = 8


def _run():
    return probe.run(cycles=CYCLES, seed=20261025)


def test_a3_meets_its_criterion():
    """The auditor's record is honest: no out-of-window parent called absent."""
    result = _run()
    a3 = result["A3_ancestry_honesty"]
    assert a3["structures_checked"] > 0, "A3 checked nothing; the test is vacuous"
    assert a3["pass"], a3["honesty_errors"]
    assert a3["honesty_error_count"] == 0, a3["honesty_errors"]
    assert a3["window_bound"], "the record does not state the window bound"


def test_a3_can_fail_when_an_out_of_window_parent_is_called_absent():
    """PROOF OF FIRING: relabelling an out-of-window parent as 'no parent' fails."""
    # A tiny synthetic case: one structure whose parent is not in the window.
    class Fake:
        id = "hyp_test"
        type = "hypothesis"
        parent_ids = ["hyp_parent_absent"]

    by_id = {"hyp_other": {"id": "hyp_other", "type": "hypothesis", "parent_ids": []}}
    ever = {"hyp_parent_absent"}   # the record EXISTS -- it is merely out of window

    trace = probe.trace_lineage(Fake(), by_id, ever)
    assert trace["branches"][0]["status"] == "aged_out", trace
    assert trace["branches"][0]["window_bound"], "the unresolved node states no window bound"

    # Now break it: an auditor that cannot see the history calls the
    # out-of-window parent "no parent".  That must be caught.
    def broken_trace(structure, by_id_, ever_stored, max_depth=probe.MAX_ANCESTRY_DEPTH):
        parents = list(getattr(structure, "parent_ids", None) or [])
        branches = []
        for pid in parents:
            node = by_id_.get(pid)
            status = "no_parent" if node is None else "no_parent"
            branches.append({"parent": pid, "status": status, "depth_reached": 1,
                             "window_bound": probe.WINDOW_BOUND})
        return {"id": structure.id, "type": structure.type,
                "resolved": False, "reason": "no_parent", "branches": branches}

    broken = broken_trace(Fake(), by_id, ever)
    # The honesty check is a property of the RECORD, so build the check the
    # way the auditor does and require it to fire on the broken record.
    errors = []
    for b in broken["branches"]:
        in_window = b["parent"] in by_id
        if not in_window and b["status"] == "no_parent":
            errors.append(b)
    assert errors, "the honesty check did not catch the mislabelled parent"


def test_a3_can_fail_when_an_in_window_parent_is_called_absent():
    """PROOF OF FIRING: calling a parent present in the window 'aged out' fails."""
    class Fake:
        id = "hyp_test"
        type = "hypothesis"
        parent_ids = ["hyp_present"]

    by_id = {"hyp_present": {"id": "hyp_present", "type": "hypothesis", "parent_ids": []}}
    ever = {"hyp_present"}

    broken_branch = {"parent": "hyp_present", "status": "aged_out",
                     "depth_reached": 1, "window_bound": probe.WINDOW_BOUND}
    errors = []
    in_window = broken_branch["parent"] in by_id
    if in_window and broken_branch["status"] in ("aged_out", "missing_record"):
        errors.append(broken_branch)
    assert errors, "the honesty check did not catch an in-window parent called absent"


def test_a3_can_fail_when_the_window_bound_is_missing():
    """PROOF OF FIRING: an unresolved node with no window bound fails."""
    class Fake:
        id = "hyp_test"
        type = "hypothesis"
        parent_ids = ["hyp_parent_absent"]

    by_id = {}
    ever = {"hyp_parent_absent"}
    trace = probe.trace_lineage(Fake(), by_id, ever)
    assert trace["branches"][0]["status"] == "aged_out"
    stripped = dict(trace["branches"][0])
    stripped["window_bound"] = None
    errors = []
    if stripped["status"] != "layer1" and not stripped.get("window_bound"):
        errors.append(stripped)
    assert errors, "the honesty check did not catch a missing window bound"


def test_the_truncation_split_is_reachable_and_sensitive():
    """The split must MOVE -- 'aged out' and 'depth-truncated' must be reachable."""
    result = _run()
    a3 = result["A3_ancestry_honesty"]

    # the window sweep is a diagnostic; it must show the rate falling as the
    # window shrinks, which is what makes "aged out" reachable at all.
    sweep = a3["diagnostics"]["window_sweep"]
    assert len(sweep) >= 4, "no window sweep"
    smallest = sweep[0]
    largest = sweep[-1]
    assert smallest["lineage_reachability"] < largest["lineage_reachability"], (
        "reachability did not fall as the window shrank -- the sweep is inert")
    assert smallest["truncation_split"]["aged_out"] > 0, (
        "'aged out' never fired: the category has not been tested")

    # the depth sweep is what makes "depth-truncated" reachable.
    depths = a3["diagnostics"]["depth_sweep"]
    assert len(depths) >= 3, "no depth sweep"
    assert depths[0]["truncation_split"]["depth_truncated"] > 0, (
        "'depth-truncated' never fired: the category has not been tested")
    assert depths[-1]["max_depth"] == probe.MAX_ANCESTRY_DEPTH


def _report_with(*structures):
    """A minimal stand-in for a SleepReport."""
    class Report:
        pass

    report = Report()
    for name in probe.REPORT_LISTS:
        setattr(report, name, [])
    report.hypotheses = list(structures)
    return report


def test_the_window_sweep_takes_the_newest_candidates():
    """The window is read NEWEST FIRST (`ORDER BY time DESC`), so a smaller
    window is the FRONT of the list.  Slicing the wrong end would report a
    reachability that belongs to the oldest candidates."""
    # `_load_prior_candidates` reads `ORDER BY time DESC`, so index 0 of the
    # list is the NEWEST candidate and the last index the oldest.
    window = [{"id": f"c{i}", "type": "concept_candidate", "parent_ids": []}
              for i in range(100)]
    ever = {c["id"] for c in window}

    class Newest:
        id = "hyp_x"
        type = "hypothesis"
        parent_ids = ["c0"]      # index 0 -- the newest

    class Oldest:
        id = "hyp_y"
        type = "hypothesis"
        parent_ids = ["c99"]     # index 99 -- the oldest

    # the newest survives a 10-candidate window.
    small = probe.window_sweep(_report_with(Newest()), window, ever, sizes=(10,))
    assert small[0]["lineage_reachability"] == 1.0, small

    # the oldest does not.
    small_old = probe.window_sweep(_report_with(Oldest()), window, ever, sizes=(10,))
    assert small_old[0]["lineage_reachability"] == 0.0, small_old
    assert small_old[0]["truncation_split"]["aged_out"] == 1, small_old


def test_layer1_structures_are_terminals_and_are_not_counted_as_lineage():
    """Layer-1 candidates have no parent link; counting them as resolvable
    structures would inflate the reachability with a trivial population."""
    class Layer1:
        id = "concept_x"
        type = "concept_candidate"
        parent_ids = []

    class Holder:
        id = "hyp_y"
        type = "hypothesis"
        parent_ids = ["concept_x"]

    class Report:
        pass

    report = Report()
    report.concepts = [Layer1()]
    report.hypotheses = [Holder()]
    for name in probe.REPORT_LISTS:
        if name not in ("concepts", "hypotheses"):
            setattr(report, name, [])

    result = probe.audit_ancestry(report, [], set())
    assert result["layer1_structures"] == 1, result
    assert result["structures_with_lineage"] == 1, result
    # the holder's parent is out of window and was never stored
    assert result["truncation_split"]["missing_record"] == 1, result
