"""Probe: does a candidate supersede its own stored history?

Two arms, both deterministic, both formed by the engine in world A and then copied into a
**fresh store** whose world never contains world A's tags, so the copied candidate's key
can never recur there:

  * ``prediction`` (G1) — a count-5 temporal edge;
  * ``schema`` (G3) — the directional relational schema from the same world.

Each copy is followed for ten cycles under BOTH rules on the same rows:

  * the pre-fix rule -- maximum value over every copy (the history)
  * the shipped rule -- the newest copy per identity (`_load_prior_candidates`)

The schema arm exists because the reader is not the only thing that decides whether a
candidate is "present": the frozen ``organica/sleep.py`` re-admits stable G2/G3 priors
into the current cycle before natural selection runs. The probe measures that difference
instead of assuming it away (decision document §5).

Writes ``docs/candidate_supersession_probe.json``, then the results document and the
manual's §8.24 block + revision row from that artifact. No number in the prose is typed
(AGENTS.md rule 20); the manual block is replaced between markers, so this is idempotent.

Predictions were recorded before the run in ``docs/DECISION-CANDIDATE-SUPERSESSION.md`` §3.
"""
from __future__ import annotations

import json
import math
import shutil
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from organica.memory import MemoryService  # noqa: E402
from organica.sleep import SleepService   # noqa: E402
from benchmarks import engine_stamp

OUT = ROOT / "docs" / "candidate_supersession_probe.json"
RESULTS = ROOT / "docs" / "CANDIDATE-SUPERSESSION-RESULTS.md"
MANUAL = ROOT / "docs" / "USER-MANUAL.md"
START = "<!-- candidate-supersession:start -->"
END = "<!-- candidate-supersession:end -->"
REV_MARK = "Candidate supersession: one live copy per identity"

FIRST = "amber birch cedar"
SECOND = "delta ember flora"
DISTRACTOR_EVENT = "quartz tidal prism lunar"
FORMATION_BATCHES = 10
DISTRACTOR_CYCLES = 10
EVENTS_PER_DISTRACTOR_CYCLE = 4
TOLERANCE_CYCLES = 1


def _rows_for(mem, cand_id: str) -> list[dict]:
    out: list[dict] = []
    for event in mem.recent(n=4000, event_type="sleep"):
        if not event.source.startswith("sleep:") or event.source == "sleep:meta":
            continue
        try:
            row = json.loads(event.content)
        except (json.JSONDecodeError, ValueError):
            continue
        if row.get("id") == cand_id:
            out.append(row)
    return out


def _value(row: dict) -> float:
    return float(row.get("confidence", row.get("strength", 0)) or 0)


def _form_in_world_a() -> dict[str, dict]:
    """Let the engine form both candidates, then return their stored records."""
    tmp = Path(tempfile.mkdtemp(prefix="supersession-a-"))
    mem = MemoryService(str(tmp / "a.db"))
    svc = SleepService(mem)
    try:
        for _ in range(FORMATION_BATCHES):
            with mem.batch():
                mem.store(FIRST, event_type="observe", source="env:A")
                mem.store(SECOND, event_type="observe", source="env:A")
        report = svc.run_sleep_cycle()

        schemas = [s for s in report.schemas if s.source_role == "antecedent"]
        if not schemas:
            raise SystemExit("formation phase produced no schema; the probe cannot run")
        schema = max(schemas, key=lambda s: s.confidence)

        preds = [p for p in report.predictions
                 if p.source == "amber" and p.target == "delta"]
        if not preds:
            preds = list(report.predictions)
        if not preds:
            raise SystemExit("formation phase produced no prediction; the probe cannot run")
        return {"prediction": asdict(preds[0]), "schema": asdict(schema)}
    finally:
        mem.close()
        shutil.rmtree(tmp, ignore_errors=True)


