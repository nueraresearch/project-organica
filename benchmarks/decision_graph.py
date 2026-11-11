"""The decision graph: every recorded decision as an object, quoted from its own document.

The records already hold questions, findings, claims, artifacts and bottlenecks. The object that
kept being discussed in prose and nowhere else was the **decision** -- *we have enough evidence,
what should we do?* -- because ``docs/DECISION-*.md`` is a document, not a record: it can be read
and it cannot be queried, joined or checked against the rest of the tree.

This module adds the machine-readable index, and it adds nothing else. The document remains the
record; ``docs/decisions.json`` is an index *into* it. Three consequences shape the design:

* **Every prose claim in the index is a verbatim quote.** ``chosen``, ``rejected[].reason``,
  ``status_quote`` and ``date`` must appear in the document they are attributed to, compared on
  whitespace-normalised text. A paraphrase fails the validator, so the index cannot drift from the
  document it claims to describe -- the defect rule 27 records for a hand-transcribed table, aimed
  at prose. The one authored field is ``rejected[].alternative``, the index's own short label for
  the alternative the document names; the *reason* beside it is quoted.
* **The index is complete or it is wrong.** Every ``docs/DECISION-*.md`` on disk must have exactly
  one entry, and every entry must name a document that exists, so adding a decision without
  indexing it fails the suite instead of leaving a silent gap.
* **Reading a decision is not making one.** Nothing here creates, rewords or re-scores a decision.
  There is no ``rationale`` field: a summary of the reasoning would be the index's opinion, and the
  document is where the reasoning lives.

    python -m benchmarks.decision_graph --check     # validate + verify the page; never writes
    python -m benchmarks.decision_graph             # rebuild docs/DECISIONS.md
    python -m benchmarks.research_trace --decision DECISION-DENSITY-EXCLUSION

**Stop condition.** This build indexes the decisions that exist, and adds no decision, no
field beyond ``decision_id``, ``date``, ``status``, ``status_quote``, ``chosen``, ``rejected``,
``open_question``, ``evidence``, ``superseded_by``, and no query beyond the trace and the drift rule below. It may be
fixed if it is found wrong; it may not grow.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "docs" / "decisions.json"
DOC = ROOT / "docs" / "DECISIONS.md"
DOCS = ROOT / "docs"
REGISTRY = ROOT / "docs" / "research_question_registry.json"

STATUSES = ("ADOPTED", "WITHDRAWN", "PENDING")
#: A question in one of these states will not change again in a direction a live decision needs.
DEAD_QUESTION_STATUSES = ("retired", "future")


def normalise(text: str) -> str:
    """Collapse whitespace so a quote may be written on one line against a wrapped document."""
    return re.sub(r"\s+", " ", text).strip()


def load(path=None) -> dict:
    return json.loads(Path(path or DECISIONS).read_text(encoding="utf-8"))


def decision_docs() -> list:
    return sorted(p.name for p in DOCS.glob("DECISION-*.md"))


def doc_text(name: str) -> str:
    return normalise((DOCS / name).read_text(encoding="utf-8"))


def title_of(name: str) -> str:
    for line in (DOCS / name).read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return name


def decision_stem(name: str) -> str:
    """A decision document's id: its file name, without a leading path or the .md suffix."""
    base = Path(name).name
    return base[:-3] if base.endswith(".md") else base


def tallying_questions(reg, decision_id) -> list:
    """The questions whose records count this decision. Derived, never stored twice.

    The registry stores the document it closes (``DECISION-X.md``) and this index is keyed by the
    stem, so both are normalised rather than one being edited to match the other.
    """
    return [
        q["id"]
        for q in reg["questions"]
        if decision_id in {decision_stem(name) for name in q.get("decisions", [])}
    ]


