"""Per-cycle death ledger: reference-arm removals against the ablation arms' removals.

Q042 asks whether reference-arm death is the dominant failure mode of 0.13.0, and the
record has only a pattern: the reference arm is dead by cycle 38 of 300, and no artifact
counts the removal events or attributes them. This harness builds that count. It runs the
six force-matrix arms at the falsifier's own setting and records, for every cycle, each
identifier that was in the previous cycle's population and is absent from this one,
with one mechanism from the closed vocabulary frozen in
``docs/REFERENCE-DEATH-LEDGER-PREREGISTRATION.md``.

The engine is unchanged. Instrumentation is in-process subclassing, composed the same way
``benchmarks/force_matrix.py`` composes its instrument, and the control is that the
ledgered reference arm at the falsifier's seed reproduces the committed series exactly.

    ./.venv/bin/python -m benchmarks.reference_death_ledger --measure
    ./.venv/bin/python -m benchmarks.reference_death_ledger --render
    ./.venv/bin/python -m benchmarks.reference_death_ledger --check

Nothing is written in ``--check`` mode.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
from collections import Counter
from datetime import date
from pathlib import Path

import organica
from benchmarks.decay_confirmation import harvest_seeds
from benchmarks.force_matrix import COLONIES
from organica.branch_streams import (
    NEUTRAL_HUB,
    NEUTRAL_PETALS,
    lattice_designs,
    lattice_stream,
)
from organica.memory import MemoryService
from organica.paths import temp_db
from organica.streams import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "docs" / "reference_death_ledger" / "parts"
ARTIFACT = ROOT / "docs" / "reference_death_ledger.json"
DOC = ROOT / "docs" / "REFERENCE-DEATH-LEDGER.md"
PREREG = ROOT / "docs" / "REFERENCE-DEATH-LEDGER-PREREGISTRATION.md"
CONTROL = ROOT / "docs" / "decay_falsifier" / "parts" / "FULL.json"

ARMS = ("FULL", "SALIENCE", "NO_CONTRADICTIONS", "NO_QUESTIONS", "NO_DREAMS", "ANTI_EIG")
SEEDS = (20302001, 20302002, 20302003)
CONTROL_SEED = 20261023
CYCLES = 300
#: Fixed in section 6 of the protocol from the falsifier's 37-cycle theory lifetime.
MARGIN = 10
#: Section 5, G2: the share of reference theory removals that may be unexplained.
UNEXPLAINED_BAND = 0.05
THEORY_REASONS = ("superseded", "parent_loss", "competing_collapse", "capped", "unexplained")
BELIEF_REASONS = ("capped", "not_reformed")
#: SHA-256 of sections 1-8, inserted from the committed protocol before the run.
FROZEN_DIGEST = "9005e175d7a958425ff6e5557b2dd6e355f0d7ffc6e0007fb7d21520a8ccd19e"

Q042 = {
    "REFERENCE_DOMINANT": (
        "SUPPORTED",
        "Yes: the reference arm's own configuration dies at least ten cycles before every "
        "ablation, so reference-arm death is a distinct failure mode and the retention "
        "policy is the first thing to fix.",
    ),
    "SHARED_DOMINANT": (
        "SUPPORTED",
        "Yes, but shared: every arm's theory layer dies within the margin, so death is the "
        "system's dominant failure mode and the lever is the common belief-formation and "
        "decay substrate, not any arm's policy.",
    ),
    "ABLATION_DOMINANT": (
        "UNSUPPORTED",
        "No: an ablation's theory layer dies at least ten cycles before the reference's, so "
        "the dominant failure mode is ablation-specific and the reference is the "
        "comparatively healthy case.",
    ),
    "UNMEASURABLE": (
        "OPEN",
        "Not measurable on this run: a gate failed, so the ledger reports the failure and "
        "claims nothing about the dominant failure mode.",
    ),
}


# ==================================================================
# The guard: the protocol is frozen, and its execution state is recorded
# ==================================================================

def protocol_digest(text: str) -> str | None:
    """SHA-256 of sections 1-8, the frozen part, and not of the outcome."""
    start = text.find("## 1.")
    end = text.find("\n## 9. Outcome")
    if start < 0 or end < 0:
        return None
    return hashlib.sha256(text[start:end].encode("utf-8")).hexdigest()


def execution_count(text: str) -> int | None:
    match = re.search(r"executions:\s*(\d+)", text)
    return int(match.group(1)) if match else None


def outcome_section(text: str) -> str:
    cut = text.find("## 9. Outcome")
    return text[cut:] if cut >= 0 else ""


def validate(text: str, artifact: dict | None, digest: str = FROZEN_DIGEST) -> list[str]:
    """Problems with the protocol and its recorded state; empty means consistent."""
    problems: list[str] = []
    if protocol_digest(text) != digest:
        problems.append("the protocol's sections 1-8 do not match the pinned digest")
    count = execution_count(text)
    outcome = outcome_section(text)
    if artifact is None:
        if count != 0:
            problems.append("the protocol records %s executions but no artifact exists" % count)
        if "Not yet written" not in outcome:
            problems.append("section 9 is written but there is no artifact")
    else:
        if count != 1:
            problems.append("an artifact exists but the protocol records %s executions" % count)
        if artifact.get("protocol_digest") != digest:
            problems.append("the artifact's digest does not match the pinned protocol")
        if artifact.get("label") not in outcome:
            problems.append("section 9 does not name the artifact's label")
        if tuple(artifact.get("seeds") or ()) != SEEDS:
            problems.append("the artifact's seeds are not the pre-registered block")
    return problems


# ==================================================================
# Attribution, as pure functions, so every rule is testable on its own
# ==================================================================

def belief_removal_reason(was_formed: bool) -> str:
    """A belief lost before retention was capped; one never formed was not re-formed."""
    return "capped" if was_formed else "not_reformed"


def theory_removal_reason(
    subject: str,
    parents: list[str],
    kept_beliefs: set[str],
    subject_counts: Counter,
    at_cap: bool,
    subject_has_theory: bool,
) -> str:
    """Why a theory present last cycle is absent this one, in precedence order."""
    if subject_has_theory:
        return "superseded"
    if any(parent not in kept_beliefs for parent in parents):
        return "parent_loss"
    if subject_counts.get(subject, 0) < 2:
        return "competing_collapse"
    if at_cap:
        return "capped"
    return "unexplained"


def decide(gates: dict, deaths: dict, margin: int = MARGIN) -> str:
    """The section-6 decision table, evaluated once and in order."""
    if not gates or not all(gates.values()):
        return "UNMEASURABLE"
    reference = deaths["FULL"]
    others = [deaths[arm] for arm in ARMS if arm != "FULL"]
    if reference - min(others) >= margin:
        return "ABLATION_DOMINANT"
    if max(others) - reference >= margin:
        return "REFERENCE_DOMINANT"
    return "SHARED_DOMINANT"


def modal_mechanism(counts: dict) -> str | None:
    """Most frequent mechanism, ties broken alphabetically so the answer is stable."""
    present = [(count, reason) for reason, count in counts.items() if count]
    if not present:
        return None
    return sorted(present, key=lambda pair: (-pair[0], pair[1]))[0][1]


# ==================================================================
# The observer: record the engine's own inputs and outputs
# ==================================================================

class LedgerMixin:
    """Records per-cycle populations and every disappearance, without changing behavior."""

    def ledger_reset(self) -> None:
        self.ledger_rows: list[dict] = []
        self._ledger_prev_beliefs: set[str] = set()
        self._ledger_prev_theories: dict[str, dict] = {}
        self._ledger_pending: dict | None = None

    def _retain_hypotheses(self, beliefs, info, temporal):
        formed = {getattr(h, "id", None) for h in beliefs}
        kept = super()._retain_hypotheses(beliefs, info, temporal)
        self._ledger_pending = {
            "formed": {item for item in formed if item},
            "kept": {h.id for h in kept},
        }
        return kept

    def _form_theories_and_questions(self, hypotheses, prior):
        theories, questions = super()._form_theories_and_questions(hypotheses, prior)
        pending = getattr(self, "_ledger_pending", None) or {
            "formed": {h.id for h in hypotheses},
            "kept": {h.id for h in hypotheses},
        }
        kept = {h.id for h in hypotheses} or pending["kept"]
        formed = pending["formed"]
        previous_beliefs = getattr(self, "_ledger_prev_beliefs", set())
        previous_theories = getattr(self, "_ledger_prev_theories", {})
        current = {
            t.id: {"subject": t.subject, "parents": list(t.parent_ids)}
            for t in theories
        }
        subjects_now = {t.subject for t in theories}
        counts: Counter = Counter(
            h.subject for h in hypotheses
            if h.expectation != "high_structural_significance"
        )
        at_cap = len(theories) >= getattr(self, "MAX_THEORIES", 8)
        row = {
            "cycle": len(getattr(self, "ledger_rows", [])),
            "formed_beliefs": len(formed),
            "retained_beliefs": len(pending["kept"]),
            "theory_input_beliefs": len(kept),
            "theories": len(theories),
            "belief_births": len(kept - previous_beliefs),
            "theory_births": len(set(current) - set(previous_theories)),
            "belief_removals": {reason: 0 for reason in BELIEF_REASONS},
            "theory_removals": {reason: 0 for reason in THEORY_REASONS},
        }
        for belief_id in previous_beliefs - kept:
            reason = belief_removal_reason(belief_id in formed)
            row["belief_removals"][reason] += 1
        for theory_id, meta in previous_theories.items():
            if theory_id in current:
                continue
            reason = theory_removal_reason(
                meta["subject"],
                meta["parents"],
                kept,
                counts,
                at_cap,
                meta["subject"] in subjects_now,
            )
            row["theory_removals"][reason] += 1
        self.ledger_rows.append(row)
        self._ledger_prev_beliefs = kept
        self._ledger_prev_theories = current
        self._ledger_pending = None
        return theories, questions


def ledger_class(arm: str):
    """Compose the ledger first in the MRO, so it observes each colony's own behavior."""
    colony, _description = COLONIES[arm]
    return type("Ledger_%s" % arm, (LedgerMixin, colony), {})


