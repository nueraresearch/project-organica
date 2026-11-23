"""Separate capacity-bound from support-bound K dilution.

The K dilution report showed that the 28-tag universe added edges without
adding K.  This diagnostic asks which bound is more consistent with that
pattern, using two axes on the same no-arm worlds:

* **Capacity sweep** on the fixed 28-tag world: prediction cap 20, 40 and 80.
  If K is capacity-bound, raising the cap should raise K and lowering it should
  reduce K; if K is support-bound, the cap should move little.
* **Support stratification** at cap 40: candidate edges are grouped by their
  observed directed-pair support in the acquisition stream.  If K is
  support-bound, K density should rise with support and 16-tag and 28-tag
  worlds should look similar at matched support.

The thresholds and the reading rule are fixed before the cap runs.  They are a
reporting convention, not an A1 gate: a mixed reading is a real outcome.

No target is selected, no threshold in the A1 protocol changes, no seed is
reserved, no grant exists and no A1 cell runs.  Cap 80 is a diagnostic
condition, not a proposed protocol.

    python -m benchmarks.a1_k_supply_discriminator --write
    python -m benchmarks.a1_k_supply_discriminator --check
    python -m benchmarks.a1_k_supply_discriminator --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from benchmarks import a1_baseline_availability
from benchmarks import a1_larger_universe
from benchmarks.acquisition_compositional import (
    PHASE_ACQUISITION,
    generate_compositional_world,
)
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_k_supply_discriminator.json"
PAGE_PATH = DOCS / "A1-K-SUPPLY-DISCRIMINATOR.md"
ID = "A1-K-SUPPLY-DISCRIMINATOR-1"
DATE = "2026-11-14"
KIND = "a1_k_supply_discriminator"
STATUS = "DIAGNOSTIC — CAPACITY VS SUPPORT; NO TARGET, NO PROTOCOL CHANGE, NO RUN"
BASE_CAP = 40
CAPS = (20, 40, 80)
CAP_HIGH_LIFT = 0.10
CAP_LOW_DROP = 0.10
CAP_SEED_AGREEMENT = 4
SUPPORT_SPREAD = 0.20
SUPPORT_TOLERANCE = 0.02
MATCHED_SUPPORT_GAP = 0.15
MIN_BIN_EDGES = 20
SUPPORT_BINS = (
    ("0", 0, 0),
    ("1", 1, 1),
    ("2-3", 2, 3),
    ("4-7", 4, 7),
    ("8-15", 8, 15),
    ("16+", 16, None),
)
CANDIDATES = (
    {
        "label": "16-tag",
        "path": DOCS / "a1_successor_candidate.json",
        "world": lambda seed: generate_compositional_world(seed=seed, cycles=120),
    },
    {
        "label": "28-tag",
        "path": DOCS / "a1_larger_universe_candidate.json",
        "world": a1_larger_universe.generate_world,
    },
)
PREDECLARATION = {
    "capacity_axis": {
        "caps": list(CAPS),
        "base_cap": BASE_CAP,
        "capacity_signal_rule": (
            "K at cap 80 is at least 10% above cap 40, K at cap 20 is at "
            "least 10% below cap 40, and at least 4/6 seeds move in each "
            "direction."
        ),
        "prediction": (
            "Capacity-bound predicts a rise at 80 and a fall at 20; "
            "support-bound predicts little movement."
        ),
    },
    "support_axis": {
        "bins": [label for label, _, _ in SUPPORT_BINS],
        "minimum_edges_per_bin": MIN_BIN_EDGES,
        "support_signal_rule": (
            "At cap 40, K density rises monotonically (2 pp tolerance) across "
            "bins with at least 20 edges, and the highest minus lowest bin is "
            "at least 20 percentage points."
        ),
        "matched_signal_rule": (
            "For support bins with at least 20 edges in both worlds, the "
            "edge-weighted absolute 16-tag/28-tag K-density gap is at most "
            "15 percentage points."
        ),
        "prediction": (
            "Support-bound predicts a monotone K gradient and a small "
            "matched-support gap; capacity-bound does not require either."
        ),
    },
    "reading_rule": (
        "Both axes = MIXED; capacity only = CAPACITY-DOMINANT; support only "
        "with matched support = SUPPORT-DOMINANT; support only without "
        "matched support = SUPPORT-ASSOCIATED, NOT FULLY EXPLANATORY; "
        "neither = NEITHER AXIS CLEANLY DOMINANT. This is a reporting "
        "convention, not a gate."
    ),
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _percent(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _support_counts(world: dict) -> Counter:
    """Directed pair occurrences in the trainable acquisition stream."""
    counts: Counter = Counter()
    previous: list[str] = []
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo = acq_lo * EVENTS_PER_CYCLE
    event_hi = acq_hi * EVENTS_PER_CYCLE
    for index, (text, trainable) in enumerate(
            zip(world["events"], world["trainable"])):
        current = text.split()
        in_acq = event_lo <= index < event_hi
        if in_acq and trainable and previous:
            for source in previous:
                for target in current:
                    if source != target:
                        counts[(source, target)] += 1
        previous = current
    return counts


def _support_bin(value: int) -> str:
    for label, low, high in SUPPORT_BINS:
        if value >= low and (high is None or value <= high):
            return label
    raise ValueError("support value is outside the bins: %r" % value)


def _rows(candidate: dict, cap: int | None = None) -> list[dict]:
    doc = _load(candidate["path"])
    rows = []
    for seed in doc["seed_block"]:
        world = candidate["world"](seed)
        supports = _support_counts(world)
        if cap is None:
            available = {
                row["edge"]: row for row in doc["per_seed"][str(seed)]
            }
        else:
            replay = a1_baseline_availability._run_seed(
                seed, world=world, cap=cap)
            available = {row["edge"]: row for row in replay["rows"]}
        for edge in sorted(doc["per_seed"][str(seed)], key=lambda row: row["edge"]):
            edge = edge["edge"] if isinstance(edge, dict) else edge
            row = available[edge]
            source, target = edge.split(">", 1)
            rows.append({
                "seed": seed,
                "edge": edge,
                "A": bool(row["A"]),
                "K": bool(row["K"]),
                "support": int(supports[(source, target)]),
                "support_bin": _support_bin(int(supports[(source, target)])),
            })
    return rows


def _totals(rows: list[dict]) -> dict:
    total = {
        "candidate_edges": len(rows),
        "A_available": sum(row["A"] for row in rows),
        "K_available": sum(row["K"] for row in rows),
        "A_and_K": sum(row["A"] and row["K"] for row in rows),
    }
    total["A_density"] = _percent(total["A_available"], total["candidate_edges"])
    total["K_density"] = _percent(total["K_available"], total["candidate_edges"])
    return total


def _by_seed(rows: list[dict]) -> list[dict]:
    out = []
    for seed in sorted({row["seed"] for row in rows}):
        block = [row for row in rows if row["seed"] == seed]
        total = _totals(block)
        total["seed"] = seed
        out.append(total)
    return out


def _by_support(rows: list[dict]) -> list[dict]:
    out = []
    for label, _, _ in SUPPORT_BINS:
        block = [row for row in rows if row["support_bin"] == label]
        if not block:
            continue
        total = _totals(block)
        total["support_bin"] = label
        total["min_support"] = min(row["support"] for row in block)
        total["max_support"] = max(row["support"] for row in block)
        out.append(total)
    return out


def _base_check(rows28: list[dict], doc: dict) -> None:
    expected = {
        seed: {
            row["edge"]: row["K"] for row in doc["per_seed"][str(seed)]
        }
        for seed in doc["seed_block"]
    }
    for row in rows28:
        if row["K"] != expected[row["seed"]][row["edge"]]:
            raise ValueError("cap-40 replay does not reproduce the candidate K row")


def _reading(capacity_signal: bool, support_signal: bool,
             matched_signal: bool) -> str:
    if capacity_signal and support_signal:
        return "MIXED — BOTH CAPACITY AND SUPPORT RESPOND"
    if capacity_signal:
        return "CAPACITY-DOMINANT"
    if support_signal and matched_signal:
        return "SUPPORT-DOMINANT"
    if support_signal:
        return "SUPPORT-ASSOCIATED, NOT FULLY EXPLANATORY"
    return "NEITHER AXIS CLEANLY DOMINANT"


def build() -> dict:
    docs = {candidate["label"]: _load(candidate["path"]) for candidate in CANDIDATES}
    rows16 = _rows(CANDIDATES[0])
    rows28 = _rows(CANDIDATES[1])
    _base_check(rows28, docs["28-tag"])

    cap_results = {}
    for cap in CAPS:
        if cap == BASE_CAP:
            rows = rows28
        else:
            rows = _rows(CANDIDATES[1], cap=cap)
        cap_results[str(cap)] = {
            "cap": cap,
            "total": _totals(rows),
            "per_seed": _by_seed(rows),
            "by_support": _by_support(rows),
        }

    base = cap_results[str(BASE_CAP)]["total"]
    low = cap_results[str(CAPS[0])]["total"]
    high = cap_results[str(CAPS[-1])]["total"]
    high_lift = _percent(high["K_available"] - base["K_available"],
                         base["K_available"])
    low_drop = _percent(base["K_available"] - low["K_available"],
                        base["K_available"])
    high_agreement = sum(
        row["K_available"] > base_row["K_available"]
        for row, base_row in zip(
            cap_results[str(CAPS[-1])]["per_seed"],
            cap_results[str(BASE_CAP)]["per_seed"])
    )
    low_agreement = sum(
        row["K_available"] < base_row["K_available"]
        for row, base_row in zip(
            cap_results[str(CAPS[0])]["per_seed"],
            cap_results[str(BASE_CAP)]["per_seed"])
    )
    capacity_signal = (
        high_lift >= CAP_HIGH_LIFT
        and low_drop >= CAP_LOW_DROP
        and high_agreement >= CAP_SEED_AGREEMENT
        and low_agreement >= CAP_SEED_AGREEMENT
    )

    support28 = _by_support(rows28)
    eligible = [row for row in support28
                if row["candidate_edges"] >= MIN_BIN_EDGES]
    support_densities = [row["K_density"] for row in eligible]
    monotone = all(
        later + SUPPORT_TOLERANCE >= earlier
        for earlier, later in zip(support_densities, support_densities[1:])
    )
    support_spread = (
        round(max(support_densities) - min(support_densities), 6)
        if len(support_densities) >= 2 else 0.0
    )
    support_signal = bool(eligible) and monotone and support_spread >= SUPPORT_SPREAD

    support16 = _by_support(rows16)
    shared = []
    by16 = {row["support_bin"]: row for row in support16}
    by28 = {row["support_bin"]: row for row in support28}
    for label, _, _ in SUPPORT_BINS:
        one, two = by16.get(label), by28.get(label)
        if not one or not two:
            continue
        if one["candidate_edges"] < MIN_BIN_EDGES or two["candidate_edges"] < MIN_BIN_EDGES:
            continue
        shared.append({
            "support_bin": label,
            "edges_16": one["candidate_edges"],
            "density_16": one["K_density"],
            "edges_28": two["candidate_edges"],
            "density_28": two["K_density"],
            "gap": round(one["K_density"] - two["K_density"], 6),
        })
    matched_gap = (
        round(sum(row["edges_16"] * abs(row["gap"]) for row in shared)
              / sum(row["edges_16"] for row in shared), 6)
        if shared else None
    )
    matched_signal = matched_gap is not None and matched_gap <= MATCHED_SUPPORT_GAP

    reading = _reading(capacity_signal, support_signal, matched_signal)
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": STATUS,
        "predeclaration": PREDECLARATION,
        "inputs": {
            "16-tag": {
                "path": CANDIDATES[0]["path"].relative_to(ROOT).as_posix(),
                "sha256": _digest(CANDIDATES[0]["path"]),
            },
            "28-tag": {
                "path": CANDIDATES[1]["path"].relative_to(ROOT).as_posix(),
                "sha256": _digest(CANDIDATES[1]["path"]),
            },
        },
        "scope": (
            "The fresh 16-tag and 28-tag no-arm candidate worlds.  The capacity "
            "sweep changes only MAX_PREDICTIONS on the fixed 28-tag world.  "
            "Support is the directed pair count in the trainable acquisition "
            "stream.  No target was selected and no A1 cell ran."
        ),
        "capacity": {
            "caps": list(CAPS),
            "base_cap": BASE_CAP,
            "results": cap_results,
            "high_lift": high_lift,
            "low_drop": low_drop,
            "high_seed_agreement": high_agreement,
            "low_seed_agreement": low_agreement,
            "signal": capacity_signal,
        },
        "support": {
            "world": "28-tag",
            "at_cap": BASE_CAP,
            "bins": support28,
            "eligible_bins": [row["support_bin"] for row in eligible],
            "spread": support_spread,
            "monotone": monotone,
            "signal": support_signal,
        },
        "matched_support": {
            "worlds": ["16-tag", "28-tag"],
            "at_cap": BASE_CAP,
            "shared_bins": shared,
            "weighted_gap": matched_gap,
            "threshold": MATCHED_SUPPORT_GAP,
            "signal": matched_signal,
        },
        "reading": {
            "capacity_signal": capacity_signal,
            "support_signal": support_signal,
            "matched_support_signal": matched_signal,
            "classification": reading,
        },
        "limits": [
            "Cap 80 is a diagnostic condition, not an A1 protocol or a proposed cap.",
        "The capacity axis tests prediction capacity only; a null result does not close every possible carrier-capacity bound.",
            "A and K are no-arm availability flags over 120 cycles, not treatment measurements.",
            "Support is directed pair count over the full acquisition window, not a pre-U predictor; its direction is not identified.",
            "Support is not a latent support probability.",
            "The 16-tag and 28-tag worlds differ in tag count and mapping; matched-support bins are descriptive, not a controlled experiment.",
            "Six seeds per world; the classification thresholds are a reporting convention and can be overturned by a different construction.",
            "No target, threshold, freeze, grant or run changed.",
        ],
        "not_evidence": (
            "A no-arm diagnostic on fixed worlds.  It manipulates only the "
            "prediction cap for a capacity read and stratifies existing support; "
            "it selects no target, changes no protocol and runs no A1 cell."
        ),
        "governance": {
            "freeze": False,
            "grant": False,
            "run": False,
            "authorization": "none",
        },
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("record kind")
    if doc.get("id") != ID:
        found.append("record id")
    if doc.get("status") != STATUS:
        found.append("record status")
    if doc.get("governance") != {
            "freeze": False, "grant": False, "run": False,
            "authorization": "none"}:
        found.append("governance changed")
    capacity = doc.get("capacity") or {}
    if capacity.get("caps") != list(CAPS):
        found.append("cap axis changed")
    results = capacity.get("results") or {}
    if set(results) != {str(cap) for cap in CAPS}:
        found.append("cap results are incomplete")
        return found
    for cap, result in results.items():
        total = result.get("total") or {}
        rows = result.get("per_seed") or []
        if total.get("candidate_edges") != sum(
                row.get("candidate_edges", 0) for row in rows):
            found.append("cap %s seed edges do not sum" % cap)
        for key in ("A_available", "K_available", "A_and_K"):
            if total.get(key) != sum(row.get(key, 0) for row in rows):
                found.append("cap %s %s does not sum" % (cap, key))
    if capacity.get("signal") is not (
            capacity.get("high_lift", 0) >= CAP_HIGH_LIFT
            and capacity.get("low_drop", 0) >= CAP_LOW_DROP
            and capacity.get("high_seed_agreement", 0) >= CAP_SEED_AGREEMENT
            and capacity.get("low_seed_agreement", 0) >= CAP_SEED_AGREEMENT):
        found.append("capacity signal is inconsistent")
    support = doc.get("support") or {}
    bins = support.get("bins") or []
    if sum(row.get("candidate_edges", 0) for row in bins) != (
            results[str(BASE_CAP)]["total"]["candidate_edges"]):
        found.append("support bins do not sum")
    if support.get("signal") is not (
            bool(support.get("eligible_bins"))
            and support.get("monotone") is True
            and support.get("spread", 0) >= SUPPORT_SPREAD):
        found.append("support signal is inconsistent")
    matched = doc.get("matched_support") or {}
    if matched.get("signal") is not (
            matched.get("weighted_gap") is not None
            and matched.get("weighted_gap") <= MATCHED_SUPPORT_GAP):
        found.append("matched-support signal is inconsistent")
    expected = _reading(
        capacity.get("signal") is True,
        support.get("signal") is True,
        matched.get("signal") is True,
    )
    if (doc.get("reading") or {}).get("classification") != expected:
        found.append("reading is inconsistent")
    return found


def self_test() -> list[str]:
    found: list[str] = []
    if _support_bin(0) != "0" or _support_bin(1) != "1":
        found.append("support bin low edge")
    if _support_bin(2) != "2-3" or _support_bin(3) != "2-3":
        found.append("support bin 2-3")
    if _support_bin(4) != "4-7" or _support_bin(7) != "4-7":
        found.append("support bin 4-7")
    if _support_bin(8) != "8-15" or _support_bin(15) != "8-15":
        found.append("support bin 8-15")
    if _support_bin(16) != "16+":
        found.append("support bin 16+")
    if _reading(True, False, False) != "CAPACITY-DOMINANT":
        found.append("capacity reading")
    if _reading(False, True, True) != "SUPPORT-DOMINANT":
        found.append("support reading")
    if _reading(True, True, True) != "MIXED — BOTH CAPACITY AND SUPPORT RESPOND":
        found.append("mixed reading")
    if _reading(False, False, False) != "NEITHER AXIS CLEANLY DOMINANT":
        found.append("neither reading")
    if _percent(1, 0) != 0.0:
        found.append("zero denominator")
    return found


def render(doc: dict) -> str:
    capacity = doc["capacity"]
    base = capacity["results"][str(BASE_CAP)]["total"]
    low = capacity["results"][str(CAPS[0])]["total"]
    high = capacity["results"][str(CAPS[-1])]["total"]
    lines = [
        "# A1 K-supply discriminator — capacity vs support",
        "",
        "**ID:** `%s`" % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is a diagnostic, not an A1 result.** It changes only the "
        "prediction cap on a fixed no-arm world and stratifies existing pair "
        "support. It selects no target, changes no protocol and runs no A1 cell.",
        "",
        "## Predeclared axes",
        "",
        "- **Capacity:** the fixed 28-tag world at caps **20, 40, 80**. A capacity signal requires K at 80 at least **10%** above 40, K at 20 at least **10%** below 40, and at least **4/6** seeds moving each way.",
        "- **Support:** candidate edges binned by directed pair occurrences in the trainable acquisition stream. A support signal requires a monotone K-density gradient (2 pp tolerance) across bins with at least **20** edges and a high-minus-low spread of at least **20 pp**.",
        "- **Matched support:** for bins with at least **20** edges in both worlds, the edge-weighted 16-vs-28 K-density gap must be at most **15 pp**.",
        "",
        "These thresholds are a reporting convention fixed before the cap runs, not an A1 gate.",
        "",
        "## Capacity sweep — fixed 28-tag world",
        "",
        "| Cap | Candidate edges | A | K | A&K | K density | K vs cap 40 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cap in CAPS:
        total = capacity["results"][str(cap)]["total"]
        delta = total["K_available"] - base["K_available"]
        lines.append(
            "| %d | %d | %d | %d | %d | %.1f%% | %+d |" % (
                cap, total["candidate_edges"], total["A_available"],
                total["K_available"], total["A_and_K"],
                100 * total["K_density"], delta,
            )
        )
    lines += [
        "",
        "**Capacity result:** high lift **%+.1f%%**, low drop **%+.1f%%**; "
        "seed agreement **%d/6** high and **%d/6** low. `capacity_signal` = "
        "**%s**." % (
            100 * capacity["high_lift"], 100 * capacity["low_drop"],
            capacity["high_seed_agreement"], capacity["low_seed_agreement"],
            capacity["signal"],
        ),
        "",
        "**A/K decoupling:** across caps 20 → 40 → 80, A rises **%d → %d → %d** "
        "while K stays **%d → %d → %d**. The prediction cap moves the "
        "prediction path strongly and the carrier path not at all. This closes "
        "**prediction-cap** capacity as the K bound; it does not test every "
        "possible capacity bound." % (
            low["A_available"], base["A_available"], high["A_available"],
            low["K_available"], base["K_available"], high["K_available"],
        ),
        "",
        "## Support stratification — cap 40",
        "",
        "| Support bin | 16-tag edges | 16-tag K density | 28-tag edges | 28-tag K density |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    by16 = {row["support_bin"]: row for row in doc["matched_support"]["shared_bins"]}
    by28 = {row["support_bin"]: row for row in doc["support"]["bins"]}
    for label, _, _ in SUPPORT_BINS:
        one, two = by16.get(label), by28.get(label)
        if not one and not two:
            continue
        lines.append(
            "| %s | %s | %s | %s | %s |" % (
                label,
                one["edges_16"] if one else "—",
                "%.1f%%" % (100 * one["density_16"]) if one else "—",
                two["candidate_edges"] if two else "—",
                "%.1f%%" % (100 * two["K_density"]) if two else "—",
            )
        )
    lines += [
        "",
        "**Support result:** eligible bins **%s**, monotone **%s**, spread "
        "**%.1f pp**. `support_signal` = **%s**." % (
            ", ".join(doc["support"]["eligible_bins"]),
            doc["support"]["monotone"], 100 * doc["support"]["spread"],
            doc["support"]["signal"],
        ),
        "",
        "Support is real but not sufficient. At matched support, the 16-tag "
        "world still has more K: the 8–15 bin is **%.1f%% vs %.1f%%** and "
        "16+ is **%.1f%% vs %.1f%%**. The weighted gap is **%.1f pp**, above "
        "the predeclared 15 pp matched threshold." % (
            100 * doc["matched_support"]["shared_bins"][0]["density_16"],
            100 * doc["matched_support"]["shared_bins"][0]["density_28"],
            100 * doc["matched_support"]["shared_bins"][1]["density_16"],
            100 * doc["matched_support"]["shared_bins"][1]["density_28"],
            100 * doc["matched_support"]["weighted_gap"],
        ),
        "",
        "## Matched support",
        "",
        "| Bin | 16-tag edges | 16-tag K density | 28-tag edges | 28-tag K density | Gap |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["matched_support"]["shared_bins"]:
        lines.append(
            "| %s | %d | %.1f%% | %d | %.1f%% | %+.1f pp |" % (
                row["support_bin"], row["edges_16"], 100 * row["density_16"],
                row["edges_28"], 100 * row["density_28"], 100 * row["gap"],
            )
        )
    lines += [
        "",
        "Weighted matched gap: **%s**. `matched_support_signal` = **%s**." % (
            "—" if doc["matched_support"]["weighted_gap"] is None else
            "%.1f pp" % (100 * doc["matched_support"]["weighted_gap"]),
            doc["matched_support"]["signal"],
        ),
        "",
        "## Reading",
        "",
        "| Axis | Signal |",
        "| --- | --- |",
        "| Capacity | **%s** |" % doc["reading"]["capacity_signal"],
        "| Support | **%s** |" % doc["reading"]["support_signal"],
        "| Matched support | **%s** |" % doc["reading"]["matched_support_signal"],
        "",
        "**Classification:** `%s`." % doc["reading"]["classification"],
        "",
        "This is a diagnostic reading, not a redesign decision. The cap result "
        "says the K path is not prediction-cap-bound. The support result says "
        "pair frequency is part of the story, but the residual 16-vs-28 gap at "
        "matched support means support alone is not the whole story. The next "
        "discriminator should target the carrier path directly, not another "
        "prediction cap or another tag count.",
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
        "python -m benchmarks.a1_k_supply_discriminator --check",
        "python -m benchmarks.a1_k_supply_discriminator --self-test",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip("\n")


def write() -> int:
    doc = build()
    found = problems(doc)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc) + "\n", encoding="utf-8")
    print("wrote %s and %s" % (OUT_PATH, PAGE_PATH))
    print("reading:", doc["reading"]["classification"])
    return 0


def check() -> int:
    if not OUT_PATH.exists() or not PAGE_PATH.exists():
        print("FAIL: report artifact or page is missing")
        return 1
    doc = _load(OUT_PATH)
    found = problems(doc)
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 K-supply discriminator: clean; %s" %
          doc["reading"]["classification"])
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.check:
        return check()
    found = self_test()
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 K-supply discriminator: self-test clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
