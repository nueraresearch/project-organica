"""Q006's pinned-engine admission re-derivation.

The protocol is `docs/Q006-ADMISSION-RE-DERIVATION-PREREGISTRATION.md`. The
reference arm is `SleepService`; the adopted arm is restored here because
`organica/admission.py` was deleted at withdrawal. Candidate construction,
eligibility, strengths and the cap remain the engine's own: the subclass
changes only the Layer-1 ordering, exactly as the withdrawn module did.

    ./.venv/bin/python -m benchmarks.q006_admission_rederivation --run
    ./.venv/bin/python -m benchmarks.q006_admission_rederivation --check
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks.acquisition_harness import gate_acquisition_sufficiency

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "docs" / "q006_admission_rederivation_prereg.json"
ARTIFACT = ROOT / "docs" / "q006_admission_rederivation.json"
PAGE = ROOT / "docs" / "Q006-ADMISSION-RE-DERIVATION-RESULT.md"

FROZEN = ("organica/sleep.py", "organica/memory.py", "organica/paths.py",
          "organica/streams.py", "organica/branch_streams.py",
          "organica/scale_streams.py", "organica/ground_truth_worlds.py")


# ---------------------------------------------------------------------------
# The withdrawn arm, restored in-process from a82e890
# ---------------------------------------------------------------------------

from organica.sleep import PredictionCandidate, SleepService  # noqa: E402

COUNT = "count"
DIVERSITY = "diversity"


def _count(candidate: PredictionCandidate) -> int:
    return int(candidate.evidence.get("temporal_count", 0))


def effective_cap(cap: int, eligible_sources: int, policy: str = DIVERSITY) -> int:
    if policy == COUNT:
        return int(cap)
    return max(int(cap), int(eligible_sources))


def rank(predictions: list[PredictionCandidate], k: int,
         policy: str = DIVERSITY) -> list[PredictionCandidate]:
    """The withdrawn module's rule: count for the reference, diversity for the arm."""
    k = int(k)
    if k <= 0:
        return []
    if policy == COUNT:
        return sorted(predictions, key=lambda p: -_count(p))[:k]
    remaining = sorted(predictions, key=lambda p: (-_count(p), p.source, p.target))
    per_source: dict[str, int] = {}
    chosen: list[PredictionCandidate] = []
    while remaining and len(chosen) < k:
        best = min(remaining, key=lambda p: (per_source.get(p.source, 0),
                                             -_count(p), p.source, p.target))
        chosen.append(best)
        per_source[best.source] = per_source.get(best.source, 0) + 1
        remaining.remove(best)
    return chosen


class DiversityFirstSleepService(SleepService):
    """The adopted ordering, restored without touching the frozen engine.

    Under COUNT this delegates to the engine; under DIVERSITY it ranks the
    engine's eligible pool by fewest already-admitted outgoing edges per
    source. Candidate construction, the minimum count, strengths and the cap
    stay the engine's own.
    """

    admission_policy = DIVERSITY
    _POOL_PROBE = 1_000_000

    def _build_predictions(self, temporal, freqs, prior_schemas=None):
        if self.admission_policy == COUNT:
            return super()._build_predictions(temporal, freqs, prior_schemas)
        cap = self.MAX_PREDICTIONS
        try:
            self.MAX_PREDICTIONS = self._POOL_PROBE
            pool = list(super()._build_predictions(temporal, freqs, prior_schemas))
        finally:
            self.MAX_PREDICTIONS = cap
        eligible_sources = len({p.source for p in pool})
        budget = effective_cap(cap, eligible_sources, self.admission_policy)
        return rank(pool, budget, self.admission_policy)


# ---------------------------------------------------------------------------
# Frozen registration and analysis
# ---------------------------------------------------------------------------

def prereg(path: Path = PREREG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def boundary() -> dict:
    diff = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *FROZEN],
                          cwd=str(ROOT), capture_output=True, text=True)
    status = subprocess.run(["git", "status", "--porcelain", "--", *FROZEN],
                            cwd=str(ROOT), capture_output=True, text=True)
    return {"frozen_files_clean": diff.returncode == 0 and not status.stdout.strip(),
            "checked": list(FROZEN)}


def _mean(values) -> float:
    values = list(values)
    return sum(values) / len(values)


