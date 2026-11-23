"""PRESENCE-CONVERSION-1: the Q3 conversion observer, frozen and unrun.

Q3 asks where world edges are lost between raw presence and final assertion. The three
stages the draft program could not observe — `C` (candidates constructed before the cap),
`E` (why a present edge did not become a candidate) and `R` (the rank each candidate
carried) — are observed by a benchmark-only subclass that calls the engine's own
`_build_predictions` with the cap lifted to a diagnostic ceiling and returns the engine's
own first `MAX_PREDICTIONS` rows unchanged.

The behaviour-neutrality control is the point of the record: for every seed the
observer-off and observer-on arms must produce identical stage fingerprints and identical
ordered admission windows. If the engine consults `MAX_PREDICTIONS` anywhere but the final
truncation, the arms diverge and Q3 is `OBSERVER NOT NEUTRAL`. The check is built to fail,
and a test proves it fires on a dropped or reordered window.

No cell has run. The record is frozen, authorised and unrun: `--measure` refuses, and
`organica/` is not edited.

    ./.venv/bin/python -m benchmarks.presence_conversion_observer --render-prereg
    ./.venv/bin/python -m benchmarks.presence_conversion_observer --check-prereg
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import organica                                                             # noqa: E402
from benchmarks import build_supersession as supersession                   # noqa: E402
from benchmarks import engine_lineage, engine_stamp                                         # noqa: E402
from benchmarks import audit_row_witness as witness_rows                  # noqa: E402
from benchmarks import presence_cap_experiment as cap                       # noqa: E402
from benchmarks.acquisition_compositional import (                          # noqa: E402
    PHASE_ACQUISITION,
    generate_compositional_world,
)
from benchmarks.acquisition_harness import (                                # noqa: E402
    SHORT_CYCLES,
    _CountingMemoryService,
    _make_scratch_db,
)
from benchmarks.acquisition_runner import (                                 # noqa: E402
    EVENTS_PER_CYCLE,
    _world_compositional_edges,
    structure_edges,
)
from organica.sleep import SleepService                                     # noqa: E402

PREREG = ROOT / "docs" / "presence_conversion_observer_prereg.json"
DOC = ROOT / "docs" / "PRESENCE-CONVERSION-OBSERVER-PREREGISTRATION.md"
ARTIFACT = ROOT / "docs" / "presence_conversion_observer_run.json"
# The block's own result file, never "another artifact" for the freshness scan. Held separately
# from ARTIFACT so a test that redirects the output path cannot make the block collide with itself.
OWN_RUN_ARTIFACT = ARTIFACT
RESULT = ROOT / "docs" / "PRESENCE-CONVERSION-OBSERVER-RESULT.md"
AUTHORISATION_DOC = ROOT / "docs" / "AUTHORISATION-PRESENCE-CONVERSION-1.md"
AUDIT = ROOT / "docs" / "presence_assertion_audit_0.14.0.json"
LADDER = ROOT / "docs" / "presence_assertion_ladder_0.14.0.json"
PARTS = ROOT / ".scratch" / "presence_conversion" / "parts"

KIND = "presence_conversion_observer_run"
CELL_KIND = "presence_conversion_cell"
CEILING = 10 ** 9
VERDICTS = ("CONVERSION OBSERVED", "PARTIAL OBSERVATION", "OBSERVER NOT NEUTRAL", "VOID")
STAGES = ("W", "P", "C", "E", "R", "S_cycle", "S_ever", "A", "A_W", "A_pred", "A_other")
#: The retained chain, in order. `E` and `R` are recorded per edge but are not retention
#: steps in this engine: construction already applies the eligibility filters, and a rank is
#: an ordering, not a subset. `S_cycle` and `S_ever` are window statistics, with `S_ever` a
#: union rather than a retention step.
CHAIN = ("W", "P", "C", "S_cycle", "S_ever", "A_pred")


class StageObserverSleepService(SleepService):
    """The shipped engine with the cap lifted for one call and the engine's own window returned.

    The only method replaced is `_build_predictions`. It calls the engine's own method with
    `MAX_PREDICTIONS` temporarily at the diagnostic ceiling, records the full pre-cap list,
    restores the shipped cap, and returns the engine's own first `cap` rows. Neutrality is not
    assumed: an observer-off arm runs on the same seed and the two are compared.
    """

    def __init__(self, memory, record: bool = True):
        super().__init__(memory)
        self.record = bool(record)
        self.windows: list[list[tuple[str, str]]] = []
        self.candidates: list[list[dict]] = []

    def _build_predictions(self, temporal, freqs, prior_schemas=None):
        shipped = self.MAX_PREDICTIONS
        self.MAX_PREDICTIONS = CEILING
        try:
            full = super()._build_predictions(temporal, freqs, prior_schemas)
        finally:
            self.MAX_PREDICTIONS = shipped
        if self.record:
            self.candidates.append(record_window(full, shipped))
            self.windows.append([(cand.source, cand.target) for cand in full[:shipped]])
        return full[:shipped]


def prereg() -> dict:
    return json.loads(PREREG.read_text(encoding="utf-8"))


def authorisation_problems(body: dict | None = None, doc: Path | None = None) -> list[str]:
    """A grant is accepted only when a dated document carries the owner's words.

    `granted: false` is the frozen state and is never a problem. A `true` grant is the owner's
    decision, recorded by amending the record; the check is that the amendment names the
    authorisation document, that the document exists, that the quoted words appear in it, and
    that the document no longer says the block is unauthorised. A field flipped without a
    signature fails the gate instead of passing as an authorisation.
    """
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


def derived() -> dict:
    """The prior facts this record quotes, read from the committed artifacts at check time."""
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    ladder = json.loads(LADDER.read_text(encoding="utf-8"))
    buckets = {key: sum(row["buckets"][key] for row in ladder["rows"])
               for key in ("not_offered", "offered_not_admitted", "admitted_not_asserted")}
    buckets["misses_total"] = sum(buckets.values())
    witness = audit["rows"][0]
    return {
        "witness": witness,
        "buckets": buckets,
        "shipped_cap": SleepService.MAX_PREDICTIONS,
        "engine_version": getattr(organica, "__version__", ""),
    }


def observer_overrides(cls=StageObserverSleepService) -> list[str]:
    """The names the observer class defines itself, excluding dunders."""
    names = set()
    for klass in cls.__mro__:
        if klass is SleepService or klass is object:
            break
        for name, value in vars(klass).items():
            if not name.startswith("__") and callable(value):
                names.add(name)
    return sorted(names)


def record_window(candidates, cap: int) -> list[dict]:
    """One row per constructed candidate, before the cap is applied."""
    rows = []
    for rank, cand in enumerate(candidates, start=1):
        evidence = cand.evidence or {}
        rows.append({
            "rank": rank,
            "edge": [cand.source, cand.target],
            "strength": float(getattr(cand, "strength", 0.0)),
            "admitted": rank <= cap,
            "support": evidence.get("count"),
            "ratio": evidence.get("ratio"),
        })
    return rows


def eligibility(present_edges, rows, temporal, min_count: int) -> dict:
    """`E`: why each present world edge did or did not become a candidate.

    Construction applies the eligibility filters, so in this engine `E` is a reason record,
    not a separate retention count. An edge that meets the minimum count but has no candidate
    is `unexplained` and fails X2 rather than being smoothed away.
    """
    constructed = {tuple(sorted(row["edge"])) for row in rows}
    out = {}
    for edge in present_edges:
        key = tuple(sorted(edge))
        if key in constructed:
            out["%s->%s" % (edge[0], edge[1])] = "constructed"
            continue
        count = (temporal.get(edge[0]) or {}).get(edge[1], 0)
        out["%s->%s" % (edge[0], edge[1])] = (
            "below_prediction_min_count" if count < min_count else "unexplained"
        )
    return out


def neutrality(off: dict, observed: dict) -> dict:
    """The behaviour-neutrality control: observer-off and observer-on must match exactly.

    Ordering counts. A set comparison would accept a reordered admission window, and a
    reordered window is a changed engine, not a recorded one.
    """
    checks = [
        ("presence fingerprint", off.get("present_fingerprint"),
         observed.get("present_fingerprint")),
        ("admission windows",
         [list(map(tuple, window)) for window in off.get("windows", [])],
         [list(map(tuple, window)) for window in observed.get("windows", [])]),
        ("admitted union", off.get("s_ever_fingerprint"), observed.get("s_ever_fingerprint")),
        ("final assertion", off.get("asserted_fingerprint"),
         observed.get("asserted_fingerprint")),
        ("asserted world edges", off.get("asserted_world_fingerprint"),
         observed.get("asserted_world_fingerprint")),
    ]
    differs = [name for name, a, b in checks if a != b]
    return {
        "neutral": not differs,
        "differs": differs,
        "rule": ("identical presence, identical ordered admission windows, identical admitted "
                 "union and identical final assertion"),
    }


def loss_chain(counts: dict, bypass: int = 0) -> dict:
    """The declared loss rule over the observed chain, with ties to the earlier stage.

    A zero denominator is not measurable and is excluded, never reported as 0.0. A negative
    drop is a gain (the admitted union can exceed one cycle's window) and is reported, not
    clamped. A bypass is an asserted edge that never passed admission: it is counted
    separately and enters neither retention nor loss.
    """
    drops: dict[str, int] = {}
    shares: dict[str, float] = {}
    gains: list[str] = []
    not_measurable: list[str] = []
    for earlier, later in zip(CHAIN, CHAIN[1:]):
        step = "%s->%s" % (earlier, later)
        before, after = counts.get(earlier), counts.get(later)
        if before is None or after is None or before == 0:
            not_measurable.append(step)
            continue
        drop = before - after
        drops[step] = drop
        shares[step] = round(drop / before, 6)
        if drop < 0:
            gains.append(step)
    suspect = None
    measurable = {step: drop for step, drop in drops.items() if step not in gains}
    if measurable:
        largest = max(measurable.values())
        if largest > 0:
            suspect = next(step for step in measurable if measurable[step] == largest)
    return {
        "retained": {stage: counts.get(stage) for stage in CHAIN},
        "absolute_drop": drops,
        "loss_share": shares,
        "gains": gains,
        "not_measurable": not_measurable,
        "bypass": int(bypass),
        "primary_suspect": suspect,
    }


def seed_fresh() -> dict:
    """The design seeds and the bootstrap must not appear in any other docs artifact.

    The witness is the audit's own seed and is a control, not a reading cell, so it is excluded.
    """
    body = prereg()
    design = body["design"]
    seeds = list(design["seeds"]) + [design["bootstrap"]]
    allow = (PREREG, OWN_RUN_ARTIFACT)
    artifact = (body.get("result") or {}).get("artifact")
    if artifact:
        allow += (ROOT / artifact,)
    return cap.seed_collisions(seeds, allow=allow)


def validate(body: dict | None = None) -> list[str]:
    found: list[str] = []
    body = body or prereg()
    facts = derived()
    if body.get("prereg") != "PRESENCE-CONVERSION-1":
        found.append("the record is not PRESENCE-CONVERSION-1")
    if body.get("status") not in ("FROZEN, NOT RUN", "FROZEN, RUN"):
        found.append("the record is not frozen")
    ran = body.get("status") == "FROZEN, RUN"
    if body.get("no_cells_run") is not (not ran):
        found.append("the record's status and its no_cells_run flag disagree")
    result = body.get("result") or {}
    if ran:
        artifact = result.get("artifact")
        if not artifact or not (ROOT / artifact).exists():
            found.append("the record claims a run but its result artifact is missing")
    elif result:
        found.append("an unrun record carries a result block")
    found.extend(authorisation_problems(body))

    engine = body.get("engine", {})
    if (engine.get("version") != facts["engine_version"]
            and not supersession.matches(body, "version", engine.get("version"))):
        found.append("the record names %r, not the installed build %r, and is not the build its "
                     "supersession disclosure names"
                     % (engine.get("version"), facts["engine_version"]))
    if engine.get("edit") != "none":
        found.append("the record does not state that no engine file changes")
    overrides = observer_overrides()
    if overrides != ["_build_predictions"] or engine.get("overrides") != overrides:
        found.append("the observer defines %r, not `_build_predictions` alone" % (overrides,))

    observer = body.get("observer", {})
    if observer.get("ceiling") != CEILING:
        found.append("the diagnostic ceiling is not the declared %r" % (CEILING,))
    if observer.get("shipped_cap") != facts["shipped_cap"] and not supersession.matches(
            body, "cap", observer.get("shipped_cap")):
        found.append("the shipped cap is not the cap this record recorded, and the record does "
                     "not disclose the recorded build")
    found += supersession.problems(body, facts["engine_version"], facts["shipped_cap"])
    for stage in ("C", "E", "R"):
        if not observer.get("records", {}).get(stage):
            found.append("the observer does not say what it records for %s" % stage)

    design = body.get("design", {})
    seeds = list(design.get("seeds", []))
    if len(seeds) != 6 or len(set(seeds)) != 6:
        found.append("the seed block is not six distinct seeds")
    if design.get("bootstrap") in seeds:
        found.append("the bootstrap seed is also a world seed")
    if design.get("arms") != ["off", "on"]:
        found.append("the design is not the observer-off and observer-on pair")
    if design.get("cells") != len(seeds) * len(design.get("arms", [])):
        found.append("the cell count is not arms times seeds")
    if design.get("cycles") != SHORT_CYCLES:
        found.append("the cycle count is not the audit's acquisition block")
    if design.get("witness_cell", {}).get("seed") != facts["witness"]["seed"]:
        found.append("the witness cell is not the published audit's first seed")
    if seed_fresh():
        found.append("the design seeds are not fresh: %r" % (seed_fresh(),))

    stages = body.get("stages", {})
    for stage in STAGES:
        if not stages.get(stage):
            found.append("the stage %s is not defined" % stage)
    gates = body.get("gates", {})
    for gate in ("X1_observer_neutral", "X2_stage_complete", "X3_no_unobserved_imputation",
                 "X4_same_object", "X5_witnesses", "X6_seed_axis", "X7_determinism",
                 "X8_control_reproduces_audit"):
        if not gates.get(gate):
            found.append("the record has no %s" % gate)
    if not body.get("loss", {}).get("rule"):
        found.append("the record declares no loss rule")
    if body.get("loss", {}).get("chain") != list(CHAIN):
        found.append("the declared chain is not the observed retention chain")
    verdicts = {row.get("verdict") for row in body.get("decision_table", [])}
    if verdicts != set(VERDICTS):
        found.append("the decision table cannot reach exactly %r" % (sorted(VERDICTS),))
    if not all(row.get("decision") and row.get("licenses")
               for row in body.get("decision_table", [])):
        found.append("a decision_table row names no decision or no licence")
    adoption = body.get("adoption", {})
    if not adoption.get("rule") or not adoption.get("withdrawal"):
        found.append("the record has no adoption rule or no withdrawal rule")
    if not adoption.get("not_authorised"):
        found.append("the record does not say what it does not authorise")
    if not body.get("stop_condition"):
        found.append("the record has no stop condition")
    if not body.get("not_evidence"):
        found.append("the record has no statement of what it does not claim")
    return found


def render_prereg(body: dict) -> str:
    facts = derived()
    witness = facts["witness"]
    buckets = facts["buckets"]
    design = body["design"]
    engine = body["engine"]
    observer = body["observer"]
    auth = body.get("authorisation") or {}
    result = body.get("result") or {}
    if result:
        status_line = (
            "**Status: %s. Authorised %s and run.** The verdict is `%s`; the artifact is `%s` "
            "and the result page is `%s`."
            % (body["status"], auth.get("granted_on", "on an unrecorded date"),
               result.get("verdict", ""), result.get("artifact", ""), result.get("page", "")))
    elif auth.get("granted"):
        status_line = (
            "**Status: %s. Authorised %s.** The grant is recorded in `%s` and quoted there; "
            "it authorises the cells and nothing else."
            % (body["status"], auth.get("granted_on", "on an unrecorded date"),
               auth.get("document", "")))
    else:
        status_line = ("**Status: %s. Not authorised.** No cell has run. This record fixes the "
                       "protocol; it does not licence a run." % body["status"])
    lines = [
        "# Presence to assertion: the conversion observer (PRESENCE-CONVERSION-1)",
        "",
        "Generated from `docs/presence_conversion_observer_prereg.json` by "
        "`python -m benchmarks.presence_conversion_observer --render-prereg`. "
        "Do not edit by hand.",
        "",
        status_line,
        "",
        "Question 3 of the conversion program "
        "(`docs/PRESENCE-ASSERTION-CONVERSION-PREREGISTRATION.md`), frozen on its own so the "
        "three internal stages can be observed without waiting for Q1 or for the Q2 cap block. "
        "It uses Q3's stage chain and loss rule without renaming them, keeps X1-X7, and adds X8: "
        "an observer-off control on the same seeds that must reproduce the published audit row, "
        "because an observer that changes behaviour is not an observer.",
        "",
        "## The question",
        "",
        body["question"],
        "",
        "## The hypothesis, stated before any cell",
        "",
        body["hypothesis"]["statement"],
        "",
        "**Prediction.** " + body["hypothesis"]["prediction"],
        "",
        "**Falsifier.** " + body["hypothesis"]["falsifier"],
        "",
        "**Alternative.** " + body["hypothesis"]["alternative"],
        "",
        "## Why the two earlier blocks cannot answer this",
        "",
        "| Block | Artifact | Reading | Why it does not answer Q3 |",
        "| --- | --- | --- | --- |",
        "| same-build presence/assertion audit | `docs/presence_assertion_audit_0.14.0.json` | "
        "%d of %d world edges present, %d asserted on the witness seed at the shipped cap | "
        "it counts the endpoints only; nothing between presence and assertion is observed |"
        % (witness["present_world_edges"], witness["world_edges"],
           witness["asserted_world_edges"]),
        "| presence-to-assertion ladder trace (exploratory) | "
        "`docs/presence_assertion_ladder_0.14.0.json` | "
        "%d misses: %d never offered, %d offered and not admitted, %d admitted and not asserted | "
        "its offered arm raises the cap in a recording subclass, so it is a counterfactual, not "
        "an observation of the shipped run; `C`, `E` and `R` are not recorded |"
        % (buckets["misses_total"], buckets["not_offered"],
           buckets["offered_not_admitted"], buckets["admitted_not_asserted"]),
        "| cap-only preregistration | `docs/presence_cap_prereg.json` | freezes one changed "
        "constant with no observer inside construction | it cannot see which candidates the cap "
        "truncated or what order they carried |",
        "",
        "## The observer, and the one method it replaces",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Engine | %s |" % engine["version"],
        "| Engine edit | **none** |",
        "| Observer | `%s` |" % engine["observer"],
        "| Base class | `%s` |" % engine["base"],
        "| Overrides | `_build_predictions` |",
        "| Mechanism | %s |" % engine["mechanism"],
        "| Why it can fail | %s |" % engine["why_it_can_fail"],
        "",
        "The observer calls the engine's own method with `MAX_PREDICTIONS` at the diagnostic "
        "ceiling of %d, records the full candidate list, restores the shipped cap of %d and "
        "returns the engine's own first %d rows. It reimplements no construction, ranking or "
        "filtering. Neutrality is the identity `engine(cap=40) == observer(cap=40)`, and it is "
        "checked on every seed rather than assumed from reading the code."
        % (observer["ceiling"], observer["shipped_cap"], observer["shipped_cap"]),
        "",
        "## What C, E and R are",
        "",
        "| Stage | Symbol | Definition | Recorded as |",
        "| --- | --- | --- | --- |",
        "| Candidate | `C` | candidates constructed before the cap | one row per candidate: edge, "
        "rank, strength, support, ratio, admitted |",
        "| Eligible | `E` | why a present edge did or did not become a candidate | one outcome "
        "per present world edge: `constructed`, `below_prediction_min_count`, or `unexplained` |",
        "| Scored | `R` | the order the engine gave each candidate | the row's rank in the "
        "pre-cap list, with its strength and support |",
        "",
        "**An identity this engine makes.** Construction already applies the eligibility "
        "filters, so `C` and `E` hold the same edges: `E` is the reason record, not a separate "
        "retention step, and reporting it as one would invent a stage. A later engine that "
        "separates construction from eligibility gains a step; this record would then be "
        "re-registered rather than re-read.",
        "",
        "## The design",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Arms | observer off (shipped `SleepService`), observer on "
        "(`StageObserverSleepService`) |",
        "| Seeds | %s |" % ", ".join(str(seed) for seed in design["seeds"]),
        "| Bootstrap | %s |" % design["bootstrap"],
        "| Cycles | %d |" % design["cycles"],
        "| Cells | %d (%d arms x %d seeds) |"
        % (design["cells"], len(design["arms"]), len(design["seeds"])),
        "| Witness cell | seed %d, observer off; it must reproduce the published audit row |"
        % design["witness_cell"]["seed"],
        "| Pairing | same seed, same world, same cap; only the observer differs |",
        "| World | the Gate-13 compositional world, warmup and acquisition as in the audit |",
        "",
        "**Freshness.** %s" % design["freshness"],
        "",
        "## The behaviour-neutrality control",
        "",
        "For each seed the two arms must produce identical presence, identical ordered admission "
        "windows, identical admitted union and identical final assertion. The comparison is "
        "ordered: a set comparison would pass a reordered window, and a reordered window is a "
        "changed engine. `X1` fails on the first difference and the verdict is `OBSERVER NOT "
        "NEUTRAL` — the block is void, no stage reading is made, and the instrument is fixed in "
        "a new block.",
        "",
        "## Gates",
        "",
        "| Gate | Requirement |",
        "| --- | --- |",
    ]
    for gate, text in body["gates"].items():
        lines.append("| `%s` | %s |" % (gate, text))
    lines += [
        "",
        "## The loss rule",
        "",
        body["loss"]["rule"],
        "",
        "Retained chain: `%s`." % " -> ".join(body["loss"]["chain"]),
        "",
        "Ties go to the earlier stage. Relative shares are reported beside the absolute drop and "
        "never name a suspect on their own. A stage with a zero denominator is not measurable "
        "and is excluded, never reported as `0.0`. An asserted edge that never passed admission "
        "is a bypass: reported separately, counted neither as retention nor as loss.",
        "",
        "## The decision table",
        "",
    ]
    for row in body["decision_table"]:
        lines += [
            "- **%s** -> **%s**." % (row["condition"], row["verdict"]),
            "  - Decision: %s" % row["decision"],
            "  - Licences: %s" % row["licenses"],
        ]
    lines += [
        "",
        "## Adoption, withdrawal and stop",
        "",
        body["adoption"]["rule"],
        "",
        "**Withdrawal.** " + body["adoption"]["withdrawal"],
        "",
        "**Not authorised by this record.** " + "; ".join(body["adoption"]["not_authorised"]),
        "",
        "**Stop condition.** " + body["stop_condition"],
        "",
        "## Cost and authorisation",
        "",
        "%d cells, %d cycles each, two arms. %s"
        % (design["cells"], design["cycles"],
           ("The block has been run; the verdict is `%s`." % result.get("verdict", "")
            if result else
            ("The block is authorised; no cell has run." if auth.get("granted") else
             "No cell is authorised: the runner refuses `--measure` while "
             "`authorisation.granted` is false."))),
        "",
        "**Authorisation.** " + body["authorisation"]["note"],
        "",
        "## What this does not claim",
        "",
        body["not_evidence"],
        "",
    ]
    return "\n".join(lines)


def check_prereg(body: dict | None = None) -> int:
    body = body or prereg()
    problems = validate(body)
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    if not DOC.exists():
        raise SystemExit("FAIL: %s does not exist" % DOC.name)
    if DOC.read_text(encoding="utf-8") != render_prereg(body):
        raise SystemExit("FAIL: the preregistration page is stale; rerun with --render-prereg")
    auth = body.get("authorisation") or {}
    state = ("authorised %s" % auth.get("granted_on", "on an unrecorded date")
             if auth.get("granted") else "unauthorised")
    print("prereg %s: %s, %s, page current" % (body["prereg"], body["status"].lower(), state))
    return 0


# --------------------------------------------------------------------------- runner

ACQ_SOURCE = "env_acq"


def _fingerprint(text: str) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()[:16]


def _part_path(seed: int, arm: str, suffix: str = "") -> Path:
    return PARTS / ("%s_%s%s.json" % (seed, arm, suffix))


def _load_part(seed: int, arm: str, suffix: str = "") -> dict:
    path = _part_path(seed, arm, suffix)
    if not path.exists():
        raise SystemExit("missing part %s; run --measure" % path.name)
    return json.loads(path.read_text(encoding="utf-8"))


def run_cell(seed: int, arm: str, cycles: int | None = None) -> dict:
    """One acquisition run on one arm; returns the cell record, not a reading.

    The observer is the only difference between the arms: `off` is the shipped `SleepService`,
    `on` is the subclass that replaces `_build_predictions` alone. Everything else --- world,
    seeds, cycles, cap --- is held fixed, which is what makes X1 an identity rather than a
    comparison of two designs.
    """
    body = prereg()
    if arm not in body["design"]["arms"]:
        raise SystemExit("unknown arm %r" % (arm,))
    cycles = int(body["design"]["cycles"] if cycles is None else cycles)
    world = generate_compositional_world(seed=seed, cycles=cycles)
    events_text, trainable = world["events"], world["trainable"]
    world_edges = _world_compositional_edges(world)

    db_path = _make_scratch_db("presence_conversion")
    mem = _CountingMemoryService(str(db_path))
    svc = StageObserverSleepService(mem) if arm == "on" else SleepService(mem)
    acq_lo, acq_hi = PHASE_ACQUISITION
    event_lo, event_hi = acq_lo * EVENTS_PER_CYCLE, acq_hi * EVENTS_PER_CYCLE
    windows: list[list[tuple[str, str]]] = []
    try:
        for i, (text, train_flag) in enumerate(zip(events_text, trainable)):
            in_acq = event_lo <= i < event_hi
            if in_acq and not train_flag:
                continue
            if i % EVENTS_PER_CYCLE == 0:
                mem.current_cycle = i // EVENTS_PER_CYCLE
            mem.store(text, event_type="observe", source=ACQ_SOURCE if in_acq else "env")
            if (i + 1) % EVENTS_PER_CYCLE == 0:
                report = svc.run_sleep_cycle()
                windows.append([(p.source, p.target) for p in report.predictions])
        asserted = {(a, b) for a, targets in structure_edges(svc._load_prior_candidates()).items()
                    for b in targets}
        temporal = [(a, b, count) for a, b, count in mem.temporal_edges(min_count=1)]
    finally:
        mem.close()
        try:
            db_path.unlink(missing_ok=True)
        except OSError:
            pass

    by_source: dict[str, dict[str, int]] = {}
    for a, b, count in temporal:
        by_source.setdefault(a, {})[b] = count
    present = world_edges & {(a, b) for a, b, _c in temporal}
    admitted = {edge for window in windows for edge in window}
    world_admitted = world_edges & admitted
    world_asserted = world_edges & asserted
    rows = [row for cycle in getattr(svc, "candidates", []) for row in cycle]
    constructed = {(row["edge"][0], row["edge"][1]) for row in rows}
    world_constructed = world_edges & constructed
    reasons = eligibility(sorted(present), rows, by_source, SleepService.PREDICTION_MIN_COUNT)
    unexplained = sorted(key for key, reason in reasons.items() if reason == "unexplained")
    window_world = [len(world_edges & set(window)) for window in windows]

    cell = {
        "kind": CELL_KIND,
        "seed": seed,
        "arm": arm,
        "cycles": len(windows),
        "engine_version": engine_stamp.engine_version(),
        "engine_sha256": engine_stamp.engine_sha256(),
        "world_edges": len(world_edges),
        "world_digest": _fingerprint(sorted(world_edges)),
        "present_world_edges": len(present),
        "present_fingerprint": cap._digest(present),
        "windows": windows,
        "s_cycle_world_edges": window_world,
        "s_cycle_max": max(window_world) if window_world else 0,
        "s_ever_world_edges": len(world_admitted),
        "s_ever_fingerprint": cap._digest(world_admitted),
        "asserted_world_edges": len(world_asserted),
        "asserted_world_fingerprint": cap._digest(world_asserted),
        "asserted_fingerprint": witness_rows.fingerprint(asserted),
        "asserted_without_admission": len(world_asserted - admitted),
        "constructed_world_edges": len(world_constructed),
        "constructed_fingerprint": cap._digest(world_constructed),
        "a_w_subset_of_p": world_asserted <= present,
        "candidates": rows if arm == "on" else None,
        "eligibility": reasons if arm == "on" else None,
        "unexplained": unexplained,
    }
    return engine_stamp.stamp(cell)


def _witness_matches(witness: dict) -> dict:
    """X8: the observer-off witness must reproduce the published audit row."""
    result = witness_rows.compare_to_audit(
        witness, witness["seed"], fields=witness_rows.WITNESS_FIELDS,
        labels=witness_rows.LABELS)
    if result["audit"] is not None:
        result["audit"] = {"seed": witness["seed"], **result["audit"]}
    return result


def _row(seed: int, off: dict, on: dict) -> dict:
    counts = {
        "W": on["world_edges"],
        "P": on["present_world_edges"],
        "C": on["constructed_world_edges"],
        "S_cycle": on["s_cycle_max"],
        "S_ever": on["s_ever_world_edges"],
        "A_pred": on["asserted_world_edges"] - on["asserted_without_admission"],
    }
    loss = loss_chain(counts, bypass=on["asserted_without_admission"])
    return {
        "seed": seed,
        "neutral": neutrality(off, on),
        "counts": counts,
        "loss": loss,
        "a_w_subset_of_p": bool(on.get("a_w_subset_of_p")),
        "witnesses": {
            "positive": on["asserted_world_edges"] > 0,
            "negative": on["present_world_edges"] - on["asserted_world_edges"] > 0,
        },
        "unexplained": on.get("unexplained") or [],
        "observed": on.get("candidates") is not None and on.get("eligibility") is not None,
        "stage_fingerprint": _fingerprint(
            "|".join("%s=%s" % item for item in sorted(counts.items()))),
    }


def verdict(body: dict, run: dict) -> tuple[str, dict]:
    """The record's decision table, read in its declared order.

    X1 comes first because a divergent observer is not a conversion result; X8 and X7 come next
    because a block that cannot reproduce the audit row or its own first seed is not admissible;
    then the stage gates; only a complete, neutral, observed block produces a target.
    """
    rows = run.get("rows") or []
    for row in rows:
        if not row["neutral"]["neutral"]:
            return "OBSERVER NOT NEUTRAL", {
                "gate": "X1_observer_neutral", "seed": row["seed"],
                "differs": row["neutral"]["differs"]}
    witness = run.get("witness") or {}
    if not witness.get("reproduces"):
        return "VOID", {"gate": "X8_control_reproduces_audit",
                        "differs": witness.get("differs", [])}
    control = run.get("control") or {}
    if not control.get("neutral"):
        return "VOID", {"gate": "X7_determinism",
                        "differs": control.get("differs", [])}
    for row in rows:
        if row.get("unexplained"):
            return "VOID", {"gate": "X2_stage_complete", "seed": row["seed"],
                            "unexplained": row["unexplained"]}
        counts = row["counts"]
        if min(counts["P"], counts["C"], counts["S_ever"]) == 0:
            return "VOID", {"gate": "X2_stage_complete", "seed": row["seed"],
                            "zero_denominator": True}
        if not row["a_w_subset_of_p"]:
            return "VOID", {"gate": "X4_same_object", "seed": row["seed"]}
        if not (row["witnesses"]["positive"] and row["witnesses"]["negative"]):
            return "VOID", {"gate": "X5_witnesses", "seed": row["seed"]}
    if len({row["stage_fingerprint"] for row in rows}) < 2:
        return "VOID", {"gate": "X6_seed_axis"}
    if not all(row["observed"] for row in rows):
        return "PARTIAL OBSERVATION", {
            "unobserved": [row["seed"] for row in rows if not row["observed"]]}
    return "CONVERSION OBSERVED", {
        "seeds": len(rows),
        "suspects": {str(row["seed"]): row["loss"]["primary_suspect"] for row in rows}}


def build(body: dict | None = None) -> dict:
    body = body or prereg()
    design = body["design"]
    rows = []
    for seed in design["seeds"]:
        rows.append(_row(seed, _load_part(seed, "off"), _load_part(seed, "on")))
    witness_cell = design["witness_cell"]
    witness = _witness_matches(_load_part(witness_cell["seed"], witness_cell["arm"], "_witness"))
    control = neutrality(_load_part(design["seeds"][0], "on"),
                         _load_part(design["seeds"][0], "on", "_control"))
    run = {"rows": rows, "witness": witness, "control": control}
    label, details = verdict(body, run)
    checks = {
        "X1_observer_neutral": all(row["neutral"]["neutral"] for row in rows),
        "X2_stage_complete": all(
            not row["unexplained"]
            and min(row["counts"]["P"], row["counts"]["C"], row["counts"]["S_ever"]) > 0
            for row in rows),
        "X3_no_unobserved_imputation": True,
        "X4_same_object": all(row["a_w_subset_of_p"] for row in rows),
        "X5_witnesses": all(
            row["witnesses"]["positive"] and row["witnesses"]["negative"] for row in rows),
        "X6_seed_axis": len({row["stage_fingerprint"] for row in rows}) >= 2,
        "X7_determinism": control["neutral"],
        "X8_control_reproduces_audit": witness["reproduces"],
    }
    artifact = {
        "kind": KIND,
        "prereg": body["prereg"],
        "engine": {"version": engine_stamp.engine_version(),
                   "sha256": engine_stamp.engine_sha256()},
        "design": {"seeds": design["seeds"], "arms": design["arms"],
                   "cycles": design["cycles"], "cells": design["cells"],
                   "witness_cell": witness_cell},
        "rows": rows,
        "witness": witness,
        "control": control,
        "checks": checks,
        "verdict": label,
        "details": details,
        "not_evidence": body["not_evidence"],
    }
    return engine_stamp.stamp(artifact)


def render_result(art: dict) -> str:
    lines = [
        "# Presence to assertion: the conversion observer — result",
        "",
        "Generated from `docs/presence_conversion_observer_run.json` by "
        "`python -m benchmarks.presence_conversion_observer --finish`. Do not edit by hand.",
        "",
        "**Engine:** `%s`. **Design:** %d design cells over %d seeds at %d cycles, "
        "plus the observer-off witness cell and the X7 determinism control."
        % (art["engine"]["version"], art["design"]["cells"],
           len(art["design"]["seeds"]), art["design"]["cycles"]),
        "",
        "**Verdict: `%s`.**" % art["verdict"],
        "",
        "## Per-seed retained chain",
        "",
        "| Seed | W | P | C | S_cycle | S_ever | A_pred | Bypass | Primary suspect | Neutral |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in art["rows"]:
        counts = row["counts"]
        lines.append("| %d | %d | %d | %d | %d | %d | %d | %d | %s | %s |" % (
            row["seed"], counts["W"], counts["P"], counts["C"], counts["S_cycle"],
            counts["S_ever"], counts["A_pred"], row["loss"]["bypass"],
            row["loss"]["primary_suspect"] or "none",
            "yes" if row["neutral"]["neutral"] else "NO"))
    lines += ["", "## Gates", "", "| Gate | Result |", "| --- | --- |"]
    for gate, passed in art["checks"].items():
        lines.append("| `%s` | %s |" % (gate, "pass" if passed else "FAIL"))
    lines += [
        "",
        "The witness cell reproduced the published audit row: %s."
        % ("yes" if art["witness"]["reproduces"] else "no"),
        "",
        "The loss rule runs over `W -> P -> C -> S_cycle -> S_ever -> A_pred`. `E` is the reason "
        "record attached to `P -> C`, not a retention step; `A_other` is the bypass and is "
        "counted in neither retention nor loss.",
        "",
        "## What this does not establish",
        "",
        art["not_evidence"],
        "",
        "## Reproduce",
        "",
        "```bash",
        "python -m benchmarks.presence_conversion_observer --measure",
        "python -m benchmarks.presence_conversion_observer --finish",
        "python -m benchmarks.presence_conversion_observer --check",
        "```",
        "",
    ]
    return "\n".join(lines)


def _run_part(seed: int, arm: str, suffix: str = "") -> None:
    """One cell, in its own process, so the engine sees a fresh hash seed."""
    path = _part_path(seed, arm, suffix)
    if path.exists():
        print("cached %s" % path.name, flush=True)
        return
    env = dict(os.environ, PYTHONHASHSEED="0")
    command = [sys.executable, "-m", "benchmarks.presence_conversion_observer",
               "--cell", str(seed), "--arm", arm, "--out", str(path)]
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, env=env,
                          timeout=3600)
    if proc.returncode != 0:
        raise SystemExit("cell seed=%d arm=%s%s failed: %s" % (
            seed, arm, suffix, (proc.stderr or proc.stdout or "")[-800:]))
    print("cell seed=%d arm=%s%s written in %.1fs" % (
        seed, arm, suffix, time.perf_counter() - started), flush=True)


def measure() -> int:
    body = prereg()
    problems = validate(body)
    if problems:
        raise SystemExit("REFUSED: the record is not valid: " + "; ".join(problems))
    if not (body.get("authorisation") or {}).get("granted"):
        raise SystemExit("REFUSED: the record is not authorised; no cell may run")
    design = body["design"]
    for seed in design["seeds"]:
        for arm in design["arms"]:
            _run_part(seed, arm)
    witness = design["witness_cell"]
    _run_part(witness["seed"], witness["arm"], "_witness")
    _run_part(design["seeds"][0], "on", "_control")
    return 0


def finish() -> int:
    body = prereg()
    problems = validate(body)
    if problems:
        raise SystemExit("REFUSED: the record is not valid: " + "; ".join(problems))
    if not (body.get("authorisation") or {}).get("granted"):
        raise SystemExit("REFUSED: the record is not authorised; no result may be written")
    art = build(body)
    ARTIFACT.write_text(json.dumps(art, indent=1) + "\n", encoding="utf-8")
    RESULT.write_text(render_result(art), encoding="utf-8")
    print("%s: %s" % (art["verdict"], json.dumps(art["details"])))
    return 0


def check() -> int:
    if not ARTIFACT.exists():
        raise SystemExit("no run artifact; run --finish")
    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    problems = []
    if art.get("kind") != KIND:
        problems.append("artifact kind")
    gaps = engine_stamp.missing(art)
    if gaps:
        problems.append("artifact is not fully stamped: %r" % gaps)
    if not supersession.accepts(prereg(), art.get("engine", {}).get("sha256")):
        problems.append("artifact build does not match the shipped engine or the recorded build")
    label, details = verdict(prereg(), {"rows": art.get("rows") or [],
                                        "witness": art.get("witness") or {},
                                        "control": art.get("control") or {}})
    if art.get("verdict") != label:
        problems.append("verdict %r is not the derived %r" % (art.get("verdict"), label))
    if art.get("details") != details:
        problems.append("details are not derived from the rows")
    if not RESULT.exists() or RESULT.read_text(encoding="utf-8") != render_result(art):
        problems.append("result page is stale")
    if problems:
        raise SystemExit("FAIL: " + "; ".join(problems))
    print("conversion observer %s: %s" % (art["prereg"], art["verdict"]))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--render-prereg", action="store_true")
    group.add_argument("--check-prereg", action="store_true")
    group.add_argument("--measure", action="store_true")
    group.add_argument("--finish", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--cell", type=int, metavar="SEED")
    parser.add_argument("--arm", choices=("off", "on"))
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    if args.cell is not None:
        if not args.arm or not args.out:
            raise SystemExit("--cell needs --arm and --out")
        if not (prereg().get("authorisation") or {}).get("granted"):
            raise SystemExit("REFUSED: the record is not authorised; no cell may run")
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(run_cell(args.cell, args.arm), indent=1) + "\n",
                       encoding="utf-8")
        print("wrote %s" % out)
        return 0
    if args.render_prereg:
        problems = validate()
        if problems:
            raise SystemExit("the record is not valid: " + "; ".join(problems))
        DOC.write_text(render_prereg(prereg()), encoding="utf-8")
        print("rendered %s" % DOC.name)
        return 0
    if args.check_prereg:
        return check_prereg()
    if args.finish:
        return finish()
    if args.check:
        return check()
    return measure()


if __name__ == "__main__":
    raise SystemExit(main())
