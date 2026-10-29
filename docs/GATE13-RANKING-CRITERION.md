# Gate 13 — the ranking criterion: what the engine computes, and what it cannot

**Status: DIAGNOSTIC RECORD (2026-10-29).** This document records the probe
that tested the third of the three V2 requirements: *a ranking that is not raw
frequency*.

The requirement had been called the hard one, with no precedent in the engine.
It turned out to have a precedent — and the precedent is the finding.

**All seeds are diagnostic** (`20261101`–`20261103`). The confirmatory sample
(`20261106`–`20261130`, 25 seeds) is untouched.

---

## 1. The engine already computes a normalized criterion, and does not use it

`organica/sleep.py:1139-1160`, `SleepService._build_predictions`:

```python
ratio = count / max(source_freq, 1)
...
strength=min(1.0, ratio),
evidence={
    "temporal_count": count,
    "source_frequency": source_freq,
    "target_frequency": freqs.get(tag_to, 0),
    "ratio": round(ratio, 3),
},
...
candidates.sort(key=lambda p: p["evidence"]["temporal_count"], reverse=True)
return candidates[:self.MAX_PREDICTIONS]
```

The engine computes a **frequency-normalized** criterion, stores it in every
candidate's evidence, and then sorts by **raw count** for admission. The
normalized quantity is used for **survival** (via `stable_prior`) and not for
**admission** — and `memory.py:264-281` says the normalization is
"load-bearing rather than cosmetic".

So requirement 3 may not need a new idea. Every criterion the probe tested
uses **only fields the engine already stores on every candidate**:

| criterion | formula | fields used |
|---|---|---|
| `count` | the engine's current ranking (baseline) | `temporal_count` |
| `ratio` | `count / source_freq` | the engine's own `strength` |
| `target_ratio` | `count / target_freq` | `target_frequency` |
| `cosine` | `count / sqrt(src_freq * dst_freq)` | the same two fields |
| `pmi` | `count / (src_freq * dst_freq / N)` | the same two fields |

## 2. The grid

Two tables × two frequency scopes × five criteria × three seeds = **60 cells**.

| table | frequency scope | what it is |
|---|---|---|
| `raw` | `world_freq` | the engine's own table and scope — **today's behavior** |
| `raw` | `world_plus_self_freq` | the engine's table, with the engine's own vocabulary counted too |
| `filtered` | `world_freq` | provenance-separated table (world-only lookback) |
| `filtered` | `world_plus_self_freq` | provenance-separated **and** self-scoped frequency |

The separation is the oracle-free provenance filter of
`docs/GATE13-RELATION-SEPARATION.md`; the self scope adds a frequency for the
engine's own vocabulary, recovered from the `events` table without touching
the engine. As in that probe, the offline reconstruction of the raw table must
**match the engine's table exactly** or the probe refuses to report. It did,
on every seed.

## 3. The result

**The best cell in the entire 60-cell grid reaches coverage 0.0804 with
precision 0.4500. The gate is 0.50.** Everything else is worse.

| table | scope | criterion | best coverage | precision | intra | inter | mixed |
|---|---|---|---|---|---|---|---|
| raw | world_freq | `count` *(the engine today)* | 0.0089 | 0.0500 | 19 | 1 | 0 |
| raw | world_freq | `ratio` / `cosine` / `pmi` | **0.0000** | 0.0000 | 0 | 0 | **20** |
| raw | world_plus_self_freq | `target_ratio` | 0.0625 | 0.3500 | 3 | 11 | 6 |
| filtered | world_freq | any | 0.0089 | 0.0500 | 19–20 | 0–1 | 0 |
| **filtered** | **world_plus_self_freq** | **`ratio`** | **0.0804** | **0.4500** | 9 | **11** | 0 |
| filtered | world_plus_self_freq | `target_ratio` | 0.0714 | 0.4000 | 8 | 12 | 0 |
| filtered | world_plus_self_freq | `pmi` | 0.0804 | 0.4500 | 11 | 9 | 0 |

Per seed, in the best configuration (`filtered` + `world_plus_self_freq`):

| seed | `ratio` | `target_ratio` | `pmi` | `count` |
|---|---|---|---|---|
| 20261101 | 0.0357 (prec 0.20) | 0.0714 (prec 0.40) | 0.0714 (prec 0.40) | 0.0000 |
| 20261102 | **0.0804** (prec **0.45**) | 0.0625 (prec 0.35) | 0.0268 (prec 0.15) | 0.0000 |
| 20261103 | 0.0536 (prec 0.30) | 0.0446 (prec 0.25) | **0.0804** (prec **0.45**) | 0.0000 |

**Three things follow.**

**(a) No criterion alone reaches the world's edges.** On the raw table under
the engine's own scope, the normalized criteria select **20 engine-vocabulary
edges and zero world edges**, on every seed.

**(b) The provenance filter alone does not reach them either** — the `filtered`
table under `world_freq` scores 0.0000–0.0089 for every criterion.

**(c) Together they change the selection's composition, and still do not clear
the gate.** With both, coverage goes from **0.0000 to 0.0804** and precision
from **0.0000 to 0.4500**, and the intra/inter balance **flips** from 20 / 0 to
roughly 8–15 / 5–13 — the world's cross-cell relations enter the selection for
the first time in meaningful numbers. But **0.0804 against 0.50 is six times
short.**

## 4. Why each scope fails — measured, not inferred

A diagnostic (`benchmarks/probe_ranking_mechanism.py`, seed `20261101`) printed
the selected edges with every number behind them.

**Under the engine's own scope (`world_freq`):**

