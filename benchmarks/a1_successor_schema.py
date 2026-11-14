"""Machine-readable A1 successor candidate schema and refusal validator.

The JSON Schema is the external contract; this module is the standard-library
validator that also checks the cross-row and governance rules JSON Schema
cannot express.  It never selects a target, freezes a manifest, reserves a
seed, issues a grant or runs a cell.

    python -m benchmarks.a1_successor_schema --write
    python -m benchmarks.a1_successor_schema --check
    python -m benchmarks.a1_successor_schema --validate docs/a1_successor_candidate.json
    python -m benchmarks.a1_successor_schema --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from benchmarks import a1_successor_preflight
from benchmarks import a1_target_selection

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SCHEMA_PATH = DOCS / "a1_successor_candidate.schema.json"
PAGE_PATH = DOCS / "A1-SUCCESSOR-SCHEMA.md"
CANDIDATE_PATH = DOCS / "a1_successor_candidate.json"
KIND = "a1_successor_candidate"
CONTROL_SEEDS = tuple(a1_target_selection.SEEDS)
EDGE_RE = re.compile(r"^([a-z]{4,})>([a-z]{4,})$")

REFUSALS = (
    "REUSED_CONTROL_SEEDS",
    "SEED_SCREENED_ON_K",
    "UNDISCLOSED_K_EXPOSURE",
    "DUPLICATE_EDGE",
    "REVERSE_DUPLICATE",
    "SELF_LOOP",
    "INDEPENDENT_BELOW_60",
    "C1_BELOW_60",
    "TARGET_POOL_BELOW_20",
    "TARGETS_SELECTED_BEFORE_PREFLIGHT",
    "UNIVERSE_INCONSISTENT",
    "NO_PREFLIGHT_PASS",
    "PASS_TREATED_AS_GRANT",
    "SCHEMA_NOT_OBJECT",
    "SCHEMA_KIND",
    "SCHEMA_ID",
    "SCHEMA_TARGETS_IN_SCOPE",
    "SCHEMA_SEED_BLOCK",
    "DUPLICATE_SEED",
    "TOO_FEW_SEEDS",
    "SEED_BLOCK_MISMATCH",
    "SCHEMA_PER_SEED",
    "SCHEMA_ROWS",
    "SCHEMA_ROW",
    "INVALID_EDGE",
    "SCHEMA_SELECTION",
    "SCHEMA_GOVERNANCE",
    "SCHEMA_BASELINE",
    "SCHEMA_STATUS",
    "SCHEMA_DATE",
    "GATE_UNREADABLE",
)


def schema() -> dict:
    """Return the JSON Schema for a candidate spec."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://project-organica.local/schemas/a1_successor_candidate.schema.json",
        "title": "A1 successor candidate",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "kind", "id", "seed_block", "targets_in_scope", "per_seed",
            "selection", "baseline", "universe", "governance",
        ],
        "properties": {
            "kind": {"const": KIND},
            "id": {"type": "string", "minLength": 1},
            "date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
            "status": {"type": "string", "pattern": "^CANDIDATE SPEC"},
            "seed_block": {
                "type": "array", "minItems": 6, "uniqueItems": True,
                "items": {"type": "integer", "minimum": 1},
            },
            "targets_in_scope": {"type": "boolean"},
            "per_seed": {
                "type": "object", "minProperties": 6,
                "propertyNames": {"pattern": "^[0-9]+$"},
                "additionalProperties": {
                    "type": "array", "minItems": 1,
                    "items": {"$ref": "#/$defs/row"},
                },
            },
            "selection": {
                "type": "object", "additionalProperties": False,
                "required": [
                    "screen", "targets_selected", "k_screened",
                    "prior_k_exposure",
                ],
                "properties": {
                    "source": {"type": "string"},
                    "u_cycle": {"type": "integer", "minimum": 1},
                    "cycles": {"type": "integer", "minimum": 1},
                    "one_orientation_per_pair": {"const": True},
                    "boundary_safe": {"type": "boolean"},
                    "boundary_note": {"type": "string"},
                    "screen": {"type": "string", "minLength": 1},
                    "targets_selected": {"const": 0},
                    "k_screened": {"const": False},
                    "prior_k_exposure": {"type": "string", "minLength": 1},
                },
            },
            "baseline": {
                "type": "object", "additionalProperties": False,
                "required": ["source", "cycles", "treatment", "A", "K"],
                "properties": {
                    "source": {"type": "string"},
                    "cycles": {"type": "integer", "minimum": 1},
                    "treatment": {"const": "none"},
                    "A": {"type": "string"},
                    "K": {"type": "string"},
                },
            },
            "universe": {
                "type": "object", "additionalProperties": False,
                "required": ["id", "digest", "selector", "runner", "scorer"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "selector": {"type": "string", "minLength": 1},
                    "runner": {"type": "string", "minLength": 1},
                    "scorer": {"type": "string", "minLength": 1},
                },
            },
            "governance": {
                "type": "object", "additionalProperties": False,
                "required": [
                    "preflight_required", "freeze", "grant", "run",
                    "authorization",
                ],
                "properties": {
                    "preflight_required": {"const": True},
                    "freeze": {"const": False},
                    "grant": {"const": False},
                    "run": {"const": False},
                    "authorization": {"const": "none"},
                },
            },
            "summaries": {
                "type": "array",
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": [
                        "seed", "candidate_edges", "independent_edges",
                        "A_available", "K_available", "A_and_K",
                        "selection_status",
                    ],
                    "properties": {
                        "seed": {"type": "integer"},
                        "candidate_edges": {"type": "integer", "minimum": 0},
                        "independent_edges": {"type": "integer", "minimum": 0},
                        "A_available": {"type": "integer", "minimum": 0},
                        "K_available": {"type": "integer", "minimum": 0},
                        "A_and_K": {"type": "integer", "minimum": 0},
                        "selection_status": {"type": "string"},
                    },
                },
            },
            "not_evidence": {"type": "string"},
        },
        "$defs": {
            "row": {
                "type": "object", "additionalProperties": False,
                "required": ["edge", "A", "K"],
                "properties": {
                    "edge": {
                        "type": "string",
                        "pattern": "^[a-z]{4,}>[a-z]{4,}$",
                    },
                    "A": {"type": "boolean"},
                    "K": {"type": "boolean"},
                },
            },
        },
    }


