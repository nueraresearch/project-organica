"""A positive control for the first cell: a world where the composite carries the signal.

The null diagnostic showed the readout is slower than pair counts when there is
nothing to learn. That is only half of what a readout must be able to do: it
must also be able to gain when a composite really is the only evidence. This
module plants that signal.

The world repeats five three-tag motifs `a b c` in the training stream, so the
engine admits each motif as a composite whose member edges are the motif's
pairs. The held-out stream then asks for `a -> c`, the motif's closure read
forwards. Training showed `c -> a` and never `a -> c`, so the pair-count arm has
no support for the held-out transition and is left with its smoothing floor;
the composite binds `a` and `c` through the same motif, so the membership arm
can raise `c` when it sees `a`.

The comparison is to the null handicap measured in
`docs/v2_first_cell_handicap.json`, not to zero: a gain only counts here if the
interval lies below minus that handicap.

    python -m benchmarks.v2_first_cell_planted --smoke
    python -m benchmarks.v2_first_cell_planted --write
    python -m benchmarks.v2_first_cell_planted --check

This is a diagnostic, not a cell and not a verdict. It tests the readout's
capacity to express a composite gain, not whether the first cell's world
contains one.
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
from benchmarks.acquisition_compositional import TAG_POOL  # noqa: E402
from organica.streams import EVENTS_PER_CYCLE  # noqa: E402

ARTIFACT = Path("docs/v2_first_cell_planted.json")
PAGE = Path("docs/V2-FIRST-CELL-PLANTED.md")
SEEDS = Path("docs/v2_first_cell_planted_seeds.json")
HANDICAP = Path("docs/v2_first_cell_handicap.json")
POWER = Path("docs/v2_first_cell_power.json")
MOTIFS = 5
REPS = 51
LEVEL = 0.99


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def declaration() -> dict:
    return _load(SEEDS)


def motif_stream(seed: int, cycles: int = 120) -> tuple[dict, list[tuple[str, str, str]]]:
    """Training repeats `a b c`; held out asks for the closure `a c`."""
    rng = random.Random(seed)
    pool = list(TAG_POOL)
    rng.shuffle(pool)
    motifs = [tuple(pool[3 * i:3 * i + 3]) for i in range(MOTIFS)]
    training: list[str] = []
    for a, b, c in motifs:
        for _ in range(REPS):
            training.extend([a, b, c])
    training = training[: readout.TRAIN_BLOCKS * EVENTS_PER_CYCLE]
    heldout: list[str] = []
    for a, _, c in motifs:
        for _ in range(19):
            heldout.extend([a, c])
    events = training + heldout[: (cycles - readout.TRAIN_BLOCKS) * EVENTS_PER_CYCLE]
    return ({"events": events, "trainable": [True] * len(events)}, motifs)


def membership_share(detections, upto: int, window: int, motifs) -> dict:
    members, mutations = readout.evolve(detections, upto, window, True)
    closure = {frozenset((a, c)) for a, _, c in motifs}
    edges = matched = 0
    for member_edges in members.values():
        for edge in member_edges:
            edges += 1
            matched += int(edge in closure)
    return {"composites": len(members), "mutations": mutations, "edges": edges,
            "closure_edges": matched,
            "closure_share": round(matched / edges, 6) if edges else None}


def measure(seed: int, cycles: int = 120) -> dict:
    stream, motifs = motif_stream(seed, cycles)
    data = readout.replay(seed, cycles, stream)
    scored = readout.arms_for(data["tags"], data["detections"], cycles)
    arms = scored["arms"]
    share = membership_share(data["detections"], scored["boundaries"]["train"] - 1,
                             scored["boundaries"]["window"], motifs)
    value = arms["C"]["log_loss"] - arms["A"]["log_loss"]
    return {
        "seed": seed,
        "detections": len(data["detections"]),
        "arms": arms,
        "membership": share,
        "d": round(value, 6),
        "d_beta_only": round(arms["B"]["log_loss"] - arms["A"]["log_loss"], 6),
        "d_revision_only": round(arms["C"]["log_loss"] - arms["B"]["log_loss"], 6),
        "motifs": ["".join(motif) for motif in motifs],
    }


def run(seeds=None, cycles: int = 120) -> dict:
    seeds = declaration()["seed_block"]["seeds"] if seeds is None else list(seeds)
    rows = [measure(seed, cycles) for seed in seeds]
    diffs = [row["d"] for row in rows]
    beta_only = [row["d_beta_only"] for row in rows]
    revision = [row["d_revision_only"] for row in rows]
    interval = readout.paired_interval(diffs, level=LEVEL, resamples=10_000)
    handicap = _load(HANDICAP)["decomposition"]
    power = _load(POWER)
    net_handicap = handicap["net_mean"]
    required = power["required_mean_d"]["0.9"]
    mean_d = round(statistics.fmean(diffs), 6)
    record = {
        "kind": "v2_first_cell_planted",
        "id": "V2-FIRST-CELL-PLANTED-1",
        "date": "2026-11-16",
        "status": ("POSITIVE-CONTROL DIAGNOSTIC — A PLANTED-SIGNAL WORLD, NOT A CELL AND NOT A VERDICT"),
        "question": ("can the readout express a gain larger than the null handicap when the composite is the "
                     "only evidence for the held-out transition?"),
        "world": {
            "construction": ("training repeats five three-tag motifs a->b->c, 51 times each; the held-out stream "
                             "asks for a->c, the motif closure read forwards, 19 times per motif"),
            "why_the_baseline_cannot": ("training shows c->a and never a->c, so the pair-count arm has zero "
                                       "support for the held-out transition and only its smoothing remains"),
            "why_the_composite_can": ("the admitted motif {a,b,c} contains the undirected member edge {a,c}, so "
                                      "the membership term can raise c when it sees a"),
            "motifs_per_world": MOTIFS, "repetitions": REPS,
            "train_blocks": readout.TRAIN_BLOCKS,
            "holdout": list(readout.HOLDOUT),
            "cycles": cycles,
        },
        "protocol": {
            "m": readout.M, "alpha": readout.ALPHA, "beta_grid": list(readout.BETA_GRID),
            "window": readout.WINDOW, "level": LEVEL, "resamples": 10_000,
            "bootstrap_seed": readout.BOOTSTRAP_SEED,
        },
        "seeds": seeds,
        "smoke_seed": declaration()["smoke_seed"],
        "per_seed": rows,
        "summary": {
            "n": len(diffs),
            "mean_d": mean_d,
            "sd_d": round(statistics.stdev(diffs), 6) if len(diffs) > 1 else None,
            "min_d": min(diffs), "max_d": max(diffs),
            "positive": sum(1 for value in diffs if value > 0),
            "negative": sum(1 for value in diffs if value < 0),
            "mean_d_beta_only": round(statistics.fmean(beta_only), 6),
            "mean_d_revision_only": round(statistics.fmean(revision), 6),
            "mean_composites": round(statistics.fmean(
                [row["membership"]["composites"] for row in rows]), 3),
            "mean_closure_share": round(statistics.fmean(
                [row["membership"]["closure_share"] for row in rows]), 6),
        },
        "interval": interval,
        "comparison": {
            "null_handicap": net_handicap,
            "required_mean_d_90": required,
            "mean_gain": round(-mean_d, 6),
            "gain_multiple_of_handicap": round(-mean_d / net_handicap, 2),
            "clears_handicap": bool(interval["hi"] < -net_handicap),
            "clears_power_bar": bool(interval["hi"] < required),
            "revision_share_of_gain": (round(abs(statistics.fmean(revision)) / abs(mean_d), 6)
                                       if mean_d else None),
        },
        "verdict": {
            "clears": None,
            "reason": ("the planted composite is the only evidence for the held-out transition; a gain that "
                       "clears the handicap shows the readout can express it, and says nothing about whether "
                       "the first cell's world contains such a motif"),
        },
        "note": ("a diagnostic, never a cell. The world is built to be the readout's best case: the held-out "
                 "transition is absent from training, and only the composite's undirected member edge binds it. "
                 "The result licenses no claim about mutable identity."),
    }
    record["verdict"]["clears"] = record["comparison"]["clears_handicap"]
    record["verdict"]["label"] = ("GAIN CLEARS THE NULL HANDICAP" if record["comparison"]["clears_handicap"]
                                  else "GAIN DOES NOT CLEAR THE NULL HANDICAP")
    return engine_stamp.stamp(record)


def render_doc(record: dict) -> str:
    rows = "\n".join(
        "| `%d` | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f | %.4f |" % (
            row["seed"], row["arms"]["A"]["log_loss"], row["arms"]["B"]["log_loss"],
            row["arms"]["C"]["log_loss"], row["d"], row["d_beta_only"],
            row["d_revision_only"],
            row["membership"]["closure_share"] if row["membership"]["closure_share"] is not None else float("nan"))
        for row in record["per_seed"])
    summary = record["summary"]
    interval = record["interval"]
    comparison = record["comparison"]
    return f"""# A planted composite signal — the readout's positive control

