"""C5 target timing, re-established on the competent block.

`A1-C5-TARGET-TIMING` cleared the cycle-4 protocol against the **representative** N=20 block. Adopting
`DECISION-A1-COMPETENT-ESTIMAND` replaced that block with the competent one, and the two share only 37
of 115 rows — so 78 rows have never been checked against the protocol that is supposed to clear them.
Signing an act that freezes those rows on the earlier audit would freeze rows no timing check covers.

This module replays the registered 120-cycle world with no arm, exactly as the original audit does, and
records the cycle-4 `U` and the first carrier cycle for every row of the competent block. A row passes
when its `U` is at or before its first carrier; a row with no observed carrier passes the timing rule
and is reported as such, because an absent carrier is not a timing violation.

    python -m benchmarks.a1_c5_competent_audit --write
    python -m benchmarks.a1_c5_competent_audit --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from benchmarks import a1_c5_target_timing as timing, engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

TARGETS = DOCS / "a1_c8_target_selection_competent.json"
OUT = DOCS / "a1_c5_target_timing_competent.json"
PAGE = DOCS / "A1-C5-TARGET-TIMING-COMPETENT.md"

ID = "A1-C5-TARGET-TIMING-COMPETENT-1"
DATE = "2026-11-15"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    sets = timing._target_set(TARGETS)
    rows = [timing._run_seed(seed, sets[seed]) for seed in timing.SEEDS]
    flat = [(group["seed"], row) for group in rows for row in group["rows"]]
    late = [(seed, row["edge"], row["u"], row["carrier_cycle"])
            for seed, row in flat if not row["u_before_carrier"]]
    return {
        "kind": "a1_c5_target_timing_competent",
        "id": ID,
        "date": DATE,
        "status": ("PASS — EVERY ROW OF THE COMPETENT BLOCK HAS ITS CYCLE-4 U AT OR BEFORE ITS FIRST CARRIER; "
                   "NO CELL RUN" if not late else
                   "FAIL — %d ROWS HAVE A CARRIER BEFORE THEIR CYCLE-4 U; THE BLOCK IS NOT CLEARED" % len(late)),
        "targets": TARGETS.name,
        "targets_digest": _digest(TARGETS),
        "u_cycle": timing.U_CYCLE,
        "seeds": rows,
        "totals": {
            "rows": len(flat),
            "late": len(late),
            "observed_carriers": sum(group["observed_carriers"] for group in rows),
            "missing_carriers": sum(group["missing_carriers"] for group in rows),
        },
        "late_rows": late,
        "not_evidence": ("A no-arm replay that checks one timing rule on the competent target block. It runs no "
                         "A1 cell, applies no arm, freezes no manifest, makes no causal claim and does not measure "
                         "C2, C8 or any other gate."),
    }


def render(doc: dict) -> str:
    totals = doc["totals"]
    lines = [
        "# C5 target timing on the competent block",
        "",
        "**ID:** `%s`  " % doc["id"],
        "**Date:** %s  " % doc["date"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an A1 result.** A no-arm replay checking one timing rule against the block that "
        "[`DECISION-A1-COMPETENT-ESTIMAND`](DECISION-A1-COMPETENT-ESTIMAND.md) adopted. No cell ran and no arm was applied.",
        "",
        "## Why this audit exists",
        "",
        "[`A1-C5-TARGET-TIMING`](A1-C5-TARGET-TIMING.md) cleared the cycle-4 protocol against the **representative** N=20 "
        "block. The competent block replaced it and shares only **37 of its 115 rows** with it, so **78 rows** were never "
        "checked against the protocol that clears them. A freeze would otherwise rest on an audit of a different block.",
        "",
        "## Rule, and what passes",
        "",
        "The protocol fixes the C5 baseline `U` at cycle **%d**, so a target row is clear when its `U` is at or before its "
        "first carrier. A row with no observed carrier by cycle 120 is clear by the rule and is reported separately: an "
        "absent carrier is not a timing violation." % doc["u_cycle"],
        "",
        "| | value |",
        "| --- | ---: |",
        "| Rows audited | **%d** |" % totals["rows"],
        "| Rows with a carrier before `U` | **%d** |" % totals["late"],
        "| Rows with an observed carrier | %d |" % totals["observed_carriers"],
        "| Rows with no carrier by cycle 120 | %d |" % totals["missing_carriers"],
        "",
        "## Per seed",
        "",
        "| Seed | Rows | Observed carriers | No carrier | Late |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for group in doc["seeds"]:
        late = sum(1 for row in group["rows"] if not row["u_before_carrier"])
        lines.append("| `%d` | %d | %d | %d | **%d** |"
                     % (group["seed"], len(group["rows"]), group["observed_carriers"],
                        group["missing_carriers"], late))
    if doc["late_rows"]:
        lines += ["", "**Late rows.**", "", "| Seed | Edge | `U` | First carrier |", "| ---: | --- | ---: | ---: |"]
        for seed, edge, u, carrier in doc["late_rows"]:
            lines.append("| `%d` | `%s` | %s | %s |" % (seed, edge, u, carrier))
    lines += [
        "",
        "## Limits",
        "",
        "- It checks **one** rule, on **this** block. It does not re-clear C1, C4, C7 or C8, and it does not measure any of them.",
        "- It replays the world without an arm. A timing rule that holds without an arm is the same class of statement the "
        "earlier audit made; it is not evidence that a treatment cell's `U` will land in the same place.",
        "- The block is not a superset of the previous one: **7 of the 24 current-target observations survive** into it "
        "(0 of 4 on seeds `20740102` and `20740104`). Whatever continuity the earlier block had with the N=4 design does not "
        "carry over, and this audit does not restore it.",
        "",
        "**Not evidence:** " + doc["not_evidence"],
        "",
        "## Provenance",
        "",
        "| Artifact | sha256 |",
        "| --- | --- |",
        "| `%s` | `%s` |" % (doc["targets"], doc["targets_digest"]),
        "",
        "_Generated by `python -m benchmarks.a1_c5_competent_audit --write`; `--check` replays the world and fails when this "
        "page or artifact disagrees with the replay._",
        "",
    ]
    return "\n".join(lines)


def problems() -> list[str]:
    doc = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else None
    if doc is None:
        return ["the competent-block timing audit is missing"]
    rebuilt = build()
    found = []
    if engine_stamp.stamp(doc) != engine_stamp.stamp(rebuilt):
        found.append("the audit artifact is stale against a fresh replay")
    text = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
    if text.strip() != render(rebuilt).strip():
        found.append("the page is stale against the audit artifact")
    if rebuilt["totals"]["late"]:
        found.append("%d rows have a carrier before their cycle-4 U" % rebuilt["totals"]["late"])
    return found


def write() -> int:
    doc = engine_stamp.stamp(build())
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE.write_text(render(doc), encoding="utf-8")
    print("wrote %s: %d rows, %d late, %d without a carrier"
          % (OUT.name, doc["totals"]["rows"], doc["totals"]["late"], doc["totals"]["missing_carriers"]))
    return 0


def check() -> int:
    found = problems()
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 C5 competent timing: clean; no cell run")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return write() if args.write else check()


if __name__ == "__main__":
    sys.exit(main())
