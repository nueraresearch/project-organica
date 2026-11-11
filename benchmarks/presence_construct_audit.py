"""The Q1 construct audit, frozen as PRESENCE-CONSTRUCT-1.

Q1 asks whether presence, admitted predictions and final assertion are measured as
comparable quantities on the same world edges, build and window.  The published audit is
count-only; this record adds the per-edge table Q1 needs, on the audit's own six seeds, so
the comparison is against the audit row rather than against a differently seeded world.

The record is frozen and unrun.  The runner exists but executes nothing without a grant:
`--measure` and `--cell` refuse while `authorisation.granted` is false, and a `true` grant
is accepted only when it names a dated document and quotes it.  `--render-prereg`,
`--check-prereg` and `--dry-run` never run a cell; the dry run prints the seven cell
commands and target part paths.

    ./.venv/bin/python -m benchmarks.presence_construct_audit --render-prereg
    ./.venv/bin/python -m benchmarks.presence_construct_audit --check-prereg
    ./.venv/bin/python -m benchmarks.presence_construct_audit --dry-run
    ./.venv/bin/python -m benchmarks.presence_construct_audit --measure
    ./.venv/bin/python -m benchmarks.presence_construct_audit --finish
    ./.venv/bin/python -m benchmarks.presence_construct_audit --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import organica                                                             # noqa: E402
from benchmarks import audit_row_witness as witness_rows                   # noqa: E402
from benchmarks import build_supersession as supersession                   # noqa: E402
from benchmarks import engine_lineage, engine_stamp                         # noqa: E402
from benchmarks.acquisition_compositional import generate_compositional_world  # noqa: E402
from benchmarks.acquisition_harness import (                                # noqa: E402
    PHASE_ACQUISITION,
    _CountingMemoryService,
    _make_scratch_db,
    asserted_fingerprint,
)
from benchmarks.acquisition_runner import (                                 # noqa: E402
    EVENTS_PER_CYCLE,
    _world_compositional_edges,
    structure_edges,
)
from organica.sleep import SleepService                                     # noqa: E402

PREREG = ROOT / "docs" / "presence_construct_audit_prereg.json"
DOC = ROOT / "docs" / "PRESENCE-CONSTRUCT-AUDIT-PREREGISTRATION.md"
AUDIT = ROOT / "docs" / "presence_assertion_audit_0.14.0.json"
ARTIFACT = ROOT / "docs" / "presence_construct_audit_run.json"
RESULT = ROOT / "docs" / "PRESENCE-CONSTRUCT-AUDIT-RESULT.md"
PARTS = ROOT / "docs" / "presence_construct_audit_parts"
AUTHORISATION_DOC = ROOT / "docs" / "AUTHORISATION-PRESENCE-CONSTRUCT-1.md"
PIN = ROOT / "docs" / "engine_pin.json"

CELL_KIND = "presence_construct_cell"
ARTIFACT_KIND = "presence_construct_audit_run"

GATES = (
    "C1_build",
    "C2_world",
    "C3_presence",
    "C4_denominator",
    "C5_object",
    "C6_witnesses",
    "C7_seed_axis",
    "C8_determinism",
    "C9_audit_row_reproduced",
)
VERDICT_ORDER = (
    "C1_build",
    "C8_determinism",
    "C5_object",
    "C4_denominator",
    "C2_world",
    "C3_presence",
    "C6_witnesses",
    "C7_seed_axis",
    "C9_audit_row_reproduced",
)
VERDICTS = ("CONSTRUCT VALID", "OBJECT MISMATCH", "NOT MEASURABLE", "VOID")
GATE_VERDICT = {
    "C5_object": "OBJECT MISMATCH",
    "C4_denominator": "NOT MEASURABLE",
}
AUDIT_FINGERPRINT = re.compile(r"[0-9a-f]{16}")


def prereg() -> dict:
    return json.loads(PREREG.read_text(encoding="utf-8"))


def audit() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def audit_seeds() -> list[int]:
    return [row["seed"] for row in audit()["rows"]]


def audit_preflight_problems(body: dict | None = None) -> list[str]:
    """The comparator must be able to serve C9 before a grant may run a cell.

    The frozen design names six seeds, so the audit must carry exactly six rows.
    Each row must carry the canonical lowercase 16-hex ``asserted_fingerprint``
    that the audit harness emits; a missing or malformed digest would make C9
    compare against a value that cannot be a fingerprint.
    """
    body = body or prereg()
    seeds = list((body.get("design") or {}).get("seeds") or [])
    rows = audit().get("rows")
    if not isinstance(rows, list):
        return ["the comparator audit has no rows list"]
    found = []
    if len(rows) != len(seeds):
        found.append("the comparator audit has %d rows for %d frozen seeds"
                     % (len(rows), len(seeds)))
    for index, row in enumerate(rows):
        fingerprint = row.get("asserted_fingerprint") if isinstance(row, dict) else None
        seed = row.get("seed") if isinstance(row, dict) else None
        if not isinstance(fingerprint, str) or not AUDIT_FINGERPRINT.fullmatch(fingerprint):
            found.append("audit row %d (seed %r) has no valid 16-hex "
                         "asserted_fingerprint: %r" % (index, seed, fingerprint))
    return found


def audit_row(seed: int) -> dict:
    row = witness_rows.audit_row(seed)
    if row is None:
        raise KeyError("the audit has no row for seed %d" % seed)
    return row


def shipped_cap() -> int:
    return int(SleepService.MAX_PREDICTIONS)


def _fingerprint(text: str) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()[:16]


def _digest(pairs) -> str:
    """Use the audit's canonical pair-set recipe; do not restate it."""
    return asserted_fingerprint(pairs)


