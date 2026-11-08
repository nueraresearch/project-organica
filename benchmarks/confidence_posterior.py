"""Run the confidence-formula amendment pre-registered in
``docs/CONFIDENCE-POSTERIOR-PREREGISTRATION.md``.

The amendment replaces one expression:

    share      confidence = support / (support + contradiction)
    posterior  confidence = (support + alpha) / (support + contradiction + alpha + beta)

``organica/`` is **not** modified.  ``PosteriorSleep`` copies
``SleepService._form_and_test_hypotheses`` verbatim with the confidence
expression parameterised, which is the same in-process pattern every ablation in
this project uses.  With ``alpha = beta = 0`` the copy must be *identical* to
the frozen engine, and that identity is the study's control C1: if the copy
drifts, nothing downstream is readable.

Cells are written one file at a time to ``.scratch/confidence_posterior/`` so a
long grid can resume, and the assembled artifact is
``docs/confidence_posterior.json``.  The readings are computed from the cells by
``analyse`` -- they are never typed.

Usage:
    python benchmarks/confidence_posterior.py --self-test
    python benchmarks/confidence_posterior.py --workers 8 --resume
    python benchmarks/confidence_posterior.py --check
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "benchmarks"))

from organica import MemoryService, SleepService  # noqa: E402
from organica.memory import MemoryService as _MemoryService  # noqa: E402,F401
from organica.paths import temp_db  # noqa: E402
from organica.sleep import (  # noqa: E402
    HypothesisCandidate,
    _make_id,
)

import cold_start as cs  # noqa: E402
from benchmarks import engine_stamp

# ---------------------------------------------------------------------------
# Design constants -- these are the protocol's, not the run's
# ---------------------------------------------------------------------------
CYCLES = 40
ARMS = ("share", "jeffreys", "laplace")
CONTROL_ARM = "share_reimplemented"
SEEDS = list(range(700001001, 700001013))
RESERVE = (700001013, 700001024)
STREAMS = (
    "baseline",
    "no_branch",
    "cold_start",
    "cold_start_unbranched",
    "real_git_history",
    "wide_lookback",
)
ALPHA_BETA = {"share": None, "jeffreys": (0.5, 0.5), "laplace": (1.0, 1.0),
              CONTROL_ARM: (0.0, 0.0)}

CELLS_DIR = REPO / ".scratch" / "confidence_posterior"
OUT = REPO / "docs" / "confidence_posterior.json"


def confidence(support: float, contradiction: float, alpha: float, beta: float) -> float:
    """The confidence a belief earns, as the arm computes it.

    With ``alpha = beta = 0`` this is the frozen engine's expression exactly,
    including its zero-denominator case.  That equality is what C1 checks.
    """
    denominator = support + contradiction + alpha + beta
    if denominator <= 0:
        return 0.0
    return round((support + alpha) / denominator, 4)


class PosteriorSleep(SleepService):
    """The frozen engine with its confidence expression parameterised.

    Everything below the marker is copied verbatim from
    ``organica/sleep.py:1406-1531`` except the two lines that compute
    ``conf`` and the death rule, which keeps using the raw total exactly as the
    frozen engine does.
    """

    LABEL = "posterior"
    ALPHA = 0.0
    BETA = 0.0

    def _form_and_test_hypotheses(
        self,
        temporal: dict[str, dict[str, int]],
        freqs: dict[str, int],
        workflows: list,
        processes: list,
        meta_concepts: list,
        prior: list[dict],
    ) -> list[HypothesisCandidate]:
        prior_hyps = {h.get("id"): h for h in prior if h.get("type") == "hypothesis"}
        candidates: dict[str, HypothesisCandidate] = {}

        for w in workflows:
            comps = w.components
            for i in range(len(comps)):
                sub = comps[i]
                for j in range(len(comps)):
                    if i != j:
                        exp = comps[j]
                        hid = _make_id("hyp", sub, exp)
                        if hid not in candidates:
                            candidates[hid] = HypothesisCandidate(
                                id=hid, generation=3, subject=sub,
                                expectation=exp, parent_ids=[w.id],
                            )
                        else:
                            if w.id not in candidates[hid].parent_ids:
                                candidates[hid].parent_ids.append(w.id)

        for p in processes:
            cycle = p.cycle
            for i in range(len(cycle)):
                sub = cycle[i]
                exp = cycle[(i + 1) % len(cycle)]
                hid = _make_id("hyp", sub, exp)
                if hid not in candidates:
                    candidates[hid] = HypothesisCandidate(
                        id=hid, generation=3, subject=sub,
                        expectation=exp, parent_ids=[p.id],
                    )
                else:
                    if p.id not in candidates[hid].parent_ids:
                        candidates[hid].parent_ids.append(p.id)

        for m in meta_concepts:
            if m.related_candidates >= 5:
                hid = _make_id("hyp", m.anchor_tag, "high_structural_significance")
                candidates[hid] = HypothesisCandidate(
                    id=hid, generation=3, subject=m.anchor_tag,
                    expectation="high_structural_significance",
                    confidence=m.confidence,
                    support_count=m.related_candidates,
                    contradiction_count=0,
                    parent_ids=[m.id],
                    evidence={"type": "meta_centrality",
                              "related_candidates": m.related_candidates},
                )

        results = []
        for hid, hyp in candidates.items():
            if hyp.expectation == "high_structural_significance":
                results.append(hyp)
                continue

            sub = hyp.subject
            exp = hyp.expectation

            targets = temporal.get(sub, {})
            support = targets.get(exp, 0)
            total_flow = sum(targets.values())
            raw_contradiction = max(0, total_flow - support)
            contradiction = raw_contradiction * self.CONTRADICTION_SCALE

            prior_h = prior_hyps.get(hid)
            prior_conf = prior_h.get("confidence") if prior_h else None

            # --- the amendment: one expression -------------------------
            conf = confidence(support, contradiction, self.ALPHA, self.BETA)

            if conf < self.DEATH_THRESHOLD and (support + contradiction) >= 3:
                continue

            hyp.confidence = conf
            hyp.support_count = support
            hyp.contradiction_count = contradiction
            hyp.evidence = {
                "support_count": support,
                "contradiction_count": contradiction,
                "raw_contradiction_count": raw_contradiction,
                "total_flow": total_flow,
                "prior_confidence": prior_conf,
                "revision_delta": round(conf - prior_conf, 4) if prior_conf is not None else 0.0,
            }
            results.append(hyp)

        markers = [h for h in results
                   if h.expectation == "high_structural_significance"]
        beliefs = [h for h in results
                   if h.expectation != "high_structural_significance"]

        info = self._belief_info(beliefs, prior_hyps, temporal)
        kept = self._retain_hypotheses(beliefs, info, temporal)
        kept_markers = self._retain_markers(markers, info)
        return kept + kept_markers


def sleep_class(arm: str):
    """The class a cell runs, for the arm name it is filed under."""
    if arm == "share":
        return SleepService
    alpha, beta = ALPHA_BETA[arm]
    return type(f"Posterior_{arm}", (PosteriorSleep,),
                {"ALPHA": alpha, "BETA": beta, "LABEL": arm})


# ---------------------------------------------------------------------------
# One cell
# ---------------------------------------------------------------------------
def stream_spec(name: str, git_events: list[str]) -> dict:
    """The cold-start condition's stream, exactly as that study runs it."""
    return {
        "baseline": dict(events=cs.STUDY_STREAM, preseed=True, per_cycle=8,
                         memory_cls=MemoryService),
        "no_branch": dict(events=cs.UNBRANCHED_STREAM, preseed=True, per_cycle=8,
                          memory_cls=MemoryService),
        "cold_start": dict(events=cs.STUDY_STREAM, preseed=False, per_cycle=1,
                           memory_cls=MemoryService),
        "cold_start_unbranched": dict(events=cs.UNBRANCHED_STREAM, preseed=False,
                                      per_cycle=1, memory_cls=MemoryService),
        "real_git_history": dict(events=git_events, preseed=False, per_cycle=1,
                                 memory_cls=MemoryService),
        "wide_lookback": dict(events=cs.STUDY_STREAM, preseed=True, per_cycle=8,
                              memory_cls=cs.WideLookbackMemory),
    }[name]


