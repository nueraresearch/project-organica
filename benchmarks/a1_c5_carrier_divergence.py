"""A1 C5 carrier divergence — the two carrier cycles as measured data, per block.

`a1_c5_target_timing` reports `earliest_observed_carrier_cycle` (over the 120
N=20 rows) beside `earliest_current_carrier_cycle` (over the 24 current Path A
rows).  On the first block those two quantities were equal, so they read as one
quantity; the 2071 screening separated them, and the adopted block separates them
again while still clearing C5.  That divergence is what makes the two fields
different observables rather than two names for one number — and until now it
lived only in changelog prose, with the failing case having no artifact behind it.

This module keeps it as data.  For each recorded block it recomputes the N=4 and
N=20 target selections, replays the registered 120-cycle world with no arm
applied, and records both cycles with the C5 verdict they produce.  The equality
case from 20630101-20630106 is cited from its superseded artifact (commit
61ac416) rather than re-measured: that block is spent by
A1-BASELINE-AVAILABILITY-1, and a spent block is not reused.

No A1 cell is run, no target is frozen, and nothing here selects a target.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import a1_c5_target_timing as c5
from benchmarks import a1_c8_target_selection as c8
from benchmarks import a1_target_selection as n4
from benchmarks.a1_c5_target_timing import U_CYCLE

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_PATH = DOCS / "a1_c5_carrier_divergence.json"
PAGE_PATH = DOCS / "A1-C5-CARRIER-DIVERGENCE.md"
ID = "A1-C5-CARRIER-DIVERGENCE-1"
DATE = "2026-11-15"
KIND = "a1_c5_carrier_divergence"

# The blocks this record measures.  A block is recorded by prefix: seeds are
# prefix * 10000 + 100 + i, the repository's block convention.
BLOCKS = (
    {
        "block": 2074,
        "role": "ADOPTED CANDIDATE",
        "note": "A1-TWO-PATH-1's candidate block; clears C5",
    },
    {
        "block": 2071,
        "role": "SCREENED — REJECTED BY C5",
        "note": "forms both selections and fails C5; the separation case",
    },
)

# Cited, not re-measured: the equality case.  Its artifact was overwritten when
# the block moved, and its seeds are spent, so re-running it would be reuse.
CITED = (
    {
        "block": 2063,
        "role": "SUPERSEDED — EQUALITY CASE",
        "earliest_observed_carrier_cycle": 5,
        "earliest_current_carrier_cycle": 5,
        "verdict": "CLEARS C5",
        "source": "docs/a1_c5_target_timing.json at commit 61ac416",
        "measured_here": False,
        "why_not_remeasured": (
            "20630101-20630106 is spent by A1-BASELINE-AVAILABILITY-1; a spent "
            "block is not reused, so this row is cited from its superseded "
            "artifact rather than re-derived"),
    },
)


def _seeds(block: int) -> tuple[int, ...]:
    return tuple(block * 10000 + 100 + i for i in range(1, 7))


def measure_block(block: int) -> dict:
    """Recompute both target selections, replay, and report both cycles."""
    seeds = _seeds(block)
    per_seed = []
    for seed in seeds:
        current_row = n4.run_seed(seed)
        current = list(current_row["selected"])
        twenty_row = c8.run_seed(seed, n=c8.N_PER_SEED, disjoint=False,
                                 max_endpoint_degree=c8.MAX_ENDPOINT_DEGREE)
        twenty = list(twenty_row["selected"])
        c5._CURRENT_CACHE[seed] = set(current)
        replay = c5._run_seed(seed, {tuple(edge.split(">", 1)) for edge in twenty})
        observed = [row["carrier_cycle"] for row in replay["rows"]
                    if row["carrier_cycle"] is not None]
        current_cycles = [row["carrier_cycle"] for row in replay["current_rows"]
                          if row["carrier_cycle"] is not None]
        per_seed.append({
            "seed": seed,
            "n4_rows": len(current),
            "n20_rows": len(twenty),
            "earliest_observed_carrier_cycle": min(observed, default=None),
            "earliest_current_carrier_cycle": min(current_cycles, default=None),
            "observed_carriers": len(observed),
            "missing_carriers": len(replay["rows"]) - len(observed),
            "carriers_at_or_before_u": sum(1 for cycle in observed
                                           if cycle <= U_CYCLE),
        })
    observed_all = [row["earliest_observed_carrier_cycle"] for row in per_seed
                    if row["earliest_observed_carrier_cycle"] is not None]
    current_all = [row["earliest_current_carrier_cycle"] for row in per_seed
                   if row["earliest_current_carrier_cycle"] is not None]
    earliest_observed = min(observed_all, default=None)
    earliest_current = min(current_all, default=None)
    before_u = sum(row["carriers_at_or_before_u"] for row in per_seed)
    clears = (earliest_observed is not None and earliest_current is not None
              and earliest_observed > U_CYCLE and earliest_current > U_CYCLE
              and before_u == 0)
    return {
        "block": block,
        "seeds": list(seeds),
        "u_cycle": U_CYCLE,
        "n20_rows": sum(row["n20_rows"] for row in per_seed),
        "current_rows": sum(row["n4_rows"] for row in per_seed),
        "earliest_observed_carrier_cycle": earliest_observed,
        "earliest_current_carrier_cycle": earliest_current,
        "current_minus_observed": (None if earliest_current is None
                                   or earliest_observed is None
                                   else earliest_current - earliest_observed),
        "observed_carriers": sum(row["observed_carriers"] for row in per_seed),
        "missing_carriers": sum(row["missing_carriers"] for row in per_seed),
        "carriers_at_or_before_u": before_u,
        "verdict": "CLEARS C5" if clears else "FAILS C5",
        "per_seed": per_seed,
        "measured_here": True,
    }


def build() -> dict:
    measured = []
    for spec in BLOCKS:
        row = measure_block(spec["block"])
        row["role"] = spec["role"]
        row["note"] = spec["note"]
        measured.append(row)
    cited = [dict(row) for row in CITED]

    divergent = [row["block"] for row in measured
                 if row["current_minus_observed"] not in (None, 0)]
    equal = [row["block"] for row in measured
             if row["current_minus_observed"] == 0]
    divergence_with_pass = any(
        row["current_minus_observed"] not in (None, 0)
        and row["verdict"] == "CLEARS C5" for row in measured)
    divergence_with_failure = any(
        row["current_minus_observed"] not in (None, 0)
        and row["verdict"] == "FAILS C5" for row in measured)

    adopted = next(row for row in measured if row["role"] == "ADOPTED CANDIDATE")
    audit = json.loads((DOCS / "a1_c5_target_timing.json").read_text(encoding="utf-8"))
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": (
            "MEASURED \u2014 OBSERVED AND CURRENT CARRIER CYCLES DIVERGE AND ARE "
            "DISTINCT OBSERVABLES"),
        "definitions": {
            "earliest_observed_carrier_cycle": (
                "the earliest cycle at which any of the 120 N=20 target rows is "
                "carried; the cycle the selection-time reading is about"),
            "earliest_current_carrier_cycle": (
                "the earliest cycle at which any of the 24 current Path A target "
                "rows is carried; the cycle the C5 flag reads"),
            "why_they_are_not_one_quantity": (
                "the current rows are four of the twenty per seed, so the observed "
                "minimum can only be earlier or equal; equality on a block is a "
                "coincidence of that block's carriers, not an identity"),
        },
        "blocks": measured,
        # Declared so the reservation scan can see this record: it measures the
        # reserved candidate block and one unreserved screening block.
        "seed_block": adopted["seeds"],
        "seed_block_note": (
            "the reserved A1-TWO-PATH-1 candidate block this record measures; the "
            "second measured block (2071) is unreserved, and the cited equality "
            "case's block is spent"),
        "cited_cases": cited,
        "finding": {
            "divergent_blocks_measured": divergent,
            "equal_blocks_measured": equal,
            "divergence_with_clearing_c5": divergence_with_pass,
            "divergence_with_failing_c5": divergence_with_failure,
            "statement": (
                "The two cycles are distinct observables: they diverge in a block "
                "that clears C5 and in a block that fails it, so neither value "
                "implies the other and neither verdict follows from the divergence "
                "itself. The earlier block where they were equal is cited, not "
                "re-measured, because its seeds are spent."),
            "what_this_does_not_establish": (
                "that either cycle predicts a C5 outcome, or that any block is "
                "typical. Two measured blocks cannot order a population."),
        },
        "adopted_block_cross_check": {
            "audit": "docs/a1_c5_target_timing.json",
            "audit_earliest_observed_carrier_cycle": audit[
                "earliest_observed_carrier_cycle"],
            "audit_earliest_current_carrier_cycle": audit[
                "earliest_current_carrier_cycle"],
            "measured_earliest_observed_carrier_cycle": adopted[
                "earliest_observed_carrier_cycle"],
            "measured_earliest_current_carrier_cycle": adopted[
                "earliest_current_carrier_cycle"],
            "agrees": (
                audit["earliest_observed_carrier_cycle"]
                == adopted["earliest_observed_carrier_cycle"]
                and audit["earliest_current_carrier_cycle"]
                == adopted["earliest_current_carrier_cycle"]),
        },
        "replay": {
            "cycles": c5.REPLAY_CYCLES,
            "cap": c5.CAP,
            "arm": "none \u2014 the registered world is replayed with no treatment",
        },
        "not_evidence": (
            "A no-arm record of two carrier cycles per block. It runs no A1 cell, "
            "freezes no target, changes no threshold and makes no causal, "
            "capability or transfer claim. It does not select, reserve or spend a "
            "seed block."),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("kind")
    if doc.get("id") != ID:
        found.append("id")
    blocks = doc.get("blocks") or []
    if not blocks:
        found.append("no measured block")
    for row in blocks:
        observed = row.get("earliest_observed_carrier_cycle")
        current = row.get("earliest_current_carrier_cycle")
        if observed is None or current is None:
            found.append("block %s has no carrier cycle" % row.get("block"))
            continue
        per_seed = row.get("per_seed") or []
        if len(per_seed) != 6:
            found.append("block %s does not record six seeds" % row["block"])
        if observed != min(s["earliest_observed_carrier_cycle"] for s in per_seed
                           if s["earliest_observed_carrier_cycle"] is not None):
            found.append("block %s observed cycle is not the per-seed minimum"
                         % row["block"])
        if current != min(s["earliest_current_carrier_cycle"] for s in per_seed
                          if s["earliest_current_carrier_cycle"] is not None):
            found.append("block %s current cycle is not the per-seed minimum"
                         % row["block"])
        if row.get("current_minus_observed") != current - observed:
            found.append("block %s difference is inconsistent" % row["block"])
        if row.get("n20_rows") != 120 or row.get("current_rows") != 24:
            found.append("block %s row counts are not 120/24" % row["block"])
        clears = (observed > doc["blocks"][0]["u_cycle"]
                  and current > doc["blocks"][0]["u_cycle"]
                  and row.get("carriers_at_or_before_u") == 0)
        if (row.get("verdict") == "CLEARS C5") != clears:
            found.append("block %s verdict does not follow its cycles" % row["block"])
    check = doc.get("adopted_block_cross_check") or {}
    if check.get("agrees") is not True:
        found.append("the adopted block disagrees with the C5 audit")
    finding = doc.get("finding") or {}
    if finding.get("divergence_with_clearing_c5") and finding.get(
            "divergence_with_failing_c5"):
        divergent = [row for row in blocks
                     if row.get("current_minus_observed") not in (None, 0)]
        if len(divergent) != len(blocks):
            found.append("the distinctness claim has a block with equal cycles")
    return found


def render(doc: dict) -> str:
    lines = [
        "# A1 C5 carrier divergence — the two cycles, measured per block",
        "",
        "**ID:** `%s`" % doc["id"],
        "",
        "**Date:** %s" % doc["date"],
        "",
        "**Status:** `%s`" % doc["status"],
        "",
        "`earliest_observed_carrier_cycle` is the earliest cycle any of the **120** "
        "N=20 rows is carried; `earliest_current_carrier_cycle` is the earliest "
        "cycle any of the **24** current Path A rows is carried. The current rows "
        "are four of the twenty per seed, so the observed minimum can only be "
        "earlier or equal — equality on a block is a coincidence of that block's "
        "carriers, not an identity.",
        "",
        "## 1. Measured blocks",
        "",
        "| Block | Role | Observed | Current | Current − observed | Before U=%d | Carriers / missing | Verdict |"
        % doc["blocks"][0]["u_cycle"],
        "| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in doc["blocks"]:
        lines.append("| %d | %s | %s | %s | %+d | %d | %d / %d | **%s** |" % (
            row["block"], row["role"],
            row["earliest_observed_carrier_cycle"],
            row["earliest_current_carrier_cycle"],
            row["current_minus_observed"], row["carriers_at_or_before_u"],
            row["observed_carriers"], row["missing_carriers"], row["verdict"]))
    lines += [
        "",
        "## 2. The equality case, cited rather than re-measured",
        "",
        "| Block | Role | Observed | Current | Verdict | Source |",
        "| ---: | --- | ---: | ---: | --- | --- |",
    ]
    for row in doc["cited_cases"]:
        lines.append("| %d | %s | %d | %d | %s | %s |" % (
            row["block"], row["role"],
            row["earliest_observed_carrier_cycle"],
            row["earliest_current_carrier_cycle"], row["verdict"],
            row["source"]))
    lines += [
        "",
        "**Why it is cited:** %s" % doc["cited_cases"][0]["why_not_remeasured"] + ".",
        "",
        "## 3. What the record establishes",
        "",
        doc["finding"]["statement"],
        "",
        "- Divergent blocks measured: %s." % ", ".join(
            str(b) for b in doc["finding"]["divergent_blocks_measured"]),
        "- Divergence with a clearing C5: **%s**; divergence with a failing C5: **%s**."
        % (doc["finding"]["divergence_with_clearing_c5"],
           doc["finding"]["divergence_with_failing_c5"]),
        "",
        "**What this does not establish:** %s" % doc["finding"][
            "what_this_does_not_establish"],
        "",
        "## 4. Cross-check against the C5 audit",
        "",
        "The adopted block is measured here twice: once by this record, once by "
        "`a1_c5_target_timing`. Both readings agree — observed **%s**, current "
        "**%s** — which is what keeps this record from becoming a second account "
        "of the same block." % (
            doc["adopted_block_cross_check"]["agreed_observed"]
            if "agreed_observed" in doc["adopted_block_cross_check"]
            else doc["adopted_block_cross_check"][
                "measured_earliest_observed_carrier_cycle"],
            doc["adopted_block_cross_check"][
                "measured_earliest_current_carrier_cycle"]),
        "",
        "## 5. Replay",
        "",
        "`%d` cycles per seed, prediction cap `%d`, %s." % (
            doc["replay"]["cycles"], doc["replay"]["cap"], doc["replay"]["arm"]),
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "Reproduce with `python -m benchmarks.a1_c5_carrier_divergence --write`; "
        "`--check` verifies the record and this page.",
    ]
    return "\n".join(lines)


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
    for row in doc["blocks"]:
        print("  block %d: observed %s, current %s, %s" % (
            row["block"], row["earliest_observed_carrier_cycle"],
            row["earliest_current_carrier_cycle"], row["verdict"]))
    return 0


def check() -> int:
    if not OUT_PATH.exists():
        print("FAIL: %s is missing" % OUT_PATH)
        return 1
    doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    found = problems(doc)
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 C5 carrier divergence: clean; %d measured block(s), %d cited case(s)"
          % (len(doc["blocks"]), len(doc["cited_cases"])))
    return 0


def self_test() -> list[str]:
    found: list[str] = []
    doc = {
        "kind": KIND,
        "id": ID,
        "blocks": [{
            "block": 2999,
            "u_cycle": U_CYCLE,
            "n20_rows": 120,
            "current_rows": 24,
            "earliest_observed_carrier_cycle": 6,
            "earliest_current_carrier_cycle": 8,
            "current_minus_observed": 2,
            "carriers_at_or_before_u": 0,
            "verdict": "CLEARS C5",
            "per_seed": [{
                "seed": 29990101 + i,
                "earliest_observed_carrier_cycle": 6,
                "earliest_current_carrier_cycle": 8,
            } for i in range(6)],
        }],
        "adopted_block_cross_check": {"agrees": True},
        "finding": {"divergence_with_clearing_c5": True,
                    "divergence_with_failing_c5": False},
    }
    if problems(doc):
        found.append("a consistent fixture was rejected: %s" % problems(doc))
    broken = json.loads(json.dumps(doc))
    broken["blocks"][0]["earliest_current_carrier_cycle"] = 5
    if not problems(broken):
        found.append("an inconsistent current cycle was accepted")
    broken = json.loads(json.dumps(doc))
    broken["adopted_block_cross_check"]["agrees"] = False
    if not problems(broken):
        found.append("a disagreement with the C5 audit was accepted")
    broken = json.loads(json.dumps(doc))
    broken["blocks"][0]["per_seed"][0]["earliest_observed_carrier_cycle"] = 3
    if not problems(broken):
        found.append("a non-minimum observed cycle was accepted")
    return found


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
        print("A1 C5 carrier divergence: self-test clean")
        return 0
    if args.write:
        return write()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
