"""Every figure in the 0.13.0 changelog entries must match its artifact.

The 0.13.0 section was written by transcribing measured values out of a
dozen artifacts, and a hand-typed number drifts silently: it looks exactly
like a correct one. Two defects of that kind have already been found in
this section -- the sleep split's ``2,436`` was git's ``--stat`` total
rather than the lines removed, and the ablation entry's bands were retyped
from a run whose arm had died at condition D.

This module pins each quoted figure to the artifact and field behind it.
A row passes only when both hold:

  (a) the figure occurs in the 0.13.0 section of ``CHANGELOG.md``, and
  (b) the artifact's value rounds to exactly the quoted string at the
      quoted precision (integers must match exactly).

Rows hold three kinds of evidence. Most read a committed artifact by field
path. A few read a fixed historical commit (the sleep split's ``numstat``,
the pre-sweep documents) -- those are stable because the commit is.
Figures with no artifact behind them are recorded as ``None`` rather than
silently dropped: the section claims things the repository does not
measure, and the check says so instead of inventing provenance.

Two numbers that would otherwise rot are read from the record instead of
from live state: the engine audit's ``20 commits`` is compared with the
audit artifact (with git checked only as a lower bound, so later engine
work cannot fail a historical sentence), and the dropped stashes are read
from the note that inventoried them, because the objects they name are
unreachable and absent from a fresh clone.

A control mutates one quoted figure in a copy of the entry text and
asserts the check reports it: a figure guard that cannot fire is not a
guard.
"""

from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import ast
import inspect
import json
import re
import statistics
import subprocess
from pathlib import Path

from organica import SleepService

ROOT = Path(__file__).resolve().parents[1]
VERSION_HEADING = "## [0.13.0]"


def _entries() -> str:
    """The 0.13.0 section: its version heading up to the next version."""
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    start = text.index(VERSION_HEADING)
    end = text.index("\n## [", start + len(VERSION_HEADING))
    return text[start:end]


def _load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _at(obj, *path):
    for key in path:
        obj = obj[key]
    return obj


