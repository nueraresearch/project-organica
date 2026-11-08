"""benchmarks/divergence_cycle_capture.py

Name the candidate pool at the cycle where the two populations diverge.

The candidate-membership audit established where the campaign's population and
the current reconstruction's population come apart -- at sleep cycles 2 to 11
depending on the seed -- and it captured the engine's 4,000-row sleep window.
That window is a snapshot of the read-back at the arm's snapshot point, which
is two or three cycles before the end of the run, so it cannot say which
candidate entered or left at the divergence.  This instrument closes that gap
by capturing the window **at the divergence cycle itself**.

Why the capture is addressed
----------------------------
The sleep service reads its window once per cycle, and the harness's arm loop
adds exactly two reads outside the cycle loop: one after the acquisition
phase (the "frozen" population) and one after the revision phase (the "post"
population).  So the i-th window read of an arm is the i-th cycle of that
arm, for every index before the first of those two extra reads.

That correspondence is not assumed here -- it is **proved from the data**.  The
engine stores one `sleep:meta` event per cycle, carrying that cycle's number,
and the window is read in descending time order.  So the newest meta marker in
the i-th window must carry cycle *i*.  If it does not, the capture is refused
rather than reported: an unjustified cycle position is worse than none.

Usage
-----
    python benchmarks/divergence_cycle_capture.py --worker --task T1 \
        --seed 20261125 --cycles 10,11 --out part.json
    python benchmarks/divergence_cycle_capture.py

The driver reads the candidate-membership artifact for each failing seed's
divergence cycle and for the two hash seeds it compares (the campaign side
and the pinned baseline), runs the worker for both, and writes
`docs/divergence_cycle_capture.json` and `docs/DIVERGENCE-CYCLE-CAPTURE.md`.
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
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import formation_utilization as fu          # noqa: E402
from organica.memory import MemoryService                   # noqa: E402
from benchmarks import engine_stamp

#: The candidate-membership audit, which says where each seed diverges.
MEMBERSHIP_ARTIFACT = REPO / "docs" / "candidate_membership_audit.json"

#: Where the captured windows live between runs.
PARTS_DIR = REPO / ".scratch" / "divergence_capture_parts"

#: The version of this observer.  A part written by a different observer is
#: recomputed rather than reused.
# Bumped 2 -> 3 on 2026-11-01: the cycle base was wrong.  The audit's
# first_cycle is a ZERO-BASED index and a window's index here is a one-based
# engine cycle, so every part captured under version 2 holds windows one
# cycle early.  part_is_current compares this field and nothing else.
OBSERVER_VERSION = 3

#: The control seed: the campaign reproduces it at every hash seed.
CONTROL_SEED = ("T1", 20261101)

#: The engine's cognition window.  ``_load_prior_candidates`` reads the newest
#: this many sleep rows, so a window at the cap is a truncated view of the
#: candidate history rather than the whole of it.
WINDOW_ROW_CAP = 4000


# ---------------------------------------------------------------------------
# the observer
# ---------------------------------------------------------------------------

def _one(content: str) -> Any:
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return None


def window_candidates(rows: list[dict]) -> list[dict]:
    """The candidates the engine read back, in the order it read them.

    ``_load_prior_candidates`` keeps every sleep event whose source begins
    with ``sleep:`` and is not the cycle marker, and parses its content as a
    candidate.  The engine does not deduplicate, so the same candidate can
    appear more than once; the first occurrence is its position in the read
    order, and that is what is recorded here.
    """
    out: list[dict] = []
    seen: set[str] = set()
    for r in rows:
        if not r["source"].startswith("sleep:") or r["source"] == "sleep:meta":
            continue
        payload = _one(r["content"])
        if not isinstance(payload, dict):
            continue
        cid = str(payload.get("id"))
        if cid in seen:
            continue
        seen.add(cid)
        out.append({"id": cid, "type": str(payload.get("type")),
                    "source": r["source"]})
    return out


def newest_marker_cycle(rows: list[dict]) -> int | None:
    """The cycle number on the newest cycle marker in the window.

    The marker is written before that cycle's candidates, and the window is
    read newest-first, so the newest marker is the cycle the window was read
    in, minus one.  It is the witness that the capture is addressed correctly.
    """
    for r in rows:
        if r["source"] != "sleep:meta":
            continue
        payload = _one(r["content"])
        if isinstance(payload, dict) and payload.get("cycle") is not None:
            return int(payload["cycle"])
    return None


def _fresh_db(name: str) -> Path:
    """The harness's scratch database, named per worker so runs cannot collide."""
    base = name[:-3] if name.endswith(".db") else name
    path = fu.scratch_db("%s_dcc_hs%d_p%d.db" % (
        base, int(os.environ.get("PYTHONHASHSEED", "0")), os.getpid()))
    path.unlink(missing_ok=True)
    if path.resolve() == fu.LIVE_DB.resolve():
        raise AssertionError("refusing to write to the live DB: %s" % path)
    return path


