"""benchmarks/store_time_observer.py

Name the write that admitted the candidate one pool holds and the other does not.

Planned in ``docs/STORE-TIME-OBSERVER-BRIEF.md``.  This file implements the
**core**: a passive wrapper over the substrate's admitting call, a per-cycle
reconciliation record, and the neutrality self-test that must pass before any
verdict may be read.

Cycle attribution is **witnessed, not assumed.**  The engine stores one
``sleep:meta`` event per cycle carrying that cycle's number, and the counter is
advanced *after* the cycle's candidates are written.  So the wrapper does not
use a read index and does not add one to the counter: it reads the cycle number
off the marker, and a cycle's construction writes are the ones that follow that
cycle's marker.  A construction write with no marker before it is reported
**unattributed** rather than given a guessed number.

Refusal rules, from the brief:

* ``--self-test`` must pass (the observed run reproduces the unobserved one, and
  the comparator is shown to detect a known difference);
* every cycle reported must reconcile (observed writes == accepted rows), or the
  cycle's verdict is ``indeterminate`` rather than "no write explains it".

Usage::

    python benchmarks/store_time_observer.py --self-test --cap 6
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import formation_utilization as fu          # noqa: E402
from organica.memory import MemoryService                   # noqa: E402
from benchmarks.divergence_cycle_capture import (                 # noqa: E402
    newest_marker_cycle, window_candidates)

#: Bumped when the record shape changes.  A part from another version is stale.
OBSERVER_VERSION = 2

#: Where per-run parts live between invocations.
PARTS_DIR = REPO / ".scratch" / "store_time_observer_parts"

#: The control seed, whose own cycles 10-12 hold a known membership difference.
CONTROL_SEED = ("T1", 20261101)

#: The brief fixes the search window: the divergence cycle and the one before.
SEARCH_WINDOW = 2


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def fresh_db(name: str) -> Path:
    """The harness's scratch database, named per process.  Never the live DB."""
    base = name[:-3] if name.endswith(".db") else name
    path = fu.scratch_db("%s_sto_p%d.db" % (base, os.getpid()))
    path.unlink(missing_ok=True)
    live = getattr(fu, "LIVE_DB", None)
    if live is not None and path.resolve() == Path(live).resolve():
        raise AssertionError("refusing to write to the live DB: %s" % path)
    return path


def digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def parse(content: str) -> Any:
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return None


def stage_of(source: str) -> str:
    """Whether a write is the cycle's own construction or an earlier ingest.

    The sleep service stores its candidates with a ``sleep:`` source; anything
    else is an ingest write and is therefore *upstream* of the cycle's scoring
    and construction.
    """
    return "construction" if str(source).startswith("sleep:") else "ingest"


#: The two builders that consume this cycle's tag scores (sleep.py:447-448).
#: (B-restated) is a write emitted by one of them; see brief section 9.
TAG_SCORED_LABELS = ("pool:concept_candidate", "pool:phrase_candidate")


def stack_names(limit: int = 6) -> tuple[str, ...]:
    """The engine functions on the stack at this store call, innermost first.

    Read-only introspection: it changes nothing the engine does, and it is the
    only way to tell a cycle-pool write from a survivor re-store, because both go
    through the same per-type writer and stamp the same source.
    """
    names: list[str] = []
    try:
        frame = sys._getframe(2)
    except (ValueError, AttributeError):        # pragma: no cover - no frames
        return tuple(names)
    while frame is not None and len(names) < limit:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return tuple(names)


def label_of(source: str, names: tuple[str, ...] = ()) -> str:
    """A write's label: phase from the engine's call structure, type from source.

    ``pool:<ctype>`` - admitted through ``_store_candidates``, a cycle-pool write.
    ``restore:<ctype>`` - the same writer outside it, i.e. natural selection
    re-storing a survivor (``organica/sleep.py:453-460``).
    ``marker`` - the ``sleep:meta`` cycle marker. ``ingest`` - everything else.
    """
    src = str(source)
    if not src.startswith("sleep:"):
        return "ingest"
    if src == "sleep:meta":
        return "marker"
    phase = "pool" if "_store_candidates" in names else "restore"
    return "%s:%s" % (phase, src.split(":", 1)[1])


