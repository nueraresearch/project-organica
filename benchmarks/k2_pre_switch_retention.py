"""K2's single-variable retention treatment.

The K2 constraint says pre-switch associations keep priority after the
revision boundary, so the new regime cannot displace them.  This module
implements that intervention as one in-process ``SleepService`` subclass:

* the only engine method it overrides is ``_natural_selection``;
* the only state it adds is the set of association keys first seen before
  the boundary and the per-seed manipulation counters;
* it changes only copies of prior candidates handed to the engine's own
  selection pass.  It never writes to memory itself.

``boundary_cycle=None`` is the K1 no-op control: the same class, the same
wiring, no intervention.  The K1 fixture must be byte-identical to the
shipped service before the K2 block may run.

This module changes no file under ``organica/``.  It is applied in process,
exactly as the existing Phase K ablations are.
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Callable, Iterable

from organica.sleep import SleepService

BOUNDARY_CYCLE = 200
PENALTY = 0.5
ASSOCIATION_TYPES = ("loop_candidate", "prediction_candidate", "hypothesis")

# The target types are fixed here and in the K2 build passport.  A type
# outside this tuple is not a K2 association and must not be touched.
VALID_ASSOCIATION_TYPES = frozenset(ASSOCIATION_TYPES)


def candidate_priority(record: dict) -> tuple[str | None, float | None]:
    """Return the candidate's retention field and numeric priority."""
    for field in ("confidence", "strength"):
        value = record.get(field)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return field, float(value)
    return None, None


def candidate_key(record: dict, key_of: Callable[[dict], str]) -> str:
    """A stable candidate identity, or an empty string when it has none."""
    return key_of(record) or ""


def _current_record(item) -> dict:
    if is_dataclass(item):
        return asdict(item)
    if isinstance(item, dict):
        return item
    return {}


def association_keys(items: Iterable, key_of: Callable[[dict], str]) -> set[str]:
    """Return the K2 association keys present in one cycle's candidates.

    ``items`` is an iterable of candidate dataclasses.  Carried-forward
    structures are views of prior state, not new candidate evidence, so they
    are skipped exactly as the engine's own selection pass skips them.
    """
    found: set[str] = set()
    for item in items or ():
        if getattr(item, "carried_forward", False):
            continue
        record = _current_record(item)
        if record.get("type") not in VALID_ASSOCIATION_TYPES:
            continue
        key = candidate_key(record, key_of)
        if key:
            found.add(key)
    return found


def apply_demotions(
    prior: list[dict],
    seen_pre_boundary: set[str],
    key_of: Callable[[dict], str],
    *,
    cycle: int,
    boundary_cycle: int,
    penalty: float,
    evidence: dict,
) -> list[dict]:
    """Copy prior associations that were first seen before the boundary.

    The returned list is safe to hand to ``super()._natural_selection``: it
    changes only the candidate's confidence/strength, preserving its identity,
    generation and evidence.  The input records are not mutated.

    ``evidence`` is the per-run counter dictionary owned by the service.  It is
    updated in place so a caller never needs a second write path.
    """
    adjusted: list[dict] = []
    for record in prior:
        ctype = record.get("type")
        key = candidate_key(record, key_of)
        field, before = candidate_priority(record)

        if (
            ctype not in VALID_ASSOCIATION_TYPES
            or not key
            or key not in seen_pre_boundary
            or field is None
            or before is None
        ):
            adjusted.append(record)
            continue

        if cycle < boundary_cycle:
            # The service never reaches this branch: the guard is here so a
            # fixture that calls the helper directly can prove the counter
            # would catch a pre-boundary demotion.
            evidence["pre_boundary_demotions"] += 1
            adjusted.append(record)
            continue

        evidence["post_boundary_target_count"] += 1
        after = round(before * penalty, 6)
        if after >= before:
            adjusted.append(record)
            continue

        changed = dict(record)
        changed[field] = after
        adjusted.append(changed)

        evidence["demoted_count"] += 1
        evidence["priority_before_sum"] = round(
            evidence["priority_before_sum"] + before, 6)
        evidence["priority_after_sum"] = round(
            evidence["priority_after_sum"] + after, 6)
        evidence["target_type_counts"][ctype] = (
            evidence["target_type_counts"].get(ctype, 0) + 1)

        delta = round(after - before, 6)
        evidence["min_priority_delta"] = (
            delta if evidence["min_priority_delta"] is None
            else min(evidence["min_priority_delta"], delta))
        evidence["max_priority_delta"] = (
            delta if evidence["max_priority_delta"] is None
            else max(evidence["max_priority_delta"], delta))
        if key not in evidence["sample_keys"] and len(evidence["sample_keys"]) < 5:
            evidence["sample_keys"].append(key)

    return adjusted


