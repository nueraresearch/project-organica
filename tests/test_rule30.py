"""Rule 30, enforced against the artifacts instead of by reading.

AGENTS.md rule 30: *a diagnostic is worth its cost only if a named architectural decision follows
from both a positive and a negative result.* A diagnostic whose two outcomes both lead back to
another diagnostic spends the resource and changes no design. That sentence is a test:

- a row with one outcome has not stated two decisions;
- two outcomes with the same decision (after normalisation) are one decision;
- two outcomes that are both *"do it again"* are the case the rule names, and the paraphrasings
  matter, so the detector reads the text rather than comparing strings;
- one diagnostic outcome beside one real decision is allowed: the design moves on the branch that
  matters, and the second branch is recorded as a measurement.

The rule is judged where the record proposes to run something: the change-to-failure map's campaign
rows, and every preregistration's decision table that states the decision a branch enables. The
coverage test makes a new table visible — it has to be judged or explicitly exempted with a reason,
so a table cannot arrive unclassified.

Every control below is a case the detector must reject. A guard that cannot fire is decoration
(AGENTS.md rule 25c), and the mutation control at the end runs the detector over a real row.
"""

from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHANGE_MAP = ROOT / "docs" / "engine_change_failure_map.json"
PREREGS = ROOT / "docs"

# Tables that state the decision each outcome branch enables.
JUDGED = {
    "presence_cap_prereg.json",
    "presence_cap_ladder_prereg.json",
    "core_band_admission_prereg.json",
    "density_interaction_prereg.json",
    "density_interaction_a2_prereg.json",
    "density_padding_prereg.json",
    "presence_conversion_observer_prereg.json",
    "presence_conversion_repair_prereg.json",
    "presence_band_rank_prereg.json",
    "presence_band_rank_2_prereg.json",
    "presence_band_rank_3_prereg.json",
    "presence_band_rank_4_prereg.json",
    "presence_band_rank_5_prereg.json",
    "presence_construct_audit_prereg.json",
    "t1_persistence_off_prereg.json",
    "t1b_persistence_off_prereg.json",
    "persistence_mechanism_prereg.json",
}

# Tables frozen before the decision text was recorded. Listed rather than skipped silently, so a
# new table cannot join them by default; the reason has to be written down.
EXEMPT = {
    "d3_persistence_prereg.json": "records a verdict and a reading per condition, not the decision",
    "d3_persistence_seed_varying_prereg.json": "records a verdict and a reading per condition, not the decision",
    "d3_persistence_engine_replication_prereg.json": "records a verdict and a reading per condition, not the decision",
    "d3_persistence_g1_recalibrated_prereg.json": "records a verdict and a reading per condition, not the decision",
    "admission_two_arm_prereg.json": "records a verdict and a reading per condition, not the decision",
    "q006_admission_rederivation_prereg.json": "records a survival verdict and a reading per condition, not a new design decision",
    "ranking_admission_prereg.json": "records a verdict and a reading per condition, not the decision",
    "q053_mechanism_prereg.json": "records a verdict and a reading per condition, not the decision",
    "rank_ordering_prereg.json": "decisions are categorical labels (positive, negative, neither)",
}

# "Do it again", as a paraphrase. Each pattern is a way of naming the next diagnostic as the
# deliverable; none of them names a change to the design.
AGAIN = (
    r"\b(run|rerun|re-run|repeat|retry|try)\b[^.;]*\b(another|a different|a further|an additional)\s+"
    r"(diagnostic|probe|variant|moderator|experiment|measurement|study|cell|block|run)\b",
    r"\b(another|a further|an additional)\s+(diagnostic|probe|variant|moderator|experiment|"
    r"measurement|study|cell|block)\b",
    r"\b(diagnose|investigate|measure|probe|explore)\b[^.;]*\b(further|again|more)\b",
    r"\b(raise|increase)\s+n\b",
    r"\bcollect more (data|seeds|evidence)\b",
    r"\bdo it again\b",
)


def normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).split().__str__()


def is_again(text: str) -> bool:
    """True when a branch names the next diagnostic rather than a change to the design."""
    flat = " ".join(text.lower().split())
    return any(re.search(pattern, flat) for pattern in AGAIN)


def rule30_problems(outcomes: list[tuple[str, str]]) -> list[str]:
    """Judge one diagnostic's outcome branches: ``(verdict, decision)`` pairs."""
    problems = []
    if len(outcomes) < 2:
        problems.append("only %d outcome recorded; the rule needs a positive and a negative"
                        % len(outcomes))
        return problems

    decisions = [(verdict, decision.strip()) for verdict, decision in outcomes]
    for verdict, decision in decisions:
        if not decision:
            problems.append("%s: no decision is stated" % verdict)

    stated = [(verdict, decision) for verdict, decision in decisions if decision]
    seen: dict[str, str] = {}
    for verdict, decision in stated:
        key = normalise(decision)
        if key in seen:
            problems.append("%s and %s state the same decision, so the outcome changes no design"
                            % (seen[key], verdict))
        seen[key] = verdict

    if stated and all(is_again(decision) for _, decision in stated):
        problems.append("every outcome leads to another diagnostic: %s"
                        % "; ".join(verdict for verdict, _ in stated))
    return problems