def f5_decision(attributed: list[dict[str, Any]],
                labels_seen: list[str],
                reconciliation: dict[str, Any],
                cycles: tuple[int, ...]) -> tuple[bool, str]:
    """F5: the finer split is admissible only if it reconciles and can discriminate.

    A label scheme that returns one value everywhere is a measurement defect, not
    a fine instrument (rule 13c), so the split must show at least two distinct
    ``pool:`` labels. An attributed candidate with no label, or with two, cannot
    be read in the restated space at all.
    """
    unreconciled = [str(c) for c in cycles
                    if not (reconciliation.get(str(c)) or {}).get("reconciled")]
    if unreconciled:
        return False, ("failed: cycle(s) %s did not reconcile; observer inadmissible"
                       % ", ".join(unreconciled))
    pool_labels = sorted({l for l in labels_seen if str(l).startswith("pool:")})
    if len(pool_labels) < 2:
        return False, ("failed: the split is degenerate (%d distinct pool labels)"
                       % len(pool_labels))
    if not attributed:
        return False, "failed: no membership difference could be traced to a write"
    unlabelled = [a for a in attributed if not a.get("label")]
    if unlabelled:
        return False, ("failed: %d attributed candidate(s) carry no label"
                       % len(unlabelled))
    return True, "labelled"


def load_trace(path: Path):
    """Read a trace written by ``--trace``.

    Returns ``(header, rows)``.  ``rows`` is a generator of dicts with the digest
    table already resolved, so a later analysis reads calls as
    ``cycle, accepted, digest, id, type, stage, source`` instead of re-deriving
    the index.  The file is gzip JSONL: one header line, then one array per call.
    """
    import gzip
    handle = gzip.open(path, "rt", encoding="utf-8")
    header = json.loads(handle.readline())
    table = header.get("digests", [])
    codes = {"0": "ingest", "1": "construction"}

    def rows():
        try:
            for line in handle:
                row = json.loads(line)
                cycle, accepted, didx, stage, source = row[:5]
                label = row[5] if len(row) > 5 else None
                entry = table[didx] if 0 <= didx < len(table) else {}
                yield {
                    "cycle": cycle,
                    "accepted": accepted,
                    "digest": entry.get("digest"),
                    "id": entry.get("id"),
                    "type": entry.get("type"),
                    "stage": codes.get(str(stage), str(stage)),
                    "source": source,
                    "label": label,
                }
        finally:
            handle.close()

    return header, rows()


def reconcile(deltas: list[int]) -> dict[str, Any]:
    """One cycle's reconciliation record, from its per-call accepted deltas.

    ``observed_writes`` counts the calls the wrapper saw; ``accepted_rows`` sums
    the rows the store gained; ``net_delta`` also subtracts rows it removed.

    A cycle reconciles only when **every observed call stored exactly one row and
    nothing was removed** - ``net == accepted == observed``.  Comparing only the
    net delta against the accepted rows is not enough, and the first version of
    this function made that mistake: a call that stored nothing contributes zero
    to both sides, so ``[1, 0]`` compared equal and a write that silently did
    nothing reconciled.  A rule that cannot fire on an empty write is decoration
    (rule 25).  An unreconciled cycle makes every verdict that depends on it
    **indeterminate**; it may not be reported as "no write explains it".
    """
    observed = len(deltas)
    accepted = sum(max(0, int(d)) for d in deltas)
    net = sum(int(d) for d in deltas)
    return {
        "observed_writes": observed,
        "accepted_rows": accepted,
        "net_delta": net,
        "reconciled": bool(observed > 0 and net == accepted == observed),
    }


# ---------------------------------------------------------------------------
# the observer
# ---------------------------------------------------------------------------

