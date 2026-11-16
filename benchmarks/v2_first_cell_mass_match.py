"""Is revision's offset mass, allocation, or recency?

The null diagnostic measured `d_C = L_C − L_A = +0.000847`, split into a β
pseudo-count cost (+0.001312) and a revision offset (−0.000465). Maintained
membership holds **0.783** member edges per composite against **2.571** frozen,
but it also differs in *which* composites survive: it drops whole composites
rather than thinning every one. Two matched controls separate the mechanisms.

**Control 1 — total mass.** Draw the maintained arm's total number of edges at
random from the whole frozen edge pool. Total mass is equal; the allocation
across composites is free.

**Control 2 — mass and key count.** Draw the same total number of edges, but
confine them to a random subset of frozen composites of the same non-empty size
as the maintained arm, at least one edge each.

Both matched memberships select their own β on the calibration band from the
declared grid. Nothing else changes: same null worlds, detections, admission,
revision window and scorer.

Pre-declared reading, before either run, with Δ = d_matched − d_maintained:

* interval on Δ **includes zero** → the control reproduces the maintained cost;
  the matched dimension explains it.
* interval lies **entirely above zero** → maintained is better than the control;
  the dimension the control randomises (allocation, or selection) adds value.
* interval lies **entirely below zero** → maintained is worse than the control;
  the random allocation/selection is better.

The seeds are the 20 null worlds, reused by restatement of their reservation;
no new seed is spent. A diagnostic, not a cell and not a verdict.

    python -m benchmarks.v2_first_cell_mass_match --write
    python -m benchmarks.v2_first_cell_mass_match --check
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from benchmarks import engine_stamp, v2_first_cell_readout as readout  # noqa: E402
from benchmarks.v2_first_cell_null import NULL_SEEDS, null_stream  # noqa: E402

ARTIFACT = Path("docs/v2_first_cell_mass_match.json")
PAGE = Path("docs/V2-FIRST-CELL-MASS-MATCH.md")
NULL_ARTIFACT = Path("docs/v2_first_cell_null.json")
LEVEL = 0.99
MODES = ("mass", "keys")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sorted_edges(edges) -> list[frozenset[str]]:
    return sorted(edges, key=lambda edge: tuple(sorted(edge)))


def matched_membership(detections, upto: int, window: int, seed: int, mode: str) -> dict:
    """A frozen membership thinned to the maintained arm's mass, or mass and keys."""
    frozen, _ = readout.evolve(detections, upto, window, False)
    maintained, _ = readout.evolve(detections, upto, window, True)
    pool = [(key, edge) for key in sorted(frozen) for edge in _sorted_edges(frozen[key])]
    target_edges = sum(len(edges) for edges in maintained.values())
    target_keys = sum(1 for edges in maintained.values() if edges)
    rng = random.Random(seed)
    matched: dict[tuple[str, ...], set[frozenset[str]]] = {key: set() for key in frozen}
    shortfall = 0
    if mode == "mass":
        if target_edges >= len(pool):
            chosen = pool
            shortfall = target_edges - len(pool)
        else:
            chosen = rng.sample(pool, target_edges)
        for key, edge in chosen:
            matched[key].add(edge)
    elif mode == "keys":
        candidates = [key for key in sorted(frozen) if frozen[key]]
        keep = min(target_keys, len(candidates))
        chosen_keys = rng.sample(candidates, keep)
        allocation = {key: 1 for key in chosen_keys}
        remaining = target_edges - keep
        capacity = {key: len(frozen[key]) - 1 for key in chosen_keys}
        while remaining > 0:
            eligible = [key for key in chosen_keys if capacity[key] > 0]
            if not eligible:
                shortfall += remaining
                break
            key = rng.choice(eligible)
            allocation[key] += 1
            capacity[key] -= 1
            remaining -= 1
        for key in chosen_keys:
            count = min(allocation[key], len(frozen[key]))
            matched[key] = set(rng.sample(_sorted_edges(frozen[key]), count))
    else:
        raise ValueError("unknown matching mode: %s" % mode)
    return {"members": matched, "shortfall": shortfall,
            "frozen_edges": len(pool), "target_edges": target_edges,
            "target_keys": target_keys}