def authorisation_problems(body: dict | None = None, doc: Path | None = None) -> list[str]:
    """A grant is accepted only when a dated document carries the owner's words.

    `granted: false` is the frozen state and is never a problem. A `true` grant is the
    owner's decision, recorded by amending the record; the check is that the amendment
    names the authorisation document, that the document exists, that the quoted words
    appear in it, and that the document no longer says the block is unauthorised.
    """
    doc = AUTHORISATION_DOC if doc is None else Path(doc)
    body = body or prereg()
    auth = body.get("authorisation") or {}
    granted = auth.get("granted")
    if granted is False:
        return []
    if granted is not True:
        return ["authorisation.granted is neither true nor false"]
    problems = []
    for field in ("granted_on", "document", "quote"):
        if not auth.get(field):
            problems.append("granted without `authorisation.%s`" % field)
    if problems:
        return problems
    expected = "docs/" + doc.name
    if auth["document"] != expected:
        problems.append("the record names %r, not %r" % (auth["document"], expected))
    if not doc.exists():
        problems.append("the authorisation document %s does not exist" % expected)
        return problems
    text = doc.read_text(encoding="utf-8")
    if auth["quote"] not in text:
        problems.append("the recorded quote does not appear in %s" % expected)
    if "REQUESTED — NOT GRANTED" in text:
        problems.append("%s still says REQUESTED — NOT GRANTED" % expected)
    return problems


