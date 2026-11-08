"""The competition census on a second world family (Q052 framing).

`docs/Q052-FRAMING-DESIGN.md` fixes this measurement before it runs. The lattice census
found that the theory layer dies when every subject stops retaining two competing
hypotheses while the supports are still in the hundreds. That census exists only for
`lattice_L1`, one factor, one stimulus family. This instrument repeats it on the second
family the capability instrument already builds, so Q053 can be scoped on evidence rather
than on an assumption that the two collapses are the same.

What it records, per the design:

* the census at the last live cycle and at the death cycle -- retained pairs, competing
  pairs, the top theory and its supports;
* `edge_mass_at_last_live` and `edge_mass_at_death`, the sum of the support counts the
  retained hypotheses carry, so support collapse can be told from competition collapse;
* the census at **every** live-to-dead and dead-to-live transition in the late window,
  because the probed arm's late series is intermittent and one snapshot of an
  intermittent series is not a representative measurement.

The lattice control runs through the same code path and must reproduce the committed
probe (cycle 299 live, 300 dead, `bravo` at 866 = 433 + 433, empty competing census).
If it does not, the block is VOID and no classification is made.

Precedence, stated here because the design fixes the conditions but not their order:
VOID, then DIFFERENT_INTERMITTENT, then DIFFERENT_SUPPORT_COLLAPSE, then
DIFFERENT_COMPETITION_PRESENT, then SAME_COMPETITION_LOSS. A collapse that is not a
terminal event is classified as such before any death-cycle census is read, because the
design's own rule is that a snapshot of an intermittent series is not representative.

    ./.venv/bin/python -m benchmarks.competition_census --measure --family burst_L1 --seed 20302901
    ./.venv/bin/python -m benchmarks.competition_census --measure --family lattice_L1 --seed 20302701
    ./.venv/bin/python -m benchmarks.competition_census --finish
    ./.venv/bin/python -m benchmarks.competition_census --render
    ./.venv/bin/python -m benchmarks.competition_census --check
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks.decay_sweep import SweepMemory
from benchmarks.force_matrix import COLONIES
from benchmarks.long_delay_capability import stream_for
from benchmarks.reference_death_ledger import CYCLES, stimulus
from organica.paths import temp_db
from organica.streams import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "q052_census" / "parts"
ARTIFACT = ROOT / "docs" / "q052_competition_census.json"
DOC = ROOT / "docs" / "Q052-COMPETITION-CENSUS.md"
DESIGN = ROOT / "docs" / "Q052-FRAMING-DESIGN.md"
ARM = "FULL"

#: What the transitions are read over: the whole run.
#: Amendment A1, made before any label was read: the design's late window (150-300) was tried
#: first and captured **no live cycle** for the first probed seed, so the census would have had
#: no dying cell to classify. Widening the capture changes no condition and no threshold; it
#: makes the transition census reachable, which rule 13(c) requires before a flat series may be
#: read as a result.
WINDOW = tuple(range(1, CYCLES + 1))

#: The lattice control: the committed probe's own cell, reproduced through this instrument.
CONTROL = {
    "family": "lattice_L1",
    "factor": 0.9924,
    "seed": 20302701,
    "last_live_cycle": 299,
    "death_cycle": 300,
    "subject": "bravo",
    "support_count": 866,
    "supports": [433, 433],
}

#: The probed arm: 0.9925 is the only burst arm whose late series has transitions. The
#: calibration has 0.95 and 1.0 alive at 300 (no death to census) and 0.99 dead across the
#: whole late window (no transition inside it), so neither is evidence for this question.
PROBED = {
    "family": "burst_L1",
    "factor": 0.9925,
    "seeds": (20302901, 20302902, 20302903),
}

BUCKETS = ("SAME_COMPETITION_LOSS", "DIFFERENT_SUPPORT_COLLAPSE",
           "DIFFERENT_COMPETITION_PRESENT", "DIFFERENT_INTERMITTENT", "VOID")
MASS_MARGIN = 0.05
CONTROL_MASS_FLOOR = 0.90


class CensusMixin:
    """Record the engine's own hypotheses, theories and edges. Changes nothing."""

    def census_reset(self) -> None:
        self._census_state: dict | None = None

    def _form_theories_and_questions(self, hypotheses, prior):
        theories, questions = super()._form_theories_and_questions(hypotheses, prior)
        by_id = {h.id: h for h in hypotheses}
        retained = [
            {"subject": h.subject, "expectation": h.expectation,
             "support_count": int(h.support_count)}
            for h in hypotheses
        ]
        self._census_state = {
            "theories": [
                {
                    "subject": t.subject,
                    "support_count": int(t.support_count),
                    "hypotheses": [
                        {"id": hypothesis_id,
                         "subject": by_id[hypothesis_id].subject,
                         "expectation": by_id[hypothesis_id].expectation,
                         "support_count": int(by_id[hypothesis_id].support_count)}
                        for hypothesis_id in t.hypotheses if hypothesis_id in by_id
                    ],
                }
                for t in theories
            ],
            "retained_hypotheses": retained,
            "edges": [[source, target, int(count)]
                      for source, target, count in self.memory.temporal_edges(min_count=1)],
        }
        return theories, questions


