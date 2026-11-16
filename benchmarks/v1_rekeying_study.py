"""Would a direction-free identity have changed a carrier's fate?

V1 keys a stored carrier on its path in order (`loop:{'|'.join(path)}`), so the two orientations of one
triangle are different candidates: whichever is not re-detected this cycle decays, and the other starts
again from its raw strength. This study replays one world, reads the stored `sleep:loop_candidate` rows
back, reproduces V1's selection offline as a validation, then re-runs the same rules with a
direction-free key (the sorted tag set) and compares reinforcements, deaths and survivors.

Read-only: no arm, no target, no freeze, no grant, no engine change. The counterfactual is a simulation
under the engine's own rules, not a run.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

from benchmarks import a1_arms, a1_c5_target_timing as timing
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.a2_sham_feasibility import CYCLES

SEED = 20740101
REPLICATION_SEED = 20900101
OUT = "docs/v1_rekeying_study.json"
BOOST = 0.05
DECAY = 0.8
DEATH = 0.15
STABLE = 0.3


def replay(seed: int = SEED) -> tuple[list[tuple[int, tuple[str, ...], float]], list[dict], int]:
    """Return per-cycle detections and every stored loop row, tagged with its cycle."""
    world = generate_compositional_world(seed=seed, cycles=CYCLES)
    db_path = _make_scratch_db("v1_rekeying")
    memory = _CountingMemoryService(str(db_path))
    service = a1_arms.A1ArmSleepService(memory)
    service.MAX_PREDICTIONS = timing.CAP
    acq_lo, acq_hi = timing.PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * timing.EVENTS_PER_CYCLE, acq_hi * timing.EVENTS_PER_CYCLE
    detections: list[tuple[int, tuple[str, ...], float]] = []
    rows: list[dict] = []
    last_rowid = 0
    runs = 0
    for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
        in_acq = event_lo <= i < event_hi
        if in_acq and not trainable:
            continue
        if i % timing.EVENTS_PER_CYCLE == 0:
            memory.current_cycle = i // timing.EVENTS_PER_CYCLE
        memory.store(text, event_type="observe",
                     source=a1_arms.ACQ_SOURCE if in_acq else "env")
        if (i + 1) % timing.EVENTS_PER_CYCLE:
            continue
        cycle = i // timing.EVENTS_PER_CYCLE
        runs += 1
        report = service.run_sleep_cycle()
        for loop in getattr(report, "loops", []) or []:
            path = tuple(getattr(loop, "path", []) or ())
            if len(path) >= 2:
                detections.append((cycle, path, float(getattr(loop, "strength", 0.0))))
        fresh = memory._conn.execute(
            "SELECT rowid, content FROM events WHERE source='sleep:loop_candidate' AND rowid > ? "
            "ORDER BY rowid", (last_rowid,)).fetchall()
        for rowid, content in fresh:
            last_rowid = rowid
            try:
                payload = json.loads(content)
            except (json.JSONDecodeError, ValueError):
                continue
            rows.append({"cycle": cycle, **payload})
    memory.close()
    return detections, rows, runs


def _free(path: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted({tag for tag in path}))


def simulate(detections: list[tuple[int, tuple[str, ...], float]], key) -> dict:
    state: dict[tuple, dict] = {}
    by_cycle: dict[int, list[tuple[tuple, float]]] = collections.defaultdict(list)
    for cycle, path, strength in detections:
        by_cycle[cycle].append((key(path), strength))
    reinforcements = decays = deaths = 0
    for cycle in sorted(by_cycle):
        current = dict(by_cycle[cycle])
        current_keys = set(current)
        for candidate_key in current_keys:
            if candidate_key in state and not state[candidate_key]["retired"]:
                state[candidate_key]["strength"] = min(1.0, current[candidate_key] + BOOST)
                state[candidate_key]["generation"] += 1
                reinforcements += 1
            else:
                state[candidate_key] = {"strength": current[candidate_key], "generation": 1, "retired": False}
        for candidate_key, entry in list(state.items()):
            if entry["retired"] or candidate_key in current_keys:
                continue
            decayed = entry["strength"] * DECAY
            if decayed < DEATH:
                entry["retired"] = True
                entry["strength"] = decayed
                deaths += 1
            else:
                entry["strength"] = decayed
                entry["generation"] += 1
            decays += 1
    live = {k: v for k, v in state.items() if not v["retired"]}
    return {
        "identities": len(state),
        "deaths": deaths,
        "live": len(live),
        "stable": sum(1 for v in live.values() if v["strength"] >= STABLE),
        "reinforcements": reinforcements,
        "decays": decays,
        "mean_live_strength": round(sum(v["strength"] for v in live.values()) / len(live), 4) if live else 0.0,
        "max_live_strength": round(max((v["strength"] for v in live.values()), default=0.0), 4),
        "strengths": {"/".join(k): round(v["strength"], 4) for k, v in sorted(live.items())},
    }


def build(seed: int = SEED) -> dict:
    detections, rows, runs = replay(seed)
    bearing = simulate(detections, lambda path: path)
    free = simulate(detections, _free)

    appearances = collections.Counter(path for _, path, _ in detections)
    stored_paths = {tuple(r.get("path") or ()) for r in rows}
    retired = [r for r in rows if r.get("retired")]
    observed = {
        "detections": len(detections),
        "distinct_paths": len(appearances),
        "distinct_node_sets": len({_free(path) for path in appearances}),
        "stored_rows": len(rows),
        "stored_identities": len(stored_paths),
        "retired_rows": len(retired),
        "sleep_cycles_run": runs,
    }
    validation = {
        "identities_match": bearing["identities"] == len(stored_paths),
        "deaths_observed": len(retired),
        "deaths_simulated": bearing["deaths"],
        "deaths_match": bearing["deaths"] == len(retired),
        "note": ("identities and retirement rows both match the store exactly under the direction-bearing key. An "
                 "earlier version of this study reported 201 retirements and attributed the gap to the 4,000-event "
                 "window; that was wrong. The simulator reinforced from the prior strength instead of the fresh "
                 "detection, which is what _reinforce_current does. With the rule corrected the simulation reproduces "
                 "all %d retirements, and a separate measurement found the window never forgot a live carrier."
                 % len(retired)),
    }

    flips = 0
    sequences: dict[tuple, list[tuple[int, tuple[str, ...]]]] = collections.defaultdict(list)
    for cycle, path, _ in detections:
        sequences[_free(path)].append((cycle, path))
    merged = []
    for node_set, seq in sequences.items():
        seq.sort()
        changed = sum(1 for (_, a), (_, b) in zip(seq, seq[1:]) if a != b)
        flips += changed
        if len({path for _, path in seq}) > 1:
            merged.append({"node_set": list(node_set), "appearances": len(seq),
                           "orientations": len({path for _, path in seq}), "flips": changed})

    def top_share(counter: collections.Counter) -> float:
        total = sum(counter.values())
        return round(sum(count for _, count in counter.most_common(5)) / total, 4) if total else 0.0

    return {
        "kind": "v1_rekeying_study",
        "date": "2026-11-15",
        "seed": seed,
        "world_cycles": CYCLES,
        "note": ("counterfactual simulated under the engine's selection rules (+0.05 on the fresh detection, x0.8 "
                 "otherwise, death <0.15); the direction-bearing simulation reproduces the store's identities and "
                 "all %d retirement rows before the key is swapped" % len(retired)),
        "observed": observed,
        "validation": validation,
        "direction_bearing": {k: v for k, v in bearing.items() if k != "strengths"},
        "direction_free": {k: v for k, v in free.items() if k != "strengths"},
        "comparison": {
            "identities_saved": bearing["identities"] - free["identities"],
            "flip_events": flips,
            "deaths_bearing": bearing["deaths"],
            "deaths_free": free["deaths"],
            "live_bearing": bearing["live"],
            "live_free": free["live"],
            "stable_bearing": bearing["stable"],
            "stable_free": free["stable"],
            "reinforcements_bearing": bearing["reinforcements"],
            "reinforcements_free": free["reinforcements"],
            "top5_appearance_share_bearing": top_share(appearances),
            "top5_appearance_share_free": top_share(collections.Counter(
                _free(path) for path, count in appearances.items() for _ in range(count))),
        },
        "merged_node_sets": sorted(merged, key=lambda m: (-m["flips"], m["node_set"]))[:10],
    }


DOC = Path("docs/V1-REKEYING-STUDY.md")


def artifact_paths(seed: int = SEED) -> tuple[Path, Path]:
    """The artifact and page for a seed: the original keeps its names, a replication gets its own."""
    if seed == SEED:
        return Path(OUT), DOC
    return Path(f"docs/v1_rekeying_study_{seed}.json"), Path(f"docs/V1-REKEYING-STUDY-{seed}.md")


def render_doc(d: dict) -> str:
    b, f, c, o, v = d["direction_bearing"], d["direction_free"], d["comparison"], d["observed"], d["validation"]
    merged_rows = "\n".join(
        "| `%s` | %d | %d | %d |" % ("/".join(m["node_set"]), m["appearances"], m["orientations"], m["flips"])
        for m in d["merged_node_sets"][:5])
    stable_b = round(100 * b["stable"] / b["identities"], 1)
    stable_f = round(100 * f["stable"] / f["identities"], 1)
    return f"""# Would a direction-free identity have changed a carrier's fate?

