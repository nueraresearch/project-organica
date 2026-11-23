"""The first V2 experiment's readout adapter: three arms on one world.

This is the consumer the charter's requirement 6(h) names, written to the
protocol in `docs/V2-FIRST-EXPERIMENT-PREREGISTRATION.md` rather than to a
result. It builds nothing inside the engine: it replays the stored world with
the frozen engine, reads the loop detections, composes them at `m = 2`, and
scores held-out next-edge log-loss for the three pre-registered arms.

    A  pair counts only
    B  content-free ids with membership frozen at admission
    C  ids with membership maintained by the 20-cycle revision rule

Nothing here decides a verdict. `--dry-run` exercises the protocol on the
declared smoke seed and writes `docs/v2_first_cell_dry_run.json`, labelled as
a dry run; the cell itself needs `DECISION-V2-FIRST-CELL` signed.

    python -m benchmarks.v2_first_cell_readout --check
    python -m benchmarks.v2_first_cell_readout --pin
    python -m benchmarks.v2_first_cell_readout --dry-run
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from benchmarks import a1_arms, a1_c5_target_timing as timing, engine_stamp  # noqa: E402
from benchmarks.acquisition_compositional import generate_compositional_world  # noqa: E402
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db  # noqa: E402
from benchmarks.heldout_prediction import _score  # noqa: E402
from organica.memory import _extract_tags  # noqa: E402
from organica.streams import EVENTS_PER_CYCLE  # noqa: E402

OUT = Path("docs/v2_first_cell_dry_run.json")
PIN = Path("docs/v2_first_cell_scorer_pin.json")
M = 2
ALPHA = 0.5
BETA_GRID = (1, 2, 4, 8)
WINDOW = 20
TRAIN_BLOCKS = 96
CALIBRATION = (80, 96)
HOLDOUT = (96, 120)
DRY_SEED = 20911101
BOOTSTRAP_SEED = 20261116
ARMS = ("A", "B", "C")


def boundaries(cycles: int) -> tuple[int, tuple[int, int], tuple[int, int], int]:
    """The declared 120-block split, scaled down for the check run only."""
    train = int(round(cycles * 0.8))
    calib = (int(round(train * 5 / 6)), train)
    window = min(WINDOW, max(2, train // 4))
    return train, calib, (train, cycles), window


def canonical(path) -> tuple[str, ...]:
    """The direction-free key: the sorted tag set, never the ordered path."""
    return tuple(sorted({tag for tag in path}))


def member_pairs(path) -> set[frozenset[str]]:
    """A loop's member edges, undirected: direction is not part of identity."""
    return {frozenset((a, b)) for a, b in zip(path, path[1:]) if a != b}


def replay(seed: int, cycles: int, stream: dict | None = None) -> dict:
    """Replay the world once and return per-event tags and per-cycle loop paths.

    `stream` overrides the generated world (`events` and `trainable`), which is
    how the null diagnostic runs a world with no temporal law through the same
    engine, the same admission and the same scorer.
    """
    world = generate_compositional_world(seed=seed, cycles=cycles) if stream is None else stream
    db_path = _make_scratch_db("v2_first_cell")
    memory = _CountingMemoryService(str(db_path))
    service = a1_arms.A1ArmSleepService(memory)
    service.MAX_PREDICTIONS = timing.CAP
    acq_lo, acq_hi = timing.PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    detections: list[tuple[int, tuple[str, ...]]] = []
    tags: list[list[str]] = []
    blocks = 0
    for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
        in_acq = event_lo <= i < event_hi
        if in_acq and not trainable:
            tags.append([])
            continue
        if i % EVENTS_PER_CYCLE == 0:
            memory.current_cycle = i // EVENTS_PER_CYCLE
        memory.store(text, event_type="observe",
                     source=a1_arms.ACQ_SOURCE if in_acq else "env")
        tags.append(list(_extract_tags(text)))
        if (i + 1) % EVENTS_PER_CYCLE:
            continue
        cycle = i // EVENTS_PER_CYCLE
        blocks += 1
        report = service.run_sleep_cycle()
        for loop in getattr(report, "loops", []) or []:
            path = tuple(getattr(loop, "path", []) or ())
            if len(set(path)) >= 2:
                detections.append((cycle, path))
    memory.close()
    return {"tags": tags, "detections": detections, "blocks": blocks}


