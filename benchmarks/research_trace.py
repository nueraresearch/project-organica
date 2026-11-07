"""Trace a claim or a question back to its evidence, and derive the work queue.

Three records already exist: the question registry (``docs/research_question_registry.json``),
the claim ledger (``docs/claim_ledger.json``) and the bottleneck map
(``docs/bottleneck_map.json``). Each is validated and rendered on its own. None of them answers
the question a reader asks between campaigns -- *why do we believe this, what would change our
mind, and what is worth doing next?* -- because the answer is a join across all three, and a join
done in prose is done differently every time it is done.

This module is that join, and it is read-only. It adds no fourth record and no field to the other
three: every value it prints is a row of a record, a path that either exists or does not, or a
derivation from those. In particular there is no stored ``next_action`` -- a stored one would be
a fourth thing to keep current, and the queue it would hold is exactly what the records already
imply.

    python -m benchmarks.research_trace --check          # drift: exit 1 on any finding
    python -m benchmarks.research_trace --claim C004     # why do we believe this?
    python -m benchmarks.research_trace --question Q012  # what is this waiting on?
    python -m benchmarks.research_trace --next           # the derived work queue
    python -m benchmarks.research_trace --decision <id>  # a recorded decision and its rejection
    python -m benchmarks.research_trace --provenance   # what each statement rests on
    python -m benchmarks.research_trace                  # a summary of both

``--check`` never writes, and it is the part that earns the rest: three of the four drift rules
below can fail on a record that every existing validator passes, because they range over pairs
the other layers check one at a time -- a claim against the current state of a question that
contradicts it, a future question against whether its blocker has since closed, and a future
question against whether its blocker can still close at all.

The gate also runs the bottleneck map's provenance tags (``benchmarks/provenance.py``): a row
tagged as a reading it did not make, or as an inference standing in for one, fails here too, so a
row cannot be retagged into stronger evidence than the record behind it supports.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import decision_graph as dg
from benchmarks import provenance
from benchmarks import research_accountability as ra

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "research_question_registry.json"
LEDGER = ROOT / "docs" / "claim_ledger.json"
MAP = ROOT / "docs" / "bottleneck_map.json"


# ---------------------------------------------------------------------------
# Loading and the two predicates everything below is built from
# ---------------------------------------------------------------------------


def load_records():
    """Load the three records this module joins."""
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    mapdoc = json.loads(MAP.read_text(encoding="utf-8"))
    return reg, ledger, mapdoc


def questions_by_id(reg):
    return {q["id"]: q for q in reg["questions"]}


def claims_by_id(ledger):
    return {c["claim_id"]: c for c in ledger["claims"]}


def rows_by_name(mapdoc):
    return {row["candidate"]: row for row in mapdoc["rows"]}


def prerequisites(q) -> list:
    """The gate a `future` question waits on, under either field name the records use."""
    return list(q.get("prerequisites", q.get("blocked_by", [])))


def answered(q) -> bool:
    """A question is answered positively only when it is closed and its outcome is SUPPORTED.

    Closed-and-UNSUPPORTED is settled too, but it settles the *negative*: it licenses no claim
    and it unblocks nothing, so it is not the predicate any rule below wants.
    """
    return q is not None and q["status"] == "closed" and q.get("outcome") == "SUPPORTED"


def dead(q) -> bool:
    """A question that will never change again in the direction a blocker needs."""
    return q is not None and (q["status"] == "retired" or q.get("outcome") == "WITHDRAWN")


# ---------------------------------------------------------------------------
# Drift: the four joins that no single layer can check
# ---------------------------------------------------------------------------


def drift(reg, ledger, mapdoc=None) -> list:
    """Return the findings a reader would otherwise have to notice by re-reading three files.

    Each finding is a dict with ``code``, ``subject`` and ``message``. The codes are stable so a
    reader can grep for one, and every message names the record it came from.
    """
    questions = questions_by_id(reg)
    findings = []

    for claim in ledger["claims"]:
        if claim["status"] != "ACTIVE":
            continue
        cid = claim["claim_id"]

        # A contradiction that has since become evidence. The claim was recorded while the
        # contradicting question was open, which is legitimate; it is not legitimate once that
        # question closes SUPPORTED and the claim is still ACTIVE and unamended.
        for qid in claim.get("contradicting_questions", []):
            q = questions.get(qid)
            if answered(q):
                findings.append(
                    {
                        "code": "claim-contradicted",
                        "subject": cid,
                        "message": (
                            "%s is ACTIVE but its contradicting question %s is now closed "
                            "SUPPORTED; reclassify the claim, record the split, or withdraw it"
                            % (cid, qid)
                        ),
                    }
                )

        # Support that was removed. A load-bearing claim is already checked against this in
        # `research_accountability`, but a HYPOTHESIS is not, and a hypothesis loses its footing
        # the same way when the question under it is retired.
        for qid in claim.get("supporting_questions", []):
            q = questions.get(qid)
            if dead(q):
                findings.append(
                    {
                        "code": "claim-support-gone",
                        "subject": cid,
                        "message": (
                            "%s is ACTIVE but rests on %s, which is %s; the support was removed "
                            "and the claim has not been reconsidered"
                            % (cid, qid, q["status"] if q["status"] == "retired" else "WITHDRAWN")
                        ),
                    }
                )

    for q in reg["questions"]:
        if q["status"] != "future":
            continue
        gate = prerequisites(q)
        if not gate:
            continue
        resolved = [pid for pid in gate if answered(questions.get(pid))]
        if len(resolved) == len(gate):
            findings.append(
                {
                    "code": "blocker-stale",
                    "subject": q["id"],
                    "message": (
                        "%s is still marked future, but every prerequisite is now closed SUPPORTED "
                        "(%s); the gate opened and the status did not"
                        % (q["id"], ", ".join(gate))
                    ),
                }
            )
            continue
        gone = [pid for pid in gate if dead(questions.get(pid))]
        if gone:
            findings.append(
                {
                    "code": "blocker-dead",
                    "subject": q["id"],
                    "message": (
                        "%s waits on %s, which can no longer close positively; the question is "
                        "dead rather than deferred and should be retired with its reason"
                        % (q["id"], ", ".join(gone))
                    ),
                }
            )

    return findings


# ---------------------------------------------------------------------------
# The derived work queue
# ---------------------------------------------------------------------------


def work_queue(reg, ledger, decisions=None) -> dict:
    """What the records imply is worth doing next, in buckets that lead to different work.

    Nothing here is a recommendation about the organism. It is a reading of the records: a
    question whose blocker has closed, a question with no registered experiment, and a claim
    holding a live contradiction.
    """
    questions = questions_by_id(reg)
    open_questions = [q for q in reg["questions"] if q["status"] == "open"]

    uncovered = [q["id"] for q in open_questions if not q.get("preregistrations")]
    unregistered = [q["id"] for q in open_questions if not q.get("evidence")]

    unblocked = [
        q["id"]
        for q in reg["questions"]
        if q["status"] == "future"
        and prerequisites(q)
        and all(answered(questions.get(pid)) for pid in prerequisites(q))
    ]
    deadlocked = [
        q["id"]
        for q in reg["questions"]
        if q["status"] == "future" and any(dead(questions.get(pid)) for pid in prerequisites(q))
    ]

    contested = [
        c["claim_id"]
        for c in ledger["claims"]
        if c["status"] == "ACTIVE"
        and any(
            not answered(questions.get(qid)) and not dead(questions.get(qid))
            for qid in c.get("contradicting_questions", [])
        )
    ]

    return {
        "unblocked": unblocked,
        "uncovered": uncovered,
        "unregistered": unregistered,
        "deadlocked": deadlocked,
        "contested": contested,
        "pending_decisions": dg.pending(decisions) if decisions is not None else [],
    }


def render_next(reg, ledger, decisions=None) -> str:
    queue = work_queue(reg, ledger, decisions)
    blocked = [q["id"] for q in reg["questions"] if q["status"] == "future"]

    lines = [
        "# The derived work queue",
        "",
        "Every line below is read from the registry or the ledger. Nothing is stored: change a",
        "record and the queue changes.",
        "",
        "## Unblocked — the gate has opened",
        "",
    ]
    if queue["unblocked"]:
        for qid in queue["unblocked"]:
            q = questions_by_id(reg)[qid]
            lines += [
                "- **%s** — %s" % (qid, q["question"]),
                "  Prerequisite met: %s. Promote it to open unchanged, or record why the blocker "
                "was not sufficient." % ", ".join(prerequisites(q)),
            ]
    else:
        lines += [
            "None. Every future question still waits on a prerequisite that has not closed "
            "SUPPORTED (%s)." % (", ".join(blocked) or "no future questions"),
        ]

    lines += [
        "",
        "## Open and uncovered — no experiment registered",
        "",
        "These have evidence in hand and no `preregistrations` entry. That is a fact about the",
        "record, not a judgement that an experiment is the right next move: some of them may be",
        "answerable from artifacts already on disk, and the deliverable then is a re-reading.",
        "",
    ]
    if queue["uncovered"]:
        for qid in queue["uncovered"]:
            lines.append("- **%s** — %s" % (qid, questions_by_id(reg)[qid]["question"]))
    else:
        lines.append("None: every open question has a preregistration.")

    lines += [
        "",
        "## Recorded and not in force — pending decisions",
        "",
        "A decision the record says is licensed and not implemented. This is a queue item with an",
        "owner already attached, not a suggestion.",
        "",
    ]
    if queue["pending_decisions"]:
        lines += ["- **%s**" % did for did in queue["pending_decisions"]]
    else:
        lines.append("None.")

    lines += [
        "",
        "## Consumed by nothing — dead blockers",
        "",
    ]
    if queue["deadlocked"]:
        lines += ["- %s — a prerequisite can no longer close positively" % qid for qid in queue["deadlocked"]]
    else:
        lines.append("None.")

    lines += [
        "",
        "## Contested — an active claim with a contradiction that is still open",
        "",
        "The claim may be correct and the contradiction unresolved; what this row says is that the",
        "contradiction is recorded and has not been answered, so the claim is not the whole story.",
        "",
    ]
    if queue["contested"]:
        for cid in queue["contested"]:
            c = claims_by_id(ledger)[cid]
            lines.append(
                "- **%s** (%s) — contradicted by %s"
                % (cid, c["classification"], ", ".join(c.get("contradicting_questions", [])))
            )
    else:
        lines.append("None.")

    lines += [""]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Traces
# ---------------------------------------------------------------------------


def _path_line(path) -> str:
    return "present" if (ROOT / path).exists() else "MISSING"


def trace_claim(cid, reg, ledger, mapdoc) -> str:
    """Why do we believe this, what does it rest on, and what would change our mind?"""
    claim = claims_by_id(ledger).get(cid)
    if claim is None:
        return "no such claim: %s" % cid
    questions = questions_by_id(reg)
    rows = rows_by_name(mapdoc)

    lines = [
        "%s — %s" % (cid, claim["claim"]),
        "classification %s, status %s" % (claim["classification"], claim["status"]),
        "",
    ]
    if claim.get("withdrawn_reason"):
        lines += ["withdrawn because: %s" % claim["withdrawn_reason"], ""]
    if claim.get("superseded_by"):
        lines += ["superseded by: %s" % claim["superseded_by"], ""]

    lines += ["supporting questions"]
    if not claim.get("supporting_questions"):
        lines += ["  none recorded"]
    for qid in claim.get("supporting_questions", []):
        q = questions.get(qid)
        if q is None:
            lines += ["  %s — NOT IN THE REGISTRY" % qid, ""]
            continue
        lines += [
            "  %s — %s" % (qid, q["question"]),
            "    status %s, outcome %s" % (q["status"], q.get("outcome")),
        ]
        if q.get("scope"):
            lines += ["    scope: %s" % q["scope"]]
        for path in q.get("evidence", []):
            lines += ["    evidence: %s (%s)" % (path, _path_line(path))]
        for name in q.get("decisions", []):
            path = "docs/%s" % name
            lines += ["    decision: %s (%s)" % (path, _path_line(path))]
        for name in q.get("bottleneck_rows", []):
            row = rows.get(name)
            lines += ["    bottleneck row: %s" % name]
            if row is not None:
                lines += ["      would change: %s" % row["would_change"]]
        lines += [""]

    lines += ["contradicting questions"]
    if not claim.get("contradicting_questions"):
        lines += ["  none recorded"]
    for qid in claim.get("contradicting_questions", []):
        q = questions.get(qid)
        if q is None:
            lines += ["  %s — NOT IN THE REGISTRY" % qid]
        else:
            lines += [
                "  %s — %s (status %s, outcome %s)"
                % (qid, q["question"], q["status"], q.get("outcome"))
            ]
    lines += [""]

    lines += ["scope limits"]
    for limit in claim.get("scope_limitations", []):
        lines += ["  - %s" % limit]

    found = [f for f in drift(reg, ledger, mapdoc) if f["subject"] == cid]
    lines += ["", "drift"]
    lines += ["  %s" % f["message"] for f in found] or ["  none"]

    return "\n".join(lines) + "\n"


def trace_question(qid, reg, ledger, mapdoc) -> str:
    """What is this waiting on, what does it rest on, and what does it block?"""
    q = questions_by_id(reg).get(qid)
    if q is None:
        return "no such question: %s" % qid
    questions = questions_by_id(reg)
    rows = rows_by_name(mapdoc)
    gate = prerequisites(q)

    lines = [
        "%s — %s" % (qid, q["question"]),
        "kind %s, status %s, outcome %s" % (q.get("kind"), q["status"], q.get("outcome")),
        "",
    ]
    if q.get("answer"):
        lines += ["answer: %s" % q["answer"], ""]
    if q.get("why_open"):
        lines += ["why open: %s" % q["why_open"], ""]
    if q.get("scope"):
        lines += ["scope: %s" % q["scope"], ""]

    lines += ["prerequisites"]
    if gate:
        for pid in gate:
            p = questions.get(pid)
            if p is None:
                lines += ["  %s — NOT IN THE REGISTRY" % pid]
            else:
                lines += [
                    "  %s — %s (status %s, outcome %s)"
                    % (pid, p["question"], p["status"], p.get("outcome"))
                ]
    else:
        lines += ["  none recorded"]
    lines += [""]

    lines += ["evidence"]
    for path in q.get("evidence", []):
        lines += ["  %s (%s)" % (path, _path_line(path))]
    if not q.get("evidence"):
        lines += ["  none recorded"]
    lines += [""]

    lines += ["preregistrations"]
    for path in q.get("preregistrations", []):
        lines += ["  %s (%s)" % (path, _path_line(path))]
    if not q.get("preregistrations"):
        lines += ["  none recorded"]
    lines += [""]

    lines += ["decision records"]
    for name in q.get("decisions", []):
        lines += ["  docs/%s (%s)" % (name, _path_line("docs/%s" % name))]
    if not q.get("decisions"):
        lines += ["  none recorded"]
    lines += [""]

    lines += ["bottleneck rows"]
    for name in q.get("bottleneck_rows", []):
        row = rows.get(name)
        lines += ["  %s — status %s" % (name, ", ".join(row["status"])) if row else "  %s — NOT IN THE MAP" % name]
        if row is not None:
            lines += ["    would change: %s" % row["would_change"]]
    if not q.get("bottleneck_rows"):
        lines += ["  none recorded"]
    lines += [""]

    lines += ["claims resting on it"]
    resting = [
        c
        for c in ledger["claims"]
        if qid in c.get("supporting_questions", []) or qid in c.get("contradicting_questions", [])
    ]
    for c in resting:
        lines += ["  %s (%s, %s) — %s" % (c["claim_id"], c["classification"], c["status"], c["claim"])]
    if not resting:
        lines += ["  none"]
    lines += [""]

    blocks = [other["id"] for other in reg["questions"] if qid in prerequisites(other)]
    lines += ["blocks"]
    lines += ["  %s — %s" % (bid, questions[bid]["question"]) for bid in blocks] or ["  none"]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def summary(reg, ledger, mapdoc, decisions=None) -> str:
    queue = work_queue(reg, ledger, decisions)
    findings = drift(reg, ledger, mapdoc)
    statuses = {}
    for q in reg["questions"]:
        statuses[q["status"]] = statuses.get(q["status"], 0) + 1
    lines = [
        "%d questions (%s), %d claims (%d active)"
        % (
            len(reg["questions"]),
            ", ".join("%s %d" % (k, statuses[k]) for k in sorted(statuses)),
            len(ledger["claims"]),
            sum(1 for c in ledger["claims"] if c["status"] == "ACTIVE"),
        ),
        "drift findings: %d" % len(findings),
        "unblocked %d, open and uncovered %d, dead blockers %d, contested claims %d, pending decisions %d"
        % (
            len(queue["unblocked"]),
            len(queue["uncovered"]),
            len(queue["deadlocked"]),
            len(queue["contested"]),
            len(queue["pending_decisions"]),
        ),
        "",
        "python -m benchmarks.research_trace --next | --claim <id> | --question <id> | --decision <id> | --check",
    ]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim", metavar="ID", help="trace one claim back to its evidence")
    parser.add_argument("--question", metavar="ID", help="trace one question to its gate and evidence")
    parser.add_argument("--decision", metavar="ID", help="trace one recorded decision and its rejection")
    parser.add_argument("--next", action="store_true", help="print the derived work queue")
    parser.add_argument(
        "--provenance",
        action="store_true",
        help="what each statement rests on: the map's tags and the figures that do not trace",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift and exit 1 on any finding; never writes",
    )
    args = parser.parse_args(argv)

    reg, ledger, mapdoc = load_records()
    report = ra.validate(reg, ledger)
    if not report["passed"]:
        for error in report["errors"]:
            print("FAIL:", error)
        return 1

    if args.check:
        findings = drift(reg, ledger, mapdoc)
        decisions = dg.load()
        decision_report = dg.validate(decisions, reg)
        if not decision_report["passed"]:
            for error in decision_report["errors"]:
                print("FAIL:", error)
            return 1
        findings += dg.drift(decisions, reg)
        findings += provenance.check_map(mapdoc, ROOT)
        findings += provenance.check_ledger(ledger, ROOT)
        findings += provenance.check_claims(ledger, ROOT)
        problem = dg.stale(decisions, reg, decision_report)
        if problem:
            print("FAIL:", problem)
            return 1
        for finding in findings:
            print("FAIL: %s: %s" % (finding["subject"], finding["message"]))
        print("drift findings:", len(findings))
        return 1 if findings else 0

    if args.claim:
        if args.claim not in claims_by_id(ledger):
            print("no such claim: %s" % args.claim)
            return 1
        print(trace_claim(args.claim, reg, ledger, mapdoc))
        return 0

    if args.question:
        if args.question not in questions_by_id(reg):
            print("no such question: %s" % args.question)
            return 1
        print(trace_question(args.question, reg, ledger, mapdoc))
        return 0

    if args.decision:
        decisions = dg.load()
        if args.decision not in {d["decision_id"] for d in decisions["decisions"]}:
            print("no such decision: %s" % args.decision)
            return 1
        print(dg.trace(args.decision, decisions, reg))
        return 0

    if args.next:
        print(render_next(reg, ledger, dg.load()))
        return 0

    if args.provenance:
        print(provenance.render_report(mapdoc, ledger, dg.load(), ROOT))
        return 0

    print(summary(reg, ledger, mapdoc, dg.load()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
