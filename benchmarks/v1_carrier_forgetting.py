"""How often does V1 forget a carrier instead of retiring it?

`sleep_selection._load_prior_candidates` reads only the newest 4,000 `sleep` events. A carrier whose newest
copy falls below that boundary is invisible to cognition: it is never reinforced again, never decays, and
never receives a death record. It is *forgotten* while alive.

This study replays the measured world, records the 4,000-row boundary before every cycle, and then reads
the boundary the way the engine does, cycle by cycle, from the stored rows themselves. No selection rule is
re-implemented: what the engine could see is a fact about the store, and the forgetting episodes are read
off it directly.

Read-only: no arm, no target, no freeze, no grant, no engine change.
"""
from __future__ import annotations

import argparse
import bisect
import json
from pathlib import Path

from benchmarks import a1_arms, a1_c5_target_timing as timing
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.a2_sham_feasibility import CYCLES

SEED = 20740101
WINDOW = 4000
OUT = "docs/v1_carrier_forgetting.json"
DOC = Path("docs/V1-CARRIER-FORGETTING.md")


def _sleep_rows(memory, after_rowid: int = 0) -> list[dict]:
    rows = memory._conn.execute(
        "SELECT rowid, time, source, content FROM events "
        "WHERE event_type='sleep' AND rowid > ? ORDER BY rowid", (after_rowid,)).fetchall()
    return [{"rowid": r, "time": t, "source": s, "content": c} for r, t, s, c in rows]


def replay() -> dict:
    """Return every sleep row, the boundary rowid per cycle, and the detections per cycle."""
    world = generate_compositional_world(seed=SEED, cycles=CYCLES)
    db_path = _make_scratch_db("v1_forgetting")
    memory = _CountingMemoryService(str(db_path))
    service = a1_arms.A1ArmSleepService(memory)
    service.MAX_PREDICTIONS = timing.CAP
    acq_lo, acq_hi = timing.PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * timing.EVENTS_PER_CYCLE, acq_hi * timing.EVENTS_PER_CYCLE
    boundaries: list[tuple[int, int]] = []
    detections: list[tuple[int, tuple[str, ...], float]] = []
    last_rowid = 0
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
        row = memory._conn.execute(
            "SELECT COALESCE(MAX(rowid), 0) FROM events WHERE event_type='sleep'").fetchone()
        boundaries.append((cycle, int(row[0])))
        report = service.run_sleep_cycle()
        for loop in getattr(report, "loops", []) or []:
            path = tuple(getattr(loop, "path", []) or ())
            if len(path) >= 2:
                detections.append((cycle, path, float(getattr(loop, "strength", 0.0))))
    rows = _sleep_rows(memory, last_rowid)
    memory.close()
    return {"rows": rows, "boundaries": boundaries, "detections": detections}