**Status:** `{record['status']}`

**Question:** the null worlds show the readout is slower than pair counts when there is nothing to learn. Can it
gain when the composite is the **only** evidence for the held-out transition?

## 1. What is planted

`{record['world']['construction']}`. Training shows `c -> a` and never `a -> c`; the held-out stream asks for
`a -> c`. The pair-count arm therefore has zero support for the scored transition and is left with its smoothing
floor. The admitted motif `{{a,b,c}}` contains the undirected member edge `{{a,c}}` — read from the `c -> a`
occurrence — so the membership term can raise `c` when it sees `a`. This is the readout's best case, built
deliberately: the composite is the only binding between the two tags.

## 2. Per-seed result

`d = L_C − L_A`; a negative value means the primitive beat the pair counts. `closure` is the share of admitted
member edges that are the planted motif's closure pair.

| Seed | A | B | C | `d` C−A | `d` B−A | `d` C−B | closure |
|---|---|---|---|---|---|---|---|
{rows}

## 3. Summary and comparison

Across {summary['n']} planted worlds: mean `d` = **{summary['mean_d']:.6f}**, sd `{summary['sd_d']:.6f}`, range
`[{summary['min_d']:.6f}, {summary['max_d']:.6f}]`; negative in {summary['negative']} of {summary['n']}. The
99% interval is `[{interval['lo']:.6f}, {interval['hi']:.6f}]` around `{interval['mean']:.6f}`.

