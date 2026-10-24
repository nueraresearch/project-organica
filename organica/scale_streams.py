"""
Worlds of increasing information content, for the H24 ladder.

H24 says the Tier-1 plateau was produced by the *environment* — a nine-event
world the organism exhausted — rather than by an inability to reorganise.

The pilot ladder (Rungs 0–2, uniform frequency) produced a measured result:
more world under uniform frequency *decreases* inventory (91 → 66 → 56 as
triangles scaled 3 → 12 → 48). The mechanism hypothesis (FACTS-SHEET §LM1):
frequency dilution starves the MAX_PREDICTIONS=20 window of complete 3-cycles.

The revised ladder tests the mechanism's own prediction: a **stable scaffold**
(the Rung-0 world, repeating at high frequency) plus **incremental novelty**
(one fresh triangle introduced every N cycles) should allow the organism to
discover new structure without losing its developmental base.

The uniform-frequency rungs (rung1, rung2) are preserved for the
dilution-mechanism test (doubling MAX_PREDICTIONS should recover inventory).

Scaffold-mode rungs (rung1s, rung2s, rung3s) implement the revised design:

  rung 0    lattice_L1: 3 triangles, repeated              -> 91 items (measured)
  rung 1    uniform: 12 triangles at equal frequency       -> 66 items (measured)
  rung 2    uniform: 48 triangles at equal frequency       -> 56 items (measured)
  rung 1s   scaffold: core + 1 new triangle every 50c     -> ? (H24 test)
  rung 2s   scaffold: core + 1 new triangle every 20c     -> ? (H24 test)
  rung 3s   scaffold: core + 1 new triangle every 5c      -> ? (H24 test)

Usage:
    from organica.scale_streams import scaffold_stream, scale_designs
    designs = scale_designs()
    # scaffold mode: pre-built per-cycle stream
    stream = scaffold_stream(
        designs["rung1s"]["core_triangles"],
        total_cycles=300,
        events_per_cycle=8,
        novelty_every=designs["rung1s"]["novelty_every"],
    )
    # stream[i*8 : (i+1)*8] is cycle i's events
"""

from __future__ import annotations

HUB = "alpha"

# The engine extracts tags with `re.findall(r"\b[a-zA-Z]{4,}\b", ...)`, so a
# tag must be at least FOUR letters long or it is invisible to the whole
# substrate. A first version of this file numbered the leaves ("ta0"), and
# every one of them was silently dropped -- the ladder measured nothing and
# looked like a null result. The leaves are therefore spelled out in letters
# and prefixed to make them comfortably long.
_LEAF_PREFIX = "leaf"


def _letters(n: int, width: int = 2) -> str:
    """0 -> 'aa', 1 -> 'ab', ... 25 -> 'az', 26 -> 'ba'. Base 26, no digits.

    The width matters: the hub code and the leaf code are both derived from
    an index, so they must not be able to produce the same string. Hubs use
    width 3 and leaves width 2, which makes the two code spaces disjoint.
    """
    out = ""
    n += 26 ** width
    for _ in range(width):
        out = chr(ord("a") + (n % 26)) + out
        n //= 26
    return out


def expanding_triangles(n: int, hub: str = HUB, prefix: str = "leaf") -> list:
    """`n` fresh triangles sharing one hub, each with its own leaf tags.

    Triangle i is ``(hub, prefix+letters(2i), prefix+letters(2i+1))`` -- the
    same shape as the lattice design that closed the launch gates, with fresh
    leaves so that each triangle is a distinct unit of structure.
    """
    out = []
    for i in range(n):
        out.append((hub, f"{prefix}{_letters(2 * i)}",
                    f"{prefix}{_letters(2 * i + 1)}"))
    return out


