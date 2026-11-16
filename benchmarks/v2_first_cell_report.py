"""The one fixed shape of the first V2 cell's report.

No cell has run. This module fixes what a cell result must contain and emits the only
report shape the project accepts. The label is derived from the interval, never typed:
a result whose stated outcome contradicts its own interval is refused, as are an
unaccounted seed, a missing beta selection, a VOID that still quotes an effect, a stale
scorer pin, and a control arm whose bystander moved without VOIDing the cell.

    python -m benchmarks.v2_first_cell_report --check
    python -m benchmarks.v2_first_cell_report --write-template
    python -m benchmarks.v2_first_cell_report --render RESULT.json [--out PATH]

The selection comparison is read from the committed artifacts rather than from the
result, so the report cannot restate those numbers differently.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"
PAGE = DOCS / "V2-FIRST-CELL-REPORT-TEMPLATE.md"
SEEDS = DOCS / "v2_first_cell_seeds.json"
MASS_MATCH = DOCS / "v2_first_cell_mass_match.json"
PLANTED_SELECTION = DOCS / "v2_first_cell_planted_selection.json"
DECISIONS = DOCS / "decisions.json"

INTERPRETATION = "DECISION-V2-FIRST-CELL-INTERPRETATION"
BETA_GRID = (1, 2, 4, 8)
GATE_IDS = ("A1", "A2", "A3", "A4", "A5")
GATE_CODES = {
    "A1": "A1_CANONICALISATION",
    "A2": "A2_IDENTIFIER",
    "A3": "A3_MUTATION",
    "A4": "A4_COST",
    "A5": "A5_DETERMINISM",
}
LABELS = ("PASS", "BOOKKEEPING", "REVERSAL", "VOID")
VOID_CODES = tuple(GATE_CODES.values()) + (
    "SEEDS_MEASURABLE",
    "PARTS_INCOMPLETE",
    "SCORER_PIN",
    "GATES_NOT_RUN",
    "M1_CONTROL",
)
MIN_MEASURABLE = 8
LEVEL = 0.99
RESAMPLES = 10000
MEAN_TOLERANCE = 5e-7


class ReportError(ValueError):
    """A result that does not fit the fixed shape."""


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def declared_seeds() -> list[int]:
    return list(_load(SEEDS)["seed_block"]["seeds"])


def selection_reference() -> dict:
    mass = _load(MASS_MATCH)["summary"]
    planted = _load(PLANTED_SELECTION)["summary"]
    null_keys = mass["mean_delta_keys"]
    planted_keys = planted["mean_delta_keys"]
    planted_gain = abs(planted["mean_d_maintained"])
    return {
        "null_keys": null_keys,
        "null_mass": mass["mean_delta_mass"],
        "planted_keys": planted_keys,
        "planted_gain": planted_gain,
        "share": planted_keys / planted_gain * 100.0,
    }


def derive_label(lo: float, hi: float) -> str:
    if hi < 0:
        return "PASS"
    if lo > 0:
        return "REVERSAL"
    return "BOOKKEEPING"


def derive_m1(bystander_delta: float) -> str:
    """M1 is the bystander check: byte-identical means PASS, any movement means FAIL."""
    return "PASS" if bystander_delta == 0 else "FAIL"


def validate_control(control, is_void: bool, codes: list[str], declared: set[int], errors: list[str]) -> set[str]:
    """Check the §8 control arm; return the VOID codes its condition supplies."""
    present: set[str] = set()
    if not isinstance(control, dict):
        errors.append("control must be an object describing the section 8 arm")
        return present

    status = control.get("status")
    if status not in ("PASS", "FAIL", "NOT RUN"):
        errors.append("control status must be PASS, FAIL or NOT RUN")
    if control.get("seed") not in declared:
        errors.append("control seed %r is not declared" % (control.get("seed"),))
    intervention = control.get("intervention")
    if intervention not in ("remove_member", "retire"):
        errors.append("control intervention must be remove_member or retire")
    for field in ("composite_id", "bystander_id", "metric"):
        if not isinstance(control.get(field), str) or not control[field].strip():
            errors.append("control %s must be a non-empty string" % field)
    if control.get("composite_id") and control.get("bystander_id"):
        if control["composite_id"] == control["bystander_id"]:
            errors.append("the control's bystander must not be its target composite")
    if intervention == "remove_member":
        if not str(control.get("removed_member") or "").strip():
            errors.append("remove_member needs the removed member")
    elif intervention == "retire" and control.get("removed_member") not in (None, ""):
        errors.append("retire takes no removed_member")

    if status == "NOT RUN":
        if not str(control.get("detail") or "").strip():
            errors.append("a control that did not run needs a reason")
        if "member_delta" in control or "bystander_delta" in control:
            errors.append("a control that did not run carries no deltas")
        return present

    member = control.get("member_delta")
    bystander = control.get("bystander_delta")
    if not _is_num(member):
        errors.append("control member_delta must be numeric")
    if not _is_num(bystander):
        errors.append("control bystander_delta must be numeric")
    if _is_num(bystander) and status in ("PASS", "FAIL"):
        derived = derive_m1(bystander)
        if status != derived:
            errors.append(
                "control status %s contradicts bystander_delta %.9f: the M1 check returns %s"
                % (status, bystander, derived)
            )
    if status == "FAIL":
        present.add("M1_CONTROL")
        if not is_void:
            errors.append("an M1 violation (control FAIL) requires VOID")
        elif "M1_CONTROL" not in codes:
            errors.append("an M1 violation requires the M1_CONTROL code")
    return present


def reading_quote(label: str) -> str:
    """The adopted sentence for this label, quoted from the decision rather than retyped."""
    data = _load(DECISIONS)
    row = [d for d in data["decisions"] if d["decision_id"] == INTERPRETATION][0]
    chosen = row["chosen"]
    if len(chosen) != 5:
        raise ReportError("the reading decision no longer carries five chosen sentences")
    index = {"PASS": 1, "BOOKKEEPING": 2, "REVERSAL": 3, "VOID": 4}[label]
    sentence = chosen[index]
    if label not in sentence:
        raise ReportError("the reading decision's sentence for %s does not name it" % label)
    return sentence


def _is_num(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate(result: dict, seeds: list[int] | None = None) -> list[str]:
    """Return every reason the result does not fit the shape; empty means it renders."""
    seeds = list(seeds if seeds is not None else declared_seeds())
    declared = set(seeds)
    errors: list[str] = []

    if result.get("kind") != "v2_first_cell_result":
        errors.append("kind must be v2_first_cell_result")
    for field in ("id", "date", "protocol", "scorer_pin"):
        if not isinstance(result.get(field), str) or not result[field].strip():
            errors.append("%s must be a non-empty string" % field)

    outcome = result.get("outcome")
    if outcome not in LABELS:
        errors.append("outcome must be one of %s" % ", ".join(LABELS))

    pin_ok = result.get("scorer_pin_ok")
    if pin_ok not in (True, False):
        errors.append("scorer_pin_ok must be true or false")

    gates = result.get("gates")
    if not isinstance(gates, dict) or set(gates) != set(GATE_IDS):
        errors.append("gates must name exactly A1-A5")
        gates = gates if isinstance(gates, dict) else {}
    failed_gates = []
    not_run = []
    for gate in GATE_IDS:
        row = gates.get(gate)
        if not isinstance(row, dict):
            errors.append("gate %s is missing" % gate)
            continue
        status = row.get("status")
        if status not in ("PASS", "FAIL", "NOT RUN"):
            errors.append("gate %s status must be PASS, FAIL or NOT RUN" % gate)
        elif not str(row.get("evidence") or "").strip():
            errors.append("gate %s needs its evidence" % gate)
        if status == "FAIL":
            failed_gates.append(gate)
        if status == "NOT RUN":
            not_run.append(gate)

    void = result.get("void")
    is_void = void is not None
    codes: list[str] = []
    if is_void:
        if not isinstance(void, dict):
            errors.append("void must be an object with codes and detail")
        else:
            codes = void.get("codes") or []
            if not isinstance(codes, list) or not codes:
                errors.append("a VOID needs at least one reason code")
            else:
                unknown = sorted(set(codes) - set(VOID_CODES))
                if unknown:
                    errors.append("unknown VOID codes: %s" % ", ".join(unknown))
            if not str(void.get("detail") or "").strip():
                errors.append("a VOID needs a detail sentence")
        if outcome != "VOID":
            errors.append("a result with a void object must use the VOID outcome")

    if outcome == "VOID" and not is_void:
        errors.append("the VOID outcome needs a void object with codes and detail")
    if failed_gates and not is_void:
        errors.append("a failed gate requires VOID: %s" % ", ".join(failed_gates))
    if not_run and not is_void:
        errors.append("a gate that did not run requires VOID: %s" % ", ".join(not_run))

    rows = result.get("per_seed")
    if not isinstance(rows, list) or not rows:
        errors.append("per_seed must be a non-empty list")
        rows = []
    seen: set[int] = set()
    measurable: list[dict] = []
    excluded: list[dict] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append("per_seed[%d] is not an object" % index)
            continue
        seed = row.get("seed")
        if seed not in declared:
            errors.append("per_seed[%d]: seed %r is not declared" % (index, seed))
            continue
        if seed in seen:
            errors.append("per_seed[%d]: seed %r is duplicated" % (index, seed))
            continue
        seen.add(seed)
        measurable_flag = row.get("measurable")
        if measurable_flag is True:
            measurable.append(row)
            if not _is_num(row.get("d")):
                errors.append("seed %d: a measurable seed needs numeric d" % seed)
            beta = row.get("beta")
            if not isinstance(beta, dict) or set(beta) != {"B", "C"}:
                errors.append("seed %d: beta must name B and C only; arm A selects no beta" % seed)
            else:
                for arm in ("B", "C"):
                    if beta[arm] not in BETA_GRID:
                        errors.append(
                            "seed %d: beta %s must be one of %s"
                            % (seed, arm, ", ".join(str(x) for x in BETA_GRID))
                        )
            if not _is_num(row.get("d_B")):
                errors.append("seed %d: a measurable seed needs numeric d_B" % seed)
        elif measurable_flag is False:
            excluded.append(row)
            if not str(row.get("exclusion") or "").strip():
                errors.append("seed %d: an unmeasured seed needs an exclusion reason" % seed)
            if "d" in row or "beta" in row or "d_B" in row:
                errors.append("seed %d: an unmeasured seed must not carry d, d_B or beta" % seed)
        else:
            errors.append("seed %d: measurable must be true or false" % seed)

    missing = declared - seen
    if missing and not is_void:
        errors.append("declared seeds missing: %s" % ", ".join(str(s) for s in sorted(missing)))
    if missing and is_void and "PARTS_INCOMPLETE" not in codes:
        errors.append("missing declared seeds require the PARTS_INCOMPLETE code")
    if len(measurable) < MIN_MEASURABLE:
        if not is_void:
            errors.append("fewer than %d measurable seeds requires VOID" % MIN_MEASURABLE)
        elif "SEEDS_MEASURABLE" not in codes:
            errors.append("fewer than %d measurable seeds requires the SEEDS_MEASURABLE code" % MIN_MEASURABLE)
    if pin_ok is not True and not is_void:
        errors.append("a stale scorer pin requires VOID")
    if pin_ok is not True and is_void and "SCORER_PIN" not in codes:
        errors.append("a stale scorer pin requires the SCORER_PIN code")

    control_present = validate_control(result.get("control"), is_void, codes, declared, errors)

    if is_void:
        if result.get("interval") is not None:
            errors.append("a VOID report carries no interval")
        present = set(GATE_CODES[g] for g in failed_gates) | control_present
        if not_run:
            present.add("GATES_NOT_RUN")
        if len(measurable) < MIN_MEASURABLE:
            present.add("SEEDS_MEASURABLE")
        if missing:
            present.add("PARTS_INCOMPLETE")
        if pin_ok is not True:
            present.add("SCORER_PIN")
        if codes and not (present & set(codes)):
            errors.append("the VOID codes name no condition this result shows")
    else:
        if outcome == "VOID":
            errors.append("the VOID label needs a void object")
        interval = result.get("interval")
        if not isinstance(interval, dict):
            errors.append("a non-VOID result needs an interval")
        else:
            for field in ("mean", "lo", "hi"):
                if not _is_num(interval.get(field)):
                    errors.append("interval %s must be numeric" % field)
            if interval.get("level") != LEVEL:
                errors.append("interval level must be %.2f" % LEVEL)
            if interval.get("resamples") != RESAMPLES:
                errors.append("interval resamples must be %d" % RESAMPLES)
            if _is_num(interval.get("mean")) and _is_num(interval.get("lo")) and _is_num(interval.get("hi")):
                lo, mean, hi = interval["lo"], interval["mean"], interval["hi"]
                if lo > hi:
                    errors.append("interval lo is above hi")
                if measurable:
                    computed = sum(row["d"] for row in measurable) / len(measurable)
                    if abs(mean - computed) > MEAN_TOLERANCE:
                        errors.append(
                            "interval mean %.9f is not the mean of the measurable seeds (%.9f)"
                            % (mean, computed)
                        )
                label = derive_label(lo, hi)
                if outcome != label:
                    errors.append(
                        "outcome %s contradicts interval [%.9f, %.9f]: the rule returns %s"
                        % (outcome, lo, hi, label)
                    )

    return errors


def _fixture(label: str, seeds: list[int] | None = None) -> dict:
    """A synthetic result used only to prove the shape; never a cell."""
    seeds = list(seeds if seeds is not None else declared_seeds())
    if label == "PASS":
        values = [-0.0010 - index * 0.0001 for index in range(len(seeds))]
    elif label == "BOOKKEEPING":
        values = [0.0008 + (index - 4.5) * 0.0002 for index in range(len(seeds))]
    elif label == "REVERSAL":
        values = [0.0020 + index * 0.0001 for index in range(len(seeds))]
    else:
        rows = [
            {
                "seed": seed,
                "measurable": False,
                "exclusion": "not run: gate A3 failed before the arms",
            }
            for seed in seeds
        ]
        return {
            "kind": "v2_first_cell_result",
            "id": "V2-FIRST-CELL-RESULT-VOID-FIXTURE",
            "date": "2026-11-16",
            "protocol": "docs/V2-FIRST-EXPERIMENT-PREREGISTRATION.md",
            "scorer_pin": "docs/v2_first_cell_scorer_pin.json",
            "scorer_pin_ok": True,
            "outcome": "VOID",
            "gates": {
                gate: {"status": "FAIL" if gate == "A3" else "PASS", "evidence": "VOID fixture"}
                for gate in GATE_IDS
            },
            "per_seed": rows,
            "interval": None,
            "control": {
                "status": "NOT RUN",
                "seed": seeds[0],
                "intervention": "remove_member",
                "composite_id": "c-000001",
                "removed_member": "a->b",
                "bystander_id": "c-000002",
                "metric": "resolved member count",
                "detail": "the A3 gate failed before the control arm",
            },
            "void": {
                "codes": ["A3_MUTATION", "SEEDS_MEASURABLE"],
                "detail": "the mutation invariant failed before the behavioural arms",
            },
        }
    mean = sum(values) / len(values)
    return {
        "kind": "v2_first_cell_result",
        "id": "V2-FIRST-CELL-RESULT-%s-FIXTURE" % label,
        "date": "2026-11-16",
        "protocol": "docs/V2-FIRST-EXPERIMENT-PREREGISTRATION.md",
        "scorer_pin": "docs/v2_first_cell_scorer_pin.json",
        "scorer_pin_ok": True,
        "outcome": label,
        "gates": {gate: {"status": "PASS", "evidence": "%s fixture" % label} for gate in GATE_IDS},
        "per_seed": [
            {
                "seed": seed,
                "measurable": True,
                "d": value,
                "d_B": value - 0.0005,
                "beta": {"B": 1, "C": 2},
            }
            for seed, value in zip(seeds, values)
        ],
        "interval": {
            "mean": mean,
            "lo": mean - (0.0009 if label == "BOOKKEEPING" else 0.00015),
            "hi": mean + (0.0009 if label == "BOOKKEEPING" else 0.00015),
            "level": LEVEL,
            "resamples": RESAMPLES,
        },
        "control": {
            "status": "PASS",
            "seed": seeds[0],
            "intervention": "remove_member",
            "composite_id": "c-000001",
            "removed_member": "a->b",
            "bystander_id": "c-000002",
            "metric": "resolved member count",
            "member_delta": 1.0,
            "bystander_delta": 0.0,
            "detail": "the target lost one member; the bystander did not move",
        },
        "void": None,
    }


def _mean(rows: list[dict], field: str) -> float:
    return sum(row[field] for row in rows) / len(rows)


def _control_section(control: dict) -> str:
    how = (
        "remove `%s`" % control["removed_member"]
        if control["intervention"] == "remove_member"
        else "retire the composite"
    )
    rows = [
        "| | |",
        "|---|---|",
        "| Seed | %d |" % control["seed"],
        "| Target | `%s` — %s |" % (control["composite_id"], how),
        "| Bystander | `%s` |" % control["bystander_id"],
        "| Metric | %s |" % control["metric"],
    ]
    if control["status"] == "NOT RUN":
        rows.append("| Status | NOT RUN |")
        detail = control["detail"].strip()
        if detail[-1:] not in (".", "!", "?"):
            detail += "."
        body = (
            "Not run: %s No M1 claim is made from this arm; it is secondary and does not change the "
            "charter outcome." % detail
        )
    else:
        rows += [
            "| Member delta | `%+.6f` |" % control["member_delta"],
            "| Bystander delta | `%+.6f` |" % control["bystander_delta"],
            "| M1 | %s |" % control["status"],
        ]
        if control["status"] == "FAIL":
            body = (
                "M1 FAIL — the bystander moved, so the mutation was not local to its composite. "
                "The cell is VOID; the deltas above are the reason, not an effect estimate."
            )
        else:
            if control["member_delta"] == 0:
                member = (
                    "The members did not move: the intervention had no effect on its own composite — a tie "
                    "on the members, which means the primitive is useless for control. This is the secondary "
                    "finding and not a charter criterion."
                )
            else:
                member = (
                    "The members moved, so the intervention is local to its composite. This is the section 8 "
                    "mechanism check, not a second earning test."
                )
            body = "M1 PASS — the bystander is unchanged (`0.000000`). " + member
    return "\n## 8. Control arm (`M1`)\n\n" + "\n".join(rows) + "\n\n" + body + "\n"


def render(result: dict, seeds: list[int] | None = None) -> str:
    seeds = list(seeds if seeds is not None else declared_seeds())
    errors = validate(result, seeds)
    if errors:
        raise ReportError("\n".join(errors))

    outcome = result["outcome"]
    is_void = outcome == "VOID"
    rows = result["per_seed"]
    measurable = [row for row in rows if row["measurable"] is True]
    excluded = [row for row in rows if row["measurable"] is False]
    reference = selection_reference()

    header = f"""# V2 first cell — result report

