"""
Project Organica — A Developmental Machine Intelligence.
Growing intelligence from memory, structure, sleep, curiosity, and experimentation.
"""

#: The single source of truth for the package version.
#:
#: Semantic Versioning 2.0.0. The project is **pre-1.0**, so the public
#: API is not declared stable: anything may change at any time, and the
#: MINOR/PATCH numbers carry the meaning instead.
#:
#: Note the three separate version namespaces in this repository, which
#: are easy to confuse and are deliberately distinct:
#:
#:   * **this number** — the released package (SemVer 2).
#:   * **Organica 1 / Organica 2** — the *architecture generation*.
#:     Organica 1 is the frozen eight-layer engine; Organica 2 is the
#:     planned successor, described in docs/ORGANICA-V2-DESIGN-NOTES.md.
#:   * **Study 1 / Study 2** — the *research campaigns*:
#:     "Ablation Study 1" is the eleven-condition study, "Ablation Study 2"
#:     is the six-colony Tier-1 matrix.
#:
#: `tests/test_versioning.py` asserts that this number, `pyproject.toml`
#: and `CITATION.cff` all agree, so the three can never drift apart.
__version__ = "0.8.0"

from .memory import MemoryService, Event
from .sleep import (
    SleepService,
    SleepReport,
    ConceptCandidate,
    PhraseCandidate,
    LoopCandidate,
    PredictionCandidate,
    AnomalyCandidate,
    MetaConceptCandidate,
    ProcessCandidate,
    WorkflowConceptCandidate,
    HypothesisCandidate,
    TheoryCandidate,
    QuestionCandidate,
    DreamCandidate,
    InvestigationCandidate,
    ExperimentCandidate,
)

__all__ = [
    "MemoryService",
    "Event",
    "SleepService",
    "SleepReport",
    "ConceptCandidate",
    "PhraseCandidate",
    "LoopCandidate",
    "PredictionCandidate",
    "AnomalyCandidate",
    "MetaConceptCandidate",
    "ProcessCandidate",
    "WorkflowConceptCandidate",
    "HypothesisCandidate",
    "TheoryCandidate",
    "QuestionCandidate",
    "DreamCandidate",
    "InvestigationCandidate",
    "ExperimentCandidate",
]