def stimulus() -> list[str]:
    """The falsifier's own lattice_L1 stimulus, built exactly as the matrix builds it."""
    designs = lattice_designs(NEUTRAL_HUB, NEUTRAL_PETALS)
    return lattice_stream(designs["L1_hub1_t3_disjoint"]["triangles"])


def run_cell(arm: str, seed: int, events: list[str]) -> list[dict]:
    """One arm on one seed, with the matrix's bootstrap and per-cycle feed."""
    db = temp_db("deathledger_%s_%s.db" % (arm, seed))
    db.unlink(missing_ok=True)
    memory = MemoryService(db_path=str(db))
    service = ledger_class(arm)(memory)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    service.ledger_reset()
    try:
        for text in events:
            memory.store(text, event_type="event", source="seed:bootstrap")
        for cycle in range(CYCLES):
            start = (cycle * EVENTS_PER_CYCLE) % len(events)
            for text in events[start:start + EVENTS_PER_CYCLE]:
                memory.store(text, event_type="event", source="cycle:%d" % cycle)
            service.run_sleep_cycle()
        return list(service.ledger_rows)
    finally:
        memory.close()
        db.unlink(missing_ok=True)


def cell_facts(rows: list[dict]) -> dict:
    """Death cycle and mechanism totals for one cell."""
    series = [row["theories"] for row in rows]
    nonzero = [index + 1 for index, count in enumerate(series) if count > 0]
    theory_removals: Counter = Counter()
    belief_removals: Counter = Counter()
    for row in rows:
        theory_removals.update(row["theory_removals"])
        belief_removals.update(row["belief_removals"])
    return {
        "cycles": len(rows),
        "theory_cycles": len(nonzero),
        "last_nonzero_cycle": nonzero[-1] if nonzero else 0,
        "death_cycle": (nonzero[-1] + 1) if nonzero else 1,
        "theories_total": sum(series),
        "beliefs_total": sum(row["retained_beliefs"] for row in rows),
        "theory_removals": {reason: int(theory_removals.get(reason, 0)) for reason in THEORY_REASONS},
        "belief_removals": {reason: int(belief_removals.get(reason, 0)) for reason in BELIEF_REASONS},
        "unexplained": int(theory_removals.get("unexplained", 0)),
    }