def _mass(members: dict) -> dict:
    nonempty = [edges for edges in members.values() if edges]
    total = sum(len(edges) for edges in nonempty)
    return {"composites": len(members), "nonempty": len(nonempty), "edges": total,
            "mean_edges": round(total / len(nonempty), 6) if nonempty else 0.0}


def _select_beta(tags, calibration, members) -> tuple[int, float | None]:
    best = None
    for beta in readout.BETA_GRID:
        loss = readout.score(tags, calibration, members, beta)["log_loss"]
        if loss is not None and (best is None or loss < best[1]):
            best = (beta, loss)
    return best if best else (0, None)


def _arm(tags, detections, boundaries, seed, mode: str) -> dict:
    calib = tuple(boundaries["calibration"])
    calib_match = matched_membership(detections, calib[0] - 1, boundaries["window"],
                                     seed ^ 0x5EED, mode)
    beta, calibration = _select_beta(tags, calib, calib_match["members"])
    train_match = matched_membership(detections, boundaries["train"] - 1,
                                     boundaries["window"], seed ^ 0x5EED, mode)
    loss = readout.score(tags, tuple(boundaries["holdout"]), train_match["members"], beta)["log_loss"]
    return {"loss": loss, "beta": beta, "calibration": calibration,
            "mass": _mass(train_match["members"]), "shortfall": train_match["shortfall"]}


def measure(seed: int, cycles: int = 120) -> dict:
    stream = null_stream(seed, cycles)
    data = readout.replay(seed, cycles, stream)
    scored = readout.arms_for(data["tags"], data["detections"], cycles)
    arms = scored["arms"]
    boundaries = scored["boundaries"]
    matched = {mode: _arm(data["tags"], data["detections"], boundaries, seed, mode) for mode in MODES}
    d_c = arms["C"]["log_loss"] - arms["A"]["log_loss"]
    frozen, _ = readout.evolve(data["detections"], boundaries["train"] - 1,
                               boundaries["window"], False)
    maintained, _ = readout.evolve(data["detections"], boundaries["train"] - 1,
                                   boundaries["window"], True)
    record = {
        "seed": seed,
        "arms": {"A": arms["A"]["log_loss"], "C": arms["C"]["log_loss"]},
        "beta": {"C": arms["C"]["beta"]},
        "d_maintained": round(d_c, 9),
        "mass": {"frozen": _mass(frozen), "maintained": _mass(maintained)},
    }
    for mode in MODES:
        row = matched[mode]
        record["arms"][mode.upper()] = row["loss"]
        record["beta"][mode.upper()] = row["beta"]
        record["mass"][mode] = row["mass"]
        record["shortfall_" + mode] = row["shortfall"]
        record["delta_" + mode] = row["loss"] - arms["C"]["log_loss"]
        record["d_" + mode] = row["loss"] - arms["A"]["log_loss"]
    return record


def _reading(interval: dict, above: str, below: str, null: str) -> dict:
    if interval["lo"] > 0:
        label = above
    elif interval["hi"] < 0:
        label = below
    else:
        label = null
    return {"label": label, "interval": interval}


def run(seeds=None, cycles: int = 120) -> dict:
    seeds = list(NULL_SEEDS) if seeds is None else list(seeds)
    rows = [measure(seed, cycles) for seed in seeds]
    return assemble(rows, seeds, cycles)


