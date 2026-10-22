"""
benchmarks/ablation_study.py
------------------------------------------------------------------
Which parts of Organica are actually doing the work?

The risk this study addresses is not "it doesn't work". It is:

    "It appears to work because one hidden subsystem is doing all the
     real cognitive work."

Ten ablations (A-J), each removing or replacing one mechanism, plus a
full-system reference (O_FULL). Every ablation is applied **in-process**
by subclassing ``SleepService`` / ``MemoryService`` or by rebinding a
method. The engine source is never edited, which matters twice over:

  * the running 90-day study is untouched -- ``organica/sleep.py`` keeps
    its modification time, so the live run stays auditable;
  * every condition provably runs the same cognitive code, so a
    difference in the results is caused by the ablation and nothing else.

PROTOCOL
--------
Stimulus:  the study stream (``organica/streams.py``), the same stimulus
           the 90-day study runs on.
Split:     the first 32 events are ingested (the TRAIN set). The last 16
           events are NEVER ingested and are replayed as a held-out set
           for the predictive metrics.
Cycles:    each condition runs the same number of sleep cycles over the
           train events, so selection dynamics (survival, decay, novelty)
           have room to develop.
Seeding:   every randomised condition uses a fixed seed, so a rerun
           reproduces the same numbers.

WHAT IS MEASURED
----------------
Definitions live in ``ablation_metrics.py`` -- that file is the
pre-registration contract. Two specified metrics (CY, EIG*) are
structurally unmeasurable in this codebase and are excluded rather than
zeroed; the Designer Surprise metrics need a human protocol and are
pending. See ``docs/ABLATION-PREREGISTRATION.md``.

Usage:
    python benchmarks/ablation_study.py
    python benchmarks/ablation_study.py --cycles 30
    python benchmarks/ablation_study.py --only A,D,H --out docs/ablation_study.json
"""

from __future__ import annotations

import argparse
import ast
import json
import random
import sys
import time
from collections import defaultdict
from dataclasses import asdict, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from organica import MemoryService, SleepService  # noqa: E402
from organica.memory import _extract_tags  # noqa: E402
from organica.paths import REPO_ROOT, temp_db  # noqa: E402
from organica.streams import STUDY_STREAM  # noqa: E402

from ablation_metrics import (  # noqa: E402
    PREDICTION_MIN_COUNT,
    canonical_signature,
    compare,
    compute_all,
    edges_implied_by_structures,
    f1,
    prediction_counts,
    predictive_f1,
    structure_tags,
)
from lineage_audit import audit as lineage_audit  # noqa: E402


# ---------------------------------------------------------------------------
# Generation labels, in ladder order
# ---------------------------------------------------------------------------
GENERATIONS = [
    ("G1 concepts", "concepts"),
    ("G1 phrases", "phrases"),
    ("G1 loops", "loops"),
    ("G1 predictions", "predictions"),
    ("G1 anomalies", "anomalies"),
    ("G2 meta-concepts", "meta_concepts"),
    ("G2 processes", "processes"),
    ("G3 workflows", "workflow_concepts"),
    ("G4 hypotheses", "hypotheses"),
    ("G5 theories", "theories"),
    ("G5 questions", "questions"),
    ("G6 dreams", "dreams"),
    ("G7 investigations", "investigations"),
    ("G8 experiments", "experiments"),
]

TRAIN_EVENTS = 32          # legacy: unused, the split is forward-looking now
EVENTS_PER_CYCLE = 8
HOLD_CYCLES = 10          # the last N cycles are scored as forward-looking predictions
DOMAIN_DIR = REPO_ROOT / "examples" / "domains"


def snapshot_structures(report) -> list[dict]:
    """The candidate dicts alive in a cycle's population.

    This is the organism's current set of structures -- not everything
    the candidate store still holds, which includes long-decayed
    historical versions of things that are no longer alive.
    """
    out: list[dict] = []
    for _label, attr in GENERATIONS:
        for cand in getattr(report, attr):
            out.append(asdict(cand))
    return out


# ===========================================================================
# Held-out protocol: forward-looking, not back-looking
# ===========================================================================
# The organism is run on the FULL study stream with exactly the daemon's
# ingestion pattern -- 8 events per cycle, rotating -- so the ablation
# measures the same organism the 90-day study is running.
#
# Scoring is forward-looking. Before a cycle's events are ingested, the
# substrate's graph and the organism's current Layer-1 predictions are
# snapshotted. The cycle's 8 events are then ingested and the snapshot is
# scored against what actually happened. The organism is therefore always
# predicting events it has not yet seen.
#
# An earlier version held out a fixed slice of the stream. That was
# rejected: the study stream is two domains in sequence, so any fixed
# slice is either within-domain (and the held-out event instances are
# textually identical to training ones) or, by accident, cross-domain.
# The forward-looking protocol avoids both problems and keeps the
# stimulus identical to the live study's.



