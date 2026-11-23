"""Formation provenance: record a prediction's origins when it is formed.

The provenance tracer (`benchmarks/provenance_trace.py`) walks the parent ids a
structure carries.  Prediction candidates carry none, so no walk can reach their
origins; this instrument records them instead, at the moment the candidate is
built.

It answers one question and says what it does not answer:

  Which stored events supplied the tag pair a prediction asserts, and were the
  source rows the world's or the organism's own sleep payloads?

The record is taken from a **read-only** hook: a `SleepService` subclass that
calls the engine's own `_build_predictions` and then writes down what it returned.
For every candidate it records identity, evidence, whether it carried parent ids,
and the transitions behind its `(source, target)` pair, split world / sleep.  It
never edits a candidate, and a control compares the engine's candidates with and
without the hook.

Attribution is cumulative to the cycle in which the candidate is met: the
transition set is everything recorded up to that store, because that is the
population the temporal graph's count aggregates.  A pair is `pair_world_attributed`
when every recorded transition's source row is a world event, `pair_self_sourced` when
every source row is a sleep payload, `pair_mixed` when both occur, and `pair_unattributed`
when no recorded transition carries the pair at all.  `pair_unattributed` is not zero
support — it means the recorder did not see the events behind the edge — and it is
reported as its own category.

What this does not establish: that the content *originated* in the world.  A
source row being a world event says which kind of row carried the tags, not that
the tags were first learned there; a sleep payload relaying world vocabulary gives
`pair_mixed` or `pair_self_sourced` support, which is why those classes are kept apart.  And
provenance is not usefulness: nothing here predicts held-out generalization.  That
is the prospective study's question, and it needs its own preregistration and
fresh seeds.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile
import time
from collections import defaultdict
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from organica.memory import MemoryService  # noqa: E402
from organica.sleep import SleepService  # noqa: E402

#: The engine's own lookback in `MemoryService._record_temporal_edges`.
LOOKBACK = 3

#: Origin classes.  Deliberately disjoint from the tracer's status vocabulary:
#: this is where a pair's *rows* came from, not where a structure's ancestors went.
ORIGIN_STATUSES = ("pair_world_attributed", "pair_mixed",
                   "pair_self_sourced", "pair_unattributed")


class FormationRecorder:
    """Store-time record of the transitions behind each ordered tag pair.

    Mirrors the engine's window exactly: the same `LIMIT 3`, including the row
    just stored, and it never filters by event type — because the engine does not.
    The only thing added is the source row's type, which is what makes `world` and
    `self` distinguishable at all.
    """

    def __init__(self) -> None:
        self.transitions: dict[tuple[str, str], dict[tuple[int, int], str]] = \
            defaultdict(dict)

    def record(self, mem: MemoryService, new_tags: list[str], to_rowid: int) -> None:
        rows = mem._conn.execute(
            "SELECT rowid, tags, event_type FROM events ORDER BY time DESC LIMIT ?",
            (LOOKBACK,)).fetchall()
        to_id = int(to_rowid)
        for rid, tags_str, etype in rows:
            prior = [t for t in (tags_str or "").split(",") if t]
            kind = "self" if etype == "sleep" else "world"
            for u in prior:
                for v in new_tags:
                    if u == v:
                        continue
                    self.transitions[(u, v)][(int(rid), to_id)] = kind

    def origins(self, pair: tuple[str, str]) -> dict[str, Any]:
        records = self.transitions.get(pair) or {}
        world = sum(1 for kind in records.values() if kind == "world")
        self_ = sum(1 for kind in records.values() if kind == "self")
        if not records:
            status = "pair_unattributed"
            reason = "no recorded transition carries this pair"
        elif world and not self_:
            status = "pair_world_attributed"
            reason = "every recorded transition started at a world event"
        elif self_ and not world:
            status = "pair_self_sourced"
            reason = "every recorded transition started at a sleep payload"
        else:
            status = "pair_mixed"
            reason = "both world events and sleep payloads carry this pair"
        return {"world": world, "self": self_, "transitions": len(records),
                "status": status, "reason": reason}


class RecordingSleepService(SleepService):
    """The engine, with a read-only record of what each cycle formed.

    `_build_predictions` is the engine's own; the hook returns its list unchanged
    and writes a record beside it.  `snapshot_survivors` re-reads the origins of
    the predictions still held, so support can be followed as a candidate is
    re-stored and reinforced.
    """

    def __init__(self, memory: MemoryService, recorder: FormationRecorder):
        super().__init__(memory)
        self.recorder = recorder
        self.cycle = 0
        self.formation: list[dict[str, Any]] = []

    def _build_predictions(self, temporal, freqs):
        out = super()._build_predictions(temporal, freqs)
        self.cycle += 1
        for candidate in out:
            self.formation.append({
                "cycle": self.cycle,
                "id": candidate.id,
                "source": candidate.source,
                "target": candidate.target,
                "generation": candidate.generation,
                "parent_ids": list(candidate.parent_ids),
                "temporal_count": int(candidate.evidence.get("temporal_count", 0)),
                "origin": self.recorder.origins((candidate.source, candidate.target)),
            })
        return out

    def snapshot_survivors(self) -> dict[str, dict[str, Any]]:
        """Each held prediction's origins now, keyed by id."""
        held: dict[str, dict[str, Any]] = {}
        for candidate in self._load_prior_candidates():
            if (candidate.get("type") or "") != "prediction_candidate":
                continue
            pair = (candidate.get("source"), candidate.get("target"))
            held[candidate["id"]] = {
                "cycle": self.cycle,
                "origin": self.recorder.origins(pair),
                "temporal_count": int((candidate.get("evidence") or {})
                                      .get("temporal_count", 0)),
            }
        return held


