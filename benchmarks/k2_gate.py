"""The frozen K2 gate: preflight refusals, void gates and validity stops.

This module owns the build contract, not the run.  It opens no database,
runs no sleep cycle and writes no result.  Its job is to make the K2 block
refuse before a cell when the build or the registration is not the one the
owner froze, and to refuse to read a criterion when the result is void or
incomplete.

The exit states are the K2 passport's:

* ``GateRefusal`` -> ``REFUSED``, exit 2, no result;
* ``validate_result`` returning ``VOID`` -> exit 3, result written but no
  criterion read;
* ``validate_result`` returning ``INCONCLUSIVE`` -> exit 0, result written,
  no criterion read.

The check names are those of the consolidated refusal matrix:
G-01..G-09, V-01..V-04 and A-01..A-03.
"""
from __future__ import annotations

import ast
import functools
import hashlib
import inspect
import json
import os
import textwrap
from pathlib import Path
from typing import Callable, Iterable

from benchmarks import engine_pin
from benchmarks.k2_pre_switch_retention import (
    ASSOCIATION_TYPES,
    BOUNDARY_CYCLE,
    PENALTY,
    K2PreSwitchRetentionService,
    empty_evidence,
)
from organica.sleep import SleepService

ROOT = Path(__file__).resolve().parent.parent
K1_FAMILY = "K1"
K2_FAMILY = "K2"
EXPECTED_FAMILIES = (K1_FAMILY, K2_FAMILY)
K2_SEEDS = tuple(range(20261023, 20261033))
K1_SEEDS = K2_SEEDS
K2_CYCLES = 300
K2_BOUNDARY_CYCLE = BOUNDARY_CYCLE
K2_PENALTY = PENALTY
K2_TARGET_TYPES = ASSOCIATION_TYPES

FROZEN_RESULT = ROOT / "docs" / "phase_k_results.json"
FROZEN_RESULT_SHA256 = (
    "cab5891fcc861c0ecf353f4b781e217928f160704932dae53843faf9a05a14ac")
DEFAULT_RESULT = ROOT / "docs" / "phase_k_k2_results.json"
DEFAULT_LEASE = ROOT / "docs" / "phase_k_k2_block_lease.json"
DEFAULT_MARKER = ROOT / "docs" / "phase_k_k2_attempt.json"
DEFAULT_CHECKPOINT = ROOT / "docs" / "phase_k_k2_results.ndjson"

BASELINE_GAP = -0.5735
K1_PRE_VALUE = -0.343658
PASS_IMPROVEMENT = 0.10
FAIL_IMPROVEMENT = 0.05
K1_MAX_ABS_CHANGE = 0.05

ASSOCIATION_EVIDENCE_FIELDS = (
    "boundary_cycle",
    "association_types",
    "cycles_observed",
    "pre_boundary_key_count",
    "post_boundary_target_count",
    "demoted_count",
    "pre_boundary_demotions",
    "priority_before_sum",
    "priority_after_sum",
    "mean_priority_delta",
    "min_priority_delta",
    "max_priority_delta",
    "target_type_counts",
    "sample_keys",
)

FORBIDDEN_ATTEMPT_NAMES = ("attempt.log", "gate.json", "audit.json")
PER_SEED_LEASE_GLOB = "phase_k_k2_seed_*lease*.json"


class GateRefusal(Exception):
    """A preflight refusal.  Carries the evidence the matrix requires."""

    def __init__(self, code: str, message: str, **evidence):
        super().__init__(message)
        self.code = code
        self.message = message
        self.evidence = evidence

    def receipt(self, **extra) -> dict:
        body = {
            "state": "REFUSED",
            "stage": "preflight",
            "exit_code": 2,
            "refusal_code": self.code,
            "message": self.message,
            "result_written": False,
            "cells_started": 0,
            "cells_completed": 0,
            "seed_records_written": 0,
            "engine_calls": 0,
            "checks": dict(self.evidence),
        }
        body.update(extra)
        return body


def _refuse(code: str, message: str, **evidence):
    raise GateRefusal(code, message, **evidence)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tree_digest(files: dict[str, str]) -> str:
    """A stable digest over the pinned per-file hashes."""
    return _sha256_text(json.dumps(files, sort_keys=True, separators=(",", ":")))


def expected_engine_tree() -> str:
    return tree_digest(engine_pin.load_pin()["files"])


def observed_engine_tree() -> str:
    return tree_digest(engine_pin.hashes())


def stable_bootstrap_seed(family: str = K2_FAMILY) -> int:
    """Registration-derived, process-independent.  Never Python's hash()."""
    digest = hashlib.sha256(
        ("CONSTRAINT-K2-1:%s" % family).encode("utf-8")).hexdigest()
    return 20261023 + int(digest[:8], 16) % 1000


def class_hash(cls: type) -> str:
    return _sha256_text(inspect.getsource(cls))


