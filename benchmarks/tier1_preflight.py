"""The Tier-1 pre-flight: G1 on a live witness, its negative controls, and D2's persistence gate.

`benchmarks/run_matrix.py` used to verify the reference arm on the campaign's own stimulus at
the campaign's snapshot cycle. On 0.13.0 that reported `FULL produced no theories`, because the
arm plateaus through cycle 36 and collapses across 37-39 while the snapshot is taken at 40
(`docs/DECISION-G1-WITNESS.md`). The check was not wrong about the count; it was reading a
terminal value as a property of the arm.

This module runs the adopted re-base (D1) and the gate the campaign never had (D2), and records
both in one artifact so a pass and a block are readable from the same file:

* **D1, the witness.** G1 runs on `L3_hub1_t3_mixed`, where the reference arm holds 12 beliefs
  and 4 theories at cycle 40, and reads the whole per-cycle trace: a colony fails only when it
  forms no theory in *any* cycle.
* **D1, the negative controls.** The suppression arms are the controls: `NO_DREAMS` must record
  zero dreams in every cycle and `NO_QUESTIONS` zero questions. A control that stops suppressing
  fails the pre-flight.
* **D1, the disclosure.** The campaign stimulus's own trace is recorded beside the pass, so the
  `L1` collapse G1 used to mistake for a broken arm stays visible instead of being replaced.
* **D2, the gate.** The reference arm is run on the campaign stimulus to the campaign horizon,
  and the first cycle with zero theories after a positive one is read. If that cycle is at or
  before the horizon, the campaign is reported **not measurable as designed**; the horizon is
  not shortened to fit the arm.

    python -m benchmarks.tier1_preflight                  # run the pre-flight, write artifact + page
    python -m benchmarks.tier1_preflight --render         # rebuild the page from the artifact
    python -m benchmarks.tier1_preflight --check          # verify the page and the verdict

The record is a run, so it is stamped with the engine's bytes and the writer (unlike a derived
page). `--check` never runs the engine. Standard library only; no engine file is changed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmarks import engine_stamp
from benchmarks import force_matrix as fm

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "tier1_preflight.json"
PAGE = ROOT / "docs" / "TIER1-PREFLIGHT.md"

VERDICTS = ("PASSES", "G1_FAILS", "REFERENCE_ARM_BROKEN", "CAMPAIGN_NOT_MEASURABLE")

MEANINGS = {
    "PASSES": "G1 holds on the live witness and the reference arm is alive at the campaign horizon",
    "G1_FAILS": "a colony or a negative control failed on the witness; the campaign must not launch",
    "REFERENCE_ARM_BROKEN": "the reference arm formed no theory on the campaign stimulus at all",
    "CAMPAIGN_NOT_MEASURABLE": "G1 holds, but the reference arm dies before the campaign horizon",
}


def decide(g1_problems: list, persistence: str) -> str:
    """One verdict, from the witness result and D2's reading. Pure, so the tests can drive it."""
    if g1_problems:
        return "G1_FAILS"
    if persistence == "REFERENCE_ARM_BROKEN":
        return "REFERENCE_ARM_BROKEN"
    if persistence == "ALIVE_AT_HORIZON":
        return "PASSES"
    return "CAMPAIGN_NOT_MEASURABLE"


def build(witness_cycles: int = fm.WITNESS_CYCLES, horizon: int = 3000,
          seed: int = fm.VERIFY_SEED) -> dict:
    """Run the witness, the controls and the persistence gate, and return the record."""
    checks, problems = fm.verify_colonies(fm.design_events(fm.WITNESS_DESIGN),
                                          witness_cycles)
    by_name = {c["colony"]: c for c in checks}
    negatives = fm.negative_control_problems(checks)
    full = by_name["FULL"]
    campaign = fm.trace_reference(fm.CAMPAIGN_DESIGN, horizon, seed)
    persistence = fm.persistence_verdict(campaign)
    verdict = decide(problems, persistence)
    return {
        "kind": "tier1_preflight",
        "date": "2026-11-09",
        "seed": seed,
        "witness": {
            "design": fm.WITNESS_DESIGN,
            "cycles": witness_cycles,
            "reference_theories": full["series"]["theories"],
            "reference_peak": max(full["series"]["theories"] or [0]),
            "reference_theory_cycles": full["theory_cycles"],
            "colonies": checks,
            "problems": list(problems),
        },
        "negative_controls": {
            "colonies": ["NO_DREAMS", "NO_QUESTIONS"],
            "dreams_max": max(by_name["NO_DREAMS"]["series"]["dreams"] or [0]),
            "questions_max": max(by_name["NO_QUESTIONS"]["series"]["questions"] or [0]),
            "problems": negatives,
            "passed": not negatives,
        },
        "campaign_stimulus": campaign,
        "persistence": {
            "verdict": persistence,
            "horizon": horizon,
            "first_zero_cycle": campaign["first_zero_cycle"],
            "peak": campaign["peak"],
        },
        "verdict": verdict,
        "launch_blocked": verdict != "PASSES",
    }


