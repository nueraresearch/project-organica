"""Guard the admission-versus-slot pre-registration against after-the-fact edits.

The protocol in ``docs/DECAY-ADMISSION-SLOT-PREREGISTRATION.md`` is frozen by digest over sections
1-9. The runner must record that digest, and the artifact must carry the pre-registered label.

The check is two-state, because this study is meant to be run in the same sitting it is frozen in:

- before the run: the protocol records ``executions: 0``, section 10 says the outcome is not written,
  no artifact exists, and the seed block is unused;
- after the run: the protocol records ``executions: 1``, the artifact carries the pinned digest and
  one of the pre-registered labels, section 10 names that label, and the seeds still match.

A protocol edited after its own run fails the digest check. A run started before its protocol was
frozen fails the execution-count check.

Run::

    python -m benchmarks.decay_admission_slot_prereg --pin
    python -m benchmarks.decay_admission_slot_prereg --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PREREG = DOCS / "DECAY-ADMISSION-SLOT-PREREGISTRATION.md"
ARTIFACT = DOCS / "decay_admission_slot.json"
REGISTRY = DOCS / "research_question_registry.json"
QUESTION = "Q044"

SEEDS = tuple(range(20301601, 20301609))
ARMS = ("engine", "no_temporal_decay")
ARTIFACT_DIGEST_KEY = "protocol_digest"
DOMINANT = 0.60
MAJORITY_SEEDS = 6
BUCKETS = (
    "ADMISSION_DOMINANT",
    "SLOT_DOMINANT",
    "MIXED",
    "SLOT_NEVER_BOUND",
    "VOID_INSTRUMENT",
)
REQUIRED_BLOCK = ("study", "executions", "seeds", "arms", "artifact", "question")

PINNED = "36b9000a954933de2e390e7c8df1ff32b013a1b4862166a94523ef196e9d9117"

_PIN_LINE = re.compile(r"^PINNED = .*$", re.MULTILINE)


def sections_1_9(text: str) -> str:
    """The frozen body: everything from section 1 up to, but not including, section 10."""
    start = text.index("## 1.")
    end = text.index("## 10.")
    return text[start:end].strip()


def protocol_digest(text: str) -> str:
    return hashlib.sha256(sections_1_9(text).encode("utf-8")).hexdigest()


def parse_block(text: str) -> dict[str, str]:
    block: dict[str, str] = {}
    for line in text.splitlines():
        if not line or line.startswith("#") or line.startswith(" ") or ":" not in line:
            if not block:
                continue
            break
        key, _, value = line.partition(":")
        block[key.strip()] = value.strip()
    return block


def seed_errors(block: dict[str, str]) -> list[str]:
    errors = []
    raw = block.get("seeds", "")
    try:
        seeds = tuple(int(part) for part in raw.split(",") if part.strip())
    except ValueError:
        return ["the seed block is not a list of integers: %r" % raw]
    if seeds != SEEDS:
        errors.append("seeds moved: protocol has %s, guard pins %s" % (list(seeds), list(SEEDS)))
    arms = tuple(part.strip() for part in block.get("arms", "").split(",") if part.strip())
    if arms != ARMS:
        errors.append("arms moved: protocol has %s, guard pins %s" % (list(arms), list(ARMS)))
    return errors


def state_errors(block: dict[str, str], artifact: dict | None, outcome: str) -> list[str]:
    """The pre-run / post-run contract, independent of the digest."""
    errors = []
    raw = block.get("executions", "")
    if raw not in {"0", "1"}:
        return ["executions must be 0 or 1, found %r" % raw]
    executions = int(raw)
    if artifact is None:
        if executions != 0:
            errors.append("the protocol records an execution but no artifact exists")
        if "Not yet written" not in outcome:
            errors.append("no artifact exists, but section 10 no longer says the outcome is unwritten")
        return errors
    if executions != 1:
        errors.append("an artifact exists, but the protocol records %d executions" % executions)
    if artifact.get(ARTIFACT_DIGEST_KEY) != PINNED:
        errors.append(
            "the artifact records digest %r, the guard pins %r"
            % (artifact.get(ARTIFACT_DIGEST_KEY), PINNED)
        )
    label = artifact.get("label")
    if label not in BUCKETS:
        errors.append("artifact label %r is not one of the pre-registered buckets" % label)
    elif label not in outcome:
        errors.append("section 10 does not record the pre-registered label %r" % label)
    if tuple(artifact.get("seeds") or ()) != SEEDS:
        errors.append("the artifact's seeds do not match the frozen block")
    return errors


def validate(
    text: str,
    registry: dict,
    artifact: dict | None = None,
    used_seeds: set[int] | None = None,
) -> list[str]:
    errors: list[str] = []
    if "## 10." not in text or "## 1." not in text:
        return ["the protocol has no section 1 / section 10 boundary"]

    block = parse_block(text)
    for name in REQUIRED_BLOCK:
        if name not in block:
            errors.append("the machine block has no %r line" % name)
    if errors:
        return errors

    if protocol_digest(text) != PINNED:
        errors.append("sections 1-9 were edited after the freeze (digest changed)")
    errors += seed_errors(block)

    if block.get("artifact") != "docs/decay_admission_slot.json":
        errors.append("the protocol names artifact %r" % block.get("artifact"))
    if block.get("question") != QUESTION:
        errors.append("the protocol names question %r" % block.get("question"))

    questions = {q.get("id"): q for q in registry.get("questions", [])}
    question = questions.get(QUESTION)
    if question is None:
        errors.append("%s is not in the registry" % QUESTION)
    else:
        evidence = [str(item) for item in question.get("evidence", [])]
        if "docs/DECAY-ADMISSION-SLOT-PREREGISTRATION.md" not in evidence:
            errors.append("%s does not cite the protocol in its evidence" % QUESTION)

    outcome = text[text.index("## 10."):]
    errors += state_errors(block, artifact, outcome)
    if artifact is None and used_seeds:
        overlap = sorted(set(SEEDS) & (used_seeds - set(SEEDS)))
        if overlap:
            errors.append("the seed block is already used under docs/: %s" % overlap)
    if artifact is None and block.get("executions") == "0":
        for bucket in BUCKETS:
            if bucket not in text:
                errors.append("the protocol never names the pre-registered label %r" % bucket)
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pin", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    text = PREREG.read_text(encoding="utf-8")
    if args.pin:
        digest = protocol_digest(text)
        module = Path(__file__)
        source = module.read_text(encoding="utf-8")
        source, count = _PIN_LINE.subn('PINNED = "%s"' % digest, source, count=1)
        if count != 1:
            print("could not find the PINNED line", file=sys.stderr)
            return 1
        module.write_text(source, encoding="utf-8")
        print("pinned %s" % digest)
        return 0
    if not args.check:
        parser.print_help()
        return 2

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.exists() else None
    used: set[int] = set()
    if artifact is None:
        from benchmarks.decay_confirmation import harvest_seeds

        used = harvest_seeds(DOCS)
    errors = validate(text, registry, artifact, used)
    if errors:
        for error in errors:
            print("FAIL %s" % error, file=sys.stderr)
        return 1
    print("OK protocol frozen, %s registered, state consistent" % QUESTION)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