def record_run(task: str, seed: int, cap: int, wrap: bool = True,
               trace: Path | None = None,
               windows_at: set[int] | None = None,
               arm_label: str = "B",
               fixed_temporal: Any = None) -> dict[str, Any]:
    """Run arm B once and return a compact record of every write.

    With ``wrap=False`` the run is unobserved; that is what the neutrality check
    compares against.  No engine file is patched on disk: two methods are
    replaced on the class for the duration of the run and restored in ``finally``.

    The record is aggregated.  A six-cycle arm issues hundreds of thousands of
    store calls, so the raw list is not kept: per cycle the wrapper keeps the
    stage counts, the per-digest first sighting (the candidate it decodes to,
    where the content is a candidate payload) and the accepted-row totals.
    """
    fu._fresh_db = fresh_db
    state: dict[str, Any] = {"marker": None, "markers": [], "unattributed": 0,
                             "reads": 0}
    per_cycle: dict[str, dict[str, Any]] = {}
    deltas: dict[str, list[int]] = {}
    # The full per-call trace, kept for later observational use: a run's database
    # is disposable, so a discarded call record cannot be recovered afterwards.
    calls: list[list[Any]] = []
    digest_table: list[dict[str, Any]] = []
    digest_index: dict[str, int] = {}
    windows: dict[int, dict[str, Any]] = {}
    totals = {"construction": 0, "ingest": 0, "accepted_rows": 0, "net_delta": 0}
    original_recent = MemoryService.recent
    original_store = MemoryService.store

    def cycle_of(stage: str, payload: Any) -> str | None:
        """The cycle a write belongs to, taken from the marker, never guessed."""
        if stage == "construction":
            if state["marker"] is None:
                state["unattributed"] += 1
                return None
            return str(state["marker"])
        # An ingest write sits between cycles; it precedes the next marker.
        if state["marker"] is None:
            return "pre-first-cycle"
        # Labelled by the cycle it precedes, so an ingest write lands inside
        # the search window of the cycle whose pool it can change.
        return "pre-%d" % (state["marker"] + 1)

    def teed_recent(self, n=50, event_type=None):
        """Witness the read-back window at the requested cycles.

        The i-th sleep read of an arm is its i-th cycle for every index before
        the harness's two trailing reads, and that is **witnessed** rather than
        assumed: the window carries the newest ``sleep:meta`` marker, and a
        window whose marker is not its own index is reported unaddressed.
        """
        events = original_recent(self, n, event_type)
        if event_type == "sleep":
            # The read index is taken before it is counted: the first sleep read
            # is index 0 and carries no marker yet, and read k carries marker k.
            # Counting first put every window one read off its own marker.
            index = state["reads"]
            state["reads"] = index + 1
            if windows_at and index in windows_at:
                rows = [{"time": e.time, "source": e.source, "content": e.content}
                        for e in events]
                marker = newest_marker_cycle(rows)
                windows[index] = {
                    "index": index,
                    "rows": len(rows),
                    "marker_cycle": marker,
                    "addressed": marker == index,
                    "candidates": window_candidates(rows),
                }
        return events

    def teed_store(self, content, event_type="observe", source="env"):
        before = self.count()
        event = original_store(self, content, event_type, source)
        after = self.count()
        accepted = int(after - before)
        stage = stage_of(source)
        label = label_of(source, stack_names())
        payload = parse(content)
        if str(source) == "sleep:meta" and isinstance(payload, dict):
            if payload.get("cycle") is not None:
                state["marker"] = int(payload["cycle"])
                state["markers"].append(int(payload["cycle"]))
        bucket = cycle_of(stage, payload)
        key = bucket if bucket is not None else "unattributed"
        d = per_cycle.setdefault(key, {"construction": 0, "ingest": 0,
                                       "labels": {}, "candidates": {}})
        d[stage] += 1
        d["labels"][label] = d["labels"].get(label, 0) + 1
        deltas.setdefault(key, []).append(accepted)
        totals[stage] += 1
        totals["accepted_rows"] += max(0, accepted)
        totals["net_delta"] += accepted
        did = digest(content)
        if did not in digest_index:
            digest_index[did] = len(digest_table)
            digest_table.append({
                "digest": did,
                "id": (str(payload.get("id"))
                       if isinstance(payload, dict) and payload.get("id") is not None
                       else None),
                "type": (str(payload.get("type"))
                         if isinstance(payload, dict) else None),
            })
        if isinstance(payload, dict) and payload.get("id") is not None:
            entry = d["candidates"].setdefault(did, {
                "id": str(payload.get("id")),
                "type": str(payload.get("type")),
                "stage": stage,
                "label": label,
            })
            entry["count"] = entry.get("count", 0) + 1
        calls.append([key, accepted, digest_index[did],
                      1 if stage == "construction" else 0, str(source), label])
        return event

    if wrap:
        MemoryService.store = teed_store
        if windows_at:
            MemoryService.recent = teed_recent
    try:
        prep = fu.prepare_world(task, seed)
        # Arm C is not standalone: it filters the support pairs and reads arm B's
        # per-cycle temporal graphs, exactly as the campaign runs it
        # (formation_utilization.py:1273-1277).
        admission = prep.get("support") if arm_label == "C" else None
        arm = fu.run_arm(prep, arm_label, cap, admission,
                         fixed_temporal=fixed_temporal)
    finally:
        MemoryService.store = original_store
        MemoryService.recent = original_recent

    raw = arm.get("_raw", {}) or {}
    graphs = raw.get("temporal_reads")
    comparable = {k: raw[k] for k in ("admitted", "temporal_reads") if k in raw}
    for key, d in per_cycle.items():
        d.update(reconcile(deltas.get(key, [])))

    trace_info: dict[str, Any] = {}
    if trace is not None:
        import gzip
        trace.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(trace, "wt", encoding="utf-8") as f:
            f.write(json.dumps({
                "kind": "store_time_observer_trace",
                "observer_version": OBSERVER_VERSION,
                "task": task,
                "seed": seed,
                "cap": cap,
                "fields": ["cycle", "accepted", "digest_index", "stage", "source",
                           "label"],
                "stage_codes": {"0": "ingest", "1": "construction"},
                "digests": digest_table,
            }, sort_keys=True) + "\n")
            for c in calls:
                f.write(json.dumps(c, separators=(",", ":")) + "\n")
        trace_info = {"path": str(trace), "calls": len(calls),
                      "digests": len(digest_table),
                      "bytes": trace.stat().st_size}
    return {
        "observer_version": OBSERVER_VERSION,
        "arm": arm_label,
        "graphs_captured": bool(graphs),
        "_graphs": graphs,
        "task": task,
        "seed": seed,
        "cap": cap,
        "raw_keys": sorted(raw.keys()),
        "comparable": comparable,
        "marker_cycles": state["markers"],
        "unattributed_writes": state["unattributed"],
        "per_cycle": per_cycle,
        "totals": totals,
        "trace": trace_info,
        "windows": windows,
        "reads": state["reads"],
    }


