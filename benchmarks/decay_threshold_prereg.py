"""Scope guard for the decay-threshold refinement: frozen before any cell runs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from benchmarks.decay_confirmation import harvest_seeds

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "DECAY-THRESHOLD-PREREGISTRATION.md"
REGISTRY = ROOT / "docs" / "research_question_registry.json"
ARTIFACT = ROOT / "docs" / "decay_threshold.json"

CANDIDATES = tuple(round(0.9901 + index * 0.0001, 4) for index in range(24))
SEEDS = (20302701, 20302702, 20302703)
SCREEN_SEED = 20302701
WORLD = "lattice_L1"
ARM = "FULL"
QUESTION = "Q050"
BUCKETS = (
    "THRESHOLD_FOUND",
    "NO_INTERIOR_SURVIVOR",
    "BELOW_SCREEN",
    "NON_MONOTONE",
    "CONFIRMATION_FAILED",
    "VOID_INSTRUMENT",
)
BLOCK_KEYS = ("study", "executions", "seeds", "candidates", "screen_seed",
              "world", "arm", "artifact", "question")
REQUIRED_SECTIONS = (
    "## 1. The question, and why it is the next one",
    "## 2. The world and the setting",
    "## 3. The candidates",
    "## 4. The instrument",
    "## 5. Seeds",
    "## 6. The endpoint and the boundary",
    "## 7. Gates",
    "## 8. Pre-committed predictions",
    "## 9. Decision table",
    "## 10. What this cannot establish",
    "## 11. Stop condition and freeze",
    "## 12. Outcome",
)
#: SHA-256 of sections 1-11 as committed.
FROZEN_DIGEST = "8e2f821d09b26591f2188de0ad30a1514731976aa95ba4d4f99d56ff220f6f89"


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
        if tuple(artifact.get("candidates") or ()) != CANDIDATES:
            found.append("the artifact's candidates are not the 24 frozen factors")
        if artifact.get("screen_seed") != SCREEN_SEED:
            found.append("the artifact's screen seed is not the pre-registered seed")
        if label == "THRESHOLD_FOUND" and artifact.get("smallest_survivor") not in CANDIDATES:
            found.append("a threshold was found but the smallest survivor is not a candidate")

    if parse_list(block.get("seeds")) != tuple(str(seed) for seed in SEEDS):
        found.append("the seed block in the protocol is not the one the guard carries")
    if block.get("candidates") != str(len(CANDIDATES)):
        found.append("the candidate count in the protocol is not %d" % len(CANDIDATES))
    if block.get("screen_seed") != str(SCREEN_SEED):
        found.append("the screen seed in the protocol is not the one the guard carries")
    if block.get("world") != WORLD:
        found.append("the world in the protocol is not %s" % WORLD)
    if block.get("arm") != ARM:
        found.append("the arm in the protocol is not %s" % ARM)
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
    parser = argparse.ArgumentParser(description="Guard the decay-threshold pre-registration.")
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
    print("decay threshold: protocol frozen, %s"
          % ("executed" if artifact else "no execution recorded"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
