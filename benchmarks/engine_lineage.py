"""Engine lineage: a recorded successor that provably serves the same rows.

The pin answers one question -- are these the bytes the pin recorded? -- and every stamped
artifact repeats the answer it was written under. That is what makes a measurement attributable,
and it is also why a behaviour-preserving edit used to be unable to land: changing a comment in
the engine invalidates an artifact whose numbers did not move, so the only ways forward were to
re-run the measurement (re-deriving its verdict) or to write a new stamp onto it (faking a run).

Neither is acceptable. This record is the third way: a **link** from the byte set an artifact
was written under to a successor byte set, with the behaviour claim proved rather than asserted.

A link carries

``from`` / ``to``
    the two engine digests (`engine_stamp.engine_sha256`), 64 hex characters each.
``decision``
    the decision that authorises the change. It must be recorded as ``ADOPTED`` in
    ``docs/decisions.json``: a lineage is a governance act, not an edit.
``proof``
    every block-canary cell digest recorded in ``docs/block_canaries.json``, mapped by block.
    That file is stamped with the *predecessor* build, so its digests are the rows the old
    engine served; ``block_canaries --check`` re-runs those cells on the shipped engine and
    fails if any digest moves. The proof is therefore checkable in both directions, and a link
    cannot be written for a build that changed behaviour.
``from_commit``
    the commit the predecessor's canaries were recorded at. The pin treats its own head as
    provenance rather than bytes (``benchmarks/engine_pin.py``), so a stored artifact's commit
    pointer is accepted only when the lineage recorded that exact commit on that exact build.
``changed_files`` / ``note`` / ``date``
    what moved and why, in words, for the reader who finds the artifact first.

``same_build(stamp)`` is the check the artifacts use: true when the stamp is the shipped engine,
or when a chain of valid links joins it to the shipped engine. An unknown digest is false, a
link whose proof does not match the recorded canaries is false, and a link authorised by a
PENDING or WITHDRAWN decision is false.

    python -m benchmarks.engine_lineage --check
    python -m benchmarks.engine_lineage --init
    python -m benchmarks.engine_lineage --record --decision DECISION-CAP-SEMANTICS \\
        --changed organica/sleep_extraction.py --note "..."
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

from benchmarks import block_canaries, engine_pin, engine_stamp

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "engine_lineage.json"
DECISIONS = ROOT / "docs" / "decisions.json"
CANARIES = ROOT / "docs" / "block_canaries.json"
KIND = "engine_lineage"
FULL = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")

POLICY = (
    "A stored artifact may pass its build check on a successor only when a recorded link joins "
    "the two, the link names an ADOPTED decision, and the link's proof is exactly the block-canary "
    "digests recorded on the predecessor build. The canary check re-runs those cells on the "
    "successor, so a link cannot bless a build that serves different rows."
)


def load(path: Path | None = None) -> dict:
    return json.loads((RECORD if path is None else path).read_text(encoding="utf-8"))


def canary_cells() -> dict[str, str]:
    """The digests the frozen blocks recorded, by block. This is what a link must prove."""
    data = json.loads(CANARIES.read_text(encoding="utf-8"))
    return {block: cell["digest"] for block, cell in (data.get("cells") or {}).items()}


def proof_cells(link: dict) -> dict[str, str]:
    """The digests a link proves: its own preserved record, or the live canary file.

    A behaviour-identical successor is proved against the digests recorded on the predecessor, so the
    record is historical. The live file moves legitimately when a *different* kind of change lands
    (a grant that alters a refusal canary, a level change), and that must not invalidate a link whose
    build was never touched.
    """
    record = link.get("proof_record")
    if record:
        path = ROOT / record
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        return {block: cell["digest"] for block, cell in (data.get("cells") or {}).items()}
    return canary_cells()


def adopted() -> set[str]:
    data = json.loads(DECISIONS.read_text(encoding="utf-8"))
    return {entry["decision_id"] for entry in data.get("decisions", [])
            if entry.get("status") == "ADOPTED"}


def _short(value) -> str:
    return str(value)[:12] if value else "?"


def link_problems(link: dict, cells: dict[str, str] | None = None,
                  decisions: set[str] | None = None) -> list[str]:
    """Everything that makes one link unable to carry a build. Empty means it can."""
    cells = proof_cells(link) if cells is None else cells
    decisions = adopted() if decisions is None else decisions
    label = "%s -> %s" % (_short(link.get("from")), _short(link.get("to")))
    found: list[str] = []

    for field in ("from", "to"):
        value = link.get(field)
        if not isinstance(value, str) or not FULL.match(value):
            found.append("%s: %s is not a 64-hex engine digest" % (label, field))
    if link.get("from") == link.get("to"):
        found.append("%s: a link must join two different builds" % label)
    if not isinstance(link.get("from_commit"), str) or not COMMIT.match(link["from_commit"]):
        found.append("%s: from_commit is not the 40-hex commit the predecessor was recorded at"
                     % label)

    if link.get("decision") not in decisions:
        found.append("%s: decision %r is not ADOPTED in docs/decisions.json; a lineage is a "
                     "recorded decision, not an edit" % (label, link.get("decision")))
    if not link.get("note"):
        found.append("%s: the link says nothing about why the bytes moved" % label)
    if not link.get("changed_files"):
        found.append("%s: the link names no engine file that changed" % label)

    if link.get("proof_record") and not (ROOT / link["proof_record"]).exists():
        found.append("%s: proof_record %r does not exist" % (label, link["proof_record"]))
    proof = link.get("proof")
    if not isinstance(proof, dict) or not proof:
        found.append("%s: the link carries no canary proof" % label)
    else:
        missing = sorted(set(cells) - set(proof))
        extra = sorted(set(proof) - set(cells))
        moved = sorted(block for block in set(cells) & set(proof) if proof[block] != cells[block])
        if missing:
            found.append("%s: the proof omits the %s canary cell(s); equivalence must cover every "
                         "frozen block" % (label, ", ".join(missing)))
        if extra:
            found.append("%s: the proof names cells no block records: %s"
                         % (label, ", ".join(extra)))
        if moved:
            found.append("%s: the proof's digest for %s is not the recorded one; a moved digest "
                         "is a behaviour change, not a lineage" % (label, ", ".join(moved)))
    return found


def problems(record: dict | None = None) -> list[str]:
    """Everything wrong with the lineage record. Empty means every link can carry a build."""
    data = load() if record is None else record
    found: list[str] = []
    if data.get("kind") != KIND:
        found.append("the record is not a %s record" % KIND)
    links = data.get("links")
    if not isinstance(links, list):
        return found + ["the record carries no links list"]
    decisions = adopted()
    seen: set[str] = set()
    for link in links:
        found.extend(link_problems(link, None, decisions))
        source = link.get("from")
        if source in seen:
            found.append("%s: two links start at the same build" % _short(source))
        seen.add(source)
    if links:
        head = links[-1].get("to")
        current = engine_stamp.engine_sha256()
        if head != current:
            found.append("the lineage head %s is not the shipped engine %s; record the link for "
                         "this build or re-pin" % (_short(head), _short(current)))
    return found


def same_build(stamp: str | None, current: str | None = None, record: dict | None = None) -> bool:
    """Is this stamped build the shipped engine, or a recorded behaviour-identical successor?

    Cheap by design: it reads the record and the canary digests, and runs no cell. The cells are
    re-run by ``block_canaries --check``, which is what keeps the proof honest.
    """
    current = engine_stamp.engine_sha256() if current is None else current
    if not stamp:
        return False
    if stamp == current:
        return True
    data = load() if record is None else record
    links = data.get("links") or []
    if not links:
        return False
    decisions = adopted()
    reached = stamp
    for _ in range(len(links) + 1):
        step = next((item for item in links if item.get("from") == reached), None)
        if step is None or link_problems(step, None, decisions):
            return False
        reached = step.get("to")
        if reached == current:
            return True
    return False


HISTORICAL = ROOT / "docs" / "engine_lineage_0.14.0.json"


def historical_links() -> list[dict]:
    """Links retired by a landing; their commits are still the record of their own build."""
    if not HISTORICAL.exists():
        return []
    return list(json.loads(HISTORICAL.read_text(encoding="utf-8")).get("links") or [])


def carried_commit(commit: str | None, stamp: str | None = None,
                   record: dict | None = None) -> bool:
    """Is this commit pointer the pin's, or one the lineage recorded on that same build?

    A commit is provenance: the pin re-taken at a later checkout moves ``head_at_pin`` without the
    bytes changing. That makes a bare commit comparison reject every artifact on every re-pin, so a
    stale pointer is accepted only when a valid link names it as that build's recorded commit.
    """
    if not commit:
        return False
    if commit == engine_stamp.pinned_commit():
        return True
    data = load() if record is None else record
    decisions = adopted()
    links = list(data.get("links") or []) + ([] if record is not None else historical_links())
    for link in links:
        if link.get("from_commit") != commit:
            continue
        if stamp is not None and link.get("from") != stamp:
            continue
        if not link_problems(link, None, decisions):
            return True
    return False


def explain(stamp: str | None) -> str:
    """One sentence for a check message: which decision carried this build, if one did."""
    if not stamp:
        return "no build recorded"
    if stamp == engine_stamp.engine_sha256():
        return "the shipped engine"
    record = load() if RECORD.exists() else {"links": []}
    reached, steps = stamp, []
    for _ in range(len(record.get("links") or []) + 1):
        step = next((item for item in record["links"] if item.get("from") == reached), None)
        if step is None:
            return "an unrecorded build %s" % _short(stamp)
        steps.append(step)
        reached = step.get("to")
        if reached == engine_stamp.engine_sha256():
            return ("%s, carried to the shipped engine by %s"
                    % (_short(stamp), ", ".join(item["decision"] for item in steps)))
    return "an unrecorded build %s" % _short(stamp)


def _live_cells() -> dict[str, str]:
    """Run every frozen block canary on the shipped engine; the successor's own digests."""
    live: dict[str, str] = {}
    for block in block_canaries.frozen_blocks():
        one = block_canaries.payload(block)
        if one.get("error"):
            raise SystemExit("cannot record a lineage: %s cannot run: %s" % (block, one["error"]))
        live[block] = block_canaries.digest(one)
    return live


