"""A provenance tracer: claim -> parent structures -> world vocabulary.

The closed study's per-claim rule asked whether the immediately preceding **event**
was the world's.  This instrument asks a different question: can a claim be traced
back, through the parent-structure ids its payload carries, to world observations?

It is a measurement in search of a protocol, not a study, and it makes no claim
about the organism.  Its resolution is stated exactly, because the two are easy to
confuse:

  structures reference each other by **structure id**, never by event id, so the
  trace terminates in a structure whose content carries **world vocabulary** --
  tags that appear in world events.  A chain is `world_rooted` when every structure
  on it carries such content and at least one terminal exists; `self_only` when no
  structure on it does; `mixed` when some do and some do not; and `unresolved`,
  with a reason, when the walk cannot reach a terminal.

That is weaker than "descends from a particular observation" and stronger than
"the row was stored during sleep".  The difference is the whole point of the
instrument, so the status vocabulary keeps it visible rather than compressing it
into a boolean.

The controls are the load-bearing part: fixtures with **known** ancestry, run before
any real data, plus a check that emptying the world vocabulary flips the
world-derived control to `self_only` -- a control that could not fire would prove
nothing (AGENTS rule 25).  Isolated defects are not enough: a claim may have one
resolvable branch and one missing, cyclic or truncation-cut branch, and a tracer
that reports the first as `world_rooted` has hidden the second.  Those mixed
lineages have their own controls, and any defect marks the status `_incomplete`.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Iterable

from organica.memory import _extract_tags  # noqa: E402

MAX_DEPTH = 7          # the engine's own get_ancestry(max_depth=7)

STATUSES = ("world_rooted", "mixed", "self_only",
            "world_rooted_incomplete", "mixed_incomplete", "self_only_incomplete",
            "unresolved_missing_records", "unresolved_cycle",
            "unresolved_depth_truncated", "unresolved_nothing_resolved",
            "unresolved_no_ancestry")

#: A resolved branch does not make a lineage complete.  When any part of the
#: ancestry is missing, cyclic or truncation-cut, the status carries
#: `_incomplete` and `defects` names the reason, while `terminals` and `nodes`
#: still report what did resolve.  A summary of the resolved branch and a
#: statement about the whole lineage are different things, and only the second
#: may be read as `world_rooted`.
INCOMPLETE_SUFFIX = "_incomplete"


def _strings(obj: Any) -> Iterable[str]:
    """Every string leaf of a payload, in a field-agnostic walk."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _strings(value)
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            yield from _strings(value)


def content_tags(payload: dict, vocabulary: set[str]) -> set[str]:
    """The tags a structure carries that the world also uses.

    Field-agnostic on purpose: the payloads put their content in different keys by
    type (`source`/`target`, `members`, `context`, `probe_payload`), and an
    instrument that only read one of them would report a structure as empty when
    it is not.  Only **values** are read, so a field's NAME never contributes.
    """
    found: set[str] = set()
    for text in _strings(payload):
        found.update(t for t in _extract_tags(text) if t in vocabulary)
    return found


def build_index(payloads: Iterable[dict]) -> dict[str, dict]:
    """id -> payload, for every stored structure that carries an id."""
    index: dict[str, dict] = {}
    for payload in payloads:
        node_id = payload.get("id")
        if isinstance(node_id, str) and node_id:
            index[node_id] = payload
    return index


