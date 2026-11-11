"""A manual table row may not still claim a runner is missing once its gate exists.

The Q1 row that froze ``PRESENCE-CONSTRUCT-1`` said no runner was installed; the
runner was built later and the row was annotated rather than rewritten.  That
repair is easy to undo -- delete the annotation, or add a new row that repeats
the old claim -- and nothing in the suite would notice, because the manual's
prose is not otherwise checked against the runners it describes.

This guard derives the protected blocks mechanically: a block is protected when
``benchmarks.gate_runner`` registers a gate for its module *and* that module
exposes a ``measure`` entry point.  A manual table row -- a dated revision row,
a current-state table row, or an action-list row -- that says a protected block
has no runner must then carry a superseding clause: ``Superseded later on ...``
in the dated log, ``superseded by action ...`` in a live action status, or an
explicit ``as superseded``.  Rows for blocks with no gated runner (Stage B, the
ranking harness, the store-time observer) are left alone, because there is no
gate whose existence contradicts them.

A check that cannot fail is decoration, so ``test_the_guard_can_fail`` removes
the Q1 annotation and requires the guard to go red.
"""
from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import importlib
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import gate_runner  # noqa: E402

MANUAL = REPO / "docs" / "USER-MANUAL.md"

# The shapes a "runner is missing" claim takes in the manual's tables.
# ``harness`` is deliberately not matched: this guard is about runners, and the
# harness rows have their own annotations.
MISSING_RUNNER = re.compile(
    r"\bno runner\b|runner[^.|]{0,40}\bnot built\b|\bhas no runner\b", re.IGNORECASE)
ANNOTATION = "Superseded later on"
SUPERSEDED = re.compile(
    r"superseded later on|superseded by action|as superseded", re.IGNORECASE)
ISO_DATE = r"\d{4}-\d{2}-\d{2}"
DATE = re.compile(ISO_DATE)
ANNOTATION_DATE = re.compile(
    r"superseded later on\s+(" + ISO_DATE + r")"
    r"|superseded by action[^|]{0,80}?\bon\s+(" + ISO_DATE + r")"
    r"|as superseded(?:\s+on)?\s+(" + ISO_DATE + r")",
    re.IGNORECASE,
)


def gated_runners() -> dict[str, set[str]]:
    """Gate name -> identifiers, for every gated module that has a runner."""
    protected: dict[str, set[str]] = {}
    for name, module, _args in gate_runner.GATES:
        try:
            mod = importlib.import_module(module)
        except ImportError:
            continue
        if not callable(getattr(mod, "measure", None)):
            continue
        identifiers = {module, module.rsplit(".", 1)[-1]}
        prereg = getattr(mod, "prereg", None)
        if callable(prereg):
            try:
                body = prereg()
            except Exception:                      # a broken record is another gate's job
                body = None
            if isinstance(body, dict):
                for key in ("prereg", "kind"):
                    value = body.get(key)
                    if isinstance(value, str):
                        identifiers.add(value)
        path = getattr(mod, "PREREG", None)
        if path is not None:
            identifiers.add(Path(path).name)
        protected[name] = identifiers
    return protected


def _row_date(line: str, annotation: re.Match) -> date | None:
    """The first date before the annotation, which is the row's own date."""
    match = DATE.search(line[:annotation.start()])
    return date.fromisoformat(match.group(0)) if match else None


def _annotation_date(line: str, annotation: re.Match) -> date | None:
    """The date attached to the superseding clause, if it has one."""
    match = ANNOTATION_DATE.search(line, annotation.start())
    if not match:
        return None
    value = next(group for group in match.groups() if group)
    return date.fromisoformat(value)


def _supersession_problem(line: str, annotation: re.Match) -> str | None:
    """Why a superseding clause is not acceptable, or None when it is later."""
    annotated = _annotation_date(line, annotation)
    row = _row_date(line, annotation)
    if annotated is None:
        return "with a superseded clause that has no date"
    if row is None:
        return "with a superseded clause but no dated row to compare"
    if annotated <= row:
        return ("with a superseded date %s that is not later than the row's %s"
                % (annotated.isoformat(), row.isoformat()))
    return None


def problems(text: str | None = None) -> list[str]:
    """Every missing-runner claim not superseded by a later-dated clause."""
    text = MANUAL.read_text(encoding="utf-8") if text is None else text
    protected = gated_runners()
    found: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.startswith("|") or not MISSING_RUNNER.search(line):
            continue
        annotation = SUPERSEDED.search(line)
        reason = _supersession_problem(line, annotation) if annotation else "without a superseded clause"
        if annotation and reason is None:
            continue
        for name, identifiers in protected.items():
            marker = next((item for item in identifiers if item in line), None)
            if marker:
                found.append(
                    "%d: the %s row claims a missing runner %s (matched %r)"
                    % (lineno, name, reason, marker))
                break
    return found


