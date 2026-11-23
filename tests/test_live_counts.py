"""A live count quoted in prose must equal its source, or say when it was true."""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json  # noqa: E402
import re  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
QUESTION_CLAIM = re.compile(r"\b(\d+)\s+questions in `?docs/RESEARCH-QUESTION-REGISTRY\.md`?")


def _live_question_count() -> int:
    registry = json.loads((ROOT / "docs/research_question_registry.json").read_text(encoding="utf-8"))
    return len(registry["questions"])


def _claims(text: str) -> list[int]:
    return [int(m.group(1)) for m in QUESTION_CLAIM.finditer(text)]


def test_every_document_that_states_the_registry_size_states_the_live_one():
    live = _live_question_count()
    offenders = {}
    for path in sorted((ROOT / "docs").glob("*.md")):
        claims = _claims(path.read_text(encoding="utf-8"))
        stale = [claim for claim in claims if claim != live]
        if stale:
            offenders[path.name] = stale
    assert not offenders, (
        "a document states a registry size that is not the current one (%d): %s" % (live, offenders))


def test_the_census_can_fail(tmp_path):
    """A check that cannot fire is decoration: the same claim, one number off, must be caught."""
    assert _claims("which of the 23 questions in `docs/RESEARCH-QUESTION-REGISTRY.md` is affordable")
    stale = _claims("which of the 23 questions in `docs/RESEARCH-QUESTION-REGISTRY.md` is affordable")
    assert stale != [_live_question_count()]
