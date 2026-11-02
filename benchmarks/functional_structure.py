"""Scoring and provenance attribution for the functional structure study.

This module implements the measurement contract of
`docs/FUNCTIONAL-STRUCTURE-PREREGISTRATION.md` §11.2 and §11.3, plus the gate
fixtures required by §6 G6.

Scope, deliberately narrow: this is the pure scoring layer — cells, losses,
the four attribution outcomes — and nothing that touches the engine. It imports
no engine module and reads no study seed, so its gates can run before any cell
exists. Standard library only.

The cell shape is the closed protocol's `score(exclude_self=True)` adopted
verbatim: one cell per (event pair, source tag, vocabulary target), the
source-equals-target cell kept in the denominator with label zero.
"""
from __future__ import annotations

import argparse
import json
import math
from typing import Any, Callable, Mapping, Sequence

EPS = 1e-12
THRESHOLD = 0.50
RELAXED = 0.90

STATUS_WORLD = "world_attributable"
STATUS_SELF = "not_a_transfer_result"
STATUS_UNATTRIBUTED = "not_attributable"
STATUS_EMPTY = "not_evaluable"

STATUSES = (STATUS_WORLD, STATUS_SELF, STATUS_UNATTRIBUTED, STATUS_EMPTY)

Cell = dict[str, Any]


def clamp(p: float) -> float:
    return min(1.0 - EPS, max(EPS, float(p)))


def cell_loss(y: int, p: float) -> float:
    p = clamp(p)
    return -(y * math.log(p) + (1 - y) * math.log1p(-p))


def cells(prob: Callable[[str, str], float],
          ctx: Sequence[Sequence[str]],
          obs: Sequence[Sequence[str]],
          vocab: Sequence[str] | set[str],
          exclude_self: bool = True) -> list[Cell]:
    """One cell per (event pair, source tag, vocabulary target).

    `exclude_self` reproduces the house shape: the target-equals-source cell is
    kept, with its label forced to zero. It is never dropped from the
    denominator.
    """
    if len(ctx) != len(obs):
        raise ValueError("ctx and obs must be the same length")
    targets = sorted(vocab)
    out: list[Cell] = []
    for i, (c, o) in enumerate(zip(ctx, obs)):
        truth = set(o) & set(targets)
        for a in c:
            for b in targets:
                y = 1 if (b in truth and (not exclude_self or b != a)) else 0
                out.append({"pair": i, "source": a, "target": b,
                            "y": y, "p": clamp(prob(a, b))})
    return out


def mean_loss(cell_list: Sequence[Cell]) -> tuple[float, int]:
    if not cell_list:
        return float("nan"), 0
    total = sum(cell_loss(c["y"], c["p"]) for c in cell_list)
    return total / len(cell_list), len(cell_list)


def score(prob, ctx, obs, vocab, exclude_self: bool = True) -> dict[str, Any]:
    """The endpoint: mean per-cell log-loss and its denominator."""
    mean, n = mean_loss(cells(prob, ctx, obs, vocab, exclude_self=exclude_self))
    return {"log_loss": mean, "cells": n}


def classify_pair(world: int, own: int) -> str:
    """World-majority only when the world count strictly exceeds the self count.

    A tie therefore counts against a transfer claim, as §11.3 fixes.
    """
    if world + own <= 0:
        return "unattributed"
    return "world" if world > own else "self"


def attribute(base: Sequence[Cell], org: Sequence[Cell],
              provenance: Mapping[tuple[str, str], tuple[int, int]],
              threshold: float = THRESHOLD) -> dict[str, Any]:
    """The §11.3 share, over realised held-out transitions only.

    `base` and `org` are aligned cell lists from the same event pairs. Cells with
    `y = 0` are excluded from the attribution — they remain in the score — because
    the question is what carried the improvement on transitions that actually
    occurred.
    """
    if len(base) != len(org):
        raise ValueError("cell lists must be aligned")
    margin = {"world": 0.0, "self": 0.0, "unattributed": 0.0}
    count = {"world": 0, "self": 0, "unattributed": 0}
    positive = 0.0
    for b, o in zip(base, org):
        if (b["pair"], b["source"], b["target"]) != (o["pair"], o["source"], o["target"]):
            raise ValueError("cell lists are not aligned")
        if b["y"] != 1:
            continue
        delta = cell_loss(b["y"], b["p"]) - cell_loss(o["y"], o["p"])
        if delta <= 0:
            continue
        world, own = provenance.get((b["source"], b["target"]), (0, 0))
        group = classify_pair(world, own)
        margin[group] += delta
        count[group] += 1
        positive += delta

    if positive <= 0:
        return {"status": STATUS_EMPTY, "withheld": None, "threshold": threshold,
                "margin_positive": 0.0, "share_world": None, "share_self": None,
                "share_unattributed": None, "counts": count}

    share = {g: margin[g] / positive for g in margin}
    if share["self"] >= threshold:
        status, withheld = STATUS_SELF, True
    elif share["unattributed"] >= threshold:
        status, withheld = STATUS_UNATTRIBUTED, True
    else:
        status, withheld = STATUS_WORLD, False
    return {"status": status, "withheld": withheld, "threshold": threshold,
            "margin_positive": positive, "share_world": share["world"],
            "share_self": share["self"], "share_unattributed": share["unattributed"],
            "counts": count}


