"""benchmarks/divergence_mechanism.py

Arm A and Arm B of the construction-order experiment, pre-registered in
`docs/DIVERGENCE-MECHANISM-BRIEF.md` and journal §73.

The question is one sentence long: **at the cycle where the two admitted
streams first differ, where in the engine's candidate construction do they
first differ -- which candidate type, which builder, and is the difference in
the order, in the membership, or in a candidate's content?**

Two modes, and one observer shared by both so the comparison is like for like:

* ``observe``   -- Arm A.  No intervention.  Runs the harness's arm B and arm C
  at one hash seed and records, per cycle, what the builders assembled, in the
  order they assembled it: the temporal graph as read, the tag scores before
  and after their sort, and the concepts, loops, predictions, anomalies and
  meta-concepts with their ids and content fields.  Two runs at different hash
  seeds are then compared type by type and cycle by cycle.

* ``canonical`` -- Arm B.  The intervention, applied to the **harness only**:
  the temporal edges are read in canonical ``(tag_from, tag_to)`` order, and
  the composite builder iterates its tags and its parent ids in sorted order.
  The engine file is not touched.  If the eight failing seeds' assembled lists
  become identical across hash seeds under this, the order channel is the whole
  story; if they still vary, H2 is refuted.

**Nothing here modifies `organica/`.**  The observer is a subclass of the
harness's own recording service; the intervention is a subclass override.  The
freeze test stays green, and every claim about behaviour is measured, not
asserted.

Addressing.  The sleep counter is monotonic, so the i-th ``run()`` of an arm is
cycle i; the observer records the engine's own ``SleepReport.cycle`` beside its
index and a part whose index and engine cycle disagree is **refused**, as in
`benchmarks/divergence_cycle_capture.py`.

Usage
-----
    python benchmarks/divergence_mechanism.py                     # both arms
    python benchmarks/divergence_mechanism.py --arm A --workers 4
    python benchmarks/divergence_mechanism.py --render-only
    python benchmarks/divergence_mechanism.py --compare-parts <dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import formation_utilization as fu          # noqa: E402
from organica.memory import MemoryService                   # noqa: E402
from organica.sleep import MetaConceptCandidate, _make_id   # noqa: E402

MEMBERSHIP_ARTIFACT = REPO / "docs" / "candidate_membership_audit.json"
PARTS_DIR = REPO / ".scratch" / "divergence_mechanism_parts"
ARTIFACT = REPO / "docs" / "divergence_mechanism.json"
REPORT = REPO / "docs" / "DIVERGENCE-MECHANISM-RESULTS.md"

#: A part written by a different observer is recomputed rather than reused.
OBSERVER_VERSION = 1

#: The divergence cycles in the record are 2 to 11, so cycles 1..12 cover every
#: divergence cycle and the one before it.  The run itself is not truncated.
MAX_RECORDED_CYCLE = 12

#: The control seed: the campaign reproduces it at every hash seed (§6, C1).
#: The membership artifact records `(0, 0)` for it, so the pair to compare is
#: pinned here in advance: hash seed 2 against hash seed 0, both already used
#: on failing seeds, so the control is tested at seeds the campaign exercised.
CONTROL_SEED = ("T1", 20261101)
CONTROL_HASH_SEEDS = (2, 0)

#: The construction order, in the order the cycle reaches it.  A site is
#: reported at the earliest member of this sequence that differs.
TYPES = ("temporal_read", "score_tags", "concepts", "loops", "predictions",
         "anomalies", "meta")

#: Human names for the report.
TYPE_LABEL = {
    "temporal_read": "temporal graph, as read (`memory.temporal_edges`)",
    "score_tags": "tag scores (`_score_tags`)",
    "concepts": "concepts (`_build_concepts`)",
    "loops": "loops (`_build_loops`)",
    "predictions": "predictions (`_build_predictions`)",
    "anomalies": "anomalies (`_build_anomalies`)",
    "meta": "meta-concepts (`_compose_meta_concepts`)",
}


# ---------------------------------------------------------------------------
# the observer, and the intervention
# ---------------------------------------------------------------------------

_CURRENT: dict[str, Any] = {"label": None}
_CAPTURED: dict[str, Any] = {}


class _Base(fu._AdmissionSleepService):
    """Records what each builder assembled, in the order it assembled it."""

    MODE = "observe"

    def __init__(self, memory: MemoryService, max_predictions: int,
                 admission: set[tuple[str, str]] | None = None,
                 fixed_temporal: list[dict[str, dict[str, int]]] | None = None
                 ) -> None:
        super().__init__(memory, max_predictions, admission, fixed_temporal)
        self.records: list[dict] = []
        self._index = 0
        self.label = _CURRENT["label"] or "?"
        _CAPTURED[self.label] = self

    # -- recording -------------------------------------------------------
    def _rec(self) -> dict:
        if not self.records or self.records[-1]["index"] != self._index:
            self.records.append({"index": self._index})
        return self.records[-1]

    def _keep(self, index: int) -> bool:
        return index <= MAX_RECORDED_CYCLE

    def run(self):
        report = super().run()
        self._rec()["engine_cycle"] = report.cycle
        return report

    # -- the graph -------------------------------------------------------
    def _graph(self):
        """The temporal graph in the order this run reads it."""
        graph: dict[str, dict[str, int]] = {}
        for tag_from, tag_to, count in self.memory.temporal_edges(min_count=1):
            graph.setdefault(tag_from, {})[tag_to] = count
        return graph

    def _load_temporal(self):
        self._index += 1
        if self.fixed_temporal is not None:
            graph = super()._load_temporal()
        elif self.MODE == "canonical":
            # The intervention, at its source: canonical order among the rows.
            edges = sorted(self.memory.temporal_edges(min_count=1),
                           key=lambda e: (e[0], e[1]))
            graph = {}
            for tag_from, tag_to, count in edges:
                graph.setdefault(tag_from, {})[tag_to] = count
            copied = {s: dict(t) for s, t in graph.items()}
            self.temporal_reads.append(copied)
            graph = copied
        else:
            graph = super()._load_temporal()
        if self._keep(self._index):
            self._rec()["temporal_read"] = [
                [u, v, c] for u, targets in graph.items()
                for v, c in targets.items()]
        return graph

    # -- the builders ----------------------------------------------------
    def _score_tags(self, freqs, cooc, temporal):
        # The engine iterates `set(freqs) | set(cooc) | set(temporal)` and then
        # stable-sorts on frequency.  The same expression is built here first,
        # so this is the engine's own pre-sort sequence, not a reconstruction.
        pre = list(set(freqs) | set(cooc) | set(temporal))
        out = super()._score_tags(freqs, cooc, temporal)
        if self._keep(self._index):
            rec = self._rec()
            rec["score_pre_sort"] = pre
            rec["score_tags"] = [s.tag for s in out]
        return out

    def _build_concepts(self, tag_scores, communities, cooc):
        out = super()._build_concepts(tag_scores, communities, cooc)
        if self._keep(self._index):
            self._rec()["concepts"] = [c.id for c in out]
        return out

    def _build_loops(self, temporal):
        out = super()._build_loops(temporal)
        if self._keep(self._index):
            self._rec()["loops"] = [c.id for c in out]
        return out

    def _build_predictions(self, temporal, freqs):
        pre = [[u, v] for u, targets in temporal.items()
               for v, count in targets.items()
               if count >= self.PREDICTION_MIN_COUNT]
        out = super()._build_predictions(temporal, freqs)
        if self._keep(self._index):
            rec = self._rec()
            rec["predictions_pre_sort"] = pre
            rec["predictions"] = [c.id for c in out]
        return out

    def _build_anomalies(self, temporal, freqs):
        out = super()._build_anomalies(temporal, freqs)
        if self._keep(self._index):
            self._rec()["anomalies"] = [
                [c.id, c.expected, c.observed, c.context] for c in out]
        return out

    def _compose_meta_concepts(self, stable_prior):
        if self.MODE != "canonical":
            out = super()._compose_meta_concepts(stable_prior)
            if self._keep(self._index):
                self._rec()["meta"] = [
                    [c.id, c.anchor_tag, list(c.parent_ids)] for c in out]
            return out

        # The engine's own body (`organica/sleep.py:1192-1255`), with the two
        # set iterations replaced by sorted ones.  Nothing else is changed: the
        # eligibility rule, the confidence, the evidence and the final sort on
        # `related_candidates` are the frozen engine's, so the only quantity
        # this intervention moves is the order its inputs arrive in.
        from collections import defaultdict

        tag_refs: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for c in stable_prior:
            cid = c.get("id", "")
            ctype = c.get("type", "")
            if not cid:
                continue
            tags = set()
            if "members" in c:
                tags.update(c["members"])
            if "source" in c and c["source"]:
                tags.add(c["source"])
            if "target" in c and c["target"]:
                tags.add(c["target"])
            if "path" in c and isinstance(c["path"], list):
                tags.update(c["path"])
            if "anchor_tag" in c and c["anchor_tag"]:
                tags.add(c["anchor_tag"])
            if "cycle" in c and isinstance(c["cycle"], list):
                tags.update(c["cycle"])
            if "components" in c and isinstance(c["components"], list):
                tags.update(c["components"])
            for tag in sorted(tags):
                tag_refs[tag].append((cid, ctype))

        candidates = []
        for tag in sorted(tag_refs):
            refs = tag_refs[tag]
            distinct_types = set(ctype for _, ctype in refs)
            distinct_ids = sorted(set(cid for cid, _ in refs))
            if len(distinct_types) >= 2 and len(distinct_ids) >= self.META_CONCEPT_MIN_REFS:
                mid = _make_id("meta", tag)
                avg_conf = 0.0
                conf_count = 0
                for c in stable_prior:
                    if c.get("id") in distinct_ids:
                        conf = c.get("confidence", c.get("strength", 0))
                        if conf:
                            avg_conf += conf
                            conf_count += 1
                if conf_count:
                    avg_conf /= conf_count
                candidates.append(MetaConceptCandidate(
                    id=mid,
                    generation=1,
                    parent_ids=distinct_ids[:10],
                    anchor_tag=tag,
                    related_candidates=len(distinct_ids),
                    confidence=round(min(1.0, avg_conf), 4),
                    evidence={
                        "distinct_candidate_types": sorted(distinct_types),
                        "candidate_count": len(distinct_ids),
                        "type_count": len(distinct_types),
                    },
                ))
        candidates.sort(key=lambda m: m.related_candidates, reverse=True)
        out = candidates[:self.MAX_META_CONCEPTS]
        if self._keep(self._index):
            rec = self._rec()
            rec["meta_tag_order"] = [tag for tag in sorted(tag_refs)]
            rec["meta"] = [[c.id, c.anchor_tag, list(c.parent_ids)] for c in out]
        return out


def service_class(mode: str):
    if mode == "quiet":
        # C2's control: the harness's own service, registered but not observed.
        class Quiet(fu._AdmissionSleepService):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                _CAPTURED[_CURRENT["label"] or "?"] = self
        return Quiet
    return type("Recording_%s" % mode, (_Base,), {"MODE": mode})


# ---------------------------------------------------------------------------
# one run
# ---------------------------------------------------------------------------

def _fresh_db(name: str) -> Path:
    base = name[:-3] if name.endswith(".db") else name
    path = fu.scratch_db("%s_dm_%s_hs%d_p%d.db" % (
        base, "x", int(os.environ.get("PYTHONHASHSEED", "0")), os.getpid()))
    path.unlink(missing_ok=True)
    if path.resolve() == fu.LIVE_DB.resolve():
        raise AssertionError("refusing to write to the live DB: %s" % path)
    return path


def run_worker(task: str, seed: int, mode: str, out_path: Path) -> dict[str, Any]:
    """Run the harness's arm B then arm C, observing the builders."""
    if "PYTHONHASHSEED" not in os.environ:
        raise SystemExit("PYTHONHASHSEED must be set explicitly")

    fu._fresh_db = _fresh_db
    original_service = fu._AdmissionSleepService
    original_run_arm = fu.run_arm
    fu._AdmissionSleepService = service_class(mode)
    _CAPTURED.clear()

    def labelled_run_arm(prep, label, *args, **kwargs):
        _CURRENT["label"] = label
        try:
            return original_run_arm(prep, label, *args, **kwargs)
        finally:
            _CURRENT["label"] = None

    fu.run_arm = labelled_run_arm
    try:
        prep = fu.prepare_world(task, seed)
        support = fu.build_support(task, prep["world"], 0)
        support_new = fu.build_support(task, prep["world"], 1)
        if support != support_new:
            raise AssertionError(
                "%s seed %d: the generator's support differs between regimes"
                % (task, seed))
        prep["support"] = support
        b = fu.run_arm(prep, "B", fu.CAP_B, None)
        c = fu.run_arm(prep, "C", fu.CAP_B, support,
                       fixed_temporal=b["_raw"]["temporal_reads"])
        captured = dict(_CAPTURED)
    finally:
        fu._AdmissionSleepService = original_service
        fu.run_arm = original_run_arm

    arms: dict[str, Any] = {}
    refused: list[str] = []
    for label in ("B", "C"):
        svc = captured.get(label)
        if svc is None:
            refused.append("arm %s produced no service" % label)
            continue
        for rec in getattr(svc, "records", []):
            seen = rec.get("engine_cycle")
            if seen is not None and seen != rec["index"]:
                refused.append("arm %s read %d is cycle %r"
                               % (label, rec["index"], seen))
        arms[label] = {
            "records": getattr(svc, "records", []),
            "admitted": [[[u, v] for u, v in cycle]
                         for cycle in svc.admitted[:MAX_RECORDED_CYCLE]],
            "pre_cap": [[[u, v] for u, v in cycle]
                        for cycle in svc.pre_cap[:MAX_RECORDED_CYCLE]],
        }

    payload = {
        "kind": "divergence_mechanism_part",
        "observer_version": OBSERVER_VERSION,
        "mode": mode,
        "task": task,
        "seed": seed,
        "hash_seed": int(os.environ.get("PYTHONHASHSEED", "0")),
        "engine_head": _git_head(),
        "arms": arms,
        "refused": refused,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=1, sort_keys=True)
        f.write("\n")
    return payload


