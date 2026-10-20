# Sleep V0 Results — The Organism's First Two Sleep Cycles

## What Happened

The organism ingested 30 dev-ops events (file modifications, test runs, failures), then slept twice.

> [!IMPORTANT]
> **Sleep cycle 2 successfully built on sleep cycle 1.** Candidates from cycle 1 were loaded, matched against cycle 2's independent rediscovery, and strengthened. This is the critical milestone: *the organism is accumulating interpretations, not just events.*

---

## Cycle 1 Output (from raw experience only)

### Concept Candidates (2)

| Members | Confidence | Observations | Avg Clustering | Predictive Reach |
|---------|-----------|-------------|----------------|-----------------|
| `auth`, `modified` | 1.00 | 15 | 0.271 | 14.5 |
| `failure` | 0.64 | 13 | 0.15 | 6.0 |

Both feel correct:
- **auth + modified** — low clustering (diverse neighbourhood), very high predictive reach (14.5 distinct future tags outside its co-occurrence cluster). This is a genuine concept.
- **failure** — a hub with degree 16 but low clustering. It connects to many things but isn't trapped in a clique.

### Prediction Candidates (8)

| Source | Target | Temporal Count | Strength |
|--------|--------|---------------|----------|
| `suite` | `passed` | 11 | 1.00 |
| `passed` | `suite` | 11 | 1.00 |
| `suite` | `failure` | 10 | 1.00 |
| `passed` | `failure` | 10 | 1.00 |
| `modified` | `suite` | 10 | 0.625 |
| `modified` | `passed` | 10 | 0.625 |
| `failure` | `modified` | 10 | 0.345 |
| `suite` | `failures` | 9 | 0.321 |

Key signals:
- `modified -> suite` (strength 0.625): File changes predict test runs. Obvious but real.
- `failure -> modified` (strength 0.345): Failures predict edits. The repair loop.
- `suite -> failure` AND `suite -> passed`: Both happen. The organism doesn't yet know which to expect.

### Top Loops (top 5 of 15)

| Path | Strength | Meaning |
|------|----------|---------|
| `passed <-> suite` | 11 | Test cycle backbone |
| `suite -> failure -> modified -> suite` | 10 | The *repair loop* (3-cycle!) |
| `passed -> failure -> modified -> passed` | 10 | Same repair loop, different entry |
| `failure <-> relation` | 9 | Error message phrase fragment |
| `failures <-> suite` | 9 | Test output structure |

### Anomaly Candidates (10)
Various "expected X but also saw Y" — mostly reflecting the variety of failure types after common tags.

---

## Cycle 2 — Stability & Evolution

Same data, no new events. The critical test: *does sleep N+1 find the same structures?*

### Evolution Results

| Metric | Count |
|--------|-------|
| Prior candidates loaded | 47 |
| Candidates **strengthened** | 37 |
| Candidates decayed | 0 |

### Specific Strengthening

```
[+] STRENGTHENED concept: ['auth', 'modified']
    confidence now:    1.0000
    prior confidence:  1.0

[+] STRENGTHENED concept: ['failure']
    confidence now:    0.6875   (was 0.6375 — boosted by +0.05)
    prior confidence:  0.6375

[+] STRENGTHENED prediction: modified -> suite
    strength now:    0.6750   (was 0.625)

[+] STRENGTHENED prediction: failure -> modified
    strength now:    0.3948   (was 0.345)

[+] STRENGTHENED loop: suite -> failure -> modified -> suite  (the repair loop)
```

---

## Architectural Decisions That Mattered

1. **Sleep events don't pollute the graphs.** `event_type="sleep"` events are stored in the events table but skip co-occurrence and temporal edge recording. Without this, cycle 2 was creating loops from its own JSON field names (`members -> confidence -> observations -> members`). The organism was eating its own thoughts.

2. **Candidates are JSON nodes, not text.** Every candidate is a `{"type": "...", "members": [...], "confidence": 0.72, "evidence": {...}}` — a reusable cognitive object that can be matched, strengthened, or decayed by future cycles.

3. **Loop cap at 15.** Without this, 60+ loops flooded memory. The combinatorial explosion from 3-cycles at low thresholds is real. The organism now keeps only the strongest 15.

4. **`LOOP_MIN_STRENGTH` raised to 5.** Further reduces noise loops.

---

## What To Watch Next

The three things the user asked us to track:

| Question | Status |
|----------|--------|
| Do candidate nodes recur across runs? | **Yes** — 37 of 47 rediscovered |
| Do nodes strengthen vs. decay? | **Yes** — `failure` concept went 0.6375 -> 0.6875 |
| Does sleep produce higher-order structures from previous sleep output? | **Not yet** — cycle 2 strengthened cycle 1's candidates but didn't create *new* candidates from them |

The third question is the next frontier. Right now sleep reads prior candidates only to boost/decay them. The next step would be: sleep noticing that several candidates share members and merging them, or noticing that a prediction candidate connects two concept candidates and forming a higher-order structure.

That's when the organism starts building structures on top of structures.