**Outcome:** `{outcome}`
**Protocol:** `{result['protocol']}` — signed 2026-11-16
**Scorer pin:** `{result['scorer_pin']}`
**Reported:** `{result['date']}`
**Read under:** [`{INTERPRETATION}`]({INTERPRETATION}.md)
"""

    ran = f"""
## 1. What ran

| | |
|---|---|
| Seeds declared | {len(seeds)} (`{seeds[0]}`–`{seeds[-1]}`) |
| Measurable | {len(measurable)} |
| Excluded | {len(excluded)} |
| Arms | A pair counts; B frozen membership; C maintained membership |
| Endpoint | mean paired `d = L_C − L_A`, held-out next-edge log-loss |
| Interval rule | paired bootstrap over seeds, 99%, 10,000 resamples |
"""

    gate_rows = "\n".join(
        "| %s | %s | %s |" % (gate, result["gates"][gate]["status"], result["gates"][gate]["evidence"])
        for gate in GATE_IDS
    )
    gates = f"""
## 2. Gates

| Gate | Status | Evidence |
|---|---|---|
{gate_rows}
"""

    if excluded:
        exclusion_rows = "\n".join(
            "| %d | %s |" % (row["seed"], row["exclusion"]) for row in excluded
        )
        exclusions = f"""
