"""
Organica Candidate Dataclasses and Scoring Models.

Defines all graph node representations across the developmental ladder:
  Generation 1: Concept, Phrase, Loop, Prediction, Anomaly
  Generation 2: MetaConcept, Process, Role
  Generation 3: WorkflowConcept, Schema
  Generation 4: Hypothesis
  Generation 5: Theory, Question
  Generation 6: Dream (Categorized)
  Generation 7: Investigation (EIG Ranking)
  Generation 8: Experiment (Active Probing)
"""

import hashlib
from dataclasses import dataclass, field
from typing import Optional, Any


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
    generation: int = 2
    parent_ids: list[str] = field(default_factory=list)
    anchor_tag: str = ""
    related_candidates: int = 0
    confidence: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class ProcessCandidate:
    type: str = "process_candidate"
    id: str = ""
    generation: int = 2
    parent_ids: list[str] = field(default_factory=list)
    cycle: list[str] = field(default_factory=list)
    strength: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class WorkflowConceptCandidate:
    type: str = "workflow_concept"
    id: str = ""
    generation: int = 3
    parent_ids: list[str] = field(default_factory=list)
    name: str = ""
    components: list[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class RoleCandidate:
    """An abstract structural role representing an equivalence class of entities
    occupying a characteristic topological and behavioral position (e.g. cluster
    cohesion, directional outflow, transition contingency) derived from empirical evidence.
    """
    type: str = "role_candidate"
    id: str = ""
    generation: int = 2
    parent_ids: list[str] = field(default_factory=list)
    exemplars: list[str] = field(default_factory=list)
    profile: dict = field(default_factory=dict)
    confidence: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class SchemaCandidate:
    """An abstract relational schema representing an invariant transition pattern
    across functional roles (e.g. antecedent -> consequent), independent of literal tokens.
    """
    type: str = "schema_candidate"
    id: str = ""
    generation: int = 3
    parent_ids: list[str] = field(default_factory=list)
    source_role: str = ""        # e.g., "antecedent"
    target_role: str = ""        # e.g., "consequent"
    source_role_id: str = ""     # ID of source RoleCandidate
    target_role_id: str = ""     # ID of target RoleCandidate
    source_exemplars: list[str] = field(default_factory=list)
    target_exemplars: list[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class HypothesisCandidate:
    type: str = "hypothesis"
    id: str = ""
    generation: int = 4
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
    generation: int = 5
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
    generation: int = 5
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
    generation: int = 6
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
    generation: int = 7
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
    generation: int = 8
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
    roles: list[RoleCandidate]                = field(default_factory=list)
    # Layer 3
    workflow_concepts: list[WorkflowConceptCandidate] = field(default_factory=list)
    schemas: list[SchemaCandidate]                    = field(default_factory=list)
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
    contradiction_density: float = 0.0  # M3: mean(contradiction / (support + contradiction)) across hypotheses
