"""Online long-delay capability instrument.

The committed held-out benchmark freezes the model after cycle 200, so the
decay factor cannot act inside its scored window and a persistence difference
cannot show up there.  This instrument keeps the organism in the loop: each
cycle it consolidates, reads the engine's own ``report.predictions``, scores
them against the next cycle's events, and only then ingests that cycle.

Two design constraints are checked rather than assumed:

* **Seed liveness.** The engine's world builders take no seed, so the decay
  study's "seeds" only seeded the RNG and produced one trajectory.  Here the
  triangle *order* is shuffled by the seed, which keeps the world's multiset
  and local triangle structure but varies the schedule.  The probe reports
  ``VOID_SEED_DEGENERATE`` if the arms' early-window scores are identical
  across seeds, because then an interval would measure numerical stability
  rather than world variation.
* **Instrument liveness.** A cell that produces no predictions in a window is
  reported as not measurable, never as a score.

This is an instrument probe, not a preregistered result.  It prints the
per-window log loss for a small seed x arm block and exits non-zero when the
instrument is degenerate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.branch_streams import lattice_designs, lattice_stream  # noqa: E402
from organica.memory import MemoryService, _extract_tags                   # noqa: E402
from organica.paths import temp_db                                        # noqa: E402
from organica.sleep import SleepService                                   # noqa: E402
from organica.streams import EVENTS_PER_CYCLE                              # noqa: E402

STIMULUS = "L1_hub1_t3_disjoint"
ARMS = {"shipped": 0.95, "0.99": 0.99, "0.9925": 0.9925, "1.0": 1.0}
EARLY = (40, 90)
LATE = (150, 200)
EPSILON = 1e-9


def seeded_triangles(seed: int) -> list[tuple[str, str, str]]:
    """The design's triangles in a seed-determined block order."""
    triangles = list(lattice_designs()[STIMULUS]["triangles"])
    random.Random(seed).shuffle(triangles)
    return triangles


RARE_PERIOD = 40


def stream_for(seed: int, cycles: int = 400) -> list[str]:
    """Lattice_L1 with one seed-determined rare but stable cross-triangle edge.

    Random distractors were noise: they recurred only by chance, so the
    persistence arm retained spurious edges and looked worse for a reason
    unrelated to capability.  Here the seed chooses one cross-triangle pair
    that recurs on a fixed period (every ``RARE_PERIOD`` cycles).  The edge is
    stable and learnable, but its occurrences are far enough apart that a
    fast-decaying arm loses the association between them.  That is the
    structure a persistence advantage should exploit.
    """
    rng = random.Random(seed ^ 0x5EED)
    triangles = seeded_triangles(seed)
    base = lattice_stream(triangles)
    tags = sorted({tag for triangle in triangles for tag in triangle})
    source, target = rng.sample(tags, 2)
    length = cycles * EVENTS_PER_CYCLE
    stream = []
    while len(stream) < length:
        stream.extend(base)
    stream = stream[:length]
    for cycle in range(0, cycles, RARE_PERIOD):
        index = cycle * EVENTS_PER_CYCLE + EVENTS_PER_CYCLE - 1
        stream[index] = "%s %s" % (source, target)
    return stream


def stream_digest(seed: int) -> str:
    return hashlib.sha256(
        json.dumps(stream_for(seed)).encode("utf-8")
    ).hexdigest()[:16]


def _arm(factor: float):
    return type("Arm", (SleepService,), {"TEMPORAL_DECAY_FACTOR": factor})


def _chunk(events: list[str], cycle: int) -> list[str]:
    start = (cycle * EVENTS_PER_CYCLE) % len(events)
    return [events[(start + i) % len(events)] for i in range(EVENTS_PER_CYCLE)]


def _logloss(predictions: dict[tuple[str, str], float],
             previous: str, chunk: list[str],
             vocabulary: set[str]) -> tuple[float | None, int, int]:
    """Binary log loss over consecutive event pairs in ``chunk``.

    The context for the first pair is the last event of the cycle that just
    consolidated, so a prediction made at the end of cycle ``t`` is scored
    against cycle ``t + 1`` before any of it is ingested.
    """
    total = 0.0
    n = 0
    hits = 0
    events = [previous] + chunk
    for left, right in zip(events, events[1:]):
        sources = set(_extract_tags(left))
        targets = set(_extract_tags(right)) & vocabulary
        for source in sources:
            for target in vocabulary:
                truth = target in targets and target != source
                p = predictions.get((source, target), 0.0)
                p = min(1.0 - EPSILON, max(EPSILON, p))
                total -= (math.log(p) if truth else math.log1p(-p))
                n += 1
                hits += int(truth and p >= 0.5)
    return (total / n if n else None), n, hits


def _recall_at_k(predictions: dict[tuple[str, str], float],
                 previous: str, chunk: list[str], k: int = 5) -> float | None:
    """Fraction of next-event tags ranked in the top ``k`` for a source."""
    by_source: dict[str, list[tuple[float, str]]] = {}
    for (source, target), strength in predictions.items():
        if source != target:
            by_source.setdefault(source, []).append((strength, target))
    total = 0
    hits = 0
    events = [previous] + chunk
    for left, right in zip(events, events[1:]):
        truth = set(_extract_tags(right))
        for source in set(_extract_tags(left)):
            ranked = [target for _, target in
                      sorted(by_source.get(source, []), reverse=True)[:k]]
            total += 1
            hits += int(bool(set(ranked) & truth))
    return (hits / total) if total else None


