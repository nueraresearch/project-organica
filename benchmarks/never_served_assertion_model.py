"""NEVER-SERVED-ASSERTION-MODEL-1.

A frozen, Firth-penalized logistic model of final assertion across all
never-served world edges:

    logit P(asserted) = b0 + b_loop * loop + b_rank * z(log2(min_rank))
                        + b_count * z(direct_count) + seed fixed effects

The loop coefficient is quasi-separated: all 26 assertions have a loop and 118
complete-case edges without a loop have no assertion.  An ordinary logistic MLE
does not have a finite estimate for that coefficient, so the model is fitted
with the Jeffreys-prior Firth penalty fixed before the fit.

The module writes the preregistration, fits the model, and writes the result.
It runs no engine cell; it reads the existing six-seed rank capture.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
RANKS = ROOT / ".scratch" / "never_served_ranks.json"
PREREG = ROOT / "docs" / "never_served_assertion_model_prereg.json"
PREREG_PAGE = ROOT / "docs" / "NEVER-SERVED-ASSERTION-MODEL-PREREGISTRATION.md"
RESULT = ROOT / "docs" / "never_served_assertion_model.json"
RESULT_PAGE = ROOT / "docs" / "NEVER-SERVED-ASSERTION-MODEL-RESULT.md"

ID = "NEVER-SERVED-ASSERTION-MODEL-1"
FROZEN_ON = "2026-11-12"
SEEDS = (20611601, 20611602, 20611603, 20611604, 20611605, 20611606)
CAP = 40
CYCLES = 120
PREDICTORS = ("loop", "rank_log2_z", "count_z")


def build_prereg() -> dict:
    return {
        "prereg": ID,
        "status": "FROZEN, NOT FIT",
        "frozen_on": FROZEN_ON,
        "question": (
            "Across every never-served world edge in the six Q4 seeds, what is the "
            "association between final assertion and (a) ever forming a reported loop, "
            "(b) the edge's best full-universe prediction rank, and (c) its direct "
            "temporal count, with seed held fixed?"
        ),
        "population": {
            "definition": (
                "Every world edge with served=false in .scratch/carrier_census.json: "
                "180 edges over seeds 20611601-20611606, of which 26 are asserted."
            ),
            "unit": "one edge within one seed",
            "outcome": "asserted=true in the final structure, from the carrier census",
            "complete_case": (
                "An edge must have a finite minimum full-universe rank; one count-4, "
                "never-asserted, no-loop edge has no rank and is excluded. The fit "
                "therefore uses 179 edges and 26 events."
            ),
            "no_imputation": "Missing rank is not imputed; the excluded row is named in the result.",
        },
        "predictors": {
            "loop": (
                "Binary ever_loop from the census: at least one reported loop candidate "
                "contains the edge in either orientation in any of the 120 cycles."
            ),
            "rank": (
                "Minimum full-universe prediction rank across all 120 cycles, measured at "
                "cap 40 with the repaired observer. Lower is better. Analyzed as "
                "log2(min_rank), then standardized over the 179 complete cases."
            ),
            "count": (
                "Direct temporal count at the end of the run, from the census; "
                "standardized over the 179 complete cases."
            ),
            "seed": "Six-level fixed effect; treatment coded with 20611601 as reference.",
            "interactions": "None.",
            "selection": "No variable selection; all three predictors and seed enter once.",
        },
        "model": {
            "family": "binary logistic regression",
            "formula": (
                "logit P(asserted) = b0 + b_loop*loop + b_rank*z(log2(min_rank)) "
                "+ b_count*z(direct_count) + seed fixed effects"
            ),
            "estimator": (
                "Firth penalized likelihood (Jeffreys prior), because loop is "
                "quasi-separated: all 26 events have loop=1 and all 118 complete-case "
                "loop=0 edges are non-events."
            ),
            "why_firth": (
                "The ordinary MLE for the loop coefficient diverges under this zero cell. "
                "Firth returns a finite estimate; it does not turn the zero cell into "
                "evidence of an infinite effect."
            ),
            "penalty": "0.5 * log|X' W X|, with W = diag(p*(1-p)).",
            "standardization": "Complete-case mean and population SD; no outcome-based scaling.",
            "convergence": "max absolute Newton step < 1e-8, at most 200 iterations.",
        },
        "inference": {
            "primary": (
                "Firth Wald 95% confidence intervals for the three reported coefficients, "
                "from the inverse information at the penalized estimate."
            ),
            "odds_ratios": (
                "exp(beta): loop is a 0/1 contrast; rank and count are per 1 SD. A rank "
                "odds ratio below 1 means a worse (larger) rank is associated with lower "
                "assertion."
            ),
            "marginal_effects": (
                "Average marginal effects on the probability scale, computed at the "
                "observed covariates: loop 1 vs 0; rank +1 SD; count +1 SD."
            ),
            "sensitivity": (
                "Leave-one-seed-out refits with the same full-sample standardization; "
                "the range of each coefficient is reported. No cluster-robust SE claim is made."
            ),
            "alpha": 0.05,
            "multiplicity": "One model, three reported coefficients; intervals are unadjusted.",
            "no_verdict": (
                "The model is descriptive. No coefficient-significance rule selects a "
                "verdict, and no causal claim is licensed."
            ),
        },
        "expected_directions": {
            "loop": "positive association; the sample has no asserted edge without a loop",
            "rank": "negative coefficient for log2 rank; a worse rank should reduce assertion",
            "count": "positive association; more direct transitions should increase assertion",
        },
        "gates": {
            "M1_population": "180 never-served edges, 26 asserted; no duplicate seed-edge rows",
            "M2_rank_coverage": "at least 95% of never-served edges have a finite minimum rank",
            "M3_label_replay": "the rank replay reproduces every census asserted and ever_loop label",
            "M4_loop_variation": "both loop levels are present; the zero cell is disclosed, not hidden",
            "M5_convergence": "the Firth fit converges with finite coefficients and information matrix",
            "M6_complete_predictors": "every fitted row has loop, rank and count; no silent row loss",
            "M7_seed_levels": "all six seeds contribute rows and the seed fixed effect is full rank",
        },
        "decision": {
            "kind": "descriptive fit, not a verdict",
            "reading": (
                "Report the three adjusted odds ratios, their intervals, the average "
                "marginal effects, the separation table, and the leave-one-seed-out ranges. "
                "A coefficient whose interval includes 1 is not read as an association."
            ),
            "labels": {
                "fit": "FIT",
                "void": "VOID: a gate failed; no coefficient is read",
            },
        },
        "data_sources": {
            "census": ".scratch/carrier_census.json",
            "ranks": ".scratch/never_served_ranks.json",
            "rank_capture": (
                "A fresh replay of the same six Q4 seeds, 120 cycles, cap 40, using the "
                "repaired observer's full-universe call; each seed's asserted fingerprint "
                "and count match docs/assertion_provenance.json."
            ),
        },
        "engine": {"version": "0.15.0", "cap": CAP, "cycles": CYCLES, "edit": "none"},
        "not_evidence": (
            "An observational model on one synthetic world family and six seeds, with 26 "
            "events. Firth stabilizes a separated coefficient; it does not establish "
            "causation, capability, retention, transfer, or a general engine property."
        ),
    }


def render_prereg(doc: dict) -> str:
    p = doc["population"]; pr = doc["predictors"]; m = doc["model"]; inf = doc["inference"]
    lines = [
        "# NEVER-SERVED-ASSERTION-MODEL-1 — preregistration",
        "",
        "**Status.** %s. Generated from `%s`; never edited by hand."
        % (doc["status"], PREREG.relative_to(ROOT).as_posix()),
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Preregistration | `%s` |" % doc["prereg"],
        "| Freeze date | %s |" % doc["frozen_on"],
        "| Population | %s |" % p["definition"],
        "| Outcome | %s |" % p["outcome"],
        "| Complete cases | %s |" % p["complete_case"],
        "| Model | %s |" % m["formula"],
        "| Estimator | %s |" % m["estimator"],
        "| Result | %s |" % ("`%s`" % doc["result"] if doc.get("result") else "not fitted"),
        "",
        "## Predictors",
        "",
        "| Name | Definition |",
        "| --- | --- |",
        "| `loop` | %s |" % pr["loop"],
        "| `rank` | %s |" % pr["rank"],
        "| `count` | %s |" % pr["count"],
        "| `seed` | %s |" % pr["seed"],
        "",
        "No interactions. No variable selection. Rank and count are standardized over the "
        "complete cases; the standardization does not use the outcome.",
        "",
        "## Why Firth",
        "",
        m["why_firth"],
        "",
        "The penalty is %s" % m["penalty"],
        "",
        "## Inference",
        "",
        inf["primary"],
        "",
        inf["odds_ratios"],
        "",
        inf["marginal_effects"],
        "",
        inf["sensitivity"],
        "",
        inf["no_verdict"],
        "",
        "## Expected directions",
        "",
        "| Predictor | Direction |",
        "| --- | --- |",
    ]
    for name, direction in doc["expected_directions"].items():
        lines.append("| `%s` | %s |" % (name, direction))
    lines += [
        "",
        "## Gates",
        "",
        "| Gate | Rule |",
        "| --- | --- |",
    ]
    for gate, rule in doc["gates"].items():
        lines.append("| `%s` | %s |" % (gate, rule))
    lines += [
        "",
        "## Reading",
        "",
        doc["decision"]["reading"],
        "",
        "## What this does not license",
        "",
        doc["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def _load_rows() -> list[dict]:
    doc = json.loads(RANKS.read_text(encoding="utf-8"))
    rows = doc["rows"]
    for row in rows:
        row["loop"] = 1.0 if row["ever_loop"] else 0.0
        row["asserted_i"] = 1.0 if row["asserted"] else 0.0
    return rows


def _inverse(a: list[list[float]]) -> list[list[float]]:
    n = len(a)
    m = [list(map(float, row)) + [1.0 if i == j else 0.0 for j in range(n)]
         for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-14:
            raise ValueError("singular information matrix")
        m[col], m[pivot] = m[pivot], m[col]
        pv = m[col][col]
        for j in range(2 * n):
            m[col][j] /= pv
        for r in range(n):
            if r != col and m[r][col] != 0.0:
                f = m[r][col]
                for j in range(2 * n):
                    m[r][j] -= f * m[col][j]
    return [row[n:] for row in m]


def _logdet(a: list[list[float]]) -> float:
    n = len(a)
    m = [list(map(float, row)) for row in a]
    out = 0.0
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-14:
            return -math.inf
        if pivot != col:
            m[col], m[pivot] = m[pivot], m[col]
            out += math.log(abs(m[col][col]))
        else:
            out += math.log(abs(m[col][col]))
        pv = m[col][col]
        for r in range(col + 1, n):
            f = m[r][col] / pv
            for j in range(col, n):
                m[r][j] -= f * m[col][j]
    return out


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def _quad(x: list[float], a: list[list[float]]) -> float:
    n = len(x)
    return sum(x[i] * a[i][j] * x[j] for i in range(n) for j in range(n))


def _fit_firth(X: list[list[float]], y: list[float], max_iter: int = 200,
               tol: float = 1e-8) -> dict:
    n, p = len(X), len(X[0])
    beta = [0.0] * p
    history = []
    for iteration in range(1, max_iter + 1):
        eta = [sum(x[j] * beta[j] for j in range(p)) for x in X]
        prob = [_sigmoid(v) for v in eta]
        w = [max(pr * (1.0 - pr), 1e-12) for pr in prob]
        info = [[sum(w[i] * X[i][j] * X[i][k] for i in range(n)) for k in range(p)]
                for j in range(p)]
        # A tiny jitter keeps the seed-dummy block invertible at extreme probabilities.
        for j in range(p):
            info[j][j] += 1e-10
        inv = _inverse(info)
        lev = [w[i] * _quad(X[i], inv) for i in range(n)]
        score = [sum((y[i] - prob[i] + lev[i] * (0.5 - prob[i])) * X[i][j]
                     for i in range(n)) for j in range(p)]
        ll = sum(y[i] * math.log(max(prob[i], 1e-15))
                 + (1.0 - y[i]) * math.log(max(1.0 - prob[i], 1e-15))
                 for i in range(n)) + 0.5 * _logdet(info)
        delta = [sum(inv[j][k] * score[k] for k in range(p)) for j in range(p)]
        step = 1.0
        accepted = False
        while step > 1e-8:
            trial = [beta[j] + step * delta[j] for j in range(p)]
            eta_t = [sum(x[j] * trial[j] for j in range(p)) for x in X]
            prob_t = [_sigmoid(v) for v in eta_t]
            w_t = [max(pr * (1.0 - pr), 1e-12) for pr in prob_t]
            info_t = [[sum(w_t[i] * X[i][j] * X[i][k] for i in range(n)) for k in range(p)]
                      for j in range(p)]
            for j in range(p):
                info_t[j][j] += 1e-10
            ll_t = sum(y[i] * math.log(max(prob_t[i], 1e-15))
                       + (1.0 - y[i]) * math.log(max(1.0 - prob_t[i], 1e-15))
                       for i in range(n)) + 0.5 * _logdet(info_t)
            if ll_t >= ll - 1e-12:
                beta = trial
                accepted = True
                break
            step *= 0.5
        history.append({"iteration": iteration, "loglik_penalized": ll,
                        "max_score": max(abs(v) for v in score), "step": step})
        if not accepted or max(abs(step * d) for d in delta) < tol:
            break
    eta = [sum(x[j] * beta[j] for j in range(p)) for x in X]
    prob = [_sigmoid(v) for v in eta]
    w = [max(pr * (1.0 - pr), 1e-12) for pr in prob]
    info = [[sum(w[i] * X[i][j] * X[i][k] for i in range(n)) for k in range(p)]
            for j in range(p)]
    for j in range(p):
        info[j][j] += 1e-10
    inv = _inverse(info)
    return {"beta": beta, "se": [math.sqrt(max(inv[j][j], 0.0)) for j in range(p)],
            "prob": prob, "info": info, "iterations": iteration,
            "max_abs_step": max(abs(history[-1]["step"] * d) for d in delta) if history else None,
            "loglik_penalized": history[-1]["loglik_penalized"] if history else None,
            "converged": bool(history and history[-1]["max_score"] < 1e-5),
            "history": history}


def _auc(y: list[float], p: list[float]) -> float:
    pos = [v for v, t in zip(p, y) if t == 1.0]
    neg = [v for v, t in zip(p, y) if t == 0.0]
    if not pos or not neg:
        return float("nan")
    wins = 0.0
    for a in pos:
        for b in neg:
            wins += 1.0 if a > b else 0.5 if a == b else 0.0
    return wins / (len(pos) * len(neg))


def _p_value(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))


def _fit(rows: list[dict], use_seeds: list[int] | None = None) -> dict:
    use_seeds = list(SEEDS) if use_seeds is None else list(use_seeds)
    data = [r for r in rows if r["min_rank"] is not None and r["seed"] in use_seeds]
    rank_vals = [math.log2(r["min_rank"]) for r in data]
    count_vals = [float(r["direct_count"]) for r in data]
    rank_mean, rank_sd = statistics.fmean(rank_vals), statistics.pstdev(rank_vals)
    count_mean, count_sd = statistics.fmean(count_vals), statistics.pstdev(count_vals)
    if rank_sd == 0 or count_sd == 0:
        raise ValueError("constant predictor")
    ref = use_seeds[0]
    levels = [s for s in use_seeds if s != ref]
    X = [[1.0, r["loop"], (math.log2(r["min_rank"]) - rank_mean) / rank_sd,
          (float(r["direct_count"]) - count_mean) / count_sd]
         + [1.0 if r["seed"] == s else 0.0 for s in levels] for r in data]
    y = [r["asserted_i"] for r in data]
    fit = _fit_firth(X, y)
    names = ["intercept"] + list(PREDICTORS) + ["seed_%d" % s for s in levels]
    coefs = []
    for name, b, se in zip(names, fit["beta"], fit["se"]):
        z = b / se if se else float("nan")
        coefs.append({"name": name, "beta": b, "se": se, "z": z,
                      "p": _p_value(z) if math.isfinite(z) else None,
                      "odds_ratio": math.exp(b) if abs(b) < 700 else float("inf"),
                      "ci95": [math.exp(b - 1.959963984540054 * se),
                               math.exp(b + 1.959963984540054 * se)]
                      if abs(b) < 700 else [None, None]})
    # Average marginal effects, holding seed and the other predictors at observed values.
    def predict(row, loop=None, rank_shift=0.0, count_shift=0.0):
        vals = [1.0, row["loop"] if loop is None else loop,
                (math.log2(row["min_rank"]) - rank_mean) / rank_sd + rank_shift,
                (float(row["direct_count"]) - count_mean) / count_sd + count_shift]
        vals += [1.0 if row["seed"] == s else 0.0 for s in levels]
        return _sigmoid(sum(v * b for v, b in zip(vals, fit["beta"])))
    ame_loop = statistics.fmean(predict(r, loop=1.0) - predict(r, loop=0.0) for r in data)
    ame_rank = statistics.fmean(predict(r, rank_shift=1.0) - predict(r) for r in data)
    ame_count = statistics.fmean(predict(r, count_shift=1.0) - predict(r) for r in data)
    # Calibration in five equal-count bins.
    order = sorted(range(len(data)), key=lambda i: fit["prob"][i])
    bins = []
    for b in range(5):
        idx = order[b * len(order) // 5:(b + 1) * len(order) // 5]
        bins.append({"bin": b + 1, "n": len(idx),
                     "mean_predicted": statistics.fmean(fit["prob"][i] for i in idx),
                     "observed": statistics.fmean(y[i] for i in idx)})
    return {
        "data": data, "X": X, "y": y, "fit": fit, "coefs": coefs,
        "rank_mean": rank_mean, "rank_sd": rank_sd,
        "count_mean": count_mean, "count_sd": count_sd,
        "levels": levels, "ref": ref,
        "auc": _auc(y, fit["prob"]),
        "brier": statistics.fmean((p - t) ** 2 for p, t in zip(fit["prob"], y)),
        "ame": {"loop": ame_loop, "rank_per_sd": ame_rank, "count_per_sd": ame_count},
        "calibration": bins,
    }


def _separation(rows: list[dict]) -> dict:
    tab = Counter((bool(r["ever_loop"]), bool(r["asserted"])) for r in rows
                  if r["min_rank"] is not None)
    return {"loop_1_asserted": tab[(True, True)], "loop_1_not": tab[(True, False)],
            "loop_0_asserted": tab[(False, True)], "loop_0_not": tab[(False, False)]}


def fit_result(prereg: dict) -> dict:
    rows = _load_rows()
    complete = [r for r in rows if r["min_rank"] is not None]
    fitted = _fit(rows)
    loo = []
    for seed in SEEDS:
        sub = [r for r in rows if r["seed"] != seed]
        try:
            f = _fit(sub, [s for s in SEEDS if s != seed])
            loo.append({"held_out": seed,
                        "loop": f["coefs"][1]["beta"],
                        "rank": f["coefs"][2]["beta"],
                        "count": f["coefs"][3]["beta"]})
        except Exception as exc:  # a held-out seed can leave a rank-deficient fit
            loo.append({"held_out": seed, "error": type(exc).__name__ + ": " + str(exc)})
    result = {
        "kind": "never_served_assertion_model",
        "prereg": ID,
        "status": "FIT",
        "not_a_result": False,
        "n_population": len(rows),
        "n_complete": len(complete),
        "n_events": sum(r["asserted"] for r in complete),
        "excluded": [{"seed": r["seed"], "edge": r["edge"], "direct_count": r["direct_count"],
                      "reason": "no finite full-universe rank"} for r in rows
                     if r["min_rank"] is None],
        "separation": _separation(rows),
        "standardization": {"rank_log2_mean": fitted["rank_mean"], "rank_log2_sd": fitted["rank_sd"],
                            "count_mean": fitted["count_mean"], "count_sd": fitted["count_sd"]},
        "coefficients": fitted["coefs"],
        "average_marginal_effects": fitted["ame"],
        "fit": {"auc": fitted["auc"], "brier": fitted["brier"],
                "loglik_penalized": fitted["fit"]["loglik_penalized"],
                "iterations": fitted["fit"]["iterations"],
                "converged": fitted["fit"]["converged"],
                "max_abs_step": fitted["fit"]["max_abs_step"]},
        "calibration": fitted["calibration"],
        "leave_one_seed_out": loo,
        "gates": {
            "M1_population": len(rows) == 180 and sum(r["asserted"] for r in rows) == 26,
            "M2_rank_coverage": len(complete) / len(rows) >= 0.95,
            "M3_label_replay": all(r["asserted"] == r["replay_asserted"]
                                   and r["ever_loop"] == r["replay_loop"] for r in rows),
            "M4_loop_variation": bool(fitted["data"]) and len({r["loop"] for r in fitted["data"]}) == 2,
            "M5_convergence": bool(fitted["fit"]["converged"]),
            "M6_complete_predictors": all(r["min_rank"] is not None for r in fitted["data"]),
            "M7_seed_levels": len({r["seed"] for r in fitted["data"]}) == 6,
        },
        "engine": prereg["engine"],
        "not_evidence": prereg["not_evidence"],
    }
    result["all_gates"] = all(result["gates"].values())
    result["verdict"] = "FIT" if result["all_gates"] else "VOID"
    return result


def _coef(result: dict, name: str) -> dict:
    return next(c for c in result["coefficients"] if c["name"] == name)


def render_result(result: dict) -> str:
    sep = result["separation"]
    lines = [
        "# Never-served assertion model — result",
        "",
        "**Status.** %s. Generated from `%s`; never edited by hand."
        % (result["verdict"], RESULT.relative_to(ROOT).as_posix()),
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Population | %d never-served edges |" % result["n_population"],
        "| Complete cases | %d |" % result["n_complete"],
        "| Events | %d asserted |" % result["n_events"],
        "| Model | Firth logistic, seed fixed effects |",
        "| AUC | %.3f |" % result["fit"]["auc"],
        "| Brier | %.4f |" % result["fit"]["brier"],
        "| Gates | %s |" % ("all pass" if result["all_gates"] else "FAILED"),
        "",
        "## Separation",
        "",
        "| | Asserted | Not asserted |",
        "| --- | ---: | ---: |",
        "| Loop formed | %d | %d |" % (sep["loop_1_asserted"], sep["loop_1_not"]),
        "| No loop | %d | %d |" % (sep["loop_0_asserted"], sep["loop_0_not"]),
        "",
        "The no-loop, asserted cell is zero. This is quasi-complete separation; the "
        "Firth penalty is what makes the loop coefficient finite.",
        "",
        "## Coefficients",
        "",
        "| Term | OR | 95% CI | p |",
        "| --- | ---: | --- | ---: |",
    ]
    for name in PREDICTORS:
        c = _coef(result, name)
        lines.append("| `%s` | %.3f | %.3f–%.3f | %s |" % (
            name, c["odds_ratio"], c["ci95"][0], c["ci95"][1],
            "%.4f" % c["p"] if c["p"] is not None else "NA"))
    lines += [
        "",
        "Rank and count odds ratios are per 1 SD. The loop odds ratio is a 0/1 contrast. "
        "A rank OR below 1 means a worse rank is associated with lower assertion.",
        "",
        "## Average marginal effects",
        "",
        "| Contrast | Probability difference |",
        "| --- | ---: |",
        "| Loop 1 vs 0 | %+.3f |" % result["average_marginal_effects"]["loop"],
        "| Rank +1 SD | %+.3f |" % result["average_marginal_effects"]["rank_per_sd"],
        "| Count +1 SD | %+.3f |" % result["average_marginal_effects"]["count_per_sd"],
        "",
        "## Calibration",
        "",
        "| Bin | n | Mean predicted | Observed |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for b in result["calibration"]:
        lines.append("| %d | %d | %.3f | %.3f |" % (
            b["bin"], b["n"], b["mean_predicted"], b["observed"]))
    lines += [
        "",
        "## Leave-one-seed-out",
        "",
        "| Held out | Loop beta | Rank beta | Count beta |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for row in result["leave_one_seed_out"]:
        if "error" in row:
            lines.append("| %d | %s | — | — |" % (row["held_out"], row["error"]))
        else:
            lines.append("| %d | %.3f | %.3f | %.3f |" % (
                row["held_out"], row["loop"], row["rank"], row["count"]))
    lines += [
        "",
        "## What this does not license",
        "",
        result["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def freeze() -> int:
    if PREREG.exists():
        print("REFUSED: prereg exists")
        return 2
    doc = engine_stamp.stamp(build_prereg())
    PREREG.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    PREREG_PAGE.write_text(render_prereg(doc), encoding="utf-8")
    print("froze %s and %s" % (PREREG.relative_to(ROOT).as_posix(), PREREG_PAGE.relative_to(ROOT).as_posix()))
    return 0


def run_fit() -> int:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if prereg.get("status") != "FROZEN, NOT FIT":
        print("REFUSED: prereg status %r" % prereg.get("status"))
        return 2
    result = engine_stamp.stamp(fit_result(prereg))
    RESULT.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    RESULT_PAGE.write_text(render_result(result), encoding="utf-8")
    prereg["status"] = "FROZEN, FIT"
    prereg["result"] = str(RESULT.relative_to(ROOT).as_posix())
    PREREG.write_text(json.dumps(prereg, indent=1) + "\n", encoding="utf-8")
    PREREG_PAGE.write_text(render_prereg(prereg), encoding="utf-8")
    print("fit %s: %s, n=%d, events=%d, gates=%s"
          % (result["verdict"], result["prereg"], result["n_complete"],
             result["n_events"], result["all_gates"]))
    for name in PREDICTORS:
        c = _coef(result, name)
        print("%s OR %.3f CI %.3f-%.3f p %s"
              % (name, c["odds_ratio"], c["ci95"][0], c["ci95"][1],
                 "%.4f" % c["p"] if c["p"] is not None else "NA"))
    return 0 if result["all_gates"] else 1


def render_all() -> int:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    PREREG_PAGE.write_text(render_prereg(prereg), encoding="utf-8")
    RESULT_PAGE.write_text(render_result(result), encoding="utf-8")
    return 0


def check() -> int:
    found = []
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    if prereg.get("prereg") != ID:
        found.append("prereg id")
    if prereg.get("status") != "FROZEN, FIT":
        found.append("prereg status")
    if result.get("verdict") != "FIT" or not result.get("all_gates"):
        found.append("result gates")
    if result.get("n_complete") != 179 or result.get("n_events") != 26:
        found.append("population")
    if result.get("separation") != {"loop_1_asserted": 26, "loop_1_not": 35,
                                    "loop_0_asserted": 0, "loop_0_not": 118}:
        found.append("separation")
    if PREREG_PAGE.read_text(encoding="utf-8").strip() != render_prereg(prereg).strip():
        found.append("prereg page stale")
    if RESULT_PAGE.read_text(encoding="utf-8").strip() != render_result(result).strip():
        found.append("result page stale")
    for item in found:
        print("FAIL:", item)
    if found:
        return 1
    print("never-served assertion model: FIT, n=%d, events=%d, gates=%s"
          % (result["n_complete"], result["n_events"], result["all_gates"]))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--fit", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.freeze:
        return freeze()
    if args.fit:
        return run_fit()
    if args.render:
        return render_all()
    if args.check:
        return check()
    print("use --freeze, --fit, --render or --check")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
