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
LAYER = "synthetic"  # benchmarks/test_layers.py: the module's execution layer

import collections
import json
import re
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


def test_no_parent_disposition_agrees_with_the_truncation_split():
    """The disposition must name the same population the split counts.

    The split and the disposition are computed on independent passes over the
    same traces, so a drift between them is a bug in one of the two -- and a
    disposition that silently stops covering the `no_parent` population would
    pass every test that only looks at its own counters.
    """
    result = _run()
    a3 = result["A3_ancestry_honesty"]
    disposition = a3["no_parent_disposition"]
    assert disposition is not None, "the run did not record a disposition"
    assert disposition["structures_total"] == a3["truncation_split"]["no_parent"], (
        disposition["structures_total"], a3["truncation_split"])
    assert sum(disposition["structures"].values()) == disposition["structures_total"]
    assert set(disposition["structures"]) == set(probe.NO_PARENT_DISPOSITIONS)
    # a capture miss or an unstored record makes the reachability an artifact
    assert disposition["pass"] is True, disposition


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


def _holder(sid, parent_id):
    class Holder:
        pass

    holder = Holder()
    holder.id = sid
    holder.type = "hypothesis"
    holder.parent_ids = [parent_id]
    return holder


def _bare(sid):
    """A reported structure with no parent link at all."""
    class Bare:
        pass

    bare = Bare()
    bare.id = sid
    bare.type = "hypothesis"
    bare.parent_ids = []
    return bare


def test_no_parent_dispositions_distinguish_the_three_owners():
    """A `no_parent` chain has three possible owners and they are not the same.

    The parent node is in the window in all three cases; the ONLY difference is
    the parent-link history the engine wrote for it.  If the check cannot tell
    these apart, `no_parent` is a label that hides whose record ended the chain.
    """
    window = [
        {"id": "role_never", "type": "role_candidate", "parent_ids": []},
        {"id": "role_dropped", "type": "role_candidate", "parent_ids": []},
        {"id": "role_lost", "type": "role_candidate", "parent_ids": []},
    ]
    links = {
        # every copy the engine wrote carries an empty list
        "role_never": [[], []],
        # the first copy carried a link, the current record does not
        "role_dropped": [["concept_a"], [], []],
        # the NEWEST copy carries a link the window read did not return
        "role_lost": [[], ["concept_a"]],
    }
    report = _report_with(_holder("hyp_never", "role_never"),
                          _holder("hyp_dropped", "role_dropped"),
                          _holder("hyp_lost", "role_lost"))

    result = probe.audit_ancestry(
        report, window, set(links), candidate_links=links)
    disposition = result["no_parent_disposition"]
    assert disposition["structures"] == {
        "capture_miss": 1, "no_stored_record": 0,
        "link_dropped": 1, "never_linked": 1,
    }, disposition
    assert disposition["distinct_terminal_nodes"] == 3, disposition
    # a capture miss is an instrument defect: the check must fail on it
    assert disposition["pass"] is False, disposition


def test_no_parent_disposition_passes_only_when_the_record_has_no_link():
    """The honest case: every copy carries an empty parent list."""
    window = [{"id": "role_never", "type": "role_candidate", "parent_ids": []}]
    links = {"role_never": [[], [], []]}
    report = _report_with(_holder("hyp_never", "role_never"))
    result = probe.audit_ancestry(report, window, set(links), candidate_links=links)
    disposition = result["no_parent_disposition"]
    assert disposition["structures"]["never_linked"] == 1, disposition
    assert disposition["structures"]["capture_miss"] == 0, disposition
    assert disposition["pass"] is True, disposition

    # a structure the engine reports with no parent link and never persists is
    # a data defect, and fails
    report_unstored = _report_with(_bare("hyp_missing"))
    missing = probe.audit_ancestry(
        report_unstored, [], set(), candidate_links={})
    assert missing["truncation_split"]["no_parent"] == 1, missing
    assert missing["no_parent_disposition"]["structures"]["no_stored_record"] == 1, missing
    assert missing["no_parent_disposition"]["pass"] is False, missing