def self_test(cap: int, trace: Path | None = None) -> dict[str, Any]:
    """C2: the wrapper must not change the run, and the check must be able to fire.

    Three results are reported separately, because they answer different
    questions: **neutrality** (the observed and unobserved runs agree),
    **comparator** (the comparison can report a difference when one is injected),
    and **reconciliation** (per-cycle observed and accepted counts agree).
    """
    started = time.time()
    unobserved = record_run(*CONTROL_SEED, cap, wrap=False)
    observed = record_run(*CONTROL_SEED, cap, wrap=True, trace=trace)

    keys = ("admitted", "temporal_reads")
    measured = [k for k in keys if k in observed["comparable"]]
    missing = [k for k in keys if k not in observed["comparable"]]
    neutrality: dict[str, Any] = {"measured_fields": measured,
                                  "missing_fields": missing, "identical": None}
    if missing:
        neutrality["note"] = ("field not present in the arm payload; neutrality on "
                              "this quantity is NOT measured")
    if measured:
        neutrality["identical"] = all(
            unobserved["comparable"].get(k) == observed["comparable"].get(k)
            for k in measured)

    injected = json.loads(json.dumps(observed["comparable"]))
    if injected.get("admitted"):
        injected["admitted"] = injected["admitted"][:-1]
    else:
        injected["admitted"] = ["__injected__"]
    comparator_fires = (unobserved["comparable"] != injected
                        and unobserved["comparable"] == observed["comparable"])

    unreconciled = [c for c, d in observed["per_cycle"].items() if not d["reconciled"]]
    markers = observed["marker_cycles"]
    # The arm fixes its own length: ``cap`` is the harness's candidate cap, not a
    # cycle count.  What must hold is that the markers are a contiguous run from
    # cycle 1, so every construction write can be attributed without guessing.
    markers_ok = bool(markers) and markers == list(range(1, len(markers) + 1))

    passed = bool(neutrality["identical"] is True and not missing
                  and comparator_fires and not unreconciled
                  and observed["unattributed_writes"] == 0 and markers_ok)
    return {
        "kind": "store_time_observer_self_test",
        "observer_version": OBSERVER_VERSION,
        "cap": cap,
        "seconds": round(time.time() - started, 1),
        "neutrality": neutrality,
        "comparator_fires": comparator_fires,
        "marker_cycles": observed["marker_cycles"],
        "markers_as_expected": markers_ok,
        "unattributed_writes": observed["unattributed_writes"],
        "cycles_recorded": len(observed["per_cycle"]),
        "unreconciled_cycles": unreconciled,
        "totals": observed["totals"],
        "cycle_summary": summarise(observed["per_cycle"]),
        "trace": observed["trace"],
        "passed": passed,
    }


def summarise(per_cycle: dict[str, Any]) -> dict[str, Any]:
    """A compact view of the per-cycle record, so the output stays readable."""
    construction = {k: v["construction"] for k, v in per_cycle.items()
                    if k.isdigit()}
    ingest = {k: v["ingest"] for k, v in per_cycle.items()
              if str(k).startswith("pre-")}
    return {
        "markers": len(construction),
        "first": min((int(k) for k in construction), default=None),
        "last": max((int(k) for k in construction), default=None),
        "construction_min": min(construction.values(), default=0),
        "construction_max": max(construction.values(), default=0),
        "ingest_buckets": len(ingest),
        "ingest_per_bucket": sorted(set(ingest.values())),
        "unreconciled": [k for k, v in per_cycle.items() if not v["reconciled"]],
    }


#: The cycles the control seed is known to differ on, arm B, hash seeds 0 and 1.
KNOWN_POSITIVE_CYCLES = (10, 11, 12)


def f4_part(task: str, seed: int, hash_seed: int) -> Path:
    return PARTS_DIR / ("f4_%s_%d_hs%d.json" % (task, seed, hash_seed))


def find_offered(part: dict[str, Any], cycle: int,
                 candidate_id: str) -> dict[str, Any] | None:
    """Where a candidate id was offered to the store, inside the brief's window."""
    for c in (str(cycle), str(cycle - 1)):
        entry = (part.get("per_cycle") or {}).get(c) or {}
        for did, cand in (entry.get("candidates") or {}).items():
            if cand.get("id") == candidate_id:
                return {"cycle": c, "digest": did, "stage": cand.get("stage"),
                        "label": cand.get("label"), "type": cand.get("type"),
                        "count": cand.get("count")}
    return None


