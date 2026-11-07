"""What a statement rests on: a closed vocabulary, the rules a tag must satisfy, and the
figures that do not trace back to an artifact.

This is the provenance layer the research records share. It began as a replacement for one
boolean on the bottleneck map (`read_for_this_record: true/false`), because a boolean cannot say
*why* a row was not read, and for a prose list naming the rows that were the owner's reading,
because a list maintained beside the rows drifts the first time a row is renamed — the failure
`AGENTS.md` rule 27 exists for.

Four tags, from the governed-belief model in `nueraresearch/project-quicksilver` (an agent may
record an observation backed by evidence, and may never promote its own inference to one):

  ``ARTIFACT_READ``       the status was checked, for this record, against the records named in
                          the row's `evidence`. Available only to a row that names something, and
                          every named path must exist on disk.
  ``OWNER_READING``       the status is the owner's reading of the named records, which this
                          record does not restate. The check therefore quotes no figure: a
                          reading that quotes a number is a transcription, and a transcription is
                          only honest when it is tagged as one.
  ``AGENT_INFERRED``      an agent inferred the status. No reading was made for this record, so
                          the tag needs no citation — and it may not carry a supported status.
  ``PROTOCOL_CONSTRAINT`` the value is fixed by a registration rather than measured, so the tag
                          must name one. Nothing in the records is tagged this way yet; the tag
                          exists because a protocol-fixed number is not a measurement, and
                          calling it one is the defect the tag prevents.

Every rule is fail-closed: an unknown tag is refused rather than defaulted, a missing tag is
refused rather than assumed, the old boolean is refused beside a tag so it cannot quietly
return, and a citing tag the row's evidence cannot back is refused. Each rule is proved to fire
in `tests/test_provenance.py`.

The layer also answers the question the tags exist for — *how much confidence should be placed
in this statement?* — in `render_report`, which tallies the map by tag, checks every figure a
public claim quotes against the artifact the claim cites, and says which decisions still record
their authority in prose. Nothing there is a new record: the tags are read from the map, the
claims from the ledger, the decisions from the index.

Standard library only; nothing here reads or writes an engine file.
"""
from __future__ import annotations

import re
from pathlib import Path

ARTIFACT_READ = "ARTIFACT_READ"
OWNER_READING = "OWNER_READING"
AGENT_INFERRED = "AGENT_INFERRED"
PROTOCOL_CONSTRAINT = "PROTOCOL_CONSTRAINT"

#: The closed set. Order is the order summaries report them in: strongest evidence first.
TAGS = (ARTIFACT_READ, OWNER_READING, AGENT_INFERRED, PROTOCOL_CONSTRAINT)

#: What each tag claims, printed into the generated page beside the counts.
MEANINGS = {
    ARTIFACT_READ: ("the status was checked, for this map, against the records named in the "
                    "row's evidence"),
    OWNER_READING: ("the status is the owner's reading of the named records, which this entry "
                    "does not restate"),
    AGENT_INFERRED: ("an agent inferred the status; no reading was made for this record, and "
                     "the validator refuses it on a row that claims support"),
    PROTOCOL_CONSTRAINT: ("the value is fixed by a registration rather than measured, so the tag "
                          "must name the registration"),
}

#: Statuses that assert evidence supports something. An inference may not carry one.
SUPPORTING_STATUSES = ("Supported within the tested scope", "Mixed / context-limited")

#: The tags whose claim is a reading, and which therefore need something to point at.
CITING_TAGS = (ARTIFACT_READ, OWNER_READING)

#: Any digit at all — used for "a reading may not quote a figure".
_FIGURE = re.compile(r"\d")

#: A figure, for the claim check: a decimal to at least two places, or an integer of at least
#: three digits. A one-decimal token such as `TR 3.2` names a result rather than reporting a
#: measurement, and flagging it would be noise the reader learns to ignore.
_CLAIM_FIGURE = re.compile(r"\d+\.\d{2,}|\b\d{3,}\b")

#: A registration, for `PROTOCOL_CONSTRAINT`: the artifact that fixes a protocol value.
_REGISTRATION = re.compile(r"prereg|registration", re.IGNORECASE)


def row_tag(row) -> str | None:
    """The row's tag, or None when it has none. Missing is not a default."""
    return row.get("provenance")


