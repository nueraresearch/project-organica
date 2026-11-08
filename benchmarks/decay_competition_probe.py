"""Capture the competition-collapse signature at the 0.9924 edge on the threshold block.

Section 12's probe found that the 0.9924 theory layer dies when every subject stops
retaining two competing hypotheses, while the surviving supports are still in the
hundreds. That was one seed. This probe reruns 0.9924 on seeds 20302701-20302703
with the same in-process observer and asks whether the last pair is always `bravo`
(subject-specific) or whether different subjects follow the same signature (general
competition collapse). Seed 20302701 is a control against the committed probe.

    ./.venv/bin/python -m benchmarks.decay_competition_probe --measure
    ./.venv/bin/python -m benchmarks.decay_competition_probe --finish
    ./.venv/bin/python -m benchmarks.decay_competition_probe --render
    ./.venv/bin/python -m benchmarks.decay_competition_probe --check
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

from benchmarks.decay_sweep import SweepMemory
from benchmarks.force_matrix import COLONIES
from benchmarks.reference_death_ledger import CYCLES, stimulus
from organica.paths import temp_db
from organica.streams import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "decay_competition" / "parts"
ARTIFACT = ROOT / "docs" / "decay_competition_probe.json"
DOC = ROOT / "docs" / "DECAY-COMPETITION-PROBE.md"
PREREG = ROOT / "docs" / "DECAY-THRESHOLD-PREREGISTRATION.md"
CONTROL = ROOT / "docs" / "decay_support_probe.json"
WORLD = "lattice_L1"
ARM = "FULL"
FACTOR = 0.9924
SEEDS = (20302701, 20302702, 20302703)
WINDOW = tuple(range(CYCLES - 5, CYCLES + 1))
CONTROL_SEED = 20302701
CONTROL_CYCLE = "299"
BUCKETS = ("SAME_PAIR", "SAME_MECHANISM", "SIGNATURE_ABSENT", "VOID")


class ProbeMixin:
    """Record the engine's own hypotheses, theories and pre-decay edges, changing nothing."""

    def probe_reset(self) -> None:
        self._probe_state: dict | None = None

    def _form_theories_and_questions(self, hypotheses, prior):
        theories, questions = super()._form_theories_and_questions(hypotheses, prior)
        by_id = {h.id: h for h in hypotheses}
        retained = [
            {
                "subject": h.subject,
                "expectation": h.expectation,
                "support_count": int(h.support_count),
            }
            for h in hypotheses
        ]
        pairs = Counter(h["subject"] for h in retained)
        competing = Counter(h["subject"] for h in retained
                            if h["expectation"] != "high_structural_significance")
        self._probe_state = {
            "theories": [
                {
                    "subject": t.subject,
                    "support_count": int(t.support_count),
                    "hypotheses": [
                        {
                            "id": hypothesis_id,
                            "subject": by_id[hypothesis_id].subject,
                            "expectation": by_id[hypothesis_id].expectation,
                            "support_count": int(by_id[hypothesis_id].support_count),
                        }
                        for hypothesis_id in t.hypotheses
                        if hypothesis_id in by_id
                    ],
                }
                for t in theories
            ],
            "retained_hypotheses": retained,
            "subjects_with_pairs": {subject: count for subject, count in pairs.items()
                                   if count >= 2},
            "subjects_with_competing": {subject: count for subject, count in competing.items()
                                        if count >= 2},
            "edges": [[source, target, int(count)]
                      for source, target, count in self.memory.temporal_edges(min_count=1)],
        }
        return theories, questions


def probe_class():
    colony, _description = COLONIES[ARM]
    return type("Probe_%s" % ARM, (ProbeMixin, colony), {})


def part_path(seed: int) -> Path:
    return PARTS / ("0.9924_%d.json" % seed)


def _load_part(seed: int) -> dict:
    path = part_path(seed)
    if not path.exists():
        raise SystemExit("missing part %s" % path.name)
    part = json.loads(path.read_text(encoding="utf-8"))
    if part.get("factor") != FACTOR or part.get("seed") != seed:
        raise SystemExit("part %s does not hold %s on seed %d" % (path.name, FACTOR, seed))
    window = part.get("window") or {}
    if sorted(int(cycle) for cycle in window) != list(WINDOW):
        raise SystemExit("part %s does not cover cycles %s" % (path.name, WINDOW))
    return part