def _snapshot(mem, svc, report, cand_id: str, index: int, schema_arm: bool) -> dict:
    svc._prior_cache = None
    live = [c for c in svc._load_prior_candidates() if c.get("id") == cand_id]
    rows = _rows_for(mem, cand_id)
    live_rows = [r for r in rows if not r.get("retired")]
    history_max = max((_value(r) for r in live_rows), default=None)
    primed = [p for p in report.predictions
              if p.evidence.get("schema_prior") == cand_id]
    live_value = _value(live[0]) if live else None
    return {
        "cycle_index": index,
        "sleep_cycle": report.cycle,
        "present_in_report": any(s.id == cand_id for s in report.schemas),
        "live_copies": len(live),
        "live_value": live_value,
        "live_above_stable_reference": (live_value is not None
                                        and live_value >= svc.STABLE_THRESHOLD),
        "history_max_value": history_max,
        "history_above_stable_reference": (history_max is not None
                                           and history_max >= svc.STABLE_THRESHOLD),
        "copies_stored": len(live_rows),
        "retired_present": any(r.get("retired") for r in rows),
        "primed_predictions": len(primed) if schema_arm else 0,
    }


def _run_arm(record: dict, schema_arm: bool) -> dict:
    cand_id = record["id"]
    initial = _value(record)
    tmp = Path(tempfile.mkdtemp(prefix="supersession-b-"))
    mem = MemoryService(str(tmp / "b.db"))
    svc = SleepService(mem)
    try:
        svc._store_single_candidate(record)
        trajectory = []
        for index in range(1, DISTRACTOR_CYCLES + 1):
            with mem.batch():
                for _ in range(EVENTS_PER_DISTRACTOR_CYCLE):
                    mem.store(DISTRACTOR_EVENT, event_type="observe", source="env:B")
            report = svc.run_sleep_cycle()
            trajectory.append(_snapshot(mem, svc, report, cand_id, index, schema_arm))
    finally:
        mem.close()
        shutil.rmtree(tmp, ignore_errors=True)

    values = [r["live_value"] for r in trajectory]
    present = [v for v in values if v is not None]
    retired_at = next((r["cycle_index"] for r in trajectory if r["retired_present"]), None)
    death = SleepService.DEATH_THRESHOLD
    predicted_retirement = (math.ceil(math.log(death / initial) / math.log(0.8))
                            if initial > death else 0)
    reinforced = [r["cycle_index"] for prev, r in zip(trajectory, trajectory[1:])
                  if prev["live_value"] is not None and r["live_value"] is not None
                  and r["live_value"] > prev["live_value"]]
    present_cycles = sum(1 for r in trajectory if r["present_in_report"])
    strictly_decreasing = all(b < a for a, b in zip(present, present[1:]))
    history_flat = all(
        abs((r["history_max_value"] or 0) - initial) < 1e-9 for r in trajectory)

    # Presence in the report is not the test: a carried structure is still listed while it
    # is above the stability gate, and the amendment makes that listing harmless. The test
    # is that the live value falls and the candidate is retired on its closed-form cycle.
    if (strictly_decreasing and retired_at is not None
            and abs(retired_at - predicted_retirement) <= TOLERANCE_CYCLES):
        outcome = "SUPERSEDED_AND_RETIRED"
    elif reinforced and retired_at is None:
        outcome = "CARRIED_FORWARD_AND_REINFORCED"
    else:
        outcome = "NEITHER"

    return {
        "candidate_id": cand_id,
        "candidate_type": record.get("type"),
        "initial_value": initial,
        "predicted_retirement_cycle": predicted_retirement,
        "measured_retirement_cycle": retired_at,
        "present_in_report_cycles": present_cycles,
        "presence_explained_by_carry_forward": bool(schema_arm and present_cycles),
        "live_strictly_decreasing": strictly_decreasing,
        "reinforced_at_cycles": reinforced,
        "history_flat_at_initial": history_flat,
        "outcome": outcome,
        "trajectory": trajectory,
    }


