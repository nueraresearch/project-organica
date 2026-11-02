"""Descriptive robustness checks for the formation-provenance study.

Reads the per-candidate scratch records the confirmatory run wrote.  It does not
run a cell, does not touch the registered endpoint, and creates no success rule:
the registered verdict and interval are unchanged, and these tables only say how
the pooled association is distributed across seeds, across leave-one-out folds,
and across candidate evidence counts.

The registered permutation preserves seed and cycle but not `temporal_count`, so a
difference could in principle reflect transition frequency rather than provenance.
The stratum table is the descriptive answer: does the direction survive at
comparable counts.  It is not a test, and it cannot establish causality or
usefulness.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.formation_provenance_study import (  # noqa: E402
    CONFIRMATORY_SEEDS, RESULT_OUT, _difference, _rate,
)

OUT = "docs/formation_provenance_robustness.json"
DOC = "docs/FORMATION-PROVENANCE-ROBUSTNESS.md"
TAIL_AT = 21  # counts at or above this are reported as one tail row


def load_rows() -> list[dict]:
    rows: list[dict] = []
    missing: list[int] = []
    for seed in CONFIRMATORY_SEEDS:
        path = ROOT / ".scratch" / f"fp_study_{seed}.json"
        if not path.exists():
            missing.append(seed)
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for c in payload["candidates"]:
            rows.append({**c, "seed": seed})
    if missing:
        raise SystemExit(f"candidate caches missing for {missing}; stopping rather "
                         "than re-running cells to recreate them")
    return rows


def _stratum(rows: list[dict], key: str) -> dict:
    w_hit, w_n = _rate(rows, "pair_world_attributed")
    s_hit, s_n = _rate(rows, "origin_includes_self")
    return {"key": key, "world_hits": w_hit, "world_n": w_n,
            "self_hits": s_hit, "self_n": s_n,
            "world_rate": round(w_hit / w_n, 6) if w_n else None,
            "self_rate": round(s_hit / s_n, 6) if s_n else None,
            "difference": round(w_hit / w_n - s_hit / s_n, 6) if w_n and s_n else None}


def _standardise(strata: list[dict]) -> float | None:
    """Pool the within-stratum differences with each stratum's own candidate weight."""
    usable = [s for s in strata if s["difference"] is not None]
    weight = sum(s["world_n"] + s["self_n"] for s in usable)
    if not weight:
        return None
    total = sum(s["difference"] * (s["world_n"] + s["self_n"]) for s in usable)
    return round(total / weight, 6)


def analyse() -> dict:
    rows = load_rows()
    per_seed = []
    for seed in CONFIRMATORY_SEEDS:
        seed_rows = [r for r in rows if r["seed"] == seed]
        w_hit, w_n = _rate(seed_rows, "pair_world_attributed")
        s_hit, s_n = _rate(seed_rows, "origin_includes_self")
        per_seed.append({"seed": seed,
                         "world": {"hits": w_hit, "n": w_n,
                                   "rate": round(w_hit / w_n, 6) if w_n else None},
                         "self_including": {"hits": s_hit, "n": s_n,
                                            "rate": round(s_hit / s_n, 6) if s_n else None},
                         "difference": round(_difference(seed_rows), 6)})

    loo = []
    for seed in CONFIRMATORY_SEEDS:
        others = [r for r in rows if r["seed"] != seed]
        loo.append({"excluded": seed, "difference": round(_difference(others), 6)})

    counts = sorted({int(r["temporal_count"]) for r in rows})
    strata = []
    for value in counts:
        subset = [r for r in rows
                  if (int(r["temporal_count"]) >= TAIL_AT) == (value >= TAIL_AT)
                  and (value < TAIL_AT and int(r["temporal_count"]) == value
                       or value >= TAIL_AT)]
        key = f"count>={TAIL_AT}" if value >= TAIL_AT else f"count={value}"
        strata.append(_stratum(subset, key))
        if value >= TAIL_AT:
            break

    registered = json.loads((ROOT / RESULT_OUT).read_text(encoding="utf-8"))
    usable = [s for s in strata if s["difference"] is not None]
    return {
        "kind": "formation_provenance_robustness",
        "status": "descriptive_only_changes_nothing",
        "changes_verdict": False,
        "creates_success_rule": False,
        "source": "cached per-candidate records; no cell was re-run",
        "seeds": list(CONFIRMATORY_SEEDS),
        "registered": {"difference": registered["difference"],
                       "interval": registered["interval"],
                       "verdict": registered["verdict"]},
        "per_seed": per_seed,
        "leave_one_seed_out": loo,
        "temporal_count_strata": strata,
        "standardised_difference": _standardise(strata),
        "strata_with_both_arms": len(usable),
        "strata_positive": sum(1 for s in usable if s["difference"] > 0),
        "note": ("descriptive robustness only: no threshold, no new success rule, and the "
                 "registered verdict and interval are unchanged"),
    }