## 3. Exclusions

| Seed | Reason |
|---|---|
{exclusion_rows}
"""
    else:
        exclusions = """
## 3. Exclusions

None; every declared seed was measurable.
"""

    if is_void:
        interval = f"""
## 4. Interval

No interval is reported. The cell is `VOID`: {', '.join('`%s`' % code for code in result['void']['codes'])} —
{result['void']['detail']}
"""
        beta = """
## 5. Beta selections

Not read (VOID).
"""
        decomposition = """
## 6. Decomposition

Not read (VOID).
"""
        selection = """
## 7. Selection comparison

Not read (VOID). The committed matched controls are not used to explain an effect the cell did not produce.
"""
    else:
        lo, mean, hi = (result["interval"][key] for key in ("lo", "mean", "hi"))
        where = {
            "PASS": "lies entirely below zero",
            "BOOKKEEPING": "includes zero",
            "REVERSAL": "lies entirely above zero",
        }[outcome]
        interval = f"""
## 4. Interval

The mean paired difference is `{mean:.6f}` with a 99% interval `[{lo:.6f}, {hi:.6f}]`
(10,000 resamples). The interval {where}, so the label is `{outcome}`.
"""
        beta_rows = "\n".join(
            "| %d | %s | %s |" % (row["seed"], row["beta"]["B"], row["beta"]["C"])
            for row in measurable
        )
        beta = f"""
