"""POST-HOC SCHEMA-PRIORITY-GATE-1.

A diagnostic on the cached schema-prime ranking features.  The shipped
prediction sort gives every schema-congruent transition a lexicographic
priority: schema first, then target entropy, transition probability, count and
edge.  This block asks what happens when that priority is gated on substantive
support:

    gate_open = schema and temporal_count >= 2 * PREDICTION_MIN_COUNT

The engine's admission floor is 5, so the gate is 10.  A schema edge below the
gate is not removed; it simply loses the priority and is ranked on the same
terms as every other transition.  No engine cell runs and no fresh seed is
spent.

    python -m benchmarks.schema_priority_gate --write
    python -m benchmarks.schema_priority_gate --check
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import engine_stamp                                      # noqa: E402

ID = "POST-HOC-SCHEMA-PRIORITY-GATE-1"
SEEDS = [20611601, 20611602, 20611603, 20611604, 20611605, 20611606]
CACHE = ROOT / ".scratch" / "rank_sort_probe"
ARTIFACT = ROOT / "docs" / "schema_priority_gate.json"
PAGE = ROOT / "docs" / "SCHEMA-PRIORITY-GATE.md"
TOP_N = 20
ADMISSION_FLOOR = 5
WEAK_BELOW = 10
GATE = 10
THRESHOLDS = (5, 8, 10, 12, 15, 20, 999)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _feature_path(seed: int) -> Path:
    return CACHE / ("%d_features.json" % seed)


def _load_cycles() -> dict[tuple[int, int], list[dict]]:
    missing = [seed for seed in SEEDS if not _feature_path(seed).exists()]
    if missing:
        raise SystemExit("missing ranking feature caches: %r" % missing)
    cycles = {}
    for seed in SEEDS:
        body = _load(_feature_path(seed))
        if body.get("seed") != seed:
            raise SystemExit("REFUSED: seed mismatch in %s" % _feature_path(seed))
        rows = body.get("cycles") or []
        if len(rows) != 120:
            raise SystemExit("REFUSED: seed %d has %d cycles" % (seed, len(rows)))
        for index, cycle in enumerate(rows):
            cycles[(seed, index)] = cycle
    return cycles


def _key(row: dict, priority: bool):
    return (
        0 if priority else 1,
        float(row["entropy"]),
        -float(row["prob"]),
        -int(row["count"]),
        tuple(row["edge"]),
    )


def _top(rows: list[dict], mode: str, gate: int = GATE) -> list[dict]:
    if mode == "no_priority":
        key = lambda row: _key(row, False)
    elif mode == "ungated":
        key = lambda row: _key(row, bool(row["schema"]))
    elif mode == "gated":
        key = lambda row: _key(
            row, bool(row["schema"]) and int(row["count"]) >= gate)
    else:
        raise ValueError(mode)
    return sorted(rows, key=key)[:TOP_N]


def _share(value: int, total: int) -> float:
    return value / float(total) if total else float("nan")


def _policy(cycles: dict[tuple[int, int], list[dict]],
            base: dict[tuple[int, int], set[tuple[str, str]]],
            mode: str, gate: int = GATE) -> dict:
    top = {key: _top(rows, mode, gate) for key, rows in cycles.items()}
    seats = sum(len(rows) for rows in top.values())
    schema_seats = 0
    priority = weak_priority = strong_priority = 0
    weak_top20 = 0
    non_schema = 0
    mean_counts = []
    mean_probs = []
    schema_per_cycle = []
    for key, rows in top.items():
        base_edges = base[key]
        schema_per_cycle.append(sum(1 for row in rows if row["schema"]))
        if rows:
            mean_counts.append(statistics.fmean(float(row["count"]) for row in rows))
            mean_probs.append(statistics.fmean(float(row["prob"]) for row in rows))
        for row in rows:
            edge = tuple(row["edge"])
            if row["schema"]:
                schema_seats += 1
                promoted = edge not in base_edges
                if int(row["count"]) < WEAK_BELOW:
                    weak_top20 += 1
                    if promoted:
                        weak_priority += 1
                elif promoted:
                    strong_priority += 1
                if promoted:
                    priority += 1
            else:
                non_schema += 1
    return {
        "mode": mode,
        "gate": gate,
        "top": top,
        "seats": seats,
        "schema_seats": schema_seats,
        "schema_share": _share(schema_seats, seats),
        "priority_seats": priority,
        "weak_priority_seats": weak_priority,
        "strong_priority_seats": strong_priority,
        "weak_schema_seats": weak_top20,
        "non_schema_seats": non_schema,
        "mean_top20_count": statistics.fmean(mean_counts),
        "mean_top20_prob": statistics.fmean(mean_probs),
        "schema_seats_per_cycle_median": statistics.median(schema_per_cycle),
    }


def _edges_by_cycle(policy: dict) -> dict[tuple[int, int], tuple]:
    return {key: tuple(tuple(row["edge"]) for row in rows)
            for key, rows in policy["top"].items()}


def _diff_edges(left: dict, right: dict) -> int:
    return sum(len(set(a) ^ set(b)) for a, b in zip(left.values(), right.values()))


def _changed_cycles(left: dict, right: dict) -> int:
    return sum(1 for a, b in zip(left.values(), right.values()) if set(a) != set(b))


def build() -> dict:
    cycles = _load_cycles()
    raw_rows = [row for rows in cycles.values() for row in rows]
    schema_rows = [row for row in raw_rows if row["schema"]]
    if not schema_rows:
        raise SystemExit("REFUSED: no schema rows")
    base = {key: {tuple(row["edge"]) for row in _top(rows, "no_priority")}
            for key, rows in cycles.items()}

    no_priority = _policy(cycles, base, "no_priority")
    ungated = _policy(cycles, base, "ungated")
    gated = _policy(cycles, base, "gated")
    no_edges = _edges_by_cycle(no_priority)
    ungated_edges = _edges_by_cycle(ungated)
    gated_edges = _edges_by_cycle(gated)

    weak_remaining_on_merit = 0
    weak_remaining_priority = 0
    for key, rows in gated["top"].items():
        for row in rows:
            if row["schema"] and int(row["count"]) < WEAK_BELOW:
                if tuple(row["edge"]) not in base[key]:
                    weak_remaining_priority += 1
                else:
                    weak_remaining_on_merit += 1

    strong_lost = 0
    for key, rows in ungated["top"].items():
        gated_keys = {tuple(row["edge"]) for row in gated["top"][key]}
        strong_lost += sum(
            1 for row in rows
            if row["schema"] and int(row["count"]) >= WEAK_BELOW
            and tuple(row["edge"]) not in gated_keys)

    threshold_rows = []
    for gate in THRESHOLDS:
        policy = _policy(cycles, base, "gated", gate)
        threshold_rows.append({
            "gate": gate,
            "schema_seats": policy["schema_seats"],
            "schema_share": policy["schema_share"],
            "priority_seats": policy["priority_seats"],
            "weak_priority_seats": policy["weak_priority_seats"],
            "weak_schema_seats": policy["weak_schema_seats"],
            "strong_priority_seats": policy["strong_priority_seats"],
        })

    per_seed = []
    for seed in SEEDS:
        seed_cycles = {key: rows for key, rows in cycles.items() if key[0] == seed}
        seed_base = {key: base[key] for key in seed_cycles}
        seed_ungated = _policy(seed_cycles, seed_base, "ungated")
        seed_gated = _policy(seed_cycles, seed_base, "gated")
        per_seed.append({
            "seed": seed,
            "cycles": len(seed_cycles),
            "schema_rows": sum(1 for rows in seed_cycles.values()
                               for row in rows if row["schema"]),
            "ungated_schema_seats": seed_ungated["schema_seats"],
            "ungated_priority_seats": seed_ungated["priority_seats"],
            "gated_schema_seats": seed_gated["schema_seats"],
            "gated_priority_seats": seed_gated["priority_seats"],
        })

    checks = {
        "all_cycles_present": len(cycles) == 120 * len(SEEDS),
        "all_schema_rows_in_ungated_top20": ungated["schema_seats"] == len(schema_rows),
        "gate_at_floor_reproduces_ungated": _edges_by_cycle(
            _policy(cycles, base, "gated", ADMISSION_FLOOR)) == ungated_edges,
        "gate_disabled_reproduces_no_priority": _edges_by_cycle(
            _policy(cycles, base, "gated", 999)) == no_edges,
        "gated_has_no_weak_priority": gated["weak_priority_seats"] == 0,
        "gate_removes_weak_priority": ungated["weak_priority_seats"] > 0,
        "all_strong_priority_retained": strong_lost == 0,
        "remaining_weak_on_merit_only": weak_remaining_on_merit
                                        == gated["weak_schema_seats"]
                                        and weak_remaining_priority == 0,
    }
    if not all(checks.values()):
        raise SystemExit("REFUSED: checks " +
                         ", ".join(key for key, value in checks.items() if not value))

    summary = {
        "cycles": len(cycles),
        "nonempty_cycles": sum(1 for rows in cycles.values() if rows),
        "empty_cycles": sum(1 for rows in cycles.values() if not rows),
        "ranked_rows": len(raw_rows),
        "schema_rows": len(schema_rows),
        "top20_seats": no_priority["seats"],
        "no_priority": {key: value for key, value in no_priority.items()
                        if key != "top"},
        "ungated": {key: value for key, value in ungated.items()
                    if key != "top"},
        "gated": {key: value for key, value in gated.items()
                  if key != "top"},
        "gate_effect": {
            "gate": GATE,
            "weak_priority_removed": (ungated["weak_priority_seats"]
                                      - gated["weak_priority_seats"]),
            "weak_schema_seats_removed": (ungated["weak_schema_seats"]
                                          - gated["weak_schema_seats"]),
            "weak_schema_seats_remaining": gated["weak_schema_seats"],
            "weak_remaining_on_merit": weak_remaining_on_merit,
            "non_schema_seats_returned": (gated["non_schema_seats"]
                                          - ungated["non_schema_seats"]),
            "strong_schema_seats_lost": strong_lost,
            "strong_priority_seats_retained": gated["strong_priority_seats"],
            "seats_changed": _diff_edges(ungated_edges, gated_edges),
            "cycles_changed": _changed_cycles(ungated_edges, gated_edges),
            "mean_count_change": (gated["mean_top20_count"]
                                  - ungated["mean_top20_count"]),
            "mean_prob_change": (gated["mean_top20_prob"]
                                 - ungated["mean_top20_prob"]),
        },
        "threshold_sweep": threshold_rows,
        "per_seed": per_seed,
        "checks": checks,
        "verdict": ("GATE REMOVES WEAK PRIORITY, RETAINS ALL STRONG SCHEMA SEATS"
                    if gated["weak_priority_seats"] == 0 and strong_lost == 0
                    else "GATE FAILS"),
    }
    return engine_stamp.stamp({
        "kind": "schema_priority_gate",
        "status": "POST-HOC DIAGNOSTIC",
        "prereg": None,
        "posthoc": True,
        "engine": "no engine run; cached ranking features only",
        "question": (
            "If schema priority requires temporal count at least twice the "
            "admission floor, how many weak schema edges stop taking top-20 "
            "priority seats, and how many strong schema seats are lost?"
        ),
        "scope": (
            "Six consumed schema-prime seeds, 120 cycles each, cached ranking "
            "features. Top 20 by the engine's transition sort. No fresh seed."
        ),
        "design": {
            "seeds": SEEDS,
            "top_n": TOP_N,
            "gate": GATE,
            "admission_floor": ADMISSION_FLOOR,
            "gate_rule": "schema priority only when temporal_count >= 10",
            "weak_definition": "schema row with temporal_count < 10",
            "ordering": (
                "priority flag, then target entropy ascending, transition "
                "probability descending, temporal count descending, source, target"
            ),
            "priority_seat": (
                "a schema row in the policy top 20 whose edge is not in the "
                "same cycle's no-priority top 20"
            ),
        },
        "cache": CACHE.relative_to(ROOT).as_posix(),
        "summary": summary,
        "not_evidence": (
            "A post-hoc diagnostic on six already-consumed seeds and cached "
            "candidate rankings. It measures top-20 ordering, not served or "
            "asserted behavior, and it does not establish that gated priority "
            "improves downstream prediction, transfer or capability."
        ),
    })


def _fmt(value, digits=3):
    return "NA" if value is None else ("%.*f" % (digits, value))


def render(art: dict) -> str:
    s = art["summary"]
    np = s["no_priority"]
    ug = s["ungated"]
    ga = s["gated"]
    e = s["gate_effect"]
    lines = [
        "# Gated schema priority — post hoc diagnostic",
        "",
        "Generated from `%s` by `python -m benchmarks.schema_priority_gate --write`. "
        "Do not edit by hand." % ARTIFACT.relative_to(ROOT).as_posix(),
        "",
        "**Verdict: `%s`.** This is a diagnostic, not a confirmatory result and "
        "not evidence that gated priority improves downstream behavior."
        % s["verdict"],
        "",
        "## Design",
        "",
        "- Six consumed seeds (`%s`), 120 cycles each, **%d** ranked rows."
        % (", ".join(str(seed) for seed in art["design"]["seeds"]), s["ranked_rows"]),
        "- **%d** nonempty cycles and **%d** top-20 seats; %d cycles have no "
        "candidates." % (s["nonempty_cycles"], s["top20_seats"], s["empty_cycles"]),
        "- **%d** schema rows." % s["schema_rows"],
        "- The gate is **temporal count >= %d**, twice the engine's admission "
        "floor of %d." % (art["design"]["gate"], art["design"]["admission_floor"]),
        "- A gated-out schema row is **not removed**. It loses the priority flag "
        "and ranks on target entropy, transition probability, count and edge "
        "like every other transition.",
        "- A **priority seat** is a schema edge in the policy top 20 that is not "
        "in the same cycle's no-priority top 20.",
        "",
        "## Top-20 composition",
        "",
        "| Policy | Schema seats | Share of seats | Priority seats | Weak priority | "
        "Weak schema in top 20 | Strong priority |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        "| No schema priority | %d | %.2f%% | 0 | 0 | %d | 0 |"
        % (np["schema_seats"], 100 * np["schema_share"], np["weak_schema_seats"]),
        "| Ungated schema priority | %d | %.2f%% | %d | %d | %d | %d |"
        % (ug["schema_seats"], 100 * ug["schema_share"], ug["priority_seats"],
           ug["weak_priority_seats"], ug["weak_schema_seats"],
           ug["strong_priority_seats"]),
        "| Gated at count >= %d | %d | %.2f%% | %d | %d | %d | %d |"
        % (art["design"]["gate"], ga["schema_seats"], 100 * ga["schema_share"],
           ga["priority_seats"], ga["weak_priority_seats"],
           ga["weak_schema_seats"], ga["strong_priority_seats"]),
        "",
        "Every ungated schema row is in the top 20: **%d** schema rows and **%d** "
        "schema seats." % (s["schema_rows"], ug["schema_seats"]),
        "",
        "## What the gate changes",
        "",
        "- **%d weak priority seats** are removed; every weak schema edge with "
        "count below %d loses the priority flag." % (e["weak_priority_removed"],
                                                     art["design"]["gate"]),
        "- **%d strong priority seats** are retained and **%d** strong schema "
        "seats are lost." % (e["strong_priority_seats_retained"],
                            e["strong_schema_seats_lost"]),
        "- **%d** weak schema seats leave the top 20; **%d** remain because they "
        "were already in the no-priority top 20 on their own ordering. Of the "
        "%d that leave, **%d** were priority seats and **%d** were ordinary seats "
        "displaced when strong schema edges moved up."
        % (e["weak_schema_seats_removed"], e["weak_schema_seats_remaining"],
           e["weak_schema_seats_removed"], e["weak_priority_removed"],
           e["weak_schema_seats_removed"] - e["weak_priority_removed"]),
        "- **%d** non-schema seats are returned." % e["non_schema_seats_returned"],
        "- **%d** seats change across **%d** cycles."
        % (e["seats_changed"], e["cycles_changed"]),
        "- Mean top-20 count changes by **%+.2f** and mean probability by "
        "**%+.4f**." % (e["mean_count_change"], e["mean_prob_change"]),
        "",
        "## Threshold sweep",
        "",
        "The gate at 5 reproduces ungated priority; the gate at 999 disables "
        "priority. Both controls reproduce their target top-20 lists exactly.",
        "",
        "| Gate count | Schema seats | Share | Priority seats | Weak priority | "
        "Weak schema in top 20 | Strong priority |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in s["threshold_sweep"]:
        lines.append("| %d | %d | %.2f%% | %d | %d | %d | %d |"
                     % (row["gate"], row["schema_seats"], 100 * row["schema_share"],
                        row["priority_seats"], row["weak_priority_seats"],
                        row["weak_schema_seats"], row["strong_priority_seats"]))
    lines += [
        "",
        "## Per seed",
        "",
        "| Seed | Schema rows | Ungated schema seats | Ungated priority | "
        "Gated schema seats | Gated priority |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in s["per_seed"]:
        lines.append("| %d | %d | %d | %d | %d | %d |"
                     % (row["seed"], row["schema_rows"],
                        row["ungated_schema_seats"], row["ungated_priority_seats"],
                        row["gated_schema_seats"], row["gated_priority_seats"]))
    lines += [
        "",
        "## Checks",
        "",
        "| Check | Passes |",
        "| --- | --- |",
    ]
    for name, passed in s["checks"].items():
        lines.append("| `%s` | %s |" % (name, "yes" if passed else "no"))
    lines += [
        "",
        "## What this does and does not establish",
        "",
        "The gate is a ranking rule: it decides whether a schema edge may jump "
        "the queue, not whether the edge is admissible. Weak schema edges can "
        "still reach the top 20 on their own entropy and probability, and all "
        "147 that do here were already there without schema priority.",
        "",
        "The result is about candidate ordering only. It does not measure served "
        "predictions, asserted edges, downstream acquisition, transfer or "
        "capability, and the six seeds are reused. No engine file changed.",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(art: dict | None = None) -> list[str]:
    art = _load(ARTIFACT) if art is None else art
    found: list[str] = []
    if art.get("kind") != "schema_priority_gate":
        found.append("artifact kind")
    if art.get("status") != "POST-HOC DIAGNOSTIC" or not art.get("posthoc"):
        found.append("diagnostic status")
    if art.get("prereg") is not None:
        found.append("prereg present")
    if engine_stamp.missing(art):
        found.append("stamp: %r" % (engine_stamp.missing(art),))
    s = art.get("summary") or {}
    if s.get("schema_rows") != 1816:
        found.append("schema rows")
    if s.get("top20_seats") != 13604:
        found.append("seat count")
    if s.get("ungated", {}).get("schema_seats") != s.get("schema_rows"):
        found.append("ungated schema seats")
    if s.get("gated", {}).get("weak_priority_seats") != 0:
        found.append("weak priority under gate")
    if s.get("gate_effect", {}).get("strong_schema_seats_lost") != 0:
        found.append("strong seats lost")
    if not all((s.get("checks") or {}).values()):
        found.append("checks")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("page stale")
    return found


def write() -> int:
    art = build()
    ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(art), encoding="utf-8")
    e = art["summary"]["gate_effect"]
    print("schema priority gate: %s %s"
          % (art["summary"]["verdict"], json.dumps({
              "schema_rows": art["summary"]["schema_rows"],
              "ungated_schema_seats": art["summary"]["ungated"]["schema_seats"],
              "gated_schema_seats": art["summary"]["gated"]["schema_seats"],
              "weak_priority_removed": e["weak_priority_removed"],
              "strong_lost": e["strong_schema_seats_lost"],
              "non_schema_returned": e["non_schema_seats_returned"],
          })))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no artifact; run --write")
    art = _load(ARTIFACT)
    found = problems(art)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("schema priority gate: %s %s"
          % (art["summary"]["verdict"], json.dumps({
              "gated_schema_seats": art["summary"]["gated"]["schema_seats"],
              "weak_priority": art["summary"]["gated"]["weak_priority_seats"],
              "strong_lost": art["summary"]["gate_effect"][
                  "strong_schema_seats_lost"],
          })))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