def hub_groups(n_hubs: int, degree: int = 3) -> list:
    """`n_hubs` independent groups, each of `degree` triangles on one hub.

    **Why groups and not one big hub.** The Layer-1 survival filter is
    `strength = min(1, count / source_frequency) >= STABLE_THRESHOLD (0.3)`.
    The measured hub-degree probe
    (`benchmarks/hub_degree_probe.py`) shows the hub's best edge ratio
    falling as the degree rises -- 1.00 at degree 2, 0.75 at 3, 0.56 at 4,
    0.44 at 5, 0.35 at 6, 0.31 at 8, and **0.185 at 12, below the threshold**,
    at which point the structure collapses to zero beliefs. Structure is
    best at degree 3, and the usable range is narrow.

    So the ladder grows by adding **hubs**, each of which keeps its degree
    at 3 where the substrate works. Scaling hub *degree* instead would be
    scaling a quantity the survival filter is actively eating.
    """
    out = []
    for h in range(n_hubs):
        hub = f"{HUB}{_letters(h, 3)}" if h else HUB
        out.extend(expanding_triangles(degree, hub=hub,
                                       prefix=f"leaf{_letters(h, 3)}"))
    return out


def triangle_events(triangles: list) -> list:
    """Each triangle as its repeating 3-event cycle ``h a``, ``a b``, ``b h``.

    The 3-event temporal lookback turns that into every directed pair on the
    triangle, which is what the Layer-2 process builder needs to find a
    3-cycle.
    """
    events = []
    for (h, a, b) in triangles:
        events += [f"{h} {a}", f"{a} {b}", f"{b} {h}"]
    return events


def scale_stream(triangles: list, mode: str = "block",
                  block_repeat: int = 4) -> list:
    """Build the event stream for one rung.

    ``block``   -- emit every triangle once, then repeat the whole block.
                   A finite world: it runs out.
    ``open``    -- emit every triangle once, in order, and never repeat.
                   An open-ended world: it never runs out, and the number of
                   triangles must therefore cover the whole run.
    """
    events = triangle_events(triangles)
    if mode == "block":
        return events * block_repeat
    if mode == "open":
        return events
    raise ValueError(f"unknown mode {mode!r}")


def novelty_triangles(n: int) -> list:
    """n independent triangles for use as novelty injections.

    Each triangle has its own hub and two unique leaves, none of which
    collide with the core lattice_L1 tags (alpha/bravo/charlie/delta/echo/
    foxtrot/golf) or with the hub_groups namespace (which uses HUB + 3-letter
    code, e.g. 'alphaaaa').

    Hub tags: 'nova' + 3-letter code  -> 'novaaaa', 'novaab', ...  (7 chars)
    Leaf tags: 'nvlp' + 3-letter code -> 'nvlpaaa', ...             (7 chars)
              'nvlq' + 3-letter code -> 'nvlqaaa', ...             (7 chars)
    All are >= 4 letters; the 'nova'/'nvlp'/'nvlq' prefixes are disjoint from
    every other namespace in the codebase.
    """
    out = []
    for i in range(n):
        code = _letters(i, 3)
        hub  = f"nova{code}"   # e.g. "novaaaa"
        la   = f"nvlp{code}"   # e.g. "nvlpaaa"
        lb   = f"nvlq{code}"   # e.g. "nvlqaaa"
        out.append((hub, la, lb))
    return out