def _find_key(obj, key):
    """The first value filed under ``key`` anywhere in a JSON artifact."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = _find_key(value, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = _find_key(value, key)
            if found is not None:
                return found
    return None


def _git(*args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {proc.stderr.strip()}")
    return proc.stdout


def _rounds_to(actual, quoted: str) -> bool:
    q = quoted.replace(",", "").lstrip("+")
    decimals = len(q.split(".")[1]) if "." in q else 0
    try:
        return f"{actual:.{decimals}f}" == f"{float(q):.{decimals}f}"
    except (TypeError, ValueError):
        return False


def _top_defs(source: str) -> dict[str, str]:
    tree = ast.parse(source)
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[node.name] = ast.get_source_segment(source, node)
    return out


def _frozen_engine_len() -> int:
    tree = ast.parse((ROOT / "tests/test_v1_freeze.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, "id", None) == "FROZEN_ENGINE":
                    return len(node.value.elts)
    raise RuntimeError("FROZEN_ENGINE not found")


def _window_mean(rows: list[dict], lo: int, hi: int) -> float:
    """Mirror benchmarks.long_delay_capability._window: half-open, lo <= cycle < hi."""
    recall = [r["recall_at_5"] for r in rows
              if lo <= r["cycle"] < hi and r.get("recall_at_5") is not None]
    return sum(recall) / len(recall)


def _check(entries: str) -> list[dict]:
    """Every row: the figure, its source, the artifact's actual value, verdict."""
    rows: list[dict] = []

    def add(figure: str, source: str, actual, ok, note: str = "") -> None:
        present = True
        if isinstance(ok, bool) and re.fullmatch(r"[-+]?[\d,]+(\.\d+)?", figure):
            present = figure in entries
        verdict = None if ok is None else (bool(ok) and present)
        rows.append({"figure": figure, "source": source, "actual": actual,
                     "ok": verdict, "note": note})

    def num(figure: str, source: str, actual, note: str = "") -> None:
        add(figure, source, actual, _rounds_to(actual, figure), note)

    # --- E1. The version statements were swept ------------------------------
    sweep = (ROOT / "docs/VERSION-STATE-SWEEP-2026-11-09.md").read_text(
        encoding="utf-8").splitlines()
    corrections = []
    inside = False
    for line in sweep:
        if line.startswith("| Where | Said |"):
            inside = True
            continue
        if inside and line.startswith("| `"):
            corrections.append(line)
        elif inside and not line.startswith("|"):
            break
    add("Six current-state claims", "docs/VERSION-STATE-SWEEP-2026-11-09.md, correction table",
        len(corrections), len(corrections) == 6)
    readme_old = _git("show", "1f9f713^:README.md")
    changelog_old = _git("show", "1f9f713^:CHANGELOG.md")
    manual_old = _git("show", "1f9f713^:docs/USER-MANUAL.md").splitlines()
    manual_phase_m = sum(1 for ln in manual_old
                         if "stays untagged" in ln and "Audit trace (Phase M)" not in ln)
    places = readme_old.count("stays untagged") + changelog_old.count("stays untagged") + manual_phase_m
    add("four places", "git show 1f9f713^:{README.md,CHANGELOG.md,USER-MANUAL.md}",
        places, places == 4,
        "README 2 + CHANGELOG 1 + manual Phase M 1; the manual's audit-trace status row "
        "is a different claim")
    facts = (ROOT / "docs/FACTS-SHEET.md").read_text(encoding="utf-8")
    add("AA27", "docs/FACTS-SHEET.md", "AA27" in facts, "AA27" in facts)
    changelog_now = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    add("0.12.1", "CHANGELOG.md 0.12.1 heading",
        "superseded by 0.13.0" in changelog_now,
        "## [0.12.1] — (unreleased; superseded by 0.13.0)" in changelog_now)
    git_row = next((ln for ln in (ROOT / "docs/USER-MANUAL.md").read_text(
        encoding="utf-8").splitlines() if ln.startswith("| Git |")), "")
    add("0.13.0", "docs/USER-MANUAL.md Git status row",
        "0.13.0" in git_row, "0.13.0" in git_row and "0.12.1" not in git_row)

    # --- E2. The test-count recorder keeps its recorded date ------------------
    test_count = (ROOT / "tests/test_test_count.py").read_text(encoding="utf-8")
    date_rule_tests = ["test_an_unchanged_result_keeps_the_recorded_date",
                       "test_a_changed_result_takes_the_day_it_ran",
                       "test_the_date_rule_ignores_when_the_result_was_seen"]
    present = [name for name in date_rule_tests if f"def {name}(" in test_count]
    add("three tests", "tests/test_test_count.py, date-rule tests added by e219403",
        len(present), len(present) == 3, ", ".join(present))
    markers = [p for p in ROOT.rglob("*.md")
               if "tests:auto" in p.read_text(errors="ignore")
               and not ({".venv", ".scratch"} & set(p.parts))]
    add("both documents", "markdown files carrying tests:auto",
        len(markers), len(markers) == 2,
        ", ".join(str(p.relative_to(ROOT)) for p in markers))

    # --- E3. The superseded stashes -----------------------------------------
    # Read from the note, not from the objects: the stashes were dropped and
    # are unreachable, so a fresh clone cannot inspect them (see the note's
    # own disposal section).
    stash_note = (ROOT / "docs/SUPERSEDED-STASHES-2026-11-09.md").read_text(
        encoding="utf-8")
    stash_rows = [ln for ln in stash_note.splitlines() if re.match(r"^\| `stash@", ln)]
    add("two stashes", "docs/SUPERSEDED-STASHES-2026-11-09.md, inventory table",
        len(stash_rows), len(stash_rows) == 2)
    add("08f3cb1", "docs/SUPERSEDED-STASHES-2026-11-09.md, correction section",
        "08f3cb1" in stash_note, "08f3cb1" in stash_note)
    add("the dangling WIP commit", "docs/SUPERSEDED-STASHES-2026-11-09.md, correction section",
        "dangling" in stash_note and "organica/sleep_selection.py" in stash_note,
        "dangling" in stash_note and "organica/sleep_selection.py" in stash_note,
        "the commit itself may be pruned; the note is the record of what it held")
    stash_ids = ["99ef5b56af588a325825dabedfbc5a114d7333ab",
                 "8cdf2b972df8052b2e4fa06a1246b95fef70d86c"]
    names = ["_parse_tag_refs", "_remote_ref",
             "test_the_tag_parser_prefers_the_peeled_commit",
             "test_the_tag_parser_accepts_a_lightweight_tag",
             "test_the_tag_parser_returns_none_when_the_tag_is_absent",
             "test_the_bare_query_really_did_return_the_wrong_object",
             "test_the_release_check_fires_when_the_tag_is_behind_master"]
    recorded = all(s in stash_note for s in stash_ids) and all(n in stash_note for n in names)
    add("byte-identical", "docs/SUPERSEDED-STASHES-2026-11-09.md, code-block comparison",
        "All seven are `SAME`" in stash_note, recorded and "All seven are `SAME`" in stash_note)
    committed = _top_defs((ROOT / "tests/test_versioning.py").read_text(encoding="utf-8"))
    add("seven definitions", "tests/test_versioning.py, top-level definitions",
        [n for n in names if n in committed], all(n in committed for n in names))

    # --- E4. Burst deaths matched against lattice deaths ---------------------
    age = _load("docs/q052_age_matched.json")
    num("10", "docs/q052_age_matched.json .tolerance", _at(age, "tolerance"))
    num("0.10", "docs/q052_age_matched.json .band", _at(age, "band"))
    add("six lattice factors", "docs/q052_age_matched.json .factors_run",
        len(_at(age, "factors_run")), len(_at(age, "factors_run")) == 6)
    nearest = sorted({m["nearest_lattice_death"] for m in _at(age, "matches")})
    add("112 and 150", "docs/q052_age_matched.json .matches[*].nearest_lattice_death",
        nearest, nearest == [112, 150])
    ratios = [r["mass_ratio"] for r in _at(age, "age_trend")]
    band = f"{min(ratios):.3f}-{max(ratios):.3f}"
    add("0.578-0.610", "docs/q052_age_matched.json .age_trend[*].mass_ratio",
        band, band == "0.578-0.610")
    num("0.032", "docs/q052_age_matched.json .age_spread", _at(age, "age_spread"))
    brackets = [f"{b['estimate']:.3f}" for b in _at(age, "bracketed")]
    add("0.582", "docs/q052_age_matched.json .bracketed[*].estimate",
        brackets, all(b == "0.582" for b in brackets))
    burst = [f"{b['mass_ratio']:.3f}" for b in _at(age, "burst")]
    add("0.308, 0.315 and 0.034", "docs/q052_age_matched.json .burst[*].mass_ratio",
        burst, burst == ["0.308", "0.315", "0.034"])
    live = [f"{r['mass_ratio']:.4f}" if r["mass_ratio"] > 0.99 else f"{r['mass_ratio']:.3f}"
            for r in _at(age, "lattice_live")]
    add("0.9998 and 0.934", "docs/q052_age_matched.json .lattice_live[*].mass_ratio",
        live, live == ["0.9998", "0.934"])
    cycles = sorted(b["death_cycle"] for b in _at(age, "burst"))
    add("131-134", "docs/q052_age_matched.json .burst[*].death_cycle",
        f"{cycles[0]}-{cycles[-1]}", cycles[0] == 131 and cycles[-1] == 134)
    deaths = [d["death_cycle"] for d in _at(age, "lattice_deaths")]
    add("300", "docs/q052_age_matched.json .lattice_deaths[*].death_cycle",
        max(deaths), max(deaths) == 300)
    add("AGE_MATCH_UNAVAILABLE", "docs/q052_age_matched.json .label",
        _at(age, "label"), _at(age, "label") == "AGE_MATCH_UNAVAILABLE")

    # --- E5. Q053 narrowed to one mechanism ---------------------------------
    design_doc = (ROOT / "docs/COMPETITION-PRESERVATION-DESIGN.md").read_text(
        encoding="utf-8").splitlines()
    start = design_doc.index("## 3. Candidate mechanisms (none chosen)")
    candidates = []
    for line in design_doc[start:]:
        if line.startswith("## 4."):
            break
        if line.startswith("| **"):
            candidates.append(line)
    add("five candidate interventions", "docs/COMPETITION-PRESERVATION-DESIGN.md §3 table",
        len(candidates), len(candidates) == 5)
    prereg_doc = (ROOT / "docs/Q053-MECHANISM-PREREGISTRATION.md").read_text(
        encoding="utf-8").splitlines()
    arm_rows = [ln for ln in prereg_doc
                if ln.startswith("| control |") or ln.startswith("| treatment |")]
    add("0.95", "docs/Q053-MECHANISM-PREREGISTRATION.md arm table",
        [ln.count("0.95") for ln in arm_rows],
        len(arm_rows) == 2 and all("0.95" in ln for ln in arm_rows))
    q053 = _load("docs/q053_mechanism_prereg.json")
    add("one mechanism", "docs/q053_mechanism_prereg.json .mechanism.name",
        _at(q053, "mechanism", "name"), _at(q053, "mechanism", "implemented") is False)
    add("2", "docs/q053_mechanism_prereg.json .design.arms",
        len(_at(q053, "design", "arms")), len(_at(q053, "design", "arms")) == 2)
    add("10", "docs/q053_mechanism_prereg.json .design.seeds",
        len(_at(q053, "design", "seeds")), len(_at(q053, "design", "seeds")) == 10)
    add("20", "docs/q053_mechanism_prereg.json .design.cells",
        _at(q053, "design", "cells"), _at(q053, "design", "cells") == 20)
    num("300", "docs/q053_mechanism_prereg.json .design.cycles", _at(q053, "design", "cycles"))
    add("5", "docs/q053_mechanism_prereg.json .design.k",
        _at(q053, "design", "k"), _at(q053, "design", "k") == 5)

    # --- E6. Q052 census, VOID, and amendment A2 ----------------------------
    census = _load("docs/q052_competition_census.json")
    num("299", "docs/q052_competition_census.json .control.last_live_cycle",
        _at(census, "control", "last_live_cycle"))
    num("300", "docs/q052_competition_census.json .control.death_cycle",
        _at(census, "control", "death_cycle"))
    supports = _at(census, "control", "supports")
    add("866 = 433 + 433", "docs/q052_competition_census.json .control",
        _at(census, "control", "support_count"),
        _at(census, "control", "support_count") == 866 and supports == [433, 433])
    num("0.578", "docs/q052_competition_census.json .control.mass_ratio",
        _at(census, "control", "mass_ratio"))
    framing = (ROOT / "docs/Q052-FRAMING-DESIGN.md").read_text(encoding="utf-8")
    num("0.90", "docs/Q052-FRAMING-DESIGN.md §3, admissibility floor",
        float(re.search(r"at least (0\.90)", framing).group(1)))
    add("empty competing census at death",
        "docs/q052_competition_census.json .control.subjects_with_competing_at_death",
        _at(census, "control", "subjects_with_competing_at_death"),
        _at(census, "control", "subjects_with_competing_at_death") == {})
    a2 = _load("docs/q052_competition_census_a2.json")
    add("0.578", "docs/q052_competition_census_a2.json .control.mass_ratio",
        _rounds_to(_at(a2, "control", "mass_ratio"), "0.578")
        and _at(a2, "control", "mass_floor_met"),
        _rounds_to(_at(a2, "control", "mass_ratio"), "0.578")
        and _at(a2, "control", "mass_floor_met"))
    add("three burst seeds", "docs/q052_competition_census_a2.json .cells",
        len(_at(a2, "cells")), len(_at(a2, "cells")) == 3)
    a2_ratios = [f"{c['mass_ratio']:.3f}" for c in _at(a2, "cells")]
    add("0.308, 0.315 and 0.034", "docs/q052_competition_census_a2.json .cells[*].mass_ratio",
        a2_ratios, a2_ratios == ["0.308", "0.315", "0.034"])
    add("no competing census at death",
        "docs/q052_competition_census_a2.json .cells[*].subjects_with_competing_at_death",
        [c["subjects_with_competing_at_death"] for c in _at(a2, "cells")],
        all(c["subjects_with_competing_at_death"] == {} for c in _at(a2, "cells")))
    add("DIFFERENT_SUPPORT_COLLAPSE", "docs/q052_competition_census_a2.json .label",
        _at(a2, "label"), _at(a2, "label") == "DIFFERENT_SUPPORT_COLLAPSE")

    # --- E7. Thirteen closed answers reopened (Q021 later closed) ------------
    registry = _load("docs/research_question_registry.json")
    reopened = _at(registry, "reopening", "reopened")
    expected = ["Q004", "Q005", "Q017", "Q024", "Q029", "Q030",
                "Q031", "Q032", "Q036", "Q043", "Q044", "Q051"]
    add("Twelve closed questions", "docs/research_question_registry.json .reopening.reopened",
        len(reopened), reopened == expected)
    add("0.13.0", "docs/research_question_registry.json .reopening.engine_version",
        _at(registry, "reopening", "engine_version"),
        _at(registry, "reopening", "engine_version") == "0.13.0")
    pin = _load("docs/engine_pin.json")
    add("fourteen files", "docs/engine_pin.json .files", len(_at(pin, "files")),
        len(_at(pin, "files")) == 14)
    kept = _at(registry, "reopening", "kept_closed")
    add("17", "docs/research_question_registry.json .reopening.kept_closed",
        len(kept), len(kept) == 17,
        "Q002, Q006 and Q021 closed on 2026-11-09 after their 0.13.0 re-measurements, and Q055 closed on 2026-11-11, so the record now holds 17")
    named = sum(1 for e in kept if "records engine_version 0.13.0" in e["reason"])
    governance = sum(1 for e in kept
                     if "the answer is about" in e["reason"]
                     or "retired on design logic" in e["reason"]
                     or "retired for the same design reason" in e["reason"])
    add("nine ... and four", "docs/research_question_registry.json .kept_closed[*].reason",
        f"{named}+{governance}", named == 9 and governance == 4)
    ledger = _load("docs/claim_ledger.json")
    claims = {c["claim_id"]: c for c in _at(ledger, "claims")}
    add("C004", "docs/claim_ledger.json .claims[C004].classification",
        claims["C004"]["classification"], claims["C004"]["classification"] == "HYPOTHESIS")

    # --- E8. Every run artifact names the engine's bytes ---------------------
    add("engine_sha256", "benchmarks/engine_stamp.py", "N/A", None,
        "entry quotes no measured figure; names fields and rules only")

    # --- E9. The sleep-path split is proven behaviour-preserving -------------
    numstat = _git("show", "--numstat", "--format=", "7becdb5").strip().splitlines()
    stats = {}
    for line in numstat:
        added_s, removed_s, path = line.split("\t")
        stats[path] = (int(added_s), int(removed_s))
    sleep_added, sleep_removed = stats["organica/sleep.py"]
    add("2,400", "git show --numstat 7becdb5 -- organica/sleep.py",
        sleep_removed, sleep_removed == 2400,
        f"sleep.py: +{sleep_added}/-{sleep_removed}; the superseded 2,436 was the --stat "
        f"changed-line total (+{sleep_added} and -{sleep_removed}), not lines removed")
    moved = ["organica/sleep_extraction.py", "organica/sleep_selection.py",
             "organica/sleep_synthesis.py", "organica/sleep_inquiry.py",
             "organica/candidates.py"]
    moved_added = sum(stats[p][0] for p in moved)
    num("2,313", "git show --numstat 7becdb5, additions to the five new modules", moved_added)
    add("four sleep modules", "git show --numstat 7becdb5, new module paths",
        [p for p in moved if p in stats], all(p in stats for p in moved),
        "module gains: " + ", ".join(f"{p.split('/')[-1]} +{stats[p][0]}"
                                     for p in moved if p in stats))
    stale = []
    for path in ("CHANGELOG.md", "tests/test_sleep_split_equivalence.py"):
        for number, line in enumerate((ROOT / path).read_text(encoding="utf-8").splitlines(), 1):
            if "2,436" in line:
                stale.append(f"{path}:{number}")
    row96 = next(ln for ln in (ROOT / "docs/USER-MANUAL.md").read_text(
        encoding="utf-8").splitlines() if ln.startswith("| 96 |"))
    if "2,436" in row96 or "2,400" not in row96:
        stale.append("docs/USER-MANUAL.md action row 96")
    add("no stale 2,436", "CHANGELOG 13 entries, split test docstring, manual action row 96",
        stale or "(none)", stale == [], "the revision-log row may quote it as superseded")
    split_test = (ROOT / "tests/test_sleep_split_equivalence.py").read_text(encoding="utf-8")
    cycles_line = re.search(r"^CYCLES = (\d+)$", split_test, re.M).group(1)
    add("twelve cycles", "tests/test_sleep_split_equivalence.py CYCLES",
        cycles_line, cycles_line == "12")
    add("7becdb5", "git cat-file -t 7becdb5", _git("cat-file", "-t", "7becdb5").strip(),
        _git("cat-file", "-t", "7becdb5").strip() == "commit")

    # --- E10. The engine guard was unlocked and re-baselined -----------------
    frozen = _frozen_engine_len()
    add("seven frozen files", "tests/test_v1_freeze.py FROZEN_ENGINE", frozen, frozen == 7)
    audit = _load("docs/engine_version_audit.json")
    add("0.12.0", "docs/engine_version_audit.json .guard_disabled_at_version",
        _at(audit, "guard_disabled_at_version"),
        _at(audit, "guard_disabled_at_version") == "0.12.0")

    # --- E11. The engine-version audit --------------------------------------
    # The audit is a snapshot; later engine work must not fail a sentence
    # about what it found. Compare the changelog with the artifact, then
    # check git only as a lower bound on what the snapshot could have seen.
    organica_stats = _git("diff", "--numstat", "v0.9.0..HEAD", "--", "organica/").strip().splitlines()
    live_added = sum(int(ln.split("\t")[0]) for ln in organica_stats)
    live_removed = sum(int(ln.split("\t")[1]) for ln in organica_stats)
    live_commits = int(_git("rev-list", "--count", "v0.9.0..HEAD", "--", "organica/").strip())
    audit_commits = _at(audit, "commits_touching_organica_since_freeze")
    add("20 commits", "docs/engine_version_audit.json .commits_touching_organica_since_freeze",
        audit_commits, audit_commits == 20)
    add("20 commits (git)", "git rev-list --count v0.9.0..HEAD -- organica/",
        live_commits, live_commits >= audit_commits,
        "the snapshot cannot exceed git's live count; engine work after the audit raises "
        "the live count without changing the recorded figure")
    num("3,043", "docs/engine_version_audit.json .insertions", _at(audit, "insertions"))
    add("3,043 (git)", "git diff v0.9.0..HEAD -- organica/, insertions",
        live_added, live_added >= _at(audit, "insertions"))
    num("1,791", "docs/engine_version_audit.json .deletions", _at(audit, "deletions"))
    add("1,791 (git)", "git diff v0.9.0..HEAD -- organica/, deletions",
        live_removed, live_removed >= _at(audit, "deletions"))
    add("nine files", "docs/engine_version_audit.json .files_changed",
        _at(audit, "files_changed"),
        _at(audit, "files_changed") == 9 and len(organica_stats) >= 9)
    frozen_changed = _at(audit, "frozen_files_changed")
    add("two of the seven frozen ones", "docs/engine_version_audit.json .frozen_files_changed",
        f"{len(frozen_changed)} of {len(_at(audit, 'frozen_files_list'))}",
        len(frozen_changed) == 2 and len(_at(audit, "frozen_files_list")) == 7)
    audit_ids = [e["id"] for e in _at(audit, "reopened")]
    add("Q001, Q002, Q003, Q007, Q008 and Q018", "docs/engine_version_audit.json .reopened",
        audit_ids, audit_ids == ["Q001", "Q002", "Q003", "Q007", "Q008", "Q018"])
    add("C001-C003", "docs/engine_version_audit.json .claims_downgraded",
        _at(audit, "claims_downgraded"),
        _at(audit, "claims_downgraded") == ["C001", "C002", "C003"])

    # --- E12. Q051 -----------------------------------------------------------
    q051d = _load("docs/long_delay_capability_design.json")
    q051c = _load("docs/long_delay_capability_confirm.json")
    calib = _load("docs/long_delay_capability_burst_L1_calibration.json")
    add("0.95", "docs/long_delay_capability_design.json .factors",
        _at(q051d, "factors"), _at(q051d, "factors") == [0.95, 0.9925])
    gates_d = _at(q051d, "gates")
    add("seven gates", "docs/long_delay_capability_design.json .gates",
        len(gates_d), len(gates_d) == 7 and all(gates_d.values()))
    add("Five design seeds", "docs/long_delay_capability_design.json .design_seeds",
        len(_at(q051d, "design_seeds")), len(_at(q051d, "design_seeds")) == 5)
    num("0.0412", "docs/long_delay_capability_design.json .delta", _at(q051d, "delta"))
    num("0.0477", "docs/long_delay_capability_design.json .late_gap_median",
        _at(q051d, "late_gap_median"))
    num("0.0275", "docs/long_delay_capability_design.json .late_gap_sd",
        _at(q051d, "late_gap_sd"))
    late_gaps, early_gaps = [], []
    for seed in _at(q051d, "design_seeds"):
        lo = _load(f"docs/capability_design/parts/{seed}_0.95.json")["rows"]
        hi = _load(f"docs/capability_design/parts/{seed}_0.9925.json")["rows"]
        late_gaps.append(_window_mean(hi, 240, 300) - _window_mean(lo, 240, 300))
        early_gaps.append(_window_mean(hi, 40, 90) - _window_mean(lo, 40, 90))
    negatives = sum(1 for g in late_gaps if g < 0)
    add("one seed reversed", "docs/capability_design/parts/*, per-seed late gaps",
        negatives, negatives == 1,
        "gaps: " + ", ".join(f"{g:+.4f}" for g in late_gaps)
        + f"; median {statistics.median(late_gaps):.4f}, sd {statistics.stdev(late_gaps):.4f}")
    early_median = statistics.median(early_gaps)
    add("0.010", "docs/capability_design/parts/*, per-seed early gaps",
        f"median {early_median:+.4f}", early_median > 0.010,
        "half-open window as the harness; derived early median +0.0138 matches manual "
        "action row 86, and the changelog quotes no early median")
    add("Ten seeds", "docs/long_delay_capability_confirm.json .confirm_seeds",
        len(_at(q051c, "confirm_seeds")), len(_at(q051c, "confirm_seeds")) == 10)
    num("0.0265", "docs/long_delay_capability_confirm.json .late_gap_median",
        _at(q051c, "late_gap_median"))
    add("9 of 10", "docs/long_delay_capability_confirm.json .late_positive",
        _at(q051c, "late_positive"), _at(q051c, "late_positive") == 9)
    num("0.0119", "docs/long_delay_capability_confirm.json .early_gap_median",
        _at(q051c, "early_gap_median"))
    add("6 of 10", "docs/long_delay_capability_confirm.json .transition_positive",
        _at(q051c, "transition_positive"), _at(q051c, "transition_positive") == 6)
    gates_c = _at(q051c, "gates")
    add("All seven gates pass", "docs/long_delay_capability_confirm.json .gates",
        f"{sum(gates_c.values())}/{len(gates_c)}",
        len(gates_c) == 7 and all(gates_c.values())
        and _at(q051c, "label") == "INCONCLUSIVE")
    add("300 cycles", "docs/long_delay_capability_burst_L1_calibration.json .cycles",
        _at(calib, "cycles"), _at(calib, "cycles") == 300)
    survivors = _at(calib, "survivors_at_300")
    add("0.95 and 1.0", "docs/long_delay_capability_burst_L1_calibration.json .survivors_at_300",
        survivors, survivors == ["0.95", "1"])
    arms = _at(calib, "arms")
    add("0.99 and 0.9925", "docs/long_delay_capability_burst_L1_calibration.json .arms",
        {k: v["final_theories"] for k, v in arms.items()},
        arms["0.99"]["final_theories"] == 0 and arms["0.9925"]["final_theories"] == 0)

    # --- E13. The decay threshold's edge ------------------------------------
    threshold = _load("docs/decay_threshold.json")
    screen = _at(threshold, "screen")
    add("24-factor screen", "docs/decay_threshold.json .screen", len(screen), len(screen) == 24)
    screen_factors = [c["factor"] for c in screen]
    add("0.9901 to 0.9924", "docs/decay_threshold.json .screen[*].factor",
        f"{screen_factors[0]:g}-{screen_factors[-1]:g}",
        screen_factors[0] == 0.9901 and screen_factors[-1] == 0.9924)
    max_death = max(c["death_cycle"] for c in screen)
    add("301", "docs/decay_threshold.json .screen[*].death_cycle", max_death, max_death < 301)
    tail = {f"{c['factor']:g}": c["death_cycle"] for c in screen if c["factor"] in (0.9923, 0.9924)}
    add("0.9923 and 0.9924 reach 300", "docs/decay_threshold.json .screen[22:24]",
        tail, tail == {"0.9923": 300, "0.9924": 300})
    probe = _load("docs/decay_support_probe.json")
    probe_factors = _at(probe, "factors")
    add("0.9925", "docs/decay_support_probe.json .factors['0.9925']",
        (probe_factors["0.9925"]["last_live_cycle"], probe_factors["0.9925"]["death_cycle"]),
        probe_factors["0.9925"]["last_live_cycle"] == 300 and 0.9925 not in screen_factors)
    edge = _load("docs/decay_threshold_edge.json")
    add("20302701-20302703", "docs/decay_threshold_edge.json .seeds",
        _at(edge, "seeds"), _at(edge, "seeds") == [20302701, 20302702, 20302703])
    add("dies at 300 on all three", "docs/decay_threshold_edge.json .cells[*].death_cycle",
        [c["death_cycle"] for c in _at(edge, "cells")],
        all(c["death_cycle"] == 300 for c in _at(edge, "cells")))
    support_doc = (ROOT / "docs/DECAY-SUPPORT-PROBE.md").read_text(encoding="utf-8")
    add("49-count", "docs/DECAY-SUPPORT-PROBE.md, earlier inference",
        "49" in support_doc and "inference" in support_doc,
        "49" in support_doc and "inference" in support_doc)
    live_theories = _at(probe_factors, "0.9924", "window", "299", "theories")
    bravo = next(t for t in live_theories if t["subject"] == "bravo")
    add("866 = 433 + 433", "docs/decay_support_probe.json .factors['0.9924'].window['299']",
        (bravo["support_count"], [h["support_count"] for h in bravo["hypotheses"]]),
        bravo["support_count"] == 866
        and [h["support_count"] for h in bravo["hypotheses"]] == [433, 433])
    top_300 = _at(probe_factors, "0.9925", "window", "300", "theories")
    alpha = next(t for t in top_300 if t["subject"] == "alpha")
    add("1309 = 438 + 438 + 433",
        "docs/decay_support_probe.json .factors['0.9925'].window['300']",
        (alpha["support_count"], [h["support_count"] for h in alpha["hypotheses"]]),
        alpha["support_count"] == 1309
        and [h["support_count"] for h in alpha["hypotheses"]] == [438, 438, 433])
    bracket = _load("docs/decay_paired_bracket.json")
    add("alive at 301", "docs/decay_paired_bracket.json .pairs",
        [(p["lower_death"], p["upper_death"]) for p in _at(bracket, "pairs")],
        all(p["lower_death"] == 300 and p["upper_death"] == 301 and p["upper_alive"]
            for p in _at(bracket, "pairs")))
    competition = _load("docs/decay_competition_probe.json")
    cells = _at(competition, "cells")
    add("299", "docs/decay_competition_probe.json .cells[*].last_live_cycle",
        [c["last_live_cycle"] for c in cells], all(c["last_live_cycle"] == 299 for c in cells))
    per_subject = []
    for cell in cells:
        counts: dict[str, int] = {}
        for row in cell["retained_at_death"]:
            if row["expectation"] != "high_structural_significance":
                counts[row["subject"]] = counts.get(row["subject"], 0) + 1
        per_subject.append(sorted(counts.values()))
    add("one competing hypothesis per subject at cycle 300",
        "docs/decay_competition_probe.json .cells[*].retained_at_death",
        per_subject, all(all(v == 1 for v in counts) for counts in per_subject)
        and all(c["theories_at_death"] == 0 for c in cells))
    add("866", "docs/decay_competition_probe.json .cells[*].top_theory",
        [c["top_theory"]["support_count"] for c in cells],
        all(c["top_theory"]["support_count"] == 866 for c in cells))

    # --- E14. The ablation harness runs all eleven conditions ----------------
    abl = _load("docs/ablation_study_0.13.0.json")
    conditions = abl["conditions"]
    comps = abl["comparisons"]
    add("11", "docs/ablation_study_0.13.0.json .conditions", len(conditions),
        len(conditions) == 11)
    num("300", "docs/ablation_study_0.13.0.json .protocol.cycles",
        _at(abl, "protocol", "cycles"))
    add("0.13.0", "docs/ablation_study_0.13.0.json .engine_version",
        abl["engine_version"], abl["engine_version"] == "0.13.0")
    add("6e0ff24d84d3", "docs/ablation_study_0.13.0.json .engine_commit",
        abl["engine_commit"], abl["engine_commit"].startswith("6e0ff24d84d3"))
    add("ed0851d1", "docs/ablation_study_0.13.0.json .engine_sha256",
        abl["engine_sha256"], abl["engine_sha256"].startswith("ed0851d1"))
    add("2026-11-09T03:01:52Z", "docs/ablation_study_0.13.0.json .generated_at",
        abl["generated_at"], abl["generated_at"] == "2026-11-09T03:01:52Z")
    num("59.440", "docs/ablation_study_0.13.0.json .comparisons.A.es_full",
        comps["A"]["es_full"], "the full system's ES; O_FULL is the reference condition")
    bands = {"A": "existential", "J": "existential", "I": "important",
             "B": "cosmetic", "C": "cosmetic", "D": "cosmetic", "E": "cosmetic",
             "F": "cosmetic", "G": "cosmetic", "H": "cosmetic"}
    for key, band in bands.items():
        add(band, f"docs/ablation_study_0.13.0.json .comparisons.{key}.impact_band",
            comps[key]["impact_band"], comps[key]["impact_band"] == band)
    num("59.440", "docs/ablation_study_0.13.0.json .comparisons.A.impact", comps["A"]["impact"])
    num("59.440", "docs/ablation_study_0.13.0.json .comparisons.J.impact", comps["J"]["impact"])
    num("15.180", "docs/ablation_study_0.13.0.json .comparisons.I.impact", comps["I"]["impact"])
    for key, figure in zip("BCDEFGH",
                           ["0.000", "0.084", "2.504", "-0.574", "-0.876", "0.193", "-0.224"]):
        num(figure, f"docs/ablation_study_0.13.0.json .comparisons.{key}.impact",
            comps[key]["impact"])
    signature = inspect.signature(SleepService._natural_selection)
    positional = [p for p in signature.parameters.values()
                  if p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
                  and p.default is inspect.Parameter.empty]
    add("five", "organica SleepService._natural_selection, required G1 parameters",
        [p.name for p in positional if p.name != "self"],
        len([p for p in positional if p.name != "self"]) == 5,
        "the pre-repair D override spelled exactly these and did not accept the G2-G8 keywords")
    add("four conditions", "no artifact", "N/A", None,
        "the failed 2026-11-09 run produced no artifact; the count is a report of the "
        "aborted run's console, not a recorded value")

    # --- E15. The four remaining decay questions are registered and scoped --
    dur = _load("docs/store_time_role_durability.json")
    num("16,962", "docs/store_time_role_durability.json .stored_rows",
        _at(dur, "stored_rows"))
    add("405", "docs/store_time_role_durability.json .measurement",
        (_at(dur, "measurement", "primed_predictions"),
         _at(dur, "measurement", "recoverable")),
        _at(dur, "measurement", "primed_predictions") == 405
        and _at(dur, "measurement", "recoverable") == 405)
    add("41", "docs/research_question_registry.json (2026-11-07 tally, superseded)", 41, None,
        "the registry now carries 51 questions; this entry records the 41/18/12/6/5 tally of "
        "2026-11-07 and is not restated against the later registry")

    # --- E16. The decay-attribution replication is pre-registered ------------
    study_prereg = _load("docs/decay_attribution_study.json")
    add("20301201-20301212", "docs/decay_attribution_study.json .seeds",
        (_at(study_prereg, "seeds")[0], _at(study_prereg, "seeds")[-1]),
        _at(study_prereg, "seeds") == list(range(20301201, 20301213)))
    add("24", "docs/decay_attribution_study.json .cells",
        len(_at(study_prereg, "cells")), len(_at(study_prereg, "cells")) == 24)
    num("300", "docs/decay_attribution_study.json .cycles", _at(study_prereg, "cycles"))
    num("12", "docs/decay_attribution_study.json .degree", _at(study_prereg, "degree"))
    add("six gates", "docs/decay_attribution_study.json .gates",
        sorted(_at(study_prereg, "gates")), len(_at(study_prereg, "gates")) == 6)
    add("2,609", "no artifact", None, None,
        "the unused-seed count came from a docs/ scan at registration time; no committed "
        "artifact records it, so it is declared rather than pinned")

    # --- E17. An uncertified falsifier run is void, not a verdict ------------
    falsifier = _load("docs/decay_falsifier.json")
    add("VOID_REFERENCE_DEAD", "docs/decay_falsifier.json .verdict",
        _at(falsifier, "verdict"), _at(falsifier, "verdict") == "VOID_REFERENCE_DEAD")
    add("REPRODUCES", "docs/decay_falsifier.json .series_verdict",
        _at(falsifier, "series_verdict"), _at(falsifier, "series_verdict") == "REPRODUCES")
    add("certified: false", "docs/decay_falsifier.json .certified",
        _at(falsifier, "certified"), _at(falsifier, "certified") is False)

    # --- E18. The Q028 trace resolves through the role pair ------------------
    prov = _load("docs/transfer_provenance.json")
    pair = _at(prov, "pair_measurement")
    num("0.5714", "docs/transfer_provenance.json .pair_measurement.share", pair["share"])
    add("8 of 14", "docs/transfer_provenance.json .pair_measurement",
        (pair["resolved"], pair["denominator"]),
        pair["resolved"] == 8 and pair["denominator"] == 14)
    add("0 of 14", "docs/transfer_provenance.json .measurement",
        (_at(prov, "measurement", "resolved"),
         _at(prov, "measurement", "transfer_events")),
        _at(prov, "measurement", "resolved") == 0
        and _at(prov, "measurement", "transfer_events") == 14)
    num("80", "docs/transfer_provenance.json .cycles", _at(prov, "cycles"))

    # --- E19. Decay attribution on the degree-12 hub -------------------------
    att = _load("docs/decay_attribution.json")
    eng = _at(att, "by_arm", "engine")
    ctl = _at(att, "by_arm", "no_temporal_decay")
    num("35", "docs/decay_attribution.json .by_arm.engine.peak", eng["peak"])
    num("15", "docs/decay_attribution.json .by_arm.engine.peak_cycle_range[0]",
        eng["peak_cycle_range"][0])
    num("16", "docs/decay_attribution.json .by_arm.engine.first_fall_range[0]",
        eng["first_fall_range"][0])
    decay_to_half = eng["peak_cycle_range"][0] + eng["half_life_range"][0]
    add("80", "docs/decay_attribution.json .peak_cycle + .half_life", decay_to_half,
        decay_to_half == 80,
        "the artifact stores the half-life as 65 cycles after the peak at 15; the entry "
        "quotes the absolute cycle 80")
    num("173", "docs/decay_attribution.json .by_arm.engine.zero_cycle_range[0]",
        eng["zero_cycle_range"][0])
    num("42", "docs/decay_attribution.json .by_arm.no_temporal_decay.peak", ctl["peak"])
    num("30", "docs/decay_attribution.json .by_arm.no_temporal_decay.final_stable_range[0]",
        ctl["final_stable_range"][0])
    num("1.25", "docs/decay_attribution.json .ratio_at_peak[0]",
        _at(att, "ratio_at_peak")[0])
    num("0.375", "docs/decay_attribution.json .ratio_after_peak[0]",
        _at(att, "ratio_after_peak")[0])
    num("31.03", "docs/decay_attribution.json .death_shares.below_threshold",
        _at(att, "death_shares", "below_threshold") * 100,
        "the artifact stores the share 0.3103; the entry quotes the percentage")
    num("68.97", "docs/decay_attribution.json .death_shares.decayed",
        _at(att, "death_shares", "decayed") * 100,
        "the artifact stores the share 0.6897; the entry quotes the percentage")
    hub_growth = (_at(att, "hub_frequency_final")[0]
                  / _at(att, "hub_frequency_at_peak")[0])
    add("18", "docs/decay_attribution.json hub_frequency final/peak", round(hub_growth),
        round(hub_growth) == 18, "1608 / 88 = 18.3x, quoted as 18x")
    sum_growth = (_at(att, "temporal_sum_final")[0]
                  / _at(att, "temporal_sum_at_peak")[0])
    add("1.8", "docs/decay_attribution.json temporal_sum final/peak",
        round(sum_growth, 1), round(sum_growth, 1) == 1.8, "1325 / 726 = 1.8x")
    last_theory = _at(att, "theory_zero_range")[0] - 1
    add("28", "docs/decay_attribution.json .theory_zero_range[0] - 1", last_theory,
        last_theory == 28, "theory zero at 29, so the last live cycle is 28")

    # --- E20. A dead reference arm voids the verdict -------------------------
    num("37", "docs/decay_falsifier.json .theories.cycles_with_any",
        _at(falsifier, "theories", "cycles_with_any"))
    num("38", "docs/decay_falsifier.json .theories.last_nonzero_cycle",
        _at(falsifier, "theories", "last_nonzero_cycle"))
    registry = _load("docs/research_question_registry.json")
    by_id = {q["id"]: q for q in _at(registry, "questions")}
    add("Q040", "docs/research_question_registry.json .questions[Q040].status",
        by_id["Q040"]["status"], by_id["Q040"]["status"] == "closed")
    add("Q041", "docs/research_question_registry.json .questions[Q041].status",
        by_id["Q041"]["status"], by_id["Q041"]["status"] == "closed")
    add("Q042", "docs/research_question_registry.json .questions[Q042] (superseded)", None, None,
        "Q042 was open when the entry was written and the registry has since closed it; the "
        "entry records the 2026-11-07 state")

    # --- E21. No store-time licensing role is recorded -----------------------
    num("16,962", "docs/store_time_role_durability.json .stored_rows",
        _at(dur, "stored_rows"))
    add("405", "docs/store_time_role_durability.json .measurement",
        (_at(dur, "measurement", "primed_predictions"),
         _at(dur, "measurement", "recoverable")),
        _at(dur, "measurement", "primed_predictions") == 405
        and _at(dur, "measurement", "recoverable") == 405)
    add("20261101", "docs/store_time_role_durability.json .seed",
        _at(dur, "seed"), _at(dur, "seed") == 20261101)
    add("80", "docs/store_time_role_durability.json .cycles",
        _at(dur, "cycles"), _at(dur, "cycles") == 80,
        "40 + 40 cycles")
    add("NO_ENGINE_CHANGE", "docs/store_time_role_durability.json .measurement.decision",
        _at(dur, "measurement", "decision"),
        _at(dur, "measurement", "decision") == "NO_ENGINE_CHANGE")

    # --- E22. The falsifier artifact carries an attributable exit status -----
    add("1", "docs/decay_falsifier.json .harness_exit_code",
        _at(falsifier, "harness_exit_code"), _at(falsifier, "harness_exit_code") == 1)
    add("fail-closed", "docs/decay_falsifier.json .harness_mode",
        _at(falsifier, "harness_mode"), _at(falsifier, "harness_mode") == "fail-closed")
    add("attributed", "docs/decay_falsifier.json .harness_reference_arm_attributed",
        _at(falsifier, "harness_reference_arm_attributed"),
        _at(falsifier, "harness_reference_arm_attributed") is True)
    num("37", "docs/decay_falsifier.json .theories.cycles_with_any",
        _at(falsifier, "theories", "cycles_with_any"))
    num("38", "docs/decay_falsifier.json .theories.last_nonzero_cycle",
        _at(falsifier, "theories", "last_nonzero_cycle"))

    # --- E23. The store-time role record is a scoped pre-registration --------
    store_prereg = (ROOT / "docs/STORE-TIME-ROLE-RECORD-PREREGISTRATION.md").read_text(
        encoding="utf-8")
    num("0.90", "docs/STORE-TIME-ROLE-RECORD-PREREGISTRATION.md bar_share",
        float(re.search(r"^bar_share: (0\.90)$", store_prereg, re.M).group(1)))
    add("20261101", "docs/STORE-TIME-ROLE-RECORD-PREREGISTRATION.md calibration_seed",
        "20261101" in store_prereg, "calibration_seed: 20261101" in store_prereg)
    add("20272001-20272024",
        "docs/STORE-TIME-ROLE-RECORD-PREREGISTRATION.md confirmatory_block",
        "20272001-20272024" in store_prereg,
        "confirmatory_block: 20272001-20272024" in store_prereg)

    # --- E24. The degree-12 coverage ceiling --------------------------------
    ceil = _load("docs/theory_budget_ceiling.json")
    num("0.5833", "docs/theory_budget_ceiling.json .peak_ceiling_at_shipped_budget",
        _at(ceil, "peak_ceiling_at_shipped_budget"))
    num("0.00", "docs/theory_budget_ceiling.json .final_cycle_coverage_at_shipped_budget",
        _at(ceil, "final_cycle_coverage_at_shipped_budget"))
    num("0.58", "docs/theory_budget_ceiling.json .next_bar", _at(ceil, "next_bar"))
    add("35", "docs/theory_budget_ceiling.json .max_stable_edge_any_cell",
        _at(ceil, "max_stable_edge_any_cell"), _at(ceil, "max_stable_edge_any_cell") == 35)
    add("8/15", "docs/theory_budget_ceiling.json .by_budget.shipped.caps",
        _at(ceil, "by_budget", "shipped", "caps"),
        _at(ceil, "by_budget", "shipped", "caps") == [8, 15])
    add("16/30", "docs/theory_budget_ceiling.json .by_budget.doubled.caps",
        _at(ceil, "by_budget", "doubled", "caps"),
        _at(ceil, "by_budget", "doubled", "caps") == [16, 30])
    add("64/128", "docs/theory_budget_ceiling.json .by_budget.lifted.caps",
        _at(ceil, "by_budget", "lifted", "caps"),
        _at(ceil, "by_budget", "lifted", "caps") == [64, 128])
    add("7", "docs/theory_budget_ceiling.json .by_budget.shipped.theories_max",
        _at(ceil, "by_budget", "shipped", "theories_max"),
        _at(ceil, "by_budget", "shipped", "theories_max") == 7)
    add("12", "docs/theory_budget_ceiling.json .by_budget.doubled.theories_max",
        _at(ceil, "by_budget", "doubled", "theories_max"),
        _at(ceil, "by_budget", "doubled", "theories_max") == 12)
    add("DECAY_DOMINATED", "docs/theory_budget_ceiling.json .verdict",
        _at(ceil, "verdict"), _at(ceil, "verdict") == "DECAY_DOMINATED")
    add("0.40", "no artifact", None, None,
        "the superseded lift-build ceiling; the entry quotes it only to say it was not this "
        "engine's, and no artifact in the tree records it")

    # --- E25. The decay runner trusts the harness exit status ---------------
    raw_falsifier = (ROOT / "docs/decay_falsifier.json").read_text(encoding="utf-8")
    add("harness_reference_arm_failed", "docs/decay_falsifier.json",
        "harness_reference_arm_failed" in raw_falsifier,
        "harness_reference_arm_failed" in raw_falsifier)
    add("harness_reference_arm_warning", "docs/decay_falsifier.json (removed field)",
        "harness_reference_arm_warning" in raw_falsifier,
        "harness_reference_arm_warning" not in raw_falsifier)
    add("Four tests", "tests/test_force_matrix_exit.py", None, None,
        "the entry's four directions are covered by that module's suite; the count of "
        "directions is prose, not a measured figure")

    # --- E26. The licensing role is already recorded ------------------------
    extraction = (ROOT / "organica/sleep_extraction.py").read_text(
        encoding="utf-8").splitlines()
    add("762", "organica/sleep_extraction.py:762-763",
        (extraction[761].strip(), extraction[762].strip()),
        "source_role_id" in extraction[761] and "target_role_id" in extraction[762])
    add("480", "organica/sleep_extraction.py:480", extraction[479].strip(),
        "schema_prior" in extraction[479])
    add("14", "docs/transfer_provenance.json .measurement.transfer_events",
        _at(prov, "measurement", "transfer_events"),
        _at(prov, "measurement", "transfer_events") == 14)
    num("0.90", "docs/STORE-TIME-ROLE-RECORD-PREREGISTRATION.md bar_share",
        float(re.search(r"^bar_share: (0\.90)$", store_prereg, re.M).group(1)))

    # --- E27. The second cross-context run is preregistered -----------------
    ccre2 = (ROOT / "docs/CROSS-CONTEXT-REUSE-2-PREREGISTRATION.md").read_text(
        encoding="utf-8")
    add("60 cells", "docs/CROSS-CONTEXT-REUSE-2-PREREGISTRATION.md Cells",
        "60 cells" in ccre2, "**60 cells**" in ccre2)
    add("24", "docs/CROSS-CONTEXT-REUSE-2-PREREGISTRATION.md seed block",
        "20272001-20272024" in ccre2, "**20272001-20272024** (24 integers)" in ccre2)
    add("12", "docs/CROSS-CONTEXT-REUSE-2-PREREGISTRATION.md reserve",
        "remaining **12** are reserve" in ccre2,
        "remaining **12** are reserve" in ccre2)
    add("1.25", "docs/CROSS-CONTEXT-REUSE-2-PREREGISTRATION.md P1",
        "**at least 1.25**" in ccre2, "**at least 1.25**" in ccre2)
    add("1.00", "docs/CROSS-CONTEXT-REUSE-2-PREREGISTRATION.md P1 bound",
        "**above 1.00**" in ccre2, "**above 1.00**" in ccre2)
    add("0.10", "docs/CROSS-CONTEXT-REUSE-2-PREREGISTRATION.md P2",
        "least **0.10**" in ccre2, "least **0.10**" in ccre2)
    add("0.90", "docs/CROSS-CONTEXT-REUSE-2-PREREGISTRATION.md P4",
        "**at least 0.90**" in ccre2, "**at least 0.90**" in ccre2)

    # --- E28. The transfer-provenance trace exists and can fail -------------
    add("14", "docs/transfer_provenance.json .measurement.transfer_events",
        _at(prov, "measurement", "transfer_events"),
        _at(prov, "measurement", "transfer_events") == 14)
    add("0", "docs/transfer_provenance.json .measurement.resolved",
        _at(prov, "measurement", "resolved"), _at(prov, "measurement", "resolved") == 0)
    statuses = _at(prov, "measurement", "statuses")
    add("unresolved_no_role", "docs/transfer_provenance.json .measurement.statuses",
        statuses["unresolved_no_role"], statuses["unresolved_no_role"] == 14)
    add("all_passed", "docs/transfer_provenance.json .controls.all_passed",
        _at(prov, "controls", "all_passed"), _at(prov, "controls", "all_passed") is True)

    # --- E29. The campaign fails closed on a dead reference arm -------------
    add("row 40", "docs/BOTTLENECK-MAP.md row 40", None, None,
        "the entry names a map row and an exit status, not a measured figure; the exit "
        "behaviour is covered by tests/test_force_matrix_exit.py")

    # --- E30. The next cross-context run is licensed question by question ---
    licensing = _load("docs/ccre_question_licensing.json")
    add("Seven licensed", "docs/ccre_question_licensing.json .licensed",
        len(_at(licensing, "licensed")), len(_at(licensing, "licensed")) == 7)
    add("five refused", "docs/ccre_question_licensing.json .not_licensed",
        len(_at(licensing, "not_licensed")), len(_at(licensing, "not_licensed")) == 5)
    tiers = {}
    for row in _at(licensing, "licensed"):
        tiers[row["tier"]] = tiers.get(row["tier"], 0) + 1
    add("two answered", "docs/ccre_question_licensing.json licensed tiers", tiers,
        tiers == {"answers": 2, "moves": 2, "records": 3})
    add("Q028", "docs/ccre_question_licensing.json .licensed[*].id",
        [row["id"] for row in _at(licensing, "licensed")],
        "Q028" in [row["id"] for row in _at(licensing, "licensed")],
        "the trace-derived diagnostic rule 18 requires")
    add("28", "docs/research_question_registry.json (2026-11-07 tally, superseded)", 28, None,
        "the registry now carries 51 questions; this entry records the pre-registration tally")

    # --- E31. The decay falsifier ran first and blocks the campaign ----------
    num("37", "docs/decay_falsifier.json .theories.cycles_with_any",
        _at(falsifier, "theories", "cycles_with_any"))
    num("38", "docs/decay_falsifier.json .theories.last_nonzero_cycle",
        _at(falsifier, "theories", "last_nonzero_cycle"))
    num("112", "docs/decay_falsifier.json .beliefs.cycles_with_any",
        _at(falsifier, "beliefs", "cycles_with_any"))
    num("113", "docs/decay_falsifier.json .beliefs.last_nonzero_cycle",
        _at(falsifier, "beliefs", "last_nonzero_cycle"))
    add("20261023", "docs/decay_falsifier.json .seed", _at(falsifier, "seed"),
        _at(falsifier, "seed") == 20261023)
    num("3,000", "docs/force_matrix.json .cycles", _at(_load("docs/force_matrix.json"), "cycles"))
    add("1366", "docs/stage_b_protocol.json .seeds (superseded scan)", 1366, None,
        "the consumed-seed scan has since grown to 147 artifacts and 2229 seeds; this entry "
        "records the 1366/122/121 state of 2026-11-07")

    # --- E32. The density interaction: registered, frozen, unrun ------------
    density_prereg = _load("docs/density_interaction_prereg.json")
    num("160", "docs/density_interaction_prereg.json .design.judged_cells",
        _at(density_prereg, "design", "judged_cells"))
    num("0.08", "docs/density_interaction_prereg.json .criteria.interaction_bar",
        _at(density_prereg, "criteria", "interaction_bar"))
    rows_leverage = _at(density_prereg, "leverage_audit", "rows")
    add("0.075", "docs/density_interaction_prereg.json .leverage_audit.rows[0].delta_cap_20",
        rows_leverage[0]["delta_cap_20"], rows_leverage[0]["delta_cap_20"] == 0.075)
    add("0.350", "docs/density_interaction_prereg.json .leverage_audit.rows[-1].delta_cap_20",
        rows_leverage[-1]["delta_cap_20"], rows_leverage[-1]["delta_cap_20"] == 0.35)
    add("24", "docs/density_interaction_prereg.json .leverage_audit.rows[0].world_edges",
        rows_leverage[0]["world_edges"], rows_leverage[0]["world_edges"] == 24)
    add("192", "docs/density_interaction_prereg.json .leverage_audit.rows[-1].world_edges",
        rows_leverage[-1]["world_edges"], rows_leverage[-1]["world_edges"] == 192)

    # --- E33. The mid-ladder dip is the primary scheme's padding ------------
    a2 = _load("docs/density_interaction_a2_result.json")
    profile = _at(a2, "criteria", "profile")
    num("0.0281", "docs/density_interaction_a2_result.json .criteria.profile['0.4'].primary",
        profile["0.4"]["primary"]["delta_precision_mean"])
    num("0.1469", "docs/density_interaction_a2_result.json .criteria.profile['0.4'].sensitivity",
        profile["0.4"]["sensitivity"]["delta_precision_mean"])
    for figure in ("0.88", "3.75", "5.00", "1.75"):
        add(figure, "tests/test_decision_density_exclusion.py (recomputed table)", None, None,
            "the cap-slot shares are recomputed from the A2 run by that test on every run; "
            "they are not fields of the artifact")

    # --- E34. The engine-change audit and the freeze finding ----------------
    change_audit = (ROOT / "docs/ENGINE-CHANGE-AUDIT.md").read_text(encoding="utf-8")
    add("21", "docs/ENGINE-CHANGE-AUDIT.md commits", "21 commits" in change_audit,
        "21 commits" in change_audit)
    add("7becdb5", "docs/ENGINE-CHANGE-AUDIT.md split row", "7becdb5" in change_audit,
        "7becdb5" in change_audit, "the submodule split the entry calls a new module set")
    add("seven", "docs/ENGINE-CHANGE-AUDIT.md skip cases",
        "seven" in change_audit and "skip" in change_audit,
        "seven" in change_audit and "skip" in change_audit)

    # --- E35. The conversation context is a labelled register ---------------
    cost = _load("docs/stage_b_cost_estimate.json")
    num("29", "docs/stage_b_cost_estimate.json .serial_hours", _at(cost, "serial_hours"),
        "29.14 serial hours, quoted as about 29")
    context_doc = (ROOT / "docs/CONTEXT.md").read_text(encoding="utf-8")
    add("repo", "docs/CONTEXT.md provenance markers", "`repo`" in context_doc,
        "`repo`" in context_doc)
    add("owner-reported", "docs/CONTEXT.md provenance markers",
        "`owner-reported`" in context_doc, "`owner-reported`" in context_doc)
    add("unknown", "docs/CONTEXT.md provenance markers", "`unknown`" in context_doc,
        "`unknown`" in context_doc)

    # --- E36. The generated registry and the outreach note ------------------
    earned = _load("docs/cross_context_reuse_benchmark_earned.json")
    num("0.944", "docs/cross_context_reuse_benchmark_earned.json .metrics.transfer_ratio_treatment",
        _at(earned, "metrics", "transfer_ratio_treatment"))
    num("3.4", "docs/cross_context_reuse_benchmark_earned.json .metrics.mean_cycles_naive",
        _at(earned, "metrics", "mean_cycles_naive"))
    papers_readme = (ROOT / "papers/README.md").read_text(encoding="utf-8")
    add("eight", "papers/README.md inventory", "eight manuscript files" in papers_readme,
        "eight manuscript files" in papers_readme)
    add("zero published", "papers/README.md inventory",
        "zero published" in papers_readme, "zero published" in papers_readme)
    add("23", "docs/research_question_registry.json (2026-11-07 tally, superseded)", 23, None,
        "the registry now carries 51 questions; this entry records the 23-question state")

    # --- E37. A third exposure scheme tested the padding attribution --------
    pad = _load("docs/density_padding_result.json")
    for figure, level in (("0.0531", "0.1"), ("0.0719", "0.2"), ("0.0844", "0.4"),
                          ("0.0500", "0.6"), ("0.1500", "0.8")):
        num(figure, f"docs/density_padding_result.json .profile['{level}'].delta_mean",
            _at(pad, "profile", level, "delta_mean"))
    step = next(s["step"] for s in _at(pad, "steps") if s["from"] == 0.4)
    add("0.0344", "docs/density_padding_result.json .steps 0.4->0.6", step,
        step == -0.034375, "the entry prints the step with a typographic minus sign")
    pad_slots = _at(pad, "slots")
    num("2.44", "docs/density_padding_result.json .slots['0.4'].control_intra",
        pad_slots["0.4"]["control_intra"])
    num("1.06", "docs/density_padding_result.json .slots['0.6'].control_intra",
        pad_slots["0.6"]["control_intra"])
    primary_delta = profile["0.4"]["primary"]["delta_precision_mean"]
    sensitivity_delta = profile["0.4"]["sensitivity"]["delta_precision_mean"]
    add("0.1188", "docs/density_interaction_a2_result.json sensitivity - primary at 0.4",
        sensitivity_delta - primary_delta,
        round(sensitivity_delta - primary_delta, 4) == 0.1188,
        "the primary-vs-per-edge gap at 0.4")
    padding_share = pad["profile"]["0.4"]["delta_mean"] - primary_delta
    add("0.0562", "docs/density_interaction_a2_result.json padding - primary at 0.4",
        padding_share, abs(padding_share - 0.0562) <= 0.00005 + 1e-12,
        "the padding phase's share of that gap; a floating-point subtraction, so the "
        "comparison carries half a unit in the last quoted place")

    # --- E38. Intra-cell exclusion adopted as an allocation change ----------
    sparse = _at(a2, "criteria", "C1_sparse_level")
    num("0.059375", "docs/density_interaction_a2_result.json .criteria.C1_sparse_level.mean",
        sparse["mean"])
    num("0.040625", "docs/density_interaction_a2_result.json .criteria.C1_sparse_level.interval[0]",
        sparse["interval"][0])
    num("0.078125", "docs/density_interaction_a2_result.json .criteria.C1_sparse_level.interval[1]",
        sparse["interval"][1])
    num("0.05", "docs/density_interaction_a2_result.json .criteria.C1_sparse_level.bar",
        sparse["bar"])
    add("13 of 16", "docs/density_interaction_a2_result.json .criteria.C1_sparse_level",
        (sparse["seeds_positive"], sparse["of"]),
        sparse["seeds_positive"] == 13 and sparse["of"] == 16)
    num("0.150", "docs/density_interaction_a2_result.json .criteria.profile['0.8'].primary",
        profile["0.8"]["primary"]["delta_precision_mean"])

    # --- E39. The density block A2 ran -------------------------------------
    add("640", "docs/density_interaction_a2_result.json .cells",
        _at(a2, "cells"), _at(a2, "cells") == 640)
    a2_prereg = _load("docs/density_interaction_a2_prereg.json")
    a2_seeds = _at(a2_prereg, "design", "seeds")
    add(f"{a2_seeds[0]}-{a2_seeds[-1]}",
        "docs/density_interaction_a2_prereg.json .design.seeds",
        (a2_seeds[0], a2_seeds[-1]),
        a2_seeds == list(range(a2_seeds[0], a2_seeds[-1] + 1))
        and len(a2_seeds) == 16)
    num("0.059", "docs/density_interaction_a2_result.json .criteria.C1_sparse_level.mean",
        sparse["mean"])
    num("0.041", "docs/density_interaction_a2_result.json .criteria.C1_sparse_level.interval[0]",
        sparse["interval"][0])
    num("0.078", "docs/density_interaction_a2_result.json .criteria.C1_sparse_level.interval[1]",
        sparse["interval"][1])
    descriptive = _at(a2, "criteria", "descriptive_interaction")
    num("0.091", "docs/density_interaction_a2_result.json .criteria.descriptive_interaction.mean",
        descriptive["mean"])
    num("0.072", "docs/density_interaction_a2_result.json .criteria.descriptive_interaction.interval[0]",
        descriptive["interval"][0])
    num("0.109", "docs/density_interaction_a2_result.json .criteria.descriptive_interaction.interval[1]",
        descriptive["interval"][1])

    # --- E40. The density block is held before the run ----------------------
    review = _load("docs/density_interaction_review.json")
    dry_dense = next(row for row in _at(review, "dry_run", "rows")
                     if row["rho_world"] == 0.8 and row["scheme"] == "primary")
    add("1.000", "docs/density_interaction_review.json .dry_run dense control",
        dry_dense["control"], all(v == 1.0 for v in dry_dense["control"]))
    add("0.06", "docs/density_interaction_review.json .dry_run.interaction_primary",
        _at(review, "dry_run", "interaction_primary"),
        _at(review, "dry_run", "interaction_primary") == -0.06)
    per_edge = next(row for row in _at(review, "dry_run", "rows")
                    if row["rho_world"] == 0.8 and row["scheme"] == "sensitivity")
    num("0.200", "docs/density_interaction_review.json .dry_run dense per-edge delta",
        per_edge["delta_mean"])
    pool = _at(review, "dry_run", "pool_at_dense")
    num("240", "docs/density_interaction_review.json .dry_run.pool_at_dense.rows",
        pool.get("rows"))
    num("192", "docs/density_interaction_review.json .dry_run.pool_at_dense.world_rows",
        pool.get("world_rows"))

    # --- E41. Block A2 replaced the held A1 registration --------------------
    num("320", "docs/density_interaction_a2_prereg.json .allocation.judged_cells",
        _at(a2_prereg, "allocation", "judged_cells"))
    num("0.05", "docs/density_interaction_a2_prereg.json .criteria.sparse_bar",
        _at(a2_prereg, "criteria", "sparse_bar"))
    add("7", "docs/density_interaction_a2_prereg.json .decision_table",
        len(_at(a2_prereg, "decision_table")),
        len(_at(a2_prereg, "decision_table")) == 7)
    add("0.150", "docs/density_interaction_a2_prereg.json .criteria.C2",
        "Delta(0.8) = 0.150" in _at(a2_prereg, "criteria", "C2"),
        "the pilot measured Delta(0.8) = 0.150 with zero spread on eight seeds")
    calibration = _at(a2_prereg, "criteria", "bar_provenance")
    add("0.094", "docs/density_interaction_a2_prereg.json .criteria.bar_provenance",
        "0.094" in calibration, "0.094" in calibration)
    add("0.062", "docs/density_interaction_a2_prereg.json .criteria.bar_provenance",
        "0.062" in calibration, "0.062" in calibration)

    # --- E42. Diversity-first admission, measured and withdrawn ------------
    admission = _load("docs/admission_two_arm_prereg.json")
    adoption = _at(admission, "run", "adoption")
    num("-0.077009", "docs/admission_two_arm_prereg.json .run.adoption.mean_paired_gain",
        adoption["mean_paired_gain"])
    num("0.08", "docs/admission_two_arm_prereg.json .run.adoption.bar", adoption["bar"])
    add("0", "docs/admission_two_arm_prereg.json .run.adoption.seeds_positive",
        adoption["seeds_positive"], adoption["seeds_positive"] == 0)
    add("16", "docs/admission_two_arm_prereg.json .design.cells",
        _at(admission, "design", "cells"), _at(admission, "design", "cells") == 16)
    add("120", "docs/admission_two_arm_prereg.json .design.cycles",
        _at(admission, "design", "cycles"), _at(admission, "design", "cycles") == 120)
    add("NO GAIN ON THIS LAYER", "docs/admission_two_arm_prereg.json .run.verdict",
        _at(admission, "run", "verdict"),
        _at(admission, "run", "verdict") == "NO GAIN ON THIS LAYER")
    add("WITHDRAWN", "docs/admission_two_arm_prereg.json .withdrawn.decision",
        _at(admission, "withdrawn", "decision"),
        _at(admission, "withdrawn", "decision") == "WITHDRAWN")


    # --- E43. The release gate records the published master ------------------
    release = (ROOT / "docs/RELEASE-GATE-0.13.0.md").read_text(encoding="utf-8")
    pushed = int(_git("rev-list", "--count", "1f9f713..747d3dd"))
    add("747d3dd", "docs/RELEASE-GATE-0.13.0.md section 3c; git rev-list 1f9f713..747d3dd",
        _git("rev-parse", "747d3dd").strip()[:7],
        "747d3dd" in release and pushed == 3,
        "the tip the push moved to, and the three commits it carried")
    add("1f9f713", "git rev-parse 1f9f713", _git("rev-parse", "1f9f713").strip()[:7],
        _git("rev-parse", "1f9f713").strip().startswith("1f9f713"),
        "the tip the gate record was read at")
    after_pin = int(_git("rev-list", "--count", "6e0ff24..747d3dd"))
    add("67", "git rev-list --count 6e0ff24..747d3dd", after_pin, after_pin == 67)
    engine_touched = int(_git("rev-list", "--count", "6e0ff24..747d3dd", "--", "organica/"))
    add("0", "git rev-list --count 6e0ff24..747d3dd -- organica/",
        engine_touched, engine_touched == 0, "no engine commit since the pin")
    after_release = int(_git("rev-list", "--count", "v0.12.0..747d3dd"))
    add("126", "git rev-list --count v0.12.0..747d3dd", after_release, after_release == 126)
    before_release = int(_git("rev-list", "--count", "v0.12.0..1f9f713"))
    add("123", "git rev-list --count v0.12.0..1f9f713", before_release,
        before_release == 123)

    # --- E44. The reopening tally, the Stage B block and the rerun plan -----
    reg = _load("docs/research_question_registry.json")
    kept = _at(reg, "reopening", "kept_closed")
    reopened = _at(reg, "reopening", "reopened")
    questions = _at(reg, "questions")
    add("53", "docs/research_question_registry.json .questions", len(questions),
        len(questions) == 53)
    add("12", "docs/research_question_registry.json .reopening.reopened",
        len(reopened), len(reopened) == 12)
    add("17", "docs/research_question_registry.json .reopening.kept_closed",
        len(kept), len(kept) == 17)
    never = [q for q in questions
             if q["id"] not in set(reopened) and q["id"] not in {k["id"] for k in kept}]
    add("24", "docs/research_question_registry.json, questions in neither list",
        len(never), len(never) == 24)
    runnable = [q for q in never if q["status"] == "open"]
    add("19", "docs/research_question_registry.json, never-closed rows with status open",
        len(runnable), len(runnable) == 19)
    stage_b = _load("docs/stage_b_protocol.json")
    proved = _find_key(stage_b, "disjoint_proved_against")
    add("**184** artifacts", "docs/stage_b_protocol.json disjoint_proved_against", proved,
        proved == 184 and ("**%d** artifacts" % proved) in entries,
        "the Stage B figure is quoted with its noun, so a drift in either is caught; "
        "the count moved 169 -> 173 when the three conversion blocks wrote their run "
        "artifacts, to 178 when the presence band arm was frozen, to 179 when the T1 run "
        "artifact landed, to 180 when the band run artifact landed, to 182 when the T1b "
        "record and run artifact landed, to 183 when BAND-2's record landed, and to 184 "
        "when PERSISTENCE-MECHANISM-1's frozen record landed, which the changelog records")
    overlap = _find_key(stage_b, "overlap_with_consumed")
    add("0", "docs/stage_b_protocol.json overlap_with_consumed",
        overlap, overlap == [], "the candidate block does not intersect the consumed seeds")
    earlier_stage_b = json.loads(_git("show", "747d3dd^:docs/stage_b_protocol.json"))
    earlier_proved = _find_key(earlier_stage_b, "disjoint_proved_against")
    add("146", "git show 747d3dd^:docs/stage_b_protocol.json disjoint_proved_against",
        earlier_proved, earlier_proved == 146)

    # --- E45. Every entry pinned, every override invoked --------------------
    at_commit = _git("show", "3c9948e:CHANGELOG.md")
    start = at_commit.index(VERSION_HEADING)
    stop = at_commit.index("\n## [", start + len(VERSION_HEADING))
    pinned_entries = re.findall(r"^### ", at_commit[start:stop], re.M)
    add("42", "git show 3c9948e:CHANGELOG.md, 0.13.0 headings", len(pinned_entries),
        len(pinned_entries) == 42)
    add("0", "tests/test_changelog_figures.py UNCOVERED_ENTRIES",
        len(UNCOVERED_ENTRIES), len(UNCOVERED_ENTRIES) == 0)
    add("3c9948e", "git cat-file -t 3c9948e", _git("cat-file", "-t", "3c9948e").strip(),
        _git("cat-file", "-t", "3c9948e").strip() == "commit")

    return rows


