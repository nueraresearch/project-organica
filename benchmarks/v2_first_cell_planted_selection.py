"""Do the matched controls change on a world that actually carries signal?

The null-world control found that at equal mass — and at equal mass and key
count — a random frozen allocation beats maintained membership. On a
structureless world frequency is noise, so that is what one should expect. This
module asks the other half: on the **planted motif world**, where the composite
is the only evidence for the held-out transition, does maintained selection beat
the random controls?

Same two controls, same β selection, same scorer; the world and its ten
measurement seeds are the positive control's, reused by restatement. Reading,
fixed before the run:

* Δ (matched − maintained) interval **above zero** → maintained selection
  captures the planted signal beyond mass and key count.
* interval **includes zero** → no selection advantage detectable even with
  signal.
* interval **below zero** → maintained selection is worse than random even when
  the world carries a planted composite.

A diagnostic, not a cell and not a verdict.

    python -m benchmarks.v2_first_cell_planted_selection --write
    python -m benchmarks.v2_first_cell_planted_selection --check
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from benchmarks import engine_stamp, v2_first_cell_readout as readout  # noqa: E402
from benchmarks.v2_first_cell_mass_match import MODES, _arm, _mass, _reading  # noqa: E402
from benchmarks.v2_first_cell_planted import declaration, motif_stream  # noqa: E402

ARTIFACT = Path("docs/v2_first_cell_planted_selection.json")
PAGE = Path("docs/V2-FIRST-CELL-PLANTED-SELECTION.md")
NULL_MATCH = Path("docs/v2_first_cell_mass_match.json")
PLANTED = Path("docs/v2_first_cell_planted.json")
LEVEL = 0.99


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def measure(seed: int, cycles: int = 120) -> dict:
    stream, motifs = motif_stream(seed, cycles)
    data = readout.replay(seed, cycles, stream)
    scored = readout.arms_for(data["tags"], data["detections"], cycles)
    arms = scored["arms"]
    boundaries = scored["boundaries"]
    matched = {mode: _arm(data["tags"], data["detections"], boundaries, seed, mode)
               for mode in MODES}
    d_c = arms["C"]["log_loss"] - arms["A"]["log_loss"]
    record = {
        "seed": seed,
        "motifs": ["".join(motif) for motif in motifs],
        "arms": {"A": arms["A"]["log_loss"], "C": arms["C"]["log_loss"]},
        "d_maintained": round(d_c, 9),
        "mass": {"maintained": _mass(readout.evolve(
            data["detections"], boundaries["train"] - 1, boundaries["window"], True)[0])},
    }
    for mode in MODES:
        row = matched[mode]
        record["arms"][mode.upper()] = row["loss"]
        record["beta_" + mode] = row["beta"]
        record["mass"][mode] = row["mass"]
        record["shortfall_" + mode] = row["shortfall"]
        record["delta_" + mode] = row["loss"] - arms["C"]["log_loss"]
        record["d_" + mode] = row["loss"] - arms["A"]["log_loss"]
    return record


def run(seeds=None, cycles: int = 120) -> dict:
    seeds = declaration()["seed_block"]["seeds"] if seeds is None else list(seeds)
    rows = [measure(seed, cycles) for seed in seeds]
    deltas = {mode: [row["delta_" + mode] for row in rows] for mode in MODES}
    intervals = {mode: readout.paired_interval(deltas[mode], level=LEVEL, resamples=10_000)
                 for mode in MODES}
    readings = {
        "mass": _reading(
            intervals["mass"],
            above="MAINTAINED BEATS A MASS-MATCHED RANDOM ALLOCATION WITH SIGNAL",
            below="A MASS-MATCHED RANDOM ALLOCATION STILL BEATS MAINTAINED WITH SIGNAL",
            null="TOTAL MASS ALONE REPRODUCES THE MAINTAINED COST WITH SIGNAL"),
        "keys": _reading(
            intervals["keys"],
            above="MAINTAINED SELECTION CAPTURES SIGNAL BEYOND MASS AND KEY COUNT",
            below="MAINTAINED SELECTION IS WORSE THAN RANDOM EVEN WITH SIGNAL",
            null="NO SELECTION ADVANTAGE DETECTABLE WITH SIGNAL"),
    }
    null = _load(NULL_MATCH)["summary"]
    comparison = {
        "null_mean_delta_keys": null["mean_delta_keys"],
        "planted_mean_delta_keys": round(statistics.fmean(deltas["keys"]), 9),
        "null_mean_delta_mass": null["mean_delta_mass"],
        "planted_mean_delta_mass": round(statistics.fmean(deltas["mass"]), 9),
    }
    if readings["keys"]["label"].startswith("MAINTAINED SELECTION CAPTURES"):
        conclusion = ("with a planted motif, maintained selection beats a random frozen control at equal mass and "
                      "key count, unlike the null. The null's selection cost is a property of noise, not an inability "
                      "to select signal.")
    elif readings["keys"]["label"].startswith("NO SELECTION ADVANTAGE"):
        conclusion = ("even with a planted motif, maintained selection is statistically indistinguishable from "
                      "random at equal mass and key count. The null's selection cost does not reverse when the world "
                      "carries a signal the composite can see.")
    else:
        conclusion = ("maintained selection remains worse than random at equal mass and key count even when the "
                      "world carries a planted motif.")
    record = {
        "kind": "v2_first_cell_planted_selection",
        "id": "V2-FIRST-CELL-PLANTED-SELECTION-1",
        "date": "2026-11-16",
        "status": ("DIAGNOSTIC — THE MATCHED CONTROLS ON THE PLANTED MOTIF WORLD, NOT A CELL AND NOT A VERDICT"),
        "question": ("on a world where the composite is the only evidence for the held-out transition, does "
                     "maintained selection beat random frozen membership at equal mass and key count?"),
        "world": {
            "construction": ("training repeats five three-tag motifs a->b->c; the held-out stream asks for a->c, "
                             "the motif closure read forwards, which training never showed"),
            "seeds": "the positive control's ten measurement seeds, reused by restatement",
            "cycles": cycles,
        },
        "design": {
            "controls": "total mass, and total mass plus non-empty key count; both select their own beta",
            "quantity": "delta = d_matched - d_maintained; positive means maintained is better than the control",
            "reading": ("99% interval above zero -> selection captures signal; includes zero -> no detectable "
                        "advantage; below zero -> selection is worse than random even with signal"),
            "level": LEVEL, "resamples": 10_000, "bootstrap_seed": readout.BOOTSTRAP_SEED,
        },
        "seeds": seeds,
        "per_seed": rows,
        "summary": {
            "n": len(rows),
            "mean_d_maintained": round(statistics.fmean([row["d_maintained"] for row in rows]), 9),
            **{("mean_d_" + mode): round(statistics.fmean([row["d_" + mode] for row in rows]), 9)
               for mode in MODES},
            **{("mean_delta_" + mode): round(statistics.fmean(deltas[mode]), 9) for mode in MODES},
            **{("sd_delta_" + mode): (round(statistics.stdev(deltas[mode]), 9)
                                      if len(deltas[mode]) > 1 else None) for mode in MODES},
            **{("positive_delta_" + mode): sum(1 for value in deltas[mode] if value > 0)
               for mode in MODES},
            "mean_edges_maintained": round(statistics.fmean(
                [row["mass"]["maintained"]["edges"] for row in rows]), 6),
            "mean_edges_mass": round(statistics.fmean(
                [row["mass"]["mass"]["edges"] for row in rows]), 6),
            "mean_edges_keys": round(statistics.fmean(
                [row["mass"]["keys"]["edges"] for row in rows]), 6),
            "mean_nonempty_maintained": round(statistics.fmean(
                [row["mass"]["maintained"]["nonempty"] for row in rows]), 3),
            "mean_nonempty_mass": round(statistics.fmean(
                [row["mass"]["mass"]["nonempty"] for row in rows]), 3),
            "mean_nonempty_keys": round(statistics.fmean(
                [row["mass"]["keys"]["nonempty"] for row in rows]), 3),
            "shortfall": sum(row["shortfall_mass"] + row["shortfall_keys"] for row in rows),
        },
        "intervals": intervals,
        "comparison": comparison,
        "verdict": {
            "mass": readings["mass"]["label"],
            "keys": readings["keys"]["label"],
            "conclusion": conclusion,
        },
        "note": ("the positive control's world is deliberately the readout's best case; this diagnostic asks "
                 "whether its selection advantage is real at matched mass, not whether the cell's world contains "
                 "such motifs. It spends no new seeds."),
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
    comparison = record["comparison"]
    return f"""# The matched controls on the planted motif world — does selection capture signal?

