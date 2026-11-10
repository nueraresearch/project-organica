"""PRESENCE-CAP-1: a frozen, cap-only test of whether the 40-slot budget limits assertion.

The record is data (`docs/presence_cap_prereg.json`) rendered to
`docs/PRESENCE-CAP-PREREGISTRATION.md`. The only manipulated variable is
`SleepService.MAX_PREDICTIONS`, set on an instance by a subclass that overrides no pipeline
method; `organica/` is not edited. `S_cycle` is read from the `SleepReport` the public API
already returns, so the measurement adds no observer to the engine.

No cell has run. The record is frozen and unauthorised: `--measure` refuses until
`authorisation.granted` is true, and `--finish` writes only when the scorer and every gate pass.

    ./.venv/bin/python -m benchmarks.presence_cap_experiment --render-prereg
    ./.venv/bin/python -m benchmarks.presence_cap_experiment --check-prereg
    ./.venv/bin/python -m benchmarks.presence_cap_experiment --measure
    ./.venv/bin/python -m benchmarks.presence_cap_experiment --finish
    ./.venv/bin/python -m benchmarks.presence_cap_experiment --check
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import inspect
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import engine_stamp                                       # noqa: E402
from benchmarks.acquisition_compositional import (                          # noqa: E402
    PHASE_ACQUISITION,
    generate_compositional_world,
)
from benchmarks.acquisition_harness import (                                # noqa: E402
    SHORT_CYCLES,
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import (                                 # noqa: E402
    EVENTS_PER_CYCLE,
    _world_compositional_edges,
    structure_edges,
)
from organica.sleep import SleepService                                     # noqa: E402

PREREG = ROOT / "docs" / "presence_cap_prereg.json"
DOC = ROOT / "docs" / "PRESENCE-CAP-PREREGISTRATION.md"
ARTIFACT = ROOT / "docs" / "presence_cap_run.json"
RESULT = ROOT / "docs" / "PRESENCE-CAP-RESULT.md"
AUDIT = ROOT / "docs" / "presence_assertion_audit_0.14.0.json"
LADDER = ROOT / "docs" / "presence_assertion_ladder_0.14.0.json"
PARTS = ROOT / ".scratch" / "presence_cap" / "parts"

KIND = "presence_cap_run"
BAR_SD_FACTOR = 2
T_LOWER_95_DF5 = 2.5706           # two-sided 0.95 t quantile at 5 degrees of freedom, declared
UNCAPPED = 10 ** 9
VERDICTS = (
    "VOID",
    "CAP NOT BINDING",
    "ADMISSION-ONLY BOTTLENECK",
    "CAP LIMITING",
    "CAP LIMITING BELOW BAR",
    "CAP NOT LIMITING",
    "MIXED",
)
# The registry artifact echoes the seeds of every docs artifact, so it cannot be read as
# evidence that a seed was consumed before this record allocated it.
REGISTRY_ECHOES = ("docs/stage_b_protocol.json",)


class CapOnlySleepService(SleepService):
    """The shipped engine with one instance constant changed and no method replaced.

    This is the whole treatment. It defines `__init__` and nothing else, so candidate
    construction, ranking, filtering, retention and storage are the engine's own.
    """

    def __init__(self, memory, cap: int):
        super().__init__(memory)
        self.MAX_PREDICTIONS = int(cap)


def prereg() -> dict:
    return json.loads(PREREG.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- derivations

def audit_counts() -> list[int]:
    body = json.loads(AUDIT.read_text(encoding="utf-8"))
    return [row["asserted_world_edges"] for row in body["rows"]]


def derived_bar() -> int:
    """Twice the between-seed standard deviation already measured at cap 40."""
    return round(BAR_SD_FACTOR * statistics.stdev(audit_counts()))


def derived_ceiling() -> float:
    """The reach-limited part of the loss: edges no 40-row window ever admitted."""
    body = json.loads(LADDER.read_text(encoding="utf-8"))
    return statistics.mean(row["buckets"]["offered_not_admitted"] for row in body["rows"])


def treatment_overrides() -> list[str]:
    """Every method the treatment defines, which must be `__init__` alone."""
    return sorted(name for name, value in vars(CapOnlySleepService).items()
                  if callable(value) and not name.startswith("__p"))


def seed_collisions(seeds: list[int], allow: tuple[Path, ...]) -> dict[int, list[str]]:
    """Every docs artifact other than the allowed ones that already names a seed."""
    allowed = {str(path) for path in allow}
    found: dict[int, list[str]] = {}
    for path in sorted(glob.glob(str(ROOT / "docs" / "*.json"))):
        rel = Path(path).relative_to(ROOT).as_posix()
        if rel in REGISTRY_ECHOES or path in allowed:
            continue
        try:
            text = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for seed in seeds:
            if str(seed) in text:
                found.setdefault(seed, []).append(rel)
    return found


# --------------------------------------------------------------------------- validation

def validate(body: dict | None = None) -> list[str]:
    found: list[str] = []
    body = body or prereg()
    if body.get("prereg") != "PRESENCE-CAP-1":
        found.append("the record is not PRESENCE-CAP-1")
    if body.get("status") != "FROZEN, NOT RUN":
        found.append("the record is not frozen and unrun")
    if body.get("no_cells_run") is not True or body.get("design", {}).get("no_cells_run") is not True:
        found.append("the record does not state that no cell has run")
    if body.get("authorisation", {}).get("granted") is not False:
        found.append("the record now claims authorisation; that is an owner decision")

    engine = body.get("engine", {})
    if engine.get("edit") != "none":
        found.append("the record does not state that no engine file changes")
    if engine.get("overrides") != ["__init__"]:
        found.append("the declared treatment overrides are not `__init__` alone")
    actual = treatment_overrides()
    if actual != ["__init__"]:
        found.append("the treatment class defines %r, so it is not a one-variable arm" % (actual,))

    design = body.get("design", {})
    seeds = list(design.get("seeds", []))
    levels = list(design.get("levels", []))
    if len(seeds) != 6 or len(set(seeds)) != 6:
        found.append("the seed block is not six distinct seeds")
    if design.get("bootstrap") in seeds:
        found.append("the bootstrap seed is also a world seed")
    if levels != [40, 80, 112, UNCAPPED]:
        found.append("the cap levels are not 40, 80, 112 and the declared diagnostic ceiling")
    if design.get("shipped_cap") != 40 or SleepService.MAX_PREDICTIONS != 40:
        found.append("the shipped cap is not 40 on this build")
    if design.get("cells") != len(seeds) * len(levels):
        found.append("the cell count is not levels times seeds")
    if design.get("cycles") != SHORT_CYCLES:
        found.append("the cycle count is not the audit's acquisition block")

    bar = body.get("bar", {})
    if bar.get("value") != derived_bar():
        found.append("the bar %r is not the derived %r" % (bar.get("value"), derived_bar()))
    if not bar.get("derivation") or not bar.get("fragility"):
        found.append("the bar has no derivation or no stated fragility")
    ceiling = body.get("ceiling", {})
    if abs(float(ceiling.get("value", -1)) - derived_ceiling()) > 1e-9:
        found.append("the admission ceiling %r is not the derived %r"
                     % (ceiling.get("value"), derived_ceiling()))
    if not ceiling.get("note"):
        found.append("the ceiling has no account of what it does and does not bound")

    collisions = seed_collisions(seeds + [design.get("bootstrap")], allow=(PREREG,))
    if collisions:
        found.append("the seed block is not fresh: %r" % (collisions,))

    endpoints = body.get("endpoints", {})
    for name in ("W", "P", "S_cycle", "S_ever", "A", "A_W", "A_pred", "A_other"):
        if not endpoints.get(name):
            found.append("the endpoint %s is not defined" % name)
    gates = body.get("gates", {})
    for name in ("K1_build", "K2_same_world", "K3_presence_invariant", "K4_cap_live",
                 "K5_cap_only", "K6_denominator"):
        if not gates.get(name):
            found.append("the record has no %s" % name)
    readings = body.get("readings", {})
    for name in ("SCALES", "FLAT", "ADMISSION SCALES, ASSERTION FLAT", "MIXED", "threshold"):
        if not readings.get(name):
            found.append("the record has no %r reading" % name)
    verdicts = {row.get("verdict") for row in body.get("decision_table", [])}
    if verdicts != set(VERDICTS):
        found.append("the decision table cannot reach exactly %r" % (sorted(VERDICTS),))
    if not all(row.get("decision") for row in body.get("decision_table", [])):
        found.append("a decision_table row names no decision")
    profile = body.get("retention_profile", {})
    if not profile.get("rule"):
        found.append("the record declares no retention rule")
    if [step.get("ratio") for step in profile.get("steps", [])] != \
            ["P/W", "S_ever/P", "A_W/S_ever"]:
        found.append("the retention steps are not the three this block measures")
    source = inspect.getsource(run_cell)
    for step in profile.get("steps", []):
        missing = [field for field in step.get("cell_fields", []) if field not in source]
        if missing:
            found.append("retention step %r names unrecorded fields %r"
                         % (step.get("ratio"), missing))
    prior = ladder_prior()
    if not prior.get("primary_suspect"):
        found.append("the retention rule cannot fire on the ladder record")
    if not prior.get("consistent"):
        found.append("the ladder prior does not reconcile its buckets with its admitted total")
    adoption = body.get("adoption", {})
    if not adoption.get("rule") or not adoption.get("withdrawal"):
        found.append("the record has no adoption rule or no withdrawal rule")
    if not adoption.get("not_authorised"):
        found.append("the record does not say what it does not authorise")
    if not body.get("stop_condition"):
        found.append("the record has no stop condition")
    if not body.get("not_evidence"):
        found.append("the record has no statement of what it does not claim")
    return found


# --------------------------------------------------------------------------- rendering

def render_prereg(body: dict) -> str:
    design = body["design"]
    levels = list(design["levels"])
    lines = [
        "# Presence to assertion: the cap-only experiment (PRESENCE-CAP-1)",
        "",
        "Generated from `docs/presence_cap_prereg.json` by "
        "`python -m benchmarks.presence_cap_experiment --render-prereg`. Do not edit by hand.",
        "",
        "**Status: %s. Not authorised.** No cell has run. This record fixes the protocol; it does "
        "not licence a run." % body["status"],
        "",
        "Question 2 of the conversion program (`%s`), frozen on its own. %s"
        % (body["program"]["draft"], body["program"]["relationship"]),
        "",
        "## The question",
        "",
        body["question"],
        "",
        "## The hypothesis, stated before any cell",
        "",
        body["hypothesis"]["statement"],
        "",
        "**Prediction.** %s" % body["hypothesis"]["prediction"],
        "",
        "**Falsifier.** %s" % body["hypothesis"]["falsifier"],
        "",
        "**Alternative.** %s" % body["hypothesis"]["alternative"],
        "",
        "## The engine is frozen; the treatment is one constant",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Engine | %s |" % body["engine"]["version"],
        "| Engine edit | **%s** |" % body["engine"]["edit"],
        "| Engine pin | `%s` |" % body["engine"]["pin"],
        "| Treatment | `%s` |" % body["engine"]["treatment"],
        "| Base class | `%s` |" % body["engine"]["treatment_base"],
        "| Overrides | %s |" % ", ".join("`%s`" % name for name in body["engine"]["overrides"]),
        "| Constants changed | %s |" % ", ".join("`%s`" % name for name in body["engine"]["changes"]),
        "",
        body["engine"]["why_not_the_existing_override"],
        "",
        "`S_cycle` is read from the `SleepReport` the engine's public `run_sleep_cycle()` already "
        "returns, so no observer sits inside the engine: %s." % body["engine"]["recorded_per_cell"],
        "",
        "## What the prior blocks already establish, and what they leave open",
        "",
        "| Block | Artifact | Reading | Why it does not answer this question |",
        "| --- | --- | --- | --- |",
    ]
    for row in body["prior"]:
        lines.append("| %s | `%s` | %s | %s |" % (
            row["block"], row["artifact"], row["reading"], row["why_it_does_not_answer"]))
    ceiling = body["ceiling"]
    bar = body["bar"]
    lines += [
        "",
        "## The ceiling the ladder already implies",
        "",
        "**%s %s per seed** (%s): %s." % (
            ceiling["value"], ceiling["unit"], ceiling["source"], ceiling["derivation"]),
        "",
        ceiling["note"],
        "",
        "## The bar, and why it is not computed on this block",
        "",
        "A mean paired gain of **%s %s**, derived as %s. Provenance: `%s`."
        % (bar["value"], bar["unit"], bar["derivation"], bar["source"]),
        "",
        "**Fragility.** %s" % bar["fragility"],
        "",
        "## Freeze notes: corrections made before any cell",
        "",
    ]
    for note in body["freeze_notes"]["corrections_before_any_cell"]:
        lines.append("- %s" % note)
    lines += [
        "",
        "## The design",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Variable | `%s` |" % design["variable"],
        "| Levels | %s |" % ", ".join(
            "`%s`%s" % (level, " (diagnostic ceiling)" if level == UNCAPPED else "")
            for level in levels),
        "| Seeds | %s |" % ", ".join(str(seed) for seed in design["seeds"]),
        "| Bootstrap | %s |" % design["bootstrap"],
        "| Cycles | %s |" % design["cycles"],
        "| Cells | %s (%s levels x %s seeds) |" % (
            design["cells"], len(levels), len(design["seeds"])),
        "| Witness cell | seed %s at cap %s |" % (
            design["witness_cell"]["seed"], design["witness_cell"]["cap"]),
        "| Pairing | %s |" % design["pairing"],
        "| World | %s |" % design["world"],
        "",
        "**Freshness.** %s" % design["freshness"],
        "",
        "**Witness.** %s." % design["witness_cell"]["why"],
        "",
        "## Endpoints, named once",
        "",
        "| Reading | Definition |",
        "| --- | --- |",
    ]
    for name, text in body["endpoints"].items():
        lines.append("| `%s` | %s |" % (name, text))
    lines += [
        "",
        "## Gates, which decide admissibility before any reading",
        "",
        "| Gate | Requirement |",
        "| --- | --- |",
    ]
    for name, rule in body["gates"].items():
        lines.append("| `%s` | %s |" % (name, rule))
    lines += [
        "",
        "## Readings, in the order they are read",
        "",
        "| Reading | Rule |",
        "| --- | --- |",
    ]
    for name, rule in body["readings"].items():
        lines.append("| %s | %s |" % ("`%s`" % name if name != "threshold" else "**Threshold**", rule))
    lines += [
        "",
        "The readings are membership readings, not aggregate counts: adding a world edge to "
        "`A_W` means the organism asserts that edge, not that a count moved.",
        "",
        "## The retention profile, declared before any cell",
        "",
        body["retention_profile"]["rule"],
        "",
        "| Stage | Prior retained | Prior drop |",
        "| --- | --- | --- |",
    ]
    prior = ladder_prior()
    retained = prior["retained"]
    drops = prior["absolute_drop"]
    lines.append("| W | %d | - |" % retained["W"])
    lines.append("| P | %d | %d |" % (retained["P"], drops["P->S_ever"]))
    lines.append("| S_ever | %d | %d |" % (retained["S_ever"], drops["S_ever->A_W"]))
    lines.append("| A_pred | %d | - |" % retained["A_pred"])
    lines += [
        "",
        "| Step | Prior ratio | Prior relative loss |",
        "| --- | --- | --- |",
    ]
    for name in ("P/W", "S_ever/P", "A_W/S_ever", "A_W|admitted/S_ever"):
        lines.append("| %s | %s | - |" % (name, prior["ratios"][name]))
    for name in ("P->S_ever", "S_ever->A_W"):
        lines.append("| %s | - | %s |" % (name, prior["loss_share"][name]))
    lines += [
        "",
        "The prior columns are recomputed from `%s` on every render, pooled over its six rows. "
        "The primary suspect stage is **%s**, and the ladder's own bucket shares over its %d "
        "misses are %s at admission, %s before it and %s after it. %d asserted edges never passed "
        "admission: they are a bypass, excluded from the retained chain, and counted neither as "
        "retention nor as loss."
        % (prior["source"], prior["primary_suspect"],
           prior["retained"]["P"] - prior["retained"]["A_pred"],
           prior["bucket_share"]["offered_not_admitted"], prior["bucket_share"]["not_offered"],
           prior["bucket_share"]["admitted_not_asserted"], prior["edges"]["bypass"]),
        "",
        "**The steps the engine makes identities.** %s" % body["retention_profile"]["identity_steps"][0],
        "",
        "**Why the last step is not `A/S_final`.** %s"
        % body["retention_profile"]["identity_steps"][1],
        "",
        "**Why `A_W/S_ever` is not pure retention.** %s"
        % body["retention_profile"]["identity_steps"][2],
        "",
        "## The decision table",
        "",
        "| Condition | Verdict | Decision | What it licenses |",
        "| --- | --- | --- | --- |",
    ]
    for row in body["decision_table"]:
        lines.append("| %s | **%s** | %s | %s |"
                     % (row["condition"], row["verdict"], row["decision"], row["reading"]))
    lines += [
        "",
        "## Adoption, withdrawal and stop",
        "",
        body["adoption"]["rule"],
        "",
        "**Withdrawal.** %s" % body["adoption"]["withdrawal"],
        "",
        "**Not authorised by this record.** %s"
        % "; ".join(body["adoption"]["not_authorised"]),
        "",
        "**Stop condition.** %s" % body["stop_condition"],
        "",
        "## Cost and authorisation",
        "",
        "%s cells (%s witness) x %s cycles. %s" % (
            body["cost"]["cells"], body["cost"]["witness_cells"],
            body["cost"]["cycles"], body["cost"]["wall_clock_estimate"]),
        "",
        "**Authorisation.** %s" % body["authorisation"]["note"],
        "",
        "## What this does not claim",
        "",
        body["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def render_result(artifact: dict) -> str:
    details = artifact.get("details", {})
    body = prereg()
    lines = [
        "# Presence to assertion: the cap-only experiment — result",
        "",
        "Generated from `docs/presence_cap_run.json` by "
        "`python -m benchmarks.presence_cap_experiment --finish`. Do not edit by hand.",
        "",
        "Protocol: `docs/PRESENCE-CAP-PREREGISTRATION.md`. Engine %s, unchanged; the only "
        "manipulated variable is the Layer-1 prediction cap."
        % artifact.get("engine", {}).get("version", "?"),
        "",
        "**Verdict: `%s`**" % artifact["verdict"],
        "",
        "| Reading | Value |",
        "| --- | --- |",
        "| bar | %s |" % body["bar"]["value"],
        "| mean paired gain at 112 | %s |" % details.get("mean_gain"),
        "| 95%% paired lower bound | %s |" % details.get("lower_bound"),
        "| reach-limited ceiling | %s |" % details.get("ceiling"),
        "| gain over ceiling | %s |" % details.get("ceiling_ratio"),
        "",
        "| Seed | Cap | Present | S_ever (world) | A_W | A_pred | A_other | Windows | Cycles at cap |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for cell in artifact.get("cells", []):
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            cell["seed"], cell["cap"], cell.get("present_world_edges"),
            cell.get("admitted_world_edges", cell.get("s_ever_world_edges")),
            cell.get("asserted_world_edges"),
            cell.get("asserted_and_admitted"), cell.get("asserted_without_admission"),
            cell.get("cycles_run"), cell.get("cycles_at_cap")))
    lines += [
        "",
        "| Seed | A_W at 40 | A_W at 80 | A_W at 112 | A_W uncapped | Gain at 112 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in artifact.get("gains", []):
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            row["seed"], row["40"], row["80"], row["112"],
            row[str(UNCAPPED)], row["gain_112"]))
    lines += [
        "",
        "**What this does not claim.** %s" % body["not_evidence"],
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------- measurement

def _digest(pairs) -> str:
    return hashlib.sha256("|".join("%s>%s" % edge for edge in sorted(pairs))
                          .encode("utf-8")).hexdigest()[:16]


def _ratio(numerator: int, denominator: int):
    """A ratio with no denominator is not measurable, never zero (rule 13b)."""
    if not denominator:
        return "not measurable"
    return round(numerator / denominator, 6)


def _suspect(drops: dict) -> str | None:
    """The earliest stage with the largest absolute drop, ties to the earlier stage."""
    measured = [(name, value) for name, value in drops.items() if value is not None]
    if not measured:
        return None
    best = max(value for _, value in measured)
    return next(name for name, value in measured if value == best)


def retention_profile(cell: dict) -> dict:
    """Stage counts, ratios and absolute drops for one cell; the bypass stays separate."""
    world = cell.get("world_edges", 0)
    present = cell.get("present_world_edges", 0)
    ever = cell.get("s_ever_world_edges", 0)
    asserted = cell.get("asserted_world_edges", 0)
    bypass = cell.get("asserted_without_admission", 0)
    admitted_asserted = max(asserted - bypass, 0)
    ratios = {
        "P/W": _ratio(present, world),
        "S_ever/P": _ratio(ever, present),
        "A_W/S_ever": _ratio(asserted, ever),
        "A_W|admitted/S_ever": _ratio(admitted_asserted, ever),
    }
    losses = {
        "P->S_ever": _ratio(present - ever, present),
        "S_ever->A_W": _ratio(ever - admitted_asserted, ever),
    }
    drops = {
        "P->S_ever": present - ever if present else None,
        "S_ever->A_W": ever - admitted_asserted if ever else None,
    }
    return {
        "steps": {
            "P/W": {"numerator": present, "denominator": world, "ratio": ratios["P/W"]},
            "S_ever/P": {"numerator": ever, "denominator": present, "ratio": ratios["S_ever/P"]},
            "A_W/S_ever": {"numerator": asserted, "denominator": ever,
                           "ratio": ratios["A_W/S_ever"]},
        },
        "retained": {"W": world, "P": present, "S_ever": ever, "A_pred": admitted_asserted},
        "ratios": ratios,
        "loss_share": losses,
        "absolute_drop": drops,
        "bypass": bypass,
        "primary_suspect": _suspect(drops),
        "not_measurable": [name for name, value in ratios.items()
                           if value == "not measurable"],
    }


def ladder_prior() -> dict:
    """The same profile pooled over the committed ladder record, recomputed every call."""
    ladder = json.loads(LADDER.read_text(encoding="utf-8"))
    rows, summary = ladder["rows"], ladder["summary"]
    world = sum(row["world_edges"] for row in rows)
    present = sum(row["present_world_edges"] for row in rows)
    admitted = sum(row["admitted_world_edges"] for row in rows)
    asserted = sum(row["asserted_world_edges"] for row in rows)
    buckets = summary["pooled_buckets"]
    admitted_not_asserted = buckets["admitted_not_asserted"]
    admitted_asserted = admitted - admitted_not_asserted
    bypass = asserted - admitted_asserted
    retained = {"W": world, "P": present, "S_ever": admitted, "A_pred": admitted_asserted}
    drops = {"P->S_ever": present - admitted, "S_ever->A_W": admitted - admitted_asserted}
    ratios = {
        "P/W": _ratio(present, world),
        "S_ever/P": _ratio(admitted, present),
        "A_W/S_ever": _ratio(asserted, admitted),
        "A_W|admitted/S_ever": _ratio(admitted_asserted, admitted),
    }
    losses = {"P->S_ever": _ratio(present - admitted, present),
              "S_ever->A_W": _ratio(admitted - admitted_asserted, admitted)}
    shares = {name: _ratio(value, summary["misses_total"]) for name, value in buckets.items()}
    return {
        "source": LADDER.name,
        "rows": len(rows),
        "retained": retained,
        "absolute_drop": drops,
        "edges": {"W": world, "P": present, "S_ever": admitted, "A_W": asserted,
                  "admitted_asserted": admitted_asserted,
                  "admitted_not_asserted": admitted_not_asserted, "bypass": bypass},
        "ratios": ratios,
        "loss_share": losses,
        "bucket_share": shares,
        "primary_suspect": _suspect(drops),
        "consistent": (bypass >= 0
                       and admitted == admitted_asserted + admitted_not_asserted
                       and retained["A_pred"] + bypass == asserted),
    }


def run_cell(seed: int, cap: int, cycles: int = SHORT_CYCLES) -> dict:
    """One acquisition run at one cap; returns readings, not a verdict."""
    world = generate_compositional_world(seed=seed, cycles=cycles)
    events_text, trainable = world["events"], world["trainable"]
    world_edges = _world_compositional_edges(world)

    db_path = _make_scratch_db("presence_cap")
    mem = _CountingMemoryService(str(db_path))
    svc = CapOnlySleepService(mem, cap)
    acq_lo, acq_hi = PHASE_ACQUISITION
    acq_event_lo, acq_event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE

    windows: list[list[tuple[str, str]]] = []
    try:
        for i, (text, train_flag) in enumerate(zip(events_text, trainable)):
            in_acq = acq_event_lo <= i < acq_event_hi
            if in_acq and not train_flag:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                mem.current_cycle = i // EVENTS_PER_CYCLE
            mem.store(text, event_type="observe", source="env_acq" if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                report = svc.run_sleep_cycle()
                windows.append([(p.source, p.target) for p in report.predictions])
        asserted_pairs = {(a, b) for a, targets in structure_edges(svc._load_prior_candidates()).items()
                          for b in targets}
        temporal_pairs = {(a, b) for a, b, _c in mem.temporal_edges(min_count=1)}
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    admitted = {edge for window in windows for edge in window}
    world_admitted = world_edges & admitted
    world_asserted = world_edges & asserted_pairs
    sizes = [len(window) for window in windows]
    cell = {
        "seed": seed,
        "cap": int(cap),
        "cap_effective": svc.MAX_PREDICTIONS,
        "engine_version": engine_stamp.engine_version(),
        "engine_sha256": engine_stamp.engine_sha256(),
        "cycles_run": len(windows),
        "world_edges": len(world_edges),
        "world_digest": _digest(world_edges),
        "present_world_edges": len(world_edges & temporal_pairs),
        "present_fingerprint": _digest(world_edges & temporal_pairs),
        "s_ever_world_edges": len(world_admitted),
        "s_ever_fingerprint": _digest(world_admitted),
        "admitted_world_edges": len(world_admitted),
        "asserted_world_edges": len(world_asserted),
        "asserted_and_admitted": len(world_asserted & admitted),
        "asserted_without_admission": len(world_asserted - admitted),
        "asserted_fingerprint": _digest(world_asserted),
        "s_cycle_sizes": sizes,
        "max_window": max(sizes) if sizes else 0,
        "median_window": statistics.median(sizes) if sizes else 0,
        "cycles_at_cap": sum(1 for size in sizes if size >= cap) if cap <= 112 else None,
    }
    cell["retention_profile"] = retention_profile(cell)
    return cell


def _part_path(seed: int, cap: int) -> Path:
    return PARTS / ("%s_%s.json" % (seed, cap))


def measure() -> int:
    body = prereg()
    if not body.get("authorisation", {}).get("granted"):
        raise SystemExit("REFUSED: the record is not authorised; no cell may run")
    for seed in body["design"]["seeds"]:
        for cap in body["design"]["levels"]:
            path = _part_path(seed, cap)
            if path.exists():
                print("cached %s" % path.name, flush=True)
                continue
            cell = run_cell(seed, cap)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(engine_stamp.stamp(cell), indent=1) + "\n", encoding="utf-8")
            print("cell seed=%d cap=%d present=%d ever=%d asserted=%d"
                  % (seed, cap, cell["present_world_edges"], cell["s_ever_world_edges"],
                     cell["asserted_world_edges"]), flush=True)
    witness = body["design"]["witness_cell"]
    path = PARTS / ("witness_%s_%s.json" % (witness["seed"], witness["cap"]))
    if not path.exists():
        cell = run_cell(witness["seed"], witness["cap"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(engine_stamp.stamp(cell), indent=1) + "\n", encoding="utf-8")
    return 0


def _load_parts(body: dict) -> dict:
    cells = []
    for seed in body["design"]["seeds"]:
        for cap in body["design"]["levels"]:
            path = _part_path(seed, cap)
            if not path.exists():
                raise SystemExit("missing part %s; run --measure" % path.name)
            cells.append(json.loads(path.read_text(encoding="utf-8")))
    witness = body["design"]["witness_cell"]
    path = PARTS / ("witness_%s_%s.json" % (witness["seed"], witness["cap"]))
    if not path.exists():
        raise SystemExit("missing witness cell; run --measure")
    return {"cells": cells,
            "witness": json.loads(path.read_text(encoding="utf-8"))}


# --------------------------------------------------------------------------- scoring

def _same_direction(steps: list[int]) -> bool:
    return all(step >= 0 for step in steps) or all(step <= 0 for step in steps)


def verdict(body: dict, run: dict) -> tuple[str, dict]:
    seeds = list(body["design"]["seeds"])
    levels = list(body["design"]["levels"])
    cells = {(cell["seed"], cell["cap"]): cell for cell in run.get("cells", [])}
    if set(cells) != {(seed, level) for seed in seeds for level in levels}:
        return "VOID", {"gate": "K1_build", "reason": "the cell set is not levels x seeds"}

    digest = run.get("engine", {}).get("sha256")
    for cell in cells.values():
        if cell.get("engine_sha256") != digest or cell.get("cap_effective") != cell.get("cap"):
            return "VOID", {"gate": "K1_build", "seed": cell.get("seed"),
                            "cap": cell.get("cap")}
    for seed in seeds:
        if len({cells[(seed, level)]["world_digest"] for level in levels}) != 1:
            return "VOID", {"gate": "K2_same_world", "seed": seed}
        if len({cells[(seed, level)]["present_fingerprint"] for level in levels}) != 1:
            return "VOID", {"gate": "K3_presence_invariant", "seed": seed}

    live, changed = 0, 0
    for seed in seeds:
        forty = cells[(seed, 40)]
        if forty["cap"] != 40 or forty["max_window"] > 40:
            return "CAP NOT BINDING", {"gate": "K4_cap_live", "seed": seed,
                                       "max_window": forty["max_window"]}
        if forty["max_window"] == 40:
            live += 1
        if any(cells[(seed, level)]["s_ever_fingerprint"] != forty["s_ever_fingerprint"]
               for level in levels if level > 40):
            changed += 1
    if live < 5 or changed < 1:
        return "CAP NOT BINDING", {"gate": "K4_cap_live", "full_windows": live,
                                  "s_ever_changed": changed}

    overrides = treatment_overrides()
    if overrides != ["__init__"]:
        return "VOID", {"gate": "K5_cap_only", "overrides": overrides}
    witness = run.get("witness") or {}
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    reference = next((row for row in audit["rows"]
                      if row["seed"] == body["design"]["witness_cell"]["seed"]), None)
    if reference is None:
        return "VOID", {"gate": "K5_cap_only", "reason": "no audit row for the witness seed"}
    if (witness.get("present_world_edges") != reference["present_world_edges"]
            or witness.get("asserted_world_edges") != reference["asserted_world_edges"]
            or witness.get("asserted_fingerprint") != reference["asserted_fingerprint"]):
        return "VOID", {"gate": "K5_cap_only",
                        "reason": "cap 40 does not reproduce the shipped control",
                        "witness": {key: witness.get(key) for key in
                                    ("present_world_edges", "asserted_world_edges",
                                     "asserted_fingerprint")},
                        "audit": {key: reference.get(key) for key in
                                  ("present_world_edges", "asserted_world_edges",
                                   "asserted_fingerprint")}}
    for cell in cells.values():
        if not (cell["world_edges"] and cell["present_world_edges"] and cell["s_ever_world_edges"]):
            return "VOID", {"gate": "K6_denominator", "seed": cell["seed"], "cap": cell["cap"]}

    def asserted(seed: int, level: int) -> int:
        return cells[(seed, level)]["asserted_world_edges"]

    def ever(seed: int, level: int) -> int:
        return cells[(seed, level)]["s_ever_world_edges"]

    steps = {seed: [asserted(seed, 80) - asserted(seed, 40),
                    asserted(seed, 112) - asserted(seed, 80),
                    asserted(seed, UNCAPPED) - asserted(seed, 112)] for seed in seeds}
    up = [seed for seed in seeds if _same_direction(steps[seed])
          and any(step > 0 for step in steps[seed]) and steps[seed][0] >= 0]
    flat = [seed for seed in seeds
            if asserted(seed, 112) <= asserted(seed, 40)
            and asserted(seed, UNCAPPED) <= asserted(seed, 40)]
    reach = [seed for seed in seeds
             if ever(seed, 112) != ever(seed, 40) or ever(seed, UNCAPPED) != ever(seed, 40)]

    gains = [asserted(seed, 112) - asserted(seed, 40) for seed in seeds]
    mean_gain = round(statistics.mean(gains), 6)
    spread = statistics.stdev(gains) if len(gains) > 1 else 0.0
    lower = round(mean_gain - T_LOWER_95_DF5 * spread / math.sqrt(len(gains)), 6)
    details = {
        "gains_112": gains,
        "mean_gain": mean_gain,
        "lower_bound": lower,
        "bar": body["bar"]["value"],
        "positive_seeds": sum(1 for gain in gains if gain > 0),
        "ceiling": round(derived_ceiling(), 6),
        "ceiling_ratio": (round(mean_gain / derived_ceiling(), 6)
                          if derived_ceiling() else None),
        "scaling_seeds": len(up),
        "flat_seeds": len(flat),
        "reach_changed_seeds": len(reach),
    }

    if len(flat) >= 5 and len(reach) >= 5:
        return "ADMISSION-ONLY BOTTLENECK", details
    if len(flat) >= 5:
        return "CAP NOT LIMITING", details
    if len(up) >= 5:
        if (mean_gain >= body["bar"]["value"] and lower > 0
                and details["positive_seeds"] >= 5):
            return "CAP LIMITING", details
        return "CAP LIMITING BELOW BAR", details
    return "MIXED", details


def build() -> dict:
    body = prereg()
    parts = _load_parts(body)
    run = {
        "kind": KIND,
        "prereg": body["prereg"],
        "engine": {"version": engine_stamp.engine_version(),
                   "sha256": engine_stamp.engine_sha256()},
        "bar": body["bar"]["value"],
        "ceiling": round(derived_ceiling(), 6),
        "cells": parts["cells"],
        "witness": {key: parts["witness"].get(key) for key in
                    ("seed", "cap", "present_world_edges", "asserted_world_edges",
                     "asserted_fingerprint")},
    }
    levels = list(body["design"]["levels"])
    index = {(cell["seed"], cell["cap"]): cell for cell in parts["cells"]}
    run["gains"] = [
        {**{str(level): index[(seed, level)]["asserted_world_edges"] for level in levels},
         "seed": seed,
         "gain_112": (index[(seed, 112)]["asserted_world_edges"]
                      - index[(seed, 40)]["asserted_world_edges"])}
        for seed in body["design"]["seeds"]
    ]
    label, details = verdict(body, run)
    return dict(run, verdict=label, details=details)


def finish() -> int:
    problems = validate()
    if problems:
        raise SystemExit("the record is not valid: " + "; ".join(problems))
    body = prereg()
    if not body.get("authorisation", {}).get("granted"):
        raise SystemExit("REFUSED: the record is not authorised; no result may be written")
    artifact = build()
    if artifact["verdict"] == "VOID":
        raise SystemExit("REFUSED: the block is void (%r); nothing written"
                         % (artifact["details"],))
    ARTIFACT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=1) + "\n",
                        encoding="utf-8")
    RESULT.write_text(render_result(artifact), encoding="utf-8")
    print("%s: %s" % (artifact["verdict"], json.dumps(artifact["details"])))
    return 0


def check_prereg(body: dict | None = None) -> int:
    body = body or prereg()
    problems = validate(body)
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    if not DOC.exists():
        raise SystemExit("FAIL: %s does not exist" % DOC.name)
    if DOC.read_text(encoding="utf-8") != render_prereg(body):
        raise SystemExit("FAIL: the preregistration page is stale; rerun with --render-prereg")
    print("prereg %s: frozen, unrun, unauthorised, page current" % body["prereg"])
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no run artifact; the block has not run (run --measure, then --finish)")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    body = prereg()
    label, details = verdict(body, artifact)
    problems = []
    if label != artifact.get("verdict"):
        problems.append("the verdict is not what the cells imply")
    if details != artifact.get("details"):
        problems.append("the details are not what the cells imply")
    if engine_stamp.missing(artifact):
        problems.append("the artifact is not fully stamped: %r" % (engine_stamp.missing(artifact),))
    if RESULT.exists() and RESULT.read_text(encoding="utf-8") != render_result(artifact):
        problems.append("the result page is stale")
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    print("presence cap %s: %s" % (artifact["verdict"], artifact["details"]))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--render-prereg", action="store_true")
    group.add_argument("--check-prereg", action="store_true")
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.render_prereg:
        problems = validate()
        if problems:
            raise SystemExit("the record is not valid: " + "; ".join(problems))
        DOC.write_text(render_prereg(prereg()), encoding="utf-8")
        print("rendered %s" % DOC.name)
        return 0
    if args.check_prereg:
        return check_prereg()
    if args.measure:
        return measure()
    if args.finish:
        return finish()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
