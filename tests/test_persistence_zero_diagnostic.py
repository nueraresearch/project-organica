"""The zero-S_ever diagnostic must stay tied to the committed runs and the replay ceiling."""
LAYER = "static"

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import persistence_zero_diagnostic as diag  # noqa: E402


def artifact() -> dict:
    return json.loads(diag.ARTIFACT.read_text(encoding="utf-8"))


def test_the_artifact_checks_and_the_page_is_rendered():
    assert diag.problems() == []
    assert diag.PAGE.read_text(encoding="utf-8").strip() == diag.render(artifact()).strip()


def test_every_zero_cell_is_a_seed_that_never_reaches_the_floor():
    art = artifact()
    zero = [row for row in art["rows"] if row["arm"] == "persistence_off"
            and row["observed_s_ever"] == 0]
    assert len(zero) == 5
    assert all(row["admissible_world_edges"] == 0 for row in zero)
    assert all(row["max_world_count"] < diag.FLOOR for row in zero)
    for row in art["rows"]:
        if row["arm"] == "persistence_off" and row["observed_s_ever"] > 0:
            assert row["admissible_world_edges"] == row["observed_s_ever"]
        if row["arm"] == "shipped":
            assert row["observed_s_ever"] <= row["admissible_world_edges"]


def test_the_full_serving_run_matches_the_cells():
    art = artifact()
    assert len(art["serving"]) == 7
    for row in art["serving"]:
        assert row["served_world_edges"] == row["observed_s_ever"]
    zero = [row for row in art["serving"] if row["observed_s_ever"] == 0]
    controls = [row for row in art["serving"] if row["observed_s_ever"] > 0]
    assert len(zero) == 5 and len(controls) == 2
    assert all(row["served_world_edges"] == 0 for row in zero)
    assert all(row["served_world_edges"] > 0 for row in controls)


def test_a_zero_cell_with_an_admissible_edge_is_rejected():
    art = artifact()
    bad = copy.deepcopy(art)
    zero = next(row for row in bad["rows"] if row["arm"] == "persistence_off"
                and row["observed_s_ever"] == 0)
    zero["admissible_world_edges"] = 1
    assert diag.problems(art=bad, page=diag.render(bad))


def test_a_zero_cell_that_serves_is_rejected():
    art = artifact()
    bad = copy.deepcopy(art)
    zero = next(row for row in bad["serving"] if row["observed_s_ever"] == 0)
    zero["served_world_edges"] = 1
    assert diag.problems(art=bad, page=diag.render(bad))