def _interval(samples: list[float], seed: int, record: dict) -> list[float]:
    reps = int(record["criteria"]["bootstrap_reps"])
    level = float(record["criteria"]["interval"])
    rng = random.Random(seed)
    n = len(samples)
    means = sorted(_mean(samples[rng.randrange(n)] for _ in range(n)) for _ in range(reps))
    tail = (1.0 - level) / 2.0
    return [round(means[min(int(tail * reps), reps - 1)], 6),
            round(means[min(int((1 - tail) * reps), reps - 1)], 6)]


def _paired(cells: list[dict], key: str) -> dict[int, float]:
    index = {(c["arm"], int(c["seed"])): c for c in cells}
    seeds = sorted({int(c["seed"]) for c in cells})
    return {seed: float(index[("adopted", seed)][key])
            - float(index[("reference", seed)][key]) for seed in seeds}


def gates(cells: list[dict], payload: dict, record: dict | None = None) -> dict:
    record = record or prereg()
    seeds = [int(s) for s in record["design"]["seeds"]]
    index = {(c["arm"], int(c["seed"])): c for c in cells}
    out: dict = {}

    differ = sum(1 for s in seeds
                 if index[("reference", s)]["asserted_fingerprint"]
                 != index[("adopted", s)]["asserted_fingerprint"])
    out["G0_liveness"] = {"seeds_where_the_arms_differ": differ, "of": len(seeds),
                          "required": len(seeds) - 1, "passed": differ >= len(seeds) - 1}

    raw = [float(c["raw_temporal_coverage"]) for c in cells]
    out["G1_world_present"] = {"min_raw_temporal_coverage": round(min(raw), 6),
                               "passed": min(raw) >= 1.0 - 1e-9}

    problems = []
    for cell in cells:
        world, covered, asserted = int(cell["world_edges"]), int(cell["covered"]), int(cell["asserted"])
        if covered > asserted:
            problems.append("covered above asserted")
        if world <= 0:
            problems.append("zero denominator")
        elif abs(float(cell["coverage"]) - round(covered / world, 6)) > 1e-6:
            problems.append("coverage is not covered over the world")
        if asserted and abs(float(cell["precision"]) - round(covered / asserted, 6)) > 1e-6:
            problems.append("precision is not covered over asserted")
    out["G2_arithmetic"] = {"problems": problems[:4], "passed": not problems}

    det = payload.get("determinism") or {}
    out["G3_determinism"] = {"matched": bool(det.get("matched")),
                             "passed": bool(det.get("matched"))}
    out["G4_denominator"] = {"min_world_edges": min(int(c["world_edges"]) for c in cells),
                             "passed": min(int(c["world_edges"]) for c in cells) > 0}
    boundary_record = payload.get("boundary") or {}
    out["G5_boundary"] = {"frozen_files_clean": bool(boundary_record.get("frozen_files_clean")),
                          "passed": bool(boundary_record.get("frozen_files_clean"))}
    out["all_passed"] = all(v.get("passed") for v in out.values() if isinstance(v, dict))
    return out


def criteria(cells: list[dict], record: dict | None = None) -> dict:
    record = record or prereg()
    crit = record["criteria"]
    gain = _paired(cells, "coverage")
    mean = _mean(gain.values())
    interval = _interval(list(gain.values()), int(record["seeds"]["bootstrap"]), record)
    width = round(interval[1] - interval[0], 6)
    positive = sum(1 for v in gain.values() if v > 0)
    conditions = {"mean_at_or_above_bar": mean >= crit["bar"],
                  "interval_lower_above_zero": interval[0] > 0,
                  "sign_test_met": positive >= int(crit["sign_test"]["required"])}
    adoption = {"mean_paired_gain": round(mean, 6), "interval": interval,
                "interval_width": width, "bar": crit["bar"],
                "seeds_positive": positive, "conditions": conditions,
                "passed": all(conditions.values())}
    precision = _paired(cells, "precision")
    guard = {"mean_paired_precision_difference": round(_mean(precision.values()), 6),
             "bar": crit["guard_bar"],
             "passed": _mean(precision.values()) >= crit["guard_bar"]}
    per_seed = {str(s): {"coverage_gain": round(gain[s], 6),
                         "precision_difference": round(precision[s], 6)}
                for s in sorted(gain)}
    return {"adoption": adoption, "guard": guard, "per_seed": per_seed}