def universe_digest(doc: dict) -> str:
    """Digest the declared edge universe, one sorted edge list per seed."""
    payload = {}
    per_seed = doc.get("per_seed") if isinstance(doc.get("per_seed"), dict) else {}
    for seed in doc.get("seed_block") or []:
        rows = per_seed.get(str(seed), [])
        if not isinstance(rows, list):
            rows = []
        payload[str(seed)] = sorted(
            str(row.get("edge")) for row in rows if isinstance(row, dict)
        )
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def schema_problems(doc: dict) -> list[str]:
    """Return structural and governance refusal codes for one candidate."""
    found: list[str] = []

    def add(code: str) -> None:
        if code not in found:
            found.append(code)

    if not isinstance(doc, dict):
        return ["SCHEMA_NOT_OBJECT"]
    if doc.get("kind") != KIND:
        add("SCHEMA_KIND")
    if not isinstance(doc.get("id"), str) or not doc.get("id"):
        add("SCHEMA_ID")
    if not isinstance(doc.get("targets_in_scope"), bool):
        add("SCHEMA_TARGETS_IN_SCOPE")
    if "date" in doc and not re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", str(doc["date"])):
        add("SCHEMA_DATE")
    if not str(doc.get("status") or "").startswith("CANDIDATE SPEC"):
        add("SCHEMA_STATUS")

    seed_block = doc.get("seed_block")
    if not isinstance(seed_block, list) or not all(
            type(seed) is int and seed > 0 for seed in seed_block):
        add("SCHEMA_SEED_BLOCK")
        seed_block = []
    if len(seed_block) != len(set(seed_block)):
        add("DUPLICATE_SEED")
    if len(seed_block) < 6:
        add("TOO_FEW_SEEDS")
    if any(seed in CONTROL_SEEDS for seed in seed_block):
        add("REUSED_CONTROL_SEEDS")

    per_seed = doc.get("per_seed")
    if not isinstance(per_seed, dict):
        add("SCHEMA_PER_SEED")
        per_seed = {}
    if set(str(seed) for seed in seed_block) != set(per_seed):
        add("SEED_BLOCK_MISMATCH")

    for seed in seed_block:
        rows = per_seed.get(str(seed))
        if not isinstance(rows, list) or not rows:
            add("SCHEMA_ROWS")
            continue
        seen: set[str] = set()
        pairs: dict[tuple[str, str], str] = {}
        for row in rows:
            if not isinstance(row, dict):
                add("SCHEMA_ROW")
                continue
            if set(row) != {"edge", "A", "K"}:
                add("SCHEMA_ROW")
            edge = row.get("edge")
            match = EDGE_RE.match(edge) if isinstance(edge, str) else None
            if not match:
                add("INVALID_EDGE")
                continue
            if type(row.get("A")) is not bool or type(row.get("K")) is not bool:
                add("SCHEMA_ROW")
            if edge in seen:
                add("DUPLICATE_EDGE")
                continue
            seen.add(edge)
            source, target = match.groups()
            if source == target:
                add("SELF_LOOP")
                continue
            pair = tuple(sorted((source, target)))
            if pair in pairs:
                add("REVERSE_DUPLICATE")
                continue
            pairs[pair] = edge

    selection = doc.get("selection")
    if not isinstance(selection, dict):
        add("SCHEMA_SELECTION")
    else:
        if selection.get("targets_selected") != 0:
            add("TARGETS_SELECTED_BEFORE_PREFLIGHT")
        if selection.get("k_screened") is not False:
            add("SEED_SCREENED_ON_K")
        prior = selection.get("prior_k_exposure")
        if not isinstance(prior, str) or not prior.strip():
            add("UNDISCLOSED_K_EXPOSURE")
        if not isinstance(selection.get("screen"), str) or not selection.get("screen"):
            add("SCHEMA_SELECTION")
    if doc.get("targets") or doc.get("selected_targets"):
        add("TARGETS_SELECTED_BEFORE_PREFLIGHT")

    baseline = doc.get("baseline")
    if not isinstance(baseline, dict) or baseline.get("treatment") != "none":
        add("SCHEMA_BASELINE")
    elif type(baseline.get("cycles")) is not int or baseline.get("cycles") < 1:
        add("SCHEMA_BASELINE")

    governance = doc.get("governance")
    if not isinstance(governance, dict):
        add("SCHEMA_GOVERNANCE")
    else:
        if governance.get("preflight_required") is not True:
            add("NO_PREFLIGHT_PASS")
        if any(governance.get(key) for key in ("freeze", "grant", "run")):
            add("PASS_TREATED_AS_GRANT")
        if governance.get("authorization") != "none":
            add("PASS_TREATED_AS_GRANT")
    status = str(doc.get("status") or "").upper()
    if status.startswith(("PASS", "FROZEN", "GRANTED", "RUN")):
        add("PASS_TREATED_AS_GRANT")

    universe = doc.get("universe")
    if not isinstance(universe, dict):
        add("UNIVERSE_INCONSISTENT")
    else:
        if not (universe.get("selector") == universe.get("runner")
                == universe.get("scorer")):
            add("UNIVERSE_INCONSISTENT")
        if universe.get("digest") != universe_digest(doc):
            add("UNIVERSE_INCONSISTENT")

    return found


