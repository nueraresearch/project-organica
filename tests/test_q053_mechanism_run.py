"""The Q053 block's mechanism is bounded, and its recorded verdict is the scorer's."""
import json

from benchmarks import q053_mechanism_run as R


class _H:
    def __init__(self, subject, expectation, support, ident):
        self.subject = subject
        self.expectation = expectation
        self.support_count = support
        self.id = ident


def test_the_floor_keeps_the_best_hypothesis_of_the_top_two_expectations():
    beliefs = [
        _H("alpha", "bravo", 40, "a1"),
        _H("alpha", "charlie", 10, "a2"),
        _H("alpha", "delta", 5, "a3"),
    ]
    kept = R.floor_selection(beliefs, 15)
    assert {h.expectation for h in kept} == {"bravo", "charlie"}, kept
    assert next(h for h in kept if h.expectation == "bravo") is beliefs[0]


def test_the_floor_adds_nothing_when_a_subject_has_one_expectation():
    beliefs = [_H("alpha", "bravo", 40, "a1"), _H("alpha", "bravo", 10, "a2")]
    kept = R.floor_selection(beliefs, 15)
    assert len(kept) == 1 and kept[0].id == "a1"


def test_the_floor_respects_the_hypothesis_cap():
    beliefs = [_H("subject%d" % i, "exp%d" % j, i * 10 + j, "h%d%d" % (i, j))
               for i in range(10) for j in range(3)]
    kept = R.floor_selection(beliefs, 15)
    assert len(kept) == 15
    assert len({h.id for h in kept}) == 15


def test_competing_subjects_excludes_the_structural_marker():
    beliefs = [_H("alpha", "bravo", 10, "a1"), _H("alpha", R.MARKER, 9, "a2")]
    assert R.competing_subjects(beliefs) == {}
    beliefs.append(_H("alpha", "charlie", 8, "a3"))
    assert R.competing_subjects(beliefs) == {"alpha": 2}


def test_the_recorded_artifact_is_the_block_and_the_scorer_agrees():
    artifact = json.loads(R.ARTIFACT.read_text(encoding="utf-8"))
    body = R.P.prereg()
    assert artifact["prereg"] == body["prereg"]
    expected = {(seed, arm) for seed in body["design"]["seeds"] for arm in R.ARMS}
    assert {(cell["seed"], cell["arm"]) for cell in artifact["cells"]} == expected
    label, details = R.P.verdict(body, artifact)
    assert (label, details) == (artifact["verdict"], artifact["details"])
    assert artifact["verdict"] in R.P.VERDICTS


def test_check_mode_writes_nothing():
    before = R.DOC.read_bytes()
    assert R.main(["--check"]) == 0
    assert R.DOC.read_bytes() == before
