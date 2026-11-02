"""Stage B: the protocol's numbers, assembled from artifacts rather than typed.

The construct record (`docs/DI-TRANSITION-CONSTRUCT.md`) fixed what onset means,
what counts as eligible and when behaviour may begin. This module turns those
decisions into the numbers a protocol needs -- the block size, the run horizon and
the seed block -- by *reading* the record rather than restating it, and it proves
the seed block is unused by scanning every artifact in ``docs/`` for seed fields.

Two things it deliberately does not do. It runs no engine, so it allocates no
world; and it computes no relation between onset and behaviour, because the whole
point of Stage A was to fix the predictor before any outcome exists.

The block size is a consequence of the claim, not a budget: the required number of
worlds is solved from the project's own decision rule (a rank correlation whose
98.33 % interval must exclude zero with the predicted sign, in 90 % of blocks), at
the smallest relation worth calling predictive, attenuated by the only reliability
estimate this project can offer for onset -- how closely two different sustention
rules agree on the same worlds.

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
LEVEL = 0.9833           # the project's decision interval, inherited
RESOLUTION_BAR = 0.90    # a block must recover the relation this often
SMALLEST_EFFECT = 0.50   # the weakest rank relation worth calling predictive
PUBLISHED_FLOOR = 48     # at reliability 1.00, from the sign-resolution artifact
MIN_REAL_SEED = 1000     # below this, an integer called "seed" is a count
CANDIDATE_BLOCK = (20270601, 20270820)


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


def _attenuate(rho: float, reliability: float) -> float:
    """Observed Spearman under classical independent error in the predictor."""
    r_g = rho * math.sqrt(reliability)
    return (6.0 / math.pi) * math.asin(r_g / 2.0)


def _worlds_for(effect: float, bar: float = RESOLUTION_BAR,
                level: float = LEVEL) -> int:
    """Worlds per configuration so a block resolves `effect` this often.

    A block resolves when Fisher's z interval at `level` excludes zero with the
    predicted sign, i.e. when atanh(rho_hat) exceeds the critical value. The
    probability of that is Phi(atanh(rho) * sqrt(n - 3) - z_crit), so the
    smallest n solving ``>= bar`` is the ceiling below. At effect 0.50 this
    returns the 48 the sign-resolution artifact published, which is the check
    that the closed form is doing the project's own rule and not a different one.
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

    # ---- the predictor, inherited rather than restated --------------------
    sustained = construct["onset_conventions"]["sustained_cycles"]
    assert sustained == 10
    assert clock["post_confirmation_margin_cycles"] == 1
    assert clock["follow_up_cycles"] == 100
    assert criteria["min_defined_share"] == 0.90
    assert criteria["min_sd_cycles"] == 3.0
    assert list(CLAIMED) == sorted(criteria["per_config"])

    # ---- reliability: how closely two rules agree on the same worlds ------
    pairs = ("5_vs_10", "10_vs_20", "5_vs_20")
    agreements = {lab: {p: rank[lab]["comparisons"][p]["spearman"] for p in pairs}
                  for lab in CLAIMED}
    agreement = min(min(row.values()) for row in agreements.values())
    agreement_where = min(
        ((lab, p) for lab in CLAIMED for p in pairs),
        key=lambda k: rank[k[0]]["comparisons"][k[1]]["spearman"])

    # ---- the block size, solved from the claim ---------------------------
    floor_worlds = _worlds_for(SMALLEST_EFFECT, bar=RESOLUTION_BAR, level=LEVEL)
    observed_effect = _attenuate(SMALLEST_EFFECT, agreement)
    assumed_reliability = 0.90          # the tabulated row at or below the proxy
    observed_at_row = _attenuate(SMALLEST_EFFECT, assumed_reliability)
    worlds_per_config = _worlds_for(observed_effect, bar=RESOLUTION_BAR, level=LEVEL)
    assert floor_worlds == PUBLISHED_FLOOR, (floor_worlds, PUBLISHED_FLOOR)

    # ---- the run horizon, per world ------------------------------------
    horizons = {lab: clock["per_config"][lab]["confirmation_cycle_median"]
                + clock["post_confirmation_margin_cycles"]
                + clock["follow_up_cycles"]
                for lab in CLAIMED}
    cycles_total = sum(horizons.values()) * worlds_per_config
    phase_l_cycles = 240 * 600

    # ---- the seed block, proved unused ---------------------------------
    consumed = _consumed_seeds()
    block = list(range(CANDIDATE_BLOCK[0], CANDIDATE_BLOCK[1] + 1))
    consumed_flat = {s for values in consumed.values() for s in values}
    overlap = sorted(set(block) & consumed_flat)
    assert not overlap, overlap[:10]
    assert len(block) >= worlds_per_config * len(CLAIMED), (
        len(block), worlds_per_config * len(CLAIMED))

    signres = json.loads(SIGNRES.read_text(encoding="utf-8"))

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
            "statement": "Stage B is not authorised. The seed block below is "
                         "candidate only: it is proved unused, which is not the "
                         "same as being spent. Nothing may be allocated until the "
                         "independent review records an outcome.",
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
            "resolution_requirement": "the endpoint's quantum (one held-out "
                                      "transition) and the number of held-out "
                                      "transitions must be reported before the run; "
                                      "a quantum coarser than the smallest effect "
                                      "the claim asserts makes the endpoint "
                                      "unmeasurable for that claim and stops the run",
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
            "reliability_proxy": "agreement between the 5-, 10- and 20-cycle "
                                 "sustention rules on the same worlds, taken at its "
                                 "worst pair. Test-retest is unavailable: the engine "
                                 "is deterministic per seed, so a re-run is not a "
                                 "replication",
            "agreement_by_config": agreements,
            "agreement_worst": agreement,
            "agreement_worst_at": {"configuration": agreement_where[0],
                                   "comparison": agreement_where[1]},
            "assumed_reliability_row": assumed_reliability,
            "attenuated_effect_at_proxy": round(observed_effect, 6),
            "attenuated_effect_at_row": round(observed_at_row, 6),
            "worlds_per_configuration_at_reliability_1": floor_worlds,
            "worlds_per_configuration": worlds_per_config,
            "worlds_total": worlds_per_config * len(CLAIMED),
            "reportable_floor_per_configuration": floor_worlds,
            "why_this_size": "The block is sized so that the decision rule resolves "
                             "a relation of the declared smallest size in %d %% of "
                             "blocks, after attenuation by the measured agreement "
                             "between sustention rules. It is a floor, not a target: "
                             "unmodelled dependence between worlds and any further "
                             "measurement error lower the real resolution "
                             "probability." % int(RESOLUTION_BAR * 100),
            "below_the_floor": "a configuration whose usable n falls below %d after "
                               "censoring is reported inconclusive, never null"
                               % floor_worlds,
            "no_replacement": "a censored world is not replaced: the denominator is "
                              "reported as realised",
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
            "candidate_block": list(CANDIDATE_BLOCK),
            "candidate_count": len(block),
            "overlap_with_consumed": overlap,
            "disjoint_proved_against": len(consumed),
            "allocated": False,
            "note": "Disjointness is checked against every integer filed under a key "
                    "naming a seed in every docs/ artifact, at build time. The block "
                    "is candidate only: no seed in it is allocated, and the "
                    "independent review must report before any is.",
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
                                "every claimed configuration. Holding in some and "
                                "not others is reported as mixed and is not "
                                "supported as stated",
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
             "statement": "a relation with the opposite sign is recorded as "
                          "reversed, which is stronger than unsupported"},
            {"id": "C", "name": "Dead configuration",
             "statement": "onset undefined in most runs of a configuration is a "
                          "world property, reported as such and never as a null"},
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
            "design_defect": "permutation control non-null, or a predictor built "
                             "from behavioural cycles; no result is reported",
            "inconclusive": "fewer usable worlds than the floor after censoring",
        },
        "review_gate": {
            "document": "docs/INDEPENDENT-METHODS-REVIEW.md",
            "outcome_recorded": False,
            "may_reject": True,
            "authority": "Approved / Approved with conditions / Rejected; a "
                         "rejection is recorded verbatim and is not argued into an "
                         "approval",
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
                "the four blocks whose criteria failed and were reported rather than "
                "re-scored",
            ],
        },
        "withdrawn_claims": [
            {"claim": "the settled-window predictor has 0.44 pairs of spread against "
                      "a one-pair floor, so the dynamic range is the obstacle",
             "status": "withdrawn in place",
             "why": "it compared a 40-cycle mean to a single-cycle quantum; 0.44 "
                    "pairs is real spread, and the decisive defect is that no "
                    "settled state exists to measure",
             "where": "docs/DI-MEASUREMENT-WINDOW.md"},
            {"claim": "onset is a validated predictor",
             "status": "never claimed, and not established",
             "why": "no relation between onset and any behavioural endpoint has "
                    "been computed, by design",
             "where": "docs/DI-TRANSITION-CONSTRUCT.md §5"},
        ],
        "inherited_sign_resolution": {
            "artifact": "docs/sign_resolution_structure_behavior.json",
            "published_floor_at_effect_0_50": PUBLISHED_FLOOR,
            "closed_form_reproduces_it": floor_worlds == PUBLISHED_FLOOR,
            "status_field_as_published": signres.get("status"),
        },
        "no_engine": "No engine ran, no seed was spent, no world was generated, and "
                     "no coefficient was computed. This artifact is a protocol.",
    }


def main() -> dict:
    result = build()
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))
    s = result["sample_size"]
    print("\nagreement (worst pair):", s["agreement_worst"], s["agreement_worst_at"])
    print("attenuated effect:", s["attenuated_effect_at_proxy"])
    print("worlds per configuration:", s["worlds_per_configuration"],
          "(floor at reliability 1.00: %d)" % s["worlds_per_configuration_at_reliability_1"])
    print("worlds total:", s["worlds_total"])
    print("horizons:", result["clock"]["median_horizon_by_config_cycles"])
    print("cycles:", result["cost"]["cycles_total"],
          "relative to Phase L:", result["cost"]["relative_to_phase_l"])
    print("candidate seeds:", result["seeds"]["candidate_block"],
          "count", result["seeds"]["candidate_count"],
          "overlap", result["seeds"]["overlap_with_consumed"])
    print("consumed seeds:", result["seeds"]["consumed_total"],
          "across", result["seeds"]["disjoint_proved_against"], "artifacts")
    return result


if __name__ == "__main__":
    main()
