"""Whether a `pruned` edge death can happen, and what the record's silence means.

`docs/DECAY-ATTRIBUTION.md` reports the fourth death reason as
`pruned (not re-emitted, x0.8 under 0.15) | not measurable`, beside `decayed 0.6897` and
`below_threshold 0.3103`. Those two numbers are read as the finding that decay dominates and
pruning does not participate. This module measures whether that reading is licensed.

It is not, and the reason is arithmetic rather than empirical. The attribution ledger follows
an edge from one cycle to the next only while the edge is *stable*: `previous = stable` at the
end of every cycle in `benchmarks/decay_attribution.py`. A stable edge therefore has a strength
of at least `STABLE_THRESHOLD` (0.30), one step of `DEATH_FACTOR` (x0.8) lands at 0.24, and the
pruning branch needs the result to be under `DEATH_THRESHOLD` (0.15) — which needs the input to
be under 0.1875, below the stable threshold the ledger starts from. So the branch cannot fire
from any edge the ledger follows, on any run, in any world. It is not a measured zero and it is
not "not measurable": it is a structural zero, and the fourth category was never observed
because the instrument stops before it.

Meanwhile the engine does prune. `_natural_selection` stores a candidate below the death
threshold as a retired record, and the per-cycle report counts it; the same parts that produced
the 0 in the ledger recorded thousands of prunings. So the honest statement is narrower than
the published one: **decay of strength across 0.30 is what the edge layer's deaths are made of,
and pruning is a later stage of the same process that the ledger stops short of watching.**

What this module does, and what it refuses to do:

* it reads the two thresholds and the factor from the engine rather than typing them, and it
  proves the branch unreachable from a stable edge;
* it drives the ledger's own `_reason` down a decaying chain and shows the branch firing at the
  step the ledger never reaches (four steps, on the shipped constants), so the rule is proved
  live and the silence is proved to be the window's;
* it sums the engine's own pruning counter and the ledger's reasons from the committed parts,
  so the contrast is measured on the run that produced the published numbers rather than on a
  new one;
* it refuses to restamp or rewrite `docs/decay_attribution.json`. That artifact is not wrong;
  the interpretation placed on one of its cells is. The correction is this record plus the
  documented reading, not a rebuilt result.

    ./.venv/bin/python -m benchmarks.pruning_reachability --measure
    ./.venv/bin/python -m benchmarks.pruning_reachability --render
    ./.venv/bin/python -m benchmarks.pruning_reachability --check
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks.decay_attribution import _reason
from organica.sleep import SleepService

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PARTS = DOCS / "decay_attribution" / "parts"
ARTIFACT = DOCS / "pruning_reachability.json"
DOC = DOCS / "PRUNING-REACHABILITY.md"

ARMS = ("engine", "no_temporal_decay")

#: The engine's selection factor for a candidate that is not re-emitted. Read from the class
#: when it is named there; the literal is what `_natural_selection` applies.
FACTOR = float(getattr(SleepService, "DEATH_FACTOR", 0.8))
FACTOR_SOURCE = ("SleepService.DEATH_FACTOR" if hasattr(SleepService, "DEATH_FACTOR")
                 else "the 0.8 literal in SleepService._natural_selection")

NO_BRANCH = "UNREACHABLE_IN_THE_LEDGER"
LIVE = "LIVE_IN_THE_ENGINE"


def thresholds() -> tuple[float, float]:
    return float(SleepService.STABLE_THRESHOLD), float(SleepService.DEATH_THRESHOLD)


def arithmetic(stable: float, death: float, factor: float) -> dict:
    """The bound that makes the branch unreachable, and the input it would need.

    The ledger judges an edge on the step from `prior_strength` to `prior_strength * factor`,
    and `prior_strength` is at least `stable` because the edge was stable when it was followed.
    The branch fires when the product is under `death`, which requires `prior_strength` under
    `death / factor`. The two conditions cannot both hold, and the module states the margin
    rather than the conclusion alone.
    """
    one_step = stable * factor
    required_prior = death / factor
    return {
        "stable_threshold": stable,
        "death_threshold": death,
        "factor": factor,
        "one_step_from_a_threshold_edge": round(one_step, 6),
        "input_the_branch_would_need": round(required_prior, 6),
        "margin_above_the_branch": round(one_step - death, 6),
        "unreachable_from_a_stable_edge": one_step >= death,
        "the_required_input_is_below_the_stable_threshold": required_prior < stable,
    }


def trace(stable: float, death: float, factor: float) -> list[dict]:
    """Drive the ledger's own `_reason` down a decaying edge until the branch fires.

    The chain starts at the stable threshold, because that is the weakest edge the ledger can
    be following when it makes a judgement, and applies the engine's factor step by step. The
    first step is the only one the ledger takes; the rest are what it never sees.
    """
    steps = []
    strength = stable
    for step in range(1, 12):
        reason = _reason(("alpha", "beta"), strength, {}, stable, death)
        steps.append({
            "step": step,
            "prior_strength": round(strength, 6),
            "after_decay": round(strength * factor, 6),
            "reason": reason,
        })
        if reason == "pruned":
            break
        strength = strength * factor
    return steps


def ledger_observation() -> dict:
    """What the committed parts recorded, by arm: the ledger's reasons and the engine's counters.

    Both come from the same cells, so the contrast is not two runs compared: it is two
    instruments reading one run. The engine's counter is over every surviving candidate type,
    not only prediction edges, and the record says so because the counter cannot be split.
    """
    out = {}
    for arm in ARMS:
        reasons: Counter = Counter()
        counters: Counter = Counter()
        cloud = Counter()
        cells = []
        for path in sorted(PARTS.glob("cell_%s_s*.json" % arm)):
            data = json.loads(path.read_text(encoding="utf-8"))
            cells.append(data.get("seed"))
            for row in data.get("series") or []:
                for name, value in (row.get("by_reason") or {}).items():
                    reasons[name] += int(value)
                for name in ("strengthened", "decayed", "pruned"):
                    counters[name] += int(row.get(name) or 0)
                if int(row.get("pruned") or 0):
                    cloud["cycles_with_a_pruning"] += 1
                    cloud["first_cycle_with_a_pruning"] = cloud.get(
                        "first_cycle_with_a_pruning") or row.get("cycle")
        out[arm] = {
            "seeds": cells,
            "ledger_edge_deaths": dict(sorted(reasons.items())),
            "engine_candidate_counters": dict(sorted(counters.items())),
            "pruning": dict(cloud),
        }
        cycles = 0
        for path in sorted(PARTS.glob("cell_%s_s*.json" % arm)):
            cycles = max(cycles, len(json.loads(path.read_text(encoding="utf-8")).get("series") or []))
        out[arm]["cycles"] = cycles
    return out


def measure() -> dict:
    stable, death = thresholds()
    bound = arithmetic(stable, death, FACTOR)
    steps = trace(stable, death, FACTOR)
    observed = ledger_observation()
    engine = observed["engine"]

    gates = {
        "G1_branch_unreachable_from_a_stable_edge": bound["unreachable_from_a_stable_edge"],
        "G2_branch_fires_when_followed_below_the_threshold": any(
            step["reason"] == "pruned" for step in steps),
        "G3_the_engine_recorded_prunings": engine["engine_candidate_counters"].get("pruned", 0) > 0,
        "G4_the_ledger_recorded_no_pruned_edge_death": (
            engine["ledger_edge_deaths"].get("pruned", 0) == 0),
        "G5_the_thresholds_came_from_the_engine": (
            stable > death > 0 and bound["one_step_from_a_threshold_edge"] == round(stable * FACTOR, 6)),
    }
    return {
        "kind": "pruning_reachability",
        "date": "2026-11-09",
        "factor_source": FACTOR_SOURCE,
        "bound": bound,
        "trace": steps,
        "steps_the_ledger_takes": 1,
        "steps_to_the_branch": next(
            (step["step"] for step in steps if step["reason"] == "pruned"), None),
        "observed": observed,
        "gates": gates,
        "label": (NO_BRANCH if all(gates.values()) else "UNEXPLAINED"),
    }


def _fmt(value) -> str:
    return "n/a" if value is None else ("%s" % value)


def render(artifact: dict) -> str:
    bound = artifact["bound"]
    engine = artifact["observed"]["engine"]
    control = artifact["observed"]["no_temporal_decay"]
    reasons = engine["ledger_edge_deaths"]
    total = sum(reasons.values())
    lines = [
        "# Can a `pruned` edge death happen? — measurement",
        "",
        "Generated from `docs/pruning_reachability.json` by",
        "`python -m benchmarks.pruning_reachability --render`. Do not edit by hand.",
        "",
        "## Label",
        "",
        "**%s**" % artifact["label"],
        "",
        "The branch is unreachable from any edge the attribution ledger follows, and the engine",
        "prunes on the same run. The record's fourth category was never observed because the",
        "instrument stops at the stable threshold, not because the mechanism is absent.",
        "",
        "## The arithmetic",
        "",
        "The ledger judges an edge on the step from a strength to `strength x %s`, and it only"
        % _fmt(bound["factor"]),
        "judges an edge that was stable last cycle:", "",
        "| Quantity | Value |",
        "| --- | --- |",
        "| Stable threshold (read from the engine) | %s |" % _fmt(bound["stable_threshold"]),
        "| Death threshold (read from the engine) | %s |" % _fmt(bound["death_threshold"]),
        "| Factor | %s, from %s |" % (_fmt(bound["factor"]), artifact["factor_source"]),
        "| Weakest stable edge, after one step | %s |"
        % _fmt(bound["one_step_from_a_threshold_edge"]),
        "| Strength the pruning branch would need | %s |"
        % _fmt(bound["input_the_branch_would_need"]),
        "| Margin above the branch | %s |" % _fmt(bound["margin_above_the_branch"]),
        "",
        "So the branch needs an input below the threshold at which the edge counts as stable. That",
        "is not a property of this world, this seed or this build; it holds for every edge the",
        "ledger is able to follow.",
        "",
        "## The branch, driven by the ledger's own rule",
        "",
        "| Step | Prior strength | After decay | Reason the ledger assigns |",
        "| --- | --- | --- | --- |",
    ]
    for step in artifact["trace"]:
        lines.append("| %d | %s | %s | `%s` |" % (
            step["step"], _fmt(step["prior_strength"]), _fmt(step["after_decay"]),
            step["reason"]))
    lines += [
        "",
        "The ledger takes step **%d** and stops; the branch fires at step **%s**. The rule is"
        % (artifact["steps_the_ledger_takes"], _fmt(artifact["steps_to_the_branch"])),
        "live, and the silence is the window's.",
        "",
        "## What the same 300 cycles recorded",
        "",
        "| Quantity | Engine arm | No-decay control |",
        "| --- | --- | --- |",
        "| Seeds | %d | %d |" % (len(engine["seeds"]), len(control["seeds"])),
        "| Cycles per seed | %s | %s |" % (_fmt(engine["cycles"]), _fmt(control["cycles"])),
        "| Ledger edge deaths | %d | %d |"
        % (total, sum(control["ledger_edge_deaths"].values())),
        "| Of those, `pruned` | %d | %d |"
        % (reasons.get("pruned", 0), control["ledger_edge_deaths"].get("pruned", 0)),
        "| Engine candidates strengthened | %s | %s |"
        % (_fmt(engine["engine_candidate_counters"].get("strengthened")),
           _fmt(control["engine_candidate_counters"].get("strengthened"))),
        "| Engine candidates decayed | %s | %s |"
        % (_fmt(engine["engine_candidate_counters"].get("decayed")),
           _fmt(control["engine_candidate_counters"].get("decayed"))),
        "| Engine candidates pruned | %s | %s |"
        % (_fmt(engine["engine_candidate_counters"].get("pruned")),
           _fmt(control["engine_candidate_counters"].get("pruned"))),
        "| Cycles with at least one pruning | %s | %s |"
        % (_fmt(engine["pruning"].get("cycles_with_a_pruning")),
           _fmt(control["pruning"].get("cycles_with_a_pruning"))),
        "",
        "## What this changes",
        "",
        "- **`decayed 0.6897` and `below_threshold 0.3103` are statements about strength crossing",
        "  the stable threshold.** They are not a comparison between decay and pruning, because",
        "  pruning is not on the instrument's axis.",
        "- **`pruned | not measurable` should read `unreachable in this ledger`.** A structural zero",
        "  and an unmeasured quantity are different claims, and the published cell does not say",
        "  which one it is.",
        "- **Pruning is live in the engine** on the run that produced the published numbers. It is a",
        "  later stage of the same decay process the ledger does watch: an edge that crosses 0.30 is",
        "  classified `decayed`, and the candidate it belongs to is retired when it reaches 0.15.",
        "",
        "## What this does not establish",
        "",
        "- **The engine's counter is not split by candidate type.** It counts every surviving",
        "  generation, so it shows that pruning happens, not how much of it is prediction edges.",
        "- **No published artifact is restamped or rewritten.** The attribution result stands; the",
        "  interpretation placed on one of its cells is what this record corrects.",
        "- **It runs no cell.** Every number above is read from artifacts already committed, apart",
        "  from the trace, which is the ledger's rule applied to a constructed chain.",
        "",
    ]
    return "\n".join(lines)


def check(artifact: dict | None = None) -> list:
    artifact = artifact or json.loads(ARTIFACT.read_text(encoding="utf-8"))
    fresh = measure()
    problems = []
    for key in ("bound", "trace", "observed", "gates", "label"):
        if artifact.get(key) != fresh.get(key):
            problems.append("%s disagrees with a fresh measurement" % key)
    failing = [name for name, value in fresh["gates"].items() if not value]
    if failing:
        problems.append("gates fail: %s" % ", ".join(sorted(failing)))
    if not ARTIFACT.exists():
        problems.append("%s does not exist" % ARTIFACT.name)
    elif ARTIFACT.read_text(encoding="utf-8").strip() != json.dumps(artifact, indent=2).strip():
        problems.append("%s is not in the recorded form" % ARTIFACT.name)
    if not DOC.exists():
        problems.append("%s does not exist" % DOC.name)
    elif DOC.read_text(encoding="utf-8") != render(artifact):
        problems.append("%s is stale" % DOC.name)
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measure", action="store_true", help="measure and write the artifact")
    parser.add_argument("--render", action="store_true", help="render the page from the artifact")
    parser.add_argument("--check", action="store_true", help="validate without writing")
    args = parser.parse_args(argv)

    if args.check:
        problems = check()
        if problems:
            for problem in problems:
                print("FAIL:", problem)
            return 1
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        print("pruning reachability: %s, %d prune(s) recorded by the engine, %d by the ledger"
              % (artifact["label"],
                 artifact["observed"]["engine"]["engine_candidate_counters"].get("pruned", 0),
                 artifact["observed"]["engine"]["ledger_edge_deaths"].get("pruned", 0)))
        return 0

    if args.render:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        DOC.write_text(render(artifact), encoding="utf-8")
        print("rendered", DOC.name)
        return 0

    artifact = engine_stamp.stamp(measure())
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    DOC.write_text(render(artifact), encoding="utf-8")
    print("pruning reachability: %s -> %s" % (artifact["label"], ARTIFACT.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
