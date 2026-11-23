"""The K2 one-block runner: grant, lease, marker, campaign, result, gate.

``k2_gate`` owns the build contract and refuses before a cell; this module owns
the one authorised block.  It is the only entry point that may acquire the K2
block lease, write the attempt marker, call the campaign's K1/K2 factories and
assemble ``docs/phase_k_k2_results.json``.

The order is fixed and every step refuses before the next one runs:

1. **grant** -- a dated owner grant at ``docs/K2-BLOCK-GRANT.json`` naming this
   block.  No grant, no undated grant, a future-dated grant or a grant for a
   different block is refused before anything is written;
2. **preflight** -- every ``k2_gate`` G row, including the engine pin, the
   treatment signature, the K1 no-op fixture, the seed block and the output
   allowlist;
3. **lease** -- exactly one block lease, created exclusively, covering K1 and
   K2 together.  A per-seed lease is never written;
4. **marker** -- exactly one attempt marker, the block's only attempt record;
5. **campaign** -- the campaign's own ``task_k1`` / ``task_k2`` factories via
   ``run_campaign``, so the treatment is the frozen one and the checkpoint is
   the campaign's;
6. **result** -- the gate-shaped result, read by ``k2_gate.validate_result``,
   never by its own label.

Exit states are the passport's: a refusal is ``REFUSED`` (exit 2, no result), a
``VOID`` result is written but no criterion is read (exit 3), and an
``INCONCLUSIVE`` result is written with no criterion read (exit 0).

``--resume`` continues an interrupted block with the same attempt id and the
same single lease; it never starts a second attempt.  A hard kill leaves the
lease ``ACTIVE``; ``--reclaim`` closes it only when its recorded attempt id
matches and its recorded process is gone.

This module changes no file under ``organica/`` and writes no result unless a
grant, a preflight and a lease all pass first.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import statistics
import sys
from datetime import date
from functools import partial
from pathlib import Path

# The campaign modules are run as scripts (``python benchmarks/...py``), so the
# repository root has to be importable before the package imports below.
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from benchmarks import engine_stamp, k2_gate as gate  # noqa: E402
from benchmarks import phase_k_campaign as campaign  # noqa: E402
from benchmarks.k2_pre_switch_retention import (  # noqa: E402
    ASSOCIATION_TYPES,
    PENALTY,
    K2PreSwitchRetentionService,
    apply_demotions,
    empty_evidence,
)
from organica.sleep import SleepService  # noqa: E402

ROOT = REPO

DEFAULT_GRANT = ROOT / "docs" / "K2-BLOCK-GRANT.json"
DEFAULT_RESULT = gate.DEFAULT_RESULT
DEFAULT_CHECKPOINT = gate.DEFAULT_CHECKPOINT
DEFAULT_LEASE = gate.DEFAULT_LEASE
DEFAULT_MARKER = gate.DEFAULT_MARKER

GRANT_KIND = "k2_block_grant"
GRANT_AUTHORIZES = "k2-block"
REQUIRED_GRANT_FIELDS = (
    "kind", "grant_id", "granted_on", "granted_by", "authorizes", "block",
)
GRANT_BLOCK_FIELDS = ("families", "seeds", "cycles", "scale", "workers")

DEFAULT_WORKERS = 1
FIXTURE_SEED = 1
FIXTURE_ID = "K1-NOOP-FIXTURE-1"


class GrantRefusal(Exception):
    """A refusal raised before the gate is consulted."""

    def __init__(self, code: str, message: str, **evidence):
        super().__init__(message)
        self.code = code
        self.message = message
        self.evidence = evidence

    def receipt(self, **extra) -> dict:
        body = {
            "state": "REFUSED",
            "stage": "grant",
            "exit_code": 2,
            "refusal_code": self.code,
            "message": self.message,
            "result_written": False,
            "cells_started": 0,
            "cells_completed": 0,
            "lease": {"state": "NOT_ACQUIRED"},
            "attempt": {"state": "NOT_WRITTEN"},
        }
        body["checks"] = dict(self.evidence)
        body.update(extra)
        return body


def _refuse(code: str, message: str, **evidence):
    raise GrantRefusal(code, message, **evidence)


def _preflight_receipt(refusal: gate.GateRefusal, **extra) -> dict:
    """The gate's refusal, made explicit about the lease and the marker.

    ``k2_gate`` never acquires a lease, so its receipt does not say so; the
    runner does, and a reader of the refusal must be able to see that no lease
    and no marker exist.
    """
    body = refusal.receipt(**extra)
    body.setdefault("lease", {"state": "NOT_ACQUIRED"})
    body.setdefault("attempt", {"state": "NOT_WRITTEN"})
    return body


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _digest(value) -> str:
    return _sha256_text(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def _write_json_atomic(path: Path, payload: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, path)


# ==================================================================
# The dated grant
# ==================================================================

def grant_digest(grant: dict) -> str:
    """A stable digest of the authorising fields, never of the free text."""
    body = {
        key: grant.get(key)
        for key in ("kind", "grant_id", "granted_on", "granted_by",
                    "authorizes", "block")
    }
    return _digest(body)


def load_grant(
    path: Path | str = DEFAULT_GRANT, *,
    today: date | None = None,
    families: tuple[str, ...] = gate.EXPECTED_FAMILIES,
    seeds: tuple[int, ...] = gate.K2_SEEDS,
    cycles: int = gate.K2_CYCLES,
    scale: int = 1,
) -> dict:
    """Read and check the owner's dated grant for this block.

    A grant is *dated* when ``granted_on`` is a real ISO date and is not in the
    future.  The block it authorises is fixed here: the same two families, the
    same ten seeds, 300 cycles at scale 1 and a fixed worker count.  Any drift
    is refused rather than run.
    """
    path = Path(path)
    if not path.exists():
        _refuse(
            "GRANT_MISSING",
            "the K2 block requires a dated owner grant and none exists",
            grant_path=str(path),
            grant_present=False,
            result_written=False,
            cells_started=0,
        )
    try:
        grant = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        _refuse(
            "GRANT_UNREADABLE",
            "the grant file is not readable JSON",
            grant_path=str(path),
            error=str(exc),
            result_written=False,
            cells_started=0,
        )
    if not isinstance(grant, dict):
        _refuse(
            "GRANT_UNREADABLE",
            "the grant is not a JSON object",
            grant_path=str(path),
            observed_type=type(grant).__name__,
            result_written=False,
            cells_started=0,
        )
    missing = [name for name in REQUIRED_GRANT_FIELDS if not grant.get(name)]
    if missing:
        _refuse(
            "GRANT_UNDATED" if "granted_on" in missing else "GRANT_INCOMPLETE",
            "the grant does not carry every authorising field",
            grant_path=str(path),
            missing_fields=missing,
            required_fields=list(REQUIRED_GRANT_FIELDS),
            result_written=False,
            cells_started=0,
        )
    try:
        granted_on = date.fromisoformat(str(grant["granted_on"]))
    except ValueError:
        _refuse(
            "GRANT_UNDATED",
            "the grant's date is not an ISO date",
            granted_on=grant.get("granted_on"),
            expected_format="YYYY-MM-DD",
            result_written=False,
            cells_started=0,
        )
    today = today or date.today()
    if granted_on > today:
        _refuse(
            "GRANT_NOT_YET_VALID",
            "the grant is dated after the day it would run",
            granted_on=granted_on.isoformat(),
            today=today.isoformat(),
            result_written=False,
            cells_started=0,
        )
    if grant.get("kind") != GRANT_KIND:
        _refuse(
            "GRANT_BLOCK_MISMATCH",
            "the grant is not a K2 block grant",
            expected_kind=GRANT_KIND,
            observed_kind=grant.get("kind"),
            result_written=False,
            cells_started=0,
        )
    if grant.get("authorizes") != GRANT_AUTHORIZES:
        _refuse(
            "GRANT_BLOCK_MISMATCH",
            "the grant does not authorise this block",
            expected_authorizes=GRANT_AUTHORIZES,
            observed_authorizes=grant.get("authorizes"),
            result_written=False,
            cells_started=0,
        )
    block = grant.get("block")
    if not isinstance(block, dict):
        _refuse(
            "GRANT_INCOMPLETE",
            "the grant does not state the block it authorises",
            missing_fields=["block"],
            required_fields=list(GRANT_BLOCK_FIELDS),
            result_written=False,
            cells_started=0,
        )
    missing_block = [
        name for name in GRANT_BLOCK_FIELDS if block.get(name) in (None, "", [])
    ]
    if missing_block:
        _refuse(
            "GRANT_INCOMPLETE",
            "the grant's block is missing fields",
            missing_fields=missing_block,
            required_fields=list(GRANT_BLOCK_FIELDS),
            result_written=False,
            cells_started=0,
        )
    expected = {
        "families": sorted(families),
        "seeds": sorted(seeds),
        "cycles": cycles,
        "scale": scale,
        "workers": block.get("workers"),
    }
    observed = {
        "families": sorted(block.get("families") or []),
        "seeds": sorted(block.get("seeds") or []),
        "cycles": block.get("cycles"),
        "scale": block.get("scale"),
        "workers": block.get("workers"),
    }
    if (observed["families"] != expected["families"]
            or observed["seeds"] != expected["seeds"]
            or observed["cycles"] != expected["cycles"]
            or observed["scale"] != expected["scale"]):
        _refuse(
            "GRANT_BLOCK_MISMATCH",
            "the grant authorises a different block than the frozen one",
            expected_block={k: expected[k] for k in
                           ("families", "seeds", "cycles", "scale")},
            observed_block={k: observed[k] for k in
                            ("families", "seeds", "cycles", "scale")},
            result_written=False,
            cells_started=0,
        )
    workers = observed["workers"]
    if not isinstance(workers, int) or isinstance(workers, bool) or workers < 1:
        _refuse(
            "GRANT_BLOCK_MISMATCH",
            "the grant does not fix a valid worker count",
            observed_workers=workers,
            minimum_workers=1,
            result_written=False,
            cells_started=0,
        )
    checked = dict(grant)
    checked["granted_on"] = granted_on.isoformat()
    checked["grant_path"] = str(path)
    checked["grant_sha256"] = grant_digest(grant)
    return checked


# ==================================================================
# Arm identity
# ==================================================================

def primary_factory():
    """The registered K2 treatment arm."""
    return partial(
        K2PreSwitchRetentionService,
        boundary_cycle=gate.K2_BOUNDARY_CYCLE,
        penalty=gate.K2_PENALTY,
        association_types=gate.K2_TARGET_TYPES,
    )


def k1_factory():
    """The K1 no-op guard: the same class, no boundary."""
    return partial(
        K2PreSwitchRetentionService,
        boundary_cycle=None,
        penalty=gate.K2_PENALTY,
        association_types=gate.K2_TARGET_TYPES,
    )


def arm_signature() -> str:
    """A digest of the two arms' wiring, so a resume cannot silently rewire."""
    body = {
        "primary": {
            "class": K2PreSwitchRetentionService.__name__,
            "boundary_cycle": gate.K2_BOUNDARY_CYCLE,
            "penalty": gate.K2_PENALTY,
            "association_types": list(ASSOCIATION_TYPES),
        },
        "k1": {
            "class": K2PreSwitchRetentionService.__name__,
            "boundary_cycle": None,
            "penalty": gate.K2_PENALTY,
            "association_types": list(ASSOCIATION_TYPES),
        },
    }
    return _digest(body)[:16]


