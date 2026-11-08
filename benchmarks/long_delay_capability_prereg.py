"""Frozen constants and the decision rule for the capability protocol.

The protocol is `docs/LONG-DELAY-CAPABILITY-PREREGISTRATION.md`.  The digest
below changes if any frozen choice changes; the campaign does not run when it
does not match.  The classifier is the only place the decision table is
implemented, so a label cannot drift from the protocol.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

PROTOCOL = {
    "question": "Q051",
    "cycles": 300,
    "events_per_cycle": 8,
    "rare_period": 40,
    "k": 5,
    "arms": [0.95, 0.99, 0.9925, 1.0],
    "primary": [0.95, 0.9925],
    "windows": {"early": [40, 90], "late": [240, 300]},
    "design_seeds": list(range(20302901, 20302906)),
    "confirm_seeds": list(range(20302911, 20302921)),
    "delta_floor": 0.010,
    "delta_sd_factor": 1.5,
    "positive_seeds_required": 8,
    "early_equivalence": 0.010,
}

PROTOCOL_DIGEST = "12692335988e00c9"

LABELS = (
    "CAPABILITY_EARNED",
    "LATE_GAIN_EARLY_COST",
    "PERSISTENCE_WITHOUT_CAPABILITY",
    "INCONCLUSIVE",
    "VOID",
)


def digest() -> str:
    blob = json.dumps(PROTOCOL, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def delta(sd_design: float) -> float:
    return max(PROTOCOL["delta_floor"],
               PROTOCOL["delta_sd_factor"] * float(sd_design))


def validate() -> list[str]:
    problems = []
    if digest() != PROTOCOL_DIGEST:
        problems.append("protocol digest changed")
    if PROTOCOL["primary"] != [0.95, 0.9925]:
        problems.append("primary pair is not shipped vs 0.9925")
    if PROTOCOL["k"] != 5:
        problems.append("k is not frozen at 5")
    early, late = PROTOCOL["windows"]["early"], PROTOCOL["windows"]["late"]
    if early[1] > late[0]:
        problems.append("windows overlap")
    if set(PROTOCOL["design_seeds"]) & set(PROTOCOL["confirm_seeds"]):
        problems.append("design and confirmatory seeds overlap")
    if PROTOCOL["delta_floor"] <= 0:
        problems.append("delta floor is not positive")
    return problems


def unused_seeds(harvested: set[int]) -> bool:
    """True when no confirmatory seed has been harvested.

    The design seeds are consumed by the design block by construction; only
    the confirmatory block's seeds must be untouched.
    """
    return not set(PROTOCOL["confirm_seeds"]) & set(harvested)


def seed_live(per_arm_early: dict[str, list[float]]) -> bool:
    """True when at least one arm's early score varies across seeds."""
    for values in per_arm_early.values():
        if len({round(float(v), 9) for v in values}) > 1:
            return True
    return False


def classify(*, early_gap: float, late_gap: float, late_positive: int,
             transition_positive: int, gates_ok: bool) -> str:
    if not gates_ok:
        return "VOID"
    bar = delta(0.0)
    early_ok = abs(early_gap) < PROTOCOL["early_equivalence"]
    late_ok = (late_gap >= bar and
               late_positive >= PROTOCOL["positive_seeds_required"])
    growth_ok = transition_positive >= PROTOCOL["positive_seeds_required"]
    if late_ok and early_ok and growth_ok:
        return "CAPABILITY_EARNED"
    if late_ok and not early_ok:
        return "LATE_GAIN_EARLY_COST"
    if late_gap <= 0:
        return "PERSISTENCE_WITHOUT_CAPABILITY"
    return "INCONCLUSIVE"


if __name__ == "__main__":
    problems = validate()
    for problem in problems:
        print("!! " + problem)
    print("digest:", digest())
    raise SystemExit(1 if problems else 0)