def change_rows() -> list[dict]:
    return json.loads(CHANGE_MAP.read_text(encoding="utf-8"))["changes"]


def change_outcomes(row: dict) -> list[tuple[str, str]]:
    return [
        ("positive", row.get("decision_if_positive", "")),
        ("negative", row.get("decision_if_negative", "")),
    ]


def table_branches(table) -> list[tuple[str, str]]:
    """Branches of any decision-table shape the preregistrations use."""
    if isinstance(table, dict):
        return [(condition, decision) for condition, decision in table.items()]
    branches = []
    for row in table:
        decision = row.get("decision")
        label = row.get("verdict") or row.get("condition") or "branch"
        if isinstance(decision, str) and decision in {"positive", "negative", "neither"}:
            continue  # a categorical label, not the decision text
        if decision:
            branches.append((label, decision))
    return branches


def prereg_tables() -> dict[str, object]:
    tables = {}
    for path in sorted(PREREGS.glob("*prereg*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if "decision_table" in data:
            tables[path.name] = data["decision_table"]
    return tables


def test_every_campaign_row_names_two_different_decisions() -> None:
    rows = [row for row in change_rows() if row["status"] == "stays"]
    assert rows, "the change map has no campaign rows to judge"
    problems = {row["id"]: rule30_problems(change_outcomes(row)) for row in rows}
    failed = {rid: found for rid, found in problems.items() if found}
    assert not failed, failed


def test_every_judged_prereg_table_names_a_decision_per_outcome() -> None:
    tables = prereg_tables()
    assert set(JUDGED) <= set(tables), sorted(set(JUDGED) - set(tables))
    problems = {}
    for name in sorted(JUDGED):
        branches = table_branches(tables[name])
        found = rule30_problems(branches)
        if found:
            problems[name] = found
    assert not problems, problems


def test_every_decision_table_is_judged_or_exempted_with_a_reason() -> None:
    """A new table cannot arrive unclassified: it is either judged or named above."""
    tables = prereg_tables()
    unclassified = sorted(set(tables) - JUDGED - set(EXEMPT))
    assert not unclassified, (
        "decision tables neither judged nor exempted: %s -- add each to JUDGED if it states the "
        "decision per outcome, or to EXEMPT with the reason it cannot be judged" % unclassified)
    assert all(reason.strip() for reason in EXEMPT.values())
    assert not set(JUDGED) & set(EXEMPT)


def test_the_rule_fires_when_both_outcomes_are_another_diagnostic() -> None:
    """The case the rule names, in the phrasings a proposal actually uses."""
    controls = [
        [("pass", "Run another diagnostic on the same cap and see"),
         ("fail", "Run another diagnostic on a denser world")],
        [("pass", "try a different moderator"),
         ("fail", "investigate further before deciding")],
        [("pass", "Adopt the rule behind an owner decision"),
         ("fail", "Adopt the rule behind an owner decision")],
        [("pass", "Raise n until the interval separates"),
         ("fail", "Probe again with more seeds")],
        [("pass", "Run another variant of the same ranking probe"),
         ("fail", "Probe again with more seeds")],
        [("pass", "Adopt the exclusion as an allocation change"), ("fail", "")],
        [("pass", "Adopt the exclusion as an allocation change")],
    ]
    for outcomes in controls:
        found = rule30_problems(outcomes)
        assert found, "the detector accepted a diagnostic that changes no design: %r" % (outcomes,)


def test_one_diagnostic_branch_beside_a_real_decision_is_allowed() -> None:
    """The rule rejects two dead ends, not one: the real branch is what licenses the run."""
    outcomes = [
        ("pass", "Adopt intra-cell exclusion as an allocation change, behind an owner decision"),
        ("fail", "Do not adopt; diagnose what the arms differ in before any further density work"),
    ]
    assert rule30_problems(outcomes) == []


def test_the_detector_fires_on_a_real_row_once_both_branches_point_at_a_probe() -> None:
    """Mutation control: a row that passes is made to fail, so the pass is not vacuous."""
    row = next(row for row in change_rows() if row["status"] == "stays")
    assert rule30_problems(change_outcomes(row)) == []

    mutated = dict(row)
    mutated["decision_if_positive"] = "Run another probe of the same mechanism"
    mutated["decision_if_negative"] = "Run another probe of the same mechanism"
    assert rule30_problems(change_outcomes(mutated)), (
        "%s passes even when both of its outcomes lead to another probe" % row["id"])
