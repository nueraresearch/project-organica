"""The rerun plan's figures are the registry's, not typed.

`docs/RERUN-CAMPAIGN-PLAN.md` allocates the registry's questions into two halves and states the
counts of each. A count typed into prose goes stale silently, so every figure and every question
id below is recomputed from `docs/research_question_registry.json` and compared against the
page. The control at the end moves one question between groups and asserts the comparison
reports it, so a checker that can never fire cannot pass for a guard.
"""

from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
import re
from pathlib import Path

from benchmarks import rerun_triage as T

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/RERUN-CAMPAIGN-PLAN.md"
REGISTRY = ROOT / "docs/research_question_registry.json"

FIGURE_ROW = re.compile(r"^\| ([A-Za-z0-9 ,'\-]+?) \| \*\*(\d+)\*\* \|", re.M)
QUESTION_ROW = re.compile(r"^\| \*\*(Q\d{3})\*\* \|", re.M)


def registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def campaign(reg: dict) -> dict:
    """The two halves, derived from the reopening record rather than from the page."""
    reopened = list(reg["reopening"]["reopened"])
    kept = [exception["id"] for exception in reg["reopening"]["kept_closed"]]
    status = {question["id"]: question["status"] for question in reg["questions"]}
    first = [qid for qid in status
             if qid not in set(reopened) and qid not in set(kept)
             and status[qid] in ("open", "future")]
    gated = [qid for qid in first if status[qid] == "future"]
    runnable = [qid for qid in first if qid not in set(gated)]
    return {
        "reopened": reopened,
        "first": first,
        "runnable": runnable,
        "gated": gated,
        "kept": kept,
        "status": status,
    }


def figures(reg: dict) -> dict[str, int]:
    split = campaign(reg)
    return {
        "Re-derivations": len(split["reopened"]),
        "First answers": len(split["first"]),
        "First answers runnable now": len(split["runnable"]),
        "First answers gated": len(split["gated"]),
        "Kept closed, outside the campaign": len(split["kept"]),
        "Campaign questions": len(split["reopened"]) + len(split["first"]),
        "Registry questions": len(reg["questions"]),
    }


def section(text: str, heading: str) -> str:
    """The body of one level-two section, up to the next one."""
    start = text.index(heading)
    rest = text[start + len(heading):]
    end = rest.find("\n## ")
    return rest if end == -1 else rest[:end]


def page_figures(text: str) -> dict[str, int]:
    return {label.strip(): int(value) for label, value in FIGURE_ROW.findall(text)}


def page_ids(text: str, heading: str) -> list[str]:
    return QUESTION_ROW.findall(section(text, heading))


def mismatches(reg: dict, text: str) -> list[str]:
    """Everything about the page the registry contradicts. Empty means they agree."""
    split = campaign(reg)
    problems = []

    stated = page_figures(text)
    for label, value in figures(reg).items():
        if stated.get(label) != value:
            problems.append("%s: page says %r, registry says %d" % (label, stated.get(label), value))

    halves = {
        "## 3. Half A": split["reopened"],
        # both of Half B's tables live in the one section: the runnable rows, then the gated ones
        "## 5. Half B": split["first"],
    }
    for heading, expected in halves.items():
        listed = page_ids(text, heading)
        if sorted(listed) != sorted(expected):
            problems.append("%s lists %s, registry has %s"
                            % (heading, sorted(listed), sorted(expected)))

    for qid in split["gated"]:
        if qid not in text:
            problems.append("gated question %s does not appear" % qid)
    if "Q012" not in text:
        problems.append("the gate on four future questions is not named")
    return problems


def test_the_plan_states_the_registry_partition() -> None:
    text = PLAN.read_text(encoding="utf-8")
    stated = page_figures(text)
    expected = figures(registry())
    assert stated == expected, (stated, expected)
    assert expected["Re-derivations"] + expected["First answers"] == expected["Campaign questions"]
    assert expected["Campaign questions"] + expected["Kept closed, outside the campaign"] == (
        expected["Registry questions"])