## 5. Beta selections

| Seed | Arm B | Arm C |
|---|---|---|
{beta_rows}

Arm A selects no beta.
"""
        mean_d = _mean(measurable, "d")
        mean_b = _mean(measurable, "d_B")
        decomposition = f"""
## 6. Decomposition

| Quantity | Value |
|---|---|
| Mean `d_C − d_A` | `{mean_d:.6f}` |
| Mean `d_B − d_A` | `{mean_b:.6f}` |
| Revision effect `d_C − d_B` | `{mean_d - mean_b:.6f}` |

`d_B` is the frozen-membership arm's difference from the baseline. The decomposition is
descriptive; `d_B` is not a second criterion.
"""
        common = (
            "The committed matched controls are `%+.6f` at equal mass and key count on the null worlds "
            "and `%+.6f` on the planted world — `%.2f%%` of its `%.6f` gain (`%+.6f` at equal mass alone)."
            % (
                reference["null_keys"],
                reference["planted_keys"],
                reference["share"],
                reference["planted_gain"],
                reference["null_mass"],
            )
        )
        if outcome == "PASS":
            margin = abs(mean)
            if margin <= reference["planted_keys"]:
                reading = (
                    "The cell's margin, `%.6f`, is at or below the largest measured selection advantage; "
                    "the pass is compatible with the composite term carrying the gain and does not "
                    "establish that maintained selection is the mechanism." % margin
                )
            else:
                reading = (
                    "The cell's margin, `%.6f`, exceeds the largest measured selection advantage; that does "
                    "not attribute the gain to selection, because the channel was measured at matched mass "
                    "and key count, not inside this cell." % margin
                )
        elif outcome == "BOOKKEEPING":
            reading = (
                "The cell shows no advantage to attribute; `d_B` and `d_C` above are descriptive and neither "
                "is a second criterion."
            )
        else:
            cost = mean
            relation = (
                "of the same order as the matched null cost"
                if abs(cost) <= abs(reference["null_keys"])
                else "larger than the matched null cost"
            )
            reading = (
                "The cell's cost, `%.6f`, is %s; either way the charter fails and the comparison is a "
                "diagnostic, not a rescue." % (cost, relation)
            )
        selection = f"""