def f4_decision(attributed: list[dict[str, Any]],
                reconciliation: dict[str, Any],
                cycles: tuple[int, ...]) -> tuple[bool, str]:
    """The control's verdict, from the brief's two conditions, in order.

    **First** every affected cycle must reconcile: the calls the observer saw must
    equal the rows the store accepted, and nothing may have been removed. A cycle
    that does not reconcile makes the observer inadmissible whatever it claims to
    have attributed, because such a cycle cannot distinguish "no write explains
    it" from "the observer missed the write".

    **Second**, at least one known membership difference must be traced to a named
    write. Attribution without reconciliation is not a verdict, and reconciliation
    without attribution is not a control.
    """
    unreconciled = [str(c) for c in cycles
                    if not (reconciliation.get(str(c)) or {}).get("reconciled")]
    if unreconciled:
        return False, ("failed: cycle(s) %s did not reconcile; observer inadmissible"
                       % ", ".join(unreconciled))
    if not attributed:
        return False, "failed: no membership difference could be traced to a write"
    return True, "attributed"


def known_positive(cycles: tuple[int, ...] = KNOWN_POSITIVE_CYCLES) -> dict[str, Any]:
    """C1 / F4: explain the control seed's own known membership difference.

    The control seed at hash seeds 0 and 1 differs in membership at cycles 10-12
    on arm B.  An observer that cannot locate the write behind at least one of
    those differences is blind to the thing it was built to see, and no verdict
    may be read from it.
    """
    from concurrent.futures import ThreadPoolExecutor

    task, seed = CONTROL_SEED
    started = time.time()

    def spawn(hash_seed: int) -> Path:
        out = f4_part(task, seed, hash_seed)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.unlink(missing_ok=True)
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = str(hash_seed)
        cmd = [sys.executable, "-X", "utf8",
               str(REPO / "benchmarks" / "store_time_observer.py"),
               "--worker", "--task", task, "--seed", str(seed),
               "--cycles", ",".join(str(c) for c in cycles), "--out", str(out)]
        subprocess.run(cmd, cwd=str(REPO), env=env, capture_output=True, text=True)
        return out

    with ThreadPoolExecutor(max_workers=2) as pool:
        paths = list(pool.map(spawn, (0, 1)))
    sides = {hs: json.loads(path.read_text(encoding="utf-8"))
             for hs, path in zip((0, 1), paths)}

    per_cycle: dict[str, Any] = {}
    attributed: list[dict[str, Any]] = []
    for cycle in cycles:
        left = sides[0]["windows"].get(str(cycle))
        right = sides[1]["windows"].get(str(cycle))
        if not left or not right or not left["addressed"] or not right["addressed"]:
            per_cycle[str(cycle)] = {
                "status": "not_measured",
                "left_addressed": bool(left and left["addressed"]),
                "right_addressed": bool(right and right["addressed"]),
            }
            continue
        ids_left = {c["id"] for c in left["candidates"]}
        ids_right = {c["id"] for c in right["candidates"]}
        only = {"only_in_hs0": sorted(ids_left - ids_right),
                "only_in_hs1": sorted(ids_right - ids_left)}
        found = []
        for side_hs, other_hs, key in ((0, 1, "only_in_hs0"), (1, 0, "only_in_hs1")):
            for cid in only[key]:
                here = find_offered(sides[side_hs], cycle, cid)
                there = find_offered(sides[other_hs], cycle, cid)
                found.append({
                    "candidate": cid,
                    "present_in": "hs%d" % side_hs,
                    "offered_here": here,
                    "offered_there": there,
                    "stage": here["stage"] if here else None,
                    # The label is the F5 measurement; carry it at the top level
                    # as well, so the gate reads the same field a reader sees.
                    "label": here.get("label") if here else None,
                })
        resolved = [f for f in found if f["offered_here"] and not f["offered_there"]]
        per_cycle[str(cycle)] = {
            "status": "differ",
            "sizes": {"hs0": len(ids_left), "hs1": len(ids_right)},
            "differences": {k: len(v) for k, v in only.items()},
            "candidates": found,
            "attributed": len(resolved),
        }
        attributed.extend([{"cycle": cycle, **f} for f in resolved])

    reconciliation: dict[str, Any] = {}
    for cycle in cycles:
        sides_ok: dict[str, Any] = {}
        for hs in (0, 1):
            entry = (sides[hs].get("per_cycle") or {}).get(str(cycle)) or {}
            sides_ok["hs%d" % hs] = {k: entry.get(k) for k in
                                     ("observed_writes", "accepted_rows",
                                      "net_delta", "reconciled")}
        reconciliation[str(cycle)] = {
            "sides": sides_ok,
            "reconciled": all(bool(v.get("reconciled")) for v in sides_ok.values()),
        }

    differing = [c for c, v in per_cycle.items() if v.get("status") == "differ"]
    labels_seen: list[str] = []
    for hs in (0, 1):
        for entry in (sides[hs].get("per_cycle") or {}).values():
            labels_seen.extend(list((entry.get("labels") or {}).keys()))
    labels_seen = sorted(set(labels_seen))
    attributed_labels = sorted({a.get("label") for a in attributed if a.get("label")})
    f5_passed, f5_verdict = f5_decision(attributed, labels_seen, reconciliation, cycles)
    tag_scored = [l for l in attributed_labels if l in TAG_SCORED_LABELS]
    passed, verdict = f4_decision(attributed, reconciliation, cycles)
    result = {
        "kind": "store_time_observer_f4",
        "observer_version": OBSERVER_VERSION,
        "control": "C1 / F4 - the control seed's known cycles 10-12",
        "task": task,
        "seed": seed,
        "cycles": list(cycles),
        "seconds": round(time.time() - started, 1),
        "cycles_differing": differing,
        "diagnostics": {
            str(hs): {
                "reads": sides[hs].get("reads"),
                "marker_seen": {str(c): (sides[hs]["windows"].get(str(c)) or {})
                                .get("marker_cycle") for c in cycles},
            } for hs in (0, 1)
        },
        "attributed": attributed,
        "labels": {
            "seen": labels_seen,
            "attributed": attributed_labels,
            "tag_scored": tag_scored,
            "prediction": "pool:dream (see brief section 9)",
            "prediction_met": (attributed_labels == ["pool:dream"]),
        },
        "f5": {"passed": f5_passed, "verdict": f5_verdict},
        "per_cycle": per_cycle,
        "reconciliation": reconciliation,
        "passed": passed,
        "verdict": verdict,
    }
    Path("docs/store_time_observer_f4.json").write_text(
        json.dumps(result, indent=1, sort_keys=True, default=str) + "\n",
        encoding="utf-8")
    return result


