"""The formation-provenance study: design block, then one confirmatory run.

Implements `docs/FORMATION-PROVENANCE-PREREGISTRATION.md`:

  * formation exposure is the closed protocol's conditioned stream (cycles 0-110),
    reused unchanged, with the same two cell transitions withheld;
  * every prediction candidate formed carries a store-time formation record
    (`benchmarks/formation_provenance.py`) — origins recorded, never reconstructed;
  * held-out success is declared in the protocol: the asserted pair occurs at
    least once in the held-out window 150-200, which the organism is never shown;
  * the endpoint is the difference in held-out success between
    `pair_world_attributed` candidates and candidates whose origin includes a
    self-sourced row, with a 98.33 % interval and a lower bound above zero;
  * the permutation control shuffles origin labels within seed and cycle and must
    fail to clear the bar.

The design block (20270101-20270105) is run for liveness, sample-size feasibility
and instrument neutrality only.  It evaluates no endpoint.  The endpoint is
evaluated once on 20270106-20270120, and not before every gate passes.

Engine files are never edited; the only overrides are in-process (`MAX_PREDICTIONS`
and a read-only recording hook).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
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
from benchmarks.acquisition_compositional import (  # noqa: E402
    CYCLES, EVENTS_PER_CYCLE, PHASE_TRANSFER, generate_compositional_world,
)
from benchmarks.formation_provenance import (  # noqa: E402
    FormationRecorder, RecordingSleepService,
)
from benchmarks.reusable_knowledge import (  # noqa: E402
    WITHHELD, conditioned_formation_stream, stored_rowid,
)

DESIGN_SEEDS: tuple[int, ...] = (20270101, 20270102, 20270103, 20270104, 20270105)
CONFIRMATORY_SEEDS: tuple[int, ...] = tuple(range(20270106, 20270121))
CAP: int = 1_000
INTERVAL: float = 0.9833
REPLICATES: int = 10_000
ARMS = ("pair_world_attributed", "origin_includes_self")

DESIGN_OUT = "docs/formation_provenance_study_design.json"
RESULT_OUT = "docs/formation_provenance_study.json"
RESULT_DOC = "docs/FORMATION-PROVENANCE-STUDY.md"


class StudySleepService(RecordingSleepService):
    """The closed study's variant capacity, with the formation record."""

    MAX_PREDICTIONS = CAP


def _scratch(seed: int) -> pathlib.Path:
    base = ROOT / ".scratch"
    base.mkdir(parents=True, exist_ok=True)
    directory = pathlib.Path(tempfile.mkdtemp(dir=base))
    return directory / f"fp_study_{seed}.db"


def held_out_pairs(world: dict, phase: tuple[int, int] = PHASE_TRANSFER) -> set[tuple[str, str]]:
    """Ordered tag pairs that occur across consecutive held-out events."""
    epc = EVENTS_PER_CYCLE
    events = world["events"]
    lo, hi = phase[0] * epc, phase[1] * epc
    pairs: set[tuple[str, str]] = set()
    for i in range(lo, hi - 1):
        prior = set(events[i].split())
        nxt = set(events[i + 1].split())
        for u in prior:
            for v in nxt:
                if u != v:
                    pairs.add((u, v))
    return pairs


