"""T1 -- the persistence-off preregistration at cap 112, frozen and unrun.

The block asks whether conversion at the shipped cap depends on temporal edge counts carried
across sleep cycles. It is a record, not a runner: no cell exists, no engine file changes, and
the arm is named and parameterised but not implemented.

    ./.venv/bin/python -m benchmarks.t1_persistence_off_prereg --render
    ./.venv/bin/python -m benchmarks.t1_persistence_off_prereg --check
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECORD = ROOT / "docs/t1_persistence_off_prereg.json"
PAGE = ROOT / "docs/T1-PERSISTENCE-OFF-PREREGISTRATION.md"
RUN = ROOT / "docs/t1_persistence_off_run.json"
ARM = ROOT / "benchmarks/t1_persistence_off_arm.py"
STATUS = "FROZEN, RUN"
RESULT_PAGE = ROOT / "docs/T1-PERSISTENCE-OFF-RESULT.md"
AUTH_DOC = ROOT / "docs/AUTHORISATION-T1-PERSISTENCE-OFF.md"
VERDICTS = ("VOID", "PERSISTENCE CONTRIBUTES", "PERSISTENCE NOT LIMITING", "MIXED")
DIRECTIONS = ("PERSISTENCE CONTRIBUTES", "PERSISTENCE NOT LIMITING")
GATES = ("G1_build", "G2_world", "G3_manipulation_live", "G4_denominator",
         "G5_seed_axis", "G6_determinism", "G7_cells")


def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def render(doc: dict) -> str:
    design = doc["design"]
    engine = doc["engine"]
    bar = doc["decision_rule"]["bar"]
    seeds = ", ".join(str(seed) for seed in design["seeds"])
    lines = [
        "# T1 — persistence-off at the shipped cap 112",
        "",
        "**Status.** %s. This page is rendered from `%s`; it is not edited by hand."
        % (doc["status"], RECORD.relative_to(ROOT)),
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Preregistration | `%s` |" % doc["prereg"],
        "| Frozen on | %s |" % doc["frozen_on"],
        "| Engine | %s, cap %d, %s |" % (engine["version"], engine["cap"], engine["edit"]),
        "| Question | %s |" % doc["question"],
        "| Cells planned | %d (%s) |" % (design["cells"], design["cells_arithmetic"]),
        "| Seeds | %s; bootstrap %d |" % (seeds, design["bootstrap"]),
        "| Cycles | %d |" % design["cycles"],
        "| Runner | %s |" % ("built" if doc["runner"]["built"] else "not built"),
        "| Cells run | %d |" % doc["runner"]["cells_run"],
        "| Authorisation | %s |"
        % ("granted" if doc["authorisation"]["granted"] else "not granted"),
        "",
        "## Arms",
        "",
        "| Arm | Service | Carried temporal counts |",
        "| --- | --- | --- |",
    ]
    for name, arm in doc["arms"].items():
        lines.append("| %s | `%s` | %s |" % (name, arm["service"], arm["carried"]))
    lines += [
        "",
        "**Manipulation.** %s" % doc["mechanism"]["changes"],
        "",
        "The arm is named `%s` and is not implemented: `%s` does not exist. The class is the "
        "frozen definition, not a built runner."
        % (doc["mechanism"]["arm_class"], ARM.relative_to(ROOT)),
        "",
        "## Endpoints",
        "",
        "| Stage | Definition | Role |",
        "| --- | --- | --- |",
    ]
    for row in doc["endpoints"]:
        lines.append("| %s | %s | %s |" % (row["stage"], row["definition"], row["role"]))
    lines += ["", doc["endpoint_note"], "", "## Gates", "", "| Gate | Rule |", "| --- | --- |"]
    for gate, rule in doc["gates"].items():
        lines.append("| %s | %s |" % (gate, rule))
    lines += [
        "",
        "## Decision rule",
        "",
        doc["decision_rule"]["rule"],
        "",
        "Margin: %d edges, %d of %d seeds in the same direction, paired bootstrap %d%% lower "
        "bound above zero, %d resamples at seed %d. %s"
        % (bar["margin"], bar["positive_seeds"], len(design["seeds"]), bar["confidence"],
           bar["resamples"], design["bootstrap"], bar["provenance"]),
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
        "## What this record does not license",
        "",
        doc["not_evidence"],
        "",
        doc["decision"],
        "",
    ]
    return "\n".join(lines)


def problems(doc: dict | None = None, page: str | None = None) -> list[str]:
    doc = record() if doc is None else doc
    page = PAGE.read_text(encoding="utf-8") if page is None else page
    found: list[str] = []
    if doc.get("prereg") != "T1-PERSISTENCE-OFF":
        found.append("the preregistration id is not T1-PERSISTENCE-OFF")
    if doc.get("status") != STATUS:
        found.append("status is %r, not %r" % (doc.get("status"), STATUS))
    if doc.get("no_cells_run") is not False:
        found.append("the record does not declare that the cells ran")
    engine = doc.get("engine") or {}
    if engine.get("version") != "0.15.0" or engine.get("cap") != 112:
        found.append("the engine is not the shipped 0.15.0 at cap 112")
    if engine.get("edit") != "none":
        found.append("the record does not declare no engine edit")
    if not ARM.exists():
        found.append("%s does not exist" % ARM.relative_to(ROOT))
    runner = doc.get("runner") or {}
    if runner.get("built") is not True:
        found.append("the record does not claim a built runner")
    if runner.get("cells_run") != 13:
        found.append("the runner claims %r cells, not 13" % (runner.get("cells_run"),))
    if runner.get("module") != ARM.relative_to(ROOT).as_posix():
        found.append("the runner module is not %s" % ARM.relative_to(ROOT))

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

    mechanism = doc.get("mechanism") or {}
    if mechanism.get("arm_class") != "PersistenceOffMemory":
        found.append("the frozen arm class is not PersistenceOffMemory")
    if mechanism.get("implemented") is not True:
        found.append("the record does not declare the arm implemented")

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
    for kind in ("runner-built", "run-completed"):
        if kind not in kinds:
            found.append("the record has no %r amendment" % kind)

    design = doc.get("design") or {}
    seeds = design.get("seeds") or []
    bootstrap = design.get("bootstrap")
    if len(seeds) != 6 or len(set(seeds)) != 6:
        found.append("the design does not hold six distinct seeds")
    if bootstrap in seeds or not isinstance(bootstrap, int):
        found.append("the bootstrap seed is not a distinct integer")
    if design.get("cells") != len(seeds) * len(doc.get("arms") or {}):
        found.append("the cell count is not arms x seeds")
    from benchmarks.presence_cap_experiment import seed_collisions
    collisions = seed_collisions(list(seeds) + [bootstrap],
                                 allow=(RECORD, PAGE, RUN, RESULT_PAGE, AUTH_DOC,
                                        ROOT / "docs" / "persistence_zero_served_diagnostic.json",
                                        ROOT / "docs" / "PERSISTENCE-ZERO-SERVED-NOTE.md",
                                        ROOT / "docs" / "ceiling_diagnostic.json"))
    for seed, paths in collisions.items():
        found.append("seed %d is not fresh: %s" % (seed, ", ".join(paths)))

    table = doc.get("decision_table") or []
    verdicts = {row.get("verdict") for row in table}
    for direction in DIRECTIONS:
        if direction not in verdicts:
            found.append("the %r direction is missing from the decision table" % direction)
    if "VOID" not in verdicts:
        found.append("the decision table has no void row")
    gated = [row for row in table if row.get("verdict") in DIRECTIONS]
    decisions = [row.get("decision") for row in gated]
    if len(set(decisions)) != len(decisions):
        found.append("two directions share one decision, so the table is not two-directional")
    for row in table:
        for key in ("condition", "verdict", "reading", "decision"):
            if not row.get(key):
                found.append("a decision row lacks %s" % key)
    gates = doc.get("gates") or {}
    for gate in GATES:
        if gate not in gates:
            found.append("the gate %s is missing" % gate)
    if "reset" not in " ".join(gates.values()).lower():
        found.append("no gate reads the reset, so the manipulation is not held live")
    try:
        import organica
        from organica.sleep import SleepService
        if SleepService.MAX_PREDICTIONS != 112:
            found.append("the shipped cap is %d, not 112" % SleepService.MAX_PREDICTIONS)
        if getattr(organica, "__version__", None) != "0.15.0":
            found.append("the shipped version is not 0.15.0")
    except Exception as exc:  # pragma: no cover
        found.append("the shipped engine could not be read: %s" % exc)
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
        print("rendered %s" % PAGE.relative_to(ROOT))
        return 0
    found = problems()
    for problem in found:
        print("FAIL:", problem)
    if found:
        return 1
    doc = record()
    print("T1 persistence-off: %s, %d cells, %d seeds, freshness clear, no cell run"
          % (doc["status"], doc["design"]["cells"], len(doc["design"]["seeds"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