def evolve(detections, upto: int, window: int, maintain: bool) -> tuple[dict, int]:
    """Admit composites on total appearances and return their member sets.

    Arm B (`maintain=False`) freezes the member set at the first cycle in which
    the key reaches `m`. Arm C recomputes it each cycle from a trailing window,
    adding and removing edges that cross `m` and counting every change as a
    mutation of the same id.
    """
    by_cycle: dict[int, list[tuple[str, ...]]] = collections.defaultdict(list)
    for cycle, path in detections:
        if cycle <= upto:
            by_cycle[cycle].append(path)
    members: dict[tuple[str, ...], set[frozenset[str]]] = {}
    appearances: collections.Counter = collections.Counter()
    mutations = 0
    history: list[dict[tuple[str, ...], set[frozenset[str]]]] = []
    for cycle in sorted(by_cycle):
        per_key: dict[tuple[str, ...], set[frozenset[str]]] = {}
        for path in by_cycle[cycle]:
            key = canonical(path)
            if len(key) < 2:
                continue
            per_key.setdefault(key, set()).update(member_pairs(path))
        for key in per_key:
            appearances[key] += 1
        if not maintain:
            for key, edges in per_key.items():
                if key not in members and appearances[key] >= M:
                    members[key] = set(edges)
            continue
        history.append(per_key)
        if len(history) > window:
            history.pop(0)
        edge_counts: collections.Counter = collections.Counter()
        for frame in history:
            for key, edges in frame.items():
                for edge in edges:
                    edge_counts[(key, edge)] += 1
        for key in appearances:
            if key not in members and appearances[key] < M:
                continue
            current = {edge for (k, edge), count in edge_counts.items() if k == key and count >= M}
            previous = members.get(key)
            if previous is None:
                members[key] = current
            elif current != previous:
                mutations += len(current ^ previous)
                members[key] = current
    return members, mutations


def transition_counts(tags, lo: int, hi: int) -> tuple[collections.Counter, dict[str, int], set[str]]:
    """Asserted edges over a block range, and the vocabulary seen in it."""
    counts: collections.Counter = collections.Counter()
    vocab: set[str] = set()
    start, stop = lo * EVENTS_PER_CYCLE, hi * EVENTS_PER_CYCLE
    for t in range(start, min(stop, len(tags))):
        vocab.update(tags[t])
    for t in range(start, min(stop, len(tags)) - 1):
        nxt = set(tags[t + 1])
        for u in set(tags[t]):
            for v in nxt:
                if u != v:
                    counts[(u, v)] += 1
    return counts, {u: sum(c for (a, _), c in counts.items() if a == u) for u in vocab}, vocab


def membership_counts(members: dict) -> collections.Counter:
    """How many admitted composites contain each undirected member edge."""
    counts: collections.Counter = collections.Counter()
    for edges in members.values():
        for edge in edges:
            counts[edge] += 1
    return counts


def probability(counts, totals, vocab, membership, beta: int):
    def p(source: str, target: str) -> float:
        if source not in vocab:
            return 0.0
        edge = frozenset((source, target))
        c_uv = membership.get(edge, 0) if beta else 0
        c_u = sum(c for pair, c in membership.items() if source in pair) if beta else 0
        numerator = counts.get((source, target), 0) + ALPHA + beta * c_uv
        denominator = totals.get(source, 0) + ALPHA * len(vocab) + beta * c_u
        return numerator / denominator
    return p


def score(tags, region, members, beta: int) -> dict:
    counts, totals, vocab = transition_counts(tags, 0, region[0])
    membership = membership_counts(members)
    contexts = [tags[t] for t in range(region[0] * EVENTS_PER_CYCLE,
                                       min(region[1] * EVENTS_PER_CYCLE, len(tags)) - 1)]
    observations = [tags[t + 1] for t in range(region[0] * EVENTS_PER_CYCLE,
                                              min(region[1] * EVENTS_PER_CYCLE, len(tags)) - 1)]
    return _score("arm", probability(counts, totals, vocab, membership, beta),
                  contexts, observations, vocab)


def evaluate(tags, detections, window: int, upto: int, region, beta: int, maintain: bool) -> dict:
    members, mutations = evolve(detections, upto, window, maintain)
    result = score(tags, region, members, beta)
    return {"beta": beta, "log_loss": result["log_loss"], "composites": len(members),
            "mutations": mutations, "scored": result["scored_binary_labels"]}


def select_beta(tags, detections, window: int, upto: int, calibration,
                maintain: bool) -> tuple[int, float | None]:
    """An arm's beta, chosen on the calibration band and its own earlier membership."""
    members, _ = evolve(detections, upto, window, maintain)
    best = None
    for beta in BETA_GRID:
        loss = score(tags, calibration, members, beta)["log_loss"]
        if loss is not None and (best is None or loss < best[1]):
            best = (beta, loss)
    return (best if best else (0, None))


def arms_for(tags, detections, cycles: int) -> dict:
    """Score the three arms on one replayed stream, using the declared split."""
    train, calib, holdout, window = boundaries(cycles)
    counts, totals, vocab = transition_counts(tags, 0, train)
    start, stop = holdout[0] * EVENTS_PER_CYCLE, min(holdout[1] * EVENTS_PER_CYCLE, len(tags))
    contexts = [tags[t] for t in range(start, stop - 1)]
    observations = [tags[t + 1] for t in range(start, stop - 1)]
    pure = _score("A", probability(counts, totals, vocab, collections.Counter(), 0),
                  contexts, observations, vocab)

    beta_b, calibration_b = select_beta(tags, detections, window, calib[0] - 1, calib, False)
    arm_b = evaluate(tags, detections, window, train - 1, holdout, beta_b, False)
    arm_b["calibration_log_loss"] = calibration_b
    beta_c, calibration_c = select_beta(tags, detections, window, calib[0] - 1, calib, True)
    arm_c = evaluate(tags, detections, window, train - 1, holdout, beta_c, True)
    arm_c["calibration_log_loss"] = calibration_c
    return {
        "arms": {
            "A": {"beta": None, "log_loss": pure["log_loss"], "composites": 0,
                  "mutations": 0, "scored": pure["scored_binary_labels"]},
            "B": arm_b,
            "C": arm_c,
        },
        "boundaries": {"train": train, "calibration": list(calib), "holdout": list(holdout),
                       "window": window},
    }


