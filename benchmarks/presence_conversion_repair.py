"""PRESENCE-CONVERSION-2: the repaired conversion observer, frozen and unrun.

Q3 (`PRESENCE-CONVERSION-1`) asked where world edges leave the path between raw presence
and final assertion, and returned `OBSERVER NOT NEUTRAL`: its observer lifted
`MAX_PREDICTIONS` for one call and returned the first 40 rows, on the assumption that the
cap is consulted only at the final truncation. It is not. `_build_predictions` spends the
cap as a quota split --- `half_cap = MAX_PREDICTIONS // 2` transitions, then the remaining
budget in count-ranked cooccurrences --- so a lifted cap returns forty entropy-ranked
transitions while the shipped cap returns twenty transitions plus up to twenty
cooccurrences. Measured on that block's own parts (seed 20611501, 89 cycles, 190
candidates per cycle): the lifted top-40 equals the shipped window in **0 of 89** cycles,
mean overlap **0.297**, and **70.8%** of the dynamically admitted edges rank at or below
40 in the lifted order. Presence is unchanged, which is why the failure is confined to the
admission windows, the admitted union, the final assertion and the asserted world edges.

This block repairs the instrument rather than re-reading the failure. The observer returns
the engine's own shipped-cap list **untouched** and makes a second, observation-only call
at the ceiling, so the arm *is* the engine and the pre-cap universe is recorded without
being served. The engine already permits it: `_prediction_frequencies` is documented as
idempotent per cycle ("a second prediction call cannot apply a delta twice"), candidate ids
are content hashes rather than a counter, and `_build_predictions` performs no memory
write. If that is wrong, `N2` fails and the block is `VOID` --- the assumption is tested,
not trusted.

No cell has run and no cell may run: the record is frozen and unauthorised, and no runner
is installed (the repaired observer is the prerequisite). `--check-prereg` validates the
record; `--render-prereg` writes the protocol page; `--dry-run` prints the fourteen planned
commands without executing one; `--measure` refuses.

    ./.venv/bin/python -m benchmarks.presence_conversion_repair --check-prereg
    ./.venv/bin/python -m benchmarks.presence_conversion_repair --render-prereg
    ./.venv/bin/python -m benchmarks.presence_conversion_repair --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks import presence_cap_experiment as cap  # noqa: E402

PREREG = ROOT / "docs" / "presence_conversion_repair_prereg.json"
DOC = ROOT / "docs" / "PRESENCE-CONVERSION-2-PREREGISTRATION.md"
AUTHORISATION_DOC = ROOT / "docs" / "AUTHORISATION-PRESENCE-CONVERSION-2.md"
ARTIFACT = ROOT / "docs" / "presence_conversion_repair_run.json"
#: This block's own pre-run N3 table. It names the twelve design cells, so it is a seed
#: *source* for the block itself and not for any other block; the freshness scan must skip it.
N3_ARTIFACT = ROOT / "docs" / "presence_conversion_2_n3_tables.json"
#: The per-edge record of the 26 asserted-but-never-served edges. It names this block's own
#: seeds, so it is a seed *source* for the block that recorded it; the freshness scan skips it.
UNEXPLAINED_ARTIFACT = ROOT / "docs" / "presence_unexplained_edges.json"
#: The per-edge provenance ledger derived from this block's own cells. It names the six
#: design seeds by definition, so it is a declared seed *source* for this block.
ASSERTION_ARTIFACT = ROOT / "docs" / "assertion_provenance.json"
#: The carrier trace derived from the same six cells. It names the design seeds by
#: definition, so it is a declared seed *source*, not a new block.
CARRIER_ARTIFACT = ROOT / "docs" / "assertion_carrier_trace.json"
#: The one-seed transition-allocation probe. It is a derived diagnostic of this block and
#: deliberately reuses one of its design seeds, so it is a declared seed *source*, not a new
#: block: excluding it would make the freshness scan read the reuse as a collision.
PROBE_ARTIFACT = ROOT / "docs" / "transition_allocation_probe.json"
#: The per-cycle turnover table, derived from this block's own campaign cells. It names the six
#: design seeds by definition, so it too is a declared seed *source* rather than a new block.
TURNOVER_ARTIFACT = ROOT / "docs" / "transition_turnover.json"

PREREG_ID = "PRESENCE-CONVERSION-2"

GATE_NAMES = (
    "N1_served_is_engine",
    "N2_observation_cannot_leak",
    "N3_allocation_recorded",
    "N4_stage_complete",
    "N5_witness_reproduces_audit",
    "N6_seed_axis",
    "N7_determinism",
)

VERDICTS = (
    "VOID",
    "SERVED NOT ENGINE",
    "OBSERVATION LEAKS",
    "CONVERSION STAGE MEASURED",
)

RUN = "FROZEN, RUN"
NOT_RUN = "FROZEN, NOT RUN"


def prereg() -> dict:
    return json.loads(PREREG.read_text(encoding="utf-8"))


def authorisation_problems(body: dict | None = None, doc: Path | None = None) -> list[str]:
    """A grant is accepted only when a dated document carries the owner's words."""
    doc = AUTHORISATION_DOC if doc is None else Path(doc)
    body = body or prereg()
    auth = body.get("authorisation") or {}
    granted = auth.get("granted")
    if granted is False:
        return []
    if granted is not True:
        return ["authorisation.granted is neither true nor false"]
    problems = []
    for field in ("granted_on", "document", "quote"):
        if not auth.get(field):
            problems.append("granted without `authorisation.%s`" % field)
    if problems:
        return problems
    expected = "docs/" + doc.name
    if auth["document"] != expected:
        problems.append("the record names %r, not %r" % (auth["document"], expected))
    if not doc.exists():
        problems.append("the authorisation document %s does not exist" % expected)
        return problems
    text = doc.read_text(encoding="utf-8")
    if auth["quote"] not in text:
        problems.append("the recorded quote does not appear in %s" % expected)
    if "REQUESTED — NOT GRANTED" in text:
        problems.append("%s still says REQUESTED — NOT GRANTED" % expected)
    return problems


