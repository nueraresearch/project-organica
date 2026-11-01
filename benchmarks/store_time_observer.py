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
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import formation_utilization as fu          # noqa: E402
from organica.memory import MemoryService                   # noqa: E402

#: Bumped when the record shape changes.  A part from another version is stale.
OBSERVER_VERSION = 1

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
                cycle, accepted, didx, stage, source = json.loads(line)
                entry = table[didx] if 0 <= didx < len(table) else {}
                yield {
                    "cycle": cycle,
                    "accepted": accepted,
                    "digest": entry.get("digest"),
                    "id": entry.get("id"),
                    "type": entry.get("type"),
                    "stage": codes.get(str(stage), str(stage)),
                    "source": source,
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
               trace: Path | None = None) -> dict[str, Any]:
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
    state: dict[str, Any] = {"marker": None, "markers": [], "unattributed": 0}
    per_cycle: dict[str, dict[str, Any]] = {}
    deltas: dict[str, list[int]] = {}
    # The full per-call trace, kept for later observational use: a run's database
    # is disposable, so a discarded call record cannot be recovered afterwards.
    calls: list[list[Any]] = []
    digest_table: list[dict[str, Any]] = []
    digest_index: dict[str, int] = {}
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

    def teed_store(self, content, event_type="observe", source="env"):
        before = self.count()
        event = original_store(self, content, event_type, source)
        after = self.count()
        accepted = int(after - before)
        stage = stage_of(source)
        payload = parse(content)
        if str(source) == "sleep:meta" and isinstance(payload, dict):
            if payload.get("cycle") is not None:
                state["marker"] = int(payload["cycle"])
                state["markers"].append(int(payload["cycle"]))
        bucket = cycle_of(stage, payload)
        key = bucket if bucket is not None else "unattributed"
        d = per_cycle.setdefault(key, {"construction": 0, "ingest": 0,
                                       "candidates": {}})
        d[stage] += 1
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
            })
            entry["count"] = entry.get("count", 0) + 1
        calls.append([key, accepted, digest_index[did],
                      1 if stage == "construction" else 0, str(source)])
        return event

    if wrap:
        MemoryService.store = teed_store
    try:
        prep = fu.prepare_world(task, seed)
        arm = fu.run_arm(prep, "B", cap, None)
    finally:
        MemoryService.store = original_store
        MemoryService.recent = original_recent

    raw = arm.get("_raw", {}) or {}
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
                "fields": ["cycle", "accepted", "digest_index", "stage", "source"],
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true",
                    help="run the neutrality and comparator checks and exit")
    ap.add_argument("--trace", default=None,
                    help="write the full per-call trace, gzip JSONL, to this path")
    ap.add_argument("--cap", type=int, default=fu.CAP_B,
                    help="the harness cap passed through to the arm; the arm "
                         "fixes its own cycle count, and the self-test reports it")
    args = ap.parse_args(argv)

    if not args.self_test:
        ap.error("only --self-test is implemented so far; the verdict pass is not built")

    trace = Path(args.trace) if args.trace else None
    result = self_test(args.cap, trace=trace)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