def validate(data, reg) -> dict:
    """Check the index against the documents, and the documents against the index."""
    errors = []
    entries = data["decisions"]
    ids = [d.get("decision_id") for d in entries]

    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        errors.append("duplicate decision ids: %r" % (duplicates,))

    on_disk = set(decision_docs())
    for d in entries:
        did = d.get("decision_id", "?")
        name = "%s.md" % did
        if name not in on_disk:
            errors.append("%s: no such decision document: docs/%s" % (did, name))
        else:
            text = doc_text(name)
            quotes = [("status_quote", d.get("status_quote", ""))]
            if d.get("open_question"):
                quotes.append(("open_question", d["open_question"]))
            quotes += [("chosen", phrase) for phrase in d.get("chosen", [])]
            quotes += [("rejected.reason", r.get("reason", "")) for r in d.get("rejected", [])]
            for field, phrase in quotes:
                if not phrase:
                    errors.append("%s: empty %s" % (did, field))
                elif normalise(phrase) not in text:
                    errors.append(
                        "%s: %s is not a verbatim quote from docs/%s: %r"
                        % (did, field, name, phrase)
                    )
            if d.get("date") and normalise(d["date"]) not in text:
                errors.append("%s: date %r does not appear in docs/%s" % (did, d["date"], name))
        if d.get("status") not in STATUSES:
            errors.append("%s: unknown status %r" % (did, d.get("status")))
        if not d.get("chosen"):
            errors.append("%s: records no chosen action" % did)
        if not tallying_questions(reg, did):
            errors.append("%s: no question in the registry tallies this decision" % did)
        for path in d.get("evidence", []):
            if not (ROOT / path).exists():
                errors.append("%s: evidence path does not exist: %s" % (did, path))
        target = d.get("superseded_by")
        if target is not None and target not in ids:
            errors.append("%s: superseded_by does not name an indexed decision: %r" % (did, target))

    unindexed = sorted(on_disk - {"%s.md" % i for i in ids})
    if unindexed:
        errors.append("decision documents missing from the index: %r" % (unindexed,))
    missing = sorted({"%s.md" % i for i in ids} - on_disk)
    if missing:
        errors.append("indexed decision documents that are not on disk: %r" % (missing,))

    counts = {status: sum(1 for d in entries if d.get("status") == status) for status in STATUSES}
    return {"passed": not errors, "errors": errors, "decisions": len(entries), "counts": counts}


def drift(data, reg) -> list:
    """A decision in force whose questions are all retired or not yet askable."""
    questions = {q["id"]: q for q in reg["questions"]}
    findings = []
    for d in data["decisions"]:
        if d["status"] != "ADOPTED":
            continue
        tallied = tallying_questions(reg, d["decision_id"])
        if not tallied:
            continue
        live = [qid for qid in tallied if questions.get(qid, {}).get("status") not in DEAD_QUESTION_STATUSES]
        if not live:
            findings.append(
                {
                    "code": "decision-orphaned",
                    "subject": d["decision_id"],
                    "message": (
                        "%s is ADOPTED but every question that tallies it is retired or future "
                        "(%s); either the decision governs no live work or the question it belongs "
                        "to needs re-opening" % (d["decision_id"], ", ".join(tallied))
                    ),
                }
            )
    return findings


def pending(data) -> list:
    """Decisions that are recorded and not in force -- the one queue the documents keep."""
    return [d["decision_id"] for d in data["decisions"] if d["status"] == "PENDING"]


def trace(decision_id, data, reg) -> str:
    entry = next((d for d in data["decisions"] if d["decision_id"] == decision_id), None)
    if entry is None:
        return "no such decision: %s" % decision_id
    name = "%s.md" % decision_id
    lines = [
        "%s — %s" % (decision_id, title_of(name)),
        "status %s, recorded %s" % (entry["status"], entry.get("date", "undated")),
        "record: docs/%s" % name,
        "",
        "quoted status",
        "  %s" % entry["status_quote"],
    ]
    if entry.get("open_question"):
        lines += ["", "open question", "  %s" % entry["open_question"]]
    lines += [
        "",
        "chosen",
    ]
    lines += ["  - %s" % phrase for phrase in entry["chosen"]]
    lines += ["", "rejected"]
    if entry.get("rejected"):
        for r in entry["rejected"]:
            lines += ["  - %s" % r["alternative"], "    because: %s" % r["reason"]]
    else:
        lines += ["  none recorded in the document"]
    lines += ["", "questions that tally it"]
    for qid in tallying_questions(reg, decision_id):
        q = next(q for q in reg["questions"] if q["id"] == qid)
        lines += ["  %s (%s, %s) — %s" % (qid, q["status"], q.get("outcome"), q["question"])]
    lines += ["", "evidence"]
    for path in entry.get("evidence", []):
        lines += ["  %s (%s)" % (path, "present" if (ROOT / path).exists() else "MISSING")]
    if entry.get("superseded_by"):
        lines += ["", "superseded by %s" % entry["superseded_by"]]
    found = [f for f in drift(data, reg) if f["subject"] == decision_id]
    lines += ["", "drift"]
    lines += ["  %s" % f["message"] for f in found] or ["  none"]
    return "\n".join(lines) + "\n"