def paired_interval(diffs, level: float = 0.99, resamples: int = 10_000) -> dict:
    """The protocol's interval: a percentile bootstrap over seeds.

    Seeds are the unit of inference, so the resample is of the ten per-seed
    differences, not of their events. The bootstrap RNG is fixed so the
    interval is a deterministic function of the differences.
    """
    values = [float(d) for d in diffs]
    if not values:
        raise ValueError("no differences to resample")
    rng = random.Random(BOOTSTRAP_SEED)
    means = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(len(values)):
            total += values[rng.randrange(len(values))]
        means.append(total / len(values))
    means.sort()
    lo = means[int(round((1 - level) / 2 * (resamples - 1)))]
    hi = means[int(round((1 + level) / 2 * (resamples - 1)))]
    return {"mean": sum(values) / len(values), "lo": lo, "hi": hi,
            "includes_zero": lo <= 0.0 <= hi, "level": level, "resamples": resamples}


def run(seed: int, cycles: int = 120, stream: dict | None = None) -> dict:
    data = replay(seed, cycles, stream)
    scored = arms_for(data["tags"], data["detections"], cycles)
    arms = scored["arms"]
    return {
        "kind": "v2_first_cell_dry_run",
        "id": "V2-FIRST-CELL-DRY-RUN-1",
        "date": "2026-11-16",
        "status": "DRY RUN — NOT A CELL, NOT A VERDICT AND NOT SCORED AGAINST THE CHARTER",
        "seed": seed, "cycles": cycles, "blocks": data["blocks"],
        "m": M, "alpha": ALPHA, "beta_grid": list(BETA_GRID),
        "window": scored["boundaries"]["window"],
        "train_blocks": scored["boundaries"]["train"],
        "calibration": scored["boundaries"]["calibration"],
        "holdout": scored["boundaries"]["holdout"],
        "arms": arms,
        "difference_c_minus_a": (round(arms["C"]["log_loss"] - arms["A"]["log_loss"], 6)
                                 if arms["C"]["log_loss"] is not None and arms["A"]["log_loss"] is not None
                                 else None),
        "note": ("one seed, one world; a variance estimate needs the ten paired seeds. This run exists to "
                 "prove the protocol is executable end to end and that its three arms produce finite scores."),
    }


def adapter_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def pin() -> dict:
    record = json.loads(PIN.read_text(encoding="utf-8"))
    for module, digest in record["modules"].items():
        if hashlib.sha256((REPO / module).read_bytes()).hexdigest() != digest:
            raise SystemExit("pinned module changed: %s" % module)
    record["status"] = ("PINNED — THE WORLD, THE DETECTOR, THE LOG-LOSS INSTRUMENT AND THE READOUT ADAPTER ARE "
                        "FIXED; RE-PINNING IS A REVIEWED COMMIT")
    record["adapter"]["sha256"] = adapter_sha256()
    record["adapter"]["note"] = "implemented and pinned before the cell; the cell still needs the authorisation decision"
    PIN.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record


def check() -> None:
    record = json.loads(PIN.read_text(encoding="utf-8"))
    if record["adapter"]["sha256"] != adapter_sha256():
        raise SystemExit("adapter hash is stale; run --pin or restore the adapter")
    for module, digest in record["modules"].items():
        if hashlib.sha256((REPO / module).read_bytes()).hexdigest() != digest:
            raise SystemExit("pinned module changed: %s" % module)
    first = run(DRY_SEED, cycles=20)
    second = run(DRY_SEED, cycles=20)
    if first["arms"] != second["arms"]:
        raise SystemExit("readout is not deterministic across two runs of the same world")
    for arm in ARMS:
        loss = first["arms"][arm]["log_loss"]
        if loss is None or loss != loss or not isinstance(loss, float):
            raise SystemExit("arm %s produced no finite log-loss" % arm)
    if first["arms"]["C"]["beta"] not in BETA_GRID:
        raise SystemExit("arm C selected a beta outside the declared grid")
    print("check: 20-block world, arms A/B/C finite, readout deterministic, pins match")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify pins and a small deterministic run")
    parser.add_argument("--pin", action="store_true", help="record the adapter's digest in the scorer pin")
    parser.add_argument("--dry-run", action="store_true", help="run one non-reserved seed and write the record")
    args = parser.parse_args()
    if args.pin:
        record = pin()
        print("pinned adapter sha256:", record["adapter"]["sha256"])
        return 0
    if args.check:
        check()
        return 0
    if args.dry_run:
        record = run(DRY_SEED)
        record = engine_stamp.stamp(record)
        OUT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(record["arms"], indent=1))
        print("difference C-A:", record["difference_c_minus_a"])
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