def build_digest() -> str:
    """The runner build a grant authorises, independent of the working tree."""
    parts = []
    for name in ("k2_block.py", "k2_gate.py", "k2_pre_switch_retention.py"):
        path = Path(__file__).resolve().parent / name
        parts.append(name + ":" + _sha256_text(path.read_text(encoding="utf-8")))
    return _sha256_text("|".join(parts))


def attempt_id_for(grant: dict, *, signature: str | None = None) -> str:
    """The block's attempt id: grant, build, arm and seed block, nothing else."""
    body = {
        "grant_id": grant.get("grant_id"),
        "granted_on": grant.get("granted_on"),
        "grant_sha256": grant_digest(grant),
        "build": build_digest(),
        "arm": signature or arm_signature(),
        "seeds": list(gate.K2_SEEDS),
    }
    return "k2-block-" + _digest(body)[:16]


# ==================================================================
# The K1 no-op fixture
# ==================================================================

def k1_fixture() -> list[dict]:
    """The shared candidate fixture: one per target type, one outside them."""
    return [
        {"id": "loop:alpha", "type": "loop_candidate", "strength": 1.0},
        {"id": "prediction:beta", "type": "prediction_candidate",
         "confidence": 0.8},
        {"id": "hypothesis:gamma", "type": "hypothesis", "confidence": 0.6},
        {"id": "concept:delta", "type": "concept_candidate", "confidence": 0.4},
    ]