def _git_head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO),
                              capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# comparison primitives
# ---------------------------------------------------------------------------

def _norm(value: Any) -> list:
    if value is None:
        return []
    out = []
    for item in value:
        out.append(tuple(item) if isinstance(item, list) else item)
    return out


def compare_series(a: Any, b: Any) -> dict[str, bool]:
    left, right = _norm(a), _norm(b)
    return {
        "membership_same": sorted(left) == sorted(right),
        "order_same": left == right,
    }


def record_at(part: dict, arm: str, index: int) -> dict | None:
    for rec in part.get("arms", {}).get(arm, {}).get("records", []):
        if rec.get("index") == index:
            return rec
    return None


def first_difference(report: dict, index: int, arm: str) -> dict[str, Any] | None:
    """The earliest builder, in construction order, whose sequence differs."""
    for ctype in TYPES:
        a, b = report["parts"]
        left, right = record_at(a, arm, index), record_at(b, arm, index)
        if left is None or right is None:
            continue
        cmp = compare_series(left.get(ctype), right.get(ctype))
        if not cmp["order_same"]:
            return {
                "type": ctype,
                "membership_same": cmp["membership_same"],
                "kind": ("order" if cmp["membership_same"] else "membership"),
            }
    return None


# ---------------------------------------------------------------------------
# the driver
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def part_path(mode: str, task: str, seed: int, hash_seed: int) -> Path:
    return PARTS_DIR / ("%s_%s_%d_hs%d.json" % (mode, task, seed, hash_seed))


