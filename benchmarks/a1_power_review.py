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


def _load(name: str) -> dict:
    return json.loads((DOCS / name).read_text(encoding="utf-8"))


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
    max_losses_at_112 = math.floor(c6_world_edges / len(c6["per_seed"]) * (1.0 - C1_FLOOR))

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
                "max_losses_if_112_rows": max_losses_at_112,
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
            "proxy is adequate; the denominator is not. The current cell emits "
            "target rows only; C4 non-target rows are needed to give C1 a "
            "denominator larger than four. Do not freeze on the current target "
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
                "independence. C4 rows or a larger N must change the denominator "
                "before freeze."
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
        "freeze_readiness": {
            "status": "OPEN",
            "pass": False,
            "can_move_now": False,
            "blocking_gate": "C1_path_separation",
            "reason": (
                "Four target rows make the precommitted 0.95 C1 floor a 100% rule "
                "(3/4 = 0.75). C4 non-target rows are instrumented but no cell has "
                "run, so C4 and the enlarged C1 denominator are unmeasured."
            ),
            "to_pass": [
                "Run the planned cells with the C4 neighbour stream.",
                "Attach paired neighbour deltas and score C1/C4.",
                "Show C1 at or above 0.95 with a denominator larger than four and C4 at or below 0.05.",
            ],
        },
        "freeze_decision": {
            "date": DATE,
            "decision": "DO NOT FREEZE",
            "answer": FREEZE_ANSWER,
            "worth_freezing": "NO — HOLD AS DRAFT UNTIL C1/C4 ARE MEASURED",
            "worth_freezing_reason": (
                "The target sets are compliant and representative, but no cell has "
                "run with the new C4 neighbour stream, so the C1 and C4 denominators "
                "remain unmeasured. Do not regenerate targets unless Path B is chosen."
            ),
            "scope": (
                "the current six-seed target artifact and the current four-target "
                "A1 cell output"
            ),
            "basis": [
                "The C6 prevalence proxy is adequate: 602/672 K and 586/672 Y_ind.",
                "The C1 denominator is at most four target rows, so the 0.95 floor is a 100% rule (3/4 = 0.75).",
                "All six seeds having all four K rows is 6.9% under independence; the design is fragile, not merely underpowered.",
            ],
            "revisit_when": [
                "The planned cells run with the C4 neighbour stream and C1/C4 are scored.",
                "A larger target block or a redesigned selector is registered before freeze.",
            ],
        },
        "inputs": {
            "target_observations": total_targets,
            "unique_target_edges": len(targets),
            "selected": sum(selected_flags),
            "candidates": len(selected_flags),
            "c6_seeds": len(c6["per_seed"]),
            "a0_hard_edges": a0_hard,
        },
        "findings": findings,
        "decision": decision,
        "tag_counts": dict(sorted(tag_counts.items())),
        "not_evidence": (
            "A read-only power/prevalence review over different-seed C6 and A0 "
            "records. It runs no A1 cell, assigns no seed, freezes no target and "
            "establishes no causal, capability or transfer claim."
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
    if freeze.get("worth_freezing") != "NO — HOLD AS DRAFT UNTIL C1/C4 ARE MEASURED":
        found.append("worth-freezing decision changed")
    readiness = doc.get("freeze_readiness") or {}
    if readiness.get("status") != "OPEN" or readiness.get("pass") is not False:
        found.append("freeze readiness changed")
    if readiness.get("can_move_now") is not False:
        found.append("freeze readiness improperly moved to pass")
    if not doc.get("representativeness"):
        found.append("power review has no estimand record")
    elif doc["representativeness"].get("estimand") != (
            "representative eligible pre-37 cycle-membership directed-edge population"):
        found.append("power review estimand changed")
    inputs = doc.get("inputs") or {}
    if inputs.get("target_observations") != 24 or inputs.get("unique_target_edges") != 23:
        found.append("power review target counts changed")
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