## 7. Selection comparison

{common} {reading}
"""

    control = _control_section(result["control"])
    quote = reading_quote(outcome)
    authorises = f"""
## 9. What this authorises

> {quote}
"""

    floor = {
        "PASS": (
            "No V2 build, module, engine change, version, tag or promotion; no capability, transfer or G4 "
            "claim; no second experiment or report. Requirement 5 closes the charter after this report."
        ),
        "BOOKKEEPING": (
            "No feature, `m`, beta-grid, readout, endpoint or interval change; no extended block, substitute "
            "seed or re-run. The block is spent; a further attempt needs a new pre-registration, fresh seeds "
            "and a new grant. \"Not found\" is not \"impossible\"."
        ),
        "REVERSAL": (
            "No relabelling as a near pass or as signal found backwards; no retune, feature or second run. "
            "The block is spent."
        ),
        "VOID": (
            "No effect estimate, interval, direction or trend; no model or capability claim. Not a negative "
            "result and not evidence for or against the primitive. No substitute seed or repaired denominator "
            "under this registration."
        ),
    }[outcome]
    limits = f"""
## 10. What this does not authorise

{floor}
"""

    scope = (
        "No result: no admissible comparison was produced."
        if is_void
        else (
            "One cell, one world family, ten paired seeds, one readout. The charter's answer is scoped to that; "
            "it is not a capability, transfer or G4 result, and no V1 result is V2 evidence."
        )
    )
    not_evidence = f"""
