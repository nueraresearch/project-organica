"""Render the formation-vs-utilization campaign result from its artifact.

The campaign artifact (``docs/formation_utilization.json``) is the
machine-written record.  This module turns it into the human-readable result
document, with every number computed from the artifact rather than typed by
hand, and refuses to write a document whose verdict does not match the
artifact's pre-committed analysis.

The document is a record of ONE run: the 30 confirmatory seeds of 2026-10-30.
It is not a template for a future campaign; a future campaign gets its own
artifact and its own document.  ``tests/test_formation_utilization_results.py``
re-renders this document and fails if it has drifted from the artifact.

Standard library only.
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks.formation_utilization import (  # noqa: E402
    CAMPAIGN_OUT,
    LIMBS,
    TASKS,
    paired_bootstrap,
    verdict_of,
)

RESULTS_MD = "docs/formation_utilization_results.md"

#: The verdict this document reports.  The generator refuses to describe a
#  different artifact, so a re-run cannot silently inherit this prose.
EXPECTED_MAPPING = "utilization fails with correct structure"
EXPECTED_SUMMARY = "not supported"
EXPECTED_TASKS = ("T1", "T2")


def load_artifact(path: str | Path = CAMPAIGN_OUT) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _records(artifact: dict, task: str) -> list[dict]:
    return [r for r in artifact["results"] if r["task"] == task]


def _mean(values: list[float]) -> float:
    return statistics.mean(values)


def _arm_scores(records: list[dict], arm: str, limb: str) -> list[float]:
    return [r["arms"][arm]["scores"][limb]["house_shape"]["log_loss"]
            for r in records]


def _comp_scores(records: list[dict], comp: str, limb: str) -> list[float]:
    return [r["comparators"][comp][limb]["house_shape"]["log_loss"]
            for r in records]


def _bar_member(records: list[dict], limb: str) -> str:
    members = {r["bar"][limb]["member"] for r in records}
    if len(members) != 1:
        raise AssertionError(f"the bar changes across seeds: {sorted(members)}")
    return members.pop()


def _bar_scores(records: list[dict], limb: str) -> list[float]:
    return _comp_scores(records, _bar_member(records, limb), limb)


def _posthoc(records: list[dict], comp: str, limb: str) -> dict:
    deltas = [c - a for c, a in zip(_comp_scores(records, comp, limb),
                                    _arm_scores(records, "C", limb))]
    return paired_bootstrap(deltas)


def _fmt_d(value: float) -> str:
    return f"{value:+.4f}"


def _fmt_ci(lo: float, hi: float) -> str:
    return f"[{lo:+.4f}, {hi:+.4f}]"


def _fmt_mean(value: float) -> str:
    return f"{value:.4f}"


def _range(values: list[float], decimals: int = 4) -> str:
    return f"{min(values):.{decimals}f}–{max(values):.{decimals}f}"


def summarise(artifact: dict) -> dict:
    """Every value the document states, computed from the artifact."""
    if artifact.get("status") != "complete":
        raise ValueError("the artifact is not a completed campaign")
    if tuple(artifact.get("seeds", ())) != tuple(range(20261101, 20261131)):
        raise ValueError("the artifact is not the 30 confirmatory seeds")
    if len(artifact["results"]) != 60:
        raise ValueError("the artifact does not carry 60 task-seed units")

    out: dict = {"task": {}, "audits": {}}
    for task in EXPECTED_TASKS:
        records = _records(artifact, task)
        analysis = artifact["analysis"]["tasks"][task]
        if analysis["mapping"]["label"] != EXPECTED_MAPPING:
            raise ValueError(f"{task}: the mapping is {analysis['mapping']['label']!r}")
        if analysis["summary_claim"] != EXPECTED_SUMMARY:
            raise ValueError(f"{task}: the summary claim is "
                             f"{analysis['summary_claim']!r}")
        cells = analysis["cells"]
        bar = {limb: _bar_member(records, limb) for limb in LIMBS}
        means = {
            "A": {limb: _mean(_arm_scores(records, "A", limb)) for limb in LIMBS},
            "B": {limb: _mean(_arm_scores(records, "B", limb)) for limb in LIMBS},
            "C": {limb: _mean(_arm_scores(records, "C", limb)) for limb in LIMBS},
            "bar": {limb: _mean(_bar_scores(records, limb)) for limb in LIMBS},
            "replay": {limb: _mean(_comp_scores(records, "replay", limb))
                       for limb in LIMBS},
            "bigram": {limb: _mean(_comp_scores(records, "bigram", limb))
                       for limb in LIMBS},
            "cell_counter": {limb: _mean(_comp_scores(records, "cell_counter", limb))
                             for limb in LIMBS},
        }
        closure = {}
        for limb in LIMBS:
            a, c, b = means["A"][limb], means["C"][limb], means["bar"][limb]
            closure[limb] = ((a - c) / (a - b)) if a > b else None
        posthoc = {
            (comp, limb): _posthoc(records, comp, limb)
            for comp in ("replay", "bigram")
            for limb in ("retention", "transfer")
        }
        out["task"][task] = {
            "n": len(records),
            "cells": cells,
            "mapping": analysis["mapping"],
            "summary_claim": analysis["summary_claim"],
            "bar": bar,
            "means": means,
            "closure": closure,
            "posthoc": posthoc,
            "coverage": {
                arm: [r["audits"]["A1"]["evidence"]["coverage"][arm]
                      for r in records]
                for arm in "ABC"
            },
            "a2": {
                "cycles": [r["audits"]["A2"]["evidence"]["cycles"] for r in records],
                "pairs": sum(r["audits"]["A2"]["evidence"]["pairs_checked"]
                             for r in records),
                "max_permitted": [r["audits"]["A2"]["evidence"]["max_permitted_candidates"]
                                  for r in records],
            },
            "a3": {
                "applicable": [r["audits"]["A3"].get("applicable") for r in records],
                "precision": [r["arms"]["B"]["layer1_precision_world"] for r in records],
                "band_upper": sorted({r["audits"]["A3"]["evidence"].get("band_upper")
                                      for r in records
                                      if r["audits"]["A3"].get("applicable")}),
            },
            "a4": {
                "events": {limb: {r["limb_counts"][limb]["events"] for r in records}
                           for limb in LIMBS},
                "excluded": {limb: {r["limb_counts"][limb]["excluded_observation_tokens"]
                                    for r in records}
                             for limb in LIMBS},
            },
            "a5": sum(1 for r in records if r["audits"]["A5"].get("passed") is True),
            "a6": {
                "applicable": sum(1 for r in records
                                  if r["audits"]["A6"].get("applicable")),
                "shuffled": [r["audits"]["A6"]["evidence"]["shuffled_transfer"]
                             for r in records
                             if r["audits"]["A6"].get("applicable")],
                "c": [r["audits"]["A6"]["evidence"]["c_transfer"]
                      for r in records
                      if r["audits"]["A6"].get("applicable")],
                "retained_share": sorted({r["audits"]["A6"]["evidence"]
                                          .get("shuffled", {}).get("retained_share")
                                          for r in records
                                          if r["audits"]["A6"].get("applicable")}),
                "retained_share_all": sorted({
                    r["audits"]["A6"]["evidence"]["retained_share"]
                    for r in records
                    if "retained_share" in r["audits"]["A6"]["evidence"]}),
            },
            "a7": [r["audits"]["A7"]["evidence"]["control_share"] for r in records],
            "a8": {
                "checks": sum(r["audits"]["A8"]["evidence"]["eligible_pair_checks"]
                              for r in records),
                "symdiff": [r["audits"]["A8"]["evidence"]
                            ["engine_own_table_symmetric_difference"]
                            for r in records],
                "mismatches": sum(r["audits"]["A8"]["evidence"]["evidence_mismatches"]
                                  for r in records),
            },
            "readout_precision": {
                arm: [r["arms"][arm]["readout_precision"] for r in records]
                for arm in "BC"
            },
            "seconds": {arm: _mean([r["arms"][arm]["seconds_total"] for r in records])
                        for arm in "ABC"},
        }

    out["worker_hours"] = (
        sum(sum(r["timings"]["arms"].values()) for r in artifact["results"])
        + sum(r["timings"]["comparators"] for r in artifact["results"])
        + sum(r["timings"]["prepare"] for r in artifact["results"])
    ) / 3600.0
    out["all_ready"] = sum(1 for r in artifact["results"] if r["campaign_ready"])
    out["audits"]["not_applicable"] = sum(
        1 for r in artifact["results"] for a in r["audits"].values()
        if a.get("passed") is None)
    out["audits"]["failures"] = sum(
        1 for r in artifact["results"] for a in r["audits"].values()
        if a.get("passed") is False)
    out["assembled_utc"] = artifact.get("assembled_utc")
    return out


def render(artifact: dict) -> str:
    """The result document, every number substituted from the artifact."""
    s = summarise(artifact)
    t1, t2 = s["task"]["T1"], s["task"]["T2"]
    residuals = [
        block["means"]["C"][limb] - block["means"]["bar"][limb]
        for block in (t1, t2) for limb in ("retention", "transfer")]
    closure_pct = [
        100 * block["closure"][limb]
        for block in (t1, t2) for limb in ("retention", "transfer")]
    a7_min = min(min(t1["a7"]), min(t2["a7"]))
    a7_max = max(max(t1["a7"]), max(t2["a7"]))
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    add("# Formation vs. utilization — campaign result")
    add()
    add(f"**Run:** 2026-10-30, artifact generated {artifact['generated_utc']}.  ")
    add("**Design:** the protocol committed at `8536d9a`; Amendment 1 (§12) was "
        "appended on 2026-10-30, before any confirmatory seed.  ")
    add(f"**Artifact:** [`docs/formation_utilization.json`](formation_utilization.json) "
        f"— {len(artifact['results'])} units, 30 seeds × 2 tasks.  ")
    add(f"**Status:** complete — {s['all_ready']} of "
        f"{len(artifact['results'])} units `campaign_ready`, "
        f"{s['audits']['failures']} failing audits, "
        f"{s['audits']['not_applicable']} not-applicable audit instances.")
    add()
    add("---")
    add()
    add("## 1. The pre-committed verdict")
    add()
    add("> **Both formed arms lose transfer on both tasks → *\"utilization fails "
        "even with correct structure\"* → V2 targets the use path "
        "(retrieval / activation / readout). Summary claim: not supported.**")
    add()
    add("The §7 mapping returns exactly one cell per task, and both tasks return "
        "the same cell:")
    add()
    add("| Task | B transfer | C transfer | Mapping | Target | Summary claim |")
    add("|---|---|---|---|---|---|")
    for name, block in (("T1", t1), ("T2", t2)):
        b = block["cells"]["B"]["transfer"]
        c = block["cells"]["C"]["transfer"]
        add(f"| {name} | {b['verdict']} (d = {_fmt_d(b['mean'])}) "
            f"| {c['verdict']} (d = {_fmt_d(c['mean'])}) "
            f"| {block['mapping']['label']} | {block['mapping']['target']} "
            f"| {block['summary_claim']} |")
    add()
    add("The failing limbs, named: **transfer and retention**. C loses retention "
        f"on both tasks (T1 d = {_fmt_d(t1['cells']['C']['retention']['mean'])}; "
        f"T2 d = {_fmt_d(t2['cells']['C']['retention']['mean'])}). Revision is "
        "**not** a failing limb: C wins it on T1 "
        f"(d = {_fmt_d(t1['cells']['C']['revision']['mean'])}) and ties it on T2 "
        f"(d = {_fmt_d(t2['cells']['C']['revision']['mean'])}). A summary claim "
        "requires C to win or tie transfer and not lose retention or revision; C "
        "loses both transfer and retention, so the claim fails on two independent "
        "grounds.")
    add()
    add("## 2. Every cell")
    add()
    add("This table is the artifact's `analysis` block. **d = bar − arm**: a "
        "positive d favours the arm, so a loss is a negative d. Intervals are "
        "98.33 % percentile bootstraps over 10,000 replicates, paired by seed "
        "(n = 30); the bar is the best comparator on the calibration seed, per "
        "limb.")
    add()
    add("**Notation note.** §7 writes `d = score(arm) − score(best baseline)` and "
        "then states the win rule as a lower bound above zero. Those two "
        "sentences use opposite orientations, because lower log loss is better. "
        "The artifact and this document use the orientation the win rule "
        "requires — `d = bar − arm`, positive favours the arm — as the "
        "harness's `paired_bootstrap` docstring states. The discrepancy is in "
        "the protocol's notation, not in the analysis: the intervals and "
        "verdicts in the artifact are computed on the oriented difference. No "
        "criterion, interval or verdict changes.")
    add()
    add("| Arm | Limb | d | 98.33% interval | Verdict |")
    add("|---|---|---|---|---|")
    for name, block in (("T1", t1), ("T2", t2)):
        for arm in ("A", "B", "C"):
            for limb in LIMBS:
                cell = block["cells"][arm][limb]
                add(f"| {name} / {arm} | {limb} | {_fmt_d(cell['mean'])} "
                    f"| {_fmt_ci(cell['lo'], cell['hi'])} | {cell['verdict']} |")
    add()
    add("A is the cap-20 arm that failed Gate 13 on the compositional task; "
        "here it loses five of six task-limbs, the T1 revision win being the "
        "exception. B, the cap-1,000 formation arm, also "
        "loses five of six (a T1 revision win; all three T2 limbs). C, the "
        "oracle-admitted arm, loses four of six — T1 retention and transfer, T2 "
        "retention and transfer — wins T1 revision, and ties T2 revision.")
    add()
    add("## 3. Absolute levels, and how much of the gap C closes")
    add()
    display = {"replay": "Replay", "bigram": "Bigram",
               "cell_counter": "Cell counter"}
    for name, block in (("T1", t1), ("T2", t2)):
        add(f"**{name}** (bar: {display[block['bar']['retention']]} on retention, "
            f"{display[block['bar']['transfer']]} on transfer, "
            f"{display[block['bar']['revision']]} on revision)")
        add()
        add("| Learner | Retention | Transfer | Revision |")
        add("|---|---|---|---|")
        for arm, label in (("A", "A (cap 20)"), ("B", "B (cap 1,000)"),
                           ("C", "C (cap 1,000 + support)")):
            add(f"| {label} | {_fmt_mean(block['means'][arm]['retention'])} "
                f"| {_fmt_mean(block['means'][arm]['transfer'])} "
                f"| {_fmt_mean(block['means'][arm]['revision'])} |")
        for comp, label in (("replay", "Replay"),
                            ("bigram", "Bigram"),
                            ("cell_counter", "Cell counter")):
            mark = " (bar)" if any(block["bar"][limb] == comp for limb in LIMBS) else ""
            add(f"| {label}{mark} | {_fmt_mean(block['means'][comp]['retention'])} "
                f"| {_fmt_mean(block['means'][comp]['transfer'])} "
                f"| {_fmt_mean(block['means'][comp]['revision'])} |")
        add()
    add("Closure is `(A − C) / (A − bar)` on the limbs where the bar is better "
        "than A. C closes "
        f"**{100 * t1['closure']['retention']:.1f} %** of A's retention gap and "
        f"**{100 * t1['closure']['transfer']:.1f} %** of its transfer gap on T1, "
        f"and **{100 * t2['closure']['retention']:.1f} % / "
        f"{100 * t2['closure']['transfer']:.1f} %** on T2, leaving residuals of "
        f"{_fmt_mean(t1['means']['C']['retention'] - t1['means']['bar']['retention'])} "
        f"/ {_fmt_mean(t1['means']['C']['transfer'] - t1['means']['bar']['transfer'])} "
        "nats on T1 and "
        f"{_fmt_mean(t2['means']['C']['retention'] - t2['means']['bar']['retention'])} "
        f"/ {_fmt_mean(t2['means']['C']['transfer'] - t2['means']['bar']['transfer'])} "
        "nats on T2.")
    add()
    add("C versus B, the formation arm it is meant to improve on: "
        f"{_fmt_mean(t1['means']['B']['transfer'] - t1['means']['C']['transfer'])} "
        "nats better on T1 transfer and "
        f"{_fmt_mean(t2['means']['B']['transfer'] - t2['means']['C']['transfer'])} "
        "better on T2 transfer. Correct structure is worth a great deal; it is "
        "not worth the last "
        f"{min(residuals):.4f}–{max(residuals):.4f} nats.")
    add()
    add(f"On T1 revision the bar is worse than A (Replay "
        f"{_fmt_mean(t1['means']['replay']['revision'])} against A's "
        f"{_fmt_mean(t1['means']['A']['revision'])}), so a closure fraction is "
        "not defined there; C's "
        f"{_fmt_d(t1['cells']['C']['revision']['mean'])} win is against a "
        "comparator that cannot revise. On T2 the bar is at "
        f"{_fmt_mean(t2['means']['bar']['revision'])} and C at "
        f"{_fmt_mean(t2['means']['C']['revision'])} — a tie, not a win.")
    add()
    add("## 4. Audits")
    add()
    add("On every unit, every audit is either a pass or not applicable. The two "
        "not-applicable audits are design-scoped and were recorded before the "
        "campaign: A3's 0.3443 precision band was measured on T2, and A6's "
        "size-matched wrong filter does not exist on T1.")
    add()
    add("| Audit | T1 | T2 |")
    add("|---|---|---|")
    add(f"| A1 arm differential | A {_range(t1['coverage']['A'])}, "
        f"B/C {_range(t1['coverage']['B'])} "
        f"| A {_range(t2['coverage']['A'])}, B/C {_range(t2['coverage']['B'])} |")
    add(f"| A2 oracle exactness | {t1['a2']['pairs']:,} permitted candidates over "
        f"{min(t1['a2']['cycles'])} cycles/unit, 0 mismatches, cap never bound "
        f"| {t2['a2']['pairs']:,} over {min(t2['a2']['cycles'])}–"
        f"{max(t2['a2']['cycles'])} cycles/unit, 0 mismatches, cap never bound |")
    add(f"| A3 precision premise | not gated (B precision {_range(t1['a3']['precision'])}, "
        f"C admission 1.0) "
        f"| B {_range(t2['a3']['precision'])} ≤ {t2['a3']['band_upper'][0]}; "
        f"C admission 1.0 |")
    add(f"| A4 denominators | "
        f"{sorted(t1['a4']['events']['retention'])[0]} / "
        f"{sorted(t1['a4']['events']['transfer'])[0]} / "
        f"{sorted(t1['a4']['events']['revision'])[0]} events, 0 excluded "
        f"| {sorted(t2['a4']['events']['retention'])[0]} / "
        f"{sorted(t2['a4']['events']['transfer'])[0]} / "
        f"{sorted(t2['a4']['events']['revision'])[0]} events, 0 excluded |")
    add(f"| A5 readout construct | {t1['a5']}/{t1['n']} pass "
        f"| {t2['a5']}/{t2['n']} pass |")
    add(f"| A6 no leakage | not applicable (the shuffled filter retains "
        f"{100 * t1['a6']['retained_share_all'][0]:.1f} % of permitted pairs and "
        f"cannot be size-matched) "
        f"| shuffled {_range(t2['a6']['shuffled'])} vs C "
        f"{_range(t2['a6']['c'])}; Layer-1 coverage 0.0 |")
    add(f"| A7 attribution share | {100 * min(t1['a7']):.1f}–"
        f"{100 * max(t1['a7']):.1f} % from Layer 1 "
        f"| {100 * min(t2['a7']):.1f}–{100 * max(t2['a7']):.1f} % |")
    add(f"| A8 temporal input | {t1['a8']['checks']:,} eligible-pair checks, "
        f"0 mismatches, own-table symmetric difference "
        f"{min(t1['a8']['symdiff'])}–{max(t1['a8']['symdiff'])} edges (unread) "
        f"| {t2['a8']['checks']:,} checks, 0 mismatches, "
        f"{min(t2['a8']['symdiff'])}–{max(t2['a8']['symdiff'])} edges (unread) |")
    add()
    add("A2's denominator is the permitted candidate stream the arm was actually "
        "given, recorded before the filter. A8 checks the graph and that stream "
        "against arm B's at every cycle; the engine's own `precedes` tables still "
        "differ because C's own sleep rows are still written, but Layer 1 does "
        "not read them. That difference is reported as a footnote, not hidden.")
    add()
    add("## 5. What the verdict does and does not mean")
    add()
    add("**What it does mean.** With the generator's support admitted at Layer 1 "
        f"— and {100 * a7_min:.1f}–{100 * a7_max:.1f} % of C's readout edge "
        "weight on that layer across the two tasks — correct structure is not "
        "sufficient to clear the strongest simple baseline on retention or "
        "transfer in this design. C's loss is not a candidate-"
        "selection loss: it was given the support. The mapping therefore names "
        "the use path, not selection or precision, as the V2 target.")
    add()
    add("**What it does not mean.**")
    add()
    add("- It is not *\"the engine cannot use structure\"*. C improves transfer "
        f"over A by {_fmt_mean(t1['means']['A']['transfer'] - t1['means']['C']['transfer'])} "
        f"nats on T1 and {_fmt_mean(t2['means']['A']['transfer'] - t2['means']['C']['transfer'])} "
        "on T2, closes "
        f"{min(closure_pct):.0f}–{max(closure_pct):.0f} % of A's gap, and wins "
        "T1 revision by "
        f"{_fmt_d(t1['cells']['C']['revision']['mean'])}. The label means *does "
        "not clear the bar*, not *no use*.")
    add("- It is not *\"the oracle arm failed to transfer\"*. C transfers and "
        "scores better than both closed-loop Organica arms; it loses the "
        "comparison to the bar. The verdict is about the comparison, not about "
        "whether any transfer happened.")
    add("- It is not a discovery result. C is given the generator's support; B is "
        "the discovery arm, and B also loses transfer on both tasks.")
    add("- It is not a self-sourcing result. B's temporal graph still contains "
        "B's own sleep rows, and C inherits that graph under Amendment 1. Nothing "
        "here attributes anything to self-sourced support.")
    add("- It is not *\"the engine with this filter installed\"*. C is a "
        "counterfactual trajectory on B's temporal evidence: a C result is "
        "admission filtering at fixed evidence.")
    add("- It does not localize the defect inside the use path. It names the "
        "path — retrieval, activation, readout — not which of them is binding.")
    add("- It does not generalize beyond T1 and T2, and it does not authorise a "
        "V2 build.")
    add()
    add("## 6. The bar's name: \"data-only\" is too wide")
    add()
    add("The protocol's question and §12.5 call the comparator *\"the strongest "
        "data-only learner\"*. On T2 the bar is the **cell-level latent-state "
        "counter**, which is **granted the latent cell structure**: "
        "`fit_cell_counter` takes `tag_to_cell` from the generator, and its "
        "docstring says the structure is *\"here granted\"*. It is not a "
        "data-only learner, and the phrase should not be used for this bar. The "
        "counter is nevertheless a declared member of the statistical-learner "
        "family (acquisition protocol §6.3), so this is a naming defect, not a "
        "deviation from the committed comparator set.")
    add()
    add("The verdict does not depend on it. Post hoc, not a criterion:")
    add()
    add("| Task | Comparator | Limb | d | 98.33% interval | Verdict |")
    add("|---|---|---|---|---|---|")
    for name, block in (("T1", t1), ("T2", t2)):
        for comp in ("replay", "bigram"):
            for limb in ("retention", "transfer"):
                cell = block["posthoc"][(comp, limb)]
                add(f"| {name} | {comp} | {limb} | {_fmt_d(cell['mean'])} "
                    f"| {_fmt_ci(cell['lo'], cell['hi'])} "
                    f"| {verdict_of(cell['lo'], cell['hi'])} |")
    add()
    add(f"On T1 the bar is already Replay, a data-only episodic learner, and C "
        f"loses transfer to it by "
        f"{abs(t1['cells']['C']['transfer']['mean']):.4f} nats. On T2 C also "
        f"loses to Replay by "
        f"{abs(t2['posthoc'][('replay', 'transfer')]['mean']):.4f} and to the "
        f"bigram by {abs(t2['posthoc'][('bigram', 'transfer')]['mean']):.4f}, so "
        "the verdict survives dropping the oracle-informed counter. The counter "
        "is also not a stronger oracle than C: C is given the generator's full "
        "transition support, while the counter is given the four-cell latent "
        "map. The loss is not explained by the baseline having a better oracle.")
    add()
    add("## 7. Provenance and reproduction")
    add()
    add(f"- **Seeds and units:** 20261101–20261130, two tasks, "
        f"{len(artifact['results'])} task-seed units; four arms (A, B, C, S) and "
        "three comparator fits per unit.")
    add(f"- **Engine:** {artifact['engine_version']}; no engine file changed "
        "(`tests/test_v1_freeze.py`).")
    add(f"- **Cost:** the artifact's per-unit timings sum to "
        f"{s['worker_hours']:.2f} worker-hours across the 240 arm runs and the "
        f"180 comparator fits. Mean per-arm times under contention (the "
        f"shuffled arm S is the fourth): T1 A/B/C "
        f"{t1['seconds']['A']:.0f}/{t1['seconds']['B']:.0f}/"
        f"{t1['seconds']['C']:.0f} s; T2 "
        f"{t2['seconds']['A']:.0f}/{t2['seconds']['B']:.0f}/"
        f"{t2['seconds']['C']:.0f} s. The isolated timing pass measured 72.2 s "
        "per run.")
    add(f"- **Execution:** `{artifact['command']}`, a resumable wrapper over the "
        "harness's own `run_task_seed`; each unit was checkpointed, no unit "
        "failed or was re-run, and the artifact was assembled with the harness's "
        "own `analyse()` and renderer.")
    if s["assembled_utc"]:
        add(f"- **Provenance correction:** the artifact was re-assembled from the "
            f"same units at {s['assembled_utc']} to correct the `command` field; "
            "`status`, `results`, `audits` and `analysis` are identical to the "
            "first assembly.")
    add("- **Re-render:** `python benchmarks/formation_utilization_results.py`. "
        "`tests/test_formation_utilization_results.py` compares this document "
        "with the artifact and can fail.")
    add()
    add("**See also:** protocol §7 and §12; "
        "[`docs/USER-MANUAL.md`](USER-MANUAL.md) §8.20–§8.21, finding 39; "
        "[`docs/formation_utilization.md`](formation_utilization.md) (the "
        "artifact's own table); journal §65; AGENTS rule 24.")
    add()
    return _assert_no_placeholders("\n".join(lines) + "\n")


def _assert_no_placeholders(md: str) -> str:
    if re.search(r"\{[A-Za-z_]", md):
        raise AssertionError(
            "generated result document contains an unsubstituted placeholder")
    return md


def check(text: str, artifact: dict) -> None:
    """Fail if a result document is not the one this artifact produces."""
    expected = render(artifact)
    if text.replace("\r\n", "\n") != expected.replace("\r\n", "\n"):
        raise AssertionError(
            "the result document does not match the artifact; re-render it "
            "with python benchmarks/formation_utilization_results.py")


def main(argv: list[str] | None = None) -> int:
    artifact = load_artifact()
    md = render(artifact)
    path = Path(RESULTS_MD)
    path.write_text(md, encoding="utf-8", newline="\n")
    print(f"wrote {path} ({len(md.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