def validate(body: dict | None = None) -> list[str]:
    """Every way the frozen record, the audit and the shipped build could disagree."""
    found: list[str] = []
    body = body or prereg()

    if body.get("prereg") != "PRESENCE-CONSTRUCT-1":
        found.append("the record is not PRESENCE-CONSTRUCT-1")
    status = body.get("status")
    if status not in ("FROZEN, NOT RUN", "FROZEN, RUN"):
        found.append("the record's status is not a frozen state")
    ran = status == "FROZEN, RUN"
    if (body.get("no_cells_run") is not (not ran)
            or body.get("design", {}).get("no_cells_run") is not (not ran)):
        found.append("the record's status and its no_cells_run flag disagree")
    result = body.get("result") or {}
    if ran:
        artifact = result.get("artifact")
        if not artifact or not (ROOT / artifact).exists():
            found.append("the record claims a run but its result artifact is missing")
    elif result:
        found.append("an unrun record carries a result block")
    granted = (body.get("authorisation") or {}).get("granted")
    if granted not in (True, False):
        found.append("authorisation.granted is neither true nor false")
    elif granted:
        found += authorisation_problems(body)
    if body.get("design", {}).get("fresh") is not False:
        found.append("the record does not disclose that the audit's seeds are reused")

    engine = body.get("engine", {})
    if engine.get("edit") != "none":
        found.append("the record does not state that no engine file changes")
    if engine.get("treatment") != "none: the shipped `organica.sleep.SleepService`, no subclass and no observer":
        found.append("the record does not name the shipped engine as the whole treatment")
    if (engine.get("version") != getattr(organica, "__version__", None)
            and not supersession.matches(body, "version", engine.get("version"))):
        found.append("the record's engine version is not the installed version and is not the "
                     "build its supersession disclosure names")
    if engine.get("cap_source") != "organica.sleep.SleepService.MAX_PREDICTIONS":
        found.append("the record does not derive the cap from the shipped constant")

    design = body.get("design", {})
    seeds = list(design.get("seeds", []))
    if seeds != audit_seeds():
        found.append("the seed block is not the audit's six seeds, in order")
    if len(seeds) != 6 or len(set(seeds)) != 6:
        found.append("the seed block is not six distinct seeds")
    control = (design.get("control_cell") or {}).get("seed")
    if control not in seeds:
        found.append("the determinism control is not one of the reading seeds")
    if design.get("cycles") != 120:
        found.append("the cycle count is not the audit's acquisition block")
    if design.get("cells") != len(seeds):
        found.append("the cell count is not one cell per seed")
    if design.get("cap") != shipped_cap() and not supersession.matches(
            body, "cap", design.get("cap")):
        found.append("the declared cap is not the shipped cap and is not the recorded build's")
    found += supersession.problems(body, getattr(organica, "__version__", None), shipped_cap())

    gates = body.get("gates", {})
    if tuple(gates) != GATES:
        found.append("the gate set is not C1-C9 in order")
    if not all(gates.get(name) for name in GATES):
        found.append("a gate has no requirement text")
    if tuple(body.get("verdict_order", ())) != VERDICT_ORDER:
        found.append("the verdict order does not cover every gate once")

    verdicts = [row.get("verdict") for row in body.get("decision_table", [])]
    if sorted(set(verdicts)) != sorted(VERDICTS) or len(verdicts) < len(VERDICTS):
        found.append("the decision table cannot reach exactly %r" % (sorted(VERDICTS),))
    if not all(row.get("decision") and row.get("licenses")
               for row in body.get("decision_table", [])):
        found.append("a decision_table row names no decision or no licence")

    audit_body = audit()
    if not supersession.accepts(body, audit_body.get("engine_sha256")):
        found.append("the comparator audit was built by an engine that is neither the shipped "
                     "one nor the recorded build this record discloses")
    found += audit_preflight_problems(body)

    runner = body.get("runner") or {}
    if runner.get("status") != "built":
        found.append("the record's runner status is not built")
    if not runner.get("entry_points"):
        found.append("the record does not name the runner's entry points")
    if not body.get("not_evidence") or not body.get("stop_condition"):
        found.append("the record does not state its stop condition or what it is not evidence for")
    if not body.get("authorisation", {}).get("required"):
        found.append("the record does not require authorisation")
    request = (body.get("authorisation") or {}).get("request")
    expected_request = "docs/" + AUTHORISATION_DOC.name
    if not request:
        found.append("the record does not name its authorisation request")
    elif request != expected_request:
        found.append("the record names %r, not %r" % (request, expected_request))
    elif not AUTHORISATION_DOC.exists():
        found.append("the authorisation request %s does not exist" % expected_request)
    elif not granted and "REQUESTED — NOT GRANTED" not in AUTHORISATION_DOC.read_text(encoding="utf-8"):
        found.append("the request no longer says REQUESTED — NOT GRANTED but the record is ungranted")
    if not granted and ran:
        found.append("an ungranted record claims a run")
    return found