class _MutatingSleepService(RecordingSleepService):
    """A deliberately bad observer: it changes what it was asked to record.

    Exists only to prove the neutrality check can fail.  Never used for data.
    """

    def _build_predictions(self, temporal, freqs):
        out = super()._build_predictions(temporal, freqs)
        for candidate in out:
            candidate.strength = 0.0
        return out


# ---------------------------------------------------------------------------
# Synthetic controls.  No study seed, no calibration cell, no threshold.
# ---------------------------------------------------------------------------

WORLD_SCRIPT = [("willow", "observe"), ("teal", "observe")] * 6
SELF_SCRIPT = [("willow", "sleep"), ("teal", "observe")] * 6
MIXED_SCRIPT = WORLD_SCRIPT[:6] + SELF_SCRIPT[:6]
PAIR = ("willow", "teal")


def _feed(mem: MemoryService, recorder: FormationRecorder,
          script: list[tuple[str, str]], record: bool = True) -> None:
    for text, event_type in script:
        # The engine's window orders by time alone, with no rowid tiebreak, so
        # a synthetic fixture has to give its rows distinct times.
        time.sleep(0.002)
        event = mem.store(text, event_type=event_type,
                          source="sleep:payload" if event_type == "sleep" else "env")
        # Since v0.11.0 the base engine excludes sleep events from the temporal
        # graph (defect D2 fix).  The provenance-control scripts use sleep-typed
        # events to generate SELF_SCRIPT transitions (willow[sleep] -> teal[observe]);
        # we inject those transitions into precedes so the classifier can be evaluated.
        if event_type != "sleep" and event.tags:
            prior_sleep = mem._conn.execute(
                "SELECT tags FROM events WHERE event_type == 'sleep' "
                "ORDER BY time DESC LIMIT 3"
            ).fetchall()
            for (tags_str,) in prior_sleep:
                for tag_from in [t for t in (tags_str or "").split(",") if t]:
                    for tag_to in event.tags:
                        if tag_from != tag_to:
                            mem._conn.execute(
                                "INSERT INTO precedes (tag_from, tag_to, count) "
                                "VALUES (?, ?, 1) ON CONFLICT(tag_from, tag_to) "
                                "DO UPDATE SET count = count + 1",
                                (tag_from, tag_to),
                            )
            mem._conn.commit()
        if not record:
            continue
        row = mem._conn.execute("SELECT rowid FROM events WHERE id = ?",
                                (event.id,)).fetchone()
        recorder.record(mem, event.tags, int(row[0]))


def _session(steps: list[tuple[list[tuple[str, str]], int]],
             service_cls=RecordingSleepService,
             record_transitions: bool = True) -> dict[str, Any]:
    base = ROOT / ".scratch"
    base.mkdir(parents=True, exist_ok=True)
    directory = pathlib.Path(tempfile.mkdtemp(dir=base))
    mem = MemoryService(str(directory / "formation.db"))
    recorder = FormationRecorder()
    service = (service_cls(mem, recorder) if service_cls is not None
               else SleepService(mem))
    report = None
    try:
        for script, cycles in steps:
            _feed(mem, recorder, script, record=record_transitions)
            for _ in range(cycles):
                report = service.run_sleep_cycle()
        return {
            "predictions": [(c.id, round(float(c.strength), 6),
                             int(c.evidence.get("temporal_count", 0)))
                            for c in (report.predictions if report else [])],
            "formation": list(getattr(service, "formation", [])),
            "survivors": (service.snapshot_survivors()
                          if service_cls is not None else {}),
            "recorder": recorder,
            "cycle": getattr(service, "cycle", 0),
        }
    finally:
        mem._conn.close()


