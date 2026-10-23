"""
Sleep Service — Stages 4 through 10 (Sleep V5: Categorized Dreams, Expected Information Gain, and Investigation Ranking).

Developmental Layer Ladder:
  Events (Experience)
    ↓
  Concepts & Predictions (Layer 1)
    ↓
  Processes & Meta-Concepts (Layer 2)
    ↓
  Workflow Concepts (Layer 3)
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

Design rules:
  1. No language generation, no text prompts, no LLMs.
  2. Pure graph nodes with deterministic IDs, lineage parents, and numeric provenance.
  3. Strict Epistemic Selection: The organism ranks what to investigate next.
"""

import hashlib
import json
import math
import random
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional

from .memory import MemoryService


def _make_id(type_prefix: str, *key_parts: str) -> str:
    key = "|".join(key_parts)
    short_hash = hashlib.sha256(key.encode()).hexdigest()[:8]
    return f"{type_prefix}_{short_hash}"


# ------------------------------------------------------------------
# Layer 1 - 5 Candidate Types
# ------------------------------------------------------------------

@dataclass
class ConceptCandidate:
    type: str = "concept_candidate"
    id: str = ""
    generation: int = 1
    parent_ids: list[str] = field(default_factory=list)
    members: list[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class PhraseCandidate:
    type: str = "phrase_candidate"
    id: str = ""
    generation: int = 1
    parent_ids: list[str] = field(default_factory=list)
    members: list[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class LoopCandidate:
    type: str = "loop_candidate"
    id: str = ""
    generation: int = 1
    parent_ids: list[str] = field(default_factory=list)
    path: list[str] = field(default_factory=list)
    strength: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class PredictionCandidate:
    type: str = "prediction_candidate"
    id: str = ""
    generation: int = 1
    parent_ids: list[str] = field(default_factory=list)
    source: str = ""
    target: str = ""
    strength: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class AnomalyCandidate:
    type: str = "anomaly"
    id: str = ""
    generation: int = 1
    parent_ids: list[str] = field(default_factory=list)
    expected: str = ""
    observed: str = ""
    context: str = ""
    evidence: dict = field(default_factory=dict)


@dataclass
class MetaConceptCandidate:
    type: str = "meta_concept"
    id: str = ""
    generation: int = 1
    parent_ids: list[str] = field(default_factory=list)
    anchor_tag: str = ""
    related_candidates: int = 0
    confidence: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class ProcessCandidate:
    type: str = "process_candidate"
    id: str = ""
    generation: int = 1
    parent_ids: list[str] = field(default_factory=list)
    cycle: list[str] = field(default_factory=list)
    strength: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class WorkflowConceptCandidate:
    type: str = "workflow_concept"
    id: str = ""
    generation: int = 2
    parent_ids: list[str] = field(default_factory=list)
    name: str = ""
    components: list[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class HypothesisCandidate:
    type: str = "hypothesis"
    id: str = ""
    generation: int = 3
    subject: str = ""
    expectation: str = ""
    confidence: float = 0.0
    support_count: int = 0
    contradiction_count: int = 0
    parent_ids: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


@dataclass
class TheoryCandidate:
    type: str = "theory"
    id: str = ""
    generation: int = 4
    subject: str = ""
    hypotheses: list[str] = field(default_factory=list)
    confidence: float = 0.0
    support_count: int = 0
    contradiction_count: int = 0
    parent_ids: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


@dataclass
class QuestionCandidate:
    type: str = "question"
    id: str = ""
    generation: int = 4
    subject: str = ""
    competing_expectations: list[str] = field(default_factory=list)
    uncertainty: float = 0.0
    parent_ids: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


# ------------------------------------------------------------------
# Layer 6 Candidate Type (V5: Categorized Dreams)
# ------------------------------------------------------------------

@dataclass
class DreamCandidate:
    type: str = "dream"
    id: str = ""
    generation: int = 5
    dream_category: str = ""   # completion | analogy | mutation | conditional
    subject: str = ""
    path_or_context: list[str] = field(default_factory=list)
    confidence: float = 0.05
    novelty: float = 0.5
    parent_ids: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


# ------------------------------------------------------------------
# Layer 7 Candidate Type (V5: Investigation Candidate / Research Agenda)
# ------------------------------------------------------------------

@dataclass
class InvestigationCandidate:
    """Ranks what to investigate next based on Expected Information Gain (EIG)."""
    type: str = "investigation"
    id: str = ""
    generation: int = 6
    target_id: str = ""         # Question or Dream ID
    target_type: str = ""       # question | dream
    subject: str = ""
    novelty: float = 0.0
    uncertainty: float = 0.0
    expected_information_gain: float = 0.0
    parent_ids: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


# ------------------------------------------------------------------
# Layer 8 Candidate Type (Sleep V6 / Path B: Active Experiment Probes)
# ------------------------------------------------------------------

@dataclass
class ExperimentCandidate:
    """A concrete intervention or test designed to resolve an investigation."""
    type: str = "experiment"
    id: str = ""
    generation: int = 7
    investigation_id: str = ""
    target_id: str = ""         # Question ID or Dream ID being probed
    target_type: str = ""       # question | dream
    action_type: str = ""       # e.g., "probe_context", "probe_sequence", "probe_state"
    probe_payload: dict = field(default_factory=dict)
    expected_outcomes: list[str] = field(default_factory=list)
    cost: float = 1.0           # Computational or environmental action cost
    priority: float = 0.0       # EIG / cost
    status: str = "proposed"    # proposed | executed | validated | refuted
    parent_ids: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


# ------------------------------------------------------------------
# Internal scoring helper
# ------------------------------------------------------------------

@dataclass
class _TagScore:
    tag: str
    frequency: int
    degree: int
    clustering: float
    predictive_reach: int
    classification: str = ""


# ------------------------------------------------------------------
# Sleep report
# ------------------------------------------------------------------

@dataclass
class SleepReport:
    cycle: int
    ran_at: float
    # Layer 1
    concepts: list[ConceptCandidate]        = field(default_factory=list)
    phrases: list[PhraseCandidate]          = field(default_factory=list)
    loops: list[LoopCandidate]              = field(default_factory=list)
    predictions: list[PredictionCandidate]  = field(default_factory=list)
    anomalies: list[AnomalyCandidate]       = field(default_factory=list)
    # Layer 2
    meta_concepts: list[MetaConceptCandidate] = field(default_factory=list)
    processes: list[ProcessCandidate]         = field(default_factory=list)
    # Layer 3
    workflow_concepts: list[WorkflowConceptCandidate] = field(default_factory=list)
    # Layer 4
    hypotheses: list[HypothesisCandidate]     = field(default_factory=list)
    # Layer 5
    theories: list[TheoryCandidate]           = field(default_factory=list)
    questions: list[QuestionCandidate]        = field(default_factory=list)
    # Layer 6
    dreams: list[DreamCandidate]              = field(default_factory=list)
    # Layer 7
    investigations: list[InvestigationCandidate] = field(default_factory=list)
    # Layer 8 (Sleep V6)
    experiments: list[ExperimentCandidate]    = field(default_factory=list)
    # Dynamics stats
    prior_candidates_loaded: int = 0
    candidates_strengthened: int = 0
    candidates_decayed: int      = 0
    candidates_pruned: int       = 0
    composites_created: int      = 0


# ------------------------------------------------------------------
# The Sleep Service (V5)
# ------------------------------------------------------------------

class SleepService:
    """Main service that orchestrates a sleep cycle.
    The original implementation had a private method ``_run_sleep_cycle`` which
    performed the full pipeline, but the public entry point expected by the
    continuous runner was missing.  This wrapper simply forwards the call to the
    existing private implementation, returning the ``SleepReport`` instance.
    """

    def run_sleep_cycle(self):
        """Public API used by ``run_continuous.py``.

        Returns
        -------
        SleepReport
            The report generated by the internal ``_run_sleep_cycle`` method.
        """
        return self.run()


    CONCEPT_MIN_DEGREE      = 4
    CONCEPT_MAX_CLUSTERING  = 0.4
    CONCEPT_MIN_REACH       = 4
    PHRASE_MIN_CLUSTERING   = 0.7
    PHRASE_MAX_REACH        = 2
    LOOP_MIN_STRENGTH       = 5
    PREDICTION_MIN_COUNT    = 5
    COOC_MIN_EDGE           = 2

    META_CONCEPT_MIN_REFS   = 3
    STABLE_THRESHOLD        = 0.3
    DEATH_THRESHOLD         = 0.15

    MAX_HYPOTHESES          = 15
    MAX_THEORIES            = 8
    MAX_QUESTIONS           = 6
    MAX_DREAMS              = 8
    MAX_INVESTIGATIONS      = 5
    MAX_EXPERIMENTS         = 5

    # ------------------------------------------------------------------
    # Per-layer output caps.
    #
    # These used to be inline literals. They are named here for one
    # reason: a cap is invisible until you measure the pool it truncates,
    # and you cannot measure a pool you cannot reconfigure. The
    # instrumentation audit (benchmarks/instrumentation_audit.py) varies
    # these to find out whether a layer's retention decision can ever
    # matter, and records the pre-cap pool size for each.
    #
    # Naming them changes no behaviour -- the values are the ones that
    # were there before.
    # ------------------------------------------------------------------
    MAX_LOOPS               = 15
    MAX_PREDICTIONS         = 20
    MAX_ANOMALIES           = 10
    MAX_META_CONCEPTS       = 15
    MAX_PROCESSES           = 10
    MAX_WORKFLOWS           = 10

    # A workflow is only composed when at least this many of its cycle's
    # tags are meta-concept anchors.
    WORKFLOW_MIN_MATCHED_METAS = 2

    # ==================================================================
    # Hypothesis retention (Layer 4)
    # ==================================================================
    # Which candidate beliefs survive into the active hypothesis set --
    # and therefore which beliefs Layer 5 can actually reason over.
    #
    # This used to be a sort by subject name, so a belief survived
    # because its subject happened to sort early. In this project the
    # common subjects (developer, engineer, executed, modified, report,
    # session, suite) are both frequent AND alphabetically early, so the
    # old rule was a popularity rule wearing a name-based disguise.
    #
    # It is now an explicit policy, so the choice can be measured rather
    # than assumed. See research-journal section 19.
    #
    #   "alphabetical"  legacy: sort by (subject, -confidence)
    #   "confidence"    most confident first
    #   "contradiction" most contradicting evidence first (RAW COUNT --
    #                   this ranks by subject popularity, because the raw
    #                   count is the subject's total outgoing flow and so
    #                   grows with how often the subject occurs)
    #   "tension"       most contested first, as a SHARE of the subject's
    #                   total outgoing flow
    #   "salience"      the composite score (default)
    #   "stochastic"    weighted lottery proportional to salience
    HYPOTHESIS_RETENTION = "salience"

    # Every policy name the retention layer accepts. Kept beside the
    # default so that a typo is caught immediately instead of silently
    # falling through to the composite score.
    VALID_RETENTION_POLICIES = (
        "alphabetical",   # legacy: sort by (subject, -confidence)
        "confidence",     # most confident first
        "contradiction",  # most contradicting evidence first (RAW COUNT)
        "tension",        # most contested first, as a SHARE of flow
        "salience",       # the composite score (default)
        "stochastic",     # weighted lottery proportional to salience
    )

    # Weights over the salience components, in the order
    # (tension, curiosity, novelty, revision). Equal by default: no tuned
    # constants, and every component can be ablated on its own.
    SALIENCE_WEIGHTS = (0.25, 0.25, 0.25, 0.25)

    # Multiplier on the contradiction term. 1.0 is the unmodified system.
    # The ablation matrix scales this to ask whether contradiction is
    # developmental fuel or bookkeeping noise.
    CONTRADICTION_SCALE = 1.0

    # Structural markers -- hypotheses whose expectation is
    # "high_structural_significance" -- are never beliefs: Layer 5
    # discards them on sight (see _form_theories_and_questions). They
    # are kept for the record, but they must not consume the belief
    # budget, because a slot they occupy is a slot Layer 5 cannot use.
    MAX_STRUCTURAL_MARKERS = 15

    # Seed for the stochastic retention policy, so a rerun reproduces
    # the same draw.
    RANDOM_SEED = 0

    def __init__(self, memory: MemoryService):
        self.memory = memory
        # Seeded so the stochastic retention policy is reproducible.
        self._rng = random.Random(self.RANDOM_SEED)

    # ==================================================================
    # Public API
    # ==================================================================

    def run(self) -> SleepReport:
        cooc     = self._load_cooccurrences()
        temporal = self._load_temporal()
        freqs    = dict(self.memory.tag_frequencies())
        prior    = self._load_prior_candidates()

        cycle = self._count_prior_cycles(prior) + 1

        # ---- Layer 1: Candidates from graphs ----
        tag_scores   = self._score_tags(freqs, cooc, temporal)
        communities  = self._find_communities(cooc)
        concepts     = self._build_concepts(tag_scores, communities, cooc)
        phrases      = self._build_phrases(tag_scores, cooc)
        loops        = self._build_loops(temporal)
        predictions  = self._build_predictions(temporal, freqs)
        anomalies    = self._build_anomalies(temporal, freqs)

        # ---- Natural Selection: Reinforcement, Decay & Pruning ----
        # Batched: this stores every decayed survivor individually, and one
        # disk sync per candidate dominated the cycle (1,023 commits = 3.0s
        # of a 4.5s cycle when profiled against the live substrate).
        with self.memory.batch():
            strengthened, decayed, pruned = self._natural_selection(
                prior, concepts, phrases, loops, predictions,
            )

        # ---- Layer 2: Composites ----
        stable_prior = [c for c in prior
                        if c.get("type") not in ("_sleep_meta", "anomaly")
                        and (c.get("confidence") or c.get("strength") or 0) >= self.STABLE_THRESHOLD]

        meta_concepts = self._compose_meta_concepts(stable_prior)
        processes     = self._compose_processes(stable_prior)

        # ---- Layer 3: Workflows ----
        workflow_concepts = self._compose_workflows(meta_concepts, processes, stable_prior)

        all_workflows = list(workflow_concepts)
        for c in stable_prior:
            if c.get("type") == "workflow_concept" and c.get("id") not in {w.id for w in all_workflows}:
                all_workflows.append(WorkflowConceptCandidate(
                    id=c.get("id"),
                    generation=c.get("generation", 2),
                    parent_ids=c.get("parent_ids", []),
                    name=c.get("name", ""),
                    components=c.get("components", []),
                    confidence=c.get("confidence", 1.0),
                    evidence=c.get("evidence", {}),
                ))

        all_processes = list(processes)
        for c in stable_prior:
            if c.get("type") == "process_candidate" and c.get("id") not in {p.id for p in all_processes}:
                all_processes.append(ProcessCandidate(
                    id=c.get("id"),
                    generation=c.get("generation", 1),
                    parent_ids=c.get("parent_ids", []),
                    cycle=c.get("cycle", []),
                    strength=c.get("strength", 1.0),
                    evidence=c.get("evidence", {}),
                ))

        all_metas = list(meta_concepts)
        for c in stable_prior:
            if c.get("type") == "meta_concept" and c.get("id") not in {m.id for m in all_metas}:
                all_metas.append(MetaConceptCandidate(
                    id=c.get("id"),
                    generation=c.get("generation", 1),
                    parent_ids=c.get("parent_ids", []),
                    anchor_tag=c.get("anchor_tag", ""),
                    related_candidates=c.get("related_candidates", 0),
                    confidence=c.get("confidence", 1.0),
                    evidence=c.get("evidence", {}),
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

        composites_created = (len(meta_concepts) + len(processes) + len(workflow_concepts) +
                              len(hypotheses) + len(theories) + len(questions) + len(dreams) +
                              len(investigations) + len(experiments))

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
            workflow_concepts=workflow_concepts,
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
        )
        with self.memory.batch():
            self._store_candidates(report)
        return report

    # ==================================================================
    # Layer 6: Categorized Dreams (V5)
    # ==================================================================

    def _generate_categorized_dreams(
        self,
        workflows: list[WorkflowConceptCandidate],
        processes: list[ProcessCandidate],
        meta_concepts: list[MetaConceptCandidate],
        questions: list[QuestionCandidate],
        cooc: dict[str, dict[str, int]],
        temporal: dict[str, dict[str, int]],
    ) -> list[DreamCandidate]:
        """Generate structured dreams across 4 distinct categories:
        1. Completion: transitive closure of observed edges (A->B, B->C => dream A->C).
        2. Analogy: substitute tag with co-occurrence synonym (A->C, A ~ B => dream B->C).
        3. Mutation: structural path extension/variation.
        4. Conditional: search for hidden context tags separating conflicting outcomes in Questions.
        """
        dreams = []
        seen = set()

        # Category 1: Completion Dreams (Transitive Closure)
        # e.g., if failure -> modified and modified -> passed exist, dream failure -> passed
        for p in processes:
            cycle = p.cycle
            if len(cycle) >= 3:
                for i in range(len(cycle)):
                    a = cycle[i]
                    c = cycle[(i + 2) % len(cycle)]
                    # If direct edge does not strongly exist, dream the shortcut
                    if c not in temporal.get(a, {}):
                        did = _make_id("dream_comp", a, c)
                        if did not in seen:
                            seen.add(did)
                            dreams.append(DreamCandidate(
                                id=did,
                                generation=5,
                                dream_category="completion",
                                subject=a,
                                path_or_context=[a, c],
                                confidence=0.08,
                                novelty=0.65,
                                parent_ids=[p.id],
                                evidence={"reason": "transitive_shortcut", "via_process": p.id},
                            ))

        # Category 2: Analogy Dreams (Knowledge Transfer via Co-occurrence Neighbors)
        # e.g., if auth ~ session in co-occurrence, and auth -> failure, dream session -> failure
        for m in meta_concepts[:3]:
            anchor = m.anchor_tag
            neighbors = sorted(cooc.get(anchor, {}).items(), key=lambda x: -x[1])
            for neighbor, count in neighbors[:2]:
                # find what anchor predicts
                for target, edge_cnt in temporal.get(anchor, {}).items():
                    if edge_cnt >= 3 and target not in temporal.get(neighbor, {}):
                        did = _make_id("dream_analogy", neighbor, target)
                        if did not in seen:
                            seen.add(did)
                            dreams.append(DreamCandidate(
                                id=did,
                                generation=5,
                                dream_category="analogy",
                                subject=neighbor,
                                path_or_context=[neighbor, target],
                                confidence=0.05,
                                novelty=0.75,
                                parent_ids=[m.id],
                                evidence={"reason": "analogy_substitution", "analog_source": anchor, "shared_cooc": count},
                            ))

        # Category 3: Mutation Dreams (Structural Path Extension)
        for w in workflows[:2]:
            comps = list(w.components)
            if len(comps) >= 2:
                # Extend path with an anchor tag not currently in the workflow
                for m in meta_concepts:
                    if m.anchor_tag not in comps:
                        mutated = comps + [m.anchor_tag]
                        did = _make_id("dream_mut", w.id, m.anchor_tag)
                        if did not in seen:
                            seen.add(did)
                            dreams.append(DreamCandidate(
                                id=did,
                                generation=5,
                                dream_category="mutation",
                                subject=comps[0],
                                path_or_context=mutated,
                                confidence=0.04,
                                novelty=0.85,
                                parent_ids=[w.id, m.id],
                                evidence={"reason": "path_extension", "extended_tag": m.anchor_tag},
                            ))
                        break

        # Category 4: Conditional Dreams (Resolving Questions)
        # For a high-uncertainty Question, search for an unmodeled co-occurring tag that might be the hidden fork condition
        for q in questions[:3]:
            sub = q.subject
            # Candidate contexts: tags co-occurring with subject
            candidate_contexts = [t for t, _ in sorted(cooc.get(sub, {}).items(), key=lambda x: -x[1])
                                  if t not in q.competing_expectations]
            for ctx in candidate_contexts[:2]:
                did = _make_id("dream_cond", sub, ctx)
                if did not in seen:
                    seen.add(did)
                    dreams.append(DreamCandidate(
                        id=did,
                        generation=5,
                        dream_category="conditional",
                        subject=sub,
                        path_or_context=[ctx, sub] + q.competing_expectations,
                        confidence=0.06,
                        novelty=0.90,
                        parent_ids=[q.id],
                        evidence={"reason": "hidden_fork_context", "context_tag": ctx, "question_id": q.id},
                    ))

        dreams.sort(key=lambda d: d.novelty, reverse=True)
        return dreams[:self.MAX_DREAMS]

    # ==================================================================
    # Layer 7: Investigation Ranking / Attention Economy (V5)
    # ==================================================================

    def _rank_investigations(
        self,
        questions: list[QuestionCandidate],
        dreams: list[DreamCandidate],
    ) -> list[InvestigationCandidate]:
        """Rank investigations based on Expected Information Gain (EIG).
        
        Currency of Epistemic Choice:
          EIG = Uncertainty * (1.0 + Novelty)
        High EIG targets promise maximum knowledge reorganization or conflict elimination.
        """
        investigations = []

        # 1. Evaluate Questions
        for q in questions:
            # Questions have high uncertainty; novelty is moderate
            novelty = 0.50
            eig = round(q.uncertainty * (1.0 + novelty), 4)
            iid = _make_id("inv", q.id)
            investigations.append(InvestigationCandidate(
                id=iid,
                generation=6,
                target_id=q.id,
                target_type="question",
                subject=q.subject,
                novelty=novelty,
                uncertainty=q.uncertainty,
                expected_information_gain=eig,
                parent_ids=[q.id],
                evidence={
                    "formula": "uncertainty * (1.0 + novelty)",
                    "competing_outcomes": q.competing_expectations,
                },
            ))

        # 2. Evaluate Dreams
        for d in dreams:
            # Dreams have high novelty; their uncertainty reflects how far they are from established reality
            # Distance from certainty: (1.0 - confidence)
            uncertainty = round(1.0 - d.confidence, 4)
            # High-novelty dreams (conditional, analogy) yield high EIG
            eig = round(uncertainty * d.novelty, 4)
            iid = _make_id("inv", d.id)
            investigations.append(InvestigationCandidate(
                id=iid,
                generation=6,
                target_id=d.id,
                target_type="dream",
                subject=d.subject,
                novelty=d.novelty,
                uncertainty=uncertainty,
                expected_information_gain=eig,
                parent_ids=[d.id],
                evidence={
                    "formula": "uncertainty * novelty",
                    "dream_category": d.dream_category,
                    "path_or_context": d.path_or_context,
                },
            ))

        # Rank by Expected Information Gain
        investigations.sort(key=lambda inv: inv.expected_information_gain, reverse=True)
        return investigations[:self.MAX_INVESTIGATIONS]

    # ==================================================================
    # Layer 8: Active Experiment Selection (Sleep V6 / Path B)
    # ==================================================================

    def _select_experiments(
        self,
        investigations: list[InvestigationCandidate],
        questions: list[QuestionCandidate],
        dreams: list[DreamCandidate],
    ) -> list[ExperimentCandidate]:
        """Convert top investigations into concrete, executable experiment interventions."""
        questions_by_id = {q.id: q for q in questions}
        dreams_by_id = {d.id: d for d in dreams}
        experiments = []

        for inv in investigations:
            # Determine probe action, cost, and payload based on target type
            if inv.target_type == "question":
                q = questions_by_id.get(inv.target_id)
                if not q:
                    continue
                # For Questions: Probe involves testing discriminating contexts for competing expectations
                action_type = "discriminating_probe"
                payload = {
                    "subject": q.subject,
                    "target_question_id": q.id,
                    "competing_outcomes": q.competing_expectations,
                    "test_vector": f"probe:{q.subject} -> ? ({' vs '.join(q.competing_expectations)})",
                }
                expected_outcomes = q.competing_expectations
                cost = 1.0  # Normalized base probe cost
            elif inv.target_type == "dream":
                d = dreams_by_id.get(inv.target_id)
                if not d:
                    continue
                # For Dreams: Probe verifies if counterfactual pathway can be provoked or validated
                action_type = f"verify_{d.dream_category}_dream"
                payload = {
                    "subject": d.subject,
                    "target_dream_id": d.id,
                    "dream_category": d.dream_category,
                    "path_or_context": d.path_or_context,
                    "test_vector": f"probe_path:{' -> '.join(d.path_or_context)}",
                }
                expected_outcomes = ["validated", "refuted"]
                # Mutation and conditional dreams are higher novelty / slightly higher cost to simulate
                cost = 1.2 if d.dream_category in ("mutation", "conditional") else 0.8
            else:
                continue

            # Priority = EIG / Cost
            priority = round(inv.expected_information_gain / max(0.1, cost), 4)
            eid = _make_id("exp", inv.id, action_type)

            experiments.append(ExperimentCandidate(
                id=eid,
                generation=7,
                investigation_id=inv.id,
                target_id=inv.target_id,
                target_type=inv.target_type,
                action_type=action_type,
                probe_payload=payload,
                expected_outcomes=expected_outcomes,
                cost=cost,
                priority=priority,
                status="proposed",
                parent_ids=[inv.id],
                evidence={
                    "investigation_eig": inv.expected_information_gain,
                    "cost": cost,
                    "formula": "EIG / cost",
                },
            ))

        experiments.sort(key=lambda exp: exp.priority, reverse=True)
        return experiments[:self.MAX_EXPERIMENTS]

    # ==================================================================
    # Lineage Ancestry Traversal (Genealogy query)
    # ==================================================================

    def get_ancestry(self, candidate_id: str, max_depth: int = 7) -> dict:
        priors = self._load_prior_candidates()
        by_id = {c["id"]: c for c in priors if "id" in c}

        def build_tree(cid: str, current_depth: int) -> dict:
            if cid not in by_id or current_depth >= max_depth:
                return {"id": cid, "found": cid in by_id}
            node = by_id[cid]
            tree = {
                "id": cid,
                "type": node.get("type"),
                "generation": node.get("generation", 1),
                "confidence": node.get("confidence", node.get("strength")),
                "parents": [build_tree(pid, current_depth + 1) for pid in node.get("parent_ids", [])]
            }
            return tree

        return build_tree(candidate_id, 0)

    # ==================================================================
    # Graph loading
    # ==================================================================

    def _load_cooccurrences(self) -> dict[str, dict[str, int]]:
        graph: dict[str, dict[str, int]] = defaultdict(dict)
        for a, b, count in self.memory.cooccurrences(min_count=1):
            graph[a][b] = count
            graph[b][a] = count
        return graph

    def _load_temporal(self) -> dict[str, dict[str, int]]:
        graph: dict[str, dict[str, int]] = defaultdict(dict)
        for tag_from, tag_to, count in self.memory.temporal_edges(min_count=1):
            graph[tag_from][tag_to] = count
        return graph

    def _load_prior_candidates(self) -> list[dict]:
        events = self.memory.recent(n=4000, event_type="sleep")
        candidates = []
        for e in events:
            if e.source.startswith("sleep:") and e.source != "sleep:meta":
                try:
                    candidates.append(json.loads(e.content))
                except (json.JSONDecodeError, ValueError):
                    pass
        return candidates

    def _count_prior_cycles(self, prior: list[dict]) -> int:
        """Return the highest sleep-cycle number recorded so far.

        The counter is kept in its own `sleep_cycles` table. It used to be
        recovered by scanning the most recent 500 sleep events for a
        `_sleep_meta` marker, which silently returned 0 once the candidate
        population exceeded 500 rows per cycle -- resetting the cycle
        counter to 1 in the middle of a run and corrupting the time axis of
        every longitudinal measurement derived from it.
        """
        return self.memory.latest_sleep_cycle()

    # ==================================================================
    # Tag scoring (internal)
    # ==================================================================

    def _score_tags(self, freqs, cooc, temporal) -> list[_TagScore]:
        scores = []
        all_tags = set(freqs) | set(cooc) | set(temporal)
        for tag in all_tags:
            freq      = freqs.get(tag, 0)
            neighbors = set(cooc.get(tag, {}).keys())
            degree    = len(neighbors)
            clustering = self._clustering_coefficient(tag, neighbors, cooc)
            p_reach   = self._predictive_reach(tag, neighbors, temporal)
            score = _TagScore(
                tag=tag, frequency=freq, degree=degree,
                clustering=clustering, predictive_reach=p_reach,
            )
            score.classification = self._classify(score)
            scores.append(score)
        scores.sort(key=lambda s: s.frequency, reverse=True)
        return scores

    def _clustering_coefficient(self, tag, neighbors, cooc) -> float:
        k = len(neighbors)
        if k < 2:
            return 0.0
        possible = k * (k - 1) / 2
        actual = 0
        neighbor_list = list(neighbors)
        for i in range(len(neighbor_list)):
            for j in range(i + 1, len(neighbor_list)):
                if neighbor_list[j] in cooc.get(neighbor_list[i], {}):
                    actual += 1
        return actual / possible

    def _predictive_reach(self, tag, cooc_neighbors, temporal) -> int:
        temporal_targets = set(temporal.get(tag, {}).keys())
        outside = temporal_targets - cooc_neighbors - {tag}
        return len(outside)

    def _classify(self, s: _TagScore) -> str:
        if s.frequency <= 1 and s.degree <= 1:
            return "noise"
        if s.clustering >= self.PHRASE_MIN_CLUSTERING and s.predictive_reach <= self.PHRASE_MAX_REACH:
            return "phrase_fragment"
        if (s.degree >= self.CONCEPT_MIN_DEGREE
                and s.clustering <= self.CONCEPT_MAX_CLUSTERING
                and s.predictive_reach >= self.CONCEPT_MIN_REACH):
            return "concept"
        if s.degree >= 5:
            return "hub"
        return "unclassified"

    # ==================================================================
    # Layer 1 Candidate Builders
    # ==================================================================

    def _build_concepts(self, tag_scores, communities, cooc) -> list[ConceptCandidate]:
        concept_tags = {s.tag: s for s in tag_scores if s.classification == "concept"}
        if not concept_tags:
            return []

        tag_to_community: dict[str, int] = {}
        for cid, members, density in communities:
            for t in members:
                tag_to_community[t] = cid

        by_community: dict[int, list[_TagScore]] = defaultdict(list)
        orphans: list[_TagScore] = []
        for tag, score in concept_tags.items():
            cid = tag_to_community.get(tag)
            if cid is not None:
                by_community[cid].append(score)
            else:
                orphans.append(score)

        candidates = []

        for cid, scores in by_community.items():
            members = sorted([s.tag for s in scores])
            edge_count = 0
            for i, m1 in enumerate(members):
                for m2 in members[i+1:]:
                    edge_count += cooc.get(m1, {}).get(m2, 0)

            avg_clust = sum(s.clustering for s in scores) / len(scores)
            avg_reach = sum(s.predictive_reach for s in scores) / len(scores)
            avg_degree = sum(s.degree for s in scores) / len(scores)
            total_obs = sum(s.frequency for s in scores)

            cid_str = _make_id("concept", *members)
            candidates.append(ConceptCandidate(
                id=cid_str,
                members=members,
                confidence=min(1.0, (avg_reach / 8) * (1 - avg_clust)),
                evidence={
                    "community_id": cid,
                    "edge_count": edge_count,
                    "observations": total_obs,
                    "avg_clustering": round(avg_clust, 3),
                    "avg_predictive_reach": round(avg_reach, 1),
                    "avg_degree": round(avg_degree, 1),
                },
            ))

        for score in orphans:
            cid_str = _make_id("concept", score.tag)
            candidates.append(ConceptCandidate(
                id=cid_str,
                members=[score.tag],
                confidence=min(1.0, (score.predictive_reach / 8) * (1 - score.clustering)),
                evidence={
                    "edge_count": sum(cooc.get(score.tag, {}).values()),
                    "observations": score.frequency,
                    "avg_clustering": round(score.clustering, 3),
                    "avg_predictive_reach": score.predictive_reach,
                    "avg_degree": score.degree,
                },
            ))

        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates

    def _build_phrases(self, tag_scores, cooc) -> list[PhraseCandidate]:
        fragments = [s for s in tag_scores if s.classification == "phrase_fragment"]
        if not fragments:
            return []

        frag_set = {s.tag for s in fragments}
        visited: set[str] = set()
        groups: list[list[_TagScore]] = []
        score_map = {s.tag: s for s in fragments}

        for s in fragments:
            if s.tag in visited:
                continue
            group = []
            queue = [s.tag]
            while queue:
                t = queue.pop()
                if t in visited or t not in frag_set:
                    continue
                visited.add(t)
                group.append(score_map[t])
                for neighbor in cooc.get(t, {}):
                    if neighbor in frag_set and neighbor not in visited:
                        queue.append(neighbor)
            if group:
                groups.append(group)

        candidates = []
        for group in groups:
            members = sorted([s.tag for s in group])
            edge_count = 0
            for i, m1 in enumerate(members):
                for m2 in members[i+1:]:
                    edge_count += cooc.get(m1, {}).get(m2, 0)

            avg_clust = sum(s.clustering for s in group) / len(group)
            avg_reach = sum(s.predictive_reach for s in group) / len(group)

            pid = _make_id("phrase", *members)
            candidates.append(PhraseCandidate(
                id=pid,
                members=members,
                confidence=min(1.0, avg_clust),
                evidence={
                    "avg_clustering": round(avg_clust, 3),
                    "avg_predictive_reach": round(avg_reach, 1),
                    "edge_count": edge_count,
                },
            ))

        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates

    def _build_loops(self, temporal) -> list[LoopCandidate]:
        loops = []
        seen: set[tuple] = set()
        tags = list(temporal.keys())

        # 2-cycles
        for a in tags:
            for b, count_ab in temporal[a].items():
                if b <= a:
                    continue
                count_ba = temporal.get(b, {}).get(a, 0)
                strength = min(count_ab, count_ba)
                if strength >= self.LOOP_MIN_STRENGTH:
                    pair = tuple(sorted([a, b]))
                    if pair not in seen:
                        seen.add(pair)
                        lid = _make_id("loop", a, b)
                        loops.append(LoopCandidate(
                            id=lid,
                            path=[a, b, a],
                            strength=strength,
                            evidence={
                                "min_edge_count": strength,
                                "edge_counts": [count_ab, count_ba],
                                "cycle_length": 2,
                            },
                        ))

        # 3-cycles
        for a in tags:
            for b in temporal.get(a, {}):
                if b == a:
                    continue
                for c in temporal.get(b, {}):
                    if c == a or c == b:
                        continue
                    count_ca = temporal.get(c, {}).get(a, 0)
                    if count_ca >= self.LOOP_MIN_STRENGTH:
                        counts = [
                            temporal[a].get(b, 0),
                            temporal[b].get(c, 0),
                            count_ca,
                        ]
                        strength = min(counts)
                        if strength >= self.LOOP_MIN_STRENGTH:
                            cycle = tuple(sorted([a, b, c]))
                            if cycle not in seen:
                                seen.add(cycle)
                                lid = _make_id("loop", a, b, c)
                                loops.append(LoopCandidate(
                                    id=lid,
                                    path=[a, b, c, a],
                                    strength=strength,
                                    evidence={
                                        "min_edge_count": strength,
                                        "edge_counts": counts,
                                        "cycle_length": 3,
                                    },
                                ))

        loops.sort(key=lambda l: l.strength, reverse=True)
        return loops[:self.MAX_LOOPS]

    def _build_predictions(self, temporal, freqs) -> list[PredictionCandidate]:
        candidates = []
        for tag_from, targets in temporal.items():
            source_freq = freqs.get(tag_from, 1)
            for tag_to, count in targets.items():
                if count >= self.PREDICTION_MIN_COUNT:
                    ratio = count / max(source_freq, 1)
                    pid = _make_id("pred", tag_from, tag_to)
                    candidates.append(PredictionCandidate(
                        id=pid,
                        source=tag_from,
                        target=tag_to,
                        strength=min(1.0, ratio),
                        evidence={
                            "temporal_count": count,
                            "source_frequency": source_freq,
                            "target_frequency": freqs.get(tag_to, 0),
                            "ratio": round(ratio, 3),
                        },
                    ))
        candidates.sort(key=lambda p: p.evidence["temporal_count"], reverse=True)
        return candidates[:self.MAX_PREDICTIONS]

    def _build_anomalies(self, temporal, freqs) -> list[AnomalyCandidate]:
        anomalies = []
        for tag_from, targets in temporal.items():
            if not targets:
                continue
            sorted_targets = sorted(targets.items(), key=lambda x: -x[1])
            if len(sorted_targets) < 2:
                continue
            top_tag, top_count = sorted_targets[0]
            for other_tag, other_count in sorted_targets[1:]:
                if top_count >= 3 * other_count and other_count >= 2:
                    aid = _make_id("anomaly", tag_from, top_tag, other_tag)
                    anomalies.append(AnomalyCandidate(
                        id=aid,
                        expected=top_tag,
                        observed=other_tag,
                        context=tag_from,
                        evidence={
                            "expected_count": top_count,
                            "observed_count": other_count,
                            "dominance_ratio": round(top_count / max(other_count, 1), 2),
                        },
                    ))
        anomalies.sort(key=lambda a: a.evidence["dominance_ratio"], reverse=True)
        return anomalies[:self.MAX_ANOMALIES]

    # ==================================================================
    # Layer 2: Structural Composition (V1)
    # ==================================================================

    def _compose_meta_concepts(self, stable_prior: list[dict]) -> list[MetaConceptCandidate]:
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

            for tag in tags:
                tag_refs[tag].append((cid, ctype))

        candidates = []
        for tag, refs in tag_refs.items():
            distinct_types = set(ctype for _, ctype in refs)
            distinct_ids = list(set(cid for cid, _ in refs))

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
        return candidates[:self.MAX_META_CONCEPTS]

    def _compose_processes(self, stable_prior: list[dict]) -> list[ProcessCandidate]:
        preds: dict[str, dict[str, dict]] = {}
        for c in stable_prior:
            if c.get("type") != "prediction_candidate":
                continue
            src = c.get("source", "")
            tgt = c.get("target", "")
            if src and tgt:
                if src not in preds:
                    preds[src] = {}
                existing = preds[src].get(tgt)
                c_strength = c.get("strength", 0)
                if not existing or c_strength > existing.get("strength", 0):
                    preds[src][tgt] = c

        if not preds:
            return []

        candidates = []
        seen_cycles: set[tuple] = set()
        sources = list(preds.keys())

        # 2-cycles
        for a in sources:
            for b in preds.get(a, {}):
                if b <= a:
                    continue
                if a in preds.get(b, {}):
                    cycle_key = tuple(sorted([a, b]))
                    if cycle_key not in seen_cycles:
                        seen_cycles.add(cycle_key)
                        pred_ab = preds[a][b]
                        pred_ba = preds[b][a]
                        strength = min(pred_ab.get("strength", 0), pred_ba.get("strength", 0))
                        parent_ids = [pred_ab.get("id", ""), pred_ba.get("id", "")]
                        parent_ids = [p for p in parent_ids if p]

                        pid = _make_id("process", a, b)
                        candidates.append(ProcessCandidate(
                            id=pid,
                            generation=1,
                            parent_ids=parent_ids,
                            cycle=[a, b],
                            strength=round(strength, 4),
                            evidence={
                                "cycle_length": 2,
                                "prediction_strengths": [
                                    round(pred_ab.get("strength", 0), 4),
                                    round(pred_ba.get("strength", 0), 4),
                                ],
                                "min_strength": round(strength, 4),
                            },
                        ))

        # 3-cycles
        for a in sources:
            for b in preds.get(a, {}):
                if b == a:
                    continue
                for c in preds.get(b, {}):
                    if c == a or c == b:
                        continue
                    if a in preds.get(c, {}):
                        cycle_key = tuple(sorted([a, b, c]))
                        if cycle_key not in seen_cycles:
                            seen_cycles.add(cycle_key)
                            pred_ab = preds[a][b]
                            pred_bc = preds[b][c]
                            pred_ca = preds[c][a]
                            strength = min(
                                pred_ab.get("strength", 0),
                                pred_bc.get("strength", 0),
                                pred_ca.get("strength", 0),
                            )
                            parent_ids = [
                                pred_ab.get("id", ""),
                                pred_bc.get("id", ""),
                                pred_ca.get("id", ""),
                            ]
                            parent_ids = [p for p in parent_ids if p]

                            pid = _make_id("process", a, b, c)
                            candidates.append(ProcessCandidate(
                                id=pid,
                                generation=1,
                                parent_ids=parent_ids,
                                cycle=[a, b, c],
                                strength=round(strength, 4),
                                evidence={
                                    "cycle_length": 3,
                                    "prediction_strengths": [
                                        round(pred_ab.get("strength", 0), 4),
                                        round(pred_bc.get("strength", 0), 4),
                                        round(pred_ca.get("strength", 0), 4),
                                    ],
                                    "min_strength": round(strength, 4),
                                },
                            ))

        candidates.sort(key=lambda p: p.strength, reverse=True)
        return candidates[:self.MAX_PROCESSES]

    # ==================================================================
    # Layer 3: High-Order Synthesis (Sleep V2)
    # ==================================================================

    def _compose_workflows(
        self,
        meta_concepts: list[MetaConceptCandidate],
        processes: list[ProcessCandidate],
        stable_prior: list[dict],
    ) -> list[WorkflowConceptCandidate]:
        if not processes or not meta_concepts:
            return []

        meta_by_anchor = {m.anchor_tag: m for m in meta_concepts}
        workflows = []

        for proc in processes:
            matched_metas = [meta_by_anchor[t] for t in proc.cycle if t in meta_by_anchor]

            if len(matched_metas) >= self.WORKFLOW_MIN_MATCHED_METAS:
                parent_ids = [proc.id] + [m.id for m in matched_metas]
                cycle_str = "_".join(proc.cycle)
                name = f"workflow_{cycle_str}"
                wid = _make_id("workflow", *sorted(proc.cycle))

                avg_conf = (proc.strength + sum(m.confidence for m in matched_metas)) / (1 + len(matched_metas))

                workflows.append(WorkflowConceptCandidate(
                    id=wid,
                    generation=2,
                    parent_ids=parent_ids,
                    name=name,
                    components=sorted(proc.cycle),
                    confidence=round(min(1.0, avg_conf), 4),
                    evidence={
                        "process_id": proc.id,
                        "process_strength": proc.strength,
                        "meta_concept_anchors": [m.anchor_tag for m in matched_metas],
                        "ancestor_count": len(parent_ids),
                    },
                ))

        workflows.sort(key=lambda w: w.confidence, reverse=True)
        return workflows[:self.MAX_WORKFLOWS]

    # ==================================================================
    # Layer 4: Falsifiable Hypotheses (Sleep V3)
    # ==================================================================

    def _form_and_test_hypotheses(
        self,
        temporal: dict[str, dict[str, int]],
        freqs: dict[str, int],
        workflows: list[WorkflowConceptCandidate],
        processes: list[ProcessCandidate],
        meta_concepts: list[MetaConceptCandidate],
        prior: list[dict],
    ) -> list[HypothesisCandidate]:
        prior_hyps = {h.get("id"): h for h in prior if h.get("type") == "hypothesis"}
        candidates: dict[str, HypothesisCandidate] = {}

        for w in workflows:
            comps = w.components
            for i in range(len(comps)):
                sub = comps[i]
                for j in range(len(comps)):
                    if i != j:
                        exp = comps[j]
                        hid = _make_id("hyp", sub, exp)
                        if hid not in candidates:
                            candidates[hid] = HypothesisCandidate(
                                id=hid,
                                generation=3,
                                subject=sub,
                                expectation=exp,
                                parent_ids=[w.id],
                            )
                        else:
                            if w.id not in candidates[hid].parent_ids:
                                candidates[hid].parent_ids.append(w.id)

        for p in processes:
            cycle = p.cycle
            for i in range(len(cycle)):
                sub = cycle[i]
                exp = cycle[(i + 1) % len(cycle)]
                hid = _make_id("hyp", sub, exp)
                if hid not in candidates:
                    candidates[hid] = HypothesisCandidate(
                        id=hid,
                        generation=3,
                        subject=sub,
                        expectation=exp,
                        parent_ids=[p.id],
                    )
                else:
                    if p.id not in candidates[hid].parent_ids:
                        candidates[hid].parent_ids.append(p.id)

        for m in meta_concepts:
            if m.related_candidates >= 5:
                hid = _make_id("hyp", m.anchor_tag, "high_structural_significance")
                candidates[hid] = HypothesisCandidate(
                    id=hid,
                    generation=3,
                    subject=m.anchor_tag,
                    expectation="high_structural_significance",
                    confidence=m.confidence,
                    support_count=m.related_candidates,
                    contradiction_count=0,
                    parent_ids=[m.id],
                    evidence={"type": "meta_centrality", "related_candidates": m.related_candidates},
                )

        results = []
        for hid, hyp in candidates.items():
            if hyp.expectation == "high_structural_significance":
                results.append(hyp)
                continue

            sub = hyp.subject
            exp = hyp.expectation

            targets = temporal.get(sub, {})
            support = targets.get(exp, 0)
            total_flow = sum(targets.values())
            raw_contradiction = max(0, total_flow - support)
            # The contradiction scale is 1.0 in the unmodified system. The
            # ablation matrix moves it to ask whether contradiction acts as
            # developmental fuel or as bookkeeping noise. The RAW value is
            # kept alongside the scaled one so that a metric can still
            # measure the world rather than the axis.
            contradiction = raw_contradiction * self.CONTRADICTION_SCALE

            prior_h = prior_hyps.get(hid)
            prior_conf = prior_h.get("confidence") if prior_h else None

            if (support + contradiction) > 0:
                conf = round(support / (support + contradiction), 4)
            else:
                conf = 0.0

            if conf < self.DEATH_THRESHOLD and (support + contradiction) >= 3:
                continue

            hyp.confidence = conf
            hyp.support_count = support
            hyp.contradiction_count = contradiction
            hyp.evidence = {
                "support_count": support,
                "contradiction_count": contradiction,
                "raw_contradiction_count": raw_contradiction,
                "total_flow": total_flow,
                "prior_confidence": prior_conf,
                "revision_delta": round(conf - prior_conf, 4) if prior_conf is not None else 0.0,
            }
            results.append(hyp)

        # ---- retention -------------------------------------------------
        # Structural markers are not beliefs -- Layer 5 discards them -- so
        # they are kept in their own allowance and cannot consume the
        # belief budget. The remaining budget goes to real beliefs, ranked
        # by the configured policy.
        markers = [h for h in results
                   if h.expectation == "high_structural_significance"]
        beliefs = [h for h in results
                   if h.expectation != "high_structural_significance"]

        info = self._belief_info(beliefs, prior_hyps, temporal)
        kept = self._retain_hypotheses(beliefs, info, temporal)
        kept_markers = self._retain_markers(markers, info)
        return kept + kept_markers

    # ==================================================================
    # Hypothesis retention
    # ==================================================================

    def _belief_info(self, beliefs, prior_hyps, temporal) -> dict:
        """Per-candidate quantities the retention policy needs.

        These are computed from the UNSCALED contradiction, so a metric
        built on them still measures the world when CONTRADICTION_SCALE
        is not 1.0.
        """
        info = {}
        for h in beliefs:
            raw = h.evidence.get("raw_contradiction_count",
                                 h.contradiction_count)
            total = h.support_count + raw
            tension = (raw / total) if total > 0 else 0.0
            prior_h = prior_hyps.get(h.id)
            prior_conf = prior_h.get("confidence") if prior_h else None
            revision = abs(h.confidence - prior_conf) if prior_conf is not None else 0.0
            info[h.id] = {
                "support": h.support_count,
                "raw_contradiction": raw,
                "tension": tension,
                "novelty": 0.0 if prior_h else 1.0,
                "revision": revision,
            }
        return info

    def _subject_entropy(self, subject: str, temporal) -> float:
        """Normalised Shannon entropy of a subject's outgoing flow.

        How undetermined the subject is: 0 when all of the subject's
        outgoing evidence points one way, 1 when it is spread evenly.
        This is the "curiosity" component of salience -- the same idea as
        the uncertainty Layer 5 computes, but available one layer earlier,
        where retention has to be decided.
        """
        counts = [c for c in temporal.get(subject, {}).values() if c > 0]
        if len(counts) < 2:
            return 0.0
        total = sum(counts)
        h = 0.0
        for c in counts:
            q = c / total
            h -= q * math.log2(q)
        return h / math.log2(len(counts))

    def _salience(self, beliefs, info, temporal) -> dict:
        """The composite salience score, one value per belief.

        Every component is unit-free and in [0, 1], so the weights are
        meaningful and no component can swamp the others:

          tension   how contested this expectation is, as a share of the
                    subject's outgoing flow. NOTE: the raw contradiction
                    COUNT is not contestation -- it is the subject's
                    popularity -- so the share is used here.
          curiosity how undetermined the subject is (normalised entropy).
          novelty   1 if this belief has never been held before.
          revision  how much this belief's confidence just moved.
        """
        w_tension, w_curiosity, w_novelty, w_revision = self.SALIENCE_WEIGHTS
        scores = {}
        for h in beliefs:
            i = info[h.id]
            scores[h.id] = (
                w_tension * i["tension"]
                + w_curiosity * self._subject_entropy(h.subject, temporal)
                + w_novelty * i["novelty"]
                + w_revision * i["revision"]
            )
        return scores

    def _retain_markers(self, markers, info) -> list:
        """Keep the inert structural markers, out of the belief budget.

        They are recorded for provenance but they are never beliefs, so
        they get their own allowance rather than competing for the slots
        Layer 5 actually reads.
        """
        markers = sorted(markers, key=lambda h: (-h.confidence, h.subject))
        return markers[:self.MAX_STRUCTURAL_MARKERS]

    def _retain_hypotheses(self, beliefs, info, temporal) -> list:
        """Apply the retention policy to the candidate beliefs."""
        policy = self.HYPOTHESIS_RETENTION
        # Validate before doing any work, so a typo in the policy name is
        # always a loud error rather than something that depends on
        # whether the pool happened to be empty.
        if policy not in self.VALID_RETENTION_POLICIES:
            raise ValueError(f"unknown HYPOTHESIS_RETENTION policy: {policy!r}")

        if not beliefs:
            return []

        if policy == "alphabetical":
            ranked = sorted(beliefs, key=lambda h: (h.subject, -h.confidence))
            return ranked[:self.MAX_HYPOTHESES]
        if policy == "confidence":
            ranked = sorted(beliefs, key=lambda h: (-h.confidence, h.subject))
            return ranked[:self.MAX_HYPOTHESES]
        if policy == "contradiction":
            ranked = sorted(beliefs, key=lambda h: (-h.contradiction_count, h.subject))
            return ranked[:self.MAX_HYPOTHESES]
        if policy == "tension":
            ranked = sorted(beliefs, key=lambda h: (-info[h.id]["tension"], h.subject))
            return ranked[:self.MAX_HYPOTHESES]

        scores = self._salience(beliefs, info, temporal)

        if policy == "salience":
            ranked = sorted(beliefs, key=lambda h: (-scores[h.id], h.subject))
            return ranked[:self.MAX_HYPOTHESES]
        if policy == "stochastic":
            return self._stochastic_retain(beliefs, scores)

        raise ValueError(f"unknown HYPOTHESIS_RETENTION policy: {policy!r}")

    def _stochastic_retain(self, beliefs, scores) -> list:
        """A weighted lottery: draw without replacement, proportional to salience."""
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
                generation=4,
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
                questions.append(QuestionCandidate(
                    id=qid,
                    generation=4,
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

    # ==================================================================
    # Natural Selection: Reinforcement, Decay & Pruning
    # ==================================================================

    def _natural_selection(
        self, prior, concepts, phrases, loops, predictions,
    ) -> tuple[int, int, int]:
        strengthened = 0
        decayed = 0
        pruned = 0

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
            prior_gen  = prior_c.get("generation", 1)
            prior_obs  = prior_c.get("evidence", {}).get("observations", 0)

            if key in current_keys:
                strengthened += 1
                self._reinforce_current(
                    key, prior_conf, prior_gen, prior_obs,
                    concepts, phrases, loops, predictions,
                )
            else:
                new_conf = prior_conf * 0.8
                if new_conf < self.DEATH_THRESHOLD:
                    pruned += 1
                else:
                    decayed += 1
                    decayed_candidate = dict(prior_c)
                    if "confidence" in decayed_candidate:
                        decayed_candidate["confidence"] = round(new_conf, 4)
                    if "strength" in decayed_candidate:
                        decayed_candidate["strength"] = round(new_conf, 4)
                    decayed_candidate["generation"] = prior_gen + 1
                    evidence = dict(decayed_candidate.get("evidence", {}))
                    evidence["decayed_from"] = round(prior_conf, 4)
                    evidence["decay_cycle"] = True
                    decayed_candidate["evidence"] = evidence
                    self._store_single_candidate(decayed_candidate)

        return strengthened, decayed, pruned

    def _candidate_key(self, c: dict) -> str:
        ctype = c.get("type", "")
        if ctype == "concept_candidate":
            members = c.get("members", [])
            return f"concept:{'|'.join(sorted(members))}" if members else ""
        if ctype == "phrase_candidate":
            members = c.get("members", [])
            return f"phrase:{'|'.join(sorted(members))}" if members else ""
        if ctype == "loop_candidate":
            path = c.get("path", [])
            return f"loop:{'|'.join(path)}" if path else ""
        if ctype == "prediction_candidate":
            return f"prediction:{c.get('source', '')}|{c.get('target', '')}"
        return ""

    def _reinforce_current(
        self, key, prior_conf, prior_gen, prior_obs,
        concepts, phrases, loops, predictions,
    ):
        boost = 0.05
        if key.startswith("concept:"):
            members_key = set(key.split(":", 1)[1].split("|"))
            for c in concepts:
                if set(c.members) == members_key:
                    c.confidence = min(1.0, c.confidence + boost)
                    c.generation = prior_gen + 1
                    c.evidence["prior_confidence"] = round(prior_conf, 4)
                    c.evidence["prior_observations"] = prior_obs
                    c.evidence["strengthened"] = True
                    break

        elif key.startswith("phrase:"):
            members_key = set(key.split(":", 1)[1].split("|"))
            for p in phrases:
                if set(p.members) == members_key:
                    p.confidence = min(1.0, p.confidence + boost)
                    p.generation = prior_gen + 1
                    p.evidence["prior_confidence"] = round(prior_conf, 4)
                    p.evidence["strengthened"] = True
                    break

        elif key.startswith("loop:"):
            path_key = key.split(":", 1)[1].split("|")
            for l in loops:
                if l.path == path_key:
                    l.strength = min(1.0, l.strength + boost)
                    l.generation = prior_gen + 1
                    l.evidence["prior_strength"] = round(prior_conf, 4)
                    l.evidence["strengthened"] = True
                    break

        elif key.startswith("prediction:"):
            parts = key.split(":", 1)[1].split("|")
            if len(parts) == 2:
                src, tgt = parts
                for p in predictions:
                    if p.source == src and p.target == tgt:
                        p.strength = min(1.0, p.strength + boost)
                        p.generation = prior_gen + 1
                        p.evidence["prior_strength"] = round(prior_conf, 4)
                        p.evidence["strengthened"] = True
                        break

    # ==================================================================
    # Community detection (internal helper)
    # ==================================================================

    def _find_communities(self, cooc) -> list[tuple[int, list[str], float]]:
        filtered: dict[str, set[str]] = defaultdict(set)
        for tag, neighbors in cooc.items():
            for neighbor, count in neighbors.items():
                if count >= self.COOC_MIN_EDGE:
                    filtered[tag].add(neighbor)
                    filtered[neighbor].add(tag)

        visited: set[str] = set()
        components: list[set[str]] = []
        for start in filtered:
            if start in visited:
                continue
            component: set[str] = set()
            queue = [start]
            while queue:
                node = queue.pop()
                if node in visited:
                    continue
                visited.add(node)
                component.add(node)
                queue.extend(filtered[node] - visited)
            if len(component) >= 2:
                components.append(component)

        results = []
        for i, component in enumerate(components):
            tags = sorted(component)
            k = len(tags)
            possible = k * (k - 1) / 2
            actual = 0
            for x in range(len(tags)):
                for y in range(x + 1, len(tags)):
                    if tags[y] in cooc.get(tags[x], {}):
                        actual += 1
            density = actual / possible if possible > 0 else 0.0
            results.append((i, tags, density))

        results.sort(key=lambda c: c[2], reverse=True)
        return results

    # ==================================================================
    # Persistence
    # ==================================================================

    def _store_candidates(self, report: SleepReport):
        self.memory.store(
            json.dumps({"type": "_sleep_meta", "cycle": report.cycle,
                        "ran_at": report.ran_at,
                        "composites_created": report.composites_created}),
            event_type="sleep", source="sleep:meta",
        )
        # Record the cycle number in the authoritative monotonic counter.
        self.memory.record_sleep_cycle(report.cycle, report.ran_at)

        for c in report.concepts:
            self._store_single_candidate(asdict(c))
        for p in report.phrases:
            self._store_single_candidate(asdict(p))
        for l in report.loops:
            self._store_single_candidate(asdict(l))
        for p in report.predictions:
            self._store_single_candidate(asdict(p))
        for a in report.anomalies:
            self._store_single_candidate(asdict(a))
        # Layer 2
        for m in report.meta_concepts:
            self._store_single_candidate(asdict(m))
        for p in report.processes:
            self._store_single_candidate(asdict(p))
        # Layer 3
        for w in report.workflow_concepts:
            self._store_single_candidate(asdict(w))
        # Layer 4
        for h in report.hypotheses:
            self._store_single_candidate(asdict(h))
        # Layer 5
        for t in report.theories:
            self._store_single_candidate(asdict(t))
        for q in report.questions:
            self._store_single_candidate(asdict(q))
        # Layer 6
        for d in report.dreams:
            self._store_single_candidate(asdict(d))
        # Layer 7
        for inv in report.investigations:
            self._store_single_candidate(asdict(inv))
        # Layer 8 (Sleep V6)
        for exp in report.experiments:
            self._store_single_candidate(asdict(exp))

    def _store_single_candidate(self, candidate: dict):
        ctype = candidate.get("type", "unknown")
        self.memory.store(
            json.dumps(candidate),
            event_type="sleep",
            source=f"sleep:{ctype}",
        )