| Quantity | Value |
|---|---|
| Mean gain (`−d`) | **{comparison['mean_gain']:.6f}** nats |
| Null handicap (measured on structureless worlds) | {comparison['null_handicap']:.6f} |
| Gain as a multiple of the handicap | **{comparison['gain_multiple_of_handicap']:.2f}×** |
| Required observed mean `d` for 90% power | {comparison['required_mean_d_90']:.6f} |
| Interval clears the handicap (`hi < −handicap`) | **{comparison['clears_handicap']}** |
| Interval clears the power bar (`hi < required`) | **{comparison['clears_power_bar']}** |
| Revision's share of the gain (`|C−B| / |C−A|`) | {comparison['revision_share_of_gain']:.3f} |

**Verdict: {record['verdict']['label']}.** {record['verdict']['reason']}.

## 4. What this does and does not establish

**It establishes that the readout can express a composite gain above the null handicap.** The gain is
**{comparison['mean_gain']:.6f}** nats against a handicap of **{comparison['null_handicap']:.6f}**, so the
handicap is a cost the composite term can overcome when the signal is real.

**It also shows the gain is not revision's.** The frozen arm B reaches `{summary['mean_d_beta_only']:.6f}` and
maintenance adds `{summary['mean_d_revision_only']:.6f}`; revision accounts for
{comparison['revision_share_of_gain']:.1%} of the gain. This world has stable motifs, so there is nothing for the
maintenance rule to discover. It is a positive control for the **composite term**, not for mutation.

