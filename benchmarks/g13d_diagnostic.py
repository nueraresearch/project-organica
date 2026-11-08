"""G13-D: the bounded capacity + world-only provenance diagnostic.

Authorized by `docs/DECISION-V2-SCOPE.md` D2 and specified in
`docs/G13-D-DIAGNOSTIC-PLAN.md`.  Five seeds, two arms, one report.

  baseline  the frozen engine: MAX_PREDICTIONS = 20, unfiltered lookback
  g13d      MAX_PREDICTIONS = 1_000 and `_record_temporal_edges` restricted to
            rows whose `event_type` is not `sleep`

The readout is held at its calibrated `alpha = 256.0` in both arms: it is a fixed
constant, not an intervention, and it is never tuned on these seeds.

Both overrides are in-process subclasses.  No frozen engine file is edited, and
nothing here is a successor architecture.

Scoring reuses `benchmarks/acquisition_runner.py` — the same windows, the same two
metric shapes, the same calibrated replay and cell-counter baselines, the same
ceiling and base rate — so the diagnostic is read against the references the
closed study used.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile
from collections import defaultdict
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from organica.memory import MemoryService  # noqa: E402
from organica.sleep import SleepService  # noqa: E402
from benchmarks.acquisition_baselines import fit_cell_counter  # noqa: E402
from benchmarks.acquisition_compositional import (  # noqa: E402
    CYCLES, EVENTS_PER_CYCLE, PHASE_ACQUISITION, PHASE_RETENTION,
    PHASE_REVISION_LEARN, PHASE_REVISION_TEST, PHASE_TRANSFER, PHASE_WARMUP,
    generate_compositional_world, make_ceiling,
)
from benchmarks.acquisition_runner import (  # noqa: E402
    evaluate_shapes, fit_replay_learner, make_organica_backoff, structure_edges,
)
from benchmarks import engine_stamp

#: The authorization fixes these; none may be changed after a number is seen.
SEEDS: tuple[int, ...] = (20261101, 20261102, 20261103, 20261104, 20261105)
ALPHA: float = 256.0            # calibrated on 20261099; a constant, not an arm
CAP: int = 1_000
BASELINE_CAP: int = 20

DIAGNOSTIC_OUT = "docs/g13d_diagnostic.json"
DIAGNOSTIC_DOC = "docs/G13D-DIAGNOSTIC.md"
PLAN_DOC = "docs/G13-D-DIAGNOSTIC-PLAN.md"

CAPACITY_NOTE = (
    "the committed counter covers prior candidates of all types, not predictions, so "
    "it cannot show that the prediction cap bound; the cap is verified structurally "
    "only (MAX_PREDICTIONS 1,000 vs 20)"
)
CORRECTION_NOTE = (
    "The capacity check as first committed counted all candidate types (3,998 in both "
    "arms) and did not test the prediction cap. It is recorded as not measured "
    "everywhere, including per seed; scores were not recomputed and are unchanged."
)


class WorldOnlyMemory(MemoryService):
    """The engine's memory with the lookback restricted to world events.

    This is the provenance intervention: the frozen query has no `event_type`
    filter, so a world event can take its `tag_from` from a sleep payload (D2).
    The body is the engine's own, with one added predicate and nothing else.
    """

    def _record_temporal_edges(self, new_tags: list[str], lookback: int = 3):
        if not new_tags:
            return
        rows = self._conn.execute(
            "SELECT tags FROM events WHERE event_type != 'sleep' "
            "ORDER BY time DESC LIMIT ?", (lookback,)).fetchall()
        for (tags_str,) in rows:
            prior_tags = [t for t in (tags_str or "").split(",") if t]
            for tag_from in prior_tags:
                for tag_to in new_tags:
                    if tag_from != tag_to:
                        self._conn.execute("""
                            INSERT INTO precedes (tag_from, tag_to, count)
                            VALUES (?, ?, 1)
                            ON CONFLICT(tag_from, tag_to) DO UPDATE SET count = count + 1
                        """, (tag_from, tag_to))


class CappedSleepService(SleepService):
    """The frozen engine with one capacity constant raised, in process."""

    MAX_PREDICTIONS = CAP


class G13DSleepService(CappedSleepService):
    """Both interventions together, on a world-only memory."""


def _scratch(label: str) -> pathlib.Path:
    base = ROOT / ".scratch"
    base.mkdir(parents=True, exist_ok=True)
    return pathlib.Path(tempfile.mkdtemp(dir=base)) / f"{label}.db"


def _windows(events: list[str], trainable: list[bool]
             ) -> tuple[list[str], set[str], dict[str, tuple[list, list]]]:
    epc = EVENTS_PER_CYCLE
    warm_lo, _ = PHASE_WARMUP
    _, acq_hi = PHASE_ACQUISITION
    exposure = list(range(warm_lo * epc, acq_hi * epc))
    train_rows = [events[i] for i in exposure if trainable[i]]
    vocab = {t for row in train_rows for t in row.split()}

    def pairs(lo: int, hi: int):
        idx = list(range(lo * epc, hi * epc))
        return ([sorted(events[idx[k]].split()) for k in range(len(idx) - 1)],
                [sorted(events[idx[k + 1]].split()) for k in range(len(idx) - 1)])

    ctxs = {
        "retention": pairs(*PHASE_RETENTION),
        "transfer_diagnostic": pairs(*PHASE_TRANSFER),
        "revision": pairs(*PHASE_REVISION_TEST),
    }
    return train_rows, vocab, ctxs


def _run_arm(seed: int, events: list[str], trainable: list[bool],
             memory_cls, service_cls, label: str) -> dict[str, Any]:
    """One arm on one seed.  Acquisition, freeze, revision, freeze."""
    epc = EVENTS_PER_CYCLE
    warm_lo, _ = PHASE_WARMUP
    acq_lo, acq_hi = PHASE_ACQUISITION
    rev_lo, rev_hi = PHASE_REVISION_LEARN
    db = _scratch(f"g13d_{seed}_{label}")
    mem = memory_cls(str(db))
    svc = service_cls(mem)
    try:
        for i in range(acq_hi * epc):
            in_acq = acq_lo * epc <= i < acq_hi * epc
            if in_acq and not trainable[i]:
                continue
            mem.store(events[i], event_type="observe",
                      source="env_acq" if in_acq else "env")
            if (i + 1) % epc == 0:
                svc.run_sleep_cycle()
        frozen = svc._load_prior_candidates()

        for cyc in range(rev_lo, rev_hi):
            for ev in events[cyc * epc:(cyc + 1) * epc]:
                mem.store(ev, event_type="observe", source="env_rev")
            svc.run_sleep_cycle()
        revised = svc._load_prior_candidates()

        temporal_rows = mem.temporal_edges(min_count=1)
        precedes_rows = mem._conn.execute("SELECT COUNT(*) FROM precedes").fetchone()[0]
        sleep_only_sources = _sleep_only_sources(mem, events, trainable)
        memory_rows = {"precedes_rows": int(precedes_rows),
                       "sleep_only_source_pairs": sleep_only_sources,
                       "temporal_pairs": len(temporal_rows)}
        return {"frozen": frozen, "revised": revised, "memory": memory_rows,
                "max_candidates": max(len(frozen), len(revised))}
    finally:
        mem._conn.close()
        for path in db.parent.iterdir():
            path.unlink(missing_ok=True)
        try:
            db.parent.rmdir()
        except OSError:
            pass


def _sleep_only_sources(mem: MemoryService, events: list[str],
                        trainable: list[bool]) -> int:
    """`precedes` source tags that occur in no world event: the filter's target."""
    world = {t for ev, ok in zip(events, trainable) if ok for t in ev.split()}
    rows = mem._conn.execute("SELECT DISTINCT tag_from FROM precedes").fetchall()
    return sum(1 for (tag_from,) in rows if tag_from not in world)