def validate(doc: dict, check_gate: bool = True) -> dict:
    """Return schema refusals and, separately, the gate result."""
    structural = schema_problems(doc)
    gate = None
    refusals = set(structural)
    if check_gate and not structural:
        try:
            gate = a1_successor_preflight.evaluate(doc)
        except Exception as exc:  # pragma: no cover - malformed spec path
            refusals.add("GATE_UNREADABLE")
            gate = {"status": "UNREADABLE", "error": str(exc), "per_seed": []}
        else:
            refusals.update(gate.get("problems") or [])
            for row in gate.get("per_seed") or []:
                refusals.update(row.get("reasons") or [])
    return {
        "schema": structural,
        "refusals": sorted(refusals),
        "gate": gate,
        "schema_ok": not structural,
    }


def page() -> str:
    lines = [
        "# A1 successor candidate schema",
        "",
        "**ID:** `A1-SUCCESSOR-SCHEMA-1`  ",
        "**Status:** `REFERENCE — MACHINE-READABLE CONTRACT; NO FREEZE, NO GRANT, NO RUN`",
        "",
        "The JSON Schema is the external contract for a candidate. The validator adds the cross-row and governance rules that JSON Schema cannot express, then runs the existing no-arm preflight as a separate gate.",
        "",
        "**Schema:** [`a1_successor_candidate.schema.json`](a1_successor_candidate.schema.json)",
        "",
        "## Commands",
        "",
        "```bash",
        "python -m benchmarks.a1_successor_schema --check",
        "python -m benchmarks.a1_successor_schema --validate docs/a1_successor_candidate.json",
        "python -m benchmarks.a1_successor_schema --self-test",
        "```",
        "",
        "`--check` verifies the schema artifact and page, and verifies the live candidate is structurally valid. `--validate` returns a non-zero status for any refusal, including a failing gate. Schema validity and gate success are reported separately.",
        "",
        "## Refusal codes",
        "",
        "| Code | Meaning |",
        "| --- | --- |",
    ]
    meanings = {
        "REUSED_CONTROL_SEEDS": "uses one of the current six control seeds",
        "SEED_SCREENED_ON_K": "declares a K-screened block",
        "UNDISCLOSED_K_EXPOSURE": "omits the prior K exposure declaration",
        "DUPLICATE_EDGE": "repeats an oriented edge",
        "REVERSE_DUPLICATE": "contains both orientations of one pair",
        "SELF_LOOP": "contains a self-edge",
        "INDEPENDENT_BELOW_60": "fewer than 60 independent edges on a seed",
        "C1_BELOW_60": "C1 ceiling below 60 on a seed",
        "TARGET_POOL_BELOW_20": "no 20-row A+K matching while targets are in scope",
        "TARGETS_SELECTED_BEFORE_PREFLIGHT": "the candidate already selects targets",
        "UNIVERSE_INCONSISTENT": "selector, runner and scorer do not agree",
        "NO_PREFLIGHT_PASS": "preflight is not declared as required",
        "PASS_TREATED_AS_GRANT": "the spec claims a freeze, grant or run",
        "SCHEMA_NOT_OBJECT": "the candidate is not a JSON object",
        "SCHEMA_KIND": "the candidate kind is wrong",
        "SCHEMA_ID": "the candidate has no ID",
        "SCHEMA_TARGETS_IN_SCOPE": "targets_in_scope is not boolean",
        "SCHEMA_SEED_BLOCK": "the seed block is malformed",
        "DUPLICATE_SEED": "the seed block repeats a seed",
        "TOO_FEW_SEEDS": "fewer than six seeds",
        "SEED_BLOCK_MISMATCH": "per_seed does not match the seed block",
        "SCHEMA_PER_SEED": "per_seed is not an object",
        "SCHEMA_ROWS": "a seed has no row list",
        "SCHEMA_ROW": "a row has the wrong fields or non-boolean A/K",
        "INVALID_EDGE": "an edge does not match tag>tag",
        "SCHEMA_SELECTION": "the selection declaration is missing or malformed",
        "SCHEMA_GOVERNANCE": "the governance declaration is missing or malformed",
        "SCHEMA_BASELINE": "the baseline is missing or is not a no-arm replay",
        "SCHEMA_STATUS": "the status is not a candidate specification",
        "SCHEMA_DATE": "the date is not YYYY-MM-DD",
        "GATE_UNREADABLE": "the preflight could not read the candidate",
    }
    for code in REFUSALS:
        lines.append("| `%s` | %s |" % (code, meanings[code]))
    lines += [
        "",
        "A schema-valid candidate may still fail the gate; the current fresh block does, at C1 **40, 37, 46, 42, 31, 38**. A gate PASS would still not freeze, grant or run anything.",
        "",
        "**Not evidence:** a schema and validator. They select no target, reserve no seed, freeze no target, issue no grant and run no cell.",
        "",
    ]
    return "\n".join(lines)


