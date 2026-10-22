"""
benchmarks/ablation_verify.py
------------------------------------------------------------------
Mechanism verification: did each ablation actually change the organism?

An ablation result is only interpretable if the perturbation occurred.
This script establishes that independently of the outcome. It answers three
questions, in this order:

  A. PERTURBATION CENSUS -- for every condition, what actually changed
     relative to O_FULL? A condition that changed nothing was not an
     ablation; it was the same organism.

  B. DID RANDOM CURIOSITY CHANGE BEHAVIOUR? -- Ablation H replaces the
     Expected-Information-Gain ranking with a random one. Three checks:
       * experiment overlap (Jaccard) between the EIG-selected set and the
         randomly-selected set;
       * rank correlation between the EIG ranking and the selection order;
       * the curiosity-score distribution of what each policy selected
         (mean, spread, and how often the selected item was in the top
         decile of available candidates).
     If the distributions are identical, the EIG implementation is not
     influencing selection -- regardless of what the aggregate score says.

  C. WHERE DO CONTRADICTIONS COME FROM? -- Ablation D removes
     falsification, and the measured contradiction count for D is 0. Three
     explanations are possible:
       A. contradictions are generated only by the falsification subsystem;
       B. the ablation accidentally disabled a dead pipeline (a bug);
       C. contradiction *generation* is independent of falsification, but
          contradiction *survival* depends on it.
     The script tests these directly by re-running the same conditions with
     the Layer-4 hypothesis cap removed. If the cap is what decides which
     competing beliefs survive, uncapping the hypothesis population should
     change the contradiction count.

Usage:
    python benchmarks/ablation_verify.py
    python benchmarks/ablation_verify.py --cycles 300 --out docs/ablation_verification.json
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from organica import MemoryService, SleepService  # noqa: E402
from organica.paths import REPO_ROOT, temp_db  # noqa: E402
from organica.streams import STUDY_STREAM  # noqa: E402

from ablation_study import (  # noqa: E402
    GENERATIONS,
    NoFalsificationService,
    RandomCuriosityService,
    run_condition,
)


# ===========================================================================
# Instrumented services
# ===========================================================================
class InstrumentedService(SleepService):
    """Records, per cycle, what the selection layers actually chose."""

    def __init__(self, memory, rng=None):
        super().__init__(memory)
        self.rng = rng
        self.records: list[dict] = []

    # -- Layer 4 ---------------------------------------------------------
    def _form_and_test_hypotheses(self, temporal, freqs, workflows, processes,
                                  meta_concepts, prior):
        hyps = super()._form_and_test_hypotheses(
            temporal, freqs, workflows, processes, meta_concepts, prior)
        self._pending_hyps = [
            {
                "subject": h.subject,
                "expectation": h.expectation,
                "support": h.support_count,
                "contradiction": h.contradiction_count,
                "confidence": h.confidence,
                "structural": h.expectation == "high_structural_significance",
            }
            for h in hyps
        ]
        return hyps

    # -- Layer 7 ---------------------------------------------------------
    def _rank_investigations(self, questions, dreams):
        # Get the full candidate set, then the actual selection.
        original = self.MAX_INVESTIGATIONS
        self.MAX_INVESTIGATIONS = 1000
        try:
            full = super()._rank_investigations(questions, dreams)
        finally:
            self.MAX_INVESTIGATIONS = original
        selected = super()._rank_investigations(questions, dreams)
        self._pending_invs = {
            "all": [(i.id, float(i.expected_information_gain)) for i in full],
            "selected": [i.id for i in selected],
        }
        return selected

    def _store_candidates(self, report):
        super()._store_candidates(report)
        self.records.append({
            "hypotheses": list(getattr(self, "_pending_hyps", [])),
            "investigations": getattr(self, "_pending_invs", {"all": [], "selected": []}),
            "populations": {
                label: len(getattr(report, attr)) for label, attr in GENERATIONS
            },
        })


class InstrumentedRandomCuriosity(InstrumentedService, RandomCuriosityService):
    """Instrumented Random Curiosity (H)."""


class InstrumentedNoFalsification(InstrumentedService, NoFalsificationService):
    """Instrumented No Falsification (D)."""


# ===========================================================================
# Running an instrumented condition
# ===========================================================================
def run_instrumented(code: str, sleep_cls, cycles: int, seed: int,
                     max_hypotheses: int | None = None) -> dict:
    original_max = SleepService.MAX_HYPOTHESES
    if max_hypotheses is not None:
        SleepService.MAX_HYPOTHESES = max_hypotheses
    db = temp_db(f"verify_{code}.db")
    if db.exists():
        db.unlink()
    mem = MemoryService(db)
    try:
        rng = random.Random(seed)
        if sleep_cls in (RandomCuriosityService, InstrumentedRandomCuriosity):
            sleep = sleep_cls(mem, rng=rng)
        else:
            sleep = sleep_cls(mem)
        for cycle in range(cycles):
            start = (cycle * 8) % len(STUDY_STREAM)
            for k in range(8):
                mem.store(STUDY_STREAM[(start + k) % len(STUDY_STREAM)],
                          event_type="event", source=f"cycle:{cycle}")
            sleep.run_sleep_cycle()
        return {"condition": code, "records": sleep.records,
                "max_hypotheses": max_hypotheses or original_max}
    finally:
        mem.close()
        try:
            db.unlink()
        except OSError:
            pass
        SleepService.MAX_HYPOTHESES = original_max


# ===========================================================================
# B. Did Random Curiosity change behaviour?
# ===========================================================================
def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def spearman(pairs: list[tuple[float, int]]) -> float:
    """Spearman rank correlation between a score and a rank (0 = best)."""
    if len(pairs) < 2:
        return 0.0

    def ranks(values: list[float]) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: values[i])
        out = [0.0] * len(values)
        for pos, idx in enumerate(order):
            out[idx] = float(pos)
        return out

    scores = [p[0] for p in pairs]
    ranks_ = [p[1] for p in pairs]
    rs, rr = ranks(scores), ranks(ranks_)
    n = len(pairs)
    ms, mr = sum(rs) / n, sum(rr) / n
    num = sum((rs[i] - ms) * (rr[i] - mr) for i in range(n))
    den_s = sum((rs[i] - ms) ** 2 for i in range(n)) ** 0.5
    den_r = sum((rr[i] - mr) ** 2 for i in range(n)) ** 0.5
    if den_s == 0 or den_r == 0:
        return 0.0
    return num / (den_s * den_r)


def curiosity_effectiveness(full: dict, random_cond: dict) -> dict:
    """Compare what EIG selection chose against what random selection chose."""
    def analyse(run: dict) -> dict:
        selected_scores, all_scores, top_decile_hits = [], [], []
        top_k_hits = []
        overlap_pairs = []
        for rec in run["records"]:
            invs = rec["investigations"]
            all_items = invs["all"]
            sel = invs["selected"]
            if not all_items:
                continue
            score_by_id = dict(all_items)
            scores = [s for _, s in all_items]
            cutoff = sorted(scores, reverse=True)[max(0, len(scores) // 10 - 1)]
            sel_scores = [score_by_id[i] for i in sel if i in score_by_id]
            selected_scores.extend(sel_scores)
            all_scores.extend(scores)
            top_decile_hits.extend([1 if s >= cutoff else 0 for s in sel_scores])
            # Scale-free selection quality: of the k candidates selected,
            # how many are in the top-k by EIG among all candidates?
            # A policy that follows EIG scores 1.0; a random policy scores
            # roughly k/N.
            k = len(sel)
            if k and all_items:
                ordered = [i for i, _ in sorted(all_items, key=lambda kv: -kv[1])][:k]
                top_k = set(ordered)
                top_k_hits.extend([1 if i in top_k else 0 for i in sel])
            # Correlate each selected candidate's EIG score with the POSITION
            # it was selected at. A policy that follows EIG puts high scores
            # first (strong negative correlation); a random policy does not
            # (correlation near zero).
            for pos, i in enumerate(sel):
                if i in score_by_id:
                    overlap_pairs.append((score_by_id[i], pos))
        return {
            "mean_score_selected": round(statistics.fmean(selected_scores), 5) if selected_scores else None,
            "mean_score_all_candidates": round(statistics.fmean(all_scores), 5) if all_scores else None,
            "stdev_score_selected": round(statistics.pstdev(selected_scores), 5) if len(selected_scores) > 1 else None,
            "stdev_score_all_candidates": round(statistics.pstdev(all_scores), 5) if len(all_scores) > 1 else None,
            "fraction_selected_in_top_decile": (
                round(sum(top_decile_hits) / len(top_decile_hits), 4) if top_decile_hits else None),
            "top_k_precision": (
                round(sum(top_k_hits) / len(top_k_hits), 4) if top_k_hits else None),
            "rank_correlation_score_vs_selection": round(spearman(overlap_pairs), 4),
            "selection_events": len(selected_scores),
        }

    def final_selection(run: dict) -> list[str]:
        for rec in reversed(run["records"]):
            if rec["investigations"]["selected"]:
                return rec["investigations"]["selected"]
        return []

    f_sel = set(final_selection(full))
    r_sel = set(final_selection(random_cond))
    f_an = analyse(full)
    r_an = analyse(random_cond)

    return {
        "final_selected_investigations_eig": sorted(f_sel),
        "final_selected_investigations_random": sorted(r_sel),
        "final_selection_jaccard": round(jaccard(f_sel, r_sel), 4),
        "eig_policy": f_an,
        "random_policy": r_an,
        "verdict": _verdict_h(f_an, r_an, jaccard(f_sel, r_sel)),
    }


def _verdict_h(f_an: dict, r_an: dict, jac: float) -> str:
    """State plainly whether the Random Curiosity ablation perturbed anything.

    Note the sign convention: the correlation is between a candidate's EIG
    score and the POSITION it was selected at, so a policy that follows
    EIG produces a NEGATIVE correlation (high score, early position).
    """
    bits = []
    corr = f_an.get("rank_correlation_score_vs_selection")
    r_corr = r_an.get("rank_correlation_score_vs_selection")
    if corr is not None and corr < -0.05:
        bits.append(f"EIG ranking drives selection order (rho={corr}; negative = "
                    f"higher score selected earlier)")
    else:
        bits.append(f"EIG ranking does NOT drive selection order (rho={corr})")
    if r_corr is not None:
        bits.append(f"random policy rho={r_corr}, i.e. no ordering effect")
    m_f = f_an.get("mean_score_selected")
    m_r = r_an.get("mean_score_selected")
    a_f = f_an.get("mean_score_all_candidates")
    a_r = r_an.get("mean_score_all_candidates")
    if m_f is not None and m_r is not None:
        bits.append(f"EIG selected mean curiosity score {m_f} vs random {m_r} "
                    f"(candidate pool means {a_f} / {a_r})")
    t_f = f_an.get("fraction_selected_in_top_decile")
    t_r = r_an.get("fraction_selected_in_top_decile")
    if t_f is not None and t_r is not None:
        bits.append(f"top-decile hit rate {t_f} (EIG) vs {t_r} (random)")
    bits.append(f"final-selection Jaccard {jac}")
    if jac >= 0.95:
        return ("PERTURBATION FAILED: the two policies chose essentially the same "
                "experiments, so any equality in the aggregate is vacuous. " + "; ".join(bits))
    return ("Perturbation confirmed: the policies chose substantially different "
            "investigations. " + "; ".join(bits))


# ===========================================================================
# C. Where do contradictions come from?
# ===========================================================================
def contradiction_report(run: dict) -> dict:
    """Per-cycle contradiction accounting for an instrumented run."""
    out = []
    for cycle, rec in enumerate(run["records"]):
        competing: dict[str, set[str]] = defaultdict(set)
        for h in rec["hypotheses"]:
            if h["structural"]:
                continue
            competing[h["subject"]].add(h["expectation"])
        subjects_with_split = sum(1 for v in competing.values() if len(v) >= 2)
        hyps = rec["hypotheses"]
        non_structural = [h for h in hyps if not h["structural"]]
        out.append({
            "cycle": cycle,
            "hypotheses": len(hyps),
            "non_structural_hypotheses": len(non_structural),
            "subjects_with_competing_expectations": subjects_with_split,
            "total_support": sum(h["support"] for h in non_structural),
            "total_contradiction": sum(h["contradiction"] for h in non_structural),
            "mean_confidence": (
                round(statistics.fmean([h["confidence"] for h in non_structural]), 4)
                if non_structural else None),
            "max_contradiction": max((h["contradiction"] for h in non_structural), default=0),
        })
    return {
        "per_cycle": out,
        "final": out[-1] if out else None,
        "max_subjects_with_competing_expectations": max(
            (o["subjects_with_competing_expectations"] for o in out), default=0),
        "mean_subjects_with_competing_expectations": (
            round(statistics.fmean([o["subjects_with_competing_expectations"] for o in out]), 3)
            if out else None),
        "max_contradiction_count_observed": max(
            (o["max_contradiction"] for o in out), default=0),
    }


def hypothesis_dump(run: dict, last: int = 12) -> list[dict]:
    """The final cycles' hypotheses with support / contradiction / confidence."""
    out = []
    for rec in run["records"][-last:]:
        out.append({
            "population": rec["populations"],
            "hypotheses": [
                {"subject": h["subject"], "expectation": h["expectation"],
                 "support": h["support"], "contradiction": h["contradiction"],
                 "confidence": h["confidence"], "structural": h["structural"]}
                for h in rec["hypotheses"]
            ],
        })
    return out