def _score_arms(seed: int) -> dict[str, Any]:
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    events = world["events"]
    trainable = world["trainable"]
    train_rows, vocab, ctxs = _windows(events, trainable)

    base: dict[str, int] = defaultdict(int)
    for row in train_rows:
        for tag in row.split():
            base[tag] += 1
    total = sum(base.values()) or 1
    base_rate = {tag: n / total for tag, n in base.items()}

    arms = {
        "baseline": _run_arm(seed, events, trainable, MemoryService,
                             SleepService, "baseline"),
        "g13d": _run_arm(seed, events, trainable, WorldOnlyMemory,
                         G13DSleepService, "g13d"),
    }

    scores: dict[str, Any] = {}
    for name, arm in arms.items():
        frozen_p = make_organica_backoff(structure_edges(arm["frozen"]),
                                         base_rate, ALPHA)
        revised_p = make_organica_backoff(structure_edges(arm["revised"]),
                                          base_rate, ALPHA)
        scores[name] = {
            "retention": evaluate_shapes(frozen_p, *ctxs["retention"], vocab),
            "transfer_diagnostic": evaluate_shapes(
                frozen_p, *ctxs["transfer_diagnostic"], vocab),
            "revision": evaluate_shapes(revised_p, *ctxs["revision"], vocab),
        }

    # Fixed references, identical for both arms: same stream, same calibration.
    replay_p = fit_replay_learner(train_rows, vocab, window=1, half_life=None,
                                  alpha=0.5)
    stat_p = fit_cell_counter(train_rows, vocab, world["tag_to_cell"], alpha=0.1)
    references = {
        "replay": {limb: evaluate_shapes(replay_p, *ctxs[limb], vocab)
                   for limb in ctxs},
        "cell_counter": {limb: evaluate_shapes(stat_p, *ctxs[limb], vocab)
                         for limb in ctxs},
        "bayes_ceiling": {
            "retention": evaluate_shapes(make_ceiling(world, 0), *ctxs["retention"], vocab),
            "transfer_diagnostic": evaluate_shapes(
                make_ceiling(world, 0), *ctxs["transfer_diagnostic"], vocab),
            "revision": evaluate_shapes(make_ceiling(world, 1), *ctxs["revision"], vocab),
        },
        "base_rate": {limb: evaluate_shapes(
            lambda u, v: base_rate.get(v, 0.0), *ctxs[limb], vocab)
            for limb in ctxs},
    }

    deltas = {}
    for limb in ("retention", "transfer_diagnostic", "revision"):
        for shape in ("house_shape", "self_cells_shape"):
            gain = (scores["g13d"][limb][shape]["log_loss"]
                    - scores["baseline"][limb][shape]["log_loss"])
            deltas[f"{limb}.{shape}"] = round(gain, 6)

    return {
        "seed": seed,
        "scores": scores,
        "deltas_g13d_minus_baseline": deltas,
        "references": references,
        "memory": {"baseline": arms["baseline"]["memory"],
                   "g13d": arms["g13d"]["memory"]},
        "all_candidates_max": {"baseline": arms["baseline"]["max_candidates"],
                               "g13d": arms["g13d"]["max_candidates"]},
        "all_candidates_max_note": ("prior candidates of all types, never a "
                                    "prediction count"),
        "checks": {
            "provenance_filter_bit": (
                arms["baseline"]["memory"]["sleep_only_source_pairs"] > 0
                and arms["g13d"]["memory"]["sleep_only_source_pairs"] == 0),
            # Never inferred from the all-type counter: it cannot see the cap.
            "cap_binding": None,
            "capacity_note": CAPACITY_NOTE,
        },
    }