def _factory_class(factory) -> type | None:
    if inspect.isclass(factory):
        return factory
    if isinstance(factory, functools.partial):
        return factory.func if inspect.isclass(factory.func) else None
    return None


def _factory_boundary(factory) -> object:
    if isinstance(factory, functools.partial):
        return factory.keywords.get("boundary_cycle", "<missing>")
    return "<missing>"


def _method_names(cls: type) -> list[str]:
    return sorted(
        name for name, value in vars(cls).items()
        if inspect.isfunction(value) and not name.startswith("__")
    )


def signature_evidence(cls: type) -> dict:
    """The proof that the class changes exactly one engine behaviour."""
    engine_names = {
        name for name in dir(SleepService)
        if not name.startswith("__") and inspect.isfunction(getattr(SleepService, name))
    }
    overrides = sorted(
        name for name in engine_names
        if name in vars(cls) and name != "__init__"
    )
    engine_methods = _method_names(cls)
    extra = [name for name in engine_methods
             if name not in {"_natural_selection"}]
    signature_expected = str(inspect.signature(
        SleepService._natural_selection).replace(
            return_annotation=inspect.Signature.empty))
    signature_observed = str(inspect.signature(
        cls._natural_selection).replace(
            return_annotation=inspect.Signature.empty))
    source = textwrap.dedent(inspect.getsource(getattr(cls, "_natural_selection")))
    tree = ast.parse(source)
    super_calls = 0
    forbidden_calls: list[str] = []
    constant_writes: list[str] = []
    forbidden = {
        "_store_single_candidate", "_reinforce_current", "_retired_record",
        "store", "memory.store",
    }
    constants = {
        "MAX_HYPOTHESES", "DEATH_THRESHOLD", "DEATH_FACTOR",
        "HYPOTHESIS_RETENTION", "MAX_PREDICTIONS",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr == "_natural_selection" and isinstance(node.func.value, ast.Call):
                if isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == "super":
                    super_calls += 1
            if attr in forbidden:
                forbidden_calls.append(attr)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute) and target.attr in constants:
                    constant_writes.append(target.attr)
    return {
        "overrides": overrides,
        "class_local_methods": engine_methods,
        "extra_methods": extra,
        "signature_expected": signature_expected,
        "signature_observed": signature_observed,
        "super_calls": super_calls,
        "forbidden_calls": sorted(set(forbidden_calls)),
        "constant_writes": sorted(set(constant_writes)),
        "class_hash": class_hash(cls),
    }


K1_FIXTURE_HASH_FIELDS = (
    "fixture_sha256", "shipped_fixture_sha256", "noop_fixture_sha256",
)


K1_SELECTION_DETAILS = ("returned_digest", "argument_set")


def k1_fixture_selection_detail(evidence: dict) -> list[str]:
    """Which part of the one selection-digest check failed, if any.

    Each recorded call returns the digest of its own effective argument set
    (defaults included), so the returned selection digest already contains the
    argument digest: comparing the two returned digests compares the argument
    sets as well, and the argument set cannot fail while the selection digest
    agrees.  It is therefore a named detail of the one check, never a second
    problem code that could not fire on its own.
    """
    detail: list[str] = []
    shipped = evidence.get("shipped_hash")
    noop = evidence.get("noop_hash")
    if not (isinstance(shipped, str) and shipped and shipped == noop):
        detail.append("returned_digest")
    shipped_arguments = evidence.get("shipped_arguments_sha256")
    noop_arguments = evidence.get("noop_arguments_sha256")
    if not (isinstance(shipped_arguments, str) and shipped_arguments
            and shipped_arguments == noop_arguments):
        detail.append("argument_set")
    return detail


def k1_fixture_hash_problems(evidence: dict) -> list[str]:
    """Why the K1 fixture is not the comparison of the two paths it claims.

    A fixture passes only when both paths saw the same candidates, were handed
    the identical candidate object, returned the same selection digest, left no
    manipulation record on the shipped path, and carried candidates the
    boundary *would* demote.  The last one stops a vacuous fixture from
    passing: a fixture with nothing to demote distinguishes nothing.  The
    selection digest is the one check on what the two paths returned; it
    carries each call's effective argument digest, so the argument set is a
    detail of that check rather than a condition of its own.
    """
    found: list[str] = []
    digests = [evidence.get(name) for name in K1_FIXTURE_HASH_FIELDS]
    if not all(isinstance(value, str) and value for value in digests):
        found.append("missing_fixture_hash")
    elif len(set(digests)) != 1:
        found.append("different_fixtures")
    if evidence.get("forwarded_identical") is not True:
        found.append("candidate_identity")
    if k1_fixture_selection_detail(evidence):
        found.append("selection_digest")
    if evidence.get("shipped_manipulation") is not None:
        found.append("shipped_path_manipulated")
    counterfactual = evidence.get("counterfactual_demoted_count")
    if (not isinstance(counterfactual, int) or isinstance(counterfactual, bool)
            or counterfactual <= 0):
        found.append("fixture_not_discriminating")
    return found


