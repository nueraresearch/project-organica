"""
benchmarks/lineage_audit.py
------------------------------------------------------------------
Law II says: "Every cognitive primitive must trace an unbroken, deterministic
DAG of parent_ids back to Generation 0 empirical events."

The project CLAIMS this holds (CHALLENGE.md, the papers, and
docs/validation_report.json's "lineage_integrity_pct: 100.0"). But nothing in
the code actually verifies it:

  * `SleepService.get_ancestry()` walks only `_load_prior_candidates()` --
    the most recent 4,000 sleep events -- and stops at max_depth 7.
  * `cross_domain_validation.py` checks that each `parent_id` is present
    among OTHER CANDIDATES in that same window. It never reaches a
    Generation 0 experience event, which is not a candidate at all.

This script measures what is actually true, against the live substrate, and
separates three different outcomes that the current check conflates:

  GROUNDED          a full parent chain resolves to a Layer 1 candidate
                    whose tags actually appear in a Generation 0 experience
                    event.
  UNVERIFIABLE      the chain is broken because an intermediate candidate
                    was EVICTED from the candidate store (bounded
                    retention), not because the lineage was ever bad.
  UNGROUNDED        the chain resolves, but the Layer 1 anchor's tags do
                    not appear in any experience event.

The second category is the interesting one: bounding the candidate store is
required for a 90-day run, and it is also what makes the published
"unbroken ancestry" claim unverifiable after a few hundred cycles.

Usage:
    python benchmarks/lineage_audit.py
    python benchmarks/lineage_audit.py --db memory.db --out docs/lineage_audit.json
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from organica.memory import _extract_tags  # noqa: E402

# Layer 1 candidates are grounded in raw experience through these fields.
GROUNDING_FIELDS = {
    "concept_candidate": ("members",),
    "phrase_candidate": ("members",),
    "loop_candidate": ("path",),
    "prediction_candidate": ("source", "target"),
    "anomaly": ("expected", "observed"),
}


def grounding_tags(candidate: dict) -> list[str]:
    """Return the raw-experience tags a Layer 1 candidate rests on."""
    fields = GROUNDING_FIELDS.get(candidate.get("type", ""))
    if not fields:
        return []
    tags: list[str] = []
    for field in fields:
        value = candidate.get(field)
        if isinstance(value, str):
            if value:
                tags.append(value)
        elif isinstance(value, list):
            tags.extend(str(v) for v in value if v)
    return tags


def audit(db_path: Path) -> dict:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)

    # ---- Generation 0: the empirical record -----------------------------
    g0_rows = conn.execute(
        "SELECT tags FROM events WHERE event_type != 'sleep'"
    ).fetchall()
    g0_tag_counts: dict[str, int] = defaultdict(int)
    for (tags_str,) in g0_rows:
        for tag in (tags_str or "").split(","):
            if tag:
                g0_tag_counts[tag] += 1
    g0_event_count = len(g0_rows)

    # ---- The candidate store --------------------------------------------
    cand_rows = conn.execute(
        "SELECT content FROM events WHERE event_type='sleep' AND source != 'sleep:meta'"
    ).fetchall()
    by_id: dict[str, dict] = {}
    for (content,) in cand_rows:
        try:
            obj = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(obj, dict) and "id" in obj:
            # Later rows win: a candidate is re-emitted each cycle, and the
            # most recent emission is the current one.
            by_id[obj["id"]] = obj

    # ---- Resolution ------------------------------------------------------
    stats = {
        "grounded": 0,
        "unverifiable_evicted": 0,
        "ungrounded_no_g0_tags": 0,
        "no_parents_at_all": 0,
    }
    failures: list[dict] = []

    def resolve(cid: str, seen: frozenset = frozenset()) -> str:
        """Return 'grounded' | 'unverifiable_evicted' | 'ungrounded_no_g0_tags'."""
        if cid in seen:
            return "cycle"
        candidate = by_id.get(cid)
        if candidate is None:
            return "unverifiable_evicted"

        ctype = candidate.get("type", "")
        if ctype in GROUNDING_FIELDS:
            tags = grounding_tags(candidate)
            if not tags:
                return "ungrounded_no_g0_tags"
            if any(tag in g0_tag_counts for tag in tags):
                return "grounded"
            return "ungrounded_no_g0_tags"

        parents = candidate.get("parent_ids") or []
        if not parents:
            # Not a Layer 1 anchor and no parents: nothing to verify.
            return "no_parents_at_all"

        seen = seen | {cid}
        for pid in parents:
            outcome = resolve(pid, seen)
            if outcome == "grounded":
                return "grounded"
            if outcome == "unverifiable_evicted":
                return "unverifiable_evicted"
        return "ungrounded_no_g0_tags"

    resolvable = 0
    for cid, candidate in by_id.items():
        if candidate.get("generation", 1) <= 1:
            continue
        resolvable += 1
        outcome = resolve(cid)
        stats[outcome] = stats.get(outcome, 0) + 1
        if outcome != "grounded" and len(failures) < 40:
            failures.append({
                "id": cid,
                "type": candidate.get("type"),
                "generation": candidate.get("generation"),
                "outcome": outcome,
                "parents": candidate.get("parent_ids", [])[:4],
            })

    conn.close()

    total = max(resolvable, 1)
    return {
        "db": str(db_path),
        "g0_experience_events": g0_event_count,
        "g0_distinct_tags": len(g0_tag_counts),
        "candidates_in_store": len(by_id),
        "candidates_requiring_lineage": resolvable,
        "grounded": stats["grounded"],
        "unverifiable_evicted": stats["unverifiable_evicted"],
        "ungrounded_no_g0_tags": stats["ungrounded_no_g0_tags"],
        "no_parents_at_all": stats["no_parents_at_all"],
        "grounded_pct": round(100 * stats["grounded"] / total, 2),
        "unverifiable_pct": round(100 * stats["unverifiable_evicted"] / total, 2),
        "ungrounded_pct": round(100 * stats["ungrounded_no_g0_tags"] / total, 2),
        "sample_failures": failures,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit Law II lineage to Generation 0.")
    ap.add_argument("--db", default="memory.db")
    ap.add_argument("--out", default="docs/lineage_audit.json")
    args = ap.parse_args()

    db_path = Path(__file__).parent.parent / args.db
    if not db_path.exists():
        print(f"ERROR: {db_path} not found")
        return 1

    result = audit(db_path)

    print("=" * 72)
    print("PROJECT ORGANICA -- LAW II LINEAGE AUDIT (to Generation 0)")
    print("=" * 72)
    print(f"  db                              : {result['db']}")
    print(f"  G0 experience events            : {result['g0_experience_events']}")
    print(f"  G0 distinct tags                : {result['g0_distinct_tags']}")
    print(f"  candidates in store             : {result['candidates_in_store']}")
    print(f"  candidates requiring lineage    : {result['candidates_requiring_lineage']}")
    print()
    print(f"  GROUNDED (chain reaches a G0 tag) : {result['grounded']:>7}  "
          f"({result['grounded_pct']}%)")
    print(f"  UNVERIFIABLE (parent evicted)     : {result['unverifiable_evicted']:>7}  "
          f"({result['unverifiable_pct']}%)")
    print(f"  UNGROUNDED (no G0 tag at root)    : {result['ungrounded_no_g0_tags']:>7}  "
          f"({result['ungrounded_pct']}%)")
    print(f"  no parents at all                 : {result['no_parents_at_all']:>7}")
    print()
    if result["unverifiable_pct"] > 0:
        print("  NOTE: 'unverifiable' means the chain is broken by bounded")
        print("  retention evicting an intermediate candidate -- not that the")
        print("  lineage was ever invalid. It is unverifiable, not broken.")
    if result["ungrounded_pct"] > 0:
        print("  NOTE: 'ungrounded' means the chain resolves but its Layer 1")
        print("  anchor does not appear in any Generation 0 experience event.")

    out = Path(__file__).parent.parent / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": "G",
        "title": "Law II Lineage Audit (resolution to Generation 0)",
        "method": "Walked every candidate's parent_ids to a Layer 1 anchor, then "
                  "checked that anchor's grounding tags appear in a Generation 0 "
                  "experience event. Unverifiable and ungrounded are reported "
                  "separately rather than conflated.",
        "result": result,
    }, indent=2))
    print(f"\n  Full report written to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