STATUS_MEANINGS = {
    "ADOPTED": "in force; the document records it as implemented or effective",
    "WITHDRAWN": "reversed by its own record; kept because a correction is part of the record",
    "PENDING": "decided and not in force; the document says so",
}


def render(data, reg, report=None) -> str:
    report = report or validate(data, reg)
    lines = [
        "# The decision graph",
        "",
        "**Generated** from `docs/decisions.json` by `python -m benchmarks.decision_graph`.",
        "Do not edit this file by hand. `--check` fails when the page, the index and the decision",
        "documents disagree.",
        "",
        "A question is what was asked, a finding is what the outcome recorded, a claim is what the",
        "project will say, and a **decision** is what it chose to do. The prose in",
        "`docs/DECISION-*.md` is the record; this page is an index into it. Every quoted line below",
        "is checked against the document it is attributed to, character for character on",
        "whitespace-normalised text, so the index cannot paraphrase the record.",
        "",
        "## Tally",
        "",
        "| status | count | meaning |",
        "| --- | --- | --- |",
    ]
    for status in STATUSES:
        lines.append(
            "| %s | %d | %s |" % (status, report["counts"][status], STATUS_MEANINGS[status])
        )
    lines += ["| **total** | **%d** | |" % report["decisions"], ""]

    lines += ["## The decisions", ""]
    for entry in data["decisions"]:
        did = entry["decision_id"]
        name = "%s.md" % did
        lines += ["### %s — %s" % (did, title_of(name)), ""]
        lines += ["**Status.** %s — *\"%s\"*" % (entry["status"], entry["status_quote"]), ""]
        if entry.get("open_question"):
            lines += ["**Open question.** *\"%s\"*" % entry["open_question"], ""]
        lines += ["**Decided.**", ""]
        lines += ["- %s" % phrase for phrase in entry["chosen"]]
        lines += [""]
        if entry.get("rejected"):
            lines += ["**Rejected.**", ""]
            for r in entry["rejected"]:
                lines += ["- *%s* — because *\"%s\"*" % (r["alternative"], r["reason"])]
            lines += [""]
        else:
            lines += [
                "**Rejected.** None recorded in the document. That is a gap in the record, not a",
                "statement that no alternative existed: a decision whose alternatives were never",
                "written down cannot be re-examined later.",
                "",
            ]
        tallied = tallying_questions(reg, did)
        if tallied:
            lines += ["**Rests on.** " + ", ".join("%s (%s)" % (qid, next(q for q in reg["questions"] if q["id"] == qid)["status"]) for qid in tallied), ""]
        if entry.get("evidence"):
            lines += ["**Evidence.** " + ", ".join("`%s`" % p for p in entry["evidence"]), ""]
        lines += ["**Record.** `docs/%s`" % name, ""]
        if entry.get("superseded_by"):
            lines += ["**Superseded by.** %s" % entry["superseded_by"], ""]

    lines += [
        "## What this graph is not",
        "",
        "- **Not a rationale.** The reasoning lives in the document. This index quotes what it says",
        "  and does not summarise it, because a summary is where a decision quietly becomes the",
        "  version that turned out to be convenient.",
        "- **Not a ranking.** A PENDING decision is not more important than an ADOPTED one; the",
        "  statuses say whether the choice is in force, not whether it was right.",
        "- **Not a re-scoring.** Withdrawing or keeping a decision is the owner's act. This page",
        "  reports the status each document states, quoted.",
        "",
    ]
    return "\n".join(lines)


def stale(data, reg, report=None):
    report = report or validate(data, reg)
    expected = render(data, reg, report)
    if not DOC.exists():
        return "the rendered decision graph does not exist: %s" % DOC
    if DOC.read_text(encoding="utf-8") != expected:
        return "%s is stale; rebuild with python -m benchmarks.decision_graph" % DOC
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate and verify the page, without writing")
    args = parser.parse_args(argv)

    data = load()
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    report = validate(data, reg)
    if not report["passed"]:
        for error in report["errors"]:
            print("FAIL:", error)
        return 1
    findings = drift(data, reg)
    for finding in findings:
        print("FAIL: %s: %s" % (finding["subject"], finding["message"]))
    if findings:
        return 1
    if args.check:
        problem = stale(data, reg, report)
        if problem:
            print("FAIL:", problem)
            return 1
    else:
        DOC.write_text(render(data, reg, report), encoding="utf-8")
    print(
        "decisions: %d (%s)"
        % (report["decisions"], ", ".join("%s %d" % (k, report["counts"][k]) for k in STATUSES))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