def validate(body: dict | None = None) -> list[str]:
    """Everything wrong with the frozen record, as a list of sentences."""
    body = prereg() if body is None else body
    found: list[str] = []

    if body.get("prereg") != PREREG_ID:
        found.append("the record names %r, not %r" % (body.get("prereg"), PREREG_ID))
    status = body.get("status")
    if status not in (NOT_RUN, RUN):
        found.append("unknown status %r" % (status,))
        return found
    ran = status == RUN
    if ran == bool(body.get("no_cells_run")):
        found.append("`no_cells_run` disagrees with status %r" % (status,))
    if not body.get("frozen_on"):
        found.append("the record carries no freeze date")

    design = body.get("design") or {}
    seeds = list(design.get("seeds") or [])
    if design.get("arms") != ["off", "on"]:
        found.append("the arms are %r, not ['off', 'on']" % (design.get("arms"),))
    if len(seeds) != 6:
        found.append("the seed block holds %d seeds, not 6" % len(seeds))
    if not isinstance(design.get("bootstrap"), int):
        found.append("the bootstrap seed is not an integer")
    if design.get("cycles") != 120:
        found.append("the block does not fix 120 cycles")
    if design.get("cells") != 12:
        found.append("the block does not fix 12 design cells")
    if "result" in body and not ran:
        found.append("an unrun record carries a result block")

    allow = [PREREG, DOC, N3_ARTIFACT, UNEXPLAINED_ARTIFACT, ASSERTION_ARTIFACT,
             CARRIER_ARTIFACT, PROBE_ARTIFACT, TURNOVER_ARTIFACT,
             ROOT / "docs/presence_band_rank_prereg.json",
             ROOT / "docs/PRESENCE-BAND-RANK-PREREGISTRATION.md",
             ROOT / "docs/presence_band_rank_run.json",
             ROOT / "docs/PRESENCE-BAND-RANK-RESULT.md",
             ROOT / "docs/AUTHORISATION-PRESENCE-BAND-1.md",
             ROOT / "docs/presence_band_rank_2_prereg.json",
             ROOT / "docs/PRESENCE-BAND-RANK-2-PREREGISTRATION.md"]
    result = body.get("result") or {}
    if ran and result.get("artifact"):
        allow.append(ROOT / result["artifact"])
    collisions = cap.seed_collisions(seeds + [design.get("bootstrap")], allow=tuple(allow))
    if collisions:
        found.append("the seed block is not fresh: %r" % (collisions,))

    gates = body.get("gates") or {}
    if tuple(gates) != GATE_NAMES:
        found.append("the gates are %r, not %r" % (tuple(gates), GATE_NAMES))

    table = body.get("decision_table") or []
    verdicts = {row.get("verdict") for row in table}
    if verdicts != set(VERDICTS):
        found.append("the decision table's verdicts are %r, not %r"
                     % (sorted(verdicts), sorted(VERDICTS)))
    for row in table:
        for field in ("condition", "verdict", "reading", "decision"):
            if not row.get(field):
                found.append("a decision row has no `%s`" % field)

    engine = body.get("engine") or {}
    if engine.get("edit") != "none":
        found.append("the block edits the engine")
    observer = body.get("observer") or {}
    served = observer.get("served") or ""
    if "untouched" not in served:
        found.append("the observer does not say the engine's own list is returned untouched")
    ceiling = observer.get("ceiling")
    shipped = observer.get("shipped_cap")
    if not isinstance(ceiling, int) or not isinstance(shipped, int) or ceiling <= shipped:
        found.append("the observer's ceiling does not exceed the shipped cap")

    found.extend(authorisation_problems(body))

    if not ran and ARTIFACT.exists():
        found.append("an unrun record has a result artifact at %s"
                     % ARTIFACT.relative_to(ROOT).as_posix())
    return found


def _cell_state(body: dict) -> str:
    """What is true of the cells, as opposed to what is permitted."""
    auth = body.get("authorisation") or {}
    if body.get("status") == RUN:
        return "The campaign has run."
    if auth.get("granted"):
        return "The grant is recorded; no runner is installed and no cell has run."
    return "No cell has run and none may run."