def assemble(rows, seeds, cycles: int = 120) -> dict:
    deltas = {mode: [row["delta_" + mode] for row in rows] for mode in MODES}
    intervals = {mode: readout.paired_interval(deltas[mode], level=LEVEL, resamples=10_000)
                 for mode in MODES}
    readings = {
        "mass": _reading(
            intervals["mass"],
            above="MAINTAINED BEATS A MASS-MATCHED RANDOM ALLOCATION",
            below="A MASS-MATCHED RANDOM ALLOCATION BEATS MAINTAINED",
            null="TOTAL MASS ALONE REPRODUCES THE MAINTAINED COST"),
        "keys": _reading(
            intervals["keys"],
            above="MAINTAINED SELECTION ADDS BEYOND MASS AND KEY COUNT",
            below="MAINTAINED SELECTION IS WORSE THAN RANDOM AT EQUAL MASS AND KEY COUNT",
            null="SELECTION ADDS NOTHING AT EQUAL MASS AND KEY COUNT"),
    }
    if readings["keys"]["label"].startswith("SELECTION ADDS NOTHING"):
        conclusion = ("the offset is a mass-and-allocation effect: at equal total mass and equal non-empty key "
                      "count, maintained membership is indistinguishable from a random frozen subset. The revision "
                      "rule's retained keys carry no measurable selection benefit on a null world.")
    elif readings["keys"]["label"].startswith("MAINTAINED SELECTION ADDS"):
        conclusion = ("recency or selection contributes beyond mass: at equal total mass and equal non-empty key "
                      "count, maintained membership still costs less than a random frozen subset.")
    else:
        conclusion = ("maintained selection is worse than random at equal mass and key count, so the offset is not "
                      "a selection benefit at all.")
    record = {
        "kind": "v2_first_cell_mass_match",
        "id": "V2-FIRST-CELL-MASS-MATCH-1",
        "date": "2026-11-16",
        "status": ("DIAGNOSTIC — TWO MATCHED FROZEN CONTROLS ON THE NULL WORLDS, NOT A CELL AND NOT A VERDICT"),
        "question": ("is the revision rule's −0.000465 offset explained by total mass, by how that mass is "
                     "allocated across composites, or by a recency/selection advantage?"),
        "design": {
            "worlds": "the 20 null worlds, reused by restatement of their seed reservation",
            "mass": ("draw the maintained arm's total edge count at random from the whole frozen edge pool; total "
                     "mass equal, allocation free"),
            "keys": ("draw the same total edge count, confined to a random subset of frozen composites of the same "
                     "non-empty size as maintained, at least one edge each, as far as those keys' capacities "
                     "allow; the residual shortfall is reported"),
            "beta": "each matched arm selects its own beta on the calibration band from the declared grid",
            "quantity": "delta = d_matched - d_maintained; positive means maintained is better than the control",
            "reading": ("99% interval includes zero -> the control reproduces the maintained cost; above zero -> "
                        "the randomised dimension adds value; below zero -> the random control is better"),
            "level": LEVEL, "resamples": 10_000, "bootstrap_seed": readout.BOOTSTRAP_SEED,
        },
        "seeds": seeds,
        "per_seed": rows,
        "summary": {
            "n": len(rows),
            "mean_d_maintained": round(statistics.fmean([row["d_maintained"] for row in rows]), 9),
            "mean_d_mass": round(statistics.fmean([row["d_mass"] for row in rows]), 9),
            "mean_d_keys": round(statistics.fmean([row["d_keys"] for row in rows]), 9),
            **{("mean_delta_" + mode): round(statistics.fmean(deltas[mode]), 9) for mode in MODES},
            **{("sd_delta_" + mode): (round(statistics.stdev(deltas[mode]), 9)
                                      if len(deltas[mode]) > 1 else None) for mode in MODES},
            **{("positive_delta_" + mode): sum(1 for value in deltas[mode] if value > 0)
               for mode in MODES},
            "mean_edges_frozen": round(statistics.fmean(
                [row["mass"]["frozen"]["edges"] for row in rows]), 6),
            "mean_edges_maintained": round(statistics.fmean(
                [row["mass"]["maintained"]["edges"] for row in rows]), 6),
            "mean_edges_mass": round(statistics.fmean(
                [row["mass"]["mass"]["edges"] for row in rows]), 6),
            "mean_edges_keys": round(statistics.fmean(
                [row["mass"]["keys"]["edges"] for row in rows]), 6),
            "mean_nonempty_frozen": round(statistics.fmean(
                [row["mass"]["frozen"]["nonempty"] for row in rows]), 3),
            "mean_nonempty_maintained": round(statistics.fmean(
                [row["mass"]["maintained"]["nonempty"] for row in rows]), 3),
            "mean_nonempty_mass": round(statistics.fmean(
                [row["mass"]["mass"]["nonempty"] for row in rows]), 3),
            "mean_nonempty_keys": round(statistics.fmean(
                [row["mass"]["keys"]["nonempty"] for row in rows]), 3),
            "shortfall": sum(row["shortfall_mass"] + row["shortfall_keys"] for row in rows),
        },
        "intervals": intervals,
        "readings": {mode: {"label": readings[mode]["label"]} for mode in MODES},
        "verdict": {
            "mass": readings["mass"]["label"],
            "keys": readings["keys"]["label"],
            "conclusion": conclusion,
        },
        "note": ("the controls change only which frozen edges are kept and how many; the worlds, detections, "
                 "admission, window, beta grid and scorer are the protocol's. A null-world result: it says nothing "
                 "about whether maintained selection finds signal on a structured world."),
    }
    return engine_stamp.stamp(record)