def run_cell(*, stream: str, arm: str, seed: int, cycles: int,
             git_events: list[str]) -> dict:
    """One (stream, arm, seed) cell, returned as a plain dict."""
    spec = stream_spec(stream, git_events)
    cls = sleep_class(arm)
    db_path = temp_db(f"cp_{stream}__{arm}__{seed}.db")
    previous_seed = cls.RANDOM_SEED
    cls.RANDOM_SEED = seed
    mem = spec["memory_cls"](db_path)
    try:
        events = spec["events"]
        if spec["preseed"]:
            for text in events:
                mem.store(text, event_type="event", source="seed:bootstrap")

        svc = cls(mem)
        first_seen: dict[str, int] = {}
        report = None
        n = len(events)
        per_cycle = spec["per_cycle"]
        for cycle in range(cycles):
            if not spec["preseed"]:
                for k in range(per_cycle):
                    text = events[(cycle * per_cycle + k) % n]
                    mem.store(text, event_type="event", source=f"cycle:{cycle}")
            else:
                start = (cycle * per_cycle) % n
                for text in events[start:start + per_cycle]:
                    mem.store(text, event_type="event", source=f"cycle:{cycle}")

            report = svc.run_sleep_cycle()
            for label, attr in cs.GENERATIONS:
                if label not in first_seen and len(getattr(report, attr)) > 0:
                    first_seen[label] = cycle + 1

        final = {label: len(getattr(report, attr)) for label, attr in cs.GENERATIONS}
        competing: dict[str, int] = {}
        for h in report.hypotheses:
            if h.expectation != "high_structural_significance":
                competing[h.subject] = competing.get(h.subject, 0) + 1
        confs = sorted(h.confidence for h in report.hypotheses)

        return {
            "stream": stream,
            "arm": arm,
            "seed": seed,
            "cycles": cycles,
            "random_seed_used": seed,
            "g5_cycle": first_seen.get("G5 theories"),
            "g5_present": "G5 theories" in first_seen,
            "cycles_to_first_emergence": first_seen,
            "final_populations": final,
            "competing_subjects_final": sum(1 for v in competing.values() if v >= 2),
            "n_hypotheses_final": len(report.hypotheses),
            "confidence_median_final": (statistics.median(confs) if confs else None),
            "confidence_max_final": (confs[-1] if confs else None),
        }
    finally:
        cls.RANDOM_SEED = previous_seed
        mem.close()
        try:
            db_path.unlink()
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Analysis -- the readings are computed, never typed
# ---------------------------------------------------------------------------
def _cells_ok(cells: list[dict]) -> bool:
    return all(c.get("cycles") == CYCLES for c in cells)