# ===========================================================================
# The ablations
# ===========================================================================
class NoSleepService(SleepService):
    """A -- Remove Sleep.

    Consolidation, synthesis and dream generation are all disabled. The
    substrate still ingests and still builds its graph; nothing is ever
    consolidated, so the organism can only ever be an event logger.
    """

    def _build_concepts(self, *a, **k): return []
    def _build_phrases(self, *a, **k): return []
    def _build_loops(self, *a, **k): return []
    def _build_predictions(self, *a, **k): return []
    def _build_anomalies(self, *a, **k): return []
    def _compose_meta_concepts(self, *a, **k): return []
    def _compose_processes(self, *a, **k): return []
    def _compose_workflows(self, *a, **k): return []
    def _form_and_test_hypotheses(self, *a, **k): return []
    def _form_theories_and_questions(self, *a, **k): return ([], [])
    def _generate_categorized_dreams(self, *a, **k): return []
    def _rank_investigations(self, *a, **k): return []
    def _select_experiments(self, *a, **k): return []

    def _natural_selection(self, prior, *a, **k):
        return (0, 0, 0)

    def _store_candidates(self, report):
        # Keep the monotonic cycle counter; store no structures at all.
        self.memory.store(
            json.dumps({"type": "_sleep_meta", "cycle": report.cycle,
                        "ran_at": report.ran_at,
                        "composites_created": 0}),
            event_type="sleep", source="sleep:meta",
        )
        self.memory.record_sleep_cycle(report.cycle, report.ran_at)


class NoLineageService(SleepService):
    """B -- Remove Lineage.

    Every candidate is stored with its ``parent_ids`` stripped. The
    structures themselves are computed identically, so any change in
    behaviour is attributable to provenance alone.
    """

    def _store_single_candidate(self, candidate: dict):
        stripped = dict(candidate)
        stripped["parent_ids"] = []
        super()._store_single_candidate(stripped)


class NoCuriosityService(SleepService):
    """C -- Remove Curiosity.

    Layers 7 and 8 are disabled: no Expected-Information-Gain ranking, no
    investigation prioritisation, no experiment selection. Theories and
    Questions are untouched.
    """

    def _rank_investigations(self, *a, **k): return []
    def _select_experiments(self, *a, **k): return []


class NoFalsificationService(SleepService):
    """D -- Remove Falsification.

    No refutation, no extinction, no belief revision. Prior candidates are
    never decayed and never pruned, and the death threshold is disabled so
    the hypothesis layer cannot cull a belief either.

    Reinforcement is KEPT. The first version of this ablation removed the
    whole of ``_natural_selection``, which took the reinforcement boost
    with it -- and with nothing boosting confidences, every candidate
    decayed to nothing and the organism ended up *smaller* than the full
    system rather than larger. That measures "no selection at all", not
    "no extinction". This version keeps reinforcement and removes only
    decay and pruning, which is what the prediction describes.
    """

    DEATH_THRESHOLD = -1.0

    def _natural_selection(self, prior, concepts, phrases, loops, predictions):
        strengthened = 0
        current_keys: set[str] = set()
        for c in concepts:
            current_keys.add(f"concept:{'|'.join(c.members)}")
        for p in phrases:
            current_keys.add(f"phrase:{'|'.join(p.members)}")
        for l in loops:
            current_keys.add(f"loop:{'|'.join(l.path)}")
        for p in predictions:
            current_keys.add(f"prediction:{p.source}|{p.target}")

        for prior_c in prior:
            key = self._candidate_key(prior_c)
            if not key:
                continue
            prior_conf = prior_c.get("confidence", prior_c.get("strength", 0))
            prior_gen = prior_c.get("generation", 1)
            prior_obs = prior_c.get("evidence", {}).get("observations", 0)

            if key in current_keys:
                strengthened += 1
                self._reinforce_current(
                    key, prior_conf, prior_gen, prior_obs,
                    concepts, phrases, loops, predictions,
                )
            else:
                # No decay, no extinction: re-stored at its current
                # confidence, forever. Nothing can die.
                kept = dict(prior_c)
                kept["generation"] = prior_gen + 1
                evidence = dict(kept.get("evidence", {}))
                evidence["no_extinction"] = True
                kept["evidence"] = evidence
                self._store_single_candidate(kept)

        return strengthened, 0, 0


class NoDreamsService(SleepService):
    """E -- Remove Dreams."""

    def _generate_categorized_dreams(self, *a, **k): return []