#: The five pre-registered cells: (task, seed, arm, divergence cycle, staged arms).
VERDICT_CELLS: tuple[tuple[str, int, str, int, tuple[str, ...]], ...] = (
    ("T1", 20261125, "B", 12, ("B", "C")),
    ("T1", 20261125, "C", 12, ("B", "C")),
    ("T2", 20261120, "B", 6, ("B", "C")),
    ("T2", 20261120, "C", 6, ("B", "C")),
    ("T2", 20261121, "B", 6, ("B",)),
)

VERDICT_HASH_SEEDS = (0, 1)


def cell_part_path(task: str, seed: int, hash_seed: int) -> Path:
    return PARTS_DIR / ("cell_%s_%d_hs%d.json" % (task, seed, hash_seed))


def classify_cell(reconciled: bool, differences: int, attributed: int,
                  labels: list[str]) -> str:
    """One cell's outcome, in the pre-registered space (brief section 10).

    Reconciliation is decided first: an unreconciled cell cannot separate "no
    write explains it" from "the observer missed the write", so it is
    ``indeterminate`` whatever it might have found. A difference with no write
    behind it is ``C_accounted`` only when the writes fully reconcile; a partial
    explanation is ``indeterminate``, never "mostly explained".
    """
    if not reconciled:
        return "indeterminate"
    if differences == 0:
        return "no_difference_at_pair"
    if attributed == 0:
        return "C_accounted"
    if attributed < differences:
        return "indeterminate"
    labs = sorted({str(l) for l in labels})
    if set(labs) & set(TAG_SCORED_LABELS):
        return "B_restated"
    if labs == ["ingest"]:
        return "A"
    return "construction_other:" + "+".join(labs)


def run_cell(task: str, seed: int, hash_seed: int, cycle: int,
             arms: tuple[str, ...], cap: int) -> Path:
    """One hash seed's staged run: arm B, then arm C reading B's own graphs."""
    out = cell_part_path(task, seed, hash_seed)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)
    parts: dict[str, Any] = {}
    graphs: Any = None
    for arm in arms:
        rec = record_run(task, seed, cap, windows_at={cycle},
                         arm_label=arm, fixed_temporal=graphs)
        if arm == "B":
            graphs = rec.get("_graphs")
        rec.pop("_graphs", None)
        rec["hash_seed"] = hash_seed
        rec["requested_cycle"] = cycle
        parts[arm] = rec
    out.write_text(json.dumps({"task": task, "seed": seed,
                               "hash_seed": hash_seed, "cycle": cycle,
                               "parts": parts}, indent=1, sort_keys=True,
                              default=str) + "\n", encoding="utf-8")
    return out