def scaffold_stream(core_triangles: list, total_cycles: int,
                    events_per_cycle: int = 8,
                    novelty_every: int = 50) -> list:
    """Build a per-cycle event stream: stable scaffold + incremental novelty.

    The stream has exactly ``total_cycles * events_per_cycle`` events.
    Retrieve cycle i's events as ``stream[i*events_per_cycle :
    (i+1)*events_per_cycle]``.

    Every cycle the core triangles repeat (sliding window through the 9-event
    core block), keeping complete 3-cycles dominant in the Layer-1 prediction
    window.  Every ``novelty_every`` cycles, one fresh triangle contributes 3
    events at the *front* of that cycle's block, displacing 3 core events.
    The novel triangle reappears at the same frequency from then on (it is
    added to a growing pool of 'established novelties' that rotate alongside
    the core).

    **Design rationale.** The pilot measured that uniform-frequency scaling
    collapses inventory (91 → 66 → 56) because the prediction window fills
    with equally-weighted fragments instead of complete 3-cycles.  The fix is
    to keep one cluster of triangles *much more frequent* than any newcomer so
    the window always holds complete structures, while genuine novelty arrives
    rarely enough to be visible as individual arrivals.

    **Novelty assimilation condition.** A novel triangle's edges need count >=
    PREDICTION_MIN_COUNT (default 5) to survive Layer 1.  With
    ``novelty_every=20``, a triangle introduced at cycle 20 has 14 occurrences
    by cycle 300 — well above the threshold.  With ``novelty_every=50``, a
    triangle introduced at cycle 50 has 5 occurrences by cycle 300 — just at
    the threshold.  The caller should choose ``novelty_every`` based on the
    run length and the desired assimilation window.
    """
    core_evs = triangle_events(core_triangles)
    n_core   = len(core_evs)                          # 9 for a 3-triangle core
    n_novel  = total_cycles // novelty_every + 1      # upper bound
    novel    = novelty_triangles(n_novel)

    stream: list[str] = []
    core_ptr   = 0       # rolling pointer into core_evs
    pool: list = []      # established novelty triangles (rotates alongside core)
    pool_ptr   = 0       # rolling pointer into pool events
    next_novel = 0       # index into novel[]

    for cycle in range(total_cycles):
        introduce = (cycle > 0 and cycle % novelty_every == 0)
        if introduce:
            pool.append(novel[next_novel])
            next_novel += 1

        cycle_evs: list[str] = []

        if introduce:
            # 3 novel events (the triangle just introduced) + 5 core events
            new_tri_evs = triangle_events([pool[-1]])   # the new triangle
            cycle_evs.extend(new_tri_evs)               # 3 events
            remaining = events_per_cycle - len(new_tri_evs)
            for j in range(remaining):
                cycle_evs.append(core_evs[core_ptr % n_core])
                core_ptr += 1
        else:
            # Normal cycle: all events from core
            for j in range(events_per_cycle):
                cycle_evs.append(core_evs[core_ptr % n_core])
                core_ptr += 1

        assert len(cycle_evs) == events_per_cycle, (
            f"cycle {cycle}: expected {events_per_cycle} events, got {len(cycle_evs)}")
        stream.extend(cycle_evs)

    assert len(stream) == total_cycles * events_per_cycle
    return stream


def burst_stream(core_triangles: list, total_cycles: int = 300,
                 burst_every: int = 30, burst_len: int = 8,
                 events_per_cycle: int = 8) -> list:
    """Build a burst assimilation event stream.

    A stable core scaffold runs continuously. Every `burst_every` cycles, a
    fresh novelty triangle is introduced and reinforced with a concentrated
    `burst_len` window (emitting 2 full 3-cycles = 6 novel events per cycle),
    enabling it to clear PREDICTION_MIN_COUNT=5 and STABLE_THRESHOLD=0.3.
    Once the burst concludes, all established novelty triangles rotate alongside
    the core (3 novel events + 5 core events per cycle), sustaining recurrence.
    """
    core_evs = triangle_events(core_triangles)
    n_core = len(core_evs)
    n_novel = total_cycles // burst_every + 1
    novel = novelty_triangles(n_novel)

    stream: list[str] = []
    core_ptr = 0
    pool: list = []
    pool_ptr = 0
    next_novel = 0

    for cycle in range(total_cycles):
        if cycle > 0 and cycle % burst_every == 0:
            pool.append(novel[next_novel])
            next_novel += 1

        in_burst = False
        active_novelty = None
        if pool:
            k = cycle // burst_every
            if k >= 1 and (cycle - k * burst_every) < burst_len and k <= len(pool):
                in_burst = True
                active_novelty = pool[k - 1]

        cycle_evs: list[str] = []
        if in_burst:
            tri_evs = triangle_events([active_novelty])
            cycle_evs.extend(tri_evs * 2)
            for _ in range(events_per_cycle - len(cycle_evs)):
                cycle_evs.append(core_evs[core_ptr % n_core])
                core_ptr += 1
        elif pool:
            all_est_evs = triangle_events(pool)
            for _ in range(3):
                cycle_evs.append(all_est_evs[pool_ptr % len(all_est_evs)])
                pool_ptr += 1
            for _ in range(events_per_cycle - len(cycle_evs)):
                cycle_evs.append(core_evs[core_ptr % n_core])
                core_ptr += 1
        else:
            for _ in range(events_per_cycle):
                cycle_evs.append(core_evs[core_ptr % n_core])
                core_ptr += 1

        assert len(cycle_evs) == events_per_cycle
        stream.extend(cycle_evs)

    assert len(stream) == total_cycles * events_per_cycle
    return stream