def present(cells: list[dict], stream: str, arm: str) -> int:
    return sum(1 for c in cells
               if c["stream"] == stream and c["arm"] == arm and c["g5_present"])


def cycles(cells: list[dict], stream: str, arm: str) -> list[int]:
    return [c["g5_cycle"] for c in cells
            if c["stream"] == stream and c["arm"] == arm and c["g5_present"]]


def analyse(cells: list[dict]) -> dict:
    """Every control, prediction and reading in the pre-registration."""
    count = len(cells)
    completed = _cells_ok(cells)

    frozen = {s: present(cells, s, CONTROL_ARM) for s in STREAMS}
    share = {s: present(cells, s, "share") for s in STREAMS}
    jeff = {s: present(cells, s, "jeffreys") for s in STREAMS}
    lap = {s: present(cells, s, "laplace") for s in STREAMS}

    # C1: the alpha=beta=0 copy must reproduce the frozen engine exactly.
    index = {(c["stream"], c["arm"], c["seed"]): c for c in cells}
    mismatches = []
    for stream in STREAMS:
        for seed in SEEDS:
            a = index.get((stream, CONTROL_ARM, seed))
            b = index.get((stream, "share", seed))
            if a is None or b is None:
                mismatches.append({"stream": stream, "seed": seed, "reason": "missing"})
                continue
            if (a["g5_cycle"] != b["g5_cycle"]
                    or a["final_populations"] != b["final_populations"]
                    or a["n_hypotheses_final"] != b["n_hypotheses_final"]):
                mismatches.append({"stream": stream, "seed": seed,
                                   "frozen": {"g5": b["g5_cycle"],
                                              "populations": b["final_populations"]},
                                   "control": {"g5": a["g5_cycle"],
                                               "populations": a["final_populations"]}})

    c1 = completed and not mismatches
    c3 = completed and frozen["baseline"] >= 11
    c2 = completed and any(
        jeff[s] != frozen[s] or lap[s] != frozen[s] for s in STREAMS)

    p0_fires = completed and frozen["wide_lookback"] >= 6
    p1 = (completed and not p0_fires
          and jeff["wide_lookback"] >= 9 and frozen["wide_lookback"] <= 1)
    unbranched = ("cold_start_unbranched", "real_git_history")
    p2 = (completed
          and max(jeff[s] for s in unbranched) >= 6
          and all(frozen[s] <= 1 for s in unbranched))
    base_jeff = cycles(cells, "baseline", "jeffreys")
    base_frozen = cycles(cells, "baseline", CONTROL_ARM)
    p3 = bool(completed and jeff["baseline"] >= 11 and base_jeff and base_frozen
              and statistics.median(base_jeff) <= statistics.median(base_frozen) + 2)

    # Only streams where the two priors actually differ can disagree in
    # direction.  ``all()`` over an empty set is True, which would report a
    # disagreement that no stream supports.
    compared = [s for s in STREAMS if jeff[s] != lap[s]]
    direction_disagreement = bool(completed and compared and all(
        (jeff[s] > frozen[s]) != (lap[s] > frozen[s]) for s in compared))

    if not completed or not (c1 and c2 and c3):
        reading = "R3"
    elif (not p0_fires) and p1 and p2:
        reading = "R1"
    else:
        reading = "R2"

    return {
        "complete": completed,
        "cells": count,
        "g5_present_counts": {"frozen": frozen, "share": share,
                              "jeffreys": jeff, "laplace": lap},
        "controls": {"C1_identity": c1, "C1_mismatches": mismatches,
                     "C2_axis_live": c2, "C3_stream_reachable": c3},
        "premise": {"P0_fires": p0_fires,
                    "frozen_wide_lookback": frozen["wide_lookback"]},
        "predictions": {"P1": p1, "P2": p2, "P3": p3},
        "prior_disagreement_in_direction": direction_disagreement,
        "reading": reading,
    }


