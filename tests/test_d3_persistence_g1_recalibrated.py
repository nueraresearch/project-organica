"""Pin the exact D3-4 reading: G1, W1, P1, C1, and the label they imply.

The stamped artifact is the record. These assertions recompute each criterion from the
cells rather than reading the verdict's prose, so a change to any cell, to the G1 bound or
to the frozen scorer is caught here instead of being restated as a passing block.
"""

import json
import statistics

import pytest

from benchmarks import d3_persistence_g1_recalibrated as G
from benchmarks import d3_persistence_prereg as P

BODY = G.prereg()
ARTIFACT = json.loads(G.ARTIFACT.read_text(encoding="utf-8"))
SEEDS = list(BODY["design"]["seeds"])
CELLS = {(cell["stage"], cell["seed"], cell["arm"]): cell for cell in ARTIFACT["cells"]}

# The exact control preflight death, seeded in the artifact. Only the first seed dies late.
CONTROL_FIRST_ZERO = {
    20611301: 58,
    20611302: 59,
    20611303: 59,
    20611304: 59,
    20611305: 59,
    20611306: 59,
}


def test_the_block_is_d3_4_on_the_shipped_engine():
    assert ARTIFACT["kind"] == G.KIND
    assert ARTIFACT["prereg"] == BODY["prereg"] == "D3-PERSISTENCE-4"
    assert ARTIFACT["engine"]["version"] == "0.14.0"
    assert len(SEEDS) == 6 and len(set(SEEDS)) == 6
    assert len(ARTIFACT["cells"]) == BODY["design"]["cells"] == 24
    assert ARTIFACT["seed_axis"]["live"] is True
    assert ARTIFACT["seed_axis"]["effective_n"] == 6
    assert set(CELLS) == {(stage, seed, arm) for stage in G.STAGES
                         for seed in SEEDS for arm in G.ARMS}


def test_g1_the_control_dies_inside_the_recalibrated_bound():
    assert BODY["g1_max_first_zero"] == 65
    observed = {seed: CELLS[("preflight", seed, "control")]["first_zero_cycle"]
                for seed in SEEDS}
    assert observed == CONTROL_FIRST_ZERO
    assert all(1 <= cycle <= BODY["g1_max_first_zero"] for cycle in observed.values())


def test_w1_all_six_treatment_witnesses_hold_39_cycles_and_peak_six():
    readings = [(CELLS[("witness", seed, "treatment")]["theory_cycles"],
                 CELLS[("witness", seed, "treatment")]["peak"])
                for seed in SEEDS]
    assert readings == [(39, 6)] * 6
    assert ARTIFACT["witness_negative_controls"]["NO_DREAMS"]["dreams_max"] == 0
    assert ARTIFACT["witness_negative_controls"]["NO_QUESTIONS"]["questions_max"] == 0


def test_p1_all_six_treatment_cells_survive_the_3000_cycle_horizon():
    for seed in SEEDS:
        cell = CELLS[("preflight", seed, "treatment")]
        counts = cell["theory_counts"]
        assert cell["first_zero_cycle"] is None
        assert cell["cycles_run"] == 3000 and len(counts) == 3000
        assert min(counts[-100:]) == 4


def test_c1_the_early_gap_is_exactly_zero_and_clears_the_bar():
    gaps = [CELLS[("preflight", seed, "treatment")]["recall_early"]
            - CELLS[("preflight", seed, "control")]["recall_early"]
            for seed in SEEDS]
    assert gaps == [0.0] * 6
    assert statistics.median(gaps) == 0.0
    assert BODY["criteria"]["C1_early_cost"]["bar"] == -0.01
    assert 0.0 >= BODY["criteria"]["C1_early_cost"]["bar"]


def test_the_stamped_verdict_is_persistence_repaired():
    assert (ARTIFACT["verdict"], ARTIFACT["details"]) == (
        "PERSISTENCE REPAIRED",
        {"alive_seeds": 6, "seeds": 6, "early_median_gap": 0.0, "early_bar": -0.01},
    )
    assert P.verdict(BODY, ARTIFACT) == (ARTIFACT["verdict"], ARTIFACT["details"])


def test_the_runner_check_is_clean():
    assert G.check() == 0


def test_the_scorer_still_refuses_a_control_that_dies_past_the_bound():
    # The recalibrated bound must remain able to void the block; otherwise G1 is decoration.
    forged = json.loads(json.dumps(ARTIFACT))
    body = dict(BODY, g1_max_first_zero=57)
    assert P.verdict(body, forged) == ("VOID", {"gate": "G1_baseline_death",
                                                "seed": 20611301})