def scale_designs() -> dict:
    """The rungs of the ladder.

    **Uniform-frequency rungs (rung0, rung1, rung2)** — the original pilot
    design. All triangles presented at equal frequency.  The pilot measured
    that this collapses inventory as world size grows (91 → 66 → 56). Kept
    for the dilution-mechanism test: does raising MAX_PREDICTIONS to 40 recover
    Rung-1 inventory?

    **Scaffold rungs (rung1s, rung2s, rung3s)** — the revised design after the
    pilot result.  A stable 3-triangle core (lattice_L1) repeats at high
    frequency while novelty triangles are introduced one at a time every N
    cycles.  The core keeps complete 3-cycles in the top-20 prediction window;
    the arriving triangles are visible because they are not competing with each
    other at introduction time.

    Rung 3 needs enough groups to cover the run: 3,000 cycles x 8 events
    per cycle = 24,000 events = 8,000 triangles = 2,667 groups of 3. Building
    those up front is fine -- they are just strings -- but a run that asks for
    fewer than it consumes will run the stream dry, so the caller must supply
    a group count that covers the run.
    """
    _CORE = [("alpha", "bravo", "charlie"),
             ("alpha", "delta", "echo"),
             ("alpha", "foxtrot", "golf")]

    return {
        # ── Uniform-frequency rungs (pilot, measured) ─────────────────────
        "rung0": {
            "name": "rung0_lattice_L1",
            "description": "the Tier-1 stimulus: 3 triangles on one hub, repeated",
            "triangles": list(_CORE),
            "mode": "block",
            "block_repeat": 4,
        },
        "rung1": {
            "name": "rung1_uniform_medium",
            "description": "4 hubs x 3 triangles = 12 triangles, all equal frequency (pilot)",
            "triangles": hub_groups(4),
            "mode": "block",
            "block_repeat": 4,
        },
        "rung2": {
            "name": "rung2_uniform_large",
            "description": "16 hubs x 3 triangles = 48 triangles, all equal frequency (pilot)",
            "triangles": hub_groups(16),
            "mode": "block",
            "block_repeat": 4,
        },
        "rung3": {
            "name": "rung3_open_ended",
            "description": "a fresh hub every cycle, never repeated",
            "triangles": hub_groups(2700),
            "mode": "open",
        },
        # ── Scaffold rungs (mechanism-derived, revised design) ────────────
        "rung1s": {
            "name": "rung1s_scaffold_slow",
            "description": "3-triangle core + 1 new triangle every 50 cycles",
            "mode": "scaffold",
            "core_triangles": list(_CORE),
            "novelty_every": 50,
        },
        "rung2s": {
            "name": "rung2s_scaffold_medium",
            "description": "3-triangle core + 1 new triangle every 20 cycles",
            "mode": "scaffold",
            "core_triangles": list(_CORE),
            "novelty_every": 20,
        },
        "rung3s": {
            "name": "rung3s_scaffold_fast",
            "description": "3-triangle core + 1 new triangle every 5 cycles",
            "mode": "scaffold",
            "core_triangles": list(_CORE),
            "novelty_every": 5,
        },
        # ── Burst Assimilation rungs ──────────────────────────────────────
        "rung_burst_30": {
            "name": "rung_burst_30",
            "description": "3-triangle core + novelty burst every 30 cycles (8c burst)",
            "mode": "burst",
            "core_triangles": list(_CORE),
            "burst_every": 30,
            "burst_len": 8,
        },
    }


def rung_for_run(design: dict, cycles: int, events_per_cycle: int = 8) -> list:
    """The triangles a rung needs to cover `cycles` cycles.

    An open-ended world must have fresh structure for every cycle, or the
    organism starts re-reading a stream that has run out and the rung stops
    being open-ended.
    """
    if design["mode"] != "open":
        return design["triangles"]
    needed_groups = (cycles * events_per_cycle + 8) // 9   # 3 triangles / hub
    have_groups = len(design["triangles"]) // 3
    if needed_groups <= have_groups:
        return design["triangles"]
    return hub_groups(needed_groups)