# ===========================================================================
# A. Perturbation census
# ===========================================================================
def perturbation_census(study_path: Path) -> list[dict]:
    """For every condition: what changed relative to O_FULL?

    Note on condition B (No Lineage): it is a *provenance* ablation, not a
    behavioural one. It strips parent links and changes nothing else, so
    "no population changed" is the expected outcome, not a failed
    perturbation. It is marked as such rather than flagged.
    """
    if not study_path.exists():
        return []
    data = json.loads(study_path.read_text(encoding="utf-8"))
    full = next((c for c in data["conditions"] if c["condition"] == "O_FULL"), None)
    if full is None:
        return []
    provenance_only = {"B"}
    out = []
    for c in data["conditions"]:
        if c["condition"] == "O_FULL":
            continue
        changed = []
        for label in [g[0] for g in GENERATIONS]:
            if c["final_populations"].get(label) != full["final_populations"].get(label):
                changed.append(f"{label}: {full['final_populations'].get(label)} -> "
                               f"{c['final_populations'].get(label)}")
        identical = not changed
        if c["condition"] in provenance_only:
            verdict = ("confirmed (provenance-only ablation: behaviour unchanged is "
                       "the result)")
        elif identical:
            verdict = "FAILED -- identical to O_FULL"
        else:
            verdict = "confirmed"
        out.append({
            "condition": c["condition"],
            "name": c["name"],
            "changed_populations": changed,
            "perturbation": verdict,
        })
    return out