def render_prereg(body: dict | None = None) -> str:
    body = body or prereg()
    rows = body["design"]["seeds"]
    audit_rows = audit()["rows"]
    first = audit_rows[0]
    now = audit_row(rows[0])
    low = min(row["asserted_world_edges"] for row in audit_rows)
    high = max(row["asserted_world_edges"] for row in audit_rows)
    design = body["design"]
    auth = body.get("authorisation") or {}
    result = body.get("result") or {}
    if result:
        status_line = (
            "**Status: %s. Authorised %s and run.** The verdict is `%s`; the artifact is `%s` "
            "and the result page is `%s`."
            % (body["status"], auth.get("granted_on", "on an unrecorded date"),
               result.get("verdict", ""), result.get("artifact", ""), result.get("page", "")))
    elif auth.get("granted"):
        status_line = (
            "**Status: %s. Authorised %s.** No cell has run. The grant is recorded in `%s` and "
            "quoted there; it authorises the cells this record fixes and nothing else."
            % (body["status"], auth.get("granted_on", "on an unrecorded date"),
               auth.get("document", "")))
    else:
        status_line = (
            "**Status: %s. Not authorised.** No cell has run. This record fixes the protocol; it "
            "does not licence a run, and the runner refuses every entry point while `granted` is "
            "false." % body["status"])

    lines = [
        "# Presence to assertion: the construct audit (PRESENCE-CONSTRUCT-1)",
        "",
        "Generated from `docs/presence_construct_audit_prereg.json` by "
        "`python -m benchmarks.presence_construct_audit --render-prereg`. Do not edit by hand.",
        "",
        status_line,
        "",
        "Question 1 of the conversion program (`%s`), frozen on its own. %s"
        % (body["program"]["draft"], body["program"]["relationship"]),
        "",
        "## The question",
        "",
        body["question"],
        "",
        "## The hypothesis, stated before any cell",
        "",
        body["hypothesis"]["statement"],
        "",
        "**Prediction.** %s" % body["hypothesis"]["prediction"],
        "",
        "**Falsifier.** %s" % body["hypothesis"]["falsifier"],
        "",
        "**Alternative.** %s" % body["hypothesis"]["alternative"],
        "",
        "## Why Q1 exists",
        "",
        "The published audit (`docs/presence_assertion_audit_0.14.0.json`) is count-only: it "
        "reports %d world edges, %d present and %d-%d asserted across its six seeds, with no "
        "per-edge membership, no `S_ever`, no `S_final`, no `A_pred` and no bypass. Q1 adds that "
        "edge-level table on the same build, world and window, and checks that presence, "
        "admission and assertion are the same object before either later block reads a "
        "conversion or cap result." % (first["world_edges"], first["present_world_edges"],
                                       low, high),
        "",
        "## The design",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Engine | `%s`, pinned, no `organica/` edit |" % body["engine"]["version"],
        "| Build | %s |" % supersession.note(body),
        "| Treatment | %s |" % body["engine"]["treatment"],
        "| Seeds | %s |" % ", ".join("`%d`" % seed for seed in design["seeds"]),
        "| Control | seed `%s`, fresh-process rerun; a control, not a reading |"
        % design["control_cell"]["seed"],
        "| Cycles | `%d` per cell, the audit's acquisition block |" % design["cycles"],
        "| Cells | `%d` readings plus the control rerun |" % design["cells"],
        "| Cap | `%d`, the shipped cap; no cap level is varied |" % design["cap"],
        "| World | %s |" % design["world"],
        "| Pairing | %s |" % design["pairing"],
        "",
        "## The seeds are the audit's, not a fresh block",
        "",
        body["freeze_notes"]["seed_reuse"],
        "",
        "## What Q1 measures, and what it does not",
        "",
        "| Stage | Meaning |",
        "| --- | --- |",
    ]
    for name in ("W", "P", "S_cycle", "S_ever", "S_final", "A", "A_W", "A_pred", "A_other"):
        lines.append("| `%s` | %s |" % (name, body["endpoints"][name]))
    lines += [
        "",
        "`C` (constructed), `E` (eligibility reason), `R` (rank) and `U` (readout use) are "
        "**not measured** here. They are defined by the draft so that a later record cannot "
        "silently collapse them; this block imputes no count for any of them.",
        "",
        "## Gates",
        "",
        "| Gate | Requirement |",
        "| --- | --- |",
    ]
    for gate in GATES:
        lines.append("| `%s` | %s |" % (gate, body["gates"][gate]))
    lines += [
        "",
        "**C9 fingerprint basis.** %s" % body["freeze_notes"]["c9_fingerprint_basis"],
        "",
        "**Audit-row preflight.** %s" % body["freeze_notes"]["audit_row_preflight"],
        "",
        "The gates are evaluated in the record's declared order: %s. The first failure names the "
        "verdict; a later gate cannot override it."
        % " -> ".join("`%s`" % name for name in VERDICT_ORDER),
        "",
        "## Verdicts",
        "",
    ]
    for row in body["decision_table"]:
        lines += [
            "- **%s**: %s" % (row["verdict"], row["condition"]),
            "  - Decision: %s" % row["decision"],
            "  - Licences: %s" % row["licenses"],
        ]
    lines += [
        "",
        "## What a pass does and does not buy",
        "",
        body["adoption"]["rule"],
        "",
        "**Withdrawal.** %s" % body["adoption"]["withdrawal"],
        "",
        "## Runner",
        "",
        "**Status: %s.** %s" % (body["runner"]["status"], body["runner"]["consequence"]),
        "",
        "## Authorisation",
        "",
        "**Record:** `%s`." % (body["authorisation"].get("document")
                               or body["authorisation"]["request"]),
        "",
        body["authorisation"]["note"],
        "",
        "## Stop condition",
        "",
        body["stop_condition"],
        "",
        "## What this is not evidence for",
        "",
        body["not_evidence"],
        "",
        "## Cost",
        "",
        "`%d` reading cells and `%d` control rerun at `%d` cycles each (`%d` cycles in total). Wall clock: %s"
        % (body["cost"]["cells"], body["cost"]["control_cells"], design["cycles"],
           body["cost"]["cycles"], body["cost"]["wall_clock_estimate"]),
        "",
        "The comparator row used above is seed `%d`: %d world edges, %d present, %d asserted."
        % (now["seed"], now["world_edges"], now["present_world_edges"],
           now["asserted_world_edges"]),
        "",
    ]
    return "\n".join(lines)