def test_the_plan_lists_exactly_the_campaign_questions() -> None:
    reg = registry()
    text = PLAN.read_text(encoding="utf-8")
    split = campaign(reg)
    assert sorted(page_ids(text, "## 3. Half A")) == sorted(split["reopened"])
    assert sorted(page_ids(text, "## 5. Half B")) == sorted(split["first"])
    assert len(split["runnable"]) == 19 and len(split["gated"]) == 6
    assert not set(split["reopened"]) & set(split["first"]), "a question cannot be in both halves"


def test_the_gated_questions_are_the_future_rows_and_name_their_lock() -> None:
    reg = registry()
    text = PLAN.read_text(encoding="utf-8")
    split = campaign(reg)
    future = [qid for qid, status in split["status"].items() if status == "future"]
    assert sorted(split["gated"]) == sorted(future), (split["gated"], future)
    for qid in split["gated"]:
        row = next(line for line in text.splitlines() if line.startswith("| **%s**" % qid))
        assert row.rstrip().endswith("|"), row
        assert "Q012" in row or "Q022" in row or "Q054" in row, row
    assert "**Q012 is the lock on five of them**" in text


def test_no_kept_closed_question_is_scheduled_as_a_cell() -> None:
    reg = registry()
    text = PLAN.read_text(encoding="utf-8")
    scheduled = set(page_ids(text, "## 3. Half A")) | set(page_ids(text, "## 5. Half B"))
    assert not scheduled & set(campaign(reg)["kept"]), (
        "a kept-closed question cannot be a campaign cell")


def test_the_comparison_fires_when_a_question_moves() -> None:
    """The control: a reclassification the page does not reflect must be reported."""
    reg = registry()
    text = PLAN.read_text(encoding="utf-8")
    assert mismatches(reg, text) == [], mismatches(reg, text)

    moved = json.loads(json.dumps(reg))
    target = moved["reopening"]["reopened"].pop()
    moved["reopening"]["kept_closed"].append(
        {"id": target, "reason": "moved by the control in tests/test_rerun_plan.py"})
    problems = mismatches(moved, text)
    assert problems, "moving a question between groups must be reported"
    assert any(target in problem for problem in problems), problems


def test_the_triage_partitions_every_reopened_question() -> None:
    reg = registry()
    assert T.problems(reg) == [], T.problems(reg)
    rows = T.triage(reg)
    assert {qid for qid, row in rows.items() if row["bucket"] == "re-runnable"} == set(T.RE_RUNNABLE)
    assert {qid for qid, row in rows.items() if row["bucket"] == "needs-harness"} == set(T.NEEDS_HARNESS)
    assert {qid for qid, row in rows.items() if row["bucket"] == "decision-only"} == set(T.DECISION_ONLY)
    assert {qid for qid, row in rows.items() if row["bucket"] == "prose-only"} == set(T.PROSE_ONLY)
    assert len(T.RE_RUNNABLE) == 11
    assert len(T.NEEDS_HARNESS) == 0 and len(T.DECISION_ONLY) == 1
    assert len(T.PROSE_ONLY) == 0


def test_the_half_a_list_is_the_re_runnable_order() -> None:
    text = PLAN.read_text(encoding="utf-8")
    start = text.index("### 3.4")
    end = text.index("## 4. Half A protocol")
    listed = re.findall(r"^\d+\. \*\*(Q\d{3})\*\*", text[start:end], re.M)
    assert listed == list(T.RE_RUNNABLE), (listed, list(T.RE_RUNNABLE))
    assert "Q017" not in listed


def test_the_triage_control_fires_when_a_row_moves_bucket() -> None:
    reg = registry()
    moved = {
        "re-runnable": set(T.RE_RUNNABLE) - {"Q051"},
        "needs-harness": set(T.NEEDS_HARNESS) | {"Q051"},
        "prose-only": set(T.PROSE_ONLY),
    }
    problems = T.problems(reg, moved)
    assert problems, "moving Q051 must be reported"
    assert any("Q051" in problem for problem in problems), problems