def _cache_path(seed: int) -> pathlib.Path:
    return ROOT / ".scratch" / f"g13d_{seed}.json"


def _aggregate_checks(per_seed: list[dict[str, Any]]) -> dict[str, Any]:
    """Pool the per-seed checks.  Capacity stays unmeasured unless every seed measured it."""
    caps = [entry["checks"].get("cap_binding") for entry in per_seed]
    return {
        "provenance_filter_bit": all(e["checks"]["provenance_filter_bit"]
                                     for e in per_seed),
        "cap_binding": None if any(c is None for c in caps) else all(caps),
        "capacity_note": CAPACITY_NOTE,
    }


def run_diagnostic(budget_seconds: float = 200.0) -> dict[str, Any]:
    import time
    started = time.monotonic()
    per_seed: list[dict[str, Any]] = []
    for seed in SEEDS:
        cached = _cache_path(seed)
        if cached.exists():
            per_seed.append(json.loads(cached.read_text(encoding="utf-8")))
            continue
        if per_seed and time.monotonic() - started > budget_seconds:
            break
        result = _score_arms(seed)
        cached.write_text(json.dumps(engine_stamp.stamp(result), sort_keys=True) + "\n", encoding="utf-8")
        per_seed.append(result)
    done = [entry["seed"] for entry in per_seed]
    if len(done) < len(SEEDS):
        return {"artifact_written": False, "computed": done,
                "pending": [s for s in SEEDS if s not in done],
                "note": "resumable: rerun the same command"}

    keys = list(per_seed[0]["deltas_g13d_minus_baseline"])
    pooled = {key: round(sum(e["deltas_g13d_minus_baseline"][key]
                             for e in per_seed) / len(per_seed), 6) for key in keys}
    art = {
        "kind": "g13d_diagnostic",
        "status": "diagnostic",
        "plan": PLAN_DOC,
        "interventions": {
            "capacity": CAP,
            "capacity_baseline": BASELINE_CAP,
            "provenance": "lookback restricted to event_type != 'sleep'",
            "in_process_only": True,
        },
        "alpha": ALPHA,
        "alpha_note": "calibrated on 20261099; a constant across both arms, not an intervention",
        "seeds": list(SEEDS),
        "confirmatory_seeds_touched": False,
        "engine_files_edited": False,
        "authorises_confirmatory": False,
        "no_verdict": True,
        "metric_note": ("log-loss on the retention, transfer-diagnostic and revision "
                        "windows; house shape is primary, self-cells co-primary"),
        "per_seed": per_seed,
        "pooled_delta_g13d_minus_baseline": pooled,
        "checks": _aggregate_checks(per_seed),
        "capacity_note": CAPACITY_NOTE,
        "correction_2026_11_02": CORRECTION_NOTE,
        "artifact_written": True,
    }
    (ROOT / DIAGNOSTIC_OUT).write_text(
        json.dumps(engine_stamp.stamp(art), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / DIAGNOSTIC_DOC).write_text(render_report(art), encoding="utf-8")
    return art


def render_report(art: dict) -> str:
    """The report, generated from the artifact.  Not typed by hand."""
    seeds = art["per_seed"]
    lines = [
        "# G13-D — diagnostic report",
        "",
        "**Generated from [`docs/g13d_diagnostic.json`](g13d_diagnostic.json); do not edit",
        "by hand.** Regenerate with",
        "`PYTHONHASHSEED=0 python -m benchmarks.g13d_diagnostic --report`.",
        "",
        f"Plan: [`{art['plan']}`](G13-D-DIAGNOSTIC-PLAN.md), committed before the run.",
        f"Seeds: {', '.join(str(s) for s in art['seeds'])} (diagnostic only).",
        "",
        "## The condition",
        "",
        f"Two interventions together: capacity `MAX_PREDICTIONS = {art['interventions']['capacity']}`",
        f"(baseline {art['interventions']['capacity_baseline']}) and a lookback restricted to",
        "`event_type != 'sleep'`. The readout is held at its calibrated",
        f"`alpha = {art['alpha']}`, which is a constant in both arms and **not** an",
        "intervention. Both overrides are in-process subclasses; no engine file was edited.",
        "",
        "## Paired difference (log-loss, g13d minus baseline)",
        "",
        "Negative means the combined condition scored better. No threshold is applied.",
        "",
        "| window.shape | " + " | ".join(str(s) for s in art["seeds"]) + " | mean |",
        "|---|" + "---|" * (len(art["seeds"]) + 1),
    ]
    for key in art["pooled_delta_g13d_minus_baseline"]:
        cells = " | ".join(f"{e['deltas_g13d_minus_baseline'][key]:+.4f}"
                           for e in seeds)
        lines.append(f"| `{key}` | {cells} | {art['pooled_delta_g13d_minus_baseline'][key]:+.4f} |")

    lines += [
        "",
        "## Absolute scores, house shape (primary)",
        "",
        "| arm | window | " + " | ".join(str(s) for s in art["seeds"]) + " |",
        "|---|---|" + "---|" * len(art["seeds"]),
    ]
    for arm in ("baseline", "g13d"):
        for limb in ("retention", "transfer_diagnostic", "revision"):
            cells = " | ".join(
                f"{e['scores'][arm][limb]['house_shape']['log_loss']:.4f}"
                for e in seeds)
            lines.append(f"| {arm} | `{limb}` | {cells} |")

    lines += [
        "",
        "## Fixed references, house shape",
        "",
        "| reference | window | " + " | ".join(str(s) for s in art["seeds"]) + " |",
        "|---|---|" + "---|" * len(art["seeds"]),
    ]
    for ref in ("replay", "cell_counter", "bayes_ceiling", "base_rate"):
        for limb in ("retention", "transfer_diagnostic", "revision"):
            cells = " | ".join(
                f"{e['references'][ref][limb]['house_shape']['log_loss']:.4f}"
                for e in seeds)
            lines.append(f"| {ref} | `{limb}` | {cells} |")

    lines += [
        "",
        "## Intervention checks",
        "",
        f"- provenance filter bit on every seed: **{art['checks']['provenance_filter_bit']}**",
        f"- capacity bound reached above {art['interventions']['capacity_baseline']} on every seed: "
        f"**{'not measured' if art['checks'].get('cap_binding') is None else art['checks']['cap_binding']}**"
        + (f" — {art['checks']['capacity_note']}" if art['checks'].get('capacity_note') else ""),
        "",
        "## What this is not",
        "",
        "A diagnostic of how the frozen engine scores when two confounds are removed",
        "together. It establishes no acquisition, transfer, comparative-advantage or V2",
        "result, it applies no threshold, and it authorizes no confirmatory run. The",
        "closed acquisition preregistration, its Gate 13 threshold, the Task 2 stopped",
        "verdict and every confirmatory seed assignment are unchanged.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="G13-D bounded diagnostic.")
    ap.add_argument("--run", action="store_true", help="run the five diagnostic seeds")
    ap.add_argument("--report", action="store_true", help="regenerate the report only")
    ap.add_argument("--budget", type=float, default=200.0)
    args = ap.parse_args(argv)
    if args.report:
        art = json.loads((ROOT / DIAGNOSTIC_OUT).read_text(encoding="utf-8"))
        (ROOT / DIAGNOSTIC_DOC).write_text(render_report(art), encoding="utf-8")
        print(json.dumps({"wrote": DIAGNOSTIC_DOC}, indent=1))
        return 0
    if not args.run:
        ap.print_help()
        return 2
    art = run_diagnostic(budget_seconds=args.budget)
    if not art.get("artifact_written", True):
        print(json.dumps(art, indent=1, sort_keys=True))
        return 0
    print(json.dumps({"wrote": [DIAGNOSTIC_OUT, DIAGNOSTIC_DOC],
                      "pooled": art["pooled_delta_g13d_minus_baseline"],
                      "checks": art["checks"]}, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
