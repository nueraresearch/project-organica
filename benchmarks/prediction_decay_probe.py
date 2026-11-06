"""Counterfactual probe: temporal-edge decay starves the stable prior.

Runs the Tier-1 matrix's own stimulus and seed twice for 80 cycles:

  shipped   ``TEMPORAL_DECAY_FACTOR = 0.95`` -- the engine as committed
  no-decay  ``TEMPORAL_DECAY_FACTOR = 1.0``  -- a harness override, engine untouched

Prediction strength is ``count / max(source_freq, 1)``: the numerator is the
decayed temporal count and the denominator is the cumulative source frequency,
which keeps growing.  A decaying numerator over a growing denominator falls by
construction, and the stable filter (>= 0.3) drops enough predictions to break
the cycles that compose processes, hypotheses and theories.

The probe asserts the difference rather than printing it: with decay the
theory population is zero by cycle 79, without decay it is still five.  This is
the pattern a fix's regression test should follow.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.branch_streams import lattice_designs, lattice_stream  # noqa: E402
from organica.memory import MemoryService                            # noqa: E402
from organica.paths import temp_db                                   # noqa: E402
from organica.sleep import SleepService                              # noqa: E402
from organica.streams import EVENTS_PER_CYCLE                        # noqa: E402

CYCLES = 80
SEED = 20261023
STIMULUS = "L1_hub1_t3_disjoint"
MARKERS = 7  # structural markers inside the hypothesis output


class Full(SleepService):
    HYPOTHESIS_RETENTION = "alphabetical"

    def _form_and_test_hypotheses(self, *args, **kwargs):
        out = super()._form_and_test_hypotheses(*args, **kwargs)
        self.beliefs = max(0, len(out) - MARKERS)
        return out

    def _form_theories_and_questions(self, *args, **kwargs):
        out = super()._form_theories_and_questions(*args, **kwargs)
        self.theories = len(out[0]) if isinstance(out, tuple) else 0
        return out

    def _compose_processes(self, *args, **kwargs):
        out = super()._compose_processes(*args, **kwargs)
        self.processes = len(out)
        return out

    def _compose_workflows(self, *args, **kwargs):
        out = super()._compose_workflows(*args, **kwargs)
        self.workflows = len(out)
        return out


class NoDecay(Full):
    TEMPORAL_DECAY_FACTOR = 1.0


def run(cls, label: str, events: list[str]) -> dict:
    db = temp_db(f"prediction_decay_{label}.db")
    db.unlink(missing_ok=True)
    memory = MemoryService(db_path=str(db))
    service = cls(memory)
    service._rng.seed(SEED)
    for text in events:
        memory.store(text, event_type="event", source="seed:bootstrap")

    rows = []
    for cycle in range(CYCLES):
        start = (cycle * EVENTS_PER_CYCLE) % len(events)
        for text in events[start:start + EVENTS_PER_CYCLE]:
            memory.store(text, event_type="event", source=f"cycle:{cycle}")
        service.run_sleep_cycle()
        rows.append({
            "cycle": cycle,
            "beliefs": getattr(service, "beliefs", None),
            "theories": getattr(service, "theories", None),
            "processes": getattr(service, "processes", None),
            "workflows": getattr(service, "workflows", None),
        })
    memory.close()
    db.unlink(missing_ok=True)
    return {"label": label, "rows": rows}


def main() -> int:
    events = lattice_stream(lattice_designs()[STIMULUS]["triangles"])
    shipped = run(Full, "shipped", events)
    relaxed = run(NoDecay, "no-decay", events)

    print("cycle  shipped(beliefs theories processes)   no-decay(beliefs theories processes)")
    for i in (0, 5, 10, 20, 30, 35, 40, 50, 60, 79):
        a = shipped["rows"][i]
        b = relaxed["rows"][i]
        print("%5d  %8s %8s %9s   %8s %8s %9s"
              % (i, a["beliefs"], a["theories"], a["processes"],
                 b["beliefs"], b["theories"], b["processes"]))

    last_shipped = shipped["rows"][-1]
    last_relaxed = relaxed["rows"][-1]
    problems = []
    if last_shipped["theories"] != 0:
        problems.append("expected the shipped arm to lose its theories by cycle 79")
    if last_relaxed["theories"] != 5:
        problems.append("expected the no-decay arm to keep five theories")
    if (last_relaxed["processes"] or 0) < 10:
        problems.append("expected the no-decay arm to keep its processes")
    for problem in problems:
        print("!! " + problem)
    if problems:
        return 1
    print("decay starves the upper layers; disabling it preserves them")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
