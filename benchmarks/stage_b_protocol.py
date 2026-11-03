"""Stage B: the protocol's numbers, assembled from artifacts rather than typed.

The construct record fixed what onset means, what counts as eligible and when
behaviour may begin. This module turns those decisions into the numbers a protocol
needs -- block size, run horizon and seed block -- by *reading* the record rather
than restating it, and it proves the seed block unused by scanning every artifact
in ``docs/`` for seed fields.

It runs no engine and computes no relation between onset and behaviour: Stage A
fixed the predictor before any outcome existed, and the protocol may not undo that.

**On reliability.** The block size needs an attenuation factor, and onset cannot be
given a reliability coefficient: the engine is deterministic per seed, so a re-run
is not a replication. The sustention-rule agreement in the construct record (0.972)
is therefore reported as what it is -- robustness of the *ordering* to the rule --
and **is not used** in the arithmetic. It bounds only the rule-choice component of
measurement error, because the two measurements share the same trajectories and
differ in definition rather than through independent error. The block is instead
sized at a declared planning assumption on reliability, conservatively, with the
whole ladder printed so a reviewer can see what each assumption costs.

    ./.venv/bin/python -m benchmarks.stage_b_protocol
"""

from __future__ import annotations

import glob
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONSTRUCT = ROOT / "docs" / "di_transition_construct.json"
SIGNRES = ROOT / "docs" / "sign_resolution_structure_behavior.json"
OUT = ROOT / "docs" / "stage_b_protocol.json"

CLAIMED = ("2:1", "3:1", "4:1", "6:1")
LEVEL = 0.9833
RESOLUTION_BAR = 0.90
SMALLEST_EFFECT = 0.50
PUBLISHED_FLOOR = 48
MIN_REAL_SEED = 1000
RELIABILITY_GRID = (1.00, 0.90, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30)
PLANNING_RELIABILITY = 0.50
SPARE_SEEDS = 4
SEED_BLOCK_START = 700000001


def _phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _phi_inv(p: float) -> float:
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _attenuate(observed: float, reliability: float) -> float:
    """Observed Spearman after attenuating the latent correlation by reliability.

    The claim is stated in observed-Spearman units, so the latent correlation is
    recovered first -- inverting ``rho_s = (6/pi) asin(rho_g / 2)`` -- then attenuated
    by ``sqrt(reliability)`` and mapped back. Inverting first is what makes reliability
    1.00 return the declared effect unchanged (0.50 -> 48 worlds); attenuating the
    observed value directly would silently move the target.
    """
    latent = 2.0 * math.sin(math.pi * observed / 6.0)
    r_g = latent * math.sqrt(reliability)
    return (6.0 / math.pi) * math.asin(r_g / 2.0)


def _worlds_for(effect: float, bar: float = RESOLUTION_BAR,
                level: float = LEVEL) -> int:
    """Worlds per configuration so a block resolves `effect` this often.

    A block resolves when Fisher's z interval at `level` excludes zero with the
    predicted sign, so the probability is Phi(atanh(rho)*sqrt(n-3) - z_crit) and the
    smallest n solving ``>= bar`` is the ceiling below. At effect 0.50 this returns
    the 48 the sign-resolution artifact published, which is the check that the
    closed form is applying the project's own rule and not a different one.
    """
    z_crit = _phi_inv(1.0 - (1.0 - level) / 2.0)
    target = z_crit + _phi_inv(bar)
    return 3 + math.ceil((target / math.atanh(effect)) ** 2)


def _consumed_seeds() -> dict[str, list[int]]:
    """Every integer filed under a key naming a seed, in every docs/ artifact."""
    found: dict[str, list[int]] = {}
    for path in sorted(glob.glob(str(ROOT / "docs" / "*.json"))):
        try:
            obj = json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        seeds: set[int] = set()

        def walk(node) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    if isinstance(value, int) and not isinstance(value, bool) \
                            and "seed" in key.lower() and value >= MIN_REAL_SEED:
                        seeds.add(value)
                    else:
                        walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(obj)
        if seeds:
            found[str(Path(path).relative_to(ROOT))] = sorted(seeds)
    return found


