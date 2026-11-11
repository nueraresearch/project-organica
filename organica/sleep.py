"""
Sleep Service — Stages 4 through 10 (Sleep V5: Categorized Dreams, Expected Information Gain, and Investigation Ranking).

Developmental Layer Ladder:
  Events (Experience)
    ↓
  Concepts & Predictions (Layer 1)
    ↓
  Processes & Meta-Concepts & Roles (Layer 2)
    ↓
  Workflow Concepts & Relational Schemas (Layer 3)
    ↓
  Hypothesis Candidates (Layer 4)
    ↓
  Theory & Question Candidates (Layer 5 - Dialectic Tension & Entropy)
    ↓
  Categorized Dreams (Layer 6):
       - completion_dream: Graph transitive shortcut
       - analogy_dream: Co-occurrence neighbor substitution
       - mutation_dream: Structural path extension/variation
       - conditional_dream: Disambiguating context for high-uncertainty questions
    ↓
  Investigation Candidates (Layer 7 - The Attention Economy):
       - Prioritizes investigations by Expected Information Gain (EIG)
       - Currency shift: Importance != Confidence; Importance ~= Expected Information Gain
    ↓
  Active Experiment Probes (Layer 8 - Active Inquiry & Law IV verification)

Design rules:
  1. No language generation, no text prompts, no LLMs.
  2. Pure graph nodes with deterministic IDs, lineage parents, and numeric provenance.
  3. Strict Epistemic Selection: The organism ranks what to investigate next.
"""

import json
import math
import random
import time
from collections import defaultdict
from typing import Optional, Any

from .candidates import (
    _make_id,
    _TagScore,
    ConceptCandidate,
    PhraseCandidate,
    LoopCandidate,
    PredictionCandidate,
    AnomalyCandidate,
    MetaConceptCandidate,
    ProcessCandidate,
    WorkflowConceptCandidate,
    RoleCandidate,
    SchemaCandidate,
    HypothesisCandidate,
    TheoryCandidate,
    QuestionCandidate,
    DreamCandidate,
    InvestigationCandidate,
    ExperimentCandidate,
    SleepReport,
)
from .memory import MemoryService
from .sleep_extraction import SleepExtractionMixin
from .sleep_synthesis import SleepSynthesisMixin
from .sleep_inquiry import SleepInquiryMixin
from .sleep_selection import SleepSelectionMixin