def check_prereg(body: dict | None = None) -> int:
    body = body or prereg()
    problems = validate(body)
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    if not DOC.exists():
        raise SystemExit("FAIL: %s does not exist" % DOC.name)
    if DOC.read_text(encoding="utf-8") != render_prereg(body):
        raise SystemExit("FAIL: the preregistration page is stale; rerun with --render-prereg")
    auth = body.get("authorisation") or {}
    state = ("authorised %s" % auth.get("granted_on", "on an unrecorded date")
             if auth.get("granted") else "unauthorised")
    print("prereg %s: %s, %s, page current" % (body["prereg"], body["status"].lower(), state))
    return 0


# --------------------------------------------------------------------------- runner

ACQ_SOURCE = "env_acq"


def _part_path(seed: int, suffix: str = "") -> Path:
    return PARTS / ("%s%s.json" % (seed, suffix))


def _load_part(seed: int, suffix: str = "") -> dict:
    path = _part_path(seed, suffix)
    if not path.exists():
        raise SystemExit("missing part %s; run --measure" % path.name)
    return json.loads(path.read_text(encoding="utf-8"))


def _stamp_problems(part: dict, label: str, body: dict | None = None) -> list[str]:
    """Reject a part that was not built by the installed engine at the current pin."""
    problems = []
    gaps = engine_stamp.missing(part)
    if gaps:
        problems.append("%s is not fully stamped: %r" % (label, gaps))
    if part.get("kind") != CELL_KIND:
        problems.append("%s is not a %s part" % (label, CELL_KIND))
    version = engine_stamp.engine_version()
    if (part.get("engine_version") and part["engine_version"] != version
            and not supersession.matches(body, "version", part["engine_version"])):
        problems.append("%s was built by engine %s, not the installed %s, and not the build "
                        "this record discloses" % (label, part["engine_version"], version))
    if part.get("engine_sha256") and not supersession.accepts(body, part["engine_sha256"]):
        problems.append("%s was built from different engine bytes (neither the shipped engine "
                        "nor the build this record discloses)" % label)
    pinned = engine_stamp.pinned_commit()
    # The commit is provenance, not bytes -- `engine_pin` says so of its own `head_at_pin`, and does
    # not compare it. A behaviour-identical successor keeps the artifact valid even when the pin was
    # re-taken at a later checkout; the byte comparison above is the one that decides the build.
    if (part.get("engine_commit") and part["engine_commit"] != pinned
            and not engine_lineage.carried_commit(part["engine_commit"], part.get("engine_sha256"))):
        problems.append("%s predates the current engine pin: engine_commit %s, pin %s"
                        % (label, part["engine_commit"], pinned))
    return problems


def _part_problems(body: dict) -> list[str]:
    """Every expected part must exist and carry the current engine's stamp."""
    design = body["design"]
    cells = [(seed, "") for seed in design["seeds"]]
    cells.append((design["control_cell"]["seed"], "_control"))
    problems = []
    for seed, suffix in cells:
        path = _part_path(seed, suffix)
        if not path.exists():
            problems.append("missing part %s" % path.name)
            continue
        try:
            part = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            problems.append("%s is not readable JSON: %s" % (path.name, exc))
            continue
        problems.extend(_stamp_problems(part, path.name, body))
    return problems


