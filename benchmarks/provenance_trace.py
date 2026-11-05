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
import pathlib
import subprocess
import sys
import time
from collections import defaultdict
from typing import Any, Iterable

from organica.memory import _extract_tags  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent

MAX_DEPTH = 7          # the engine's own get_ancestry(max_depth=7)

#: The diagnostic's plan, committed before the run, and its two artifacts.
PLAN_DOC = "docs/PROVENANCE-ANALYSIS-PLAN.md"
DIAGNOSTIC_OUT = "docs/provenance_diagnostic.json"
DIAGNOSTIC_DOC = "docs/PROVENANCE-DIAGNOSTIC.md"

#: A claim, for the tracer, is any structure of these types.  Same test the
#: study's own claim selector applies (`_claim_edges`), which keeps the traced
#: population equal to the study's claim population.
CLAIM_TYPE_WORDS = ("prediction", "hypothesis")

#: Ancestor depth, bucketed so a shallow result cannot read as a deep one.
DEPTH_BUCKETS = ("0", "1", "2", "3", "4-6", "7+")

#: Why a lineage is incomplete, counted separately: a chain cut by our own depth
#: cap is not a chain whose ancestors were pruned.
DEFECTS = ("missing_records", "cycle", "depth_truncated")

#: The counting units, in the order they nest.  Named as what they count.
LEVEL_ROWS = (
    ("study_claim_rows",
     "raw stored claim rows with an asserted edge (the study's `_claim_edges` count)"),
    ("raw_claim_rows", "raw stored claim rows (all claim-typed rows)"),
    ("unique_structures", "unique structure ids"),
    ("unique_structures_with_edge", "unique structure ids with an asserted edge"),
    ("unique_asserted_edges", "unique asserted edges"),
    ("edges_with_complete_rooted_claim",
     "unique asserted edges with a complete `world_rooted` claim"),
)

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


def _detect_cycle(root: str, edges: dict[str, list[str]]) -> bool:
    """True only for a back edge to a node on the CURRENT path.

    Convergence is not a loop.  In a diamond lineage two parents share an ancestor:
    that ancestor is reached twice, but it is fully explored by the time the second
    branch arrives, so no path returns to a node it is still inside.  Treating every
    repeated visit as a cycle marks a complete multi-parent lineage `_incomplete`,
    which is why this tracks colour rather than a visited set.
    """
    white, grey, black = 0, 1, 2
    colour: dict[str, int] = defaultdict(int)
    colour[root] = grey
    stack: list[tuple[str, Any]] = [(root, iter(edges.get(root, ())))]
    while stack:
        node, children = stack[-1]
        advanced = False
        for parent in children:
            if colour[parent] == grey:
                return True
            if colour[parent] == white:
                colour[parent] = grey
                stack.append((parent, iter(edges.get(parent, ()))))
                advanced = True
                break
        if not advanced:
            colour[node] = black
            stack.pop()
    return False


def build_index(payloads: Iterable[dict]) -> dict[str, dict]:
    """id -> payload, for every stored structure that carries an id."""
    index: dict[str, dict] = {}
    for payload in payloads:
        node_id = payload.get("id")
        if isinstance(node_id, str) and node_id:
            index[node_id] = payload
    return index


def dedupe_candidates(payloads: Iterable[dict]) -> list[dict]:
    """One payload per candidate id: the highest-generation snapshot of it.

    The engine re-stores every living candidate each sleep cycle, so the frozen
    snapshot holds the same logical structure many times.  Tracing every copy
    would count one lineage once per cycle it survived; this keeps the newest
    state of each, which is the state the readout reads.
    """
    best: dict[str, tuple[int, int, dict]] = {}
    for order, payload in enumerate(payloads):
        node_id = payload.get("id")
        if not isinstance(node_id, str) or not node_id:
            continue
        gen = payload.get("generation")
        rank = (int(gen) if isinstance(gen, int) else 1, order)
        if node_id not in best or rank > best[node_id][:2]:
            best[node_id] = (*rank, payload)
    return [payload for _rank, payload in
            ((v[:2], v[2]) for v in best.values())]