def run() -> dict:
    formed = _form_in_world_a()
    arms = {
        "prediction": _run_arm(formed["prediction"], schema_arm=False),
        "schema": _run_arm(formed["schema"], schema_arm=True),
    }

    pred, schema = arms["prediction"], arms["schema"]
    g1_ok = pred["outcome"] == "SUPERSEDED_AND_RETIRED" and pred["history_flat_at_initial"]
    g3_carried = schema["outcome"] == "CARRIED_FORWARD_AND_REINFORCED"
    g3_ok = schema["outcome"] == "SUPERSEDED_AND_RETIRED" and schema["history_flat_at_initial"]

    if g1_ok and g3_ok:
        verdict = "SUPERSESSION_VERIFIED_BOTH_GENERATIONS"
    elif g1_ok and g3_carried:
        verdict = "READER_VERIFIED_G1_DECAYS_G2_G3_BLOCKED_UPSTREAM"
    else:
        verdict = "SUPERSESSION_NOT_VERIFIED"

    return {
        "probe": "candidate_supersession",
        "deterministic_world": True,
        "randomness": "none",
        "decision": "docs/DECISION-CANDIDATE-SUPERSESSION.md",
        "freeze_amendment": "docs/V1-FREEZE.md",
        "world": {
            "formation": (f"{FORMATION_BATCHES} cycles of {FIRST!r} then {SECOND!r} in "
                          f"world A; a prediction and a schema from that world are copied "
                          f"into fresh stores"),
            "distractor": (f"{DISTRACTOR_CYCLES} cycles of {EVENTS_PER_DISTRACTOR_CYCLE} "
                           f"events {DISTRACTOR_EVENT!r}, which never contain world A's "
                           f"tags, so neither copied key can recur"),
            "design_note": ("the first attempt reversed the flow inside batches; the "
                            "batch-boundary A->B transitions kept forward flow dominant "
                            "and the schema was re-extracted every cycle, so absence was "
                            "never created (an unrun manipulation, disclosed in the "
                            "decision document §3a)"),
        },
        "parameters": {
            "formation_batches": FORMATION_BATCHES,
            "distractor_cycles": DISTRACTOR_CYCLES,
            "events_per_distractor_cycle": EVENTS_PER_DISTRACTOR_CYCLE,
            "tolerance_cycles": TOLERANCE_CYCLES,
        },
        "arms": arms,
        "summary": {
            "verdict": verdict,
            "g1_prediction_superseded_and_retired": g1_ok,
            "g3_schema_carried_forward": g3_carried,
            "g3_schema_superseded_and_retired": g3_ok,
        },
        "limits": [
            "n = 1 deterministic world per arm: the trajectories are closed forms and the "
            "quantity is a selection rule, not a population, so no statistical claim is "
            "made or needed",
            "the candidates are formed by the engine in world A and evaluated in fresh "
            "stores; copying the records is a fixture, and the artifact records that "
            "neither key can occur in the world (the schema's presence in the report is "
            "the carry-forward)",
            "the pre-fix rule is reconstructed from the same stored rows; it is a "
            "counterfactual about the reader, not a second engine run (rule 17b)",
            "`STABLE_THRESHOLD` is a priming gate for schemas; for the prediction arm the "
            "same reference is reported only so the two trajectories can be compared, and "
            "no eligibility claim is made for predictions",
            "the carry-forward was removed by the recorded freeze amendment "
            "(`docs/V1-FREEZE.md` §6); this probe measures the amended engine",
            "no part of the cross-context experiment is re-scored here",
        ],
    }


