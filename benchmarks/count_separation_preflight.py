"""Count-separation preflight for the (a)+T1 build.

**NOT A RESULT.** This module asks one build-time question: can a single co-occurrence
floor leave every committed K1 seed with a full-recall served set inside the 18-69 band
that the 0.412011 bar permits?  It draws no fresh seed, runs no campaign cell, registers
nothing, opens no database of record and writes no artifact.

The rule, fixed here before any measurement:

* The temporal path admits a pair when its temporal count reaches the engine's own
  ``PREDICTION_MIN_COUNT`` gate.  ``M`` counts unordered pairs, the unit the pair F1 and
  the 18/69 arithmetic use.
* At floor ``F >= 1`` a candidate is admitted when its co-occurrence count is at least
  ``F``; ``M_s(F)`` is the number of admitted candidates on seed ``s``.
* ``F*`` is the largest integer that keeps all eighteen gold pairs on every seed: the
  minimum gold co-occurrence count across the seeds.  If a gold pair is not on the
  temporal path, or has no co-occurrence count, no floor preserves it and the preflight
  fails before the band is read.
* PASS only when ``18 <= M_s(F*) <= 69`` on every committed seed.  Anything else is a
  FAIL, and a FAIL is a STOP: no grant, no cell.

The real measurement (``--run``) runs the 0.15.0 engine over the committed K1 world in a
scratch database, reads the temporal and co-occurrence tables at ``min_count=1``, and
prints a flushed per-seed heartbeat so a ten-seed run is visibly alive.  It has not been
run to a report: the only ``--run`` invocation was killed at 120 s before it printed
anything, and its scratch database was removed.  ``--self-test`` (synthetic fixtures) and
``smoke_test`` (one hand-built event stream, no seed) are the modes that have run.

The report carries two arithmetic diagnostics that do not change the pass rule above.
Per seed it prints the gold pairs' minimum co-occurrence count and the ``M(F)`` step
curve -- at every floor at or below ``F*``, both the admitted pair count and the
directed admitted count -- so a floor written into a grant can carry an explicit
fresh-seed margin instead of sitting exactly on the pooled minimum.  ``F*`` is the
minimum over the committed seeds, and a fresh seed can fall below it; the curve is what
makes that risk visible.  The directed count is what the engine ranks *before* it caps
at ``MAX_PREDICTIONS`` (112): when it exceeds the cap the seed is marked ``CAP BINDS``
and the headline is ``PASS OF THE BAND ONLY``, because the served set is then not ``M``.

``--run`` refuses with exit code 2 unless
``docs/constraint_decisions/DECISION-COOCCURRENCE-BUILD.json`` records the owner's choice
of allocation law ``a`` or ``b`` and term sheet ``T1`` or ``T2``.  This preflight measures
the (a)+T1 build; a record for (b) or T2 is refused as inapplicable.  The check runs
before the engine is imported or a seed is touched.

Usage::

    python -m benchmarks.count_separation_preflight --self-test   # synthetic fixtures only
    python -m benchmarks.count_separation_preflight --run          # refuses without a recorded decision
"""
from __future__ import annotations

import argparse
import json
from bisect import bisect_left
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION_RECORD = (ROOT / "docs" / "constraint_decisions"
                   / "DECISION-COOCCURRENCE-BUILD.json")
DECISION_LAW = "a"
DECISION_TERM_SHEET = "T1"

SEEDS = tuple(range(20261023, 20261033))
GOLD_PAIRS = 18
BAND_LOW = 18
BAND_HIGH = 69
TEMPORAL_MIN_COUNT = 5          # mirrors SleepService.PREDICTION_MIN_COUNT
MAX_SERVED = 112                # mirrors SleepService.MAX_PREDICTIONS
ENGINE_VERSION = "0.15.0"
CYCLES = 300
LATE_CYCLE = 150
EVENTS_PER_CYCLE = 8
HEADER = ("NOT A RESULT - count-separation preflight (build-time diagnostic; "
          "no fresh seed is drawn, no campaign cell runs, nothing is written).")

Pair = tuple[str, str]


def _pair(a: str, b: str) -> Pair:
    return (a, b) if a <= b else (b, a)