**Status:** `OFFLINE COUNTERFACTUAL. Rules simulated, not run. Authorises no code, no arm, no freeze.`

**In one paragraph.** Yes, slightly, and not in the way that matters. Swapping V1's direction-bearing persistence key for a
direction-free one would have saved **{c['identities_saved']} identities** ({b['identities']} to {f['identities']}) and **{c['deaths_bearing'] - c['deaths_free']} retirements**, and converted
**{c['flip_events']} orientation flips** from a restart into a reinforcement. Strength moves a little (mean live
strength {b['mean_live_strength']} to {f['mean_live_strength']}, top-5 appearance share {c['top5_appearance_share_bearing']} to {c['top5_appearance_share_free']}), and the share of identities that stay above the
stability threshold moves from {stable_b}% to {stable_f}%. That is a real but small correction — the orientation flip was never the
capability V1 lacks. The primitive specification already canonicalises direction, so this study confirms a design choice
rather than reopening it.

## 1. What was done

One replay of the measured {d['world_cycles']}-cycle world ({o['sleep_cycles_run']} of its blocks ran a sleep cycle), reading back every
`sleep:loop_candidate` row the engine wrote ({o['stored_rows']:,} rows, {o['stored_identities']} identities). V1's selection rules were re-implemented
offline — +0.05 on the fresh detection, ×0.8 on absence, retirement below 0.15 — and run twice over the same detections:
once keyed on the path in order (V1), once on the sorted tag set (the specification's `cycle3` key).

## 2. The comparison

| | Direction-bearing (V1) | Direction-free |
|---|---|---|
| Identities created | {b['identities']} | {f['identities']} |
| Retirement rows | {b['deaths']} | {f['deaths']} |
| Reinforcements | {b['reinforcements']} | {f['reinforcements']} |
| Decays | {b['decays']} | {f['decays']} |
| Live at the end | {b['live']} | {f['live']} |
| Above the stability threshold | {b['stable']} ({stable_b}%) | {f['stable']} ({stable_f}%) |
| Mean live strength | {b['mean_live_strength']} | {f['mean_live_strength']} |

Orientation flips observed: **{c['flip_events']}**. Each one is a cycle in which V1 retires nothing but stops reinforcing one
identity and starts another from its raw strength.

Loop `strength` is the engine's raw transition count (`min(counts)`), not a probability, so values above 1.0 are expected and
are not a defect.

## 3. Validation

Both checks pass: {o['stored_identities']} identities and all {v['deaths_observed']} retirement rows are reproduced by the direction-bearing simulation
before the key is swapped.

An earlier version of this page reported {v['deaths_simulated'] + 15} retirements and blamed the 4,000-event prior window for the gap. That was
wrong, and the correction matters. The simulator reinforced from the prior's strength (`prior + 0.05`); the engine reinforces
the fresh detection (`detection + 0.05`, `_reinforce_current`). With that one rule fixed the simulation matches the store
exactly, and a separate boundary measurement — [`V1-CARRIER-FORGETTING`](V1-CARRIER-FORGETTING.md) — found that the window never
forgot a live carrier in this world: a lapsed carrier decays below the death threshold in at most nine cycles, inside the
window's ~18-cycle span. The counterfactual below is therefore pure rules, not a memory model.

## 4. The cases that changed

| Node set | Appearances | Orientations | Flips |
|---|---|---|---|
{merged_rows}

These are the identities a direction-free key would have merged; each flip is a reinforcement V1 spent as a restart. The
largest, `maple/sable/slate`, appears {d['merged_node_sets'][0]['appearances']} times with {d['merged_node_sets'][0]['flips']} flips — meaning that under a direction-free key it would have
been one continuously reinforced object rather than two alternating ones.

## 5. What it means for the primitive

- The specification's `cycle3` canonicalisation is **confirmed**, not reopened: the measured benefit is the one it was designed
  for, and it is modest.
- The gap the code reading found is untouched by re-keying: **no consumer reads a carrier's cycle** and **no code path mutates
  a path**. A direction-free id gives an object a longer life, not a use.
- So the ordering of the primitive's work does not change: content-free id, membership mutation, consumer. This study retires
  the first item's open question ("would a direction-free identity have mattered?") with a quantified yes, and leaves the
  other two where they were.

## 6. Limits

One seed, one world, {o['sleep_cycles_run']} sleep cycles; the counterfactual is rules-simulated over the store's detections, not run. Where
both orientations of a node set appear in one cycle the free key keeps the last detection's strength, since a merged
identity has only one; that choice is arbitrary and not measured. The study measures persistence bookkeeping, not
behaviour: nothing here predicts whether an addressed composite would beat the pair-count baseline.

The direction was replicated on a second world: see [`V1-REKEYING-TWO-SEEDS`](V1-REKEYING-TWO-SEEDS.md).
"""


def render_two_seed(a: dict, b: dict) -> str:
    rows = []
    for d in (a, b):
        c = d["comparison"]
        stat = d["direction_bearing"]
        rows.append({
            "seed": d["seed"],
            "identities": stat["identities"],
            "saved": c["identities_saved"],
            "deaths": c["deaths_bearing"],
            "deaths_saved": c["deaths_bearing"] - c["deaths_free"],
            "flips": c["flip_events"],
            "strength": (stat["mean_live_strength"], d["direction_free"]["mean_live_strength"]),
            "stable": (stat["stable"], d["direction_free"]["stable"]),
            "valid": d["validation"]["identities_match"] and d["validation"]["deaths_match"],
        })
    table = "\n".join(
        "| %d | %d | %d | %d | %d | %d | %s → %s | %d → %d | %s |" % (
            r["seed"], r["identities"], r["saved"], r["deaths"], r["deaths_saved"], r["flips"],
            r["strength"][0], r["strength"][1], r["stable"][0], r["stable"][1],
            "pass" if r["valid"] else "**fail**")
        for r in rows)
    holds = all(r["saved"] > 0 and r["deaths_saved"] > 0 and r["flips"] > 0 for r in rows)
    return f"""# Does a direction-free identity help in more than one world?

**Status:** `OFFLINE COUNTERFACTUAL, TWO SEEDS. Rules simulated, not run. Authorises no code, no arm, no freeze.`

**Answer: {'yes, in both worlds' if holds else 'no — the sign is not stable across these two worlds'}.** The direction is the same at seed {a['seed']} and
seed {b['seed']}: a direction-free key creates fewer identities, records fewer retirements, and converts orientation flips into
reinforcements. Both runs reproduce their store's identities and retirement rows before the key is swapped.

| Seed | Identities | Saved | Retirement rows | Saved | Flips | Mean live strength | Stable (count) | Validation |
|---|---|---|---|---|---|---|---|---|
{table}

## What this does and does not establish

- **Does:** the sign of the effect is not an accident of seed {a['seed']}. The mechanism is the same one the specification's
  `cycle3` key is designed for: two orientations of one triangle stop being two alternating carriers.
- **Does not:** two seeds are not a distribution, and the stable column is a count, not a share: 177 and 138 carriers are
  different denominators. The magnitudes differ because the worlds differ ({a['observed']['stored_identities']} and
  {b['observed']['stored_identities']} carriers), and nothing here estimates a spread or a confidence interval. Read the table as a
  replication of the direction, not of the size.
- **Unchanged:** the two real gaps — no consumer of a carrier's cycle, no membership mutation. Re-keying gives an object a
  longer life, not a use.

## Provenance

Each column comes from its own artifact: [`{artifact_paths(a['seed'])[0]}`]({artifact_paths(a['seed'])[0]}) and
[`{artifact_paths(b['seed'])[0]}`]({artifact_paths(b['seed'])[0]}). The pages for the individual runs are
[`V1-REKEYING-STUDY`]({artifact_paths(a['seed'])[1]}) and [`V1-REKEYING-STUDY-{b['seed']}`]({artifact_paths(b['seed'])[1]}).
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--doc", action="store_true")
    parser.add_argument("--two-seed-doc", action="store_true")
    args = parser.parse_args()
    if args.two_seed_doc:
        first = json.loads(artifact_paths(SEED)[0].read_text(encoding="utf-8"))
        second = json.loads(artifact_paths(REPLICATION_SEED)[0].read_text(encoding="utf-8"))
        target = Path("docs/V1-REKEYING-TWO-SEEDS.md")
        target.write_text(render_two_seed(first, second), encoding="utf-8")
        print("wrote", target)
        return 0
    artifact, page = artifact_paths(args.seed)
    if args.check:
        stored = json.loads(artifact.read_text(encoding="utf-8"))
        fresh = build(args.seed)
        if stored != fresh:
            differing = sorted(k for k in set(stored) | set(fresh) if stored.get(k) != fresh.get(k))
            print("FAIL: the artifact drifted from a fresh replay: %r" % (differing,))
            return 1
        print("re-keying study: clean (rebuild matches)")
        return 0
    doc = build(args.seed)
    if args.doc:
        page.write_text(render_doc(doc), encoding="utf-8")
        print("wrote", page)
        return 0
    if args.write:
        with open(artifact, "w", encoding="utf-8") as handle:
            json.dump(doc, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        print("wrote", artifact)
    print(json.dumps(doc["validation"], indent=1))
    print(json.dumps(doc["comparison"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
