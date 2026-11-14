"""The one-page A1 disposition memo, checked against the record's own figures."""
from pathlib import Path

TEXT = Path("docs/A1-DISPOSITION-MEMO.md").read_text(encoding="utf-8")


def test_memo_is_decision_support_not_a_decision():
    assert "A1-DISPOSITION-1" in TEXT
    assert "DRAFT — OWNER DECISION REQUIRED; NO FREEZE, NO GRANT, NO RUN" in TEXT
    assert "does not choose" in TEXT
    assert "no target is frozen, no seed is reserved and no A1 cell has run." in TEXT
    assert "Current default:** hold" in TEXT


def test_memo_carries_the_c1_and_k_figures():
    for phrase in (
        "31–44",
        "382 candidate + 286 reverse + 4 extra",
        "384 unique undirected edges",
        "281", "228", "95", "42", "59",
        "16–29 rows",
        "31.8%", "89.1%", "28–31 edges",
        "154/382", "28/228",
        "44.7–77.1%", "0–100%", "97.2%",
        "93.8–95.2%", "75%", "62.5%", "50%",
    ):
        assert phrase in TEXT, phrase


def test_memo_carries_the_competitive_target_figures():
    for phrase in (
        "23–36 A&K-available rows",
        "6/6",
        "12/24",
        "20 competent targets",
        "pre-treatment rather than future-blind",
        "still does not repair C1",
    ):
        assert phrase in TEXT, phrase


def test_memo_has_both_branches_and_a_stop_rule():
    assert "## 3. Redesign branch — requirements" in TEXT
    assert "## 4. Park branch — criteria" in TEXT
    assert "**Stop rule:**" in TEXT
    assert "do not freeze, do not grant and do not run" in TEXT
    assert "not run / not identified under the current design" in TEXT
    assert "does not mean treatment failure" in TEXT
    assert "## 5. Decision rule" in TEXT
    assert "## 6. What would settle it" in TEXT


def test_memo_links_the_source_records():
    for target in (
        "A1-DESIGN-VIABILITY.md",
        "A1-K-DECOMPOSITION.md",
        "A1-N20-COMPETENT-SELECTION.md",
        "A1-BASELINE-AVAILABILITY.md",
        "A1-TARGET-VIABILITY.md",
        "A1-PRE-FREEZE-CHECKLIST.md",
    ):
        assert target in TEXT, target