def verdict(gate_report: dict, criterion_report: dict, record: dict | None = None) -> dict:
    record = record or prereg()
    if not gate_report["all_passed"]:
        failed = sorted(k for k, v in gate_report.items()
                        if isinstance(v, dict) and v.get("passed") is False)
        return {"verdict": "VOID", "decision": "neither", "failed_gates": failed,
                "reading": "a gate failed; no criterion is read"}
    adoption, guard = criterion_report["adoption"], criterion_report["guard"]
    if adoption["passed"] and guard["passed"]:
        return {"verdict": "ADOPTED ARM GAINS", "decision": "gains",
                "reading": "the restored adopted admission covers more of the world's edges at the same budget without losing precision"}
    if adoption["passed"]:
        return {"verdict": "PRICED TRADE", "decision": "trade",
                "reading": "coverage rises and precision falls; nothing is claimed as a gain"}
    if adoption["interval_width"] > record["criteria"]["underpowered_width"]:
        return {"verdict": "UNDERPOWERED", "decision": "neither",
                "reading": "the interval cannot place the difference"}
    return {"verdict": "NO GAIN ON THIS LAYER", "decision": "close",
            "reading": "the adopted rule does not cover more of the world here; the historical negative answer survives"}


def classify(verdict_value: str, record: dict | None = None) -> str:
    record = record or prereg()
    if verdict_value == "NO GAIN ON THIS LAYER":
        return "SURVIVED"
    if verdict_value == "ADOPTED ARM GAINS":
        return "REVERSED"
    if verdict_value == "PRICED TRADE":
        return "CHANGED"
    return "NOT_MEASURABLE"


def analyze(payload: dict, record: dict | None = None) -> dict:
    record = record or prereg()
    gate_report = gates(payload["cells"], payload, record)
    criterion_report = criteria(payload["cells"], record) if gate_report["all_passed"] else {}
    decision = verdict(gate_report, criterion_report, record)
    return {"gates": gate_report, "criteria": criterion_report,
            "decision": decision, "survival": classify(decision["verdict"], record)}


def run(out: Path = ARTIFACT) -> dict:
    record = prereg()
    if not record["status"].startswith("FROZEN"):
        raise SystemExit("the registration is not frozen; no cell may run")
    cycles = int(record["design"]["cycles"])
    arms = {"reference": SleepService, "adopted": DiversityFirstSleepService}
    cells = []
    for seed in record["design"]["seeds"]:
        for arm in record["design"]["arms"]:
            stats = gate_acquisition_sufficiency(seed=int(seed), cycles=cycles,
                                                 service_cls=arms[arm])
            cells.append({
                "seed": int(seed), "arm": arm,
                "coverage": stats["asserted_coverage"],
                "covered": stats["covered_asserted_edges"],
                "asserted": stats["asserted_edges"],
                "precision": round(stats["covered_asserted_edges"] / stats["asserted_edges"], 6)
                if stats["asserted_edges"] else 0.0,
                "world_edges": stats["world_edges"],
                "raw_temporal_coverage": stats["raw_temporal_coverage"],
                "asserted_fingerprint": stats["asserted_fingerprint"],
                "service": stats["arm"],
            })
    first = int(record["design"]["seeds"][0])
    rerun = gate_acquisition_sufficiency(seed=first, cycles=cycles,
                                         service_cls=arms["reference"])
    reference_first = next(c for c in cells
                           if c["seed"] == first and c["arm"] == "reference")
    payload = {
        "kind": "q006_admission_rederivation",
        "date": record["date"],
        "protocol": "docs/Q006-ADMISSION-RE-DERIVATION-PREREGISTRATION.md",
        "prereg": record["prereg"],
        "seeds": list(record["design"]["seeds"]),
        "bootstrap_seed": int(record["seeds"]["bootstrap"]),
        "cycles": cycles,
        "cells": cells,
        "determinism": {"seed": first, "rerun_fingerprint": rerun["asserted_fingerprint"],
                        "matched": rerun["asserted_fingerprint"]
                        == reference_first["asserted_fingerprint"]},
        "boundary": boundary(),
        "provenance": {"runner": "benchmarks/q006_admission_rederivation.py",
                       "instrument": "benchmarks/acquisition_harness.py:gate_acquisition_sufficiency",
                       "arms": {a: arms[a].__name__ for a in record["design"]["arms"]},
                       "engine_runs": len(record["design"]["seeds"]) * 2 + 1},
    }
    payload.update(analyze(payload, record))
    payload = engine_stamp.stamp(payload)
    out.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(payload), encoding="utf-8")
    print(payload["decision"]["verdict"], "|", payload["survival"], "->", out)
    return payload