def arm_summary(cells: list[dict], arm: str) -> dict:
    rows = [cell for cell in cells if cell["arm"] == arm]
    deaths = [cell["death_cycle"] for cell in rows]
    theory: Counter = Counter()
    belief: Counter = Counter()
    for cell in rows:
        theory.update(cell["theory_removals"])
        belief.update(cell["belief_removals"])
    return {
        "cells": len(rows),
        "death_cycles": deaths,
        "median_death_cycle": statistics.median(deaths),
        "min_death_cycle": min(deaths),
        "max_death_cycle": max(deaths),
        "theory_cycles": sum(cell["theory_cycles"] for cell in rows),
        "theory_removals": {reason: int(theory.get(reason, 0)) for reason in THEORY_REASONS},
        "belief_removals": {reason: int(belief.get(reason, 0)) for reason in BELIEF_REASONS},
        "unexplained": int(theory.get("unexplained", 0)),
        "theories_total": sum(cell["theories_total"] for cell in rows),
    }


def seeds_are_fresh() -> bool:
    """True when no other artifact already used the block; this run's own record is fine."""
    if ARTIFACT.exists():
        try:
            recorded = json.loads(ARTIFACT.read_text(encoding="utf-8")).get("seeds") or []
        except (OSError, ValueError):
            recorded = []
        if tuple(recorded) == SEEDS:
            return True
    return not (set(SEEDS) & harvest_seeds(ROOT / "docs"))