def run_cell(seed: int, events: list[str]) -> dict:
    db = temp_db("competition_%s.db" % seed)
    db.unlink(missing_ok=True)
    memory = SweepMemory(db_path=str(db), factor=FACTOR)
    service = probe_class()(memory)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    service.probe_reset()
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
                window[cycle + 1] = json.loads(json.dumps(service._probe_state))
        calls = list(memory.calls)
        facts = {
            "decay_calls_count": len(calls),
            "decay_factors": sorted({call["factor"] for call in calls}),
            "decay_rows_min": min((call["rows"] for call in calls), default=0),
            "mass_unchanged": all(call["mass_before"] == call["mass_after"] for call in calls),
        }
        return {"factor": FACTOR, "seed": seed, "facts": facts,
                "window": {str(cycle): window[cycle] for cycle in WINDOW}}
    finally:
        memory.close()
        db.unlink(missing_ok=True)


def measure(seeds=SEEDS) -> int:
    events = stimulus()
    for seed in seeds:
        path = part_path(seed)
        if path.exists():
            _load_part(seed)
            print("cached", path.name, flush=True)
            continue
        part = run_cell(seed, events)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(part, indent=1) + "\n", encoding="utf-8")
        print("competition 0.9924 %d live=%s death=%s"
              % (seed, part["window"][str(CYCLES - 1)]["theories"] and "yes" or "no",
                 part["window"][str(CYCLES)]["theories"] and "yes" or "no"), flush=True)
    return 0


def _pairs(row: dict, competing: bool = False) -> dict:
    kept = row["retained_hypotheses"]
    if competing:
        kept = [hypothesis for hypothesis in kept
                if hypothesis["expectation"] != "high_structural_significance"]
    counts = Counter(hypothesis["subject"] for hypothesis in kept)
    return {subject: count for subject, count in counts.items() if count >= 2}


def endpoint(part: dict) -> dict:
    window = {int(cycle): row for cycle, row in part["window"].items()}
    live = [cycle for cycle, row in window.items() if row["theories"]]
    if not live:
        raise SystemExit("seed %d never formed a theory" % part["seed"])
    last_live = max(live)
    death = last_live + 1
    if death not in window:
        raise SystemExit("seed %d has no death-cycle capture" % part["seed"])
    top = max(window[last_live]["theories"], key=lambda theory: theory["support_count"])
    return {
        "seed": part["seed"],
        "factor": FACTOR,
        "last_live_cycle": last_live,
        "death_cycle": death,
        "top_theory": {
            "subject": top["subject"],
            "support_count": top["support_count"],
            "competing": [{"expectation": hypothesis["expectation"],
                           "support_count": hypothesis["support_count"]}
                          for hypothesis in top["hypotheses"]],
        },
        "theories_at_last_live": [theory["subject"] for theory in window[last_live]["theories"]],
        "theories_at_death": len(window[death]["theories"]),
        "subjects_with_pairs_at_death": _pairs(window[death]),
        "subjects_with_competing_at_death": _pairs(window[death], competing=True),
        "subjects_with_pairs_at_last_live": _pairs(window[last_live]),
        "subjects_with_competing_at_last_live": _pairs(window[last_live], competing=True),
        "retained_at_death": window[death]["retained_hypotheses"],
        "decay_calls_count": part["facts"]["decay_calls_count"],
        "decay_factors": part["facts"]["decay_factors"],
        "decay_rows_min": part["facts"]["decay_rows_min"],
    }


def cells_from_parts() -> list[dict]:
    return [endpoint(_load_part(seed)) for seed in SEEDS]


def signature_holds(cell: dict) -> bool:
    return (len(cell["top_theory"]["competing"]) >= 2
            and cell["theories_at_death"] == 0
            and not cell["subjects_with_competing_at_death"])


def predictions_for(cells: list[dict]) -> dict:
    return {
        "P1_same_subject_all_seeds": len({cell["top_theory"]["subject"]
                                          for cell in cells}) == 1,
        "P2_two_competing_all_seeds": all(
            len(cell["top_theory"]["competing"]) == 2 for cell in cells
        ),
        "P3_no_competing_pair_at_death_all_seeds": all(
            not cell["subjects_with_competing_at_death"] for cell in cells
        ),
    }


def seed_insensitive(cells: list[dict]) -> bool:
    """True when every cell reproduced the same trajectory, not three independent draws."""
    def key(cell):
        return (cell["last_live_cycle"], cell["death_cycle"],
                cell["top_theory"]["subject"], cell["top_theory"]["support_count"],
                tuple((item["expectation"], item["support_count"])
                      for item in cell["top_theory"]["competing"]),
                cell["theories_at_death"])
    return len({key(cell) for cell in cells}) == 1