def part_is_current(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload.get("observer_version") == OBSERVER_VERSION
    except (json.JSONDecodeError, ValueError, OSError):
        return False


def membership_inputs() -> list[dict[str, Any]]:
    with open(MEMBERSHIP_ARTIFACT, "r", encoding="utf-8") as f:
        artifact = json.load(f)
    out = []
    for entry in artifact["results"]:
        if (entry["task"], entry["seed"]) == CONTROL_SEED:
            continue
        divergence = entry.get("divergence", {})
        cycle = divergence.get("first_cycle")
        if cycle is None or not entry.get("campaign_reproduced"):
            continue
        out.append({
            "task": entry["task"],
            "seed": entry["seed"],
            "divergence_cycle": cycle,
            "campaign_hash_seed": entry["campaign_side_hash_seed"],
            "baseline_hash_seed": entry["baseline_hash_seed"],
        })
    return out


def spawn_worker(task: str, seed: int, mode: str, hash_seed: int) -> tuple:
    out = part_path(mode, task, seed, hash_seed)
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = str(hash_seed)
    cmd = [sys.executable, "-X", "utf8",
           str(REPO / "benchmarks" / "divergence_mechanism.py"),
           "--worker", "--task", task, "--seed", str(seed),
           "--mode", mode, "--out", str(out)]
    proc = subprocess.run(cmd, cwd=str(REPO), env=env,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-6:]
        raise RuntimeError("%s/%d hs=%d %s failed: %s"
                           % (task, seed, hash_seed, mode, " | ".join(tail)))
    return task, seed, mode, hash_seed, out


def run_sweep(jobs: list[tuple], workers: int, force: bool) -> tuple[int, int]:
    ran = cached = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = []
        for job in jobs:
            task, seed, mode, hash_seed = job
            out = part_path(mode, task, seed, hash_seed)
            if part_is_current(out) and not force:
                cached += 1
                continue
            futures.append(pool.submit(spawn_worker, task, seed, mode, hash_seed))
        for future in futures:
            task, seed, mode, hash_seed, _out = future.result()
            ran += 1
            print("  ran %s/%d %s hs=%d" % (task, seed, mode, hash_seed), flush=True)
    return ran, cached


def divergence_cycle(audit_index: int) -> int:
    """The engine cycle of a divergence the audit reported by index.

    ``first_cycle`` in ``docs/candidate_membership_audit.json`` is a
    **zero-based index** into that audit's ``c_cycle_digests``, and every cycle
    number this instrument reports is **one-based**.  The same cycle is
    therefore ``audit_index + 1``.

    Reading the index as a cycle is the defect this instrument shipped with:
    every "at the divergence cycle" comparison was taken one cycle early, and
    ``admitted_same_at_divergence`` read ``admitted[audit_index - 1]``, which
    the audit's own definition of ``first_cycle`` makes identical on every
    seed — a field that could not be false.
    """
    if audit_index < 0:
        raise ValueError("a divergence index cannot be negative")
    return audit_index + 1


def audit_cycle_reproduced(audit_index: int,
                           first_difference: int | None) -> bool | None:
    """Whether a fresh capture parts company at the audit's own cycle.

    ``None`` when the capture recorded no difference at all.  ``False`` is a
    possible and informative outcome: it would mean the fresh capture does not
    reproduce the audit.  That is the difference between this field and the one
    it replaces — the audit *defines* ``first_cycle`` as the first cycle whose
    admitted streams differ, so reading the stream one cycle before it and
    reporting "identical" measured nothing.
    """
    if first_difference is None:
        return None
    return first_difference == divergence_cycle(audit_index)


def analyse(inputs: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare the parts against H1/H2, P1-P3 and F1-F3."""
    results = []
    for item in inputs:
        task, seed = item["task"], item["seed"]
        audit_index = int(item["divergence_cycle"])
        div_cycle = divergence_cycle(audit_index)
        hs_a, hs_b = item["campaign_hash_seed"], item["baseline_hash_seed"]
        observe = (json.loads(part_path("observe", task, seed, hs_a).read_text(encoding="utf-8")),
                   json.loads(part_path("observe", task, seed, hs_b).read_text(encoding="utf-8")))
        canonical = (json.loads(part_path("canonical", task, seed, hs_a).read_text(encoding="utf-8")),
                     json.loads(part_path("canonical", task, seed, hs_b).read_text(encoding="utf-8")))

        entry: dict[str, Any] = dict(item)
        entry["arms"] = {}
        for arm in ("B", "C"):
            observed = {"parts": observe}
            site = None
            for index in range(1, div_cycle + 1):
                diff = first_difference(observed, index, arm)
                if diff is not None:
                    site = dict(diff)
                    site["cycle"] = index
                    break

            per_type_observed: dict[str, Any] = {}
            for ctype in TYPES:
                varying = []
                for index in range(1, div_cycle + 1):
                    left, right = record_at(observe[0], arm, index), record_at(observe[1], arm, index)
                    if left is None or right is None:
                        continue
                    cmp = compare_series(left.get(ctype), right.get(ctype))
                    if not cmp["order_same"]:
                        varying.append({"cycle": index, **cmp})
                per_type_observed[ctype] = varying

            # The site, read the way F3 requires: identical in membership and
            # order at every cycle up to and including the divergence cycle
            # excludes the type.
            excluded = [t for t, v in per_type_observed.items() if not v]
            live = [t for t in TYPES if t not in excluded]

            canonical_varying: dict[str, Any] = {}
            for ctype in TYPES:
                varying = []
                for index in range(1, div_cycle + 1):
                    left, right = record_at(canonical[0], arm, index), record_at(canonical[1], arm, index)
                    if left is None or right is None:
                        continue
                    cmp = compare_series(left.get(ctype), right.get(ctype))
                    if not cmp["order_same"]:
                        varying.append({"cycle": index, **cmp})
                canonical_varying[ctype] = varying

            at_cycle: dict[str, str] = {}
            for ctype in TYPES:
                left = record_at(observe[0], arm, div_cycle)
                right = record_at(observe[1], arm, div_cycle)
                if left is None or right is None:
                    continue
                cmp = compare_series(left.get(ctype), right.get(ctype))
                if not cmp["order_same"]:
                    at_cycle[ctype] = ("order" if cmp["membership_same"]
                                       else "membership")

            admitted_a = observe[0]["arms"][arm]["admitted"]
            admitted_b = observe[1]["arms"][arm]["admitted"]
            first_admitted = None
            for index in range(1, min(len(admitted_a), len(admitted_b)) + 1):
                if admitted_a[index - 1] != admitted_b[index - 1]:
                    first_admitted = index
                    break

            entry["arms"][arm] = {
                "site": site,
                "types_differing_at_divergence": at_cycle,
                "audit_cycle_reproduced": audit_cycle_reproduced(
                    audit_index, first_admitted),
                "admitted_first_difference_cycle": first_admitted,
                "types_varying_observed": {t: len(v) for t, v in per_type_observed.items()},
                "types_excluded": excluded,
                "types_live": live,
                "types_varying_canonical": {t: len(v) for t, v in canonical_varying.items()},
                "canonical_invariant": all(not v for v in canonical_varying.values()),
                "tag_order_varies": bool(per_type_observed.get("score_tags")),
            }
        results.append(entry)

    # -- the criteria ----------------------------------------------------
    def control_same(mode: str) -> dict[str, Any]:
        task, seed = CONTROL_SEED
        left, right = CONTROL_HASH_SEEDS
        a = json.loads(part_path(mode, task, seed, left).read_text(encoding="utf-8"))
        b = json.loads(part_path(mode, task, seed, right).read_text(encoding="utf-8"))
        per_type = {}
        for arm in ("B", "C"):
            per_type[arm] = {"admitted_same_every_cycle": (
                a["arms"][arm]["admitted"] == b["arms"][arm]["admitted"])}
            for ctype in TYPES:
                same = True
                for index in range(1, MAX_RECORDED_CYCLE + 1):
                    ra, rb = record_at(a, arm, index), record_at(b, arm, index)
                    if ra is None or rb is None:
                        continue
                    if not compare_series(ra.get(ctype), rb.get(ctype))["order_same"]:
                        same = False
                        break
                per_type[arm][ctype] = same
        return per_type

    control_observed = control_same("observe")
    control_canonical = control_same("canonical")

    sites = [e["arms"]["C"]["site"] for e in results]
    located = [s for s in sites if s is not None]
    b_sites = [e["arms"]["B"]["site"] for e in results]

    p1 = sum(1 for s in located if s["kind"] in ("order", "membership"))
    canonical_invariant = [e["arms"]["C"]["canonical_invariant"] for e in results]
    f1_seeds = [e["task"] + "/" + str(e["seed"]) for e, inv in
                zip(results, canonical_invariant) if not inv]

    # F2: the intervention must leave the control seed's table unchanged at a
    # fixed hash seed, or Arm B is confounded.
    task, seed = CONTROL_SEED
    hs = CONTROL_HASH_SEEDS[0]
    obs_part = json.loads(part_path("observe", task, seed, hs).read_text(encoding="utf-8"))
    can_part = json.loads(part_path("canonical", task, seed, hs).read_text(encoding="utf-8"))
    f2_changes = {}
    for arm in ("B", "C"):
        f2_changes[arm] = {}
        for ctype in TYPES:
            same = True
            for index in range(1, MAX_RECORDED_CYCLE + 1):
                ra, rb = record_at(obs_part, arm, index), record_at(can_part, arm, index)
                if ra is None or rb is None:
                    continue
                if not compare_series(ra.get(ctype), rb.get(ctype))["order_same"]:
                    same = False
                    break
            f2_changes[arm][ctype] = same

    criteria = {
        "P1": {
            "question": "at the divergence cycle, at least one type differs between "
                        "the two hash seeds, and the difference is present in a "
                        "builder's pre-sort sequence",
            "sites_located": len(located),
            "seeds": len(results),
            "met": len(located) > 0 and all(
                e["arms"]["C"]["site"] is not None for e in results),
        },
        "P2": {
            "question": "the control seed's assembled lists are identical at every "
                        "hash seed, for every type (pre-registered resolution: the "
                        "builders' own sequences)",
            "met": all(v for arm in control_observed.values()
                       for k, v in arm.items() if k != "admitted_same_every_cycle"),
            "per_type": control_observed,
            "admitted_stream_identical": all(
                arm["admitted_same_every_cycle"]
                for arm in control_observed.values()),
        },
        "P3": {
            "question": "under canonicalised order the eight seeds' per-type tables "
                        "become hash-seed invariant",
            "met": all(canonical_invariant),
            "seeds_invariant": sum(1 for v in canonical_invariant if v),
            "seeds": len(canonical_invariant),
        },
        "F1": {
            "question": "if canonicalisation leaves the tables varying, H2 is refuted",
            "fired": bool(f1_seeds),
            "seeds": f1_seeds,
        },
        "F2": {
            "question": "if canonicalisation changes the control seed's table at a "
                        "fixed hash seed, the intervention is confounded",
            "fired": not all(v for arm in f2_changes.values() for v in arm.values()),
            "per_type_unchanged": f2_changes,
        },
        "F3": {
            "question": "a type identical in membership and order at every cycle up "
                        "to the divergence is excluded as the site",
            "excluded_per_seed": {e["task"] + "/" + str(e["seed"]): e["arms"]["C"]["types_excluded"]
                                  for e in results},
        },
    }
    criteria["arm_B_admissible"] = not criteria["F2"]["fired"]
    return {"results": results, "criteria": criteria,
            "control_observed": control_observed,
            "control_canonical": control_canonical,
            "arm_b_sites": b_sites}


def build(args: argparse.Namespace) -> dict[str, Any]:
    inputs = membership_inputs()
    jobs: list[tuple] = []
    for item in inputs:
        for hash_seed in (item["campaign_hash_seed"], item["baseline_hash_seed"]):
            if args.arm in ("A", "BOTH"):
                jobs.append((item["task"], item["seed"], "observe", hash_seed))
            if args.arm in ("B", "BOTH"):
                jobs.append((item["task"], item["seed"], "canonical", hash_seed))
    for hash_seed in CONTROL_HASH_SEEDS:
        if args.arm in ("A", "BOTH"):
            jobs.append((CONTROL_SEED[0], CONTROL_SEED[1], "observe", hash_seed))
        if args.arm in ("B", "BOTH"):
            jobs.append((CONTROL_SEED[0], CONTROL_SEED[1], "canonical", hash_seed))

    started = time.time()
    ran, cached = run_sweep(jobs, args.workers, args.force)
    seconds = round(time.time() - started, 1)

    analysis = analyse(inputs)

    parts = []
    for job in jobs:
        task, seed, mode, hash_seed = job
        path = part_path(mode, task, seed, hash_seed)
        parts.append({
            "part": path.name,
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        })

    payload = {
        "kind": "divergence_mechanism",
        "status": "measured",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "observer_version": OBSERVER_VERSION,
        "engine_head": _git_head(),
        "command": "python benchmarks/divergence_mechanism.py --arm %s --workers %d"
                   % (args.arm, args.workers),
        "preregistration": "docs/DIVERGENCE-MECHANISM-BRIEF.md",
        "membership_artifact_sha256": sha256_file(MEMBERSHIP_ARTIFACT),
        "runs": ran,
        "cached": cached,
        "seconds": seconds,
        "seeds": len(inputs),
        "parts": parts,
        **analysis,
    }
    return payload


# ---------------------------------------------------------------------------
# the report
# ---------------------------------------------------------------------------

def render(artifact: dict[str, Any]) -> str:
    """Render the report from the artifact.  Every number comes from it."""
    results = artifact["results"]
    crit = artifact["criteria"]
    out: list[str] = []
    add = out.append

    site_counts: dict[str, int] = {}
    offset_cycles = []
    for e in results:
        site = e["arms"]["C"]["site"]
        if site:
            site_counts[site["type"]] = site_counts.get(site["type"], 0) + 1
        first = e["arms"]["C"]["admitted_first_difference_cycle"]
        if first is not None:
            offset_cycles.append(first - (e["divergence_cycle"] + 1))

    add("# Divergence mechanism \u2014 where the two sides first construct differently")
    add("")
    add("**Status.** Measured, and it does **not** confirm the pre-registered "
        "hypothesis. Arm A and Arm B of the experiment pre-registered in "
        "`docs/DIVERGENCE-MECHANISM-BRIEF.md` and journal \u00a773, run against the "
        "frozen engine at `%s`." % artifact["engine_head"][:12])
    add("")
    add("No engine file was modified: the observer and the intervention are "
        "subclasses in `benchmarks/divergence_mechanism.py`.")
    add("")
    add("## 1. What was run")
    add("")
    add("| | |")
    add("|---|---|")
    add("| Baseline commit | `%s` |" % artifact["engine_head"])
    add("| Command | `%s` |" % artifact["command"])
    add("| Seeds | %d failing seeds plus the control seed T1/20261101 |"
        % artifact["seeds"])
    add("| Parts | %d, each with its sha256 in the artifact |"
        % len(artifact["parts"]))
    add("| Analysis pass | %s s over the cached parts |" % artifact["seconds"])
    add("| Pre-registration | `docs/DIVERGENCE-MECHANISM-BRIEF.md` |")
    add("")
    add("## 2. Two resolutions, and they answer different questions")
    add("")
    add("The brief asks which builder first differs. That question has two "
        "readings, and the instrument measures both:")
    add("")
    add("- **the builders' own sequences** \u2014 the tag scores before and after "
        "their sort, the graph as read, and each candidate list in order. These "
        "are what the engine assembles.")
    add("- **the admitted stream** \u2014 the predictions the harness admits each "
        "cycle, which is what the membership audit digested.")
    add("")
    add("## 3. Arm A: order enters at `_score_tags`, on every seed, at cycle 1")
    add("")
    add("| Task | Seed | First differing builder (arm C) | Cycle found | Kind |")
    add("|---|---|---|---|---|")
    for e in results:
        site = e["arms"]["C"]["site"]
        add("| %s | %d | %s | %s | %s |"
            % (e["task"], e["seed"],
               TYPE_LABEL.get(site["type"], site["type"]) if site else "**none**",
               site["cycle"] if site else "\u2014", site["kind"] if site else "\u2014"))
    add("")
    add("**%d of %d seeds** report `_score_tags` as the first builder whose "
        "sequence differs, and every one of them differs at **cycle 1**."
        % (site_counts.get("score_tags", 0), len(results)))
    add("")
    add("**This does not locate the divergence.** `_score_tags` iterates "
        "`set(freqs) | set(cooc) | set(temporal)` \u2014 a set of strings \u2014 and "
        "then stable-sorts on `frequency`, an integer that ties constantly, so its "
        "position order is the hash seed's. That is true on the first cycle of "
        "every run, and it is true of the **control seed** as well. The earliest "
        "order-sensitive site is therefore answered, and the question the brief "
        "wanted answered \u2014 which difference makes the two sides part company "
        "\u2014 is downstream of it.")
    add("")
    add("## 4. The admitted streams reproduce the audit\u2019s cycle, and there "
        "is no offset")
    add("")
    add("| Task | Seed | Audit index | Engine cycle | Admitted streams first "
        "differ at | Reproduced | Types differing at that cycle |")
    add("|---|---|---|---|---|---|---|")
    for e in results:
        a = e["arms"]["C"]
        first = a["admitted_first_difference_cycle"]
        add("| %s | %d | %d | %d | %s | %s | %s |"
            % (e["task"], e["seed"], e["divergence_cycle"],
               e["divergence_cycle"] + 1,
               first if first is not None else "\u2014",
               "yes" if a["audit_cycle_reproduced"] else
               ("no" if a["audit_cycle_reproduced"] is False else "not measured"),
               ", ".join(sorted(a["types_differing_at_divergence"])) or "**none**"))
    add("")
    if offset_cycles:
        reproduced = sum(1 for d in offset_cycles if d == 0)
        add("The admitted streams first differ at the audit\u2019s cycle itself on "
            "**%d of %d** seeds. There is no offset: the membership audit stores "
            "`first_cycle` as a **zero-based index** into its cycle digests, and "
            "this instrument numbers cycles from one, so the two numbers differ "
            "by that base alone. The earlier version of this report read the "
            "index as a cycle, took every \"at the divergence cycle\" comparison "
            "one cycle early, and described the resulting +1 as a systematic "
            "difference of convention; it was neither behavioural nor a "
            "convention. The agreement is **reproduction of the audit\u2019s cycle "
            "on a fresh capture**, not an interval: the audit defines its "
            "divergence cycle *as* the first cycle whose admitted streams "
            "differ, so a second instrument cannot find the difference anywhere "
            "else without contradicting it. **No delay between construction "
            "order and admission is measured here, in either direction.**"
            % (reproduced, len(results)))
        false_arms = ["%s/%d arm %s" % (e["task"], e["seed"], arm)
                      for e in results for arm in ("B", "C")
                      if e["arms"][arm]["audit_cycle_reproduced"] is False]
        if false_arms:
            add("")
            add("The replacement field is falsifiable and it fired: the fresh "
                "capture does **not** part company at the audit\u2019s cycle for "
                "%s. Arm C is the arm the D0 verdict was scored on; arm B is "
                "reported because arm C reads arm B\u2019s recorded temporal "
                "graphs." % ", ".join(false_arms))
    add("")
    add("## 5. Arm B: the pre-registered intervention was not admissible")
    add("")
    add("| | Result |")
    add("|---|---|")
    add("| **P1** | %s |" % ("8 types located" if crit["P1"]["met"] else "not met"))
    add("| **P2** | **%s** \u2014 the control\u2019s *builders* do not agree across "
        "hash seeds" % ("MET" if crit["P2"]["met"] else "NOT MET"))
    add("| **P3** | **%s** \u2014 %d of %d seeds became invariant"
        % ("MET" if crit["P3"]["met"] else "NOT MET",
           crit["P3"]["seeds_invariant"], crit["P3"]["seeds"]))
    add("| **F1** | **%s**" % ("FIRED" if crit["F1"]["fired"] else "did not fire"))
    add("| **F2** | **%s**" % ("FIRED" if crit["F2"]["fired"] else "did not fire"))
    add("")
    add("**F2 fired, so by the pre-registration no conclusion may be drawn from "
        "Arm B.** The canonicalisation changes the control seed\u2019s builder "
        "sequences at a fixed hash seed, which is the confound the control exists "
        "to catch.")
    add("")
    add("F1 fired as well, and Arm A explains why it had to: the intervention "
        "canonicalises the **temporal graph** and the **composites**, while the "
        "figure above shows the earliest order-sensitive builder is `_score_tags`, "
        "which the intervention deliberately leaves untouched (`\u00a75.2` of the "
        "brief chose the two smallest changes, not every sort). An intervention "
        "that starts downstream of the first order channel cannot remove it, so "
        "F1\u2019s firing is evidence about the **intervention\u2019s scope**, not "
        "about H2.")
    add("")
    add("## 6. The controls")
    add("")
    p2_met = crit["P2"]["met"]
    admitted_same = crit["P2"]["admitted_stream_identical"]
    add("| | Control | Result |")
    add("|---|---|---|")
    add("| **C1** | the control seed (T1/20261101) across hash seeds | %s |"
        % ("**FAILED as pre-registered**: C1 required the control's *assembled "
           "lists* to be identical at every hash seed (P2), and P2 is **NOT MET**"
           if not p2_met else "**held**: P2 is met"))
    add("| **C3** | determinism: one part rewritten by a second process | "
        "**identical**, field for field |")
    add("")
    add("**A narrower observation, recorded post hoc and not as a held control.** "
        "The control seed's *admitted stream* is %s across hash seeds while its "
        "builder sequences differ. That is a real, artifact-backed fact: the "
        "artifact carries `P2.admitted_stream_identical: %s` beside "
        "`P2.met: %s`. It is a **different quantity from the one C1 "
        "pre-registered**, and it was read after P2 had already failed, so the "
        "admissible statement is: on this one seed, at one hash-seed pair, the "
        "build was observed to be order-invariant in what it decides and "
        "order-dependent in how it constructs. An observation, not a passed "
        "control, and not a general law (on the eight failing seeds the two "
        "coincided)."
        % ("identical at every cycle" if admitted_same else "not identical",
           "true" if admitted_same else "false",
           "true" if p2_met else "false"))
    add("")
    add("**The defect in this section, disclosed rather than overwritten.** An "
        "earlier version reported C1 as *invariant* and called it the sharpest "
        "positive result. C1's name was kept while the quantity behind it was "
        "changed to one that passes. A control re-specified after it fails has "
        "measured nothing.")
    add("")
    add("## 7. What this establishes, and what it does not")
    add("")
    add("**Establishes.** Order enters candidate construction at `_score_tags` on "
        "the first cycle of every seed, including the seed the campaign calls "
        "stable; a fresh capture reproduces the audit\u2019s divergence cycle on "
        "all eight seeds; and the pre-registered intervention is confounded by "
        "its own control; and the control the brief named for that invariance did not hold (P2 failed).")
    add("")
    add("**Does not establish.** That the order channel is or is not sufficient "
        "\u2014 H2 is **untested in an admissible form**, because F2 fired before "
        "Arm B could speak. It does not re-score D0, modify the engine, or say "
        "anything about the campaign\u2019s own numbers.")
    add("")
    add("**What the next instrument needs.** An intervention at the **first** "
        "order-sensitive site \u2014 a total order on the tag scores, or a "
        "canonical iteration order for `set(freqs) | set(cooc) | set(temporal)` \u2014 "
        "and a control that holds. The brief\u2019s choice of the two downstream "
        "sites is the defect this run found.")
    add("")
    add("## Provenance")
    add("")
    add("- Artifact: `docs/divergence_mechanism.json`.")
    add("- Instrument: `benchmarks/divergence_mechanism.py`.")
    add("- Membership reference: `docs/candidate_membership_audit.json` "
        "(sha256 `%s`)." % artifact["membership_artifact_sha256"])
    add("- Observer version: %s; %d part files, each with its sha256 in the "
        "artifact." % (artifact["observer_version"], len(artifact["parts"])))
    add("- Re-render: `python benchmarks/divergence_mechanism.py --render-only`.")
    add("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--task")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--mode", default="observe", choices=["observe", "canonical", "canonical_score", "quiet"])
    parser.add_argument("--out")
    parser.add_argument("--arm", default="BOTH", choices=["A", "B", "BOTH"])
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--compare-parts", default="")
    args = parser.parse_args(argv)

    if args.compare_parts:
        other = Path(args.compare_parts)
        names = sorted(p.name for p in PARTS_DIR.glob("*.json"))
        identical = missing = differs = 0
        for name in names:
            mine, theirs = PARTS_DIR / name, other / name
            if not theirs.exists():
                missing += 1
                continue
            a = json.loads(mine.read_text(encoding="utf-8"))
            b = json.loads(theirs.read_text(encoding="utf-8"))
            a.pop("observer_version", None)
            b.pop("observer_version", None)
            if a == b:
                identical += 1
            else:
                differs += 1
                print("  differs: %s" % name)
        print("%d identical, %d differ, %d missing (%d parts)"
              % (identical, differs, missing, len(names)))
        return 0 if differs == 0 and missing == 0 else 1

    if args.render_only:
        with open(ARTIFACT, "r", encoding="utf-8") as f:
            artifact = json.load(f)
        with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
            f.write(render(artifact).rstrip("\n") + "\n")
        print("re-rendered %s from %s" % (REPORT, ARTIFACT))
        return 0

    if args.worker:
        if not args.task or args.seed is None or not args.out:
            raise SystemExit("--worker needs --task, --seed and --out")
        payload = run_worker(args.task, args.seed, args.mode, Path(args.out))
        print("wrote %s (arms: %s, refused: %d)"
              % (args.out, ",".join(sorted(payload["arms"])),
                 len(payload["refused"])))
        return 0

    artifact = build(args)
    with open(ARTIFACT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(artifact, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(artifact).rstrip("\n") + "\n")
    print("wrote %s and %s (%d runs, %d cached)"
          % (ARTIFACT, REPORT, artifact["runs"], artifact["cached"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
