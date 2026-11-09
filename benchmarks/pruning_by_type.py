"""Split the engine's pruning counter by candidate type, and end each edge's death properly.

`docs/PRUNING-REACHABILITY.md` showed that the attribution ledger cannot see a `pruned` edge
death: it judges an edge only on its first step below the stable threshold (0.30 x 0.8 = 0.24,
still above the 0.15 death threshold), so the branch is unreachable from any edge it follows.
That left the fourth category correctly labelled but still unmeasured, and the engine's counter
is a single total over every surviving candidate, so "2,374 prunings" said nothing about
prediction edges.

This harness closes both gaps without touching the engine:

* it observes `_store_single_candidate` and counts the retired records the engine writes, by the
  candidate's own `type` — the same write that increments the engine's `pruned` counter — and it
  reconciles the two on every cycle, so the split is the engine's behaviour and not a
  reimplementation of it;
* it follows every edge that made the peak to its terminal event: the candidate retired, still
  stable at the end of the horizon, or gone from the stable set and never retired.

The endpoint is therefore `pruned / (pruned + withdrawn)` over the peak edges, which is the share
this project could not state before: not "how many prunings happened", but "of the structures
that formed and then disappeared, how many were removed by pruning".

    ./.venv/bin/python -m benchmarks.pruning_by_type --measure [--limit N]
    ./.venv/bin/python -m benchmarks.pruning_by_type --aggregate
    ./.venv/bin/python -m benchmarks.pruning_by_type --check
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from benchmarks import decay_attribution as da
from benchmarks import engine_stamp

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PARTS = DOCS / "pruning_by_type" / "parts"
ARTIFACT = DOCS / "pruning_by_type.json"
DOC = DOCS / "PRUNING-BY-TYPE.md"

CYCLES = da.CYCLES
ARMS = da.ARMS
#: The terminal categories, in the order the page reports them.
TERMINAL = ("pruned", "withdrawn_without_pruning", "alive")


class PruningLedger(da.Ledger):
    """The attribution ledger plus a record of what the engine retires, by candidate type.

    The observation is a read of the record the engine is already writing: nothing is added to
    it, nothing is filtered out, and the record is passed to the engine's own writer unchanged.
    Every cycle the counts are reconciled against the engine's `pruned` return value, so a split
    that does not add up is a failed instrument rather than a finding.
    """

    def __init__(self, memory, decay_factor: float):
        super().__init__(memory, decay_factor)
        self.cycle = 0
        self.retired_by_type: Counter = Counter()
        self.retired_edges: set = set()
        self.retired_at: dict = {}
        self.retired_this_cycle = 0
        self.mismatches: list = []

    def begin_cycle(self) -> None:
        super().begin_cycle()
        self.retired_this_cycle = 0

    def _store_single_candidate(self, candidate: dict):
        if candidate.get("retired"):
            ctype = candidate.get("type") or "unknown"
            self.retired_by_type[ctype] += 1
            self.retired_this_cycle += 1
            if ctype == "prediction_candidate":
                edge = (candidate.get("source"), candidate.get("target"))
                self.retired_edges.add(edge)
                self.retired_at.setdefault(edge, self.cycle + 1)
        return super()._store_single_candidate(candidate)


def cell(arm: str, seed: int, cycles: int = CYCLES) -> dict:
    """One arm on one seed: the peak edges followed to their terminal events."""
    events = da.lattice_world(da.DEGREE)
    world = da.world_edges(events)
    factor = 0.95 if arm == "engine" else 1.0
    db = da.temp_db("prunebytype_%s_%s.db" % (arm, seed))
    db.unlink(missing_ok=True)
    memory = da.LedgerMemory(db_path=str(db))
    service = PruningLedger(memory, factor)
    if hasattr(service, "_rng"):
        service._rng.seed(seed)
    for text in events[:12]:
        memory.store(text, event_type="event", source="seed:bootstrap")

    stable_series: list[set] = []
    per_cycle: list[dict] = []
    try:
        for cycle in range(cycles):
            da._feed(memory, events, cycle)
            service.begin_cycle()
            service.cycle = cycle
            memory.decay_calls = []
            service.run_sleep_cycle()
            now = da.stored(service)
            stable = {edge for edge, value in now.items()
                      if value >= service.STABLE_THRESHOLD}
            stable_series.append(stable)
            engine_pruned = int(service.selection[2])
            if engine_pruned != service.retired_this_cycle:
                service.mismatches.append({
                    "cycle": cycle + 1,
                    "engine_pruned": engine_pruned,
                    "observed_retired": service.retired_this_cycle,
                })
            per_cycle.append({
                "cycle": cycle + 1,
                "stable": len(stable),
                "engine_pruned": engine_pruned,
                "observed_retired": service.retired_this_cycle,
            })
    finally:
        memory.close()
        db.unlink(missing_ok=True)

    peak = max((len(s) for s in stable_series), default=0)
    peak_index = next((i for i, s in enumerate(stable_series) if len(s) == peak), None)
    peak_edges = sorted(stable_series[peak_index]) if peak_index is not None else []
    final = stable_series[-1] if stable_series else set()
    terminal = {category: [] for category in TERMINAL}
    for edge in peak_edges:
        key = "%s|%s" % edge
        if edge in service.retired_edges:
            terminal["pruned"].append(key)
        elif edge in final:
            terminal["alive"].append(key)
        else:
            terminal["withdrawn_without_pruning"].append(key)

    return {
        "arm": arm,
        "seed": seed,
        "cycles": cycles,
        "degree": da.DEGREE,
        "peak_edges": len(peak_edges),
        "peak_cycle": (peak_index + 1) if peak_index is not None else None,
        "terminal": terminal,
        "retired_by_type": dict(sorted(service.retired_by_type.items())),
        "retired_prediction_edges": len(service.retired_edges),
        "reconciliation_mismatches": service.mismatches,
        "per_cycle": per_cycle,
    }


def _path(arm: str, seed: int) -> Path:
    return PARTS / ("cell_%s_s%d.json" % (arm, seed))


def run(limit: int | None = None) -> int:
    PARTS.mkdir(parents=True, exist_ok=True)
    spent = 0
    for arm in ARMS:
        for seed in da.attribution_seeds():
            path = _path(arm, seed)
            if path.exists():
                print("cached", path.name)
                continue
            if limit is not None and spent >= limit:
                print("limit reached; run again to continue")
                return 0
            row = cell(arm, seed)
            path.write_text(json.dumps(engine_stamp.stamp(row), indent=2) + "\n",
                            encoding="utf-8")
            spent += 1
            print("measured", path.name, "peak", row["peak_edges"],
                  "pruned", len(row["terminal"]["pruned"]),
                  "mismatches", len(row["reconciliation_mismatches"]))
    return 0


def aggregate() -> dict:
    cells = [json.loads(p.read_text(encoding="utf-8"))
             for p in sorted(PARTS.glob("cell_*.json"))]
    arms = {}
    for arm in ARMS:
        mine = [c for c in cells if c["arm"] == arm]
        by_type: Counter = Counter()
        terminal: Counter = Counter({category: 0 for category in TERMINAL})
        mismatches = 0
        for c in mine:
            by_type.update(c["retired_by_type"])
            for category in TERMINAL:
                terminal[category] += len(c["terminal"][category])
            mismatches += len(c["reconciliation_mismatches"])
        deaths = terminal["pruned"] + terminal["withdrawn_without_pruning"]
        arms[arm] = {
            "seeds": [c["seed"] for c in mine],
            "cycles": mine[0]["cycles"] if mine else None,
            "peak_edges": sum(c["peak_edges"] for c in mine),
            "terminal": dict(terminal),
            "deaths": deaths,
            "pruned_share_of_deaths": (round(terminal["pruned"] / deaths, 4)
                                       if deaths else None),
            "retired_by_type": dict(sorted(by_type.items())),
            "reconciliation_mismatches": mismatches,
            "per_seed": [
                {"seed": c["seed"], "peak_edges": c["peak_edges"],
                 "pruned": len(c["terminal"]["pruned"]),
                 "withdrawn_without_pruning": len(c["terminal"]["withdrawn_without_pruning"]),
                 "alive": len(c["terminal"]["alive"]),
                 "retired_prediction_edges": c["retired_prediction_edges"]}
                for c in mine
            ],
        }
    engine = arms["engine"]
    gates = {
        "G1_the_observer_reconciles_with_the_engine": (
            engine["reconciliation_mismatches"] == 0 and len(cells) > 0),
        "G2_prediction_candidates_are_among_the_retired_types": (
            engine["retired_by_type"].get("prediction_candidate", 0) > 0),
        "G3_the_denominator_exists": engine["deaths"] > 0,
        "G4_every_peak_edge_has_a_terminal_category": (
            engine["deaths"] + engine["terminal"]["alive"] == engine["peak_edges"]),
    }
    share = engine["pruned_share_of_deaths"]
    if share is None:
        label = "NO_DENOMINATOR"
    elif share >= 0.99:
        label = "PRUNING_IS_TERMINAL"
    elif share > 0:
        label = "PRUNING_PARTIAL"
    else:
        label = "PRUNING_ABSENT"
    return {
        "kind": "pruning_by_type",
        "date": "2026-11-09",
        "arms": arms,
        "gates": gates,
        "label": label if all(gates.values()) else "INSTRUMENT_INVALID",
    }


def _fmt(value) -> str:
    return "n/a" if value is None else "%s" % value


def render(artifact: dict) -> str:
    engine = artifact["arms"]["engine"]
    control = artifact["arms"]["no_temporal_decay"]
    lines = [
        "# What pruning removes, by candidate type — measurement",
        "",
        "Generated from `docs/pruning_by_type.json` by",
        "`python -m benchmarks.pruning_by_type --aggregate`. Do not edit by hand.",
        "",
        "## Label",
        "",
        "**%s**" % artifact["label"],
        "",
        "## The terminal event of every peak edge",
        "",
        "Each edge that made the peak is followed to the end of the horizon and placed in exactly",
        "one category. `pruned` means the engine wrote a retirement record for its candidate;",
        "`withdrawn_without_pruning` means the edge left the stable set and no retirement record",
        "was written; `alive` means it was still stable at the last cycle and is not a death.",
        "",
        "| Category | Engine arm | No-decay control |",
        "| --- | --- | --- |",
        "| Peak edges | %s | %s |" % (_fmt(engine["peak_edges"]), _fmt(control["peak_edges"])),
        "| Pruned | %s | %s |" % (_fmt(engine["terminal"].get("pruned", 0)),
                                  _fmt(control["terminal"].get("pruned", 0))),
        "| Withdrawn, never pruned | %s | %s |"
        % (_fmt(engine["terminal"].get("withdrawn_without_pruning", 0)),
           _fmt(control["terminal"].get("withdrawn_without_pruning", 0))),
        "| Alive at the end | %s | %s |" % (_fmt(engine["terminal"].get("alive", 0)),
                                           _fmt(control["terminal"].get("alive", 0))),
        "| Deaths | %s | %s |" % (_fmt(engine["deaths"]), _fmt(control["deaths"])),
        "| Pruned share of deaths | %s | %s |"
        % (_fmt(engine["pruned_share_of_deaths"]), _fmt(control["pruned_share_of_deaths"])),
        "",
        "## What the engine retired, by type",
        "",
        "The observer counts the record the engine writes, so this is the same population its own",
        "counter totals. The reconciliation column is what makes the split attributable: the",
        "observed retirements must equal the engine's `pruned` return value on every cycle.",
        "",
        "| Candidate type | Engine arm | No-decay control |",
        "| --- | --- | --- |",
    ]
    types = sorted(set(engine["retired_by_type"]) | set(control["retired_by_type"]))
    for ctype in types:
        lines.append("| `%s` | %s | %s |" % (
            ctype, _fmt(engine["retired_by_type"].get(ctype, 0)),
            _fmt(control["retired_by_type"].get(ctype, 0))))
    lines += [
        "",
        "| Quantity | Engine arm | No-decay control |",
        "| --- | --- | --- |",
        "| Seeds | %d | %d |" % (len(engine["seeds"]), len(control["seeds"])),
        "| Cycles per seed | %s | %s |" % (_fmt(engine["cycles"]), _fmt(control["cycles"])),
        "| Reconciliation mismatches | %s | %s |"
        % (_fmt(engine["reconciliation_mismatches"]),
           _fmt(control["reconciliation_mismatches"])),
        "",
        "## Per seed, engine arm",
        "",
        "| Seed | Peak edges | Pruned | Withdrawn | Alive |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in engine["per_seed"]:
        lines.append("| %d | %d | %d | %d | %d |" % (
            row["seed"], row["peak_edges"], row["pruned"],
            row["withdrawn_without_pruning"], row["alive"]))
    lines += [
        "",
        "## What this changes",
        "",
        "- **The fourth category is now measured for edges, not only for candidates.** The share",
        "  above is pruning's part in the deaths of the structures that formed, which the",
        "  attribution ledger's window could not express.",
        "- **`decayed` and `pruned` are two stages of one process.** An edge crossing 0.30 is",
        "  labelled `decayed` by the attribution ledger; the candidate behind it is retired when",
        "  it reaches 0.15, and this record counts that retirement as the terminal event.",
        "- **The engine's total counter is now split.** A total of prunings across every surviving",
        "  generation said nothing about edges; the type table says how much of it they are.",
        "",
        "## What this does not establish",
        "",
        "- **One world, one degree, three seeds.** It measures this collapse, as the attribution",
        "  record does, and inherits its scope.",
        "- **Retirement is not deletion.** The engine stores a retired record so the candidate",
        "  cannot resurrect; whether the row is later removed from the substrate is a different",
        "  question.",
        "- **A withdrawn edge was not pruned inside the horizon.** It says nothing about whether it",
        "  would have been pruned later.",
        "",
    ]
    return "\n".join(lines)


def check(artifact: dict | None = None) -> list:
    if not ARTIFACT.exists():
        return ["%s does not exist" % ARTIFACT.name]
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    reference = artifact or stored
    fresh = aggregate()
    problems = []
    for key in ("arms", "gates", "label"):
        if reference.get(key) != fresh.get(key):
            problems.append("%s disagrees with a fresh aggregation" % key)
    failing = [name for name, ok in fresh["gates"].items() if not ok]
    if failing:
        problems.append("gates fail: %s" % ", ".join(sorted(failing)))
    if not DOC.exists():
        problems.append("%s does not exist" % DOC.name)
    elif DOC.read_text(encoding="utf-8") != render(stored):
        problems.append("%s is stale" % DOC.name)
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measure", action="store_true", help="run the cells that are not cached")
    parser.add_argument("--limit", type=int, default=None, help="measure at most N new cells")
    parser.add_argument("--aggregate", action="store_true", help="write the artifact and the page")
    parser.add_argument("--check", action="store_true", help="validate without writing")
    args = parser.parse_args(argv)

    if args.check:
        problems = check()
        for problem in problems:
            print("FAIL:", problem)
        if problems:
            return 1
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        print("pruning by type: %s, engine share %s of %d deaths"
              % (artifact["label"],
                 _fmt(artifact["arms"]["engine"]["pruned_share_of_deaths"]),
                 artifact["arms"]["engine"]["deaths"]))
        return 0

    if args.measure:
        code = run(limit=args.limit)
        if code:
            return code
        missing = [_path(arm, seed) for arm in ARMS for seed in da.attribution_seeds()
                   if not _path(arm, seed).exists()]
        if missing:
            print("%d cell(s) still unmeasured; the artifact is not written until all are"
                  % len(missing))
            return 0
        artifact = engine_stamp.stamp(aggregate())
        ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
        DOC.write_text(render(artifact), encoding="utf-8")
        print("pruning by type: %s -> %s" % (artifact["label"], ARTIFACT.name))
        return 0

    if args.aggregate:
        existing = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.exists() else {}
        artifact = dict(engine_stamp.stamp(aggregate()))
        for key in engine_stamp.STAMPED:
            if existing.get(key):
                artifact[key] = existing[key]
        ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
        DOC.write_text(render(artifact), encoding="utf-8")
        print("aggregated -> %s" % ARTIFACT.name)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
