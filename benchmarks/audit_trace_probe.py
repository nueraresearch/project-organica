"""Feasibility probe for the development audit trace (docs/AUDIT-TRACE-SPEC.md).

The specification claims that the **selection contest** — the candidates that
died, the candidates that lost, and the ones that survived — can be
reconstructed *from outside* the engine, using only what the engine already
reports and what the substrate already persists.  That claim is the load-bearing
one, and it was read out of the source.  This probe tests it.

It is an instrument probe, not an experiment about the organism: it produces no
claim about what Organica does, only about whether an outside auditor can
reproduce what the engine did.

Four checks:

  A1  evidence replay exactness   — for every reported belief, the auditor's
      recomputed support / contradiction / confidence equal the engine's.
      NOTE: this reconciles **aggregate** counts (the `precedes` table), not
      the individual observations behind them.
  A2  selection reconstruction    — the auditor's reconstructed retained set
      equals the engine's reported retained set, cycle by cycle.
  A7  event-level attribution     — every temporal edge resolves to the
      concrete events that produced it, the attributed total equals the
      aggregate count, and each belief's support resolves to event ids with a
      world/self split.  Requires a passive store-time observer.
  A4  behaviour invariance         — an observer that records the trace leaves
      the engine's outputs byte-identical.

The engine is not modified and is not instrumented.  The observer subclasses
MemoryService, calls the parent unchanged, and only *reads* the lookback
window the engine had just used.  Nothing in `organica/` is touched.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import math
import sys
import time
from dataclasses import asdict, fields
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.ground_truth_worlds import generate_cause_world  # noqa: E402
from organica.memory import MemoryService  # noqa: E402
from organica.paths import temp_db  # noqa: E402
from organica.sleep import SleepService, SleepReport, _make_id  # noqa: E402

CYCLES = 120
EVENTS_PER_CYCLE = 8
SEED = 20261025
INVARIANCE_CYCLES = 12
TIE_GROUP = 4


class _TieClock:
    """A clock that returns the same timestamp for every N calls.

    Used by the forced-tie arm: the engine's lookback query has no
    tie-breaker, so the forced-tie arm makes the window's contents genuinely
    ambiguous and checks that the observer still reproduces the engine's
    choice.
    """

    def __init__(self, group: int = TIE_GROUP, base: float = 1_700_000_000.0):
        self.group = group
        self.base = base
        self.calls = 0

    def time(self) -> float:
        value = self.base + (self.calls // self.group) * 0.0001
        self.calls += 1
        return value



# ------------------------------------------------------------------
# The passive observer.
# ------------------------------------------------------------------

class ObservingMemoryService(MemoryService):
    """Records the engine's lookback window at store time.  Read-only.

    The engine's `_record_temporal_edges` looks back at the three most recent
    rows by `ORDER BY time DESC LIMIT 3` — a window that **includes the event
    being stored**, because `store()` inserts the row before recording edges.
    Re-running the same query immediately afterwards observes exactly the
    window the engine used, without changing anything.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # edge (from_tag, to_tag) -> list of (prior_event_id, prior_event_type,
        #                                  to_event_id)
        self.attribution: dict[tuple[str, str], list[tuple[str, str, str]]] = {}
        # every DISTINCT transition, deduplicated by
        # (from_tag, to_tag, prior_event_id, to_event_id).  The attribution
        # lists above are cumulative: a transition stays in the engine's
        # support count for as long as the edge exists, so summing them per
        # belief per cycle counts the same transition many times over.
        self.unique_transitions: dict[tuple[str, str, str, str], str] = {}
        # how many stores saw a lookback window containing two rows with the
        # same timestamp (the engine's query has no tie-breaker)
        self.tied_windows = 0
        self.store_order: list[str] = []
        # how many `sleep` events the engine stores per cycle. The cognition
        # window is the most recent 4,000 sleep events, so this converts the
        # window into a span in CYCLES -- a measurement rather than an
        # estimate.
        self.sleep_events = 0
        # every candidate id the engine has ever stored in this run.  This is
        # what lets A3 tell "aged out of the cognition window" apart from
        # "no record was ever written" -- the difference between a persistence
        # limit and a data defect.
        self.candidate_ids: set[str] = set()
        # the cycle in which each candidate was last stored.  Candidates are
        # RE-STORED every cycle -- the natural-selection decay path writes a
        # decayed copy of every surviving prior candidate (sleep.py:1784-1800)
        # -- so the window's SPAN IN STORES is not the same as the AGE OF ITS
        # CONTENT.  This measures the second.
        self.current_cycle = -1
        self.last_store_cycle: dict[str, int] = {}

    def store(self, content: str, event_type: str = "observe", source: str = "env"):
        event = super().store(content, event_type=event_type, source=source)
        self.store_order.append(event.id)
        if event_type == "sleep":
            self.sleep_events += 1
            # Candidates are persisted one per sleep event, as JSON, with a
            # source of `sleep:<type>` (sleep.py:1916-1967).  The cycle marker
            # is exactly `sleep:meta` -- an EXACT match, because a candidate of
            # type `meta_concept` is stored with the source `sleep:meta_concept`,
            # which starts with the marker's prefix but is not the marker.
            # (The engine makes the same distinction: `source != "sleep:meta"`
            # at sleep.py:881 and memory.py:472.)
            if source != "sleep:meta":
                try:
                    payload = json.loads(content)
                except (json.JSONDecodeError, ValueError):
                    payload = None
                if isinstance(payload, dict) and payload.get("id"):
                    cid = payload["id"]
                    self.candidate_ids.add(cid)
                    self.last_store_cycle[cid] = self.current_cycle
        # The engine records graph edges only for world events: `store()`
        # guards the call with `if event_type != "sleep"`.  The observer must
        # mirror that guard exactly, or it attributes transitions the engine
        # never made.
        if event_type == "sleep":
            return event
        rows = self._conn.execute(
            "SELECT id, time, event_type, tags, rowid FROM events "
            "ORDER BY time DESC LIMIT 3"
        ).fetchall()
        times = [r[1] for r in rows]
        if len(times) != len(set(times)):
            self.tied_windows += 1
        for prior_id, _t, prior_type, prior_tags, _rowid in rows:
            for tag_from in (prior_tags or "").split(","):
                if not tag_from:
                    continue
                for tag_to in event.tags:
                    if tag_from == tag_to:
                        continue
                    self.attribution.setdefault((tag_from, tag_to), []).append(
                        (prior_id, prior_type, event.id)
                    )
                    self.unique_transitions[
                        (tag_from, tag_to, prior_id, event.id)
                    ] = prior_type
        return event