def control_facts(rows: list[dict]) -> dict:
    """Compare the ledgered reference cell with the committed falsifier series."""
    recorded = json.loads(CONTROL.read_text(encoding="utf-8"))
    row = next(r for r in recorded["rows"] if r["colony"] == "FULL")
    theories = [item["theories"] for item in rows]
    beliefs = [item["retained_beliefs"] for item in rows]
    expected_theories = list(row["series"]["theories"])
    expected_beliefs = list(row["series"]["beliefs"])
    mismatch = None
    for index, (got, want) in enumerate(zip(theories, expected_theories)):
        if got != want:
            mismatch = {"cycle": index + 1, "ledger": got, "recorded": want}
            break
    belief_mismatch = None
    for index, (got, want) in enumerate(zip(beliefs, expected_beliefs)):
        if got != want:
            belief_mismatch = {"cycle": index + 1, "ledger": got, "recorded": want}
            break
    return {
        "seed": CONTROL_SEED,
        "cycles": len(rows),
        "theory_match": theories == expected_theories,
        "belief_match": beliefs == expected_beliefs,
        "first_theory_mismatch": mismatch,
        "first_belief_mismatch": belief_mismatch,
        "ledger_last_nonzero_theory_cycle": next(
            (index + 1 for index, count in reversed(list(enumerate(theories))) if count > 0), 0
        ),
    }


# ==================================================================
# The campaign
# ==================================================================

def load_parts() -> list[dict]:
    """The 18 cells from their recorded parts, refusing a missing or short cell."""
    cells: list[dict] = []
    for arm in ARMS:
        for seed in SEEDS:
            path = PARTS / ("%s_%d.json" % (arm, seed))
            if not path.exists():
                raise SystemExit("missing part for %s seed %d; refusing to finish" % (arm, seed))
            part = json.loads(path.read_text(encoding="utf-8"))
            if part.get("arm") != arm or part.get("seed") != seed:
                raise SystemExit("part %s does not hold the cell it is named for" % path.name)
            rows = part.get("ledger") or []
            if len(rows) != CYCLES:
                raise SystemExit("part %s holds %d cycles, not %d" % (path.name, len(rows), CYCLES))
            cells.append({"arm": arm, "seed": seed, **part["facts"]})
    return cells


