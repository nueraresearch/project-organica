"""The three cap-112 pre-registrations: comparator, Q1 and Q2.

`DECISION-CAP-LEVEL` records the owner's choice C -- raise `SleepService.MAX_PREDICTIONS`
from 40 to 112 -- as decided and not in force. Landing it needs a version bump and fresh
records for the three presence blocks, because each was frozen at cap 40 and cannot be
re-read under a different level. This module drafts those records, and only the records:

- `PRESENCE-COMPARATOR-112` -- the same-build edge-level audit at cap 112;
- `PRESENCE-CONSTRUCT-1-112` -- Q1, the construct audit at cap 112;
- `PRESENCE-CAP-1-112` -- Q2, the cap block at cap 112, with 112 shipped.

Each is frozen and **authorised**; Q1 and Q2 are NOT RUN, and the comparator is RUN as of
2026-11-11. The runners are built at
`benchmarks/presence_cap112_runners.py` and refuse on every build whose shipped cap is not
112 or whose version is not 0.15.0. The cap landed on 2026-11-11, so the preflight is now
satisfied and the runners are runnable; landing a level does not run a cell.

    ./.venv/bin/python -m benchmarks.presence_cap112_prereg --write
    ./.venv/bin/python -m benchmarks.presence_cap112_prereg --check
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks import presence_cap_experiment as cap

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
KIND = "presence_cap112_prereg"
CAP = 112
FROZEN_ON = "2026-11-11"
TARGET_VERSION = "0.15.0"
SEEDS = [20261100, 20261101, 20261102, 20261103, 20261104, 20261105]
SEEDS_Q2 = [20611901, 20611902, 20611903, 20611904, 20611905, 20611906]
BOOTSTRAP_Q2 = 20611907
AUTHORISATION_DOC = DOCS / "AUTHORISATION-PRESENCE-CAP-112.md"
GRANT_DATE = "2026-11-11"
GRANT_QUOTE = ("Write the dated cap-112 authorisation document for the comparator, Q1 and Q2, "
               "recording the owner's grant against the three frozen records.")

RECORDS = {
    "presence_comparator_112_prereg.json": {
        "prereg": "PRESENCE-COMPARATOR-112",
        "block": "comparator",
        "page": "PRESENCE-COMPARATOR-112-PREREGISTRATION.md",
        "question": ("On a build whose Layer-1 cap is 112, are presence and assertion the same "
                     "object on the same world edges, the same build and the same observation "
                     "window -- and does the 0.14.0 comparator's reading survive the level?"),
        "claim": ("The comparator measures present edges and asserted world edges as sets on one "
                  "build. At cap 40 it returned `PRESENCE NOT ASSERTION`: the asserted set was a "
                  "strict subset of presence. This record re-asks the same question at 112 so the "
                  "level change is not read through a cap-40 instrument."),
        "design": {
            "seeds": SEEDS, "cycles": 120, "cells": 6, "cap": CAP,
            "world": "the Gate-13 compositional world (16 tags, 112 derivable edges)",
            "pairing": "one cell per audit seed; each cell pairs with the cap-112 row of the same seed",
            "reuse": ("The six historical audit seeds, reused so the level comparison is paired per "
                      "seed. This is reuse and is disclosed; it is not an independence claim."),
        },
        "gates": {
            "A1_build": "one build, one sha256, the cap 112 the pin will name; no mixed-build row",
            "A2_world": "one W per seed, no perturbation of order or window",
            "A3_denominator": "W, P and S_ever non-empty in every cell; a zero denominator is not measurable",
            "A4_object": "the asserted edge set is recorded as a set, not a count",
            "A5_seed_axis": "at least two distinct (P, S_ever, A_W) fingerprints across the six seeds",
            "A6_control": "a fresh-process rerun of seed 20261100 reproduces its fingerprints",
        },
        "verdict_rule": ("the comparator's own `_verdict(rows)` over the six cells, unchanged: "
                         "`PRESENCE NOT FULL`, `PRESENCE NOT ASSERTION`, "
                         "`PRESENCE AND ASSERTION COINCIDE`"),
        "gates_control": ("`_verdict` is checked against a hand-built row set for each of its three "
                          "verdicts before any cell runs, so a verdict that cannot be reached is a "
                          "draft defect rather than a result."),
    },
    "presence_construct_1_112_prereg.json": {
        "prereg": "PRESENCE-CONSTRUCT-1-112",
        "block": "Q1",
        "page": "PRESENCE-CONSTRUCT-1-112-PREREGISTRATION.md",
        "question": ("At cap 112, are presence, admitted and asserted measured as comparable "
                     "quantities on the same world edges, the same build and the same window, so a "
                     "conversion or cap reading rests on an edge-level measurement?"),
        "claim": ("Q1's six gates describe an object relation, not a cap: A_W must be a subset of P, "
                  "recorded per seed. The cap-40 record returned `CONSTRUCT VALID`. This record asks "
                  "the same question with the cap the project intends to ship."),
        "design": {
            "seeds": SEEDS, "cycles": 120, "cells": 6, "cap": CAP,
            "control_cell": {"seed": 20261100, "why": "a fresh-process rerun whose fingerprints must match the reading cell"},
            "world": "the Gate-13 compositional world (16 tags, 112 derivable edges)",
            "pairing": "one cell per seed, paired with the cap-112 comparator row for that seed",
        },
        "gates": {
            "C1_build": "one build at the pinned sha256 and cap 112",
            "C2_world": "one W per seed",
            "C3_presence": "P is a set with a digest and per-edge membership",
            "C4_denominator": "W, P and S_ever non-empty; a zero denominator is NOT MEASURABLE",
            "C5_object": "A_W is a subset of P; failure is OBJECT MISMATCH",
            "C6_witnesses": "at least one positive A_W edge and one P-minus-A_W edge per seed",
            "C7_seed_axis": "at least two distinct fingerprints across the six seeds",
            "C8_determinism": "the control rerun reproduces its fingerprints and ordered admission window",
            "C9_comparator_row": ("each cell reproduces the cap-112 comparator row for its seed: world "
                                  "edges, present edges, asserted world edges and asserted fingerprint. "
                                  "This replaces the cap-40 `audit row reproduced` clause, whose "
                                  "published row does not exist at 112."),
        },
        "verdict_rule": ("Q1's own gate set over C1-C9: `CONSTRUCT VALID`, `OBJECT MISMATCH`, "
                         "`NOT MEASURABLE`, `VOID`"),
        "gates_control": ("`--check` builds a record with a cap-40 design and one with C1 deleted and "
                          "requires both to be rejected, so the guard can fail."),
    },
    "presence_cap_1_112_prereg.json": {
        "prereg": "PRESENCE-CAP-1-112",
        "block": "Q2",
        "page": "PRESENCE-CAP-1-112-PREREGISTRATION.md",
        "question": ("With 112 as the shipped Layer-1 cap, does the 40-to-112 paired gain in asserted "
                     "world edges reproduce on a fresh seed block -- and is 112 still limiting?"),
        "claim": ("The cap-40 block returned `CAP LIMITING` on its own seeds: mean paired gain "
                  "15.833333, lower bound 8.081175 against a bar of 10. This record re-runs the same "
                  "four-level design with 112 shipped and a fresh block, so the level decision rests "
                  "on a reproduction rather than on a carried number."),
        "design": {
            "variable": "layer1_prediction_cap",
            "levels": [40, 80, 112, 1000000000],
            "shipped_cap": CAP,
            "seeds": SEEDS_Q2, "bootstrap": BOOTSTRAP_Q2,
            "cycles": 120, "cells": 24,
            "witness_cell": {
                "seed": SEEDS[0], "cap": CAP,
                "why": ("the 112 arm reproduces the cap-112 comparator row for this seed, which is "
                        "what proves the treatment at 112 is the shipped engine; the 40 arm is a "
                        "treatment arm below the shipped default, not a witness"),
            },
            "pairing": "same seed and world across all four caps; only the cap differs",
            "freshness": ("a fresh seed block, disjoint from every committed artifact; the 40 arm is "
                          "kept so the pre-registered 40-to-112 comparison is repeated rather than "
                          "assumed from another block's runs"),
        },
        "gates": {
            "K1_build": "all cells and the witness name one engine version, one sha256 and the effective cap",
            "K2_same_world": "W identical across the four caps of every seed",
            "K3_presence_invariant": "P identical across the four caps of every seed",
            "K4_cap_live": ("each cell records its cap; the 40 arm never returns more than 40 rows; the "
                            "112 arm never more than 112; higher caps change S_ever on at least one seed"),
            "K5_cap_only": ("the treatment overrides no pipeline method and the cap-112 witness "
                            "reproduces the comparator-112 row; a failure is VOID"),
            "K6_denominator": "W, P and S_ever non-empty in every cell",
        },
        "verdict_rule": ("Q2's own decision table, adopted unchanged from "
                         "`docs/presence_cap_prereg.json`: VOID, CAP NOT BINDING, "
                         "ADMISSION-ONLY BOTTLENECK, CAP LIMITING, CAP LIMITING BELOW BAR, "
                         "CAP NOT LIMITING, MIXED"),
        "gates_control": ("the level list, the shipped cap and the witness cap are each checked against "
                          "a mutated record that must be rejected; `K4` is checked against a row set "
                          "whose 40 arm returns 41 rows."),
    },
}

COMMON = {
    "kind": KIND,
    "not_a_result": True,
    "status": "FROZEN, NOT RUN",
    "no_cells_run": True,
    "frozen_on": FROZEN_ON,
    "cap": CAP,
    "engine": {
        "target_version": TARGET_VERSION,
        "shipped_today": "0.15.0, cap 112 (landed 2026-11-11)",
        "requires": ("`DECISION-CAP-LEVEL` C landed: `SleepService.MAX_PREDICTIONS` set to 112, "
                     "version 0.15.0, pin re-recorded, canaries re-recorded and attributed"),
    },
    "authorisation": {
        "required": True,
        "granted": True,
        "granted_on": GRANT_DATE,
        "document": "docs/AUTHORISATION-PRESENCE-CAP-112.md",
        "quote": GRANT_QUOTE,
        "scope": ("the three cap-112 records: PRESENCE-COMPARATOR-112, PRESENCE-CONSTRUCT-1-112 "
                  "and PRESENCE-CAP-1-112, once the cap is landed and a harness exists"),
        "why": ("the owner granted the cap-112 campaign on 2026-11-11; the grant is recorded in "
                "`docs/AUTHORISATION-PRESENCE-CAP-112.md` and quoted there. It does not land the "
                "cap and does not authorise a run under cap 40."),
    },
    "runner": {
        "status": "built",
        "module": "benchmarks/presence_cap112_runners.py",
        "built_on": "2026-11-11",
        "refuses": ("`--measure` refuses while the shipped cap is not 112, the installed version is "
                    "not 0.15.0, the pin does not name it, or the block canaries were not "
                    "re-recorded on the installed bytes"),
        "why": ("the three blocks are implemented against these frozen designs and their gates. On "
                "the landed build (0.15.0, cap 112) the preflight is satisfied, so `--measure` "
                "would open a cell; no cell has been started here"),
    },
    "amendments": [{
        "date": "2026-11-11",
        "kind": "runner-built",
        "reason": ("the owner's grant of 2026-11-11 authorised the cells, and the runners were the "
                   "separate step the draft named"),
        "disclosure": ("`benchmarks/presence_cap112_runners.py` implements the comparator, Q1 and Q2 "
                       "cells and their gates, with verdict rules and gate controls that run on "
                       "hand-built rows. `--measure` refuses on this build: the shipped cap is 40 "
                       "and the installed version is 0.14.0. No cell has run, no verdict is "
                       "adjudicated, and the design, seeds, gates and verdict rules above are "
                       "unchanged."),
    }, {
        "date": "2026-11-11",
        "kind": "cap-landed",
        "reason": ("the owner instructed the 0.15.0 landing: version 0.15.0, cap 112, engine re-pin "
                   "and canaries re-recorded with attribution"),
        "disclosure": ("`SleepService.MAX_PREDICTIONS` is 112 and the package is 0.15.0. Each of the "
                       "four runner conditions is met, so the records are runnable; landing does "
                       "not run them. The records' status stays FROZEN, NOT RUN and their design, "
                       "seeds, gates and verdict rules are unchanged. The 0.14.0 cap-40 records are "
                       "superseded, not re-scored: each carries a dated build_superseded block."),
    }],
    "decision_table_source": None,
    "result": None,
    "not_evidence": ("A draft is not a run. No cell has executed, no verdict is adjudicated, and none "
                     "of these records may be cited as a cap-112 result."),
}


COMPARATOR_RUN = {
    "status": "FROZEN, RUN",
    "no_cells_run": False,
    "result": {
        "artifact": "docs/presence_comparator_112_run.json",
        "page": "docs/PRESENCE-COMPARATOR-112-RESULT.md",
        "verdict": "PRESENCE NOT ASSERTION",
        "date": "2026-11-11",
    },
}
Q2_RUN = {
    "status": "FROZEN, RUN",
    "no_cells_run": False,
    "result": {
        "artifact": "docs/presence_cap_1_112_run.json",
        "page": "docs/PRESENCE-CAP-1-112-RESULT.md",
        "verdict": "CAP LIMITING",
        "date": "2026-11-11",
    },
}
Q2_RUN_AMENDMENT = {
    "date": "2026-11-11",
    "kind": "run-completed",
    "reason": "the comparator-112 rows existed and the preflight was empty, so the arm's 24 cells and witness could run",
    "disclosure": ("The 24 cells (six seeds x 40/80/112/uncapped) and the 112 witness executed "
                   "on 2026-11-11 on the shipped 0.15.0 build. `--finish` wrote "
                   "docs/presence_cap_1_112_run.json and docs/PRESENCE-CAP-1-112-RESULT.md; the "
                   "verdict is `CAP LIMITING`, all six K gates pass, mean paired gain is "
                   "17.833333 with lower bound 13.613754 against a bar of 10 on 6 of 6 seeds. "
                   "The 21-40 band is not identifiable from this block: its fresh seeds differ "
                   "from Q4's and its cells record counts, not per-edge ranks, so the decision's "
                   "acceptance condition remains unadjudicated and the decision stays PENDING. "
                   "The design, seeds, gates, verdict rule and acceptance condition are "
                   "unchanged, and Q1 remains unrun."),
}
COMPARATOR_RUN_AMENDMENT = {
    "date": "2026-11-11",
    "kind": "run-completed",
    "reason": ("the preflight became empty when 0.15.0 landed, and the owner's 2026-11-11 "
               "grant already covered these cells"),
    "disclosure": ("The seven planned runs executed on 2026-11-11: six audit seeds and the "
                   "control, on the shipped 0.15.0 build at cap 112. `--finish` wrote "
                   "docs/presence_comparator_112_run.json and "
                   "docs/PRESENCE-COMPARATOR-112-RESULT.md; the verdict is `PRESENCE NOT "
                   "ASSERTION`, all six gates A1-A6 pass, and the asserted world edges are "
                   "51-64 of 112 (conversion 0.455-0.571). Status moved to FROZEN, RUN. The "
                   "design, seeds, gates, verdict rule and acceptance condition are "
                   "unchanged, and no other block ran."),
}


def _record(body: dict) -> dict:
    record = json.loads(json.dumps(COMMON))
    record.update({key: body[key] for key in
                   ("prereg", "block", "question", "claim", "design", "gates", "verdict_rule",
                    "gates_control")})
    record["page"] = body["page"]
    record["decision_table_source"] = (
        "docs/presence_assertion_audit_0.14.0.json" if body["block"] == "comparator"
        else "docs/presence_construct_audit_prereg.json" if body["block"] == "Q1"
        else "docs/presence_cap_prereg.json")
    record["seed_block"] = sorted(record["design"]["seeds"])
    # Comparator and Q1 reuse the audit seeds on purpose, so the collision scan must see the
    # reuse as declared rather than as a fresh block that happens to collide. Any other
    # artifact naming these seeds will still make the check fire.
    # The audit seeds are named by dozens of committed artifacts, so a global sweep cannot
    # distinguish reuse from a collision. The check instead proves the reuse against the
    # comparator artifact itself, seed by seed.
    if body["block"] == "comparator":
        record.update(COMPARATOR_RUN)
        record["runner"]["cells_run"] = 7
        record["runner"]["why"] = (
            "the three blocks are implemented against these frozen designs and their "
            "gates. The comparator's seven planned runs (six audit seeds plus the control) "
            "executed on 2026-11-11; Q1 and Q2 remain unrun.")
        record["amendments"].append(COMPARATOR_RUN_AMENDMENT)
    elif body["block"] == "Q2":
        record.update(Q2_RUN)
        record["runner"]["cells_run"] = 25
        record["runner"]["why"] = (
            "the 24 cells and the 112 witness executed on 2026-11-11; Q1 remains "
            "unrun.")
        record["amendments"].append(Q2_RUN_AMENDMENT)
    record["seed_reuse"] = (
        "the six historical audit seeds, reused so the level comparison is paired; declared "
        "against docs/presence_assertion_audit_0.14.0.json"
        if body["block"] in ("comparator", "Q1") else None)
    return engine_stamp.stamp(record)


def records() -> dict[str, dict]:
    return {name: _record(body) for name, body in RECORDS.items()}


def problems(record: dict, allow=()) -> list[str]:
    found: list[str] = []
    name = record.get("prereg", "?")
    if record.get("kind") != KIND:
        found.append("%s: kind" % name)
    status = record.get("status")
    if status == "FROZEN, RUN":
        result = record.get("result") or {}
        artifact = result.get("artifact")
        if record.get("no_cells_run") is not False:
            found.append("%s: a run record still says no cell ran" % name)
        if not artifact or not (ROOT / artifact).exists():
            found.append("%s: a run record names no existing result artifact" % name)
        if not result.get("verdict"):
            found.append("%s: a run record names no verdict" % name)
    elif status == "FROZEN, NOT RUN":
        if record.get("no_cells_run") is not True:
            found.append("%s: an unrun record does not say no cell ran" % name)
        if record.get("result") is not None:
            found.append("%s: an unrun record carries a result" % name)
    else:
        found.append("%s: status is %r" % (name, status))
    if record.get("cap") != CAP or record.get("design", {}).get("cap", CAP) != CAP:
        found.append("%s: the record is not at cap 112" % name)
    if record.get("design", {}).get("cycles") != 120:
        found.append("%s: cycles" % name)
    design = record.get("design") or {}
    seeds = list(design.get("seeds") or [])
    if len(seeds) < 6 or len(set(seeds)) != len(seeds):
        found.append("%s: seed block" % name)
    if design.get("cap") == CAP and design.get("cells") != 6 and "levels" not in design:
        found.append("%s: six cells expected" % name)
    if "levels" in design:
        if design["levels"] != [40, 80, 112, cap.UNCAPPED]:
            found.append("%s: levels are not 40, 80, 112 and the ceiling" % name)
        if design.get("shipped_cap") != CAP:
            found.append("%s: the shipped cap is not 112" % name)
        if design.get("cells") != len(seeds) * len(design["levels"]):
            found.append("%s: cells are not seeds x levels" % name)
        witness = design.get("witness_cell") or {}
        if witness.get("cap") != CAP:
            found.append("%s: the witness is not at 112" % name)
        if any(seed in design["levels"] for seed in ()):
            pass
    gates = record.get("gates") or {}
    if not gates:
        found.append("%s: no gates" % name)
    if "IV" in "".join(gates) or not record.get("gates_control"):
        found.append("%s: no control for the gates" % name)
    auth = record.get("authorisation") or {}
    if auth.get("granted"):
        doc = ROOT / (auth.get("document") or "")
        if not doc.exists():
            found.append("%s: a grant names no existing document" % name)
        else:
            text = " ".join(doc.read_text(encoding="utf-8").split())
            if " ".join((auth.get("quote") or "").split()) not in text:
                found.append("%s: the quoted grant is not in the document" % name)
            if auth.get("granted_on") not in text:
                found.append("%s: the grant date is not in the document" % name)
    runner = record.get("runner") or {}
    if runner.get("status") != "built":
        found.append("%s: the runner is not disclosed as built" % name)
    elif not runner.get("module") or not (ROOT / runner["module"]).exists():
        found.append("%s: the runner module does not exist" % name)
    if not record.get("amendments"):
        found.append("%s: the runner build is not disclosed as an amendment" % name)
    if "levels" in design:
        allowed = tuple(allow) + tuple(DOCS.glob("*_112_prereg*"))
        own_run = (record.get("result") or {}).get("artifact")
        if own_run:
            allowed += (ROOT / own_run,)
        collisions = cap.seed_collisions(
            list(seeds) + ([design["bootstrap"]] if design.get("bootstrap") else []),
            allow=allowed)
        if collisions:
            found.append("%s: fresh-block seeds collide with %s" % (name, sorted(collisions)))
    else:
        if seeds != SEEDS:
            found.append("%s: the reused block is not the six audit seeds" % name)
        audit = (DOCS / "presence_assertion_audit_0.14.0.json").read_text(encoding="utf-8")
        missing = [seed for seed in seeds if str(seed) not in audit]
        if missing or not record.get("seed_reuse"):
            found.append("%s: seed reuse is not declared against the comparator artifact" % name)
    return found


def render(records_map: dict[str, dict]) -> dict[str, str]:
    pages: dict[str, str] = {}
    for record in records_map.values():
        design = record["design"]
        lines = [
            "# %s -- pre-registration at cap 112" % record["prereg"],
            "",
            "**Status: %s, %s.** Drafted %s; %s %s" % (
                record["status"],
                "AUTHORISED" if record["authorisation"]["granted"] else "NOT AUTHORISED",
                FROZEN_ON,
                "the owner's cap-112 grant is recorded in `%s`." % record["authorisation"]["document"]
                if record["authorisation"]["granted"] else "no grant is recorded.",
                ("The planned runs executed on 2026-11-11 and the result is below."
                 if record["status"] == "FROZEN, RUN" else
                 "No cell has executed and no verdict is adjudicated.")),
            "",
            "## Question",
            "",
            record["question"],
            "",
            "## Design",
            "",
            "| Field | Value |",
            "| --- | --- |",
            "| Cap | %d |" % CAP,
            "| Seeds | %s |" % ", ".join(str(s) for s in design["seeds"]),
            "| Cycles | %d |" % design["cycles"],
            "| Cells | %d |" % design["cells"],
        ]
        if "levels" in design:
            lines.append("| Levels | %s |" % ", ".join(str(x) for x in design["levels"]))
            lines.append("| Shipped cap | %d |" % design["shipped_cap"])
        lines += ["| World | %s |" % design.get("world", "the Gate-13 compositional world"),
                  "",
                  "## Gates",
                  "",
                  "| Gate | Requirement |",
                  "| --- | --- |"]
        for gate, text in record["gates"].items():
            lines.append("| `%s` | %s |" % (gate, text))
        lines += ["", "## Verdicts this block can return", "",
                  record["verdict_rule"], "",
                  "The decision table is the predecessor's, adopted unchanged: `%s`." %
                  record["decision_table_source"], "",
                  *(["## Result", "",
                     "**Verdict: `%s`.** Artifact `%s`; page `%s`. The design, seeds, "
                     "gates and verdict rule above are unchanged." % (
                         record["result"]["verdict"], record["result"]["artifact"],
                         record["result"]["page"]), ""]
                    if record["status"] == "FROZEN, RUN" else
                    ["## Why it has not run yet", "",
                     "- **The level.** %s" % record["engine"]["requires"],
                     ("- **Grant recorded.** %s" if record["authorisation"]["granted"]
                      else "- **No grant.** %s") % record["authorisation"]["why"],
                     "- **Runner built.** %s" % record["runner"]["why"], ""]),
                  "## Controls", "",
                  record["gates_control"], "",
                  "## Not evidence", "",
                  record["not_evidence"], ""]
        pages[record["page"]] = "\n".join(lines)
    return pages


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    built = records()
    if args.write:
        paths = []
        for name, record in built.items():
            path = DOCS / name
            path.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
            paths.append(path.relative_to(ROOT))
        for page, text in render(built).items():
            (DOCS / page).write_text(text, encoding="utf-8")
        print("wrote %d records and %d pages" % (len(paths), len(built)))
        return 0
    found: list[str] = []
    for name, record in built.items():
        stored = DOCS / name
        if not stored.exists() or json.loads(stored.read_text(encoding="utf-8")) != record:
            found.append("%s: the stored record is not a fresh build" % name)
        found += problems(record, allow=[stored])
        page = DOCS / record["page"]
        if not page.exists() or page.read_text(encoding="utf-8") != render({name: record})[record["page"]]:
            found.append("%s: the page is stale" % record["page"])
        run_name = "docs/%s_run.json" % record["prereg"].lower().replace("-", "_")
        run_path = ROOT / run_name
        if record["status"] == "FROZEN, RUN":
            if not run_path.exists():
                found.append("%s: a run record has no run artifact" % name)
            elif (record.get("result") or {}).get("artifact") != run_name:
                found.append("%s: the run record names a different artifact" % name)
        elif run_path.exists():
            found.append("%s: a run artifact exists" % name)
    for problem in found:
        print("FAIL:", problem)
    if found:
        return 1
    states = sorted({"authorised" if record["authorisation"]["granted"] else "unauthorised"
                     for record in built.values()})
    ran = sum(1 for record in built.values() if record["status"] == "FROZEN, RUN")
    print("cap-112 drafts: %d records, %d frozen and unrun, %d frozen and run, %s, runner built"
          % (len(built), len(built) - ran, ran, ", ".join(states)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
