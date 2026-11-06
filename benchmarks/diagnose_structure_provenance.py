"""Store-time observer: which structure type contributes each asserted edge, by arm and by seed group.

The engine writes one `event_type="sleep"` row per cycle carrying the cycle's living candidates; `structure_edges`
aggregates all of them into w(a,b). This wraps `MemoryService.store` and captures those payloads as they are written, so
attribution is a store-time observation of the same candidates the readout aggregates -- not a post-hoc DB replay, which
pruning would make unsound (AGENTS rule 17(d)).

Fidelity is checked three ways, and nothing is interpreted unless all three hold: the replay must reproduce the stored
`asserted`/`covered`/digest; the reconstructed edge set must equal `structure_edges` on the database's own candidate
list; and the per-edge weights must agree.

Replays the same 10 seeds x 2 arms as §8.12 (seeds and uplift matching read from that artifact). Writes
`docs/gate13_structure_provenance.json`.
"""
from __future__ import annotations

import hashlib
import json
import statistics as st
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService
from benchmarks.acquisition_harness import _make_scratch_db
from benchmarks.acquisition_compositional import generate_compositional_world, PHASE_ACQUISITION
from benchmarks.acquisition_runner import _world_compositional_edges, structure_edges, EVENTS_PER_CYCLE
from benchmarks.run_ratio_admission_arm import make_arm
from benchmarks.run_paired_capacity_test import NON_VOCAB_MARKERS

BLOCK = json.loads((REPO / "docs/gate13_ratio_block2.json").read_text())
PATH_ART = json.loads((REPO / "docs/gate13_assertion_path.json").read_text())
IDX = {(r["arm"], r["cap"], r["seed"]): r for r in BLOCK["raw"]}


def edge_items(c):
    """The (edge, weight) pairs a candidate contributes -- same branches as structure_edges, tagged by type."""
    t = c.get("type", "")
    out = []
    if t in ("concept_candidate", "phrase_candidate"):
        m = list(c.get("members") or [])
        for i, a in enumerate(m):
            for b in m[i + 1:]:
                out += [((a, b), 1.0), ((b, a), 1.0)]
    elif t == "loop_candidate":
        p = list(c.get("path") or [])
        for a, b in zip(p, p[1:]):
            out += [((a, b), 1.0), ((b, a), 1.0)]
    elif t == "prediction_candidate":
        s, tg = c.get("source"), c.get("target")
        ev = c.get("evidence") or {}
        if s and tg:
            out.append(((s, tg), float(ev.get("temporal_count") or 1.0)))
    elif t == "hypothesis":
        s, e = c.get("subject"), c.get("expectation")
        if s and e:
            out.append(((s, e), 1.0))
    elif t == "process_candidate":
        cyc = list(c.get("cycle") or [])
        for i, a in enumerate(cyc):
            out.append(((a, cyc[(i + 1) % len(cyc)]), 1.0))
    elif t == "workflow_concept":
        comps = list(c.get("components") or [])
        for a, b in zip(comps, comps[1:]):
            out.append(((a, b), 1.0))
    elif t == "dream":
        p = list(c.get("path_or_context") or [])
        for a, b in zip(p, p[1:]):
            out.append(((a, b), 1.0))
    return out


def payloads_to_candidates(payloads):
    """Reconstruct the live candidate list exactly as `_load_prior_candidates` would: newest generation per key, death
    records dropped. Each sleep row is one candidate dict written with source `sleep:<type>`."""
    by_key = {}
    for src, content in payloads[-4000:]:      # `_load_prior_candidates` reads only the newest 4000 sleep rows
        if not (src and src.startswith("sleep:") and src != "sleep:meta"):
            continue
        try:
            c = json.loads(content)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(c, dict) or not c.get("type"):
            continue
        key = c.get("id") or json.dumps(c, sort_keys=True)
        by_key[key] = c          # payloads are chronological, so the last copy is the newest
    return [c for c in by_key.values() if not c.get("retired")]


def attribute(cands):
    contrib = {}
    for c in cands:
        t = c.get("type", "")
        for e, w in edge_items(c):
            d = contrib.setdefault(e, {})
            d[t] = d.get(t, 0.0) + w
    return contrib


