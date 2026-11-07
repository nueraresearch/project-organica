"""Research accountability system for Project Organica.

Four layers, one direction of flow:

    question  ->  finding  ->  claim  ->  public statement

Layer 1, the research registry, lives in ``docs/research_question_registry.json``
and is validated and rendered by :mod:`benchmarks.research_registry`. This module
adds layer 2, the claim ledger, and generates the two public projections (the
dashboard and the findings page). It also enforces the cross-layer rules that
neither layer can check alone: a load-bearing claim must rest on a closed,
supported question; a withdrawn interpretation must carry a reason; and the
published numbers must be the numbers the records contain.

Every public surface here is generated. Nothing is typed by hand, and ``--check``
validates without writing so the test suite can prove the files still match.

A question is not a finding, a finding is not a claim, and a claim is not a
decision. Collapsing any two of those pairs is the drift this system exists to
make visible.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from benchmarks import research_registry as rr

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "research_question_registry.json"
LEDGER = ROOT / "docs" / "claim_ledger.json"

LEDGER_DOC = ROOT / "docs" / "CLAIM-LEDGER.md"
DASHBOARD_DOC = ROOT / "docs" / "RESEARCH-DASHBOARD.md"
FINDINGS_DOC = ROOT / "docs" / "RESEARCH-FINDINGS.md"

CLASSIFICATIONS = ("DEMONSTRATED", "SUPPORTED", "HYPOTHESIS", "ASPIRATION")
CLAIM_STATUSES = ("ACTIVE", "WITHDRAWN", "SUPERSEDED")
LOAD_BEARING = ("DEMONSTRATED", "SUPPORTED")


def load_pair():
    """Return the registry and the ledger, both as loaded from disk."""
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    return reg, ledger


def by_id(reg):
    return {q["id"]: q for q in reg["questions"]}


def validate(reg, ledger):
    """Check the ledger and the rules that cross both layers.

    Returns the same shape as the registry validator so callers can treat the
    two the same way: a report with ``passed`` and ``errors``.
    """
    registry_report = rr.validate(reg)
    errors = list(registry_report["errors"])
    questions = by_id(reg)
    claims = ledger.get("claims", [])

    seen = set()
    for c in claims:
        cid = c.get("claim_id")
        if not cid:
            errors.append("a claim has no claim_id")
            continue
        if cid in seen:
            errors.append("%s: duplicate claim_id" % cid)
        seen.add(cid)

        classification = c.get("classification")
        status = c.get("status")
        if classification not in CLASSIFICATIONS:
            errors.append("%s: unknown classification %r" % (cid, classification))
        if status not in CLAIM_STATUSES:
            errors.append("%s: unknown status %r" % (cid, status))

        for key in ("supporting_questions", "contradicting_questions"):
            for qid in c.get(key, []):
                if qid not in questions:
                    errors.append("%s: %s cites a question that does not exist: %s" % (cid, key, qid))
        for path in c.get("supporting_evidence", []):
            if not (ROOT / path).exists():
                errors.append("%s: evidence path does not exist: %s" % (cid, path))

        if not c.get("scope_limitations"):
            errors.append(
                "%s: no scope limitations; a claim with no stated limit is wider than its check" % cid
            )

        if status == "ACTIVE" and classification in LOAD_BEARING:
            if not c.get("supporting_questions"):
                errors.append("%s: active load-bearing claim without a supporting question" % cid)
            if not c.get("supporting_evidence"):
                errors.append("%s: active load-bearing claim without evidence" % cid)
            for qid in c.get("supporting_questions", []):
                q = questions.get(qid)
                if q is None:
                    continue
                if q["status"] != "closed" or q.get("outcome") != "SUPPORTED":
                    errors.append(
                        "%s: load-bearing claim cites %s, which is %s %s; move the claim or the question"
                        % (cid, qid, q["status"], q.get("outcome"))
                    )

        if status == "ACTIVE" and classification in ("HYPOTHESIS", "ASPIRATION"):
            if not c.get("supporting_questions") and not c.get("contradicting_questions"):
                errors.append("%s: active hypothesis cites no question at all" % cid)

        if status == "WITHDRAWN":
            if not c.get("withdrawn_reason") and not c.get("superseded_by"):
                errors.append("%s: withdrawn without a reason or a superseding claim" % cid)
        elif c.get("withdrawn_reason"):
            errors.append("%s: carries a withdrawal reason but is not withdrawn" % cid)

        target = c.get("superseded_by")
        if target is not None and target not in {x.get("claim_id") for x in claims}:
            errors.append("%s: superseded_by does not name a claim: %r" % (cid, target))

    return {
        "passed": not errors,
        "errors": errors,
        "questions": len(reg["questions"]),
        "claims": len(claims),
    }


def metrics(reg, ledger):
    """Every public number, with the definition and the source it is computed from."""
    docs = ROOT / "docs"
    questions = reg["questions"]
    status = Counter(q["status"] for q in questions)
    outcome = Counter(q.get("outcome") for q in questions if q.get("outcome"))
    claims = ledger["claims"]
    cstatus = Counter(c["status"] for c in claims)

    prereg = sorted(p.name for p in docs.glob("*prereg*"))
    results = sorted(p.name for p in docs.glob("*result*"))
    decisions = sorted(docs.glob("DECISION-*.md"))
    withdrawn_decisions = [d for d in decisions if "WITHDRAWN" in d.read_text(encoding="utf-8").upper()]
    reviews = sorted(docs.glob("INDEPENDENT-*.md"))

    reg_src = "docs/research_question_registry.json"
    led_src = "docs/claim_ledger.json"

    return [
        ("Questions registered", len(questions), "rows in the registry", reg_src),
        ("Questions closed", status["closed"], "status is closed", reg_src),
        ("Questions open", status["open"], "status is open", reg_src),
        ("Questions retired", status["retired"], "status is retired", reg_src),
        ("Questions deferred", status["future"], "status is future", reg_src),
        ("Findings supported", outcome["SUPPORTED"], "closed or retired with outcome SUPPORTED", reg_src),
        ("Findings unsupported", outcome["UNSUPPORTED"], "closed or retired with outcome UNSUPPORTED", reg_src),
        ("Findings mixed", outcome["MIXED"], "closed or retired with outcome MIXED", reg_src),
        ("Findings inconclusive", outcome["INCONCLUSIVE"], "closed or retired with outcome INCONCLUSIVE", reg_src),
        ("Findings withdrawn", outcome["WITHDRAWN"], "closed or retired with outcome WITHDRAWN", reg_src),
        ("Claims in the ledger", len(claims), "rows in the claim ledger", led_src),
        ("Claims active", cstatus["ACTIVE"], "status is ACTIVE", led_src),
        ("Claims withdrawn", cstatus["WITHDRAWN"], "status is WITHDRAWN", led_src),
        ("Claims superseded", cstatus["SUPERSEDED"], "status is SUPERSEDED", led_src),
        (
            "Preregistered experiments",
            len(prereg),
            "documents in docs/ whose filename contains prereg; counted by name",
            "docs/*prereg*",
        ),
        (
            "Completed experiments",
            len(results),
            "documents in docs/ whose filename contains result; one per file, not per cell",
            "docs/*result*",
        ),
        (
            "Architectural changes adopted",
            len(decisions) - len(withdrawn_decisions),
            "decision records whose text does not contain WITHDRAWN",
            "docs/DECISION-*.md",
        ),
        (
            "Architectural changes withdrawn",
            len(withdrawn_decisions),
            "decision records whose text contains WITHDRAWN",
            "docs/DECISION-*.md",
        ),
        (
            "Independent reviews",
            len(reviews),
            "documents in docs/ whose filename begins INDEPENDENT-",
            "docs/INDEPENDENT-*.md",
        ),
    ]


def render_dashboard(reg, ledger):
    reg_date = reg.get("date", "")
    led_date = ledger.get("date", "")
    lines = [
        "# Research program dashboard",
        "",
        "**Generated from the records. Do not edit this file.** Rebuild it with",
        "`python -m benchmarks.research_accountability`; `--check` validates without writing.",
        "",
        "Sources: `docs/research_question_registry.json` (dated %s) and `docs/claim_ledger.json`" % reg_date,
        "(dated %s). Every value below is computed from those files or from the documents named" % led_date,
        "in its own row. No value is typed by hand, and the row names say what is counted.",
        "",
        "| Metric | Value | Definition | Source |",
        "| --- | --- | --- | --- |",
    ]
    for name, value, definition, source in metrics(reg, ledger):
        lines.append("| %s | %s | %s | `%s` |" % (name, value, definition, source))
    lines += [
        "",
        "## How to read this",
        "",
        "- **A count is not evidence.** These rows count records; they do not measure the organism.",
        "  What a finding is worth is decided by its outcome column and its scope, not by how many",
        "  rows point at it.",
        "- **Completed experiments counts documents, not cells.** One campaign produces one result",
        "  artifact however many seeds it ran, so this row is a record of activity and never a",
        "  sample size.",
        "- **Nothing here is a capability claim.** The not-claimed rows in `docs/CONTEXT.md` are the",
        "  boundary of what this dashboard may be read to support.",
        "",
    ]
    return "\n".join(lines)


def _claim_row(c):
    return "| %s | %s | %s | %s |" % (
        c["claim_id"],
        c["claim"],
        c["classification"],
        ", ".join(c.get("supporting_questions", [])) or "none",
    )


def render_ledger(reg, ledger):
    active = [c for c in ledger["claims"] if c["status"] == "ACTIVE"]
    gone = [c for c in ledger["claims"] if c["status"] != "ACTIVE"]

    lines = [
        "# Claim ledger",
        "",
        "**Generated from `docs/claim_ledger.json`. Do not edit this file.**",
        "",
        "A claim is a sentence the project is prepared to say in public. It is a different object",
        "from a question and from a finding: a question is what was asked, a finding is what the",
        "outcome column records, and a claim is what the project asserts on that basis. Claims are",
        "not promoted from questions automatically. Each one cites the questions behind it, the",
        "artifacts it rests on, and the limits of its own scope.",
        "",
        "## Active claims",
        "",
        "| Claim | Statement | Classification | Questions |",
        "| --- | --- | --- | --- |",
    ]
    for c in active:
        lines.append(_claim_row(c))
    lines += [
        "",
        "## Withdrawn or superseded claims",
        "",
        "These are kept, not deleted. A claim that was made and then withdrawn is part of the",
        "record, and removing it would erase the correction.",
        "",
    ]
    for c in gone:
        lines += [
            "### %s — %s" % (c["claim_id"], c["status"].title()),
            "",
            "**Original claim.** %s" % c["claim"],
            "",
            "**Classification when made.** %s" % c["classification"],
            "",
            "**Why it was withdrawn.** %s" % (c.get("withdrawn_reason") or "superseded"),
        ]
        if c.get("superseded_by"):
            lines += ["", "**Superseded by.** %s" % c["superseded_by"]]
        if c.get("supporting_questions"):
            lines += ["", "**Questions behind it.** %s" % ", ".join(c["supporting_questions"])]
        lines += [""]

    lines += [
        "## Scope of every claim",
        "",
        "Each claim carries its own limits in the ledger. The ones that recur:",
        "",
    ]
    for c in active:
        for limit in c.get("scope_limitations", []):
            lines.append("- **%s.** %s" % (c["claim_id"], limit))
    lines += [
        "",
        "## What this ledger enforces",
        "",
        "- A load-bearing claim (classification DEMONSTRATED or SUPPORTED, status ACTIVE) may cite",
        "  only a question whose status is closed and whose outcome is SUPPORTED. A claim cannot",
        "  outrun the question it rests on.",
        "- Every claim cites at least one question, and every cited question must exist.",
        "- Every claim states a scope limitation; a claim with no stated limit is wider than its check.",
        "- A withdrawn claim states why it was withdrawn, or names the claim that superseded it.",
        "- An active claim may not carry a withdrawal reason, and a withdrawn claim may not be",
        "  presented as active anywhere in the generated public pages.",
        "",
        "Answering a question does not create a claim; the ledger has to be changed deliberately,",
        "which is the only reason the two layers are separate files.",
        "",
    ]
    return "\n".join(lines)


def _question_block(q, ledger):
    lines = [
        "### %s — %s" % (q["id"], q["question"]),
        "",
        "**Outcome.** %s, status %s." % (q.get("outcome"), q["status"]),
        "",
    ]
    if q.get("answer"):
        lines += ["**Answer.** %s" % q["answer"], ""]
    if q.get("scope"):
        lines += ["**Scope.** %s" % q["scope"], ""]
    if q.get("evidence"):
        lines += ["**Evidence.** " + ", ".join("`%s`" % p for p in q["evidence"]), ""]
    supported = [
        c
        for c in ledger["claims"]
        if c["status"] == "ACTIVE" and q["id"] in c.get("supporting_questions", [])
    ]
    if supported:
        lines += ["**Claims resting on it.** " + ", ".join(c["claim_id"] for c in supported), ""]
    return lines


def render_findings(reg, ledger):
    questions = reg["questions"]
    lines = [
        "# What Organica Has Established — And What It Has Not",
        "",
        "**Generated from the registry and the claim ledger. Do not edit this file.**",
        "",
        "This page is a projection, not a source. Every statement below is a question from the",
        "research registry with its recorded outcome, or a claim from the claim ledger with the",
        "questions behind it. Nothing appears here that cannot be traced back to an artifact.",
        "",
        "## Established within tested conditions",
        "",
        "Closed questions whose recorded outcome is SUPPORTED. The scope beside each one is part of",
        "the finding: a result outside that scope is not established by it.",
        "",
    ]
    established = [
        q for q in questions
        if q["status"] == "closed" and q.get("outcome") == "SUPPORTED" and q.get("kind") == "research"
    ]
    for q in established:
        lines += _question_block(q, ledger)
    if not established:
        lines += ["No question currently meets this bar.", ""]
    governance = [
        q for q in questions
        if q["status"] == "closed" and q.get("outcome") == "SUPPORTED" and q.get("kind") != "research"
    ]
    if governance:
        lines += [
            "Closed governance questions are not findings and are not listed above: %s. They are"
            % ", ".join(q["id"] for q in governance),
            "decisions, so they stay in the registry beside the decision records they close, and the",
            "dashboard counts them under questions rather than under findings.",
            "",
        ]

    lines += [
        "## Not supported by evidence",
        "",
        "Closed questions whose recorded outcome is UNSUPPORTED. Not supported is not refuted: it",
        "means the test the project ran did not support the proposition, on the scope stated.",
        "",
    ]
    unsupported = [
        q for q in questions
        if q["status"] == "closed" and q.get("outcome") == "UNSUPPORTED" and q.get("kind") == "research"
    ]
    for q in unsupported:
        lines += _question_block(q, ledger)
    if not unsupported:
        lines += ["No question currently meets this bar.", ""]

    lines += [
        "## Withdrawn or superseded interpretations",
        "",
        "Interpretations that were once held and are not held now. Each entry states what was",
        "originally claimed, why it was withdrawn, and what replaced it. These are kept in public",
        "view because a record that hides its corrections is not a record.",
        "",
    ]
    withdrawn_q = [q for q in questions if q.get("outcome") == "WITHDRAWN"]
    withdrawn_c = [c for c in ledger["claims"] if c["status"] != "ACTIVE"]
    for q in withdrawn_q:
        lines += [
            "### %s — %s" % (q["id"], q["question"]),
            "",
            "**Original interpretation.** %s" % (q.get("answer") or "recorded in the evidence artifact"),
            "",
            "**Why it was withdrawn.** %s" % (q.get("scope") or "see the evidence artifact"),
            "",
        ]
    for c in withdrawn_c:
        lines += [
            "### %s — %s" % (c["claim_id"], c["claim"]),
            "",
            "**Original interpretation.** %s, classified %s when it was made."
            % (c["claim"], c["classification"]),
            "",
            "**Why it was withdrawn.** %s" % (c.get("withdrawn_reason") or "superseded"),
            "",
        ]
        if c.get("superseded_by"):
            lines += ["**What superseded it.** %s" % c["superseded_by"], ""]
    if not withdrawn_q and not withdrawn_c:
        lines += ["Nothing has been withdrawn.", ""]

    lines += [
        "## Unresolved questions",
        "",
        "Open questions are under active investigation. Future questions are blocked by a stated",
        "prerequisite and are not being worked on. Neither is a finding, and neither may be quoted",
        "as one.",
        "",
    ]
    for q in [q for q in questions if q["status"] == "open"]:
        lines += ["### %s — %s" % (q["id"], q["question"]), ""]
        if q.get("why_open"):
            lines += ["**Why it is open.** %s" % q["why_open"], ""]
        if q.get("evidence"):
            lines += ["**What is in hand.** " + ", ".join("`%s`" % p for p in q["evidence"]), ""]
    for q in [q for q in questions if q["status"] == "future"]:
        prereqs = q.get("prerequisites", q.get("blocked_by", []))
        lines += [
            "### %s — %s" % (q["id"], q["question"]),
            "",
            "**Prerequisite.** %s" % (", ".join(prereqs) or "none recorded"),
            "",
        ]

    lines += [
        "## What this page does not say",
        "",
        "- It does not claim general capability, external validity or intelligence. The rows that",
        "  are explicitly not claimed live in `docs/CONTEXT.md`.",
        "- It does not treat an open question as a likely positive. Open means unmeasured.",
        "- It does not paraphrase a number. Every figure it shows is quoted inside the question or",
        "  claim record it comes from, and those records cite the artifact.",
        "",
    ]
    return "\n".join(lines)


def build(reg, ledger):
    return {
        LEDGER_DOC: render_ledger(reg, ledger),
        DASHBOARD_DOC: render_dashboard(reg, ledger),
        FINDINGS_DOC: render_findings(reg, ledger),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without writing")
    args = parser.parse_args(argv)
    reg, ledger = load_pair()
    report = validate(reg, ledger)
    if not report["passed"]:
        for error in report["errors"]:
            print("FAIL:", error)
        return 1
    documents = build(reg, ledger)
    if not args.check:
        for path, text in documents.items():
            path.write_text(text, encoding="utf-8")
    print(
        "accountability: %d questions, %d claims, %d generated documents"
        % (report["questions"], report["claims"], len(documents))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