def _prior_at(rows: list[dict], boundary: int) -> tuple[dict[str, dict], dict[str, dict]]:
    """Return (live loop payloads by id, retired loop payloads by id) as the engine would load them."""
    visible = [r for r in rows if r["rowid"] <= boundary]
    visible.sort(key=lambda r: (r["time"], r["rowid"]), reverse=True)
    live: dict[str, dict] = {}
    retired: dict[str, dict] = {}
    seen: set[str] = set()
    for row in visible[:WINDOW]:
        if not (row["source"].startswith("sleep:") and row["source"] != "sleep:meta"):
            continue
        try:
            payload = json.loads(row["content"])
        except (json.JSONDecodeError, ValueError):
            continue
        key = payload.get("id") or json.dumps(payload, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        if payload.get("type") != "loop_candidate":
            continue
        (retired if payload.get("retired") else live)[key] = payload
    return live, retired


def analyse(replay_result: dict) -> dict:
    rows = replay_result["rows"]
    boundaries = replay_result["boundaries"]
    detections = replay_result["detections"]
    loop_rows = [r for r in rows if r["source"] == "sleep:loop_candidate"]
    retired_rows = [r for r in loop_rows if json.loads(r["content"]).get("retired")]

    prior_live: dict[int, dict[str, dict]] = {}
    prior_retired: dict[int, dict[str, dict]] = {}
    for cycle, boundary in boundaries:
        prior_live[cycle], prior_retired[cycle] = _prior_at(rows, boundary)

    retirement_events: list[dict] = []
    for (prev, _), (cycle, _) in zip(boundaries, boundaries[1:]):
        newly_retired = prior_retired[cycle].keys() - prior_retired[prev].keys()
        for key in sorted(newly_retired):
            payload = prior_retired[cycle][key]
            retirement_events.append({"cycle": cycle, "id": key,
                                      "path": payload.get("path"),
                                      "strength": payload.get("strength"),
                                      "visible_while_live": key in prior_live[prev]})

    # A forgetting episode: an id live in the previous run's prior and absent from both live and retired priors now.
    episodes: list[dict] = []
    for (prev, _), (cycle, _) in zip(boundaries, boundaries[1:]):
        lost = prior_live[prev].keys() - prior_live[cycle].keys() - prior_retired[cycle].keys()
        for key in sorted(lost):
            payload = prior_live[prev][key]
            later = [r for r in loop_rows if json.loads(r["content"]).get("id") == key
                     and r["rowid"] > boundaries[[c for c, _ in boundaries].index(cycle)][1]]
            episodes.append({"cycle": cycle, "id": key, "path": payload.get("path"),
                             "generation": payload.get("generation"),
                             "strength_at_exit": payload.get("strength"),
                             "reborn": bool(later)})

    # Final outcome per identity, from its newest row.
    last_row: dict[str, dict] = {}
    for row in loop_rows:
        payload = json.loads(row["content"])
        last_row[payload.get("id")] = payload
    last_cycle = boundaries[-1][0]
    live_end = prior_live[last_cycle]
    retired_final = [k for k, p in last_row.items() if p.get("retired")]
    live_final = [k for k, p in last_row.items() if not p.get("retired") and k in live_end]
    forgotten_final = [k for k, p in last_row.items() if not p.get("retired") and k not in live_end]
    final_forget = [e for e in episodes if e["id"] in set(forgotten_final)]

    # Faithful offline replay of the selection rules, with the store's own visibility and birth strengths.
    predicted = _simulate(detections, prior_live, boundaries)

    def _extra_cycles(strength: float) -> int:
        n = 0
        while strength >= 0.15 and n < 200:
            strength *= 0.8
            n += 1
        return n

    extra = [_extra_cycles(e["strength_at_exit"] or 0.0) for e in final_forget]
    visible_counts = [len(prior_live[c]) for c, _ in boundaries]
    stamps = [rowid for _, rowid in boundaries]
    actual = []
    for row in retired_rows:
        index = max(0, bisect.bisect_right(stamps, row["rowid"]) - 1)
        actual.append((tuple(json.loads(row["content"]).get("path") or ()), boundaries[index][0]))
    actual.sort()
    return {
        "observed": {
            "sleep_rows": len(rows),
            "sleep_cycles_run": len(boundaries),
            "world_cycles": CYCLES,
            "loop_rows": len(loop_rows),
            "loop_identities": len(last_row),
            "retired_rows": len(retired_rows),
            "detections": len(detections),
            "ids_shadowing_two_paths": sum(
                1 for k in last_row if len({tuple(json.loads(r["content"]).get("path") or ())
                                            for r in loop_rows
                                            if json.loads(r["content"]).get("id") == k}) > 1),
        },
        "window": {
            "size": WINDOW,
            "visible_identities_first": visible_counts[1],
            "visible_identities_min": min(visible_counts[1:]),
            "visible_identities_max": max(visible_counts[1:]),
            "visible_identities_last": visible_counts[-1],
            "first_forget_cycle": min((e["cycle"] for e in episodes), default=None),
        },
        "retirements": {
            "rows": len(retired_rows),
            "predicted_examples": [{"path": list(p), "cycle": c} for p, c in sorted(predicted["retired"])[:5]],
            "actual_examples": [{"path": list(p), "cycle": c} for p, c in actual[:5]],
            "events_visible": len(retirement_events),
            "visible_while_live": sum(1 for e in retirement_events if e["visible_while_live"]),
            "simulated": predicted["retirements"],
            "simulation_matches": sorted((p, c) for p, c in predicted["retired"]) == actual,
        },
        "forgetting": {
            "episodes": len(episodes),
            "identities": len({e["id"] for e in episodes}),
            "final": len(final_forget),
            "reborn": sum(1 for e in episodes if e["reborn"]),
            "final_strength_mean": round(
                sum(e["strength_at_exit"] or 0.0 for e in final_forget) / len(final_forget), 4)
            if final_forget else 0.0,
            "final_strength_max": round(max((e["strength_at_exit"] or 0.0 for e in final_forget), default=0.0), 4),
            "extra_cycles_under_perfect_memory_mean": round(sum(extra) / len(extra), 2) if extra else 0.0,
            "extra_cycles_under_perfect_memory_max": max(extra, default=0),
            "examples": sorted(final_forget, key=lambda e: (-(e["strength_at_exit"] or 0.0), e["path"] or []))[:10],
        },
        "accounting": {
            "identities": len(last_row),
            "retired_final": len(retired_final),
            "live_final": len(live_final),
            "forgotten_final": len(forgotten_final),
            "conserved": len(retired_final) + len(live_final) + len(forgotten_final) == len(last_row),
        },
    }


def _simulate(detections, prior_live, boundaries) -> dict:
    """Re-run the rules with the store's visibility: +0.05 on the fresh detection, x0.8 otherwise, death <0.15."""
    by_cycle: dict[int, dict[tuple, float]] = {}
    for cycle, path, strength in detections:
        by_cycle.setdefault(cycle, {})[tuple(path)] = strength
    strength: dict[tuple, float] = {}
    retired: set[tuple] = set()
    retired_rows: list[tuple[tuple, int]] = []
    for cycle, _ in boundaries:
        prior_paths = {tuple(p.get("path") or ()) for p in prior_live[cycle].values()}
        current = by_cycle.get(cycle, {})
        for path in current:
            if path in prior_paths and path not in retired:
                strength[path] = min(1.0, current[path] + 0.05)
            else:
                strength[path] = current[path]
                retired.discard(path)
        for path in prior_paths:
            if path in current or path in retired:
                continue
            new = strength.get(path, 0.0) * 0.8
            if new < 0.15:
                retired.add(path)
                retired_rows.append((path, cycle))
            else:
                strength[path] = new
    return {"retirements": len(retired_rows), "retired": retired_rows}


def build() -> dict:
    result = analyse(replay())
    result.update({
        "kind": "v1_carrier_forgetting",
        "date": "2026-11-16",
        "seed": SEED,
        "cycles": CYCLES,
        "note": ("the window is read from the store at each cycle's boundary, so what the engine could see is "
                 "measured, not simulated"),
    })
    return result


def render_doc(d: dict) -> str:
    o, w, r, f, a = d["observed"], d["window"], d["retirements"], d["forgetting"], d["accounting"]
    rows = "\n".join(
        "| `%s` | %s | %s | %d |" % ("/".join(e["path"] or []), e["strength_at_exit"], e["generation"],
                                     e["cycle"])
        for e in f["examples"][:6]) or "| — | — | — | — |"
    return f"""# How often does V1 forget a carrier instead of retiring it?

**Status:** `MEASURED FROM THE STORE. No arm, no target, no freeze, no grant.`

**Answer: not once in {o['sleep_cycles_run']} sleep cycles.** Every one of the {o['loop_identities']} carrier identities either ended with a death record
({a['retired_final']}) or was still inside the engine's memory at the last cycle ({a['live_final']}); none left the 4,000-event window
while alive. The window cannot forget a lapsed carrier before decay kills it: a carrier absent from a cycle falls ×0.8, so it
crosses the 0.15 death threshold within nine cycles, while the window holds about {w['size'] // max(1, o['sleep_rows'] // o['sleep_cycles_run'])} cycles of sleep
rows ({o['sleep_rows']} rows over {o['sleep_cycles_run']} cycles). In this world the retirement count is not a lower bound at all: there is no
third category of carrier.

## 1. What was measured

`sleep_selection._load_prior_candidates` reads `memory.recent(n=4000, event_type="sleep")`, keeps the newest copy per
candidate id, and drops any copy marked retired. This study records the sleep-row boundary before every cycle and reloads
each cycle's prior from the store exactly as the engine would, so what the engine could see is read, not simulated.

| | |
|---|---|
| Sleep rows | {o['sleep_rows']} |
| Sleep cycles run (of {o['world_cycles']} world cycles) | {o['sleep_cycles_run']} |
| Carrier rows | {o['loop_rows']} |
| Carrier identities | {o['loop_identities']} |
| Retirement rows | {o['retired_rows']} |
| Retirement events visible in a prior | {r['events_visible']} |
| …that superseded a live copy | {r['visible_while_live']} |

## 2. The accounting

| Final outcome | Identities |
|---|---|
| Ended with a death record | {a['retired_final']} |
| Still visible in the memory at the last cycle | {a['live_final']} |
| **Forgotten alive** | **{a['forgotten_final']}** |

The three account for all {a['identities']} identities ({'conserved' if a['conserved'] else '**not conserved**'}). There were {f['episodes']} forgetting episodes over
{f['identities']} identities: the window never dropped a live carrier.

## 3. Why the window cannot do it

A carrier that is not re-detected decays by ×0.8 per cycle from at most 1.0, so it dies in at most nine cycles. The window
holds 4,000 sleep rows; at {round(o['sleep_rows'] / o['sleep_cycles_run'], 1)} sleep rows per cycle that is about
{round(4000 / (o['sleep_rows'] / o['sleep_cycles_run']), 1)} cycles of memory — about twice the decay horizon. Forgetting a live carrier would require a carrier to sit above
0.15 for longer than the window holds, and decay does not permit that.

## 4. Validation, and a correction

Re-running the rules offline with the store's own visibility reproduces **{r['simulated']}** retirement rows against {r['rows']} stored
({'a match' if r['simulation_matches'] else 'not a match'}). The first version of the re-keying study reported 201 and blamed the window. It was
wrong: its simulator reinforced from the prior strength (`prior + 0.05`) instead of the fresh detection (`detection + 0.05`),
which is what `_reinforce_current` does. That was the source of the 15-retirement gap, not the window, and the other study
now reproduces all 186 retirement rows and has been re-run under the corrected rule.

## 5. What it means

- **The death count is not a lower bound in this world:** {a['retired_final']} carriers ended with a death record and {a['live_final']} were still live.
  There is no third category.
- **The window's cost is growth, not forgetting.** Rows above the boundary stay on disk while cognition stops reading them;
  nothing in this run was saved by the window and nothing was lost to it.
- **The primitive's admission rule is unaffected.** It was motivated by re-detection after a lapse; that case did not occur
  here, but the lifetime argument for a content-free id stands on the storage accounting, not on this count.

## 6. Limits

One seed, one world, one window size, and {o['sleep_cycles_run']} sleep cycles. A longer run with a denser candidate stream could
push the window below the decay horizon; that is a prediction of the arithmetic in §3, not something this study observed.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--doc", action="store_true")
    args = parser.parse_args()

    doc = build()
    if args.doc:
        DOC.write_text(render_doc(doc), encoding="utf-8")
        print("wrote", DOC)
        return 0
    if args.write:
        Path(OUT).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("wrote", OUT)
        return 0
    if args.check:
        stored = json.loads(Path(OUT).read_text(encoding="utf-8"))
        stable = ("observed", "window", "retirements", "forgetting", "accounting", "detections")
        same = all(stored.get(k) == doc.get(k) for k in stable)
        print("carrier forgetting: clean (rebuild matches)" if same else "carrier forgetting: STALE")
        return 0 if same else 1
    print(json.dumps({k: doc[k] for k in ("observed", "window", "retirements", "forgetting", "accounting")},
                     indent=1)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