def replay(arm, cap, seed):
    world = generate_compositional_world(seed=seed, cycles=300, events_per_cycle=EVENTS_PER_CYCLE)
    events, trainable = world["events"], world["trainable"]
    vocab = set(world["tag_to_cell"])
    world_edges = _world_compositional_edges(world)
    acq_lo, acq_hi = PHASE_ACQUISITION

    path = _make_scratch_db(f"prov_{arm}_{cap}_{seed}")
    mem = MemoryService(str(path))
    svc = make_arm(mem, arm, cap)
    payloads = []                                  # (source, content) for every sleep row, in write order
    orig_store = mem.store

    def store(content, *a, **kw):
        if kw.get("event_type", (a[0] if a else "observe")) == "sleep":
            payloads.append((kw.get("source"), content))
        return orig_store(content, *a, **kw)

    mem.store = store
    try:
        for ci in range(acq_hi):
            in_acq = acq_lo <= ci < acq_hi
            for i in range(ci * EVENTS_PER_CYCLE, (ci + 1) * EVENTS_PER_CYCLE):
                if in_acq and not trainable[i]:
                    continue
                mem.store(events[i], event_type="observe", source="env_acq" if in_acq else "env")
            svc.run_sleep_cycle()

        db_cands = svc._load_prior_candidates()
        asserted = {(u, v) for u, tg in structure_edges(db_cands).items() for v in tg
                    if u in vocab and v in vocab and u not in NON_VOCAB_MARKERS and v not in NON_VOCAB_MARKERS}
        covered = asserted & world_edges
        digest = hashlib.sha1("\n".join(sorted(f"{u}>{v}" for u, v in asserted)).encode()).hexdigest()[:16]
    finally:
        mem.close()
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass

    recon = payloads_to_candidates(payloads)
    contrib = attribute(recon)
    db_map = structure_edges(db_cands)
    db_edges = {(u, v) for u, tg in db_map.items() for v in tg}
    edge_ok = set(contrib) == db_edges
    weight_ok = edge_ok and all(abs(sum(contrib[e].values()) - db_map[e[0]][e[1]]) < 1e-9 for e in contrib)

    by_type, sole_type = {}, {}
    for e in covered:
        ts = contrib.get(e, {})
        for t in ts:
            by_type[t] = by_type.get(t, 0) + 1
        if len(ts) == 1:
            t = next(iter(ts))
            sole_type[t] = sole_type.get(t, 0) + 1
    return {
        "arm": arm, "cap": cap, "seed": seed, "payloads": len(payloads),
        "reconstructed_candidates": len(recon),
        "db_candidates": len(db_cands),
        "verified": {"asserted": len(asserted), "covered": len(covered), "hash": digest},
        "edges_match_structure_edges": edge_ok, "weights_match_structure_edges": weight_ok,
        "covered": len(covered),
        "covered_by_type": dict(sorted(by_type.items())),
        "covered_sole_type": dict(sorted(sole_type.items())),
        "covered_multi_type": sum(1 for e in covered if len(contrib.get(e, {})) > 1),
        "types_from_window": ["prediction_candidate"],
    }


def main():
    failing = PATH_ART["seeds_failing"]
    matched = {int(k): v for k, v in PATH_ART["matched"].items()}
    plan = [("fail", s) for s in sorted(failing)] + [("match", m) for m in [matched[s] for s in sorted(failing)]]
    cells, bad = {}, []
    for group, seed in plan:
        for arm in ("C", "R"):
            r = replay(arm, 20, seed)
            want = IDX[(arm, 20, seed)]
            r["group"] = group
            r["replay_matches_artifact"] = (
                r["verified"]["asserted"] == want["asserted"]
                and r["verified"]["covered"] == want["covered"]
                and r["verified"]["hash"] == want["asserted_hash"])
            cells[f"{seed}_{arm}"] = r
            if not (r["replay_matches_artifact"] and r["edges_match_structure_edges"] and r["weights_match_structure_edges"]):
                bad.append(f"{seed}_{arm}")
            print(f"{group} {seed} {arm}: covered {r['covered']} types {r['covered_by_type']} "
                  f"multi {r['covered_multi_type']} verified={r['replay_matches_artifact']} "
                  f"edges={r['edges_match_structure_edges']} weights={r['weights_match_structure_edges']}", flush=True)

    types = sorted({t for c in cells.values() for t in c["covered_by_type"]})
    summary = {}
    for group in ("fail", "match"):
        summary[group] = {}
        for arm in ("C", "R"):
            rows = [c for c in cells.values() if c["group"] == group and c["arm"] == arm]
            summary[group][arm] = {t: round(st.fmean(r["covered_by_type"].get(t, 0) for r in rows), 2) for t in types}
            summary[group][arm]["covered_total"] = round(st.fmean(r["covered"] for r in rows), 2)
            summary[group][arm]["multi_type"] = round(st.fmean(r["covered_multi_type"] for r in rows), 2)
    art = {
        "what": "store-time attribution of asserted world edges to structure type, block-2 cap 20",
        "status": "EXPLORATORY. Observes the same payloads structure_edges aggregates; verified against it three ways.",
        "verification_failures": bad,
        "types_seen": types,
        "note": ("`structure_edges` has eight type branches, not six: concept_candidate and phrase_candidate share one "
                 "branch; loop_candidate, prediction_candidate, hypothesis, process_candidate, workflow_concept and "
                 "dream are the others. Only prediction_candidate is the object the admission window ranks."),
        "summary": summary,
        "cells": cells,
    }
    (REPO / "docs/gate13_structure_provenance.json").write_text(json.dumps(art, indent=2) + "\n")
    print("\nverification failures:", bad)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"elapsed {time.time() - t0:.0f}s")