## 11. Not evidence

{scope}
"""

    return (header + ran + gates + exclusions + interval + beta + decomposition + selection
            + control + authorises + limits + not_evidence)


def _example() -> dict:
    """A complete, renderable result for the schema block; not a cell."""
    seeds = declared_seeds()
    return {
        "kind": "v2_first_cell_result",
        "id": "V2-FIRST-CELL-RESULT-1",
        "date": "2026-11-16",
        "protocol": "docs/V2-FIRST-EXPERIMENT-PREREGISTRATION.md",
        "scorer_pin": "docs/v2_first_cell_scorer_pin.json",
        "scorer_pin_ok": True,
        "outcome": "PASS",
        "gates": {gate: {"status": "PASS", "evidence": "what was checked"} for gate in GATE_IDS},
        "per_seed": [
            {
                "seed": seed,
                "measurable": True,
                "d": -0.001,
                "d_B": -0.0005,
                "beta": {"B": 1, "C": 2},
            }
            for seed in seeds[:-1]
        ] + [{"seed": seeds[-1], "measurable": False, "exclusion": "no held-out positives"}],
        "interval": {"mean": -0.001, "lo": -0.0012, "hi": -0.0008, "level": 0.99, "resamples": 10000},
        "control": {
            "status": "PASS",
            "seed": seeds[0],
            "intervention": "remove_member",
            "composite_id": "c-000001",
            "removed_member": "a->b",
            "bystander_id": "c-000002",
            "metric": "resolved member count",
            "member_delta": 1.0,
            "bystander_delta": 0.0,
            "detail": "the target lost one member; the bystander did not move",
        },
        "void": None,
    }


def skeleton() -> str:
    reference = selection_reference()
    schema = json.dumps(_example(), indent=2)
    return f"""# V2 first cell — report template