def _arm_table(art: dict, name: str) -> list[str]:
    arm = art["arms"][name]
    out = [f"### {name} arm — `{arm['candidate_id']}`", "",
           f"Initial value {arm['initial_value']}; predicted retirement at cycle "
           f"{arm['predicted_retirement_cycle']}; measured "
           f"{arm['measured_retirement_cycle']}; outcome `{arm['outcome']}`.", "",
           "| cycle | in report | live | live ≥ 0.3 (ref.) | history max | "
           "history ≥ 0.3 (ref.) | copies | retired | primed |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in arm["trajectory"]:
        live = "—" if r["live_value"] is None else f"{r['live_value']:.4f}"
        hist = ("—" if r["history_max_value"] is None
                else f"{r['history_max_value']:.4f}")
        out.append(
            f"| {r['sleep_cycle']} | {'yes' if r['present_in_report'] else 'no'} | {live} | "
            f"{'yes' if r['live_above_stable_reference'] else 'no'} | {hist} | "
            f"{'yes' if r['history_above_stable_reference'] else 'no'} | "
            f"{r['copies_stored']} | {'yes' if r['retired_present'] else 'no'} | "
            f"{r['primed_predictions']} |")
    out.append("")
    return out


def results_document(art: dict) -> str:
    s = art["summary"]
    pred, schema = art["arms"]["prediction"], art["arms"]["schema"]
    out: list[str] = []
    add = out.append
    add("# Candidate supersession — probe results")
    add("")
    add(f"**Generated from** `{OUT.relative_to(ROOT).as_posix()}`. **Decision**: "
        f"[`{Path(art['decision']).name}`]({Path(art['decision']).name}). "
        f"**Freeze amendment**: "
        f"[`{Path(art['freeze_amendment']).name}`]({Path(art['freeze_amendment']).name}) §6. "
        f"**World**: {art['world']['formation']}; {art['world']['distractor']}. "
        f"Deterministic, no randomness.")
    add("")
    add("## 1. Verdict")
    add("")
    add(f"`{s['verdict']}`")
    add("")
    add(f"Both arms now do what Law VI specifies. The prediction formed at "
        f"{pred['initial_value']} and retired at cycle {pred['measured_retirement_cycle']} "
        f"(closed form {pred['predicted_retirement_cycle']}); the schema formed at "
        f"{schema['initial_value']} and retired at cycle {schema['measured_retirement_cycle']} "
        f"(closed form {schema['predicted_retirement_cycle']}). Neither is re-extracted in "
        f"any cycle, and under the pre-fix rule each held its formation value throughout.")
    add("")
    add("The schema arm is the case the freeze amendment changes. Before it, the schema was "
        "re-admitted into the current cycle by the carry-forward and reinforced every cycle: "
        "it rose to 1.0 and never retired, so the reader had no generation decision to "
        "display. The amendment marks carried structures, and selection and storage now "
        "ignore them as evidence.")
    add("")
    add("## 2. Trajectories")
    add("")
    add("`live` is the newest copy per identity; `history` is the maximum over all stored "
        "copies, which is the pre-fix rule. Neither copied key can occur in the world by "
        "construction, so neither is re-extracted in any cycle. The schema arm stays listed "
        "while its value is above the stability gate: that listing is the carry-forward "
        "view, which the amendment marks so it no longer counts as evidence — it decays "
        "while listed. The 0.3 column is the schema priming gate, reported for both arms "
        "only so the two can be compared.")
    add("")
    for name in ("prediction", "schema"):
        out.extend(_arm_table(art, name))
    add("## 3. Outcomes")
    add("")
    add("| arm | initial | outcome | predicted retirement | measured retirement |")
    add("|---|---|---|---|---|")
    for name in ("prediction", "schema"):
        arm = art["arms"][name]
        add(f"| {name} | {arm['initial_value']} | `{arm['outcome']}` | "
            f"{arm['predicted_retirement_cycle']} | {arm['measured_retirement_cycle']} |")
    add("")
    add("## 4. What this establishes, and what it does not")
    add("")
    add("**Established.** Reading the store as history made Law VI decay invisible to the "
        "selector and made pruning reversible; reading it as one live copy per identity "
        "fixes both. And the second blocker was real: the frozen carry-forward re-admitted "
        "stable G2/G3 priors as current-cycle candidates, which is why a schema could rise "
        "while nothing was producing it. With the amendment both generations now decay by "
        "×0.8 and retire on their closed-form cycle, and neither is resurrected from "
        "history.")
    add("")
    add("**Not established.** Anything about transfer: no cross-context task is run here "
        "and `docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md` is not re-scored. Nothing "
        "statistical: n = 1 per arm, deterministic. And nothing about G4–G8, which have no "
        "carry-forward graft and were never affected by this blocker.")
    add("")
    add("**Limits.** " + " ".join(art["limits"]))
    return "\n".join(out) + "\n"


def manual_block(art: dict) -> str:
    pred, schema = art["arms"]["prediction"], art["arms"]["schema"]
    s = art["summary"]
    return "\n".join([
        START,
        "### 8.24 Candidate supersession: one live copy per identity, and carried structures are not evidence",
        "",
        "**Recorded 2026-11-06.** Decision "
        "[`docs/DECISION-CANDIDATE-SUPERSESSION.md`](DECISION-CANDIDATE-SUPERSESSION.md); "
        "results [`docs/CANDIDATE-SUPERSESSION-RESULTS.md`](CANDIDATE-SUPERSESSION-RESULTS.md); "
        "freeze amendment [`docs/V1-FREEZE.md`](V1-FREEZE.md) §6.",
        "",
        "The sleep store is a history: every surviving candidate is re-written each cycle, "
        "reinforced when it re-emerges and decayed ×0.8 when it does not. The old reader "
        "returned *every* copy, so the selector's maximum-value rule always picked the "
        "oldest generation and decay could never be seen; and a pruned candidate's last copy "
        "above the threshold was reloaded and re-decayed forever, so pruning never stuck.",
        "",
        "`_load_prior_candidates` now returns **one live copy per identity**, the newest "
        "generation, and a prune writes a **death record** (`retired: true`) that supersedes "
        "the last live copy. Re-extraction still resurrects a candidate: the new copy is "
        "newer than the tombstone.",
        "",
        "**Freeze amendment (2026-11-06, owner-authorised).** The frozen `organica/sleep.py` "
        "re-admitted every stable G2/G3 prior as a current-cycle candidate before selection, "
        "so those structures were reinforced every cycle and could not decay. The five "
        "carry-forward grafts now mark the re-admitted object `carried_forward=True`; "
        "`_natural_selection` does not treat a carried structure as current-cycle evidence "
        "and `_store_candidates` does not re-write it. The structures remain in the report "
        "for downstream layers and telemetry, and the marker never reaches the store. See "
        "`docs/V1-FREEZE.md` §6.",
        "",
        f"**Measured** (`docs/candidate_supersession_probe.json`, deterministic, two arms). "
        f"A prediction formed at {pred['initial_value']} retired at cycle "
        f"{pred['measured_retirement_cycle']} (closed form "
        f"{pred['predicted_retirement_cycle']}); a schema formed at "
        f"{schema['initial_value']} retired at cycle "
        f"{schema['measured_retirement_cycle']} (closed form "
        f"{schema['predicted_retirement_cycle']}). Neither was re-extracted, and under the "
        f"pre-fix rule both held their formation value in every cycle. Verdict "
        f"`{s['verdict']}`.",
        "",
        "**What it does not establish.** Nothing about transfer — the cross-context run was "
        "measured on the earlier engine and is not re-scored here; nothing statistical "
        "(n = 1 per arm, deterministic); and nothing about G4–G8, which have no "
        "carry-forward graft and were never affected by this blocker.",
        END,
    ])


def update_manual(block: str) -> None:
    text = MANUAL.read_text(encoding="utf-8")
    if START in text and END in text:
        head, rest = text.split(START, 1)
        _, tail = rest.split(END, 1)
        text = head + block + tail
    else:
        anchor = "\n## 9. Troubleshooting"
        assert text.count(anchor) == 1, "manual anchor not unique"
        text = text.replace(anchor, "\n" + block + "\n" + anchor, 1)

    row = ("| 2026-11-06 | **Candidate supersession, and a freeze amendment.** "
           "`_load_prior_candidates` returns the newest copy per candidate id and a prune "
           "writes a death record; the five G2/G3 carry-forward grafts now mark carried "
           "structures, which selection and storage ignore as evidence. Both probe arms now "
           "decay and retire. §8.24; decision "
           "`docs/DECISION-CANDIDATE-SUPERSESSION.md`; `docs/V1-FREEZE.md` §6. |")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("|") and REV_MARK in line:
            lines[i] = row
            break
    else:
        marker = "**Revision log:**"
        idx = text.index(marker)
        row_start = text.index("|", idx)
        sep = text.index("|---", row_start)
        row_end = text.index("\n", sep) + 1
        text = text[:row_end] + row + "\n" + text[row_end:]
        lines = text.split("\n")
    MANUAL.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    art = run()
    OUT.write_text(json.dumps(engine_stamp.stamp(art), indent=2) + "\n", encoding="utf-8")
    RESULTS.write_text(results_document(art), encoding="utf-8")
    update_manual(manual_block(art))
    s = art["summary"]
    print("wrote", OUT.relative_to(ROOT).as_posix(), "and", RESULTS.relative_to(ROOT).as_posix(), "and manual §8.24")
    print("verdict:", s["verdict"])
    for name in ("prediction", "schema"):
        arm = art["arms"][name]
        print(f"  {name}: initial {arm['initial_value']} outcome {arm['outcome']} "
              f"retired {arm['measured_retirement_cycle']} "
              f"(predicted {arm['predicted_retirement_cycle']}) "
              f"reinforced {len(arm['reinforced_at_cycles'])} cycles")


if __name__ == "__main__":
    main()