def _key_of(record: dict) -> str:
    return record.get("id", "")


def _noop_probe(boundary_cycle: int | None) -> K2PreSwitchRetentionService:
    """A receiver with the state the selection pass reads, and no database."""
    service = K2PreSwitchRetentionService.__new__(K2PreSwitchRetentionService)
    service.boundary_cycle = boundary_cycle
    service.penalty = PENALTY
    service.association_types = ASSOCIATION_TYPES
    service._seen_pre_boundary = {record["id"] for record in k1_fixture()}
    service.manipulation = empty_evidence(boundary_cycle)
    return service


def k1_noop_evidence(fixture: list[dict] | None = None) -> dict:
    """Compare the no-op K1 arm with the shipped K1 path on one fixture.

    The shipped path (``SleepService._natural_selection``, which is the K1
    primary arm when ``task_k1`` runs without a factory) and the no-op override
    are both called on the *same* candidates and the *same* receiver state.
    For the duration of the fixture only, the engine's selection body is
    replaced by a recorder that returns the fixture's own digest, so the two
    returns compare the complete effective argument set, defaults included.
    The recorder is restored in ``finally``; nothing under ``organica/`` is
    edited and no sleep cycle is executed.

    Each recorded call returns the digest of its own effective argument set,
    so ``shipped_hash`` already contains ``shipped_arguments_sha256`` and the
    gate compares the argument sets and the selections in one check.

    The fixture is discriminating: the same candidates are demoted when the
    boundary is live (``counterfactual_demoted_count``), so a no-op that did
    nothing and one that demoted are distinguishable.
    """
    fixture = k1_fixture() if fixture is None else fixture
    signature = inspect.signature(SleepService._natural_selection)
    original = SleepService._natural_selection
    calls: list[dict] = []

    def recorder(self, prior, *args, **kwargs):
        bound = signature.bind(self, prior, *args, **kwargs)
        bound.apply_defaults()
        arguments = {name: value for name, value in bound.arguments.items()
                     if name != "self"}
        calls.append({"prior": prior, "arguments": arguments})
        return (len(prior), _digest(arguments))

    probe = _noop_probe(None)
    SleepService._natural_selection = recorder
    try:
        shipped_return = SleepService._natural_selection(
            probe, fixture, [], [], [], [])
        noop_return = probe._natural_selection(fixture, [], [], [], [])
    finally:
        SleepService._natural_selection = original

    shipped_call, noop_call = calls[0], calls[1]
    counterfactual = empty_evidence(gate.K2_BOUNDARY_CYCLE)
    apply_demotions(
        fixture, {record["id"] for record in fixture}, _key_of,
        cycle=gate.K2_BOUNDARY_CYCLE, boundary_cycle=gate.K2_BOUNDARY_CYCLE,
        penalty=PENALTY, evidence=counterfactual)
    return {
        "kind": "k1_noop_fixture",
        "fixture_id": FIXTURE_ID,
        "fixture_seed": FIXTURE_SEED,
        "fixture_size": len(fixture),
        "fixture_sha256": _digest(fixture),
        "shipped_fixture_sha256": _digest(shipped_call["prior"]),
        "noop_fixture_sha256": _digest(noop_call["prior"]),
        "shipped_hash": _digest(shipped_return),
        "noop_hash": _digest(noop_return),
        "shipped_arguments_sha256": _digest(shipped_call["arguments"]),
        "noop_arguments_sha256": _digest(noop_call["arguments"]),
        "forwarded_identical": (shipped_call["prior"] is fixture
                                and noop_call["prior"] is fixture),
        "shipped_manipulation": None,
        "noop_manipulation": probe.manipulation,
        "counterfactual_demoted_count": counterfactual["demoted_count"],
        "demoted_count": probe.manipulation["demoted_count"],
        "pre_boundary_demotions": probe.manipulation["pre_boundary_demotions"],
        "priority_before_sum": probe.manipulation["priority_before_sum"],
        "priority_after_sum": probe.manipulation["priority_after_sum"],
        "boundary_cycle": probe.manipulation["boundary_cycle"],
    }