def render(art: dict) -> str:
    loo = [f["difference"] for f in art["leave_one_seed_out"]]
    diffs = [s["difference"] for s in art["per_seed"]]
    lines = [
        "# Formation provenance — robustness checks (descriptive)",
        "",
        "**Generated from [`docs/formation_provenance_robustness.json`](formation_provenance_robustness.json).**",
        "These tables are descriptive. They create no success rule, apply no threshold, and",
        "**do not change the registered verdict or interval** — the endpoint was evaluated once",
        "on the confirmatory seeds and that result stands.",
        "",
        f"Input: the cached per-candidate records of seeds {art['seeds'][0]}–{art['seeds'][-1]};",
        "no cell was re-run.",
        "",
        "## Registered result (unchanged)",
        "",
        f"Difference {art['registered']['difference']:+.4f}, interval "
        f"{art['registered']['interval']}, verdict **{art['registered']['verdict']}**.",
        "",
        "## Per seed",
        "",
        "| seed | world hits/n | world rate | self hits/n | self rate | difference |",
        "|---|---|---|---|---|---|",
    ]
    for row in art["per_seed"]:
        w, s = row["world"], row["self_including"]
        lines.append(f"| {row['seed']} | {w['hits']}/{w['n']} | {w['rate']:.4f} | "
                     f"{s['hits']}/{s['n']} | {s['rate']:.4f} | {row['difference']:+.4f} |")
    lines += [
        "",
        f"Per-seed differences range {min(diffs):+.4f} to {max(diffs):+.4f}; "
        f"**{sum(1 for d in diffs if d > 0)} of {len(diffs)}** are positive.",
        "",
        "## Leave one seed out",
        "",
        f"Pooled differences range {min(loo):+.4f} to {max(loo):+.4f} when one seed is removed;",
        f"**{sum(1 for d in loo if d > 0)} of {len(loo)}** folds stay positive.",
        "",
        "## By candidate evidence count (`temporal_count`)",
        "",
        "The registered permutation preserved seed and cycle, not evidence count, so this table",
        "asks whether the direction survives at comparable counts.",
        "",
        "| stratum | world hits/n | world rate | self hits/n | self rate | difference |",
        "|---|---|---|---|---|---|",
    ]
    for s in art["temporal_count_strata"]:
        wrate = "—" if s["world_rate"] is None else f"{s['world_rate']:.4f}"
        srate = "—" if s["self_rate"] is None else f"{s['self_rate']:.4f}"
        diff = "—" if s["difference"] is None else f"{s['difference']:+.4f}"
        lines.append(f"| `{s['key']}` | {s['world_hits']}/{s['world_n']} | {wrate} | "
                     f"{s['self_hits']}/{s['self_n']} | {srate} | {diff} |")
    lines += [
        "",
        f"Stratum-weighted difference: **{art['standardised_difference']:+.4f}**, over "
        f"{art['strata_with_both_arms']} strata holding both arms; the direction is positive in "
        f"**{art['strata_positive']} of {art['strata_with_both_arms']}**.",
        "",
        "## What these checks do and do not say",
        "",
        "They say whether the pooled association is carried by one seed, and whether it survives",
        "when candidates are compared at the same recorded evidence count. A positive",
        "stratum-weighted difference suggests provenance carries information not explained by the",
        "transition count alone. That is still descriptive: these are observational strata, not an",
        "intervention, and nothing here shows the knowledge is useful, that it originated in the",
        "world, or that provenance causes held-out occurrence.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    art = analyse()
    (ROOT / OUT).write_text(json.dumps(art, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / DOC).write_text(render(art), encoding="utf-8")
    print(json.dumps({
        "per_seed_range": [min(s["difference"] for s in art["per_seed"]),
                           max(s["difference"] for s in art["per_seed"])],
        "loo_range": [min(f["difference"] for f in art["leave_one_seed_out"]),
                      max(f["difference"] for f in art["leave_one_seed_out"])],
        "standardised": art["standardised_difference"],
        "strata_positive": [art["strata_positive"], art["strata_with_both_arms"]],
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