def census_class():
    colony, _description = COLONIES[ARM]
    return type("Census_%s" % ARM, (CensusMixin, colony), {})


def part_path(family: str, seed: int) -> Path:
    return PARTS / ("%s_%d.json" % (family, seed))


def events_for(family: str, seed: int) -> list[str]:
    if family == CONTROL["family"]:
        return stimulus()
    return stream_for(seed, cycles=CYCLES, family=family)


def run_cell(family: str, factor: float, seed: int, events: list[str]) -> dict:
    db = temp_db("q052_%s_%s.db" % (family, seed))
    db.unlink(missing_ok=True)
    memory = SweepMemory(db_path=str(db), factor=factor)
    service = census_class()(memory)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    service.census_reset()
    window: dict[int, dict] = {}
    try:
        for text in events:
            memory.store(text, event_type="event", source="seed:bootstrap")
        for cycle in range(CYCLES):
            start = (cycle * EVENTS_PER_CYCLE) % len(events)
            for text in events[start:start + EVENTS_PER_CYCLE]:
                memory.store(text, event_type="event", source="cycle:%d" % cycle)
            service.run_sleep_cycle()
            if cycle + 1 in WINDOW:
                window[cycle + 1] = json.loads(json.dumps(service._census_state))
        calls = list(memory.calls)
        facts = {
            "decay_calls_count": len(calls),
            "decay_factors": sorted({call["factor"] for call in calls}),
            "decay_rows_min": min((call["rows"] for call in calls), default=0),
            "stream_digest": _digest(events),
        }
        # Only the cycles that carry a transition are kept. A full 300-cycle capture is
        # millions of lines once each cycle's retained hypotheses and edges are serialized,
        # and the design asks for the census at the transitions, not at every cycle.
        steps = _transitions_from(window)
        keep = sorted({step["cycle"] - 1 for step in steps} | {step["cycle"] for step in steps})
        facts["live_cycles"] = sum(1 for row in window.values() if row["theories"])
        return {"family": family, "factor": factor, "seed": seed, "facts": facts,
                "window": {str(cycle): window[cycle] for cycle in keep},
                "captured_cycles": [keep[0], keep[-1]] if keep else []}
    finally:
        memory.close()
        db.unlink(missing_ok=True)


def _digest(events: list[str]) -> str:
    import hashlib
    return hashlib.sha256(json.dumps(events).encode("utf-8")).hexdigest()[:16]


def measure(family: str, seeds) -> int:
    factor = CONTROL["factor"] if family == CONTROL["family"] else PROBED["factor"]
    for seed in seeds:
        path = part_path(family, seed)
        if path.exists():
            print("cached", path.name, flush=True)
            continue
        part = run_cell(family, factor, seed, events_for(family, seed))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(engine_stamp.stamp(part), indent=1) + "\n", encoding="utf-8")
        steps = transitions(part)
        print("%s %s seed %d live %d/%d cycles, transitions %s"
              % (family, factor, seed, part["facts"]["live_cycles"], CYCLES,
                 ["%s@%d" % (s["kind"], s["cycle"]) for s in steps]), flush=True)
    return 0


def _census(row: dict) -> dict:
    retained = row["retained_hypotheses"]
    pairs = Counter(h["subject"] for h in retained)
    competing = Counter(h["subject"] for h in retained
                        if h["expectation"] != "high_structural_significance")
    top = max(row["theories"], key=lambda t: t["support_count"]) if row["theories"] else None
    return {
        "theories": len(row["theories"]),
        "edge_mass": sum(int(h["support_count"]) for h in retained),
        "subjects_with_pairs": {s: c for s, c in pairs.items() if c >= 2},
        "subjects_with_competing": {s: c for s, c in competing.items() if c >= 2},
        "top_theory": None if top is None else {
            "subject": top["subject"],
            "support_count": top["support_count"],
            "competing": [{"expectation": h["expectation"],
                           "support_count": h["support_count"]}
                          for h in top["hypotheses"]],
        },
    }


