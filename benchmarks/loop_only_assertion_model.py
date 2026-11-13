"""CONFIRMATORY-LOOP-ONLY-ASSERTION-1.

A frozen confirmatory test of the loop-only subgroup model.  The exploratory
Q4 fit found that among never-served edges that ever formed a loop, the direct
temporal count had a positive Firth odds ratio (1.69, 0.85-3.36) while rank was
null (1.09, 0.62-1.90).  This block asks whether that count association is
present on twelve fresh seeds.

    logit P(asserted) = b0 + b_rank*z(log2(min_rank))
                        + b_count*z(direct_count) + seed fixed effects

The loop term is absent because every row in the population formed a loop.
The population, predictors, Firth estimator, seed fixed effects and primary
criterion are frozen before any fresh seed runs.  The replay uses the repaired
observer: cap-40 served windows plus a full-universe rank capture.

    python -m benchmarks.loop_only_assertion_model --freeze
    python -m benchmarks.loop_only_assertion_model --collect
    python -m benchmarks.loop_only_assertion_model --write
    python -m benchmarks.loop_only_assertion_model --check
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from benchmarks import engine_stamp                                      # noqa: E402
from benchmarks.never_served_assertion_model import (                     # noqa: E402
    _auc,
    _fit_firth,
    _p_value,
    _sigmoid,
)
from benchmarks.never_served_assertion_model_replication import (         # noqa: E402
    CAP,
    CYCLES,
    _run_seed,
)

ID = "CONFIRMATORY-LOOP-ONLY-ASSERTION-1"
FROZEN_ON = "2026-11-12"
SEEDS = list(range(20616101, 20616113))
CACHE = ROOT / ".scratch" / "loop_only_assertion_traces"
PREREG = ROOT / "docs" / "loop_only_assertion_model_prereg.json"
ARTIFACT = ROOT / "docs" / "loop_only_assertion_model.json"
PAGE = ROOT / "docs" / "LOOP-ONLY-ASSERTION-MODEL.md"
COLLISION_ALLOW = (PREREG, ARTIFACT)
MIN_LOOP_EDGES = 40
MIN_EVENTS = 10


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _trace_path(seed: int) -> Path:
    return CACHE / ("%d.json" % seed)


def build_prereg() -> dict:
    return {
        "prereg": ID,
        "kind": "loop_only_assertion_model_prereg",
        "status": "FROZEN, NOT FIT",
        "frozen_on": FROZEN_ON,
        "question": (
            "Among never-served world edges that ever form a reported loop, does "
            "the direct temporal count remain positively associated with final "
            "assertion after rank and seed are held fixed?"
        ),
        "reference": {
            "source": ".scratch/loop_forming_assertion_model.json",
            "status": "exploratory Q4 subgroup fit, not confirmatory",
            "n_loop": 61,
            "n_asserted": 26,
            "rank_or_firth": 1.09,
            "rank_ci95_firth": [0.62, 1.90],
            "count_or_firth": 1.69,
            "count_ci95_firth": [0.85, 3.36],
            "count_or_mle": 1.89,
            "count_ci95_mle": [0.92, 3.88],
            "count_lrt_p_mle": 0.067,
        },
        "design": {
            "seeds": SEEDS,
            "cells": len(SEEDS),
            "cycles": CYCLES,
            "cap": CAP,
            "world": (
                "generate_compositional_world(seed=, cycles=120) with the "
                "PHASE_ACQUISITION schedule and one replay per seed"
            ),
            "population": (
                "every world edge with zero direct served windows AND ever_loop=True; "
                "the loop term is therefore constant and is not estimated"
            ),
            "outcome": "asserted=true in the final structure",
            "rank": (
                "minimum 1-based position in the repaired observer's full pre-cap "
                "universe across all 120 cycles"
            ),
            "count": "final direct temporal transition count",
            "loop": (
                "ever_loop: at least one reported loop_candidate path contains the "
                "edge in either orientation in any cycle"
            ),
            "freshness": (
                "The collision scan over docs JSON is empty at freeze time. No seed "
                "in this block has been replayed before the freeze."
            ),
        },
        "model": {
            "family": "binary logistic regression",
            "formula": (
                "logit P(asserted) = b0 + b_rank*z(log2(min_rank)) "
                "+ b_count*z(direct_count) + seed fixed effects"
            ),
            "estimator": (
                "Firth penalized likelihood (Jeffreys prior); fixed before the run "
                "because the subgroup is small and the event count is limited"
            ),
            "standardization": "complete-case mean and population SD",
            "seed": "twelve-level fixed effect, first seed as reference",
            "interactions": "none",
            "selection": "none",
        },
        "inference": {
            "primary": (
                "Firth Wald 95% interval for the count odds ratio per 1 SD. "
                "The count coefficient is the single primary criterion."
            ),
            "secondary": (
                "Rank OR per 1 SD, reported descriptively with its interval; no "
                "rank-based verdict."
            ),
            "alpha": 0.05,
            "multiplicity": "one primary coefficient; rank is secondary and unadjusted",
            "no_causal_claim": "Observational subgroup model; no coefficient is causal.",
        },
        "criteria": [
            {"id": "C1", "name": "count direction", "test": "count OR > 1"},
            {"id": "C2", "name": "count interval", "test": "count 95% CI lower bound > 1"},
            {"id": "C3", "name": "gates", "test": "all confirmatory gates pass"},
        ],
        "verdicts": {
            "CONFIRMED": "C1-C3 all pass.",
            "DIRECTIONAL ONLY": "C1 and C3 pass, but the count interval includes 1.",
            "NOT CONFIRMED": "The count OR is at or below 1, or C3 fails.",
            "VOID": "A gate fails; no coefficient is read.",
        },
        "gates": {
            "M1_population": (
                "at least %d loop-forming never-served edges and %d asserted events; "
                "no duplicate seed-edge rows" % (MIN_LOOP_EDGES, MIN_EVENTS)
            ),
            "M2_rank_coverage": "at least 95% of loop-forming edges have a finite rank",
            "M3_no_duplicate": "one row per seed-edge",
            "M4_seed_levels": "all twelve seeds contribute rows",
            "M5_convergence": "Firth fit converges with finite coefficients and information",
            "M6_complete": "every fitted row has a finite rank and a count",
            "M7_loop_only": "every fitted row has ever_loop=true",
        },
        "sample_size": {
            "planned_seeds": len(SEEDS),
            "minimum_loop_edges": MIN_LOOP_EDGES,
            "minimum_events": MIN_EVENTS,
            "power_calculation": (
                "none. Twelve seeds are used to improve on the exploratory 61-edge "
                "subgroup, not to claim a powered test of the exploratory point estimate."
            ),
        },
        "result": ARTIFACT.relative_to(ROOT).as_posix(),
        "not_evidence": (
            "A twelve-seed observational subgroup model in one synthetic world family. "
            "It does not establish causation, capability, retention, transfer or a "
            "general engine property."
        ),
    }


def _validate_prereg(body: dict) -> list[str]:
    found: list[str] = []
    if body.get("prereg") != ID:
        found.append("prereg id")
    if body.get("status") not in ("FROZEN, NOT FIT", "FROZEN, FIT"):
        found.append("prereg status")
    design = body.get("design") or {}
    if design.get("seeds") != SEEDS:
        found.append("seed block")
    if design.get("cycles") != CYCLES or design.get("cap") != CAP:
        found.append("cycles or cap")
    if [row.get("id") for row in body.get("criteria") or []] != ["C1", "C2", "C3"]:
        found.append("criteria")
    if set(body.get("verdicts") or {}) != {"CONFIRMED", "DIRECTIONAL ONLY",
                                           "NOT CONFIRMED", "VOID"}:
        found.append("verdict vocabulary")
    if body.get("result") != ARTIFACT.relative_to(ROOT).as_posix():
        found.append("result path")
    return found


def collect() -> int:
    if not PREREG.exists():
        raise SystemExit("freeze the preregistration first")
    CACHE.mkdir(parents=True, exist_ok=True)
    for seed in SEEDS:
        path = _trace_path(seed)
        if path.exists():
            print("cached", seed)
            continue
        trace = _run_seed(seed)
        path.write_text(json.dumps(trace, indent=1) + "\n", encoding="utf-8")
        print("collected", seed, "never_served", trace["never_served"],
              "loop", sum(1 for row in trace["rows"] if row["ever_loop"]),
              "asserted", sum(1 for row in trace["rows"] if row["asserted"]))
    return 0


def _load_traces() -> list[dict]:
    missing = [seed for seed in SEEDS if not _trace_path(seed).exists()]
    if missing:
        raise SystemExit("missing cached traces: %r; run --collect" % missing)
    return [_load(_trace_path(seed)) for seed in SEEDS]


def _loop_rows(traces: list[dict]) -> list[dict]:
    rows = []
    for trace in traces:
        rows.extend(row for row in trace["rows"] if row["ever_loop"])
    return rows


def _fit_loop_only(rows: list[dict], use_seeds=None, with_loo=True) -> dict:
    use_seeds = list(SEEDS) if use_seeds is None else list(use_seeds)
    data = []
    for row in rows:
        if row["seed"] not in use_seeds:
            continue
        item = dict(row)
        item["asserted_i"] = 1.0 if row["asserted"] else 0.0
        data.append(item)
    data = [row for row in data if row["min_rank"] is not None]
    rank_vals = [math.log2(float(row["min_rank"])) for row in data]
    count_vals = [float(row["direct_count"]) for row in data]
    rank_mean, rank_sd = statistics.fmean(rank_vals), statistics.pstdev(rank_vals)
    count_mean, count_sd = statistics.fmean(count_vals), statistics.pstdev(count_vals)
    if rank_sd == 0 or count_sd == 0:
        raise ValueError("constant predictor")
    levels = use_seeds[1:]
    X = [[1.0,
          (math.log2(float(row["min_rank"])) - rank_mean) / rank_sd,
          (float(row["direct_count"]) - count_mean) / count_sd]
         + [1.0 if row["seed"] == seed else 0.0 for seed in levels]
         for row in data]
    y = [row["asserted_i"] for row in data]
    fit = _fit_firth(X, y)
    names = ["intercept", "rank_log2_z", "count_z"] + ["seed_%d" % seed for seed in levels]
    coefs = []
    for name, beta, se in zip(names, fit["beta"], fit["se"]):
        z = beta / se if se else float("nan")
        coefs.append({
            "name": name,
            "beta": beta,
            "se": se,
            "z": z,
            "p": _p_value(z) if math.isfinite(z) else None,
            "odds_ratio": math.exp(beta),
            "ci95": [math.exp(beta - 1.959963984540054 * se),
                     math.exp(beta + 1.959963984540054 * se)],
        })

    def predict(row, rank_shift=0.0, count_shift=0.0):
        values = [1.0,
                  (math.log2(float(row["min_rank"])) - rank_mean) / rank_sd + rank_shift,
                  (float(row["direct_count"]) - count_mean) / count_sd + count_shift]
        values += [1.0 if row["seed"] == seed else 0.0 for seed in levels]
        return _sigmoid(sum(value * beta for value, beta in zip(values, fit["beta"])))

    ame_rank = statistics.fmean(predict(row, rank_shift=1.0) - predict(row)
                                for row in data)
    ame_count = statistics.fmean(predict(row, count_shift=1.0) - predict(row)
                                 for row in data)
    loo = []
    if with_loo:
        for seed in SEEDS:
            sub = [row for row in data if row["seed"] != seed]
            try:
                fold = _fit_loop_only(sub, [s for s in SEEDS if s != seed], with_loo=False)
                loo.append({"held_out": seed, "rank": fold["rank"]["beta"],
                            "count": fold["count"]["beta"]})
            except Exception as exc:
                loo.append({"held_out": seed, "error": type(exc).__name__ + ": " + str(exc)})
    return {
        "data": data,
        "fit": fit,
        "coefs": coefs,
        "rank": next(row for row in coefs if row["name"] == "rank_log2_z"),
        "count": next(row for row in coefs if row["name"] == "count_z"),
        "rank_mean": rank_mean,
        "rank_sd": rank_sd,
        "count_mean": count_mean,
        "count_sd": count_sd,
        "auc": _auc(y, fit["prob"]),
        "brier": statistics.fmean((p - t) ** 2 for p, t in zip(fit["prob"], y)),
        "ame": {"rank_per_sd": ame_rank, "count_per_sd": ame_count},
        "loo": loo,
    }


def _gates(rows: list[dict], fitted: dict) -> dict:
    data = fitted["data"]
    return {
        "M1_population": (
            len(rows) >= MIN_LOOP_EDGES
            and sum(1 for row in data if row["asserted"]) >= MIN_EVENTS
            and len({(row["seed"], row["edge"]) for row in rows}) == len(rows)
        ),
        "M2_rank_coverage": len(data) / len(rows) >= 0.95 if rows else False,
        "M3_no_duplicate": len({(row["seed"], row["edge"]) for row in rows}) == len(rows),
        "M4_seed_levels": len({row["seed"] for row in data}) == len(SEEDS),
        "M5_convergence": bool(fitted["fit"]["converged"]),
        "M6_complete": all(row["min_rank"] is not None for row in data),
        "M7_loop_only": all(bool(row["ever_loop"]) for row in data),
    }


def build() -> dict:
    prereg = _load(PREREG)
    found = _validate_prereg(prereg)
    from benchmarks.presence_cap_experiment import seed_collisions
    if seed_collisions(SEEDS, allow=COLLISION_ALLOW):
        found.append("seed collision")
    if found:
        raise SystemExit("REFUSED: " + "; ".join(found))

    traces = _load_traces()
    rows = _loop_rows(traces)
    fitted = _fit_loop_only(rows)
    gates = _gates(rows, fitted)
    all_gates = all(gates.values())
    criteria = {
        "C1_count_direction": fitted["count"]["odds_ratio"] > 1.0,
        "C2_count_interval": fitted["count"]["ci95"][0] > 1.0,
        "C3_gates": all_gates,
    }
    if not all_gates:
        verdict = "VOID"
    elif criteria["C1_count_direction"] and criteria["C2_count_interval"]:
        verdict = "CONFIRMED"
    elif criteria["C1_count_direction"]:
        verdict = "DIRECTIONAL ONLY"
    else:
        verdict = "NOT CONFIRMED"
    data = fitted["data"]
    summary = {
        "n_never_served": sum(trace["never_served"] for trace in traces),
        "n_loop": len(rows),
        "n_complete": len(data),
        "n_events": sum(1 for row in data if row["asserted"]),
        "rank": fitted["rank"],
        "count": fitted["count"],
        "average_marginal_effects": fitted["ame"],
        "auc": fitted["auc"] if math.isfinite(fitted["auc"]) else None,
        "brier": fitted["brier"],
        "gates": gates,
        "all_gates": all_gates,
        "criteria": criteria,
        "verdict": verdict,
        "excluded": [{"seed": row["seed"], "edge": row["edge"],
                      "reason": "no finite full-universe rank"}
                     for row in rows if row["min_rank"] is None],
    }
    return engine_stamp.stamp({
        "kind": "loop_only_assertion_model",
        "status": "RUN",
        "prereg": PREREG.relative_to(ROOT).as_posix(),
        "question": prereg["question"],
        "scope": (
            "Twelve fresh seeds, one compositional world family, 120 cycles, cap 40, "
            "loop-forming never-served edges only."
        ),
        "reference": prereg["reference"],
        "design": prereg["design"],
        "model": prereg["model"],
        "inference": prereg["inference"],
        "criteria": prereg["criteria"],
        "gates": prereg["gates"],
        "seeds": [{
            "seed": trace["seed"],
            "never_served": trace["never_served"],
            "loop": sum(1 for row in trace["rows"] if row["ever_loop"]),
            "asserted": trace["never_served_asserted"],
            "loop_asserted": sum(1 for row in trace["rows"]
                                 if row["ever_loop"] and row["asserted"]),
        } for trace in traces],
        "rows": rows,
        "summary": summary,
        "leave_one_seed_out": fitted["loo"],
        "not_evidence": prereg["not_evidence"],
    })


def _fmt(value, digits=3):
    return "NA" if value is None else ("%.*f" % (digits, value))


def _fmt_p(value):
    return "NA" if value is None else "%.2e" % value


def render(art: dict) -> str:
    summary = art["summary"]
    rank = summary["rank"]
    count = summary["count"]
    ref = art["reference"]
    lines = [
        "# Loop-only assertion model — confirmatory",
        "",
        "Generated from `%s` by `python -m benchmarks.loop_only_assertion_model --write`. "
        "Do not edit by hand." % ARTIFACT.relative_to(ROOT),
        "",
        "**Verdict: `%s`.** The design was frozen in `%s` before the fresh block ran."
        % (summary["verdict"], PREREG.relative_to(ROOT)),
        "",
        "## Design",
        "",
        "- Seeds: **%s**." % ", ".join(str(seed) for seed in art["design"]["seeds"]),
        "- **%d** cycles, cap **%d**, PHASE_ACQUISITION, repaired full-universe rank capture."
        % (art["design"]["cycles"], art["design"]["cap"]),
        "- Population: never-served world edges that ever formed a reported loop.",
        "- Model: Firth logistic; rank and count per 1 SD; twelve seed fixed effects.",
        "- Primary criterion: count OR > 1 and its 95% CI lower bound > 1.",
        "",
        "## Result",
        "",
        "| Quantity | Exploratory Q4 | Fresh block |",
        "| --- | ---: | ---: |",
        "| Loop-forming edges | %d | %d |" % (ref["n_loop"], summary["n_loop"]),
        "| Asserted events | %d | %d |" % (ref["n_asserted"], summary["n_events"]),
        "| Count OR | %.2f | %.2f |" % (ref["count_or_firth"], count["odds_ratio"]),
        "| Count 95%% CI | %.2f–%.2f | %.2f–%.2f |"
        % (ref["count_ci95_firth"][0], ref["count_ci95_firth"][1],
           count["ci95"][0], count["ci95"][1]),
        "| Rank OR | %.2f | %.2f |" % (ref["rank_or_firth"], rank["odds_ratio"]),
        "| Rank 95%% CI | %.2f–%.2f | %.2f–%.2f |"
        % (ref["rank_ci95_firth"][0], ref["rank_ci95_firth"][1],
           rank["ci95"][0], rank["ci95"][1]),
        "| AUC | — | %s |" % _fmt(summary["auc"]),
        "| Brier | — | %s |" % _fmt(summary["brier"], 4),
        "",
        "## Count association",
        "",
        "The primary estimate is the Firth count OR per 1 SD: **%.2f** "
        "(95%% CI **%.2f–%.2f**, p **%s**). The point estimate is %s 1; the interval %s 1."
        % (count["odds_ratio"], count["ci95"][0], count["ci95"][1],
           _fmt_p(count["p"]), "above" if count["odds_ratio"] > 1 else "at or below",
           "excludes" if count["ci95"][0] > 1 else "includes"),
        "",
        "Average marginal effect of count +1 SD: **%+.3f** probability."
        % summary["average_marginal_effects"]["count_per_sd"],
        "",
        "## Rank (secondary)",
        "",
        "Rank OR per 1 SD: **%.2f** (95%% CI **%.2f–%.2f**). No rank-based verdict was "
        "pre-specified; this is reported descriptively."
        % (rank["odds_ratio"], rank["ci95"][0], rank["ci95"][1]),
        "",
        "## Gates",
        "",
        "| Gate | Passes |",
        "| --- | --- |",
    ]
    for name, passed in summary["gates"].items():
        lines.append("| `%s` | %s |" % (name, "yes" if passed else "no"))
    lines += [
        "",
        "## Leave-one-seed-out",
        "",
        "| Held out | Rank beta | Count beta |",
        "| ---: | ---: | ---: |",
    ]
    for row in art["leave_one_seed_out"]:
        if "error" in row:
            lines.append("| %d | %s | — |" % (row["held_out"], row["error"]))
        else:
            lines.append("| %d | %.3f | %.3f |"
                         % (row["held_out"], row["rank"], row["count"]))
    lines += [
        "",
        "## Per seed",
        "",
        "| Seed | Never served | Loop-forming | Asserted | Loop-forming asserted |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in art["seeds"]:
        lines.append("| %d | %d | %d | %d | %d |" % (
            row["seed"], row["never_served"], row["loop"], row["asserted"],
            row["loop_asserted"]))
    lines += [
        "",
        "## What this does and does not establish",
        "",
        "This is a confirmatory subgroup test on a fresh twelve-seed block, not a "
        "capability or causal result. It conditions on loop formation, so it does not "
        "test whether loops cause assertion or whether retention matters. The sample "
        "is still modest, the world family is synthetic, and the model is observational.",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(art: dict | None = None) -> list[str]:
    art = _load(ARTIFACT) if art is None else art
    found: list[str] = []
    if art.get("kind") != "loop_only_assertion_model":
        found.append("artifact kind")
    if art.get("status") != "RUN":
        found.append("artifact status")
    if engine_stamp.missing(art):
        found.append("stamp: %r" % (engine_stamp.missing(art),))
    found.extend(_validate_prereg(_load(PREREG)))
    if art.get("prereg") != PREREG.relative_to(ROOT).as_posix():
        found.append("prereg path")
    rows = art.get("rows") or []
    if len({(row["seed"], row["edge"]) for row in rows}) != len(rows):
        found.append("duplicate rows")
    fitted = _fit_loop_only(rows)
    summary = art.get("summary") or {}
    if summary.get("n_loop") != len(rows):
        found.append("summary loop")
    if summary.get("n_complete") != len(fitted["data"]):
        found.append("summary complete")
    if summary.get("n_events") != sum(1 for row in fitted["data"] if row["asserted"]):
        found.append("summary events")
    if summary.get("rank") != fitted["rank"]:
        found.append("summary rank")
    if summary.get("count") != fitted["count"]:
        found.append("summary count")
    gates = _gates(rows, fitted)
    if summary.get("gates") != gates:
        found.append("summary gates")
    expected = ("VOID" if not all(gates.values())
                else "CONFIRMED" if (fitted["count"]["odds_ratio"] > 1
                                     and fitted["count"]["ci95"][0] > 1)
                else "DIRECTIONAL ONLY" if fitted["count"]["odds_ratio"] > 1
                else "NOT CONFIRMED")
    if summary.get("verdict") != expected:
        found.append("summary verdict")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("page stale")
    from benchmarks.presence_cap_experiment import seed_collisions
    if seed_collisions(SEEDS, allow=COLLISION_ALLOW):
        found.append("seed collision")
    return found


def freeze() -> int:
    if PREREG.exists():
        print("REFUSED: prereg exists")
        return 2
    PREREG.write_text(json.dumps(engine_stamp.stamp(build_prereg()), indent=1) + "\n",
                      encoding="utf-8")
    print("froze %s" % PREREG.relative_to(ROOT))
    return 0


def write() -> int:
    body = build()
    ARTIFACT.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(body), encoding="utf-8")
    prereg = _load(PREREG)
    prereg["status"] = "FROZEN, FIT"
    prereg["completed_on"] = FROZEN_ON
    prereg["verdict"] = body["summary"]["verdict"]
    PREREG.write_text(json.dumps(prereg, indent=1) + "\n", encoding="utf-8")
    s = body["summary"]
    print("loop-only assertion model: %s %s" % (s["verdict"], json.dumps({
        "n_loop": s["n_loop"],
        "events": s["n_events"],
        "count_or": round(s["count"]["odds_ratio"], 3),
        "count_ci": [round(v, 3) for v in s["count"]["ci95"]],
        "rank_or": round(s["rank"]["odds_ratio"], 3),
    })))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no artifact; run --write")
    art = _load(ARTIFACT)
    found = problems(art)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    s = art["summary"]
    print("loop-only assertion model: %s %s" % (s["verdict"], json.dumps({
        "n_loop": s["n_loop"],
        "events": s["n_events"],
        "count_or": round(s["count"]["odds_ratio"], 3),
        "count_ci": [round(v, 3) for v in s["count"]["ci95"]],
    })))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--collect", action="store_true")
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.freeze:
        return freeze()
    if args.collect:
        return collect()
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
