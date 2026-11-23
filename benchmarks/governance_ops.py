"""Operational governance checks over the existing research records.

This is a control surface, not a seventh registry. Questions, claims, decisions, the constraint
ledger, seed reservations and run artifacts remain the sources of truth. The only authored facts
here are the operational ones no existing record carries: expiring waivers, dependency baselines,
review policy and an append-only event log. Everything else is derived on read.

    python -m benchmarks.governance_ops --write          # baseline dependency hashes
    python -m benchmarks.governance_ops --check          # all derived checks
    python -m benchmarks.governance_ops --preflight run  # before starting a run
    python -m benchmarks.governance_ops --preflight publish
    python -m benchmarks.governance_ops --queue
    python -m benchmarks.governance_ops --lottery
    python -m benchmarks.governance_ops --canary
    python -m benchmarks.governance_ops --ledger
    python -m benchmarks.governance_ops --portfolio
    python -m benchmarks.governance_ops --claims
    python -m benchmarks.governance_ops --waivers
    python -m benchmarks.governance_ops --events

The module runs no engine cell and writes no research result. `--write` only refreshes the
dependency baseline in `docs/governance_ops.json`.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from benchmarks import a1_seed_reservations
from benchmarks import decision_graph as dg
from benchmarks import engine_pin
from benchmarks import engine_stamp
from benchmarks import research_trace as rt

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OPS = DOCS / "governance_ops.json"

KIND = "governance_ops"
ID = "GOVERNANCE-OPS-1"
CLAIM_RE = re.compile(r"\bC\d{3}\b")
PREREG_RE = re.compile(r"(prereg|pre-registration)", re.IGNORECASE)
RESULT_RE = re.compile(r"(result|run|audit|study|feasibility|probe|availability)", re.IGNORECASE)

GOVERNANCE_DECISIONS = {
    "DECISION-V2-SCOPE",
    "DECISION-STAGE-B-SEQUENCE",
    "DECISION-ENGINE-EFFECT-STANDARD",
    "DECISION-UNCERTIFIED-RUN",
    "DECISION-0X-ENGINEERING-CHARTER",
    "DECISION-V2-CHARTER",
    "DECISION-V2-RUNTIME-FAILURE",
    "DECISION-V2-FIRST-CELL",
}

DEFAULT_POLICY = {
    "portfolio": {
        "question_review_days": 90,
        "constraint_review_days": 30,
        "max_open_questions": 35,
        "max_active_constraints": 4,
        "kill_or_park": "Keep only while a named decision can change the constraint; otherwise park it with a reason.",
    },
    "queue": {"stale_after_days": 30, "waiver_warning_days": 14},
    "public_documents": ["papers", "README.md", "docs/FACTS-SHEET.md"],
    "dependency_ignored": ["docs/USER-MANUAL.md"],
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_json(path: Path) -> dict | None:
    try:
        return _load(path)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def default_ops() -> dict:
    return {
        "kind": KIND,
        "id": ID,
        "date": "2026-11-17",
        "policy": json.loads(json.dumps(DEFAULT_POLICY)),
        "decision_classes": {},
        "implementations": {},
        "owners": {},
        "reviews": {"questions": {}, "constraints": {}},
        "waivers": [],
        "events": [],
        "runs": [
            {
                "id": "A1-TWO-PATH-1",
                "result": "docs/a1_two_path_result.json",
                "grant": "DECISION-V2-A4-BASE-WORLD",
                "prereg": "docs/A1-TWO-PATH-MANIFEST.md",
                "seed_label": "two-path candidate block, held for A1-TWO-PATH-1",
            },
            {
                "id": "V2-FIRST-CELL",
                "marker": "docs/v2_first_cell_run.json",
                "result": "docs/v2_first_cell_result.json",
                "grant": "DECISION-V2-FIRST-CELL",
                "prereg": "docs/V2-FIRST-EXPERIMENT-PREREGISTRATION.md",
                "seed_label": "first V2 cell, ten paired worlds",
            },
        ],
        "dependency_baseline": {},
    }


def ops() -> dict:
    """The operations record, or the defaults when it has not been created."""
    doc = _read_json(OPS)
    if not doc:
        return default_ops()
    base = default_ops()
    base.update(doc)
    base["policy"] = dict(DEFAULT_POLICY, **doc.get("policy", {}))
    return base


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _sha(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


_PREREG_CACHE = None


def _direct_prereg(name: str) -> str | None:
    for candidate in (ROOT / name, DOCS / name, DOCS / (name + ".md"), DOCS / (name + ".json")):
        if candidate.is_file():
            return _rel(candidate)
    return None


def resolve_prereg(name: str) -> str | None:
    """Resolve a preregistration path, bare filename or registration id to a document.

    The question registry uses all three forms. The resolver is deliberately read-only and
    accepts a document only when its own `prereg`, `id` or `registration` field names it.
    """
    global _PREREG_CACHE
    if not name:
        return None
    direct = _direct_prereg(name)
    if direct:
        return direct
    if _PREREG_CACHE is None:
        found: dict[str, list[tuple[int, str]]] = {}
        for path in sorted(list(DOCS.glob("*.json")) + list((DOCS / "constraint_registrations").glob("*.json"))):
            payload = _read_json(path)
            if not isinstance(payload, dict):
                continue
            rel = _rel(path)
            for field in ("prereg",):
                value = payload.get(field)
                if not isinstance(value, str) or not value:
                    continue
                linked = _direct_prereg(value) if value.endswith((".json", ".md")) else None
                score = 0 if "prereg" in path.name.lower() else 2
                found.setdefault(value, []).append((score, linked or rel))
            for field in ("id", "registration", "name"):
                value = payload.get(field)
                if isinstance(value, str) and value:
                    score = 0 if "prereg" in path.name.lower() else 1
                    found.setdefault(value, []).append((score, rel))
        _PREREG_CACHE = {key: sorted(values)[0][1] for key, values in found.items()}
    return _PREREG_CACHE.get(name)


def _date(value, field="date") -> date:
    if not isinstance(value, str):
        raise ValueError("%s must be an ISO date" % field)
    return datetime.strptime(value, "%Y-%m-%d").date()


def _age(value, today: date) -> int:
    try:
        return max(0, (today - _date(value)).days)
    except (TypeError, ValueError):
        return 0


def _records():
    reg, ledger, mapdoc = rt.load_records()
    decisions = dg.load()
    return reg, ledger, decisions, mapdoc


# ---------------------------------------------------------------------------
# Dependencies and invalidation
# ---------------------------------------------------------------------------


def dependency_paths() -> dict[str, list[str]]:
    """The artifact edges the existing records already declare."""
    reg, ledger, decisions, mapdoc = _records()
    ignored = set(ops().get("policy", {}).get("dependency_ignored", []))
    paths: dict[str, list[str]] = {}
    for claim in ledger["claims"]:
        paths["claim:" + claim["claim_id"]] = [
            path for path in claim.get("supporting_evidence", []) if path not in ignored]
    for decision in decisions["decisions"]:
        paths["decision:" + decision["decision_id"]] = [
            path for path in decision.get("evidence", []) if path not in ignored]
    for question in reg["questions"]:
        for prereg in question.get("preregistrations", []):
            resolved = resolve_prereg(prereg)
            if resolved:
                paths["prereg:" + prereg] = [resolved]
    for row in mapdoc["constraint_ledger"]["rows"]:
        key = "constraint:" + row["constraint"]
        names = []
        if row.get("registration"):
            names.append(row["registration"])
        for field in ("result", "decision"):
            if row.get(field):
                names.append(row[field])
        paths[key] = names
    return paths


def dependency_baseline() -> dict:
    records = {}
    for name, names in sorted(dependency_paths().items()):
        records[name] = {path: _sha(ROOT / path) for path in names}
    return {"engine_sha256": engine_stamp.engine_sha256(), "records": records}


def write_dependency_baseline(path: Path = OPS) -> int:
    doc = ops()
    doc["dependency_baseline"] = dependency_baseline()
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return len(doc["dependency_baseline"]["records"])


def dependency_findings(ops_doc: dict | None = None) -> list[dict]:
    doc = ops_doc or ops()
    baseline = doc.get("dependency_baseline") or {}
    if not baseline:
        return [{"code": "unbaselined", "subject": "dependency-baseline",
                 "message": "no dependency baseline; run --write once"}]
    findings = []
    current_engine = engine_stamp.engine_sha256()
    if baseline.get("engine_sha256") != current_engine:
        findings.append({
            "code": "engine-changed",
            "subject": "engine",
            "message": "the pinned engine changed; every measured claim and decision needs review",
        })
    saved = baseline.get("records") or {}
    current = dependency_paths()
    for name, paths in sorted(current.items()):
        previous = saved.get(name)
        if previous is None:
            findings.append({"code": "unbaselined", "subject": name,
                             "message": "%s has no dependency baseline" % name})
            continue
        for path in paths:
            if path not in previous:
                findings.append({"code": "unbaselined", "subject": name,
                                 "message": "%s gained a dependency with no baseline: %s" % (name, path)})
            elif not (ROOT / path).exists():
                findings.append({"code": "missing", "subject": name,
                                 "message": "%s depends on a missing artifact: %s" % (name, path)})
            elif _sha(ROOT / path) != previous[path]:
                findings.append({"code": "needs-review", "subject": name,
                                 "message": "%s depends on a changed artifact: %s" % (name, path)})
        for path in previous:
            if path not in paths:
                findings.append({"code": "dropped", "subject": name,
                                 "message": "%s no longer declares a baselined dependency: %s" % (name, path)})
    return findings


# ---------------------------------------------------------------------------
# Decision classes, evidence bars and implementation
# ---------------------------------------------------------------------------


def decision_class(entry: dict, ops_doc: dict | None = None) -> str:
    doc = ops_doc or ops()
    override = (doc.get("decision_classes") or {}).get(entry["decision_id"])
    if override:
        return override
    if entry["decision_id"] in GOVERNANCE_DECISIONS:
        return "governance"
    evidence = [str(path) for path in entry.get("evidence", [])]
    if any(RESULT_RE.search(path) for path in evidence):
        return "experiment-backed"
    if any(PREREG_RE.search(path) for path in evidence):
        return "preregistration"
    return "governance"


def _implementation(entry: dict, cls: str, ops_doc: dict) -> dict:
    override = (ops_doc.get("implementations") or {}).get(entry["decision_id"])
    if override:
        return override
    evidence = [str(path) for path in entry.get("evidence", [])]
    if cls == "experiment-backed":
        for path in evidence:
            if RESULT_RE.search(path):
                return {"kind": "artifact", "ref": path}
        return {"kind": "missing", "ref": ""}
    if cls == "preregistration":
        for path in evidence:
            if PREREG_RE.search(path):
                return {"kind": "preregistration", "ref": path}
        return {"kind": "missing", "ref": ""}
    return {"kind": "no_code_change", "ref": "docs/%s.md" % entry["decision_id"],
            "reason": "governance decision; the decision record is the implementation"}


def class_counts(ops_doc: dict | None = None) -> dict[str, int]:
    doc = ops_doc or ops()
    counts = {}
    for entry in dg.load()["decisions"]:
        cls = decision_class(entry, doc)
        counts[cls] = counts.get(cls, 0) + 1
    return counts


def decision_findings(ops_doc: dict | None = None) -> list[dict]:
    doc = ops_doc or ops()
    findings = []
    for entry in dg.load()["decisions"]:
        cls = decision_class(entry, doc)
        if cls not in ("experiment-backed", "governance", "preregistration"):
            findings.append({"code": "unknown-class", "subject": entry["decision_id"],
                             "message": "%s has unknown class %r" % (entry["decision_id"], cls)})
            continue
        implementation = _implementation(entry, cls, doc)
        if implementation.get("kind") == "missing":
            findings.append({"code": "not-implemented", "subject": entry["decision_id"],
                             "message": "%s is %s but has no %s evidence path" % (entry["decision_id"], cls, cls)})
            continue
        ref = str(implementation.get("ref") or "")
        if implementation.get("kind") in ("artifact", "preregistration", "record", "no_code_change"):
            if not ref or not (ROOT / ref).exists():
                findings.append({"code": "implementation-missing", "subject": entry["decision_id"],
                                 "message": "%s names a missing implementation record: %s" % (entry["decision_id"], ref)})
        elif implementation.get("kind") == "commit":
            if not re.fullmatch(r"[0-9a-f]{40}", ref):
                findings.append({"code": "implementation-invalid", "subject": entry["decision_id"],
                                 "message": "%s names a commit that is not 40 hex characters" % entry["decision_id"]})
        elif implementation.get("kind") == "no_code_change":
            if not str(implementation.get("reason") or "").strip():
                findings.append({"code": "implementation-invalid", "subject": entry["decision_id"],
                                 "message": "%s claims no code change without a reason" % entry["decision_id"]})
        else:
            findings.append({"code": "implementation-invalid", "subject": entry["decision_id"],
                             "message": "%s has no recognized implementation kind" % entry["decision_id"]})
    return findings


# ---------------------------------------------------------------------------
# Waivers
# ---------------------------------------------------------------------------


def waiver_findings(ops_doc: dict | None = None, today: date | None = None) -> list[dict]:
    doc = ops_doc or ops()
    today = today or date.today()
    findings = []
    seen = set()
    for waiver in doc.get("waivers", []):
        wid = str(waiver.get("id") or "<unnamed>")
        if wid in seen:
            findings.append({"code": "duplicate-waiver", "subject": wid,
                             "message": "waiver id is duplicated"})
        seen.add(wid)
        for field in ("scope", "owner", "reason", "expires"):
            if not str(waiver.get(field) or "").strip():
                findings.append({"code": "waiver-incomplete", "subject": wid,
                                 "message": "waiver has no %s" % field})
        try:
            expires = _date(waiver.get("expires"), "expires")
        except ValueError as exc:
            findings.append({"code": "waiver-invalid", "subject": wid, "message": str(exc)})
            continue
        if expires < today:
            findings.append({"code": "waiver-expired", "subject": wid,
                             "message": "waiver expired on %s" % expires.isoformat()})
        for path in waiver.get("records", []):
            if not (ROOT / path).exists():
                findings.append({"code": "waiver-missing-record", "subject": wid,
                                 "message": "waiver names a missing record: %s" % path})
    return findings


# ---------------------------------------------------------------------------
# Claim usage and publication gate
# ---------------------------------------------------------------------------


def public_documents(ops_doc: dict | None = None) -> list[Path]:
    doc = ops_doc or ops()
    found = []
    for item in doc.get("policy", {}).get("public_documents", []):
        path = ROOT / item
        if path.is_dir():
            found.extend(sorted(path.rglob("*.md")))
        elif path.is_file():
            found.append(path)
    return sorted(set(found))


def claim_usage(ops_doc: dict | None = None, ledger: dict | None = None) -> dict[str, list[str]]:
    doc = ops_doc or ops()
    ledger = ledger or rt.load_records()[1]
    known = {claim["claim_id"] for claim in ledger["claims"]}
    usage = {claim_id: [] for claim_id in known}
    for path in public_documents(doc):
        text = path.read_text(encoding="utf-8")
        for claim_id in sorted(set(CLAIM_RE.findall(text))):
            usage.setdefault(claim_id, []).append(_rel(path))
    return {key: sorted(value) for key, value in sorted(usage.items()) if value}


def claim_usage_findings(ops_doc: dict | None = None) -> list[dict]:
    doc = ops_doc or ops()
    ledger = rt.load_records()[1]
    claims = {claim["claim_id"]: claim for claim in ledger["claims"]}
    findings = []
    for claim_id, documents in claim_usage(doc, ledger).items():
        claim = claims.get(claim_id)
        if claim is None:
            findings.append({"code": "unknown-claim", "subject": claim_id,
                             "message": "public documents cite a claim absent from the ledger: %s"
                                        % ", ".join(documents)})
        elif claim["status"] != "ACTIVE":
            findings.append({"code": "inactive-claim", "subject": claim_id,
                             "message": "public documents cite a %s claim: %s"
                                        % (claim["status"].lower(), ", ".join(documents))})
    return findings


# ---------------------------------------------------------------------------
# Claim-chain audit, lottery and canaries
# ---------------------------------------------------------------------------


def claim_chain(claim: dict, reg: dict, ledger: dict | None = None) -> list[dict]:
    ledger = ledger or {"claims": [claim]}
    questions = {q["id"]: q for q in reg.get("questions", [])}
    findings = []
    for question_id in claim.get("supporting_questions", []):
        question = questions.get(question_id)
        if question is None:
            findings.append({"code": "broken-chain", "subject": claim["claim_id"],
                             "message": "supporting question %s is not in the registry" % question_id})
            continue
        for prereg in question.get("preregistrations", []):
            if not resolve_prereg(prereg):
                findings.append({"code": "broken-chain", "subject": claim["claim_id"],
                                 "message": "%s names a missing preregistration %s" % (question_id, prereg)})
        for decision in question.get("decisions", []):
            if not (DOCS / decision).exists():
                findings.append({"code": "broken-chain", "subject": claim["claim_id"],
                                 "message": "%s names a missing decision record %s" % (question_id, decision)})
    for path in claim.get("supporting_evidence", []):
        if not (ROOT / path).exists():
            findings.append({"code": "broken-chain", "subject": claim["claim_id"],
                             "message": "supporting evidence is missing: %s" % path})
    return findings


def lottery(today: date | None = None, count: int = 3) -> dict:
    today = today or date.today()
    week = today.strftime("%G-W%V")
    claims = [claim for claim in rt.load_records()[1]["claims"] if claim["status"] == "ACTIVE"]
    ordered = sorted(claims, key=lambda claim: hashlib.sha256(
        ("%s:%s" % (week, claim["claim_id"])).encode("utf-8")).hexdigest())
    sample = ordered[:max(1, min(count, len(ordered)))]
    findings = []
    for claim in sample:
        findings.extend(claim_chain(claim, rt.load_records()[0]))
    return {"week": week, "sampled": [claim["claim_id"] for claim in sample], "findings": findings}


def canary_problems() -> list[str]:
    """Proof that the chain auditor can fail; returns the problems with the canary itself."""
    problems = []
    reg = {"questions": []}
    orphan = {"claim_id": "C999", "supporting_questions": ["Q999"], "supporting_evidence": []}
    if not claim_chain(orphan, reg):
        problems.append("an orphan claim was accepted")
    reg = {"questions": [{"id": "Q999", "preregistrations": ["docs/no-such-prereg.json"],
                          "decisions": []}]}
    broken = {"claim_id": "C999", "supporting_questions": ["Q999"], "supporting_evidence": []}
    if not claim_chain(broken, reg):
        problems.append("a missing preregistration was accepted")
    if not waiver_findings({"waivers": [{"id": "W1", "scope": "x", "owner": "x",
                                         "reason": "x", "expires": "2000-01-01", "records": []}]}):
        problems.append("an expired waiver was accepted")
    return problems


# ---------------------------------------------------------------------------
# Owner queue
# ---------------------------------------------------------------------------


def owner_queue(ops_doc: dict | None = None, today: date | None = None) -> list[dict]:
    doc = ops_doc or ops()
    today = today or date.today()
    reg, ledger, decisions, mapdoc = _records()
    items = []
    owners = doc.get("owners") or {}

    for entry in decisions["decisions"]:
        if entry["status"] != "PENDING":
            continue
        items.append({
            "kind": "decision", "id": entry["decision_id"],
            "date": entry.get("date", ""), "age": _age(entry.get("date"), today),
            "owner": owners.get(entry["decision_id"], "owner"),
            "default": "hold" if entry.get("open_question") else "decide or hold",
        })

    for waiver in doc.get("waivers", []):
        try:
            expires = _date(waiver.get("expires"), "expires")
        except ValueError:
            continue
        if expires <= today + timedelta(days=int(doc["policy"]["queue"]["waiver_warning_days"])):
            items.append({
                "kind": "waiver", "id": waiver.get("id", "<unnamed>"),
                "date": expires.isoformat(), "age": max(0, (today - expires).days),
                "owner": waiver.get("owner", "owner"),
                "default": "renew or expire",
            })

    for finding in dependency_findings(doc):
        if finding["code"] not in ("needs-review", "missing"):
            continue
        items.append({
            "kind": "claim-or-decision", "id": finding["subject"],
            "date": "", "age": 0, "owner": owners.get(finding["subject"], "owner"),
            "default": "review before reuse",
        })

    for question in reg["questions"]:
        if question["status"] != "open" or question.get("preregistrations"):
            continue
        items.append({
            "kind": "question", "id": question["id"],
            "date": reg.get("date", ""), "age": _age(reg.get("date"), today),
            "owner": owners.get(question["id"], "owner"),
            "default": "hold or register an experiment",
        })

    for row in mapdoc["constraint_ledger"]["rows"]:
        if row["state"] not in ("open", "in-test") or row.get("registration"):
            continue
        items.append({
            "kind": "constraint", "id": row["constraint"],
            "date": mapdoc["constraint_ledger"].get("date", ""),
            "age": _age(mapdoc["constraint_ledger"].get("date"), today),
            "owner": owners.get(row["constraint"], "owner"),
            "default": "hold until instrumented",
        })

    return sorted(items, key=lambda item: (-item["age"], item["kind"], item["id"]))


def render_queue(items: list[dict], today: date | None = None) -> str:
    today = today or date.today()
    lines = ["# Owner action queue — %s" % today.isoformat(), ""]
    if not items:
        lines.append("No item needs the owner this week.")
    for item in items:
        lines.append("- **%s %s** — %s; age %d days; default: **%s**"
                     % (item["kind"], item["id"], item["owner"], item["age"], item["default"]))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Run, seed and grant ledger
# ---------------------------------------------------------------------------


def run_ledger(ops_doc: dict | None = None) -> dict:
    doc = ops_doc or ops()
    seeds = []
    for row in a1_seed_reservations.reservations():
        seeds.append({
            "label": row["label"], "owner": row["owner"],
            "seeds": row["seeds"], "count": len(row["seeds"]),
            "status": "spent" if row["spent"] else "held",
        })
    runs = []
    for entry in doc.get("runs", []):
        result = ROOT / entry["result"] if entry.get("result") else None
        marker = ROOT / entry["marker"] if entry.get("marker") else None
        status = "UNRUN"
        if result is not None and result.exists():
            payload = _read_json(result) or {}
            status = payload.get("status", "COMPLETED")
        elif marker is not None and marker.exists():
            payload = _read_json(marker) or {}
            status = payload.get("status", "STARTED")
        runs.append({
            "id": entry["id"], "status": status,
            "seed_label": entry.get("seed_label", ""),
            "grant": entry.get("grant", ""),
            "prereg": entry.get("prereg", ""),
            "result": entry.get("result", ""),
        })
    run_by_label = {run["seed_label"]: run for run in runs if run.get("seed_label")}
    stranded = []
    for block in seeds:
        if block["status"] != "spent" or block["label"] in run_by_label:
            continue
        if re.search(r"(diagnostic|dry run|calibration|no cell|control)", block["label"], re.IGNORECASE):
            continue
        stranded.append(block["label"])
    return {"seeds": seeds, "runs": runs, "stranded": stranded}


def run_ledger_findings(ops_doc: dict | None = None) -> list[dict]:
    ledger = run_ledger(ops_doc)
    findings = []
    seen = {}
    for block in ledger["seeds"]:
        for seed in block["seeds"]:
            if seed in seen:
                findings.append({"code": "seed-collision", "subject": str(seed),
                                 "message": "seed %d is in both %s and %s"
                                            % (seed, seen[seed], block["label"])})
            seen[seed] = block["label"]
    return findings


def render_ledger(ledger: dict) -> str:
    lines = ["# Run, seed and grant ledger", "", "## Seed blocks", ""]
    for block in ledger["seeds"]:
        lines.append("- **%s** — %s, %d seeds, owner `%s`"
                     % (block["label"], block["status"], block["count"], block["owner"]))
    lines += ["", "## Runs", ""]
    for run in ledger["runs"]:
        lines.append("- **%s** — %s; grant `%s`; prereg `%s`"
                     % (run["id"], run["status"], run["grant"], run["prereg"]))
    if ledger.get("stranded"):
        lines += ["", "## Spent blocks with no declared run", ""]
        for label in ledger["stranded"]:
            lines.append("- %s" % label)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Portfolio review
# ---------------------------------------------------------------------------


def _review_date(base: str, days: int) -> str:
    try:
        return (_date(base) + timedelta(days=days)).isoformat()
    except (TypeError, ValueError):
        return ""


def portfolio(ops_doc: dict | None = None, today: date | None = None) -> dict:
    doc = ops_doc or ops()
    today = today or date.today()
    policy = doc["policy"]["portfolio"]
    reg, _ledger, _decisions, mapdoc = _records()
    questions = []
    for question in reg["questions"]:
        if question["status"] not in ("open", "future"):
            continue
        override = (doc.get("reviews", {}).get("questions") or {}).get(question["id"], {})
        review_by = override.get("review_by") or _review_date(
            reg.get("date", ""), int(policy["question_review_days"]))
        questions.append({"id": question["id"], "status": question["status"],
                          "review_by": review_by,
                          "kill_or_park": override.get("kill_or_park") or policy["kill_or_park"]})
    constraints = []
    for row in mapdoc["constraint_ledger"]["rows"]:
        if row["state"] not in ("open", "in-test"):
            continue
        override = (doc.get("reviews", {}).get("constraints") or {}).get(row["constraint"], {})
        review_by = override.get("review_by") or _review_date(
            mapdoc["constraint_ledger"].get("date", ""), int(policy["constraint_review_days"]))
        constraints.append({"id": row["constraint"], "state": row["state"],
                            "review_by": review_by,
                            "kill_or_park": override.get("kill_or_park") or policy["kill_or_park"]})
    return {"date": today.isoformat(), "questions": questions, "constraints": constraints,
            "policy": policy}


def portfolio_findings(ops_doc: dict | None = None, today: date | None = None) -> list[dict]:
    today = today or date.today()
    view = portfolio(ops_doc, today)
    findings = []
    policy = view["policy"]
    active_questions = [row for row in view["questions"] if row["status"] == "open"]
    if len(active_questions) > int(policy["max_open_questions"]):
        findings.append({"code": "wip-exceeded", "subject": "questions",
                         "message": "%d active questions exceed the WIP limit of %d"
                                    % (len(active_questions), int(policy["max_open_questions"]))})
    if len(view["constraints"]) > int(policy["max_active_constraints"]):
        findings.append({"code": "wip-exceeded", "subject": "constraints",
                         "message": "%d active constraints exceed the WIP limit of %d"
                                    % (len(view["constraints"]), int(policy["max_active_constraints"]))})
    for row in view["questions"] + view["constraints"]:
        if not row["review_by"]:
            findings.append({"code": "review-missing", "subject": row["id"],
                             "message": "%s has no review date" % row["id"]})
        elif _date(row["review_by"]) < today:
            findings.append({"code": "review-overdue", "subject": row["id"],
                             "message": "%s was due for review on %s" % (row["id"], row["review_by"])})
    return findings


# ---------------------------------------------------------------------------
# Append-only governance events
# ---------------------------------------------------------------------------


def append_event(event: dict, path: Path = OPS) -> dict:
    """Append one event after validating the whole stream; never rewrite an earlier event."""
    doc = ops()
    doc.setdefault("events", []).append(dict(event))
    findings = event_findings(doc)
    if findings:
        raise ValueError("; ".join(item["message"] for item in findings))
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return event


def event_findings(ops_doc: dict | None = None) -> list[dict]:
    doc = ops_doc or ops()
    findings = []
    seen = set()
    previous = None
    for event in doc.get("events", []):
        eid = str(event.get("id") or "<unnamed>")
        if eid in seen:
            findings.append({"code": "duplicate-event", "subject": eid, "message": "event id is duplicated"})
        seen.add(eid)
        for field in ("date", "actor", "record", "from", "to", "reason"):
            if not str(event.get(field) or "").strip():
                findings.append({"code": "event-incomplete", "subject": eid,
                                 "message": "event has no %s" % field})
        try:
            when = _date(event.get("date"), "event date")
        except ValueError as exc:
            findings.append({"code": "event-invalid", "subject": eid, "message": str(exc)})
            continue
        if previous is not None and when < previous:
            findings.append({"code": "event-order", "subject": eid,
                             "message": "event is dated before the preceding event"})
        previous = when
        for path in event.get("artifacts", []):
            if not (ROOT / path).exists():
                findings.append({"code": "event-missing-artifact", "subject": eid,
                                 "message": "event names a missing artifact: %s" % path})
    return findings


# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------


def _capture(fn) -> tuple[bool, str]:
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            code = fn()
    except SystemExit as exc:
        code = exc.code
    except Exception as exc:  # a failed check is a failed preflight, not a traceback
        return False, "%s: %s" % (type(exc).__name__, exc)
    return (code in (0, None)), out.getvalue().strip()


def _suite_check() -> tuple[bool, str]:
    result = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q"],
                            cwd=ROOT, capture_output=True, text=True)
    tail = (result.stdout or "").strip().splitlines()
    return result.returncode == 0, (tail[-1] if tail else "pytest produced no output")


def _prereg_check() -> tuple[bool, str]:
    reg, _ledger, _decisions, mapdoc = _records()
    missing = []
    for question in reg["questions"]:
        for path in question.get("preregistrations", []):
            if not resolve_prereg(path):
                missing.append(path)
    for row in mapdoc["constraint_ledger"]["rows"]:
        if row.get("registration") and not (ROOT / row["registration"]).exists():
            missing.append(row["registration"])
    return not missing, ("missing preregistrations: " + ", ".join(sorted(set(missing)))
                         if missing else "all declared preregistrations exist")


def _grant_check() -> tuple[bool, str]:
    """Every declared run with a result must name an adopted grant and an existing prereg."""
    decisions = {entry["decision_id"]: entry for entry in dg.load()["decisions"]}
    doc = ops()
    missing = []
    checked = 0
    for run in doc.get("runs", []):
        result = ROOT / run["result"] if run.get("result") else None
        if result is None or not result.exists():
            continue
        checked += 1
        grant = decisions.get(run.get("grant"))
        if grant is None or grant.get("status") != "ADOPTED":
            missing.append("%s has no adopted grant %s" % (run["id"], run.get("grant")))
        prereg = run.get("prereg", "")
        if prereg and not (ROOT / prereg).exists():
            missing.append("%s names a missing preregistration %s" % (run["id"], prereg))
    return not missing, ("; ".join(missing) if missing
                         else "%d result run(s) have an adopted grant" % checked)


def preflight(mode: str, suite: bool = True, ops_doc: dict | None = None) -> list[dict]:
    doc = ops_doc or ops()
    checks = []
    if suite:
        ok, detail = _suite_check()
        checks.append({"name": "suite", "ok": ok, "detail": detail})
    for name, fn in (
        ("research-trace", lambda: rt.main(["--check"])),
        ("decision-graph", lambda: dg.main(["--check"])),
        ("engine-pin", lambda: engine_pin.main(["--check"])),
        ("seed-reservations", lambda: a1_seed_reservations.main(["--check"])),
    ):
        ok, detail = _capture(fn)
        checks.append({"name": name, "ok": ok, "detail": detail})
    ok, detail = _prereg_check()
    checks.append({"name": "preregistrations", "ok": ok, "detail": detail})
    ok, detail = _grant_check()
    checks.append({"name": "grants", "ok": ok, "detail": detail})
    if mode == "publish":
        for name, findings in (
            ("claim-usage", claim_usage_findings(doc)),
            ("decision-in-force", decision_findings(doc)),
            ("waivers", waiver_findings(doc)),
        ):
            checks.append({"name": name, "ok": not findings,
                           "detail": "; ".join(item["message"] for item in findings) or "clean"})
    return checks


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def all_findings(ops_doc: dict | None = None, today: date | None = None) -> list[dict]:
    doc = ops_doc or ops()
    return (dependency_findings(doc) + decision_findings(doc) + waiver_findings(doc, today)
            + claim_usage_findings(doc) + run_ledger_findings(doc)
            + portfolio_findings(doc, today) + event_findings(doc))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="refresh the dependency baseline")
    group.add_argument("--check", action="store_true", help="run every governance check")
    group.add_argument("--preflight", choices=("run", "publish"))
    group.add_argument("--queue", action="store_true")
    group.add_argument("--waivers", action="store_true")
    group.add_argument("--claims", action="store_true")
    group.add_argument("--lottery", action="store_true")
    group.add_argument("--canary", action="store_true")
    group.add_argument("--ledger", action="store_true")
    group.add_argument("--portfolio", action="store_true")
    group.add_argument("--events", action="store_true")
    group.add_argument("--classes", action="store_true")
    group.add_argument("--append-event", metavar="RECORD")
    parser.add_argument("--no-suite", action="store_true", help="preflight without running pytest")
    parser.add_argument("--event-actor", default="owner")
    parser.add_argument("--event-from", default="")
    parser.add_argument("--event-to", default="")
    parser.add_argument("--event-reason", default="")
    parser.add_argument("--event-artifact", action="append", default=[])
    args = parser.parse_args(argv)

    if args.write:
        count = write_dependency_baseline()
        print("governance ops: baselined %d record(s)" % count)
        return 0
    if args.append_event:
        events = ops().get("events", [])
        event = {
            "id": "EVT-%04d" % (len(events) + 1),
            "date": date.today().isoformat(),
            "actor": args.event_actor,
            "record": args.append_event,
            "from": args.event_from,
            "to": args.event_to,
            "reason": args.event_reason,
            "artifacts": args.event_artifact,
        }
        try:
            append_event(event)
        except ValueError as exc:
            print("FAIL:", exc)
            return 1
        print("appended %s" % event["id"])
        return 0
    if args.classes:
        for cls, count in sorted(class_counts().items()):
            print("%s: %d" % (cls, count))
        return 0
    if args.check:
        findings = all_findings()
        for finding in findings:
            print("FAIL: %s: %s" % (finding["subject"], finding["message"]))
        print("governance findings:", len(findings))
        return 1 if findings else 0
    if args.preflight:
        checks = preflight(args.preflight, suite=not args.no_suite)
        for check in checks:
            if not check["ok"]:
                print("FAIL: %s: %s" % (check["name"], check["detail"]))
        if all(check["ok"] for check in checks):
            print("preflight %s: clean (%d checks)" % (args.preflight, len(checks)))
        return 0 if all(check["ok"] for check in checks) else 1
    if args.queue:
        print(render_queue(owner_queue()), end="")
        return 0
    if args.waivers:
        findings = waiver_findings()
        for finding in findings:
            print("FAIL: %s: %s" % (finding["subject"], finding["message"]))
        print("waivers:", len(ops().get("waivers", [])))
        return 1 if findings else 0
    if args.claims:
        for claim_id, documents in claim_usage().items():
            print("%s: %s" % (claim_id, ", ".join(documents)))
        return 0
    if args.lottery:
        result = lottery()
        print("week %s: %s" % (result["week"], ", ".join(result["sampled"])))
        for finding in result["findings"]:
            print("FAIL: %s: %s" % (finding["subject"], finding["message"]))
        return 1 if result["findings"] else 0
    if args.canary:
        problems = canary_problems()
        for problem in problems:
            print("FAIL:", problem)
        print("canaries:", "clean" if not problems else "%d problem(s)" % len(problems))
        return 1 if problems else 0
    if args.ledger:
        print(render_ledger(run_ledger()), end="")
        findings = run_ledger_findings()
        for finding in findings:
            print("FAIL: %s: %s" % (finding["subject"], finding["message"]))
        return 1 if findings else 0
    if args.portfolio:
        view = portfolio()
        print("# Portfolio review — %s" % view["date"])
        print("\nQuestions: %d; constraints: %d" % (len(view["questions"]), len(view["constraints"])))
        for row in view["questions"] + view["constraints"]:
            print("- %s (%s): review by %s" % (row["id"], row.get("state", row.get("status")), row["review_by"]))
        findings = portfolio_findings()
        for finding in findings:
            print("FAIL: %s: %s" % (finding["subject"], finding["message"]))
        return 1 if findings else 0
    if args.events:
        for event in ops().get("events", []):
            print("%s %s %s: %s -> %s (%s)" % (event.get("id"), event.get("date"),
                                                event.get("actor"), event.get("from"),
                                                event.get("to"), event.get("reason")))
        findings = event_findings()
        for finding in findings:
            print("FAIL: %s: %s" % (finding["subject"], finding["message"]))
        return 1 if findings else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