def _reach(temporal: dict[tuple[str, str], int], pair: Pair) -> int:
    """A pair's temporal count: the larger of its two directed edges."""
    a, b = pair
    return max(temporal.get((a, b), 0), temporal.get((b, a), 0))


@dataclass(frozen=True)
class SeedCounts:
    """One seed's counts.  ``temporal`` is directed; ``cooccurrence`` is unordered."""

    seed: int | str
    gold: tuple[Pair, ...]
    temporal: dict[tuple[str, str], int]
    cooccurrence: dict[Pair, int]


@dataclass(frozen=True)
class Verdict:
    """What the rule returns. ``floor`` is None when no floor preserves the gold set."""

    floor: int | None
    served: dict
    passed: bool
    reasons: tuple[str, ...]
    # seed -> (F, M, directed) breakpoints from 1 to floor; the last point is F*.
    curve: dict = field(default_factory=dict)
    gold_min: dict = field(default_factory=dict)


def measure(counts) -> Verdict:
    """Apply the fixed rule to one set of per-seed counts."""
    counts = list(counts)
    if not counts:
        raise ValueError("the preflight needs at least one seed")
    reasons: list[str] = []
    if len({seed.seed for seed in counts}) != len(counts):
        reasons.append("the seed set repeats a seed")
    for seed in counts:
        if len(set(seed.gold)) != len(seed.gold):
            reasons.append("seed %s lists a gold pair twice" % seed.seed)
        if len(set(seed.gold)) != GOLD_PAIRS:
            reasons.append("seed %s has %d gold pairs, not %d"
                           % (seed.seed, len(set(seed.gold)), GOLD_PAIRS))
        off_temporal = [pair for pair in seed.gold
                        if _reach(seed.temporal, pair) < TEMPORAL_MIN_COUNT]
        if off_temporal:
            reasons.append("seed %s: %d gold pair(s) are not on the temporal path "
                           "(temporal count below %d), starting with %r"
                           % (seed.seed, len(off_temporal), TEMPORAL_MIN_COUNT,
                              off_temporal[0]))
        off_cooc = [pair for pair in seed.gold if seed.cooccurrence.get(pair, 0) < 1]
        if off_cooc:
            reasons.append("seed %s: %d gold pair(s) have no co-occurrence count, "
                           "starting with %r" % (seed.seed, len(off_cooc), off_cooc[0]))
    if reasons:
        return Verdict(None, {}, False, tuple(reasons))

    gold_min = {seed.seed: min(seed.cooccurrence[pair] for pair in seed.gold)
                for seed in counts}
    floor = min(gold_min.values())
    served: dict = {}
    curve: dict = {}
    for seed in counts:
        pair_counts = sorted(seed.cooccurrence.get(pair, 0) for pair in {
            _pair(a, b) for (a, b), count in seed.temporal.items()
            if count >= TEMPORAL_MIN_COUNT})
        edge_counts = sorted(
            seed.cooccurrence.get(_pair(a, b), 0)
            for (a, b), count in seed.temporal.items()
            if count >= TEMPORAL_MIN_COUNT)
        served[seed.seed] = len(pair_counts) - bisect_left(pair_counts, floor)
        final_ranked = len(edge_counts) - bisect_left(edge_counts, floor)
        points = []
        previous = None
        for level in range(1, floor + 1):
            admitted = len(pair_counts) - bisect_left(pair_counts, level)
            ranked = len(edge_counts) - bisect_left(edge_counts, level)
            if (admitted, ranked) != previous:
                points.append((level, admitted, ranked))
                previous = (admitted, ranked)
        if points[-1][0] != floor:
            points.append((floor, served[seed.seed], final_ranked))
        curve[seed.seed] = tuple(points)
    for seed in sorted(served, key=str):
        if served[seed] < BAND_LOW:
            reasons.append("seed %s: M=%d is below %d" % (seed, served[seed], BAND_LOW))
        if served[seed] > BAND_HIGH:
            reasons.append("seed %s: M=%d is above %d" % (seed, served[seed], BAND_HIGH))
    return Verdict(floor, served, not reasons, tuple(reasons), curve, gold_min)


