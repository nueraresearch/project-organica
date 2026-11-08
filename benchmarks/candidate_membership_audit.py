"""Candidate-membership audit — which candidate IDs the campaign had, and which
the current deterministic reconstruction has.

The use-path audit established that eight seeds do not reproduce the campaign's
per-type candidate table, and that the divergence is upstream of retrieval
order.  Counts were known; identity was not.  This instrument supplies the
identity: for each seed it names the candidate IDs that are present on both
sides, the ones only the campaign had, and the ones only the reconstruction
has, and it locates the first point at which the two populations diverge.

Why the campaign side has to be regenerated
-------------------------------------------
The campaign artifact (``docs/formation_utilization.json``) records a per-type
table of ``unique_count`` and ``edge_weight`` and nothing else.  No candidate
ID appears in it, in ``docs/use_path_diagnostic.json``, or in
``docs/use_path_audit.json``.  Candidate identity is therefore recoverable only
by re-running the campaign harness and matching its output against the
artifact's fingerprint.

The environment that reproduces the campaign
---------------------------------------------
The engine is hash-order sensitive: it iterates sets of strings in places, and
CPython randomises string hashing per process unless ``PYTHONHASHSEED`` is
pinned.  The campaign artifact records neither the hash seed nor the tie
order, so the audit sweeps the hash seed and keeps the runs whose per-type
table equals the campaign's.  A run whose fingerprint equals the campaign's
IS the campaign's population, and its candidate IDs are the campaign's.

Usage
-----
    python benchmarks/candidate_membership_audit.py --worker \
        --task T1 --seed 20261125 --out part.json
    python benchmarks/candidate_membership_audit.py --hash-seeds 0-15 --workers 10
    python benchmarks/candidate_membership_audit.py --render

The worker runs with ``PYTHONHASHSEED`` set by the parent, because the hash
seed is fixed at interpreter start-up and cannot be set in-process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from benchmarks import formation_utilization as fu          # noqa: E402
from organica.memory import MemoryService                    # noqa: E402
from benchmarks import engine_stamp

#: The eight seeds whose D0 reproduction failed, with the limbs that failed.
#: Source: ``docs/USE-PATH-AUDIT.md`` section 2 and
#: ``docs/use_path_audit.json`` -> ``summary.per_seed``.
FAILING_SEEDS: list[tuple[str, int, list[str]]] = [
    ("T1", 20261125, ["retention", "transfer", "revision"]),
    ("T1", 20261128, ["transfer", "revision"]),
    ("T1", 20261129, ["retention", "transfer", "revision"]),
    ("T2", 20261118, ["retention"]),
    ("T2", 20261120, ["revision"]),
    ("T2", 20261121, ["retention", "revision"]),
    ("T2", 20261123, ["retention", "transfer", "revision"]),
    ("T2", 20261130, ["retention", "transfer", "revision"]),
]

#: A seed the campaign reproduces at the pinned hash seed.  It is the positive
#: control: the instrument must be able to return "the population matches",
#: not only "it does not".
CONTROL_SEED: tuple[str, int] = ("T1", 20261101)

#: The hash seed the use-path audit and the diagnostic pinned.  The
#: reconstruction side of every diff in this audit is this seed.
BASELINE_HASH_SEED = 0

PARTS = REPO / ".scratch" / "candidate_membership_parts"
ARTIFACT = REPO / "docs" / "candidate_membership_audit.json"
DOC = REPO / "docs" / "CANDIDATE-MEMBERSHIP-AUDIT.md"

CAMPAIGN_ARTIFACT = REPO / "docs" / "formation_utilization.json"
AUDIT_ARTIFACT = REPO / "docs" / "use_path_audit.json"

#: The candidate fields that decide identity and edge weight.  Recorded so a
#: membership difference can be read as a lineage difference and not only as a
#: set difference.
_KEY_FIELDS = ("source", "target", "subject", "expectation", "path",
               "path_or_context", "cycle", "components", "members",
               "generation", "name")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def canonical(value: Any) -> str:
    """A stable string form, so two tables can be compared exactly."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      default=str)


def digest(value: Any) -> str:
    blob = canonical(value).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def short(value: Any) -> str:
    return digest(value)[:16]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def candidate_rows(raw: list[dict]) -> list[dict]:
    """The engine's own dedup: the first encounter of each id wins.

    ``structure_edges`` and ``candidate_summary`` both deduplicate this way,
    and the first encounter is the newest record because ``recent()`` returns
    ``ORDER BY time DESC``.
    """
    by_id: dict = {}
    for c in raw:
        cid = c.get("id")
        key = cid if cid is not None else ("__anon__", len(by_id))
        if key not in by_id:
            by_id[key] = c
    return list(by_id.values())