def claim_structures(payloads: Iterable[dict]) -> list[dict]:
    """The claim-typed structures of a snapshot, for tracing."""
    out = []
    for payload in payloads:
        kind = payload.get("type") or payload.get("event_type") or ""
        if any(word in kind for word in CLAIM_TYPE_WORDS):
            out.append(payload)
    return out


def edge_key(claim: dict) -> tuple[str, str] | None:
    """The pair a claim asserts, or None.  Same rule `_claim_edges` applies."""
    kind = claim.get("type") or claim.get("event_type") or ""
    if "prediction" in kind:
        pair = (claim.get("source"), claim.get("target"))
    elif "hypothesis" in kind:
        pair = (claim.get("subject"), claim.get("expectation"))
    else:
        pair = (None, None)
    if all(isinstance(v, str) and v for v in pair):
        return pair  # type: ignore[return-value]
    return None


def has_asserted_edge(claim: dict) -> bool:
    """Whether the claim names the pair it asserts, as `_claim_edges` requires."""
    return edge_key(claim) is not None


def parent_link_levels(raw_claims: Iterable[dict],
                       latest_claims: Iterable[dict]) -> dict[str, dict[str, int]]:
    """Whether an id EVER had parents, versus whether its latest snapshot does.

    Deduplication keeps the highest-generation snapshot of a structure, so "this
    structure has no parents" describes that snapshot only.  An earlier snapshot
    of the same id may have carried links, and only the raw rows can say so.  The
    two questions are counted separately and never merged: a structure that lost
    its links is not a structure that never had any.
    """
    out: dict[str, dict[str, int]] = {}
    for word in CLAIM_TYPE_WORDS:
        raw = [c for c in raw_claims
               if word in (c.get("type") or c.get("event_type") or "")]
        latest = [c for c in latest_claims
                  if word in (c.get("type") or c.get("event_type") or "")]
        ever = {c["id"] for c in raw
                if isinstance(c.get("id"), str) and (c.get("parent_ids") or [])}
        now = {c["id"] for c in latest
               if isinstance(c.get("id"), str) and (c.get("parent_ids") or [])}
        out[word] = {
            "raw_rows": len(raw),
            "raw_rows_with_parents": sum(1 for c in raw if c.get("parent_ids")),
            "unique_ids": len({c["id"] for c in raw if isinstance(c.get("id"), str)}),
            "ids_ever_with_parents": len(ever),
            "ids_latest_with_parents": len(now),
            "ids_with_parents_only_in_earlier_snapshots": len(ever - now),
        }
    return out


def counting_levels(raw_claims: Iterable[dict], claims: Iterable[dict],
                    status_by_id: dict[str, str]) -> dict[str, Any]:
    """The same lineage question at three resolutions, and how they map.

    A survivor is re-stored every sleep cycle, so the raw snapshot holds the same
    logical claim many times: the study's per-claim rule counts those **rows**
    (`_claim_edges`), the tracer walks **unique structure ids**, and a pair of
    tags may be asserted by several structures.  Three counts, three units.  None
    may stand in for another, and the tracer says which one it walked.
    """
    raw = list(raw_claims)
    unique = list(claims)
    per_id: dict[str, int] = defaultdict(int)
    for claim in raw:
        node_id = claim.get("id")
        if isinstance(node_id, str) and node_id:
            per_id[node_id] += 1
    edges: dict[tuple[str, str], set[str]] = defaultdict(set)
    for claim in unique:
        key = edge_key(claim)
        node_id = claim.get("id")
        if key and isinstance(node_id, str) and node_id:
            edges[key].add(node_id)

    def stat(values: list[int]) -> dict[str, Any]:
        if not values:
            return {"min": 0, "median": 0.0, "max": 0, "mean": 0.0}
        middle = len(values) // 2
        median = (values[middle] if len(values) % 2 else
                  (values[middle - 1] + values[middle]) / 2)
        return {"min": values[0], "median": median, "max": values[-1],
                "mean": round(sum(values) / len(values), 3)}

    return {
        "raw_claim_rows": len(raw),
        "raw_claim_rows_with_edge": sum(1 for c in raw if edge_key(c)),
        "unique_structures": len(unique),
        "unique_structures_with_edge": sum(1 for c in unique if edge_key(c)),
        "unique_asserted_edges": len(edges),
        "edges_with_complete_rooted_claim": sum(
            1 for ids in edges.values()
            if any(status_by_id.get(i) == "world_rooted" for i in ids)),
        "rows_per_structure": stat(sorted(per_id.values())),
        "structures_per_edge": stat(sorted(len(ids) for ids in edges.values())),
    }