def _finding(code, subject, message) -> dict:
    return {"code": code, "subject": subject, "message": message}


def check_map(body, root=None) -> list:
    """Return the provenance findings for `body`, empty when every tag holds.

    `root` is optional so the unit tests can check the rules without a filesystem; when it is
    given, every path a citing row names must exist, which is what makes `ARTIFACT_READ` a
    claim about a reading rather than a label an agent can type.
    """
    findings = []
    for row in body.get("rows", []):
        name = row.get("candidate") or "<unnamed row>"
        tag = row_tag(row)

        if "read_for_this_record" in row:
            findings.append(_finding(
                "stale-flag", name,
                "%s still carries `read_for_this_record`; the boolean was replaced by a "
                "provenance tag, and a row carrying both says two different things" % name))

        if tag is None:
            findings.append(_finding(
                "tag-missing", name,
                "%s carries no provenance tag; a missing tag is refused rather than read as a "
                "reading" % name))
            continue

        if tag not in TAGS:
            findings.append(_finding(
                "tag-unknown", name,
                "%s is tagged %r, which is not in the closed set %s; an unrecognised tag is "
                "refused rather than read as a reading" % (name, tag, list(TAGS))))
            continue

        evidence = [path for path in row.get("evidence", []) if path]
        if tag in CITING_TAGS and not evidence:
            findings.append(_finding(
                "unbacked-tag", name,
                "%s is tagged %s and names no record; that tag claims a reading of something"
                % (name, tag)))
        if root is not None:
            for path in evidence:
                if not (root / path).exists():
                    findings.append(_finding(
                        "missing-evidence", name,
                        "%s names %s, which is not on disk; the tag points at a record that "
                        "cannot be checked" % (name, path)))

        if tag == PROTOCOL_CONSTRAINT and not any(_REGISTRATION.search(p) for p in evidence):
            findings.append(_finding(
                "constraint-without-registration", name,
                "%s is tagged %s, which claims a value fixed by a protocol, and names no "
                "registration; a protocol-fixed value reported as a measurement is the defect "
                "this tag exists to prevent" % (name, tag)))

        # A tag that names its source may quote what it read. A tag that names none may not:
        # the figure came from somewhere, and saying where is the whole point of the tag.
        if tag in (OWNER_READING, AGENT_INFERRED) and _FIGURE.search(str(row.get("check", ""))):
            findings.append(_finding(
                "figure-without-reading", name,
                "%s is tagged %s but its check quotes a figure; a figure came from an artifact, "
                "so the row is a transcription and must be tagged %s with the record it read"
                % (name, tag, ARTIFACT_READ)))

        if tag == AGENT_INFERRED and set(row.get("status", [])) & set(SUPPORTING_STATUSES):
            findings.append(_finding(
                "inference-supports", name,
                "%s is an agent inference but claims %s; an inference never stands in for a "
                "reading" % (name, "; ".join(sorted(set(row["status"]) & set(SUPPORTING_STATUSES))))))

    return findings


def _public_sentences(claim) -> str:
    """The words the project is prepared to say in public, and why it withdrew them."""
    return " ".join([claim.get("claim", ""), claim.get("withdrawn_reason", "")])


def _text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def figures_in(claim) -> list:
    """The figures a claim's public sentence quotes, sorted and de-duplicated."""
    return sorted(set(_CLAIM_FIGURE.findall(_public_sentences(claim))))


def check_claims(ledger, root=None) -> list:
    """Every figure a public claim quotes must exist in an artifact the claim cites.

    A claim quoting arithmetic that is in none of its cited artifacts is a transcription of
    something else — the defect of `AGENTS.md` rule 27, aimed at the sentences the project says
    out loud. `root` is optional for the unit tests; without it only the "names nothing" rule
    can run, because nothing can be read.
    """
    findings = []
    for claim in ledger.get("claims", []):
        cid = claim.get("claim_id") or "<unnamed claim>"
        figures = figures_in(claim)
        if not figures:
            continue
        named = [path for path in claim.get("supporting_evidence", []) if path]
        if not named:
            findings.append(_finding(
                "figure-unbacked", cid,
                "%s quotes %s and cites no artifact, so the figure cannot be checked"
                % (cid, ", ".join(figures))))
            continue
        if root is None:
            continue
        for figure in figures:
            if any(figure in _text(Path(root) / path) for path in named):
                continue
            findings.append(_finding(
                "figure-untraceable", cid,
                "%s quotes %s and none of its cited artifacts contains it (%s); either the "
                "figure is a transcription of another record or the citation is wrong"
                % (cid, figure, ", ".join(named))))
            findings[-1]["figure"] = figure
    return findings