| src → dst | count | world-freq | self-freq | **ratio** | src in world? | src in self map? |
|---|---|---|---|---|---|---|
| `type` → `cedar` | 48 | **0** | 158,183 | **48.0000** | no | yes |
| `generation` → `cedar` | 48 | **0** | 158,112 | **48.0000** | no | yes |
| `dream` → `cedar` | 48 | **0** | 2,797 | **48.0000** | no | yes |

`_record_tag_counts` is inside the `if event_type != "sleep":` block in
`store()`, so **`tag_counts` is world-scoped and the engine's own words are
absent from it**. `freqs.get(tag_from, 1)` therefore returns **1**, and
`ratio = count / 1 = count` — the maximum possible ratio for that count. **The
engine's normalized criterion is undefined for exactly the edges it would need
to discriminate, and ranks them first.**

**Under the self-inclusive scope (`world_plus_self_freq`):**

| src → dst | count | world-freq | self-freq | **ratio** |
|---|---|---|---|---|
| `mutation` → `cedar` | 43 | 0 | 260 | **0.1654** |
| `conditional` → `birch` | 6 | 0 | 79 | **0.0759** |
| *(best world edge)* `sable` → `fern` | 48 | 115 | **2,601** | **0.0177** |
| *(best world edge)* `olive` → `fern` | 44 | 112 | **7,753** | **0.0056** |

**Now the failure runs the other way.** The world's tags appear in the
engine's own sleep output constantly — `sable` 2,601 times, `olive` 7,753,
`maple` 35,986, `cedar` 52,070 — so once the engine's own speech is counted,
the **world's tags acquire enormous denominators and are penalised**, and the
engine's *rare* metadata words (`mutation`, `conditional`) rise to the top.

**Both scopes fail, for opposite reasons, and the reason underneath both is
the same: the engine's sleep output names the world's tags.** The world
vocabulary and the engine's own vocabulary are not separable **by frequency in
either direction**, because they are not separable at all in the substrate —
the organism talks about the world using the world's words.

## 5. What this settles

1. **Requirement 3 is not "find a better formula."** Every formula built from
   the fields the engine already stores was measured, and **all of them fail**,
   in both frequency scopes, on both tables, on every seed.
2. **The discriminator cannot be a per-tag statistic.** It must be a
   **relation-level** property: *which event did this relation come from*.
   That is exactly the provenance separation of
   `docs/GATE13-RELATION-SEPARATION.md`, and it is the only one available.
3. **The two fixes are complementary and jointly necessary.** Neither alone
   moves the needle (0.0089); together they move coverage from 0.0000 to
   0.0804 and precision to 0.4500. **And together they are still six times
   short of the gate.**
4. **The engine's own normalized criterion is actively harmful here.** Under
   the engine's own scope it selects engine vocabulary exclusively, because
   the frequency it normalises by is world-scoped and therefore absent for
   the contaminated rows. The `ratio` the engine computes and stores is not a
   neutral alternative to raw count; on this table it is worse.

## 6. What this changes for V2

The requirement list is now stated in terms of what each fix has to touch:

1. **Provenance separation (relation-level).** The world relation table must
   not contain relations sourced from the organism's own output. One filtered
   lookback query — `memory.py:332` — and the information (`event_type`) is
   already in the schema. **Cheapest, and oracle-free.**
2. **A relation-level criterion, not a tag-level one.** After the provenance
   filter, the remaining competition is between the world's **own** relation
   families: intra-cell co-occurrence (the two tags of a cell, which co-occur
   in every event of that cell) and cross-cell transition (the law). **No
   per-tag frequency statistic can separate those**, because they involve the
   same tags. The discriminator has to be structural — for example, whether a
   source's target is its *unique* successor or *one of several*.
3. **Relation-family separation.** The `cooccurrences` and `precedes` tables
   are already separate in the substrate; they are re-mixed downstream, in
   Layer 1.

**Requirement 2 is the one with no precedent, and it is now the one with a
measured dead end** — the tag-level versions of it are all ruled out.

## 7. What this does not establish

- **It does not establish that any V2 would work**, or that requirement 2 is
  satisfiable. It establishes what requirement 2 must **not** be.
- **It does not change any verdict.** The six negative task families, the
  Phase L protocol verdict `H3-L — INCONCLUSIVE`, the Phase L
  characterization, and the campaign's stop at Gate 13 all stand.
- **It does not change the confirmatory sample.** Every seed used is
  diagnostic and remains diagnostic.
- **It does not reopen the frozen engine.** Every number here comes from an
  offline reconstruction validated against the engine's own table.
- **It does not propose a rule for requirement 2.** The structural criterion
  named in §6 is a direction, not a design, and it has not been measured.
- **The engine's own vocabulary and the world's vocabulary overlap heavily**
  (`sable` appears 2,601 times in the engine's own output). That is a
  property of the engine worth knowing, and it is the reason the per-tag
  route is closed — not a defect in itself.

## 8. Reproducing

```bash
# the ranking grid (3 seeds; ~6 min)
python benchmarks/probe_ranking_criterion.py

# why each scope fails, with every number behind the selection (~4 min)
python benchmarks/probe_ranking_mechanism.py
```

**Artifacts:**

- `docs/gate13_ranking_criterion.json` — the grid
- `docs/gate13_relation_separation.json` — the provenance separation
- `docs/gate13_allocation_rule.json` — the allocation-rule probe
- `docs/gate13_capacity_sweep.json` — the capacity sweep
- `docs/GATE13-CAUSAL-ACCOUNT.md`, `docs/GATE13-RELATION-SEPARATION.md` — the
  two records this extends