def trace(claim: dict, index: dict[str, dict], vocabulary: set[str],
          max_depth: int = MAX_DEPTH) -> dict[str, Any]:
    """Follow `parent_ids` from one claim to its terminal structures.

    Breadth-first, cycle-safe, depth-capped.  `parents` is the number of parent
    references that did not resolve, because a chain that silently drops an
    unresolvable ancestor would look complete when it is not.
    """
    root = claim.get("id")
    if not isinstance(root, str) or not root:
        return {"status": "unresolved_nothing_resolved", "reason": "claim has no id",
                "nodes": [], "terminals": [], "missing": 0, "cycle": False,
                "depth_hit": False}
    nodes: list[dict] = []
    seen: set[str] = set()
    frontier = [root]
    missing = 0
    cycle = False
    depth_hit = False
    depth = 0
    while frontier:
        if depth > max_depth:
            depth_hit = True
            break
        nxt: list[str] = []
        for node_id in frontier:
            if node_id in seen:
                cycle = True
                continue
            seen.add(node_id)
            node = index.get(node_id)
            if node is None:
                missing += 1
                continue
            parents = [p for p in (node.get("parent_ids") or []) if isinstance(p, str)]
            nodes.append({"id": node_id, "type": node.get("type"),
                          "world_tags": sorted(content_tags(node, vocabulary)),
                          "parents": len(parents)})
            nxt.extend(parents)
        frontier = nxt
        depth += 1
    terminals = [n for n in nodes if n["parents"] == 0]
    # Grounding is judged on ANCESTORS only.  A claim's own surface words are the
    # thing being explained, not evidence for its origin: crediting them would make
    # every claim that names a world tag "world_rooted" by definition.
    ancestors = nodes[1:]
    grounded = [n for n in ancestors if n["world_tags"]]
    defects = []
    if missing:
        defects.append("missing_records")
    if cycle:
        defects.append("cycle")
    if depth_hit:
        defects.append("depth_truncated")
    if not nodes:
        if missing:
            status = "unresolved_missing_records"
            reason = "the claim itself is not among the stored structures"
        else:
            status, reason = "unresolved_nothing_resolved", "no structure resolved"
    elif not terminals and depth_hit:
        status, reason = "unresolved_depth_truncated", f"no terminal within depth {max_depth}"
    elif not terminals and cycle:
        status, reason = "unresolved_cycle", "the parent links form a cycle"
    elif not terminals:
        status, reason = "unresolved_missing_records", "parents referenced but not stored"
    elif not ancestors:
        status, reason = ("unresolved_no_ancestry",
                          "the claim is itself a terminal: it has no parent links")
    else:
        if len(grounded) == len(ancestors):
            base, base_reason = ("world_rooted",
                                 "every resolved ancestor carries world vocabulary")
        elif not grounded:
            base, base_reason = ("self_only",
                                 "no resolved ancestor carries world vocabulary")
        else:
            base, base_reason = ("mixed",
                                 "some resolved ancestors carry world vocabulary, "
                                 "some do not")
        if defects:
            status = base + INCOMPLETE_SUFFIX
            reason = (f"{base_reason}; ancestry incomplete ({', '.join(defects)}), so "
                      f"this describes the resolved branch only")
        else:
            status, reason = base, base_reason
    return {"status": status, "reason": reason, "nodes": nodes,
            "terminals": [n["id"] for n in terminals], "missing": missing,
            "cycle": cycle, "depth_hit": depth_hit, "defects": defects,
            "complete": not defects}


# ---------------------------------------------------------------------------
# Controls: fixtures whose ancestry is known by construction.
# ---------------------------------------------------------------------------