def report(verdict: Verdict, *, header: bool = True) -> str:
    """The preflight's output. The header says what it is.

    Each ``M(F)`` entry is the smallest floor at which that pair of counts holds;
    the values are constant up to the next entry, and the last entry is ``F*``.
    """
    lines = [HEADER] if header else []
    floor = "none" if verdict.floor is None else str(verdict.floor)
    lines.append("largest recall-preserving floor: %s" % floor)
    capped: list = []
    for seed in sorted(verdict.served, key=str):
        curve = verdict.curve[seed]
        directed = curve[-1][2]
        binds = directed > MAX_SERVED
        if binds:
            capped.append(seed)
        lines.append("  seed %s: M=%d, gold min=%d, directed admitted=%d/%d%s"
                     % (seed, verdict.served[seed], verdict.gold_min[seed],
                        directed, MAX_SERVED, " (CAP BINDS)" if binds else ""))
        lines.append("    M(F)/directed(F): " + "  ".join(
            "%d:%d/%d" % point for point in curve))
    if verdict.passed:
        if capped:
            lines.append("PASS OF THE BAND ONLY: 18 <= M_s(F*) <= 69 on every seed, "
                         "but the %d cap binds on seed(s) %s, so the engine "
                         "truncates before serving M; this is not a floor-only "
                         "result." % (MAX_SERVED, ", ".join(str(seed) for seed in capped)))
        else:
            lines.append("PASS: 18 <= M_s(F*) <= 69 on every seed.")
    else:
        lines.append("FAIL: " + "; ".join(verdict.reasons))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# The collection path.  ``--run`` is the only caller that uses a committed seed.
# ---------------------------------------------------------------------------

def collect_stream(events, cycles: int, gold, *, label: int | str,
                   verbose: bool = False) -> SeedCounts:
    """Run the engine over ``events`` and read the temporal and co-occurrence tables.

    No seed is required; ``label`` names the stream in reports and may be a string.
    """
    from organica.memory import MemoryService
    from organica.paths import temp_db
    from organica.sleep import SleepService

    if SleepService.PREDICTION_MIN_COUNT != TEMPORAL_MIN_COUNT:
        raise SystemExit("the engine's temporal gate is %d, not the preflight's %d"
                         % (SleepService.PREDICTION_MIN_COUNT, TEMPORAL_MIN_COUNT))
    if SleepService.MAX_PREDICTIONS != MAX_SERVED:
        raise SystemExit("the engine's prediction cap is %d, not the preflight's %d"
                         % (SleepService.MAX_PREDICTIONS, MAX_SERVED))
    if len(events) < cycles * EVENTS_PER_CYCLE:
        raise ValueError("the stream carries %d events, fewer than %d cycles x %d"
                         % (len(events), cycles, EVENTS_PER_CYCLE))

    db = temp_db("count_separation_preflight.db")
    db.unlink(missing_ok=True)
    memory = MemoryService(db_path=str(db))
    service = SleepService(memory)
    try:
        for cycle in range(cycles):
            chunk = events[cycle * EVENTS_PER_CYCLE:(cycle + 1) * EVENTS_PER_CYCLE]
            for event in chunk:
                memory.store(event, event_type="event", source="cycle:%d" % cycle)
            if chunk:
                service.run_sleep_cycle()
            if verbose and ((cycle + 1) % 50 == 0 or cycle + 1 == cycles):
                print("[preflight] seed %s: cycle %d/%d" % (label, cycle + 1, cycles),
                      flush=True)
        temporal: dict[tuple[str, str], int] = {}
        for a, b, count in memory.temporal_edges(min_count=1):
            temporal[(a, b)] = int(count)
        cooccurrence: dict[Pair, int] = {}
        for a, b, count in memory.cooccurrences(min_count=1):
            cooccurrence[_pair(a, b)] = int(count)
    finally:
        memory.close()
        db.unlink(missing_ok=True)
        try:
            db.parent.rmdir()
        except OSError:
            pass
    return SeedCounts(label, tuple(gold), temporal, cooccurrence)