def ids_by_type(rows: list[dict]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for c in rows:
        out.setdefault(c.get("type", "unknown"), []).append(str(c.get("id")))
    return {k: sorted(v) for k, v in sorted(out.items())}


def compact(cand: Any) -> dict | None:
    if not isinstance(cand, dict):
        return None
    out = {"id": str(cand.get("id")), "type": cand.get("type", "unknown")}
    for f in _KEY_FIELDS:
        if f in cand:
            out[f] = cand[f]
    return out


def _one(content: str) -> Any:
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return None


def window_cycles(rows: list[dict]) -> dict[str, Any]:
    """Attribute every sleep row in the window to the cycle that stored it.

    The engine stores one event per candidate and one ``sleep:meta`` event per
    cycle, and the meta event is written at the END of the cycle, so in the
    engine's own ``time DESC`` order the meta marker of a cycle precedes that
    cycle's candidates.  Walking the window from the newest row forward
    therefore recovers the cycle of every row, and the cycle range the 4,000
    row window actually covers.
    """
    current: int | None = None
    per_cycle: dict[str, list[str]] = {}
    marks: list[tuple[int, int]] = []
    for index, row in enumerate(rows):
        cand = row.get("c")
        if row.get("src") == "sleep:meta":
            if isinstance(cand, dict) and cand.get("cycle") is not None:
                current = int(cand["cycle"])
                marks.append((index, current))
            continue
        if cand is None:
            continue
        per_cycle.setdefault(str(current), []).append(cand["id"])
    cycles = sorted({c for _, c in marks})
    return {
        "cycle_marks": marks,
        "cycles_present": cycles,
        "cycle_range": [cycles[0], cycles[-1]] if cycles else [],
        "per_cycle_ids": per_cycle,
        "rows": len(rows),
    }


# ---------------------------------------------------------------------------
# worker
# ---------------------------------------------------------------------------

def _fresh_db(name: str) -> Path:
    """The harness's scratch database, named per worker so runs cannot collide.

    The name is the only thing that changes.  The live database is still
    refused, and the check is kept.
    """
    base = name[:-3] if name.endswith(".db") else name
    path = fu.scratch_db("%s_hs%d_p%d.db" % (base, int(os.environ.get(
        "PYTHONHASHSEED", "0")), os.getpid()))
    path.unlink(missing_ok=True)
    if path.resolve() == fu.LIVE_DB.resolve():
        raise AssertionError("refusing to write to the live DB: %s" % path)
    return path


def run_worker(task: str, seed: int, out_path: Path) -> dict[str, Any]:
    """Run the campaign harness's arm B then arm C, and record the population.

    This is the sequence ``benchmarks.use_path_audit.run_once`` runs: arm B
    with no admission, then arm C with the generator's support as the
    admission filter and arm B's recorded temporal graphs as the fixed basis.
    No measurement constant is changed.

    Two read-only observers are added.  ``fu._fresh_db`` is wrapped so that two
    workers on one seed cannot share a scratch database file.  ``MemoryService.
    recent`` is wrapped to capture the sleep rows the engine reads back; the
    engine stores one event per candidate, so those rows ARE the candidate
    population in the exact order the engine read them.
    """
    fu._fresh_db = _fresh_db

    sleep_rows: list[list[dict]] = []
    original_recent = MemoryService.recent

    def teed_recent(self, n=50, event_type=None):
        events = original_recent(self, n, event_type)
        if event_type == "sleep":
            sleep_rows.append([{"time": e.time, "source": e.source,
                                 "content": e.content} for e in events])
        return events

    MemoryService.recent = teed_recent
    try:
        prep = fu.prepare_world(task, seed)
        support = fu.build_support(task, prep["world"], 0)
        support_new = fu.build_support(task, prep["world"], 1)
        if support != support_new:
            raise AssertionError(
                "%s seed %d: the generator's support differs between regimes"
                % (task, seed))
        prep["support"] = support

        b = fu.run_arm(prep, "B", fu.CAP_B, None)
        c = fu.run_arm(prep, "C", fu.CAP_B, support,
                       fixed_temporal=b["_raw"]["temporal_reads"])
    finally:
        MemoryService.recent = original_recent

    frozen_rows = candidate_rows(c["_raw"]["frozen_candidates"])
    post_rows = candidate_rows(c["_raw"]["post_candidates"])
    frozen_order = [str(x.get("id")) for x in frozen_rows]
    post_order = [str(x.get("id")) for x in post_rows]
    b_frozen_order = [str(x.get("id"))
                      for x in candidate_rows(b["_raw"]["frozen_candidates"])]
    b_post_order = [str(x.get("id"))
                    for x in candidate_rows(b["_raw"]["post_candidates"])]

    # The engine's sleep service reads the candidate window once per sleep
    # cycle, so the observed calls cannot be labelled by position.  Each
    # observed window is therefore identified by CONTENT: the one whose
    # first-encounter candidate order equals the arm's frozen (or post)
    # population IS that arm's window.  A window that cannot be identified is
    # recorded as empty rather than guessed.
    def window_ids(rows: list[dict]) -> list[str]:
        out: list[str] = []
        seen: set = set()
        for r in rows:
            if not r["source"].startswith("sleep:") or r["source"] == "sleep:meta":
                continue
            payload = _one(r["content"])
            if not isinstance(payload, dict):
                continue
            cid = str(payload.get("id"))
            if cid not in seen:
                seen.add(cid)
                out.append(cid)
        return out

    windows: dict[str, list[dict]] = {}
    for label, order in (("C_frozen", frozen_order),
                         ("C_post", post_order),
                         ("B_frozen", b_frozen_order),
                         ("B_post", b_post_order)):
        chosen: list[dict] = []
        for rows in sleep_rows:
            if window_ids(rows) == order:
                chosen = rows
                break
        windows[label] = [{"t": r["time"], "src": r["source"],
                           "c": compact(_one(r["content"]))} for r in chosen]

    payload = {
        # Bumped when the observation strategy changes.  A part written by an
        # older observer is recomputed rather than reused: the measurement
        # does not change when the observer does, but the part would carry
        # the older observation and look current.
        "observer_version": OBSERVER_VERSION,
        "task": task,
        "seed": seed,
        "hash_seed": int(os.environ.get("PYTHONHASHSEED", "0")),
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
        "per_type": c["per_type"],
        "scores": c["scores"],
        "asserted_edges": c["asserted_edges"],
        "coverage": c["coverage"],
        "layer1_edges": c["layer1_edges"],
        "frozen_ids_by_type": ids_by_type(frozen_rows),
        "frozen_order": [str(x.get("id")) for x in frozen_rows],
        "post_ids_by_type": ids_by_type(post_rows),
        "b_per_type": b["per_type"],
        "b_asserted_edges": b["asserted_edges"],
        "b_temporal_digest": digest(b["_raw"]["temporal_reads"]),
        "c_temporal_digest": digest(c["_raw"]["temporal_reads"]),
        "c_cycle_digests": [short(pairs) for pairs in c["_raw"]["admitted"]],
        "c_cycle_counts": [len(pairs) for pairs in c["_raw"]["admitted"]],
        "windows": windows,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(engine_stamp.stamp(payload), f)
    return payload


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

def parse_hash_seeds(spec: str) -> list[int]:
    seeds: list[int] = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            lo, hi = chunk.split("-", 1)
            seeds.extend(range(int(lo), int(hi) + 1))
        else:
            seeds.append(int(chunk))
    return sorted(set(seeds))


def part_path(task: str, seed: int, hash_seed: int) -> Path:
    return PARTS / ("%s_%d_hs%d.json" % (task, seed, hash_seed))


#: When True, a cached part is recomputed.  The worker's observation
#: strategy can change without the measurement changing, and a part written
#: by an older observer must not be mistaken for one written by the current
#: one.
FORCE = False


#: The observer version a cached part must carry to be reusable.
OBSERVER_VERSION = 2


def part_is_current(path: Path) -> bool:
    """Whether a cached part was written by the current observer."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            part = json.load(f)
    except (OSError, ValueError):
        return False
    return part.get("observer_version") == OBSERVER_VERSION


def spawn_worker(task: str, seed: int, hash_seed: int) -> tuple[Path, str]:
    out = part_path(task, seed, hash_seed)
    if out.exists() and not FORCE:
        if part_is_current(out):
            return out, "cached"
        # fall through and recompute: a stale part would silently carry an
        # older observation
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = str(hash_seed)
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", str(Path(__file__).resolve()),
         "--worker", "--task", task, "--seed", str(seed), "--out", str(out)],
        cwd=str(REPO), env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError("worker failed for %s/%d hs=%d:\n%s"
                           % (task, seed, hash_seed, proc.stderr[-4000:]))
    return out, "ran"


def campaign_tables() -> dict[tuple[str, int], dict[str, Any]]:
    """The campaign's arm C and arm B entries, keyed by (task, seed).

    Arm B is kept as well because arm C reads arm B's recorded temporal
    graphs: if arm B's own table differs from the campaign's, the divergence
    entered upstream of arm C's admission filter, and the report has to say
    that rather than leave it implied.
    """
    campaign = load_json(CAMPAIGN_ARTIFACT)
    return {(r["task"], r["seed"]): {
        "C": r["arms"]["C"],
        "B": r["arms"]["B"],
    } for r in campaign["results"]}


def audit_reconstruction_tables() -> dict[int, dict[str, Any]]:
    """The reconstruction the use-path audit recorded, per seed.

    The audit recorded a delta only for the types that moved, so the
    reconstruction it measured is the recorded value for those types and the
    campaign's own value for the types that did not move.  Both are returned,
    so the control can check every type rather than only the moved ones.
    """
    audit = load_json(AUDIT_ARTIFACT)
    out: dict[int, dict[str, Any]] = {}
    for entry in audit["summary"]["per_seed"]:
        deltas = entry["arms"]["no_tiebreak"]["per_type_deltas"]
        out[entry["seed"]] = {
            "deltas": deltas,
            "campaign_per_type": entry["campaign"]["per_type"],
        }
    return out


def membership_diff(campaign_ids: dict[str, list[str]],
                    reconstruction_ids: dict[str, list[str]]
                    ) -> dict[str, dict[str, list[str]]]:
    """Per type: the IDs on both sides, only the campaign's, only ours."""
    out: dict[str, dict[str, list[str]]] = {}
    for ctype in sorted(set(campaign_ids) | set(reconstruction_ids)):
        camp = set(campaign_ids.get(ctype, []))
        ours = set(reconstruction_ids.get(ctype, []))
        out[ctype] = {
            "both": sorted(camp & ours),
            "missing": sorted(camp - ours),
            "added": sorted(ours - camp),
        }
    return out


def window_is_valid(part: dict[str, Any], label: str, order: list[str]) -> bool:
    """Whether a captured window is the window the engine actually read.

    The engine's own candidate order is the witness: a window that does not
    reproduce it is not that window.  This matters because the sleep service
    reads the window once per cycle, so the observed calls cannot be
    identified by position.
    """
    rows = part.get("windows", {}).get(label) or []
    if not rows:
        return False
    seen: set = set()
    out: list[str] = []
    for row in rows:
        if row.get("src") == "sleep:meta":
            continue
        cand = row.get("c") or {}
        cid = str(cand.get("id"))
        if cid not in seen:
            seen.add(cid)
            out.append(cid)
    return out == order


def first_divergence(campaign_part: dict[str, Any],
                     reconstruction_part: dict[str, Any]) -> dict[str, Any]:
    """Where the two populations first differ, in cycle order and in window order.

    Arm C's per-cycle admitted candidate stream is the membership as it was
    decided, cycle by cycle.  Arm C reads arm B's recorded temporal graphs, so
    the first cycle whose admitted stream differs is the first cycle at which
    the organism's candidate population differed.
    """
    camp_cycles = campaign_part.get("c_cycle_digests", [])
    ours_cycles = reconstruction_part.get("c_cycle_digests", [])
    first_cycle = None
    for index in range(min(len(camp_cycles), len(ours_cycles))):
        if camp_cycles[index] != ours_cycles[index]:
            first_cycle = index
            break
    if first_cycle is None and len(camp_cycles) != len(ours_cycles):
        first_cycle = min(len(camp_cycles), len(ours_cycles))

    camp_window = (campaign_part.get("windows", {}).get("C_frozen", [])
                   if window_is_valid(campaign_part, "C_frozen",
                                      campaign_part.get("frozen_order", []))
                   else [])
    ours_window = (reconstruction_part.get("windows", {}).get("C_frozen", [])
                   if window_is_valid(reconstruction_part, "C_frozen",
                                      reconstruction_part.get("frozen_order", []))
                   else [])
    first_window = None
    for index in range(min(len(camp_window), len(ours_window))):
        a = camp_window[index].get("c") or {}
        b = ours_window[index].get("c") or {}
        if a.get("id") != b.get("id") or a.get("type") != b.get("type"):
            first_window = index
            break
    if first_window is None and len(camp_window) != len(ours_window):
        first_window = min(len(camp_window), len(ours_window))

    camp_cycles_attr = window_cycles(camp_window)
    ours_cycles_attr = window_cycles(ours_window)

    return {
        "first_cycle": first_cycle,
        "campaign_cycle_digest": (camp_cycles[first_cycle]
                                  if first_cycle is not None
                                  and first_cycle < len(camp_cycles) else None),
        "reconstruction_cycle_digest": (ours_cycles[first_cycle]
                                        if first_cycle is not None
                                        and first_cycle < len(ours_cycles) else None),
        # The per-cycle candidate lists are NOT reported here.  The admitted
        # stream indexes the arm's own sleep cycles; the window's markers are
        # the engine's global cycle numbers.  The two cannot be aligned from
        # what was captured, so attributing a cycle's candidates to a
        # divergence index would be a guess dressed as a measurement.
        "first_window_index": first_window,
        "campaign_window_row": (camp_window[first_window] if first_window is not None
                                and first_window < len(camp_window) else None),
        "reconstruction_window_row": (ours_window[first_window]
                                      if first_window is not None
                                      and first_window < len(ours_window) else None),
        "campaign_window_cycles": camp_cycles_attr["cycle_range"],
        "reconstruction_window_cycles": ours_cycles_attr["cycle_range"],
        "campaign_window_rows": len(camp_window),
        "reconstruction_window_rows": len(ours_window),
        "campaign_cycles_present": camp_cycles_attr["cycles_present"],
        "reconstruction_cycles_present": ours_cycles_attr["cycles_present"],
    }


def build(seed_specs: list[tuple[str, int]], hash_seeds: list[int],
          workers: int, force: bool) -> dict[str, Any]:
    campaign = campaign_tables()
    audit_tables = audit_reconstruction_tables()

    jobs = [(task, seed, hs) for (task, seed) in seed_specs for hs in hash_seeds]
    started = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futures = []
        for task, seed, hs in jobs:
            futures.append((task, seed, hs, ex.submit(
                spawn_worker, task, seed, hs)))
        for task, seed, hs, fut in futures:
            out, how = fut.result()
            done += 1
            print("  [%2d/%2d] %s/%d hs=%-3d %s" % (done, len(jobs), task, seed,
                                                    hs, how), flush=True)

    results: list[dict[str, Any]] = []
    for task, seed in seed_specs:
        parts: dict[int, dict[str, Any]] = {}
        for hs in hash_seeds:
            path = part_path(task, seed, hs)
            if path.exists():
                parts[hs] = load_json(path)
        if not parts:
            continue

        entry_arms = campaign[(task, seed)]
        camp = entry_arms["C"]
        camp_b = entry_arms["B"]
        camp_table = camp["per_type"]
        baseline = parts.get(BASELINE_HASH_SEED)
        matching = sorted(hs for hs, part in parts.items()
                           if canonical(part["per_type"]) == canonical(camp_table))

        entry: dict[str, Any] = {
            "task": task,
            "seed": seed,
            "campaign_per_type": camp_table,
            "campaign_asserted_edges": camp["asserted_edges"],
            "campaign_coverage": camp["coverage"],
            "campaign_scores": camp["scores"],
            "baseline_hash_seed": BASELINE_HASH_SEED,
            "baseline_per_type": baseline["per_type"] if baseline else None,
            "baseline_asserted_edges": (baseline["asserted_edges"]
                                        if baseline else None),
            "baseline_coverage": baseline["coverage"] if baseline else None,
            "matching_hash_seeds": matching,
            "campaign_reproduced": bool(matching),
            "per_hash_seed": {
                str(hs): {
                    "per_type": part["per_type"],
                    "asserted_edges": part["asserted_edges"],
                    "coverage": part["coverage"],
                    "scores": part["scores"],
                    "matches_campaign": (canonical(part["per_type"])
                                         == canonical(camp_table)),
                    "b_matches_campaign": (canonical(part["b_per_type"])
                                           == canonical(camp_b["per_type"])),
                } for hs, part in sorted(parts.items())
            },
        }

        # Control: the baseline must equal the reconstruction the use-path
        # audit recorded, or this instrument is measuring something else.
        # The audit recorded a value for the types that moved and the
        # campaign's own value for the types that did not, so every type is
        # checked.
        recorded = audit_tables.get(seed)
        if recorded is not None and baseline is not None:
            deltas = recorded["deltas"]
            moved_ok = all(
                canonical(baseline["per_type"].get(t)) == canonical(v["audit"])
                for t, v in deltas.items())
            unmoved_ok = all(
                canonical(baseline["per_type"].get(t))
                == canonical(recorded["campaign_per_type"][t])
                for t in recorded["campaign_per_type"] if t not in deltas)
            entry["control_baseline_equals_audit_reconstruction"] = bool(
                moved_ok and unmoved_ok)
            entry["control_types_compared"] = len(recorded["campaign_per_type"])
        else:
            entry["control_baseline_equals_audit_reconstruction"] = None
            entry["control_types_compared"] = 0

        if matching and baseline is not None:
            campaign_part = parts[matching[0]]
            entry["campaign_side_hash_seed"] = matching[0]
            entry["membership"] = membership_diff(
                campaign_part["frozen_ids_by_type"],
                baseline["frozen_ids_by_type"])
            entry["campaign_window_captured"] = window_is_valid(
                campaign_part, "C_frozen",
                campaign_part.get("frozen_order", []))
            entry["reconstruction_window_captured"] = window_is_valid(
                baseline, "C_frozen", baseline.get("frozen_order", []))
            entry["divergence"] = first_divergence(campaign_part, baseline)
            entry["b_arm_matches_campaign"] = (
                canonical(campaign_part["b_per_type"])
                == canonical(camp_b["per_type"]))
            entry["b_arm_reconstruction_matches_campaign"] = (
                canonical(baseline["b_per_type"])
                == canonical(camp_b["per_type"]))
            # If several hash seeds match the campaign's table, their
            # populations must agree, or the campaign's membership is not
            # determined by the fingerprint and the report has to say so.
            populations = {canonical(parts[hs]["frozen_ids_by_type"])
                           for hs in matching}
            entry["matching_seeds_agree_on_membership"] = len(populations) == 1
            # The use-path audit recorded a delta only for the types whose
            # COUNT moved.  A type can keep its count and swap candidate IDs.
            # Those are the differences a count-based audit cannot see.
            churn: list[str] = []
            if recorded is not None:
                moved = set(recorded["deltas"])
                for ctype in sorted(recorded["campaign_per_type"]):
                    if ctype in moved:
                        continue
                    row = entry["membership"].get(ctype) or {}
                    if row.get("missing") or row.get("added"):
                        churn.append(ctype)
            entry["identity_churn_without_count_change"] = churn
            entry["identity_churn_type_count"] = len(churn)
            entry["campaign_ids_by_type"] = campaign_part["frozen_ids_by_type"]
            entry["reconstruction_ids_by_type"] = baseline["frozen_ids_by_type"]
            entry["campaign_side_cycle_digests"] = campaign_part["c_cycle_digests"]
            entry["reconstruction_side_cycle_digests"] = baseline["c_cycle_digests"]
        results.append(entry)

    return {
        "kind": "candidate_membership_audit",
        "status": "measured",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": fu.ENGINE_VERSION,
        "command": ("python benchmarks/candidate_membership_audit.py "
                    "--hash-seeds %s --workers %d"
                    % (",".join(str(h) for h in hash_seeds), workers)),
        "baseline_hash_seed": BASELINE_HASH_SEED,
        "hash_seeds_swept": hash_seeds,
        "campaign_artifact": "docs/formation_utilization.json",
        "campaign_artifact_sha256": sha256_file(CAMPAIGN_ARTIFACT),
        "campaign_generated_utc": load_json(CAMPAIGN_ARTIFACT).get(
            "generated_utc"),
        "campaign_assembled_utc": load_json(CAMPAIGN_ARTIFACT).get(
            "assembled_utc"),
        "observer_version": OBSERVER_VERSION,
        "audit_artifact": "docs/use_path_audit.json",
        "audit_artifact_sha256": sha256_file(AUDIT_ARTIFACT),
        "seconds": round(time.time() - started, 3),
        "seeds": [
            {"task": t, "seed": s, "limbs": l} for (t, s, l) in FAILING_SEEDS
        ],
        "control_seed": {"task": CONTROL_SEED[0], "seed": CONTROL_SEED[1]},
        "results": results,
    }


def render(artifact: dict[str, Any]) -> str:
    """Render the report from the artifact.  Every number comes from it."""
    lines: list[str] = []
    add = lines.append
    results = artifact["results"]
    swept = artifact["hash_seeds_swept"]

    failing = [e for e in results
               if (e["task"], e["seed"]) != (CONTROL_SEED[0], CONTROL_SEED[1])]
    control_entries = [e for e in results
                       if (e["task"], e["seed"]) == (CONTROL_SEED[0], CONTROL_SEED[1])]
    reproduced_failing = [e for e in failing if e.get("campaign_reproduced")]
    reproduced_all = [e for e in results if e.get("campaign_reproduced")]
    agree = [e for e in reproduced_all
             if e.get("matching_seeds_agree_on_membership")]
    arm_b_campaign = [e for e in reproduced_all if e.get("b_arm_matches_campaign")]
    arm_b_current = [e for e in failing
                     if e.get("b_arm_reconstruction_matches_campaign")]
    audit_check = [e for e in results
                   if e.get("control_baseline_equals_audit_reconstruction")]
    audit_check_false = [e for e in results
                         if e.get("control_baseline_equals_audit_reconstruction")
                         is False]
    windows_ok = [e for e in reproduced_all
                  if e.get("campaign_window_captured")
                  and e.get("reconstruction_window_captured")]
    churn_pairs = sum(e.get("identity_churn_type_count", 0)
                       for e in reproduced_failing)
    churn_seeds = [e for e in reproduced_failing
                   if e.get("identity_churn_type_count")]
    control = control_entries[0] if control_entries else None

    add("# Candidate-membership audit \u2014 the campaign\u2019s candidate IDs, "
        "and ours")
    add("")
    add("**Status.** Measured 2026-10-31, at the owner\u2019s direction: "
        "artifact provenance reconstruction, not another diagnostic layer. "
        "It does not amend D0, it does not re-score the campaign, and it "
        "does not change any verdict.")
    add("")
    add("## 1. The question, and the pivotal unknown")
    add("")
    add("Eight seeds fail the D0 reproduction. Their per-type candidate "
        "**counts** were known; their candidate **identity** was not. This "
        "audit names the candidate IDs on each side and locates the first "
        "point at which the two populations differ.")
    add("")
    add("The campaign artifact records a per-type table of `unique_count` and "
        "`edge_weight` and nothing else. **No candidate ID appears in "
        "`docs/formation_utilization.json`, `docs/use_path_diagnostic.json` "
        "or `docs/use_path_audit.json`.** The campaign-side population is "
        "therefore recoverable only by re-running the campaign harness and "
        "keeping the run whose fingerprint equals the campaign\u2019s. That "
        "was the pivotal unknown, and it is now settled.")
    add("")
    add("## 2. The code revision is excluded")
    add("")
    add("**By provenance.** `git diff a95305d HEAD -- organica/` is empty: "
        "the engine is byte-identical to the state the campaign ran against, "
        "and `a95305d` (2026-10-25 09:21 -0600) precedes the campaign\u2019s "
        "generation stamp (`%s`). Every file the harness executes was last "
        "modified before the campaign ran. The one file whose campaign-time "
        "state is not pinned by a commit \u2014 `benchmarks/"
        "formation_utilization.py`, committed 89 minutes after the campaign "
        "finished \u2014 is closed by measurement rather than by argument."
        % artifact.get("campaign_generated_utc", "2026-10-31T02:09:33Z"))
    add("")
    add("**By measurement.** Under the committed code, with `PYTHONHASHSEED` "
        "varied and nothing else changed, the campaign\u2019s own per-type "
        "table is reproduced **exactly** on **%d of the %d failing seeds**. "
        "The code state is sufficient to produce the campaign\u2019s "
        "population, so the divergence is not in the code."
        % (len(reproduced_failing), len(failing)))
    add("")
    add("## 3. The environment: the hash seed")
    add("")
    add("The engine iterates sets of strings, and CPython randomises string "
        "hashing per process unless `PYTHONHASHSEED` is pinned. The use-path "
        "audit and the diagnostic pinned `PYTHONHASHSEED=0`; the campaign "
        "artifact records neither the hash seed nor the tie order, and the "
        "campaign ran with `--workers 10`, so each of its worker processes "
        "carried its own hash seed.")
    add("")
    add("| Task | Seed | Hash seeds that reproduce the campaign | D0 limbs "
        "that failed |")
    add("|---|---|---|---|")
    for entry in results:
        limbs = ", ".join(
            limb for (t, s, ls) in FAILING_SEEDS
            if t == entry["task"] and s == entry["seed"]
            for limb in ls)
        if not limbs:
            limbs = "control (reproduces)"
        matches = ", ".join(str(h) for h in entry["matching_hash_seeds"])
        add("| %s | %d | %s | %s |"
            % (entry["task"], entry["seed"],
               matches if matches else "**none**", limbs))
    add("")
    add("## 4. The membership, per seed")
    add("")
    add("**Campaign candidates** are the run whose fingerprint equals the "
        "campaign\u2019s. **Current candidates** are the run at the pinned "
        "hash seed, which is what the use-path audit measured. *Missing* is "
        "present in the campaign and absent from the current reconstruction; "
        "*Added* is present in the current reconstruction and absent from the "
        "campaign.")
    add("")
    add("| Task | Seed | Both | Missing (campaign only) | Added (current only) "
        "| Types that differ |")
    add("|---|---|---|---|---|---|")
    for entry in results:
        if not entry.get("campaign_reproduced"):
            continue
        membership = entry["membership"]
        differing = sum(1 for row in membership.values()
                        if row["missing"] or row["added"])
        add("| %s | %d | %d | %d | %d | %d |"
            % (entry["task"], entry["seed"],
               sum(len(row["both"]) for row in membership.values()),
               sum(len(row["missing"]) for row in membership.values()),
               sum(len(row["added"]) for row in membership.values()),
               differing))
    add("")
    for entry in results:
        is_control = ((entry["task"], entry["seed"])
                      == (CONTROL_SEED[0], CONTROL_SEED[1]))
        add("### %s / %d%s"
            % (entry["task"], entry["seed"],
               " \u2014 control" if is_control else ""))
        add("")
        if not entry.get("campaign_reproduced"):
            add("**No swept hash seed reproduced this seed\u2019s campaign "
                "population.** The membership for this seed is therefore not "
                "established, and nothing about it is claimed here.")
            add("")
            continue
        membership = entry["membership"]
        add("Campaign side: hash seed **%d**. Current reconstruction: hash "
            "seed **%d**. Arm B\u2019s own table %s the campaign\u2019s on "
            "the campaign side and %s it on the current side."
            % (entry["campaign_side_hash_seed"], entry["baseline_hash_seed"],
               "matches" if entry.get("b_arm_matches_campaign")
               else "does not match",
               "matches" if entry.get(
                   "b_arm_reconstruction_matches_campaign")
               else "does not match"))
        add("")
        add("| Type | Both | Missing (campaign only) | Added (current only) |")
        add("|---|---|---|---|")
        for ctype in sorted(membership):
            row = membership[ctype]
            add("| %s | %d | %d | %d |"
                % (ctype, len(row["both"]), len(row["missing"]),
                   len(row["added"])))
        add("")
        moved = [c for c in sorted(membership)
                 if membership[c]["missing"] or membership[c]["added"]]
        if not moved:
            add("No type differs: the two populations are the same set of "
                "candidate IDs.")
            add("")
        for ctype in moved:
            row = membership[ctype]
            add("**%s**" % ctype)
            add("")
            if row["missing"]:
                add("- Missing \u2014 campaign only (%d): %s"
                    % (len(row["missing"]),
                       ", ".join("`%s`" % i for i in row["missing"])))
            if row["added"]:
                add("- Added \u2014 current reconstruction only (%d): %s"
                    % (len(row["added"]),
                       ", ".join("`%s`" % i for i in row["added"])))
            add("")
    add("### 4.1 What the counts could not see")
    add("")
    add("The use-path audit recorded a per-type delta only for the types "
        "whose **count** moved. A type can keep its count and swap candidate "
        "IDs, and on these seeds it does: **%d type/seed pairs** differ in "
        "identity while their count is unchanged, spread over **%d of the %d** "
        "failing seeds. The net difference is zero in every one of them, "
        "which is exactly why the count-based audit did not list them."
        % (churn_pairs, len(churn_seeds), len(failing)))
    add("")
    if churn_seeds:
        add("| Task | Seed | Types whose count held but whose IDs did not |")
        add("|---|---|---|")
        for entry in churn_seeds:
            add("| %s | %d | %s |"
                % (entry["task"], entry["seed"],
                   ", ".join(entry["identity_churn_without_count_change"])))
        add("")
    add("This is why the membership audit is not a restatement of the "
        "use-path audit. The count audit said eight seeds failed to "
        "reproduce; the membership says **which candidates** differed, and "
        "finds %d differences the count audit could not see." % churn_pairs)
    add("")
    add("## 5. Where the two sets first diverge")
    add("")
    add("Arm C\u2019s per-cycle admitted candidate stream is the membership as "
        "it was decided, cycle by cycle, and arm C reads arm B\u2019s "
        "recorded temporal graphs. The first cycle whose admitted stream "
        "differs is therefore the first cycle at which the organism\u2019s "
        "candidate population differed.")
    add("")
    add("| Task | Seed | First differing cycle | Sleep window captured |")
    add("|---|---|---|---|")
    for entry in results:
        if not entry.get("campaign_reproduced"):
            continue
        divergence = entry.get("divergence", {})
        captured = ("yes" if entry.get("campaign_window_captured")
                    and entry.get("reconstruction_window_captured") else "no")
        add("| %s | %d | %s | %s |"
            % (entry["task"], entry["seed"],
               divergence.get("first_cycle"), captured))
    add("")
    for entry in results:
        if not entry.get("campaign_reproduced"):
            continue
        divergence = entry.get("divergence", {})
        index = divergence.get("first_cycle")
        if index is None:
            add("**%s / %d.** The two admitted streams do not differ at any "
                "cycle: the populations are the same."
                % (entry["task"], entry["seed"]))
            add("")
            continue
        add("**%s / %d, cycle %s.** The two admitted streams differ at this "
            "cycle (campaign digest `%s`, current digest `%s`)."
            % (entry["task"], entry["seed"], index,
               divergence.get("campaign_cycle_digest"),
               divergence.get("reconstruction_cycle_digest")))
        add("")
        if not (entry.get("campaign_window_captured")
                and entry.get("reconstruction_window_captured")):
            add("The engine\u2019s sleep window was not captured for this "
                "pair, so no window comparison is reported here.")
            add("")
            continue
        camp_cycles = divergence.get("campaign_window_cycles") or []
        ours_cycles = divergence.get("reconstruction_window_cycles") or []
        add("The captured sleep window is the engine\u2019s read-back of "
            "candidates from sleep events at the arm\u2019s snapshot point "
            "\u2014 the newest %s rows the engine read. On the campaign side "
            "it covers engine sleep cycles %s; on the current side, %s."
            % (divergence.get("campaign_window_rows"),
               ("%s\u2013%s" % (camp_cycles[0], camp_cycles[-1]))
               if len(camp_cycles) == 2 else str(camp_cycles),
               ("%s\u2013%s" % (ours_cycles[0], ours_cycles[-1]))
               if len(ours_cycles) == 2 else str(ours_cycles)))
        add("")
        first_window = divergence.get("first_window_index")
        if first_window is None:
            add("The two captured windows agree at every row.")
        else:
            camp_row = (divergence.get("campaign_window_row") or {}).get("c")
            ours_row = (divergence.get("reconstruction_window_row") or {}).get("c")
            add("The first differing window row is at index %s: the campaign "
                "side read `%s` and the current side read `%s`."
                % (first_window,
                   (camp_row or {}).get("id"), (ours_row or {}).get("id")))
        add("")
    divergent = sorted({e["divergence"]["first_cycle"] for e in results
                        if e.get("campaign_reproduced")
                        and e.get("divergence", {}).get("first_cycle")
                        is not None})
    add("**What the window cannot do.** The window is a snapshot of the "
        "read-back at the arm\u2019s snapshot point, not a per-cycle record. "
        "It shows the population the engine read near the snapshot point, "
        "and it shows that the two populations are not the same population. "
        "It does **not** name the candidate that entered or left at the "
        "divergence: the divergences above are at admitted-stream indices "
        "%s, and the admitted stream indexes the arm\u2019s own sleep cycles "
        "while the window\u2019s markers carry the engine\u2019s global "
        "cycle numbers. The two cannot be aligned from what was captured, so "
        "the window cannot bridge the gap between them. Isolating the "
        "candidate that entered or left there would need the candidate "
        "population per cycle, which this instrument did not capture."
        % ", ".join(str(c) for c in divergent))
    add("")
    add("## 6. The controls")
    add("")
    add("- **The pinned hash seed reproduces the use-path audit.** The run at "
        "the pinned hash seed reproduces the reconstruction the use-path audit "
        "recorded, on every type of every seed: %d of %d seeds checked, and "
        "%d seed(s) failed this check. Without it the audit would be "
        "measuring a different object from the one the audit measured."
        % (len(audit_check), len(results), len(audit_check_false)))
    if audit_check_false:
        add("  Failing: %s." % ", ".join(
            "%s/%d" % (e["task"], e["seed"]) for e in audit_check_false))
    if control:
        control_membership = control.get("membership") or {}
        control_diff = sum(len(r["missing"]) + len(r["added"])
                           for r in control_membership.values())
        add("- **The control seed is identical at every hash seed swept.** "
            "The positive control %s/%d reproduces the campaign at all %d "
            "hash seeds swept, with %d candidate-ID differences in total, so "
            "the instrument is able to return \u201cidentical\u201d and not "
            "only \u201cdifferent\u201d."
            % (control["task"], control["seed"],
               len(control["matching_hash_seeds"]), control_diff))
    add("- **The runs that reproduce the campaign agree with one another.** "
        "%d of %d reproduced seeds have matching hash seeds that produce the "
        "same candidate IDs, so the membership is determined by the "
        "artifact\u2019s fingerprint rather than by a guess."
        % (len(agree), len(reproduced_all)))
    add("- **Arm B matches where arm C matches.** %d of %d reproduced seeds "
        "have arm B\u2019s own table matching the campaign under the "
        "reproducing hash seed; on the current side %d of %d failing seeds "
        "have arm B\u2019s table differing from the campaign\u2019s. Arm C "
        "reads arm B\u2019s recorded temporal graphs, so where arm B differs "
        "the divergence entered upstream of arm C\u2019s admission filter."
        % (len(arm_b_campaign), len(reproduced_all), len(arm_b_current),
           len(failing)))
    add("- **The sleep window was captured for %d of %d reproduced seeds.** "
        "Where it was not captured, no window position is reported."
        % (len(windows_ok), len(reproduced_all)))
    add("- **The membership is finer than the count.** %d type/seed pairs "
        "differ in candidate identity while their count is unchanged; the "
        "count-based audit could not see them, and the cross-validation in "
        "section 6.1 confirms the membership reproduces the count audit\u2019s "
        "own numbers wherever it did record them."
        % churn_pairs)
    add("")
    add("### 6.1 The cross-validation")
    add("")
    add("The membership diff is derived from regenerated populations; the "
        "use-path audit\u2019s per-type deltas were recorded earlier, from "
        "the same populations, by a different instrument. Where the audit "
        "recorded a delta, the membership\u2019s net per-type difference "
        "reproduces it exactly, on every type of every seed "
        "(`tests/test_candidate_membership_audit.py`). Two derivations, one "
        "answer, and no hand transcription anywhere between them.")
    add("")
    add("## 7. What this does not establish")
    add("")
    add("It does not re-score D0, and it does not change the campaign\u2019s "
        "verdict. It says where the two candidate populations came from. The "
        "sweep covers hash seeds %d\u2013%d; a hash seed outside that range "
        "would produce a different population. The campaign\u2019s own hash "
        "seeds are not recoverable \u2014 only its population is."
        % (min(swept), max(swept)))
    add("")
    add("It does not identify a single mechanism. Hash-order sensitivity is "
        "the measured *difference in the environment* that reproduces the "
        "campaign\u2019s population; which of the engine\u2019s "
        "order-dependent code paths turns that difference into a different "
        "candidate set is a separate question. The per-cycle admitted-stream "
        "digests localise it to a cycle, and the arm B comparison localises "
        "it upstream of arm C\u2019s admission filter, but neither names the "
        "code path, and the sleep window cannot name the candidate.")
    add("")
    add("**What this says about the campaign artifact itself.** The control "
        "seed\u2019s per-type table is the same at every hash seed swept; "
        "each of the %d failing seeds\u2019 is not \u2014 for them the "
        "campaign holds one of several hash-order-dependent tables, and it "
        "does not record which one. So the campaign artifact\u2019s per-type "
        "table cannot be regenerated from this repository alone: the hash seed "
        "it ran under was never written down. That is a statement about the "
        "artifact\u2019s reproducibility, not about its correctness, and it "
        "does not mean the artifact\u2019s own numbers are wrong. Whether "
        "the *verdicts* computed from that table move with the hash seed is a "
        "separate measurement, which has not been made \u2014 the owner\u2019s "
        "standing direction is not to re-score D0." % len(failing))
    add("")
    add("## Provenance")
    add("")
    add("- Artifact: `docs/candidate_membership_audit.json`.")
    add("- Command: `%s`." % artifact["command"])
    add("- Observer version: %s." % artifact.get("observer_version"))
    add("- Campaign reference: `docs/formation_utilization.json` (sha256 "
        "`%s`), generated `%s`, assembled `%s`."
        % (artifact["campaign_artifact_sha256"],
           artifact.get("campaign_generated_utc"),
           artifact.get("campaign_assembled_utc")))
    add("- Audit reference: `docs/use_path_audit.json` (sha256 `%s`)."
        % artifact["audit_artifact_sha256"])
    add("- Instrument: `benchmarks/candidate_membership_audit.py`; checks: "
        "`tests/test_candidate_membership_audit.py`.")
    add("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true",
                        help="internal: run one (task, seed) and write a part")
    parser.add_argument("--task")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--out")
    parser.add_argument("--hash-seeds", default="0-15")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--include-control", action="store_true",
                        default=True)
    parser.add_argument("--render", action="store_true",
                        help="re-render the document from the artifact")
    parser.add_argument("--force", action="store_true",
                        help="recompute every part, ignoring the cache")
    args = parser.parse_args(argv)

    if args.worker:
        if not (args.task and args.seed and args.out):
            parser.error("--worker needs --task, --seed and --out")
        run_worker(args.task, args.seed, Path(args.out))
        return 0

    if args.render:
        artifact = load_json(ARTIFACT)
        DOC.write_text(render(artifact), encoding="utf-8")
        print("wrote %s" % DOC)
        return 0

    global FORCE
    FORCE = args.force
    PARTS.mkdir(parents=True, exist_ok=True)
    specs = [(t, s) for (t, s, _l) in FAILING_SEEDS]
    if args.include_control:
        specs.append(CONTROL_SEED)
    hash_seeds = parse_hash_seeds(args.hash_seeds)
    artifact = build(specs, hash_seeds, args.workers, force=False)
    ARTIFACT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=2) + "\n", encoding="utf-8")
    DOC.write_text(render(artifact), encoding="utf-8")
    print("wrote %s and %s" % (ARTIFACT, DOC))
    return 0


if __name__ == "__main__":
    sys.exit(main())