def render_prereg(body: dict) -> str:
    """The protocol page, rendered from the record rather than typed."""
    design = body["design"]
    engine = body["engine"]
    observer = body["observer"]
    lines = [
        "# %s — the repaired conversion observer, frozen" % body["prereg"],
        "",
        "**Status: %s. %s** Frozen %s; the record is"
        % (body["status"], _cell_state(body), body["frozen_on"]),
        "`docs/%s` and this page is rendered from it. Authorisation: %s."
        % (PREREG.name, "requested, not granted" if not body["authorisation"].get("granted")
           else "granted " + str(body["authorisation"].get("granted_on"))),
        "",
        "## 1. Why this block exists",
        "",
        body["program"]["relationship"],
        "",
        "## 2. The question",
        "",
        body["question"],
        "",
        "**Hypothesis.** " + body["hypothesis"]["statement"],
        "",
        "**Prediction.** " + body["hypothesis"]["prediction"],
        "",
        "**Falsifier.** " + body["hypothesis"]["falsifier"],
        "",
        "## 3. The repair",
        "",
        engine["mechanism"],
        "",
        "- served: " + observer["served"],
        "- observed: " + observer["observed"],
        "- ceiling `%d`, shipped cap `%d`." % (observer["ceiling"], observer["shipped_cap"]),
        "",
        "## 4. Design",
        "",
        "| | |",
        "|---|---|",
        "| Arms | %s |" % " / ".join(design["arms"]),
        "| Seeds | %s (bootstrap %s) |" % (", ".join(str(s) for s in design["seeds"]),
                                           design["bootstrap"]),
        "| Cycles | %d |" % design["cycles"],
        "| Design cells | %d |" % design["cells"],
        "| Witness cell | seed %s |" % design["witness_cell"]["seed"],
        "",
        "## 5. Gates",
        "",
    ]
    for name, text in body["gates"].items():
        lines += ["**`%s`** — %s" % (name, text), ""]
    lines += ["## 6. Decision table", "", "| Condition | Verdict | Reading | Decision |", "|---|---|---|---|"]
    for row in body["decision_table"]:
        lines.append("| %s | `%s` | %s | %s |"
                     % (row["condition"], row["verdict"], row["reading"], row["decision"]))
    lines += [
        "",
        "## 7. What this block does not license",
        "",
        body["not_evidence"],
        "",
        "## 8. Stop condition",
        "",
        body["stop_condition"],
        "",
        "## 9. Runner",
        "",
        body["runner"]["why"],
        "",
    ]
    return "\n".join(lines)


def check_prereg(body: dict | None = None) -> int:
    body = prereg() if body is None else body
    problems = validate(body)
    if DOC.exists():
        fresh = render_prereg(body)
        if DOC.read_text(encoding="utf-8") != fresh:
            problems.append("the protocol page is stale; run --render-prereg")
    else:
        problems.append("the protocol page %s does not exist" % DOC.name)
    if problems:
        for problem in problems:
            print("FAIL:", problem)
        return 1
    auth = body["authorisation"]
    print("prereg %s: %s, %s, page current"
          % (body["prereg"], body["status"].lower(),
             "authorised " + str(auth.get("granted_on")) if auth.get("granted") else "unauthorised"))
    return 0


def planned_commands() -> list[str]:
    """The fourteen runs the block would execute, as commands. Nothing is run."""
    body = prereg()
    design = body["design"]
    commands = []
    for seed in design["seeds"]:
        for arm in design["arms"]:
            commands.append("python -m benchmarks.presence_conversion_repair --cell %d %s"
                            % (seed, arm))
    commands.append("python -m benchmarks.presence_conversion_repair --cell %d off-witness"
                    % design["witness_cell"]["seed"])
    commands.append("python -m benchmarks.presence_conversion_repair --cell %d on-rerun"
                    % design["seeds"][0])
    return commands


def refuse() -> None:
    """`--measure` refuses: unauthorised blocks cannot run, and this one has no runner."""
    body = prereg()
    if not (body.get("authorisation") or {}).get("granted"):
        raise SystemExit("%s is not authorised: no cell may run; record a dated grant first"
                         % PREREG_ID)
    raise SystemExit("%s is authorised but has no runner: no harness executes the fourteen "
                     "runs or adjudicates N1-N7 (see runner.why)" % PREREG_ID)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-prereg", action="store_true",
                        help="validate the frozen record and the rendered page without writing")
    parser.add_argument("--render-prereg", action="store_true",
                        help="write the protocol page from the record")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the planned commands without running one")
    parser.add_argument("--measure", action="store_true",
                        help="refuse: the block is unauthorised and has no runner")
    args = parser.parse_args(argv)

    if args.check_prereg:
        return check_prereg()
    if args.render_prereg:
        DOC.write_text(render_prereg(prereg()), encoding="utf-8")
        print("wrote", DOC.relative_to(ROOT).as_posix())
        return 0
    if args.dry_run:
        for command in planned_commands():
            print(command)
        return 0
    if args.measure:
        refuse()
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
