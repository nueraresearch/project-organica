"""Does the primary scheme's partial final pass explain the ladder's non-monotonicity?

The A2 record showed the primary exposure scheme's Delta profile is not monotone
(0.0594, 0.0531, 0.0281, 0.0312, 0.1500) while the sensitivity scheme's rises through the
middle. `docs/DECISION-DENSITY-EXCLUSION.md` attributes the difference to the padding: the
primary stream is a base of length `2|W| + 24` cycled to exactly 400 events, so its final
pass is partial, ends inside the world-edge head at 0.1-0.6 and inside the filler tail only
at 0.8. This module tests that attribution instead of resting on it.

It adds a third exposure scheme, `whole_cycle` (the base repeated a whole number of times,
so every base position is exposed equally and the stream always ends on the filler tail),
and registers two criteria before any cell:

* **P1** every adjacent step of the mean Delta is >= 0.
* **P2** the advantage does not shrink from the sparse end to 0.6.

Registration: `docs/density_padding_prereg.json`, written before the run. The A2 block is
not amended: its two schemes, criteria and artifacts are untouched, and the seeds and
densities are inherited from it by reference so the comparison is paired.

    ./.venv/bin/python -m benchmarks.density_padding --write --run --score
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from statistics import mean

from benchmarks.density_worlds import (PRIMARY_CAP, RANKERS, TOTAL_EVENTS, base_stream,
                                       is_intra_cell, measure, stream, world_edges)
from benchmarks.run_density_interaction import run_pool
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "docs" / "density_padding_prereg.json"
RESULT = ROOT / "docs" / "density_padding_result.json"
RUN = ROOT / "docs" / "density_padding_run.json"
DOC = ROOT / "docs" / "DENSITY-PADDING-PREREGISTRATION.md"
A2_PREREG = ROOT / "docs" / "density_interaction_a2_prereg.json"
A2_RESULT = ROOT / "docs" / "density_interaction_a2_result.json"

SCHEME = "whole_cycle"
FILLER = "constant"
ARMS = ("control", "intra_cell_excluded")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def _load(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def seeds_and_densities(a2_path: Path = A2_PREREG) -> tuple[list[int], list[float]]:
    """Inherit the registered A2 grid by reference: same worlds, paired cells."""
    design = _load(a2_path)["design"]
    seeds = [int(s) for s in design["seeds"]]
    for key in ("densities", "rhos", "rho_ladder", "density_ladder"):
        if key in design:
            return seeds, [float(r) for r in design[key]]
    raise SystemExit("the A2 registration carries no density ladder under a known key")


def totals() -> dict[str, int]:
    """Events per density under whole-cycle padding: base length times whole passes."""
    seeds, densities = seeds_and_densities()
    out = {}
    for rho in densities:
        base = len(base_stream(seeds[0], rho, FILLER))
        out["%.1f" % rho] = base * math.ceil(TOTAL_EVENTS / base)
    return out


def registration() -> dict:
    seeds, densities = seeds_and_densities()
    return {
        "prereg": "DENSITY-PADDING-1",
        "title": "Does the primary scheme's partial final pass explain the density ladder's non-monotonicity?",
        "status": "REGISTERED",
        "date": "2026-11-07",
        "amends": None,
        "question": (
            "The A2 record shows the primary scheme's advantage is not monotone across the "
            "ladder while the sensitivity scheme's rises. The decision record attributes this "
            "to the primary scheme's partial final pass. If that attribution is right, a scheme "
            "that pads in whole cycles should have a monotone ladder."),
        "inherits": {
            "seeds": "docs/density_interaction_a2_prereg.json:design.seeds",
            "densities": "docs/density_interaction_a2_prereg.json:design.densities",
            "cap": PRIMARY_CAP,
            "filler": FILLER,
            "world": "benchmarks/density_worlds.py, unchanged for the registered schemes",
        },
        "scheme": {
            "name": SCHEME,
            "definition": (
                "the base stream (world edges in sorted order, then the within-cell filler) "
                "repeated ceil(TOTAL_EVENTS / len(base)) times, so every base occurrence is "
                "emitted the same number of times and the stream always ends on the filler tail"),
            "totals": totals(),
            "why_not_fixed_total": (
                "holding total exposure at 400 events is exactly what forces a partial final "
                "pass, so this scheme removes the phase by letting the total vary"),
        },
        "endpoint": "precision at cap %d; Delta = treated precision - control precision" % PRIMARY_CAP,
        "criteria": {
            "P1_every_step_non_negative": {
                "judged": True,
                "definition": "for every adjacent pair in the ladder, mean Delta(next) - mean Delta(current) >= 0",
            },
            "P2_does_not_shrink": {
                "judged": True,
                "definition": "mean Delta(0.6) >= mean Delta(0.1)",
            },
        },
        "gate": {
            "name": "phase_neutral",
            "definition": (
                "at every density each base occurrence appears exactly `passes` times, the last "
                "event is a filler event, and len(stream) == passes * len(base)"),
        },
        "negative_control": (
            "P1 applied to the registered A2 primary profile must return not monotone; a "
            "criterion that cannot fire on the profile it was written for is decoration"),
        "decision_table": {
            "monotone": (
                "the padding phase explains the mid-ladder dip: report the primary ladder as an "
                "instrument property in the decision record and quote the whole-cycle profile as "
                "the phase-free reading"),
            "not_monotone": (
                "the padding phase is not the whole story: name the failing step and the class "
                "that holds the budget there, and stop attributing the ladder to padding alone"),
        },
        "not_claimed": [
            "no cognitive or behavioural claim: the endpoint is a selection reading",
            "no claim about exposure in general: the scheme varies total exposure with density",
            "no amendment to A2: its schemes, criteria and artifacts are unchanged",
        ],
        "run": None,
    }


def write_registration() -> None:
    if PREREG.exists():
        raise SystemExit("the registration is already committed; do not rewrite it")
    if RUN.exists() or RESULT.exists():
        raise SystemExit("cells or results exist without a registration")
    body = registration()
    PREREG.write_text(json.dumps(engine_stamp.stamp(body), indent=2) + "\n", encoding="utf-8")
    DOC.write_text(render_document(body), encoding="utf-8")
    print("registered %s" % body["prereg"])


# ---------------------------------------------------------------------------
# Gate and cells
# ---------------------------------------------------------------------------

def phase_gate() -> dict:
    """The scheme must be phase-neutral, and the primary scheme must fail this check."""
    seeds, densities = seeds_and_densities()
    rows = []
    for rho in densities:
        base = base_stream(seeds[0], rho, FILLER)
        passable = len(stream(seeds[0], rho, SCHEME, FILLER))
        passes = math.ceil(TOTAL_EVENTS / len(base))
        counts = Counter(stream(seeds[0], rho, SCHEME, FILLER))
        base_counts = Counter(base)
        equal = len(counts) == len(base_counts) and all(
            counts[text] == base_counts[text] * passes for text in base_counts)
        ends_filler = len(stream(seeds[0], rho, SCHEME, FILLER)[-1].split()) == 4
        rows.append({"rho_world": rho, "base": len(base), "passes": passes,
                     "events": passable, "equal_exposure": bool(equal),
                     "ends_on_filler": bool(ends_filler),
                     "passed": bool(equal and ends_filler
                                    and passable == passes * len(base))})
    primary = Counter(stream(seeds[0], 0.4, "primary", FILLER))
    primary_base = Counter(base_stream(seeds[0], 0.4, FILLER))
    ratios = {primary[text] / primary_base[text] for text in primary_base}
    return {
        "scheme": SCHEME,
        "rows": rows,
        "passed": all(row["passed"] for row in rows),
        "primary_control": {
            "rho_world": 0.4,
            "distinct_exposure_ratios": sorted(ratios),
            "passed": len(ratios) == 1,
        },
    }


def cells_for(seed: int, rho: float, pool, world: set) -> list[dict]:
    out = []
    for arm in ARMS:
        selected = RANKERS[arm](pool, PRIMARY_CAP)
        stats = measure(pool, world, selected)
        out.append({
            "seed": int(seed), "rho_world": float(rho), "scheme": SCHEME, "arm": arm,
            "cap": PRIMARY_CAP, "precision": stats["precision"],
            "covered": stats["covered"], "asserted": stats["asserted"],
            "presence": stats["presence"], "rho_rank": stats["rho_rank"],
            "pool_rows": stats["pool_rows"],
            "pool_intra_cell_rows": stats["pool_intra_cell_rows"],
            "selected": ["%s>%s" % pair for pair in selected],
        })
    return out


def _choose(text: str | None, seeds: list[int]) -> list[int]:
    """A contiguous index slice of the inherited seeds: `0-3`, or one index."""
    if not text:
        return list(seeds)
    lo, _, hi = text.partition("-")
    start = int(lo)
    stop = int(hi) + 1 if hi else int(lo) + 1
    chosen = seeds[start:stop]
    if not chosen:
        raise SystemExit("the seed slice %r selects nothing" % (text,))
    return chosen


def run(seed_slice: str | None = None, append: bool = False) -> dict:
    """Execute the chosen seeds. Slices exist because 80 engine pools exceed one sitting."""
    if RESULT.exists():
        raise SystemExit("a result exists; this registration has already been scored")
    body = _load(PREREG)
    if body["status"] not in ("REGISTERED", "RUNNING"):
        raise SystemExit("the registration is not open: %r" % (body["status"],))
    gate = phase_gate()
    if not gate["passed"]:
        raise SystemExit("the phase gate failed; the scheme is not phase-neutral: %r" % gate["rows"])
    if gate["primary_control"]["passed"]:
        raise SystemExit("the gate cannot fire: the primary stream is already phase-neutral")
    seeds, densities = seeds_and_densities()
    chosen = _choose(seed_slice, seeds)
    cells: list[dict] = []
    slices: list[list[int]] = []
    if append and RUN.exists():
        prior = _load(RUN)
        cells = list(prior["cells"])
        slices = list(prior.get("slices", []))
        already = {int(c["seed"]) for c in cells}
        if already & set(chosen):
            raise SystemExit("these seeds are already in the run: %r" % (sorted(already & set(chosen)),))
    for seed in chosen:
        for rho in densities:
            pool = run_pool(seed, rho, SCHEME, FILLER)["pool"]
            cells.extend(cells_for(seed, rho, pool, world_edges(seed, rho)))
    slices.append(chosen)
    covered = sorted({int(c["seed"]) for c in cells})
    if len(cells) != len(covered) * len(densities) * 2:
        raise SystemExit("the run is ragged: %d cells for %d seeds" % (len(cells), len(covered)))
    complete = covered == sorted(seeds)
    payload = {
        "prereg": body["prereg"], "scheme": SCHEME, "filler": FILLER,
        "cells": cells, "gate": gate,
        "slices": slices, "seeds_complete": covered,
        "densities": densities,
        "provenance": {"runner": "benchmarks/density_padding.py",
                       "engine": "frozen v1 via benchmarks.run_density_interaction.run_pool"},
    }
    RUN.write_text(json.dumps(engine_stamp.stamp(payload), indent=2) + "\n", encoding="utf-8")
    body["status"] = "RUN" if complete else "RUNNING"
    body["run"] = {"cells": len(cells), "seeds": len(covered), "of_seeds": len(seeds),
                   "densities": len(densities), "gate_passed": True,
                   "artifact": "docs/density_padding_run.json",
                   "slices": len(slices)}
    PREREG.write_text(json.dumps(engine_stamp.stamp(body), indent=2) + "\n", encoding="utf-8")
    print("%d cells written (%d of %d seeds)" % (len(cells), len(covered), len(seeds)))
    return payload


# ---------------------------------------------------------------------------
# Score
# ---------------------------------------------------------------------------

def _delta(cells: list[dict], rho: float) -> dict[int, float]:
    index = {(c["arm"], round(c["rho_world"], 6), c["seed"]): c for c in cells}
    seeds = sorted({c["seed"] for c in cells})
    return {s: index[("intra_cell_excluded", rho, s)]["precision"]
            - index[("control", rho, s)]["precision"] for s in seeds}


def score() -> dict:
    body = _load(PREREG)
    if body["status"] != "RUN":
        raise SystemExit("nothing to score: the registration has not run")
    cells = _load(RUN)["cells"]
    seeds, densities = seeds_and_densities()
    index = {(c["arm"], round(c["rho_world"], 6), c["seed"]): c for c in cells}
    profile, slots = {}, {}
    for rho in densities:
        d = _delta(cells, rho)
        profile["%.1f" % rho] = {
            "delta_mean": round(mean(d.values()), 6),
            "control_mean": round(mean(index[("control", rho, s)]["precision"] for s in seeds), 6),
            "treated_mean": round(mean(index[("intra_cell_excluded", rho, s)]["precision"]
                                       for s in seeds), 6),
            "seeds_positive": sum(1 for s in seeds if d[s] > 0),
            "of": len(seeds),
        }
        s_intra = s_cross = t_cross = 0.0
        for seed in seeds:
            world = world_edges(seed, rho)
            for row in index[("control", rho, seed)]["selected"]:
                a, b = row.split(">")
                if (a, b) in world:
                    continue
                if is_intra_cell(a, b):
                    s_intra += 1
                else:
                    s_cross += 1
            for row in index[("intra_cell_excluded", rho, seed)]["selected"]:
                a, b = row.split(">")
                if (a, b) not in world:
                    t_cross += 1
        slots["%.1f" % rho] = {
            "control_intra": round(s_intra / len(seeds), 4),
            "control_cross": round(s_cross / len(seeds), 4),
            "treated_cross": round(t_cross / len(seeds), 4),
        }
    steps = []
    for left, right in zip(densities, densities[1:]):
        step = profile["%.1f" % right]["delta_mean"] - profile["%.1f" % left]["delta_mean"]
        steps.append({"from": left, "to": right, "step": round(step, 6)})
    p1 = all(step["step"] >= 0 for step in steps)
    p2 = profile["%.1f" % 0.6]["delta_mean"] >= profile["%.1f" % 0.1]["delta_mean"]

    a2 = _load(A2_RESULT)["criteria"]["profile"]
    primary_a2 = {rho: a2["%.1f" % rho]["primary"]["delta_precision_mean"] for rho in densities}
    a2_steps = [primary_a2[b] - primary_a2[a] for a, b in zip(densities, densities[1:])]
    control = {"profile": "A2 primary", "steps": [round(s, 6) for s in a2_steps],
               "P1_passed": all(s >= 0 for s in a2_steps)}

    if p1 and p2:
        verdict = "WHOLE-CYCLE PADDING RESTORES A MONOTONE LADDER"
        reading = ("the partial final pass is the whole of the mid-ladder dip; the primary "
                   "profile reports its own padding phase, and the phase-free scheme rises")
    else:
        failing = [step for step in steps if step["step"] < 0]
        verdict = "WHOLE-CYCLE PADDING DOES NOT RESTORE A MONOTONE LADDER"
        reading = ("the padding phase is not the whole story; the failing step is %s"
                   % (", ".join("%.1f->%.1f (%.4f)" % (s["from"], s["to"], s["step"])
                                for s in failing) or "P2"))
    result = {
        "prereg": body["prereg"], "scheme": SCHEME, "cells": len(cells),
        "profile": profile,
        "slots": slots,
        "steps": steps,
        "criteria": {
            "P1": {"judged": True, "passed": bool(p1),
                   "definition": body["criteria"]["P1_every_step_non_negative"]["definition"]},
            "P2": {"judged": True, "passed": bool(p2),
                   "definition": body["criteria"]["P2_does_not_shrink"]["definition"]},
        },
        "negative_control": control,
        "decision": {"verdict": verdict, "reading": reading,
                     "monotone": bool(p1 and p2)},
        "gate_passed": True,
        "provenance": {"cells": "docs/density_padding_run.json",
                       "prereg": "docs/density_padding_prereg.json",
                       "a2": "docs/density_interaction_a2_result.json"},
    }
    RESULT.write_text(json.dumps(engine_stamp.stamp(result), indent=2) + "\n", encoding="utf-8")
    DOC.write_text(render_document(body, result), encoding="utf-8")
    print(verdict)
    return result


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render(body: dict, result: dict | None = None) -> str:
    scheme = body["scheme"]
    lines = [
        "# Density padding: does the partial final pass explain the ladder?",
        "",
        "**Pre-registration**: `%s`. **Status**: %s. **Date**: %s." % (
            body["prereg"], body["status"], body["date"]),
        "",
        "**Inherited grid**: seeds and densities by reference from `docs/density_interaction_a2_prereg.json`,",
        "cap %d, filler `%s`. The A2 block is **not** amended: its schemes, criteria and artifacts are" % (
            body["inherits"]["cap"], body["inherits"]["filler"]),
        "untouched, and this block adds one scheme.",
        "",
        "## 1. Question",
        "",
        body["question"],
        "",
        "## 2. The third scheme",
        "",
        "`%s`: %s." % (scheme["name"], scheme["definition"]),
        "",
        "Events per density: " + ", ".join(
            "%.1f = %d" % (float(rho), count) for rho, count in scheme["totals"].items()) + ".",
        "",
        "Why the total is not held fixed: %s." % scheme["why_not_fixed_total"],
        "",
        "## 3. Endpoint",
        "",
        body["endpoint"] + ".",
        "",
        "## 4. Gate",
        "",
        "`%s`: %s. The gate is checked before any cell runs, and the primary stream is put"
        % (body["gate"]["name"], body["gate"]["definition"]),
        "through the same check as a negative control: if the primary stream is already phase-neutral,",
        "the gate cannot fire and the run is refused.",
        "",
        "## 5. Criteria",
        "",
        "- **P1**: %s." % body["criteria"]["P1_every_step_non_negative"]["definition"],
        "- **P2**: %s." % body["criteria"]["P2_does_not_shrink"]["definition"],
        "",
        "Both are judged, and the block passes only if both hold. The rule is exact rather than",
        "tolerance-based because the question is qualitative: a negative step means the ladder is not",
        "monotone, whatever its size.",
        "",
        "## 6. Decision table",
        "",
        "- **Monotone**: %s." % body["decision_table"]["monotone"],
        "- **Not monotone**: %s." % body["decision_table"]["not_monotone"],
        "",
        "## 7. Not claimed",
        "",
    ]
    lines += ["- %s." % item for item in body["not_claimed"]]
    if result is not None:
        profile = result["profile"]
        lines += [
            "",
            "## 8. Result",
            "",
            "**%s.** %s." % (result["decision"]["verdict"], result["decision"]["reading"]),
            "",
            "Cells: %d. Slots are means over the inherited seeds; the phase gate %s." % (
                result["cells"], "passed" if result["gate_passed"] else "failed"),
            "",
            "| rho | control | treated | Delta | seeds positive |",
            "| --- | --- | --- | --- | --- |",
        ]
        for rho in profile:
            row = profile[rho]
            lines.append("| %s | %.4f | %.4f | %.4f | %d of %d |" % (
                rho, row["control_mean"], row["treated_mean"], row["delta_mean"],
                row["seeds_positive"], row["of"]))
        lines += [
            "",
            "Slots in the cap-20 selection (means over the inherited seeds). The treated arm cannot",
            "hold an intra-cell row by construction, so its non-world slots are all cross-cell:",
            "",
            "| rho | control intra-cell | control cross-cell non-world | treated cross-cell non-world |",
            "| --- | --- | --- | --- |",
        ]
        for rho, row in result["slots"].items():
            lines.append("| %s | %.2f | %.2f | %.2f |" % (
                rho, row["control_intra"], row["control_cross"], row["treated_cross"]))
        lines += ["", "Adjacent steps:", ""]
        lines += ["- %.1f -> %.1f: %+.4f" % (s["from"], s["to"], s["step"]) for s in result["steps"]]
        lines += [
            "",
            "Criteria: P1 %s, P2 %s. Negative control: the same P1 on the A2 primary profile returns %s,"
            % ("**passed**" if result["criteria"]["P1"]["passed"] else "**failed**",
               "**passed**" if result["criteria"]["P2"]["passed"] else "**failed**",
               "passed (the criterion cannot fire)" if result["negative_control"]["P1_passed"]
               else "not monotone, as it must"),
            "so the check is known to be able to fail on the profile it was written for.",
        ]
    return "\n".join(lines) + "\n"


def render_document(body: dict, result: dict | None = None) -> str:
    return render(body, result)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the registration and its document")
    parser.add_argument("--run", action="store_true", help="execute the cells")
    parser.add_argument("--score", action="store_true", help="score and render the result")
    parser.add_argument("--seeds", default=None, help="index slice of the inherited seeds, e.g. 0-3")
    parser.add_argument("--append", action="store_true", help="append to an existing partial run")
    args = parser.parse_args(argv)
    if not any((args.write, args.run, args.score)):
        parser.print_help()
        return 2
    if args.write:
        write_registration()
    if args.run:
        run(args.seeds, args.append)
    if args.score:
        score()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