def build() -> dict:
    construct = json.loads(CONSTRUCT.read_text(encoding="utf-8"))
    clock = construct["behavioural_clock"]
    rank = construct["threshold_rank_sensitivity"]["per_config"]
    criteria = construct["stage_b_measurement_criteria"]

    sustained = construct["onset_conventions"]["sustained_cycles"]
    assert sustained == 10
    assert clock["post_confirmation_margin_cycles"] == 1
    assert clock["follow_up_cycles"] == 100
    assert criteria["min_defined_share"] == 0.90
    assert criteria["min_sd_cycles"] == 3.0
    assert list(CLAIMED) == sorted(criteria["per_config"])

    pairs = ("5_vs_10", "10_vs_20", "5_vs_20")
    agreements = {lab: {p: rank[lab]["comparisons"][p]["spearman"] for p in pairs}
                  for lab in CLAIMED}
    agreement = min(min(row.values()) for row in agreements.values())
    agreement_where = min(((lab, p) for lab in CLAIMED for p in pairs),
                          key=lambda k: rank[k[0]]["comparisons"][k[1]]["spearman"])

    ladder = {}
    for rel in RELIABILITY_GRID:
        effect = _attenuate(SMALLEST_EFFECT, rel)
        ladder["%.2f" % rel] = {
            "observed_effect_spearman": round(effect, 6),
            "worlds_per_configuration": _worlds_for(effect),
        }
    floor_worlds = _worlds_for(SMALLEST_EFFECT)
    assert floor_worlds == PUBLISHED_FLOOR, (floor_worlds, PUBLISHED_FLOOR)
    assert ladder["1.00"]["worlds_per_configuration"] == floor_worlds
    planned = ladder["%.2f" % PLANNING_RELIABILITY]["worlds_per_configuration"]
    worlds_total = planned * len(CLAIMED)
    # Reliability descends down the grid, so the requirement must ascend:
    # a worse instrument needs more worlds.
    ordered = [ladder["%.2f" % r]["worlds_per_configuration"] for r in RELIABILITY_GRID]
    assert ordered == sorted(ordered), ordered

    horizons = {lab: clock["per_config"][lab]["confirmation_cycle_median"]
                + clock["post_confirmation_margin_cycles"]
                + clock["follow_up_cycles"] for lab in CLAIMED}
    cycles_total = int(sum(horizons.values()) * planned)
    phase_l_cycles = 240 * 600

    consumed = _consumed_seeds()
    block = list(range(SEED_BLOCK_START,
                       SEED_BLOCK_START + worlds_total + SPARE_SEEDS))
    consumed_flat = {s for values in consumed.values() for s in values}
    overlap = sorted(set(block) & consumed_flat)
    assert not overlap, overlap[:10]
    assert len(block) == worlds_total + SPARE_SEEDS

    assignment = {}
    for i, lab in enumerate(sorted(CLAIMED)):
        chunk = block[i * planned:(i + 1) * planned]
        assignment[lab] = {"first": chunk[0], "last": chunk[-1], "count": len(chunk)}

    signres = json.loads(SIGNRES.read_text(encoding="utf-8"))

    # ---- the endpoint's granularity, from the cells that already exist -----
    # A non-zero held-out count is not a resolution test. The quantum is one / the
    # number of withheld transitions, so the count decides how finely the outcome can
    # be scored at all. This uses design-block cells, declared as such; it informs the
    # gate and does not discharge it, because Stage B's own enumeration does not exist.
    calib = json.loads((ROOT / "docs" / "reusable_knowledge_calibration.json")
                       .read_text(encoding="utf-8"))
    counts: list[int] = []

    def _collect(node, key: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k == key and isinstance(v, int) and not isinstance(v, bool):
                    counts.append(v)
                else:
                    _collect(v, key)
        elif isinstance(node, list):
            for item in node:
                _collect(item, key)

    _collect(calib, "revision_held_out_pairs")
    assert counts, "no design-block held-out counts to reason from"
    counts.sort()
    n_min, n_max = counts[0], counts[-1]
    n_med = counts[len(counts) // 2]
    assumed_sd = 0.05                      # a deliberately tight outcome spread
    gap = 2.0 * SMALLEST_EFFECT * assumed_sd   # top-vs-bottom gap at rho = 0.50

    resolution = {
        "status": "informed by design-block cells; not discharged for Stage B",
        "confirmed": False,
        "what_would_confirm_it": "the withheld enumeration for the four claimed "
                                  "configurations, reporting the count per world and "
                                  "the per-world standard error of the endpoint "
                                  "before any world runs",
        "evidence_source": "docs/reusable_knowledge_calibration.json",
        "evidence_kind": "design-block cells, declared as such and not confirmatory",
        "endpoint_scale": {
            "unit": "mean pairwise binary log loss, in nats per scored cell",
            "is_a_proportion": False,
            "where_defined": "benchmarks/acquisition_compositional.py -- score(), "
                            "called by benchmarks/reusable_knowledge.py -- limbs()",
            "one_over_count_quantum": "withdrawn: this endpoint has no 1/count "
                                     "lattice of outcome levels, so the previous "
                                     "quantum and level-count figures described an "
                                     "endpoint the protocol does not use "
                                     "(docs/AI-REVIEW-2026-11-02.md, rubric 1)",
            "what_the_count_buys": "the precision of a per-world mean: a world's "
                                   "score averages over its withheld cells, so more "
                                   "cells mean a less noisy score, not a finer grid",
        },
        "held_out_transitions": {"cells": len(counts), "min": n_min,
                                 "median": n_med, "max": n_max},
        "assumed_outcome_sd": assumed_sd,
        "assumed_sd_is": "a planning assumption for the across-world spread of the "
                         "endpoint in nats, not a measurement on any Stage B world",
        "effect_gap_at_rho_0_50": round(gap, 6),
        "rules": {
            "too_coarse": "twice a world's standard error of the endpoint, "
                          "s/sqrt(N) over its scored cells, larger than the effect gap "
                          "at the declared smallest effect -> the score cannot separate "
                          "two worlds the claim distinguishes, so it is a design defect "
                          "and the run does not start",
            "too_sparse": "fewer than half the planned worlds at 40 or more "
                          "held-out transitions -> design defect, run does not start",
            "saturated": "a configuration whose realised across-world SD is below "
                         "twice the median per-world standard error is unmeasurable "
                         "there: excluded and reported, never scored as a null",
            "undefined": "zero withheld transitions -> excluded by the existing E6 "
                        "gate, never zeroed (AGENTS 13b)",
            "screening": "the enumeration runs before any world, and its own report "
                         "is the gate -- not this paragraph",
        },
        "limit": "this bounds granularity; it does not show that the outcome varies "
                 "across worlds, which only the run can show",
    }

    return {
        "what_this_is": "The Stage B protocol's arithmetic: block size, run horizon "
                        "and seed block, assembled from the construct record and "
                        "checked against it. No engine run, no seed allocated, no "
                        "world generated, no relation between onset and behaviour "
                        "computed.",
        "status": {
            "authorised": False,
            "seeds_allocated": 0,
            "worlds_run": 0,
            "statement": "Stage B is not authorised. The seed block is candidate "
                         "only, and the pre-assignment inside it is a plan: it is "
                         "proved unused, which is not the same as being spent.",
        },
        "predictor": {
            "name": "confirmed onset of DI",
            "unit": "cycles",
            "definition": construct["definitions"]["onset"],
            "anchor": construct["onset_conventions"]["anchor"],
            "available_from": construct["onset_conventions"]["available_from"],
            "sustention_rule_cycles": sustained,
            "sustention_rule_frozen": True,
            "direction": "earlier confirmed onset predicts a higher held-out "
                         "prediction score after learning",
        },
        "claimed_configurations": list(CLAIMED),
        "glossary": {
            "pre-assigned": "mapped to a configuration in the protocol, in advance, "
                            "with a specific seed. It is a plan: no world runs, and "
                            "nothing is spent, until the review records an outcome",
            "allocated": "released for an executed run. No seed is allocated by "
                         "this document, which is why pre-assignment and allocation "
                         "are different words here and are never used as synonyms",
            "reserved": "deliberately not used: the four spares are reserved and "
                        "never drawn, and a censored world does not release its seed",
        },
        "endpoint_resolution": resolution,
        "eligibility": {
            "rule": "onset defined in >= %s of runs, within each claimed "
                    "configuration, never on the pooled set"
                    % criteria["min_defined_share"],
            "resolution_rule": "within-configuration SD >= %s cycles, reported with "
                               "the IQR, range and distinct-value count"
                               % criteria["min_sd_cycles"],
            "worlds_below_denominator_are": "reported as censored and excluded, "
                                            "never scored as a zero (AGENTS 13b)",
        },
        "behavioural_endpoint": {
            "name": "revision_held_out",
            "definition": "next-tag prediction on the revision-test window under the "
                          "rotated law, restricted to transitions withheld from both "
                          "formation and revision learning, scored by the calibrated "
                          "readout with no refit during evaluation",
            "inherited_from": "docs/STRUCTURE-BEHAVIOR-DESIGN.md §3",
            "learn_cycles": clock["learn_cycles"],
            "test_cycles": clock["test_cycles"],
            "implementation_to_inspect": [
                "benchmarks/reusable_knowledge.py -- revision_held_out, "
                "held_out['revision_held_out_pairs'], and the WITHHELD set selected "
                "inside limbs()'s held_only() define what is scored and withheld",
                "benchmarks/formation_provenance_study.py -- held_out_pairs() is that "
                "study's own pair selector, NOT this endpoint's withholding rule "
                "(docs/AI-REVIEW-2026-11-02.md, rubric 3)",
            ],
            "resolution_requirement": "the endpoint's quantum (one held-out "
                                      "transition) and the number of held-out "
                                      "transitions must be reported before the run; "
                                      "a quantum coarser than the smallest effect the "
                                      "claim asserts makes the endpoint unmeasurable "
                                      "for that claim and the run does not start",
            "resolution_confirmed": False,
        },
        "clock": {
            "post_confirmation_margin_cycles": clock["post_confirmation_margin_cycles"],
            "follow_up_cycles": clock["follow_up_cycles"],
            "first_behavioural_index": "confirmation index + %d"
                                       % clock["post_confirmation_margin_cycles"],
            "last_behavioural_index": "confirmation index + %d"
                                      % (clock["post_confirmation_margin_cycles"]
                                         + clock["follow_up_cycles"] - 1),
            "horizon_is_per_world": True,
            "horizon_rule": "readings = confirmation index + %d; a fixed horizon "
                            "that ends mid-follow-up fails criterion 4 rather than "
                            "shortening the follow-up"
                            % (clock["post_confirmation_margin_cycles"]
                               + clock["follow_up_cycles"]),
            "median_horizon_by_config_cycles": horizons,
        },
        "sample_size": {
            "decision_level": LEVEL,
            "resolution_bar": RESOLUTION_BAR,
            "smallest_effect_spearman": SMALLEST_EFFECT,
            "reliability_measured": False,
            "why_reliability_is_not_measured": "the engine is deterministic per "
                                               "seed, so re-running a world is not a "
                                               "replication and no test-retest "
                                               "estimate exists",
            "reliability_planning_assumption": PLANNING_RELIABILITY,
            "planning_assumption_is_established_lower_bound": False,
            "block_is_conditional_on_the_assumption": True,
            "why_this_assumption": "no reliability estimate exists, so one is "
                                   "declared rather than inferred. 0.50 is the "
                                   "weakest predictor still worth testing -- below it "
                                   "the measure carries less signal than error -- so "
                                   "the block is sized at the worst instrument the "
                                   "claim could survive rather than at a flattering "
                                   "one",
            "attenuation_ladder": ladder,
            "worlds_per_configuration_at_reliability_1": floor_worlds,
            "worlds_per_configuration": planned,
            "worlds_total": worlds_total,
            "reportable_floor_per_configuration": floor_worlds,
            "a_higher_reliability_would_shrink_the_block": True,
            "worlds_total_if_reviewer_accepts_0_70": (
                ladder["0.70"]["worlds_per_configuration"] * len(CLAIMED)),
            "why_this_size": "The block is sized so the decision rule resolves a "
                             "relation of the declared smallest size in %d %% of "
                             "blocks at the declared reliability assumption. The "
                             "assumption is stated, not derived, and every "
                             "alternative row is printed beside it."
                             % int(RESOLUTION_BAR * 100),
            "it_is_a_floor": "unmodelled dependence between worlds and any further "
                             "measurement error lower the real resolution "
                             "probability, so this is the least number the claim can "
                             "be tested with, not the most",
            "below_the_floor": "a configuration whose usable n falls below %d after "
                               "censoring is reported inconclusive, never null"
                               % floor_worlds,
            "no_replacement": "a censored world is not replaced: the denominator is "
                              "reported as realised",
        },
        "sustention_rule_agreement": {
            "worst_pair_spearman": agreement,
            "where": {"configuration": agreement_where[0],
                      "comparison": agreement_where[1]},
            "by_config": agreements,
            "establishes": "the ordering of worlds is robust to the sustention rule, "
                           "and the predictor's ranking does not depend on the "
                           "declared 10-cycle choice",
            "does_not_establish": "a reliability coefficient. The two measurements "
                                  "come from the same trajectories, share nearly all "
                                  "their measurement information, and differ in "
                                  "operational definition rather than through "
                                  "independent random error, so the statistic bounds "
                                  "only the rule-choice component of measurement "
                                  "error -- not the reliability of onset",
            "used_in_the_block_size": False,
        },
        "cost": {
            "cycles_total": cycles_total,
            "cycles_if_every_world_ran_600": phase_l_cycles,
            "relative_to_phase_l": round(cycles_total / phase_l_cycles, 4),
            "note": "Estimated from the median confirmation cycle per configuration "
                    "in the Phase L record, which is the best available estimate of "
                    "where fresh worlds will emerge. It is an estimate, not a "
                    "measurement.",
        },
        "seeds": {
            "consumed_blocks": consumed,
            "consumed_total": len(consumed_flat),
            "candidate_block": [block[0], block[-1]],
            "candidate_count": len(block),
            "preassigned": assignment,
            "preassigned_total": worlds_total,
            "unused": {"first": block[worlds_total], "last": block[-1],
                       "count": SPARE_SEEDS},
            "substitution_allowed": False,
            "overlap_with_consumed": overlap,
            "disjoint_proved_against": len(consumed),
            "allocated": False,
            "note": "Every configuration's seeds are pre-assigned before any world "
                    "runs, the spare seeds are named as unused, and substitution is "
                    "prohibited: a censored world does not release its seed to "
                    "another world, and the spare seeds are never drawn.",
        },
        "analysis": {
            "unit": "one world (seed) within one configuration",
            "estimator": "Spearman rank correlation between confirmed onset and "
                         "revision_held_out across worlds of one configuration",
            "effect_size_beside_it": "OLS slope of standardised outcome on "
                                     "standardised onset",
            "interval": "percentile bootstrap resampling worlds within the "
                        "configuration, %s level, 10,000 replicates" % LEVEL,
            "pooling": "none; every configuration is reported alone and no pooled "
                       "coefficient may be quoted",
            "aggregation_rule": "the construct is supported only if the predicted "
                                "relation holds with an interval excluding zero in "
                                "every claimed configuration. Holding in some and not "
                                "others is reported as mixed and is not supported as "
                                "stated",
            "permutation_control": "onset shuffled across worlds within the "
                                   "configuration; the interval must include zero",
            "size_baseline": "the same estimator with structural size in place of "
                             "onset, reported beside it",
        },
        "falsifiers": [
            {"id": "A", "name": "Absence",
             "statement": "a within-configuration interval containing zero in any "
                          "claimed configuration leaves the construct unsupported"},
            {"id": "B", "name": "Reversal",
             "statement": "a relation with the opposite sign is recorded as reversed, "
                          "which is stronger than unsupported"},
            {"id": "C", "name": "Dead configuration",
             "statement": "onset undefined in most runs of a configuration is a world "
                          "property, reported as such and never as a null"},
            {"id": "D", "name": "Pooled only",
             "statement": "a relation across configurations but not inside one does "
                          "not answer the protocol's question and does not support "
                          "the construct"},
        ],
        "outcomes": {
            "supported": "present with the predicted sign in every claimed "
                         "configuration, size baseline and permutation both null",
            "mixed": "present in some, absent in others; not supported as stated",
            "not_supported": "absent in every configuration",
            "reversed": "reversed in any configuration, recorded there",
            "size_effect": "explained by structural size rather than onset",
            "design_defect": "permutation control non-null, a predictor built from "
                             "behavioural cycles, or an endpoint whose quantum cannot "
                             "resolve the declared effect",
            "inconclusive": "fewer usable worlds than the floor after censoring",
            "underpowered_for_the_claim": "the reviewer or the power computation "
                                          "concludes the block is too small; that is "
                                          "a design limitation found before any cycle "
                                          "is spent, not a failure of the project",
        },
        "review_gate": {
            "document": "docs/INDEPENDENT-METHODS-REVIEW.md",
            "outcome_recorded": False,
            "may_reject": True,
            "authority": "Approved / Approved with conditions / Rejected; a rejection "
                         "is recorded verbatim and is not argued into an approval",
            "questions_for_the_reviewer": [
                "is the block size adequately justified at the declared reliability "
                "assumption, and is the ladder the right way to handle an unmeasured "
                "reliability?",
                "is the sustention-rule agreement correctly described as robustness "
                "rather than reliability, and is it right to exclude it from the "
                "arithmetic?",
                "does the behavioural endpoint have sufficient resolution, and is its "
                "operational definition unambiguous in the code named in section 3?",
                "are the pre-assigned seeds, the four unused seeds and the "
                "no-substitution rule sufficient to keep attrition from becoming a "
                "search?",
                "does the aggregation rule, which requires the relation in every "
                "claimed configuration, prevent a favourable but misleading reading?",
            ],
            "send_with_the_package": [
                "docs/DI-MEASUREMENT-WINDOW.md",
                "docs/DI-TRANSITION-CONSTRUCT.md",
                "docs/di_transition_construct.json",
                "docs/STAGE-B-PROTOCOL.md",
                "docs/stage_b_protocol.json",
                "docs/STRUCTURE-BEHAVIOR-DESIGN.md",
                "docs/sign_resolution_structure_behavior.json",
                "docs/V1-SYNTHESIS.md",
            ],
            "history_for_the_reviewer": [
                "the Stage A dynamic-range claim (\"0.44 pairs against a one-pair "
                "floor\") and its withdrawal: it compared a 40-cycle mean to a "
                "single-cycle quantum",
                "the 20 of 119 onsets that are not the first non-zero reading, and "
                "the 2 runs whose eligibility depends on the sustention rule",
                "the behavioural horizon's index-versus-count reconciliation",
                "the 0.972 agreement statistic first presented as a reliability "
                "proxy, and its correction: it is robustness of the ordering, and the "
                "block is now sized at a declared assumption instead",
                "the four block-level criteria that failed in earlier phases and were "
                "reported rather than re-scored",
            ],
        },
        "withdrawn_claims": [
            {"claim": "the settled-window predictor has 0.44 pairs of spread against a "
                      "one-pair floor, so the dynamic range is the obstacle",
             "status": "withdrawn in place",
             "why": "it compared a 40-cycle mean to a single-cycle quantum; 0.44 pairs "
                    "is real spread, and the decisive defect is that no settled state "
                    "exists to measure",
             "where": "docs/DI-MEASUREMENT-WINDOW.md"},
            {"claim": "onset is a validated predictor",
             "status": "never claimed, and not established",
             "why": "no relation between onset and any behavioural endpoint has been "
                    "computed, by design",
             "where": "docs/DI-TRANSITION-CONSTRUCT.md §5"},
            {"claim": "onset has a reliability of 0.972, so the 54-world block is "
                      "attenuation-corrected",
             "status": "withdrawn in place",
             "why": "the 0.972 is the agreement between two sustention rules on the "
                    "same trajectories; it is robustness of the ordering, not a "
                    "reliability coefficient, and using it as one required an "
                    "unjustified substitution",
             "where": "docs/STAGE-B-PROTOCOL.md §6"},
        ],
        "inherited_sign_resolution": {
            "artifact": "docs/sign_resolution_structure_behavior.json",
            "published_floor_at_effect_0_50": PUBLISHED_FLOOR,
            "closed_form_reproduces_it": floor_worlds == PUBLISHED_FLOOR,
            "status_field_as_published": signres.get("status"),
        },
        "no_engine": "No engine ran, no seed was spent, no world was generated, and no "
                     "coefficient was computed. This artifact is a protocol.",
    }


def main() -> dict:
    result = build()
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))
    s = result["sample_size"]
    print("\nagreement (reported, not used):",
          result["sustention_rule_agreement"]["worst_pair_spearman"])
    for rel, row in s["attenuation_ladder"].items():
        print("  rel %s -> effect %.4f -> %3d/config (%4d total)"
              % (rel, row["observed_effect_spearman"],
                 row["worlds_per_configuration"],
                 row["worlds_per_configuration"] * len(CLAIMED)))
    print("planning assumption:", s["reliability_planning_assumption"], "->",
          s["worlds_per_configuration"], "per config,", s["worlds_total"], "total")
    print("horizons:", result["clock"]["median_horizon_by_config_cycles"])
    print("cycles:", result["cost"]["cycles_total"], "rel:",
          result["cost"]["relative_to_phase_l"])
    print("seeds:", result["seeds"]["candidate_block"],
          result["seeds"]["candidate_count"], "unused:", result["seeds"]["unused"],
          "overlap:", result["seeds"]["overlap_with_consumed"])
    print("consumed:", result["seeds"]["consumed_total"], "across",
          result["seeds"]["disjoint_proved_against"])
    print("preassigned:", result["seeds"]["preassigned"])
    return result


if __name__ == "__main__":
    main()
