"""The self-sourcing reference rate, re-derived from data the rule does not judge.

`docs/AUDIT-TRACE-SPEC.md` section 11 fixes the reference a claim's own
self-sourced share is compared against.  On 2026-10-26 that reference was
**17.9 %** (802 of 4,481 distinct evidence transitions), measured by an observer
whose lookback read the sleep rows the engine never reads.  The regenerations of
the same probe on 0.16.0 read 0 on all three arms, because the engine's support
lookback excludes sleep rows and no support transition can be self-sourced.

This module writes the reference from those three committed artifacts — none of
which the reusable-knowledge rule judges — so the value carries a provenance
rather than a hand-typed past (AGENTS rules 19, 27 and 29).  `--check`
re-derives it and fails on drift; `--self-test` proves the check can fail.

Standard library only; the only file written is its own artifact, and only under
`--write`.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "self_sourced_reference.json"

ARMS = {
    "default": "docs/audit_trace_probe.json",
    "stress": "docs/audit_trace_probe_stress.json",
    "tie": "docs/audit_trace_probe_tie.json",
}

#: The block the reference is read from, and the one the disqualifier means.
POPULATION = "distinct_evidence"
POPULATIONS = ("distinct_evidence", "support_references", "all_transitions_recorded")

UNIT = ("distinct supporting transitions behind reported beliefs, deduplicated by "
        "(from_tag, to_tag, prior_event_id, to_event_id)")

#: The engine's own lookback, asserted against the frozen source rather than
#: quoted from memory: a sleep row can never be a prior event.
ENGINE_SQL = ("SELECT tags FROM events WHERE event_type != 'sleep' "
              "ORDER BY time DESC, rowid DESC LIMIT ?")

DERIVED_ON = "2026-11-23"


def _population(block: dict) -> dict:
    total = block.get("total_transitions", block.get("total"))
    return {"self_sourced": block["self_sourced"],
            "total_transitions": total,
            "self_sourced_share": block["self_sourced_share"]}


def _structural_reason() -> dict:
    source = (ROOT / "organica" / "memory.py").read_text(encoding="utf-8")
    if ENGINE_SQL not in source:
        raise AssertionError(
            "the engine's lookback is not the SQL this reference was derived "
            "against; re-derive the reference before quoting it")
    return {
        "path": "organica/memory.py",
        "sql": ENGINE_SQL,
        "consequence": ("a sleep row can never be a prior event, so the engine's "
                        "`precedes` table cannot contain a self-sourced transition "
                        "on this build: the reference is a structural zero, not an "
                        "estimated rate"),
    }


def _arms() -> dict:
    out: dict[str, dict] = {}
    for name, rel in ARMS.items():
        data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        a7 = data["A7_event_level_attribution"]
        out[name] = {
            "artifact": rel,
            "beliefs_checked": a7["beliefs_checked"],
            "pass": a7["pass"],
            "populations": {p: _population(a7[p]) for p in POPULATIONS},
            "engine_version": data.get("engine_version"),
            "engine_sha256": data.get("engine_sha256"),
        }
    return out


def build() -> dict:
    """The reference and its provenance, derived from the three commits."""
    arms = _arms()
    shares = {arms[a]["populations"][POPULATION]["self_sourced_share"] for a in arms}
    if len(shares) != 1:
        raise AssertionError(
            f"the three arms disagree on the reference population's share: {shares}")
    engines = {(arms[a]["engine_version"], arms[a]["engine_sha256"]) for a in arms}
    if len(engines) != 1:
        raise AssertionError(f"the three arms are not one engine build: {engines}")
    return {
        "kind": "self_sourced_reference",
        "reference": shares.pop(),
        "population": POPULATION,
        "unit": UNIT,
        "criterion": ("AUDIT-TRACE-SPEC section 11, condition 3: a claim's "
                      "self-sourced share must be no higher than this reference"),
        "derived_on": DERIVED_ON,
        "derived_from": ("data the rule does not judge: the audit-trace probe's "
                         "three arms, not the reusable-knowledge calibration seeds "
                         "20261201-20261205 or the confirmatory block 20261207-20261226"),
        "source_blocks": "A7_event_level_attribution",
        "structural_reason": _structural_reason(),
        "derived_document": ("no engine runs here: the reference is read from the "
                             "three arm artifacts, and each arm carries that "
                             "artifact's own engine stamp"),
        "arms": arms,
        "note": ("Re-derived 2026-11-23 under AGENTS rule 19. The superseded 17.9 % "
                 "(802 of 4,481) was measured by an observer that read sleep rows the "
                 "engine never reads; it is withdrawn as a measurement and replaced, "
                 "not re-scored. Because the value is a structural zero, the criterion "
                 "it governs has no firing condition on this build, and the "
                 "reusable-knowledge guard refuses to authorise a confirmatory set on "
                 "it (rule 25)."),
    }


def diff(expected: dict, actual: dict, path: str = "") -> list[str]:
    """Every path at which two provenance records disagree."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        out = []
        for key in sorted(set(expected) | set(actual)):
            here = f"{path}.{key}" if path else key
            if key not in expected or key not in actual:
                out.append(f"{here}: present on one side only")
            else:
                out += diff(expected[key], actual[key], here)
        return out
    if expected != actual:
        return [f"{path}: expected {expected!r}, found {actual!r}"]
    return []


def check(path: Path = OUT) -> tuple[bool, list[str]]:
    if not path.exists():
        return False, [f"no reference artifact at {path}"]
    problems = diff(build(), json.loads(path.read_text(encoding="utf-8")))
    return not problems, problems


def self_test() -> int:
    """Prove the check fails on a doctored arm and passes on the real one."""
    expected = build()
    ok, problems = check()
    if not ok:
        print("the committed reference does not match its sources:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    doctored = copy.deepcopy(expected)
    doctored["arms"]["stress"]["populations"][POPULATION]["self_sourced"] = 1
    problems = diff(expected, doctored)
    if not any("self_sourced" in p for p in problems):
        print("the check did not notice a doctored arm", file=sys.stderr)
        return 1
    print(f"self-test: the check notices a doctored arm ({len(problems)} difference(s)) "
          f"and the committed reference matches all three artifacts")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="re-derive the reference and compare it with the artifact")
    ap.add_argument("--write", action="store_true", help="rewrite the artifact")
    ap.add_argument("--self-test", action="store_true",
                    help="prove the check fails on a doctored arm")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.write:
        OUT.write_text(json.dumps(build(), indent=1, sort_keys=True) + "\n",
                       encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
        return 0
    ok, problems = check()
    if ok:
        print(f"reference {build()['reference']} matches all three audit arms")
        return 0
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