class SleepService(SleepExtractionMixin, SleepSynthesisMixin, SleepInquiryMixin, SleepSelectionMixin):
    """Main service that orchestrates a sleep cycle across all developmental layers."""

    CONCEPT_MIN_DEGREE      = 4
    CONCEPT_MAX_CLUSTERING  = 1.0     # Retuned from 0.4: dense cliques / correlated groups (clustering up to 1.0) form concepts
    CONCEPT_MIN_REACH       = 4
    PHRASE_MIN_CLUSTERING   = 0.7
    PHRASE_MAX_REACH        = 2
    LOOP_MIN_STRENGTH       = 5
    PREDICTION_MIN_COUNT    = 5
    COOC_MIN_EDGE           = 2

    META_CONCEPT_MIN_REFS   = 3
    STABLE_THRESHOLD        = 0.3
    DEATH_THRESHOLD         = 0.15

    # Temporal precedence edge decay factor applied each sleep cycle (Law VI).
    # 0.95 = 5% per-cycle decay; early-regime counts fade over ~20 cycles.
    TEMPORAL_DECAY_FACTOR   = 0.95

    # Source-frequency denominator decay, matched to the temporal graph.
    # The raw tag count grows without bound on a repeated stimulus, so dividing a
    # decayed temporal count by it dilutes a re-presented edge with its own history.
    # D3-PERSISTENCE-2 measured this repair; the owner promoted it on 2026-11-10.
    FREQUENCY_DECAY         = 0.95

    MAX_HYPOTHESES          = 15
    MAX_THEORIES            = 8
    MAX_QUESTIONS           = 6
    MAX_DREAMS              = 8
    MAX_INVESTIGATIONS      = 5
    MAX_EXPERIMENTS         = 5

    # Per-layer output caps
    MAX_LOOPS               = 15
    # 112 since 0.15.0: DECISION-CAP-LEVEL option C, landed 2026-11-11. The cap is the
    # returned window and its transition/cooccurrence split is derived from it (E1).
    MAX_PREDICTIONS         = 112
    MAX_ANOMALIES           = 10
    MAX_META_CONCEPTS       = 15
    MAX_PROCESSES           = 10
    MAX_WORKFLOWS           = 10
    MAX_ROLES               = 10
    MAX_SCHEMAS             = 5

    WORKFLOW_MIN_MATCHED_METAS = 2

    HYPOTHESIS_RETENTION = "salience"

    VALID_RETENTION_POLICIES = (
        "alphabetical",    # legacy: sort by (subject, -confidence)
        "confidence",      # most confident first
        "contradiction",   # most contradicting evidence first (RAW COUNT)
        "tension",         # most contested first, as a SHARE of flow
        "salience",        # the composite score (default)
        "stochastic",      # weighted lottery proportional to salience
        "shannon_entropy", # most informationally undetermined subject first
    )

    SALIENCE_WEIGHTS = (0.25, 0.25, 0.25, 0.25)
    CONTRADICTION_SCALE = 1.0
    MAX_STRUCTURAL_MARKERS = 15
    RANDOM_SEED = 0

    def __init__(self, memory: MemoryService):
        self.memory = memory
        self._rng = random.Random(self.RANDOM_SEED)
        self._decayed_freqs: dict[str, float] = {}
        self._last_raw_freqs: dict[str, float] = {}
        self._frequency_cycle_key = None
        self.frequency_updates = 0

    def _update_frequency_denominator(self, raw: dict[str, int]) -> dict[str, float]:
        """One cycle's decayed counter: D = 0.95 * D_previous + the raw count delta."""
        raw = {tag: float(count) for tag, count in raw.items()}
        if not self._decayed_freqs:
            self._decayed_freqs = dict(raw)
        else:
            tags = set(raw) | set(self._decayed_freqs) | set(self._last_raw_freqs)
            self._decayed_freqs = {
                tag: (self.FREQUENCY_DECAY * self._decayed_freqs.get(tag, 0.0)
                      + max(0.0, raw.get(tag, 0.0) - self._last_raw_freqs.get(tag, 0.0)))
                for tag in tags
            }
        self._last_raw_freqs = raw
        self.frequency_updates += 1
        return self._decayed_freqs

    def _prediction_frequencies(self, raw: dict[str, int]) -> dict[str, float]:
        """Update once per sleep cycle, so a second prediction call cannot apply a delta twice."""
        key = self.memory.latest_sleep_cycle()
        if key != self._frequency_cycle_key:
            self._frequency_cycle_key = key
            self._update_frequency_denominator(raw)
        return self._decayed_freqs

    def run_sleep_cycle(self) -> SleepReport:
        """Public API used by ``run_continuous.py``."""
        return self.run()

    def run(self) -> SleepReport:
        cooc     = self._load_cooccurrences()
        temporal = self._load_temporal()
        freqs    = dict(self.memory.tag_frequencies())
        prior    = self._load_prior_candidates()
        self._prior_cache = prior

        try:
            cycle = self._count_prior_cycles(prior) + 1

            # Build index of recent empirical events for Layer 1 grounding (Defect D3)
            recent_events = self.memory.recent(n=500, event_type="observe")
            tag_events: dict[str, list[str]] = defaultdict(list)
            for e in recent_events:
                for t in e.tags:
                    if len(tag_events[t]) < 10:
                        tag_events[t].append(e.id)
            self._current_tag_events = tag_events

            # ---- Layer 1: Candidates from graphs ----
            tag_scores   = self._score_tags(freqs, cooc, temporal)
            hub_tags     = {s.tag for s in tag_scores if s.classification == "hub"}
            if hub_tags:
                filtered_cooc = {
                    t: {nbr: cnt for nbr, cnt in targets.items() if nbr not in hub_tags}
                    for t, targets in cooc.items() if t not in hub_tags
                }
                communities  = self._find_communities(filtered_cooc)
            else:
                communities  = self._find_communities(cooc)
            concepts     = self._build_concepts(tag_scores, communities, cooc)
            phrases      = self._build_phrases(tag_scores, cooc)
            loops        = self._build_loops(temporal)
            self._current_cooc = cooc
            prior_schemas = [
                c for c in prior
                if c.get("type") == "schema_candidate"
                and (c.get("confidence") or c.get("strength") or 0) >= self.STABLE_THRESHOLD
            ]
            self._current_prior_schemas = prior_schemas
            try:
                predictions  = self._build_predictions(temporal, freqs)
            finally:
                self._current_cooc = None
                self._current_tag_events = None
                self._current_prior_schemas = None
            anomalies    = self._build_anomalies(temporal, freqs)

            # ---- Layer 2: Composites ----
            stable_prior = [c for c in prior
                            if c.get("type") not in ("_sleep_meta", "anomaly")
                            and (c.get("confidence") or c.get("strength") or 0) >= self.STABLE_THRESHOLD]

            meta_concepts = self._compose_meta_concepts(stable_prior)
            processes     = self._compose_processes(stable_prior)
            roles         = self._extract_structural_roles(
                communities=communities,
                concepts=concepts,
                temporal=temporal,
                freqs=freqs,
                predictions=predictions,
                recent_events=recent_events,
            )

            all_roles = list(roles)
            for c in stable_prior:
                if c.get("type") == "role_candidate" and c.get("id") not in {r.id for r in all_roles}:
                    all_roles.append(RoleCandidate(
                        id=c.get("id"),
                        generation=c.get("generation", 2),
                        parent_ids=c.get("parent_ids", []),
                        exemplars=c.get("exemplars", []),
                        profile=c.get("profile", {}),
                        confidence=c.get("confidence", 1.0),
                        evidence=c.get("evidence", {}),
                        carried_forward=True,
                    ))

            # ---- Layer 3: Workflows ----
            workflow_concepts = self._compose_workflows(meta_concepts, processes, stable_prior)

            all_workflows = list(workflow_concepts)
            for c in stable_prior:
                if c.get("type") == "workflow_concept" and c.get("id") not in {w.id for w in all_workflows}:
                    all_workflows.append(WorkflowConceptCandidate(
                        id=c.get("id"),
                        generation=c.get("generation", 3),
                        parent_ids=c.get("parent_ids", []),
                        name=c.get("name", ""),
                        components=c.get("components", []),
                        confidence=c.get("confidence", 1.0),
                        evidence=c.get("evidence", {}),
                        carried_forward=True,
                    ))

            all_processes = list(processes)
            for c in stable_prior:
                if c.get("type") == "process_candidate" and c.get("id") not in {p.id for p in all_processes}:
                    all_processes.append(ProcessCandidate(
                        id=c.get("id"),
                        generation=c.get("generation", 2),
                        parent_ids=c.get("parent_ids", []),
                        cycle=c.get("cycle", []),
                        strength=c.get("strength", 1.0),
                        evidence=c.get("evidence", {}),
                        carried_forward=True,
                    ))

            all_metas = list(meta_concepts)
            for c in stable_prior:
                if c.get("type") == "meta_concept" and c.get("id") not in {m.id for m in all_metas}:
                    all_metas.append(MetaConceptCandidate(
                        id=c.get("id"),
                        generation=c.get("generation", 2),
                        parent_ids=c.get("parent_ids", []),
                        anchor_tag=c.get("anchor_tag", ""),
                        related_candidates=c.get("related_candidates", 0),
                        confidence=c.get("confidence", 1.0),
                        evidence=c.get("evidence", {}),
                        carried_forward=True,
                    ))

            # ---- Layer 3b: Relational Schemas ----
            schemas = self._extract_relational_schemas(
                temporal=temporal,
                freqs=freqs,
                communities=communities,
                concepts=concepts,
                predictions=predictions,
                prior=prior,
                roles=all_roles,
                recent_events=recent_events,
            )

            all_schemas = list(schemas)
            for c in stable_prior:
                if c.get("type") == "schema_candidate" and c.get("id") not in {s.id for s in all_schemas}:
                    all_schemas.append(SchemaCandidate(
                        id=c.get("id"),
                        generation=c.get("generation", 3),
                        parent_ids=c.get("parent_ids", []),
                        source_role=c.get("source_role", ""),
                        target_role=c.get("target_role", ""),
                        source_exemplars=c.get("source_exemplars", []),
                        target_exemplars=c.get("target_exemplars", []),
                        confidence=c.get("confidence", 1.0),
                        evidence=c.get("evidence", {}),
                        carried_forward=True,
                    ))

            # ---- Layer 4: Hypotheses (V3) ----
            hypotheses = self._form_and_test_hypotheses(
                temporal=temporal,
                freqs=freqs,
                workflows=all_workflows,
                processes=all_processes,
                meta_concepts=all_metas,
                prior=prior,
            )

            # ---- Layer 5: Theories & Questions (Curiosity) (V4) ----
            theories, questions = self._form_theories_and_questions(hypotheses, prior)

            # ---- Layer 6: Categorized Dreams (V5) ----
            dreams = self._generate_categorized_dreams(
                workflows=all_workflows,
                processes=all_processes,
                meta_concepts=all_metas,
                questions=questions,
                cooc=cooc,
                temporal=temporal,
            )

            # ---- Layer 7: Investigation Candidates / Attention Economy (V5) ----
            investigations = self._rank_investigations(questions, dreams)

            # ---- Layer 8: Active Experiment Selection (V6 / Path B) ----
            experiments = self._select_experiments(investigations, questions, dreams)

            # ---- Natural Selection: Unified G1–G8 Pass (Law VI) ----
            with self.memory.batch():
                strengthened, decayed, pruned = self._natural_selection(
                    prior, concepts, phrases, loops, predictions,
                    meta_concepts=all_metas,
                    processes=all_processes,
                    roles=all_roles,
                    workflows=all_workflows,
                    schemas=all_schemas,
                    hypotheses=hypotheses,
                    theories=theories,
                    questions=questions,
                    dreams=dreams,
                    investigations=investigations,
                    experiments=experiments,
                )

            # ---- Temporal Precedence Edge Decay (World-Adaptation) ----
            self.memory.decay_temporal_edges(factor=self.TEMPORAL_DECAY_FACTOR, min_count=1)

            composites_created = (len(meta_concepts) + len(processes) + len(workflow_concepts) +
                                  len(all_schemas) + len(hypotheses) + len(theories) + len(questions) +
                                  len(dreams) + len(investigations) + len(experiments))

            # M3 — contradiction density
            if hypotheses:
                densities = []
                for h in hypotheses:
                    total = h.support_count + h.contradiction_count
                    densities.append(h.contradiction_count / total if total > 0 else 0.0)
                m3 = round(sum(densities) / len(densities), 6)
            else:
                m3 = 0.0

            report = SleepReport(
                cycle=cycle,
                ran_at=time.time(),
                concepts=concepts,
                phrases=phrases,
                loops=loops,
                predictions=predictions,
                anomalies=anomalies,
                meta_concepts=meta_concepts,
                processes=processes,
                roles=all_roles,
                workflow_concepts=workflow_concepts,
                schemas=all_schemas,
                hypotheses=hypotheses,
                theories=theories,
                questions=questions,
                dreams=dreams,
                investigations=investigations,
                experiments=experiments,
                prior_candidates_loaded=len(prior),
                candidates_strengthened=strengthened,
                candidates_decayed=decayed,
                candidates_pruned=pruned,
                composites_created=composites_created,
                contradiction_density=m3,
            )
            with self.memory.batch():
                self._store_candidates(report)
            return report
        finally:
            self._prior_cache = None

    def _stochastic_retain(self, beliefs, scores) -> list:
        pool = list(beliefs)
        weights = [max(0.0, scores[h.id]) + 1e-9 for h in pool]
        chosen = []
        while pool and len(chosen) < self.MAX_HYPOTHESES:
            total = sum(weights)
            if total <= 0:
                chosen.extend(pool[:self.MAX_HYPOTHESES - len(chosen)])
                break
            pick = self._rng.random() * total
            acc = 0.0
            for i, w in enumerate(weights):
                acc += w
                if acc >= pick:
                    chosen.append(pool.pop(i))
                    weights.pop(i)
                    break
        return chosen

    # ==================================================================
    # Layer 5: Theories & Questions / Curiosity (Sleep V4)
    # ==================================================================

    def _form_theories_and_questions(
        self,
        hypotheses: list[HypothesisCandidate],
        prior: list[dict],
    ) -> tuple[list[TheoryCandidate], list[QuestionCandidate]]:
        by_subject: dict[str, list[HypothesisCandidate]] = defaultdict(list)
        for h in hypotheses:
            if h.expectation != "high_structural_significance":
                by_subject[h.subject].append(h)

        closed_qids = {
            p.get("id") for p in prior
            if p.get("type") == "question" and (p.get("closed") or p.get("evidence", {}).get("closed") or p.get("evidence", {}).get("resolved_by"))
        }

        theories = []
        questions = []

        for subject, hyps in by_subject.items():
            if len(hyps) < 2:
                continue

            hyps.sort(key=lambda h: h.support_count, reverse=True)
            top_hyps = hyps[:3]
            hyp_ids = [h.id for h in top_hyps]
            expectations = [h.expectation for h in top_hyps]

            total_support = sum(h.support_count for h in top_hyps)
            total_contra = sum(h.contradiction_count for h in top_hyps)
            avg_conf = sum(h.confidence for h in top_hyps) / len(top_hyps)

            tid = _make_id("theory", subject, *sorted(expectations))
            theories.append(TheoryCandidate(
                id=tid,
                generation=5,
                subject=subject,
                hypotheses=hyp_ids,
                confidence=round(avg_conf, 4),
                support_count=total_support,
                contradiction_count=total_contra,
                parent_ids=hyp_ids,
                evidence={
                    "competing_count": len(top_hyps),
                    "expectations": expectations,
                    "hypothesis_confidences": [h.confidence for h in top_hyps],
                },
            ))

            h1, h2 = top_hyps[0], top_hyps[1]
            s1, s2 = h1.support_count, h2.support_count
            total_pair = s1 + s2
            if total_pair > 0:
                p1 = s1 / total_pair
                p2 = s2 / total_pair
                entropy = 0.0
                if p1 > 0 and p2 > 0:
                    entropy = -(p1 * math.log2(p1) + p2 * math.log2(p2))

                maturity = min(1.0, total_pair / 10.0)
                uncertainty = round(entropy * maturity, 4)

                qid = _make_id("question", subject, *sorted([h1.expectation, h2.expectation]))
                if qid not in closed_qids:
                    questions.append(QuestionCandidate(
                        id=qid,
                        generation=5,
                        subject=subject,
                        competing_expectations=[h1.expectation, h2.expectation],
                        uncertainty=uncertainty,
                        parent_ids=[h1.id, h2.id],
                        evidence={
                            "ratio": [round(p1, 3), round(p2, 3)],
                            "supports": [s1, s2],
                            "total_pair_evidence": total_pair,
                        },
                    ))

        theories.sort(key=lambda t: t.support_count, reverse=True)
        questions.sort(key=lambda q: q.uncertainty, reverse=True)
        return theories[:self.MAX_THEORIES], questions[:self.MAX_QUESTIONS]