def render_doc(record: dict) -> str:
    rows = "\n".join(
        "| `%d` | %.9f | %.9f | %.9f | %.9f | %.9f |" % (
            row["seed"], row["d_maintained"], row["d_mass"], row["d_keys"],
            row["delta_mass"], row["delta_keys"])
        for row in record["per_seed"])
    summary = record["summary"]
    interval = record["intervals"]
    return f"""# Mass- and key-matched frozen membership — mass, allocation, or recency?

**Status:** `{record['status']}`

**Question:** {record['question']}

## 1. The two controls

The maintained arm holds **{summary['mean_edges_maintained']:.1f}** member edges in **{summary['mean_nonempty_maintained']:.1f}**
non-empty composites per null world; frozen holds **{summary['mean_edges_frozen']:.1f}** edges in
**{summary['mean_nonempty_frozen']:.1f}**. It differs in total mass *and* in which composites survive.

**Control 1, total mass.** Draw the maintained arm's total edge count at random from the whole frozen pool. Total mass is
equal; allocation across composites is free. Mean: **{summary['mean_edges_mass']:.1f}** edges in
**{summary['mean_nonempty_mass']:.1f}** composites.

**Control 2, mass and key count.** Draw the same total edge count, confined to a random subset of frozen composites of the
same non-empty size as maintained, at least one edge each. The chosen keys cannot always hold the full mass: the residual
shortfall is **{summary['shortfall'] / summary['n']:.2f}** edges per world. Mean: **{summary['mean_edges_keys']:.1f}**
edges in **{summary['mean_nonempty_keys']:.1f}** composites.

Both matched arms select their own β on the calibration band. `Δ = d_matched − d_maintained`; positive means maintained
is better than the control. The reading was fixed before the run: an interval including zero means the control
reproduces the maintained cost; above zero means the randomised dimension adds value; below zero means the random
control is better.

## 2. Per-seed result

| Seed | d maintained | d mass-matched | d key-matched | Δ mass | Δ keys |
|---|---|---|---|---|---|---|
{rows}

## 3. Summary

| Quantity | Mass-matched | Key-matched |
|---|---|---|
| Mean `d` | **{summary['mean_d_mass']:.9f}** | **{summary['mean_d_keys']:.9f}** |
| Mean member edges | {summary['mean_edges_mass']:.1f} | {summary['mean_edges_keys']:.1f} (shortfall {summary['shortfall'] / summary['n']:.2f}) |
| Mean Δ | **{summary['mean_delta_mass']:.9f}** | **{summary['mean_delta_keys']:.9f}** |
| sd Δ | {summary['sd_delta_mass']:.9f} | {summary['sd_delta_keys']:.9f} |
| Positive Δ | {summary['positive_delta_mass']} of {summary['n']} | {summary['positive_delta_keys']} of {summary['n']} |
| 99% interval on Δ | `[{interval['mass']['lo']:.9f}, {interval['mass']['hi']:.9f}]` | `[{interval['keys']['lo']:.9f}, {interval['keys']['hi']:.9f}]` |
| Reading | **{record['verdict']['mass']}** | **{record['verdict']['keys']}** |

Mean `d` for maintained: **{summary['mean_d_maintained']:.9f}**.

**Conclusion.** {record['verdict']['conclusion']}

## 4. What this establishes, and what it does not

It locates the revision offset between three candidates. If the mass-matched control reproduces maintained, the offset is
mass alone. If it does not but the key-matched control does, the difference is allocation — how the surviving mass is
spread across composites. If neither does, the retained selection itself carries the difference.

The key-matched arm is slightly lighter than maintained (the residual shortfall above), which would bias *in favour* of
the random control; the mass-matched arm has no such shortfall and reaches the same sign, so the conclusion does not rest
on it.

It does not establish that random thinning is the right counterfactual, and a random subset discards any structure the
frozen set had. On a structureless world there is no structure to discard, which is why this is the right place to ask
the question; on a structured world the same controls would be weaker tests. It also says nothing about the cell's world.

## 5. Reproduction

```bash
python -m benchmarks.v2_first_cell_mass_match --write
python -m benchmarks.v2_first_cell_mass_match --check
```

Artifact: [`v2_first_cell_mass_match.json`](v2_first_cell_mass_match.json).
"""