def collect(seed: int, *, verbose: bool = False) -> SeedCounts:
    """Run the 0.15.0 engine over one committed K1 seed."""
    import organica
    if organica.__version__ != ENGINE_VERSION:
        raise SystemExit("the preflight is specified on the %s engine; this is %s"
                         % (ENGINE_VERSION, organica.__version__))
    from benchmarks.phase_k_campaign import (
        EVENTS_PER_CYCLE as CAMPAIGN_EVENTS, Entity, _core_entities, generate_world)

    if CAMPAIGN_EVENTS != EVENTS_PER_CYCLE:
        raise SystemExit("the K1 world emits %d events per cycle, not the preflight's %d"
                         % (CAMPAIGN_EVENTS, EVENTS_PER_CYCLE))

    features = _core_entities("k1", 3)
    entities = [
        Entity("core_a", features[0], 0, weight=3),
        Entity("core_b", features[1], 0, weight=3),
        Entity("late_c", features[2], LATE_CYCLE, weight=3),
    ]
    world = generate_world(seed, CYCLES, entities)
    gold = tuple(sorted({_pair(*pair) for group in world["gold_pairs"].values()
                         for pair in group}))
    return collect_stream(world["events"], CYCLES, gold, label=seed, verbose=verbose)


def collect_all(seeds=SEEDS) -> list[SeedCounts]:
    """The committed-seed loop. It reports per-seed progress and flushes it."""
    out: list[SeedCounts] = []
    for index, seed in enumerate(seeds, 1):
        print("[preflight] seed %s: collecting (%d/%d)" % (seed, index, len(seeds)),
              flush=True)
        counts = collect(seed, verbose=True)
        out.append(counts)
        print("[preflight] seed %s: collected (gold %d, temporal edges %d, "
              "co-occurrence %d)" % (seed, len(counts.gold), len(counts.temporal),
                                     len(counts.cooccurrence)), flush=True)
    return out


# ---------------------------------------------------------------------------
# Self-test: synthetic fixtures, no seed and no engine run.
# ---------------------------------------------------------------------------

def _fixture(seed: int, *, gold_cooc: int = 10, decoys: int = 0,
             decoy_cooc: int = 10,
             decoy_temporal: int = TEMPORAL_MIN_COUNT,
             reverse_temporal: int = 0) -> SeedCounts:
    gold = tuple(_pair("gold%02dleft" % i, "gold%02dright" % i)
                 for i in range(GOLD_PAIRS))
    temporal: dict[tuple[str, str], int] = {}
    for a, b in gold:
        temporal[(a, b)] = 10
        if reverse_temporal:
            temporal[(b, a)] = reverse_temporal
    cooccurrence = {pair: gold_cooc for pair in gold}
    for i in range(decoys):
        pair = _pair("decoy%03dleft" % i, "decoy%03dright" % i)
        temporal[pair] = decoy_temporal
        if reverse_temporal:
            temporal[(pair[1], pair[0])] = reverse_temporal
        cooccurrence[pair] = decoy_cooc
    return SeedCounts(seed, gold, temporal, cooccurrence)