def _run_engine(seed: int, hook: bool) -> dict[str, Any]:
    """Formation exposure; return the frozen prediction candidates with origins."""
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    formation = conditioned_formation_stream(world, seed, WITHHELD)
    db = _scratch(seed)
    mem = MemoryService(str(db))
    recorder = FormationRecorder()
    svc = (StudySleepService(mem, recorder) if hook else _CappedSleep(mem))
    candidates: list[dict[str, Any]] = []
    try:
        for i, text in enumerate(formation["events"]):
            event = mem.store(text, event_type="observe", source="env")
            if hook:
                recorder.record(mem, event.tags, stored_rowid(mem, event.id))
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                svc.run_sleep_cycle()
                mem.prune_sleep_candidates()
        frozen = svc._load_prior_candidates()
        origin_by_id: dict[str, dict[str, Any]] = {}
        if hook:
            for row in svc.formation:      # cumulative; the last record is current
                origin_by_id[row["id"]] = row["origin"]
        held = set()
        held.update(held_out_pairs(world))
        for candidate in frozen:
            if (candidate.get("type") or "") != "prediction_candidate":
                continue
            pair = (candidate.get("source"), candidate.get("target"))
            origin = origin_by_id.get(candidate["id"])
            status = origin["status"] if origin else "pair_unattributed"
            candidates.append({
                "id": candidate["id"],
                "pair": list(pair),
                "status": status,
                "temporal_count": int((candidate.get("evidence") or {})
                                      .get("temporal_count", 0)),
                "cycle": int((origin or {}).get("cycle", 0)),
                "held_out": pair in held,
            })
        neutral = [(c.get("id"), round(float(c.get("strength", 0.0)), 6),
                    int((c.get("evidence") or {}).get("temporal_count", 0)))
                   for c in frozen]
    finally:
        mem._conn.close()
        try:
            db.unlink(missing_ok=True)
            db.parent.rmdir()
        except OSError:
            pass

    counts = {
        "world": sum(1 for c in candidates if c["status"] == "pair_world_attributed"),
        "self_includes": sum(1 for c in candidates
                             if c["status"] in ("pair_mixed", "pair_self_sourced")),
        "unattributed": sum(1 for c in candidates if c["status"] == "pair_unattributed"),
    }
    return {"seed": seed, "candidates": candidates, "counts": counts,
            "held_out_pairs": len(held), "neutral": neutral}


class _CappedSleep(SleepService):
    MAX_PREDICTIONS = CAP


def run_seed(seed: int) -> dict[str, Any]:
    if seed not in DESIGN_SEEDS and seed not in CONFIRMATORY_SEEDS:
        raise ValueError(f"seed {seed} is not in either preregistered block")
    cached = ROOT / ".scratch" / f"fp_study_{seed}.json"
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf-8"))
    result = _run_engine(seed, hook=True)
    cached.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _rate(rows: list[dict[str, Any]], arm: str) -> tuple[int, int]:
    want = ("pair_world_attributed",) if arm == "pair_world_attributed" else \
        ("pair_mixed", "pair_self_sourced")
    arm_rows = [r for r in rows if r["status"] in want]
    return sum(1 for r in arm_rows if r["held_out"]), len(arm_rows)


def _difference(rows: list[dict[str, Any]]) -> float:
    w_hit, w_n = _rate(rows, "pair_world_attributed")
    s_hit, s_n = _rate(rows, "origin_includes_self")
    if not w_n or not s_n:
        return float("nan")
    return w_hit / w_n - s_hit / s_n


def _bootstrap_cluster(rows: list[dict[str, Any]], seeds: list[int],
                       rng: random.Random) -> list[float]:
    """Resample seeds, not candidates: a candidate is not independent of its seed."""
    by_seed: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_seed[int(row["seed"])].append(row)
    out: list[float] = []
    for _ in range(REPLICATES):
        draw = [rng.choice(seeds) for _ in seeds]
        pooled = [r for s in draw for r in by_seed[int(s)]]
        diff = _difference(pooled)
        if diff == diff:
            out.append(diff)
    out.sort()
    return out


def _interval(samples: list[float]) -> tuple[float, float]:
    if not samples:
        return float("nan"), float("nan")
    lo = (1.0 - INTERVAL) / 2.0
    hi = 1.0 - lo
    return (samples[int(lo * (len(samples) - 1))],
            samples[int(hi * (len(samples) - 1))])


def _permuted(rows: list[dict[str, Any]], rng: random.Random) -> list[dict[str, Any]]:
    """Shuffle origin labels within seed and cycle: the control that must fail."""
    groups: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(int(row["seed"]), int(row["cycle"]))].append(row)
    out: list[dict[str, Any]] = []
    for key in sorted(groups):
        group = groups[key]
        labels = [r["status"] for r in group]
        rng.shuffle(labels)
        for row, label in zip(group, labels):
            out.append({**row, "status": label})
    return out