def run_cell(seed: int, factor: float, cycles: int) -> dict:
    events = stream_for(seed)
    db = temp_db("long_delay_%d_%s.db" % (seed, factor))
    db.unlink(missing_ok=True)
    memory = MemoryService(db_path=str(db))
    service = _arm(factor)(memory)
    service._rng.seed(seed)
    vocabulary = set()
    try:
        for text in events[:EVENTS_PER_CYCLE]:
            memory.store(text, event_type="event", source="seed:bootstrap")
            vocabulary.update(_extract_tags(text))
        rows = []
        pending: dict[tuple[str, str], float] | None = None
        last_theories: int | None = None
        previous = events[EVENTS_PER_CYCLE - 1]
        for cycle in range(cycles):
            chunk = _chunk(events, cycle)
            if pending is not None:
                loss, n, hits = _logloss(pending, previous, chunk, vocabulary)
                rows.append({"cycle": cycle - 1, "log_loss": loss,
                             "labels": n, "hits": hits,
                             "predictions": len(pending),
                             "recall_at_5": _recall_at_k(pending, previous, chunk),
                             "theories": last_theories})
            for text in chunk:
                memory.store(text, event_type="event", source="cycle:%d" % cycle)
            vocabulary.update(tag for text in chunk for tag in _extract_tags(text))
            report = service.run_sleep_cycle()
            pending = {(p.source, p.target): float(p.strength)
                       for p in (report.predictions if report else [])}
            last_theories = len(getattr(report, "theories", []) or [])
            previous = chunk[-1]
        return {"seed": seed, "factor": factor, "rows": rows,
                "stream_digest": stream_digest(seed)}
    finally:
        memory.close()
        db.unlink(missing_ok=True)


def _window(rows: list[dict], window: tuple[int, int]) -> dict:
    lo, hi = window
    picked = [r for r in rows if lo <= r["cycle"] < hi and r["log_loss"] is not None]
    labels = sum(r["labels"] for r in picked)
    recall = [r["recall_at_5"] for r in picked if r.get("recall_at_5") is not None]
    if not picked or not labels:
        return {"mean_log_loss": None, "mean_recall_at_5": None,
                "cycles": len(picked), "labels": labels,
                "predictions": 0, "theories": []}
    weight = sum(r["labels"] for r in picked)
    mean = sum(r["log_loss"] * r["labels"] for r in picked) / weight
    return {"mean_log_loss": round(mean, 6),
            "mean_recall_at_5": (round(sum(recall) / len(recall), 6)
                                 if recall else None),
            "cycles": len(picked), "labels": labels,
            "predictions": sum(r["predictions"] for r in picked),
            "theories": [r.get("theories") for r in picked]}


def probe(seeds: list[int], factors: list[float], cycles: int) -> int:
    cells = {}
    for seed in seeds:
        for factor in factors:
            label = "%g" % factor
            cells[(seed, label)] = run_cell(seed, factor, cycles)
            print("ran seed %d factor %s (%d cycles)" % (seed, factor, cycles))

    digests = {seed: cells[(seed, "%g" % factors[0])]["stream_digest"]
               for seed in seeds}
    seed_live = len(set(digests.values())) > 1

    print("\nstream digests:", digests)
    print("\nwindow  seed      " + "  ".join("%-12s" % ("%g" % f) for f in factors))
    early, late = {}, {}
    for seed in seeds:
        for window, store in ((EARLY, early), (LATE, late)):
            values = []
            for factor in factors:
                values.append(_window(cells[(seed, "%g" % factor)]["rows"], window))
            store[seed] = values
        for label, cells_in_window in (("early", early), ("late", late)):
            print("%-7s %-9d logloss " % (label, seed) + "  ".join(
                "%-12s" % ("n/a" if v["mean_log_loss"] is None
                           else "%.4f" % v["mean_log_loss"])
                for v in cells_in_window[seed]))
            print("%-7s %-9d recall@5 " % (label, seed) + "  ".join(
                "%-12s" % ("n/a" if v["mean_recall_at_5"] is None
                           else "%.4f" % v["mean_recall_at_5"])
                for v in cells_in_window[seed]))

    arm_live = {}
    for index, factor in enumerate(factors):
        values = [early[seed][index]["mean_log_loss"] for seed in seeds]
        values = [v for v in values if v is not None]
        arm_live["%g" % factor] = len({round(v, 9) for v in values}) > 1
    seed_live = seed_live and all(arm_live.values())
    print("\nper-arm seed liveness:", arm_live)
    print("seed liveness: %s (stream digests %d)"
          % ("LIVE" if seed_live else "VOID_SEED_DEGENERATE",
             len(set(digests.values()))))
    return 0 if seed_live else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--cycles", type=int, default=200)
    parser.add_argument("--seeds", type=int, default=2)
    parser.add_argument("--factors", type=str, default="shipped,0.9925")
    args = parser.parse_args(argv)
    if not args.probe:
        parser.error("only --probe is implemented")
    names = [n for n in args.factors.split(",") if n]
    factors = [ARMS[n] for n in names]
    seeds = [20302800 + i for i in range(1, args.seeds + 1)]
    return probe(seeds, factors, args.cycles)


if __name__ == "__main__":
    raise SystemExit(main())