def depth_bucket(depth: int) -> str:
    if depth <= 3:
        return str(max(depth, 0))
    return "4-6" if depth <= 6 else "7+"


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
    edges: dict[str, list[str]] = {}
    missing_ids: set[str] = set()
    frontier = [root]
    depth_hit = False
    depth = 0
    while frontier:
        if depth > max_depth:
            depth_hit = True
            break
        nxt: list[str] = []
        for node_id in frontier:
            if node_id in seen:
                continue
            seen.add(node_id)
            node = index.get(node_id)
            if node is None:
                missing_ids.add(node_id)
                continue
            parents = [p for p in (node.get("parent_ids") or []) if isinstance(p, str)]
            nodes.append({"id": node_id, "type": node.get("type"),
                          "world_tags": sorted(content_tags(node, vocabulary)),
                          "parents": len(parents)})
            edges[node_id] = []
            for parent in parents:
                if parent in index:
                    edges[node_id].append(parent)
                else:
                    missing_ids.add(parent)
                nxt.append(parent)
        frontier = nxt
        depth += 1
    cycle = _detect_cycle(root, edges) if root in edges else False
    missing = len(missing_ids)
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
    # Diamond lineage: two parents sharing one ancestor.  The ancestor is reached by
    # two paths, which is convergence and must stay complete.
    diamond_left = {"id": "dia_l", "type": "phrase_candidate",
                    "members": ["willow"], "parent_ids": ["dia_root"]}
    diamond_right = {"id": "dia_r", "type": "phrase_candidate",
                     "members": ["teal"], "parent_ids": ["dia_root"]}
    diamond_root = {"id": "dia_root", "type": "concept_candidate",
                    "members": ["cedar"], "parent_ids": []}
    claim_diamond = {"id": "pred_dia", "type": "prediction_candidate",
                     "source": "willow", "target": "teal",
                     "parent_ids": ["dia_l", "dia_r"]}
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
        "diamond_shared_ancestor": (
            claim_diamond,
            build_index([claim_diamond, diamond_left, diamond_right, diamond_root]),
            vocab, "world_rooted"),
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
                     "depth": len(got["nodes"]),
                     "ancestor_depth": max(0, len(got["nodes"]) - 1),
                     "defects": got["defects"]})
    summary = summarise_rows(rows)
    summary.update({"rows": rows,
                    "note": "instrument diagnostic; no threshold and no verdict"})
    return summary


def _empty() -> dict[str, int]:
    return {s: 0 for s in STATUSES}