def _fixtures() -> dict[str, tuple[dict, dict[str, dict], set[str], str]]:
    vocab = {"willow", "teal", "cedar", "maple"}
    world_phrase = {"id": "phrase_1", "type": "phrase_candidate",
                    "members": ["willow", "teal"], "parent_ids": []}
    world_concept = {"id": "concept_1", "type": "concept_candidate",
                     "members": ["cedar", "maple"], "parent_ids": []}
    claim_world = {"id": "pred_w", "type": "prediction_candidate",
                   "source": "willow", "target": "teal", "parent_ids": ["phrase_1"]}
    claim_self = {"id": "pred_s", "type": "prediction_candidate",
                  "source": "willow", "target": "teal", "parent_ids": ["pred_s0"]}
    self_parent = {"id": "pred_s0", "type": "prediction_candidate",
                   "source": "zeta", "target": "kappa", "parent_ids": []}
    claim_mixed = {"id": "pred_m", "type": "prediction_candidate",
                   "source": "willow", "target": "teal",
                   "parent_ids": ["phrase_1", "pred_s0"]}
    claim_missing = {"id": "pred_x", "type": "prediction_candidate",
                     "source": "willow", "target": "teal", "parent_ids": ["ghost_1"]}
    cyc_a = {"id": "cyc_a", "type": "hypothesis", "parent_ids": ["cyc_b"]}
    cyc_b = {"id": "cyc_b", "type": "hypothesis", "parent_ids": ["cyc_a"]}
    claim_cycle = {"id": "cyc_a", "type": "hypothesis", "parent_ids": ["cyc_b"]}
    deep = [{"id": f"d{i}", "type": "process_candidate", "parent_ids": [f"d{i + 1}"]}
            for i in range(MAX_DEPTH + 2)]
    deep.append({"id": f"d{MAX_DEPTH + 2}", "type": "concept_candidate",
                 "members": ["willow"], "parent_ids": []})
    claim_deep = {"id": "d0", "type": "process_candidate", "parent_ids": ["d1"]}
    # Mixed-lineage fixtures: one resolvable branch plus one defective branch, so a
    # resolved terminal can no longer hide the defect.
    claim_wm = {"id": "pred_wm", "type": "prediction_candidate",
                "source": "willow", "target": "teal",
                "parent_ids": ["phrase_1", "ghost_1"]}
    claim_sc = {"id": "pred_sc", "type": "prediction_candidate",
                "source": "willow", "target": "teal",
                "parent_ids": ["pred_s0", "cyc_a"]}
    deep_tagged = [{"id": f"d{i}", "type": "process_candidate",
                    "members": ["maple"], "parent_ids": [f"d{i + 1}"]}
                   for i in range(MAX_DEPTH + 2)]
    deep_tagged.append({"id": f"d{MAX_DEPTH + 2}", "type": "concept_candidate",
                        "members": ["maple"], "parent_ids": []})
    claim_wd = {"id": "pred_wd", "type": "prediction_candidate",
                "source": "willow", "target": "teal",
                "parent_ids": ["phrase_1", "d0"]}
    return {
        "world_derived": (claim_world,
                          build_index([claim_world, world_phrase, world_concept]),
                          vocab, "world_rooted"),
        "self_only": (claim_self, build_index([claim_self, self_parent]),
                      vocab, "self_only"),
        "mixed": (claim_mixed, build_index([claim_mixed, world_phrase, self_parent]),
                  vocab, "mixed"),
        "missing_parent": (claim_missing, build_index([claim_missing]), vocab,
                           "unresolved_missing_records"),
        "cycle": (claim_cycle, build_index([claim_cycle, cyc_a, cyc_b]), vocab,
                  "unresolved_cycle"),
        "depth_capped": (claim_deep, build_index([claim_deep, *deep]), vocab,
                         "unresolved_depth_truncated"),
        "world_rooted_with_missing_parent": (
            claim_wm, build_index([claim_wm, world_phrase]), vocab,
            "world_rooted_incomplete"),
        "self_only_with_cycle": (
            claim_sc, build_index([claim_sc, self_parent, cyc_a, cyc_b]), vocab,
            "self_only_incomplete"),
        "world_rooted_with_depth_truncation": (
            claim_wd, build_index([claim_wd, world_phrase, *deep_tagged]), vocab,
            "world_rooted_incomplete"),
    }


def run_controls() -> dict[str, Any]:
    """Prove the tracer on ancestry it knows before it touches real data."""
    results = {}
    for name, (claim, index, vocab, expected) in _fixtures().items():
        got = trace(claim, index, vocab)
        results[name] = {"expected": expected, "status": got["status"],
                         "passed": got["status"] == expected,
                         "reason": got["reason"]}
    # The control must be able to fire: strip the world vocabulary and the
    # world-derived fixture has to stop being world-rooted.
    claim, index, vocab, _ = _fixtures()["world_derived"]
    flipped = trace(claim, index, set())
    results["vocabulary_removed_flips_control"] = {
        "expected": "self_only", "status": flipped["status"],
        "passed": flipped["status"] == "self_only",
        "reason": "a tracer that cannot change its answer is decoration",
    }
    return {"controls": results,
            "all_passed": all(r["passed"] for r in results.values()),
            "resolution": ("structure ids, not event ids: world_rooted means every "
                           "ancestor carries tags the world uses")}


def trace_claims(claims: Iterable[dict], payloads: Iterable[dict],
                 world_vocabulary: set[str]) -> dict[str, Any]:
    """Trace a set of claims and summarise the statuses.  No verdict, no threshold."""
    index = build_index(payloads)
    # A claim is a structure too: index it before tracing so a readout candidate
    # whose own row was pruned is reported as missing, not as nothing resolved.
    for claim in claims:
        node_id = claim.get("id")
        if isinstance(node_id, str) and node_id and node_id not in index:
            index[node_id] = claim
    rows = []
    for claim in claims:
        got = trace(claim, index, world_vocabulary)
        rows.append({"id": claim.get("id"), "type": claim.get("type"),
                     **{k: got[k] for k in ("status", "reason", "missing", "cycle")},
                     "depth": len(got["nodes"])})
    counts: dict[str, int] = {s: 0 for s in STATUSES}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {"claims": len(rows), "statuses": counts, "rows": rows,
            "note": "instrument diagnostic; no threshold and no verdict"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Provenance tracer (controls only).")
    ap.add_argument("--controls", action="store_true",
                    help="run the known-ancestry controls and exit non-zero on failure")
    args = ap.parse_args(argv)
    if not args.controls:
        ap.print_help()
        return 2
    result = run_controls()
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