**Status:** `{record['status']}`

**Question:** {record['question']}

## 1. The world and the controls

{record['world']['construction']}. The world and its ten measurement seeds are the positive control's, reused by
restatement; no new seed is spent. Both controls are the null diagnostic's: draw the maintained arm's total edge count at
random from the frozen pool (free allocation), and draw the same total confined to a random subset of frozen composites of
the maintained arm's non-empty size. Both select their own β on the calibration band.

`Δ = d_matched − d_maintained`; positive means maintained is better than the control. The reading was fixed before the
run: above zero means selection captures signal; including zero means no detectable advantage; below zero means selection
is worse than random even with signal.

## 2. Per-seed result

| Seed | d maintained | d mass-matched | d key-matched | Δ mass | Δ keys |
|---|---|---|---|---|---|
{rows}

## 3. Summary

| Quantity | Mass-matched | Key-matched |
|---|---|---|
| Mean `d` | **{summary['mean_d_mass']:.9f}** | **{summary['mean_d_keys']:.9f}** |
| Mean Δ | **{summary['mean_delta_mass']:.9f}** | **{summary['mean_delta_keys']:.9f}** |
| sd Δ | {summary['sd_delta_mass']:.9f} | {summary['sd_delta_keys']:.9f} |
| Positive Δ | {summary['positive_delta_mass']} of {summary['n']} | {summary['positive_delta_keys']} of {summary['n']} |
| 99% interval on Δ | `[{interval['mass']['lo']:.9f}, {interval['mass']['hi']:.9f}]` | `[{interval['keys']['lo']:.9f}, {interval['keys']['hi']:.9f}]` |
| Reading | **{record['verdict']['mass']}** | **{record['verdict']['keys']}** |