def summarise_rows(rows: Iterable[dict]) -> dict[str, Any]:
    """Count statuses overall, by claim type and by lineage depth.

    The complete, incomplete and unresolved families are reported side by side
    and are never summed into one number: only `complete_world_rooted` may be
    described as rooted, and an incomplete lineage is not a rooted one with a
    note attached.
    """
    rows = list(rows)
    statuses = _empty()
    by_type: dict[str, dict[str, int]] = {}
    by_depth: dict[str, dict[str, int]] = {b: _empty() for b in DEPTH_BUCKETS}
    defects = {name: 0 for name in DEFECTS}
    for row in rows:
        status = row["status"]
        statuses[status] = statuses.get(status, 0) + 1
        kind = row.get("type") or "unknown"
        by_type.setdefault(kind, _empty())[status] += 1
        by_depth[depth_bucket(row.get("ancestor_depth", 0))][status] += 1
        for defect in row.get("defects") or ():
            defects[defect] = defects.get(defect, 0) + 1
    complete = {s: n for s, n in statuses.items()
                if not s.startswith("unresolved_") and not s.endswith(INCOMPLETE_SUFFIX)}
    incomplete = {s: n for s, n in statuses.items() if s.endswith(INCOMPLETE_SUFFIX)}
    unresolved = {s: n for s, n in statuses.items() if s.startswith("unresolved_")}
    return {"claims": len(rows), "statuses": statuses,
            "complete": complete, "incomplete": incomplete, "unresolved": unresolved,
            "complete_world_rooted": statuses["world_rooted"],
            "incomplete_total": sum(incomplete.values()),
            "unresolved_total": sum(unresolved.values()),
            "by_type": by_type, "by_depth": by_depth, "defects": defects}


def merge_summaries(summaries: Iterable[dict]) -> dict[str, Any]:
    """Pool per-seed summaries without collapsing their families together."""
    pooled = _empty()
    by_type: dict[str, dict[str, int]] = {}
    by_depth: dict[str, dict[str, int]] = {b: _empty() for b in DEPTH_BUCKETS}
    claims = with_edge = indexed = 0
    defects = {name: 0 for name in DEFECTS}
    levels: dict[str, int] = defaultdict(int)
    parent_links: dict[str, dict[str, int]] = {}
    for summary in summaries:
        for name, n in (summary.get("defects") or {}).items():
            defects[name] = defects.get(name, 0) + n
        for name, n in (summary.get("levels") or {}).items():
            if isinstance(n, int):
                levels[name] += n
        for kind, row in (summary.get("parent_links") or {}).items():
            target = parent_links.setdefault(kind, {})
            for name, n in row.items():
                if isinstance(n, int):
                    target[name] = target.get(name, 0) + n
        claims += summary.get("claims", 0)
        with_edge += summary.get("claims_with_asserted_edge", 0)
        indexed += summary.get("structures_indexed", 0)
        for status, n in summary["statuses"].items():
            pooled[status] = pooled.get(status, 0) + n
        for kind, row in summary.get("by_type", {}).items():
            target = by_type.setdefault(kind, _empty())
            for status, n in row.items():
                target[status] = target.get(status, 0) + n
        for bucket, row in summary.get("by_depth", {}).items():
            target = by_depth.setdefault(bucket, _empty())
            for status, n in row.items():
                target[status] = target.get(status, 0) + n
    complete = {s: n for s, n in pooled.items()
                if not s.startswith("unresolved_") and not s.endswith(INCOMPLETE_SUFFIX)}
    incomplete = {s: n for s, n in pooled.items() if s.endswith(INCOMPLETE_SUFFIX)}
    unresolved = {s: n for s, n in pooled.items() if s.startswith("unresolved_")}
    return {"claims": claims, "claims_with_asserted_edge": with_edge,
            "structures_indexed": indexed, "statuses": pooled,
            "complete": complete, "incomplete": incomplete, "unresolved": unresolved,
            "complete_world_rooted": pooled["world_rooted"],
            "incomplete_total": sum(incomplete.values()),
            "unresolved_total": sum(unresolved.values()),
            "by_type": by_type, "by_depth": by_depth, "defects": defects,
            "levels": dict(levels), "parent_links": parent_links}


# ---------------------------------------------------------------------------
# The diagnostic: the instrument pointed at the five already-used calibration
# seeds, under a plan committed before the run.
# ---------------------------------------------------------------------------

def _assert_diagnostic(art: dict) -> None:
    """A diagnostic may not carry a threshold, a verdict or an authorisation."""
    if art.get("no_threshold") is not True or art.get("no_verdict") is not True:
        raise AssertionError("the diagnostic must declare no threshold and no verdict")
    if art.get("authorises_confirmatory") is not False:
        raise AssertionError("the diagnostic may not authorise a confirmatory run")
    if art.get("study_reopened") is not False:
        raise AssertionError("the diagnostic may not reopen the closed study")


