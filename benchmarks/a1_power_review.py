"""A1 power and prevalence review from existing artifacts only.

This opens no engine, assigns no seed and runs no A1 cell.  It asks whether
four target rows per seed are enough for the precommitted C1 floor and what
the existing C6/A0 records imply about target denominators.
"""
import argparse
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_power_review.json"
PAGE_PATH = DOCS / "A1-POWER-REVIEW.md"
KIND = "A1-POWER-REVIEW-1"
DATE = "2026-11-14"
C1_FLOOR = 0.95
FREEZE_ANSWER = "NO — NOT AS CURRENTLY EMITTED"
N_PER_SEED = 4
C1_CURVE_DENOMINATORS = (4, 20, 56, 59, 60, 63, 64)
C1_CURVE_RETENTIONS = (0.95, 0.97, 0.98, 1.0)


def _load(name: str) -> dict:
    return json.loads((DOCS / name).read_text(encoding="utf-8"))


def _binomial_tail(n: int, q: float, need: int) -> float:
    """Probability that at least ``need`` of ``n`` independent rows survive."""
    if need <= 0:
        return 1.0
    if need > n:
        return 0.0
    return sum(
        math.comb(n, k) * (q ** k) * ((1.0 - q) ** (n - k))
        for k in range(need, n + 1)
    )


def _all_six_probability(n: int, q: float) -> float:
    need = math.ceil(n * C1_FLOOR)
    per_arm = _binomial_tail(n, q, need)
    return per_arm ** 12


def _required_retention(n: int, target: float) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if _all_six_probability(n, mid) >= target:
            hi = mid
        else:
            lo = mid
    return hi


