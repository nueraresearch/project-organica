"""Adoption authorises the primitive build, and this record writes no code."""
import json
from pathlib import Path

from benchmarks import v2_first_cell_gates as gates

ROOT = Path(__file__).resolve().parents[1]


def _entry():
    data = json.loads((ROOT / "docs" / "decisions.json").read_text(encoding="utf-8"))
    return next(d for d in data["decisions"] if d["decision_id"] == "DECISION-V2-PRIMITIVE-BUILD")


def test_adoption_authorises_the_build_but_writes_no_code():
    entry = _entry()
    assert entry["status"] == "ADOPTED"
    assert "THIS RECORD WRITES NO CODE" in entry["status_quote"]
    assert not (ROOT / "benchmarks" / "v2_primitive.py").exists()


def test_the_build_is_bounded_to_one_benchmark_module():
    chosen = " ".join(_entry()["chosen"])
    assert "one new benchmark module and its tests" in chosen
    assert "never the live" in chosen
    assert "`m`" in chosen and "`DECISION-V2-FIRST-CELL`" in chosen


def test_the_gate_record_still_reports_a2_to_a5_not_run():
    record = gates._load(gates.OUT)
    assert [record["gates"][gate]["status"] for gate in ("A1", "A2", "A3", "A4", "A5")] == [
        "PASS", "NOT RUN", "NOT RUN", "NOT RUN", "NOT RUN"
    ]


def test_the_decision_stops_at_the_gate_record():
    entry = _entry()
    assert "The build stops when A2–A5 have a gate record" in entry["chosen"][2]
