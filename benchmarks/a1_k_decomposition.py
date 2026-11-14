"""Where does A1's K availability go?

A read-only decomposition of the six registered candidate universes against the
no-arm A+K+ baseline.  It asks where K availability is concentrated: by seed,
by tag, by cycle-36 U strength, by first-K timing, by orientation and by local
degree.  It does not select targets, set a threshold, recommend a redesign or
run an A1 cell.

The quantities are descriptive.  K is measured over 120 no-arm cycles, U is
measured at cycle 36, and their association has no identified direction: K may
support later U rather than U predicting K.  Tag incidence is pooled across
seeds and confounded with seed and edge membership.  Six seeds do not establish
that a pattern is structural across the world family.

    python -m benchmarks.a1_k_decomposition --write
    python -m benchmarks.a1_k_decomposition --check
    python -m benchmarks.a1_k_decomposition --self-test
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BASELINE_PATH = DOCS / "a1_baseline_availability.json"
TARGET_SELECTION_PATH = DOCS / "a1_target_selection.json"
OUT_PATH = DOCS / "a1_k_decomposition.json"
PAGE_PATH = DOCS / "A1-K-DECOMPOSITION.md"
ID = "A1-K-DECOMPOSITION-1"
DATE = "2026-11-14"
KIND = "a1_k_decomposition"
STATUS = "DESCRIPTIVE — K SCARCITY DECOMPOSITION; NO ARM, NO THRESHOLD, NO DISPOSITION"
SEEDS = (20630101, 20630102, 20630103, 20630104, 20630105, 20630106)
C1_FLOOR = 60


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _seed_rows(baseline: dict, selection: dict, seed: int) -> list[dict]:
    rows = {
        row["edge"]: row
        for row in next(
            block for block in baseline["per_seed"] if int(block["seed"]) == seed
        )["rows"]
    }
    u = selection["per_seed"][str(seed)]["u"]
    degree: Counter[str] = Counter()
    for edge in u:
        source, target = edge.split(">", 1)
        degree[source] += 1
        degree[target] += 1
    out = []
    for edge in sorted(u):
        source, target = edge.split(">", 1)
        row = rows[edge]
        out.append({
            "seed": seed,
            "edge": edge,
            "source": source,
            "target": target,
            "A": bool(row["A"]),
            "K": bool(row["K"]),
            "K_cycles": int(row["K_cycles"]),
            "first_K_cycle": row.get("first_K_cycle"),
            "U_strength": int(u[edge]["strength"]),
            "max_endpoint_degree": max(degree[source], degree[target]),
            "min_endpoint_degree": min(degree[source], degree[target]),
        })
    return out


def _percent(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _quartile_labels(values: list[int]) -> list[int]:
    ordered = sorted(values)
    return [
        ordered[len(ordered) // 4],
        ordered[len(ordered) // 2],
        ordered[3 * len(ordered) // 4],
    ]


def _quartile(value: int, cuts: list[int]) -> str:
    if value <= cuts[0]:
        return "Q1"
    if value <= cuts[1]:
        return "Q2"
    if value <= cuts[2]:
        return "Q3"
    return "Q4"


def _first_k_bin(cycle: int | None) -> str:
    if cycle is None:
        return "never"
    if cycle <= 30:
        return "1–30"
    if cycle <= 60:
        return "31–60"
    if cycle <= 90:
        return "61–90"
    return "91–120"


def build() -> dict:
    baseline = _load(BASELINE_PATH)
    selection = _load(TARGET_SELECTION_PATH)
    rows = []
    for seed in SEEDS:
        rows.extend(_seed_rows(baseline, selection, seed))

    per_seed = []
    for seed in SEEDS:
        block = [row for row in rows if row["seed"] == seed]
        A = sum(row["A"] for row in block)
        K = sum(row["K"] for row in block)
        both = sum(row["A"] and row["K"] for row in block)
        k_only_missing = sum(row["A"] and not row["K"] for row in block)
        a_only_missing = sum(not row["A"] and row["K"] for row in block)
        both_missing = sum(not row["A"] and not row["K"] for row in block)
        strengths = sorted(row["U_strength"] for row in block)
        cuts = _quartile_labels(strengths)
        low = [row for row in block if row["U_strength"] <= cuts[1]]
        high = [row for row in block if row["U_strength"] > cuts[1]]
        per_seed.append({
            "seed": seed,
            "candidate_edges": len(block),
            "A_available": A,
            "K_available": K,
            "A_and_K": both,
            "K_only_missing": k_only_missing,
            "A_only_missing": a_only_missing,
            "both_missing": both_missing,
            "K_rate": _percent(K, len(block)),
            "required_K_rate_for_60": _percent(C1_FLOOR, len(block)),
            "low_half_rows": len(low),
            "low_half_K": sum(row["K"] for row in low),
            "low_half_K_rate": _percent(sum(row["K"] for row in low), len(low)),
            "high_half_rows": len(high),
            "high_half_K": sum(row["K"] for row in high),
            "high_half_K_rate": _percent(sum(row["K"] for row in high), len(high)),
            "quartile_cuts": cuts,
        })

    total = {
        "candidate_edges": len(rows),
        "A_available": sum(row["A"] for row in rows),
        "K_available": sum(row["K"] for row in rows),
        "A_and_K": sum(row["A"] and row["K"] for row in rows),
        "K_only_missing": sum(row["A"] and not row["K"] for row in rows),
        "A_only_missing": sum(not row["A"] and row["K"] for row in rows),
        "both_missing": sum(not row["A"] and not row["K"] for row in rows),
    }
    total["K_rate"] = _percent(total["K_available"], total["candidate_edges"])
    total["A_rate"] = _percent(total["A_available"], total["candidate_edges"])
    total["A_and_K_rate"] = _percent(total["A_and_K"], total["candidate_edges"])
    total["K_only_share"] = _percent(total["K_only_missing"], total["candidate_edges"])
    total["A_only_share"] = _percent(total["A_only_missing"], total["candidate_edges"])

    tag_stats: dict[str, dict] = {}
    for row in rows:
        for tag in (row["source"], row["target"]):
            stats = tag_stats.setdefault(tag, {
                "tag": tag, "incidences": 0, "K_available": 0,
                "seed_rates": {},
            })
            stats["incidences"] += 1
            stats["K_available"] += int(row["K"])
            stats["seed_rates"].setdefault(row["seed"], [0, 0])
            stats["seed_rates"][row["seed"]][0] += int(row["K"])
            stats["seed_rates"][row["seed"]][1] += 1
    tag_rows = []
    for stats in tag_stats.values():
        rates = [
            available / count
            for available, count in stats["seed_rates"].values()
        ]
        tag_rows.append({
            "tag": stats["tag"],
            "incidences": stats["incidences"],
            "K_available": stats["K_available"],
            "K_missing": stats["incidences"] - stats["K_available"],
            "K_rate": _percent(stats["K_available"], stats["incidences"]),
            "min_seed_rate": round(min(rates), 6),
            "max_seed_rate": round(max(rates), 6),
            "seeds_below_half": sum(rate < 0.5 for rate in rates),
        })
    tag_rows.sort(key=lambda row: (row["K_rate"], row["tag"]))

    cuts = _quartile_labels([row["U_strength"] for row in rows])
    quartiles = []
    for label in ("Q1", "Q2", "Q3", "Q4"):
        block = [row for row in rows if _quartile(row["U_strength"], cuts) == label]
        quartiles.append({
            "label": label,
            "min_strength": min(row["U_strength"] for row in block),
            "max_strength": max(row["U_strength"] for row in block),
            "edges": len(block),
            "K_available": sum(row["K"] for row in block),
            "K_rate": _percent(sum(row["K"] for row in block), len(block)),
        })

    timing = []
    labels = ("1–30", "31–60", "61–90", "91–120", "never")
    for label in labels:
        block = [row for row in rows if _first_k_bin(row["first_K_cycle"]) == label]
        timing.append({
            "label": label,
            "edges": len(block),
            "share_of_all": _percent(len(block), len(rows)),
        })
    available = sum(row["K"] for row in rows)
    for row in timing:
        row["share_of_K_available"] = (
            _percent(row["edges"], available) if row["label"] != "never" else 0.0
        )

    orientation = Counter()
    pairs = 0
    for row in rows:
        reverse = row["target"] + ">" + row["source"]
        candidates = next(
            block for block in baseline["per_seed"]
            if int(block["seed"]) == row["seed"]
        )["rows"]
        reverse_row = next((entry for entry in candidates if entry["edge"] == reverse), None)
        if reverse_row is None:
            continue
        pairs += 1
        if row["K"] and reverse_row["K"]:
            orientation["both"] += 1
        elif row["K"]:
            orientation["candidate_only"] += 1
        elif reverse_row["K"]:
            orientation["reverse_only"] += 1
        else:
            orientation["neither"] += 1
    orientation_counts = {
        "pairs_with_reverse": pairs,
        "both": orientation["both"],
        "candidate_only": orientation["candidate_only"],
        "reverse_only": orientation["reverse_only"],
        "neither": orientation["neither"],
        "concordant": orientation["both"] + orientation["neither"],
    }
    orientation_counts["concordant_rate"] = _percent(
        orientation_counts["concordant"], pairs)

    degrees = Counter(row["max_endpoint_degree"] for row in rows)
    topology = {
        "max_endpoint_degree_distribution": {
            str(degree): count for degree, count in sorted(degrees.items())
        },
        "note": (
            "The candidate universe is near-regular: every 64-edge seed is "
            "8-regular on 16 tags, and each 63-edge seed has fourteen tags of "
            "degree 8 and two of degree 7. Endpoint degree has no useful "
            "variation, so local degree cannot explain the K split."
        ),
    }

    arithmetic = [
        {"independent_edges": edges, "required_K_rate": _percent(C1_FLOOR, edges)}
        for edges in (63, 64, 80, 96, 120)
    ]

    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "source_artifacts": {
            "baseline_availability": BASELINE_PATH.relative_to(ROOT).as_posix(),
            "target_selection": TARGET_SELECTION_PATH.relative_to(ROOT).as_posix(),
        },
        "scope": (
            "Six registered seeds, 382 first-36-cycle candidate edges, and the "
            "no-arm A+K+ baseline at 120 cycles. All quantities are descriptive; "
            "no treatment was applied and no threshold was set."
        ),
        "per_seed": per_seed,
        "totals": total,
        "tag_rows": tag_rows,
        "u_quartiles": {
            "cuts": cuts,
            "rows": quartiles,
            "note": (
                "Pooled quartiles across the 382 candidate edges. The per-seed "
                "low/high-half split is in the seed table; it uses each seed's "
                "own median, so the labels are not the same boundaries."
            ),
        },
        "first_k_timing": {
            "rows": timing,
            "note": (
                "First cycle at which K is present in the 120-cycle no-arm "
                "baseline. 'never' means no K anywhere in the observed window, "
                "not that K is impossible."
            ),
        },
        "orientation": orientation_counts,
        "topology": topology,
        "required_rate_arithmetic": arithmetic,
        "findings": [
            "K is the lower path on five of six seeds and ties A on the sixth: "
            "A 281/382, K 228/382, A&K 186/382.",
            "The K-specific gap is larger than the A-specific gap: 95 rows have "
            "A but no K; 42 have K but no A; 59 have neither.",
            "K availability rises with cycle-36 U strength: pooled quartile "
            "rates are 31.8%, 49.5%, 80.8% and 89.1% from Q1 to Q4.",
            "The association is per-seed, but the high-U half still contains "
            "only 28–31 edges per seed, so U enrichment cannot by itself form a "
            "60-row C1 stream.",
            "K scarcity is mostly absence, not lateness: 154/382 rows have no K "
            "in 120 cycles; only 28/228 available rows first form K after cycle 60.",
            "No tag is consistently absent across seeds. Pooled tag rates span "
            "44.7–77.1%, but per-seed rates swing from 0.0 to 1.0; tag identity "
            "is not a stable redesign axis on these six seeds.",
            "K is almost entirely orientation-concordant: 278/286 candidate/"
            "reverse pairs agree (177 both, 101 neither); only 8 pairs differ. "
            "Reverse orientation is not a K lever.",
            "Local degree cannot explain the split: the candidate universe is "
            "near-regular (degree 8, or 7/8 on the 63-edge seeds).",
        ],
        "limits": [
            "K is measured in a no-arm replay over 120 cycles; it is not a "
            "treatment measurement.",
            "U is measured at cycle 36. The K–U association has no identified "
            "direction: K may support later U, or both may share a cause.",
            "Tag rows count endpoint incidences, not edges; an edge contributes "
            "to two tags. Pooled tag rates are confounded with seed.",
            "Six seeds do not establish a world-family-wide structure.",
            "No target was selected, no threshold changed, no freeze or grant "
            "exists and no A1 cell ran.",
        ],
        "redesign_arithmetic": (
            "At 63–64 independent edges, reaching 60 K-available rows would "
            "require a K rate of 93.8–95.2%. The observed seeds are at "
            "49.2–68.8%, and the high-U half is at 71.4–96.6% but has only "
            "28–31 rows per seed. A larger independent universe lowers the "
            "required rate; 80 rows need 75%, 96 need 62.5%, and 120 need 50%. "
            "These are arithmetic requirements, not a proposed design."
        ),
        "not_evidence": (
            "A descriptive decomposition of existing no-arm artifacts. It does "
            "not identify a cause, select targets, set a threshold, choose a "
            "redesign or park A1."
        ),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("record kind")
    if doc.get("id") != ID:
        found.append("record id")
    if doc.get("status") != STATUS:
        found.append("record status")
    rows = doc.get("per_seed") or []
    if [row.get("seed") for row in rows] != list(SEEDS):
        found.append("seed block")
        return found
    totals = doc.get("totals") or {}
    for key in ("candidate_edges", "A_available", "K_available", "A_and_K",
                "K_only_missing", "A_only_missing", "both_missing"):
        if totals.get(key) != sum(row.get(key, 0) for row in rows):
            found.append("total %s is inconsistent" % key)
    for row in rows:
        if row.get("candidate_edges") != (
                row.get("A_available", 0) + row.get("A_only_missing", 0) +
                row.get("both_missing", 0)):
            found.append("seed %s path partition is inconsistent" % row.get("seed"))
        if row.get("K_only_missing") != (
                row.get("A_available", 0) - row.get("A_and_K", 0)):
            found.append("seed %s K-only gap is inconsistent" % row.get("seed"))
        if row.get("A_only_missing") != (
                row.get("K_available", 0) - row.get("A_and_K", 0)):
            found.append("seed %s A-only gap is inconsistent" % row.get("seed"))
        if row.get("K_available") != (
                row.get("A_and_K", 0) + row.get("A_only_missing", 0)):
            found.append("seed %s K total is inconsistent" % row.get("seed"))
        if row.get("A_available") != (
                row.get("A_and_K", 0) + row.get("K_only_missing", 0)):
            found.append("seed %s A total is inconsistent" % row.get("seed"))
        if row.get("high_half_rows", 0) + row.get("low_half_rows", 0) != row.get("candidate_edges"):
            found.append("seed %s U-half partition is inconsistent" % row.get("seed"))
        if row.get("high_half_K", 0) + row.get("low_half_K", 0) != row.get("K_available"):
            found.append("seed %s U-half K total is inconsistent" % row.get("seed"))
    quartiles = doc.get("u_quartiles") or {}
    if sum(row.get("edges", 0) for row in quartiles.get("rows", [])) != totals.get("candidate_edges"):
        found.append("U-quartile edge total is inconsistent")
    timing = doc.get("first_k_timing") or {}
    if sum(row.get("edges", 0) for row in timing.get("rows", [])) != totals.get("candidate_edges"):
        found.append("first-K timing total is inconsistent")
    orientation = doc.get("orientation") or {}
    if sum(orientation.get(key, 0) for key in (
            "both", "candidate_only", "reverse_only", "neither")) != orientation.get("pairs_with_reverse"):
        found.append("orientation partition is inconsistent")
    if sum(row.get("incidences", 0) for row in doc.get("tag_rows", [])) != 2 * totals.get("candidate_edges"):
        found.append("tag incidence total is inconsistent")
    return found


def self_test() -> list[str]:
    found: list[str] = []
    if _first_k_bin(None) != "never":
        found.append("missing K should be 'never'")
    if _first_k_bin(30) != "1–30" or _first_k_bin(31) != "31–60":
        found.append("first-K bin boundaries are wrong")
    if _quartile(11, [11, 16, 20]) != "Q1":
        found.append("Q1 boundary is wrong")
    if _quartile(21, [11, 16, 20]) != "Q4":
        found.append("Q4 boundary is wrong")
    if _percent(1, 0) != 0.0:
        found.append("zero denominator should be zero")
    return found


def render(doc: dict) -> str:
    totals = doc["totals"]
    lines = [
        "# A1 K-availability decomposition — descriptive",
        "",
        "**ID:** `%s`" % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an A1 result.** It decomposes the no-arm K-availability "
        "counts; it runs no cell, selects no target, sets no threshold and "
        "chooses no redesign.",
        "",
        doc["scope"],
        "",
        "## Headline",
        "",
        "- Candidate edges: **%d**. A available: **%d** (%.1f%%). K available: "
        "**%d** (%.1f%%). A&K: **%d** (%.1f%%)." % (
            totals["candidate_edges"], totals["A_available"],
            100 * totals["A_rate"], totals["K_available"],
            100 * totals["K_rate"], totals["A_and_K"],
            100 * totals["A_and_K_rate"]),
        "- **K-specific gap:** %d rows have A but no K; %d have K but no A; "
        "%d have neither. K is the larger single-path deficit." % (
            totals["K_only_missing"], totals["A_only_missing"],
            totals["both_missing"]),
        "",
        "## By seed",
        "",
        "| Seed | Edges | A | K | A&K | A, no K | K, no A | Neither | K rate | K rate needed for 60 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["per_seed"]:
        lines.append(
            "| `%d` | %d | %d | %d | %d | %d | %d | %d | %.1f%% | %.1f%% |" % (
                row["seed"], row["candidate_edges"], row["A_available"],
                row["K_available"], row["A_and_K"], row["K_only_missing"],
                row["A_only_missing"], row["both_missing"],
                100 * row["K_rate"], 100 * row["required_K_rate_for_60"],
            )
        )
    lines += [
        "",
        "K is lower than A on five seeds and ties on `20630101`. Even if every "
        "candidate were selected, the K ceiling is 31–44; the remaining K "
        "shortfall to 60 is **16–29 rows** per seed.",
        "",
        "## U-strength quartiles",
        "",
        "Pooled quartiles across all 382 candidate edges. Strength is the "
        "cycle-36 directed U value; the bins are Q1 ≤ %d, Q2 %d–%d, Q3 %d–%d, "
        "Q4 ≥ %d." % (
            doc["u_quartiles"]["cuts"][0],
            doc["u_quartiles"]["cuts"][0] + 1, doc["u_quartiles"]["cuts"][1],
            doc["u_quartiles"]["cuts"][1] + 1, doc["u_quartiles"]["cuts"][2],
            doc["u_quartiles"]["cuts"][2] + 1),
        "",
        "| Quartile | Strength range | Edges | K available | K rate |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["u_quartiles"]["rows"]:
        lines.append(
            "| %s | %d–%d | %d | %d | %.1f%% |" % (
                row["label"], row["min_strength"], row["max_strength"],
                row["edges"], row["K_available"], 100 * row["K_rate"],
            )
        )
    lines += [
        "",
        "| Seed | Low-U half rows | Low-U K rate | High-U half rows | High-U K rate |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["per_seed"]:
        lines.append(
            "| `%d` | %d | %.1f%% | %d | %.1f%% |" % (
                row["seed"], row["low_half_rows"], 100 * row["low_half_K_rate"],
                row["high_half_rows"], 100 * row["high_half_K_rate"],
            )
        )
    lines += [
        "",
        "The high-U half has a higher K rate on all six seeds, but it contains "
        "only 28–31 edges per seed. Enriching U cannot by itself produce a "
        "60-row C1 stream.",
        "",
        "## When K appears",
        "",
        "| First K cycle | Edges | Share of all candidates | Share of K-available |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in doc["first_k_timing"]["rows"]:
        lines.append(
            "| %s | %d | %.1f%% | %s |" % (
                row["label"], row["edges"], 100 * row["share_of_all"],
                "—" if row["label"] == "never" else "%.1f%%" % (100 * row["share_of_K_available"]),
            )
        )
    lines += [
        "",
        "%d of 382 rows have no K in 120 cycles; only %d of the 228 available "
        "rows first form K after cycle 60. The main pattern is absence, not "
        "late arrival." % (
            next(row["edges"] for row in doc["first_k_timing"]["rows"] if row["label"] == "never"),
            sum(row["edges"] for row in doc["first_k_timing"]["rows"]
                if row["label"] in ("61–90", "91–120")),
        ),
        "",
        "## By tag",
        "",
        "Tag rows count **endpoint incidences**, not edges; each edge contributes "
        "to two tags. Pooled across seeds, so seed and tag are confounded.",
        "",
        "| Tag | Incidences | K available | K missing | K rate | Seed rate range | Seeds below 50% |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["tag_rows"]:
        lines.append(
            "| `%s` | %d | %d | %d | %.1f%% | %.1f–%.1f%% | %d/6 |" % (
                row["tag"], row["incidences"], row["K_available"],
                row["K_missing"], 100 * row["K_rate"],
                100 * row["min_seed_rate"], 100 * row["max_seed_rate"],
                row["seeds_below_half"],
            )
        )
    lines += [
        "",
        "No tag is consistently unavailable: the pooled range is 44.7–77.1%, "
        "but every tag swings widely by seed. Tag identity is not a stable "
        "redesign axis on these six seeds.",
        "",
        "## Orientation and topology",
        "",
        "| Candidate/reverse pair | Count |",
        "| --- | ---: |",
        "| Both K | %d |" % doc["orientation"]["both"],
        "| Neither K | %d |" % doc["orientation"]["neither"],
        "| Candidate only | %d |" % doc["orientation"]["candidate_only"],
        "| Reverse only | %d |" % doc["orientation"]["reverse_only"],
        "",
        "K is **%.1f%%** concordant across candidate/reverse pairs (%d/%d). "
        "Only %d pairs differ, so reverse orientation is not a K lever." % (
            100 * doc["orientation"]["concordant_rate"],
            doc["orientation"]["concordant"],
            doc["orientation"]["pairs_with_reverse"],
            doc["orientation"]["candidate_only"] + doc["orientation"]["reverse_only"],
        ),
        "",
        doc["topology"]["note"],
        "",
        "## Redesign arithmetic",
        "",
        doc["redesign_arithmetic"],
        "",
        "| Independent edges | K rate needed for 60 |",
        "| ---: | ---: |",
    ]
    for row in doc["required_rate_arithmetic"]:
        lines.append("| %d | %.1f%% |" % (
            row["independent_edges"], 100 * row["required_K_rate"]))
    lines += [
        "",
        "## Limits",
        "",
    ]
    for limit in doc["limits"]:
        lines.append("- %s" % limit)
    lines += [
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_k_decomposition --check",
        "python -m benchmarks.a1_k_decomposition --self-test",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip("\n")


def write() -> int:
    doc = build()
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc) + "\n", encoding="utf-8")
    found = problems(doc)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = _load(OUT_PATH)
    found = problems(doc)
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print(
        "A1 K decomposition: clean; K %d/%d (%.1f%%), A %d/%d (%.1f%%), "
        "K-only gap %d"
        % (doc["totals"]["K_available"], doc["totals"]["candidate_edges"],
           100 * doc["totals"]["K_rate"], doc["totals"]["A_available"],
           doc["totals"]["candidate_edges"], 100 * doc["totals"]["A_rate"],
           doc["totals"]["K_only_missing"])
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        found = self_test()
        if found:
            for problem in found:
                print("FAIL:", problem)
            return 1
        print("A1 K decomposition: self-test clean")
        return 0
    if args.write:
        return write()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