def transitions(part: dict) -> list[dict]:
    """Every live-to-dead and dead-to-live transition in the capture, with both censuses."""
    return _transitions_from({int(cycle): row for cycle, row in part["window"].items()})


def _transitions_from(window: dict) -> list[dict]:
    cycles = sorted(window)
    out = []
    for previous, cycle in zip(cycles, cycles[1:]):
        if cycle != previous + 1:
            continue
        was_live = bool(window[previous]["theories"])
        is_live = bool(window[cycle]["theories"])
        if was_live == is_live:
            continue
        out.append({
            "cycle": cycle,
            "kind": "LIVE_TO_DEAD" if was_live else "DEAD_TO_LIVE",
            "census_before": _census(window[previous]),
            "census_at": _census(window[cycle]),
        })
    return out


def cells_for(part: dict) -> list[dict]:
    """One dying cell per live-to-dead transition, which is the unit the design classifies."""
    window = {int(cycle): row for cycle, row in part["window"].items()}
    out = []
    for step in transitions(part):
        if step["kind"] != "LIVE_TO_DEAD":
            continue
        last_live = step["cycle"] - 1
        before = _census(window[last_live])
        at = _census(window[step["cycle"]])
        ratio = None if not before["edge_mass"] else round(
            at["edge_mass"] / before["edge_mass"], 6)
        out.append({
            "seed": part["seed"],
            "family": part["family"],
            "factor": part["factor"],
            "last_live_cycle": last_live,
            "death_cycle": step["cycle"],
            "theories_at_last_live": len(window[last_live]["theories"]),
            "theories_at_death": at["theories"],
            "top_theory": before["top_theory"],
            "subjects_with_pairs_at_death": at["subjects_with_pairs"],
            "subjects_with_competing_at_death": at["subjects_with_competing"],
            "subjects_with_pairs_at_last_live": before["subjects_with_pairs"],
            "subjects_with_competing_at_last_live": before["subjects_with_competing"],
            "edge_mass_at_last_live": before["edge_mass"],
            "edge_mass_at_death": at["edge_mass"],
            "mass_ratio": ratio,
            "retained_at_death": window[step["cycle"]]["retained_hypotheses"],
        })
    return out


def load_part(family: str, seed: int) -> dict:
    path = part_path(family, seed)
    if not path.exists():
        raise SystemExit("missing part %s" % path.name)
    part = json.loads(path.read_text(encoding="utf-8"))
    if part["family"] != family or part["seed"] != seed:
        raise SystemExit("part %s does not hold %s on seed %d" % (path.name, family, seed))
    if not part.get("window") or part.get("facts", {}).get("live_cycles") is None:
        raise SystemExit("part %s carries no census capture" % path.name)
    return part


def control_check(part: dict) -> dict:
    """Does this instrument reproduce the committed lattice cell?"""
    window = {int(cycle): row for cycle, row in part["window"].items()}
    last_live = max(c for c, row in window.items() if row["theories"])
    census = _census(window[last_live])
    top = census["top_theory"] or {}
    supports = [item["support_count"] for item in top.get("competing", [])]
    death = last_live + 1
    at = _census(window.get(death, {"theories": [], "retained_hypotheses": []}))
    reproduced = (
        last_live == CONTROL["last_live_cycle"]
        and death == CONTROL["death_cycle"]
        and top.get("subject") == CONTROL["subject"]
        and top.get("support_count") == CONTROL["support_count"]
        and supports == CONTROL["supports"]
    )
    ratio = None if not census["edge_mass"] else round(
        at["edge_mass"] / census["edge_mass"], 6)
    return {
        "reproduced": reproduced,
        "last_live_cycle": last_live,
        "death_cycle": death,
        "top_subject": top.get("subject"),
        "top_support_count": top.get("support_count"),
        "top_supports": supports,
        "subjects_with_competing_at_death": at["subjects_with_competing"],
        "mass_ratio": ratio,
        "mass_floor_met": ratio is not None and ratio >= CONTROL_MASS_FLOOR,
    }


