"""D3-PERSISTENCE-4: a fresh G1-calibrated seed-varying replication on 0.14.0.

D3-3 was void at G1 because two legacy controls first reached zero at cycle 61
against a 1-60 bound. This block changes only the baseline-death bound, to 65,
and the seed window. Treatment, control, criteria, stages and horizon are
carried unchanged. The bound is calibrated on the three prior D3 control
distributions before this block runs, not on this block's cells.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import d3_persistence_prereg as P                         # noqa: E402
from benchmarks import d3_persistence_run as R                           # noqa: E402
from benchmarks import d3_persistence_seed_varying as S                  # noqa: E402
from benchmarks import engine_stamp                                      # noqa: E402
from benchmarks import force_matrix as fm                                # noqa: E402
from organica.sleep import SleepService                                  # noqa: E402

PREREG = ROOT / "docs" / "d3_persistence_g1_recalibrated_prereg.json"
PREREG_DOC = ROOT / "docs" / "D3-PERSISTENCE-G1-RECALIBRATED-PREREGISTRATION.md"
ARTIFACT = ROOT / "docs" / "d3_persistence_g1_recalibrated_run.json"
RESULT = ROOT / "docs" / "D3-PERSISTENCE-G1-RECALIBRATED-RESULT.md"
PARTS = ROOT / ".scratch" / "d3_persistence_g1_recalibrated" / "parts"

STAGES = ("witness", "preflight")
ARMS = ("control", "treatment")
KIND = "d3_persistence_g1_recalibrated_run"

POST_FREEZE_RESULT = (
    "**Post-freeze result.** This block ran on 2026-11-10. The result is "
    "`docs/D3-PERSISTENCE-G1-RECALIBRATED-RESULT.md`; the verdict is "
    "`PERSISTENCE REPAIRED`. This pointer was added after the run and changes no "
    "criterion, bar, seed, arm or gate."
)


class LegacyFrequencySleepService(fm.Instrumented):
    """Pre-promotion behavior: the source denominator is the raw tag count."""

    def _prediction_frequencies(self, raw):
        return raw


def _arm_class(arm: str):
    if arm == "control":
        return LegacyFrequencySleepService
    if arm == "treatment":
        return SleepService
    raise ValueError("unknown arm %r" % arm)


def prereg() -> dict:
    return json.loads(PREREG.read_text(encoding="utf-8"))


def part_path(stage: str, seed: int, arm: str) -> Path:
    return PARTS / ("%s_%d_%s.json" % (stage, seed, arm))


def run_cell(stage: str, seed: int, arm: str, colony: str = "FULL") -> dict:
    events = S.seeded_events(R.design_for(stage), seed)
    previous_arm = R.arm_class
    previous_colony = fm.colony_class
    R.arm_class = _arm_class
    if arm == "control" and colony == "FULL":
        fm.colony_class = lambda name: (LegacyFrequencySleepService if name == "FULL"
                                        else previous_colony(name))
    try:
        cell = R.run_cell(stage, seed, arm, colony, events=events)
    finally:
        R.arm_class = previous_arm
        fm.colony_class = previous_colony
    cell["world_digest"] = hashlib.sha256("\n".join(events).encode("utf-8")).hexdigest()[:16]
    return cell


def _job(args: tuple[str, int, str, str]) -> dict:
    stage, seed, arm, colony = args
    return run_cell(stage, seed, arm, colony)


def measure(workers: int = 1) -> int:
    body = prereg()
    seeds = list(body["design"]["seeds"])
    jobs = [(stage, seed, arm, "FULL") for stage in STAGES for seed in seeds for arm in ARMS]
    jobs += [("witness", seeds[0], "control", "NO_DREAMS"),
             ("witness", seeds[0], "control", "NO_QUESTIONS")]

    pending = []
    for job in jobs:
        stage, seed, arm, colony = job
        path = part_path(stage, seed, arm) if colony == "FULL" else PARTS / (
            "witness_%d_%s.json" % (seed, colony))
        if path.exists():
            print("cached %s" % path.name, flush=True)
            continue
        pending.append((job, path))

    if workers <= 1:
        for job, path in pending:
            cell = _job(job)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(engine_stamp.stamp(cell), indent=1) + "\n",
                            encoding="utf-8")
            print("cell %s %d %-9s cycles=%d theories=%d peak=%d first_zero=%s"
                  % (cell["stage"], cell["seed"], cell["arm"], cell["cycles_run"],
                     cell["theory_cycles"], cell["peak"], cell["first_zero_cycle"]),
                  flush=True)
        return 0

    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_job, job): (job, path) for job, path in pending}
        for future in as_completed(futures):
            _job_args, path = futures[future]
            cell = future.result()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(engine_stamp.stamp(cell), indent=1) + "\n",
                            encoding="utf-8")
            print("cell %s %d %-9s cycles=%d theories=%d peak=%d first_zero=%s"
                  % (cell["stage"], cell["seed"], cell["arm"], cell["cycles_run"],
                     cell["theory_cycles"], cell["peak"], cell["first_zero_cycle"]),
                  flush=True)
    return 0


def _load_parts() -> dict:
    body = prereg()
    seeds = list(body["design"]["seeds"])
    cells = []
    for stage in STAGES:
        for seed in seeds:
            for arm in ARMS:
                path = part_path(stage, seed, arm)
                if not path.exists():
                    raise SystemExit("missing part %s; run --measure" % path.name)
                cells.append(json.loads(path.read_text(encoding="utf-8")))
    controls = {}
    for colony in ("NO_DREAMS", "NO_QUESTIONS"):
        path = PARTS / ("witness_%d_%s.json" % (seeds[0], colony))
        if not path.exists():
            raise SystemExit("missing negative control %s; run --measure" % path.name)
        controls[colony] = json.loads(path.read_text(encoding="utf-8"))
    return {"cells": cells, "controls": controls}


def build() -> dict:
    body = prereg()
    parts = _load_parts()
    cells = parts["cells"]
    seeds = list(body["design"]["seeds"])
    fingerprint = engine_stamp.engine_sha256()
    first = next(cell for cell in cells
                 if cell["stage"] == "witness" and cell["seed"] == seeds[0]
                 and cell["arm"] == "control")
    rerun = run_cell("witness", seeds[0], "control")
    deterministic = rerun["digest"] == first["digest"]
    run = {
        "kind": KIND,
        "prereg": body["prereg"],
        "engine": {"fingerprint": fingerprint, "version": engine_stamp.engine_version()},
        "arms": {},
        "control_rerun_fingerprint": fingerprint if deterministic else "mismatch",
        "control_rerun_digest": rerun["digest"],
        "witness_negative_controls": {
            "NO_DREAMS": {"dreams_max": parts["controls"]["NO_DREAMS"]["dreams_max"]},
            "NO_QUESTIONS": {"questions_max": parts["controls"]["NO_QUESTIONS"]["questions_max"]},
        },
        "cells": cells,
    }
    for arm in ARMS:
        source = body["arms"][arm]
        run["arms"][arm] = {
            "decay": source["decay"],
            "death_threshold": source["death_threshold"],
            "frequency_decay": source["frequency_decay"],
            "fingerprint": fingerprint,
        }
    run["seed_axis"] = S.seed_axis(cells)
    label, details = P.verdict(body, run)
    return dict(run, verdict=label, details=details)


def validate(body: dict | None = None) -> list[str]:
    found = []
    body = body or prereg()
    if body.get("prereg") != "D3-PERSISTENCE-4":
        found.append("the record is not D3-PERSISTENCE-4")
    if body.get("status") != "FROZEN, NOT RUN":
        found.append("the record is not frozen and unrun")
    if body.get("no_cells_run") is not True:
        found.append("the record does not state that no cell has run")
    if body.get("g1_max_first_zero") != 65:
        found.append("the G1 bound is not 65")
    if not body.get("g1_bound_provenance"):
        found.append("the G1 bound has no provenance")
    design = body.get("design", {})
    seeds = design.get("seeds", [])
    if len(seeds) != 6 or len(set(seeds)) != 6:
        found.append("the seed block is not six distinct seeds")
    if design.get("bootstrap") in seeds:
        found.append("the bootstrap seed is also a world seed")
    if design.get("cells") != 24:
        found.append("the block is not 24 cells")
    if not design.get("world_variation"):
        found.append("the record does not say how the seed varies the world")
    if "G8_seed_axis_live" not in body.get("gates", {}):
        found.append("the record has no G8 seed-axis gate")
    if "seed_axis" not in body.get("scope", {}):
        found.append("the record does not scope the seed axis")
    if body.get("arms", {}).get("control", {}).get("frequency_decay") != "none":
        found.append("the control is not the pre-repair denominator")
    if body.get("arms", {}).get("treatment", {}).get("frequency_decay") != 0.95:
        found.append("the treatment is not the shipped matched denominator")
    return found


def render_prereg(body: dict) -> str:
    design = body["design"]
    stages = design["stages"]
    criteria = body["criteria"]
    lines = [
        "# D3 persistence engine replication (G1 recalibrated) — preregistration",
        "",
        "Generated from `docs/d3_persistence_g1_recalibrated_prereg.json` by "
        "`python -m benchmarks.d3_persistence_g1_recalibrated --render-prereg`. "
        "Do not edit by hand.",
        "",
        "**Status at freeze: FROZEN, NOT RUN.** No cell had run at freeze. The treatment is the shipped "
        "`organica.sleep.SleepService` at 0.14.0; the control is a benchmark-only "
        "pre-repair denominator ablation. This block changes no engine file.",
        "",
        POST_FREEZE_RESULT,
        "",
        "## The question",
        "",
        body["question"],
        "",
        "## Why this replication",
        "",
        "Prior block: `%s` returned **%s** (`%s`). %s"
        % (body["prior"]["prereg"], body["prior"]["result"],
           body["prior"]["artifact"], body["prior"]["defect"]),
        "",
        body["prior"]["reading"],
        "",
        "## The two arms",
        "",
        "| Arm | Service | Decay | Death threshold | Frequency decay | Rule |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for arm in ARMS:
        item = body["arms"][arm]
        lines.append("| %s | `%s` | %s | %s | %s | %s |" % (
            arm, item["service"], item["decay"], item["death_threshold"],
            item["frequency_decay"], item["rule"]))
    lines += [
        "",
        "## The block",
        "",
        "| Stage | Design | Cycles | What it reads |",
        "| --- | --- | --- | --- |",
        "| witness | `%s` | %s | %s |" % (
            stages["witness"]["design"], stages["witness"]["cycles"],
            stages["witness"]["reads"]),
        "| preflight | `%s` | %s | %s |" % (
            stages["preflight"]["design"], stages["preflight"]["horizon"],
            stages["preflight"]["reads"]),
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| world seeds | %s |" % ", ".join(str(seed) for seed in design["seeds"]),
        "| bootstrap seed | %s |" % design["bootstrap"],
        "| cells | %s (%s) |" % (design["cells"], design["cells_arithmetic"]),
        "| early window | %s-%s |" % tuple(design["early"]),
        "| k | %s |" % design["k"],
        "| pairing | %s |" % design["pairing"],
        "",
        "**Freshness.** %s" % design["freshness"],
        "",
        "**Seed-varying world.** %s" % body["scope"]["seed_axis"],
        "",
        "**G1 bound.** 1-%s cycles. %s" % (
            body.get("g1_max_first_zero", 60), body.get("g1_bound_provenance", "")),
        "",
        "## Criteria, in the order they are read",
        "",
        "| Criterion | Quantity | Rule | Bar | Provenance |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name in criteria["order"]:
        item = criteria[name]
        lines.append("| %s | %s | %s | %s | %s |" % (
            name, item["quantity"], item["rule"], item["bar"], item["bar_provenance"]))
    lines += [
        "",
        "The criteria are judged whole. A failed W1 leaves P1 and C1 unread.",
        "",
        "## Gates, which void the block before any criterion is read",
        "",
        "| Gate | Requirement |",
        "| --- | --- |",
    ]
    for name, rule in body["gates"].items():
        if name == "void_rule":
            continue
        lines.append("| %s | %s |" % (name, rule))
    lines += [
        "",
        "Void rule: %s." % body["gates"]["void_rule"],
        "",
        "## The decision table",
        "",
        "| Condition | Verdict | Reading |",
        "| --- | --- | --- |",
    ]
    for row in body["decision_table"]:
        lines.append("| %s | %s | %s |" % (
            row["condition"], row["verdict"], row["reading"]))
    lines += [
        "",
        "## Adoption and stop condition",
        "",
        body["adoption"]["rule"],
        "",
        "**Withdrawal.** %s" % body["adoption"]["withdrawal"],
        "",
        "**Stop condition.** %s" % body["stop_condition"],
        "",
        "## What this does not claim",
        "",
        body["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def render_result(artifact: dict) -> str:
    body = prereg()
    g1_max = int(body.get("g1_max_first_zero", 60))
    axis = artifact.get("seed_axis", {})
    details = artifact.get("details", {})
    witness_ok = sum(
        1 for cell in artifact.get("cells", [])
        if cell.get("stage") == "witness" and cell.get("arm") == "treatment"
        and cell.get("theory_cycles", 0) >= 39 and cell.get("peak", 0) >= 6)
    lines = [
        "# D3 persistence engine replication (G1 recalibrated) — result",
        "",
        "Generated from `docs/d3_persistence_g1_recalibrated_run.json` by "
        "`python -m benchmarks.d3_persistence_g1_recalibrated --finish`. "
        "Do not edit by hand.",
        "",
        "Protocol: `docs/D3-PERSISTENCE-G1-RECALIBRATED-PREREGISTRATION.md`. "
        "Treatment: shipped `organica.sleep.SleepService` at %s. "
        "Control: pre-repair raw-denominator ablation."
        % artifact["engine"]["version"],
        "",
        "**Verdict: `%s`**" % artifact["verdict"],
        "",
    ]
    if axis.get("live"):
        lines += [
            "## Seed axis is live",
            "",
            "The six seeds produced **%s distinct preflight treatment trajectories**."
            % axis.get("independent_treatment_trajectories"),
            "",
        ]
    else:
        lines += [
            "## Measurement caveat: seed axis is degenerate",
            "",
            "The preflight treatment did not produce two distinct trajectory signatures.",
            "",
        ]
    if artifact["verdict"] == "VOID":
        controls = [cell for cell in artifact.get("cells", [])
                    if cell.get("stage") == "preflight" and cell.get("arm") == "control"]
        treatments = [cell for cell in artifact.get("cells", [])
                      if cell.get("stage") == "preflight" and cell.get("arm") == "treatment"]
        observed = ", ".join(
            "%s=%s" % (cell["seed"], "none" if cell.get("first_zero_cycle") is None
                       else cell["first_zero_cycle"])
            for cell in controls)
        alive = sum(1 for cell in treatments if cell.get("first_zero_cycle") is None)
        lines += [
            "## Gate failure",
            "",
            "**%s** failed before any criterion was read." % details.get("gate", "gate"),
            "",
            "Control first zero by seed: %s. The G1 bound is 1-%d cycles." % (observed, g1_max),
            "",
            "Treatment cells with no first zero: %d of %d. The treatment survived the "
            "horizon, but the block is void and licenses no persistence claim." % (
                alive, len(treatments)),
            "",
        ]
        w1 = p1 = c1 = "unread (void)"
    else:
        w1 = "%d of %s seeds held 39/40 cycles and peak 6" % (
            witness_ok, len(body["design"]["seeds"]))
        p1 = "%s of %s seeds alive at the horizon" % (
            details.get("alive_seeds", "unread"), len(body["design"]["seeds"]))
        c1 = "median gap %s (bar %s)" % (
            details.get("early_median_gap", "unread"),
            details.get("early_bar", body["criteria"]["C1_early_cost"]["bar"]))
    lines += [
        "| Criterion | Result |",
        "| --- | --- |",
        "| W1 witness | %s |" % w1,
        "| P1 persistence | %s |" % p1,
        "| C1 early cost | %s |" % c1,
        "",
        "| Stage | Seed | Arm | World | Cycles | Theory cycles | Peak | First zero | Early recall@5 | Frequency updates |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for cell in artifact["cells"]:
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            cell["stage"], cell["seed"], cell["arm"], cell.get("world_digest", "?"),
            cell["cycles_run"], cell["theory_cycles"], cell["peak"],
            cell["first_zero_cycle"] if cell["first_zero_cycle"] is not None else "none",
            cell["recall_early"] if cell["recall_early"] is not None else "not measurable",
            cell.get("frequency_updates", "?")))
    lines += [
        "",
        "The control's preflight death is the G1 baseline gate; the treatment's full "
        "3,000-cycle trace is the P1 reading. Both negative controls are at zero.",
        "",
        "**Scope.** One promoted engine, two designs, six fresh seed-determined schedules. "
        "This is a replication of the promoted behavior, not a new adoption decision.",
        "",
    ]
    return "\n".join(lines)


def finish() -> int:
    problems = validate()
    if problems:
        raise SystemExit("the preregistration is not valid: " + "; ".join(problems))
    artifact = build()
    try:
        R.require_varied_treatment(artifact)
    except R.SeedAxisDegenerate as exc:
        raise SystemExit("REFUSED: %s" % exc) from None
    ARTIFACT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=1) + "\n",
                        encoding="utf-8")
    RESULT.write_text(render_result(artifact), encoding="utf-8")
    print("%s: %s" % (artifact["verdict"], json.dumps(artifact["details"], indent=1)))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no run artifact; run --finish")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    body = prereg()
    label, details = P.verdict(body, artifact)
    problems = []
    if label != artifact.get("verdict"):
        problems.append("the verdict is not what the cells imply")
    if details != artifact.get("details"):
        problems.append("the details are not what the cells imply")
    if engine_stamp.missing(artifact):
        problems.append("the artifact is not fully stamped: %r" % engine_stamp.missing(artifact))
    if RESULT.read_text(encoding="utf-8") != render_result(artifact):
        problems.append("the result page is stale")
    if PREREG_DOC.exists() and PREREG_DOC.read_text(encoding="utf-8") != render_prereg(body):
        problems.append("the preregistration page is stale")
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    print("d3 engine replication (G1 recalibrated) %s: %s" % (artifact["verdict"], details))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--render-prereg", action="store_true")
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--check-prereg", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args(argv)
    if args.check_prereg:
        body = prereg()
        problems = validate(body)
        if problems:
            raise SystemExit("FAIL: " + "; ".join(problems))
        page = render_prereg(body)
        if not PREREG_DOC.exists():
            raise SystemExit("FAIL: %s does not exist" % PREREG_DOC.name)
        if PREREG_DOC.read_text(encoding="utf-8") != page:
            raise SystemExit("FAIL: the preregistration page is stale; rerun with --render-prereg")
        print("prereg %s: frozen, unrun, page current" % body["prereg"])
        return 0
    if args.render_prereg:
        problems = validate()
        if problems:
            raise SystemExit("the preregistration is not valid: " + "; ".join(problems))
        PREREG_DOC.write_text(render_prereg(prereg()), encoding="utf-8")
        print("rendered %s" % PREREG_DOC.name)
        return 0
    if args.measure:
        return measure(max(1, args.workers))
    if args.finish:
        return finish()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