class NoHypothesisLayerService(SleepService):
    """F -- Remove the Hypothesis Layer.

    Generation 4 is bypassed entirely. Theories and Questions are built
    directly from Workflow components, with support and contradiction
    counted from the temporal graph, so the comparison against O_FULL is
    about *where the causal bridge comes from*, not about how much
    evidence is available.
    """

    def _compose_workflows(self, meta_concepts, processes, stable_prior):
        workflows = super()._compose_workflows(meta_concepts, processes, stable_prior)
        self._ablation_workflows = workflows
        return workflows

    def _form_and_test_hypotheses(self, *a, **k):
        return []   # Generation 4 produces nothing.

    def _form_theories_and_questions(self, hypotheses, prior):
        from collections import defaultdict
        from organica.sleep import TheoryCandidate, QuestionCandidate, _make_id

        workflows = getattr(self, "_ablation_workflows", [])
        temporal = self._load_temporal()

        # Direct workflow -> expectation readings, bypassing Generation 4.
        readings: dict[str, dict[str, int]] = defaultdict(dict)
        for w in workflows:
            comps = w.components
            for i, sub in enumerate(comps):
                for j, exp in enumerate(comps):
                    if i == j:
                        continue
                    targets = temporal.get(sub, {})
                    support = targets.get(exp, 0)
                    total = sum(targets.values())
                    readings[sub][exp] = support
                    del total

        theories, questions = [], []
        for subject, exps in readings.items():
            if len(exps) < 2:
                continue
            ordered = sorted(exps.items(), key=lambda kv: kv[1], reverse=True)[:3]
            expectations = [e for e, _ in ordered]
            supports = [s for _, s in ordered]
            total_support = sum(supports)
            total_contra = 0
            avg_conf = round(sum(s / max(1, s + 1) for s in supports) / len(supports), 4)
            tid = _make_id("theory", subject, *sorted(expectations))
            theories.append(TheoryCandidate(
                id=tid, generation=4, subject=subject,
                hypotheses=[], confidence=avg_conf,
                support_count=total_support, contradiction_count=total_contra,
                parent_ids=[],
                evidence={"competing_count": len(expectations),
                          "expectations": expectations,
                          "source": "workflow_direct"},
            ))
            s1, s2 = supports[0], supports[1]
            total_pair = s1 + s2
            if total_pair > 0:
                import math
                p1, p2 = s1 / total_pair, s2 / total_pair
                entropy = 0.0
                if p1 > 0 and p2 > 0:
                    entropy = -(p1 * math.log2(p1) + p2 * math.log2(p2))
                maturity = min(1.0, total_pair / 10.0)
                uncertainty = round(entropy * maturity, 4)
                qid = _make_id("question", subject, *sorted(expectations[:2]))
                questions.append(QuestionCandidate(
                    id=qid, generation=4, subject=subject,
                    competing_expectations=expectations[:2],
                    uncertainty=uncertainty, parent_ids=[],
                    evidence={"ratio": [round(p1, 3), round(p2, 3)],
                              "supports": [s1, s2],
                              "total_pair_evidence": total_pair,
                              "source": "workflow_direct"},
                ))
        theories.sort(key=lambda t: t.support_count, reverse=True)
        questions.sort(key=lambda q: q.uncertainty, reverse=True)
        return theories[:self.MAX_THEORIES], questions[:self.MAX_QUESTIONS]


class NoQuestionsService(SleepService):
    """G -- Remove Questions. Theories are kept."""

    def _form_theories_and_questions(self, hypotheses, prior):
        theories, _questions = super()._form_theories_and_questions(hypotheses, prior)
        return theories, []


class RandomCuriosityService(SleepService):
    """H -- Random Curiosity.

    Expected Information Gain is replaced by a random ordering of the
    same candidate set: same node volume, same candidates, no information
    criterion. If this performs like the full system, the EIG
    implementation is not providing value.
    """

    def __init__(self, memory, rng=None):
        super().__init__(memory)
        self._rng = rng or random.Random(0)

    def _rank_investigations(self, questions, dreams):
        # Get the FULL ranked candidate list (the engine caps it at
        # MAX_INVESTIGATIONS), then shuffle it and re-cap. Shuffling
        # after the cap would be a no-op: the same five candidates would
        # be selected, only reordered -- which would test nothing.
        original = self.MAX_INVESTIGATIONS
        self.MAX_INVESTIGATIONS = 1000
        try:
            investigations = super()._rank_investigations(questions, dreams)
        finally:
            self.MAX_INVESTIGATIONS = original
        self._rng.shuffle(investigations)
        return investigations[:original]