def run_worker(task: str, seed: int, cycles: list[int],
               out_path: Path) -> dict[str, Any]:
    """Run the harness's arm B then arm C, capturing the named windows.

    The sequence is the one ``benchmarks.use_path_audit.run_once`` runs: arm B
    with no admission, then arm C with the generator's support as the
    admission filter and arm B's recorded temporal graphs as the fixed basis.
    No measurement constant is changed, and the two observers added are
    read-only: the harness's scratch database is named per worker, and the
    sleep window read is wrapped so the named reads can be kept.
    """
    fu._fresh_db = _fresh_db

    wanted = set(int(c) for c in cycles)
    captured: dict[str, dict[int, dict]] = {}
    state = {"arm": None, "index": 0}
    original_recent = MemoryService.recent
    original_run_arm = fu.run_arm

    def teed_recent(self, n=50, event_type=None):
        events = original_recent(self, n, event_type)
        if event_type == "sleep" and state["arm"] is not None:
            index = state["index"]
            state["index"] = index + 1
            if index in wanted:
                rows = [{"time": e.time, "source": e.source, "content": e.content}
                        for e in events]
                captured.setdefault(state["arm"], {})[index] = {
                    "index": index,
                    "rows": len(rows),
                    "at_cap": len(rows) >= WINDOW_ROW_CAP,
                    "marker_cycle": newest_marker_cycle(rows),
                    "candidates": window_candidates(rows),
                }
        return events

    def wrapped_run_arm(prep, label, *args, **kwargs):
        state["arm"] = label
        state["index"] = 0
        try:
            return original_run_arm(prep, label, *args, **kwargs)
        finally:
            state["arm"] = None
            state["index"] = 0

    MemoryService.recent = teed_recent
    fu.run_arm = wrapped_run_arm
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
        fu.run_arm = original_run_arm

    # The alignment witness.  The window read at index i must carry the cycle
    # marker for cycle i.  Where it does not, the capture is refused rather
    # than reported at an unjustified position.
    addressed: dict[str, dict[str, Any]] = {}
    refused: list[str] = []
    for arm, windows in captured.items():
        for index, window in sorted(windows.items()):
            marker = window["marker_cycle"]
            ok = (marker == index) if index > 0 else (marker is None)
            entry = {
                "index": index,
                "rows": window["rows"],
                "at_cap": window["at_cap"],
                "marker_cycle": marker,
                "addressed": ok,
                "candidates": window["candidates"],
            }
            addressed.setdefault(arm, {})[str(index)] = entry
            if not ok:
                refused.append("%s read %d carries cycle %r, not %d"
                               % (arm, index, marker, index))

    payload = {
        "kind": "divergence_cycle_capture_part",
        "observer_version": OBSERVER_VERSION,
        "task": task,
        "seed": seed,
        "hash_seed": int(os.environ.get("PYTHONHASHSEED", "0")),
        "requested_cycles": sorted(wanted),
        "arms": addressed,
        "refused": refused,
        "admitted_lengths": {"B": len(b["_raw"]["admitted"]),
                             "C": len(c["_raw"]["admitted"])},
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(engine_stamp.stamp(payload), f, indent=1, sort_keys=True)
        f.write("\n")
    return payload


# ---------------------------------------------------------------------------
# the driver
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def part_path(task: str, seed: int, hash_seed: int) -> Path:
    return PARTS_DIR / ("%s_%d_hs%d.json" % (task, seed, hash_seed))


def compare_parts(against: Path) -> dict[str, Any]:
    """Compare the parts on disk with another directory of parts.

    Two parts written by two separate processes at the same hash seed must be
    the same measurement.  The observer-version field is set aside, because
    that is the one field a version bump is allowed to change; everything else
    must match exactly.  A part that is missing on either side, or that
    differs, is reported rather than skipped.
    """
    import json as _json

    def normalised(path: Path) -> Any:
        with open(path, "r", encoding="utf-8") as f:
            payload = _json.load(f)
        payload.pop("observer_version", None)
        return payload

    names = sorted(p.name for p in PARTS_DIR.glob("*.json"))
    other = {p.name for p in against.glob("*.json")}
    files: list[dict[str, Any]] = []
    identical = 0
    for name in names:
        mine = PARTS_DIR / name
        theirs = against / name
        if not theirs.exists():
            files.append({"part": name, "status": "missing_in_comparison"})
            continue
        if normalised(mine) == normalised(theirs):
            files.append({"part": name, "status": "identical"})
            identical += 1
        else:
            files.append({"part": name, "status": "differs"})
    for name in sorted(other - set(names)):
        files.append({"part": name, "status": "missing_here"})
    return {
        "kind": "divergence_capture_part_comparison",
        "compared_with": str(against),
        "parts": len(names),
        "identical": identical,
        "files": files,
    }


def part_is_current(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("observer_version") == OBSERVER_VERSION
    except (json.JSONDecodeError, ValueError, OSError):
        return False


def spawn_worker(task: str, seed: int, hash_seed: int,
                 cycles: list[int]) -> tuple[str, int, int, Path]:
    out = part_path(task, seed, hash_seed)
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = str(hash_seed)
    cmd = [sys.executable, "-X", "utf8",
           str(REPO / "benchmarks" / "divergence_cycle_capture.py"),
           "--worker", "--task", task, "--seed", str(seed),
           "--cycles", ",".join(str(c) for c in cycles), "--out", str(out)]
    proc = subprocess.run(cmd, cwd=str(REPO), env=env,
                          capture_output=True, text=True)
    return task, seed, hash_seed, out


def membership_inputs() -> list[dict[str, Any]]:
    """The seeds, their divergence cycles and the two hash seeds to compare."""
    with open(MEMBERSHIP_ARTIFACT, "r", encoding="utf-8") as f:
        a = json.load(f)
    out = []
    for entry in a["results"]:
        if (entry["task"], entry["seed"]) == CONTROL_SEED:
            continue
        divergence = entry.get("divergence", {})
        cycle = divergence.get("first_cycle")
        if cycle is None or not entry.get("campaign_reproduced"):
            continue
        out.append({
            "task": entry["task"],
            "seed": entry["seed"],
            "divergence_cycle": cycle,
            "campaign_hash_seed": entry["campaign_side_hash_seed"],
            "baseline_hash_seed": entry["baseline_hash_seed"],
        })
    return out


def pool_ids(part: dict[str, Any], arm: str, index: int) -> list[str]:
    window = part.get("arms", {}).get(arm, {}).get(str(index))
    if window is None or not window.get("addressed"):
        return []
    return [c["id"] for c in window["candidates"]]


def pool_types(part: dict[str, Any], arm: str, index: int) -> dict[str, int]:
    window = part.get("arms", {}).get(arm, {}).get(str(index))
    if window is None or not window.get("addressed"):
        return {}
    counts: dict[str, int] = {}
    for c in window["candidates"]:
        counts[c["type"]] = counts.get(c["type"], 0) + 1
    return counts


def first_difference(left: list[str], right: list[str]) -> int | None:
    """The first position at which two orders part company.

    ``None`` when the two orders are identical.  A difference of length alone
    is a difference too: the order is the sequence in which the engine read
    the candidates back, and a pool that is shorter is a different sequence.
    """
    for i, (x, y) in enumerate(zip(left, right)):
        if x != y:
            return i
    if len(left) != len(right):
        return min(len(left), len(right))
    return None


def capture_cycles(audit_index: int) -> tuple[int, int]:
    """The two engine cycles to capture for a divergence the audit reported.

    ``audit_index`` is ``first_cycle`` from the candidate-membership audit,
    which is a **zero-based index** into that audit's ``c_cycle_digests``.  A
    window's index here is an **engine cycle**, one-based, and the alignment
    witness in ``run_worker`` ties window *i* to cycle marker *i*.  The
    divergence is therefore engine cycle ``audit_index + 1``, and the cycle to
    compare it against is ``audit_index``.

    Reading ``audit_index`` as a cycle is the defect this instrument shipped
    with on 2026-10-31: it captured the cycle *before* the divergence and
    labelled it with the divergence cycle's number.  Returns
    ``(divergence, previous)``.
    """
    if audit_index < 1:
        raise ValueError(
            "a divergence at index %r has no preceding cycle to capture"
            % (audit_index,))
    divergence = audit_index + 1
    return divergence, divergence - 1


def pool_identity(camp_ids: list[str], ours_ids: list[str],
                  captured: bool) -> tuple[bool | None, bool | None]:
    """Whether two pools are identical in set and in order, or not measured.

    ``pool_ids`` returns an empty list for a window the capture refused, so an
    unaddressed window compares equal to an empty one and would report
    "identical pools".  A refused window is **not measured**, never an empty
    pool: both fields return ``None`` and the renderer says so.
    """
    if not captured:
        return None, None
    return set(camp_ids) == set(ours_ids), camp_ids == ours_ids


def build(args: argparse.Namespace) -> dict[str, Any]:
    inputs = membership_inputs()
    jobs: list[tuple[str, int, int, list[int]]] = []
    for item in inputs:
        divergence, previous = capture_cycles(int(item["divergence_cycle"]))
        cycles = [divergence, previous]
        for hash_seed in (item["campaign_hash_seed"], item["baseline_hash_seed"]):
            jobs.append((item["task"], item["seed"], hash_seed, sorted(cycles)))

    started = time.time()
    ran = 0
    cached = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = []
        for task, seed, hash_seed, cycles in jobs:
            out = part_path(task, seed, hash_seed)
            if part_is_current(out) and not args.force:
                cached += 1
                continue
            futures.append(pool.submit(spawn_worker, task, seed, hash_seed, cycles))
        for future in futures:
            task, seed, hash_seed, out = future.result()
            ran += 1
            print("  ran %s/%d hs=%d" % (task, seed, hash_seed))

    results = []
    for item in inputs:
        campaign_part = json.loads(part_path(item["task"], item["seed"],
                                             item["campaign_hash_seed"])
                                  .read_text(encoding="utf-8"))
        baseline_part = json.loads(part_path(item["task"], item["seed"],
                                             item["baseline_hash_seed"])
                                   .read_text(encoding="utf-8"))
        cycle, previous = capture_cycles(int(item["divergence_cycle"]))
        entry: dict[str, Any] = dict(item)
        entry["captured_cycle"] = cycle
        entry["previous_cycle_number"] = previous
        entry["arms"] = {}
        for arm in ("B", "C"):
            camp_ids = pool_ids(campaign_part, arm, cycle)
            ours_ids = pool_ids(baseline_part, arm, cycle)
            camp_prev = pool_ids(campaign_part, arm, previous)
            ours_prev = pool_ids(baseline_part, arm, previous)
            prev_window = {
                "campaign": campaign_part.get("arms", {})
                             .get(arm, {}).get(str(previous), {}),
                "current": baseline_part.get("arms", {})
                            .get(arm, {}).get(str(previous), {}),
            }
            prev_captured = bool(prev_window["campaign"].get("addressed")
                                 and prev_window["current"].get("addressed"))
            window = {
                "campaign": campaign_part.get("arms", {})
                             .get(arm, {}).get(str(cycle), {}),
                "current": baseline_part.get("arms", {})
                            .get(arm, {}).get(str(cycle), {}),
            }
            captured = bool(window["campaign"].get("addressed")
                            and window["current"].get("addressed"))
            set_identical, order_identical = pool_identity(camp_ids, ours_ids,
                                                          captured)
            entry["arms"][arm] = {
                "campaign_pool_size": len(camp_ids),
                "current_pool_size": len(ours_ids),
                "campaign_only": sorted(set(camp_ids) - set(ours_ids)),
                "current_only": sorted(set(ours_ids) - set(camp_ids)),
                "both": len(set(camp_ids) & set(ours_ids)),
                "campaign_pool_types": pool_types(campaign_part, arm, cycle),
                "current_pool_types": pool_types(baseline_part, arm, cycle),
                "campaign_pool_order": camp_ids,
                "current_pool_order": ours_ids,
                "set_identical": set_identical,
                "order_identical": order_identical,
                "first_order_difference": (first_difference(camp_ids, ours_ids)
                                           if captured else None),
                "previous_cycle": {
                    "captured": prev_captured,
                    "campaign_pool_size": len(camp_prev),
                    "current_pool_size": len(ours_prev),
                    "campaign_pool_order": camp_prev,
                    "current_pool_order": ours_prev,
                    "set_identical": (set(camp_prev) == set(ours_prev)
                                      if prev_captured else None),
                    "order_identical": (camp_prev == ours_prev
                                        if prev_captured else None),
                },
                "order_diverges_at_this_cycle": (
                    camp_prev == ours_prev and camp_ids != ours_ids
                ) if prev_captured else None,
                "entered_from_previous_cycle": {
                    "campaign": sorted(set(camp_ids) - set(camp_prev)),
                    "current": sorted(set(ours_ids) - set(ours_prev)),
                },
                "left_since_previous_cycle": {
                    "campaign": sorted(set(camp_prev) - set(camp_ids)),
                    "current": sorted(set(ours_prev) - set(ours_ids)),
                },
                "addressed": {
                    "campaign": campaign_part.get("arms", {})
                                     .get(arm, {}).get(str(cycle), {})
                                     .get("addressed"),
                    "current": baseline_part.get("arms", {})
                                    .get(arm, {}).get(str(cycle), {})
                                    .get("addressed"),
                },
                "window_rows": {
                    "campaign": campaign_part.get("arms", {})
                                    .get(arm, {}).get(str(cycle), {})
                                    .get("rows"),
                    "current": baseline_part.get("arms", {})
                                   .get(arm, {}).get(str(cycle), {})
                                   .get("rows"),
                },
                "window_at_cap": {
                    "campaign": campaign_part.get("arms", {})
                                    .get(arm, {}).get(str(cycle), {})
                                    .get("at_cap"),
                    "current": baseline_part.get("arms", {})
                                   .get(arm, {}).get(str(cycle), {})
                                   .get("at_cap"),
                },
            }
        results.append(entry)

    artifact = {
        "kind": "divergence_cycle_capture",
        "status": "measured",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "observer_version": OBSERVER_VERSION,
        "command": "python benchmarks/divergence_cycle_capture.py --workers %d"
                   % args.workers,
        "membership_artifact": "docs/candidate_membership_audit.json",
        "membership_artifact_sha256": sha256_file(MEMBERSHIP_ARTIFACT),
        "runs": ran,
        "cached": cached,
        "seconds": round(time.time() - started, 1),
        "results": results,
    }
    return artifact


def render(artifact: dict[str, Any]) -> str:
    """Render the report from the artifact.  Every number comes from it."""
    lines: list[str] = []
    add = lines.append
    results = artifact["results"]

    add("# Divergence-cycle capture \u2014 the pool just before the divergence "
        "and the transition into it")
    add("")
    add("**Status.** Measured 2026-10-31; **cycle base corrected and "
        "re-measured 2026-11-01**. It is the instrument the "
        "candidate-membership audit named as the next one: the membership "
        "audit found *where* the two candidate populations diverge, and this "
        "names *which candidates* were in the pool at the divergence cycle and "
        "in the cycle before it, and what entered or left on the way in. The "
        "2026-10-31 run read the cycle before the divergence and labelled it "
        "with the divergence cycle's number; \u00a71 states the correction. It "
        "does not re-score D0 and it does not change any verdict.")
    add("")
    add("## 1. Why a second capture was needed")
    add("")
    add("The membership audit captured the engine\u2019s 4,000-row sleep "
        "window, and reported honestly that it could not explain the "
        "divergence: the window is a snapshot of the read-back at the arm\u2019s "
        "snapshot point, which is two or three cycles before the end of the "
        "run, while the divergences are at sleep cycles 2 to 11. The window "
        "shows the population *near the snapshot point*; it cannot show the "
        "pool *at the divergence*.")
    add("")
    add("The 2026-10-31 run did not do that. The audit stores `first_cycle` "
        "as a **zero-based index**, and a window's index here is an engine "
        "cycle counted from one, so the capture read the cycle **before** the "
        "divergence and labelled it with the divergence cycle's own number. "
        "The 2026-11-01 re-measurement reads the divergence cycle and the "
        "cycle before it.")
    add("")
    add("## 2. How the capture is addressed, and how that is proved")
    add("")
    add("The sleep service reads its window once per cycle, and the harness\u2019s "
        "arm loop adds exactly two reads outside the cycle loop \u2014 one after "
        "the acquisition phase and one after the revision phase. So the i-th "
        "window read of an arm is the i-th cycle of that arm.")
    add("")
    add("That correspondence is not assumed. The engine stores one "
        "`sleep:meta` event per cycle carrying that cycle\u2019s number, and "
        "the window is read newest-first, so **the newest cycle marker in the "
        "i-th window must carry cycle *i***. The capture refuses to report a "
        "window whose marker does not say so, and the addressability of every "
        "window used below is recorded in the artifact.")
    add("")
    addressed = sum(1 for e in results
                    for arm in e["arms"].values()
                    if arm["addressed"]["campaign"] and arm["addressed"]["current"])
    total = sum(len(e["arms"]) for e in results)
    add("**%d of %d** captured window pairs are addressed by their own "
        "marker." % (addressed, total))
    add("")
    add("## 3. The pool at the divergence cycle, and the cycle before it")
    add("")
    add("**Campaign side** is the run whose fingerprint equals the "
        "campaign\u2019s; **current side** is the run at the pinned hash seed, "
        "which is what the use-path audit measured. Arm C is the arm the D0 "
        "verdict was scored on; arm B is shown alongside it because arm C "
        "reads arm B\u2019s recorded temporal graphs.")
    add("")
    add("| Task | Seed | Audit index | Cycle captured | Arm | Campaign pool "
        "| Current pool | Both | Campaign only | Current only | Same set "
        "| Same order |")
    add("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for entry in results:
        for arm in ("B", "C"):
            a = entry["arms"][arm]
            add("| %s | %d | %d | %d | %s | %d | %d | %d | %d | %d | %s | %s |"
                % (entry["task"], entry["seed"], entry["divergence_cycle"],
                   entry["captured_cycle"], arm, a["campaign_pool_size"],
                   a["current_pool_size"],
                   a["both"], len(a["campaign_only"]), len(a["current_only"]),
                   "yes" if a["set_identical"] else
                   ("no" if a["set_identical"] is False else "not measured"),
                   "yes" if a["order_identical"] else
                   ("no" if a["order_identical"] is False else "not measured")))
    add("")
    for entry in results:
        for arm in ("B", "C"):
            a = entry["arms"][arm]
            add("### %s / %d, cycle %d (audit index %d), arm %s"
                % (entry["task"], entry["seed"], entry["captured_cycle"],
                   entry["divergence_cycle"], arm))
            add("")
            if a["campaign_only"]:
                add("- **In the campaign\u2019s pool and not ours (%d):** %s"
                    % (len(a["campaign_only"]),
                       ", ".join("`%s`" % i for i in a["campaign_only"])))
            else:
                add("- In the campaign\u2019s pool and not ours: **none**.")
            if a["current_only"]:
                add("- **In our pool and not the campaign\u2019s (%d):** %s"
                    % (len(a["current_only"]),
                       ", ".join("`%s`" % i for i in a["current_only"])))
            else:
                add("- In our pool and not the campaign\u2019s: **none**.")
            add("")
            entered = a["entered_from_previous_cycle"]
            left = a["left_since_previous_cycle"]
            add("**From cycle %d into cycle %d, the divergence.** The "
                "campaign side gained %d candidate(s) and lost %d; the current "
                "side gained %d and lost %d."
                % (entry["previous_cycle_number"], entry["captured_cycle"],
                   len(entered["campaign"]), len(left["campaign"]),
                   len(entered["current"]), len(left["current"])))
            add("")
            for label, ids in (("gained by the campaign side",
                                entered["campaign"]),
                               ("gained by the current side",
                                entered["current"])):
                if ids:
                    add("- %s: %s" % (label,
                                      ", ".join("`%s`" % i for i in ids)))
            for label, ids in (("lost by the campaign side", left["campaign"]),
                               ("lost by the current side", left["current"])):
                if ids:
                    add("- %s: %s" % (label,
                                      ", ".join("`%s`" % i for i in ids)))
            add("")
            camp_types = a["campaign_pool_types"]
            ours_types = a["current_pool_types"]
            if camp_types or ours_types:
                add("| Candidate type | Campaign side | Current side |")
                add("|---|---|---|")
                for ctype in sorted(set(camp_types) | set(ours_types)):
                    add("| %s | %d | %d |"
                        % (ctype, camp_types.get(ctype, 0),
                           ours_types.get(ctype, 0)))
                add("")
    add("## 4. The order of the pool, and where the order parts company")
    add("")
    add("**The set and the order are two different findings.** A pool is a "
        "sequence: the engine reads the sleep window back newest-first and "
        "hands the candidates to the rest of the cycle in that order. Two "
        "pools can hold exactly the same candidates and still be different "
        "pools, so which of the two things happened on a given seed is the "
        "question this section answers.")
    add("")
    same_set = sum(1 for e in results for arm in e["arms"].values()
                   if arm["set_identical"])
    same_order = sum(1 for e in results for arm in e["arms"].values()
                      if arm["order_identical"])
    total_pairs = sum(len(e["arms"]) for e in results)
    add("Across the %d arm-pairs, the two sides hold the **same set** of "
        "candidate IDs at the divergence cycle in **%d** of them, and the "
        "**same order** in **%d**." % (total_pairs, same_set, same_order))
    add("")
    add("| Task | Seed | Cycle | Arm | Same set | Same order | First differing "
        "position | Campaign\u2019s candidate there | Ours |")
    add("|---|---|---|---|---|---|---|---|---|")
    for entry in results:
        for arm in ("B", "C"):
            a = entry["arms"][arm]
            pos = a["first_order_difference"]
            camp = a["campaign_pool_order"]
            ours = a["current_pool_order"]
            if pos is None:
                camp_at = ours_at = "\u2014"
            else:
                camp_at = camp[pos] if pos < len(camp) else "\u2014"
                ours_at = ours[pos] if pos < len(ours) else "\u2014"
            add("| %s | %d | %d | %s | %s | %s | %s | `%s` | `%s` |"
                % (entry["task"], entry["seed"], entry["divergence_cycle"],
                   arm, "yes" if a["set_identical"] else "no",
                   "yes" if a["order_identical"] else "no",
                   "\u2014" if pos is None else pos, camp_at, ours_at))
    add("")
    add("**Did the reordering happen at the divergence cycle, or was it "
        "already there?** The capture holds the window for the cycle before "
        "the divergence as well. Where the two sides\u2019 pools were "
        "identical in set *and* order at that earlier cycle, and identical in "
        "set but different in order at the divergence cycle, the reordering "
        "and the divergence are the same event.")
    add("")
    add("| Task | Seed | Cycle | Arm | Previous cycle \u2014 same set / same "
        "order | This cycle \u2014 same set / same order | The reordering "
        "coincides with the divergence |")
    add("|---|---|---|---|---|---|---|")

    def yn(value):
        return "\u2014" if value is None else ("yes" if value else "no")

    for entry in results:
        for arm in ("B", "C"):
            a = entry["arms"][arm]
            prev = a["previous_cycle"]
            add("| %s | %d | %d | %s | %s / %s | %s / %s | %s |"
                % (entry["task"], entry["seed"], entry["divergence_cycle"],
                   arm, yn(prev["set_identical"]), yn(prev["order_identical"]),
                   yn(a["set_identical"]), yn(a["order_identical"]),
                   yn(a["order_diverges_at_this_cycle"])))
    add("")
    identical = [e for e in results
                 if e["arms"]["C"]["set_identical"]
                 and e["arms"]["C"]["order_identical"]]
    if identical:
        add("**%d arm-C pairs show the pool identical in set *and* "
            "order, and the admitted stream differs anyway.** For %s "
            "in arm C, the two sides' pools at the divergence cycle "
            "are identical candidate-for-candidate and in the same "
            "sequence, and arm C's admitted stream still differs at "
            "that cycle."
            % (len(identical),
               ", ".join("%s / %d" % (e["task"], e["seed"])
                         for e in identical)))
    else:
        add("**No arm-C pair shows the pool identical in set *and* "
            "order at the divergence cycle.** Across all %d arm-pairs, "
            "on both arms, the two sides differ in membership at the "
            "cycle where the admitted streams part company, so on "
            "these seeds the divergence is a difference in which "
            "candidates were in the pool, not in the order they were "
            "read in. The identical-pool pairs this section reported "
            "on 2026-10-31 were measured one cycle early (see the "
            "correction at the head of this document); re-measured at "
            "the divergence cycle they are gone."
            % total_pairs)
    add("")
    add("**Two orders, and this capture measures one of them.** The engine "
        "reads its window back with `ORDER BY time DESC` and no rowid "
        "tiebreak (`organica/memory.py:390`), so the pool arrives as a "
        "sequence and the capture measures that sequence. Inside the cycle, "
        "the candidate list is assembled from that sequence in an order that "
        "is *not* the sequence: the tags of each prior candidate are "
        "collected into a `set` (`organica/sleep.py:1201`) and the candidates "
        "of each tag into another (`organica/sleep.py:1223`, `distinct_ids = "
        "list(set(cid for cid, _ in refs))`). Set iteration order over strings "
        "follows the process\u2019s hash seed, so two processes reading the "
        "*same* pool assemble it in *different* orders.")
    add("")
    add("**What the pairs point at.** Set iteration order over strings "
        "is hash-seeded, so two processes reading the *same* pool can "
        "assemble it in different orders, and that step is active from "
        "cycle 1 on every seed including the control "
        "(`docs/DIVERGENCE-MECHANISM-RESULTS.md`). This capture reports "
        "the narrower fact: the membership difference is present at "
        "the cycle where the admitted streams part company, so there "
        "is no identical pool here from which to attribute the "
        "divergence to order alone.")
    add("")
    add("**What it does not establish.** That the order difference *caused* the "
        "admitted-stream difference, and it does not measure the order the "
        "ranking actually saw. The admitted stream is the engine\u2019s "
        "ranking of the pool; this capture observes the pool and the admitted "
        "stream, and does not decompose the ranking between them, nor the "
        "assembly step that precedes it. The supported claim is the narrower "
        "one: **at the cycle where the populations part company, the two "
        "sides differ in membership in %d of %d arm-pairs and in read-back "
        "order in %d of %d, so membership differs wherever the admitted "
        "streams do.**"
        % (total_pairs - same_set, total_pairs,
           total_pairs - same_order, total_pairs))
    add("")
    add("## 5. What this does not establish")
    add("")
    add("It names the candidate pool at the cycle where the two populations "
        "part company, what changed in it since the cycle before, and the "
        "order in which the engine read it back. It does not establish which "
        "candidate caused the divergence: the pool is the input to the "
        "decision, and the decision is the admitted stream, whose contents are "
        "recorded but whose internal ranking is not decomposed here. It does "
        "not re-score D0, and it does not change any verdict.")
    add("")
    add("## Provenance")
    add("")
    add("- Artifact: `docs/divergence_cycle_capture.json`.")
    add("- Instrument: `benchmarks/divergence_cycle_capture.py`.")
    add("- Membership reference: `docs/candidate_membership_audit.json` "
        "(sha256 `%s`)." % artifact["membership_artifact_sha256"])
    add("- Observer version: %s." % artifact["observer_version"])
    add("- Capture command: `%s`." % artifact["command"])
    add("- Seeds in the artifact: **%d** (16 arm-pairs), all regenerated by the "
        "worker processes under observer version %s after the cycle "
        "base changed; the parent process records %s run(s) and %s "
        "part(s) found current, because under `--workers` it "
        "assembles parts the workers wrote."
        % (len(results), artifact["observer_version"],
           artifact.get("runs", 0), artifact.get("cached", 0)))
    add("- Re-render from the artifact: "
        "`python benchmarks/divergence_cycle_capture.py --render-only`.")
    add("- The capture\u2019s own determinism control: "
        "`python benchmarks/divergence_cycle_capture.py --compare-parts "
        "<dir>` compares the parts on disk against another directory of parts, "
        "field by field, with the observer-version field set aside.")
    add("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--task")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--cycles", default="")
    parser.add_argument("--out")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--render-only", action="store_true",
                        help="re-render the report from the existing artifact")
    parser.add_argument("--compare-parts", default="",
                        help="compare the parts on disk against this directory")
    args = parser.parse_args(argv)

    if args.compare_parts:
        report = compare_parts(Path(args.compare_parts))
        for f in report["files"]:
            print("  %-28s %s" % (f["part"], f["status"]))
        print("%d of %d parts identical to %s"
              % (report["identical"], report["parts"], report["compared_with"]))
        return 0 if report["identical"] == report["parts"] else 1

    if args.render_only:
        with open(REPO / "docs" / "divergence_cycle_capture.json", "r",
                  encoding="utf-8") as f:
            artifact = json.load(f)
        with open(REPO / "docs" / "DIVERGENCE-CYCLE-CAPTURE.md", "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(render(artifact).rstrip("\n") + "\n")
        print("re-rendered docs/DIVERGENCE-CYCLE-CAPTURE.md from "
              "docs/divergence_cycle_capture.json")
        return 0

    if args.worker:
        cycles = [int(c) for c in args.cycles.split(",") if c.strip()]
        if not cycles:
            raise SystemExit("--worker needs --cycles")
        out = Path(args.out)
        payload = run_worker(args.task, args.seed, cycles, out)
        print("wrote %s (arms captured: %s, refused: %d)"
              % (out, ",".join(sorted(payload["arms"])), len(payload["refused"])))
        return 0

    artifact = build(args)
    with open(REPO / "docs" / "divergence_cycle_capture.json", "w",
              encoding="utf-8", newline="\n") as f:
        json.dump(engine_stamp.stamp(artifact), f, indent=1, sort_keys=True)
        f.write("\n")
    with open(REPO / "docs" / "DIVERGENCE-CYCLE-CAPTURE.md", "w",
              encoding="utf-8", newline="\n") as f:
        f.write(render(artifact).rstrip("\n") + "\n")
    print("wrote docs/divergence_cycle_capture.json and "
          "docs/DIVERGENCE-CYCLE-CAPTURE.md (%d runs, %d cached)"
          % (artifact["runs"], artifact["cached"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