def check_ledger(ledger, root=None) -> list:
    """The claim ledger's tags: closed, present, and consistent with the classification.

    Path existence is left to `benchmarks.research_accountability`, which already checks every
    cited evidence file; this checks only what a tag claims. The figure check is separate and
    deliberately not part of this gate: it currently reports two claims whose quoted numbers
    appear in no artifact they cite, and a gate is only added once its findings are resolved.
    """
    findings = []
    for claim in ledger.get("claims", []):
        cid = claim.get("claim_id") or "<unnamed claim>"
        tag = claim.get("provenance")
        if tag is None:
            findings.append(_finding(
                "claim-tag-missing", cid,
                "%s carries no provenance tag, so it cannot say whether its classification rests "
                "on a recorded result or on the owner's reading" % cid))
            continue
        if tag not in TAGS:
            findings.append(_finding(
                "claim-tag-unknown", cid,
                "%s is tagged %r, which is not in the closed set %s" % (cid, tag, list(TAGS))))
            continue
        named = [path for path in claim.get("supporting_evidence", []) if path]
        if tag != AGENT_INFERRED and not named:
            findings.append(_finding(
                "claim-unbacked-tag", cid,
                "%s is tagged %s and cites no artifact; that tag claims support the entry does "
                "not name" % (cid, tag)))
        if tag == AGENT_INFERRED and claim.get("classification") in ("DEMONSTRATED", "SUPPORTED"):
            findings.append(_finding(
                "inference-supports-claim", cid,
                "%s is an agent inference but is classified %s; an inference never stands in "
                "for a reading" % (cid, claim.get("classification"))))
        if tag == PROTOCOL_CONSTRAINT and not any(_REGISTRATION.search(path) for path in named):
            findings.append(_finding(
                "constraint-without-registration", cid,
                "%s is tagged %s, which claims a value fixed by a protocol, and names no "
                "registration" % (cid, tag)))
    return findings


def claim_counts(ledger) -> dict:
    """How many claims carry each tag. Derived, and it refuses an untagged claim."""
    out = {tag: 0 for tag in TAGS}
    for claim in ledger.get("claims", []):
        tag = claim.get("provenance")
        if tag not in out:
            raise ValueError("claim %r has no valid provenance tag: %r"
                             % (claim.get("claim_id"), tag))
        out[tag] += 1
    return out


def where_recorded(figure: str, root) -> list:
    """Artifacts that contain a figure, excluding the generated pages that restate it.

    The point is to turn "this number is not in the artifact you cite" into "this number is in
    that artifact, and the citation is one line away from being right". A figure that appears
    only in prose has no entry here, which is itself the finding.
    """
    skip = {"claim_ledger.json", "CLAIM-LEDGER.md", "RESEARCH-FINDINGS.md",
            "RESEARCH-DASHBOARD.md"}
    found = []
    for path in sorted(Path(root).glob("docs/*")):
        if path.suffix not in (".json", ".md") or path.name in skip:
            continue
        if figure in _text(path):
            found.append(path)
    # A JSON artifact is the measurement; a markdown file is usually a restatement of one.
    # Report the artifact first, because naming it is what would repair the finding.
    found.sort(key=lambda path: (path.suffix != ".json", path.name))
    return [str(path.relative_to(root)) for path in found]


def counts(body) -> dict:
    """How many rows carry each tag. Derived, never typed into the artifact.

    Raises `ValueError` on a row with no valid tag rather than counting it under a default,
    because a summary that silently absorbs an untagged row reports a total that is not true.
    """
    out = {tag: 0 for tag in TAGS}
    for row in body["rows"]:
        tag = row_tag(row)
        if tag not in out:
            raise ValueError("row %r has no valid provenance tag: %r"
                             % (row.get("candidate"), tag))
        out[tag] += 1
    return out