def check(record: dict | None = None) -> list[str]:
    record = json.loads(ARTIFACT.read_text(encoding="utf-8")) if record is None else record
    frozen = prereg()
    problems: list[str] = []
    if record.get("kind") != "q006_admission_rederivation":
        problems.append("wrong kind")
    if record.get("prereg") != frozen["prereg"]:
        problems.append("wrong registration")
    if tuple(record.get("seeds", ())) != tuple(frozen["design"]["seeds"]):
        problems.append("seed block is not the frozen eight")
    if len(record.get("cells", [])) != 16:
        problems.append("cell count is not 16")
    if {c.get("arm") for c in record.get("cells", [])} != set(frozen["design"]["arms"]):
        problems.append("arm set is not the frozen pair")
    expected = analyze(record, frozen)
    if record.get("gates") != expected["gates"]:
        problems.append("gates do not follow from the stored cells")
    if record.get("criteria") != expected["criteria"]:
        problems.append("criteria do not follow from the stored cells")
    if record.get("decision") != expected["decision"]:
        problems.append("decision does not follow from the stored cells")
    if record.get("survival") != expected["survival"]:
        problems.append("survival classification does not follow from the verdict")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(record):
        problems.append("result page is stale")
    return problems


def render(record: dict) -> str:
    decision = record["decision"]
    c = record["criteria"]
    a = c["adoption"]
    g = c["guard"]
    d = record["determinism"]
    lines = [
        "# Q006 admission re-derivation — result",
        "",
        f"**Verdict: `{decision['verdict']}` — {record['survival']} the historical answer.**",
        "",
        f"Protocol: `{record['protocol']}`. Engine: `{record['engine_version']}` "
        f"(`{record['engine_sha256'][:12]}`). Seeds: "
        f"{record['seeds'][0]}–{record['seeds'][-1]}, two arms, {record['cycles']} cycles.",
        "",
        "The historical answer was `NO GAIN ON THIS LAYER` on an unattributed build. "
        "This block re-runs the same endpoint on the pinned engine with a fresh seed block.",
        "",
        "## Result",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        f"| Mean paired coverage gain (adopted − reference) | {a['mean_paired_gain']:+.6f} |",
        f"| 95% interval | [{a['interval'][0]:+.6f}, {a['interval'][1]:+.6f}] |",
        f"| Interval width | {a['interval_width']:.6f} |",
        f"| Seeds positive | {a['seeds_positive']} of {len(record['seeds'])} |",
        f"| Mean paired precision difference | {g['mean_paired_precision_difference']:+.6f} |",
        f"| Gain bar / guard | {a['bar']:.2f} / {g['bar']:.2f} |",
        f"| Determinism re-run matched | {d['matched']} |",
        "",
        "## Per seed",
        "",
        "| Seed | Coverage gain | Precision difference |",
        "| --- | --- | --- |",
    ]
    for seed, values in c["per_seed"].items():
        lines.append(f"| {seed} | {values['coverage_gain']:+.6f} | "
                     f"{values['precision_difference']:+.6f} |")
    failed = [name for name, value in record["gates"].items()
              if isinstance(value, dict) and not value.get("passed")]
    lines += [
        "",
        "## Gates",
        "",
        f"All gates passed: **{record['gates']['all_passed']}**."
        + (f" Failed: {', '.join(failed)}." if failed else ""),
        "",
        f"**What this means.** {decision['reading']}. The historical answer is "
        f"**{record['survival']}** on this block.",
        "",
        "The cells are in `docs/q006_admission_rederivation.json`. No engine file changed; "
        "the adopted arm is an in-process restoration.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", default=str(ARTIFACT))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.check:
        problems = check()
        if problems:
            print("FAIL: " + "; ".join(problems))
            return 1
        print("Q006 admission re-derivation: OK")
        return 0
    if not args.run:
        parser.print_help()
        return 0
    target = Path(args.out)
    if target.exists() and not args.force:
        print("refusing to overwrite %s without --force" % target)
        return 1
    run(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