# ------------------------------------------------------------------
# A3 -- ancestry honesty and lineage completeness.
#
# The definition these implement is fixed in advance in
# docs/AUDIT-TRACE-SPEC.md section 12.  Two links, kept apart:
#
#   Level 1 -- developmental lineage: candidate -> candidate, via
#              `parent_ids`.  It terminates at Layer 1 (the tag-built
#              structures).  NO PARENT LINK POINTS AT AN EVENT.
#   Level 2 -- evidential linkage: claim -> transitions -> events.
#
# Success in one cannot stand in for success in the other.
# ------------------------------------------------------------------

# The engine's own Layer 1 -- the candidate lists the sleep report labels
# "# Layer 1" (sleep.py:270-275).  These are built from tags and carry no
# parent link, so a lineage terminates here.  `anomaly` is included because
# the engine's report groups it under Layer 1 and it is built from tags like
# the rest; the spec's list of four is refined by the engine's own layering.
LAYER1_TYPES = frozenset({
    "concept_candidate", "phrase_candidate", "loop_candidate",
    "prediction_candidate", "anomaly",
})

MAX_ANCESTRY_DEPTH = 7       # sleep.py:841 -- get_ancestry(max_depth=7)
WINDOW_SLEEP_EVENTS = 4000   # sleep.py:878 -- recent(n=4000, event_type="sleep")

# The report's fourteen candidate lists (sleep.py:266-291).
REPORT_LISTS = (
    "concepts", "phrases", "loops", "predictions", "anomalies",
    "meta_concepts", "processes", "workflow_concepts",
    "hypotheses", "theories", "questions", "dreams",
    "investigations", "experiments",
)

# Pre-committed precedence when a structure fails to resolve, and more than
# one branch carries a reason.  Ordered by how much each reason damages
# trust in the trace:
#   missing_record  a data defect -- a parent id with no record anywhere
#   aged_out        the record is gone from the window -- a persistence limit
#   depth_truncated the chain exists and the walk cut it -- a representation
#                   limit, and the most benign of the three
#   no_parent       the chain simply ended without reaching Layer 1
SPLIT_PRECEDENCE = ("missing_record", "aged_out", "depth_truncated", "no_parent")

# The window bound every unresolved node must carry.  Stated in the record
# itself, not in a footnote (spec section 3.2).
WINDOW_BOUND = (
    f"{WINDOW_SLEEP_EVENTS} sleep events (the most recent "
    f"{WINDOW_SLEEP_EVENTS} rows of `events` with event_type='sleep')"
)


def _ancestor_status(node_id: str, by_id: dict, ever_stored: set[str],
                     depth: int, max_depth: int) -> tuple[str, int]:
    """Follow one lineage branch to its end.

    Mirrors the engine's own `build_tree` (sleep.py:845-856): a node that is
    not in the window stops the walk, and so does a node at `max_depth`.

    Returns `(status, depth_reached)`.  `status` is one of:
      "layer1"          the branch reached a Layer-1 terminal -- resolved
      "aged_out"        the record exists but fell outside the window
      "missing_record"  no record was ever written under this id
      "depth_truncated" the depth limit cut a chain that was still going
      "no_parent"       the chain ended at a node that is not Layer 1
    """
    node = by_id.get(node_id)
    if node is None:
        # The id is referenced by a parent link but is not in the cognition
        # window.  It was either aged out -- the record exists elsewhere --
        # or the record was never written at all.  It is NOT "no parent":
        # the chain did not end, the record is simply out of reach.
        if node_id in ever_stored:
            return "aged_out", depth
        return "missing_record", depth

    parents = node.get("parent_ids") or []
    if depth >= max_depth:
        if parents:
            return "depth_truncated", depth
        return ("layer1" if node.get("type") in LAYER1_TYPES else "no_parent"), depth
    if not parents:
        return ("layer1" if node.get("type") in LAYER1_TYPES else "no_parent"), depth

    best = None
    for pid in parents:
        status, reached = _ancestor_status(pid, by_id, ever_stored, depth + 1, max_depth)
        if best is None:
            best = (status, reached)
        elif status == "layer1":
            # a resolved branch always wins
            best = (status, reached)
        elif best[0] == "layer1":
            pass
        elif reached > best[1]:
            best = (status, reached)
        elif reached == best[1] and SPLIT_PRECEDENCE.index(status) < SPLIT_PRECEDENCE.index(best[0]):
            best = (status, reached)
    return best


def trace_lineage(structure, by_id: dict, ever_stored: set[str],
                  max_depth: int = MAX_ANCESTRY_DEPTH) -> dict:
    """Trace one structure's lineage and classify the outcome.

    A structure *resolves* when at least one of its parent branches reaches
    a Layer-1 terminal within the depth limit.  When it does not resolve,
    the reason is taken from its failing branches by the pre-committed
    precedence.
    """
    parents = list(getattr(structure, "parent_ids", None) or [])
    branches = []
    for pid in parents:
        status, depth = _ancestor_status(pid, by_id, ever_stored, 1, max_depth)
        branches.append({
            "parent": pid,
            "status": status,
            "depth_reached": depth,
            # every unresolved node carries the window bound
            "window_bound": WINDOW_BOUND if status != "layer1" else None,
        })

    resolved = any(b["status"] == "layer1" for b in branches)
    reason = None
    if not resolved and branches:
        reason = min((b["status"] for b in branches),
                     key=lambda s: SPLIT_PRECEDENCE.index(s))
    elif not resolved:
        reason = "no_parent"

    return {
        "id": getattr(structure, "id", ""),
        "type": getattr(structure, "type", ""),
        "resolved": resolved,
        "reason": reason,
        "branches": branches,
    }