def finish() -> dict:
    """Complete an interrupted campaign from its parts, running only the control.

    Used when all 18 cells wrote their parts but the process stopped before the artifact.
    No cell is rerun, replaced or dropped, and the artifact records how it was finished.
    """
    text = PREREG.read_text(encoding="utf-8")
    if protocol_digest(text) != FROZEN_DIGEST:
        raise SystemExit("the protocol does not match its pinned digest; refusing to finish")
    if execution_count(text) != 0:
        raise SystemExit("the protocol already records an execution; refusing to finish")
    fresh = seeds_are_fresh()
    if not fresh:
        raise SystemExit("the pre-registered seed block is already used under docs/")
    cells = load_parts()
    control = control_facts(run_cell("FULL", CONTROL_SEED, stimulus()))
    return assemble(cells, control, fresh, resumed=True)


def measure() -> dict:
    text = PREREG.read_text(encoding="utf-8")
    if protocol_digest(text) != FROZEN_DIGEST:
        raise SystemExit("the protocol does not match its pinned digest; refusing to run")
    if execution_count(text) != 0:
        raise SystemExit("the protocol already records an execution; refusing to run again")
    fresh = seeds_are_fresh()
    if not fresh:
        raise SystemExit("the pre-registered seed block is already used under docs/")

    events = stimulus()
    PARTS.mkdir(parents=True, exist_ok=True)
    cells: list[dict] = []
    for arm in ARMS:
        for seed in SEEDS:
            rows = run_cell(arm, seed, events)
            facts = cell_facts(rows)
            part = {"arm": arm, "seed": seed, "facts": facts, "ledger": rows}
            (PARTS / ("%s_%d.json" % (arm, seed))).write_text(
                json.dumps(part, indent=1) + "\n", encoding="utf-8"
            )
            cells.append({"arm": arm, "seed": seed, **facts})

    control_rows = run_cell("FULL", CONTROL_SEED, events)
    control = control_facts(control_rows)
    return assemble(cells, control, fresh)


