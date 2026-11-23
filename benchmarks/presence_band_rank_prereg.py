"""PRESENCE-BAND-1 -- the per-edge band arm at 40 versus 112, frozen and unrun.

Q2 measured the cap's effect on counts and could not identify the Q4 rank-21-40
transitions: its seeds were fresh and its cells recorded counts, not per-edge ranks.
This block is the instrument that can. It names the 62 edges, runs the same six Q4
worlds at cap 40 and cap 112, and records each named edge's rank and service in both
arms, so the admission decision's acceptance condition is read on edges rather than
on an aggregate.

The block is a record, not a runner: no cell has run, the arm module does not exist,
and no engine file changes. The 40 arm is the pre-treatment control; the 112 arm is
the designated counterfactual.

    ./.venv/bin/python -m benchmarks.presence_band_rank_prereg --render
    ./.venv/bin/python -m benchmarks.presence_band_rank_prereg --check
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECORD = ROOT / "docs/presence_band_rank_prereg.json"
PAGE = ROOT / "docs/PRESENCE-BAND-RANK-PREREGISTRATION.md"
RUN = ROOT / "docs/presence_band_rank_run.json"
ARM = ROOT / "benchmarks/presence_band_rank_arm.py"
Q4 = ROOT / "docs/presence_conversion_repair_run.json"
DECISION = ROOT / "docs/DECISION-ADMISSION-STEP.md"
STATUS = "FROZEN, RUN"
DIRECTIONS = ("BAND IN SERVICE", "BAND NOT IN SERVICE")
VERDICTS = ("VOID", "BAND IN SERVICE", "BAND PARTLY IN SERVICE", "BAND NOT IN SERVICE",
            "BAND NOT REPRODUCED")
RESULT_PAGE = ROOT / "docs" / "PRESENCE-BAND-RANK-RESULT.md"
AUTH_DOC = ROOT / "docs" / "AUTHORISATION-PRESENCE-BAND-1.md"
BAND_TOTAL = 62
PARTS = ROOT / ".scratch/presence_repair/parts"


def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def render(doc: dict) -> str:
    design = doc["design"]
    engine = doc["engine"]
    band = doc["band"]
    seeds = ", ".join(str(seed) for seed in design["seeds"])
    lines = [
        "# PRESENCE-BAND-1 — the 21–40 transitions at 40 versus 112",
        "",
        "**Status.** %s. This page is rendered from `%s`; it is not edited by hand."
        % (doc["status"], RECORD.relative_to(ROOT).as_posix()),
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Preregistration | `%s` |" % doc["prereg"],
        "| Frozen on | %s |" % doc["frozen_on"],
        "| Engine | %s, cap %d, %s |" % (engine["version"], engine["cap"], engine["edit"]),
        "| Question | %s |" % doc["question"],
        "| Cells planned | %d (%s) |" % (design["cells"], design["cells_arithmetic"]),
        "| Seeds | %s |" % seeds,
        "| Caps | %s |" % ", ".join(str(cap) for cap in design["caps"]),
        "| Cycles | %d |" % design["cycles"],
        "| Named band edges | %d |" % band["total"],
        "| Runner | %s |" % ("built" if doc["runner"]["built"] else "not built"),
        "| Cells run | %d |" % doc["runner"]["cells_run"],
        "| Authorisation | %s |"
        % ("granted" if doc["authorisation"]["granted"] else "not granted"),
        "",
        "## The 62 named edges",
        "",
        "These are Q4's never-served present transitions whose minimum block rank in the "
        "ceiling universe was 21–40. They are frozen here by identity, so the arm reads "
        "service on the named edges rather than on a rank band recomputed at run time.",
        "",
        "| Seed | Edge | Q4 best rank |",
        "| ---: | --- | ---: |",
    ]
    for seed, row in band["seeds"].items():
        for source, target, rank in row["edges"]:
            lines.append("| %s | `%s>%s` | %s |" % (seed, source, target, rank))
    lines += [
        "",
        "| Seed | World digest | Present | Named edges |",
        "| ---: | --- | ---: | ---: |",
    ]
    for seed, row in band["seeds"].items():
        lines.append("| %s | `%s` | %d | %d |"
                     % (seed, row["world_digest"], row["present"], len(row["edges"])))
    lines += [
        "",
        "**Derivation.** %s" % band["derivation"],
        "",
        "**Source.** `%s`, with the per-cycle candidate ledger from `%s`; both are Q4's, "
        "frozen before this record." % (band["source"]["artifact"], band["source"]["parts"]),
        "",
        "## What this block is, and is not",
        "",
        doc["program"]["relationship"],
        "",
        "## Design",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Arms | %s |" % " and ".join("cap %d" % cap for cap in design["caps"]),
        "| Variable | `SleepService.MAX_PREDICTIONS`, set per cell |",
        "| Observer | %s |" % design["observer"],
        "| World | %s |" % design["world"],
        "| Pairing | %s |" % design["pairing"],
        "| Reuse | %s |" % design["reuse"],
        "| Cycles | %d |" % design["cycles"],
        "| Cells | %d |" % design["cells"],
        "",
        "**Treatment.** %s" % engine["treatment"],
        "",
        "## Endpoints",
        "",
        "| Stage | Definition | Role |",
        "| --- | --- | --- |",
    ]
    for row in doc["endpoints"]:
        lines.append("| %s | %s | %s |" % (row["stage"], row["definition"], row["role"]))
    lines += ["", "## Gates", "", "| Gate | Rule |", "| --- | --- |"]
    for gate, rule in doc["gates"].items():
        lines.append("| `%s` | %s |" % (gate, rule))
    lines += [
        "",
        "## Acceptance condition",
        "",
        "> %s" % doc["acceptance"]["quote"],
        "",
        "Source: `%s`. %s" % (doc["acceptance"]["source"], doc["acceptance"]["owner"]),
        "",
        "## Prediction, stated before any cell",
        "",
        "**Prediction.** %s" % doc["prediction"]["statement"],
        "",
        "**Because.** %s" % doc["prediction"]["because"],
        "",
        "**Falsifier.** %s" % doc["prediction"]["falsifier"],
        "",
        doc["prediction"]["note"],
        "",
        "## Decision table",
        "",
        "| Condition | Verdict | Reading | Decision |",
        "| --- | --- | --- | --- |",
    ]
    for row in doc["decision_table"]:
        lines.append("| %s | **%s** | %s | %s |"
                     % (row["condition"], row["verdict"], row["reading"], row["decision"]))
    if doc.get("result"):
        result = doc["result"]
        lines += ["", "## Result", "",
                  "**%s** -- `%s`, %s." % (result["verdict"], result["artifact"], result["date"]),
                  "", result.get("note", ""), ""]
    lines += [
        "",
        "## Authorisation and stop",
        "",
        "**Authorisation.** %s" % doc["authorisation"]["note"],
        "",
        "**Cost.** %s cells (%s) x %d cycles. %s"
        % (doc["cost"]["cells"], doc["cost"]["witness_cells"], doc["cost"]["cycles"],
           doc["cost"]["wall_clock_estimate"]),
        "",
        "**Stop condition.** %s" % doc["stop_condition"],
        "",
        "## What this record does not license",
        "",
        doc["not_evidence"],
        "",
    ]
    if doc.get("amendments"):
        lines += ["", "## Amendments", ""]
        for row in doc["amendments"]:
            lines.append("- **%s — `%s`.** %s"
                         % (row.get("date"), row.get("kind"), row.get("note")))
    return "\n".join(lines)


def band_from_part(part: dict) -> dict:
    """One Q4 seed's band from its part: present transitions never served, best rank 21-40."""
    present = {tuple(edge) for edge in part.get("present_edges") or []}
    served = {tuple(item.split(">"))
              for cycle in part.get("windows_world") or [] for item in cycle}
    best: dict = {}
    for cycle in part.get("universe") or []:
        for row in cycle:
            if row.get("relation") != "transition":
                continue
            edge = tuple(row["edge"])
            if edge not in present:
                continue
            best[edge] = min(best.get(edge, 10 ** 9), int(row["rank"]))
    return {edge: rank for edge, rank in best.items()
            if 21 <= rank <= 40 and edge not in served}