def record(decision: str, note: str, changed: list[str], path: Path | None = None) -> dict:
    """Append the link from the canary-recorded build to the shipped one, after proving it."""
    if decision not in adopted():
        raise SystemExit("%s is not ADOPTED in docs/decisions.json; record the decision before "
                         "the lineage it authorises" % decision)
    recorded = json.loads(CANARIES.read_text(encoding="utf-8"))
    predecessor = recorded.get("engine_sha256")
    successor = engine_stamp.engine_sha256()
    if not predecessor:
        raise SystemExit("docs/block_canaries.json names no build; cannot anchor a lineage")
    if predecessor == successor:
        raise SystemExit("the recorded canaries are on the shipped build; there is no successor "
                         "to link")
    live = _live_cells()
    recorded_cells = canary_cells()
    moved = sorted(block for block in recorded_cells if live.get(block) != recorded_cells[block])
    if moved:
        raise SystemExit("the canaries moved on this build (%s); a behaviour change is not a "
                         "lineage -- re-record the blocks and their verdicts instead"
                         % ", ".join(moved))

    target = RECORD if path is None else path
    data = load(target) if target.exists() else {"kind": KIND, "links": []}
    links = list(data.get("links") or [])
    links = [item for item in links if item.get("from") != predecessor]
    links.append({
        "from": predecessor,
        "to": successor,
        "version": engine_pin.package_version(),
        "decision": decision,
        "date": date.today().isoformat(),
        "from_commit": recorded.get("engine_commit"),
        "changed_files": sorted(changed),
        "proof": recorded_cells,
        "note": note,
    })
    body = engine_stamp.stamp({
        "kind": KIND,
        "policy": POLICY,
        "links": links,
        "recorded": date.today().isoformat(),
    })
    target.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return body


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify every recorded link")
    parser.add_argument("--init", action="store_true", help="write an empty lineage record")
    parser.add_argument("--record", action="store_true",
                        help="append the link from the canary-recorded build to the shipped one")
    parser.add_argument("--decision", help="the ADOPTED decision that authorises the change")
    parser.add_argument("--note", help="why the bytes moved, for the reader who finds it later")
    parser.add_argument("--changed", action="append", default=[],
                        help="an engine file the change touched; repeat for each")
    args = parser.parse_args(argv)

    if args.init:
        if RECORD.exists():
            raise SystemExit("%s already exists; a lineage is appended, never rewritten"
                             % RECORD.relative_to(ROOT))
        body = engine_stamp.stamp({
            "kind": KIND,
            "policy": POLICY,
            "links": [],
            "recorded": date.today().isoformat(),
        })
        RECORD.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
        print("wrote %s with no links" % RECORD.relative_to(ROOT))
        return 0

    if args.record:
        if not args.decision or not args.note or not args.changed:
            raise SystemExit("--record needs --decision, --note and at least one --changed file")
        body = record(args.decision, args.note, args.changed)
        link = body["links"][-1]
        print("recorded %s -> %s under %s"
              % (link["from"][:12], link["to"][:12], link["decision"]))
        return 0

    if args.check or not argv:
        found = problems()
        for problem in found:
            print("FAIL:", problem)
        if found:
            return 1
        print("engine lineage: %d link(s), head %s"
              % (len(load().get("links") or []), _short(engine_stamp.engine_sha256())))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