def _fixture() -> dict:
    tags = ["tag" + chr(97 + i) * 2 for i in range(16)]
    edges = sorted({
        "%s>%s" % (tags[i], tags[(i + j) % 16])
        for i in range(16) for j in range(1, 5)
    })[:64]
    per_seed = {
        str(seed): [{"edge": edge, "A": True, "K": True} for edge in edges]
        for seed in range(1, 7)
    }
    doc = {
        "kind": KIND,
        "id": "fixture",
        "date": "2026-11-14",
        "status": "CANDIDATE SPEC — fixture",
        "seed_block": list(range(1, 7)),
        "targets_in_scope": True,
        "per_seed": per_seed,
        "selection": {
            "source": "fixture",
            "u_cycle": 36,
            "cycles": 120,
            "one_orientation_per_pair": True,
            "boundary_safe": True,
            "boundary_note": "fixture",
            "screen": "none",
            "targets_selected": 0,
            "k_screened": False,
            "prior_k_exposure": "none",
        },
        "baseline": {
            "source": "fixture",
            "cycles": 120,
            "treatment": "none",
            "A": "fixture",
            "K": "fixture",
        },
        "universe": {
            "id": "fixture-universe",
            "digest": "",
            "selector": "candidate-stream",
            "runner": "candidate-stream",
            "scorer": "candidate-stream",
        },
        "governance": {
            "preflight_required": True,
            "freeze": False,
            "grant": False,
            "run": False,
            "authorization": "none",
        },
        "not_evidence": "fixture",
    }
    doc["universe"]["digest"] = universe_digest(doc)
    return doc


