"""
organica/environment.py
-----------------------
Environment interface and active experimentation dispatchers for Organica (Law IV).

Enables Organica to move from purely passive observation into active, embodied
inquiry: generated Layer-8 experiments emit concrete interventions into an
external environment, observe the resulting sensory feedback, store the empirical
outcome in MemoryService, and validate or refute hypotheses in real time.
"""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

from organica.memory import MemoryService
from organica.sleep import ExperimentCandidate, SleepReport, SleepService

log = logging.getLogger("organica.environment")


class Environment(ABC):
    """Abstract interface for an environment Organica can perceive and intervene upon."""

    @abstractmethod
    def step(self) -> list[str]:
        """Produce the next natural environmental observations (raw event strings)."""
        pass

    @abstractmethod
    def intervene(self, action_type: str, target: str, payload: dict[str, Any]) -> list[str]:
        """Execute a probe intervention on the environment and return the resulting sensory feedback.

        Parameters
        ----------
        action_type : str
            Type of intervention, e.g. "probe_context", "probe_sequence", "probe_state".
        target : str
            Identifier or name of the target entity/subject being probed.
        payload : dict
            Specific parameters or context for the probe.

        Returns
        -------
        list[str]
            Sensory event strings produced as immediate feedback from the intervention.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the environment to its initial state."""
        pass


class ReactiveWorld(Environment):
    """A deterministic, rule-grounded synthetic reactive world for testing active inquiry.

    The world possesses latent causal transitions. When no intervention occurs, it emits
    a natural background stream. When probed with specific actions (e.g. stimulating a
    subject or perturbing a sequence), it produces state transitions that either validate
    or refute the organism's hypothesis expectations.
    """

    def __init__(
        self,
        rules: Optional[dict[str, dict[str, str]]] = None,
        natural_stream: Optional[Sequence[str]] = None,
    ):
        # rules: { subject: { action_type: expected_outcome } }
        self.rules = rules or {
            "developer": {
                "probe_context": "developer executed test suite",
                "probe_sequence": "test suite passed with green status",
            },
            "engineer": {
                "probe_context": "engineer committed patch",
                "probe_sequence": "build pipeline succeeded cleanly",
            },
            "auth": {
                "probe_state": "authentication token validated",
            },
        }
        self.natural_stream = list(natural_stream) if natural_stream else [
            "developer executed test suite",
            "test suite passed with green status",
            "engineer committed patch",
            "build pipeline succeeded cleanly",
            "auth service issued session token",
        ]
        self._cursor = 0
        self.history: list[str] = []

    def step(self) -> list[str]:
        """Return the next natural event from the stream."""
        if not self.natural_stream:
            return []
        ev = self.natural_stream[self._cursor % len(self.natural_stream)]
        self._cursor += 1
        self.history.append(ev)
        return [ev]

    def intervene(self, action_type: str, target: str, payload: dict[str, Any]) -> list[str]:
        """Execute a causal intervention."""
        subject = payload.get("subject", target).lower()
        subject_rules = self.rules.get(subject, {})
        
        # Check if the world has a reactive outcome for this action and subject
        if action_type in subject_rules:
            feedback = subject_rules[action_type]
        elif "default" in subject_rules:
            feedback = subject_rules["default"]
        else:
            # Fallback neutral reaction
            feedback = f"{subject} exhibited neutral state response"

        self.history.append(f"[intervention] {action_type} on {subject} -> {feedback}")
        return [feedback]

    def reset(self) -> None:
        self._cursor = 0
        self.history.clear()


@dataclass
class ActiveInquiryResult:
    """Summary of an active inquiry cycle combining perception, sleep, and intervention."""
    cycle: int
    observations_ingested: int
    experiments_proposed: int
    experiments_executed: int
    experiments_validated: int
    experiments_refuted: int
    questions_closed: int
    execution_records: list[dict[str, Any]] = field(default_factory=list)


class ActiveInquiryLoop:
    """Orchestrates the active perception-consolidation-intervention loop.

    1. Perceive: Steps the Environment and ingests raw events into MemoryService (Law I).
    2. Consolidate: Executes a sleep cycle in SleepService, producing Layer 1-8 structures.
    3. Intervene: Dispatches proposed experiments to Environment.intervene(), records sensory
       feedback in MemoryService, and resolves hypotheses (Law IV).
    """

    def __init__(
        self,
        memory: MemoryService,
        sleep_service: SleepService,
        environment: Environment,
        events_per_step: int = 5,
    ):
        self.memory = memory
        self.sleep_service = sleep_service
        self.environment = environment
        self.events_per_step = events_per_step
        self.cycle_count = 0

    def step_and_sleep(self) -> tuple[SleepReport, ActiveInquiryResult]:
        """Perform one complete active cognitive cycle."""
        # 1. Perception phase: ingest natural observations into memory
        new_events: list[str] = []
        with self.memory.batch():
            for _ in range(self.events_per_step):
                evs = self.environment.step()
                for text in evs:
                    self.memory.store(text, event_type="observe", source=f"env:{self.cycle_count}")
                    new_events.append(text)

        # 2. Consolidation phase: sleep
        report = self.sleep_service.run_sleep_cycle()

        # 3. Active Intervention phase: dispatch Layer 8 experiments
        proposed_exps = [e for e in report.experiments if getattr(e, "status", "proposed") == "proposed"]
        
        execution_records: list[dict[str, Any]] = []
        validated_count = 0
        refuted_count = 0

        if proposed_exps:
            def environment_executor(exp: ExperimentCandidate) -> str:
                # Intervene on the environment
                feedback_events = self.environment.intervene(
                    action_type=exp.action_type or "probe_context",
                    target=exp.target_id,
                    payload=exp.probe_payload,
                )
                
                # Store resulting sensory observations in episodic memory
                with self.memory.batch():
                    for fb in feedback_events:
                        self.memory.store(
                            fb,
                            event_type="observe",
                            source=f"intervention:{exp.id}",
                        )

                # Check if feedback contains any expected outcomes
                matched = False
                expected = [o.lower() for o in exp.expected_outcomes]
                for fb in feedback_events:
                    fb_lower = fb.lower()
                    if any(exp_tag in fb_lower for exp_tag in expected):
                        matched = True
                        break

                return "validated" if matched else "refuted"

            # Execute via SleepService's experiment execution engine
            results = self.sleep_service.execute_experiments(
                experiments=proposed_exps,
                executor_fn=environment_executor,
            )
            execution_records = results
            for r in results:
                if r.get("status") == "validated":
                    validated_count += 1
                else:
                    refuted_count += 1

        inquiry_summary = ActiveInquiryResult(
            cycle=self.cycle_count,
            observations_ingested=len(new_events),
            experiments_proposed=len(report.experiments),
            experiments_executed=len(execution_records),
            experiments_validated=validated_count,
            experiments_refuted=refuted_count,
            questions_closed=len(getattr(report, "questions_closed", [])),
            execution_records=execution_records,
        )

        self.cycle_count += 1
        return report, inquiry_summary
