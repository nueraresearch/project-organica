"""Render the A1 board — both halves — from its sources.

The board used to be hand-written prose with a one-directional guard. Then the decision half became a
render of `docs/decisions.json`, which closed the "a row outlives its status" direction for decisions
only. This module finishes the job:

* the **decision block** is rendered from `docs/decisions.json` (status, id, the record's own scope line);
* the **branch block** is rendered from `docs/a1_board_manifest.json`, where each branch names what
  settles it — a decision, an artifact with strings it must contain, a pair of acts whose `Status:`
  lines decide it, or a conditional on another decision — and the check that proves it.

No state is typed in either block. A branch whose artifact is missing renders `OPEN — ARTIFACT NOT
PROVEN` rather than being dropped; an act renders `NOT SIGNED` until every named act's own status line
says `SIGNED`. `--check` compares both blocks against their renders, so a change on either side leaves
a stale board rather than a passing one. `--verify` runs the checks the manifest points at.

    python -m benchmarks.a1_board --write
    python -m benchmarks.a1_board --check
    python -m benchmarks.a1_board --verify
    python -m benchmarks.a1_board --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX_PATH = DOCS / "decisions.json"
MANIFEST_PATH = DOCS / "a1_board_manifest.json"
CHECKLIST_PATH = DOCS / "A1-PRE-FREEZE-CHECKLIST.md"
START = "<!-- a1-board:start -->"
END = "<!-- a1-board:end -->"
ART_START = "<!-- a1-artifacts:start -->"
ART_END = "<!-- a1-artifacts:end -->"
PREFIX = "DECISION-A1"
SCOPE_LIMIT = 210
KINDS = {"decision", "artifact", "act", "conditional", "absent"}


# --------------------------------------------------------------------------------------- decisions


def _index() -> dict:
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def _text(decision_id: str) -> str:
    return (DOCS / ("%s.md" % decision_id)).read_text(encoding="utf-8")


def _clip(text: str) -> str:
    text = " ".join(text.replace("|", "/").split())
    if text:
        text = text[0].upper() + text[1:]
    if len(text) <= SCOPE_LIMIT:
        return text
    window = text[:SCOPE_LIMIT]
    for cut in (window.rfind(". "), window.rfind("; "), window.rfind(" ")):
        if cut > SCOPE_LIMIT // 2:
            return window[:cut].rstrip(",;:.") + " …"
    return window.rstrip(",;:") + " …"


def _scope(decision_id: str) -> str:
    text = _text(decision_id)
    match = re.search(r"^\*\*Scope:\*\*\s*(.+?)(?=\n\s*\n)", text, re.M | re.S)
    if match:
        return _clip(match.group(1))
    title = re.search(r"^#\s+(.+)$", text, re.M)
    if not title:
        return "—"
    return _clip(re.sub(r"\s+—\s+(decision record|a decision record).*$", "", title.group(1)))


def _state(entry: dict) -> str:
    status = entry.get("status")
    if status == "ADOPTED":
        return "**ADOPTED**"
    if status == "WITHDRAWN":
        return "**WITHDRAWN**"
    if "FOR OWNER ADOPTION" in (entry.get("status_quote") or ""):
        return "**AWAITING SIGNATURE**"
    return "**PENDING — NOT BLOCKING**"


def _rank(entry: dict) -> tuple:
    order = {"**AWAITING SIGNATURE**": 0, "**PENDING — NOT BLOCKING**": 1,
             "**WITHDRAWN**": 2, "**ADOPTED**": 3}[_state(entry)]
    return (order, entry.get("date") or "", entry["decision_id"])


def rows(entries: list[dict] | None = None) -> list[dict]:
    entries = entries if entries is not None else _index()["decisions"]
    a1 = [entry for entry in entries if entry["decision_id"].startswith(PREFIX)]
    return [{"id": entry["decision_id"], "state": _state(entry), "date": entry.get("date"),
             "scope": _scope(entry["decision_id"])} for entry in sorted(a1, key=_rank)]


def _non_a1_pending(entries: list[dict]) -> list[str]:
    return sorted(entry["decision_id"] for entry in entries
                  if entry["status"] == "PENDING"
                  and not entry["decision_id"].startswith(PREFIX))


def render(entries: list[dict] | None = None) -> str:
    entries = entries if entries is not None else _index()["decisions"]
    table = rows(entries)
    counts = {state: sum(1 for row in table if row["state"] == state)
              for state in ("**AWAITING SIGNATURE**", "**PENDING — NOT BLOCKING**",
                            "**WITHDRAWN**", "**ADOPTED**")}
    header = ("**Owner decisions** — %d A1 records in `docs/decisions.json`: %d adopted, %d withdrawn, "
              "%d awaiting signature, %d pending and blocking nothing. Generated from the index and each "
              "record's own scope line; a status change on disk makes this block stale until it is "
              "regenerated." % (len(table), counts["**ADOPTED**"], counts["**WITHDRAWN**"],
                                counts["**AWAITING SIGNATURE**"],
                                counts["**PENDING — NOT BLOCKING**"]))
    lines = [header, "",
             "| Decision | State | What it decides |",
             "| --- | --- | --- |"]
    for row in table:
        lines.append("| [`%s`](%s.md) | %s | %s |"
                     % (row["id"], row["id"], row["state"], row["scope"]))
    outside = _non_a1_pending(entries)
    if outside:
        lines += ["", "_Also `PENDING` in the index, outside A1 (`PENDING` is not an open question; these are decided "
                  "and not in force): %s._" % ", ".join("`%s`" % name for name in outside)]
    return "\n".join(lines)


# ----------------------------------------------------------------------------------------- branches


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _present(text: str, needle: str) -> bool:
    """Identifier-like needles must match whole; prose is matched as it is written.

    A plain substring test accepted `CONTROL_NOT_SCORED_PROBE` for `CONTROL_NOT_SCORED`, so a
    renamed symbol would have proved the branch. Word boundaries close that.
    """
    if IDENTIFIER.match(needle):
        return re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(needle), text) is not None
    return needle in text


def _has_strings(spec: dict) -> bool:
    path = ROOT / spec["path"]
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return all(_present(text, item) for item in spec.get("strings") or [])


def _status_lines(paths: list[str]) -> list[str]:
    found = []
    for name in paths:
        path = ROOT / name
        if not path.exists():
            found.append("MISSING")
            continue
        match = re.search(r"^\*\*Status:\*\*\s*(.+)$", path.read_text(encoding="utf-8"), re.M)
        found.append((match.group(1) if match else "NO STATUS LINE").strip("`"))
    return found


def branch_state(branch: dict, entries: list[dict] | None = None) -> str:
    entries = entries if entries is not None else _index()["decisions"]
    by_id = {entry["decision_id"]: entry for entry in entries}
    kind = branch.get("kind")
    if kind == "decision":
        entry = by_id.get(branch["decision"])
        if entry is None:
            return "**OPEN — DECISION NOT INDEXED**"
        state = _state(entry)
        if state == "**ADOPTED**":
            return "**CLOSED — ADOPTED**"
        return state
    if kind == "artifact":
        ok = (ROOT / branch["artifact"]).exists() and all(_has_strings(spec)
                                                          for spec in branch.get("contains") or [])
        return "**CLOSED — ARTIFACT EXISTS**" if ok else "**OPEN — ARTIFACT NOT PROVEN**"
    if kind == "act":
        statuses = _status_lines(branch.get("docs") or [])
        signed = statuses and all("SIGNED" in status for status in statuses)
        return "**CLOSED — SIGNED**" if signed else "**NOT SIGNED**"
    if kind == "conditional":
        entry = by_id.get(branch["when_pending"])
        holds = all(_has_strings(spec) for spec in branch.get("contains") or [])
        if entry is not None and entry["status"] == "PENDING" and holds:
            return "**%s**" % branch["open_state"]
        restated = all(_has_strings(spec) for spec in branch.get("restated") or [])
        return "**%s**" % (branch["closed_state"] if restated else "OPEN — RESTATEMENT MISSING")
    if kind == "absent":
        if any((ROOT / name).exists() for name in branch.get("must_not_exist") or []):
            return "**REVIEW — SOMETHING APPEARED**"
        return "**%s**" % branch["state"]
    return "**OPEN — UNKNOWN KIND**"


def branch_rows(entries: list[dict] | None = None,
                branches: list[dict] | None = None) -> list[dict]:
    branches = branches if branches is not None else _manifest()["branches"]
    return [{"id": branch["id"], "branch": branch["branch"],
             "state": branch_state(branch, entries), "note": branch.get("note") or "",
             "artifact": branch.get("artifact") or branch.get("decision") or "",
             "proved_by": branch.get("proved_by") or []} for branch in branches]


def _link(target: str) -> str:
    """A link that resolves from `docs/`, where the board lives."""
    if target.startswith("docs/"):
        name = target.split("/", 1)[1]
        return "[`%s`](%s)" % (name, name)
    if target.startswith(("tests/", "benchmarks/")):
        return "[`%s`](../%s)" % (target, target)
    return "[`%s`](%s.md)" % (target, target)


def render_branches(entries: list[dict] | None = None,
                    branches: list[dict] | None = None) -> str:
    table = branch_rows(entries, branches)
    closed = sum(1 for row in table if "CLOSED" in row["state"])
    header = ("**Branches and artifacts** — %d branches, %d closed. Each state is derived from the record, "
              "artifact or act named in its row, via `docs/a1_board_manifest.json`; nothing in this table is "
              "typed, and a branch whose artifact is missing renders `OPEN — ARTIFACT NOT PROVEN`."
              % (len(table), closed))
    lines = [header, "",
             "| Branch | State | What the row rests on | Check |",
             "| --- | --- | --- | --- |"]
    for row in table:
        rests = row["note"]
        if row["artifact"]:
            rests = "%s — %s" % (rests, _link(row["artifact"])) if rests else _link(row["artifact"])
        checks = ", ".join(_link(target) for target in row["proved_by"]) or "—"
        lines.append("| %s | %s | %s | %s |" % (row["branch"], row["state"], rests, checks))
    return "\n".join(lines)


# ------------------------------------------------------------------------------------------ blocks


def _span(text: str, start: str, end: str) -> tuple[int, int] | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    left = text.index(start) + len(start)
    right = text.index(end)
    if right < left:
        return None
    return left, right


def block(text: str) -> str | None:
    span = _span(text, START, END)
    return None if span is None else text[span[0]:span[1]].strip("\n")


def artifact_block(text: str) -> str | None:
    span = _span(text, ART_START, ART_END)
    return None if span is None else text[span[0]:span[1]].strip("\n")


def splice(text: str, body: str, start: str = START, end: str = END) -> str:
    span = _span(text, start, end)
    if span is None:
        raise ValueError("the checklist has no single %s / %s pair" % (start, end))
    return text[:span[0]] + "\n" + body + "\n" + text[span[1]:]


def manifest_problems(branches: list[dict] | None = None,
                      entries: list[dict] | None = None) -> list[str]:
    branches = branches if branches is not None else _manifest()["branches"]
    entries = entries if entries is not None else _index()["decisions"]
    by_id = {entry["decision_id"] for entry in entries}
    found: list[str] = []
    ids = [branch.get("id") for branch in branches]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        found.append("duplicate branch ids: %r" % (duplicates,))
    for branch in branches:
        label = branch.get("id", "?")
        if branch.get("kind") not in KINDS:
            found.append("%s: unknown kind %r" % (label, branch.get("kind")))
        if branch.get("kind") == "decision" and branch.get("decision") not in by_id:
            found.append("%s: names an unindexed decision %r" % (label, branch.get("decision")))
        if branch.get("kind") == "conditional" and branch.get("when_pending") not in by_id:
            found.append("%s: conditional on an unindexed decision" % label)
        for target in branch.get("proved_by") or []:
            if not (ROOT / target).exists():
                found.append("%s: the check it names does not exist: %s" % (label, target))
        for spec in (branch.get("contains") or []) + (branch.get("restated") or []):
            if not (ROOT / spec["path"]).exists():
                found.append("%s: names a missing artifact: %s" % (label, spec["path"]))
    return found


def block_problems(text: str, entries: list[dict] | None = None,
                   branches: list[dict] | None = None) -> list[str]:
    found: list[str] = []
    if _span(text, START, END) is None:
        found.append("the decision-block markers are missing, duplicated or out of order")
    elif block(text) != render(entries):
        found.append("the generated decision block is stale against docs/decisions.json")
    if _span(text, ART_START, ART_END) is None:
        found.append("the branch-block markers are missing, duplicated or out of order")
    elif artifact_block(text) != render_branches(entries, branches):
        found.append("the generated branch block is stale against docs/a1_board_manifest.json")
    entries = entries if entries is not None else _index()["decisions"]
    current = block(text) or ""
    for entry in entries:
        if not entry["decision_id"].startswith(PREFIX):
            continue
        occurrences = current.count("[`%s`]" % entry["decision_id"])
        if occurrences != 1:
            found.append("%s appears %d times in the generated block, not once"
                         % (entry["decision_id"], occurrences))
    rows_now = artifact_block(text) or ""
    for row in branch_rows(entries, branches):
        occurrences = rows_now.count("| %s |" % row["branch"])
        if occurrences != 1:
            found.append("branch %s appears %d times in the branch block, not once"
                         % (row["id"], occurrences))
    found += manifest_problems(branches, entries)
    return found


def written_text() -> str:
    text = CHECKLIST_PATH.read_text(encoding="utf-8")
    text = splice(text, render())
    return splice(text, render_branches(), ART_START, ART_END)


def write() -> int:
    try:
        updated = written_text()
    except ValueError as error:
        print("FAIL:", error)
        return 1
    CHECKLIST_PATH.write_text(updated, encoding="utf-8")
    print("wrote both blocks into %s" % CHECKLIST_PATH.name)
    print("  " + render().splitlines()[0])
    print("  " + render_branches().splitlines()[0])
    return 0


def check() -> int:
    found = block_problems(CHECKLIST_PATH.read_text(encoding="utf-8"))
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    table = rows()
    branches = branch_rows()
    print("A1 board: clean; %d A1 records (%d awaiting signature), %d branches (%d closed)"
          % (len(table), sum(1 for row in table if row["state"] == "**AWAITING SIGNATURE**"),
             len(branches), sum(1 for row in branches if "CLOSED" in row["state"])))
    return 0


def verify() -> int:
    """Run the checks the manifest points at, so the mapping is not decorative."""
    targets = sorted({target for branch in _manifest()["branches"]
                      for target in branch.get("proved_by") or []
                      if target.startswith("tests/")})
    if not targets:
        print("FAIL: the manifest points at no test")
        return 1
    command = [sys.executable, "-m", "pytest", "-q", *targets]
    print("verifying %d checks: %s" % (len(targets), " ".join(targets)))
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        print("FAIL: a check the manifest relies on did not pass")
        return 1
    print("A1 board: every check the manifest names passes")
    return 0


def self_test() -> list[str]:
    found: list[str] = []
    entries = _index()["decisions"]
    branches = _manifest()["branches"]
    text = CHECKLIST_PATH.read_text(encoding="utf-8")
    if block_problems(text, entries, branches):
        found.append("the committed checklist was rejected: %s"
                     % block_problems(text, entries, branches))
    # A status flip on disk must make the decision block stale.
    flipped = json.loads(json.dumps(entries))
    target = next(entry for entry in flipped if entry["decision_id"] == "DECISION-A1-C1-CEILING")
    target["status"] = "ADOPTED"
    target["status_quote"] = "ADOPTED"
    if not any("decision block is stale" in problem
               for problem in block_problems(text, flipped, branches)):
        found.append("an adopted decision left its AWAITING SIGNATURE row in place")
    # A branch whose artifact disappears must render OPEN rather than pass.
    broken = json.loads(json.dumps(branches))
    victim = next(branch for branch in broken if branch["id"] == "c4-completeness")
    victim["contains"] = [{"path": "benchmarks/a1_arms.py", "strings": ["NOT_A_REAL_SYMBOL"]}]
    if "OPEN" not in branch_state(victim, entries):
        found.append("a branch with an unmet artifact assertion rendered closed")
    # A decision-kind branch follows the index.
    contract = next(branch for branch in broken if branch["id"] == "competence-contract")
    withdrawn = json.loads(json.dumps(flipped))
    for entry in withdrawn:
        if entry["decision_id"] == "DECISION-A1-C8-NMIN":
            entry["status"] = "WITHDRAWN"
    if "WITHDRAWN" not in branch_state(contract, withdrawn):
        found.append("a withdrawn decision left its branch closed")
    # A duplicated marker makes the block unlocatable.
    if not block_problems(text.replace(END, END + "\n" + END, 1), entries, branches):
        found.append("duplicated markers were accepted")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--verify", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        return write()
    if args.check:
        return check()
    if args.verify:
        return verify()
    found = self_test()
    for problem in found:
        print("FAIL:", problem)
    if not found:
        print("A1 board: self-test clean")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