def gates_for(cells: list[dict], control: dict | None = None) -> dict:
    if control is None:
        control = control_facts()
    by_seed = {cell["seed"]: cell for cell in cells}
    return {
        "G1_factor_live": bool(cells) and all(
            cell["decay_calls_count"] == CYCLES
            and cell["decay_factors"] == [FACTOR]
            and cell["decay_rows_min"] > 0
            for cell in cells
        ),
        "G2_capture_window": bool(cells) and all(
            cell["last_live_cycle"] in WINDOW
            and cell["death_cycle"] in WINDOW
            and cell["death_cycle"] == cell["last_live_cycle"] + 1
            for cell in cells
        ),
        "G3_control_reproduced": (
            CONTROL_SEED in by_seed
            and by_seed[CONTROL_SEED]["top_theory"]["subject"] == control["subject"]
            and by_seed[CONTROL_SEED]["top_theory"]["support_count"] == control["support_count"]
            and [item["support_count"] for item in
                 by_seed[CONTROL_SEED]["top_theory"]["competing"]] == control["supports"]
        ),
        "G4_threshold_block": len(cells) == len(SEEDS)
        and {cell["seed"] for cell in cells} == set(SEEDS),
        "G5_artifact_matches_parts": True,
    }


def control_facts() -> dict:
    probe = json.loads(CONTROL.read_text(encoding="utf-8"))
    cycle = probe["factors"][str(FACTOR)]["window"][CONTROL_CYCLE]
    top = max(cycle["theories"], key=lambda theory: theory["support_count"])
    return {
        "subject": top["subject"],
        "support_count": top["support_count"],
        "supports": [hypothesis["support_count"] for hypothesis in top["hypotheses"]],
    }


def label_for(cells: list[dict], gates: dict | None = None) -> str:
    if gates is None:
        gates = gates_for(cells)
    if not all(gates.values()):
        return "VOID"
    if not cells or not all(signature_holds(cell) for cell in cells):
        return "SIGNATURE_ABSENT"
    subjects = {cell["top_theory"]["subject"] for cell in cells}
    if len(subjects) == 1:
        return "SAME_PAIR"
    return "SAME_MECHANISM"


def finish() -> dict:
    cells = cells_from_parts()
    control = control_facts()
    gates = gates_for(cells, control)
    label = label_for(cells, gates)
    artifact = {
        "date": date.today().isoformat(),
        "engine_version": __import__("organica").__version__,
        "question": "Q050 competition-collapse diagnostic",
        "preregistration": PREREG.relative_to(ROOT).as_posix(),
        "protocol_section": "15",
        "control_probe": CONTROL.relative_to(ROOT).as_posix(),
        "control": control,
        "world": WORLD,
        "arm": ARM,
        "factor": FACTOR,
        "seeds": list(SEEDS),
        "cycles": CYCLES,
        "window": list(WINDOW),
        "cells": cells,
        "gates": gates,
        "predictions": predictions_for(cells),
        "seed_insensitive": seed_insensitive(cells),
        "label": label,
    }
    if artifact["predictions"]["P1_same_subject_all_seeds"] \
            and artifact["predictions"]["P2_two_competing_all_seeds"]:
        artifact["prediction_same_pair"] = True
    else:
        artifact["prediction_same_pair"] = False
    problems = validate(artifact, cells, control)
    if problems:
        raise SystemExit("refusing to write: " + "; ".join(problems))
    ARTIFACT.write_text(json.dumps(artifact, indent=1) + "\n", encoding="utf-8")
    return artifact


