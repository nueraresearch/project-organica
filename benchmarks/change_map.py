"""Map every post-freeze engine change to a mechanism and a falsifier.

The engine-change audit (``docs/ENGINE-CHANGE-AUDIT.md``) inventories what moved
after the freeze and says plainly that its fourth column is reconstruction from
commit messages. This module is that column's replacement: one row per change
group, each naming the failure the change could move, the mechanism by which it
would move it, and a falsifier that would show the mechanism false.

Two rules do the excluding rather than taste. A row with no failure to move is
not a campaign row, and a row whose positive and negative outcomes lead to the
same decision is not worth running (AGENTS.md rule 30), so the validator rejects
both instead of letting them travel inside a bundled change.

Coverage is derived from git: every commit that touched ``organica/`` since the
freeze tag must be claimed by exactly one row. A new engine commit therefore
fails the check until the map explains it, which is the property the audit said
did not exist.

No figure is stored in the rendered document. Measured values stay in the
artifacts the rows name, so the map cannot drift from a measurement it does not
hold. A row that has been run carries a ``result``: a verdict and the artifact
it was read from, never the numbers, which stay where they were measured.

Nothing is written in ``--check`` mode.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "docs" / "engine_change_failure_map.json"
DOC = ROOT / "docs" / "ENGINE-CHANGE-FAILURE-MAP.md"
FREEZE_TAG = "v0.9.0"
ENGINE = "organica"

KINDS = ("recorded_failure", "open_question", "none")
STATUSES = ("stays", "excluded")
RESULT_VERDICTS = ("FALSIFIED", "REPRODUCES", "INTERMITTENT", "INCONCLUSIVE")
MIN_TEXT = 60


def load():
    return json.loads(MAP.read_text(encoding="utf-8"))


def commits_since_freeze():
    """The commits that touched the engine since the freeze, read from git."""
    proc = subprocess.run(
        ["git", "log", "--format=%h", "%s..HEAD" % FREEZE_TAG, "--", ENGINE],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError("git log failed: " + proc.stderr.strip())
    return sorted(line.strip() for line in proc.stdout.splitlines() if line.strip())


def validate(data):
    errors = []
    rows = data["changes"]
    seen_ids = set()
    claimed = {}

    for row in rows:
        rid = row.get("id", "")
        if not rid:
            errors.append("a row has no id")
        elif rid in seen_ids:
            errors.append("%s: duplicate id" % rid)
        seen_ids.add(rid)

        status = row.get("status")
        if status not in STATUSES:
            errors.append("%s: unknown status %r" % (rid, status))

        for commit in row.get("commits", []):
            if commit in claimed:
                errors.append(
                    "%s: commit %s is also claimed by %s" % (rid, commit, claimed[commit])
                )
            claimed[commit] = rid

        failure = row.get("failure", {})
        kind = failure.get("kind")
        if kind not in KINDS:
            errors.append("%s: unknown failure kind %r" % (rid, kind))
        artifact = failure.get("artifact")
        if artifact and not (ROOT / artifact).exists():
            errors.append("%s: failure artifact does not exist: %s" % (rid, artifact))
        if kind != "none" and not artifact:
            errors.append("%s: names a failure without an artifact" % rid)

        result = row.get("result")
        if result:
            if status != "stays":
                errors.append("%s: carries a result but is not in the campaign" % rid)
            if result.get("verdict") not in RESULT_VERDICTS:
                errors.append("%s: unknown result verdict %r" % (rid, result.get("verdict")))
            result_artifact = result.get("artifact")
            if not result_artifact:
                errors.append("%s: a result must name the artifact it was read from" % rid)
            elif not (ROOT / result_artifact).exists():
                errors.append(
                    "%s: result artifact does not exist: %s" % (rid, result_artifact)
                )
            elif result_artifact == artifact:
                errors.append(
                    "%s: the result artifact is the pre-change artifact; the falsifier writes "
                    "its own" % rid
                )
            if row.get("measured_on_that_build") is not True:
                errors.append(
                    "%s: a result means the falsifier ran on this build, so "
                    "measured_on_that_build must be true" % rid
                )
            if len(result.get("note", "")) < MIN_TEXT:
                errors.append("%s: result note is too thin to say what it means" % rid)

        if status == "stays":
            if kind == "none":
                errors.append("%s: stays in the campaign with no failure to move" % rid)
            if len(row.get("mechanism", "")) < MIN_TEXT:
                errors.append("%s: mechanism is too thin to be testable" % rid)
            if len(row.get("falsifier", "")) < MIN_TEXT:
                errors.append("%s: falsifier is too thin to fail" % rid)
            if not row.get("observables"):
                errors.append("%s: no observables, so the falsifier cannot be run" % rid)
            if not row.get("prior_measurement"):
                errors.append("%s: does not say what the pre-change measurement was" % rid)
            positive = row.get("decision_if_positive", "").strip()
            negative = row.get("decision_if_negative", "").strip()
            if not positive or not negative:
                errors.append("%s: a decision is missing" % rid)
            elif positive == negative:
                errors.append(
                    "%s: the two decisions are the same, so running it changes no design" % rid
                )
        else:
            if not row.get("reason", "").strip():
                errors.append("%s: excluded without a reason" % rid)

    live = commits_since_freeze()
    unclaimed = sorted(set(live) - set(claimed))
    unknown = sorted(set(claimed) - set(live))
    if unclaimed:
        errors.append("engine commits with no row: %s" % ", ".join(unclaimed))
    if unknown:
        errors.append(
            "rows cite commits that are not in %s..HEAD: %s" % (FREEZE_TAG, ", ".join(unknown))
        )

    return {
        "passed": not errors,
        "errors": errors,
        "rows": len(rows),
        "commits": len(live),
        "stays": sum(1 for row in rows if row.get("status") == "stays"),
        "excluded": sum(1 for row in rows if row.get("status") == "excluded"),
    }


def _measured(value):
    return {True: "yes", False: "no", "partial": "in part"}.get(value, "no")


def render(data, report):
    lines = [
        "# Change-to-failure map",
        "",
        "**Generated from `docs/engine_change_failure_map.json`. Do not edit this file.** Rebuild",
        "with `python -m benchmarks.change_map`; `--check` validates and compares without writing.",
        "",
        "The engine-change audit (`docs/ENGINE-CHANGE-AUDIT.md`) lists what moved after the freeze and",
        "says plainly that its fourth column is reconstruction from commit messages. This map is that",
        "column's replacement: one row per change group, each naming the failure the change could move,",
        "the mechanism by which it would move it, and a falsifier that would show the mechanism false.",
        "",
        "**No measured figure is stated on this page.** Every value lives in the artifact its row",
        "names, so the map cannot drift from a measurement it does not hold.",
        "",
        "## Coverage",
        "",
        "- **%d** commits touched `%s` between `%s` and HEAD, and every one is claimed below."
        % (report["commits"], ENGINE, data["freeze_tag"]),
        "- **%d** rows: **%d** stay in the campaign, **%d** are excluded."
        % (report["rows"], report["stays"], report["excluded"]),
        "- A row stays only if it names a failure with an artifact, a mechanism, a falsifier,",
        "  observables, a pre-change measurement, and two decisions that differ. A diagnostic whose",
        "  two outcomes lead to the same place spends the resource and changes no design, so the",
        "  validator excludes it (AGENTS.md rule 30).",
        "- Coverage is read from git, not typed: a new commit under `%s` fails the check until a row" % ENGINE,
        "  explains it.",
        "",
        "## The map",
        "",
        "| Row | Commits | Change | Failure | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in data["changes"]:
        failure = row["failure"]
        if failure["kind"] == "none":
            target = "none recorded"
        else:
            target = "%s in `%s`" % (failure["kind"].replace("_", " "), failure["artifact"])
        lines.append(
            "| %s | %s | %s | %s | %s |"
            % (
                row["id"],
                ", ".join("`%s`" % c for c in row["commits"]),
                row["title"],
                target,
                row["status"],
            )
        )

    for row in data["changes"]:
        failure = row["failure"]
        lines += [
            "",
            "## %s — %s" % (row["id"], row["title"]),
            "",
            "**Commits.** %s" % ", ".join("`%s`" % c for c in row["commits"]),
            "",
            "**What changed.** %s" % row["what_changed"],
            "",
            "**Failure.** %s" % failure["note"],
            "",
        ]
        if failure.get("artifact"):
            lines += ["**Artifact.** `%s`" % failure["artifact"], ""]
        lines += [
            "**Measured on that build.** %s." % _measured(row.get("measured_on_that_build")),
            "",
            "**Pre-change measurement.** %s" % row["prior_measurement"],
            "",
            "**Mechanism.** %s" % row["mechanism"],
            "",
            "**Falsifier.** %s" % row["falsifier"],
            "",
        ]
        if row.get("observables"):
            lines += ["**Observables.** " + "; ".join(row["observables"]), ""]
        if row.get("result"):
            result = row["result"]
            lines += [
                "**Result.** **%s** — %s Read from `%s`."
                % (result["verdict"], result["note"], result["artifact"]),
                "",
            ]
        lines += [
            "**If it holds.** %s" % row["decision_if_positive"],
            "",
            "**If it does not.** %s" % row["decision_if_negative"],
            "",
        ]
        if row["status"] == "excluded":
            lines += ["**Why it is not in the campaign.** %s" % row["reason"], ""]

    lines += [
        "## What this map does not establish",
        "",
        "- **It does not say any change improved anything.** A mechanism is a hypothesis about how a",
        "  change could move a failure; the falsifier is how that hypothesis would be shown wrong.",
        "- **It does not rank the rows.** A row stays because it is testable, not because it is",
        "  promising, and no row is placed in a run order by this document.",
        "- **It does not cover anything outside the engine.** Benchmarks, harnesses, documentation and",
        "  the owner's decisions are free to change and are not part of the engine's identity; the pin",
        "  in `docs/engine_pin.json` is what fixes that identity.",
        "- **It is not a preregistration.** A preregistration commits thresholds before a run; this",
        "  map only says which hypotheses are worth committing to, and the campaign still has to fix",
        "  its comparators and its criteria before any cell.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the map and compare the document against a fresh render, without writing",
    )
    args = parser.parse_args(argv)

    data = load()
    report = validate(data)
    if not report["passed"]:
        for error in report["errors"]:
            print("FAIL:", error)
        return 1

    if args.check:
        if not DOC.exists():
            print("FAIL: the map document does not exist: %s" % DOC)
            return 1
        if DOC.read_text(encoding="utf-8") != render(data, report):
            print("FAIL: %s is stale; rebuild with python -m benchmarks.change_map" % DOC)
            return 1
    else:
        DOC.write_text(render(data, report), encoding="utf-8")

    print(
        "change map: %d rows over %d commits, %d stay / %d excluded"
        % (report["rows"], report["commits"], report["stays"], report["excluded"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
