#!/usr/bin/env python3
"""
Organica Organism Health Dashboard
-----------------------------------
Reads organica.log and produces a full health report covering:

  Population Metrics   — what exists right now
  Evolution Metrics    — birth/death rates per cycle
  Epistemic Metrics    — belief dynamics
  Cognitive Metrics    — lineage depth, memory growth
  Belief Revision      — "what changed its mind?"

Run:
  python dashboard.py              # reads organica.log in cwd
  python dashboard.py path/to/organica.log
"""

import json
import sys
import pathlib
from collections import defaultdict

# ---------------------------------------------------------------------------
# Load log
# ---------------------------------------------------------------------------
log_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("organica.log")
if not log_path.exists():
    print(f"ERROR: log file not found: {log_path}")
    sys.exit(1)

cycles = []
for line in log_path.read_text(encoding="utf-8").splitlines():
    idx = line.find("{")
    if idx != -1:
        try:
            cycles.append(json.loads(line[idx:]))
        except Exception:
            pass

if not cycles:
    print("No cycle data found in log.")
    sys.exit(0)

# ---------------------------------------------------------------------------
# Population Metrics (current snapshot)
# ---------------------------------------------------------------------------
last = cycles[-1]
first = cycles[0]

print("=" * 60)
print("  ORGANICA ORGANISM HEALTH DASHBOARD")
print("=" * 60)
print(f"  Log file   : {log_path}")
print(f"  Cycles     : {len(cycles)}  ({first['timestamp']} → {last['timestamp']})")
print(f"  Total composites generated: {last['total_composites']:,}")
print()

print("── POPULATION (current) ─────────────────────────────────")
pop_keys = ["concepts", "predictions", "loops", "hypotheses",
            "theories", "questions", "dreams", "investigations", "experiments"]
for k in pop_keys:
    val = last.get(k, 0)
    bar = "█" * min(val, 40)
    print(f"  {k:<16} {val:>4}  {bar}")
print()

# ---------------------------------------------------------------------------
# Evolution Metrics — birth/death per cycle
# ---------------------------------------------------------------------------
print("── EVOLUTION (per-cycle averages) ───────────────────────")

births = [c.get("composites_created", 0) for c in cycles]
deaths = [c.get("candidates_pruned", 0) for c in cycles]
strengthened = [c.get("candidates_strengthened", 0) for c in cycles]

avg_birth = sum(births) / len(births)
avg_death = sum(deaths) / len(deaths)
avg_strengthen = sum(strengthened) / len(strengthened)
peak_birth = max(births)
peak_death = max(deaths)

# Extinction rate = cycles where pruning > birth
extinction_cycles = sum(1 for b, d in zip(births, deaths) if d > b)
extinction_rate = extinction_cycles / len(cycles) * 100

print(f"  Avg births/cycle       : {avg_birth:.1f}  (peak: {peak_birth})")
print(f"  Avg deaths/cycle       : {avg_death:.1f}  (peak: {peak_death})")
print(f"  Avg reinforcements     : {avg_strengthen:.1f}")
print(f"  Extinction rate        : {extinction_rate:.1f}% of cycles (death > birth)")
print()

# ---------------------------------------------------------------------------
# Hypothesis trajectory — track count over time as proxy for belief revision
# ---------------------------------------------------------------------------
print("── EPISTEMIC METRICS (hypothesis dynamics) ──────────────")

hyp_counts = [c.get("hypotheses", 0) for c in cycles]
max_hyp = max(hyp_counts)
min_hyp = min(hyp_counts)
# Find first cycle where hypothesis count dropped after reaching max
peak_cycle = hyp_counts.index(max_hyp)
belief_death_cycles = []
for i in range(1, len(hyp_counts)):
    if hyp_counts[i] < hyp_counts[i - 1]:
        belief_death_cycles.append((i, hyp_counts[i - 1], hyp_counts[i]))

