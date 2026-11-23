"""Scope guard for the six-arm substrate repair study: frozen before any cell runs.

The protocol (`docs/SUBSTRATE-REPAIR-PREREGISTRATION.md`) was written before any cell ran. This
module keeps it that way:

* the six arms, two conditions, seed block, question and artifact path are carried here and checked
  against the protocol's machine-readable header;
* the protocol records no execution and the result artifact does not exist, so a protocol written
  after the run is rejected rather than accepted as a pre-registration;
* Q046 is registered, open and carries this protocol;
* every decision-table label has a row with a decision, so no bucket is a label without a
  consequence (AGENTS.md rule 30);
* sections 1-10 are pinned by SHA-256, so a one-byte edit to the frozen text fails the check.

`validate` is pure and takes the parsed registry, so its tests can tamper with one thing at a time
and require the corresponding failure. `main --check` writes nothing.

    ./.venv/bin/python -m benchmarks.substrate_repair_prereg --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from benchmarks.decay_confirmation import harvest_seeds

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "SUBSTRATE-REPAIR-PREREGISTRATION.md"
REGISTRY = ROOT / "docs" / "research_question_registry.json"
ARTIFACT = ROOT / "docs" / "substrate_repair.json"

SEEDS = (20302301, 20302302, 20302303)
CONTROL_SEED = 20261023
ARMS = ("FULL", "SALIENCE", "NO_CONTRADICTIONS", "NO_QUESTIONS", "NO_DREAMS", "ANTI_EIG")
CONDITIONS = ("shipped", "repaired")
QUESTION = "Q046"
BUCKETS = (
    "SUBSTRATE_REPAIR",
    "PARTIAL_REPAIR",
    "NO_REPAIR",
    "REPAIR_HARMS",
    "BASELINE_NOT_REPRODUCED",
    "REPAIR_NOT_LIVE",
    "VOID_INSTRUMENT",
)
BLOCK_KEYS = ("study", "executions", "seeds", "arms", "conditions", "artifact", "question")
REQUIRED_SECTIONS = (
    "## 1. The question, and why it is the next one",
    "## 2. The world and the setting",
    "## 3. The repair",
    "## 4. Cells and seeds",
    "## 5. The endpoint and the comparison",
    "## 6. Gates",
    "## 7. Pre-committed predictions",
    "## 8. Decision table",
    "## 9. What this cannot establish",
    "## 10. Stop condition and freeze",
    "## 11. Outcome",
)
#: SHA-256 of sections 1-10 as committed. A later edit cannot pass as the frozen protocol.
FROZEN_DIGEST = "e1654d034df50d6602d062dabd6bc58d8a15b0c847c6ce340877b5d7043ea392"


def protocol_digest(text: str) -> str | None:
    """SHA-256 of sections 1-10, the frozen part, and not of the outcome."""
    start = text.find("## 1.")
    cut = text.find("\n## 11. Outcome")
    if start < 0 or cut < 0:
        return None
    return hashlib.sha256(text[start:cut].encode("utf-8")).hexdigest()


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


def validate(text: str, registry: dict, artifact: dict | None = None,
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

    executions = block.get("executions")
    outcome = text[text.find("## 11. Outcome"):] if "## 11. Outcome" in text else ""
    if artifact is None:
        if executions != "0":
            found.append("the protocol records %r executions but no artifact exists" % executions)
        if "Not yet written" not in outcome:
            found.append("section 11 is written but there is no artifact")
    else:
        if executions != "1":
            found.append("an artifact exists but the protocol records %s executions" % executions)
        if artifact.get("protocol_digest") != FROZEN_DIGEST:
            found.append("the artifact's digest does not match the pinned protocol")
        label = artifact.get("label")
        if label not in BUCKETS:
            found.append("artifact label %r is not one of the frozen buckets" % label)
        elif label not in outcome:
            found.append("section 11 does not name the artifact's label %r" % label)
        if tuple(artifact.get("seeds") or ()) != SEEDS:
            found.append("the artifact's seeds are not the pre-registered block")

    if parse_list(block.get("seeds")) != tuple(str(seed) for seed in SEEDS):
        found.append("the seed block in the protocol is not the one the guard carries")
    if parse_list(block.get("arms")) != ARMS:
        found.append("the arms in the protocol are not the frozen six")
    if parse_list(block.get("conditions")) != CONDITIONS:
        found.append("the conditions in the protocol are not the frozen pair")
    if block.get("question") != QUESTION:
        found.append("the question in the protocol is not %s" % QUESTION)
    if block.get("artifact") != ARTIFACT.relative_to(ROOT).as_posix():
        found.append("the artifact path in the protocol is not the one the guard reads")

    questions = {q.get("id"): q for q in registry.get("questions", [])}
    entry = questions.get(QUESTION)
    if entry is None:
        found.append("%s is not in the registry" % QUESTION)
    else:
        if DOC.name not in (entry.get("preregistrations") or []):
            found.append("%s does not carry this pre-registration" % QUESTION)
        if artifact is None and entry.get("status") not in ("open", "future"):
            found.append("%s is %r before the run" % (QUESTION, entry.get("status")))

    for label in BUCKETS:
        rows = [line for line in text.splitlines() if line.startswith("| `%s`" % label)]
        if not rows:
            found.append("the decision table has no row for %s" % label)
        elif len([cell for cell in rows[0].strip().strip("|").split("|") if cell.strip()]) < 3:
            found.append("%s carries no decision" % label)

    if "{" in text or "}" in text:
        found.append("the protocol contains a brace placeholder")
    digest = protocol_digest(text)
    if digest != FROZEN_DIGEST:
        found.append("the frozen protocol text moved: digest %s, pinned %s"
                     % (digest, FROZEN_DIGEST))

    overlap = sorted(set(SEEDS) & set(seeds_used))
    if overlap:
        found.append("the seed block overlaps seeds already used under docs/: %r" % overlap)
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Guard the substrate repair pre-registration.")
    parser.add_argument("--check", action="store_true",
                        help="validate the frozen protocol without writing")
    parser.parse_args(argv)
    text = DOC.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.exists() else None
    found = validate(text, registry, artifact,
                     seeds_used=harvest_seeds(ROOT / "docs") - set(SEEDS))
    if found:
        for problem in found:
            print("FAIL:", problem)
        return 1
    print("substrate repair: protocol frozen, %s"
          % ("executed" if artifact else "no execution recorded"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