def self_test() -> list[str]:
    found: list[str] = []
    spec = _fixture()
    if schema_problems(spec):
        found.append("the clean fixture has schema refusals")
    result = validate(spec)
    if result["gate"]["status"] != "PASS":
        found.append("the clean fixture does not pass the gate")
    if result["refusals"]:
        found.append("the clean fixture has refusals")

    def check(label: str, mutate, code: str) -> None:
        bad = json.loads(json.dumps(spec))
        mutate(bad)
        codes = schema_problems(bad)
        if code not in codes:
            found.append("%s did not produce %s" % (label, code))

    check("reused seed", lambda d: d["seed_block"].__setitem__(0, CONTROL_SEEDS[0]), "REUSED_CONTROL_SEEDS")
    check("k screen", lambda d: d["selection"].__setitem__("k_screened", True), "SEED_SCREENED_ON_K")
    check("no exposure", lambda d: d["selection"].__setitem__("prior_k_exposure", ""), "UNDISCLOSED_K_EXPOSURE")
    check("selected target", lambda d: d["selection"].__setitem__("targets_selected", 1), "TARGETS_SELECTED_BEFORE_PREFLIGHT")
    check("freeze", lambda d: d["governance"].__setitem__("freeze", True), "PASS_TREATED_AS_GRANT")
    check("universe", lambda d: d["universe"].__setitem__("scorer", "other"), "UNIVERSE_INCONSISTENT")

    def reverse(doc: dict) -> None:
        first = doc["per_seed"]["1"][0]["edge"]
        a, b = first.split(">", 1)
        doc["per_seed"]["1"].append({"edge": b + ">" + a, "A": True, "K": True})
    check("reverse", reverse, "REVERSE_DUPLICATE")

    short = json.loads(json.dumps(spec))
    short["seed_block"] = short["seed_block"][:5]
    if "TOO_FEW_SEEDS" not in schema_problems(short):
        found.append("short block did not produce TOO_FEW_SEEDS")

    failing = json.loads(json.dumps(spec))
    for rows in failing["per_seed"].values():
        for row in rows:
            row["K"] = False
    result = validate(failing)
    if "C1_BELOW_60" not in result["refusals"]:
        found.append("K-free candidate did not fail C1")
    return found


def check() -> int:
    found: list[str] = []
    if not SCHEMA_PATH.exists():
        found.append("schema artifact is missing")
    elif SCHEMA_PATH.read_text(encoding="utf-8") != json.dumps(schema(), indent=2) + "\n":
        found.append("schema artifact is stale")
    if not PAGE_PATH.exists():
        found.append("schema page is missing")
    elif PAGE_PATH.read_text(encoding="utf-8") != page() + "\n":
        found.append("schema page is stale")
    if not CANDIDATE_PATH.exists():
        found.append("candidate artifact is missing")
    else:
        result = validate(json.loads(CANDIDATE_PATH.read_text(encoding="utf-8")))
        if not result["schema_ok"]:
            found.append("candidate schema refusals: %r" % result["schema"])
        print("candidate schema: %s" % ("clean" if result["schema_ok"] else "FAIL"))
        print("candidate gate: %s" % (result["gate"] or {}).get("status", "UNKNOWN"))
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 successor schema: clean")
    return 0


def write() -> int:
    SCHEMA_PATH.write_text(json.dumps(schema(), indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(page() + "\n", encoding="utf-8")
    print("wrote %s and %s" % (SCHEMA_PATH, PAGE_PATH))
    return check()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--validate", metavar="PATH")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.check:
        return check()
    if args.validate:
        path = Path(args.validate)
        result = validate(json.loads(path.read_text(encoding="utf-8")))
        print(json.dumps(result, indent=2))
        return 0 if not result["refusals"] else 1
    found = self_test()
    for problem in found:
        print("FAIL:", problem)
    if not found:
        print("A1 successor schema: self-test clean")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