def _c1_power_curve() -> dict:
    """Reference C1 pass probabilities for the planned and fallback denominators.

    The curve assumes a common, independent Bernoulli retention rate ``q`` for
    every row on both paths. A seed passes only when both the A- and K- arms
    meet 0.95; the all-six column additionally assumes independent seeds. These
    are assumptions for a sensitivity curve, not estimates from A1.
    """
    rows = []
    for n in C1_CURVE_DENOMINATORS:
        need = math.ceil(n * C1_FLOOR)
        for q in C1_CURVE_RETENTIONS:
            per_arm = _binomial_tail(n, q, need)
            per_seed = per_arm ** 2
            rows.append({
                "denominator": n,
                "required_retained": need,
                "allowed_losses": n - need,
                "assumed_retention": q,
                "per_arm": round(per_arm, 6),
                "per_seed": round(per_seed, 6),
                "all_six_seeds": round(per_seed ** 6, 6),
            })
    impact = []
    previous = None
    for n in C1_CURVE_DENOMINATORS:
        row = next(item for item in rows
                   if item["denominator"] == n and item["assumed_retention"] == 0.95)
        change = None if previous is None else round(row["all_six_seeds"] - previous, 6)
        impact.append({
            "denominator": n,
            "required_retained": row["required_retained"],
            "allowed_losses": row["allowed_losses"],
            "effective_floor": round(row["required_retained"] / n, 6),
            "all_six_at_095": row["all_six_seeds"],
            "change_from_previous": change,
        })
        previous = row["all_six_seeds"]
    cliff_low = next(item for item in impact if item["denominator"] == 59)
    cliff_high = next(item for item in impact if item["denominator"] == 60)
    required_targets = (0.5, 0.8, 0.9, 0.95)
    required_retention = {
        "targets": list(required_targets),
        "rows": [
            {
                "target_all_six": target,
                "required_q_by_denominator": {
                    str(n): round(_required_retention(n, target), 6)
                    for n in C1_CURVE_DENOMINATORS
                },
            }
            for target in required_targets
        ],
        "assumption": "Required q under the same independent Bernoulli, six-independent-seed model.",
    }
    baseline = next(row for row in rows
                    if row["denominator"] == 63 and row["assumed_retention"] == 0.95)
    sensitivity = next(row for row in rows
                       if row["denominator"] == 63 and row["assumed_retention"] == 0.98)
    return {
        "model": (
            "Independent Bernoulli retention on each row; the stated retention "
            "rate q is common to A- and K-; a seed passes only when both arms "
            "meet 0.95; all-six assumes independent seeds."
        ),
        "assumptions": [
            "The retention rate is an assumption, not an A1 measurement.",
            "Rows are independent and identically distributed within an arm.",
            "A- and K- have the same assumed retention rate and are independent.",
            "The six seeds are independent; the all-six column is the product of six per-seed probabilities.",
            "The gate is evaluated per seed; no pooling across seeds is used.",
        ],
        "floor": C1_FLOOR,
        "denominators": list(C1_CURVE_DENOMINATORS),
        "assumed_retention_rates": list(C1_CURVE_RETENTIONS),
        "minimum_denominator_for_one_loss": min(
            n for n in C1_CURVE_DENOMINATORS
            if n - math.ceil(n * C1_FLOOR) >= 1
        ),
        "rows": rows,
        "denominator_impact": impact,
        "cliff_60": {
            "from": 59,
            "to": 60,
            "at_59": cliff_low,
            "at_60": cliff_high,
            "all_six_ratio": round(
                cliff_high["all_six_at_095"] / cliff_low["all_six_at_095"], 2
            ),
            "explanation": (
                "At 59 rows, 57/59 = 0.9661 and only two losses pass; at 60 rows, "
                "57/60 = 0.95 and three losses pass. The extra row crosses a loss "
                "boundary in the gate arithmetic, not an empirical effect."
            ),
        },
        "required_retention": required_retention,
        "baseline_example": {
            "denominator": 63,
            "assumed_retention": 0.95,
            "per_arm": baseline["per_arm"],
            "per_seed": baseline["per_seed"],
            "all_six_seeds": baseline["all_six_seeds"],
        },
        "sensitivity_example": {
            "denominator": 63,
            "assumed_retention": 0.98,
            "per_arm": sensitivity["per_arm"],
            "per_seed": sensitivity["per_seed"],
            "all_six_seeds": sensitivity["all_six_seeds"],
        },
        "reading": (
            "At a true retention of 0.95, the 63-row denominator gives a "
            "%.1f%% chance for one arm, %.1f%% for both arms on one seed, and "
            "%.1f%% across all six seeds. At 0.98, the corresponding all-six "
            "chance is %.1f%%. A denominator of 20 is the smallest listed value "
            "that can still pass with one lost row."
            % (baseline["per_arm"] * 100, baseline["per_seed"] * 100,
               baseline["all_six_seeds"] * 100, sensitivity["all_six_seeds"] * 100)
        ),
        "status": "REFERENCE CURVE — NOT AN OBSERVED DENOMINATOR OR RESULT",
    }


def _permutation(selected: list[int], values: list[float]) -> float:
    observed = (statistics.mean(v for s, v in zip(selected, values) if s)
                - statistics.mean(v for s, v in zip(selected, values) if not s))
    rng = random.Random(0)
    hits = 0
    draws = 20000
    for _ in range(draws):
        rng.shuffle(selected)
        diff = (statistics.mean(v for s, v in zip(selected, values) if s)
                - statistics.mean(v for s, v in zip(selected, values) if not s))
        hits += abs(diff) >= abs(observed)
    return hits / draws