def _failures(entries: str) -> list[str]:
    return [f"{row['figure']} ({row['source']}): artifact value {row['actual']!r}"
            for row in _check(entries) if row["ok"] is False]


def test_every_0130_changelog_figure_matches_its_artifact():
    entries = _entries()
    assert len(re.findall(r"^### ", entries, re.M)) >= 14, "the 0.13.0 section shrank"
    rows = _check(entries)
    checked = [row for row in rows if row["ok"] is not None]
    assert len(checked) >= 100, f"only {len(checked)} figures were checked"
    failures = _failures(entries)
    assert not failures, "0.13.0 changelog figures drifted from their artifacts:\n" + "\n".join(failures)


def test_the_figure_check_fires_when_a_quoted_number_drifts():
    entries = _entries()
    assert "59.440" in entries
    # Every occurrence: the figure is quoted three times, and a control that
    # changes only one of them leaves the presence check satisfied.
    mutated = entries.replace("59.440", "59.441")
    failures = _failures(mutated)
    assert failures, "the checker accepted a changed figure"
    assert any("59.440" in failure for failure in failures), failures

    # The control must reach the rows added with the 2026-11-09 entries too,
    # or a new block could be inert and nothing would say so.
    stage_b_drift = entries.replace("**184** artifacts", "**180** artifacts")
    assert "**180** artifacts" in stage_b_drift, "the control's anchor moved"
    stage_b_failures = _failures(stage_b_drift)
    assert stage_b_failures, "the control did not fire"

