"""The A1 park recommendation is a recommendation, not an owner decision."""
from pathlib import Path

TEXT = Path("docs/A1-PARK-RECOMMENDATION.md").read_text(encoding="utf-8")


def test_recommendation_is_unsigned_and_does_not_run_anything():
    assert "A1-PARK-RECOMMENDATION-1" in TEXT
    assert "RECOMMENDATION — OWNER DECISION REQUIRED; NO FREEZE, NO GRANT, NO RUN" in TEXT
    assert "**Recommendation: park the current A1 design.**" in TEXT
    assert "This is a recommendation, not the owner's decision" in TEXT
    assert "No target is frozen, no seed is reserved, no grant is issued and no A1 cell is run." in TEXT


def test_recommendation_carries_both_failed_candidates():
    for phrase in (
        "44, 31, 39, 35, 43, 36",
        "40, 37, 46, 42, 31, 38",
        "158–172",
        "23, 40, 42, 55, 47, 37",
        "23–55",
        "18, 15, 16, 26, 26, 18",
        "14 rows short",
        "five short",
    ):
        assert phrase in TEXT, phrase


def test_park_scope_is_not_a_treatment_claim():
    assert "Park does not mean" in TEXT
    assert "treatment failure" in TEXT
    assert "negative C2/C8 result" in TEXT
    assert "evidence that the effect is absent" in TEXT
    assert "not identified under the current design" in TEXT


def test_reopen_conditions_are_explicit():
    for phrase in (
        "without selecting on K",
        "60 independent C1 rows",
        "20-row",
        "one edge universe",
        "new protocol, freeze, seed reservation and dated grant",
        "specifically explain and overcome the measured K dilution",
        "a larger edge count alone is not enough",
    ):
        assert phrase in TEXT, phrase