def assemble(cells: list[dict], control: dict, fresh: bool, resumed: bool = False) -> dict:
    """Build the artifact from the cells and the control; the only place it is written."""
    summary = {arm: arm_summary(cells, arm) for arm in ARMS}
    deaths = {arm: summary[arm]["median_death_cycle"] for arm in ARMS}
    reference_cells = [cell for cell in cells if cell["arm"] == "FULL"]
    reference_removals = sum(
        sum(cell["theory_removals"].values()) for cell in reference_cells
    )
    reference_unexplained = sum(cell["unexplained"] for cell in reference_cells)
    axis_live = any(
        (
            tuple(summary[arm]["death_cycles"]),
            tuple(sorted(summary[arm]["theory_removals"].items())),
        )
        != (
            tuple(summary["FULL"]["death_cycles"]),
            tuple(sorted(summary["FULL"]["theory_removals"].items())),
        )
        for arm in ARMS
        if arm != "FULL"
    )
    gates = {
        "G1_neutral_observer": bool(control["theory_match"] and control["belief_match"]),
        "G2_attribution_complete": (
            reference_removals > 0
            and reference_unexplained <= UNEXPLAINED_BAND * reference_removals
        ),
        "G3_axis_live": bool(axis_live),
        "G4_denominators": (
            all(cell["cycles"] == CYCLES for cell in cells)
            and all(cell["theory_cycles"] >= 10 for cell in reference_cells)
        ),
        "G5_seed_independence": bool(fresh),
    }
    label = decide(gates, deaths)
    total_theory_removals = sum(
        sum(cell["theory_removals"].values()) for cell in cells
    )
    predictions = {
        "P1_every_arm_dies_before_end": all(cell["death_cycle"] < CYCLES for cell in cells),
        "P2_every_ablation_within_margin": all(
            abs(summary[arm]["median_death_cycle"] - deaths["FULL"]) < MARGIN
            for arm in ARMS
            if arm != "FULL"
        ),
        "P3_reference_modal_parent_loss": (
            modal_mechanism(summary["FULL"]["theory_removals"]) == "parent_loss"
        ),
        "P4_no_unexplained_in_reference": reference_unexplained == 0,
    }
    artifact = {
        "date": date.today().isoformat(),
        "engine_version": organica.__version__,
        "resumed_from_parts": resumed,
        "question": "Q042",
        "protocol_digest": FROZEN_DIGEST,
        "preregistration": "docs/REFERENCE-DEATH-LEDGER-PREREGISTRATION.md",
        "seeds": list(SEEDS),
        "control_seed": CONTROL_SEED,
        "cycles": CYCLES,
        "margin": MARGIN,
        "unexplained_band": UNEXPLAINED_BAND,
        "arms": list(ARMS),
        "cells": cells,
        "summary": summary,
        "label": label,
        "q042": {"outcome": Q042[label][0], "answer": Q042[label][1]},
        "gates": gates,
        "predictions": predictions,
        "control": control,
        "secondary": {
            "total_theory_removals": total_theory_removals,
            "reference_theory_removals": reference_removals,
            "reference_share_of_theory_removals": (
                round(reference_removals / total_theory_removals, 4)
                if total_theory_removals else None
            ),
            "modal_mechanism": {arm: modal_mechanism(summary[arm]["theory_removals"]) for arm in ARMS},
            "reference_belief_removals": summary["FULL"]["belief_removals"],
            "unexplained_share": (
                round(reference_unexplained / reference_removals, 4)
                if reference_removals else None
            ),
        },
    }
    ARTIFACT.write_text(json.dumps(artifact, indent=1) + "\n", encoding="utf-8")
    return artifact


# ==================================================================
# Rendering, from the artifact only
# ==================================================================

def _share(part: int, whole: int) -> str:
    return "%.1f%%" % (100.0 * part / whole) if whole else "n/a"