def summarise(cells: list[dict]) -> dict:
    """Descriptive statistics, including the mechanism's own signature."""
    out: dict[str, dict] = {}
    for stream in STREAMS:
        for arm in ("share", CONTROL_ARM, "jeffreys", "laplace"):
            subset = [c for c in cells if c["stream"] == stream and c["arm"] == arm]
            if not subset:
                continue
            med = [c["confidence_median_final"] for c in subset
                   if c["confidence_median_final"] is not None]
            mx = [c["confidence_max_final"] for c in subset
                  if c["confidence_max_final"] is not None]
            out[f"{stream}/{arm}"] = {
                "cells": len(subset),
                "g5_present": sum(1 for c in subset if c["g5_present"]),
                "median_of_median_confidence": (statistics.median(med) if med else None),
                "max_confidence_seen": (max(mx) if mx else None),
                "median_competing_subjects": statistics.median(
                    [c["competing_subjects_final"] for c in subset]),
            }
    return out


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def cell_path(stream: str, arm: str, seed: int) -> Path:
    return CELLS_DIR / f"{stream}__{arm}__{seed}.json"


def all_jobs(git_events: list[str]) -> list[dict]:
    jobs = []
    for stream in STREAMS:
        for arm in ARMS + (CONTROL_ARM,):
            for seed in SEEDS:
                jobs.append(dict(stream=stream, arm=arm, seed=seed,
                                 cycles=CYCLES, git_events=git_events))
    return jobs


def run_jobs(jobs: list[dict], workers: int) -> list[dict]:
    CELLS_DIR.mkdir(parents=True, exist_ok=True)
    done: list[dict] = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_cell, **job): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            cell = future.result()
            path = cell_path(job["stream"], job["arm"], job["seed"])
            path.write_text(json.dumps(engine_stamp.stamp(cell), indent=2), encoding="utf-8")
            done.append(cell)
            print(f"  {job['stream']:<22} {job['arm']:<20} {job['seed']}  "
                  f"G5={'yes' if cell['g5_present'] else 'no '}", flush=True)
    return done


