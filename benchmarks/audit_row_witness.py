"""One definition of the published audit row and its asserted fingerprint.

Q1's ``C9_audit_row_reproduced``, Q2's ``K5_cap_only`` witness and Q3's
``X8_control_reproduces_audit`` ask the same question: does a fresh cell
reproduce the published audit row?  Each gate once carried its own field list,
its own audit lookup and its own digest call.  Q2 and Q3 briefly fingerprinted
the world-restricted ``A_W`` subset while the audit fingerprints the whole
asserted structure, so two blocks could disagree about "the same fingerprint".

The audit harness owns the digest recipe, and this module delegates to it.  It
also owns which fields a witness compares and how those fields are labelled in
a failure.  A witness gate should call :func:`compare_to_audit`; a cell that
records an asserted fingerprint should call :func:`fingerprint`.

The digest is the audit's own function,
:func:`benchmarks.acquisition_harness.asserted_fingerprint`:
``sha256("|".join("a>b" for sorted edges))``, truncated to 16 hex characters.
It covers the whole asserted pair set, never the world-restricted subset.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "presence_assertion_audit_0.14.0.json"

# C9 compares the whole audit row it can see; K5 and X8 compare the three fields
# the witness cell records.  Both lists are explicit so a new field is a
# deliberate change to every witness gate, not an accident in one.
AUDIT_ROW_FIELDS = (
    "world_edges",
    "present_world_edges",
    "asserted_world_edges",
    "asserted_fingerprint",
)
WITNESS_FIELDS = (
    "present_world_edges",
    "asserted_world_edges",
    "asserted_fingerprint",
)
LABELS = {
    "world_edges": "world edges",
    "present_world_edges": "present world edges",
    "asserted_world_edges": "asserted world edges",
    "asserted_fingerprint": "asserted fingerprint",
}


def fingerprint(pairs) -> str:
    """The audit's canonical whole-set asserted fingerprint, from the harness."""
    from benchmarks.acquisition_harness import asserted_fingerprint
    return asserted_fingerprint(pairs)


def load_rows(path: Path | str | None = None) -> list[dict]:
    body = json.loads(Path(path or AUDIT).read_text(encoding="utf-8"))
    return list(body.get("rows") or [])


def audit_row(seed: int, path: Path | str | None = None) -> dict | None:
    """The published row for ``seed``, or ``None`` when the audit has no such row."""
    return next((row for row in load_rows(path) if row.get("seed") == seed), None)


def compare(reference: dict, witness: dict, fields=WITNESS_FIELDS,
            labels: dict | None = None) -> dict:
    """Compare a witness against a reference row, field by field.

    ``labels`` defaults to the field names, which is the shape C9's details use;
    pass :data:`LABELS` for the human-readable form K5/X8 report.
    """
    labels = labels or {field: field for field in fields}
    differs = [labels[field] for field in fields
               if reference.get(field) != witness.get(field)]
    return {
        "reproduces": not differs,
        "differs": differs,
        "audit": {field: reference.get(field) for field in fields},
        "seen": {field: witness.get(field) for field in fields},
    }


def compare_to_audit(witness: dict, seed: int | None = None, *,
                     path: Path | str | None = None, fields=WITNESS_FIELDS,
                     labels: dict | None = None) -> dict:
    """Compare ``witness`` with the audit row for ``seed`` (default: its own seed)."""
    seed = witness.get("seed") if seed is None else seed
    reference = audit_row(seed, path)
    if reference is None:
        return {
            "reproduces": False,
            "differs": ["the witness seed is not in the audit"],
            "audit": None,
            "seen": {field: witness.get(field) for field in fields},
        }
    return compare(reference, witness, fields, labels)
