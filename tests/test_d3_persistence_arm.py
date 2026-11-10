"""The frozen D3 arm must be usable by the pre-flight, and its denominator must decay as frozen."""
from benchmarks import tier1_preflight as tp
from benchmarks.d3_persistence_arm import MatchedFrequencySleepService as Arm


class Sentinel:
    """A stand-in for the treatment class: build only has to forward it."""


def _check(name, theories):
    zeros = {name: [0, 0, 0, 0]}
    return {
        "colony": name,
        "retention_policy": "alphabetical" if name == "FULL" else "salience",
        "contradiction_scale": 0.0,
        "theory_cycles": 4 if theories else 0,
        "series": {
            "theories": [theories] * 4,
            "dreams": zeros.get("NO_DREAMS", [1, 1, 1, 1]),
            "questions": zeros.get("NO_QUESTIONS", [1, 1, 1, 1]),
        },
    }


def test_the_preflight_forwards_the_fixed_arm_to_the_witness_and_the_campaign(monkeypatch):
    calls = {}
    checks = [_check("FULL", 4), _check("SALIENCE", 3), _check("NO_CONTRADICTIONS", 1),
              _check("NO_DREAMS", 0), _check("NO_QUESTIONS", 1), _check("ANTI_EIG", 1)]

    def verify(events, cycles, service_class=None):
        calls["witness"] = service_class
        return checks, []

    def trace(design, horizon, seed, stop_at_death=True, service_class=None):
        calls["campaign"] = service_class
        return {"design": design, "horizon": horizon, "cycles_run": horizon, "peak": 4,
                "first_zero_cycle": None, "alive_at_horizon": True,
                "theory_counts": [4] * horizon}

    monkeypatch.setattr(tp.fm, "verify_colonies", verify)
    monkeypatch.setattr(tp.fm, "trace_reference", trace)

    shipped = tp.build(witness_cycles=4, horizon=8)
    fixed = tp.build(witness_cycles=4, horizon=8, reference_class=Sentinel)

    assert calls["witness"] is Sentinel and calls["campaign"] is Sentinel
    assert shipped["verdict"] == "PASSES" and fixed["verdict"] == "PASSES"
    # The hook changes which arm runs, not how a result is decided.
    assert {k: shipped[k] for k in ("verdict", "launch_blocked")} == {
        k: fixed[k] for k in ("verdict", "launch_blocked")}


def test_the_denominator_decays_with_the_temporal_graph():
    arm = object.__new__(Arm)
    arm._decayed_freqs = {}
    arm._last_raw = {}
    arm.frequency_updates = 0

    assert arm._update({"a": 10}) == {"a": 10.0}
    # D = 0.95 * previous + the raw count's increase, per tag.
    assert arm._update({"a": 20, "b": 5}) == {"a": 19.5, "b": 5.0}
    # A tag absent from the raw graph decays; it does not vanish.
    assert arm._update({"a": 20}) == {"a": 18.525, "b": 4.75}
    assert arm.frequency_updates == 3


def test_the_arm_keeps_every_shipped_constant_except_the_denominator():
    assert issubclass(Arm, tp.fm.SleepService)
    assert Arm.FREQUENCY_DECAY == 0.95
    assert Arm.TEMPORAL_DECAY_FACTOR == 0.95
    assert Arm.DEATH_THRESHOLD == 0.15