A matched control on this world ([`V2-FIRST-CELL-PLANTED-SELECTION`](V2-FIRST-CELL-PLANTED-SELECTION.md))
finds that at equal mass and non-empty key count maintained selection beats a random frozen subset by
**0.002091** nats, so the retained selection does carry signal here; it is a small part of the planted gain.

**The interval's scope is narrow.** The ten seeds vary only the tag-to-role mapping; the planted structure is
identical, so the interval measures mapping variation, not a population of worlds. The magnitude does not depend on
that distinction, but its width should not be read as a between-world estimate.

**It tests a binding, not a conjunction.** The composite term is a set of undirected member edges, so the
control shows that an admitted motif can carry a directed transition training never showed. It does not show that
the term represents `a` and `b` jointly — the readout never conditions on the conjunction, only on the edge.

**It does not establish that the first cell's world contains such a motif.** The held-out transition was chosen
to be absent from training and bound only by the composite; no natural world is guaranteed to have that shape. The
cell remains the test of whether the primitive earns its handicap on the pre-registered world, and this diagnostic
does not change the pre-registration or spend the cell's seeds.

## 5. Reproduction

```bash
python -m benchmarks.v2_first_cell_planted --smoke   # the declared smoke seed, not scored
python -m benchmarks.v2_first_cell_planted --write   # ten measurement seeds, artifact and page
python -m benchmarks.v2_first_cell_planted --check   # freshness, determinism, declared block
```

Artifact: [`v2_first_cell_planted.json`](v2_first_cell_planted.json). Seeds:
[`v2_first_cell_planted_seeds.json`](v2_first_cell_planted_seeds.json).
"""


def smoke() -> dict:
    seed = declaration()["smoke_seed"]
    row = measure(seed)
    print(json.dumps({"seed": seed, "d": row["d"], "d_beta_only": row["d_beta_only"],
                      "membership": row["membership"]}, indent=2))
    return row


def check() -> None:
    record = _load(ARTIFACT)
    if render_doc(record) != PAGE.read_text(encoding="utf-8"):
        raise SystemExit("planted page is stale; rebuild with --write")
    if record["kind"] != "v2_first_cell_planted":
        raise SystemExit("artifact is not the planted positive control")
    declared = declaration()["seed_block"]["seeds"]
    if record["seeds"] != declared:
        raise SystemExit("artifact does not cover the declared seed block")
    for row in record["per_seed"]:
        if abs((row["arms"]["C"]["log_loss"] - row["arms"]["A"]["log_loss"]) - row["d"]) > 1e-6:
            raise SystemExit("a recorded difference does not match its arm losses")
        if row["arms"]["C"]["beta"] not in readout.BETA_GRID:
            raise SystemExit("arm C selected a beta outside the grid")
    first = run(declared[:2], cycles=16)
    second = run(declared[:2], cycles=16)
    if [row["d"] for row in first["per_seed"]] != [row["d"] for row in second["per_seed"]]:
        raise SystemExit("planted measurement is not deterministic")
    print("check: page fresh, ten declared seeds measured, readout deterministic, "
          "gain clears the handicap: %s" % record["comparison"]["clears_handicap"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="run the declared smoke seed, not scored")
    parser.add_argument("--write", action="store_true", help="measure the ten seeds and write artifact and page")
    parser.add_argument("--check", action="store_true", help="verify freshness, determinism and the block")
    args = parser.parse_args()
    if args.smoke:
        smoke()
        return 0
    if args.write:
        record = run()
        ARTIFACT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        PAGE.write_text(render_doc(record), encoding="utf-8")
        print(json.dumps({"summary": record["summary"], "interval": record["interval"],
                          "comparison": record["comparison"]}, indent=2))
        return 0
    if args.check:
        check()
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