def audit_ancestry(report, window_candidates: list[dict], ever_stored: set[str],
                   max_depth: int = MAX_ANCESTRY_DEPTH) -> dict:
    """Measure lineage completeness for one cycle's structures.

    `window_candidates` must be the window the engine itself would read for
    these structures -- that is, the candidates persisted by the cycle that
    produced them.  Reading the window *before* the cycle would miss the
    structures' own parents, which are persisted at the end of the cycle.
    """
    by_id = {c["id"]: c for c in window_candidates if isinstance(c, dict) and c.get("id")}

    seen: set[str] = set()
    structures = []
    for name in REPORT_LISTS:
        for s in getattr(report, name, None) or []:
            sid = getattr(s, "id", "")
            if not sid or sid in seen:
                continue
            seen.add(sid)
            structures.append(s)

    # Layer-1 structures ARE terminals -- they have no lineage to resolve,
    # so counting them would inflate the rate with a trivial population.
    # They are reported separately, and the population is named.
    layer1 = [s for s in structures if getattr(s, "type", "") in LAYER1_TYPES]
    with_lineage = [s for s in structures if getattr(s, "type", "") not in LAYER1_TYPES]

    traces = [trace_lineage(s, by_id, ever_stored, max_depth) for s in with_lineage]
    resolved = [t for t in traces if t["resolved"]]
    split = {reason: 0 for reason in SPLIT_PRECEDENCE}
    for t in traces:
        if not t["resolved"] and t["reason"]:
            split[t["reason"]] += 1

    # Branch-level counts: the raw picture, so a reader is not forced to
    # rely on the precedence rule for the structure-level split.  "layer1"
    # counts branches that DID resolve.
    branch_counts = {reason: 0 for reason in SPLIT_PRECEDENCE}
    branch_counts["layer1"] = 0
    for t in traces:
        for b in t["branches"]:
            branch_counts[b["status"]] = branch_counts.get(b["status"], 0) + 1

    # --- the honesty check -------------------------------------------
    # A node that is not in the window must never be reported as "no
    # parent": the chain did not end, the record is out of reach.  And a
    # node that IS in the window must never be reported as absent.  Both
    # directions are checked against the data, not against the code path.
    honesty_errors = []
    for t in traces:
        for b in t["branches"]:
            in_window = b["parent"] in by_id
            if not in_window and b["status"] == "no_parent":
                honesty_errors.append({
                    "id": t["id"], "parent": b["parent"],
                    "error": "out-of-window parent reported as having no parent",
                })
            if in_window and b["status"] in ("aged_out", "missing_record"):
                honesty_errors.append({
                    "id": t["id"], "parent": b["parent"],
                    "error": "in-window parent reported as absent",
                })
            if b["status"] != "layer1" and not b.get("window_bound"):
                honesty_errors.append({
                    "id": t["id"], "parent": b["parent"],
                    "error": "unresolved node without a stated window bound",
                })

    return {
        "structures_reported": len(structures),
        "layer1_structures": len(layer1),
        "structures_with_lineage": len(with_lineage),
        "resolved": len(resolved),
        "lineage_reachability": (len(resolved) / len(with_lineage)) if with_lineage else None,
        "truncation_split": split,
        "branch_level_counts": branch_counts,
        "honesty_errors": honesty_errors,
        "honest": not honesty_errors,
        "traces": traces,
    }


def _accumulate_a3(acc: dict, result: dict) -> None:
    """Fold one cycle's A3 result into the run-wide accumulator."""
    acc["cycles"].append(result)
    acc["structures"] += result["structures_with_lineage"]
    acc["resolved"] += result["resolved"]
    for reason, n in result["truncation_split"].items():
        acc["split"][reason] += n
    for reason, n in result["branch_level_counts"].items():
        acc["branch_counts"][reason] += n
    acc["honesty_errors"].extend(result["honesty_errors"])


def depth_sweep(report, window_candidates: list[dict], ever_stored: set[str],
                depths=(1, 2, 3, 5, 7)) -> list[dict]:
    """A DIAGNOSTIC, not a criterion: reachability as a function of depth limit.

    The engine's limit is depth 7.  This sweep asks what the reachability
    would have been at smaller limits, which is how the "depth-truncated"
    branch is shown to be reachable -- a category that never fires is a
    category that has not been tested.
    """
    out = []
    for depth in depths:
        result = audit_ancestry(report, window_candidates, ever_stored, max_depth=depth)
        out.append({
            "max_depth": depth,
            "lineage_reachability": result["lineage_reachability"],
            "truncation_split": result["truncation_split"],
        })
    return out


