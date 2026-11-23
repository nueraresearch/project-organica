"""Scope guard for the decay-adaptation pilot: frozen before any cell runs.

The protocol (`docs/DECAY-ADAPTATION-PREREGISTRATION.md`) was written before any cell ran. This
module keeps it that way: the four arms, two families, five seeds, cycle count, question and
artifact path are carried here and checked against the protocol's machine-readable header; Q049 is
registered, open and carries this protocol; every decision-table label has a row with a decision;
and sections 1-11 are pinned by SHA-256.

    ./.venv/bin/python -m benchmarks.decay_adaptation_prereg --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from benchmarks.decay_confirmation import harvest_seeds

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "DECAY-ADAPTATION-PREREGISTRATION.md"
REGISTRY = ROOT / "docs" / "research_question_registry.json"
ARTIFACT = ROOT / "docs" / "decay_adaptation.json"

ARMS = ("shipped", "factor099", "factor09925", "no_decay")
FAMILIES = ("cause_mix", "mapping_mix")
SEEDS = (20302601, 20302602, 20302603, 20302604, 20302605)
CYCLES = 80
QUESTION = "Q049"
BUCKETS = (
    "BOTH_COST",
    "NO_DECAY_ONLY_COST",
    "OPERATING_ONLY_COST",
    "ARM_BETTER",
    "NO_COST_DETECTED",
    "VOID_INSTRUMENT",
)
BLOCK_KEYS = ("study", "executions", "seeds", "arms", "families", "cycles", "artifact", "question")
REQUIRED_SECTIONS = (
    "## 1. The question, and why it is the next one",
    "## 2. The worlds and the setting",
    "## 3. The arms",
    "## 4. The instrument",
    "## 5. Seeds",
    "## 6. The endpoint, the delta and the margin",
    "## 7. Gates",
    "## 8. Pre-committed predictions",
    "## 9. Decision table",
    "## 10. What this cannot establish",
    "## 11. Stop condition and freeze",
    "## 12. Outcome",
)
#: SHA-256 of sections 1-11 as committed. A later edit cannot pass as the frozen protocol.
FROZEN_DIGEST = "4879a7642366de812e197b5161dff954afd5efbe30dd7dc0c0bef8e24f6fd590"


def protocol_digest(text: str) -> str | None:
    start = text.find("## 1.")
    cut = text.find("\n## 12. Outcome")
    if start < 0 or cut < 0:
        return None
    return hashlib.sha256(text[start:cut].encode("utf-8")).hexdigest()


def parse_block(text: str) -> dict[str, str]:
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
    found: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in text:
            found.append("missing section: %s" % section)

    block = parse_block(text)
    for key in BLOCK_KEYS:
        if key not in block:
            found.append("the machine block has no %r line" % key)

    executions = block.get("executions")
    outcome = text[text.find("## 12. Outcome"):] if "## 12. Outcome" in text else ""
    if artifact is None:
        if executions != "0":
            found.append("the protocol records %r executions but no artifact exists" % executions)
        if "Not yet written" not in outcome:
            found.append("section 12 is written but there is no artifact")
    else:
        if executions != "1":
            found.append("an artifact exists but the protocol records %s executions" % executions)
        if artifact.get("protocol_digest") != FROZEN_DIGEST:
            found.append("the artifact's digest does not match the pinned protocol")
        label = artifact.get("label")
        if label not in BUCKETS:
            found.append("artifact label %r is not one of the frozen buckets" % label)
        elif label not in outcome:
            found.append("section 12 does not name the artifact's label %r" % label)
        if tuple(artifact.get("seeds") or ()) != SEEDS:
            found.append("the artifact's seeds are not the pre-registered block")
        if tuple(artifact.get("arms") or ()) != ARMS:
            found.append("the artifact's arms are not the frozen four")
        if tuple(artifact.get("families") or ()) != FAMILIES:
            found.append("the artifact's families are not the frozen two")
        if len(artifact.get("cells") or []) != len(ARMS) * len(FAMILIES) * len(SEEDS):
            found.append("the artifact does not carry the full 40-cell design")

    if parse_list(block.get("seeds")) != tuple(str(seed) for seed in SEEDS):
        found.append("the seed block in the protocol is not the one the guard carries")
    if parse_list(block.get("arms")) != ARMS:
        found.append("the arms in the protocol are not the frozen four")
    if parse_list(block.get("families")) != FAMILIES:
        found.append("the families in the protocol are not the frozen two")
    if block.get("cycles") != str(CYCLES):
        found.append("the cycle count in the protocol is not %d" % CYCLES)
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
    parser = argparse.ArgumentParser(description="Guard the decay-adaptation pre-registration.")
    parser.add_argument("--check", action="store_true")
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
    print("decay adaptation: protocol frozen, %s"
          % ("executed" if artifact else "no execution recorded"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