def empty_evidence(boundary_cycle: int | None) -> dict:
    """The per-seed manipulation record, with every required field present."""
    return {
        "boundary_cycle": boundary_cycle,
        "association_types": list(ASSOCIATION_TYPES),
        "cycles_observed": 0,
        "pre_boundary_key_count": 0,
        "post_boundary_target_count": 0,
        "demoted_count": 0,
        "pre_boundary_demotions": 0,
        "priority_before_sum": 0.0,
        "priority_after_sum": 0.0,
        "mean_priority_delta": None,
        "min_priority_delta": None,
        "max_priority_delta": None,
        "target_type_counts": {name: 0 for name in ASSOCIATION_TYPES},
        "sample_keys": [],
    }


class K2PreSwitchRetentionService(SleepService):
    """Lower pre-boundary association priority after the revision boundary.

    K2 arm: ``K2PreSwitchRetentionService(mem, boundary_cycle=200)``.
    K1 no-op: ``K2PreSwitchRetentionService(mem, boundary_cycle=None)``.

    The class deliberately has no helper methods.  Its entire engine-facing
    behaviour lives in the one override below; module-level functions do the
    pure work so the signature check can prove the class changed one thing.
    """

    def __init__(
        self,
        memory,
        *,
        boundary_cycle: int | None = BOUNDARY_CYCLE,
        penalty: float = PENALTY,
        association_types: tuple[str, ...] = ASSOCIATION_TYPES,
    ):
        super().__init__(memory)
        if boundary_cycle is not None and boundary_cycle < 1:
            raise ValueError("boundary_cycle must be a positive cycle or None")
        if not 0.0 < penalty < 1.0:
            raise ValueError("penalty must be strictly between zero and one")
        if tuple(association_types) != ASSOCIATION_TYPES:
            raise ValueError(
                "association_types is fixed by the K2 registration: %r"
                % (ASSOCIATION_TYPES,))
        self.boundary_cycle = boundary_cycle
        self.penalty = float(penalty)
        self.association_types = ASSOCIATION_TYPES
        self._seen_pre_boundary: set[str] = set()
        self.manipulation = empty_evidence(boundary_cycle)

    def _natural_selection(
        self, prior, concepts, phrases, loops, predictions,
        meta_concepts=None, processes=None, roles=None, workflows=None, schemas=None,
        hypotheses=None, theories=None, questions=None,
        dreams=None, investigations=None, experiments=None,
    ):
        adjusted = prior
        if self.boundary_cycle is not None:
            cycle = self._count_prior_cycles(prior) + 1
            self.manipulation["cycles_observed"] = max(
                self.manipulation["cycles_observed"], cycle)

            current = []
            for group in (
                concepts, phrases, loops, predictions, meta_concepts, processes,
                roles, workflows, schemas, hypotheses, theories, questions,
                dreams, investigations, experiments,
            ):
                current.extend(association_keys(group or (), self._candidate_key))

            if cycle < self.boundary_cycle:
                self._seen_pre_boundary.update(current)
                for record in prior:
                    if record.get("type") in VALID_ASSOCIATION_TYPES:
                        key = candidate_key(record, self._candidate_key)
                        if key:
                            self._seen_pre_boundary.add(key)
                self.manipulation["pre_boundary_key_count"] = len(
                    self._seen_pre_boundary)

            adjusted = apply_demotions(
                prior,
                self._seen_pre_boundary,
                self._candidate_key,
                cycle=cycle,
                boundary_cycle=self.boundary_cycle,
                penalty=self.penalty,
                evidence=self.manipulation,
            )
            if self.manipulation["demoted_count"]:
                self.manipulation["mean_priority_delta"] = round(
                    (self.manipulation["priority_after_sum"]
                     - self.manipulation["priority_before_sum"])
                    / self.manipulation["demoted_count"], 6)

        return super()._natural_selection(
            adjusted, concepts, phrases, loops, predictions,
            meta_concepts=meta_concepts,
            processes=processes,
            roles=roles,
            workflows=workflows,
            schemas=schemas,
            hypotheses=hypotheses,
            theories=theories,
            questions=questions,
            dreams=dreams,
            investigations=investigations,
            experiments=experiments,
        )
