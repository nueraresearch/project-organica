"""Render the ranking pre-registration from its artifact, so no number is typed by hand.

    ./.venv/bin/python -m benchmarks.write_rank_ordering_prereg
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "docs" / "rank_ordering_prereg.json"
OUT = ROOT / "docs" / "RANK-ORDERING-PREREGISTRATION.md"


def render(body: dict) -> str:
    design = body["design"]
    seeds = body["seeds"]
    gates = body["gates"]
    crit = body["criteria"]
    alloc = body["allocation"]
    low, high = seeds["block"]
    densities = ", ".join("%.1f" % d for d in design["densities"])
    caps = " and ".join(str(c) for c in design["caps"])
    edges = ", ".join(str(n) for n in design["world_edges_at_each_density"])
    table = "\n".join(
        "| %s | %s | **%s** | %s |" % (r["M1"], r["M2"], r["verdict"], r["reading"])
        for r in body["decision_table"])

    text = """# The ranking experiment, frozen before any cell (2026-11-07)

**Status: FROZEN, NOT RUN (judged block).** No judged cell has been executed, no judged world
generated, no judged engine cycle spent, and no result artifact exists. One smoke pool outside
the block has been run; it is recorded in §7 and in `not_run.smoke`, it is not evidence, and it
blocked the block. The criteria, gates, bar and allocation below were committed before the run;
nothing here may be changed afterwards. A defect found later is disclosed as an amendment, and
the pre-registered reading stands unless the amendment says plainly that it withdraws it.

The hypothesis is in `docs/NONFREQUENCY-RANKING-DESIGN.md`; this file is the test of it. The
numbers are in `docs/rank_ordering_prereg.json`, and this document is rendered from that
artifact by `benchmarks/write_rank_ordering_prereg.py`.

## 1. Question

Does ordering eligible candidates by **source diversity**, rather than by count, recover more
of a sparse world's edges at the engine's own cap? The design record varies the ordering at
fixed eligibility; the density record varies eligibility at fixed ordering. Neither subsumes
the other, and this block tests the first.

## 2. Design

- **Arms:** `control` (**%s**) and `diversity` (**%s**).
- **Caps:** %s.
- **World family:** %s, so |P_world| = 240 directed non-self pairs.
- **Densities:** %s, i.e. %s true edges.
- **Eligibility:** %s.
- **Exposure:** %s.
- **Horizon:** %s.
- **Cells:** %d (%s).

Coverage is |asserted and W| / |W|; precision is |asserted and W| / |asserted|, always
reported beside rho_rank; the presence ceiling is |W available in memory| / |W|.

## 3. Seeds

World seeds **%d-%d**, eight of them, plus bootstrap seed **%d** for the analysis interval.
%s. The block is the ninth number of the same window, and it is not a world seed.

%s.

## 4. Gates — comparability, not success

| Gate | Requirement |
| --- | --- |
| G0 liveness | %s |
| G1 presence | %s |
| G2 arithmetic | %s |
| G3 axis live | %s |
| G4 control reproduces | %s |
| G5 identity at density 1 | %s |

%s. The control ceiling in G4 is **%.2f**: if the count ordering already covers the world at
the sparsest level, the world or the cap is wrong and no delta can be read.

**A gate was amended before any cell ran.** %s

## 5. Criteria

**M1 — the level.** %s. The bar is **%.2f**.

The bar's provenance, fixed before any cell: %s It is not recomputed from the run it judges,
and a later block may not inherit it as a convention.

**M2 — the gradient.** %s.

The interval is a **%d%%** percentile bootstrap over seeds, paired within seed, **%d**
replicates.

## 6. Decision table

| M1 | M2 | Verdict | Reading |
| --- | --- | --- | --- |
%s

A gate failure is **VOID**, reported as the gate and never as a verdict. A negative pole is
licensed **only** by a decisive M1 failure: %s.

## 7. Analysis code path

`benchmarks/score_rank_ordering.py`, frozen with this file and importing nothing from
`organica`. It reads `docs/rank_ordering_run.json` and writes
`docs/rank_ordering_result.json`:

```
%s
```

It refuses a cell set that is not exactly the pre-registered grid, a duplicate cell, and a
result with no identity self-test. It computes the gates first; if any gate fails it reports
the gate and reads no criterion. The bootstrap seed comes from the artifact, so the interval
is deterministic given the cells.

