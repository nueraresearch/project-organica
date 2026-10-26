"""A published document must contain the number, not the template.

Seven literal `{...}` placeholders shipped in the committed audit-trace
specification -- `{ties}`, `{t_dist:,}`, `{t_edges}`, `{t_cycles}`, `{t_a1:,}`,
`{t_a2}` from the second and third review rounds, and `{share:.1f}` from the
fourth.  They sat inside sentences that assert results, so a reader saw a
number that was never computed while the real value sat in a committed
artifact the whole time.

The reason it survived three review rounds is that a placeholder is *silent*.
It does not look wrong in a diff; it looks like a sentence.  Reading harder
does not find braces.  So this guard is mechanical: it scans the document set
for unsubstituted placeholders and fails on any it finds.

The discriminator is code font.  A placeholder **named** as an example of
syntax is written in backticks (`{ties}`); a placeholder **standing in for a
value** is written as prose.  Only the second kind is a defect.

Reference: AGENTS.md rule 20; journal section 46; facts sheet AA17.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Documents that are read as a measurement record.  The placeholder guard is
# deliberately scoped to these: the papers and the architecture notes use LaTeX
# braces legitimately, and a guard that cries wolf is a guard that gets ignored.
GUARDED = [
    "docs/AUDIT-TRACE-SPEC.md",
    "docs/USER-MANUAL.md",
    "docs/FACTS-SHEET.md",
    "docs/PHASE-L-SYNTHESIS.md",
    "docs/phase_l_results.md",
    "docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md",
    "docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md",
    "research-journal/phase_g_findings_20261021.md",
    "CHANGELOG.md",
    "README.md",
    "AGENTS.md",
]

# A template placeholder is a brace group holding an identifier, optionally
# followed by a format spec: {ties}  {t_dist:,}  {share:.1f}
PLACEHOLDER = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*(?::[^{}]*)?\}")

# Inline code spans -- a placeholder *named* as an example lives here.
CODE_SPAN = re.compile(r"`[^`]*`")

# LaTeX uses braces legitimately ({Experience} inside \text{}).
LATEX = re.compile(r"\\(text|longrightarrow|xrightarrow|log|in|le|ge|frac|sum)\b")

# Identifiers that legitimately appear in braces as prose.
ALLOWED = {
    "support_count",
    "contradiction_count",
    "raw_contradiction_count",
    "total_flow",
    "prior_confidence",
    "revision_delta",
    "event_type",
    "parent_ids",
    "found",
    "id",
    "type",
    "generation",
    "confidence",
    "parents",
    "seed",
    "value",
}

# The seven tokens that were the shipped defect are *named* on purpose, in the
# documents that record the defect.  Naming them is not the same as leaving
# them unsubstituted -- and the specification, where they were the defect, is
# held to the stricter rule below.
DEFECT_TOKENS = {"ties", "t_dist", "t_edges", "t_cycles", "t_a1", "t_a2", "t_a7", "share"}

# Documents where a placeholder is a defect wherever it appears, even if it is
# one of the seven named tokens.
STRICT = {"docs/AUDIT-TRACE-SPEC.md"}


def _scan(text: str, strict: bool = False) -> list[tuple[int, str]]:
    """Return (lineno, token) for every unsubstituted placeholder in prose."""
    hits: list[tuple[int, str]] = []
    in_fence = False
    for lineno, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if LATEX.search(line):
            continue
        # strip inline code spans: a placeholder shown in code font is an
        # example of syntax, not a value standing in for a measurement.
        prose = CODE_SPAN.sub(" ", line)
        for match in PLACEHOLDER.finditer(prose):
            name = match.group(0)[1:-1].split(":", 1)[0]
            if name in ALLOWED:
                continue
            if not strict and name in DEFECT_TOKENS:
                continue
            hits.append((lineno, match.group(0)))
    return hits


def test_guarded_documents_have_no_unsubstituted_placeholders():
    """No committed measurement document may ship a template placeholder."""
    findings: list[str] = []
    for rel in GUARDED:
        path = REPO / rel
        assert path.exists(), f"guarded document missing: {rel}"
        strict = rel in STRICT
        for lineno, token in _scan(path.read_text(encoding="utf-8"), strict=strict):
            findings.append(f"{rel}:{lineno}: {token}")
    assert not findings, (
        "unsubstituted template placeholders in committed documents:\n  "
        + "\n  ".join(findings)
    )


def test_the_guard_can_fail():
    """A check that cannot fail is decoration -- so prove this one goes red."""
    planted = "producing **{ties}** stores with a genuinely tied window.\n"
    assert _scan(planted, strict=True), "the guard did not notice a planted placeholder"
    # ...it must not fire on a real field name...
    clean = "the candidate carries {support_count} and {revision_delta} in evidence.\n"
    assert not _scan(clean), "the guard fired on legitimate field names"
    # ...nor on a placeholder that is being *named* rather than used.
    named = "the seven shipped were `{ties}` and `{share:.1f}`.\n"
    assert not _scan(named), "the guard fired on a placeholder named in code font"
    # ...and it must still catch a *new* token, which is the failure mode a
    # future editing script would actually produce.
    fresh = "the rate is {self_sourced_share} on the run.\n"
    assert _scan(fresh), "the guard missed a new, unsubstituted token"


def test_the_spec_states_the_frozen_reference_rate_as_a_number():
    """The reference rate must appear as a value, not as a template."""
    spec = (REPO / "docs/AUDIT-TRACE-SPEC.md").read_text(encoding="utf-8")
    assert "Reference rate: 17.9%" in spec, "the frozen reference rate is not stated as a number"
    assert "{share" not in spec, "the reference rate is still a template"