def build() -> dict:
    selection = _load("a1_target_selection.json")
    c6 = _load("c6_timing_block.json")
    a0 = _load("carrier_formation_a0.json")

    targets = {edge for row in selection["per_seed"].values() for edge in row["selected"]}
    total_targets = sum(len(row["selected"]) for row in selection["per_seed"].values())
    selected_flags: list[int] = []
    strengths: list[float] = []
    for row in selection["per_seed"].values():
        chosen = set(row["selected"])
        for edge, u in row["u"].items():
            selected_flags.append(1 if edge in chosen else 0)
            strengths.append(float(u["strength"]))
    selected_strength = [v for s, v in zip(selected_flags, strengths) if s]
    unselected_strength = [v for s, v in zip(selected_flags, strengths) if not s]
    permutation_p = _permutation(selected_flags[:], strengths)

    c6_k = sum(r["k_edges"] for r in c6["per_seed"])
    c6_world_edges = sum(r["world_edges"] for r in c6["per_seed"])
    c6_y = sum(r["y_ind_edges"] for r in c6["per_seed"])
    per_seed_k = [r["k_edges"] / r["world_edges"] for r in c6["per_seed"]]
    all_four_k = [p ** N_PER_SEED for p in per_seed_k]
    all_six_all_four = math.prod(all_four_k)

    parts: dict[int, dict[str, dict]] = {}
    for path in sorted((DOCS / "c6_timing_parts").glob("2062*.json")):
        if "determinism" in path.name:
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        parts[int(doc["seed"])] = {row["edge"]: row for row in doc["rows"]}

    overlap = []
    for rows in parts.values():
        for edge in targets:
            if edge in rows:
                overlap.append(rows[edge])
    overlap_k = sum(1 for row in overlap if row.get("first_k") is not None)
    overlap_y = sum(1 for row in overlap if row.get("first_y_ind") is not None)

    a0_hard = int(a0["summary"]["edges"])
    a0_present = int(a0["summary"]["stage_totals"]["present"])
    hard_rate = a0_hard / a0_present if a0_present else 0.0
    expected_hard_targets = N_PER_SEED * len(selection["per_seed"]) * hard_rate
    any_hard = 1.0 - (1.0 - hard_rate) ** (N_PER_SEED * len(selection["per_seed"]))

    # At n rows, a 0.95 floor passes only when (n - losses) / n >= 0.95.
    max_losses_at_4 = math.floor(N_PER_SEED * (1.0 - C1_FLOOR))
    # C4 emits every non-target edge in the A1 universe, so its row count is
    # candidate_count minus the four targets.  C1 adds those rows to the four
    # target rows; it is not 112, which is C6's larger proxy world.
    # Baseline-unavailable edges reduce the observed denominator further.
    planned_c1_rows = {
        seed: int(row["candidate_count"])
        for seed, row in selection["per_seed"].items()
    }
    planned_non_target = {
        seed: rows - N_PER_SEED for seed, rows in planned_c1_rows.items()
    }
    planned_max_losses = {
        seed: math.floor(rows * (1.0 - C1_FLOOR))
        for seed, rows in planned_c1_rows.items()
    }
    planned_min_rows = min(planned_c1_rows.values())
    planned_max_rows = max(planned_c1_rows.values())
    planned_min_losses = min(planned_max_losses.values())
    planned_max_losses_allowed = max(planned_max_losses.values())
    planned_total_rows = sum(planned_c1_rows.values())
    planned_non_target_total = sum(planned_non_target.values())

    tag_counts = Counter(tag for edge in targets for tag in edge.split(">", 1))
    findings = [
        {
            "id": "selection_is_random_on_u",
            "finding": "The 24 targets are statistically indistinguishable from the 358 unselected candidates on cycle-36 strength.",
            "evidence": {
                "selected_n": len(selected_strength),
                "unselected_n": len(unselected_strength),
                "selected_median": statistics.median(selected_strength),
                "unselected_median": statistics.median(unselected_strength),
                "selected_mean": round(statistics.mean(selected_strength), 3),
                "unselected_mean": round(statistics.mean(unselected_strength), 3),
                "permutation_p": permutation_p,
            },
        },
        {
            "id": "all_candidates_eligible",
            "finding": "Cycle membership and positive U do not narrow the candidate universe; every candidate is eligible.",
            "evidence": {
                "candidate_counts": {s: r["candidate_count"] for s, r in selection["per_seed"].items()},
                "eligible_counts": {s: r["eligible_count"] for s, r in selection["per_seed"].items()},
            },
        },
        {
            "id": "c6_denominator_proxy",
            "finding": "C6 supplies a high K/Y_ind denominator in its own world; this is a proxy, not target validation.",
            "evidence": {
                "c6_k": c6_k,
                "c6_world_edges": c6_world_edges,
                "c6_y": c6_y,
                "c6_k_rate": round(c6_k / c6_world_edges, 3),
                "c6_y_rate": round(c6_y / c6_world_edges, 3),
                "per_seed_k_rate_min": round(min(per_seed_k), 3),
                "per_seed_k_rate_max": round(max(per_seed_k), 3),
                "per_seed_all_four_k": [round(value, 3) for value in all_four_k],
                "all_six_all_four_k_independence": round(all_six_all_four, 3),
                "target_overlap_observations": len(overlap),
                "target_overlap_k": overlap_k,
                "target_overlap_y": overlap_y,
            },
        },
        {
            "id": "c1_denominator_fragility",
            "finding": "With four target rows, the 0.95 C1 floor is effectively 100% preservation; one lost row gives 0.75.",
            "evidence": {
                "rows_per_seed": N_PER_SEED,
                "c1_floor": C1_FLOOR,
                "max_losses_at_4": max_losses_at_4,
                "effective_floor_at_4": 1.0,
                "illustration_3_of_4": 0.75,
            },
        },
        {
            "id": "c1_denominator_expansion",
            "finding": (
                "C4 plus the four target rows would raise the planned C1 "
                "denominator from four to %d-%d rows per seed, allowing %d losses "
                "at 0.95; the observed denominator is still unmeasured."
                % (planned_min_rows, planned_max_rows, planned_max_losses_allowed)
            ),
            "evidence": {
                "planned_c1_rows_by_seed": planned_c1_rows,
                "planned_non_target_rows_by_seed": planned_non_target,
                "planned_min_rows": planned_min_rows,
                "planned_max_rows": planned_max_rows,
                "planned_total_rows": planned_total_rows,
                "planned_non_target_total": planned_non_target_total,
                "allowed_losses_min": planned_min_losses,
                "allowed_losses_max": planned_max_losses_allowed,
                "max_losses_with_planned_c4": planned_max_losses,
                "status": "UNMEASURED — no A1 cell has run",
                "baseline_caveat": (
                    "C1 counts only edges available in the paired A+K+ control, "
                    "so the observed denominator will be at most %d-%d."
                    % (planned_min_rows, planned_max_rows)
                ),
            },
        },
        {
            "id": "hard_edge_baseline",
            "finding": "A0's hard-edge prevalence is low, but a random 24-target sample has a material chance of containing one.",
            "evidence": {
                "a0_hard_edges": a0_hard,
                "a0_present_edges": a0_present,
                "hard_rate": round(hard_rate, 4),
                "expected_hard_targets": round(expected_hard_targets, 2),
                "prob_any_hard_independence": round(any_hard, 3),
            },
        },
    ]

    decision = {
        "verdict": "FREEZE READINESS OPEN — C1 DENOMINATOR FRAGILITY",
        "reading": (
            "P0 and feasibility pass, but four target rows per seed make the "
            "precommitted 0.95 C1 floor a 100% preservation rule. The prevalence "
            "proxy is adequate; the denominator is not. C4 non-target rows are "
            "implemented and, with the four target rows, would raise the planned "
            "denominator to 63-64 per seed, allowing 3 losses, but no cell has "
            "run. C1 remains unmeasured; do not freeze on the current target "
            "artifact."
        ),
        "freeze_question": {
            "question": (
                "Does a random eligible-edge design have enough expected measurable "
                "structure to justify freeze?"
            ),
            "answer": FREEZE_ANSWER,
            "basis": (
                "K and Y_ind prevalence are high enough that missing structure is "
                "not the blocker. The blocker is C1: four rows make the 0.95 floor "
                "a 100% rule, and the all-six all-four-K proxy is 6.9% under "
                "independence. C4 rows plus targets would raise the planned "
                "denominator to 63-64 per seed, but no cell has run, so the "
                "observed denominator is still unmeasured."
            ),
            "if_yes": "Freeze the representative eligible-edge design after the manifest review.",
            "if_no": "Do not freeze; enlarge the C1 denominator with C4 rows or redesign the target block.",
        },
        "next": [
            "If Path A (representative eligible-edge effect) is retained: run the planned cells with the C4 neighbour stream and score C1/C4.",
            "If Path B (high-carrier-propensity effect) is required: redesign the selector and regenerate targets before freeze; that is a different experiment.",
            "Re-run this review after C1/C4 are measured; do not freeze before that.",
        ],
    }

    return {
        "kind": KIND,
        "id": KIND,
        "date": DATE,
        "status": decision["verdict"],
        "representativeness": {
            "estimand": "representative eligible pre-37 cycle-membership directed-edge population",
            "selector": (
                "outcome-blind hash order over all eligible edges; U is not a ranking input"
            ),
            "evidence": {
                "selected_observations": total_targets,
                "unique_target_edges": len(targets),
                "unselected_candidates": len(selected_flags) - total_targets,
                "selected_mean_strength": round(statistics.mean(selected_strength), 3),
                "unselected_mean_strength": round(statistics.mean(unselected_strength), 3),
                "permutation_p": permutation_p,
            },
            "not_a_sample_of": [
                "high-U edges",
                "hard edges",
                "carrier-enriched anomalies",
            ],
            "consequence": (
                "A1 tests a representative eligible-edge effect. It does not test an "
                "effect among high-propensity or anomalous edges; that would require a "
                "different selector and a new target set before freeze."
            ),
        },
        "sources": {
            "selection": "docs/a1_target_selection.json",
            "c6": "docs/c6_timing_block.json",
            "c6_parts": "docs/c6_timing_parts/20621101..20621106.json",
            "a0": "docs/carrier_formation_a0.json",
        },
        "gate_order": {
            "decision": "POST-FREEZE VOID GATE",
            "date": DATE,
            "record": "docs/A1-C4-GATE-ORDER.md",
            "effect": (
                "C4 is not a pre-freeze blocker. C1 and C4 are scored in the "
                "same post-freeze result assembly; a C4 failure VOIDs the run."
            ),
        },
        "freeze_readiness": {
            "status": "OPEN",
            "pass": False,
            "can_move_now": False,
            "blocking_gate": "target_freeze_not_authorized",
            "reason": (
                "C4 is a post-freeze void gate, so C1/C4 are no longer pre-freeze "
                "measurement blockers. The targets remain draft and the manifest "
                "remains unfrozen because no separate owner freeze act has been "
                "recorded; no grant or run exists."
            ),
            "to_pass": [
                "Freeze the representative target manifest in a separate owner act.",
                "Record the dated grant and run the planned cells.",
                "Assemble C1/C4; a failed C4 VOIDs the result.",
            ],
        },
        "freeze_decision": {
            "date": DATE,
            "decision": "DO NOT FREEZE",
            "gate_order_note": (
                "The dated DO NOT FREEZE record predates the 2026-11-14 gate-order "
                "decision. C4 is now post-freeze VOID; this record remains the "
                "historical freeze decision and does not authorise a freeze."
            ),
            "answer": FREEZE_ANSWER,
            "worth_freezing": "NO — HOLD AS DRAFT; TARGET FREEZE NOT AUTHORIZED",
            "worth_freezing_reason": (
                "The target sets are compliant and representative, but no separate "
                "target freeze has been performed. C4 is now a post-freeze VOID gate, "
                "so the C1/C4 measurement cannot be a pre-freeze condition. Do not "
                "regenerate targets unless Path B is chosen."
            ),
            "scope": (
                "the current six-seed target artifact and the current four-target "
                "A1 cell output"
            ),
            "basis": [
                "The C6 prevalence proxy is adequate: 602/672 K and 586/672 Y_ind.",
                "The C1 denominator is four target rows, so the 0.95 floor is a 100% rule (3/4 = 0.75); C4 would add 59-60 planned non-target rows per seed, bringing the planned C1 denominator to 63-64, but none has been observed.",
                "All six seeds having all four K rows is 6.9% under independence; the design is fragile, not merely underpowered.",
            ],
            "revisit_when": [
                "The planned cells run with the C4 neighbour stream and C1/C4 are scored.",
                "A larger target block or a redesigned selector is registered before freeze.",
            ],
        },
        "c1_power_curve": _c1_power_curve(),
        "inputs": {
            "target_observations": total_targets,
            "unique_target_edges": len(targets),
            "selected": sum(selected_flags),
            "candidates": len(selected_flags),
            "planned_c1_denominator_min": planned_min_rows,
            "planned_c1_denominator_max": planned_max_rows,
            "planned_total_rows": planned_total_rows,
            "planned_non_target_rows": planned_non_target_total,
            "c6_seeds": len(c6["per_seed"]),
            "a0_hard_edges": a0_hard,
        },
        "findings": findings,
        "decision": decision,
        "tag_counts": dict(sorted(tag_counts.items())),
        "not_evidence": (
            "A read-only power/prevalence review over different-seed C6 and A0 "
            "records. Its C1 expansion is a planned count from the A1 candidate "
            "counts, not an observed denominator. It runs no A1 cell, assigns no "
            "seed, freezes no target and establishes no causal, capability or "
            "transfer claim."
        ),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("power review kind")
    if not doc.get("findings"):
        found.append("power review has no findings")
    if (doc.get("decision") or {}).get("verdict") != "FREEZE READINESS OPEN — C1 DENOMINATOR FRAGILITY":
        found.append("power review decision changed")
    if not (doc.get("decision") or {}).get("freeze_question"):
        found.append("power review has no freeze question")
    elif doc["decision"]["freeze_question"].get("answer") != FREEZE_ANSWER:
        found.append("power review freeze answer changed")
    freeze = doc.get("freeze_decision") or {}
    if freeze.get("decision") != "DO NOT FREEZE" or freeze.get("answer") != FREEZE_ANSWER:
        found.append("freeze decision changed")
    if freeze.get("worth_freezing") != "NO — HOLD AS DRAFT; TARGET FREEZE NOT AUTHORIZED":
        found.append("worth-freezing decision changed")
    readiness = doc.get("freeze_readiness") or {}
    if readiness.get("status") != "OPEN" or readiness.get("pass") is not False:
        found.append("freeze readiness changed")
    if readiness.get("can_move_now") is not False:
        found.append("freeze readiness improperly moved to pass")
    if (doc.get("gate_order") or {}).get("decision") != "POST-FREEZE VOID GATE":
        found.append("C4 gate order changed")
    if not doc.get("representativeness"):
        found.append("power review has no estimand record")
    elif doc["representativeness"].get("estimand") != (
            "representative eligible pre-37 cycle-membership directed-edge population"):
        found.append("power review estimand changed")
    inputs = doc.get("inputs") or {}
    if inputs.get("target_observations") != 24 or inputs.get("unique_target_edges") != 23:
        found.append("power review target counts changed")
    if (inputs.get("planned_c1_denominator_min") != 63
            or inputs.get("planned_c1_denominator_max") != 64
            or inputs.get("planned_total_rows") != 382
            or inputs.get("planned_non_target_rows") != 358):
        found.append("power review planned C1 denominator changed")
    expansion = next((finding for finding in doc.get("findings", [])
                      if finding.get("id") == "c1_denominator_expansion"), None)
    if expansion is None:
        found.append("power review has no C1 expansion finding")
    elif expansion.get("evidence", {}).get("status", "").split(" ")[0] != "UNMEASURED":
        found.append("C1 expansion is not marked unmeasured")
    curve = doc.get("c1_power_curve") or {}
    if curve.get("status") != "REFERENCE CURVE — NOT AN OBSERVED DENOMINATOR OR RESULT":
        found.append("C1 power curve is not marked as a reference")
    if curve.get("floor") != C1_FLOOR:
        found.append("C1 power curve floor changed")
    if curve.get("assumed_retention_rates") != list(C1_CURVE_RETENTIONS):
        found.append("C1 power curve retention assumptions changed")
    expected = {(n, q) for n in C1_CURVE_DENOMINATORS for q in C1_CURVE_RETENTIONS}
    rows = {(row.get("denominator"), row.get("assumed_retention"))
            for row in curve.get("rows", [])}
    if rows != expected:
        found.append("C1 power curve rows do not cover every denominator and retention rate")
    if len(curve.get("denominator_impact") or []) != len(C1_CURVE_DENOMINATORS):
        found.append("C1 power curve has no full denominator-impact table")
    cliff = curve.get("cliff_60") or {}
    if cliff.get("from") != 59 or cliff.get("to") != 60:
        found.append("C1 power curve does not record the 60-row cliff")
    required = curve.get("required_retention") or {}
    if len(required.get("rows") or []) != 4:
        found.append("C1 power curve has no required-retention scenarios")
    return found


def render(doc: dict) -> str:
    rows = [
        "# A1 power and prevalence review",
        "",
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an A1 result.** No arm cell was run; no target was frozen.",
        "",
        "| Finding | Evidence |",
        "| --- | --- |",
    ]
    for finding in doc["findings"]:
        evidence = "; ".join("%s=%s" % (k, v) for k, v in finding["evidence"].items())
        rows.append("| **%s** — %s | %s |" % (finding["id"], finding["finding"], evidence))
    curve = doc["c1_power_curve"]
    cells = {(row["denominator"], row["assumed_retention"]): row
             for row in curve["rows"]}
    rows += [
        "",
        "## C1 power curve",
        "",
        curve["reading"],
        "",
        "**Model:** %s" % curve["model"],
        "",
        "**Retention rate assumption:** each column names the assumed `q`; "
        "these are reference probabilities, not A1 measurements.",
        "",
        "| Denominator | Required | Allowed losses | q=.95 arm | q=.95 seed | q=.95 all six | q=.98 arm | q=.98 seed | q=.98 all six |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for n in curve["denominators"]:
        base = cells[(n, 0.95)]
        sens = cells[(n, 0.98)]
        rows.append(
            "| %d | %d | %d | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f |"
            % (n, base["required_retained"], base["allowed_losses"],
               base["per_arm"], base["per_seed"], base["all_six_seeds"],
               sens["per_arm"], sens["per_seed"], sens["all_six_seeds"]))
    rows += [
        "",
        "The curve also records `q=.97` and `q=1.00` in the artifact. "
        "The `all six` columns are the product of six independent per-seed "
        "probabilities, because C1 must pass on every seed.",
        "",
        "At `.95` and 63 rows, one arm passes with probability **%.6f**, both "
        "arms on one seed with **%.6f**, and all six seeds with **%.6f**. "
        "At `.98`, the all-six probability is **%.6f**. The target-only "
        "four-row fallback is the first row; 20 rows is the smallest listed "
        "denominator that can still pass with one loss."
        % (cells[(63, 0.95)]["per_arm"], cells[(63, 0.95)]["per_seed"],
           cells[(63, 0.95)]["all_six_seeds"],
           cells[(63, 0.98)]["all_six_seeds"]),
        "",
    ]
    impact = curve["denominator_impact"]
    rows += [
        "",
        "### Denominator impact at q=.95",
        "",
        "The `all six` column is the probability that C1 passes on every seed "
        "under the stated independent-retention model. `Change` is relative to "
        "the previous listed denominator, not an empirical effect.",
        "",
        "| Denominator | Required | Allowed losses | Effective floor | q=.95 all six | Change |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in impact:
        change = "—" if item["change_from_previous"] is None else "%+.6f" % item["change_from_previous"]
        rows.append(
            "| %d | %d | %d | %.4f | %.6f | %s |"
            % (item["denominator"], item["required_retained"],
               item["allowed_losses"], item["effective_floor"],
               item["all_six_at_095"], change))
    cliff = curve["cliff_60"]
    rows += [
        "",
        "### The 60-row cliff",
        "",
        cliff["explanation"],
        "",
        "At `q=.95`, the all-six probability moves from **%.6f** at 59 rows "
        "to **%.6f** at 60 rows, a **%.2fx** step. This is a loss-boundary "
        "effect: the extra row is not a new measurement, and the cliff is not "
        "evidence that 60 rows are scientifically special."
        % (cliff["at_59"]["all_six_at_095"],
           cliff["at_60"]["all_six_at_095"], cliff["all_six_ratio"]),
        "",
        "### Required retention for all-six power",
        "",
        "Each cell is the assumed `q` needed for the stated all-six-seed power "
        "under the same independent model. These are scenarios, not observed "
        "retention rates.",
        "",
        "| Target all-six | n=4 | n=20 | n=56 | n=59 | n=60 | n=63 | n=64 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in curve["required_retention"]["rows"]:
        required = item["required_q_by_denominator"]
        rows.append(
            "| %d%% | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f |"
            % (round(item["target_all_six"] * 100), required["4"], required["20"],
               required["56"], required["59"], required["60"], required["63"],
               required["64"]))
    rows += [
        "",
        "The required-retention table makes the cost explicit: at 63 rows, "
        "80%% all-six power needs `q=%.6f`; 50%% needs `q=%.6f`. The "
        "target-only four-row design needs a still higher rate for the same "
        "power because it allows no losses."
        % (
            curve["required_retention"]["rows"][1]["required_q_by_denominator"]["63"],
            curve["required_retention"]["rows"][0]["required_q_by_denominator"]["63"],
        ),
        "",
    ]
    rows += [
        "",
        "## What population A1 tests",
        "",
        "**Estimand:** %s." % doc["representativeness"]["estimand"],
        "",
        doc["representativeness"]["consequence"],
        "",
        "It is **not** a sample of %s." % ", ".join(doc["representativeness"]["not_a_sample_of"]),
        "",
        "## Freeze question",
        "",
        "**%s**" % doc["decision"]["freeze_question"]["question"],
        "",
        "**Answer: %s.** %s" % (
            doc["decision"]["freeze_question"]["answer"],
            doc["decision"]["freeze_question"]["basis"],
        ),
        "",
        "- If yes: %s" % doc["decision"]["freeze_question"]["if_yes"],
        "- If no: %s" % doc["decision"]["freeze_question"]["if_no"],
        "",
        "## Freeze readiness",
        "",
        "**Status: %s. Can it move to PASS now? %s.**" % (
            doc["freeze_readiness"]["status"],
            "YES" if doc["freeze_readiness"]["can_move_now"] else "NO",
        ),
        "",
        doc["freeze_readiness"]["reason"],
        "",
        "**To reach PASS:**",
        "- %s" % "\n- ".join(doc["freeze_readiness"]["to_pass"]),
        "",
        "## Gate order",
        "",
        "**C4 decision: %s.** %s" % (
            doc["gate_order"]["decision"],
            doc["gate_order"]["effect"],
        ),
        "",
        "**Record:** [`A1-C4-GATE-ORDER.md`](A1-C4-GATE-ORDER.md).",
        "",
        "## Freeze decision",
        "",
        "**%s (%s).** Answer: **%s**." % (
            doc["freeze_decision"]["decision"],
            doc["freeze_decision"]["date"],
            doc["freeze_decision"]["answer"],
        ),
        "",
        "**Scope:** %s." % doc["freeze_decision"]["scope"],
        "",
        "**Are the target sets worth freezing?** **%s.** %s" % (
            doc["freeze_decision"]["worth_freezing"],
            doc["freeze_decision"]["worth_freezing_reason"],
        ),
        "",
        "**Basis:**",
    ] + ["- %s" % item for item in doc["freeze_decision"]["basis"]] + [
        "",
        "**Revisit when:**",
    ] + ["- %s" % item for item in doc["freeze_decision"]["revisit_when"]] + [
        "",
        "## Decision",
        "",
        "**%s**" % doc["decision"]["verdict"],
        "",
        doc["decision"]["reading"],
        "",
        "### Next",
    ] + ["- %s" % item for item in doc["decision"]["next"]] + [
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
    ]
    return "\n".join(rows)


def write() -> int:
    doc = build()
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc), encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print(doc["status"])
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    found = problems(doc)
    rebuilt = build()
    if doc != rebuilt:
        found.append("power review is stale against its sources")
    if not PAGE_PATH.exists():
        found.append("power review page is missing")
    elif PAGE_PATH.read_text(encoding="utf-8") != render(doc):
        found.append("power review page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 power review: clean")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
