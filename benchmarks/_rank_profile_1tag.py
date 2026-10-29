"""Quick diagnostic: for the 1-tag stimulus, what ranks do world-tag->world-tag
edges appear at in precedes vs. internal-vocabulary edges?

Runs seed 20261100 only and prints the full precedes rank profile annotated
with whether (src, dst) is a world edge, a vocabulary-to-world edge (internal
word -> world tag), or a world-to-vocabulary edge, or noise.
"""
from __future__ import annotations
import random, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from organica.memory import MemoryService
from organica.sleep import SleepService
from organica.paths import temp_db
from benchmarks.acquisition_compositional import (
    TAG_POOL, CELLS, TAGS_PER_CELL, flip_p, flip_q, LAW_R0, cell_name,
    PHASE_ACQUISITION,
)

WORLD_TAGS = set(TAG_POOL)
CYCLES_ACQ = 110
EVENTS_PER_CYCLE = 8

def run(seed=20261100):
    rng = random.Random(seed)
    pool = list(TAG_POOL)
    rng.shuffle(pool)
    cell_tags = {c: sorted(pool[i*TAGS_PER_CELL:(i+1)*TAGS_PER_CELL])
                 for i, c in enumerate(CELLS)}
    held = CELLS[rng.randrange(len(CELLS))]
    held_flip_p = flip_p(held)

    events, trainable = [], []
    state = CELLS[rng.randrange(len(CELLS))]
    acq_lo, acq_hi = PHASE_ACQUISITION

    for cycle in range(CYCLES_ACQ):
        for _ in range(EVENTS_PER_CYCLE):
            kind = rng.choices(("flip_p","flip_q"), weights=[0.65,0.35], k=1)[0]
            nxt = flip_p(state) if kind=="flip_p" else flip_q(state)
            tag = rng.choice(cell_tags[nxt])
            events.append(tag)
            in_acq = acq_lo*EVENTS_PER_CYCLE <= len(events)-1 < acq_hi*EVENTS_PER_CYCLE
            trainable.append(not (state==held and nxt==held_flip_p and in_acq))
            state = nxt

    world_edges = {(s,d) for c in CELLS for nc in (flip_p(c),flip_q(c))
                   for s in cell_tags[c] for d in cell_tags[nc]}

    db_path = temp_db(f"rankprobe_{seed}")
    mem = MemoryService(db_path)
    svc = SleepService(mem)
    for cycle in range(CYCLES_ACQ):
        for i in range(cycle*EVENTS_PER_CYCLE, (cycle+1)*EVENTS_PER_CYCLE):
            if trainable[i]:
                mem.store(events[i])
        svc.run_sleep_cycle()

    rows = mem._conn.execute(
        "SELECT tag_from, tag_to, count FROM precedes ORDER BY count DESC"
    ).fetchall()

    total = len(rows)
    print(f"Seed {seed}  |  held={cell_name(held)}->{cell_name(held_flip_p)}")
    print(f"Total precedes rows: {total}  |  world_edges: {len(world_edges)}")
    print(f"{'Rank':>5}  {'src':>12} -> {'dst':<12}  {'count':>6}  type")
    print("-"*65)

    world_tag_pair_ranks = []
    for rank, (src, dst, cnt) in enumerate(rows, 1):
        src_is_world = src in WORLD_TAGS
        dst_is_world = dst in WORLD_TAGS
        is_world_edge = (src, dst) in world_edges

        if src_is_world and dst_is_world:
            etype = "WORLD-EDGE" if is_world_edge else "world-pair (not edge)"
            world_tag_pair_ranks.append(rank)
        elif not src_is_world and dst_is_world:
            etype = "internal->world"
        elif src_is_world and not dst_is_world:
            etype = "world->internal"
        else:
            etype = "internal->internal"

        if rank <= 30 or is_world_edge and rank <= 50:
            print(f"{rank:>5}  {src:>12} -> {dst:<12}  {cnt:>6}  {etype}")

    print()
    first_world_pair = min(world_tag_pair_ranks) if world_tag_pair_ranks else None
    print(f"First world-tag pair at rank: {first_world_pair}")
    print(f"Total world-tag pair rows in top 50: {sum(1 for r in world_tag_pair_ranks if r<=50)}")
    print(f"Total world-tag pair rows in top 100: {sum(1 for r in world_tag_pair_ranks if r<=100)}")

    mem.close()
    db_path.unlink(missing_ok=True)

run(20261100)
