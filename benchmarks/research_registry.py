"""The research-question registry: what was asked, what closed, what is retired, what waits.

A results-rich, questions-poor record is the failure mode this file exists to prevent. The
registry is data (`docs/research_question_registry.json`) rendered to
`docs/RESEARCH-QUESTION-REGISTRY.md`, and the checks below are what keep it honest:

* every `docs/DECISION-*.md` on disk must be tallied by some question, so a new decision
  fails the test until it is registered;
* every row of the bottleneck map must be claimed by some question, and no question may
  claim a row that does not exist;
* a closed or retired question must carry an answer and evidence that exists on disk;
* a future question must name prerequisites that exist.

    ./.venv/bin/python -m benchmarks.research_registry            # validate + render
    ./.venv/bin/python -m benchmarks.research_registry --check     # validate only
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "docs" / "research_question_registry.json"
DOC = ROOT / "docs" / "RESEARCH-QUESTION-REGISTRY.md"
MAP = ROOT / "docs" / "bottleneck_map.json"

STATUSES = ("closed", "open", "retired", "future")
OUTCOMES = ("SUPPORTED", "UNSUPPORTED", "MIXED", "INCONCLUSIVE", "WITHDRAWN")
HEADINGS = {
    "closed": "1. Closed — answered, and the answer constrained the space",
    "open": "2. Open — evidence in hand, no settled answer",
    "retired": "3. Retired — no longer worth resources",
    "future": "4. Future — valid only after a prerequisite is met",
}


def load(path: Path = REGISTRY) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def decision_files() -> list[str]:
    return sorted(p.name for p in (ROOT / "docs").glob("DECISION-*.md"))


def map_rows() -> list[str]:
    return [row["candidate"] for row in json.loads(MAP.read_text(encoding="utf-8"))["rows"]]


def validate(reg: dict) -> dict:
    errors: list[str] = []
    questions = reg["questions"]
    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        errors.append("duplicate ids: %r" % (sorted(i for i in set(ids) if ids.count(i) > 1),))
    known = set(ids)
    for q in questions:
        qid = q.get("id", "?")
        if q.get("status") not in STATUSES:
            errors.append("%s: unknown status %r" % (qid, q.get("status")))
        if not q.get("question"):
            errors.append("%s: no question text" % qid)
        if q.get("status") in ("closed", "retired"):
            if not q.get("answer"):
                errors.append("%s: closed or retired without an answer" % qid)
            if not q.get("evidence"):
                errors.append("%s: closed or retired without evidence" % qid)
        if q.get("status") == "open" and not (q.get("why_open") or q.get("evidence")):
            errors.append("%s: open with neither evidence nor why_open" % qid)
        prerequisites = q.get("prerequisites", q.get("blocked_by", []))
        if q.get("status") == "future":
            if not prerequisites:
                errors.append("%s: future without prerequisites" % qid)
            for prerequisite in prerequisites:
                if prerequisite not in known:
                    errors.append("%s: prerequisite is not a question: %r" % (qid, prerequisite))
        outcome = q.get("outcome")
        status = q.get("status")
        if status in ("closed", "retired"):
            if outcome is None:
                errors.append("%s: closed or retired without an outcome" % qid)
            elif outcome not in OUTCOMES:
                errors.append("%s: unknown outcome %r" % (qid, outcome))
        elif outcome is not None:
            errors.append("%s: open or future question carries an outcome" % qid)
        reopened = q.get("reopened")
        if reopened is not None:
            if status != "open":
                errors.append("%s: carries a reopening record but is %r" % (qid, status))
            for field in ("date", "reason", "measured_on"):
                if not reopened.get(field):
                    errors.append("%s: reopening record has no %s" % (qid, field))
        if "prerequisites" in q and "blocked_by" in q and q["prerequisites"] != q["blocked_by"]:
            errors.append("%s: prerequisites and blocked_by disagree" % qid)
        for path in q.get("evidence", []):
            if not (ROOT / path).exists():
                errors.append("%s: evidence path does not exist: %s" % (qid, path))
        for name in q.get("decisions", []):
            if not (ROOT / "docs" / name).exists():
                errors.append("%s: decision record does not exist: %s" % (qid, name))

    tallied = {name for q in questions for name in q.get("decisions", [])}
    untallied = [name for name in decision_files() if name not in tallied]
    if untallied:
        errors.append("decision records not tallied by any question: %r" % (untallied,))
    stale = sorted(name for name in tallied if name not in decision_files())
    if stale:
        errors.append("questions cite decision records that are not on disk: %r" % (stale,))

    rows = map_rows()
    claimed = Counter(name for q in questions for name in q.get("bottleneck_rows", []))
    unknown = [name for name in claimed if name not in rows]
    if unknown:
        errors.append("questions claim bottleneck rows that do not exist: %r" % (unknown,))
    unclaimed = [name for name in rows if name not in claimed]
    if unclaimed:
        errors.append("bottleneck rows no question claims: %r" % (unclaimed,))

    opening = reg.get("reopening")
    if opening is None:
        errors.append("the registry records no reopening; a bulk status change needs its criterion")
    else:
        for field in ("date", "criterion", "engine_version", "engine_sha256"):
            if not opening.get(field):
                errors.append("reopening record has no %s" % field)
        with_record = sorted(q["id"] for q in questions if q.get("reopened"))
        if sorted(opening.get("reopened", [])) != with_record:
            errors.append("reopening names %r but the rows carrying a reopening record are %r"
                          % (sorted(opening.get("reopened", [])), with_record))
        for qid in opening.get("reopened", []):
            if qid not in known:
                errors.append("reopening names a question that does not exist: %r" % (qid,))
        for exception in opening.get("kept_closed", []):
            if exception.get("id") not in known:
                errors.append("reopening keeps closed a question that does not exist: %r"
                              % (exception.get("id"),))
            if not exception.get("reason"):
                errors.append("reopening keeps %r closed without a reason" % (exception.get("id"),))
            if exception.get("id") in with_record:
                errors.append("reopening keeps %r closed and reopened it" % (exception.get("id"),))

    tally = Counter(q["status"] for q in questions)
    return {"passed": not errors, "errors": errors,
            "tally": {status: tally.get(status, 0) for status in STATUSES},
            "questions": len(questions)}


def render(reg: dict, report: dict) -> str:
    tally = report["tally"]
    lines = [
        "# Research-question registry",
        "",
        "**Generated** from `docs/research_question_registry.json` by",
        "`python -m benchmarks.research_registry`. Do not edit this file by hand: the tally below is",
        "recomputed from the data, and `tests/test_research_registry.py` fails if the two disagree.",
        "",
        "The point of this artifact is the column that results never get: **what was asked, what the",
        "answer closed, what stopped being worth resources, and what is waiting on a prerequisite.**",
        "A project at this size remembers its results and forgets its dead ends, and the dead ends are",
        "where the method is.",
        "",
        "## Tally",
        "",
        "| status | count | meaning |",
        "| --- | --- | --- |",
        "| closed | %d | a result constrained the space; the answer is recorded with its scope |" % tally["closed"],
        "| open | %d | evidence exists, no answer is settled |" % tally["open"],
        "| retired | %d | no longer worth resources; the reason is recorded |" % tally["retired"],
        "| future | %d | valid only after a named prerequisite is met |" % tally["future"],
        "| **total** | **%d** | |" % report["questions"],
        "",
    ]
    opening = reg.get("reopening")
    if opening:
        lines += [
            "## 0. Reopened on %s" % opening["date"],
            "",
            opening["criterion"],
            "",
            "**Reopened: %s.** **Kept closed: %d**, each with its reason below. The build the "
            "criterion names is `%s` (`%s`)." % (
                ", ".join(opening["reopened"]), len(opening.get("kept_closed", [])),
                opening["engine_version"], opening["engine_sha256"][:16]),
            "",
        ]
        for exception in opening.get("kept_closed", []):
            lines += ["- **%s** -- %s" % (exception["id"], exception["reason"])]
        lines += [""]
    lines += [
        "## How this stays current",
        "",
        "Three checks run in the test suite and can fail: a new `docs/DECISION-*.md` that no question",
        "tallies, a bottleneck-map row that no question claims, and a question that cites evidence",
        "which is not on disk. Registering a decision is therefore part of making one.",
        "",
    ]
    for status in STATUSES:
        lines += ["## " + HEADINGS[status], ""]
        for q in reg["questions"]:
            if q["status"] != status:
                continue
            lines += ["### %s — %s" % (q["id"], q["question"]), ""]
            if q.get("kind"):
                lines += ["*%s question.*" % q["kind"], ""]
            if q.get("outcome"):
                lines += ["**Outcome.** %s" % q["outcome"], ""]
            if q.get("answer"):
                lines += ["**Answer.** %s" % q["answer"], ""]
            if q.get("reopened"):
                lines += ["**Reopened %s.** Measured on: %s. %s" % (
                    q["reopened"]["date"], q["reopened"]["measured_on"],
                    q["reopened"]["reason"]), ""]
            if q.get("why_open"):
                lines += ["**Why it is open.** %s" % q["why_open"], ""]
            if q.get("scope"):
                lines += ["**Scope.** %s" % q["scope"], ""]
            if q.get("prerequisites"):
                lines += ["**Prerequisites.** %s" % ", ".join(q["prerequisites"]), ""]
            if q.get("preregistrations"):
                lines += ["**Preregistered in.** " + ", ".join("`%s`" % x for x in q["preregistrations"]), ""]
            if q.get("evidence"):
                lines += ["**Evidence.** " + ", ".join("`%s`" % p for p in q["evidence"]), ""]
            if q.get("decisions"):
                lines += ["**Decision record.** " + ", ".join("`docs/%s`" % d for d in q["decisions"]), ""]
            if q.get("bottleneck_rows"):
                lines += ["**Bottleneck rows.** " + "; ".join(q["bottleneck_rows"]), ""]
    lines += [
        "## What this registry is not",
        "",
        "- **It is not a capability claim.** It records what was asked and what constrained the answer;",
        "  the claim status of every entry lives in the artifact it cites.",
        "- **The future section is conditional, not evidence.** A question listed there is a statement",
        "  about what would become worth asking, not about what the project can do today.",
        "- **It does not rank questions by promise.** The retired section exists precisely because",
        "  promise is not a reason to spend resources (AGENTS.md rule 30).",
        "",
    ]
    return "\n".join(lines) + "\n"


def stale(reg, report=None):
    """Return a failure message when the document is not a fresh render, else None.

    A document that was rendered once and then edited by hand passes every
    record-level check while disagreeing with the record it claims to show, so
    the comparison belongs in validation rather than in a separate courtesy the
    author has to remember.
    """
    report = report or validate(reg)
    expected = render(reg, report)
    if not DOC.exists():
        return "the rendered document does not exist: %s" % DOC
    if DOC.read_text(encoding="utf-8") != expected:
        return "%s is stale; rebuild with python -m benchmarks.research_registry" % DOC
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate and verify the rendered document against a fresh render, without writing",
    )
    args = parser.parse_args(argv)
    reg = load()
    report = validate(reg)
    if not report["passed"]:
        for error in report["errors"]:
            print("FAIL:", error)
        return 1
    if args.check:
        problem = stale(reg, report)
        if problem:
            print("FAIL:", problem)
            return 1
    else:
        DOC.write_text(render(reg, report), encoding="utf-8")
    print("tally:", report["tally"], "questions:", report["questions"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