def self_test() -> list[str]:
    """Prove the rule passes at its boundaries and fails where it must."""
    failures: list[str] = []

    def expect(label, verdict, passed, floor, *, reason=None):
        if verdict.passed is not passed:
            failures.append("%s: passed=%r, expected %r (%s)"
                            % (label, verdict.passed, passed,
                               "; ".join(verdict.reasons) or "no reason"))
        if floor is not None and verdict.floor != floor:
            failures.append("%s: floor=%r, expected %r" % (label, verdict.floor, floor))
        if reason is not None and not any(reason in text for text in verdict.reasons):
            failures.append("%s: no reason mentions %r" % (label, reason))

    exact = measure([_fixture(1)])
    expect("the 18-pair boundary", exact, True, 10)
    if exact.served.get(1) != BAND_LOW:
        failures.append("the 18-pair boundary: M=%r" % exact.served.get(1))

    upper = measure([_fixture(1, decoys=BAND_HIGH - GOLD_PAIRS)])
    expect("the 69-pair boundary", upper, True, 10)
    if upper.served.get(1) != BAND_HIGH:
        failures.append("the 69-pair boundary: M=%r" % upper.served.get(1))

    over = measure([_fixture(1, decoys=BAND_HIGH - GOLD_PAIRS + 1)])
    expect("70 pairs", over, False, 10, reason="above 69")

    floorless = measure([_fixture(1, gold_cooc=0)])
    expect("a gold pair with no co-occurrence", floorless, False, None,
           reason="no co-occurrence count")

    gated = measure([_fixture(1, decoys=BAND_HIGH - GOLD_PAIRS + 1,
                              decoy_temporal=TEMPORAL_MIN_COUNT - 1)])
    expect("the temporal gate", gated, True, 10)
    if gated.served.get(1) != BAND_LOW:
        failures.append("the temporal gate: M=%r (decoys were admitted)"
                        % gated.served.get(1))

    seed_a = _fixture(1, decoys=1, decoy_cooc=9)
    seed_b = _fixture(2, gold_cooc=8, decoys=1, decoy_cooc=8)
    across = measure([seed_a, seed_b])
    expect("the floor is global", across, True, 8)
    if across.served.get(1) != GOLD_PAIRS + 1:
        failures.append("the floor is global: seed 1 M=%r, expected %d"
                        % (across.served.get(1), GOLD_PAIRS + 1))

    missing = _fixture(1)
    missing.temporal.pop(missing.gold[0])
    expect("a gold pair off the temporal path", measure([missing]), False, None,
           reason="temporal path")

    duplicated = measure([_fixture(1), _fixture(1)])
    expect("a repeated seed", duplicated, False, None, reason="repeats a seed")

    margin = measure([_fixture(1, decoys=1, decoy_cooc=7)])
    expect("the floor margin", margin, True, 10)
    if margin.gold_min.get(1) != 10:
        failures.append("the floor margin: gold min=%r, expected 10"
                        % (margin.gold_min.get(1),))
    curve = margin.curve.get(1, ())
    if not curve or curve[-1][:2] != (10, GOLD_PAIRS):
        failures.append("the floor margin: the curve ends at %r, expected (10, %d)"
                        % (curve[-1:], GOLD_PAIRS))
    if (1, GOLD_PAIRS + 1, GOLD_PAIRS + 1) not in margin.curve.get(1, ()):
        failures.append("the floor margin: the curve does not show M=19 at F=1")

    capped = measure([_fixture(1, decoys=BAND_HIGH - GOLD_PAIRS,
                               reverse_temporal=10)])
    expect("the directed cap", capped, True, 10)
    if capped.curve[1][-1][2] != 2 * BAND_HIGH:
        failures.append("the directed cap: directed=%r, expected %d"
                        % (capped.curve[1][-1][2], 2 * BAND_HIGH))
    if "CAP BINDS" not in report(capped):
        failures.append("the directed cap: the report does not flag it")
    if "CAP BINDS" in report(exact):
        failures.append("the 18-pair boundary: the cap note fired without a binding cap")

    if not report(exact).startswith("NOT A RESULT"):
        failures.append("the report does not say NOT A RESULT")
    return failures


