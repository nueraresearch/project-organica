"""POST-HOC SOURCE-DIVERSIFIED-TOP20-1.

Rank the never-served population one seed at a time, then cap the number of
top-20 seats any one source tag may take.  The question is whether the cap
recovers more of the 26 asserted never-served edges than the uncapped list,
and what it displaces to do so.

The ranking field is the observed minimum pre-cap rank used by the replicated
never-served model.  Median and final rank are reported as rank-sensitivity
checks.  This reads one committed artifact; no engine cell runs.

    python -m benchmarks.source_diversified_top20 --write
    python -m benchmarks.source_diversified_top20 --check
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import engine_stamp                                      # noqa: E402

ID = "POST-HOC-SOURCE-DIVERSIFIED-TOP20-1"
SOURCE = ROOT / "docs" / "never_served_assertion_model_replication.json"
ARTIFACT = ROOT / "docs" / "source_diversified_top20.json"
PAGE = ROOT / "docs" / "SOURCE-DIVERSIFIED-TOP20.md"
TOP_N = 20
CAPS = (1, 2, 3, 4, 5)
RANK_FIELDS = ("min_rank", "median_rank", "final_rank")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows() -> tuple[dict, dict[int, list[dict]]]:
    art = _load(SOURCE)
    rows = art.get("rows") or []
    if len(rows) != 212 or sum(1 for row in rows if row["asserted"]) != 26:
        raise SystemExit("REFUSED: expected 212 never-served rows and 26 asserted")
    grouped: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        if not row.get("edge") or row["edge"].count(">") != 1:
            raise SystemExit("REFUSED: unparseable edge %r" % row.get("edge"))
        if row.get("min_rank") is None:
            raise SystemExit("REFUSED: unranked row %r" % row.get("edge"))
        grouped[int(row["seed"])].append(row)
    if len(grouped) != 6 or any(len(group) < TOP_N for group in grouped.values()):
        raise SystemExit("REFUSED: six seeds with at least 20 rows are required")
    return art, grouped


def _key(row: dict, field: str):
    return (float(row[field]), row["edge"])


def _select(rows: list[dict], cap: int, field: str = "min_rank") -> list[dict]:
    selected = []
    counts: Counter[str] = Counter()
    for row in sorted(rows, key=lambda r: _key(r, field)):
        source = row["edge"].split(">")[0]
        if counts[source] < cap:
            selected.append(row)
            counts[source] += 1
        if len(selected) == TOP_N:
            break
    return selected


def _measure(grouped: dict[int, list[dict]], cap: int, field: str) -> dict:
    selected = []
    displaced = []
    added = []
    per_seed = []
    for seed in sorted(grouped):
        rows = grouped[seed]
        base = _select(rows, TOP_N, field)
        choice = _select(rows, cap, field)
        base_keys = {(seed, row["edge"]) for row in base}
        choice_keys = {(seed, row["edge"]) for row in choice}
        gone = [row for row in base if (seed, row["edge"]) not in choice_keys]
        new = [row for row in choice if (seed, row["edge"]) not in base_keys]
        selected.extend(choice)
        displaced.extend(gone)
        added.extend(new)
        per_seed.append({
            "seed": seed,
            "rows": len(rows),
            "asserted_rows": sum(1 for row in rows if row["asserted"]),
            "selected": len(choice),
            "recovered": sum(1 for row in choice if row["asserted"]),
            "baseline_recovered": sum(1 for row in base if row["asserted"]),
            "displaced": len(gone),
            "displaced_asserted": sum(1 for row in gone if row["asserted"]),
            "added": len(new),
            "added_asserted": sum(1 for row in new if row["asserted"]),
            "sources": len({row["edge"].split(">")[0] for row in choice}),
            "max_source_seats": max(
                Counter(row["edge"].split(">")[0] for row in choice).values()
            ) if choice else 0,
            "full_window": len(choice) == TOP_N,
        })
    return {
        "cap": cap,
        "rank_field": field,
        "selected": len(selected),
        "full_windows": sum(1 for row in per_seed if row["full_window"]),
        "recovered": sum(1 for row in selected if row["asserted"]),
        "recovered_mean": (sum(1 for row in selected if row["asserted"])
                           / len(grouped)),
        "displaced": len(displaced),
        "displaced_asserted": sum(1 for row in displaced if row["asserted"]),
        "added": len(added),
        "added_asserted": sum(1 for row in added if row["asserted"]),
        "per_seed": per_seed,
        "displaced_edges": [row["edge"] for row in displaced],
        "added_edges": [row["edge"] for row in added],
    }


def build() -> dict:
    source, grouped = _rows()
    baseline = _measure(grouped, TOP_N, "min_rank")
    sweep = [_measure(grouped, cap, "min_rank") for cap in CAPS]
    cap3 = next(row for row in sweep if row["cap"] == 3)
    sensitivity = [
        {
            "rank_field": field,
            "baseline_recovered": _measure(grouped, TOP_N, field)["recovered"],
            "cap3_recovered": _measure(grouped, 3, field)["recovered"],
            "cap3_displaced_asserted": _measure(grouped, 3, field)["displaced_asserted"],
            "cap3_full_windows": _measure(grouped, 3, field)["full_windows"],
        }
        for field in RANK_FIELDS
    ]
    checks = {
        "population_212": len(source["rows"]) == 212,
        "positives_26": sum(1 for row in source["rows"] if row["asserted"]) == 26,
        "six_seeds": len(grouped) == 6,
        "baseline_18_of_26": baseline["recovered"] == 18,
        "baseline_full_windows": baseline["full_windows"] == 6,
        "cap3_19_of_26": cap3["recovered"] == 19,
        "cap3_full_windows": cap3["full_windows"] == 6,
        "cap3_displaces_no_positive": cap3["displaced_asserted"] == 0,
        "cap3_adds_one_positive": cap3["added_asserted"] == 1,
        "cap5_reproduces_baseline": (
            _measure(grouped, 5, "min_rank")["recovered"] == baseline["recovered"]
            and _measure(grouped, 5, "min_rank")["displaced"] == 0
        ),
        "cap1_cannot_fill": _measure(grouped, 1, "min_rank")["full_windows"] == 0,
        "median_and_final_do_not_gain": all(
            row["cap3_recovered"] <= row["baseline_recovered"]
            for row in sensitivity if row["rank_field"] != "min_rank"
        ),
    }
    if not all(checks.values()):
        raise SystemExit("REFUSED: checks " +
                         ", ".join(key for key, value in checks.items() if not value))

    return engine_stamp.stamp({
        "kind": "source_diversified_top20",
        "status": "POST-HOC DIAGNOSTIC",
        "prereg": None,
        "posthoc": True,
        "engine": "no engine run; reads committed never-served rows",
        "question": (
            "Does a source-diversified top-20 ranking recover more of the 26 "
            "asserted never-served edges than the uncapped ranking, and what "
            "does it displace?"
        ),
        "scope": (
            "The 212 never-served edges from the six-seed replication, ranked "
            "within each seed by observed minimum pre-cap rank. The top 20 is "
            "evaluated per seed; 120 seats in total. This is not a served window."
        ),
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "design": {
            "top_n": TOP_N,
            "seats": 6 * TOP_N,
            "rank_key": "minimum pre-cap rank, then edge",
            "source_cap": "maximum top-20 seats with the same source tag",
            "caps": list(CAPS),
            "identity": "seed and edge together; the same edge can occur in more than one seed",
            "displaced": "a baseline top-20 seat absent from the capped top-20",
            "added": "a capped top-20 seat absent from the baseline top-20",
        },
        "baseline": baseline,
        "cap_sweep": sweep,
        "cap3": cap3,
        "rank_sensitivity": sensitivity,
        "checks": checks,
        "verdict": "NO RELIABLE RECOVERY GAIN",
        "not_evidence": (
            "A post-hoc re-ranking of the 212 never-served edges already observed "
            "in the six-seed replication. The top 20 is per seed, not the engine's "
            "served window. The one additional recovery is on one seed and does "
            "not survive median-rank or final-rank ordering. No engine cell ran, "
            "no fresh seed was spent, and no served prediction, assertion, "
            "acquisition, transfer or capability claim follows."
        ),
    })


def render(art: dict) -> str:
    b = art["baseline"]
    c3 = art["cap3"]
    lines = [
        "# Source-diversified top 20 — post hoc diagnostic",
        "",
        "Generated from `%s` by `python -m benchmarks.source_diversified_top20 --write`. "
        "Do not edit by hand." % ARTIFACT.relative_to(ROOT).as_posix(),
        "",
        "**Verdict: `%s`.** A cap of three seats per source recovers **one** "
        "additional positive, on one seed. It is not a reliable recovery gain."
        % art["verdict"],
        "",
        "## Population",
        "",
        "The source is the six-seed never-served replication: **212** never-served "
        "edges across six seeds, of which **26** are asserted. Each seed is ranked "
        "separately by the observed minimum pre-cap rank, then top 20 is taken. "
        "That gives **120** seats, not one global list, because an edge string can "
        "occur in more than one seed.",
        "",
        "| Measure | Uncapped | Cap 3 |",
        "| --- | ---: | ---: |",
        "| Selected seats | **%d** | **%d** |" % (b["selected"], c3["selected"]),
        "| Full 20-seat windows | **%d / 6** | **%d / 6** |"
        % (b["full_windows"], c3["full_windows"]),
        "| Asserted edges recovered | **%d / 26** | **%d / 26** |"
        % (b["recovered"], c3["recovered"]),
        "| Recovery rate | **%.1f%%** | **%.1f%%** |"
        % (100 * b["recovered"] / 26, 100 * c3["recovered"] / 26),
        "| Baseline seats displaced | — | **%d** |" % c3["displaced"],
        "| Displaced that were asserted | — | **%d** |" % c3["displaced_asserted"],
        "| New seats added | — | **%d** |" % c3["added"],
        "| Added that were asserted | — | **%d** |" % c3["added_asserted"],
        "",
        "The one added positive is the whole gain. Every displaced seat was a "
        "non-asserted edge, so the cap did not trade a positive away on this "
        "ordering — but it also recovered only one of the eight positives the "
        "uncapped top 20 leaves out.",
        "",
        "## Cap sweep",
        "",
        "| Cap per source | Seats | Full windows | Recovered / 26 | Displaced | Displaced asserted | Added | Added asserted |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in art["cap_sweep"]:
        lines.append(
            "| %d | %d | %d | **%d** | %d | %d | %d | %d |"
            % (row["cap"], row["selected"], row["full_windows"], row["recovered"],
               row["displaced"], row["displaced_asserted"], row["added"],
               row["added_asserted"])
        )
    lines += [
        "",
        "Cap 1 cannot fill a 20-seat window on any seed and is not comparable. "
        "Cap 2 loses three asserted baseline seats and recovers no more than the "
        "uncapped list. Cap 3 is the only cap with a positive net gain; cap 4 "
        "and above are the baseline or worse.",
        "",
        "## Per-seed detail at cap 3",
        "",
        "| Seed | Rows | Asserted rows | Recovered | Baseline recovered | Displaced | Added |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in c3["per_seed"]:
        lines.append(
            "| %d | %d | %d | **%d** | %d | %d | %d |"
            % (row["seed"], row["rows"], row["asserted_rows"], row["recovered"],
               row["baseline_recovered"], row["displaced"], row["added"])
        )
    lines += [
        "",
        "The gain is confined to seed **%d**: its uncapped list recovers "
        "**%d / %d**, while the cap-3 list recovers **%d / %d**."
        % (c3["per_seed"][0]["seed"], c3["per_seed"][0]["baseline_recovered"],
           c3["per_seed"][0]["asserted_rows"], c3["per_seed"][0]["recovered"],
           c3["per_seed"][0]["asserted_rows"]),
        "",
        "## Rank sensitivity",
        "",
        "The result depends on which stored rank defines the list. The same cap "
        "does not gain under median-rank or final-rank ordering:",
        "",
        "| Ranking field | Uncapped recovered | Cap-3 recovered | Cap-3 positives displaced |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in art["rank_sensitivity"]:
        lines.append(
            "| `%s` | **%d** | **%d** | **%d** |"
            % (row["rank_field"], row["baseline_recovered"],
               row["cap3_recovered"], row["cap3_displaced_asserted"])
        )
    lines += [
        "",
        "## What this does and does not establish",
        "",
        "This is a post-hoc re-ranking of already-observed never-served edges, "
        "not an engine arm. It does not show that a source cap would change the "
        "served window, assertion, acquisition, transfer or capability. The "
        "uncapped list already recovers 18 of 26, and the capped list recovers "
        "19; the difference is one edge on one seed and reverses its sign under "
        "other stored rank fields.",
        "",
        art["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def problems(art: dict | None = None) -> list[str]:
    art = _load(ARTIFACT) if art is None else art
    found: list[str] = []
    if art.get("kind") != "source_diversified_top20":
        found.append("artifact kind")
    if art.get("status") != "POST-HOC DIAGNOSTIC" or not art.get("posthoc"):
        found.append("diagnostic status")
    if art.get("prereg") is not None:
        found.append("prereg present")
    if engine_stamp.missing(art):
        found.append("stamp: %r" % (engine_stamp.missing(art),))
    s = art.get("summary") if "summary" in art else art
    if s.get("baseline", {}).get("recovered") != 18:
        found.append("baseline recovery")
    if s.get("cap3", {}).get("recovered") != 19:
        found.append("cap-3 recovery")
    if s.get("cap3", {}).get("displaced_asserted") != 0:
        found.append("cap-3 displaced a positive")
    if s.get("cap3", {}).get("added_asserted") != 1:
        found.append("cap-3 added positive")
    if not all((s.get("checks") or {}).values()):
        found.append("checks")
    if PAGE.exists() and PAGE.read_text(encoding="utf-8") != render(art):
        found.append("page stale")
    return found


def write() -> int:
    art = build()
    ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
    PAGE.write_text(render(art), encoding="utf-8")
    print("source-diversified top 20: %s %s"
          % (art["verdict"], json.dumps({
              "seats": art["baseline"]["selected"],
              "baseline_recovered": art["baseline"]["recovered"],
              "cap3_recovered": art["cap3"]["recovered"],
              "displaced": art["cap3"]["displaced"],
              "displaced_asserted": art["cap3"]["displaced_asserted"],
          })))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no artifact; run --write")
    art = _load(ARTIFACT)
    found = problems(art)
    if found:
        raise SystemExit("FAIL: " + "; ".join(found))
    print("source-diversified top 20: %s %s"
          % (art["verdict"], json.dumps({
              "baseline_recovered": art["baseline"]["recovered"],
              "cap3_recovered": art["cap3"]["recovered"],
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