# ---------------------------------------------------------------------------
# G6 fixtures — synthetic, no engine, no study seed.
# ---------------------------------------------------------------------------

def _fixture(n_world: int = 0, n_self: int = 0, n_unattributed: int = 0,
             n_losing_self: int = 0) -> tuple[list[Cell], list[Cell], dict]:
    """Cells with identical positive margin per winning cell.

    Baseline is always 0.5; a winning Organica cell is 0.9, a losing one 0.4, so
    the share is a ratio of counts and the boundary is exact.
    """
    base: list[Cell] = []
    org: list[Cell] = []
    prov: dict[tuple[str, str], tuple[int, int]] = {}
    i = 0
    groups = (("world", n_world, 0.9), ("self", n_self, 0.9),
              ("unattributed", n_unattributed, 0.9), ("self", n_losing_self, 0.4))
    for group, n, p_org in groups:
        for _ in range(n):
            s, t = f"src{i:05d}", f"tgt{i:05d}"
            base.append({"pair": i, "source": s, "target": t, "y": 1, "p": 0.5})
            org.append({"pair": i, "source": s, "target": t, "y": 1, "p": p_org})
            prov[(s, t)] = {"world": (3, 0), "self": (0, 3),
                            "unattributed": (0, 0)}[group]
            i += 1
    return base, org, prov


def gate_fixtures() -> list[dict[str, Any]]:
    """G6: every outcome of the attribution rule, and its boundary.

    Raises AssertionError on any mismatch, so a gate run is an audit and not a
    report. No engine is started and no study seed is read.
    """
    report: list[dict[str, Any]] = []
    cases = {
        "world_passes": (_fixture(n_world=3, n_losing_self=2), STATUS_WORLD, False),
        "self_withholds": (_fixture(n_world=2, n_self=3), STATUS_SELF, True),
        "unattributed_withholds": (_fixture(n_world=1, n_unattributed=3),
                                   STATUS_UNATTRIBUTED, True),
        "empty_is_not_evaluable": (_fixture(n_losing_self=4), STATUS_EMPTY, None),
        "boundary_fires_at_half": (_fixture(n_world=5, n_self=5), STATUS_SELF, True),
        "just_below_boundary_passes": (_fixture(n_world=5001, n_self=4999),
                                       STATUS_WORLD, False),
    }
    for name, ((base, org, prov), want_status, want_withheld) in cases.items():
        got = attribute(base, org, prov)
        assert got["status"] == want_status, f"{name}: {got['status']} != {want_status}"
        assert got["withheld"] is want_withheld, f"{name}: withheld {got['withheld']}"
        report.append({"case": name, "status": got["status"],
                       "withheld": got["withheld"],
                       "share_self": got["share_self"],
                       "share_unattributed": got["share_unattributed"]})

    # The fixture must carry the signal: relaxing the threshold to 0.90 has to stop
    # the 0.60 self-majority case from withholding.
    base, org, prov = _fixture(n_world=2, n_self=3)
    relaxed = attribute(base, org, prov, threshold=RELAXED)
    assert relaxed["status"] == STATUS_WORLD, relaxed
    assert relaxed["withheld"] is False, relaxed
    report.append({"case": "relaxed_threshold_stops_withholding",
                   "status": relaxed["status"], "withheld": relaxed["withheld"],
                   "share_self": relaxed["share_self"],
                   "share_unattributed": relaxed["share_unattributed"]})

    assert classify_pair(2, 2) == "self", "a tie must count against the claim"
    assert classify_pair(3, 1) == "world"
    assert classify_pair(0, 0) == "unattributed"
    report.append({"case": "tie_is_self_majority", "status": "classified",
                   "withheld": None, "share_self": None,
                   "share_unattributed": None})

    seen = {r["status"] for r in report}
    for status in (STATUS_WORLD, STATUS_SELF, STATUS_UNATTRIBUTED, STATUS_EMPTY):
        assert status in seen, f"gate never produced {status}"
    return report


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gates", action="store_true", help="run the G6 fixtures")
    args = ap.parse_args(argv)
    if not args.gates:
        ap.error("nothing to do; pass --gates")
    print(json.dumps(gate_fixtures(), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
