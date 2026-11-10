"""Run Q053's frozen 20-cell block on lattice_L1.

The preregistration (`docs/q053_mechanism_prereg.json`) fixes the block, the two arms, the
criteria and the gates; it deliberately shipped no runner and no mechanism. This module adds
both, in process only:

* the mechanism is a `SleepService` subclass that changes **one** step, hypothesis retention.
  It keeps the highest-support hypothesis of each subject's top two expectations, then fills
  the remaining slots with the shipped salience ranking. The engine source is not edited.
* the runner is the committed online next-cycle recall@5 instrument
  (`benchmarks.long_delay_capability`), extended with the competition share the mechanism gate
  reads. It writes one part per cell, so the block is resumable, and `--finish` assembles the
  run artifact and hands it to the committed scorer.

    ./.venv/bin/python -m benchmarks.q053_mechanism_run --measure
    ./.venv/bin/python -m benchmarks.q053_mechanism_run --finish
    ./.venv/bin/python -m benchmarks.q053_mechanism_run --check

The block may not grow: `--measure` refuses a seed outside the frozen ten, and `--finish`
refuses a cell set that is not exactly 2 arms x 10 seeds.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import engine_stamp                                    # noqa: E402
from benchmarks import q053_mechanism_prereg as P                      # noqa: E402
from benchmarks.long_delay_capability import (                         # noqa: E402
    EVENTS_PER_CYCLE, _chunk, _recall_at_k, stream_for, stream_digest)
from organica.memory import MemoryService, _extract_tags                # noqa: E402
from organica.paths import temp_db                                      # noqa: E402
from organica.sleep import SleepService                                 # noqa: E402

PARTS = ROOT / ".scratch" / "q053_mechanism" / "parts"
ARTIFACT = ROOT / "docs" / "q053_mechanism_run.json"
DOC = ROOT / "docs" / "Q053-MECHANISM-RESULT.md"
ARMS = ("control", "treatment")
MARKER = "high_structural_significance"


def competing_subjects(hypotheses) -> dict[str, int]:
    """Subjects retaining two or more competing (non-marker) hypotheses."""
    counts = Counter(h.subject for h in hypotheses if h.expectation != MARKER)
    return {subject: count for subject, count in counts.items() if count >= 2}


def floor_selection(beliefs, max_hypotheses: int) -> list:
    """The mechanism, isolated from the engine so it can be tested on synthetic beliefs.

    For each subject: rank its expectations by their best hypothesis's support_count
    (descending, ties on the expectation tag) and keep the highest-support hypothesis of the
    top two. The result is ordered by support, and the caller fills the remaining capacity
    from the shipped ranking.
    """
    by_subject: dict[str, list] = defaultdict(list)
    for hypothesis in beliefs:
        by_subject[hypothesis.subject].append(hypothesis)
    kept = []
    for subject in sorted(by_subject):
        best: dict[str, object] = {}
        for hypothesis in by_subject[subject]:
            current = best.get(hypothesis.expectation)
            if current is None or ((hypothesis.support_count, hypothesis.expectation)
                                   > (current.support_count, current.expectation)):
                best[hypothesis.expectation] = hypothesis
        ranked = sorted(best.values(), key=lambda h: (-h.support_count, h.expectation))
        kept.extend(ranked[:2])
    kept.sort(key=lambda h: (-h.support_count, h.subject, h.expectation))
    return kept[:max_hypotheses]


class RetainSecondCompetingSleepService(SleepService):
    """The shipped engine plus the second-competing retention floor at the prune.

    The floor's picks must be exempt from the death threshold, which is applied upstream in
    `_form_hypotheses`. Disabling it there (0.0) lets every candidate reach retention; the
    override then re-applies the shipped 0.15 rule to every candidate that is **not** a floor
    pick, so only the two expectations per subject are exempt. The decay constant, the
    confidence formula and the shipped ranking are unchanged.
    """

    DEATH_THRESHOLD = 0.0

    def _retain_hypotheses(self, beliefs, info, temporal) -> list:
        floor = floor_selection(beliefs, self.MAX_HYPOTHESES)
        floor_ids = {hypothesis.id for hypothesis in floor}
        survivors = [
            hypothesis for hypothesis in beliefs
            if hypothesis.id in floor_ids
            or not (hypothesis.confidence < SleepService.DEATH_THRESHOLD
                    and (hypothesis.support_count + hypothesis.contradiction_count) >= 3)
        ]
        shipped = super()._retain_hypotheses(survivors, info, temporal)
        kept, seen = [], set()
        for hypothesis in floor + list(shipped):
            if len(kept) >= self.MAX_HYPOTHESES:
                break
            if hypothesis.id not in seen:
                kept.append(hypothesis)
                seen.add(hypothesis.id)
        return kept


def arm_class(arm: str):
    if arm == "control":
        return SleepService
    if arm == "treatment":
        return RetainSecondCompetingSleepService
    raise ValueError("unknown arm %r" % arm)


def _window(rows: list[dict], window: tuple[int, int]) -> dict:
    low, high = window
    picked = [row for row in rows if low <= row["cycle"] < high and row["recall_at_5"] is not None]
    recall = [row["recall_at_5"] for row in picked if row["recall_at_5"] is not None]
    return {
        "recall": round(sum(recall) / len(recall), 6) if recall else None,
        "cycles": len(picked),
        "predictions": sum(row["predictions"] for row in picked),
        "theory_zero_share": (round(sum(1 for row in picked if not row["theories"]) / len(picked), 6)
                              if picked else 0.0),
        "competition_share": (round(sum(1 for row in picked if row["competing"]) / len(picked), 6)
                              if picked else 0.0),
    }


def run_cell(seed: int, arm: str, cycles: int = 300):  # noqa: C901 - one loop, mirroring the instrument
    events = stream_for(seed, family="lattice_L1")
    db = temp_db("q053_%s_%d.db" % (arm, seed))
    db.unlink(missing_ok=True)
    memory = MemoryService(db_path=str(db))
    service = arm_class(arm)(memory)
    service._rng.seed(seed)
    vocabulary: set[str] = set()
    try:
        for text in events[:EVENTS_PER_CYCLE]:
            memory.store(text, event_type="event", source="seed:bootstrap")
            vocabulary.update(_extract_tags(text))
        rows: list[dict] = []
        pending: dict[tuple[str, str], float] | None = None
        last_theories: int | None = None
        last_competing = False
        previous = events[EVENTS_PER_CYCLE - 1]
        for cycle in range(cycles):
            chunk = _chunk(events, cycle)
            if pending is not None:
                rows.append({
                    "cycle": cycle - 1,
                    "predictions": len(pending),
                    "recall_at_5": _recall_at_k(pending, previous, chunk),
                    "theories": last_theories,
                    "competing": last_competing,
                })
            for text in chunk:
                memory.store(text, event_type="event", source="cycle:%d" % cycle)
            vocabulary.update(tag for text in chunk for tag in _extract_tags(text))
            report = service.run_sleep_cycle()
            pending = {(p.source, p.target): float(p.strength)
                       for p in (report.predictions if report else [])}
            last_theories = len(getattr(report, "theories", []) or [])
            last_competing = bool(competing_subjects(getattr(report, "hypotheses", []) or []))
            previous = chunk[-1]
        early = _window(rows, (40, 90))
        late = _window(rows, (240, 300))
        cell = {
            "seed": seed,
            "arm": arm,
            "decay": service.TEMPORAL_DECAY_FACTOR,
            "death_threshold": SleepService.DEATH_THRESHOLD,
            "floor_exemption": arm == "treatment",
            "early_recall": early["recall"],
            "late_recall": late["recall"],
            "early_competition_share": early["competition_share"],
            "late_competition_share": late["competition_share"],
            "late_theory_zero_share": late["theory_zero_share"],
            "predictions_early": early["predictions"],
            "predictions_late": late["predictions"],
            "stream_digest": stream_digest(seed, "lattice_L1"),
            "cycles": cycles,
        }
        digest = hashlib.sha256(json.dumps(cell, sort_keys=True).encode("utf-8")).hexdigest()[:16]
        return dict(cell, digest=digest)
    finally:
        memory.close()
        db.unlink(missing_ok=True)


def part_path(seed: int, arm: str) -> Path:
    return PARTS / ("%d_%s.json" % (seed, arm))


def measure(seeds: list[int], arms: tuple[str, ...] = ARMS) -> int:
    body = P.prereg()
    unknown = sorted(set(seeds) - set(body["design"]["seeds"]))
    if unknown:
        raise SystemExit("seed(s) outside the frozen block: %r" % unknown)
    for seed in seeds:
        for arm in arms:
            path = part_path(seed, arm)
            if path.exists():
                print("cached", path.name, flush=True)
                continue
            cell = run_cell(seed, arm, body["design"]["cycles"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(engine_stamp.stamp(cell), indent=1) + "\n", encoding="utf-8")
            print("cell %d %-9s late=%.4f comp=%.2f zero=%.2f preds=%d/%d"
                  % (seed, arm, cell["late_recall"], cell["late_competition_share"],
                     cell["late_theory_zero_share"], cell["predictions_early"],
                     cell["predictions_late"]), flush=True)
    return 0


def _load_parts() -> list[dict]:
    body = P.prereg()
    cells = []
    for seed in body["design"]["seeds"]:
        for arm in ARMS:
            path = part_path(seed, arm)
            if not path.exists():
                raise SystemExit("missing part %s; run --measure" % path.name)
            cells.append(json.loads(path.read_text(encoding="utf-8")))
    return cells


def build() -> dict:
    body = P.prereg()
    cells = _load_parts()
    fingerprint = engine_stamp.engine_sha256()
    control = next(cell for cell in cells
                   if cell["seed"] == body["design"]["seeds"][0] and cell["arm"] == "control")
    # The determinism gate: the same cell, run a second time, must reproduce its digest.
    rerun = run_cell(body["design"]["seeds"][0], "control", body["design"]["cycles"])
    if rerun["digest"] != control["digest"]:
        raise SystemExit("G3 fails: the control re-run did not reproduce %s" % control["digest"])
    run = {
        "prereg": body["prereg"],
        "engine": {"fingerprint": fingerprint, "version": __import__("organica").__version__},
        "arms": {
            "control": {"decay": body["arms"]["control"]["decay"],
                        "death_threshold": body["arms"]["control"]["death_threshold"],
                        "fingerprint": fingerprint},
            "treatment": {"decay": body["arms"]["treatment"]["decay"],
                          "death_threshold": body["arms"]["treatment"]["death_threshold"],
                          "fingerprint": fingerprint + "+floor"},
        },
        "control_rerun_fingerprint": fingerprint,
        "control_rerun_digest": rerun["digest"],
        "cells": [{key: cell[key] for key in (
            "seed", "arm", "early_recall", "late_recall", "late_competition_share",
            "late_theory_zero_share", "predictions_early", "predictions_late", "digest")}
            for cell in cells],
    }
    label, details = P.verdict(body, run)
    return dict(run, verdict=label, details=details)


def _table(artifact: dict) -> str:
    lines = [
        "# Q053 mechanism result — the 20-cell block on `lattice_L1`",
        "",
        "Generated from `docs/q053_mechanism_run.json` by "
        "`python -m benchmarks.q053_mechanism_run --finish`. Do not edit by hand.",
        "",
        "Protocol: `docs/Q053-MECHANISM-PREREGISTRATION.md` (frozen 2026-11-08). "
        "Mechanism: second-competing retention floor, implemented **in process** in "
        "`benchmarks/q053_mechanism_run.py`; no engine file changed.",
        "",
        "**Verdict: `%s`**" % artifact["verdict"],
        "",
        "| Criterion | Result |",
        "| --- | --- |",
        "| M1 mechanism (late competition share, median gap, bar %s) | %s |"
        % (artifact["details"].get("m1_bar"), artifact["details"].get("m1_median_gap")),
        "| C1 capability (late recall@5, median gap, bar %s) | %s |"
        % (artifact["details"].get("capability_bar"),
           artifact["details"].get("capability_median_gap", "unread: M1 failed")),
        "| C1 interval | %s |" % (artifact["details"].get("interval", "unread")),
        "| C1 positive seeds | %s of 10 |" % artifact["details"].get("positive_seeds", "unread"),
        "| C2 early cost (median gap, bound -0.01) | %s |"
        % artifact["details"].get("early_median_gap", "unread"),
        "",
        "| Seed | Arm | Early recall@5 | Late recall@5 | Late competition | Late theory-zero |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for cell in artifact["cells"]:
        lines.append("| %s | %s | %.4f | %.4f | %.2f | %.2f |"
                     % (cell["seed"], cell["arm"], cell["early_recall"], cell["late_recall"],
                        cell["late_competition_share"], cell["late_theory_zero_share"]))
    lines += [
        "",
        "The control's late theory-zero share is the liveness gate: a control that survives "
        "would compare two live arms and void the block.",
        "",
        "**Scope.** One world family, one mechanism, one block. The verdict licenses no "
        "adoption; adoption is a separate owner decision. The mechanism changes retention only, "
        "and the raw/asserted distinction is not at issue here.",
        "",
        "## Status reconciliation",
        "",
        "The preregistration page says **FROZEN, NOT RUN** because that was its state at freeze on "
        "2026-11-08, and a frozen protocol is amended rather than rewritten. The block ran on "
        "2026-11-09 under the owner decision recorded in the manual (action row 110). The "
        "mechanism was implemented **in process only** in `benchmarks/q053_mechanism_run.py`; no "
        "engine file changed.",
        "",
        "## Why the gate failed, and what it does not mean",
        "",
        "The floor retained only hypotheses that formation proposed in the same cycle. Across the "
        "late windows no subject presented two competing beliefs, so the floor had nothing to "
        "exempt: M1 is exactly 0.00 on every seed. Per the frozen decision table the capability "
        "endpoint is **unread**: this is a manipulation-check failure, not a null capability "
        "result, and not evidence that preservation cannot help. The loss the preregistration "
        "targets happens after formation stops proposing the second expectation, in the "
        "prior-decay path, which this block does not touch. A retry needs a new preregistration "
        "that acts there; this block may not grow into one.",
        "",
    ]
    return "\n".join(lines)


def finish() -> int:
    artifact = build()
    problems = P.validate()
    if problems:
        raise SystemExit("the preregistration is not valid: " + "; ".join(problems))
    ARTIFACT.write_text(json.dumps(engine_stamp.stamp(artifact), indent=1) + "\n", encoding="utf-8")
    DOC.write_text(_table(artifact), encoding="utf-8")
    print("%s: %s" % (artifact["verdict"], json.dumps(artifact["details"], indent=1)))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no run artifact; run --finish")
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    body = P.prereg()
    label, details = P.verdict(body, artifact)
    problems = []
    if label != artifact.get("verdict"):
        problems.append("the artifact's verdict is not the one its cells imply")
    if details != artifact.get("details"):
        problems.append("the artifact's details are not the ones its cells imply")
    if DOC.read_text(encoding="utf-8") != _table(artifact):
        problems.append("the result page is stale")
    expected = {(seed, arm) for seed in body["design"]["seeds"] for arm in ARMS}
    if {(cell["seed"], cell["arm"]) for cell in artifact["cells"]} != expected:
        problems.append("the cells are not the frozen block")
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    print("q053 block: %s (M1 gap %s)" % (label, details.get("m1_median_gap")))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--seed", type=int, action="append", default=None)
    parser.add_argument("--arm", choices=ARMS, action="append", default=None)
    args = parser.parse_args(argv)
    if args.measure:
        seeds = args.seed or list(P.prereg()["design"]["seeds"])
        return measure(seeds, tuple(args.arm or ARMS))
    if args.finish:
        return finish()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