def test_the_manual_has_no_unmarked_missing_runner_claim():
    assert gated_runners(), "no gated runner was found; the guard would be vacuous"
    assert problems() == []


def test_at_least_one_protected_runner_is_the_construct_audit():
    ids = set().union(*gated_runners().values())
    assert "PRESENCE-CONSTRUCT-1" in ids
    assert "PRESENCE-CONVERSION-1" in ids


def test_the_guard_can_fail():
    """Removing a valid later annotation must make the guard fire."""
    annotated = ("| 2026-11-10 | **Construct audit.** No runner was installed for "
                 "`PRESENCE-CONSTRUCT-1`; **Superseded later on 2026-11-11:** the runner exists. |")
    assert problems(annotated + "\n") == []
    removed = annotated.replace(" **Superseded later on 2026-11-11:** the runner exists.", "")
    findings = problems(removed + "\n")
    assert findings, "the guard did not notice a missing-runner claim with the annotation removed"
    assert "PRESENCE-CONSTRUCT-1" in findings[0]


def test_the_guard_ignores_blocks_without_a_gated_runner():
    row = ("| 2026-11-10 | **A block without a gate.** No runner exists for "
           "`RANK-ORDERING-1`; nothing is registered in `gate_runner`. |")
    assert problems(row + "\n") == []


def test_the_guard_ignores_a_meta_row_without_the_claim():
    row = ("| 2026-11-10 | **Meta.** The row marks its earlier missing-runner "
           "statement as superseded the same day; `PRESENCE-CONSTRUCT-1` is unaffected. |")
    assert problems(row + "\n") == []


def test_the_guard_scans_a_current_state_table_row():
    row = ("| **Q1 conversion block** | The block is frozen, but no runner exists "
           "for `PRESENCE-CONSTRUCT-1` yet. |")
    findings = problems(row + "\n")
    assert findings, "the guard ignored a missing-runner claim in a current-state table"
    assert "PRESENCE-CONSTRUCT-1" in findings[0]


def test_the_guard_scans_an_action_row():
    row = ("| 25 | **Ranking preregistration.** "
           "`benchmarks.presence_construct_audit` has no runner. |")
    findings = problems(row + "\n")
    assert findings, "the guard ignored a missing-runner claim in an action row"
    assert "construct audit prereg" in findings[0]


def test_an_annotated_action_row_is_accepted():
    row = ("| 25 | **DECIDED 2026-11-07.** The runner is not built for "
           "`PRESENCE-CONSTRUCT-1`; **superseded by action 26 on 2026-11-08:** the runner was built. |")
    assert problems(row + "\n") == []


def test_a_same_day_annotation_is_not_accepted():
    row = ("| 2026-11-10 | **Construct audit.** No runner was installed for "
           "`PRESENCE-CONSTRUCT-1`; **Superseded later on 2026-11-10:** the runner exists. |")
    findings = problems(row + "\n")
    assert findings, "a same-day supersession satisfied the guard"
    assert "not later" in findings[0]


def test_an_earlier_annotation_is_not_accepted():
    row = ("| 2026-11-10 | **Construct audit.** No runner was installed for "
           "`PRESENCE-CONSTRUCT-1`; **Superseded later on 2026-11-09:** the runner exists. |")
    findings = problems(row + "\n")
    assert findings, "an earlier supersession satisfied the guard"
    assert "not later" in findings[0]


def test_an_undated_annotation_is_not_accepted():
    row = ("| 25 | **DECIDED 2026-11-07.** The runner is not built for "
           "`PRESENCE-CONSTRUCT-1`; **superseded by action 26:** the runner was built. |")
    findings = problems(row + "\n")
    assert findings, "an undated supersession satisfied the guard"
    assert "no date" in findings[0]


def test_a_later_annotation_is_accepted():
    row = ("| 2026-11-10 | **Construct audit.** No runner was installed for "
           "`PRESENCE-CONSTRUCT-1`; **Superseded later on 2026-11-11:** the runner exists. |")
    assert problems(row + "\n") == []


def test_the_stage_b_row_is_reconciled_with_its_runner():
    """The dated row keeps its claim, but in the past tense and pointing at the module."""
    text = MANUAL.read_text(encoding="utf-8")
    row = next(line for line in text.splitlines()
               if "The owner approved the three Stage B decisions" in line)
    assert "no runner existed" in row
    assert "no runner exists" not in row
    assert "benchmarks/stage_b_runner.py" in row
    assert "Superseded later on 2026-11-04" in row
    assert "The Stage B runner exists" in text
    runner = REPO / "benchmarks" / "stage_b_runner.py"
    assert runner.exists(), "the row claims a runner module that is missing"
    source = runner.read_text(encoding="utf-8")
    for flag in ("--cell", "--all", "--assemble", "--estimate"):
        assert flag in source, flag