# ==================================================================
# The one lease and the one marker
# ==================================================================

def _now() -> str:
    return date.today().isoformat()


def _pid_alive(pid) -> bool:
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def acquire_lease(
    lease_path: Path | str, *,
    attempt_id: str,
    grant: dict,
    owner: str | None = None,
    resume: bool = False,
) -> dict:
    """Create the block's single lease, or reopen it for a resume.

    A fresh block uses ``O_EXCL`` so two processes cannot both hold it.  A
    resume rewrites the same file, preserving its acquisition time and counting
    the resume; it never creates a second lease.
    """
    lease_path = Path(lease_path)
    lease_path.parent.mkdir(parents=True, exist_ok=True)
    prior = _read_json(lease_path) if lease_path.exists() else {}
    if not resume:
        try:
            handle = os.open(
                lease_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            _refuse(
                "K2_BLOCK_LEASE_HELD",
                "the K2 block lease already exists",
                lease_path=str(lease_path),
                lease_state=prior.get("state"),
                lease_owner=prior.get("owner"),
                result_written=False,
                cells_started=0,
            )
        else:
            os.close(handle)
    body = dict(prior)
    body.update({
        "kind": "k2_block_lease",
        "state": "ACTIVE",
        "attempt_id": attempt_id,
        "owner": owner or os.environ.get("USER") or "unknown",
        "pid": os.getpid(),
        "grant_id": grant.get("grant_id"),
        "granted_on": grant.get("granted_on"),
        "grant_sha256": grant.get("grant_sha256"),
        "families": list(gate.EXPECTED_FAMILIES),
        "seeds": list(gate.K2_SEEDS),
        "cells_total": len(gate.EXPECTED_FAMILIES) * len(gate.K2_SEEDS),
        "cells_completed": 0,
        "per_seed_leases": 0,
        "acquired_at": prior.get("acquired_at") or _now(),
        "resume_count": (int(prior.get("resume_count", 0)) + 1) if resume else 0,
        "reopened_at": _now() if resume else None,
    })
    # A reopened lease keeps its history but not the previous run's outcome.
    body.pop("outcome", None)
    body.pop("error", None)
    _write_json_atomic(lease_path, body)
    return body


def close_lease(
    lease_path: Path | str, *, state: str, attempt_id: str, **extra,
) -> dict:
    """Close the block's lease as ``CLOSED`` or ``INTERRUPTED``."""
    lease_path = Path(lease_path)
    body = _read_json(lease_path)
    body.update({
        "kind": "k2_block_lease",
        "state": state,
        "attempt_id": attempt_id,
        "pid": os.getpid(),
        "finished_at": _now(),
    })
    body.update(extra)
    _write_json_atomic(lease_path, body)
    return body


def write_marker(marker_path: Path | str, payload: dict) -> dict:
    """Write the block's single attempt marker, merging any prior marker."""
    marker_path = Path(marker_path)
    body = _read_json(marker_path) if marker_path.exists() else {}
    body.update(payload)
    body["kind"] = "k2_attempt"
    _write_json_atomic(marker_path, body)
    return body


def _reclaim_lease(
    lease_path: Path | str, *, attempt_id: str,
    pid_alive=_pid_alive,
) -> dict:
    """Close a stale ``ACTIVE`` lease left by a killed process.

    Reclaiming needs both facts: the lease must belong to this attempt and the
    process it names must be gone.  Anything else is refused, and a lease whose
    process still exists is never taken.
    """
    lease_path = Path(lease_path)
    lease = _read_json(lease_path)
    if lease.get("state") != "ACTIVE":
        return lease
    if lease.get("attempt_id") != attempt_id:
        _refuse(
            "K2_LEASE_NOT_RECLAIMABLE",
            "the active lease belongs to another attempt",
            lease_path=str(lease_path),
            attempt_id_current=attempt_id,
            attempt_id_lease=lease.get("attempt_id"),
            lease_state="ACTIVE",
            result_written=False,
            cells_started=0,
        )
    if pid_alive(lease.get("pid")):
        _refuse(
            "K2_LEASE_NOT_RECLAIMABLE",
            "the active lease's process is still running",
            lease_path=str(lease_path),
            lease_pid=lease.get("pid"),
            lease_state="ACTIVE",
            result_written=False,
            cells_started=0,
        )
    return close_lease(
        lease_path, state="INTERRUPTED", attempt_id=attempt_id,
        reclaimed_at=_now(), reclaimed_from_pid=lease.get("pid"),
        outcome="RECLAIMED",
    )


# ==================================================================
# The campaign and the gate-shaped result
# ==================================================================

def _campaign(**kwargs) -> dict:
    return campaign.run_campaign(**kwargs)


class CheckpointError(campaign.CheckpointError):
    """The recording cannot be read as one complete record per cell.

    A refusal, not a crash: the checkpoint is written before the result is
    assembled, so a recording that cannot be read has no result behind it and
    must not acquire a lease or start a cell.
    """

    def receipt(self, **extra) -> dict:
        body = {
            "state": "REFUSED",
            "stage": "checkpoint",
            "exit_code": 2,
            "refusal_code": self.code,
            "message": self.message,
            "result_written": False,
            "cells_started": 0,
            "cells_completed": 0,
            "lease": {"state": "NOT_ACQUIRED"},
            "attempt": {"state": "NOT_WRITTEN"},
        }
        body["checks"] = dict(self.evidence)
        body.update(extra)
        return body


def _with_receipt(refusal: campaign.CheckpointError) -> CheckpointError:
    """The campaign's refusal in the block's receipt-publishing subclass."""
    if isinstance(refusal, CheckpointError):
        return refusal
    return CheckpointError(refusal.code, refusal.message, **refusal.evidence)


def read_checkpoint_report(path: Path | str) -> dict:
    """The campaign's strict reader, narrowed to this block's two families.

    One file has one reader: the campaign owns both the writer and the rules,
    and the block adds only what it needs -- the two families this block may
    contain, and a refusal receipt that says no lease and no marker exist.
    """
    try:
        return campaign.read_checkpoint_report(
            path, families=gate.EXPECTED_FAMILIES)
    except campaign.CheckpointError as refusal:
        raise _with_receipt(refusal) from None


def read_checkpoint(path: Path | str) -> list[dict]:
    """The checkpoint's records: one per cell, in first-appearance order."""
    return read_checkpoint_report(path)["records"]


def repair_partial_final_row(path: Path | str) -> dict:
    """The campaign's repair, narrowed to this block's two families."""
    try:
        return campaign.repair_partial_final_row(
            path, families=gate.EXPECTED_FAMILIES)
    except campaign.CheckpointError as refusal:
        raise _with_receipt(refusal) from None


def _checkpoint_cells(path: Path | str) -> int:
    """How many complete cells the recording holds, without raising."""
    try:
        return len(read_checkpoint(path))
    except CheckpointError:
        return 0


def _number(value) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def paired_gap(records: list[dict], family: str) -> tuple[float | None, int]:
    """The paired mean of Organica minus the best-of-grid baseline."""
    diffs: list[float] = []
    for record in records:
        if record.get("family") != family:
            continue
        organica = _number(record.get("organica"))
        baseline = _number((record.get("best_simple_baseline") or {}).get("primary"))
        if organica is None or baseline is None:
            continue
        diffs.append(organica - baseline)
    if not diffs:
        return None, 0
    return round(statistics.mean(diffs), 6), len(diffs)


def assemble_result(
    *,
    records: list[dict],
    attempt_id: str,
    signature: str,
    grant: dict,
    engine_tree_sha256: str,
    workers: int,
) -> dict:
    """Build the result ``k2_gate.validate_result`` reads.

    The records are the campaign's own per-seed records; the gate reads their
    ``family``, ``seed`` and ``manipulation`` evidence, and the raw scores are
    kept so a resume can rebuild the campaign's done set from the same file.
    """
    k2_gap, k2_n = paired_gap(records, gate.K2_FAMILY)
    k1_gap, k1_n = paired_gap(records, gate.K1_FAMILY)
    if k1_gap is None:
        abs_change = None
    else:
        abs_change = round(abs(abs(k1_gap) - abs(gate.K1_PRE_VALUE)), 6)
    return {
        "kind": "k2_block_result",
        "state": "RESULT_WRITTEN",
        "attempt_id": attempt_id,
        "arm_signature": signature,
        "arm": {
            "class": K2PreSwitchRetentionService.__name__,
            "class_hash": gate.class_hash(K2PreSwitchRetentionService),
            "primary_boundary_cycle": gate.K2_BOUNDARY_CYCLE,
            "k1_boundary_cycle": None,
            "penalty": gate.K2_PENALTY,
            "association_types": list(ASSOCIATION_TYPES),
        },
        "engine_tree_sha256": engine_tree_sha256,
        "k2_gap": k2_gap,
        "k2_cells": k2_n,
        "k1": {
            "pre_value": gate.K1_PRE_VALUE,
            "post_value": k1_gap,
            "abs_change": abs_change,
            "cells": k1_n,
        },
        "protocol": {
            "preregistration": "docs/PHASE-K-PREREGISTRATION.md",
            "registration": "CONSTRAINT-K2-1",
            "passport": "docs/K2-BUILD-PASSPORT.md",
            "families": list(gate.EXPECTED_FAMILIES),
            "seeds": list(gate.K2_SEEDS),
            "cycles": gate.K2_CYCLES,
            "cycle_scale": 1,
            "workers": workers,
            "python_hash_seed": "0",
            "bootstrap_seed": gate.stable_bootstrap_seed(),
            "decision_alpha": 1 - 0.9833,
            "baseline_gap": gate.BASELINE_GAP,
            "k1_pre_value": gate.K1_PRE_VALUE,
            "grant_id": grant.get("grant_id"),
            "granted_on": grant.get("granted_on"),
            "grant_sha256": grant.get("grant_sha256"),
        },
        "records": [
            {
                "family": record.get("family"),
                "seed": record.get("seed"),
                "attempt_id": attempt_id,
                "organica": record.get("organica"),
                "ablation": record.get("ablation"),
                "best_simple_baseline": record.get("best_simple_baseline"),
                "all_models": record.get("all_models"),
                "manipulation": record.get("manipulation"),
                "protocol": record.get("protocol"),
            }
            for record in records
        ],
    }


# ==================================================================
# The block
# ==================================================================

def run_block(
    *,
    grant_path: Path | str = DEFAULT_GRANT,
    out_path: Path | str = DEFAULT_RESULT,
    checkpoint_path: Path | str = DEFAULT_CHECKPOINT,
    lease_path: Path | str = DEFAULT_LEASE,
    marker_path: Path | str = DEFAULT_MARKER,
    resume: bool = False,
    reclaim: bool = False,
    owner: str | None = None,
    today: date | None = None,
    env: dict | None = None,
    campaign_runner=None,
    allowed_outputs=None,
    pid_alive=_pid_alive,
) -> dict:
    """Run the one K2 block, or refuse before a cell.

    No side effect happens before the grant and the gate pass: the lease is
    acquired after preflight, and the marker after the lease.
    """
    out_path = Path(out_path)
    checkpoint_path = Path(checkpoint_path)
    lease_path = Path(lease_path)
    marker_path = Path(marker_path)
    allowed = tuple(Path(path) for path in (
        allowed_outputs if allowed_outputs is not None else (out_path,)))

    try:
        grant = load_grant(grant_path, today=today)
    except GrantRefusal as refusal:
        return refusal.receipt(grant_path=str(grant_path))

    primary = primary_factory()
    noop = k1_factory()
    signature = arm_signature()
    attempt_id = attempt_id_for(grant, signature=signature)

    if resume and reclaim:
        try:
            _reclaim_lease(lease_path, attempt_id=attempt_id, pid_alive=pid_alive)
        except GrantRefusal as refusal:
            return refusal.receipt(
                grant_id=grant["grant_id"], attempt_id=attempt_id)

    try:
        report = gate.preflight(
            families=list(gate.EXPECTED_FAMILIES),
            seeds=list(gate.K2_SEEDS),
            scale=1,
            smoke=False,
            out_path=out_path,
            checkpoint_path=checkpoint_path,
            lease_path=lease_path,
            marker_path=marker_path,
            primary_factory=primary,
            k1_factory=noop,
            treatment_cls=K2PreSwitchRetentionService,
            resume=resume,
            env=dict(os.environ if env is None else env),
            engine_tree_sha256=gate.observed_engine_tree(),
            bootstrap_seed=gate.stable_bootstrap_seed(),
            baseline_gap=gate.BASELINE_GAP,
            k1_pre_value=gate.K1_PRE_VALUE,
            association_age_source="treatment_state",
            allowed_outputs=allowed,
            k1_noop_evidence=k1_noop_evidence(),
            attempt_id=attempt_id,
            arm_signature=signature,
        )
    except gate.GateRefusal as refusal:
        return _preflight_receipt(
            refusal, grant_id=grant["grant_id"], attempt_id=attempt_id)

    # The result is assembled by reading the checkpoint back, so the recording
    # is read here -- before the lease, so a corrupt one refuses without
    # starting a cell -- and a partial tail left by a kill is cut back before
    # the resumed campaign appends past it.
    try:
        checkpoint = repair_partial_final_row(checkpoint_path)
    except CheckpointError as refusal:
        return refusal.receipt(
            grant_id=grant["grant_id"], attempt_id=attempt_id,
            checkpoint_path=str(checkpoint_path))

    workers = int(grant["block"]["workers"])
    lease = acquire_lease(
        lease_path, attempt_id=attempt_id, grant=grant, owner=owner,
        resume=resume)
    prior_marker = _read_json(marker_path) if marker_path.exists() else {}
    marker = write_marker(marker_path, {
        "attempt_id": attempt_id,
        "arm_signature": signature,
        "state": "ACTIVE",
        "grant_id": grant["grant_id"],
        "granted_on": grant["granted_on"],
        "grant_sha256": grant["grant_sha256"],
        "families": list(gate.EXPECTED_FAMILIES),
        "seeds": list(gate.K2_SEEDS),
        "lease_path": str(lease_path),
        "started_at": prior_marker.get("started_at") or _now(),
        "resumed_at": _now() if resume else None,
        "resume_count": (
            int(prior_marker.get("resume_count", 0)) + 1 if resume else 0),
        "cells_total": len(gate.EXPECTED_FAMILIES) * len(gate.K2_SEEDS),
    })

    runner = campaign_runner or _campaign
    try:
        runner(
            families=list(gate.EXPECTED_FAMILIES),
            seeds=list(gate.K2_SEEDS),
            workers=workers,
            scale=1,
            out_path=out_path,
            resume=resume,
            checkpoint_path=checkpoint_path,
            primary_factories={
                gate.K2_FAMILY: primary,
                gate.K1_FAMILY: noop,
            },
        )
        checkpoint = read_checkpoint_report(checkpoint_path)
        payload = assemble_result(
            records=checkpoint["records"],
            attempt_id=attempt_id,
            signature=signature,
            grant=grant,
            engine_tree_sha256=report["engine_tree_sha256"],
            workers=workers,
        )
        decision = gate.validate_result(payload)
        payload["gate"] = decision
        _write_json_atomic(out_path, engine_stamp.stamp(payload))
    except BaseException as exc:
        # A block that stops for any reason is resumable: the lease says so,
        # the marker says so, and neither is replaced by a second attempt.
        close_lease(
            lease_path, state="INTERRUPTED", attempt_id=attempt_id,
            outcome="INTERRUPTED", error=repr(exc),
            cells_completed=_checkpoint_cells(checkpoint_path),
        )
        write_marker(marker_path, {
            "state": "INTERRUPTED",
            "updated_at": _now(),
            "error": repr(exc),
        })
        raise

    cells = checkpoint["cells"]
    close_lease(
        lease_path, state="CLOSED", attempt_id=attempt_id,
        outcome=decision["verdict"], cells_completed=cells,
    )
    write_marker(marker_path, {
        "state": "COMPLETE",
        "updated_at": _now(),
        "cells_completed": cells,
        "result_path": str(out_path),
        "gate_verdict": decision["verdict"],
        "gate_failed": decision["failed_gates"],
    })

    exit_code = 3 if decision["verdict"] == "VOID" else 0
    return {
        "state": "VALIDATED",
        "stage": "result",
        "exit_code": exit_code,
        "grant_id": grant["grant_id"],
        "granted_on": grant["granted_on"],
        "attempt_id": attempt_id,
        "arm_signature": signature,
        "lease": {"state": "CLOSED", "path": str(lease_path),
                  "acquired_at": lease["acquired_at"],
                  "resume_count": lease["resume_count"]},
        "attempt": {"state": "COMPLETE", "path": str(marker_path),
                    "resume_count": marker["resume_count"]},
        "result_path": str(out_path),
        "cells_completed": cells,
        "checkpoint": {
            "path": str(checkpoint_path),
            "rows": checkpoint["rows"],
            "cells": checkpoint["cells"],
            "duplicate_rows": checkpoint["duplicate_rows"],
            "duplicate_cells": checkpoint["duplicate_cells"],
            "partial_final_row": checkpoint["partial_final_row"],
        },
        "gate": decision,
        "result_written": True,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the one authorised K2 block, or refuse before a cell.")
    parser.add_argument("--grant", default=str(DEFAULT_GRANT),
                        help="the dated owner grant (required)")
    parser.add_argument("--out", default=str(DEFAULT_RESULT))
    parser.add_argument("--checkpoint", default=str(DEFAULT_CHECKPOINT))
    parser.add_argument("--lease", default=str(DEFAULT_LEASE))
    parser.add_argument("--marker", default=str(DEFAULT_MARKER))
    parser.add_argument("--resume", action="store_true",
                        help="continue an interrupted block under the same attempt")
    parser.add_argument("--reclaim", action="store_true",
                        help="close an ACTIVE lease only when its process is gone")
    args = parser.parse_args(argv)

    receipt = run_block(
        grant_path=args.grant,
        out_path=args.out,
        checkpoint_path=args.checkpoint,
        lease_path=args.lease,
        marker_path=args.marker,
        resume=args.resume,
        reclaim=args.reclaim,
    )
    print(json.dumps(receipt, indent=2))
    if receipt["state"] == "REFUSED":
        print("REFUSED: no cell ran.", file=sys.stderr)
    else:
        print("result: %s" % receipt["gate"]["verdict"], file=sys.stderr)
    return int(receipt["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