def _git_head_for(path: str) -> str | None:
    """The commit a document was last changed at, or None outside a checkout."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%H", "--", path],
                             cwd=ROOT, capture_output=True, text=True, check=False)
    except OSError:
        return None
    head = out.stdout.strip()
    return head or None


def _trace_seed(rk: Any, seed: int, cap: int) -> dict[str, Any]:
    """One calibration cell: two snapshots, their claim structures traced."""
    world = rk.generate_compositional_world(seed=seed, cycles=rk.CYCLES)
    formation = rk.conditioned_formation_stream(world, seed, rk.WITHHELD)
    revision = rk.conditioned_revision_stream(world, seed,
                                              formation["raw_cells"][-1], rk.WITHHELD)
    relations = rk.relation_sets(world, rk.WITHHELD)
    engine = rk.run_engine(formation, revision, seed, cap,
                           frozenset(relations["withheld"]),
                           collect_structures=True)
    vocabulary = {t for row in formation["events"] + revision["events"]
                  for t in row.split()}
    entry: dict[str, Any] = {"seed": seed}
    withheld = frozenset(relations["withheld"])
    for limb in ("formation", "revision"):
        raw = engine["structures"][limb]
        payloads = dedupe_candidates(raw)
        claims = claim_structures(payloads)
        summary = trace_claims(claims, payloads, vocabulary)
        rows = summary.pop("rows")
        status_by_id = {r["id"]: r["status"] for r in rows if r.get("id")}
        levels = counting_levels(claim_structures(raw), claims, status_by_id)
        # The study's own claim count, from the study's own selector, must equal
        # this tracer's raw-row count at the same resolution.  If it does not, the
        # two instruments are counting different things again.
        levels["study_claim_rows"] = len(rk._claim_edges(raw, withheld))
        if levels["study_claim_rows"] != levels["raw_claim_rows_with_edge"]:
            raise AssertionError(
                f"{limb}: the study's claim count "
                f"({levels['study_claim_rows']}) and this tracer's raw-row count "
                f"({levels['raw_claim_rows_with_edge']}) disagree")
        summary["levels"] = levels
        summary["parent_links"] = parent_link_levels(claim_structures(raw), claims)
        summary["claims_with_asserted_edge"] = levels["unique_structures_with_edge"]
        summary["structures_indexed"] = len(payloads)
        entry[limb] = summary
    return entry


def _seed_cache(seed: int, cap: int, hashseed: str | None) -> pathlib.Path:
    return ROOT / ".scratch" / f"provenance_v4_{seed}_{cap}_{hashseed or 'unpinned'}.json"


def run_diagnostic(seeds: tuple[int, ...] | None = None,
                   budget_seconds: float = 210.0) -> dict[str, Any]:
    """Trace the claims of the five calibration cells.  Descriptive, not a study.

    Same seeds, same cap, same hash pin as the calibration and the postmortem, so
    the snapshots are the ones those artifacts already describe.  Nothing here
    evaluates a criterion: there is no threshold to pass and no verdict to reach.
    """
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from benchmarks import reusable_knowledge as rk

    if rk.hash_seed() is None:
        raise ValueError("set PYTHONHASHSEED to the calibration value: this re-reads "
                         "the calibration cells")
    controls = run_controls()
    if not controls["all_passed"]:
        raise RuntimeError("the tracer's controls must pass before it is pointed at "
                           "real data")
    target = tuple(seeds) if seeds else rk.CALIBRATION_SEEDS
    cap = rk.MAX_PREDICTIONS
    started = time.monotonic()
    per_seed: list[dict] = []
    for seed in target:
        # A cell takes minutes, longer than one command may run, so each cell is
        # cached and a re-invocation resumes rather than restarting.  The artifact
        # is written only when every requested seed is present.
        cache = _seed_cache(seed, cap, rk.hash_seed())
        if cache.exists():
            per_seed.append(json.loads(cache.read_text(encoding="utf-8")))
            continue
        if per_seed and time.monotonic() - started > budget_seconds:
            break
        entry = _trace_seed(rk, seed, cap)
        cache.write_text(json.dumps(entry, sort_keys=True) + "\n", encoding="utf-8")
        per_seed.append(entry)
    done = [entry["seed"] for entry in per_seed]
    if len(done) < len(target):
        return {"artifact_written": False, "computed": done,
                "pending": [s for s in target if s not in done],
                "note": "resumable: rerun the same command, finished cells are cached"}

    totals = {limb: merge_summaries(entry[limb] for entry in per_seed)
              for limb in ("formation", "revision")}
    art = {
        "kind": "provenance_diagnostic",
        "instrument": "benchmarks/provenance_trace.py",
        "plan_doc": PLAN_DOC,
        "plan_frozen_at_commit": _git_head_for(PLAN_DOC),
        "controls": {"all_passed": controls["all_passed"],
                     "count": len(controls["controls"])},
        "seeds": list(target),
        "seed_set": ("the five already-used calibration seeds; no confirmatory seed "
                     "was run or touched"),
        "cap": cap,
        "variant": rk.variant_label(cap),
        "pythonhashseed": rk.hash_seed(),
        "confirmatory_seeds_touched": False,
        "study_reopened": False,
        "authorises_confirmatory": False,
        "no_threshold": True,
        "no_verdict": True,
        "question": ("do the stored structures carry usable parent chains, and how "
                     "often can the tracer resolve them?"),
        "resolution": ("world_rooted means vocabulary overlap across a complete "
                       "ancestor chain; it is not observation-level provenance"),
        "totals": totals,
        "seeds_detail": per_seed,
        "note": ("Descriptive diagnostic on already-used seeds. The closed study's "
                 "verdict is unchanged, no criterion is evaluated here, and nothing "
                 "in this artifact authorises a confirmatory run."),
        "artifact_written": True,
    }
    _assert_diagnostic(art)
    (ROOT / DIAGNOSTIC_OUT).write_text(json.dumps(art, indent=1, sort_keys=True) + "\n",
                                       encoding="utf-8")
    (ROOT / DIAGNOSTIC_DOC).write_text(render_report(art), encoding="utf-8")
    return art


def _lvl(entry: dict, limb: str, key: str, field: str) -> Any:
    """One counting level from a per-seed entry, or 0 when it was not recorded."""
    node = ((entry.get(limb) or {}).get("levels") or {}).get(key) or {}
    return node.get(field, 0)


def _family_row(summary: dict, limb: str) -> str:
    return f"| {limb} | {summary['claims']} | {summary['claims_with_asserted_edge']} | " \
           f"{summary['complete_world_rooted']} | {summary['incomplete_total']} | " \
           f"{summary['unresolved_total']} |"


def render_report(art: dict) -> str:
    """The results document, generated from the artifact.  Never typed by hand."""
    totals = art["totals"]
    lines = [
        "# Provenance diagnostic — five already-used calibration seeds",
        "",
        "**Generated from [`docs/provenance_diagnostic.json`](provenance_diagnostic.json);",
        "do not edit by hand.** Regenerate with",
        "`PYTHONHASHSEED=0 python -m benchmarks.provenance_trace --report`.",
        "",
        f"Plan: [`{art['plan_doc']}`](PROVENANCE-ANALYSIS-PLAN.md), frozen at commit",
        f"`{art['plan_frozen_at_commit']}` before this run. Seeds:",
        f"{', '.join(str(s) for s in art['seeds'])} (calibration only), cap",
        f"`{art['cap']}`, variant `{art['variant']}`.",
        "",
        "## What this is, and what it is not",
        "",
        "A descriptive diagnostic of the instrument and of the lineage the engine",
        "records. **There is no threshold, no pass mark and no verdict in this",
        "document.** `world_rooted` means vocabulary overlap across a complete",
        "ancestor chain; it is not observation-level provenance, and nothing here",
        "validates transfer or reopens the closed study.",
        "",
        f"The tracer's {art['controls']['count']} controls passed before the run",
        "(`all_passed: " + str(art["controls"]["all_passed"]).lower() + "`).",
        "",
        "## Statuses, by limb",
        "",
        "| status | formation | revision |",
        "|---|---|---|",
    ]
    for status in STATUSES:
        lines.append(f"| `{status}` | {totals['formation']['statuses'].get(status, 0)} "
                     f"| {totals['revision']['statuses'].get(status, 0)} |")
    lines += [
        "",
        "The three families are counted separately and are never summed: a lineage",
        "with a resolvable branch and a missing, cyclic or truncated one is not a",
        "rooted lineage with a note attached.",
        "",
        "| family | limb | claims | with asserted edge | complete `world_rooted` | incomplete | unresolved |",
        "|---|---|---|---|---|---|---|",
        _family_row(totals["formation"], "formation"),
        _family_row(totals["revision"], "revision"),
        "",
        "### Why a lineage is incomplete",
        "",
        "| defect | formation | revision |",
        "|---|---|---|",
        *[f"| `{name}` | {totals['formation'].get('defects', {}).get(name, 0)} "
          f"| {totals['revision'].get('defects', {}).get(name, 0)} |"
          for name in DEFECTS],
        "",
        "## Counting units",
        "",
        "The same lineage question at three resolutions. A survivor is re-stored every",
        "sleep cycle, so the study's per-claim rule counts **raw snapshot rows**, while",
        "the tracer walks **unique structure ids**; a pair of tags may also be asserted",
        "by more than one structure, which is a third unit. None of the three may stand",
        "in for another.",
        "",
        "| unit | formation | revision |",
        "|---|---|---|",
        *[f"| {label} | {totals['formation'].get('levels', {}).get(key, 0)} "
          f"| {totals['revision'].get('levels', {}).get(key, 0)} |"
          for key, label in LEVEL_ROWS],
        "",
        "| seed | rows per structure (median / max) | structures per asserted edge (median / max) |",
        "|---|---|---|",
        *[f"| {entry['seed']} | {_lvl(entry, 'formation', 'rows_per_structure', 'median')} / "
          f"{_lvl(entry, 'formation', 'rows_per_structure', 'max')} | "
          f"{_lvl(entry, 'formation', 'structures_per_edge', 'median')} / "
          f"{_lvl(entry, 'formation', 'structures_per_edge', 'max')} |"
          for entry in art["seeds_detail"]],
        "",
        "## Parent links in the raw snapshots",
        "",
        "Deduplication keeps the highest-generation snapshot of a structure, so a",
        "statement that a structure has no parents describes that snapshot only. These",
        "counts ask both questions separately: whether **any** raw snapshot of an id",
        "carried parent links, and whether the **latest** one does. A structure that",
        "lost its links is not a structure that never had any.",
        "",
        "| type | limb | raw rows | raw rows with parents | unique ids | ids ever with parents | ids with parents in the latest snapshot | ids whose parents appear only in earlier snapshots |",
        "|---|---|---|---|---|---|---|---|",
        *[f"| `{kind}` | {limb} | {row.get('raw_rows', 0)} | {row.get('raw_rows_with_parents', 0)} "
          f"| {row.get('unique_ids', 0)} | {row.get('ids_ever_with_parents', 0)} "
          f"| {row.get('ids_latest_with_parents', 0)} "
          f"| {row.get('ids_with_parents_only_in_earlier_snapshots', 0)} |"
          for limb in ("formation", "revision")
          for kind, row in sorted((totals[limb].get("parent_links") or {}).items())],
        "",
        "## By claim type",
        "",
        "| type | limb | claims | complete `world_rooted` | incomplete | unresolved |",
        "|---|---|---|---|---|---|",
    ]
    for limb in ("formation", "revision"):
        for kind, row in sorted(totals[limb]["by_type"].items()):
            claims = sum(row.values())
            rooted = row.get("world_rooted", 0)
            incomplete = sum(n for s, n in row.items() if s.endswith(INCOMPLETE_SUFFIX))
            unresolved = sum(n for s, n in row.items() if s.startswith("unresolved_"))
            lines.append(f"| `{kind}` | {limb} | {claims} | {rooted} | {incomplete} | {unresolved} |")
    lines += [
        "",
        "## By lineage depth (ancestors resolved)",
        "",
        "| depth | limb | claims | complete `world_rooted` | incomplete | unresolved |",
        "|---|---|---|---|---|---|",
    ]
    for limb in ("formation", "revision"):
        for bucket in DEPTH_BUCKETS:
            row = totals[limb]["by_depth"].get(bucket) or {}
            claims = sum(row.values())
            if not claims:
                continue
            rooted = row.get("world_rooted", 0)
            incomplete = sum(n for s, n in row.items() if s.endswith(INCOMPLETE_SUFFIX))
            unresolved = sum(n for s, n in row.items() if s.startswith("unresolved_"))
            lines.append(f"| {bucket} | {limb} | {claims} | {rooted} | {incomplete} | {unresolved} |")
    lines += [
        "",
        "## Per seed",
        "",
        "| seed | limb | claims | complete `world_rooted` | incomplete | unresolved |",
        "|---|---|---|---|---|---|",
    ]
    for entry in art["seeds_detail"]:
        for limb in ("formation", "revision"):
            summary = entry[limb]
            lines.append(f"| {entry['seed']} | {limb} | {summary['claims']} "
                         f"| {summary['complete_world_rooted']} "
                         f"| {summary['incomplete_total']} "
                         f"| {summary['unresolved_total']} |")
    lines += [
        "",
        "## What each outcome means, agreed in advance",
        "",
        "As fixed in the plan before the run: a mostly unresolved result points to",
        "missing lineage in the recorded structures, and the next instrument would",
        "need a store-time record of the content's origin. A mostly vocabulary-overlap",
        "result says useful chains exist, which is consistent with world inheritance",
        "*and* with self-generated content that reuses world words, so it does not",
        "establish that the links track world evidence. Either way, the next",
        "confirmatory study needs its own preregistration and fresh seeds; the closed",
        "study's failure stays intact.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Provenance tracer (controls only).")
    ap.add_argument("--controls", action="store_true",
                    help="run the known-ancestry controls and exit non-zero on failure")
    ap.add_argument("--diagnostic", action="store_true",
                    help="trace the five calibration cells; descriptive only")
    ap.add_argument("--budget", type=float, default=210.0,
                    help="seconds of cells to compute before returning progress")
    ap.add_argument("--report", action="store_true",
                    help="regenerate the results document from the committed artifact")
    args = ap.parse_args(argv)
    if args.report:
        art = json.loads((ROOT / DIAGNOSTIC_OUT).read_text(encoding="utf-8"))
        (ROOT / DIAGNOSTIC_DOC).write_text(render_report(art), encoding="utf-8")
        print(json.dumps({"wrote": DIAGNOSTIC_DOC,
                          "claims": art["totals"]["formation"]["claims"]},
                         indent=1, sort_keys=True))
        return 0
    if args.diagnostic:
        art = run_diagnostic(budget_seconds=args.budget)
        if not art.get("artifact_written", True):
            print(json.dumps(art, indent=1, sort_keys=True))
            return 0
        print(json.dumps({"wrote": [DIAGNOSTIC_OUT, DIAGNOSTIC_DOC],
                          "totals": {limb: {k: art["totals"][limb][k] for k in
                                            ("claims", "complete_world_rooted",
                                             "incomplete_total", "unresolved_total")}
                                     for limb in ("formation", "revision")}},
                         indent=1, sort_keys=True))
        return 0
    if not args.controls:
        ap.print_help()
        return 2
    result = run_controls()
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