class RandomSleepService(SleepService):
    """I -- Random Sleep.

    Every layer's output is replaced by random structures of the same
    count, drawn from the substrate's tag vocabulary. The node volume is
    identical to the full system; only the content is noise.
    """

    def __init__(self, memory, rng=None):
        super().__init__(memory)
        self._rng = rng or random.Random(0)

    # -- helpers ---------------------------------------------------------
    def _tags(self) -> list[str]:
        tags = sorted(self.memory.tag_frequencies().keys())
        return tags or ["void"]

    def _rand_sample(self, k: int) -> list[str]:
        tags = self._tags()
        k = max(1, min(k, len(tags)))
        return self._rng.sample(tags, k=k)

    def _rand_obj(self, c):
        tags = self._tags()
        rid = f"rnd_{self._rng.randrange(10 ** 9)}"
        if hasattr(c, "members"):
            return replace(c, id=rid, members=self._rand_sample(len(c.members)))
        if hasattr(c, "path"):
            return replace(c, id=rid, path=self._rand_sample(len(c.path)))
        if hasattr(c, "source") and hasattr(c, "target"):
            return replace(c, id=rid, source=self._rng.choice(tags), target=self._rng.choice(tags))
        if hasattr(c, "expectation"):
            return replace(c, id=rid, subject=self._rng.choice(tags),
                           expectation=self._rng.choice(tags))
        if hasattr(c, "competing_expectations"):
            a, b = self._rng.sample(tags, k=min(2, len(tags)))
            return replace(c, id=rid, subject=self._rng.choice(tags),
                           competing_expectations=[a, b], uncertainty=self._rng.random())
        if hasattr(c, "cycle"):
            return replace(c, id=rid, cycle=self._rand_sample(max(2, len(c.cycle))))
        if hasattr(c, "components"):
            return replace(c, id=rid, name=rid,
                           components=self._rand_sample(max(2, len(c.components))))
        if hasattr(c, "anchor_tag"):
            return replace(c, id=rid, anchor_tag=self._rng.choice(tags))
        if hasattr(c, "dream_category"):
            return replace(c, id=rid, subject=self._rng.choice(tags),
                           path_or_context=self._rand_sample(2))
        if hasattr(c, "target_id"):
            return replace(c, id=rid, target_id=rid,
                           expected_information_gain=self._rng.random())
        return replace(c, id=rid)

    def _rand_all(self, items):
        return [self._rand_obj(c) for c in items]

    # -- the ablation ----------------------------------------------------
    def _build_concepts(self, *a, **k): return self._rand_all(super()._build_concepts(*a, **k))
    def _build_phrases(self, *a, **k): return self._rand_all(super()._build_phrases(*a, **k))
    def _build_loops(self, *a, **k): return self._rand_all(super()._build_loops(*a, **k))
    def _build_predictions(self, *a, **k): return self._rand_all(super()._build_predictions(*a, **k))
    def _build_anomalies(self, *a, **k): return self._rand_all(super()._build_anomalies(*a, **k))
    def _compose_meta_concepts(self, *a, **k): return self._rand_all(super()._compose_meta_concepts(*a, **k))
    def _compose_processes(self, *a, **k): return self._rand_all(super()._compose_processes(*a, **k))
    def _compose_workflows(self, *a, **k): return self._rand_all(super()._compose_workflows(*a, **k))
    def _form_and_test_hypotheses(self, *a, **k): return self._rand_all(super()._form_and_test_hypotheses(*a, **k))
    def _form_theories_and_questions(self, *a, **k):
        t, q = super()._form_theories_and_questions(*a, **k)
        return self._rand_all(t), self._rand_all(q)
    def _generate_categorized_dreams(self, *a, **k): return self._rand_all(super()._generate_categorized_dreams(*a, **k))
    def _rank_investigations(self, *a, **k): return self._rand_all(super()._rank_investigations(*a, **k))
    def _select_experiments(self, *a, **k): return self._rand_all(super()._select_experiments(*a, **k))


class NoStructureMemory(MemoryService):
    """J -- Memory Without Structure.

    Raw events are stored; no graph edges are ever written. No
    co-occurrence, no temporal edges. If structures still emerge, then
    structure is leaking in from somewhere else -- the contamination check.
    """

    def _record_cooccurrences(self, tags): return None
    def _record_temporal_edges(self, new_tags, lookback: int = 3): return None