**Generated** from the seeds, the matched-control artifacts and the reading decision by
`python -m benchmarks.v2_first_cell_report --write-template`. Do not edit it by hand;
`--check` fails when the page and the renderer disagree.

No cell has run. This page fixes the one shape a cell report may take, so the report is not
composed after the numbers are seen. `--render RESULT.json` validates a result and emits that
shape; every case listed under "What the renderer refuses" stops it.

The four labels and what each authorises are fixed by
[`{INTERPRETATION}`]({INTERPRETATION}.md); the report quotes that decision verbatim rather than
paraphrasing it.

## The fixed shape

| Section | Must contain |
|---|---|
| Header | the outcome label, the protocol, the scorer pin, the date, the reading decision |
| 1. What ran | declared, measurable and excluded seed counts; arms; endpoint; interval rule |
| 2. Gates | `A1`–`A5`, each `PASS`, `FAIL` or `NOT RUN`, with its evidence; `NOT RUN` only in a `VOID` |
| 3. Exclusions | every unmeasured seed and its reason |
| 4. Interval | mean, 99% interval, level and resamples — or "no interval" when `VOID` |
| 5. Beta selections | per seed, arm B and arm C; arm A selects none |
| 6. Decomposition | mean `d_C`, mean `d_B`, and their difference |
| 7. Selection comparison | the committed matched controls and the cell's margin against them |
| 8. Control arm (`M1`) | target, intervention, bystander, metric, member and bystander deltas; a bystander change is `M1` FAIL |
| 9. What this authorises | the adopted sentence for the label, quoted |
| 10. What this does not authorise | the floor for that label |
| 11. Not evidence | the scope of one cell |

## The result artifact

`--render` accepts this schema. Extra fields are ignored; a missing field is refused.

```json
{schema}
```

`VOID` replaces the interval with `null` and adds
`"void": {{"codes": [...], "detail": "..."}}`; a non-`VOID` result carries `"void": null`.

## What the renderer refuses

- an outcome label that contradicts its interval — the label is derived, not typed;
- an interval whose mean is not the mean of the measurable seeds, or whose level is not 99%
  with 10,000 resamples;
- a missing, duplicated or undeclared seed, or an unmeasured seed with no reason;
- fewer than 8 measurable seeds without `VOID`, and a `VOID` without the `SEEDS_MEASURABLE` code;
- a failed `A1`–`A5` gate without `VOID`, or a `VOID` without that gate's code;
- a gate marked `NOT RUN` outside a `VOID`, or a `VOID` without the `GATES_NOT_RUN` code;
- a `VOID` that carries an interval;
- a beta outside `{{1, 2, 4, 8}}`, a missing B or C selection, or a beta for arm A;
- a stale or missing scorer pin without `VOID`;
- a control arm that is missing, names its own composite as the bystander, or whose status contradicts
  the bystander delta;
