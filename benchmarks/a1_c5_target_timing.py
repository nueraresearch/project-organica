"""C5 target timing: a fixed earlier-U sample before any preserved target carrier.

The target-selection pass keeps its cycle-36 diagnostic because that is where
the four-target and N=20 eligibility artifacts were formed.  C5 needs a
different sample: an edge-level covariate measured before a carrier can form.
A no-arm replay of the registered worlds found the earliest carrier at cycle 5,
so this protocol fixes the C5 baseline at cycle 4, before that carrier and
before the cycle-4 sleep call.  It does not change a target edge.

    python -m benchmarks.a1_c5_target_timing --write
    python -m benchmarks.a1_c5_target_timing --check
    python -m benchmarks.a1_c5_target_timing --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from benchmarks import a1_arms
from benchmarks.acquisition_compositional import generate_compositional_world
from benchmarks.acquisition_harness import _CountingMemoryService, _make_scratch_db
from benchmarks.acquisition_runner import EVENTS_PER_CYCLE, PHASE_ACQUISITION

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CURRENT_PATH = DOCS / "a1_target_selection.json"
N20_PATH = DOCS / "a1_c8_target_selection.json"
AUDIT_PATH = DOCS / "a1_c5_target_timing.json"
PAGE_PATH = DOCS / "A1-C5-TARGET-TIMING.md"
ID = "A1-C5-TARGET-TIMING-1"
DATE = "2026-11-14"
KIND = "a1_c5_target_timing"
U_CYCLE = 4
SELECTION_U_CYCLE = 36
REPLAY_CYCLES = 120
CAP = 40
SEEDS = (20630101, 20630102, 20630103, 20630104, 20630105, 20630106)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _selected(path: Path, seed: int) -> list[str]:
    row = (_load(path).get("per_seed") or {}).get(str(seed)) or {}
    return list(row.get("selected") or [])


def _run_seed(seed: int, targets: set[tuple[str, str]]) -> dict:
    """Replay the registered 120-cycle world with no arm applied."""
    world = generate_compositional_world(seed=seed, cycles=REPLAY_CYCLES)
    db_path = _make_scratch_db("a1_c5_target_timing")
    memory = _CountingMemoryService(str(db_path))
    service = a1_arms.A1ArmSleepService(memory)
    service.MAX_PREDICTIONS = CAP
    carrier_first: dict[tuple[str, str], int] = {}
    u_at_cycle: dict[tuple[str, str], dict] = {}
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    try:
        for i, (text, trainable) in enumerate(zip(world["events"], world["trainable"])):
            in_acq = event_lo <= i < event_hi
            if in_acq and not trainable:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                memory.current_cycle = i // EVENTS_PER_CYCLE
            memory.store(text, event_type="observe",
                         source=a1_arms.ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                cycle = (i + 1) // EVENTS_PER_CYCLE
                if cycle == U_CYCLE:
                    u_at_cycle = a1_arms.sample_u(memory, targets, U_CYCLE)
                report = service.run_sleep_cycle()
                for edge in targets:
                    if edge in a1_arms._carrier_edges(report):
                        carrier_first.setdefault(edge, cycle)
    finally:
        memory.close()
        db_path.unlink(missing_ok=True)

    rows = []
    for edge in sorted(targets):
        carrier = carrier_first.get(edge)
        u = u_at_cycle.get(edge, {
            "direct_count": None,
            "reverse_count": None,
            "strength": None,
            "measured_cycle": None,
        })
        rows.append({
            "seed": seed,
            "edge": "%s>%s" % edge,
            "carrier_cycle": carrier,
            "u": u,
            "u_before_carrier": carrier is None or U_CYCLE <= carrier,
        })
    return {
        "seed": seed,
        "rows": rows,
        "current_rows": [
            row for row in rows
            if not _CURRENT_CACHE.get(seed) or row["edge"] in _CURRENT_CACHE[seed]
        ],
        "observed_carriers": sum(1 for row in rows if row["carrier_cycle"] is not None),
        "missing_carriers": sum(1 for row in rows if row["carrier_cycle"] is None),
    }


_CURRENT_CACHE: dict[int, set[str]] = {}


def _target_set(path: Path, seeds=SEEDS) -> dict[int, set[tuple[str, str]]]:
    found: dict[int, set[tuple[str, str]]] = {}
    for seed in seeds:
        found[seed] = {tuple(edge.split(">", 1)) for edge in _selected(path, seed)}
    return found


def _current_sets() -> dict[int, set[str]]:
    return {seed: set(_selected(CURRENT_PATH, seed)) for seed in SEEDS}


def _n20_sets() -> dict[int, set[tuple[str, str]]]:
    return _target_set(N20_PATH)


def _problems_for(rows: list[dict], *, require_all_carriers: bool = False) -> list[str]:
    found: list[str] = []
    for row in rows:
        u = row.get("u") or {}
        for field in ("direct_count", "reverse_count", "strength", "measured_cycle"):
            if u.get(field) is None:
                found.append("seed %s edge %s has no %s at cycle %d"
                             % (row.get("seed"), row.get("edge"), field, U_CYCLE))
        if u.get("measured_cycle") not in (None, U_CYCLE):
            found.append("seed %s edge %s has a different U cycle"
                         % (row.get("seed"), row.get("edge")))
        carrier = row.get("carrier_cycle")
        if carrier is None:
            if require_all_carriers:
                found.append("seed %s edge %s has no carrier" % (row.get("seed"), row.get("edge")))
            continue
        if not isinstance(carrier, int) or carrier < U_CYCLE:
            found.append("seed %s edge %s has a carrier before cycle %d"
                         % (row.get("seed"), row.get("edge"), U_CYCLE))
    return found


def build() -> dict:
    global _CURRENT_CACHE
    _CURRENT_CACHE = _current_sets()
    current = _current_sets()
    n20 = _n20_sets()
    per_seed = []
    for seed in SEEDS:
        row = _run_seed(seed, n20[seed])
        row["preserved"] = sorted(current[seed])
        row["preserved_count"] = len(current[seed])
        row["preserved_rows"] = [
            row_row for row_row in row["current_rows"]
            if row_row["edge"] in current[seed]
        ]
        row["n20_count"] = len(n20[seed])
        row["all_current_retained"] = current[seed] <= {
            "%s>%s" % edge for edge in n20[seed]
        }
        per_seed.append(row)
    current_rows = [row for seed_row in per_seed for row in seed_row["preserved_rows"]]
    n20_rows = [row for seed_row in per_seed for row in seed_row["rows"]]
    observed = [row for row in n20_rows if row["carrier_cycle"] is not None]
    current_observed = [row for row in current_rows if row["carrier_cycle"] is not None]
    earliest = min((row["carrier_cycle"] for row in observed), default=None)
    current_earliest = min((row["carrier_cycle"] for row in current_observed), default=None)
    before = [row for row in observed if row["carrier_cycle"] < U_CYCLE]
    current_before = [row for row in current_observed if row["carrier_cycle"] < U_CYCLE]
    problems = _problems_for(n20_rows)
    for seed_row in per_seed:
        if not seed_row["all_current_retained"]:
            problems.append("seed %s does not retain every current target" % seed_row["seed"])
        if seed_row["preserved_count"] != 4:
            problems.append("seed %s does not have four preserved targets" % seed_row["seed"])
    if len(current_rows) != 24:
        problems.append("current target rows are not 24")
    if len(n20_rows) != 120:
        problems.append("N=20 target rows are not 120")
    if earliest is None or earliest <= U_CYCLE:
        problems.append("no observed carrier is after the fixed U cycle")
    if current_before:
        problems.append("a current target carrier is before the fixed U cycle")
    return {
        "kind": KIND,
        "id": ID,
        "date": DATE,
        "status": (
            "PASS — FIXED EARLIER-U AT CYCLE 4; ALL CURRENT TARGETS PRESERVED"
            if not problems else "FAIL — C5 TIMING NOT CLEARED"
        ),
        "u_cycle": U_CYCLE,
        "selection_u_cycle": SELECTION_U_CYCLE,
        "replay_cycles": REPLAY_CYCLES,
        "rule": (
            "C5 U is sampled after the cycle-4 observations are stored and before "
            "the cycle-4 sleep call. The cycle-36 sample remains the target-selection "
            "diagnostic and is not the C5 baseline."
        ),
        "preserved": True,
        "current_target_observations": len(current_rows),
        "n20_target_observations": len(n20_rows),
        "current_observed_carriers": len(current_observed),
        "current_missing_carriers": len(current_rows) - len(current_observed),
        "current_carriers_before_u": len(current_before),
        "earliest_observed_carrier_cycle": earliest,
        "earliest_current_carrier_cycle": current_earliest,
        "u_before_earliest_carrier": earliest is not None and U_CYCLE < earliest,
        "problems": problems,
        "per_seed": per_seed,
        "current_rows": current_rows,
        "n20_rows": n20_rows,
        "not_evidence": (
            "A no-arm target-timing audit. It runs no A1 cell, freezes no "
            "target and makes no causal, capability or transfer claim. C5 remains "
            "unrun until a granted cell produces its own U and carrier rows."
        ),
    }


def problems(doc: dict) -> list[str]:
    found: list[str] = []
    if doc.get("kind") != KIND:
        found.append("audit kind")
    if doc.get("id") != ID:
        found.append("audit id")
    if doc.get("u_cycle") != U_CYCLE or doc.get("selection_u_cycle") != SELECTION_U_CYCLE:
        found.append("audit U boundary changed")
    if doc.get("preserved") is not True:
        found.append("the audit does not preserve the current targets")
    if doc.get("current_target_observations") != 24:
        found.append("current target count changed")
    if doc.get("n20_target_observations") != 120:
        found.append("N=20 target count changed")
    if doc.get("current_carriers_before_u") != 0:
        found.append("a current carrier precedes U")
    if doc.get("current_missing_carriers") != 10:
        found.append("current missing-carrier count changed")
    if doc.get("current_observed_carriers") != 14:
        found.append("current observed-carrier count changed")
    if doc.get("earliest_observed_carrier_cycle") != 5:
        found.append("earliest carrier cycle changed")
    if doc.get("earliest_current_carrier_cycle") != 5:
        found.append("earliest current carrier cycle changed")
    if doc.get("u_before_earliest_carrier") is not True:
        found.append("U is not before the earliest carrier")
    found.extend(doc.get("problems") or [])
    current = _current_sets()
    rows = doc.get("current_rows") or []
    if len(rows) != 24:
        found.append("current rows are not 24")
    for seed in SEEDS:
        edges = {row.get("edge") for row in rows if row.get("seed") == seed}
        if edges != current[seed]:
            found.append("seed %d current rows do not match the target artifact" % seed)
    found.extend(_problems_for(rows))
    n20 = doc.get("n20_rows") or []
    if len(n20) != 120:
        found.append("N=20 rows are not 120")
    expected_n20 = _n20_sets()
    for seed in SEEDS:
        edges = {row.get("edge") for row in n20 if row.get("seed") == seed}
        wanted = {"%s>%s" % edge for edge in expected_n20[seed]}
        if edges != wanted:
            found.append("seed %d N=20 rows do not match the expansion artifact" % seed)
    found.extend(_problems_for(n20))
    return found


def self_test() -> list[str]:
    found: list[str] = []
    good = {
        "seed": 1,
        "edge": "a>b",
        "carrier_cycle": 5,
        "u": {"direct_count": 1, "reverse_count": 1, "strength": 2,
              "measured_cycle": U_CYCLE},
    }
    if _problems_for([good]):
        found.append("the timing fixture is rejected")
    broken = dict(good, carrier_cycle=U_CYCLE - 1)
    if not _problems_for([broken]):
        found.append("a carrier before the U cycle is not rejected")
    missing = dict(good, carrier_cycle=None)
    if _problems_for([missing]):
        found.append("an absent carrier is treated as a timing failure")
    if not _problems_for([missing], require_all_carriers=True):
        found.append("the all-carrier variant accepts an absent carrier")
    no_u = dict(good, u={"direct_count": None, "reverse_count": None,
                         "strength": None, "measured_cycle": None})
    if not _problems_for([no_u]):
        found.append("the timing fixture accepts a missing U")
    return found


def render(doc: dict) -> str:
    lines = [
        "# A1 C5 target timing — fixed earlier U",
        "",
        "**ID:** `%s`" % doc["id"],
        "**Status:** `%s`" % doc["status"],
        "",
        "**This is not an A1 result.** It is a no-arm timing audit; no cell was run and no target was changed.",
        "",
        "## Decision",
        "",
        "C5's U is fixed at **cycle %d**, sampled after the cycle-%d observations are stored and before"
        % (doc["u_cycle"], doc["u_cycle"]),
        "the cycle-%d sleep call. The cycle-%d sample remains the target-selection diagnostic; it is not"
        % (doc["u_cycle"], doc["selection_u_cycle"]),
        "the C5 baseline. The four current targets are retained in every seed.",
        "",
        "| Check | Value |",
        "| --- | --- |",
        "| Current target observations | %d |" % doc["current_target_observations"],
        "| N=20 target observations | %d |" % doc["n20_target_observations"],
        "| Current targets with an observed carrier | %d |" % doc["current_observed_carriers"],
        "| Current targets without an observed carrier by cycle %d | %d |"
        % (doc["replay_cycles"], doc["current_missing_carriers"]),
        "| Current carriers before cycle %d | %d |" % (doc["u_cycle"], doc["current_carriers_before_u"]),
        "| Earliest observed carrier | cycle %s |" % doc["earliest_observed_carrier_cycle"],
        "| Earliest current carrier | cycle %s |" % doc["earliest_current_carrier_cycle"],
        "",
        "An absent carrier is not a C5 timing violation; carrier absence is left to the",
        "structural gates that require it. A carrier before cycle %d is a failure." % doc["u_cycle"],
        "",
        "## Per-seed audit",
        "",
        "| Seed | Current targets | Preserved | Observed carriers | Missing carriers |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in doc["per_seed"]:
        lines.append("| `%d` | %d | %d | %d | %d |" % (
            row["seed"], row["preserved_count"], len(row["preserved_rows"]),
            row["observed_carriers"], row["missing_carriers"]))
    lines += [
        "",
        "The full per-observation rows are in [`a1_c5_target_timing.json`](a1_c5_target_timing.json).",
        "Each row records the first carrier cycle, the cycle-%d U counts and whether U precedes the carrier."
        % doc["u_cycle"],
        "",
        "**Not evidence:** %s" % doc["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.a1_c5_target_timing --check",
        "python -m benchmarks.a1_c5_target_timing --self-test",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip("\n")


def write() -> int:
    doc = build()
    AUDIT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.write_text(render(doc) + "\n", encoding="utf-8")
    found = problems(doc)
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("wrote %s and %s" % (AUDIT_PATH, PAGE_PATH))
    return 0


def check() -> int:
    if not AUDIT_PATH.exists():
        print("FAIL: %s is missing" % AUDIT_PATH)
        return 1
    doc = _load(AUDIT_PATH)
    found = problems(doc)
    if PAGE_PATH.read_text(encoding="utf-8") != render(doc) + "\n":
        found.append("the page is stale")
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("A1 C5 target timing: clean; cycle-%d U, earliest carrier cycle %d, four current targets preserved"
          % (doc["u_cycle"], doc["earliest_observed_carrier_cycle"]))
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
        print("A1 C5 target timing: self-test clean")
        return 0
    if args.write:
        return write()
    return check() if args.check else check()


if __name__ == "__main__":
    raise SystemExit(main())