def classify(cells: list[dict], control: dict, probed_transitions: dict) -> tuple[str, dict]:
    fired = {
        "control_reproduced": bool(control["reproduced"]),
        "control_mass_floor": bool(control["mass_floor_met"]),
        "dying_cells": len(cells),
        "intermittent": any(count >= 2 for count in probed_transitions.values()),
        "support_collapse": any(
            cell["mass_ratio"] is not None
            and cell["mass_ratio"] <= control["mass_ratio"] - MASS_MARGIN
            for cell in cells),
        "competition_present": any(
            cell["subjects_with_competing_at_death"] for cell in cells),
        "same": bool(cells) and all(
            not cell["subjects_with_competing_at_death"]
            and len(cell["subjects_with_pairs_at_death"]) >= 2
            and any(count >= 2 for count in cell["subjects_with_competing_at_last_live"].values())
            and cell["mass_ratio"] is not None
            and cell["mass_ratio"] >= control["mass_ratio"] - MASS_MARGIN
            for cell in cells),
    }
    if not control["reproduced"] or not control["mass_floor_met"] or len(cells) < 2:
        return "VOID", fired
    if fired["intermittent"]:
        return "DIFFERENT_INTERMITTENT", fired
    if fired["support_collapse"]:
        return "DIFFERENT_SUPPORT_COLLAPSE", fired
    if fired["competition_present"]:
        return "DIFFERENT_COMPETITION_PRESENT", fired
    if fired["same"]:
        return "SAME_COMPETITION_LOSS", fired
    return "VOID", fired


def finish() -> dict:
    control_part = load_part(CONTROL["family"], CONTROL["seed"])
    control = control_check(control_part)
    cells: list[dict] = []
    per_seed_transitions: dict[str, list] = {}
    probed_transitions: dict[int, int] = {}
    for seed in PROBED["seeds"]:
        part = load_part(PROBED["family"], seed)
        steps = transitions(part)
        per_seed_transitions[str(seed)] = steps
        probed_transitions[seed] = sum(1 for step in steps if step["kind"] == "LIVE_TO_DEAD")
        cells.extend(cells_for(part))
    label, fired = classify(cells, control, probed_transitions)
    artifact = {
        "date": date.today().isoformat(),
        "engine_version": __import__("organica").__version__,
        "question": "Q052 framing -- is burst_L1's late collapse competition loss?",
        "design": DESIGN.relative_to(ROOT).as_posix(),
        "window": [WINDOW[0], WINDOW[-1]],
        "window_amendment": ("A1: the design's late window (150-300) captured no live cycle on "
                             "seed %d, so the census was widened to the full run before any "
                             "label was read. No condition or threshold changed." % PROBED["seeds"][0]),
        "cycles": CYCLES,
        "arm": ARM,
        "control": {**CONTROL, **control},
        "probed": {"family": PROBED["family"], "factor": PROBED["factor"],
                   "seeds": list(PROBED["seeds"]),
                   "live_to_dead_transitions": probed_transitions},
        "cells": cells,
        "transitions": per_seed_transitions,
        "fired": fired,
        "label": label,
        "scope": ("One family, one factor, three fresh seeds. The classification decides Q053's "
                  "scope; it is not a capability result and scores no prediction task."),
    }
    problems = validate(artifact)
    if problems:
        raise SystemExit("refusing to write: " + "; ".join(problems))
    ARTIFACT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=1) + "\n",
                        encoding="utf-8")
    return artifact


def validate(artifact: dict | None = None) -> list[str]:
    found: list[str] = []
    if artifact is None:
        if not ARTIFACT.exists():
            return ["the artifact does not exist"]
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if artifact.get("label") not in BUCKETS:
        found.append("label %r is not one of the frozen buckets" % artifact.get("label"))
    if artifact.get("control", {}).get("family") != CONTROL["family"]:
        found.append("the control is not the lattice control")
    if artifact.get("probed", {}).get("family") != PROBED["family"]:
        found.append("the probed family is not burst_L1")
    if artifact.get("probed", {}).get("factor") != PROBED["factor"]:
        found.append("the probed factor is not the one chosen before the run")
    if artifact.get("probed", {}).get("seeds") != list(PROBED["seeds"]):
        found.append("the seeds are not the fresh block named before the run")
    for cell in artifact.get("cells", []):
        for field in ("edge_mass_at_last_live", "edge_mass_at_death", "mass_ratio",
                      "subjects_with_pairs_at_death", "subjects_with_competing_at_death"):
            if field not in cell:
                found.append("cell %s/%s is missing %s"
                             % (cell.get("family"), cell.get("seed"), field))
    if artifact.get("label") != classify(
            artifact.get("cells", []),
            {**artifact.get("control", {})},
            artifact.get("probed", {}).get("live_to_dead_transitions", {}))[0]:
        found.append("the label is not the one its cells and control imply")
    return found