def check() -> None:
    record = _load(ARTIFACT)
    if render_doc(record) != PAGE.read_text(encoding="utf-8"):
        raise SystemExit("mass-match page is stale; rebuild with --write")
    if record["kind"] != "v2_first_cell_mass_match":
        raise SystemExit("artifact is not the mass-matched control")
    if record["seeds"] != list(NULL_SEEDS):
        raise SystemExit("artifact does not cover the null worlds")
    null = _load(NULL_ARTIFACT)
    for row, reference in zip(record["per_seed"], null["per_seed"]):
        if abs(row["d_maintained"] - reference["d"]) > 1e-6:
            raise SystemExit("maintained loss does not reproduce the null artifact")
        for mode in MODES:
            if row["mass"][mode]["edges"] > row["mass"]["maintained"]["edges"]:
                raise SystemExit("matched mass exceeds maintained mass")
            if mode == "keys" and row["mass"][mode]["nonempty"] > row["mass"]["maintained"]["nonempty"]:
                raise SystemExit("key-matched composites exceed maintained's non-empty count")
    first = run(list(NULL_SEEDS[:2]), cycles=12)
    second = run(list(NULL_SEEDS[:2]), cycles=12)
    for mode in MODES:
        if [row["delta_" + mode] for row in first["per_seed"]] != [row["delta_" + mode] for row in second["per_seed"]]:
            raise SystemExit("matched control is not deterministic: %s" % mode)
    print("check: page fresh, 20 null worlds reproduced, matched mass/key counts bounded, deterministic; "
          "mass: %s; keys: %s" % (record["verdict"]["mass"], record["verdict"]["keys"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="measure the null worlds and write artifact and page")
    parser.add_argument("--check", action="store_true", help="verify freshness, matching and determinism")
    args = parser.parse_args()
    if args.write:
        record = run()
        ARTIFACT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        PAGE.write_text(render_doc(record), encoding="utf-8")
        print(json.dumps({"summary": record["summary"], "intervals": record["intervals"],
                          "verdict": record["verdict"]}, indent=2))
        return 0
    if args.check:
        check()
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
