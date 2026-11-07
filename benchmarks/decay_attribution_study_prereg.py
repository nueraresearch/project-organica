"""Scope guard for the decay-attribution replication: frozen before it executes.

The protocol (`docs/DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md`) was written before any cell ran.
This module keeps it that way:

* the seed block is the one carried here, and no seed in it is used anywhere under `docs/`;
* the protocol records **no execution** and the result artifact does not exist, so a protocol
  written after the run is rejected rather than accepted as a pre-registration;
* every question it claims is registered and carries this protocol, and the four numbers the
  frozen header calls unassigned are accounted for by the dated scope amendment;
* the decision table has a non-empty decision for each of its four labels, so no bucket is a label
  without a consequence (AGENTS.md rule 30);
* sections 1-9 are pinned by SHA-256, so a one-byte edit to the frozen text fails the check.

`validate` is pure and takes the parsed registry, so its tests can tamper with one thing at a time
and require the corresponding failure. `main --check` writes nothing.

    ./.venv/bin/python -m benchmarks.decay_attribution_study_prereg --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from benchmarks.decay_confirmation import harvest_seeds

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "DECAY-ATTRIBUTION-STUDY-PREREGISTRATION.md"
REGISTRY = ROOT / "docs" / "research_question_registry.json"
ARTIFACT = ROOT / "docs" / "decay_attribution_study.json"

#: Frozen here, written before any cell ran, and checked against every seed under docs/.
SEEDS = tuple(range(20301201, 20301213))
ARMS = ("engine", "no_temporal_decay")
QUESTIONS = ("Q029", "Q030", "Q031", "Q032", "Q036")
UNASSIGNED = ("Q033", "Q034", "Q035", "Q037")
#: Brought into scope by section 11, which was written before any cell ran.
AMENDED = ("Q033", "Q034", "Q037")
#: Registered, but deliberately not carried by this run: it needs budget arms.
OUT_OF_SCOPE = ("Q035",)
BUCKETS = ("REPLICATED", "REPLICATED_WITH_SHIFT", "NOT_REPLICATED", "VOID_INSTRUMENT")
BLOCK_KEYS = ("study", "executions", "seeds", "arms", "artifact", "questions", "unassigned")
REQUIRED_SECTIONS = (
    "## 1. Scope, and the question numbers that do not exist",
    "## 2. The instrument and the single run",
    "## 3. Seeds",
    "## 4. Quantities, and what counts as measurable",
    "## 5. Controls and gates",
    "## 6. Pre-committed predictions, as replication targets",
    "## 7. Decision table",
    "## 8. What this cannot establish",
    "## 9. Stop condition and freeze",
    "## 10. Outcome",
)
#: SHA-256 of sections 1-9 as committed. A later edit cannot pass as the frozen protocol.
FROZEN_DIGEST = "2e67000fc134a6b5c10281887e32a7be500dc3bbb7e8e82f4975563271ba7d0f"
#: SHA-256 of the section 11 amendment, pinned when it was written.
AMENDMENT_DIGEST = "f68208a512eb63d9115d07740377836c4df1a87c41308e119a4ab8f82fe51177"


def protocol_digest(text: str) -> str:
    """SHA-256 of sections 1-9, not of the outcome section."""
    cut = text.find("\n## 10.")
    return hashlib.sha256((text[:cut] if cut >= 0 else text).encode("utf-8")).hexdigest()


def amendment_digest(text: str) -> str:
    """SHA-256 of the scope amendment, or the empty hash when it is missing."""
    cut = text.find("\n## 11.")
    return hashlib.sha256((text[cut:] if cut >= 0 else "").encode("utf-8")).hexdigest()


def parse_block(text: str) -> dict[str, str]:
    """The machine-readable header, read as key: value lines before the title."""
    values: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("#"):
            break
        for key in BLOCK_KEYS:
            if line.startswith(key + ":"):
                values[key] = line.split(":", 1)[1].strip()
    return values


def parse_list(value: str | None) -> tuple[str, ...]:
    return tuple(item.strip() for item in (value or "").split(",") if item.strip())


def validate(text: str, registry: dict, artifact_exists: bool = False,
             seeds_used=()) -> list[str]:
    """Every way the committed protocol could have stopped being a pre-registration."""
    found: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in text:
            found.append("missing section: %s" % section)

    block = parse_block(text)
    for key in BLOCK_KEYS:
        if key not in block:
            found.append("the machine block has no %r line" % key)

    if block.get("executions") != "0":
        found.append("the protocol records %r executions; a pre-registration cannot be written "
                     "after the run" % block.get("executions"))
    if artifact_exists:
        found.append("the result artifact already exists, so this protocol is post-hoc")
    if parse_list(block.get("seeds")) != tuple(str(s) for s in SEEDS):
        found.append("the seed block in the protocol is not the one the guard carries")
    if parse_list(block.get("arms")) != ARMS:
        found.append("the arms in the protocol are not the frozen pair")
    if parse_list(block.get("questions")) != QUESTIONS:
        found.append("the questions in the protocol are not the frozen five")
    if parse_list(block.get("unassigned")) != UNASSIGNED:
        found.append("the unassigned question numbers are not the frozen four")
    if block.get("artifact") != ARTIFACT.relative_to(ROOT).as_posix():
        found.append("the artifact path in the protocol is not the one the guard reads")

    questions = {q["id"]: q for q in registry.get("questions", [])}
    for qid in QUESTIONS:
        if qid not in questions:
            found.append("%s is not in the registry" % qid)
        elif DOC.name not in (questions[qid].get("preregistrations") or []):
            found.append("%s does not carry this pre-registration" % qid)
    amendment = text[text.find("\n## 11."):] if "\n## 11." in text else ""
    if not amendment:
        found.append("the scope amendment (section 11) is missing")
    for qid in AMENDED:
        if qid not in questions:
            found.append("%s was brought into scope but is not registered" % qid)
        elif DOC.name not in (questions[qid].get("preregistrations") or []):
            found.append("%s does not carry this pre-registration" % qid)
        elif qid not in amendment:
            found.append("%s is registered but the amendment does not name it" % qid)
    for qid in OUT_OF_SCOPE:
        if qid not in questions:
            found.append("%s is named out of scope but is not registered" % qid)
        elif DOC.name in (questions[qid].get("preregistrations") or []):
            found.append("%s is out of this run's scope but carries its pre-registration" % qid)
    amended = amendment_digest(text)
    if amended != AMENDMENT_DIGEST:
        found.append("the amendment text moved: digest %s, pinned %s" % (amended, AMENDMENT_DIGEST))

    for label in BUCKETS:
        rows = [ln for ln in text.splitlines() if ln.startswith("| `%s`" % label)]
        if not rows:
            found.append("the decision table has no row for %s" % label)
        elif len([cell for cell in rows[0].strip().strip("|").split("|") if cell.strip()]) < 3:
            found.append("%s carries no decision" % label)

    digest = protocol_digest(text)
    if digest != FROZEN_DIGEST:
        found.append("the frozen protocol text moved: digest %s, pinned %s" % (digest, FROZEN_DIGEST))

    overlap = sorted(set(SEEDS) & set(seeds_used))
    if overlap:
        found.append("the seed block overlaps seeds already used under docs/: %r" % overlap)
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Guard the decay-attribution replication.")
    parser.add_argument("--check", action="store_true",
                        help="validate the frozen protocol without writing")
    parser.parse_args(argv)
    text = DOC.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    found = validate(text, registry, artifact_exists=ARTIFACT.exists(),
                     seeds_used=harvest_seeds(ROOT / "docs"))
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("decay attribution study: protocol frozen, no execution recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