def k1_fixture_manipulation_problems(evidence: dict) -> list[str]:
    """The fields in which the no-op's manipulation record is not empty."""
    observed = evidence.get("noop_manipulation")
    expected = empty_evidence(None)
    if not isinstance(observed, dict):
        return ["noop_manipulation"]
    return sorted(
        name for name in set(expected) | set(observed)
        if observed.get(name) != expected.get(name))


def signature_problems(cls: type) -> list[tuple[str, dict]]:
    evidence = signature_evidence(cls)
    problems: list[tuple[str, dict]] = []
    if evidence["overrides"] != ["_natural_selection"]:
        problems.append(("K2_SIGNATURE_MULTIPLE_OVERRIDES", evidence))
    if evidence["extra_methods"]:
        problems.append(("K2_SIGNATURE_EXTRA_METHOD", evidence))
    if evidence["signature_expected"] != evidence["signature_observed"]:
        problems.append(("K2_SIGNATURE_MISMATCH", evidence))
    if evidence["super_calls"] != 1:
        problems.append(("K2_SIGNATURE_NO_SUPER", evidence))
    if evidence["forbidden_calls"]:
        problems.append(("K2_SIGNATURE_WRITE_PATH", evidence))
    if evidence["constant_writes"]:
        problems.append(("K2_ENGINE_CONSTANT_CHANGED", evidence))
    return problems


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def _safe_resolve(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path


def _check_output(
    out_path: Path, *, allowed_outputs: Iterable[Path], resume: bool,
) -> dict:
    if _safe_resolve(out_path) == _safe_resolve(FROZEN_RESULT):
        _refuse(
            "OUTPUT_IS_FROZEN",
            "the K2 result may not use the frozen Phase K artifact",
            output_path=str(out_path),
            frozen_sha256=FROZEN_RESULT_SHA256,
            output_before_sha256=FROZEN_RESULT_SHA256,
            output_after_sha256=FROZEN_RESULT_SHA256,
            result_written=False,
            cells_started=0,
            lease={"state": "NOT_ACQUIRED"},
        )
    allowed = {_safe_resolve(Path(path)) for path in allowed_outputs}
    if _safe_resolve(out_path) not in allowed:
        _refuse(
            "OUTPUT_PATH_NOT_REGISTERED",
            "the output path is outside the K2 allowlist",
            output_path=str(out_path),
            allowed_outputs=sorted(str(path) for path in allowed_outputs),
            result_written=False,
            cells_started=0,
        )
    if out_path.is_symlink():
        _refuse(
            "OUTPUT_NOT_REGULAR",
            "the output path is a symlink",
            output_kind="symlink",
            output_path=str(out_path),
            overwrite_attempted=False,
            result_written=False,
            cells_started=0,
        )
    if out_path.exists() and not out_path.is_file():
        _refuse(
            "OUTPUT_NOT_REGULAR",
            "the output path is not a regular file",
            output_kind="non-regular",
            output_path=str(out_path),
            overwrite_attempted=False,
            result_written=False,
            cells_started=0,
        )
    if out_path.exists() and not resume:
        before = out_path.read_bytes()
        _refuse(
            "OUTPUT_EXISTS",
            "a fresh K2 attempt may not overwrite an existing result",
            output_kind="file",
            output_path=str(out_path),
            output_before_sha256=hashlib.sha256(before).hexdigest(),
            output_after_sha256=hashlib.sha256(before).hexdigest(),
            overwrite_attempted=False,
            result_written=False,
            cells_started=0,
        )
    return {
        "output_path": str(out_path),
        "output_exists": out_path.exists(),
        "resume": bool(resume),
    }


def _check_lease_and_marker(
    lease_path: Path, marker_path: Path, checkpoint_path: Path,
    *, resume: bool, extra_paths: Iterable[Path],
) -> dict:
    for path in extra_paths:
        path = Path(path)
        if path.exists():
            _refuse(
                "DUPLICATE_ATTEMPT_RECORD",
                "a second attempt/audit record exists",
                unexpected_paths=[str(path)],
                marker_count=2,
                allowed_marker_count=1,
                result_written=False,
                cells_started=0,
            )
    parent = marker_path.parent
    if parent.exists():
        for name in FORBIDDEN_ATTEMPT_NAMES:
            path = parent / name
            if path.exists():
                _refuse(
                    "DUPLICATE_AUDIT_LAYER",
                    "a second audit/log layer exists",
                    unexpected_paths=[str(path)],
                    audit_layers=["attempt", "result"],
                    result_written=False,
                    cells_started=0,
                )
        markers = sorted(parent.glob("phase_k_k2_attempt*.json"))
        if len(markers) > 1:
            _refuse(
                "DUPLICATE_ATTEMPT_RECORD",
                "more than one K2 attempt marker exists",
                unexpected_paths=[str(p) for p in markers],
                marker_count=len(markers),
                allowed_marker_count=1,
                result_written=False,
                cells_started=0,
            )
        per_seed = sorted(parent.glob(PER_SEED_LEASE_GLOB))
        if per_seed:
            _refuse(
                "K2_PER_SEED_LEASE_FORBIDDEN",
                "one block lease covers K1 and K2; per-seed leases are forbidden",
                per_seed_leases=[str(p) for p in per_seed],
                lease_count=1,
                result_written=False,
                cells_started=0,
            )

    marker = _read_json(marker_path) if marker_path.exists() else {}
    marker_state = marker.get("state")
    if marker_state and not resume:
        _refuse(
            "K2_ATTEMPT_ALREADY_COMPLETED",
            "a K2 attempt marker already exists",
            marker_state=marker_state,
            attempt_id=marker.get("attempt_id"),
            marker_unchanged=True,
            result_written=False,
            cells_started=0,
        )

    lease = _read_json(lease_path) if lease_path.exists() else {}
    lease_state = lease.get("state")
    if lease_state == "ACTIVE":
        _refuse(
            "K2_BLOCK_LEASE_HELD",
            "the K2 block lease is held by another attempt",
            lease_path=str(lease_path),
            lease_state="ACTIVE",
            lease_owner=lease.get("owner"),
            attempt_id_current=lease.get("attempt_id"),
            marker_unchanged=True,
            result_written=False,
            cells_started=0,
        )
    if lease_path.exists() and not resume:
        _refuse(
            "K2_BLOCK_LEASE_HELD",
            "a closed K2 lease already records a block attempt",
            lease_path=str(lease_path),
            lease_state=lease_state or "CLOSED",
            lease_owner=lease.get("owner"),
            marker_unchanged=True,
            result_written=False,
            cells_started=0,
        )

    if checkpoint_path.exists() and not resume:
        _refuse(
            "CHECKPOINT_EXISTS",
            "a fresh K2 attempt may not append to an existing checkpoint",
            checkpoint_path=str(checkpoint_path),
            result_written=False,
            cells_started=0,
        )
    return {
        "lease_path": str(lease_path),
        "lease_state": lease_state or "NOT_ACQUIRED",
        "marker_path": str(marker_path),
        "marker_state": marker_state,
        "checkpoint_path": str(checkpoint_path),
    }


def _check_resume(out_path: Path, checkpoint_path: Path, *,
                  expected_attempt_id: str | None, arm_signature: str | None,
                  seeds: tuple[int, ...]) -> dict:
    if not out_path.exists():
        return {"records_loaded": 0}
    prior = _read_json(out_path)
    existing_attempt = prior.get("attempt_id")
    existing_arm = prior.get("arm_signature") or (
        (prior.get("arm") or {}).get("signature"))
    mismatched = []
    if expected_attempt_id and existing_attempt and existing_attempt != expected_attempt_id:
        mismatched.append("attempt_id")
    if arm_signature and existing_arm and existing_arm != arm_signature:
        mismatched.append("arm_signature")
    prior_seeds = prior.get("protocol", {}).get("seeds")
    if prior_seeds is not None and list(prior_seeds) != list(seeds):
        mismatched.append("seeds")
    if mismatched:
        _refuse(
            "RESUME_ARM_MISMATCH",
            "the existing K2 result belongs to another arm or seed block",
            attempt_id_existing=existing_attempt,
            attempt_id_current=expected_attempt_id,
            mismatched_fields=mismatched,
            records_loaded=0,
            result_written=False,
            cells_started=0,
        )
    if checkpoint_path.exists():
        foreign_families = []
        foreign_attempts = []
        records = 0
        for line in checkpoint_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            records += 1
            if row.get("attempt_id") and expected_attempt_id and row["attempt_id"] != expected_attempt_id:
                foreign_attempts.append(row["attempt_id"])
            if row.get("family") and row["family"] not in EXPECTED_FAMILIES:
                foreign_families.append(row["family"])
        if foreign_attempts or foreign_families:
            _refuse(
                "CHECKPOINT_ATTEMPT_MISMATCH",
                "the checkpoint contains rows from another attempt or family",
                foreign_attempt_ids=sorted(set(foreign_attempts)),
                foreign_families=sorted(set(foreign_families)),
                records_loaded=0,
                result_written=False,
                cells_started=0,
            )
        return {"records_loaded": records}
    return {"records_loaded": 0}


def _check_arms(
    primary_factory, k1_factory, *,
    treatment_cls: type, association_age_source: str,
    k1_noop_evidence: dict | None,
) -> dict:
    if primary_factory is None:
        _refuse(
            "K2_PRIMARY_ARM_MISSING",
            "K2 has no primary treatment arm",
            primary_factory=None,
            resolved_class=None,
            boundary_cycle=None,
            expected_boundary_cycle=K2_BOUNDARY_CYCLE,
            result_written=False,
            cells_started=0,
        )
    primary_cls = _factory_class(primary_factory)
    if primary_cls is None or not issubclass(primary_cls, treatment_cls):
        _refuse(
            "K2_PRIMARY_ARM_NOT_TREATMENT",
            "the K2 primary arm is not the registered treatment class",
            resolved_class=getattr(primary_cls, "__name__", None),
            boundary_cycle=_factory_boundary(primary_factory),
            expected_boundary_cycle=K2_BOUNDARY_CYCLE,
            primary_arm_label=getattr(primary_cls, "__name__", None),
            result_written=False,
            cells_started=0,
        )
    keywords = getattr(primary_factory, "keywords", {}) if isinstance(
        primary_factory, functools.partial) else {}
    observed_params = {
        "boundary_cycle": _factory_boundary(primary_factory),
        "penalty": keywords.get("penalty", K2_PENALTY),
        "types": list(keywords.get("association_types", K2_TARGET_TYPES)),
    }
    expected_params = {"boundary_cycle": K2_BOUNDARY_CYCLE,
                       "penalty": K2_PENALTY,
                       "types": list(K2_TARGET_TYPES)}
    if observed_params != expected_params:
        _refuse(
            "ARM_PARAMETER_DRIFT",
            "the K2 primary parameters are not the registered values",
            expected_params=expected_params,
            observed_params=observed_params,
            result_written=False,
            cells_started=0,
        )
    if k1_factory is None:
        _refuse(
            "K1_PRIMARY_ARM_MISSING",
            "K2 has no K1 no-op control arm",
            primary_factory=None,
            resolved_class=None,
            boundary_cycle=None,
            expected_boundary_cycle=None,
            result_written=False,
            cells_started=0,
        )
    k1_cls = _factory_class(k1_factory)
    if k1_cls is None or not issubclass(k1_cls, treatment_cls):
        _refuse(
            "K1_PRIMARY_ARM_NOT_NOOP",
            "the K1 primary arm is not the registered no-op class",
            resolved_class=getattr(k1_cls, "__name__", None),
            boundary_cycle=_factory_boundary(k1_factory),
            expected_boundary_cycle=None,
            result_written=False,
            cells_started=0,
        )
    if _factory_boundary(k1_factory) is not None:
        _refuse(
            "K1_NOOP_BOUNDARY_NOT_NONE",
            "the K1 control must use boundary_cycle=None",
            boundary_cycle=_factory_boundary(k1_factory),
            expected_boundary_cycle=None,
            result_written=False,
            cells_started=0,
        )
    if association_age_source != "treatment_state":
        _refuse(
            "PRE_BOUNDARY_AGE_UNAVAILABLE",
            "pre-boundary age must come from treatment state, not an engine change",
            association_age_source=association_age_source,
            required_engine_change=True,
            engine_files_modified=[],
            cells_started=0,
        )
    if k1_noop_evidence is None:
        _refuse(
            "K1_NOOP_FIXTURE_MISSING",
            "the K2 block requires the shipped-vs-no-op K1 fixture",
            primary_factory=getattr(_factory_class(primary_factory),
                                    "__name__", None),
            k1_factory=getattr(_factory_class(k1_factory), "__name__", None),
            fixture_required=True,
            result_written=False,
            cells_started=0,
        )
    hash_problems = k1_fixture_hash_problems(k1_noop_evidence)
    if hash_problems:
        _refuse(
            "K1_NOOP_FIXTURE_MISMATCH",
            "the K1 no-op fixture is not a comparison of the shipped path",
            fixture_id=k1_noop_evidence.get("fixture_id"),
            fixture_seed=k1_noop_evidence.get("fixture_seed"),
            fixture_problems=hash_problems,
            fixture_sha256=k1_noop_evidence.get("fixture_sha256"),
            shipped_fixture_hash=k1_noop_evidence.get("shipped_fixture_sha256"),
            noop_fixture_hash=k1_noop_evidence.get("noop_fixture_sha256"),
            shipped_hash=k1_noop_evidence.get("shipped_hash"),
            noop_hash=k1_noop_evidence.get("noop_hash"),
            selection_detail=k1_fixture_selection_detail(k1_noop_evidence),
            shipped_arguments_sha256=k1_noop_evidence.get(
                "shipped_arguments_sha256"),
            noop_arguments_sha256=k1_noop_evidence.get(
                "noop_arguments_sha256"),
            counterfactual_demoted_count=k1_noop_evidence.get(
                "counterfactual_demoted_count"),
            k1_expected_pre_value=K1_PRE_VALUE,
            result_written=False,
            cells_started=0,
        )
    manipulation_problems = k1_fixture_manipulation_problems(k1_noop_evidence)
    if manipulation_problems:
        _refuse(
            "K1_NOOP_MANIPULATION_MISMATCH",
            "the K1 no-op arm recorded a manipulation it must not have",
            fixture_id=k1_noop_evidence.get("fixture_id"),
            differing_fields=manipulation_problems,
            observed_manipulation=k1_noop_evidence.get("noop_manipulation"),
            expected_manipulation=empty_evidence(None),
            result_written=False,
            cells_started=0,
        )
    return {
        "primary_class": primary_cls.__name__,
        "primary_boundary_cycle": _factory_boundary(primary_factory),
        "k1_class": k1_cls.__name__,
        "k1_boundary_cycle": _factory_boundary(k1_factory),
        "association_age_source": association_age_source,
    }


def preflight(
    *,
    families: Iterable[str],
    seeds: Iterable[int],
    scale: int = 1,
    smoke: bool = False,
    out_path: Path | str | None = None,
    checkpoint_path: Path | str | None = None,
    lease_path: Path | str | None = None,
    marker_path: Path | str | None = None,
    primary_factory=None,
    k1_factory=None,
    treatment_cls: type = K2PreSwitchRetentionService,
    resume: bool = False,
    env: dict | None = None,
    engine_tree_sha256: str | None = None,
    bootstrap_seed: int | None = None,
    baseline_gap: float = BASELINE_GAP,
    k1_pre_value: float = K1_PRE_VALUE,
    association_age_source: str = "treatment_state",
    allowed_outputs: Iterable[Path | str] | None = None,
    extra_paths: Iterable[Path | str] = (),
    k1_noop_evidence: dict | None = None,
    attempt_id: str | None = None,
    arm_signature: str | None = None,
) -> dict:
    """Run every preflight check.  Raise ``GateRefusal`` on the first failure.

    This function has no side effects: it does not acquire the lease, write the
    marker, open a database or start a cell.  The caller acquires the lease only
    after this returns.
    """
    family_list = list(families)
    seed_list = list(seeds)
    out_path = Path(out_path) if out_path is not None else DEFAULT_RESULT
    allowed = tuple(Path(path) for path in (
        allowed_outputs if allowed_outputs is not None else (out_path,)))
    checkpoint_path = Path(checkpoint_path) if checkpoint_path is not None else (
        out_path.with_suffix(".ndjson"))
    lease_path = Path(lease_path) if lease_path is not None else (
        out_path.parent / "phase_k_k2_block_lease.json")
    marker_path = Path(marker_path) if marker_path is not None else (
        out_path.parent / "phase_k_k2_attempt.json")

    output = _check_output(out_path, allowed_outputs=allowed, resume=resume)

    expected_families = list(EXPECTED_FAMILIES)
    if sorted(family_list) != sorted(expected_families):
        _refuse(
            "FAMILY_SET_MISMATCH",
            "the K2 block must contain exactly K1 and K2",
            expected_families=expected_families,
            observed_families=family_list,
            missing=sorted(set(expected_families) - set(family_list)),
            extra=sorted(set(family_list) - set(expected_families)),
            result_written=False,
            cells_started=0,
        )

    expected_seeds = list(K2_SEEDS)
    if seed_list != expected_seeds:
        _refuse(
            "SEED_BLOCK_MISMATCH",
            "the K2 block is not the registered ten seeds",
            expected_seeds=expected_seeds,
            observed_seeds=seed_list,
            missing=[s for s in expected_seeds if s not in seed_list],
            extra=[s for s in seed_list if s not in expected_seeds],
            duplicates=sorted({s for s in seed_list if seed_list.count(s) > 1}),
            order_ok=seed_list == sorted(seed_list),
            result_written=False,
            cells_started=0,
        )

    if smoke:
        _refuse(
            "SMOKE_NOT_A_JUDGED_CELL",
            "a smoke run is not a K2 judged cell",
            smoke=True,
            scale=scale,
            switch_cycle=K2_BOUNDARY_CYCLE // max(scale, 1),
            expected_switch_cycle=K2_BOUNDARY_CYCLE,
            result_written=False,
            cells_started=0,
        )
    if scale != 1:
        _refuse(
            "JUDGED_RUN_REQUIRES_SCALE_1",
            "the K2 judged block requires cycle scale 1",
            scale=scale,
            switch_cycle=K2_BOUNDARY_CYCLE // max(scale, 1),
            expected_switch_cycle=K2_BOUNDARY_CYCLE,
            expected_cycles=K2_CYCLES,
            result_written=False,
            cells_started=0,
        )

    environment = dict(os.environ if env is None else env)
    if environment.get("PYTHONHASHSEED") != "0":
        _refuse(
            "PYTHONHASHSEED_NOT_ZERO",
            "PYTHONHASHSEED must be exactly 0",
            python_hash_seed=environment.get("PYTHONHASHSEED"),
            expected_python_hash_seed="0",
            result_written=False,
            cells_started=0,
        )
    expected_bootstrap = stable_bootstrap_seed(K2_FAMILY)
    if bootstrap_seed is not None and bootstrap_seed != expected_bootstrap:
        _refuse(
            "BOOTSTRAP_SEED_UNSTABLE",
            "the bootstrap seed is not the registration-derived value",
            bootstrap_seed=bootstrap_seed,
            expected_bootstrap_seed=expected_bootstrap,
            stable=False,
            result_written=False,
            cells_started=0,
        )

    expected_engine = expected_engine_tree()
    observed_engine = engine_tree_sha256 or observed_engine_tree()
    if observed_engine != expected_engine:
        _refuse(
            "ENGINE_PIN_MISMATCH",
            "the engine tree is not the pinned tree",
            expected_tree_sha256=expected_engine,
            observed_tree_sha256=observed_engine,
            changed_files=[],
            result_written=False,
            cells_started=0,
        )

    if baseline_gap != BASELINE_GAP:
        _refuse(
            "BASELINE_PROVENANCE_DRIFT",
            "the K2 baseline gap is not the registered value",
            expected_baseline_gap=BASELINE_GAP,
            observed_baseline_gap=baseline_gap,
            result_written=False,
            cells_started=0,
        )
    if k1_pre_value != K1_PRE_VALUE:
        _refuse(
            "K1_PRE_VALUE_MISSING",
            "the K1 pre-intervention value is not the archived value",
            expected_k1_pre_value=K1_PRE_VALUE,
            observed_k1_pre_value=k1_pre_value,
            result_written=False,
            cells_started=0,
        )

    lease = _check_lease_and_marker(
        lease_path, marker_path, checkpoint_path,
        resume=resume, extra_paths=extra_paths)

    if resume:
        resume_state = _check_resume(
            out_path, checkpoint_path,
            expected_attempt_id=attempt_id,
            arm_signature=arm_signature,
            seeds=K2_SEEDS,
        )
    else:
        resume_state = {"records_loaded": 0}

    arms = _check_arms(
        primary_factory, k1_factory,
        treatment_cls=treatment_cls,
        association_age_source=association_age_source,
        k1_noop_evidence=k1_noop_evidence,
    )
    for code, evidence in signature_problems(treatment_cls):
        _refuse(code, "the K2 treatment violates its single-variable contract",
                **evidence, result_written=False, cells_started=0)

    return {
        "state": "PREFLIGHT_OK",
        "stage": "preflight",
        "exit_code": 0,
        "families": family_list,
        "seeds": seed_list,
        "scale": scale,
        "output": output,
        "lease": lease,
        "resume": resume_state,
        "arms": arms,
        "bootstrap_seed": expected_bootstrap,
        "engine_tree_sha256": expected_engine,
        "checks": {
            "output": "passed",
            "block": "passed",
            "lease": "passed",
            "arms": "passed",
            "signature": "passed",
            "bootstrap": "passed",
            "engine": "passed",
            "baseline": "passed",
        },
    }


def _records_by_cell(records: list[dict]) -> tuple[dict, list[str], list[str]]:
    cells: dict[tuple[str, int], dict] = {}
    missing: list[str] = []
    duplicates: list[str] = []
    for record in records:
        family = record.get("family")
        seed = record.get("seed")
        key = (family, seed)
        if key in cells:
            duplicates.append("%s/%s" % key)
        cells[key] = record
    for family in EXPECTED_FAMILIES:
        for seed in K2_SEEDS:
            if (family, seed) not in cells:
                missing.append("%s/%s" % (family, seed))
    return cells, missing, duplicates


def _association_problems(record: dict) -> tuple[list[str], list[str], list[str]]:
    evidence = record.get("manipulation")
    if not isinstance(evidence, dict):
        return (["manipulation"], [], [])
    missing = [name for name in ASSOCIATION_EVIDENCE_FIELDS
               if name not in evidence]
    failed: list[str] = []
    audit: list[str] = []
    demoted = evidence.get("demoted_count")
    pre = evidence.get("pre_boundary_demotions")
    before = evidence.get("priority_before_sum")
    after = evidence.get("priority_after_sum")
    counts = evidence.get("target_type_counts")
    if not isinstance(demoted, int) or demoted <= 0:
        failed.append("G3_manipulation_occurred")
    if pre != 0:
        failed.append("G4_no_pre_boundary_demotions")
    if not isinstance(counts, dict) or any(
            name not in K2_TARGET_TYPES for name in counts):
        failed.append("G5_target_scope")
    if isinstance(before, (int, float)) and isinstance(after, (int, float)):
        if after >= before:
            audit.append("A1_evidence_complete")
    if isinstance(counts, dict) and isinstance(demoted, int):
        if sum(counts.values()) != demoted:
            audit.append("A1_evidence_complete")
    return missing, failed, audit


def _k1_problems(records: list[dict]) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    failed: list[str] = []
    for record in records:
        evidence = record.get("manipulation")
        if not isinstance(evidence, dict):
            missing.append("manipulation")
            continue
        for name in ("demoted_count", "pre_boundary_demotions",
                     "priority_before_sum", "priority_after_sum"):
            if name not in evidence:
                missing.append(name)
        if evidence.get("demoted_count") != 0:
            failed.append("A2_k1_guard_computable")
        if evidence.get("pre_boundary_demotions") != 0:
            failed.append("A2_k1_guard_computable")
        if evidence.get("priority_before_sum") != evidence.get("priority_after_sum"):
            failed.append("A2_k1_guard_computable")
    return missing, failed


def decide(k2_gap: float, k1_abs_change: float) -> dict:
    """The pre-registered decision, without reading a criterion after a gate."""
    improvement = k2_gap - BASELINE_GAP
    if k1_abs_change > K1_MAX_ABS_CHANGE:
        return {"verdict": "FAIL", "improvement": improvement,
                "reason": "K1 absolute change above 0.05"}
    if improvement >= PASS_IMPROVEMENT:
        return {"verdict": "PASS", "improvement": improvement,
                "reason": "K2 improvement at least 0.10"}
    if improvement < FAIL_IMPROVEMENT:
        return {"verdict": "FAIL", "improvement": improvement,
                "reason": "K2 improvement below 0.05"}
    return {"verdict": "INCONCLUSIVE", "improvement": improvement,
            "reason": "K2 improvement between 0.05 and 0.10"}


def validate_result(result: dict) -> dict:
    """Apply the V and A gates, then the decision rule.

    A result that fails a V gate is ``VOID`` and no criterion is read.  A result
    that is merely incomplete is ``INCONCLUSIVE`` and no criterion is read.
    """
    records = result.get("records")
    if not isinstance(records, list):
        return {
            "verdict": "INCONCLUSIVE",
            "failed_gates": ["A1_evidence_complete"],
            "criteria_read": False,
            "confirmed_families": [],
            "reason": "no records",
        }
    cells, missing, duplicates = _records_by_cell(records)
    failed: list[str] = []
    audit: list[str] = []
    if missing or duplicates or len(cells) != len(EXPECTED_FAMILIES) * len(K2_SEEDS):
        failed.append("G6_cell_completeness")
    if not missing and not duplicates:
        k2_records = [cells[(K2_FAMILY, seed)] for seed in K2_SEEDS]
        k1_records = [cells[(K1_FAMILY, seed)] for seed in K2_SEEDS]
        for record in k2_records:
            missing_fields, problems, arithmetic = _association_problems(record)
            if missing_fields:
                audit.append("A1_evidence_complete")
            failed.extend(problems)
            audit.extend(arithmetic)
        missing_k1, k1_failed = _k1_problems(k1_records)
        if missing_k1:
            audit.append("A1_evidence_complete")
        audit.extend(k1_failed)

    arm = result.get("arm") or {}
    expected_class_hash = class_hash(K2PreSwitchRetentionService)
    if arm.get("class_hash") != expected_class_hash:
        audit.append("A3_provenance")
    if result.get("verdict") == "SUPPORTED":
        failed.append("G7_gate_before_criterion")

    engine = result.get("engine_tree_sha256")
    if engine is None:
        audit.append("A1_evidence_complete")
    elif engine != expected_engine_tree():
        failed.append("G8_engine_pin_stable")

    k1 = result.get("k1") or {}
    k1_abs_change = k1.get("abs_change")
    if (not isinstance(k1_abs_change, (int, float))
            or k1.get("pre_value") != K1_PRE_VALUE):
        audit.append("A2_k1_guard_computable")
    k2_gap = result.get("k2_gap")
    if not isinstance(k2_gap, (int, float)):
        audit.append("A1_evidence_complete")

    failed = sorted(set(failed))
    audit = sorted(set(audit))
    if failed:
        return {
            "verdict": "VOID",
            "failed_gates": failed,
            "criteria_read": False,
            "confirmed_families": [],
            "reason": "a V gate failed; no criterion is read",
        }
    if audit:
        return {
            "verdict": "INCONCLUSIVE",
            "failed_gates": audit,
            "criteria_read": False,
            "confirmed_families": [],
            "reason": "the result cannot be read",
        }
    decision = decide(float(k2_gap), float(k1_abs_change))
    decision.update({
        "failed_gates": [],
        "criteria_read": True,
        "confirmed_families": [K2_FAMILY] if decision["verdict"] == "PASS" else [],
    })
    return decision