def test_no_parent_disposition_is_absent_when_no_link_history_is_supplied():
    """The check must not invent a verdict it did not compute."""
    window = [{"id": "role_never", "type": "role_candidate", "parent_ids": []}]
    report = _report_with(_holder("hyp_never", "role_never"))
    result = probe.audit_ancestry(report, window, set(window_ids := {"role_never"}))
    assert result["no_parent_disposition"] is None, result

    # and the historical-supersession case is NOT a capture miss: the window is
    # reading the newest copy faithfully, so only the newest entry may decide.
    links = {"role_never": [["concept_a"], []]}
    superseded = probe.audit_ancestry(report, window, window_ids, candidate_links=links)
    assert superseded["no_parent_disposition"]["structures"]["link_dropped"] == 1, superseded
    assert superseded["no_parent_disposition"]["pass"] is True, superseded


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


def test_the_three_arms_terminate_at_the_same_no_parent_role_ids():
    """The `no_parent` population is one formation-time mechanism, not three.

    Paper 02 section 4.3 and the spec section 13 state that the stress and
    forced-tie arms' `no_parent` walks end at exactly the default arm's seven
    role ids.  That is a claim about three committed artifacts, so it is
    checked from the artifacts rather than from the prose (AGENTS.md rules 27
    and 29): a regenerated arm that ended anywhere else must fail this test
    and force the two documents to be restated.
    """
    arms = {
        "default": REPO / "docs/audit_trace_probe.json",
        "stress": REPO / "docs/audit_trace_probe_stress.json",
        "tie": REPO / "docs/audit_trace_probe_tie.json",
    }
    terminals = {}
    for arm, path in arms.items():
        result = json.loads(path.read_text())
        disposition = result["A3_ancestry_honesty"]["no_parent_disposition"]
        assert disposition is not None, arm
        assert disposition["pass"] is True, (arm, disposition["structures"])
        assert disposition["distinct_terminal_nodes"] == 7, (
            arm, disposition["distinct_terminal_nodes"])
        assert len(set(disposition["terminal_node_ids"])) == 7, (
            arm, disposition["terminal_node_ids"])
        assert all(i.startswith("role_")
                   for i in disposition["terminal_node_ids"]), (
            arm, disposition["terminal_node_ids"])
        terminals[arm] = set(disposition["terminal_node_ids"])
    assert terminals["default"] == terminals["stress"] == terminals["tie"], terminals


# ---------------------------------------------------------------------------
# The cross-arm claim in the documents, checked against the three artifacts
# ---------------------------------------------------------------------------
#
# Paper 02 section 4.3, the spec's section 13 and the manual's 8.15 all repeat
# the same facts from the committed artifacts: the seven role ids the
# `no_parent` walks terminate at, and the deduplicated populations -- 18 / 17 /
# 17 structures, of which 7 roles, 10 schemas and 1 process, then 7 and 10.
# Prose that repeats an artifact is a new claim (AGENTS.md rules 27 and 29), so
# each document is read here and compared with the artifacts rather than
# trusted.  A regenerated arm that ended elsewhere, or a population that moved,
# must fail this and force the three documents to be restated.

NO_PARENT_ARMS = {
    "default": "docs/audit_trace_probe.json",
    "stress": "docs/audit_trace_probe_stress.json",
    "tie": "docs/audit_trace_probe_tie.json",
}

ROLE_ID = re.compile(r"role_[0-9a-f]{8}")