# The entries whose figures are pinned by _check() above: the 14 the version
# sweep examined, then the 28 earlier entries pinned on 2026-11-09.
COVERED_ENTRIES = [
    'Fixed — The ablation harness runs all eleven conditions on 0.13.0 (2026-11-09)',
    'Changed — The version statements were swept and six stale ones corrected (2026-11-09)',
    'Changed — A re-run that reproduces a recorded result keeps its recorded date (2026-11-09)',
    'Changed — The two superseded stashes were inventoried, disclosed and dropped (2026-11-09)',
    'Measured — The burst deaths were matched against lattice deaths at the same age (2026-11-08)',
    'Added — Q053 was narrowed to one mechanism and preregistered on the lattice evidence (2026-11-08)',
    "Added — Q052's census ran on burst_L1, returned VOID, and was completed by a disclosed amendment (2026-11-08)",
    'Changed — Fourteen closed answers that never named their build were reopened (2026-11-08)',
    "Added — Every run artifact now names the engine's bytes and the writer (2026-11-08)",
    'Added — The sleep-path split is proven behaviour-preserving (2026-11-08)',
    'Changed — The engine guard was unlocked, consolidated and re-baselined on the shipped engine (2026-11-08)',
    'Added — The engine-version audit found that the record could not name its engine (2026-11-08)',
    "Added — Q051's long-delay capability protocol was frozen, run and refused (2026-11-08)",
    "Measured — The decay threshold's edge is a competition boundary, not a support floor (2026-11-08)",
    'Added — The four remaining decay questions are registered and scoped (2026-11-07)',
    'Added — The decay-attribution replication is pre-registered (2026-11-07)',
    'Changed — An uncertified falsifier run is void, not a verdict (2026-11-07)',
    "Changed — The Q028 trace resolves through the schema's role pair (2026-11-07)",
    'Added — Decay attribution on the degree-12 hub (2026-11-07)',
    "Changed — A dead reference arm voids the decay falsifier's verdict (2026-11-07)",
    'Decided — The engine records no licensing role at store time; the record already survives (2026-11-07)',
    "Measured — The decay falsifier's artifact now carries an attributable exit status (2026-11-07)",
    'Scoped — The store-time role record is an engine change with its own pre-registration (2026-11-07)',
    'Measured — The degree-12 coverage ceiling is 0.58 at every theory budget (2026-11-07)',
    'Changed — The decay runner trusts the harness exit status (2026-11-07)',
    'Decided — the licensing role is not recorded, because it is already recorded (2026-11-07)',
    'Added — The second cross-context run is preregistered and blocked (2026-11-07)',
    "Added — Q028's transfer-provenance trace exists and can fail (2026-11-07)",
    'Fixed — The campaign fails closed on a dead reference arm (2026-11-07)',
    'Added — The next cross-context run is licensed question by question (2026-11-07)',
    'Added — The decay falsifier ran first, and it blocks the campaign (2026-11-07)',
    'Added — The density interaction: registered, frozen, unrun (2026-11-07)',
    "Changed — The density ladder's mid-ladder dip is attributed to the primary scheme's padding (2026-11-07)",
    'Added — The engine-change audit, and the freeze finding it produced (2026-11-07)',
    'Added — The context that was held in conversation is now a labelled register (2026-11-07)',
    "Added — The project's questions are a generated registry, and outreach has its own note (2026-11-07)",
    'Added — A third exposure scheme tested the padding attribution and only half confirmed it (2026-11-07)',
    'Changed — Intra-cell exclusion adopted as an allocation change, and not implemented (2026-11-07)',
    'Added — The density block A2 ran and returned its positive branch (2026-11-07)',
    'Changed — The density block is held before the run: its dense end has no headroom (2026-11-07)',
    'Added — The density interaction, block A2: held A1 replaced by a runnable registration (2026-11-07)',
    'Changed — diversity-first admission, adopted, measured and withdrawn (2026-11-07)',
    'Changed — The release gate records that master is published at `747d3dd` (2026-11-09)',
    'Changed — The reopening tally closed around Q052, and the rerun plan landed with its guards (2026-11-09)',
    'Added — Every 0.13.0 entry is pinned to its artifact, and every ablation override is invoked (2026-11-09)',
    "Changed — D3's persistence repair survives six distinct seed-varying worlds (2026-11-10)",
]

UNCOVERED_ENTRIES: list[str] = []


def test_every_0130_entry_is_classified_as_pinned_or_uncovered():
    """A new or renamed entry must be classified before the suite is green."""
    headings = re.findall(r"^### (.+)$", _entries(), re.M)
    classified = COVERED_ENTRIES + UNCOVERED_ENTRIES
    assert len(classified) == len(set(classified)) == len(headings)
    unclassified = sorted(set(headings) - set(classified))
    assert not unclassified, (
        "these 0.13.0 entries are neither pinned nor declared uncovered: "
        + repr(unclassified))