def validate(artifact: dict, cells: list[dict] | None = None,
             control: dict | None = None) -> list[str]:
    found: list[str] = []
    if cells is None:
        try:
            cells = cells_from_parts()
        except SystemExit as error:
            return [str(error)]
    if control is None:
        control = control_facts()
    expected = gates_for(cells, control)
    if artifact.get("gates") != expected:
        found.append("the artifact's gates do not match the committed parts")
    if expected.get("G5_artifact_matches_parts"):
        got = json.loads(json.dumps(artifact.get("cells") or [], sort_keys=True))
        want = json.loads(json.dumps(cells, sort_keys=True))
        if got != want:
            found.append("the artifact's per-cell facts do not equal the parts")
    if artifact.get("label") not in BUCKETS:
        found.append("label %r is not one of the frozen buckets" % artifact.get("label"))
    if artifact.get("label") != label_for(cells, expected):
        found.append("the artifact's label is not the one its cells imply")
    if artifact.get("predictions") != predictions_for(cells):
        found.append("the artifact's predictions do not match the committed parts")
    if artifact.get("seeds") != list(SEEDS):
        found.append("the artifact's seeds are not the pre-registered block")
    if artifact.get("factor") != FACTOR:
        found.append("the artifact's factor is not 0.9924")
    if artifact.get("cycles") != CYCLES:
        found.append("the artifact's cycle count is not %d" % CYCLES)
    return found


def render(artifact: dict) -> str:
    lines = [
        "# The competition-collapse signature at 0.9924 — result",
        "",
        "Generated from `docs/decay_competition_probe.json` by "
        "`python -m benchmarks.decay_competition_probe --render`. Do not edit by hand.",
        "",
        "Protocol: `docs/DECAY-THRESHOLD-PREREGISTRATION.md` section 15. The probe records the "
        "engine's retained hypotheses, formed theories and pre-decay edge counts for cycles "
        "295-300. Seed 20302701 is the control against the committed support probe.",
        "",
        "**Label: `%s`**" % artifact["label"],
        "",
        "| Seed | Last live | Death | Top subject | Support | Competing supports |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for cell in artifact["cells"]:
        competing = ", ".join("%s %s" % (item["expectation"], item["support_count"])
                              for item in cell["top_theory"]["competing"])
        lines.append("| %s | %s | %s | %s | %s | %s |"
                     % (cell["seed"], cell["last_live_cycle"], cell["death_cycle"],
                        cell["top_theory"]["subject"], cell["top_theory"]["support_count"],
                        competing))
    lines += [
        "",
        "**Pair-loss signature on all three seeds:** %s."
        % ("yes" if all(signature_holds(cell) for cell in artifact["cells"]) else "no"),
        "",
        "At the death cycle each subject retains one competing hypothesis plus one "
        "`high_structural_significance` marker; the engine drops that marker before theory "
        "formation, so the competing population has one member per subject. The artifact keeps "
        "both counts.",
        "",
        "**Seed variation:** %s." % (
            "none; the three cells reproduce the same trajectory, so this is not three "
            "independent draws" if artifact.get("seed_insensitive") else
            "present; the cells differ"),
        "",
        "## Gates",
        "",
        "| Gate | Result |",
        "| --- | --- |",
    ]
    for name, ok in artifact["gates"].items():
        lines.append("| %s | %s |" % (name, "pass" if ok else "FAIL"))
    lines += [
        "",
        "## Scope",
        "",
        "This is a mechanism diagnostic on the three threshold seeds, requested after the paired "
        "edge check. It does not change Q050's label, is not a new threshold, and scores no "
        "adaptation or capability task. The supports are temporal transition counts, not "
        "observations, and survival is theory-layer presence, not theory identity.",
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
    parser.add_argument("--seed", type=int, action="append", default=None)
    args = parser.parse_args(argv)
    if args.measure:
        seeds = tuple(args.seed or SEEDS)
        unknown = sorted(set(seeds) - set(SEEDS))
        if unknown:
            raise SystemExit("seed %r is not in the pre-registered block" % unknown)
        return measure(seeds)
    if args.finish:
        artifact = finish()
        print("%s: %s" % (artifact["label"],
                          ", ".join("%d %s/%s" % (cell["seed"],
                                                  cell["top_theory"]["subject"],
                                                  cell["top_theory"]["support_count"])
                                    for cell in artifact["cells"])))
        return 0
    if args.render:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        page = render(artifact)
        if "{" in page or "}" in page:
            raise SystemExit("the page contains a brace; refusing to write it")
        DOC.write_text(page, encoding="utf-8")
        print("rendered %s" % DOC.name)
        return 0

    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    problems = validate(artifact)
    text = PREREG.read_text(encoding="utf-8")
    if "## 15. Competition-collapse signature" not in text:
        problems.append("the protocol has no section 15")
    for label in BUCKETS:
        if label not in text:
            problems.append("the protocol does not name %s" % label)
    if artifact["label"] not in DOC.read_text(encoding="utf-8"):
        problems.append("the page does not name the artifact's label")
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    print("competition probe: %s" % artifact["label"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