def ledger_problems(doc: dict, parts: dict) -> list[str]:
    """Compare the frozen names and ranks with the Q4 parts they were derived from."""
    found: list[str] = []
    for seed, row in ((doc.get("band") or {}).get("seeds") or {}).items():
        part = parts.get(seed)
        if part is None:
            continue
        if str(part.get("seed")) != seed:
            found.append("seed %s's part names seed %r" % (seed, part.get("seed")))
        if part.get("world_digest") != row.get("world_digest"):
            found.append("seed %s's part digest is not the frozen one" % seed)
        frozen = {(source, target): rank for source, target, rank in row.get("edges") or []}
        computed = band_from_part(part)
        if computed != frozen:
            missing = len(set(frozen) - set(computed))
            extra = len(set(computed) - set(frozen))
            diffs = sum(1 for edge in set(frozen) & set(computed) if frozen[edge] != computed[edge])
            found.append("seed %s's band does not match its Q4 part: "
                         "%d missing, %d extra, %d rank difference(s)"
                         % (seed, missing, extra, diffs))
    return found


def problems(doc: dict | None = None, page: str | None = None) -> list[str]:
    doc = record() if doc is None else doc
    page = PAGE.read_text(encoding="utf-8") if page is None else page
    found: list[str] = []
    if doc.get("prereg") != "PRESENCE-BAND-1":
        found.append("the preregistration id is not PRESENCE-BAND-1")
    if doc.get("status") != STATUS:
        found.append("status is %r, not %r" % (doc.get("status"), STATUS))
    if doc.get("no_cells_run") is not False:
        found.append("the record does not declare that the cells ran")
    if not RUN.exists():
        found.append("%s does not exist" % RUN.relative_to(ROOT).as_posix())
    if not ARM.exists():
        found.append("%s does not exist" % ARM.relative_to(ROOT).as_posix())
    engine = doc.get("engine") or {}
    if engine.get("version") != "0.15.0" or engine.get("cap") != 112:
        found.append("the engine is not the shipped 0.15.0 at cap 112")
    if engine.get("edit") != "none":
        found.append("the record does not declare no engine edit")
    if not engine.get("treatment"):
        found.append("the record does not name the treatment")
    try:
        import organica
        from organica.sleep import SleepService
        if SleepService.MAX_PREDICTIONS != 112:
            found.append("the shipped cap is %d, not 112" % SleepService.MAX_PREDICTIONS)
        if getattr(organica, "__version__", None) != "0.15.0":
            found.append("the shipped version is not 0.15.0")
    except Exception as exc:  # pragma: no cover - import failure is reported, not raised
        found.append("the shipped engine could not be read: %s" % exc)

    design = doc.get("design") or {}
    seeds = list(design.get("seeds") or [])
    if len(seeds) != 6 or len(set(seeds)) != 6:
        found.append("the design does not hold six distinct seeds")
    if design.get("caps") != [40, 112] or design.get("shipped_cap") != 112:
        found.append("the caps are not 40 and 112 with 112 shipped")
    if design.get("cells") != len(seeds) * 2:
        found.append("the cell count is not caps x seeds")
    if design.get("cycles") != 120:
        found.append("the cycle count is not Q4's 120")
    if not design.get("reuse") or "Q4" not in design["reuse"]:
        found.append("the Q4 seed reuse is not declared")

    band = doc.get("band") or {}
    band_seeds = band.get("seeds") or {}
    if band.get("total") != BAND_TOTAL:
        found.append("the band total is not %d" % BAND_TOTAL)
    if set(band_seeds) != {str(seed) for seed in seeds}:
        found.append("the band's seeds are not the design's seeds")
    total = 0
    for seed, row in band_seeds.items():
        edges = row.get("edges") or []
        total += len(edges)
        for edge in edges:
            if (not isinstance(edge, list) or len(edge) != 3
                    or not all(isinstance(part, str) and part for part in edge[:2])
                    or not 21 <= int(edge[2]) <= 40):
                found.append("seed %s has a malformed or out-of-band edge %r"
                             % (seed, edge))
                break
        if len({tuple(edge[:2]) for edge in edges}) != len(edges):
            found.append("seed %s names one edge twice" % seed)
    if total != BAND_TOTAL:
        found.append("the per-seed edges sum to %d, not %d" % (total, BAND_TOTAL))
    if PARTS.is_dir():
        available = {}
        for seed in band_seeds:
            path = PARTS / ("%s-on.json" % seed)
            if path.exists():
                available[seed] = json.loads(path.read_text(encoding="utf-8"))
        if available:
            found.extend(ledger_problems(doc, available))
    if not band.get("derivation") or "21-40" not in band["derivation"]:
        found.append("the band has no derivation naming the 21-40 rule")

    q4 = json.loads(Q4.read_text(encoding="utf-8")) if Q4.exists() else {}
    if q4.get("verdict") != "CONVERSION STAGE MEASURED":
        found.append("the Q4 artifact is missing or not the stage measurement")
    else:
        table = {str(row["seed"]): row for row in q4.get("stage_table", [])}
        for seed, row in band_seeds.items():
            q4_row = table.get(seed)
            if q4_row is None:
                found.append("seed %s has no Q4 stage row" % seed)
                continue
            if len(row.get("edges") or []) != q4_row.get("never_served_rank_half_to_cap"):
                found.append("seed %s's band is not Q4's 21-40 count" % seed)
        if (q4.get("rank_semantics") or {}).get("in_cap_never_served") != BAND_TOTAL:
            found.append("Q4's rank semantics do not name %d in-cap never-served edges"
                         % BAND_TOTAL)

    acceptance = doc.get("acceptance") or {}
    quote = " ".join((acceptance.get("quote") or "").split())
    if "served at 112" not in quote or "per seed" not in quote:
        found.append("the acceptance quote does not state service at 112 per seed")
    if not quote.startswith("The 21") or len(quote) > 220:
        found.append("the acceptance quote is not the decision's acceptance sentence")
    decision_text = " ".join(DECISION.read_text(encoding="utf-8").split()) if DECISION.exists() else ""
    if not quote or quote not in decision_text:
        found.append("the acceptance quote is not in the admission-step decision")

    gates = doc.get("gates") or {}
    for gate in ("B1_build", "B2_world", "B3_band_identity", "B4_control_40",
                 "B5_cap_live", "B6_denominator", "B7_determinism", "B8_seed_axis"):
        if gate not in gates:
            found.append("the gate %s is missing" % gate)
    joined = " ".join(gates.values()).lower()
    for needed in ("21-40", "0 of 62", "56", "zero denominator", "rerun"):
        if needed not in joined:
            found.append("no gate carries %r" % needed)

    table = doc.get("decision_table") or []
    verdicts = {row.get("verdict") for row in table}
    for direction in DIRECTIONS:
        if direction not in verdicts:
            found.append("the %r direction is missing" % direction)
    if "VOID" not in verdicts or "BAND NOT REPRODUCED" not in verdicts:
        found.append("the decision table has no void or identity row")
    gated = [row for row in table if row.get("verdict") in DIRECTIONS]
    decisions = [row.get("decision") for row in gated]
    if len(set(decisions)) != len(decisions):
        found.append("two directions share one decision, so the table is not two-directional")
    for row in table:
        for key in ("condition", "verdict", "reading", "decision"):
            if not row.get(key):
                found.append("a decision row lacks %s" % key)

    auth = doc.get("authorisation") or {}
    for field in ("granted_on", "document", "quote"):
        if not auth.get(field):
            found.append("the grant lacks `authorisation.%s`" % field)
    if auth.get("granted") is not True:
        found.append("the record claims no authorisation")
    document = ROOT / (auth.get("document") or "docs/NO-SUCH-GRANT.md")
    if not document.exists():
        found.append("the authorisation document does not exist")
    else:
        text = document.read_text(encoding="utf-8")
        if auth.get("quote") not in text:
            found.append("the quoted grant does not appear in its document")
        if auth.get("granted_on") not in text:
            found.append("the grant date does not appear in its document")
    result = doc.get("result") or {}
    if not result:
        found.append("the record carries no result block")
    else:
        if result.get("verdict") not in VERDICTS:
            found.append("the result verdict is %r" % (result.get("verdict"),))
        for field in ("artifact", "page"):
            path = ROOT / (result.get(field) or "docs/NO-SUCH-RESULT")
            if not path.exists():
                found.append("the result %s does not exist" % field)
    kinds = [row.get("kind") for row in doc.get("amendments") or []]
    for kind in ("grant-recorded", "harness-fixed", "run-completed"):
        if kind not in kinds:
            found.append("the record has no %r amendment" % kind)
    runner = doc.get("runner") or {}
    if runner.get("built") is not True:
        found.append("the record does not claim a built runner")
    if runner.get("cells_run") != 13:
        found.append("the runner claims %r cells, not 13" % (runner.get("cells_run"),))
    if runner.get("planned_module") != ARM.relative_to(ROOT).as_posix():
        found.append("the planned arm module is not %s" % ARM.relative_to(ROOT).as_posix())
    if not doc.get("not_evidence") or "capability" not in doc["not_evidence"].lower():
        found.append("the record does not disclaim a capability claim")
    if "no cell has run" in (doc.get("not_evidence") or "").lower():
        found.append("the record still says that no cell has run")
    if page.strip() != render(doc).strip():
        found.append("the page does not match the record; run --render")
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args(argv)
    if args.render:
        PAGE.write_text(render(record()), encoding="utf-8")
        print("rendered %s" % PAGE.relative_to(ROOT).as_posix())
        return 0
    found = problems()
    for problem in found:
        print("FAIL:", problem)
    if found:
        return 1
    doc = record()
    print("presence band: %s, %d cells, %d named edges, %d runs, %s"
          % (doc["status"], doc["design"]["cells"], doc["band"]["total"],
             doc["runner"]["cells_run"], doc["result"]["verdict"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