def render(artifact: dict) -> str:
    control = artifact["control"]
    lines = [
        "# The Q052 census: is `burst_L1`'s late collapse competition loss?",
        "",
        "Generated from `docs/q052_competition_census.json` by "
        "`python -m benchmarks.competition_census --render`. Do not edit by hand.",
        "",
        "Design: `docs/Q052-FRAMING-DESIGN.md`. Window: cycles %d-%d."
        % tuple(artifact["window"]),
        "",
        "**Label: `%s`**" % artifact["label"],
        "",
        "## The control, reproduced through this instrument",
        "",
        "| Field | Value | Expected |",
        "| --- | --- | --- |",
        "| last live cycle | %s | %s |" % (control["last_live_cycle"], CONTROL["last_live_cycle"]),
        "| death cycle | %s | %s |" % (control["death_cycle"], CONTROL["death_cycle"]),
        "| top subject | %s | %s |" % (control["top_subject"], CONTROL["subject"]),
        "| top support | %s | %s |" % (control["top_support_count"], CONTROL["support_count"]),
        "| competing supports | %s | %s |" % (control["top_supports"], CONTROL["supports"]),
        "| competing at death | %d subject(s) | empty |"
        % len(control["subjects_with_competing_at_death"]),
        "| mass ratio | %s | %s or more |" % (control["mass_ratio"], CONTROL_MASS_FLOOR),
        "",
        "## The probed arm",
        "",
        "`%s` at factor `%s`, seeds %s. Live-to-dead transitions in the window: %s."
        % (artifact["probed"]["family"], artifact["probed"]["factor"],
           ", ".join(str(s) for s in artifact["probed"]["seeds"]),
           ", ".join("%s: %s" % (seed, count)
                     for seed, count in artifact["probed"]["live_to_dead_transitions"].items())),
        "",
        "| Seed | Last live | Death | Top subject | Support | Pairs at death | Competing at death | Mass ratio |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for cell in artifact["cells"]:
        top = cell["top_theory"] or {}
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            cell["seed"], cell["last_live_cycle"], cell["death_cycle"],
            top.get("subject"), top.get("support_count"),
            len(cell["subjects_with_pairs_at_death"]),
            len(cell["subjects_with_competing_at_death"]), cell["mass_ratio"]))
    lines += [
        "",
        "## Which conditions fired",
        "",
        "| Condition | Fired |",
        "| --- | --- |",
    ]
    for name, value in artifact["fired"].items():
        lines.append("| %s | %s |" % (name, value))
    lines += [
        "",
        "## Scope",
        "",
        artifact["scope"],
        "The supports are temporal transition counts, not observations, and survival is "
        "theory-layer presence, not theory identity. A label here decides which families Q053 "
        "may test; it says nothing about capability.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--render", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--family", choices=(CONTROL["family"], PROBED["family"]))
    parser.add_argument("--seed", type=int, action="append", default=None)
    args = parser.parse_args(argv)
    if args.measure:
        family = args.family or PROBED["family"]
        allowed = [CONTROL["seed"]] if family == CONTROL["family"] else list(PROBED["seeds"])
        seeds = tuple(args.seed or allowed)
        unknown = sorted(set(seeds) - set(allowed))
        if unknown:
            raise SystemExit("seed %r is not in the block named before the run" % unknown)
        return measure(family, seeds)
    if args.finish:
        artifact = finish()
        print("%s: %s" % (artifact["label"],
                          ", ".join("%s %d dying cell(s)" % (s, n)
                                    for s, n in
                                    artifact["probed"]["live_to_dead_transitions"].items())))
        return 0
    if args.render:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        page = render(artifact)
        if "{" in page or "}" in page:
            raise SystemExit("the page contains a brace; refusing to write it")
        DOC.write_text(page, encoding="utf-8")
        print("rendered %s" % DOC.name)
        return 0
    problems = validate()
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    print("competition census: %s" % json.loads(ARTIFACT.read_text(encoding="utf-8"))["label"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