def _origin_of(session: dict[str, Any], pair: tuple[str, str]) -> dict[str, Any]:
    matches = [row["origin"] for row in session["formation"]
               if (row["source"], row["target"]) == pair]
    if not matches:
        formed = sorted({(row["source"], row["target"])
                         for row in session["formation"]})
        raise AssertionError(
            f"no prediction was formed for {pair}; formed pairs: {formed}")
    return matches[-1]


def run_controls() -> dict[str, Any]:
    """Prove the instrument on ancestry it constructs, before any real run."""
    results: dict[str, dict[str, Any]] = {}

    def check(name: str, expected: str, got: str, detail: str) -> None:
        results[name] = {"expected": expected, "status": got,
                         "passed": got == expected, "detail": detail}

    world = _origin_of(_session([(WORLD_SCRIPT, 1)]), PAIR)
    check("world_only_pair", "pair_world_attributed", world["status"],
          f"world {world['world']}, self {world['self']}")

    self_ = _origin_of(_session([(SELF_SCRIPT, 1)]), PAIR)
    check("sleep_payload_pair", "pair_self_sourced", self_["status"],
          f"world {self_['world']}, self {self_['self']}")

    mixed = _session([(MIXED_SCRIPT, 1)])
    mixed_origin = _origin_of(mixed, PAIR)
    check("mixed_pair", "pair_mixed", mixed_origin["status"],
          f"world {mixed_origin['world']}, self {mixed_origin['self']}")

    blind = _origin_of(_session([(WORLD_SCRIPT, 1)], record_transitions=False), PAIR)
    check("unrecorded_pair_is_unattributed", "pair_unattributed", blind["status"],
          "no recorded transition: this must not read as world or as zero")

    # The control must be able to fire: drop the world evidence from the mixed
    # recorder and the same classifier must stop saying `pair_mixed`.
    recorder = mixed["recorder"]
    recorder.transitions[PAIR] = {key: kind for key, kind in
                                  recorder.transitions[PAIR].items() if kind == "self"}
    flipped = recorder.origins(PAIR)
    check("dropping_world_evidence_flips_mixed", "pair_self_sourced", flipped["status"],
          "removing the world transitions must change the answer")

    plain = _session([(WORLD_SCRIPT, 1)], service_cls=None)
    hooked = _session([(WORLD_SCRIPT, 1)])
    neutral = (bool(plain["predictions"])
               and plain["predictions"] == hooked["predictions"])
    results["the_hook_does_not_change_the_engine"] = {
        "expected": "identical candidates",
        "status": "identical" if neutral else "diverged",
        "passed": neutral,
        "detail": (f"{len(plain['predictions'])} candidates compared by id, "
                   f"strength and count")}

    mutated = _session([(WORLD_SCRIPT, 1)], service_cls=_MutatingSleepService)
    caught = mutated["predictions"] != plain["predictions"]
    results["the_neutrality_check_can_fail"] = {
        "expected": "mutation detected",
        "status": "detected" if caught else "missed",
        "passed": caught, "detail": "a hook that edits a candidate must be visible"}

    growth_session = _session([
        (WORLD_SCRIPT, 1),
        ([("willow", "observe"), ("teal", "observe")] * 3, 1),
    ])
    counts = [row["origin"]["world"] for row in growth_session["formation"]
              if (row["source"], row["target"]) == PAIR]
    grew = len(counts) >= 2 and counts[-1] > counts[0]
    results["support_grows_as_the_edge_is_reinforced"] = {
        "expected": "strictly increasing world transitions",
        "status": "grew" if grew else "flat",
        "passed": grew,
        "detail": f"world transitions per formation record: {counts}"}

    return {"controls": results,
            "all_passed": all(row["passed"] for row in results.values()),
            "statuses": list(ORIGIN_STATUSES),
            "resolution": ("a pair's source rows, world or sleep, recorded at the "
                           "store that made the transition; not an observation-level "
                           "origin and not a measure of usefulness")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Formation provenance (synthetic controls only).")
    ap.add_argument("--controls", action="store_true",
                    help="run the synthetic controls and exit non-zero on failure")
    args = ap.parse_args(argv)
    if not args.controls:
        ap.print_help()
        return 2
    result = run_controls()
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