Mean `d` for maintained: **{summary['mean_d_maintained']:.9f}**. Mean member edges: maintained
{summary['mean_edges_maintained']:.1f} in {summary['mean_nonempty_maintained']:.1f} composites; mass control
{summary['mean_edges_mass']:.1f} in {summary['mean_nonempty_mass']:.1f}; key control {summary['mean_edges_keys']:.1f} in
{summary['mean_nonempty_keys']:.1f} (shortfall {summary['shortfall'] / summary['n']:.2f} edges per world).

**Compared with the null worlds:** key-matched Δ was **{comparison['null_mean_delta_keys']:.9f}** on the null and is
**{comparison['planted_mean_delta_keys']:.9f}** here; mass-matched Δ was
**{comparison['null_mean_delta_mass']:.9f}** and is **{comparison['planted_mean_delta_mass']:.9f}** here.

**Conclusion.** {record['verdict']['conclusion']}

## 4. What this establishes, and what it does not

It tests whether the maintained rule's selection has value when the world carries a signal the composite can see. The
planted world is deliberately the readout's best case — the held-out transition is the motif closure, absent from training
and bound only by the composite — so a selection advantage, if the rule has one, should show here.

It does not establish that the cell's world contains such motifs, and it does not test the engine's own selection: the
maintained membership is the readout's 20-cycle revision rule, applied to this world's detections. The positive control's
motifs are stable, so frozen and maintained membership may differ little; the key-matched control is the sharper test.

## 5. Reproduction

```bash
python -m benchmarks.v2_first_cell_planted_selection --write
python -m benchmarks.v2_first_cell_planted_selection --check
```

Artifact: [`v2_first_cell_planted_selection.json`](v2_first_cell_planted_selection.json).
"""


def check() -> None:
    record = _load(ARTIFACT)
    if render_doc(record) != PAGE.read_text(encoding="utf-8"):
        raise SystemExit("planted-selection page is stale; rebuild with --write")
    if record["kind"] != "v2_first_cell_planted_selection":
        raise SystemExit("artifact is not the planted-selection control")
    declared = declaration()["seed_block"]["seeds"]
    if record["seeds"] != declared:
        raise SystemExit("artifact does not cover the planted seed block")
    for row in record["per_seed"]:
        for mode in MODES:
            if row["mass"][mode]["edges"] > row["mass"]["maintained"]["edges"]:
                raise SystemExit("matched mass exceeds maintained mass")
    first = run(declared[:2], cycles=16)
    second = run(declared[:2], cycles=16)
    for mode in MODES:
        if [row["delta_" + mode] for row in first["per_seed"]] != [row["delta_" + mode] for row in second["per_seed"]]:
            raise SystemExit("planted selection control is not deterministic: %s" % mode)
    print("check: page fresh, planted seeds measured, matched mass bounded, deterministic; keys: %s"
          % record["verdict"]["keys"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="measure the planted seeds and write artifact and page")
    parser.add_argument("--check", action="store_true", help="verify freshness, matching and determinism")
    args = parser.parse_args()
    if args.write:
        record = run()
        ARTIFACT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        PAGE.write_text(render_doc(record), encoding="utf-8")
        print(json.dumps({"summary": record["summary"], "intervals": record["intervals"],
                          "comparison": record["comparison"], "verdict": record["verdict"]}, indent=2))
        return 0
    if args.check:
        check()
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