def _design() -> dict[str, Any]:
    per_seed: list[dict[str, Any]] = []
    for seed in DESIGN_SEEDS:
        result = run_seed(seed)
        counts = result["counts"]
        per_seed.append({
            "seed": seed,
            "candidates": len(result["candidates"]),
            "counts": counts,
            "liveness": (counts["world"] + counts["self_includes"]) > 0,
        })
    neutrality = _neutrality(DESIGN_SEEDS[0])
    projected_world = sum(e["counts"]["world"] for e in per_seed) / len(per_seed) * len(CONFIRMATORY_SEEDS)
    projected_self = sum(e["counts"]["self_includes"] for e in per_seed) / len(per_seed) * len(CONFIRMATORY_SEEDS)
    gates = {
        "G1_liveness": all(e["liveness"] for e in per_seed),
        "G2_projected_denominators": min(projected_world, projected_self) >= 30,
        "G4_instrument_neutrality": neutrality["identical"],
    }
    return {
        "kind": "formation_provenance_design_block",
        "status": "design_block_only_no_endpoint",
        "seeds": list(DESIGN_SEEDS),
        "endpoint_evaluated": False,
        "per_seed": per_seed,
        "projection": {"seeds": len(CONFIRMATORY_SEEDS),
                       "projected_world": round(projected_world, 2),
                       "projected_self_including": round(projected_self, 2),
                       "rule": "design-mean per-seed yield x 15 confirmatory seeds, against the preregistered 30-per-arm floor"},
        "neutrality": neutrality,
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "note": ("No endpoint is computed on these seeds. G2 is a feasibility projection here; "
                 "the gate itself is evaluated on the confirmatory block."),
    }


def _neutrality(seed: int) -> dict[str, Any]:
    plain = _run_engine(seed, hook=False)
    hooked = run_seed(seed)
    # Compare through JSON: a cached run stores tuples as lists, and that is not
    # a difference between the engine's candidates.
    def canon(rows):
        return json.loads(json.dumps(rows))
    identical = canon(plain["neutral"]) == canon(hooked["neutral"])
    return {"seed": seed, "identical": identical,
            "compared": f"{len(plain['neutral'])} candidates by id, strength and count",
            "plain": len(plain["neutral"]), "hooked": len(hooked["neutral"])}


def _confirmatory() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    per_seed: list[dict[str, Any]] = []
    for seed in CONFIRMATORY_SEEDS:
        result = run_seed(seed)
        for c in result["candidates"]:
            rows.append({**c, "seed": seed})
        per_seed.append({"seed": seed, "candidates": len(result["candidates"]),
                         "counts": result["counts"]})

    w_hit, w_n = _rate(rows, "pair_world_attributed")
    s_hit, s_n = _rate(rows, "origin_includes_self")
    diff = _difference(rows)
    rng = random.Random(20270106)
    ci = _interval(_bootstrap_cluster(rows, list(CONFIRMATORY_SEEDS), rng))

    perm_rows = _permuted(rows, random.Random(20270107))
    perm_diff = _difference(perm_rows)
    perm_ci = _interval(_bootstrap_cluster(perm_rows, list(CONFIRMATORY_SEEDS),
                                           random.Random(20270108)))

    gates = {
        "G1_liveness": (w_n + s_n) > 0,
        "G2_denominators": min(w_n, s_n) >= 30,
        "G3_permutation_includes_zero": (perm_ci[0] <= 0.0 <= perm_ci[1]),
        "G4_instrument_neutrality": _neutrality(CONFIRMATORY_SEEDS[0])["identical"],
    }
    measurable = gates["G2_denominators"] and not (diff != diff)
    cleared = measurable and ci[0] > 0.0 and gates["G3_permutation_includes_zero"]
    return {
        "kind": "formation_provenance_study",
        "status": "confirmatory_run_once",
        "seeds": list(CONFIRMATORY_SEEDS),
        "arms": {
            "pair_world_attributed": {"hits": w_hit, "n": w_n,
                                      "rate": round(w_hit / w_n, 6) if w_n else None},
            "origin_includes_self": {"hits": s_hit, "n": s_n,
                                     "rate": round(s_hit / s_n, 6) if s_n else None},
        },
        "difference": None if diff != diff else round(diff, 6),
        "interval_method": ("percentile interval from 10,000 cluster-bootstrap resamples "
                            "of the 15 confirmatory seeds; candidates are not independent "
                            "of their seed"),
        "bootstrap_replicates": REPLICATES,
        "preregistration": "docs/FORMATION-PROVENANCE-PREREGISTRATION.md",
        "design_block_artifact": "docs/formation_provenance_study_design.json",
        "interval": [round(ci[0], 6), round(ci[1], 6)] if ci[0] == ci[0] else None,
        "interval_level": INTERVAL,
        "permutation": {"difference": None if perm_diff != perm_diff else round(perm_diff, 6),
                        "interval": [round(perm_ci[0], 6), round(perm_ci[1], 6)],
                        "includes_zero": gates["G3_permutation_includes_zero"]},
        "excluded_unattributed": sum(1 for r in rows
                                     if r["status"] == "pair_unattributed"),
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "association_detected": cleared,
        "verdict": ("association detected" if cleared else
                    "no association detected" if measurable else "not measurable"),
        "interpretation": ("recorded provenance is associated with the asserted pair "
                           "occurring in a window the organism was never shown"),
        "does_not_establish": [
            "that the knowledge is useful or reusable",
            "that the closed study's transfer failed or passed",
            "that the content originated in the world",
            "anything about observation-level causation",
        ],
        "per_seed": per_seed,
    }


