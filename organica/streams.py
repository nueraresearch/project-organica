"""
organica/streams.py
------------------------------------------------------------------
The experience streams Organica can be run against.

A "stream" is just an ordered list of raw text events. No schema, no
labels, no categories -- the organism is supposed to work out what
matters from the structure of the text alone.

Two families live here:

  * `STUDY_STREAM` -- the stream used by the 90-day longitudinal study.
    It is deliberately built so that one subject ("developer executed
    test suite") is followed by BOTH a positive and a negative outcome.
    That is what lets Layer 5 coalesce two competing hypotheses into a
    Theory, and it is what gives the EIG attention economy something to
    be uncertain about. The original study stream rotated through 30
    unrelated events, which made Generation 5 unreachable -- see
    `research-journal/phase_g_findings_20261021.md`.

  * The four Phase F reproduction domains, each a self-contained world
    that demonstrates emergence in a few seconds.
"""

from __future__ import annotations

#: How many events the daemon injects per sleep cycle.
EVENTS_PER_CYCLE = 8


# ---------------------------------------------------------------------------
# The 90-day longitudinal study stream
# ---------------------------------------------------------------------------
STUDY_STREAM = [
    # --- Domain 1: developer workflow ---
    # "developer executed test suite" precedes both a failures report and a
    # passed report, so "developer" and "executed" accumulate two competing
    # expectations -> a Theory and a Question with real entropy.
    "developer modified auth login session",
    "developer executed test suite",
    "test suite report failures detected session",
    "developer modified api router endpoint",
    "developer executed test suite",
    "test suite report passed validation clean",
    "developer modified auth login session",
    "developer executed test suite",
    "test suite report failures detected session",
    "developer modified api router endpoint",
    "developer executed test suite",
    "test suite report passed validation clean",
] * 2 + [
    # --- Domain 2: defect triage ---
    # "engineer committed patch" likewise precedes both a failed and a
    # passed test run.
    "reporter filed issue ticket defect",
    "engineer reproduced defect stacktrace",
    "engineer committed patch defect",
    "pipeline executed tests failed",
    "reporter filed issue ticket regression",
    "engineer reproduced regression stacktrace",
    "engineer committed patch regression",
    "pipeline executed tests passed",
] * 3


# ---------------------------------------------------------------------------
# The four Phase F reproduction domains
# ---------------------------------------------------------------------------
DEVELOPER_WORKFLOW = [
    "developer modified auth login session",
    "developer executed test suite",
    "test suite report failures detected session",
    "failure detected in login module",
    "developer modified auth session handler",
    "developer executed test suite",
    "test suite report passed validation clean",
    "developer modified api router endpoint",
    "developer executed test suite",
    "test suite report failures detected router",
    "failure detected in router endpoint",
    "developer modified api router handler",
    "developer executed test suite",
    "test suite report passed validation clean",
] * 4

BUG_TRACKING = [
    "user reported issue ticket assigned",
    "triage assigned issue engineer review",
    "engineer reproduce issue commit patch",
    "pipeline executed tests verified passed",
    "support agent closed issue resolved",
    "user reported issue ticket assigned",
    "triage assigned issue engineer review",
    "engineer reproduce commit patch failed",
    "engineer reproduce commit patch retry",
    "pipeline executed tests verified passed",
    "support agent closed issue resolved",
] * 4

SYNTHETIC_ECOLOGY = [
    "organism search energy level depleted",
    "organism locate resource food available",
    "organism consume food energy restored",
    "biome replenish vegetation growth season",
    "organism rest metabolism stable recovered",
    "organism search energy level depleted",
    "organism locate resource food available",
    "organism consume food energy restored",
    "biome replenish vegetation growth season",
] * 5

ROBOT_SIMULATION = [
    "robot drive forward velocity motion",
    "sonar detect obstacle distance near",
    "actuator steer pivot turn left",
    "sonar sense clear corridor open",
    "robot drive forward velocity motion",
    "sonar detect obstacle distance near",
    "actuator steer pivot turn right",
    "sonar sense clear corridor open",
    "robot drive forward velocity motion",
] * 5

#: name -> (description, events)
DOMAINS = {
    "developer_workflow": (
        "Software CI/CD: failure -> modified -> passed",
        DEVELOPER_WORKFLOW,
    ),
    "bug_tracking": (
        "Issue triage -> engineer -> commit -> verify -> close",
        BUG_TRACKING,
    ),
    "synthetic_ecology": (
        "Organism -> forage -> consume -> replenish",
        SYNTHETIC_ECOLOGY,
    ),
    "robot_simulation": (
        "Drive -> detect obstacle -> turn -> clear path",
        ROBOT_SIMULATION,
    ),
}


__all__ = [
    "EVENTS_PER_CYCLE",
    "STUDY_STREAM",
    "DEVELOPER_WORKFLOW",
    "BUG_TRACKING",
    "SYNTHETIC_ECOLOGY",
    "ROBOT_SIMULATION",
    "DOMAINS",
]