def window_content_age(window_candidates: list[dict], last_store_cycle: dict[str, int],
                       final_cycle: int) -> dict:
    """How far back, in CYCLES, the window's candidate content actually reaches.

    The window is the most recent 4,000 SLEEP EVENTS.  Its span in stores is
    therefore small -- but candidates are re-stored every cycle, so the
    window's *content* can be much older than its span in stores.  This
    measures the second, which is the one that bounds how much developmental
    history is recoverable.
    """
    ages = []
    for c in window_candidates:
        cid = c.get("id") if isinstance(c, dict) else None
        if cid is None:
            continue
        last = last_store_cycle.get(cid)
        if last is None:
            continue
        ages.append(final_cycle - last)
    if not ages:
        return {"candidates": 0}
    ages.sort()
    return {
        "candidates": len(ages),
        "oldest_age_cycles": ages[-1],
        "median_age_cycles": ages[len(ages) // 2],
        "youngest_age_cycles": ages[0],
        "distinct_cycles_spanned": len(set(ages)),
        "note": "Age in cycles of each candidate still held by the window, "
                "measured from the cycle it was last stored in. This is the "
                "window's CONTENT age, which is not the same as its span in "
                "stores: candidates are re-stored every cycle by the decay "
                "path, so a window of 4,000 sleep events can still hold "
                "structures that were first formed many cycles earlier.",
    }


def window_sweep(report, window_candidates: list[dict], ever_stored: set[str],
                 sizes=(25, 50, 100, 200, 500, 1000, 2000, 4000),
                 max_depth: int = MAX_ANCESTRY_DEPTH) -> list[dict]:
    """A DIAGNOSTIC, not a criterion: reachability as a function of window size.

    The engine's window is fixed at 4,000 sleep events.  This sweep asks what
    the reachability would have been at smaller windows, which is how the
    "aged out" branch is shown to be reachable and how much of the
    incompleteness is the window rather than the architecture.

    It reads the same candidate list the engine holds and slices it; it does
    not touch the engine, and it is reported separately from the criteria.
    """
    out = []
    for size in sizes:
        # `_load_prior_candidates` reads `recent(n=4000, event_type="sleep")`,
        # which is ordered NEWEST FIRST.  The newest `size` candidates are
        # therefore the FRONT of the list, not the back.
        subset = window_candidates[:size] if size < len(window_candidates) else window_candidates
        result = audit_ancestry(report, subset, ever_stored, max_depth)
        out.append({
            "window_candidates": len(subset),
            "lineage_reachability": result["lineage_reachability"],
            "truncation_split": result["truncation_split"],
            "branch_level_counts": result["branch_level_counts"],
        })
    return out


# ------------------------------------------------------------------
# The auditor.  Every rule below mirrors a line in organica/sleep.py.
# ------------------------------------------------------------------

def _temporal_graph(mem: MemoryService) -> dict[str, dict[str, int]]:
    """Mirror of SleepService._load_temporal (sleep.py:871-874)."""
    graph: dict[str, dict[str, int]] = {}
    for tag_from, tag_to, count in mem.temporal_edges(min_count=1):
        graph.setdefault(tag_from, {})[tag_to] = count
    return graph


def _stable_prior(prior: list[dict], stable_threshold: float) -> list[dict]:
    """Mirror of the stable_prior filter in SleepService.run (sleep.py:463-465)."""
    return [
        c for c in prior
        if c.get("type") not in ("_sleep_meta", "anomaly")
        and (c.get("confidence") or c.get("strength") or 0) >= stable_threshold
    ]


def _subject_entropy(subject: str, temporal: dict[str, dict[str, int]]) -> float:
    """Mirror of SleepService._subject_entropy (sleep.py:1559-1576)."""
    counts = [c for c in temporal.get(subject, {}).values() if c > 0]
    if len(counts) < 2:
        return 0.0
    total = sum(counts)
    h = 0.0
    for c in counts:
        q = c / total
        h -= q * math.log2(q)
    return h / math.log2(len(counts))


def reconstruct(report, prior: list[dict], temporal: dict[str, dict[str, int]],
                svc: SleepService) -> dict:
    """Rebuild the belief contest from the report and the substrate.

    Mirrors SleepService._form_and_test_hypotheses (sleep.py:1406-1528),
    _belief_info (1534-1557), _salience (1578-1602) and _retain_hypotheses
    (1614-1647) under the default "salience" policy.
    """
    stable = _stable_prior(prior, svc.STABLE_THRESHOLD)

    cur_workflows = [asdict(w) for w in report.workflow_concepts]
    cur_processes = [asdict(p) for p in report.processes]
    cur_metas = [asdict(m) for m in report.meta_concepts]

    # --- all_workflows / all_processes / all_metas (sleep.py:473-509) --------
    all_workflows = list(cur_workflows)
    have = {w["id"] for w in all_workflows}
    for c in stable:
        if c.get("type") == "workflow_concept" and c.get("id") not in have:
            all_workflows.append({
                "id": c.get("id"), "components": c.get("components", []),
                "confidence": c.get("confidence", 1.0),
            })
    all_processes = list(cur_processes)
    have = {p["id"] for p in all_processes}
    for c in stable:
        if c.get("type") == "process_candidate" and c.get("id") not in have:
            all_processes.append({
                "id": c.get("id"), "cycle": c.get("cycle", []),
                "strength": c.get("strength", 1.0),
            })
    all_metas = list(cur_metas)
    have = {m["id"] for m in all_metas}
    for c in stable:
        if c.get("type") == "meta_concept" and c.get("id") not in have:
            all_metas.append({
                "id": c.get("id"), "anchor_tag": c.get("anchor_tag", ""),
                "related_candidates": c.get("related_candidates", 0),
                "confidence": c.get("confidence", 0.0),
            })

    # --- the candidate pool (sleep.py:1418-1469) ---------------------------
    pool: dict[str, dict] = {}
    for w in all_workflows:
        comps = list(w["components"])
        for i in range(len(comps)):
            for j in range(len(comps)):
                if i != j:
                    hid = _make_id("hyp", comps[i], comps[j])
                    pool.setdefault(hid, {"id": hid, "subject": comps[i], "expectation": comps[j]})
    for p in all_processes:
        cyc = list(p["cycle"])
        for i in range(len(cyc)):
            sub, exp = cyc[i], cyc[(i + 1) % len(cyc)]
            hid = _make_id("hyp", sub, exp)
            pool.setdefault(hid, {"id": hid, "subject": sub, "expectation": exp})
    markers = []
    for m in all_metas:
        if m["related_candidates"] >= 5:
            hid = _make_id("hyp", m["anchor_tag"], "high_structural_significance")
            markers.append({
                "id": hid, "subject": m["anchor_tag"],
                "expectation": "high_structural_significance",
                "confidence": m["confidence"], "support_count": m["related_candidates"],
                "contradiction_count": 0,
            })

    # --- counts, confidence, death rule (sleep.py:1480-1500) ---------------
    prior_hyps = {h.get("id"): h for h in prior if h.get("type") == "hypothesis"}
    beliefs: dict[str, dict] = {}
    died: list[str] = []
    for hid, cand in pool.items():
        sub, exp = cand["subject"], cand["expectation"]
        targets = temporal.get(sub, {})
        support = targets.get(exp, 0)
        total_flow = sum(targets.values())
        raw_contradiction = max(0, total_flow - support)
        contradiction = raw_contradiction * svc.CONTRADICTION_SCALE
        conf = round(support / (support + contradiction), 4) if (support + contradiction) > 0 else 0.0
        if conf < svc.DEATH_THRESHOLD and (support + contradiction) >= 3:
            died.append(hid)
            continue
        prior_h = prior_hyps.get(hid)
        prior_conf = prior_h.get("confidence") if prior_h else None
        cand.update({
            "support_count": support, "contradiction_count": contradiction,
            "raw_contradiction_count": raw_contradiction,
            "total_flow": total_flow, "confidence": conf,
            "prior_confidence": prior_conf,
            "revision_delta": round(conf - prior_conf, 4) if prior_conf is not None else 0.0,
        })
        beliefs[hid] = cand

    # --- salience (sleep.py:1534-1602) -------------------------------------
    info = {}
    for hid, c in beliefs.items():
        raw = c["raw_contradiction_count"]
        total = c["support_count"] + raw
        prior_h = prior_hyps.get(hid)
        prior_conf = prior_h.get("confidence") if prior_h else None
        info[hid] = {
            "tension": (raw / total) if total > 0 else 0.0,
            "curiosity": _subject_entropy(c["subject"], temporal),
            "novelty": 0.0 if prior_h else 1.0,
            "revision": abs(c["confidence"] - prior_conf) if prior_conf is not None else 0.0,
        }
    w_t, w_c, w_n, w_r = svc.SALIENCE_WEIGHTS
    for hid, c in beliefs.items():
        i = info[hid]
        c["salience"] = (w_t * i["tension"] + w_c * i["curiosity"]
                         + w_n * i["novelty"] + w_r * i["revision"])
        c["components"] = i

    # --- retention (sleep.py:1641-1643) ------------------------------------
    ranked = sorted(beliefs.values(), key=lambda h: (-h["salience"], h["subject"]))
    kept = ranked[:svc.MAX_HYPOTHESES]
    kept_ids = {h["id"] for h in kept}
    lost = [h for h in ranked[svc.MAX_HYPOTHESES:]]

    kept_markers = sorted(markers, key=lambda h: (-h["confidence"], h["subject"]))[:svc.MAX_STRUCTURAL_MARKERS]
    kept_marker_ids = {m["id"] for m in kept_markers}

    return {
        "kept_ids": kept_ids,
        "kept_marker_ids": kept_marker_ids,
        "beliefs": beliefs,
        "died_ids": set(died),
        "lost": [{"id": h["id"], "subject": h["subject"], "expectation": h["expectation"],
                   "salience": round(h["salience"], 6),
                   "components": {k: round(v, 6) for k, v in h["components"].items()}}
                  for h in lost],
        "kept_detail": [{"id": h["id"], "subject": h["subject"], "expectation": h["expectation"],
                         "salience": round(h["salience"], 6),
                         "support_count": h["support_count"],
                         "contradiction_count": h["contradiction_count"],
                         "confidence": h["confidence"],
                         "components": {k: round(v, 6) for k, v in h["components"].items()}}
                        for h in kept],
    }


def _attribution_for(observer: ObservingMemoryService, subject: str,
                      expectation: str) -> list[dict]:
    """The concrete transitions behind one belief's support."""
    out = []
    for prior_id, prior_type, to_id in observer.attribution.get((subject, expectation), []):
        out.append({
            "from_event": prior_id,
            "from_event_type": prior_type,
            "to_event": to_id,
            "source": "self" if prior_type == "sleep" else "world",
        })
    return out


def run(cycles: int = CYCLES, seed: int = SEED, max_hypotheses: int | None = None,
        force_tie: bool = False) -> dict:
    world = generate_cause_world(cycles=cycles, events_per_cycle=EVENTS_PER_CYCLE, seed=seed)
    events = world["events"]

    db = temp_db("audit_trace_probe.db")
    db.unlink(missing_ok=True)
    mem = ObservingMemoryService(db_path=str(db))
    svc = SleepService(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)
    if max_hypotheses is not None:
        # STRESS ARM ONLY.  The belief budget is tightened so that the pool
        # exceeds the cap and the "lost on rank" branch is exercised.  This is
        # a stress test of the *auditor*, not a claim about the organism: the
        # auditor reads the same budget, and the engine's files are untouched.
        svc.MAX_HYPOTHESES = max_hypotheses

    # Forced-tie arm: the engine's lookback query is `ORDER BY time DESC
    # LIMIT 3` with no tie-breaker, so under equal timestamps the window is
    # not determined by the schema.  This arm makes ties happen on purpose
    # and requires the observer to reproduce the engine's choice anyway.
    clock_patch = _TieClock() if force_tie else None
    stack = contextlib.ExitStack()
    if clock_patch is not None:
        stack.enter_context(mock.patch.object(time, "time", clock_patch.time))

    cycle_reports = []
    a1_fail = a2_fail = a7_fail = 0
    a1_checked = a2_checked = a7_checked = 0
    self_sourced_total = world_sourced_total = 0
    belief_edges: set[tuple[str, str]] = set()
    # --- A3 accumulators -------------------------------------------------
    prev_report = None
    a3: dict = {
        "cycles": [],
        "structures": 0,
        "resolved": 0,
        "split": {reason: 0 for reason in SPLIT_PRECEDENCE},
        "branch_counts": {reason: 0 for reason in SPLIT_PRECEDENCE},
        "honesty_errors": [],
    }
    a3["branch_counts"]["layer1"] = 0
    a3_claims = a3_claims_linked = 0
    a3_final = None
    a3_window_sweep: list[dict] = []
    a3_depth_sweep: list[dict] = []
    a3_window_age: dict = {}
    try:
        for cycle in range(cycles):
            chunk = events[cycle * EVENTS_PER_CYCLE:(cycle + 1) * EVENTS_PER_CYCLE]
            for event in chunk:
                mem.store(event, event_type="event", source=f"cycle:{cycle}")

            # Snapshots taken at exactly the moment the engine reads them.
            temporal = _temporal_graph(mem)
            prior = svc._load_prior_candidates()
            mem.current_cycle = cycle

            report = svc.run_sleep_cycle()

            rec = reconstruct(report, prior, temporal, svc)

            reported = {h.id: h for h in report.hypotheses}
            reported_beliefs = {i: h for i, h in reported.items()
                                if h.expectation != "high_structural_significance"}
            reported_markers = {i: h for i, h in reported.items()
                                if h.expectation == "high_structural_significance"}

            # --- A1: evidence replay exactness (aggregate counts) ----------
            a1_errors = []
            for hid, h in reported_beliefs.items():
                mine = rec["beliefs"].get(hid)
                if mine is None:
                    a1_errors.append({"id": hid, "error": "not in reconstructed pool"})
                    continue
                for field in ("support_count", "contradiction_count", "confidence"):
                    if abs(float(getattr(h, field)) - float(mine[field])) > 1e-9:
                        a1_errors.append({"id": hid, "field": field,
                                          "engine": getattr(h, field), "auditor": mine[field]})
                a1_checked += 1
            if a1_errors:
                a1_fail += 1

            # --- A2: selection reconstruction ------------------------------
            a2_ok = (set(reported_beliefs) == rec["kept_ids"]
                     and set(reported_markers) == rec["kept_marker_ids"])
            a2_checked += 1
            if not a2_ok:
                a2_fail += 1

            # --- A7: event-level attribution -------------------------------
            a7_errors = []
            for hid, h in reported_beliefs.items():
                transitions = _attribution_for(mem, h.subject, h.expectation)
                belief_edges.add((h.subject, h.expectation))
                if len(transitions) != h.support_count:
                    a7_errors.append({"id": hid, "error": "attribution count mismatch",
                                       "attributed": len(transitions),
                                       "support_count": h.support_count})
                    continue
                world_n = sum(1 for t in transitions if t["source"] == "world")
                self_n = len(transitions) - world_n
                world_sourced_total += world_n
                self_sourced_total += self_n
                a7_checked += 1
            if a7_errors:
                a7_fail += 1

            # --- A3: ancestry honesty + lineage completeness ---------------
            # The structures reported THIS cycle are traced against the
            # window the engine would read for them -- which is the window
            # as it stands AFTER this cycle's candidates are persisted.  That
            # window is the one loaded at the start of the NEXT cycle, so
            # the previous cycle's report is traced here, not this cycle's.
            if prev_report is not None:
                a3_result = audit_ancestry(prev_report, prior, mem.candidate_ids)
                _accumulate_a3(a3, a3_result)

            # Evidence linkage (Level 2) is measured at the report's OWN
            # cycle: a belief's support count is cumulative, so it has to be
            # compared against the attribution as it stood when the report
            # was produced.
            for hid, h in reported_beliefs.items():
                transitions = _attribution_for(mem, h.subject, h.expectation)
                a3_claims += 1
                if len(transitions) == h.support_count and all(
                    t["source"] in ("world", "self") for t in transitions
                ):
                    a3_claims_linked += 1

            prev_report = report

            cycle_reports.append({
                "cycle": cycle + 1,
                "reported_beliefs": len(reported_beliefs),
                "reported_markers": len(reported_markers),
                "pool": len(rec["beliefs"]) + len(rec["died_ids"]),
                "died": len(rec["died_ids"]),
                "lost": len(rec["lost"]),
                "a1_errors": a1_errors,
                "a2_match": a2_ok,
                "a7_errors": a7_errors,
                "kept_detail": rec["kept_detail"],
                "lost_detail": rec["lost"][:5],
            })

        # --- A7 aggregate: every edge's attributed total == its count -----
        # The cross-check between two independent paths: the per-event
        # attribution, and the `precedes` aggregate table the engine builds.
        edge_mismatches = []
        edges_checked = 0
        aggregate_edges = set()
        for tag_from, tag_to, count in mem.temporal_edges(min_count=1):
            edges_checked += 1
            aggregate_edges.add((tag_from, tag_to))
            attributed = len(mem.attribution.get((tag_from, tag_to), []))
            if attributed != count:
                edge_mismatches.append({
                    "from": tag_from, "to": tag_to,
                    "aggregate_count": count, "attributed": attributed,
                })
        attributed_only = [f"{f}->{t}" for (f, t) in mem.attribution
                           if (f, t) not in aggregate_edges]

        # --- A3: the final cycle's structures, traced against the final window
        # The loop above traces each cycle's report at the start of the next
        # cycle.  The last cycle's report has no next cycle, so it is traced
        # here against the window as it stands after the run.
        if prev_report is not None:
            final_window = svc._load_prior_candidates()
            a3_final = audit_ancestry(prev_report, final_window, mem.candidate_ids)
            _accumulate_a3(a3, a3_final)
            a3_window_sweep = window_sweep(prev_report, final_window, mem.candidate_ids)
            a3_depth_sweep = depth_sweep(prev_report, final_window, mem.candidate_ids)
            a3_window_age = window_content_age(final_window, mem.last_store_cycle, cycles - 1)
    finally:
        mem.close()
        db.unlink(missing_ok=True)
        stack.close()

    cycles_with_beliefs = [c for c in cycle_reports if c["reported_beliefs"]]
    total_attributed = world_sourced_total + self_sourced_total

    # --- the distinct-evidence view --------------------------------------
    # The attribution lists are cumulative, and the run above re-counts a
    # belief's whole support in every cycle in which that belief is reported.
    # So the pooled number above is a count of SUPPORT REFERENCES, not of
    # distinct transitions.  The distinct view is what the disqualifier in
    # the spec needs: "is the evidence behind this claim the organism's own
    # output?"  It is restricted to the edges that actually back a reported
    # belief -- counting every transition in the run would mix in edges no
    # reported belief ever rested on.
    distinct_belief = set()
    for edge in belief_edges:
        for prior_id, prior_type, to_id in mem.attribution.get(edge, []):
            distinct_belief.add((edge[0], edge[1], prior_id, to_id, prior_type))
    unique_self = sum(1 for t in distinct_belief if t[4] == "sleep")
    unique_total = len(distinct_belief)
    unique_world = unique_total - unique_self
    unique_share = (unique_self / unique_total) if unique_total else 0.0
    reference_share = (self_sourced_total / total_attributed) if total_attributed else 0.0
    all_self = sum(1 for t in mem.unique_transitions.values() if t == "sleep")
    all_total = len(mem.unique_transitions)
    return {
        "purpose": "Feasibility probe for docs/AUDIT-TRACE-SPEC.md — can the "
                   "selection contest be reconstructed from outside the engine, "
                   "and can evidence be resolved to event ids?",
        "instrument_note": "Instrument probe, not an experiment about the organism. "
                           "It makes no claim about what Organica does; it checks "
                           "whether an outside auditor can reproduce what the engine did. "
                           "No engine file was modified or instrumented. The observer "
                           "subclasses MemoryService, calls the parent unchanged, and "
                           "only reads the lookback window the engine had just used.",
        "protocol": {
            "world": "organica/ground_truth_worlds.generate_cause_world",
            "cycles": cycles, "events_per_cycle": EVENTS_PER_CYCLE, "seed": seed,
            "retention_policy": SleepService.HYPOTHESIS_RETENTION,
            "max_hypotheses": svc.MAX_HYPOTHESES,
            "default_max_hypotheses": SleepService.MAX_HYPOTHESES,
            "stress_arm": max_hypotheses is not None,
            "salience_weights": list(SleepService.SALIENCE_WEIGHTS),
            "death_threshold": SleepService.DEATH_THRESHOLD,
            "contradiction_scale": SleepService.CONTRADICTION_SCALE,
            "report_candidate_lists": len([f.name for f in fields(SleepReport)
                                           if f.name not in ("cycle", "ran_at",
                                                             "prior_candidates_loaded",
                                                             "candidates_strengthened",
                                                             "candidates_decayed",
                                                             "candidates_pruned",
                                                             "composites_created")]),
        },
        "A1_evidence_replay_aggregate": {
            "beliefs_checked": a1_checked, "cycles_failing": a1_fail,
            "pass": a1_fail == 0,
            "scope": "aggregate counts only — the `precedes` table, not the "
                     "individual observations behind them",
        },
        "A2_selection_reconstruction": {
            "cycles_checked": a2_checked, "cycles_failing": a2_fail,
            "pass": a2_fail == 0,
        },
        "A7_event_level_attribution": {
            "beliefs_checked": a7_checked, "cycles_failing": a7_fail,
            "pass": a7_fail == 0 and not edge_mismatches and not attributed_only,
            "aggregate_edges_checked": edges_checked,
            "edge_mismatches": edge_mismatches[:10],
            "attributed_but_absent_from_aggregate": attributed_only[:10],
            "distinct_evidence": {
                "total_transitions": unique_total,
                "self_sourced": unique_self,
                "world_sourced": unique_world,
                "self_sourced_share": round(unique_share, 6),
                "belief_edges": len(belief_edges),
                "note": "each DISTINCT supporting transition counted once, "
                        "deduplicated by (from_tag, to_tag, prior_event_id, "
                        "to_event_id), and restricted to the edges that "
                        "actually back a reported belief. This is the share of "
                        "unique evidence behind the reported support, and it "
                        "is the figure the pre-committed disqualifier is read "
                        "against.",
            },
            "all_transitions_recorded": {
                "total_transitions": all_total,
                "self_sourced": all_self,
                "self_sourced_share": (round(all_self / all_total, 6)
                                        if all_total else 0.0),
                "note": "every distinct transition the observer recorded, "
                        "including edges that no reported belief ever rested "
                        "on. Context, not the disqualifier's figure.",
            },
            "support_references": {
                "total": total_attributed,
                "self_sourced": self_sourced_total,
                "world_sourced": world_sourced_total,
                "self_sourced_share": round(reference_share, 6),
                "note": "the SAME support counted once per belief per cycle in "
                        "which that belief is reported. This is a weighted view "
                        "of reported support, NOT a share of unique transitions: "
                        "a transition that occurred early is counted again in "
                        "every later cycle where the belief is still reported.",
            },
            "timestamp_ties": {
                "stores_with_tied_window": mem.tied_windows,
                "forced": bool(force_tie),
                "note": "The engine's lookback query is `ORDER BY time DESC "
                        "LIMIT 3` with no tie-breaker, so under equal "
                        "timestamps the window is not determined by the schema. "
                        "The forced-tie arm makes ties happen on purpose and "
                        "requires the observer to reproduce the engine's choice "
                        "anyway.",
            },
            "cognition_window": {
                "sleep_events_total": mem.sleep_events,
                "sleep_events_per_cycle": round(mem.sleep_events / cycles, 2) if cycles else 0.0,
                "window_sleep_events": 4000,
                "window_span_cycles": (round(4000 / (mem.sleep_events / cycles), 1)
                                       if cycles and mem.sleep_events else None),
                "note": "The cognition window is the most recent 4,000 sleep "
                        "events (sleep.py:876-886). The span in CYCLES depends "
                        "on how many sleep events the engine stores per cycle, "
                        "so it is measured here rather than estimated. A "
                        "structure that keeps being produced stays inside the "
                        "window because candidates are re-stored every cycle; "
                        "one that stops being produced ages out after roughly "
                        "this many cycles.",
            },
            "note": "Every temporal edge must resolve to the concrete events "
                    "that produced it, and the attributed total must equal the "
                    "aggregate count. The world/self split is the D2 quantity: "
                    "a supporting transition whose prior event is the "
                    "organism's own sleep payload is self-sourced.",
        },
        "A3_ancestry_honesty": {
            "pass": not a3["honesty_errors"],
            "criterion": "Every ancestry node is either resolved within the "
                         "window, or explicitly marked absent WITH the window "
                         "bound stated. A record that reports a parent as "
                         "having no parent when it was merely out of window "
                         "fails the build.",
            "window_bound": WINDOW_BOUND,
            "max_depth": MAX_ANCESTRY_DEPTH,
            "structures_checked": a3["structures"],
            "structures_resolved": a3["resolved"],
            "lineage_reachability": (round(a3["resolved"] / a3["structures"], 6)
                                     if a3["structures"] else None),
            "truncation_split": a3["split"],
            "branch_level_counts": a3["branch_counts"],
            "honesty_errors": a3["honesty_errors"][:10],
            "honesty_error_count": len(a3["honesty_errors"]),
            "evidence_linkage": {
                "claims_checked": a3_claims,
                "claims_linked": a3_claims_linked,
                "share": (round(a3_claims_linked / a3_claims, 6) if a3_claims else None),
                "note": "Level 2, measured at each claim's own cycle: the share "
                        "of reported beliefs whose support resolves to event ids "
                        "with a world/self split that fully accounts for the "
                        "reported support count. Evidence linkage and lineage "
                        "reachability are DIFFERENT populations and neither "
                        "stands in for the other.",
            },
            "populations": {
                "lineage": "reported structures whose type is NOT a Layer-1 type. "
                           "Layer-1 structures ARE terminals -- they have no "
                           "parent link -- so counting them would inflate the "
                           "rate with a trivial population.",
                "claims": "reported hypotheses with a real expectation (the same "
                          "population A7 checks).",
            },
            "note": "Structures reported in cycle N are traced against the "
                    "window the engine would read for them -- the window as it "
                    "stands AFTER cycle N's candidates are persisted, which is "
                    "the window loaded at the start of cycle N+1. Tracing a "
                    "cycle's report against the window read BEFORE that cycle "
                    "would miss the structures' own parents, which do not exist "
                    "in the substrate yet.",
            "diagnostics": {
                "window_sweep": a3_window_sweep,
                "window_sweep_note": "DIAGNOSTIC, not a criterion: reachability "
                                     "as a function of window size, computed by "
                                     "slicing the candidate list the engine "
                                     "holds. It shows how much of the "
                                     "incompleteness is the window rather than "
                                     "the architecture. The engine's own window "
                                     "is fixed at 4,000 sleep events.",
                "depth_sweep": a3_depth_sweep,
                "depth_sweep_note": "DIAGNOSTIC, not a criterion: reachability "
                                    "as a function of the depth limit. It is "
                                    "how the 'depth-truncated' branch is shown "
                                    "to be reachable -- a category that never "
                                    "fires is a category that has not been "
                                    "tested. The engine's own limit is 7.",
                "window_content_age": a3_window_age,
            },
        },
        "summary": {
            "cycles_run": len(cycle_reports),
            "cycles_with_beliefs": len(cycles_with_beliefs),
            "max_pool": max((c["pool"] for c in cycle_reports), default=0),
            "max_died": max((c["died"] for c in cycle_reports), default=0),
            "max_lost": max((c["lost"] for c in cycle_reports), default=0),
            "total_died": sum(c["died"] for c in cycle_reports),
            "total_lost": sum(c["lost"] for c in cycle_reports),
        },
        "cycles": cycle_reports,
    }


def _reports_signature(reports: list[dict]) -> str:
    """A stable signature of the engine's outputs.

    `ran_at` is a wall-clock timestamp and differs between any two runs; it
    is not part of the engine's behavioural output, so it is excluded.  Every
    other field — every candidate, every counter — must match exactly.
    """
    stripped = []
    for r in reports:
        r = dict(r)
        r.pop("ran_at", None)
        stripped.append(r)
    return json.dumps(stripped, sort_keys=True)


def run_invariance(cycles: int = INVARIANCE_CYCLES, seed: int = SEED) -> dict:
    """A4 — does the observer change the engine's outputs?  It must not."""
    def once(observing: bool) -> list[dict]:
        world = generate_cause_world(cycles=cycles, events_per_cycle=EVENTS_PER_CYCLE, seed=seed)
        db = temp_db(f"audit_trace_invariance_{'obs' if observing else 'plain'}.db")
        db.unlink(missing_ok=True)
        mem = (ObservingMemoryService if observing else MemoryService)(db_path=str(db))
        svc = SleepService(mem)
        if hasattr(svc, "_rng"):
            svc._rng.seed(seed)
        out = []
        try:
            for cycle in range(cycles):
                for event in world["events"][cycle * EVENTS_PER_CYCLE:(cycle + 1) * EVENTS_PER_CYCLE]:
                    mem.store(event, event_type="event", source=f"cycle:{cycle}")
                report = svc.run_sleep_cycle()
                out.append(asdict(report))
        finally:
            mem.close()
            db.unlink(missing_ok=True)
        return out

    plain = _reports_signature(once(False))
    observed = _reports_signature(once(True))
    return {
        "A4_behaviour_invariance": {
            "cycles": cycles, "seed": seed,
            "observer_on_equals_observer_off": plain == observed,
            "pass": plain == observed,
            "note": "The observer subclasses MemoryService, calls the parent "
                    "unchanged, and only reads. It must not change a single "
                    "reported field.",
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=CYCLES)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--max-hypotheses", type=int, default=None,
                        help="stress arm: tighten the belief budget so the "
                             "'lost on rank' branch is exercised")
    parser.add_argument("--force-tie", action="store_true",
                        help="forced-tie arm: make timestamps collide so the "
                             "engine's untie-broken lookback window is "
                             "genuinely ambiguous")
    parser.add_argument("--out", default=str(REPO / "docs" / "audit_trace_probe.json"))
    args = parser.parse_args()
    result = run(args.cycles, args.seed, args.max_hypotheses, args.force_tie)
    result.update(run_invariance())
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "cycles"}, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
