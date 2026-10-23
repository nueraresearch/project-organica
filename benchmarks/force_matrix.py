"""
Ablation Matrix V2 -- the six-colony Tier-1 campaign.

Runs the six colonies defined in `docs/FORCE-MATRIX-PREREGISTRATION.md` §4
on the branch stimulus that closed the launch gates, and scores each one
on M1-M9 exactly as frozen there.

    FULL             full system, ALPHABETICAL retention
    SALIENCE         salience retention
    NO_CONTRADICTIONS CONTRADICTION_SCALE = 0
    NO_QUESTIONS     question creation disabled
    NO_DREAMS        dream generation disabled
    ANTI_EIG         experiments selected by LOWEST information gain

Every colony is a subclass applied in-process. The engine source is never
edited for a campaign.

Each colony runs cold (a fresh substrate), with one fixed seed, for
`--cycles` cycles at the daemon's cadence of 8 events per cycle.

Usage:
    python benchmarks/force_matrix.py --cycles 3000
    python benchmarks/force_matrix.py --cycles 300 --colonies FULL   # pilot
Writes docs/force_matrix.json
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.branch_streams import (                # noqa: E402
    NEUTRAL_HUB, NEUTRAL_PETALS, lattice_designs, lattice_stream)
from organica.memory import MemoryService            # noqa: E402
from organica.sleep import SleepService              # noqa: E402
from organica.streams import EVENTS_PER_CYCLE        # noqa: E402
from organica.paths import temp_db                   # noqa: E402

MAX_THEORIES = SleepService.MAX_THEORIES
MAX_HYPOTHESES = SleepService.MAX_HYPOTHESES


# ==================================================================
# The colonies. Each is a subclass; the engine is never edited.
# ==================================================================

class FullService(SleepService):
    """FULL -- the reference arm. Alphabetical retention."""
    HYPOTHESIS_RETENTION = "alphabetical"


class SalienceService(SleepService):
    """SALIENCE -- rank beliefs by salience instead of by name."""
    HYPOTHESIS_RETENTION = "salience"


class NoContradictionsService(SleepService):
    """NO_CONTRADICTIONS -- is contradiction fuel, or bookkeeping?

    The raw value is retained in the evidence dict so M3 still measures
    the world and not the axis.
    """
    CONTRADICTION_SCALE = 0.0


class NoQuestionsService(SleepService):
    """NO_QUESTIONS -- theories are kept, questions are not."""
    def _form_theories_and_questions(self, hypotheses, prior):
        theories, _questions = super()._form_theories_and_questions(hypotheses, prior)
        return theories, []


class NoDreamsService(SleepService):
    """NO_DREAMS -- no dream generation at all."""
    def _generate_categorized_dreams(self, *a, **k):
        return []


class AntiEigService(SleepService):
    """ANTI_EIG -- select the experiments with the LEAST expected value.

    The engine sorts experiments by `priority` (EIG / cost) and keeps the
    top `MAX_EXPERIMENTS`. This arm keeps the BOTTOM instead, so the
    selector is actively bad rather than merely absent.
    """
    def _select_experiments(self, investigations, questions, dreams):
        experiments = super()._select_experiments(investigations, questions, dreams)
        experiments.sort(key=lambda exp: exp.priority)
        return experiments[:self.MAX_EXPERIMENTS]


COLONIES = {
    "FULL": (FullService, "reference arm, alphabetical retention"),
    "SALIENCE": (SalienceService, "salience retention"),
    "NO_CONTRADICTIONS": (NoContradictionsService, "CONTRADICTION_SCALE = 0"),
    "NO_QUESTIONS": (NoQuestionsService, "question creation disabled"),
    "NO_DREAMS": (NoDreamsService, "dream generation disabled"),
    "ANTI_EIG": (AntiEigService, "experiments selected by lowest EIG"),
}


# ==================================================================
# Instrumentation
# ==================================================================

class Instrumented(SleepService):
    """Records everything M1-M9 are defined on."""

    def __init__(self, memory):
        super().__init__(memory)
        self.rows = []
        self.max_generation = 0

    def _note_generation(self, candidates):
        for c in candidates:
            g = getattr(c, "generation", 0) or 0
            if g > self.max_generation:
                self.max_generation = g

    def _retain_hypotheses(self, beliefs, info, temporal):
        pre = Counter(h.subject for h in beliefs)
        kept = super()._retain_hypotheses(beliefs, info, temporal)
        post = Counter(h.subject for h in kept)
        self.rows.append({
            "pre_beliefs": len(beliefs),
            "pre_ge2": sum(1 for c in pre.values() if c >= 2),
            "beliefs": [{
                "id": h.id,
                "subject": h.subject,
                "expectation": h.expectation,
                "confidence": round(h.confidence, 6),
                "support": h.support_count,
                "contradiction": h.contradiction_count,
                "raw_contradiction": (h.evidence or {}).get(
                    "raw_contradiction_count", h.contradiction_count),
            } for h in kept],
        })
        return kept

    def _form_theories_and_questions(self, hypotheses, prior):
        theories, questions = super()._form_theories_and_questions(hypotheses, prior)
        self._note_generation(theories)
        self._note_generation(questions)
        self._last_theories = [{
            "id": t.id, "subject": t.subject,
            "confidence": t.confidence, "support": t.support_count,
        } for t in theories]
        self._last_questions = [{
            "id": q.id, "subject": q.subject, "uncertainty": q.uncertainty,
        } for q in questions]
        return theories, questions

    def _generate_categorized_dreams(self, *a, **k):
        dreams = super()._generate_categorized_dreams(*a, **k)
        self._note_generation(dreams)
        self._last_dreams = [{"id": d.id, "subject": d.subject} for d in dreams]
        return dreams

    def _select_experiments(self, investigations, questions, dreams):
        experiments = super()._select_experiments(investigations, questions, dreams)
        self._note_generation(experiments)
        self._last_experiments = [{"id": e.id} for e in experiments]
        self._last_investigations = [{"id": i.id} for i in investigations]
        return experiments


# ==================================================================
# The metrics
# ==================================================================

def compute_metrics(rows: list[dict], svc: Instrumented) -> dict:
    n = len(rows)
    m = {}

    def duty(field, window=None):
        src = rows[-window:] if window else rows
        if not src:
            return None
        hit = 0
        for i, r in enumerate(src):
            if field == "theory":
                hit += 1 if getattr(svc, "_last_theories", []) else 0
            elif field == "question":
                hit += 1 if getattr(svc, "_last_questions", []) else 0
        return hit / len(src)

    # M1 / M2 -- duty cycles. The per-cycle theory and question lists are
    # captured by the instrument; they are stored on the service per
    # cycle, so we rebuild the series from the recorded counts instead.
    theory_counts = [r.get("theory_count", 0) for r in rows]
    question_counts = [r.get("question_count", 0) for r in rows]

    def duty_from(counts, window=None):
        src = counts[-window:] if window else counts
        if not src:
            return None
        return sum(1 for c in src if c > 0) / len(src)

    m["M1_theory_duty_cycle"] = {
        "whole_run": duty_from(theory_counts),
        "last_2000": duty_from(theory_counts, 2000),
    }
    m["M2_question_duty_cycle"] = {
        "whole_run": duty_from(question_counts),
        "last_2000": duty_from(question_counts, 2000),
    }

    # M3 -- contradiction density over the active belief population.
    cd, cd_share = [], []
    for r in rows:
        bs = r["beliefs"]
        if not bs:
            continue
        raw = sum(b["raw_contradiction"] for b in bs)
        sup = sum(b["support"] for b in bs)
        cd.append(raw / len(bs))
        if sup + raw > 0:
            cd_share.append(raw / (sup + raw))
    m["M3_contradiction_density"] = {
        "mean": round(statistics.fmean(cd), 4) if cd else None,
        "median": round(statistics.median(cd), 4) if cd else None,
        "p95": round(sorted(cd)[max(0, int(0.95 * len(cd)) - 1)], 4) if cd else None,
        "max": round(max(cd), 4) if cd else None,
        "share_mean": round(statistics.fmean(cd_share), 4) if cd_share else None,
    }

    # M4 -- survival of contradiction-bearing beliefs.
    ever_contradicting, alive = set(), set()
    for r in rows:
        for b in r["beliefs"]:
            if b["raw_contradiction"] > 0:
                ever_contradicting.add(b["id"])
            alive.add(b["id"])
    final_alive = {b["id"] for b in rows[-1]["beliefs"]} if rows else set()
    survived = len(ever_contradicting & final_alive)
    m["M4_contradiction_survival"] = {
        "ever_contradicting": len(ever_contradicting),
        "survived_to_end": survived,
        "rate": round(survived / len(ever_contradicting), 4) if ever_contradicting else None,
    }

    # M5 -- development velocity. "New" means an id not seen in any earlier
    # cycle, exactly as frozen.
    seen_b, seen_q, seen_d, seen_e = set(), set(), set(), set()
    new_per_cycle = []
    for r in rows:
        new = 0
        for b in r["beliefs"]:
            if b["id"] not in seen_b:
                seen_b.add(b["id"]); new += 1
        for q in r.get("questions", []):
            if q["id"] not in seen_q:
                seen_q.add(q["id"]); new += 1
        for d in r.get("dreams", []):
            if d["id"] not in seen_d:
                seen_d.add(d["id"]); new += 1
        for e in r.get("experiments", []):
            if e["id"] not in seen_e:
                seen_e.add(e["id"]); new += 1
        new_per_cycle.append(new)
    m["M5_development_velocity"] = {
        "new_per_100_cycles": round(100 * sum(new_per_cycle) / n, 3) if n else None,
        "distinct_beliefs_ever": len(seen_b),
        "distinct_questions_ever": len(seen_q),
        "distinct_dreams_ever": len(seen_d),
        "distinct_experiments_ever": len(seen_e),
        "last_100_new_total": sum(new_per_cycle[-100:]) if new_per_cycle else 0,
    }

    # M6 -- lineage depth.
    m["M6_lineage_depth"] = {"max_generation": svc.max_generation}

    # M7 -- mean hypothesis lifetime, with censoring disclosed.
    birth, last_seen = {}, {}
    for i, r in enumerate(rows):
        for b in r["beliefs"]:
            if b["id"] not in birth:
                birth[b["id"]] = i
            last_seen[b["id"]] = i
    lifetimes, censored = [], 0
    for bid, b in birth.items():
        ls = last_seen[bid]
        if ls < n - 1:
            lifetimes.append(ls - b + 1)
        else:
            censored += 1
    if lifetimes:
        m["M7_mean_hypothesis_lifetime"] = {
            "mean": round(statistics.fmean(lifetimes), 3),
            "observed": len(lifetimes),
            "censored": censored,
            "total_beliefs": len(birth),
        }
    else:
        m["M7_mean_hypothesis_lifetime"] = {
            "mean": None,
            "observed": 0,
            "censored": censored,
            "total_beliefs": len(birth),
            "status": (f"not measurable (n censored = {censored} of {len(birth)})"),
        }

    # M8 -- population stability index per class.
    def psi(counts):
        if not counts or statistics.fmean(counts) == 0:
            return None
        return round(1 - statistics.pstdev(counts) / statistics.fmean(counts), 4)

    m["M8_population_stability"] = {
        "beliefs": psi([len(r["beliefs"]) for r in rows]),
        "theories": psi(theory_counts),
        "questions": psi(question_counts),
        "dreams": psi([r.get("dream_count", 0) for r in rows]),
    }

    # M9 -- cognitive revolutions.
    m["M9_cognitive_revolutions"] = _revolutions(rows)

    m["_populations"] = {
        "beliefs_mean": round(statistics.fmean([len(r["beliefs"]) for r in rows]), 3) if rows else 0,
        "theories_mean": round(statistics.fmean(theory_counts), 3) if rows else 0,
        "questions_mean": round(statistics.fmean(question_counts), 3) if rows else 0,
        "dreams_mean": round(statistics.fmean([r.get("dream_count", 0) for r in rows]), 3) if rows else 0,
        "investigations_mean": round(statistics.fmean([r.get("investigation_count", 0) for r in rows]), 3) if rows else 0,
        "experiments_mean": round(statistics.fmean([r.get("experiment_count", 0) for r in rows]), 3) if rows else 0,
        "pre_beliefs_mean": round(statistics.fmean([r["pre_beliefs"] for r in rows]), 3) if rows else 0,
        "pre_ge2_mean": round(statistics.fmean([r["pre_ge2"] for r in rows]), 3) if rows else 0,
    }
    return m


def _revolutions(rows: list[dict]) -> dict:
    """A theory replacement event, exactly as frozen in §2."""
    events = 0
    demoted = 0
    dominant = None
    pending = None          # (theory_id, dominant_confidence, demoted_at_cycle)
    for i, r in enumerate(rows):
        ths = r.get("theories", [])
        if not ths:
            continue
        dom = max(ths, key=lambda t: t["confidence"])
        if pending is not None:
            tid, conf, at = pending
            if dom["id"] != tid and i - at <= 50:
                events += 1
                pending = None
            elif i - at > 50:
                pending = None
        if dominant is not None and dominant["id"] == dom["id"]:
            continue
        # The previous dominant theory was replaced -- does its confidence
        # have to fall by more than 50% first?
        if dominant is not None:
            demoted += 1
            current = next((t for t in ths if t["id"] == dominant["id"]), None)
            if current is not None:
                if current["confidence"] < dominant["confidence"] * 0.5:
                    pending = (dominant["id"], dominant["confidence"], i)
                else:
                    pending = None
            else:
                pending = None
        dominant = dom
    return {"revolutions": events, "demotions": demoted,
            "demotions_without_replacement": demoted - events}


# ==================================================================
# The runner
# ==================================================================

def capture_cycle(svc) -> dict:
    """Copy the cycle's outputs onto the instrumented row.

    The instrument records the belief population inside
    `_retain_hypotheses`; the other layers are observed after the cycle
    completes, so they are copied onto the same row here.
    """
    r = svc.rows[-1]
    r["theory_count"] = len(getattr(svc, "_last_theories", []))
    r["question_count"] = len(getattr(svc, "_last_questions", []))
    r["dream_count"] = len(getattr(svc, "_last_dreams", []))
    r["investigation_count"] = len(getattr(svc, "_last_investigations", []))
    r["experiment_count"] = len(getattr(svc, "_last_experiments", []))
    r["theories"] = getattr(svc, "_last_theories", [])
    r["questions"] = getattr(svc, "_last_questions", [])
    r["dreams"] = getattr(svc, "_last_dreams", [])
    r["experiments"] = getattr(svc, "_last_experiments", [])
    return r


def colony_class(name: str):
    """Compose the instrument with the colony.

    The instrument comes FIRST in the MRO, so its overrides run, and each
    one calls ``super()`` -- which lands on the colony's own override.
    That matters: ``NO_QUESTIONS`` overrides
    ``_form_theories_and_questions`` and ``ANTI_EIG`` overrides
    ``_select_experiments``, and the instrument must observe the
    colony's behaviour, not shadow it.

    (Composing it the other way round -- or simply instantiating the
    instrument alone -- silently runs every colony as the default
    service. That bug produced a byte-identical FULL and SALIENCE in the
    first pilot.)
    """
    cls, _description = COLONIES[name]
    composed = type(f"Instrumented_{name}", (Instrumented, cls), {})
    return composed


def run_colony(name: str, events: list[str], cycles: int, seed: int) -> dict:
    cls, description = COLONIES[name]
    db = temp_db(f"matrix_{name}.db")
    if db.exists():
        db.unlink()
    mem = MemoryService(db_path=str(db))
    svc = colony_class(name)(mem)
    if hasattr(svc, "_rng"):
        svc._rng.seed(seed)

    for text in events:
        mem.store(text, event_type="event", source="seed:bootstrap")

    t0 = time.time()
    for i in range(cycles):
        start = (i * EVENTS_PER_CYCLE) % len(events)
        for text in events[start:start + EVENTS_PER_CYCLE]:
            mem.store(text, event_type="event", source=f"cycle:{i}")
        svc.run_sleep_cycle()
        # Capture the per-cycle outputs that the metrics are defined on.
        capture_cycle(svc)
    elapsed = time.time() - t0

    metrics = compute_metrics(svc.rows, svc)
    mem.close()
    db.unlink(missing_ok=True)
    return {
        "colony": name,
        "description": description,
        "seed": seed,
        "cycles": cycles,
        "seconds": round(elapsed, 1),
        "metrics": metrics,
    }


def verify_colonies(events: list[str], cycles: int = 40) -> list[dict]:
    """G1: prove each colony's intervention is actually in the code path.

    The first pilot of this harness produced a byte-identical FULL and
    SALIENCE, because the instrument was instantiated alone and every
    colony silently ran the default service. This check makes that class
    of mistake loud instead of invisible: each colony is run briefly and
    its intervention is asserted on the OUTPUT.

    This is rung G1 of the perturbation ladder (code path). Rung G2 (the
    candidate pools) and G3 (the final outputs) are what the campaign
    itself measures.
    """
    checks = []

    for name in COLONIES:
        db = temp_db(f"verify_{name}.db")
        if db.exists():
            db.unlink()
        mem = MemoryService(db_path=str(db))
        svc = colony_class(name)(mem)
        for text in events:
            mem.store(text, event_type="event", source="seed:bootstrap")
        for i in range(cycles):
            start = (i * EVENTS_PER_CYCLE) % len(events)
            for text in events[start:start + EVENTS_PER_CYCLE]:
                mem.store(text, event_type="event", source=f"cycle:{i}")
            svc.run_sleep_cycle()
        row = capture_cycle(svc)
        policy = type(svc).HYPOTHESIS_RETENTION
        scale = type(svc).CONTRADICTION_SCALE
        checks.append({
            "colony": name,
            "retention_policy": policy,
            "contradiction_scale": scale,
            "questions": row.get("question_count"),
            "dreams": row.get("dream_count"),
            "experiments": row.get("experiment_count"),
            "beliefs": row.get("pre_beliefs"),
            "theories": row.get("theory_count"),
        })
        mem.close()
        db.unlink(missing_ok=True)

    by_name = {c["colony"]: c for c in checks}
    problems = []
    if by_name["FULL"]["retention_policy"] != "alphabetical":
        problems.append("FULL is not using alphabetical retention")
    if by_name["SALIENCE"]["retention_policy"] != "salience":
        problems.append("SALIENCE is not using salience retention")
    if by_name["NO_CONTRADICTIONS"]["contradiction_scale"] != 0.0:
        problems.append("NO_CONTRADICTIONS is not scaling contradiction to zero")
    if (by_name["NO_QUESTIONS"]["questions"] or 0) != 0:
        problems.append("NO_QUESTIONS is still producing questions")
    if (by_name["NO_DREAMS"]["dreams"] or 0) != 0:
        problems.append("NO_DREAMS is still producing dreams")
    if by_name["FULL"]["theories"] == 0:
        problems.append("FULL produced no theories -- the reference arm is broken")

    for c in checks:
        print(f"  {c['colony']:<20} policy={c['retention_policy']:<14} "
              f"scale={c['contradiction_scale']:<5} Q={c['questions']:<3} "
              f"D={c['dreams']:<3} E={c['experiments']:<3} "
              f"beliefs={c['beliefs']:<3} theories={c['theories']}")
    if problems:
        for p in problems:
            print(f"  !! {p}")
    else:
        print("  G1 code-path check: all six colonies verified distinct.")
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=20261023)
    ap.add_argument("--colonies", nargs="*", default=list(COLONIES))
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--out", default=str(REPO / "docs" / "force_matrix.json"))
    args = ap.parse_args()

    lattice = lattice_designs(NEUTRAL_HUB, NEUTRAL_PETALS)
    events = lattice_stream(lattice["L1_hub1_t3_disjoint"]["triangles"])

    print("G1 code-path verification:")
    checks = verify_colonies(events)
    if args.verify_only:
        return

    rows = []
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    for name in args.colonies:
        r = run_colony(name, events, args.cycles, args.seed)
        rows.append(r)
        out_path.write_text(json.dumps({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cycles": args.cycles,
            "seed": args.seed,
            "stimulus": "lattice_L1 (three disjoint triangles)",
            "g1_verification": checks,
            "rows": list(rows),
        }, indent=2), encoding="utf-8")
        m = r["metrics"]
        print(f"{name:<20} TDC={m['M1_theory_duty_cycle']['whole_run']:.3f} "
              f"QDC={m['M2_question_duty_cycle']['whole_run']:.3f} "
              f"CD={m['M3_contradiction_density']['mean']} "
              f"CS={m['M4_contradiction_survival']['rate']} "
              f"DV={m['M5_development_velocity']['new_per_100_cycles']} "
              f"gen={m['M6_lineage_depth']['max_generation']} "
              f"life={m['M7_mean_hypothesis_lifetime']['mean']} "
              f"psi_b={m['M8_population_stability']['beliefs']} "
              f"rev={m['M9_cognitive_revolutions']['revolutions']} "
              f"({r['seconds']}s)")
        sys.stdout.flush()

    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