# ===========================================================================
# Domain streams (for cross-domain transfer)
# ===========================================================================
def extract_event_list(path: Path) -> list[str]:
    """Pull the event list out of a domain example script.

    The domain scripts define their events inside ``run()``, so they
    cannot simply be imported. Parsing the literal keeps one source of
    truth: if an example changes its stream, this follows.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not (isinstance(target, ast.Name)
                    and target.id in ("events", "STREAM", "EVENTS")):
                continue
            value = node.value
            if isinstance(value, ast.BinOp) and isinstance(value.op, ast.Mult):
                try:
                    left = ast.literal_eval(value.left)
                    right = ast.literal_eval(value.right)
                except (ValueError, TypeError):
                    continue
                if isinstance(left, list) and isinstance(right, int):
                    return list(left) * right
            if isinstance(value, (ast.List, ast.Tuple)):
                try:
                    return list(ast.literal_eval(value))
                except (ValueError, TypeError):
                    continue
    return []


def load_domains() -> dict[str, list[str]]:
    domains = {}
    if not DOMAIN_DIR.exists():
        return domains
    for path in sorted(DOMAIN_DIR.glob("*.py")):
        events = extract_event_list(path)
        if events:
            domains[path.stem] = events
    return domains


def build_graph(mem_cls, events: list[str]) -> dict[str, set[str]]:
    """Build a temporal graph from a list of events, and return the edges
    that reach the prediction threshold."""
    db = temp_db("ablation_graph.db")
    mem = mem_cls(db)
    try:
        for text in events:
            mem.store(text, event_type="event", source="ablation")
        rows = mem._conn.execute(
            "SELECT tag_from, tag_to FROM precedes WHERE count >= ?",
            (PREDICTION_MIN_COUNT,),
        ).fetchall()
        edges: dict[str, set[str]] = defaultdict(set)
        for a, b in rows:
            edges[a].add(b)
        return dict(edges)
    finally:
        mem.close()
        try:
            db.unlink()
        except OSError:
            pass


def replay(edges: dict[str, set[str]], sequence: list[str]) -> float:
    """Score an edge map against a held-out event sequence."""
    if len(sequence) < 2:
        return 0.0
    contexts = [_extract_tags(e) for e in sequence[:-1]]
    observed = [_extract_tags(e) for e in sequence[1:]]
    return predictive_f1(edges, contexts, observed)


def cross_domain_transfer(mem_cls, domains: dict[str, list[str]]) -> dict:
    """CDT = accuracy with transfer - accuracy without transfer.

    For each target domain B: B is split in half. The transferred model
    is trained on a donor domain A and evaluated on B's held-out half;
    the untransferred model is trained on B's first half and evaluated on
    the same held-out half. Both are scored on identical data.
    """
    names = sorted(domains)
    pairs = []
    for target in names:
        t_events = domains[target]
        if len(t_events) < 4:
            continue
        half = len(t_events) // 2
        b_train, b_test = t_events[:half], t_events[half:]
        base_edges = build_graph(mem_cls, b_train)
        pa_without = replay(base_edges, b_train[-1:] + b_test)
        for donor in names:
            if donor == target:
                continue
            d_edges = build_graph(mem_cls, domains[donor])
            pa_with = replay(d_edges, b_train[-1:] + b_test)
            shared = set(_extract_tags(" ".join(domains[donor]))) & set(
                _extract_tags(" ".join(t_events))
            )
            pairs.append({
                "donor": donor,
                "target": target,
                "pa_with_transfer": round(pa_with, 4),
                "pa_without_transfer": round(pa_without, 4),
                "cdt": round(pa_with - pa_without, 4),
                "shared_tags": len(shared),
            })
    if not pairs:
        return {"pairs": [], "mean_cdt": None}
    mean_cdt = sum(p["cdt"] for p in pairs) / len(pairs)
    return {
        "pairs": pairs,
        "mean_cdt": round(mean_cdt, 4),
        "mean_shared_tags": round(sum(p["shared_tags"] for p in pairs) / len(pairs), 2),
    }


# ===========================================================================
# Running one condition
# ===========================================================================
def run_condition(code: str, name: str, description: str, sleep_cls, mem_cls,
                  stream: list[str], cycles: int, seed: int) -> dict:
    """Run one ablation condition and collect its raw observations."""
    rng = random.Random(seed)
    db = temp_db(f"ablation_{code}.db")
    if db.exists():
        db.unlink()
    mem = mem_cls(db)

    created_ids: dict[str, set[str]] = defaultdict(set)
    seen_signatures: set[str] = set()
    novel_nodes = 0
    all_new_nodes = 0

    try:
        if sleep_cls in (RandomSleepService, RandomCuriosityService):
            sleep = sleep_cls(mem, rng=rng)
        else:
            sleep = sleep_cls(mem)

        last_report = None
        last_event_text = None
        counts = {"pred": [0.0, 0.0, 0.0], "graph": [0.0, 0.0, 0.0], "comp": [0.0, 0.0, 0.0]}
        scored_cycles = 0
        # Contradiction history. Generation 5 oscillates (journal finding 6),
        # so a single-cycle snapshot of contradictions is exactly the kind of
        # reading the project warns against. The density is measured over the
        # whole run instead.
        contradiction_history: list[dict] = []

        for cycle in range(cycles):
            start = (cycle * EVENTS_PER_CYCLE) % len(stream)
            chunk = [stream[(start + k) % len(stream)] for k in range(EVENTS_PER_CYCLE)]

            # Snapshot what the organism knows BEFORE these events arrive.
            snapshot = None
            if last_report is not None and cycle >= cycles - HOLD_CYCLES:
                snap_pred: dict[str, set[str]] = defaultdict(set)
                for p in last_report.predictions:
                    snap_pred[p.source].add(p.target)
                snap_graph: dict[str, set[str]] = defaultdict(set)
                for a, b in mem._conn.execute(
                    "SELECT tag_from, tag_to FROM precedes WHERE count >= ?",
                    (PREDICTION_MIN_COUNT,),
                ).fetchall():
                    snap_graph[a].add(b)
                snap_comp = edges_implied_by_structures(snapshot_structures(last_report))
                snapshot = (snap_pred, snap_graph, snap_comp)

            for text in chunk:
                mem.store(text, event_type="event", source=f"cycle:{cycle}")

            report = sleep.run_sleep_cycle()

            if snapshot is not None:
                seq = ([last_event_text] if last_event_text is not None else []) + chunk
                ctx = [_extract_tags(e) for e in seq[:-1]]
                obs = [_extract_tags(e) for e in seq[1:]]
                for key, edge_map in zip(("pred", "graph", "comp"), snapshot):
                    c = prediction_counts(edge_map, ctx, obs)
                    counts[key][0] += c[0]
                    counts[key][1] += c[1]
                    counts[key][2] += c[2]
                scored_cycles += 1

            last_report = report
            last_event_text = chunk[-1]

            # ---- contradiction accounting, per cycle -------------------
            competing: dict[str, set[str]] = defaultdict(set)
            for h in report.hypotheses:
                if h.expectation != "high_structural_significance":
                    competing[h.subject].add(h.expectation)
            competing_subjects = sum(1 for v in competing.values() if len(v) >= 2)
            cycle_population = sum(len(getattr(report, attr)) for _label, attr in GENERATIONS)
            contradiction_history.append({
                "cycle": cycle,
                "competing_subjects": competing_subjects,
                "population": cycle_population,
                "hypotheses": len(report.hypotheses),
                "theories": len(report.theories),
                "questions": len(report.questions),
            })

            for label, attr in GENERATIONS:
                for cand in getattr(report, attr):
                    d = asdict(cand)
                    cid = d.get("id", "")
                    if cid and cid not in created_ids[label]:
                        created_ids[label].add(cid)
                        all_new_nodes += 1
                        sig = canonical_signature(d)
                        if sig not in seen_signatures:
                            seen_signatures.add(sig)
                            novel_nodes += 1

        pa_organism = f1(*counts["pred"])
        pa_substrate = f1(*counts["graph"])
        pa_compressed = f1(*counts["comp"])

        # ---- surviving structures -------------------------------------
        # "Surviving" means alive in the final cycle's population -- not
        # everything the candidate store still holds, which includes
        # long-decayed historical versions.
        populations = {label: len(getattr(last_report, attr)) for label, attr in GENERATIONS}
        n_surviving = sum(populations.values())
        surviving_structures = snapshot_structures(last_report)

        # ---- experience coverage --------------------------------------
        # How much of the experience stream do the surviving structures
        # actually represent? An event is covered when every one of its
        # tags appears in some surviving structure. This is the numerator
        # of SCR, and it is what stops "destroy your own structures" from
        # scoring as excellent compression.
        struct_tags = structure_tags(surviving_structures)
        distinct_event_tags = {
            tuple(t for t in (row[0] or "").split(",") if t)
            for row in mem._conn.execute(
                "SELECT DISTINCT tags FROM events WHERE event_type != 'sleep'"
            ).fetchall()
        }
        distinct_event_tags.discard(())
        covered = sum(1 for tags in distinct_event_tags if set(tags) <= struct_tags)
        n_experience_distinct = len(distinct_event_tags)
        n_experience_instances = mem._conn.execute(
            "SELECT COUNT(*) FROM events WHERE event_type != 'sleep'"
        ).fetchone()[0]

        # ---- contradictions -------------------------------------------
        # Density is measured over the whole run, not read off the final
        # cycle. A single cycle is a sample of an oscillating quantity.
        usable = [h for h in contradiction_history if h["population"] > 0]
        if usable:
            densities = [(h["competing_subjects"] / h["population"]) * 1000.0
                         for h in usable]
            cd_mean = sum(densities) / len(densities)
            cd_duty = sum(1 for h in usable if h["competing_subjects"] > 0) / len(usable)
            cd_mean_subjects = (sum(h["competing_subjects"] for h in usable) / len(usable))
        else:
            cd_mean = None
            cd_duty = None
            cd_mean_subjects = None
        final_competing = contradiction_history[-1]["competing_subjects"] if contradiction_history else 0

        # ---- lineage ---------------------------------------------------
        audit = lineage_audit(db)

        observations = {
            "n_experience_events": n_experience_distinct,
            "n_experience_event_instances": n_experience_instances,
            "covered_events": covered,
            "n_surviving_structures": n_surviving,
            "created": {label: len(ids) for label, ids in created_ids.items()},
            "survived": populations,
            "pa": pa_organism,
            "pa_substrate": pa_substrate,
            "pa_compressed": pa_compressed,
            "scored_cycles": scored_cycles,
            "contradictions": final_competing,
            "contradiction_history": contradiction_history,
            "cd_mean_density": cd_mean,
            "cd_duty_cycle": cd_duty,
            "cd_mean_competing_subjects": cd_mean_subjects,
            "active_nodes": n_surviving,
            "novel_nodes": novel_nodes,
            "all_new_nodes": all_new_nodes,
            "grounded": audit["grounded"],
            "resolvable": audit["candidates_requiring_lineage"],
        }

        return {
            "condition": code,
            "name": name,
            "description": description,
            "cycles": cycles,
            "seed": seed,
            "observations": observations,
            "final_populations": populations,
            "lineage": {
                "grounded": audit["grounded"],
                "unverifiable_evicted": audit["unverifiable_evicted"],
                "ungrounded": audit["ungrounded_no_g0_tags"],
                "no_parents_at_all": audit["no_parents_at_all"],
            },
            "metrics": compute_all(observations),
        }
    finally:
        mem.close()
        try:
            db.unlink()
        except OSError:
            pass


# ===========================================================================
# The condition table
# ===========================================================================
CONDITIONS = [
    ("O_FULL", "Full system",
     "Everything on. The reference condition every ablation is compared against.",
     SleepService, MemoryService),
    ("A", "No Sleep",
     "Consolidation, synthesis and dream generation disabled. Experience only.",
     NoSleepService, MemoryService),
    ("B", "No Lineage",
     "Every candidate stored with its parent_ids stripped. Structures computed identically.",
     NoLineageService, MemoryService),
    ("C", "No Curiosity",
     "Expected Information Gain ranking and investigation prioritisation disabled (Layers 7-8).",
     NoCuriosityService, MemoryService),
    ("D", "No Falsification",
     "No refutation, no extinction, no belief revision. Nothing can ever die.",
     NoFalsificationService, MemoryService),
    ("E", "No Dreams",
     "Completion, analogy, mutation and conditional dream generation disabled.",
     NoDreamsService, MemoryService),
    ("F", "No Hypothesis Layer",
     "Generation 4 bypassed. Theories and Questions built directly from Workflow components.",
     NoHypothesisLayerService, MemoryService),
    ("G", "No Questions",
     "Generation 5 Question creation disabled. Theories kept.",
     NoQuestionsService, MemoryService),
    ("H", "Random Curiosity",
     "EIG ranking replaced by a random ordering of the same candidates. Same node volume.",
     RandomCuriosityService, MemoryService),
    ("I", "Random Sleep",
     "Every layer's output replaced by random structures of the same count.",
     RandomSleepService, MemoryService),
    ("J", "Memory Without Structure",
     "Raw events stored; no co-occurrence or temporal edges ever written.",
     SleepService, NoStructureMemory),
]


# ===========================================================================
# Reporting
# ===========================================================================
METRIC_LABELS = [
    ("pa", "PA"),
    ("pa_substrate", "PA_sub"),
    ("ip", "IP"),
    ("scr", "SCR"),
    ("ss", "SS"),
    ("lc", "LC"),
    ("cd", "CD"),
    ("cdt", "CDT"),
    ("nsr", "NSR"),
]


def fmt(value) -> str:
    if value is None:
        return "  n/a"
    if isinstance(value, float):
        return f"{value:5.3f}"
    return f"{value:>5}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Organica ablation study.")
    ap.add_argument("--cycles", type=int, default=30,
                    help="sleep cycles per condition (default: 30)")
    ap.add_argument("--out", default="docs/ablation_study.json")
    ap.add_argument("--only", default="",
                    help="comma-separated condition codes, e.g. A,D,H")
    args = ap.parse_args()

    only = {c.strip().upper() for c in args.only.split(",") if c.strip()}

    print("=" * 100)
    print("ORGANICA ABLATION STUDY -- which mechanisms are doing the work?")
    print("=" * 100)
    print(f"  stimulus     : study stream ({len(STUDY_STREAM)} events), "
          f"{EVENTS_PER_CYCLE}/cycle, same ingestion as the live daemon")
    print(f"  scoring      : forward-looking -- the last {HOLD_CYCLES} cycles are "
          f"scored against events the organism had not yet seen")
    print(f"  cycles       : {args.cycles} per condition")
    print("  engine       : untouched (all ablations applied in-process)")
    print()

    results = []
    for idx, (code, name, desc, sleep_cls, mem_cls) in enumerate(CONDITIONS):
        if only and code not in only:
            continue
        t0 = time.time()
        res = run_condition(code, name, desc, sleep_cls, mem_cls, STUDY_STREAM,
                            args.cycles, seed=1000 + idx)
        res["wall_seconds"] = round(time.time() - t0, 1)
        results.append(res)
        m = res["metrics"]
        print(f"  {code:<7} {name:<28} ES={fmt(m.get('es'))}  "
              f"PA={fmt(m.get('pa'))}  LC={fmt(m.get('lc'))}  "
              f"NSR={fmt(m.get('nsr'))}  ({res['wall_seconds']}s)")

    if not results:
        print("  no conditions matched")
        return 1

    full = next((r for r in results if r["condition"] == "O_FULL"), None)
    if full is None:
        print("\n  WARNING: O_FULL was not run; no Impact scores can be computed.")
        full = results[0]

    # ---- cross-domain transfer (architecture-level, not per condition) --
    domains = load_domains()
    cdt = cross_domain_transfer(MemoryService, domains) if domains else {"pairs": [], "mean_cdt": None}
    if cdt.get("mean_cdt") is not None:
        full["metrics"]["cdt"] = cdt["mean_cdt"]
        full["metrics"]["cdt_detail"] = cdt

    # ---- the primary table: per-metric deltas --------------------------
    comparisons = {}
    for res in results:
        if res["condition"] == "O_FULL":
            continue
        comparisons[res["condition"]] = compare(full["metrics"], res["metrics"])

    print()
    print("=" * 100)
    print("PER-METRIC DELTAS  (full system minus ablated -- the primary result)")
    print("=" * 100)
    header = f"{'cond':<7}" + "".join(f"{lbl:>9}" for _, lbl in METRIC_LABELS)
    print(header)
    print("-" * 100)
    print(f"{'O_FULL':<7}" + "".join(
        f"{fmt(full['metrics'].get(k)):>9}" for k, _ in METRIC_LABELS))
    print("-" * 100)
    for res in results:
        if res["condition"] == "O_FULL":
            continue
        deltas = comparisons[res["condition"]]["deltas"]
        print(f"{res['condition']:<7}" + "".join(
            f"{fmt(deltas.get(k)):>9}" for k, _ in METRIC_LABELS))

    print()
    print("=" * 100)
    print("IMPACT  (ES_full - ES_ablated; bands: <5 cosmetic, 5-15 supportive,")
    print("        15-30 important, 30-50 foundational, >50 existential)")
    print("=" * 100)
    for res in results:
        if res["condition"] == "O_FULL":
            continue
        c = comparisons[res["condition"]]
        print(f"  {res['condition']:<7} {res['name']:<28} ES {fmt(c['es_full'])} -> "
              f"{fmt(c['es_ablated'])}   impact={fmt(c['impact'])}  [{c['impact_band']}]")

    if cdt.get("mean_cdt") is not None:
        print()
        print(f"  Cross-domain transfer (CDT): mean {cdt['mean_cdt']} "
              f"over {len(cdt['pairs'])} domain pairs, "
              f"mean shared vocabulary {cdt.get('mean_shared_tags')} tags")

    out = REPO_ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": "G",
        "title": "Organica Ablation Study",
        "preregistration": "docs/ABLATION-PREREGISTRATION.md",
        "protocol": {
            "stimulus": "organica/streams.py STUDY_STREAM (full, 48 events)",
            "ingestion": f"{EVENTS_PER_CYCLE} events per cycle, rotating -- "
                         "identical to the live daemon",
            "scoring": f"forward-looking: the last {HOLD_CYCLES} cycles are scored "
                       "against events the organism had not yet seen",
            "events_per_cycle": EVENTS_PER_CYCLE,
            "cycles": args.cycles,
            "engine_modified": False,
            "ablation_method": "in-process subclassing of SleepService/MemoryService",
            "random_seed_base": 1000,
            "note": "single seed per condition; no variance estimate is claimed",
        },
        "not_measurable": {
            "cy": "Q_resolved / Q_generated -- no experiment executor exists, so no "
                  "Question is ever resolved; identically 0 for every condition",
            "eig_star": "H_before - H_after -- experiments are generated but never "
                        "executed, so no belief entropy ever changes; identically 0",
            "dpf": "requires the human designer to record predictions before a run; "
                   "cannot be automated without circularity",
        },
        "cross_domain_transfer": cdt,
        "conditions": results,
        "comparisons": comparisons,
    }, indent=2), encoding="utf-8")
    print(f"\n  Full report written to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
