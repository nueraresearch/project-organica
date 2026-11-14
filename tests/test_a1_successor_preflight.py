"""The no-arm successor preflight, including its negative control."""
import json
from pathlib import Path

from benchmarks import a1_successor_preflight as preflight

LAYER = "static"  # reads committed no-arm rows; runs and selects nothing


def _artifact():
    return json.loads(
        Path("docs/a1_successor_preflight.json").read_text(encoding="utf-8")
    )


def test_preflight_is_not_run_and_control_fails():
    doc = _artifact()
    assert preflight.problems(doc) == []
    assert doc["status"] == "NOT RUN — NO SUCCESSOR UNIVERSE; CURRENT CONTROL FAILS"
    assert doc["successor"]["status"] == "NOT RUN"
    assert "NO_SUCCESSOR_UNIVERSE" in doc["successor"]["problems"]
    assert doc["current_control"]["status"] == "FAIL"
    assert doc["gate"]["freeze"] is False
    assert doc["gate"]["grant"] is False
    assert doc["gate"]["run"] is False


def test_current_control_is_the_known_c1_failure():
    rows = {row["seed"]: row for row in _artifact()["current_control"]["per_seed"]}
    assert [rows[seed]["independent_edges"] for seed in preflight.SEEDS] == [
        64, 63, 64, 64, 64, 63,
    ]
    assert [rows[seed]["A_available"] for seed in preflight.SEEDS] == [
        44, 44, 52, 43, 49, 49,
    ]
    assert [rows[seed]["K_available"] for seed in preflight.SEEDS] == [
        44, 31, 39, 35, 43, 36,
    ]
    assert [rows[seed]["C1_ceiling"] for seed in preflight.SEEDS] == [
        44, 31, 39, 35, 43, 36,
    ]
    assert [rows[seed]["target_matching"] for seed in preflight.SEEDS] == [
        32, 23, 36, 27, 35, 33,
    ]
    assert all(row["reasons"] == ["C1_BELOW_60"] for row in rows.values())
    assert _artifact()["current_control"]["seeds_passed"] == 0


def test_clean_synthetic_candidate_passes_and_reverse_duplicate_fails():
    tags = ["t%02d" % i for i in range(16)]
    edges = sorted({
        "%s>%s" % (tags[i], tags[(i + j) % 16])
        for i in range(16) for j in range(1, 5)
    })[:64]
    spec = {
        "kind": "a1_successor_candidate",
        "id": "fixture",
        "seed_block": list(range(1, 7)),
        "targets_in_scope": True,
        "per_seed": {
            str(seed): [{"edge": edge, "A": True, "K": True} for edge in edges]
            for seed in range(1, 7)
        },
    }
    result = preflight.evaluate(spec)
    assert result["status"] == "PASS"
    assert all(row["pass"] for row in result["per_seed"])
    assert result["per_seed"][0]["target_matching"] >= 20

    bad = json.loads(json.dumps(spec))
    first = bad["per_seed"]["1"][0]["edge"]
    source, target = first.split(">", 1)
    bad["per_seed"]["1"].append(
        {"edge": target + ">" + source, "A": True, "K": True})
    result = preflight.evaluate(bad)
    assert result["status"] == "FAIL"
    assert "REVERSE_DUPLICATE" in result["per_seed"][0]["reasons"]


def test_preflight_rejects_a_short_or_duplicate_seed_block():
    spec = {
        "kind": "a1_successor_candidate",
        "id": "short",
        "seed_block": [1, 1],
        "targets_in_scope": False,
        "per_seed": {"1": [{"edge": "a>b", "A": True, "K": True}]},
    }
    result = preflight.evaluate(spec)
    assert result["status"] == "FAIL"
    assert "TOO_FEW_SEEDS" in result["problems"]
    assert "DUPLICATE_SEED" in result["problems"]


def test_page_is_current_and_does_not_claim_a_run():
    doc = _artifact()
    page = Path("docs/A1-SUCCESSOR-PREFLIGHT.md").read_text(encoding="utf-8")
    assert page == preflight.render(doc) + "\n"
    assert "NOT RUN" in page
    assert "CURRENT CONTROL FAILS" in page
    assert "does **not** freeze" in page
    assert preflight.self_test() == []