print(f"  Hypothesis count range : {min_hyp} → {max_hyp} (peak at cycle {peak_cycle})")
print(f"  Belief collapse events : {len(belief_death_cycles)}")
if belief_death_cycles:
    print(f"  Notable collapses:")
    for cyc, before, after in belief_death_cycles[:10]:
        ts = cycles[cyc].get("timestamp", "?")
        print(f"    Cycle {cyc:>4} ({ts}): hypotheses {before} → {after}  (-{before - after})")

# Dream count trajectory
dream_counts = [c.get("dreams", 0) for c in cycles]
first_dream_cycle = next((i for i, d in enumerate(dream_counts) if d > 0), None)
print(f"\n  First dream appeared   : cycle {first_dream_cycle} ({cycles[first_dream_cycle]['timestamp'] if first_dream_cycle else 'never'})")

# Investigation backlog trend
inv_counts = [c.get("investigations", 0) for c in cycles]
first_inv_cycle = next((i for i, v in enumerate(inv_counts) if v > 0), None)
print(f"  First investigation    : cycle {first_inv_cycle} ({cycles[first_inv_cycle]['timestamp'] if first_inv_cycle else 'never'})")
print()

# ---------------------------------------------------------------------------
# Cognitive Metrics — memory growth, loop detection
# ---------------------------------------------------------------------------
print("── COGNITIVE METRICS ────────────────────────────────────")

loop_counts = [c.get("loops", 0) for c in cycles]
first_loop = next((i for i, v in enumerate(loop_counts) if v > 0), None)
max_loops = max(loop_counts)

# Memory growth rate (composites per cycle, sliding window last 50)
recent = cycles[-50:]
recent_growth = sum(c.get("composites_created", 0) for c in recent) / len(recent)
early = cycles[:50]
early_growth = sum(c.get("composites_created", 0) for c in early) / len(early)

print(f"  First behavioral loop  : cycle {first_loop}")
print(f"  Max concurrent loops   : {max_loops}")
print(f"  Memory growth (early)  : {early_growth:.1f} composites/cycle (cycles 0-49)")
print(f"  Memory growth (recent) : {recent_growth:.1f} composites/cycle (last 50 cycles)")
growth_trend = "accelerating" if recent_growth > early_growth else "stabilizing/decelerating"
print(f"  Growth trend           : {growth_trend}")
print()

# ---------------------------------------------------------------------------
# "What changed its mind?" — Belief revision narrative
# ---------------------------------------------------------------------------
print("── BELIEF REVISION NARRATIVE ────────────────────────────")
print("  (Tracking hypothesis count as proxy for confidence changes)")
print()

if not belief_death_cycles:
    print("  No belief collapses detected yet.")
    print("  Hypothesis count has been monotonically stable or growing.")
    print()
    print("  >> This is an early warning sign of potential echo-chamber dynamics.")
    print("  >> Consider injecting contradictory event streams to stress-test.")
else:
    for cyc, before, after in belief_death_cycles[:5]:
        ts = cycles[cyc].get("timestamp", "?")
        composites_at = cycles[cyc].get("total_composites", "?")
        pruned_at = cycles[cyc].get("candidates_pruned", 0)
        print(f"  Cycle {cyc} | {ts}")
        print(f"    Hypotheses: {before} → {after}  (dropped {before - after})")
        print(f"    Composites at this point: {composites_at:,}")
        print(f"    Candidates pruned this cycle: {pruned_at}")
        print()

# ---------------------------------------------------------------------------
# Key open questions
# ---------------------------------------------------------------------------
print("── STRONG HYPOTHESES KILLED (count) ─────────────────────")
total_killed = sum(max(0, b - a) for b, a in zip(hyp_counts, hyp_counts[1:]))
total_born = sum(max(0, a - b) for b, a in zip(hyp_counts, hyp_counts[1:]))
print(f"  Total hypothesis births   : {total_born}")
print(f"  Total hypothesis deaths   : {total_killed}")
print(f"  Epistemic health ratio    : {total_killed / max(total_born, 1):.2f}  (target > 0.3)")
print(f"  (A ratio near 0 = archive; near 1 = living epistemic system)")
print()

print("=" * 60)
print("  END OF REPORT")
print("=" * 60)
