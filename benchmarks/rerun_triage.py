"""Triage the reopened questions into re-runnable, needs-harness, decision-only and prose-only.

The registry's `reopening.reopened` list is the population. A row is **re-runnable** when a
frozen protocol resolves, a JSON comparator exists in its evidence, and a harness module exists;
**needs-harness** when code and a comparator exist but the protocol does not; **prose-only** when
the answer is a judgment with neither a protocol nor a dedicated harness.

Eight of the eleven re-runnable rows name at least one protocol without the `docs/` prefix. The
registry is not rewritten here: each path is resolved under `docs/`, and the resolution is
disclosed beside the path rather than silently corrected.

    ./.venv/bin/python -m benchmarks.rerun_triage
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "research_question_registry.json"

#: Eleven rows with a protocol, a JSON comparator and a harness. Q006 and Q021 are closed and excluded. The order is execution order.
RE_RUNNABLE = (
    "Q024",  # diversity-first admission, measured by the two-arm comparison
    "Q004",  # density exclusion, acquisition-bound trap
    "Q005",  # density padding, the primary scheme's partial pass
    "Q029",  # why the degree-12 structure disappears
    "Q030",  # whether temporal decay is the removal mechanism
    "Q031",  # when the fall begins and how long it takes
    "Q032",  # whether theory death causes the edge loss
    "Q036",  # the peak structure's half-life
    "Q044",  # admission count or ranked slot, on the attribution ledger
    "Q043",  # store-time role record, independent of the decay cluster
    "Q051",  # long-delay capability, last because it rests on Q024 and Q044
)

NEEDS_HARNESS = {}

DECISION_ONLY = {
    "Q017": ("the answer (No) is a judgment about whether to try more admission variants. Its "
             "protocol decides whether a variant build is warranted after Q006 and Q024; it has "
             "no dedicated harness and cannot run as a cell."),
}

PROSE_ONLY = {}

#: Modules that compute each row's endpoint. Every path must exist for the row to be runnable.
HARNESS = {
    "Q004": ("benchmarks/run_density_interaction.py", "benchmarks/score_density_interaction_a2.py"),
    "Q005": ("benchmarks/density_padding.py",),
    "Q024": ("benchmarks/run_ranking_admission.py", "benchmarks/score_ranking_admission.py"),
    "Q029": ("benchmarks/decay_attribution.py",),
    "Q030": ("benchmarks/decay_attribution.py",),
    "Q031": ("benchmarks/decay_attribution.py",),
    "Q032": ("benchmarks/decay_attribution.py",),
    "Q036": ("benchmarks/decay_attribution.py",),
    "Q043": ("benchmarks/store_time_role_durability.py",),
    "Q044": ("benchmarks/decay_admission_slot.py",),
    "Q051": ("benchmarks/long_delay_capability_confirm.py",
             "benchmarks/long_delay_capability_design.py"),
    "Q021": ("benchmarks/cross_context_reuse_benchmark.py",),
}

#: The comparator to use where the first JSON in evidence is a design or ledger, not the result.
COMPARATOR = {
    "Q044": "docs/decay_admission_slot.json",
    "Q051": "docs/long_delay_capability_confirm.json",
}


def registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def resolve(path: str) -> str | None:
    """Resolve a registry path, accepting the missing `docs/` prefix rather than editing it."""
    for candidate in (Path(path), ROOT / "docs" / path):
        if candidate.exists():
            return candidate.resolve().relative_to(ROOT).as_posix()
    return None


def _question(reg: dict, qid: str) -> dict:
    return next(q for q in reg["questions"] if q["id"] == qid)


def row(reg: dict, qid: str, bucket: str) -> dict:
    question = _question(reg, qid)
    protocols = []
    for raw in question.get("preregistrations") or []:
        resolved = resolve(raw)
        if resolved:
            protocols.append({"path": resolved, "registry_path": raw})
    comparator = COMPARATOR.get(qid)
    if comparator is None:
        for evidence in question.get("evidence") or []:
            if evidence.endswith(".json") and (ROOT / evidence).exists():
                comparator = evidence
                break
    harnesses = [path for path in HARNESS.get(qid, ()) if (ROOT / path).exists()]
    return {
        "id": qid,
        "bucket": bucket,
        "question": question["question"],
        "protocols": protocols,
        "comparator": comparator,
        "harnesses": harnesses,
        "reason": NEEDS_HARNESS.get(qid) or PROSE_ONLY.get(qid) or "",
    }


def triage(reg: dict, split: dict[str, set[str]] | None = None) -> dict[str, dict]:
    split = split or buckets()
    rows = {}
    for bucket in ("re-runnable", "needs-harness", "decision-only", "prose-only"):
        for qid in split.get(bucket, set()):
            rows[qid] = row(reg, qid, bucket)
    return rows


def buckets() -> dict[str, set[str]]:
    return {
        "re-runnable": set(RE_RUNNABLE),
        "needs-harness": set(NEEDS_HARNESS),
        "decision-only": set(DECISION_ONLY),
        "prose-only": set(PROSE_ONLY),
    }


def problems(reg: dict, split: dict[str, set[str]] | None = None) -> list[str]:
    """Everything the registry, the files and the declared buckets contradict."""
    split = split or buckets()
    found: list[str] = []
    reopened = set(reg["reopening"]["reopened"])
    covered: set[str] = set()
    for name, ids in split.items():
        if covered & ids:
            found.append("%s is in more than one bucket" % sorted(covered & ids))
        covered |= ids
    if covered != reopened:
        found.append("the buckets cover %s, the registry reopened %s"
                     % (sorted(covered), sorted(reopened)))
    if set(RE_RUNNABLE) != set(split.get("re-runnable", ())):
        found.append("the execution order is not the re-runnable set")
    if set(NEEDS_HARNESS) != set(split.get("needs-harness", ())):
        found.append("the declared needs-harness rows moved")
    if set(DECISION_ONLY) != set(split.get("decision-only", ())):
        found.append("the declared decision-only rows moved")
    if set(PROSE_ONLY) != set(split.get("prose-only", ())):
        found.append("the declared prose-only rows moved")

    rows = triage(reg, split)
    for qid, entry in rows.items():
        if entry["bucket"] == "re-runnable":
            if not entry["protocols"]:
                found.append("%s has no resolving protocol" % qid)
            if not entry["comparator"]:
                found.append("%s has no JSON comparator" % qid)
            if not entry["harnesses"]:
                found.append("%s has no existing harness" % qid)
        elif entry["bucket"] == "needs-harness":
            if entry["protocols"]:
                found.append("%s has a protocol and is not needs-harness" % qid)
            if not entry["harnesses"] or not entry["comparator"]:
                found.append("%s is missing code as well as a protocol" % qid)
        elif entry["bucket"] == "decision-only":
            if not entry["protocols"]:
                found.append("%s has no decision protocol" % qid)
            if entry["harnesses"]:
                found.append("%s has a harness and is not decision-only" % qid)
        else:
            if entry["protocols"] or entry["harnesses"]:
                found.append("%s has a protocol or harness and is not prose-only" % qid)
    return found


def render(reg: dict) -> str:
    rows = triage(reg)
    lines = ["# Reopened-question triage", ""]
    for bucket in ("re-runnable", "needs-harness", "decision-only", "prose-only"):
        lines.append("## %s" % bucket)
        lines.append("")
        for qid, entry in rows.items():
            if entry["bucket"] != bucket:
                continue
            lines.append("- **%s** — %s" % (qid, entry["question"]))
            if entry["protocols"]:
                lines.append("  protocol: %s" % ", ".join(p["path"] for p in entry["protocols"]))
            if entry["comparator"]:
                lines.append("  comparator: %s" % entry["comparator"])
            if entry["harnesses"]:
                lines.append("  harness: %s" % ", ".join(entry["harnesses"]))
            if entry["reason"]:
                lines.append("  why: %s" % entry["reason"])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    reg = registry()
    found = problems(reg)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print(render(reg))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