def load_cells() -> list[dict]:
    cells = []
    for path in sorted(CELLS_DIR.glob("*.json")):
        cells.append(json.loads(path.read_text(encoding="utf-8")))
    return cells


def self_test(workers: int) -> int:
    """C1 on a reduced grid, before the real one is started."""
    git_events = cs.git_commit_stream()
    jobs = []
    for stream in ("baseline", "no_branch"):
        for arm in ("share", CONTROL_ARM):
            for seed in SEEDS[:2]:
                jobs.append(dict(stream=stream, arm=arm, seed=seed,
                                 cycles=CYCLES, git_events=git_events))
    print(f"self-test: {len(jobs)} cells, C1 identity only")
    cells = run_jobs(jobs, workers)
    index = {(c["stream"], c["arm"], c["seed"]): c for c in cells}
    bad = []
    for stream in ("baseline", "no_branch"):
        for seed in SEEDS[:2]:
            a = index[(stream, CONTROL_ARM, seed)]
            b = index[(stream, "share", seed)]
            if (a["g5_cycle"], a["final_populations"], a["n_hypotheses_final"]) != \
               (b["g5_cycle"], b["final_populations"], b["n_hypotheses_final"]):
                bad.append((stream, seed, a["g5_cycle"], b["g5_cycle"]))
    for stream in ("baseline", "no_branch"):
        for seed in SEEDS[:2]:
            for path in (cell_path(stream, "share", seed),
                         cell_path(stream, CONTROL_ARM, seed)):
                path.unlink(missing_ok=True)
    if bad:
        print(f"  C1 FAILED on {len(bad)} cell(s): {bad}")
        return 1
    print("  C1 held: the alpha=beta=0 copy is identical to the frozen engine")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Confidence-formula amendment study.")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--limit", type=int, default=0,
                    help="run at most N pending cells this pass (chunking; the grid is unchanged)")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    if args.self_test:
        return self_test(args.workers)

    git_events = cs.git_commit_stream()
    if not git_events:
        print("the unengineered stream is empty; refusing to run")
        return 2

    jobs = all_jobs(git_events)
    if args.check:
        # A check recomputes the reading from the cells already on disk; it
        # must never run the grid again.
        jobs = []
    if args.resume:
        jobs = [j for j in jobs if not cell_path(j["stream"], j["arm"], j["seed"]).exists()]
    if args.limit:
        jobs = jobs[:args.limit]
    print(f"{len(jobs)} cells to run, {CYCLES} cycles each, {args.workers} workers")

    started = time.time()
    if jobs:
        run_jobs(jobs, args.workers)
    cells = load_cells()
    print(f"\n{len(cells)} cells on disk ({round(time.time() - started, 1)}s this pass)")

    analysis = analyse(cells)
    if not analysis["complete"]:
        print("INCOMPLETE: the grid is not fully run, so no reading is computed")
        print(json.dumps({"complete": False, "cells": len(cells)}, indent=2))
        return 3

    artifact = {
        "what_this_is": (
            "The confidence-formula amendment, run under "
            "docs/CONFIDENCE-POSTERIOR-PREREGISTRATION.md. organica/ is "
            "unmodified; every posterior arm is an in-process override."
        ),
        "protocol": "docs/CONFIDENCE-POSTERIOR-PREREGISTRATION.md",
        "design": {"cycles": CYCLES, "arms": list(ARMS), "control_arm": CONTROL_ARM,
                   "streams": list(STREAMS), "seeds": SEEDS, "reserve": list(RESERVE)},
        "analysis": analysis,
        "summary": summarise(cells),
        "cells": sorted(cells, key=lambda c: (c["stream"], c["arm"], c["seed"])),
    }
    out = Path(args.out)
    out.write_text(json.dumps(engine_stamp.stamp(artifact), indent=2), encoding="utf-8")
    print(f"\nreading: {analysis['reading']}")
    for key, value in analysis["predictions"].items():
        print(f"  {key}: {value}")
    print(f"  controls: {analysis['controls']['C1_identity']}, "
          f"{analysis['controls']['C2_axis_live']}, "
          f"{analysis['controls']['C3_stream_reachable']}")
    print(f"written to {out}")

    if args.check:
        stored = json.loads(out.read_text(encoding="utf-8"))
        return 0 if stored["analysis"] == analysis else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