- an `M1` violation without `VOID` and the `M1_CONTROL` code, or a control that did not run without
  a reason;
- a `VOID` whose codes name no condition the result shows.

## The control arm

The section 8 arm intervenes on one composite — `remove_member` or `retire` — and measures the effect on
its members, with a bystander composite as the control. The bystander delta must be exactly zero: `M1`
requires the bystander to be byte-identical, so any movement is `M1` FAIL and the cell is `VOID`. A member
delta of zero is a tie on the members — the primitive is useless for control — and is reported as the
secondary finding; it neither passes nor fails the charter. A control that was not run is reported with its
reason and makes no `M1` claim, because the arm is secondary and adds no VOID trigger.

## The committed selection comparison

These numbers are read from the artifacts at render time, never from the result: at equal mass and
key count the matched control is `{reference['null_keys']:+.6f}` on the null worlds and
`{reference['planted_keys']:+.6f}` on the planted world, `{reference['share']:.2f}%` of its
`{reference['planted_gain']:.6f}` gain (`{reference['null_mass']:+.6f}` at equal mass alone).
A `PASS` states the cell's margin against `{reference['planted_keys']:+.6f}`; a `REVERSAL` states its
cost against `{abs(reference['null_keys']):.6f}`.
"""


def _self_check() -> int:
    for lo, hi, label in ((-2.0, -1.0, "PASS"), (-1.0, 1.0, "BOOKKEEPING"), (1.0, 2.0, "REVERSAL")):
        if derive_label(lo, hi) != label:
            raise ReportError("derive_label(%.1f, %.1f) is not %s" % (lo, hi, label))
    if derive_label(-0.001, 0.0) != "BOOKKEEPING" or derive_label(0.0, 0.001) != "BOOKKEEPING":
        raise ReportError("a boundary interval must be BOOKKEEPING")
    pass_text = render(_fixture("PASS"))
    if "**Outcome:** `PASS`" not in render(_example()):
        raise ReportError("the documented schema does not render")
    for heading in ("## 1. What ran", "## 2. Gates", "## 3. Exclusions", "## 4. Interval",
                    "## 5. Beta selections", "## 6. Decomposition", "## 7. Selection comparison",
                    "## 8. Control arm (`M1`)", "## 9. What this authorises",
                    "## 10. What this does not authorise", "## 11. Not evidence"):
        if heading not in pass_text:
            raise ReportError("the rendered report is missing %r" % heading)
    void_text = render(_fixture("VOID"))
    if "No interval is reported" not in void_text or "Not read (VOID)" not in void_text:
        raise ReportError("a VOID report quotes an effect")
    bad = _fixture("PASS")
    bad["interval"] = {"mean": 0.003, "lo": 0.0028, "hi": 0.0032, "level": LEVEL, "resamples": RESAMPLES}
    if not any("contradicts interval" in error for error in validate(bad)):
        raise ReportError("a label contradicting its interval was not refused")
    dropped = _fixture("PASS")
    dropped["per_seed"] = dropped["per_seed"][:-1]
    if not any("declared seeds missing" in error for error in validate(dropped)):
        raise ReportError("a missing seed was not refused")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="validate the template and the refusals")
    group.add_argument("--write-template", action="store_true", help="regenerate the template page")
    group.add_argument("--render", metavar="RESULT", help="render a cell result")
    parser.add_argument("--out", metavar="PATH", help="write the rendered report here")
    args = parser.parse_args(argv)

    if args.check:
        expected = skeleton()
        actual = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
        if actual != expected:
            print("the template page is stale; run --write-template", file=sys.stderr)
            return 1
        _self_check()
        print("check: template fresh; labels derive; PASS and VOID render; refusals fire")
        return 0

    if args.write_template:
        PAGE.write_text(skeleton(), encoding="utf-8")
        print("wrote %s" % PAGE)
        return 0

    result = _load(Path(args.render))
    try:
        report = render(result)
    except ReportError as error:
        print("refused:\n%s" % error, file=sys.stderr)
        return 1
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print("wrote %s" % args.out)
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