def render(artifact: dict) -> str:
    label = artifact["label"]
    summary = artifact["summary"]
    gates = artifact["gates"]
    predictions = artifact["predictions"]
    control = artifact["control"]
    secondary = artifact["secondary"]
    lines: list[str] = []
    lines.append("# Reference-arm death ledger — result")
    lines.append("")
    lines.append(
        "**Measured %s: `%s`.** Six arms × three seeds × %d cycles on the falsifier's "
        "`lattice_L1` stimulus, engine %s. %s"
        % (
            artifact["date"],
            label,
            artifact["cycles"],
            artifact["engine_version"],
            artifact["q042"]["answer"],
        )
    )
    lines.append("")
    lines.append("## Death cycles")
    lines.append("")
    lines.append("| Arm | Per-seed death cycle | Median | Theory cycles | Theory removals |")
    lines.append("| --- | --- | --- | --- | --- |")
    for arm in artifact["arms"]:
        row = summary[arm]
        lines.append(
            "| %s | %s | %s | %d | %d |"
            % (
                arm,
                ", ".join(str(value) for value in row["death_cycles"]),
                row["median_death_cycle"],
                row["theory_cycles"],
                sum(row["theory_removals"].values()),
            )
        )
    lines.append("")
    lines.append(
        "The reference arm's median death cycle is **%s**; the earliest ablation death is "
        "**%s** and the latest is **%s**. Reference-arm theory removals are **%d of %d** "
        "events (%s), and the reference's modal mechanism is `%s`."
        % (
            summary["FULL"]["median_death_cycle"],
            min(summary[arm]["min_death_cycle"] for arm in artifact["arms"] if arm != "FULL"),
            max(summary[arm]["max_death_cycle"] for arm in artifact["arms"] if arm != "FULL"),
            secondary["reference_theory_removals"],
            secondary["total_theory_removals"],
            _share(
                secondary["reference_theory_removals"],
                secondary["total_theory_removals"],
            ),
            secondary["modal_mechanism"]["FULL"],
        )
    )
    lines.append("")
    lines.append("## Mechanisms")
    lines.append("")
    lines.append("### Theory removals")
    lines.append("")
    lines.append("| Arm | " + " | ".join(THEORY_REASONS) + " |")
    lines.append("| --- | " + " | ".join("---" for _ in THEORY_REASONS) + " |")
    for arm in artifact["arms"]:
        row = summary[arm]["theory_removals"]
        lines.append(
            "| %s | %s |"
            % (arm, " | ".join(str(row.get(reason, 0)) for reason in THEORY_REASONS))
        )
    lines.append("")
    lines.append("### Belief removals")
    lines.append("")
    lines.append("| Arm | " + " | ".join(BELIEF_REASONS) + " |")
    lines.append("| --- | " + " | ".join("---" for _ in BELIEF_REASONS) + " |")
    for arm in artifact["arms"]:
        row = summary[arm]["belief_removals"]
        lines.append(
            "| %s | %s |"
            % (arm, " | ".join(str(row.get(reason, 0)) for reason in BELIEF_REASONS))
        )
    lines.append("")
    lines.append("## Gates")
    lines.append("")
    lines.append("| Gate | Result |")
    lines.append("| --- | --- |")
    for name, passed in gates.items():
        lines.append("| %s | %s |" % (name, "pass" if passed else "FAIL"))
    lines.append("")
    lines.append(
        "The neutrality control compared the ledgered reference arm at seed %d against "
        "`docs/decay_falsifier/parts/FULL.json`: theories match **%s**, beliefs match "
        "**%s**."
        % (
            control["seed"],
            "yes" if control["theory_match"] else "no",
            "yes" if control["belief_match"] else "no",
        )
    )
    lines.append("")
    lines.append("## Predictions")
    lines.append("")
    lines.append("| Prediction | Result |")
    lines.append("| --- | --- |")
    for name, held in predictions.items():
        lines.append("| %s | %s |" % (name, "held" if held else "failed"))
    lines.append("")
    lines.append("## Q042")
    lines.append("")
    lines.append("**%s.** %s" % (artifact["q042"]["outcome"], artifact["q042"]["answer"]))
    lines.append("")
    lines.append(
        "Removal events are not distinct objects: a theory that returns and dies again "
        "counts again. The ledger is observational, and it cannot see why an edge failed to "
        "form — only that the belief carrying it was not formed."
    )
    lines.append("")
    lines.append(
        "The outcome section of the pre-registration is written from this artifact, and "
        "`--check` rejects a protocol whose execution record and artifact disagree."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--measure", action="store_true", help="run the 18 cells and the control")
    group.add_argument("--finish", action="store_true", help="complete from recorded parts, control only")
    group.add_argument("--render", action="store_true", help="write the page from the artifact")
    group.add_argument("--check", action="store_true", help="verify the protocol and artifact only")
    args = parser.parse_args()

    if args.measure or args.finish:
        artifact = measure() if args.measure else finish()
        print(
            "%s: %s, reference death %s, %d theory removals"
            % (
                "measured" if args.measure else "finished",
                artifact["label"],
                artifact["summary"]["FULL"]["median_death_cycle"],
                artifact["secondary"]["reference_theory_removals"],
            )
        )
    elif args.render:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        page = render(artifact)
        if "{" in page:
            raise SystemExit("the rendered page contains a brace; refusing to write it")
        DOC.write_text(page, encoding="utf-8")
        print("rendered %s" % DOC.name)
    else:
        text = PREREG.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.exists() else None
        problems = validate(text, artifact)
        if problems:
            raise SystemExit("FAIL: " + "; ".join(problems))
        page = DOC.read_text(encoding="utf-8")
        if artifact["label"] not in page:
            raise SystemExit("FAIL: the page does not name the artifact's label")
        print("reference death ledger: protocol frozen, executed, page current")


if __name__ == "__main__":
    main()