def _sentence(tag: str, n: int, total: int, names: list) -> str:
    if tag == ARTIFACT_READ:
        return ("%d of %d rows are `%s` — %s." % (n, total, tag, MEANINGS[tag]))
    verb = "is" if n == 1 else "are"
    return "%d %s `%s` — %s: %s." % (n, verb, tag, MEANINGS[tag], "; ".join(names))


def render_summary(body) -> str:
    """One paragraph naming the tags in use, with every count derived from the rows.

    The counts used to be typed into the artifact (`checked_rows: 7`) and restated in prose.
    They are computed here instead, so a retagged row changes the paragraph or the page is
    stale — there are two states, and no third one in which the number is merely old.
    """
    per_tag = counts(body)
    total = len(body["rows"])
    used = [tag for tag in TAGS if per_tag[tag]]
    unused = [tag for tag in TAGS if not per_tag[tag]]

    lines = [
        " ".join(
            _sentence(tag, per_tag[tag], total,
                      [row["candidate"] for row in body["rows"] if row_tag(row) == tag])
            for tag in used
        )
    ]
    if unused:
        lines.append(" ".join(
            "`%s` is defined and unused here: %s." % (tag, MEANINGS[tag]) for tag in unused
        ))
    lines.append(
        "The tag is checked rather than described: a tag the row's evidence cannot back is "
        "refused, a row may not quote a figure without claiming the reading that produced it, "
        "and an inference may not carry a supported status."
    )
    return "\n\n".join(lines)


def render_report(mapdoc, ledger, decisions, root=None) -> str:
    """The governance read-out: how much of each record rests on a reading of an artifact.

    Every count here is derived from a record. The claim section is a check rather than a tag
    because a claim already carries its basis in `classification`; a second field would be a
    second thing to keep current, so what is verified instead is mechanical — a quoted figure
    either exists in the artifact the claim cites, or it does not.
    """
    per_tag = counts(mapdoc)
    total = len(mapdoc["rows"])
    lines = ["Provenance — what each statement rests on", "",
             "Bottleneck map (%d rows)" % total]
    for tag in TAGS:
        names = [row["candidate"] for row in mapdoc["rows"] if row_tag(row) == tag]
        if not names:
            detail = "defined and unused: " + MEANINGS[tag]
        elif tag == ARTIFACT_READ:
            detail = MEANINGS[tag]
        else:
            detail = "; ".join(names)
        lines.append("  %-20s %2d  %s" % (tag, per_tag[tag], detail))

    claims = ledger.get("claims", [])
    active = [claim for claim in claims if claim.get("status") == "ACTIVE"]
    per_claim = claim_counts(ledger)
    quoting = [claim for claim in claims if figures_in(claim)]
    figure_count = sum(len(figures_in(claim)) for claim in claims)
    findings = check_claims(ledger, root)
    lines += [
        "",
        "Claims (%d, %d active)" % (len(claims), len(active)),
    ]
    for tag in TAGS:
        ids = [claim["claim_id"] for claim in claims if claim.get("provenance") == tag]
        detail = "; ".join(ids) if ids and tag != ARTIFACT_READ else ("" if ids else "none")
        lines.append("  %-20s %2d  %s" % (tag, per_claim[tag], detail))
    lines += [
        "  public sentences quoting a figure: %d claims, %d figures"
        % (len(quoting), figure_count),
        "  figures absent from every artifact the claim cites: %d"
        % len([f for f in findings if f["code"] == "figure-untraceable"]),
    ]
    for finding in findings:
        lines.append("    - " + finding["message"])
        if finding.get("figure") and root is not None:
            found = where_recorded(finding["figure"], root)
            if found:
                lines.append("      recorded in: " + ", ".join(found[:3]))
            else:
                lines.append("      recorded in: no artifact in docs/ contains this string")

    recorded = decisions.get("decisions", [])
    by_status = {}
    for decision in recorded:
        by_status[decision["status"]] = by_status.get(decision["status"], 0) + 1
    lines += [
        "",
        "Decisions (%d: %s)" % (
            len(recorded),
            ", ".join("%d %s" % (count, status) for status, count in sorted(by_status.items()))),
        "  each decision names the documents behind it; who decided is recorded in the document",
        "  itself, so no decision carries a provenance tag yet",
        "",
        "A tag says who made the reading. A figure either traces to a cited artifact or it does",
        "not, and the second case is the one worth looking at.",
    ]
    return "\n".join(lines)