The runner, `benchmarks/run_rank_ordering.py`, is built and passes its self-tests: the G5
identity check on an all-true population, a generator audit of the density ladder, and an
arm-liveness check that the two orderings differ at the sparsest density. `--run` refuses a
pre-registration that is not frozen, a seed block that is not contiguous, and an existing output
file without `--force`. No cell may run before this file is committed.

## 8. Allocation

**%d** seeds (of which **%d** are world seeds), **%d** cells, **%d** thresholds, **%d** bar.
The bar is declared here and never computed from the outcome.

## 9. What this block cannot say

- A pass is support within **one** world family, **two** caps and **eight** seeds. It is not a
  general claim that diversity ordering works, and it does not generalise to other families.
- A null is about this cap and this world family. It does not show that ordering is irrelevant
  anywhere else.
- Coverage is not behavior. Nothing here measures whether a belief predicts anything.
- The identity check at density 1 spends **no** engine cell: it is a harness self-test on a
  synthetic population, and it validates the arms, not the world.
- It does not touch the bottleneck map. That artifact keeps exactly one specified experiment,
  the density interaction, and a test asserts it.
""" % (
        body["arms"]["control"]["name"], body["arms"]["diversity"]["name"],
        caps, design["world_family"], densities, edges,
        design["eligibility"], design["exposure"], design["horizon"],
        design["cells"], design["cells_arithmetic"],
        low, high, seeds["bootstrap"], seeds["freshness"], seeds["consumed"],
        gates["G0_liveness"], gates["G1_presence_ceiling"], gates["G2_arithmetic_consistency"],
        gates["G3_axis_live"], gates["G4_control_reproduces"],
        gates["G5_identity_at_density_1"], gates["void_rule"],
        gates["control_coverage_ceiling"], body["amendments"][0]["why"],
        crit["M1_rule"], crit["M1_bar"], crit["M1_bar_provenance"], crit["M2_rule"],
        int(round(crit["interval"] * 100)), crit["bootstrap_reps"],
        table, crit["underpowered_rule"],
        body["analysis"]["command"],
        alloc["seeds"], alloc["world_seeds"], alloc["cells"],
        alloc["thresholds"], alloc["bars"],
    )
    smoke = (body.get("not_run") or {}).get("smoke")
    if smoke:
        text = text.replace(
            "No cell may run before this file is committed.",
            "No cell may run before this file is committed.\n\n" + _smoke(smoke))
    return text


def _smoke(smoke: dict) -> str:
    pool, counts, observed = smoke["pool"], smoke["counts"], smoke["observed"]
    return (
        "**A smoke pool was run before any judged cell, and it stopped the block.** Seed "
        "**%d** at rho_world %.1f, %d sleep cycles, %d derived cells: every world edge was "
        "present (%d of %d), and **the control and the diversity arm each covered 0 world "
        "edges at cap 20 and at cap 40**. The %d intra-cell filler rows carry counts %d-%d, "
        "%d per source across all %d sources, while the world's rows carry %d-%d and the best "
        "ranks **%d**, so the diversity ordering -- whose tie-break is count -- fills its "
        "remaining slots with filler once every source has one. Delta is therefore 0 by "
        "construction at the primary point, M1 cannot pass, and a zero-width interval is not "
        "underpowered, so the only reachable verdict is the negative pole. The pool itself "
        "behaved as the audits predicted (%d rows; presence %s), which is why this is a defect "
        "in what the arms can reach rather than in what the engine stores. No judged cell may "
        "run until the owner decides how to repair the treatment; the numbers are in "
        "`not_run.smoke`." % (
            smoke["seed"], smoke["rho_world"], smoke["engine_cycles"],
            smoke["cells_derived"], pool["world_rows"], smoke["generator"]["world_edges"],
            pool["filler_rows"], counts["filler_range"][0], counts["filler_range"][1],
            counts["filler_rows_per_source"], counts["sources_with_filler"],
            counts["world"][0], counts["world"][-1],
            counts["rank_of_first_world_edge"], pool["rows"],
            observed["control_cap_20"]["presence"]))


def main() -> None:
    body = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    text = render(body)
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT), "lines:", len(text.splitlines()))


if __name__ == "__main__":
    main()