# ===========================================================================
# Main
# ===========================================================================
def main() -> int:
    ap = argparse.ArgumentParser(description="Ablation mechanism verification.")
    ap.add_argument("--cycles", type=int, default=300)
    ap.add_argument("--out", default="docs/ablation_verification.json")
    ap.add_argument("--study", default="docs/ablation_study.json")
    args = ap.parse_args()

    print("=" * 100)
    print("ABLATION MECHANISM VERIFICATION -- did the perturbation happen?")
    print("=" * 100)

    # ---- A. census ----------------------------------------------------
    census = perturbation_census(REPO_ROOT / args.study)
    if census:
        print("\nA. PERTURBATION CENSUS")
        for row in census:
            mark = "!! " if row["perturbation"].startswith("FAILED") else "OK "
            detail = "; ".join(row["changed_populations"][:4]) or "no population changed"
            print(f"  {mark}{row['condition']:<3} {row['name']:<28} {detail}")

    # ---- instrumented runs --------------------------------------------
    print("\nRunning instrumented conditions...")
    t0 = time.time()
    full = run_instrumented("O_FULL", InstrumentedService, args.cycles, 1000)
    print(f"  O_FULL instrumented ({time.time()-t0:.0f}s)")
    t0 = time.time()
    rand = run_instrumented("H", InstrumentedRandomCuriosity, args.cycles, 1007)
    print(f"  H (Random Curiosity) instrumented ({time.time()-t0:.0f}s)")
    t0 = time.time()
    nofals = run_instrumented("D", InstrumentedNoFalsification, args.cycles, 1003)
    print(f"  D (No Falsification) instrumented ({time.time()-t0:.0f}s)")
    t0 = time.time()
    full_unc = run_instrumented("O_FULL_uncapped", InstrumentedService, args.cycles, 1000,
                                 max_hypotheses=200)
    print(f"  O_FULL uncapped instrumented ({time.time()-t0:.0f}s)")
    t0 = time.time()
    nofals_unc = run_instrumented("D_uncapped", InstrumentedNoFalsification, args.cycles, 1003,
                                   max_hypotheses=200)
    print(f"  D uncapped instrumented ({time.time()-t0:.0f}s)")

    # ---- B. random curiosity ------------------------------------------
    print("\nB. DID RANDOM CURIOSITY CHANGE BEHAVIOUR?")
    h_check = curiosity_effectiveness(full, rand)
    for label in ("eig_policy", "random_policy"):
        a = h_check[label]
        print(f"  {label:<14} mean score selected={a['mean_score_selected']} "
              f"(all candidates {a['mean_score_all_candidates']})  "
              f"top-decile hit rate={a['fraction_selected_in_top_decile']}  "
              f"rank corr={a['rank_correlation_score_vs_selection']}")
    print(f"  final-selection Jaccard: {h_check['final_selection_jaccard']}")
    print(f"  VERDICT: {h_check['verdict']}")

    # ---- C. contradictions ---------------------------------------------
    print("\nC. WHERE DO CONTRADICTIONS COME FROM?")
    c_full = contradiction_report(full)
    c_d = contradiction_report(nofals)
    c_full_u = contradiction_report(full_unc)
    c_d_u = contradiction_report(nofals_unc)
    print(f"  O_FULL  (hypothesis cap 15)  : subjects with competing expectations "
          f"max={c_full['max_subjects_with_competing_expectations']} "
          f"mean={c_full['mean_subjects_with_competing_expectations']}")
    print(f"  D       (hypothesis cap 15)  : subjects with competing expectations "
          f"max={c_d['max_subjects_with_competing_expectations']} "
          f"mean={c_d['mean_subjects_with_competing_expectations']}")
    print(f"  O_FULL  (cap removed)        : subjects with competing expectations "
          f"max={c_full_u['max_subjects_with_competing_expectations']} "
          f"mean={c_full_u['mean_subjects_with_competing_expectations']}")
    print(f"  D       (cap removed)        : subjects with competing expectations "
          f"max={c_d_u['max_subjects_with_competing_expectations']} "
          f"mean={c_d_u['mean_subjects_with_competing_expectations']}")
    print(f"  max contradiction count ever observed: "
          f"O_FULL={c_full['max_contradiction_count_observed']}  "
          f"D={c_d['max_contradiction_count_observed']}  "
          f"O_FULL_uncapped={c_full_u['max_contradiction_count_observed']}  "
          f"D_uncapped={c_d_u['max_contradiction_count_observed']}")
    print("  Final-cycle hypothesis sample (D, cap 15):")
    for h in (nofals["records"][-1]["hypotheses"][:8] if nofals["records"] else []):
        print(f"    {h['subject'][:18]:<18} -> {h['expectation'][:18]:<18} "
              f"support={h['support']:<4} contradiction={h['contradiction']:<4} "
              f"confidence={h['confidence']}")

    out = REPO_ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "title": "Ablation Mechanism Verification",
        "purpose": "Establish that each ablation perturbed the organism before any "
                   "outcome is interpreted.",
        "cycles": args.cycles,
        "perturbation_census": census,
        "random_curiosity_check": h_check,
        "contradiction_analysis": {
            "o_full_capped": c_full,
            "no_falsification_capped": c_d,
            "o_full_uncapped": c_full_u,
            "no_falsification_uncapped": c_d_u,
        },
        "hypothesis_dumps": {
            "o_full": hypothesis_dump(full),
            "no_falsification": hypothesis_dump(nofals),
        },
    }, indent=2), encoding="utf-8")
    print(f"\n  Full report written to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