def run_cell(seed: int, cycles: int | None = None) -> dict:
    """One acquisition run with the shipped engine; records stages and one row per edge."""
    body = prereg()
    cycles = int(body["design"]["cycles"] if cycles is None else cycles)
    world = generate_compositional_world(seed=seed, cycles=cycles)
    world_edges = _world_compositional_edges(world)

    db_path = _make_scratch_db("presence_construct")
    mem = _CountingMemoryService(str(db_path))
    svc = SleepService(mem)
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    windows: list[list[tuple[str, str]]] = []
    try:
        for i, (text, train_flag) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not train_flag:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                mem.current_cycle = i // EVENTS_PER_CYCLE
            mem.store(text, event_type="observe",
                      source=ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                report = svc.run_sleep_cycle()
                windows.append([(p.source, p.target) for p in report.predictions])
        asserted_pairs = {(a, b) for a, targets in
                          structure_edges(svc._load_prior_candidates()).items()
                          for b in targets}
        temporal_pairs = {(a, b) for a, b, _c in mem.temporal_edges(min_count=1)}
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    present = world_edges & temporal_pairs
    ever = world_edges & {edge for window in windows for edge in window}
    asserted_world = world_edges & asserted_pairs
    final = ever & asserted_pairs
    a_pred = asserted_world & ever
    a_other = asserted_world - ever

    admissions: dict[tuple[str, str], int] = {}
    for window in windows:
        for edge in set(window) & world_edges:
            admissions[edge] = admissions.get(edge, 0) + 1
    table = [{
        "source": a,
        "target": b,
        "present": (a, b) in present,
        "admitted": (a, b) in ever,
        "asserted": (a, b) in asserted_world,
        "admissions": admissions.get((a, b), 0),
    } for a, b in sorted(world_edges)]

    counts = {
        "W": len(world_edges),
        "P": len(present),
        "S_ever": len(ever),
        "S_final": len(final),
        "A_W": len(asserted_world),
        "A_pred": len(a_pred),
        "A_other": len(a_other),
    }
    cell = {
        "kind": CELL_KIND,
        "seed": seed,
        "cycles": len(windows),
        "cap": shipped_cap(),
        "engine_version": engine_stamp.engine_version(),
        "engine_sha256": engine_stamp.engine_sha256(),
        "world_edges": counts["W"],
        "world_digest": _digest(world_edges),
        "present_world_edges": counts["P"],
        "present_fingerprint": _digest(present),
        "s_cycle_world_edges": [len(world_edges & set(window)) for window in windows],
        "s_cycle_max": max((len(world_edges & set(window)) for window in windows), default=0),
        "s_ever_world_edges": counts["S_ever"],
        "s_ever_fingerprint": _digest(ever),
        "s_final_world_edges": counts["S_final"],
        "s_final_fingerprint": _digest(final),
        "asserted_total": len(asserted_pairs),
        "asserted_fingerprint": asserted_fingerprint(asserted_pairs),
        "asserted_world_edges": counts["A_W"],
        "asserted_world_fingerprint": _digest(asserted_world),
        "a_pred_world_edges": counts["A_pred"],
        "a_other_world_edges": counts["A_other"],
        "a_w_subset_of_p": asserted_world <= present,
        "stage_fingerprint": _fingerprint(
            "|".join("%s=%s" % item for item in sorted(counts.items()))),
        "pse_fingerprint": _fingerprint("P:%s|S_ever:%s|A_W:%s" % (
            _digest(present), _digest(ever), _digest(asserted_world))),
        "windows_world": [["%s>%s" % edge for edge in window if edge in world_edges]
                          for window in windows],
        "edges": table,
    }
    return engine_stamp.stamp(cell)


def _failures(body: dict, rows: list[dict], control: dict) -> dict[str, dict]:
    """The gate failures, each keyed by gate, evaluated independently."""
    found: dict[str, dict] = {}
    version = engine_stamp.engine_version()
    digest = engine_stamp.engine_sha256()
    pinned = engine_stamp.pinned_commit()

    bad = [cell["seed"] for cell in rows + [control]
           if (cell.get("engine_version") != version
               and not supersession.matches(body, "version", cell.get("engine_version")))
           or not supersession.accepts(body, cell.get("engine_sha256"))
           or (cell.get("engine_commit") != pinned
               and not engine_lineage.carried_commit(cell.get("engine_commit"),
                                                     cell.get("engine_sha256")))
           or engine_stamp.missing(cell)]
    if bad:
        found["C1_build"] = {"seeds": bad}

    differs = [field for field in ("stage_fingerprint", "pse_fingerprint", "windows_world")
               if control.get(field) != rows[0].get(field)]
    if differs:
        found["C8_determinism"] = {"seed": rows[0]["seed"], "differs": differs}

    for cell in rows:
        absent = [(edge["source"], edge["target"]) for edge in cell["edges"]
                  if edge["asserted"] and not edge["present"]]
        if absent or not cell.get("a_w_subset_of_p"):
            found["C5_object"] = {"seed": cell["seed"],
                                  "edges": ["%s>%s" % edge for edge in absent[:5]]}
            break

    for cell in rows:
        empty = [stage for stage in ("world_edges", "present_world_edges", "s_ever_world_edges")
                 if not cell.get(stage)]
        if empty:
            found["C4_denominator"] = {"seed": cell["seed"], "empty": empty}
            break

    wrong = [cell["seed"] for cell in rows
             if cell["world_edges"] != audit_row(cell["seed"])["world_edges"]]
    if wrong:
        found["C2_world"] = {"seeds": wrong}

    bad = []
    for cell in rows:
        present = {(edge["source"], edge["target"]) for edge in cell["edges"]
                   if edge["present"]}
        if (len(cell["edges"]) != cell["world_edges"]
                or len(present) != cell["present_world_edges"]
                or _digest(present) != cell["present_fingerprint"]):
            bad.append(cell["seed"])
    if bad:
        found["C3_presence"] = {"seeds": bad}

    bad = [cell["seed"] for cell in rows
           if not any(edge["asserted"] for edge in cell["edges"])
           or not any(edge["present"] and not edge["asserted"] for edge in cell["edges"])]
    if bad:
        found["C6_witnesses"] = {"seeds": bad}

    distinct = len({cell["pse_fingerprint"] for cell in rows})
    if distinct < 2:
        found["C7_seed_axis"] = {"distinct": distinct}

    for cell in rows:
        result = witness_rows.compare(
            audit_row(cell["seed"]), cell,
            fields=witness_rows.AUDIT_ROW_FIELDS)
        if not result["reproduces"]:
            found["C9_audit_row_reproduced"] = {"seed": cell["seed"],
                                                "differs": result["differs"]}
            break
    return found


def verdict(body: dict | None = None, rows: list[dict] | None = None,
            control: dict | None = None) -> tuple[str, dict]:
    """The record's decision table, read in its declared order."""
    body = body or prereg()
    rows = rows or []
    control = control or {}
    failures = _failures(body, rows, control)
    for gate in VERDICT_ORDER:
        if gate in failures:
            return GATE_VERDICT.get(gate, "VOID"), {"gate": gate, **failures[gate]}
    return "CONSTRUCT VALID", {"seeds": len(rows)}


def build(body: dict | None = None) -> dict:
    body = body or prereg()
    design = body["design"]
    rows = [_load_part(seed) for seed in design["seeds"]]
    control = _load_part(design["control_cell"]["seed"], "_control")
    failures = _failures(body, rows, control)
    checks = {gate: gate not in failures for gate in GATES}
    label, details = verdict(body, rows, control)
    artifact = {
        "kind": ARTIFACT_KIND,
        "prereg": body["prereg"],
        "engine": {"version": engine_stamp.engine_version(),
                   "sha256": engine_stamp.engine_sha256()},
        "design": {"seeds": design["seeds"], "cycles": design["cycles"],
                   "cells": design["cells"], "cap": design["cap"],
                   "control_cell": design["control_cell"]},
        "rows": rows,
        "control": control,
        "checks": checks,
        "verdict": label,
        "details": details,
        "not_evidence": body["not_evidence"],
    }
    return engine_stamp.stamp(artifact)


def render_result(artifact: dict) -> str:
    lines = [
        "# Presence to assertion: the construct audit — result",
        "",
        "Generated from `docs/presence_construct_audit_run.json` by "
        "`python -m benchmarks.presence_construct_audit --finish`. Do not edit by hand.",
        "",
        "**Verdict: `%s`**" % artifact["verdict"],
        "",
        "| Seed | W | P | S_ever | S_final | A_W | A_pred | A_other |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in artifact["rows"]:
        lines.append("| %d | %d | %d | %d | %d | %d | %d | %d |" % (
            row["seed"], row["world_edges"], row["present_world_edges"],
            row["s_ever_world_edges"], row["s_final_world_edges"],
            row["asserted_world_edges"], row["a_pred_world_edges"],
            row["a_other_world_edges"]))
    lines += [
        "",
        "## Gates",
        "",
        "| Gate | Result |",
        "| --- | --- |",
    ]
    for gate in GATES:
        lines.append("| `%s` | %s |" % (gate, "PASS" if artifact["checks"][gate] else "FAIL"))
    lines += [
        "",
        "The gates are read in the record's declared order: %s. The first failure names the "
        "verdict." % " -> ".join("`%s`" % gate for gate in VERDICT_ORDER),
        "",
        "## What this does not claim",
        "",
        artifact["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.presence_construct_audit --measure",
        "python -m benchmarks.presence_construct_audit --finish",
        "python -m benchmarks.presence_construct_audit --check",
        "```",
        "",
    ]
    return "\n".join(lines)


def _cell_command(seed: int, suffix: str = "") -> tuple[list[str], Path]:
    """The command and target part path for one cell."""
    path = _part_path(seed, suffix)
    command = [sys.executable, "-m", "benchmarks.presence_construct_audit",
               "--cell", str(seed), "--out", str(path)]
    return command, path


def _run_part(seed: int, suffix: str = "") -> None:
    """One cell in its own process, so the engine sees a fresh hash seed."""
    command, path = _cell_command(seed, suffix)
    if path.exists():
        print("cached %s" % path.name, flush=True)
        return
    env = dict(os.environ, PYTHONHASHSEED="0")
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, env=env,
                          timeout=3600)
    if proc.returncode != 0:
        raise SystemExit("cell seed=%d%s failed: %s" % (
            seed, suffix, (proc.stderr or proc.stdout or "")[-800:]))
    print("cell seed=%d%s written in %.1fs" % (
        seed, suffix, time.perf_counter() - started), flush=True)


def measure() -> int:
    body = prereg()
    problems = validate(body)
    if problems:
        raise SystemExit("REFUSED: the record is not valid: " + "; ".join(problems))
    if not (body.get("authorisation") or {}).get("granted"):
        raise SystemExit("REFUSED: the record is not authorised; no cell may run")
    design = body["design"]
    for seed in design["seeds"]:
        _run_part(seed)
    _run_part(design["control_cell"]["seed"], "_control")
    return 0


def dry_run() -> int:
    """Print the seven cell commands and part paths without executing anything."""
    body = prereg()
    problems = validate(body)
    if problems:
        raise SystemExit("REFUSED: the record is not valid: " + "; ".join(problems))
    design = body["design"]
    cells = [(seed, "") for seed in design["seeds"]]
    cells.append((design["control_cell"]["seed"], "_control"))
    print("Q1 dry run: %d cell commands; no cell will run." % len(cells))
    for seed, suffix in cells:
        command, path = _cell_command(seed, suffix)
        print("cell seed=%d%s" % (seed, suffix))
        print("  command: %s" % " ".join(shlex.quote(part) for part in command))
        print("  part: %s" % path)
    print("No cell was run.")
    return 0


def finish() -> int:
    body = prereg()
    problems = validate(body)
    if problems:
        raise SystemExit("REFUSED: the record is not valid: " + "; ".join(problems))
    if not (body.get("authorisation") or {}).get("granted"):
        raise SystemExit("REFUSED: the record is not authorised; no result may be written")
    artifact = build(body)
    ARTIFACT.write_text(json.dumps(artifact, indent=1) + "\n", encoding="utf-8")
    RESULT.write_text(render_result(artifact), encoding="utf-8")
    print("%s: %s" % (artifact["verdict"], json.dumps(artifact["details"])))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no run artifact; run --finish")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    body = prereg()
    problems = []
    if artifact.get("kind") != ARTIFACT_KIND:
        problems.append("artifact kind")
    gaps = engine_stamp.missing(artifact)
    if gaps:
        problems.append("artifact is not fully stamped: %r" % (gaps,))
    if not supersession.accepts(body, artifact.get("engine", {}).get("sha256")):
        problems.append("artifact build is neither the shipped engine nor the recorded build "
                        "this record discloses")
    problems += _part_problems(body)
    label, details = verdict(body, artifact.get("rows") or [],
                             artifact.get("control") or {})
    if artifact.get("verdict") != label:
        problems.append("verdict %r is not the derived %r" % (artifact.get("verdict"), label))
    if artifact.get("details") != details:
        problems.append("details are not derived from the rows")
    if not RESULT.exists() or RESULT.read_text(encoding="utf-8") != render_result(artifact):
        problems.append("result page is stale")
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    print("construct audit %s: %s" % (artifact["prereg"], artifact["verdict"]))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--render-prereg", action="store_true")
    group.add_argument("--check-prereg", action="store_true")
    group.add_argument("--measure", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--cell", type=int, metavar="SEED")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    if args.cell is not None:
        if not args.out:
            raise SystemExit("--cell needs --out")
        body = prereg()
        problems = validate(body)
        if problems:
            raise SystemExit("REFUSED: the record is not valid: " + "; ".join(problems))
        if not (body.get("authorisation") or {}).get("granted"):
            raise SystemExit("REFUSED: the record is not authorised; no cell may run")
        if not args.out.endswith(".json"):
            raise SystemExit("--out must be a .json part path")
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(run_cell(args.cell), indent=1) + "\n", encoding="utf-8")
        print("wrote %s" % path)
        return 0
    if args.render_prereg:
        problems = validate()
        if problems:
            raise SystemExit("the record is not valid: " + "; ".join(problems))
        DOC.write_text(render_prereg(prereg()), encoding="utf-8")
        print("rendered %s" % DOC.name)
        return 0
    if args.check_prereg:
        return check_prereg()
    if args.dry_run:
        return dry_run()
    if args.finish:
        return finish()
    if args.check:
        return check()
    return measure()


if __name__ == "__main__":
    raise SystemExit(main())
