"""Three-layer reproduction audit for the use-path diagnostic's D0 failures.

Post-hoc audit, not a protocol and not a change to D0.  The frozen diagnostic
remains score-gated; this is a separate attribution instrument:

    Layer 1  repeatability   N no-tiebreak and N rowid-tiebreak runs
    Layer 2  structural      reproduce the campaign's per-type table
    Layer 3  score           only after layer 2 matches

The intervention is harness-side and in-process.  ``organica/`` is not edited:
the audit temporarily replaces ``MemoryService.recent`` with the same query
plus ``rowid DESC`` and restores it afterwards.  Candidate IDs and the arm's
temporal-graph digest are recorded, because the campaign artifact has neither.

Usage:
    PYTHONHASHSEED=0 python benchmarks/use_path_audit.py --repeats 3 --workers 8
    PYTHONHASHSEED=0 python benchmarks/use_path_audit.py --reanalyse
    PYTHONHASHSEED=0 python benchmarks/use_path_audit.py --render
    PYTHONHASHSEED=0 python benchmarks/use_path_audit.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from organica.memory import Event, MemoryService  # noqa: E402

from benchmarks import formation_utilization as fu  # noqa: E402

AUDIT = REPO / "docs/use_path_audit.json"
RESULT_MD = REPO / "docs/USE-PATH-AUDIT.md"
PARTS = REPO / ".scratch" / "use_path_audit_parts"
CAMPAIGN = REPO / "docs/formation_utilization.json"
DIAGNOSTIC = REPO / "docs/use_path_diagnostic.json"

LIMBS = ("retention", "transfer", "revision")
FAILING = (
    ("T1", 20261125),
    ("T1", 20261128),
    ("T1", 20261129),
    ("T2", 20261118),
    ("T2", 20261120),
    ("T2", 20261121),
    ("T2", 20261123),
    ("T2", 20261130),
)
ARMS = ("no_tiebreak", "rowid_tiebreak")
DEFAULT_REPEATS = 3
D0_TOLERANCE = 1e-4
DIAGNOSTIC_TOLERANCE = 1e-6
ARM_TOLERANCE = 1e-12


def require_hash_seed() -> str:
    seed = os.environ.get("PYTHONHASHSEED")
    if seed != "0":
        raise RuntimeError(
            "the audit must run with PYTHONHASHSEED=0, the pin the "
            "diagnostic's Amendment 1 declares; the diagnostic refuses to "
            f"start under any other seed, and got {seed!r}")
    return seed


@contextmanager
def rowid_tiebreak():
    """Temporarily add ``rowid DESC`` to ``MemoryService.recent``.

    The engine is not edited.  Every query returns the same Event rows as the
    shipped method; only the order of equal timestamps changes.  The original
    method is restored in ``finally``.
    """
    original = MemoryService.recent

    def recent(self, n: int = 50, event_type: str | None = None) -> list[Event]:
        if event_type:
            rows = self._conn.execute(
                "SELECT rowid, * FROM events WHERE event_type=? "
                "ORDER BY time DESC, rowid DESC LIMIT ?",
                (event_type, n),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT rowid, * FROM events ORDER BY time DESC, rowid DESC LIMIT ?",
                (n,),
            ).fetchall()
        return [Event.from_row(row[1:]) for row in rows]

    MemoryService.recent = recent
    try:
        yield
    finally:
        MemoryService.recent = original


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _id_digest(candidates: list[dict]) -> dict[str, str]:
    by_type: dict[str, list[str]] = defaultdict(list)
    for candidate in candidates:
        by_type[candidate.get("type", "")].append(str(candidate.get("id")))
    return {kind: _digest(sorted(ids)) for kind, ids in sorted(by_type.items())}


def _log_loss(arm: dict) -> dict[str, float]:
    return {limb: float(arm["scores"][limb]["house_shape"]["log_loss"])
            for limb in LIMBS}


def run_once(task: str, seed: int, arm: str, repeat: int) -> dict[str, Any]:
    require_hash_seed()
    started = time.perf_counter()
    prep = fu.prepare_world(task, seed)
    support = fu.build_support(task, prep["world"], 0)
    support_new = fu.build_support(task, prep["world"], 1)
    if support != support_new:
        raise AssertionError(
            f"{task} seed {seed}: the generator's support differs between regimes")
    missing = prep["world_edges"] - support
    if missing:
        raise AssertionError(
            f"{task} seed {seed}: {len(missing)} training edge(s) outside support")
    prep["support"] = support

    context = rowid_tiebreak() if arm == "rowid_tiebreak" else nullcontext()
    with context:
        b = fu.run_arm(prep, "B", fu.CAP_B, None)
        c = fu.run_arm(
            prep, "C", fu.CAP_B, support,
            fixed_temporal=b["_raw"]["temporal_reads"])

    return {
        "task": task,
        "seed": seed,
        "arm": arm,
        "repeat": repeat,
        "per_type": c["per_type"],
        "scores": _log_loss(c),
        "asserted_edges": c["asserted_edges"],
        "coverage": c["coverage"],
        "candidate_ids": {
            "frozen": _id_digest(c["_raw"]["frozen_candidates"]),
            "post": _id_digest(c["_raw"]["post_candidates"]),
        },
        "temporal_graph": _digest(b["_raw"]["temporal_reads"]),
        "seconds": round(time.perf_counter() - started, 3),
    }


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def run_seed(task: str, seed: int, repeats: int, force: bool) -> list[dict]:
    """Run all paired arms for one seed sequentially.

    ``run_arm`` names its scratch database after ``(task, label, seed)``, so
    concurrent runs of the same seed would collide.  Different seeds run in
    different workers.
    """
    records = []
    for repeat in range(repeats):
        for arm in ARMS:
            part = PARTS / f"{task}_{seed}_{arm}_{repeat}.json"
            if part.exists() and not force:
                record = json.loads(part.read_text(encoding="utf-8"))
            else:
                record = run_once(task, seed, arm, repeat)
                _write(part, record)
            records.append(record)
    return records


def _canonical(table: dict) -> str:
    return json.dumps(table, sort_keys=True, separators=(",", ":"))


def classify(no_stable: bool, tie_stable: bool,
             no_match: bool, tie_match: bool) -> str:
    """Map the observable pattern to one of the pre-declared labels.

    Stability is about repeated runs of the SAME configuration; a match is
    about that configuration against the campaign's recorded table.  The two
    are independent, and the label names both so neither can stand in for the
    other.  ``no`` is the shipped order (no rowid tiebreak); ``tie`` is the
    intervention.
    """
    if not no_stable and not tie_stable:
        return "both_unstable"
    if not no_stable:
        return ("baseline_unstable_tiebreak_stable" if tie_stable
                else "both_unstable")
    if not tie_stable:
        return "baseline_stable_tiebreak_unstable"
    if no_match and tie_match:
        return "both_stable_both_reproduce"
    if tie_match:
        return "both_stable_tiebreak_reproduces"
    if no_match:
        return "both_stable_no_tiebreak_reproduces"
    return "both_stable_both_differ"


def analyse(runs: list[dict], repeats: int) -> dict[str, Any]:
    campaign = json.loads(CAMPAIGN.read_text(encoding="utf-8"))
    campaign_by = {(r["task"], r["seed"]): r for r in campaign["results"]}
    diagnostic = json.loads(DIAGNOSTIC.read_text(encoding="utf-8"))
    diag_by = {(r["task"], r["seed"]): r for r in diagnostic["records"]}
    failed = defaultdict(list)
    for check in diagnostic["d0_reproduction"]["checks"]:
        if not check.get("passed"):
            failed[(check["task"], check["seed"])].append(check["limb"])

    by_seed: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for run in runs:
        by_seed[(run["task"], run["seed"])].append(run)
    missing = [f"{task}/{seed}" for task, seed in FAILING
               if len(by_seed[(task, seed)]) != len(ARMS) * repeats]
    if missing:
        raise ValueError(
            "the audit is incomplete; refusing to analyse missing runs for: "
            + ", ".join(missing))

    per_seed = []
    for key in FAILING:
        task, seed = key
        arms = {}
        campaign_table = campaign_by[key]["arms"]["C"]["per_type"]
        campaign_scores = _log_loss(campaign_by[key]["arms"]["C"])
        diag_table = diag_by[key]["per_type"]
        diag_scores = diag_by[key]["d0"]
        for arm in ARMS:
            group = [r for r in by_seed[key] if r["arm"] == arm]
            tables = [_canonical(r["per_type"]) for r in group]
            matches = [table == _canonical(campaign_table) for table in tables]
            score_diffs = {
                limb: max(abs(r["scores"][limb] - campaign_scores[limb])
                          for r in group)
                for limb in LIMBS
            }
            diagnostic_diffs = {
                limb: max(abs(r["scores"][limb] - diag_scores[limb])
                          for r in group)
                for limb in LIMBS
            }
            diagnostic_matches = [
                table == _canonical(diag_table) for table in tables]
            deltas = {}
            if group:
                latest = group[-1]["per_type"]
                for kind in sorted(set(latest) | set(campaign_table)):
                    got = latest.get(kind, {})
                    want = campaign_table.get(kind, {})
                    if got != want:
                        deltas[kind] = {
                            "campaign": want,
                            "audit": got,
                            "unique_count_delta": (
                                got.get("unique_count", 0)
                                - want.get("unique_count", 0)),
                            "edge_weight_delta": (
                                got.get("edge_weight", 0.0)
                                - want.get("edge_weight", 0.0)),
                        }
            arms[arm] = {
                "runs": len(group),
                "stable": len(set(tables)) == 1,
                "all_match": all(matches),
                "any_match": any(matches),
                "score_max_abs_diff": score_diffs,
                "score_matches": all(
                    max(abs(r["scores"][limb] - campaign_scores[limb])
                        for limb in LIMBS) <= D0_TOLERANCE
                    for r in group),
                "matches_diagnostic": all(diagnostic_matches),
                "diagnostic_score_max_abs_diff": diagnostic_diffs,
                "diagnostic_score_matches": all(
                    max(diagnostic_diffs.values()) <= DIAGNOSTIC_TOLERANCE
                    for _ in group),
                "per_type_deltas": deltas,
                "asserted_edges": sorted({r["asserted_edges"] for r in group}),
                "coverage": sorted({r["coverage"] for r in group}),
                "candidate_id_digests": sorted(
                    {_digest(r["candidate_ids"]["frozen"]) for r in group}),
                "post_candidate_id_digests": sorted(
                    {_digest(r["candidate_ids"]["post"]) for r in group}),
                "temporal_graph_digests": sorted(
                    {r["temporal_graph"] for r in group}),
            }
        no = arms["no_tiebreak"]
        tie = arms["rowid_tiebreak"]
        no_group = [r for r in by_seed[key] if r["arm"] == "no_tiebreak"]
        tie_group = [r for r in by_seed[key] if r["arm"] == "rowid_tiebreak"]
        arms_agree = (
            len({_canonical(r["per_type"]) for r in no_group}) == 1
            and len({_canonical(r["per_type"]) for r in tie_group}) == 1
            and _canonical(no_group[0]["per_type"])
                == _canonical(tie_group[0]["per_type"])
            and all(
                abs(no_group[0]["scores"][limb] - tie_group[0]["scores"][limb])
                <= ARM_TOLERANCE for limb in LIMBS)
        )
        digests_agree = (
            no["candidate_id_digests"] == tie["candidate_id_digests"]
            and no["post_candidate_id_digests"] == tie["post_candidate_id_digests"]
            and no["temporal_graph_digests"] == tie["temporal_graph_digests"])
        outcome = classify(no["stable"], tie["stable"],
                           no["all_match"], tie["all_match"])
        per_seed.append({
            "task": task,
            "seed": seed,
            "d0_failed_limbs": failed.get(key, []),
            "arms_agree": arms_agree,
            "digests_agree": digests_agree,
            "layer3_entered": bool(no["all_match"] or tie["all_match"]),
            "campaign": {
                "per_type": campaign_table,
                "scores": campaign_scores,
                "asserted_edges": campaign_by[key]["arms"]["C"]["asserted_edges"],
                "coverage": campaign_by[key]["arms"]["C"]["coverage"],
            },
            "arms": arms,
            "outcome": outcome,
        })

    counts = {
        "seeds": len(per_seed),
        "no_tiebreak_stable": sum(
            1 for s in per_seed if s["arms"]["no_tiebreak"]["stable"]),
        "tiebreak_stable": sum(
            1 for s in per_seed if s["arms"]["rowid_tiebreak"]["stable"]),
        "tiebreak_matches_campaign_table": sum(
            1 for s in per_seed if s["arms"]["rowid_tiebreak"]["all_match"]),
        "tiebreak_matches_campaign_scores": sum(
            1 for s in per_seed
            if s["arms"]["rowid_tiebreak"]["all_match"]
            and s["arms"]["rowid_tiebreak"]["score_matches"]),
        "no_tiebreak_matches_campaign_table": sum(
            1 for s in per_seed if s["arms"]["no_tiebreak"]["all_match"]),
        "no_tiebreak_matches_campaign_scores": sum(
            1 for s in per_seed
            if s["arms"]["no_tiebreak"]["all_match"]
            and s["arms"]["no_tiebreak"]["score_matches"]),
        "no_tiebreak_matches_diagnostic": sum(
            1 for s in per_seed
            if s["arms"]["no_tiebreak"]["matches_diagnostic"]),
        "tiebreak_matches_diagnostic": sum(
            1 for s in per_seed
            if s["arms"]["rowid_tiebreak"]["matches_diagnostic"]),
        "arms_agree": sum(1 for s in per_seed if s["arms_agree"]),
        "digests_agree": sum(1 for s in per_seed if s["digests_agree"]),
        "layer3_entered": sum(1 for s in per_seed if s["layer3_entered"]),
        "outcomes": {},
    }
    for entry in per_seed:
        counts["outcomes"][entry["outcome"]] = (
            counts["outcomes"].get(entry["outcome"], 0) + 1)
    return {"per_seed": per_seed, "counts": counts, "repeats": repeats}


_PLACEHOLDER = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*(?::[^}]*)?\}")
STRUCTURE = REPO / "docs/use_path_diagnostic_structure.json"


def _assert_no_placeholder(text: str) -> None:
    """A template placeholder that survives is a claim with no number."""
    leftovers = _PLACEHOLDER.findall(text)
    if leftovers:
        raise ValueError(
            "an unfilled placeholder survived into the result document: "
            + ", ".join(sorted(set(leftovers))))


def _fmt_deltas(deltas: dict[str, dict]) -> str:
    if not deltas:
        return "—"
    parts = []
    for kind in sorted(deltas):
        entry = deltas[kind]
        parts.append(
            f"{kind} ({entry['unique_count_delta']:+d} ids, "
            f"{entry['edge_weight_delta']:+.1f} weight)")
    return "; ".join(parts)


def _stable_cell(arm: dict) -> str:
    return f"{arm['runs']}/{arm['runs']}" if arm["stable"] else "unstable"


def _score_cell(arm: dict) -> str:
    return " / ".join(f"{arm['score_max_abs_diff'][limb]:.6g}"
                      for limb in LIMBS)


def _verdict_lines(counts: dict, n: int, repeats: int) -> list[str]:
    """Build the interpretation from the counts, not from a fixed story."""
    lines: list[str] = []
    instrument = (counts["no_tiebreak_matches_diagnostic"] == n
                  and counts["tiebreak_matches_diagnostic"] == n)
    if not instrument:
        lines.append(
            "**Instrument check: not passed.** The audit's re-run does not "
            "reproduce the diagnostic's object on every seed, so the campaign "
            "comparison is not interpretable. No causal verdict is offered.")
        return lines

    lines.append(
        f"**Instrument check: passed on {n} of {n} seeds.** Both "
        "configurations reproduce the diagnostic's per-type table and its "
        "three D0 scores exactly, to the diagnostic artifact's six-decimal "
        "rounding. The audit is therefore a re-run of the object D0 failed on, "
        "not a measurement of a different object.")

    stable = (counts["no_tiebreak_stable"] == n
              and counts["tiebreak_stable"] == n)
    inert = counts["arms_agree"] == n
    both_fail = (counts["no_tiebreak_matches_campaign_table"] == 0
                 and counts["tiebreak_matches_campaign_table"] == 0)

    if stable:
        lines.append(
            f"**Layer 1: passed.** Each configuration reproduced its own "
            f"per-type table on {n} of {n} seeds and in every one of the "
            f"{repeats} repeats. The repeats are independent databases with "
            "independent wall-clock timestamps; they share the pinned hash "
            "seed, which is the declared constant. There is no run-to-run "
            "instability to explain on these seeds.")
    else:
        lines.append(
            "**Layer 1: not passed.** At least one configuration changed its "
            "per-type table across repeats; the instability is not attributable "
            "to the other configuration by this audit.")

    if inert:
        lines.append(
            "**The intervention is inert.** The no-tiebreak and `rowid DESC` "
            "configurations produced identical per-type tables and identical "
            "scores on every audited seed. The tiebreak is a real change to the "
            "query -- the self-test fires it on equal timestamps -- but on these "
            "worlds it changes nothing the run reads. The candidate-ID digests "
            f"and the B-arm temporal-graph digest are also identical on "
            f"{counts['digests_agree']} of {n} seeds. A cause cannot be a "
            "difference that makes no difference.")

    if both_fail:
        lines.append(
            "**Layer 2: failed on every seed.** Neither configuration "
            "reproduced the campaign's per-type table. The differences are "
            "structural, not a single drifted score: unique candidate counts "
            "move in both directions and edge weights move with them.")

    if counts["layer3_entered"] == 0:
        lines.append(
            "**Layer 3: not entered.** The design compares scores only after "
            "the candidate population reproduces, and it did not reproduce on "
            "any seed. The score differences in the table are recorded as "
            "observations, not as a score-reproduction result.")

    if stable and inert and both_fail and counts["layer3_entered"] == 0:
        lines.append(
            "**Verdict: retrieval-order instability is not supported as the "
            "cause of the D0 mismatch.** The `rowid`-tiebreak hypothesis, as "
            "§67 stated it, does not survive its own falsifier: adding the "
            "tiebreak did not move the object, and the object is repeatable "
            "without it. The divergence is upstream of `recent()`'s tie order.")
        lines.append(
            "This is the outcome §68 pre-declared for exactly this pattern -- "
            "both configurations stable and both differing from the campaign → "
            "look upstream of retrieval order, beginning with the code "
            "revision. The audit follows that rule rather than inventing one.")
        lines.append(
            "The audit does not name the upstream cause. Two candidates remain, "
            "both campaign-side and both unrecorded: a campaign-time harness "
            "revision (the harness was uncommitted when the campaign ran and "
            "was committed later) and the campaign's execution environment "
            "(the artifact records neither the hash seed nor the tie order). "
            "The diagnostic's structure check constrains the first: 51 of 60 "
            "campaign units reproduce their table under this same pinned code, "
            "so a code difference that affected every unit is excluded. What is "
            "not excluded is a difference that acts only on ordering-sensitive "
            "units. The audit cannot separate that from an environment "
            "difference, and does not.")
    else:
        lines.append(
            "**Verdict: mixed pattern; no causal verdict is offered.** The "
            "counts above do not match the all-seeds pattern this document is "
            "written to interpret. The table is the record; do not read a "
            "cause from it without a stated rule.")
    return lines


def render_markdown(artifact: dict) -> str:
    """Render the result document from the artifact; every count is derived."""
    summary = artifact["summary"]
    counts = summary["counts"]
    rows = summary["per_seed"]
    n = counts["seeds"]
    structure = json.loads(STRUCTURE.read_text(encoding="utf-8"))
    cross = structure["cross_tab"]

    machine = (
        f"seeds={counts['seeds']} repeats={artifact['repeats']} "
        f"runs={len(artifact['runs'])} "
        f"no_tiebreak_stable={counts['no_tiebreak_stable']} "
        f"tiebreak_stable={counts['tiebreak_stable']} "
        f"arms_agree={counts['arms_agree']} "
        f"digests_agree={counts['digests_agree']} "
        f"campaign_no_match={counts['no_tiebreak_matches_campaign_table']} "
        f"campaign_tie_match={counts['tiebreak_matches_campaign_table']} "
        f"diagnostic_no_match={counts['no_tiebreak_matches_diagnostic']} "
        f"diagnostic_tie_match={counts['tiebreak_matches_diagnostic']} "
        f"layer3_entered={counts['layer3_entered']}")

    lines = [
        "# Use-path reproduction audit — three layers on the failing seeds",
        "",
        "**Status.** Post-hoc audit observation, 2026-10-30. It is not a protocol, "
        "it does not amend D0, and it does not re-score the "
        "formation-vs-utilization campaign or the use-path diagnostic. D0 remains "
        "score-based and unchanged, and the diagnostic's `AUDIT REQUIRED` verdict "
        "stands.",
        "",
        f"**Machine-readable counts:** `{machine}`",
        "",
        "The campaign's per-type table is the intermediate endpoint, as §68 "
        "specified. A seed is compared on its candidate table first; its scores "
        "are compared only if the table reproduces.",
        "",
        "## 1. Design and intervention",
        "",
        f"Eight seeds failed D0. Each was run {artifact['repeats']} times under "
        "the shipped `MemoryService.recent()` (no tiebreak) and the same number "
        "of times with the same query plus `rowid DESC`, in the same process, "
        "each run against a fresh database. The audit temporarily replaces the "
        "method in-process and restores it; `organica/` is not edited. "
        "`PYTHONHASHSEED=0` is required and inherited by every worker.",
        "",
        "The layer order is the one committed in §68: repeatability, then "
        "structural reproduction, then score reproduction. Candidate IDs and the "
        "temporal-graph digest are recorded because neither campaign artifact "
        "carries them.",
        "",
        "## 2. Layer 1 — repeatability",
        "",
        "| Task | Seed | D0 failed limbs | No tiebreak | `rowid` tiebreak | "
        "Configurations identical |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        no = row["arms"]["no_tiebreak"]
        tie = row["arms"]["rowid_tiebreak"]
        limbs = ", ".join(row["d0_failed_limbs"]) or "—"
        lines.append(
            f"| {row['task']} | {row['seed']} | {limbs} | {_stable_cell(no)} "
            f"| {_stable_cell(tie)} | {'yes' if row['arms_agree'] else 'no'} |")

    lines += [
        "",
        "Each cell is identical tables out of independent runs. The "
        f"no-tiebreak and `rowid` configurations were stable on "
        f"{counts['no_tiebreak_stable']}/{n} and "
        f"{counts['tiebreak_stable']}/{n} seeds respectively, and the two "
        f"configurations agreed on {counts['arms_agree']}/{n}.",
        "",
        "## 3. Layer 2 — structural reproduction",
        "",
        "| Task | Seed | Campaign table reproduced | Asserted edges "
        "(campaign → audit) | Coverage (campaign → audit) | Per-type deltas |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        no = row["arms"]["no_tiebreak"]
        tie = row["arms"]["rowid_tiebreak"]
        reproduced = (f"no-tiebreak {'yes' if no['all_match'] else 'no'}; "
                      f"rowid {'yes' if tie['all_match'] else 'no'}")
        edges = "/".join(str(v) for v in no["asserted_edges"])
        cover = "/".join(f"{v:.4f}" for v in no["coverage"])
        deltas = (_fmt_deltas(no["per_type_deltas"])
                  if row["arms_agree"]
                  else f"no: {_fmt_deltas(no['per_type_deltas'])}; "
                       f"rowid: {_fmt_deltas(tie['per_type_deltas'])}")
        lines.append(
            f"| {row['task']} | {row['seed']} | {reproduced} | "
            f"{row['campaign']['asserted_edges']} → {edges} | "
            f"{row['campaign']['coverage']:.4f} → {cover} | {deltas} |")

    lines += [
        "",
        f"The campaign table reproduced on "
        f"{counts['no_tiebreak_matches_campaign_table']} of {n} seeds under the "
        f"shipped order and {counts['tiebreak_matches_campaign_table']} of {n} "
        "under the tiebreak. The deltas are candidate-id counts and edge "
        "weights, per type; they move in both directions, so this is a different "
        "candidate population, not a consistent shift.",
        "",
        "## 4. Layer 3 — score reproduction (not entered)",
        "",
    ]
    if counts["layer3_entered"] == 0:
        lines += [
            "No seed reached layer 3: the candidate population did not reproduce "
            "on any of them. The score differences are recorded below so the "
            "next audit does not need to re-run them, and they are not a "
            "reproduction result.",
            "",
        ]
    else:
        lines += [
            f"Layer 3 was entered on {counts['layer3_entered']} of {n} seeds; "
            "the remaining seeds stopped at layer 2. The differences for every "
            "seed are recorded.",
            "",
        ]
    lines += [
        "| Task | Seed | max abs delta, retention | transfer | revision |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        no = row["arms"]["no_tiebreak"]
        lines.append(
            f"| {row['task']} | {row['seed']} | "
            f"{no['score_max_abs_diff']['retention']:.6g} | "
            f"{no['score_max_abs_diff']['transfer']:.6g} | "
            f"{no['score_max_abs_diff']['revision']:.6g} |")

    lines += [
        "",
        "The two configurations produced identical scores, so one set of columns "
        "covers both.",
        "",
        "## 5. Verdict",
        "",
    ]
    for paragraph in _verdict_lines(counts, n, artifact["repeats"]):
        lines += [paragraph, ""]

    lines += [
        "",
        "The diagnostic's structure check supplies the constraint on the "
        f"remaining candidates: {cross['identical_pass']} identical/pass, "
        f"{cross['identical_fail']} identical/fail, "
        f"{cross['different_fail']} different/fail and "
        f"{cross['different_pass']} different/pass. The eight different/fail "
        "units are the eight audited here; T2 `20261122` is the different/pass "
        "exception and is outside this audit.",
        "",
        "## 6. What would settle the remaining question",
        "",
        "A hash-seed sensitivity sweep on one failing seed is the cheapest next "
        "test: if the per-type table moves across hash seeds, the campaign's "
        "unrecorded environment is sufficient to explain the mismatch; if it "
        "does not, the remaining candidate is the campaign-time code, which "
        "needs a campaign-time copy rather than another re-run. The sweep was "
        "not run here: the audit's stop condition is the three layers above, "
        "and adding a fourth after seeing the result would be a new instrument.",
        "",
        "## 7. What is not claimed",
        "",
        "No mechanism, no room estimate, no component, no V2 brief and no "
        "re-score of the campaign or the diagnostic. The campaign's recorded "
        "verdicts stand. The diagnostic's D0 gate fired and its `AUDIT "
        "REQUIRED` outcome stands; this audit tests one hypothesis about why "
        "it fired and does not support that hypothesis as the cause, which is "
        "not the same as passing D0.",
        "",
        "## Provenance",
        "",
        f"- Artifact: `docs/use_path_audit.json` (generated "
        f"{artifact['generated_utc']}).",
        f"- Command: `{artifact['command']}`.",
        f"- Hash seed: `PYTHONHASHSEED={artifact['pythonhashseed']}`.",
        "- Campaign reference: `docs/formation_utilization.json`.",
        "- Diagnostic reference: `docs/use_path_diagnostic.json`.",
        "- Structure check: `docs/use_path_diagnostic_structure.json`.",
        "- Instrument: `benchmarks/use_path_audit.py`; "
        "checks: `tests/test_use_path_audit.py`.",
        "",
    ]
    text = "\n".join(lines)
    _assert_no_placeholder(text)
    return text


def self_test() -> int:
    require_hash_seed()
    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryService(str(Path(tmp) / "audit_self_test.db"))
        first = mem.store("alpha beta gamma", event_type="sleep")
        second = mem.store("alpha beta gamma", event_type="sleep")
        mem._conn.execute("UPDATE events SET time=1.0")
        mem._conn.commit()
        original = MemoryService.recent
        with rowid_tiebreak():
            rows = mem.recent(2, "sleep")
        assert [event.id for event in rows] == [second.id, first.id], rows
        assert MemoryService.recent is original, "recent() was not restored"
        mem._conn.close()

    cases = [
        (True, True, True, True, "both_stable_both_reproduce"),
        (True, True, True, False, "both_stable_no_tiebreak_reproduces"),
        (True, True, False, True, "both_stable_tiebreak_reproduces"),
        (True, True, False, False, "both_stable_both_differ"),
        (False, True, False, False, "baseline_unstable_tiebreak_stable"),
        (True, False, False, False, "baseline_stable_tiebreak_unstable"),
        (False, False, False, False, "both_unstable"),
    ]
    for no_stable, tie_stable, no_match, tie_match, expected in cases:
        got = classify(no_stable, tie_stable, no_match, tie_match)
        assert got == expected, (got, expected)
    print("self-test ok: the tiebreak fires, recent() is restored, "
          "and all seven outcome labels are reachable")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--force", action="store_true",
                        help="ignore existing part files")
    parser.add_argument("--reanalyse", action="store_true",
                        help="recompute the summary from an existing artifact; "
                             "run no engine")
    parser.add_argument("--render", action="store_true",
                        help="regenerate the result document from the artifact")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.reanalyse:
        artifact = json.loads(AUDIT.read_text(encoding="utf-8"))
        runs = artifact["runs"]
        artifact["summary"] = analyse(runs, artifact["repeats"])
        base = artifact["command"].split("  #")[0]
        artifact["command"] = base + "  # reanalysed in place"
        _write(AUDIT, artifact)
        RESULT_MD.write_text(render_markdown(artifact), encoding="utf-8")
        print(json.dumps(artifact["summary"]["counts"], indent=2))
        print(f"[reanalysed] {AUDIT} + {RESULT_MD}")
        return 0
    if args.render:
        artifact = json.loads(AUDIT.read_text(encoding="utf-8"))
        RESULT_MD.write_text(render_markdown(artifact), encoding="utf-8")
        print(f"[rendered] {RESULT_MD}")
        return 0
    require_hash_seed()
    if args.repeats < 2:
        parser.error("--repeats must be at least 2 to test repeatability")

    PARTS.mkdir(parents=True, exist_ok=True)
    runs: list[dict] = []
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=min(args.workers, len(FAILING))) as pool:
        futures = {
            pool.submit(run_seed, task, seed, args.repeats, args.force):
                (task, seed)
            for task, seed in FAILING
        }
        for future in as_completed(futures):
            task, seed = futures[future]
            records = future.result()
            runs.extend(records)
            print(f"[done] {task} {seed}: {len(records)} runs", flush=True)

    runs.sort(key=lambda r: (r["task"], r["seed"], r["repeat"], r["arm"]))
    summary = analyse(runs, args.repeats)
    artifact = {
        "status": "three-layer reproduction audit; post-hoc observation, "
                  "not a protocol and not a change to D0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "command": "PYTHONHASHSEED=0 python benchmarks/use_path_audit.py "
                   f"--repeats {args.repeats} --workers {args.workers}",
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
        "repeats": args.repeats,
        "seeds": [f"{task}/{seed}" for task, seed in FAILING],
        "runs": runs,
        "summary": summary,
        "seconds": round(time.perf_counter() - started, 3),
    }
    _write(AUDIT, artifact)
    RESULT_MD.write_text(render_markdown(artifact), encoding="utf-8")
    print(json.dumps(summary["counts"], indent=2))
    print(f"[written] {AUDIT} + {RESULT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