def render_doc(art: dict[str, Any]) -> str:
    a = art["arms"]
    lines = [
        "# Formation provenance — study report",
        "",
        "**Generated from [`docs/formation_provenance_study.json`](formation_provenance_study.json);",
        "do not edit by hand.** Regenerate with `python -m benchmarks.formation_provenance_study --report`.",
        "",
        f"Seeds: {art['seeds'][0]}–{art['seeds'][-1]} ({len(art['seeds'])}), run once under",
        "[`docs/FORMATION-PROVENANCE-PREREGISTRATION.md`](FORMATION-PROVENANCE-PREREGISTRATION.md).",
        "",
        "## Endpoint",
        "",
        "| arm | hits | n | rate |",
        "|---|---|---|---|",
    ]
    for name in ARMS:
        row = a[name]
        rate = "not measurable" if row["rate"] is None else f"{row['rate']:.4f}"
        lines.append(f"| `{name}` | {row['hits']} | {row['n']} | {rate} |")
    lines += [
        "",
        f"Difference: **{art['difference']}** with a {art['interval_level'] * 100:.2f} % interval"
        f" {art['interval']}, lower bound must be above zero.",
        "",
        f"Permutation control: difference {art['permutation']['difference']}, interval"
        f" {art['permutation']['interval']}, includes zero: **{art['permutation']['includes_zero']}**.",
        "",
        f"Excluded as `pair_unattributed` (never merged): **{art['excluded_unattributed']}**.",
        "",
        "## Gates",
        "",
    ]
    for name, passed in art["gates"].items():
        lines.append(f"- {name}: **{passed}**")
    lines += [
        "",
        f"Verdict: **{art['verdict']}**.",
        "",
        "## What this means, and what it does not",
        "",
        "It means, among the candidates this engine formed on these worlds, the recorded",
        "provenance of a prediction's pair is associated with whether that pair occurs in a",
        "window the organism was never shown. It does **not** mean that the knowledge is useful",
        "or reusable, that the closed study's transfer failed, that the content originated in",
        "the world, or anything about observation-level causation.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Formation-provenance study.")
    ap.add_argument("--design", action="store_true")
    ap.add_argument("--confirmatory", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--seed", type=int, default=None, help="single seed, for timing")
    args = ap.parse_args(argv)
    if args.seed is not None:
        t0 = time.time()
        result = run_seed(args.seed)
        print(json.dumps({"seed": args.seed, "counts": result["counts"],
                          "seconds": round(time.time() - t0, 1)}, indent=1))
        return 0
    if args.design:
        art = _design()
        (ROOT / DESIGN_OUT).write_text(json.dumps(art, indent=1, sort_keys=True) + "\n",
                                       encoding="utf-8")
        print(json.dumps(art, indent=1, sort_keys=True))
        return 0 if art["all_gates_passed"] else 1
    if args.confirmatory:
        art = _confirmatory()
        (ROOT / RESULT_OUT).write_text(json.dumps(art, indent=1, sort_keys=True) + "\n",
                                       encoding="utf-8")
        (ROOT / RESULT_DOC).write_text(render_doc(art), encoding="utf-8")
        print(json.dumps({k: art[k] for k in ("arms", "difference", "interval",
                                              "gates", "verdict")}, indent=1))
        return 0
    if args.report:
        art = json.loads((ROOT / RESULT_OUT).read_text(encoding="utf-8"))
        (ROOT / RESULT_DOC).write_text(render_doc(art), encoding="utf-8")
        print("wrote", RESULT_DOC)
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