def smoke_test(verbose: bool = False) -> list[str]:
    """Exercise the collection path on a hand-built stream. No seed is used."""
    tags = ("amber", "birch", "cedar", "maple", "indigo", "willow", "yarrow")
    pairs = [_pair(a, b) for i, a in enumerate(tags) for b in tags[i + 1:]][:GOLD_PAIRS]
    events = []
    for cycle in range(18):
        for i in range(EVENTS_PER_CYCLE):
            a, b = pairs[(cycle * EVENTS_PER_CYCLE + i) % len(pairs)]
            events.append("%s %s" % (a, b))

    counts = collect_stream(events, 18, pairs, label="hand-built", verbose=verbose)
    failures: list[str] = []
    if counts.seed != "hand-built":
        failures.append("the label was not kept: %r" % (counts.seed,))
    if len(counts.gold) != GOLD_PAIRS:
        failures.append("the gold set has %d pairs, not %d"
                        % (len(counts.gold), GOLD_PAIRS))
    missing = [pair for pair in pairs
               if counts.cooccurrence.get(pair, 0) < 1
               or _reach(counts.temporal, pair) < TEMPORAL_MIN_COUNT]
    if missing:
        failures.append("the engine did not record %d gold pair(s), starting with %r"
                        % (len(missing), missing[0]))

    verdict = measure([counts])
    if verdict.floor != 8:
        failures.append("the hand-built stream's floor is %r, expected 8"
                        % (verdict.floor,))
    if not verdict.passed:
        failures.append("the hand-built stream failed: " + "; ".join(verdict.reasons))
    if verdict.served.get("hand-built") != GOLD_PAIRS:
        failures.append("M=%r, expected %d"
                        % (verdict.served.get("hand-built"), GOLD_PAIRS))
    if verdict.gold_min.get("hand-built") != 8:
        failures.append("the gold min is %r, expected 8"
                        % (verdict.gold_min.get("hand-built"),))
    curve = verdict.curve.get("hand-built", ())
    if not curve or curve[-1][:2] != (8, GOLD_PAIRS):
        failures.append("the curve ends at %r, expected (8, %d)"
                        % (curve[-1:], GOLD_PAIRS))
    directed = curve[-1][2] if curve else 0
    if not GOLD_PAIRS <= directed <= 2 * GOLD_PAIRS:
        failures.append("the directed count is %d, expected %d-%d"
                        % (directed, GOLD_PAIRS, 2 * GOLD_PAIRS))
    if not report(verdict).startswith("NOT A RESULT"):
        failures.append("the report does not say NOT A RESULT")
    return failures


# ---------------------------------------------------------------------------
# The --run gate.  A rule that must be remembered is not a check.
# ---------------------------------------------------------------------------

def decision_problems(path: Path | None = None) -> list[str]:
    """Why ``--run`` may not start.  Empty only when a recorded owner decision
    chooses the (a)+T1 build this preflight measures."""
    path = DECISION_RECORD if path is None else Path(path)
    label = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    if not path.exists():
        return ['no recorded owner decision at %s (needs kind "build_decision", '
                'decided_by "owner", an ISO date, allocation_law "a" or "b" and '
                'term_sheet "T1" or "T2")' % label]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return ["the decision record %s cannot be read: %s" % (label, exc)]
    if not isinstance(body, dict):
        return ["the decision record %s is not an object" % label]
    problems: list[str] = []
    if body.get("kind") != "build_decision":
        problems.append("%s: kind is not \"build_decision\"" % label)
    if body.get("decided_by") != "owner":
        problems.append("%s: decided_by is not \"owner\"" % label)
    try:
        date.fromisoformat(str(body.get("date", "")))
    except ValueError:
        problems.append("%s: date is not an ISO date" % label)
    law = body.get("allocation_law")
    term = body.get("term_sheet")
    if law not in ("a", "b"):
        problems.append("%s: allocation_law is %r, not \"a\" or \"b\"" % (label, law))
    if term not in ("T1", "T2"):
        problems.append("%s: term_sheet is %r, not \"T1\" or \"T2\"" % (label, term))
    if not problems and (law != DECISION_LAW or term != DECISION_TERM_SHEET):
        problems.append("%s records (%s)/%s; this preflight measures the (%s)/%s "
                        "build and does not apply"
                        % (label, law, term, DECISION_LAW, DECISION_TERM_SHEET))
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true",
                       help="synthetic fixtures only; runs no seed")
    group.add_argument("--run", action="store_true",
                       help="the preflight on the committed seeds; refuses without a "
                            "recorded decision; output is NOT A RESULT")
    args = parser.parse_args(argv)

    if args.self_test:
        failures = self_test()
        if failures:
            print("NOT A RESULT - preflight self-test (synthetic fixtures, no seed)")
            for failure in failures:
                print("FAIL: " + failure)
            return 1
        print("NOT A RESULT - preflight self-test passed on synthetic fixtures "
              "(boundaries 18 and 69, fail at 70, floorless gold set, temporal gate, "
              "global floor, repeated seed, margin curve, binding cap); no seed was run")
        return 0

    refused = decision_problems()
    if refused:
        print("REFUSED: --run needs a recorded owner decision before it can start.",
              flush=True)
        for problem in refused:
            print("REFUSED: " + problem, flush=True)
        return 2

    print(HEADER, flush=True)
    counts = collect_all()
    verdict = measure(counts)
    print(report(verdict, header=False))
    return 0 if verdict.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
