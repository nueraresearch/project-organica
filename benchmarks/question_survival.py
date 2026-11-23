"""Which open questions still rest on a named build, and which rest on prose.

The engine-version audit (`docs/ENGINE-VERSION-AUDIT.md`) answered one question for the record
as a whole: *which artifacts name their build?* It did not answer it per question, and the
registry's ``status`` cannot: a question is ``open`` both when no cell has ever been run and when
the cells were run on a build that no longer exists. Those are different debts, and conflating
them is how "the answer changed across builds" stays invisible until someone re-runs it.

This module joins the two records and adds nothing else:

* every ``open`` and ``future`` question in ``docs/research_question_registry.json``;
* every evidence path it names, whether the path exists, and — for a JSON artifact — the build
  the artifact names (its own stamp, its nested provenance, or the engine-version audit's
  record of it, in that order);
* the decisions the question cites, and whether any is PENDING;
* the registry's own ``blocked_by`` prerequisite, for questions not yet askable.

The verdict per question is **derived** from those facts, never authored. The one authored thing
in the file is the state vocabulary and the precedence among its cases, which is a rule about
what counts as a debt, and is printed into the page so a reader can disagree with it:

    broken-evidence      a cited path does not exist; nothing can be read until it does
    prerequisite         blocked_by names a question, so the prerequisite is the debt
    governance-held      a cited decision is PENDING; the block is a decision, not a measurement
    answered-other-build the answer names a build and none of them is the pinned build
    answered-named-build the answer names at least one build, the pinned one among them
    answered-no-build    an answer is recorded and no cited artifact names any build
    open-with-evidence   no answer recorded, but evidence exists
    open-no-evidence     no answer and no evidence

``answered-no-build`` is deliberately not called stale: the artifact cannot say whether it is
old. The registry's prose often can (thirteen rows say the answer predates 0.12.0), and the page
reports that prose count separately rather than folding a statement into a measurement.

    python -m benchmarks.question_survival            # rebuild the artifact and the page
    python -m benchmarks.question_survival --check    # verify both against the registry

The page is generated from the artifact; the artifact is generated from the registry and the
tree. ``--check`` fails when either one drifts, and when a reviewed question disappears.
Standard library only; nothing here runs the engine or changes a status.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from benchmarks import engine_pin

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REGISTRY = DOCS / "research_question_registry.json"
DECISIONS = DOCS / "decisions.json"
AUDIT = DOCS / "engine_version_audit.json"
ARTIFACT = DOCS / "question_survival.json"
PAGE = DOCS / "question_survival.md"
REVIEWED = ("open", "future")

STATES = (
    "broken-evidence",
    "prerequisite",
    "governance-held",
    "answered-older-build",
    "answered-at-pin",
    "answered-no-build",
    "open-with-evidence",
    "open-no-evidence",
)

MEANINGS = {
    "broken-evidence": "a cited path does not exist, so the row cannot be read at all",
    "prerequisite": "blocked_by names another question; that question is the debt",
    "governance-held": "a cited decision is PENDING; the block is a decision, not a measurement",
    "answered-older-build": "the answer predates a later build by its own record, or names a build and none is the pin",
    "answered-at-pin": "the answer was not reopened, and a cited artifact names the pinned build",
    "answered-no-build": "an answer is recorded and no cited artifact names any build",
    "open-with-evidence": "no answer recorded, but at least one evidence path exists",
    "open-no-evidence": "no answer and no evidence path",
}


def decisions_by_stem(root=ROOT):
    path = Path(root) / "docs" / "decisions.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {d["decision_id"]: d.get("status") for d in data["decisions"]}


def audit_builds(root=ROOT):
    """The build the engine-version audit recorded for an artifact, by path."""
    path = Path(root) / "docs" / "engine_version_audit.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {entry["path"]: entry["engine_version"]
            for entry in data.get("artifacts_with_engine_version", [])}


def _stamps(record):
    """Every build a record names, from its own fields or its nested provenance."""
    if isinstance(record, list):
        found = set()
        for item in record:
            found |= _stamps(item)
        return found
    if not isinstance(record, dict):
        return set()
    found = set()
    version = record.get("engine_version")
    if isinstance(version, str) and version:
        found.add(version)
    provenance = record.get("provenance")
    if isinstance(provenance, dict):
        for key in ("git_describe", "engine_version"):
            value = provenance.get(key)
            if isinstance(value, str) and value:
                found.add(value)
    return found


def ref_builds(ref, root=ROOT, audited=None):
    """The builds a cited path names: the artifact first, the audit second, empty if neither."""
    audited = audit_builds(root) if audited is None else audited
    path = Path(root) / ref
    found = set()
    if path.suffix == ".json" and path.exists():
        try:
            found |= _stamps(json.loads(path.read_text(encoding="utf-8")))
        except ValueError:
            found = set()
    if ref in audited:
        found.add(audited[ref])
    return sorted(found)


def resolve_prereg(ref, root=ROOT):
    """A registration ref may be written with or without its directory; report which landed."""
    if (Path(root) / ref).exists():
        return "path"
    if (Path(root) / "docs" / ref).exists():
        return "docs-convention"
    return "missing"


def pin(root=ROOT):
    return engine_pin.package_version()


def classify(question, builds, missing, pending):
    """One state per question, by the precedence the module docstring prints.

    Pure, so the tests can drive every branch without touching the registry.
    """
    if missing:
        return "broken-evidence"
    if question.get("blocked_by"):
        return "prerequisite"
    if pending:
        return "governance-held"
    answered = bool(question.get("answer"))
    pinned = pin()
    if answered:
        if str(question.get("why_open", "")).startswith("Reopened"):
            return "answered-older-build"
        if builds and pinned in builds:
            return "answered-at-pin"
        if builds:
            return "answered-older-build"
        return "answered-no-build"
    if question.get("evidence"):
        return "open-with-evidence"
    return "open-no-evidence"


def rows(reg, root=ROOT):
    audited = audit_builds(root)
    statuses = decisions_by_stem(root)
    pinned = pin(root)
    out = []
    for question in reg["questions"]:
        if question["status"] not in REVIEWED:
            continue
        evidence = question.get("evidence") or []
        missing = [ref for ref in evidence if not (Path(root) / ref).exists()]
        builds = sorted({b for ref in evidence for b in ref_builds(ref, root, audited)})
        json_refs = [ref for ref in evidence if ref.endswith(".json")]
        named = [ref for ref in json_refs if ref_builds(ref, root, audited)]
        cited = [Path(name).stem for name in question.get("decisions") or []]
        pending = [d for d in cited if statuses.get(d) == "PENDING"]
        preregs = question.get("preregistrations") or []
        out.append({
            "id": question["id"],
            "status": question["status"],
            "question": question["question"],
            "state": classify(question, builds, missing, pending),
            "builds": builds,
            "builds_include_pin": pinned in builds,
            "evidence": len(evidence),
            "json_evidence": len(json_refs),
            "named_build": len(named),
            "missing": missing,
            "reopened_in_prose": str(question.get("why_open", "")).startswith("Reopened"),
            "answered": bool(question.get("answer")),
            "blocked_by": question.get("blocked_by") or [],
            "pending_decisions": pending,
            "preregistrations": [{"ref": ref, "resolved": resolve_prereg(ref, root)}
                                 for ref in preregs],
        })
    return out


def build(reg=None, root=ROOT):
    reg = reg or json.loads(Path(root, "docs/research_question_registry.json")
                            .read_text(encoding="utf-8"))
    reviewed = rows(reg, root)
    states = Counter(row["state"] for row in reviewed)
    json_refs = sum(row["json_evidence"] for row in reviewed)
    named = sum(row["named_build"] for row in reviewed)
    missing = sum(len(row["missing"]) for row in reviewed)
    reopened = sum(1 for row in reviewed if row["reopened_in_prose"])
    kept = {entry["id"] if isinstance(entry, dict) else entry
            for entry in reg.get("reopening", {}).get("kept_closed", [])}
    reopened_ids = {entry["id"] if isinstance(entry, dict) else entry
                    for entry in reg.get("reopening", {}).get("reopened", [])}
    never_open = [q["id"] for q in reg["questions"]
                  if q["status"] == "open" and q["id"] not in reopened_ids
                  and q["id"] not in kept]
    return {
        "kind": "question_survival",
        "date": "2026-11-09",
        "note": "Derived from the registry, the decisions index and the engine-version audit. "
                "No status is changed and no engine is run.",
        "pinned_version": pin(root),
        "populations": {
            "open": sum(1 for q in reg["questions"] if q["status"] == "open"),
            "future": sum(1 for q in reg["questions"] if q["status"] == "future"),
            "closed": sum(1 for q in reg["questions"] if q["status"] == "closed"),
            "retired": sum(1 for q in reg["questions"] if q["status"] == "retired"),
            "reviewed": len(reviewed),
            "reopened_by_the_sweep": len(reopened_ids),
            "open_and_never_closed": len(never_open),
            "reopened_in_prose": reopened,
        },
        "evidence": {
            "json_refs": json_refs,
            "named_build": named,
            "unnamed_build": json_refs - named,
            "missing_paths": [ref for row in reviewed for ref in row["missing"]],
            "missing_path_count": missing,
            "distinct_builds": sorted({b for row in reviewed for b in row["builds"]}),
        },
        "states": {state: states.get(state, 0) for state in STATES},
        "questions": reviewed,
    }


def render(record):
    pop = record["populations"]
    ev = record["evidence"]
    lines = [
        "# Question survival: which open questions rest on a named build",
        "",
        "**Generated** from `docs/research_question_registry.json`, `docs/decisions.json` and",
        "`docs/engine_version_audit.json` by `python -m benchmarks.question_survival`.",
        "Do not edit this file by hand; `--check` fails when the page, the artifact or the",
        "registry disagree.",
        "",
        "A question's `status` cannot say whether its evidence still describes the shipped",
        "engine: `open` covers both *never measured* and *measured on a build that no longer",
        "exists*. This page separates those, and changes no status.",
        "",
        "## Population",
        "",
        "| population | count |",
        "| --- | --- |",
        "| questions in the registry | %d |" % sum(
            pop[k] for k in ("open", "future", "closed", "retired")),
        "| open | %d |" % pop["open"],
        "| future | %d |" % pop["future"],
        "| closed | %d |" % pop["closed"],
        "| retired | %d |" % pop["retired"],
        "| **reviewed here (open + future)** | **%d** |" % pop["reviewed"],
        "",
        "The dashboard's narrower population is %d: the open questions the 2026-11-08 sweep "
        "neither\nreopened nor kept closed. The other %d were reopened by that sweep and are "
        "still open;\n%d of the reviewed questions say in their own `why_open` that the "
        "recorded answer\npredates a later build." % (
            pop["open_and_never_closed"], pop["reopened_by_the_sweep"], pop["reopened_in_prose"]),
        "",
        "## Evidence by build",
        "",
        "| quantity | count |",
        "| --- | --- |",
        "| JSON artifacts cited by reviewed questions | %d |" % ev["json_refs"],
        "| of those, naming a build | %d |" % ev["named_build"],
        "| of those, naming no build | %d |" % ev["unnamed_build"],
        "| cited paths that do not exist | %d |" % ev["missing_path_count"],
        "",
        "Builds named anywhere in the reviewed evidence: %s." % (
            ", ".join("`%s`" % b for b in ev["distinct_builds"]) or "none"),
        "Pinned build: `%s`." % record["pinned_version"],
        "",
        "## States",
        "",
        "| state | count | meaning |",
        "| --- | --- | --- |",
    ]
    for state in STATES:
        lines.append("| `%s` | %d | %s |" % (state, record["states"][state], MEANINGS[state]))
    lines += [
        "",
        "The order above is the precedence `classify()` applies. A row is assigned its first",
        "matching case, so a question that is both governed by a PENDING decision and older than",
        "the pin is reported as `governance-held`: the decision is what has to move first.",
        "",
        "`answered-older-build` is decided first from the row's own `why_open`: a reopened answer",
        "is an older answer by its own record, whatever build its cited artifacts name now. The",
        "builds column reports what those artifacts name today, not the build behind the answer.",
        "",
        "## The reviewed questions",
        "",
        "| id | status | state | builds named | JSON evidence named | reopened |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in record["questions"]:
        builds = ", ".join(row["builds"]) or "none"
        lines.append("| %s | %s | `%s` | %s | %d of %d | %s |" % (
            row["id"], row["status"], row["state"], builds, row["named_build"],
            row["json_evidence"], "yes" if row["reopened_in_prose"] else "no"))
    lines += [
        "",
        "## What this page does not say",
        "",
        "- **It does not close a question.** A status is the registry's to change, on evidence;",
        "  this page only reports what the evidence already names.",
        "- **It does not call an unnamed build old.** `answered-no-build` means the artifact",
        "  cannot say which build produced it, which is a different defect from a named older",
        "  build and needs a different repair (re-run versus re-read).",
        "- **It does not rank the questions.** The counts separate kinds of debt, not priorities.",
        "",
    ]
    return "\n".join(lines)


def stale(record=None, reg=None, root=ROOT):
    """Why the artifact or the page is out of date, or None when both match a rebuild."""
    expected = record or build(reg, root)
    for path, payload in ((Path(root) / "docs/question_survival.json", expected),
                          (Path(root) / "docs/question_survival.md", render(expected))):
        if not path.exists():
            return "missing: %s" % path.relative_to(root).as_posix()
    on_disk = json.loads((Path(root) / "docs/question_survival.json").read_text(encoding="utf-8"))
    if on_disk != expected:
        return "docs/question_survival.json is stale; rebuild with python -m benchmarks.question_survival"
    page = (Path(root) / "docs/question_survival.md").read_text(encoding="utf-8")
    if page != render(expected):
        return "docs/question_survival.md is stale; rebuild with python -m benchmarks.question_survival"
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify the artifact and the page without writing")
    args = parser.parse_args(argv)

    record = build()
    if record["evidence"]["missing_paths"]:
        for ref in record["evidence"]["missing_paths"]:
            print("FAIL: a reviewed question cites a path that does not exist:", ref)
        return 1
    if args.check:
        problem = stale(record)
        if problem:
            print("FAIL:", problem)
            return 1
    else:
        ARTIFACT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        PAGE.write_text(render(record), encoding="utf-8")
    print("questions: %d reviewed (%s)" % (
        record["populations"]["reviewed"],
        ", ".join("%s %d" % (state, record["states"][state]) for state in STATES
                  if record["states"][state])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