def render_page(record: dict) -> str:
    witness = record["witness"]
    controls = record["negative_controls"]
    campaign = record["campaign_stimulus"]
    persistence = record["persistence"]
    lines = [
        "# Tier-1 pre-flight",
        "",
        "**Generated** from `docs/tier1_preflight.json` by",
        "`python -m benchmarks.tier1_preflight --render`. Do not edit this file by hand.",
        "The record is stamped with the engine's bytes and the writer.",
        "",
        "**Verdict: `%s` — %s.**" % (record["verdict"], MEANINGS[record["verdict"]]),
        "",
        "Decision: `docs/DECISION-G1-WITNESS.md` (ADOPTED, D1 and D2). The campaign's own",
        "stimulus is `%s`; the witness G1 reads is `%s`." % (
            campaign["design"], witness["design"]),
        "",
        "## G1 on the live witness",
        "",
        ("The reference arm formed a theory in %d of %d cycles (peak %d). A colony fails only "
         "when it forms no theory in any cycle.") % (
            witness["reference_theory_cycles"], witness["cycles"], witness["reference_peak"]),
        "",
        "| colony | retention | contradiction scale | theory cycles | theories | beliefs | dreams | questions |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for colony in witness["colonies"]:
        lines.append("| %s | %s | %s | %d | %d | %d | %d | %d |" % (
            colony["colony"], colony["retention_policy"], colony["contradiction_scale"],
            colony["theory_cycles"], colony["theories"], colony["beliefs"],
            colony["dreams"], colony["questions"]))
    lines += ["", "## Negative controls", ""]
    lines += [
        "The suppression arms are the controls. They must report zero in every cycle, not only",
        "in the last one:",
        "",
        "| control | layer | maximum over the trace |",
        "| --- | --- | --- |",
        "| `NO_DREAMS` | dreams | %d |" % controls["dreams_max"],
        "| `NO_QUESTIONS` | questions | %d |" % controls["questions_max"],
        "",
        "**Controls passed: %s.**" % ("yes" if controls["passed"] else "no"),
        "",
        "## The campaign stimulus, disclosed",
        "",
        "The witness changed; the collapse that motivated it did not. Run on `%s` for %d cycles:" % (
            campaign["design"], campaign["cycles_run"]),
        "",
        "| quantity | value |",
        "| --- | --- |",
        "| peak theories | %d |" % campaign["peak"],
        "| first zero after a positive cycle | %s |" % (
            campaign["first_zero_cycle"] if campaign["first_zero_cycle"] is not None else "none"),
        "| cycles run | %d |" % campaign["cycles_run"],
        "",
        "## D2, the persistence gate",
        "",
        "| quantity | value |",
        "| --- | --- |",
        "| horizon | %d |" % persistence["horizon"],
        "| first zero cycle | %s |" % (
            persistence["first_zero_cycle"] if persistence["first_zero_cycle"] is not None
            else "none"),
        "| verdict | `%s` |" % persistence["verdict"],
        "",
        "A first zero at or before the horizon blocks the campaign: the arm is not alive across",
        "the window the campaign would measure, and the horizon is not shortened to fit it.",
        "",
        "## What this does not do",
        "",
        "- **It does not restore persistence.** D3 is PENDING; that is a cognition change and needs",
        "  its own preregistration.",
        "- **It does not run the campaign.** The verdict says whether the campaign may launch.",
        "- **It does not re-score the recorded G1.** The `v0.7.0-14-gea8e6d2` artifact remains what",
        "  it measured; this pre-flight is about whether a campaign can be run on 0.13.0.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true", help="rebuild the page from the artifact")
    parser.add_argument("--check", action="store_true", help="verify the page and the verdict")
    parser.add_argument("--cycles", type=int, default=fm.WITNESS_CYCLES,
                        help="witness cycles (40 keeps the L3 arm alive)")
    parser.add_argument("--horizon", type=int, default=3000, help="the campaign horizon D2 tests")
    args = parser.parse_args(argv)

    if args.render or args.check:
        if not ARTIFACT.exists():
            print("FAIL: no pre-flight artifact to read:", ARTIFACT.relative_to(ROOT))
            return 1
        record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        expected = render_page(record)
        if args.check:
            if record.get("verdict") not in VERDICTS:
                print("FAIL: unknown verdict %r" % record.get("verdict"))
                return 1
            if PAGE.read_text(encoding="utf-8") != expected:
                print("FAIL: docs/TIER1-PREFLIGHT.md is stale; rerun --render")
                return 1
            if record["launch_blocked"] != (record["verdict"] != "PASSES"):
                print("FAIL: launch_blocked disagrees with the verdict")
                return 1
            print("pre-flight: %s (%s)" % (record["verdict"],
                                           MEANINGS[record["verdict"]]))
            return 0
        PAGE.write_text(expected, encoding="utf-8")
        print("rebuilt", PAGE.relative_to(ROOT))
        return 0

    record = engine_stamp.stamp(build(args.cycles, args.horizon))
    ARTIFACT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    PAGE.write_text(render_page(record), encoding="utf-8")
    print("pre-flight: %s" % record["verdict"])
    print("  witness %s: theory cycles %d/%d, peak %d" % (
        record["witness"]["design"], record["witness"]["reference_theory_cycles"],
        record["witness"]["cycles"], record["witness"]["reference_peak"]))
    print("  controls passed: %s" % record["negative_controls"]["passed"])
    print("  campaign %s: first zero %s against horizon %d (%s)" % (
        record["campaign_stimulus"]["design"],
        record["persistence"]["first_zero_cycle"], record["persistence"]["horizon"],
        record["persistence"]["verdict"]))
    return 0 if not record["launch_blocked"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
