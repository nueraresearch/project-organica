"""The A1 pre-freeze machinery: U ordering, target selection and target-set checks."""
import inspect

from benchmarks import a1_arms
from benchmarks import a1_target_selection as selection
from benchmarks import a1_two_path


def test_cycle_36_u_is_sampled_before_consolidation():
    source = inspect.getsource(a1_arms.run_cell)
    assert source.index("pending_u = sample_u(") < source.index("report = service.run_sleep_cycle()")


def test_u_row_reports_direct_reverse_and_strength():
    class Memory:
        def temporal_edges(self, min_count=1):
            assert min_count == 1
            return [("a", "b", 3), ("b", "a", 2)]

    row = a1_arms.sample_u(Memory(), {("a", "b")}, 36)[("a", "b")]
    assert row == {
        "direct_count": 3,
        "reverse_count": 2,
        "strength": 5,
        "measured_cycle": 36,
    }


def test_selection_is_deterministic_and_magnitude_blind():
    universe = {
        ("a", "b"), ("b", "a"), ("c", "d"), ("d", "c"),
        ("e", "f"), ("f", "e"), ("g", "h"), ("h", "g"),
    }
    candidates = selection.candidate_edges(7, universe)
    assert candidates == selection.candidate_edges(7, universe)
    temporal = {
        "a": {"b": 1}, "b": {"a": 1},
        "c": {"d": 1}, "d": {"c": 1},
        "e": {"f": 1}, "f": {"e": 1},
        "g": {"h": 1}, "h": {"g": 1},
    }
    members = selection.cycle_members(temporal, candidates)
    u = {edge: selection._u_row(temporal, edge, 36) for edge in candidates}
    first, _ = selection.select_edges(7, candidates, u, members)
    bigger = {edge: dict(value, strength=value["strength"] + 100) for edge, value in u.items()}
    second, _ = selection.select_edges(7, candidates, bigger, members)
    assert first == second
    assert len(first) == 4


def test_selection_refuses_to_reduce_below_n():
    universe = {("a", "b"), ("b", "a"), ("c", "d"), ("d", "c"), ("e", "f"), ("f", "e")}
    candidates = selection.candidate_edges(7, universe)
    temporal = {"a": {"b": 1}, "b": {"a": 1}, "c": {"d": 1}, "d": {"c": 1},
                "e": {"f": 1}, "f": {"e": 1}}
    members = selection.cycle_members(temporal, candidates)
    u = {edge: selection._u_row(temporal, edge, 36) for edge in candidates}
    selected, _ = selection.select_edges(7, candidates, u, members)
    assert selected == []


def test_target_set_problems_accepts_four_disjoint_world_edges():
    doc = a1_two_path.manifest()
    doc["targets"]["status"] = "FIXED BEFORE FREEZE"
    doc["targets"]["by_seed"] = {
        str(seed): a1_two_path._artifact_targets(seed) for seed in a1_two_path.SEEDS
    }
    assert a1_two_path.target_set_problems(doc) == []


def test_target_set_problems_rejects_short_and_overlapping_sets():
    doc = a1_two_path.manifest()
    doc["targets"]["status"] = "FIXED BEFORE FREEZE"
    doc["targets"]["by_seed"] = {
        str(seed): a1_two_path._artifact_targets(seed) for seed in a1_two_path.SEEDS
    }
    first_seed = str(a1_two_path.SEEDS[0])
    doc["targets"]["by_seed"][first_seed] = doc["targets"]["by_seed"][first_seed][:3]
    problems = a1_two_path.target_set_problems(doc)
    assert any("does not have 4 targets" in problem for problem in problems)

    doc["targets"]["by_seed"] = {
        str(seed): a1_two_path._artifact_targets(seed) for seed in a1_two_path.SEEDS
    }
    edges = doc["targets"]["by_seed"][first_seed]
    a, _ = edges[0].split(">", 1)
    _, b = edges[1].split(">", 1)
    doc["targets"]["by_seed"][first_seed][1] = "%s>%s" % (a, b)
    problems = a1_two_path.target_set_problems(doc)
    assert any("disjoint" in problem for problem in problems)


def test_selection_self_test():
    assert selection.self_test() == []


def test_selection_artifact_is_internally_consistent():
    import json
    doc = json.loads(selection.OUT_PATH.read_text(encoding="utf-8"))
    assert selection.problems(doc) == []
    assert sum(len(row["selected"]) for row in doc["per_seed"].values()) == 24


def test_adversarial_audit_artifact_is_current():
    import json
    from benchmarks import a1_adversarial_audit as audit
    doc = json.loads(audit.OUT_PATH.read_text(encoding="utf-8"))
    assert audit.problems(doc) == []
    assert audit.PAGE_PATH.read_text(encoding="utf-8") == audit.render(doc)