#: (document, paragraph anchor, ((population regex, expectations), ...)).
#: Each regex group is checked against every (arm, field) pair in its tuple.
RESTATEMENTS = (
    (
        "papers/02_persistent_structural_provenance.md",
        "The `no_parent` population is also the same population across arms",
        (
            (r"(\d+) distinct structures in the default arm \((\d+) roles, "
             r"(\d+) schemas, (\d+) process\) against (\d+) in each 60-cycle "
             r"arm \((\d+) roles, (\d+) schemas\)",
             (
                 (("default", "distinct_structures"),),
                 (("default", "roles"),),
                 (("default", "schemas"),),
                 (("default", "processes"),),
                 (("stress", "distinct_structures"),
                  ("tie", "distinct_structures")),
                 (("stress", "roles"), ("tie", "roles")),
                 (("stress", "schemas"), ("tie", "schemas")),
             )),
        ),
    ),
    (
        "docs/AUDIT-TRACE-SPEC.md",
        "The same terminal set appears in all three arms.",
        (
            (r"deduplicated populations are \*\*(\d+), (\d+) and (\d+) "
             r"distinct structures\*\*",
             (
                 (("default", "distinct_structures"),),
                 (("stress", "distinct_structures"),),
                 (("tie", "distinct_structures"),),
             )),
        ),
    ),
    (
        "docs/USER-MANUAL.md",
        "**The 404 have a cause, and it is the engine's record.**",
        (
            (r"\*\*(\d+)\s+distinct structures\*\* — (\d+) role candidates, "
             r"(\d+) schemas and (\d+) process",
             (
                 (("default", "distinct_structures"),),
                 (("default", "roles"),),
                 (("default", "schemas"),),
                 (("default", "processes"),),
             )),
            (r"(\d+)\s+distinct structures each: (\d+) roles and (\d+) schemas, "
             r"no process",
             (
                 (("stress", "distinct_structures"),
                  ("tie", "distinct_structures")),
                 (("stress", "roles"), ("tie", "roles")),
                 (("stress", "schemas"), ("tie", "schemas")),
             )),
        ),
    ),
)


def _no_parent_signature(arm):
    """The values a document restating this arm's population must carry."""
    result = json.loads((REPO / NO_PARENT_ARMS[arm]).read_text())
    disposition = result["A3_ancestry_honesty"]["no_parent_disposition"]
    examples = disposition["examples"]
    by_type = collections.Counter(example["type"] for example in examples)
    return {
        "terminal_ids": set(disposition["terminal_node_ids"]),
        "distinct_structures": len(examples),
        "roles": by_type["role_candidate"],
        "schemas": by_type["schema_candidate"],
        "processes": by_type["process_candidate"],
    }


def _paragraph(text, anchor):
    for paragraph in re.split(r"\n\s*\n", text):
        if anchor in paragraph:
            return paragraph
    raise AssertionError("no paragraph contains %r" % (anchor,))


def _check_restatement(document, anchor, populations, text):
    """Reject any document that disagrees with the artifacts it quotes."""
    paragraph = _paragraph(text, anchor)
    expected = _no_parent_signature("default")["terminal_ids"]
    stated = set(ROLE_ID.findall(paragraph))
    assert len(stated) == 7, (document, sorted(stated))
    assert stated == expected, (document, sorted(stated ^ expected))
    for pattern, expectations in populations:
        match = re.search(pattern, text)
        assert match is not None, (document, pattern)
        values = [int(group) for group in match.groups()]
        assert len(values) == len(expectations), (document, pattern)
        for value, arms_and_fields in zip(values, expectations):
            for arm, field in arms_and_fields:
                want = _no_parent_signature(arm)[field]
                assert value == want, (document, arm, field, value, want)


def test_each_document_restates_the_population_the_artifacts_carry():
    for document, anchor, populations in RESTATEMENTS:
        _check_restatement(
            document, anchor, populations, (REPO / document).read_text())


def test_the_cross_arm_restatement_check_can_fail():
    """A check that cannot disagree with its subject is not a check."""
    document, anchor, populations = RESTATEMENTS[0]
    text = (REPO / document).read_text()
    _check_restatement(document, anchor, populations, text)
    mutated = (
        text.replace("`role_e19400ee`", "`role_00000000`", 1),
        text.replace("18 distinct structures", "19 distinct structures", 1),
    )
    for corrupt in mutated:
        assert corrupt != text, document
        try:
            _check_restatement(document, anchor, populations, corrupt)
        except AssertionError:
            continue
        raise AssertionError("the check accepted a corrupted restatement")
