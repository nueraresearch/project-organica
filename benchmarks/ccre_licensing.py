"""Which questions the next cross-context run may answer, and which it may not.

A run that answers more questions than its design licenses has not become more
productive; it has started borrowing. This module is the line between an
experiment and a story: each licensed question names the measurement that would
answer it, the observations the run must record to make that measurement
possible, the outcome that counts as an answer and the outcome that does not,
and the two different decisions the two outcomes would enable (AGENTS.md rule
30). Questions the design cannot adjudicate are listed as refused, with the
reason, so a later reader cannot quietly reintroduce them.

Two structural rules are enforced rather than stated. At least one licensed
question must be **trace-derived** (AGENTS.md rule 18), and a question that the
registry has already closed or retired may not be licensed as one this run will
answer, because its answer is already in the record.

The record sets no threshold, no bar and no sample size, and the rendered page
states no measured figure: those belong to the run's own preregistration, fixed
before the first cell (AGENTS.md rule 19), and a licensing record that carried a
number would become a bar nobody voted on.

Nothing is written in ``--check`` mode.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import research_registry as rr

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "ccre_question_licensing.json"
DOC = ROOT / "docs" / "CCRE-QUESTION-LICENSING.md"

TIERS = ("answers", "moves", "records")
SETTLING = ("answers", "moves")
MIN_TEXT = 60
MIN_REFUSED = 20


def load():
    return json.loads(RECORD.read_text(encoding="utf-8"))


def registry_questions():
    return {q["id"]: q for q in rr.load()["questions"]}


def validate(record):
    errors = []
    questions = registry_questions()
    licensed = record.get("licensed", [])

    seen = set()
    for row in licensed:
        qid = row.get("id", "")
        if qid not in questions:
            errors.append("%s: licensed but not in the registry" % qid)
        if qid in seen:
            errors.append("%s: licensed more than once" % qid)
        seen.add(qid)

        tier = row.get("tier")
        if tier not in TIERS:
            errors.append("%s: unknown tier %r" % (qid, tier))
        if len(row.get("measurement", "")) < MIN_TEXT:
            errors.append("%s: the measurement is too thin to run" % qid)
        if not row.get("observation"):
            errors.append("%s: names no observation, so nothing would be recorded" % qid)

        if tier in SETTLING:
            status = questions.get(qid, {}).get("status")
            if status in ("closed", "retired"):
                errors.append(
                    "%s: the registry already answers this question (%s); licensing it again "
                    "re-asks a settled question" % (qid, status)
                )
            for field in ("answered_if", "not_answered_if"):
                if len(row.get(field, "")) < MIN_TEXT:
                    errors.append("%s: %s is too thin to judge the run" % (qid, field))
            positive = row.get("decision_if_positive", "").strip()
            negative = row.get("decision_if_negative", "").strip()
            if not positive or not negative:
                errors.append("%s: a decision is missing" % qid)
            elif positive == negative:
                errors.append("%s: the two decisions are the same, so the run changes no design" % qid)

        prior = row.get("prior_artifact")
        if prior and not (ROOT / prior).exists():
            errors.append("%s: prior artifact does not exist: %s" % (qid, prior))

    if not any(row.get("tier") == "answers" for row in licensed):
        errors.append("no question is licensed to be answered, so the run answers nothing")
    if not any(row.get("trace_derived") for row in licensed):
        errors.append(
            "no trace-derived diagnostic is licensed; the next protocol must contain one "
            "(AGENTS.md rule 18)"
        )

    refused = record.get("not_licensed", [])
    if not refused:
        errors.append("nothing is refused, which means the boundary was never drawn")
    licensed_text = {questions[qid]["question"] for qid in seen if qid in questions}
    for row in refused:
        question = row.get("question", "").strip()
        if len(question) < MIN_REFUSED:
            errors.append("a refused question is too short to identify: %r" % question)
        if len(row.get("reason", "")) < MIN_TEXT:
            errors.append("%r: refused without a reason" % question)
        if question in licensed_text:
            errors.append("%r: both licensed and refused" % question)

    preregistration = record.get("preregistration")
    if preregistration and not (ROOT / preregistration).exists():
        errors.append("the named preregistration does not exist: %s" % preregistration)

    tally = {tier: sum(1 for row in licensed if row.get("tier") == tier) for tier in TIERS}
    return {
        "passed": not errors,
        "errors": errors,
        "licensed": len(licensed),
        "refused": len(refused),
        "tally": tally,
        "trace_derived": sum(1 for row in licensed if row.get("trace_derived")),
    }


def render(record, report):
    lines = [
        "# Questions the next cross-context run may answer",
        "",
        "**Generated from `docs/ccre_question_licensing.json`. Do not edit this file.** Rebuild with",
        "`python -m benchmarks.ccre_licensing`; `--check` validates and compares without writing.",
        "",
        "A run that answers more questions than its design licenses has not become more productive;",
        "it has started borrowing. This page is the boundary: what the campaign `%s`"
        % record["campaign"],
        "can adjudicate, what it can only move, what it records for free, and what it may not answer",
        "at all. **No measured figure is stated here**, and no threshold, bar or sample size either:",
        "those belong to the run's own preregistration, fixed before the first cell (AGENTS.md rule",
        "19).",
        "",
        "## The boundary at a glance",
        "",
        "| Tier | Count | What a result in this tier may claim |",
        "| --- | --- | --- |",
        "| answers | %d | the question is settled, within the scope its registry entry states |"
        % report["tally"]["answers"],
        "| moves | %d | evidence moves the question; it is not settled |" % report["tally"]["moves"],
        "| records | %d | an observation is recorded; no claim is made from it |"
        % report["tally"]["records"],
        "| refused | %d | nothing, in either direction |" % report["refused"],
        "",
        "**Trace-derived diagnostics licensed:** %d. AGENTS.md rule 18 requires at least one, and "
        "the validator fails without it." % report["trace_derived"],
        "",
        "",
        "## Licensed",
        "",
    ]
    for row in record["licensed"]:
        question = registry_questions().get(row["id"], {}).get("question", "")
        lines += [
            "### %s — %s" % (row["id"], question),
            "",
            "**Tier.** %s%s"
            % (
                row["tier"],
                " (trace-derived)" if row.get("trace_derived") else "",
            ),
            "",
            "**Measurement.** %s" % row["measurement"],
            "",
            "**Recorded.** " + "; ".join(row["observation"]),
            "",
        ]
        if row.get("tier") in SETTLING:
            lines += [
                "**Answered if.** %s" % row["answered_if"],
                "",
                "**Not answered if.** %s" % row["not_answered_if"],
                "",
                "**If it holds.** %s" % row["decision_if_positive"],
                "",
                "**If it does not.** %s" % row["decision_if_negative"],
                "",
            ]
        if row.get("prior_artifact"):
            lines += ["**Prior artifact.** `%s`" % row["prior_artifact"], ""]

    lines += [
        "## Refused, with the reason",
        "",
        "These are not uninteresting questions. They are questions this design cannot adjudicate,",
        "so a result from it says nothing about them in either direction.",
        "",
        "| Question | Why this run cannot answer it |",
        "| --- | --- |",
    ]
    for row in record["not_licensed"]:
        lines.append("| %s | %s |" % (row["question"], row["reason"]))

    lines += [
        "",
        "## What this record does not do",
        "",
        "- **It sets no bar.** A licensing record says what may be claimed; a preregistration says",
        "  what counts as a result. Without the second, the first is only a list of intentions.",
        "- **It adds no evidence.** Every row names a measurement still to be made, and the prior",
        "  artifact column says what the last one showed.",
        "- **It does not authorise a run.** No cell may start until the campaign has its own",
        "  preregistration, its comparators fixed and its controls able to fail (AGENTS.md rule 11).",
        "- **It cannot make a refused question partially answerable.** If someone later wants one, it",
        "  needs its own design, and a design that measures it is a different experiment.",
        "",
    ]
    if record.get("preregistration"):
        lines += [
            "## The preregistration this record belongs to",
            "",
            "`%s`." % record["preregistration"],
            "",
        ]
    else:
        lines += [
            "## There is no preregistration yet",
            "",
            "This campaign has no protocol on disk, so nothing here is committed and no cell may run.",
            "The first artifact the run needs is that protocol, not a result.",
            "",
        ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the record and compare the page against a fresh render, without writing",
    )
    args = parser.parse_args(argv)

    record = load()
    report = validate(record)
    if not report["passed"]:
        for error in report["errors"]:
            print("FAIL:", error)
        return 1

    if args.check:
        if not DOC.exists():
            print("FAIL: the licensing page does not exist: %s" % DOC)
            return 1
        if DOC.read_text(encoding="utf-8") != render(record, report):
            print("FAIL: %s is stale; rebuild with python -m benchmarks.ccre_licensing" % DOC.name)
            return 1
    else:
        DOC.write_text(render(record, report), encoding="utf-8")

    print(
        "ccre licensing: %d licensed (%d answers / %d moves / %d records), %d refused"
        % (
            report["licensed"],
            report["tally"]["answers"],
            report["tally"]["moves"],
            report["tally"]["records"],
            report["refused"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