def verdict_cell(task: str, seed: int, arm: str, cycle: int,
                 sides: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """Compare the two hash seeds at one cycle and name the write behind each gap."""
    win = {}
    for hs in VERDICT_HASH_SEEDS:
        part = (sides.get(hs) or {}).get("parts", {}).get(arm) or {}
        win[hs] = ((part.get("windows") or {}).get(str(cycle))
                   or (part.get("windows") or {}).get(cycle))
    left, right = win.get(0), win.get(1)
    entry: dict[str, Any] = {"task": task, "seed": seed, "arm": arm,
                             "cycle": cycle}
    if not left or not right or not left.get("addressed") or not right.get("addressed"):
        entry.update({"outcome": "indeterminate", "reason": "window not addressed",
                      "addressed": {str(hs): bool(win[hs] and win[hs].get("addressed"))
                                    for hs in VERDICT_HASH_SEEDS}})
        return entry
    ids = {0: {c["id"] for c in left["candidates"]},
           1: {c["id"] for c in right["candidates"]}}
    only = {0: sorted(ids[0] - ids[1]), 1: sorted(ids[1] - ids[0])}
    differences = len(only[0]) + len(only[1])
    found = []
    for hs, other in ((0, 1), (1, 0)):
        for cid in only[hs]:
            here = find_offered(sides[hs]["parts"][arm], cycle, cid)
            there = find_offered(sides[other]["parts"][arm], cycle, cid)
            found.append({"candidate": cid, "present_in": "hs%d" % hs,
                          "offered_here": here, "offered_there": there,
                          "label": (here or {}).get("label"),
                          "resolved": bool(here and not there)})
    resolved = [f for f in found if f["resolved"]]
    reconciled = all(
        bool((((sides.get(hs) or {}).get("parts", {}).get(arm) or {})
              .get("per_cycle", {}).get(str(cycle), {}) or {}).get("reconciled"))
        for hs in VERDICT_HASH_SEEDS)
    labels = [f["label"] for f in resolved]
    entry.update({
        "sizes": {"hs0": len(ids[0]), "hs1": len(ids[1])},
        "differences": differences,
        "attributed": len(resolved),
        "labels": sorted({str(l) for l in labels}),
        "reconciled": reconciled,
        "candidates": found,
        "outcome": classify_cell(reconciled, differences, len(resolved), labels),
    })
    return entry


def verdicts(cap: int = fu.CAP_B) -> dict[str, Any]:
    """Run the five pre-registered cells and write the verdict artifacts."""
    from concurrent.futures import ThreadPoolExecutor

    started = time.time()
    jobs = []
    for task, seed, _arm, cycle, arms in VERDICT_CELLS:
        for hs in VERDICT_HASH_SEEDS:
            jobs.append((task, seed, hs, cycle, arms))

    def spawn(job) -> Path:
        task, seed, hs, cycle, arms = job
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = str(hs)
        cmd = [sys.executable, "-X", "utf8",
               str(REPO / "benchmarks" / "store_time_observer.py"),
               "--cell", "--task", task, "--seed", str(seed),
               "--cycle", str(cycle), "--arms", ",".join(arms),
               "--out", str(cell_part_path(task, seed, hs))]
        proc = subprocess.run(cmd, cwd=str(REPO), env=env,
                              capture_output=True, text=True)
        if proc.returncode != 0:
            sys.stderr.write("cell worker failed (%s %s hs%s):\n%s\n"
                             % (task, seed, hs, proc.stderr[-2000:]))
        return cell_part_path(task, seed, hs)

    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        list(pool.map(spawn, jobs))

    sides: dict[tuple[str, int], dict[int, dict[str, Any]]] = {}
    for task, seed, _arm, _cycle, _arms in VERDICT_CELLS:
        sides.setdefault((task, seed), {})
        for hs in VERDICT_HASH_SEEDS:
            path = cell_part_path(task, seed, hs)
            if path.exists():
                sides[(task, seed)][hs] = json.loads(path.read_text(encoding="utf-8"))

    cells = [verdict_cell(task, seed, arm, cycle, sides[(task, seed)])
             for task, seed, arm, cycle, _arms in VERDICT_CELLS]
    counts: dict[str, int] = {}
    for c in cells:
        counts[c["outcome"]] = counts.get(c["outcome"], 0) + 1
    result = {
        "kind": "store_time_observer_verdicts",
        "observer_version": OBSERVER_VERSION,
        "preregistration": "docs/STORE-TIME-OBSERVER-BRIEF.md section 10",
        "hash_seeds": list(VERDICT_HASH_SEEDS),
        "cells": cells,
        "outcome_counts": counts,
        "seconds": round(time.time() - started, 1),
    }
    Path("docs/store_time_observer_verdicts.json").write_text(
        json.dumps(result, indent=1, sort_keys=True, default=str) + "\n",
        encoding="utf-8")
    Path("docs/STORE-TIME-OBSERVER-VERDICTS.md").write_text(
        render_verdicts(result), encoding="utf-8")
    return result


def render_verdicts(result: dict[str, Any]) -> str:
    """The verdict table, written from the artifact and nothing else."""
    lines = ["# The store-time observer: verdicts over the five search cases", "",
             "**Status: frozen on generation.** Written by `--verdict` from",
             "`docs/store_time_observer_verdicts.json`. Pre-registration:",
             "`docs/STORE-TIME-OBSERVER-BRIEF.md` section 10, committed before the run.", "",
             "Hash seeds " + " and ".join(str(h) for h in result["hash_seeds"]) +
             ". Arm C is run as a staged pair: arm B first, its per-cycle temporal",
             "graphs handed to C, both observed.", "",
             "| Case | Cycle | Pool sizes | Differences | Attributed | Labels | Outcome |",
             "|---|---|---|---|---|---|---|"]
    for c in result["cells"]:
        size = c.get("sizes")
        lines.append("| %s / %s / %s | %s | %s | %s | %s | %s | **%s** |" % (
            c["task"], c["seed"], c["arm"], c["cycle"],
            ("%d/%d" % (size["hs0"], size["hs1"])) if size else "not measured",
            c.get("differences", "not measured"), c.get("attributed", "0"),
            ", ".join("`%s`" % l for l in c.get("labels") or []) or "none",
            c["outcome"]))
    lines += ["", "## Outcome counts", ""]
    for outcome, n in sorted(result["outcome_counts"].items()):
        lines.append("- `%s`: %d" % (outcome, n))
    lines += ["", "## What the buckets mean", "",
              "`no_difference_at_pair` - the windows were identical at this hash-seed",
              "pair, so the cell measured nothing; it is not `C_accounted`.",
              "`C_accounted` - differences exist, no write explains them, and the",
              "writes fully reconciled. `indeterminate` - unreconciled, or only",
              "partially explained. A partial explanation is never folded into",
              "`C_accounted`.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cell", action="store_true",
                    help="run one hash seed's staged cell (arm B, then C) and write a part")
    ap.add_argument("--verdict", action="store_true",
                    help="run the five pre-registered cells and write the verdicts")
    ap.add_argument("--arms", default="B")
    ap.add_argument("--cycle", type=int, default=0)
    ap.add_argument("--worker", action="store_true",
                    help="capture one arm at this process's hash seed and write a part")
    ap.add_argument("--known-positive", action="store_true",
                    help="run C1 / F4 on the control seed and write the result")
    ap.add_argument("--task", default=CONTROL_SEED[0])
    ap.add_argument("--seed", type=int, default=CONTROL_SEED[1])
    ap.add_argument("--cycles", default="10,11,12")
    ap.add_argument("--out", default=None)
    ap.add_argument("--self-test", action="store_true",
                    help="run the neutrality and comparator checks and exit")
    ap.add_argument("--trace", default=None,
                    help="write the full per-call trace, gzip JSONL, to this path")
    ap.add_argument("--cap", type=int, default=fu.CAP_B,
                    help="the harness cap passed through to the arm; the arm "
                         "fixes its own cycle count, and the self-test reports it")
    args = ap.parse_args(argv)

    trace = Path(args.trace) if args.trace else None

    if args.cell:
        arms = tuple(a.strip() for a in str(args.arms).split(",") if a.strip())
        run_cell(args.task, args.seed,
                 int(os.environ.get("PYTHONHASHSEED", "0")),
                 args.cycle, arms, args.cap)
        return 0

    if args.verdict:
        result = verdicts(args.cap)
        print(json.dumps({"outcome_counts": result["outcome_counts"],
                          "seconds": result["seconds"],
                          "cells": [{k: c.get(k) for k in
                                     ("task", "seed", "arm", "cycle", "outcome")}
                                    for c in result["cells"]]},
                         indent=1, sort_keys=True))
        return 0

    if args.worker:
        cycles = tuple(int(c) for c in str(args.cycles).split(",") if c.strip())
        out = Path(args.out or PARTS_DIR / ("worker_%s_%d.json" % (args.task, args.seed)))
        out.parent.mkdir(parents=True, exist_ok=True)
        part = record_run(args.task, args.seed, args.cap,
                          trace=None, windows_at=set(cycles))
        part["hash_seed"] = int(os.environ.get("PYTHONHASHSEED", "0"))
        part["requested_cycles"] = list(cycles)
        out.write_text(json.dumps(part, indent=1, sort_keys=True, default=str) + "\n",
                       encoding="utf-8")
        print(json.dumps({"part": str(out)}, sort_keys=True))
        return 0

    if args.known_positive:
        result = known_positive()
        print(json.dumps({k: result[k] for k in
                          ("verdict", "passed", "cycles_differing", "seconds")},
                         indent=1, sort_keys=True))
        return 0 if result["passed"] else 1

    if not args.self_test:
        ap.error("choose --self-test, --known-positive or --worker")

    result = self_test(args.cap, trace=trace)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
