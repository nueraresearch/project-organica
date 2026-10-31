"""Every number the two manuscripts state, checked against the artifact it came from.

Why this file exists
--------------------
Two transcription defects reached the manuscripts and were only caught by
reading, not by any test:

* Paper 01's §4.3 quoted three Phase L adjacent-difference intervals that
  ``docs/phase_l_results.json`` does not support. The quoted **means** were
  right and every conclusion survived, but the intervals were stale:
  ``[+0.148, +0.261]`` for ``[+0.150, +0.261]``, ``[+0.443, +0.559]`` for
  ``[+0.441, +0.557]``, and ``[-0.059, -0.020]`` for ``[-0.061, -0.020]``.
* The Gate 13 precision ceiling was quoted as **0.3443** throughout, when the
  maximum of the 36 measurements in ``docs/gate13_allocation_rule.json`` is
  **0.3438**.

Both were numbers typed by hand from an artifact. These tests are the
mechanical half of AGENTS.md rule 27 (a table transcribed from an artifact is
a new claim and needs a mechanical check against that artifact) and rule 29
(a hand-transcribed ceiling becomes a ceiling everywhere it is quoted).

Discipline (mirrors AGENTS.md):

  * The check must be able to FAIL. ``TestTheCheckCanFail`` feeds the
    checkers fabricated numbers and asserts that they are rejected.
  * The checker does not reuse the manuscript's own parser for the expected
    value: every expectation is computed from the artifact, so a change in
    the artifact is a change in the expectation.
  * Standard library only.
  * Nothing here re-scores anything. The artifacts are read, never written.
"""
from __future__ import annotations

import io
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

PAPER_01 = "papers/01_developmental_structure_formation.md"
PAPER_02 = "papers/02_persistent_structural_provenance.md"

#: Documents that state the Gate 13 precision ceiling.
CEILING_CARRIERS = [
    "AGENTS.md",
    "CHANGELOG.md",
    "docs/ACQUISITION-ENDPOINT-AUDIT.md",
    "docs/FACTS-SHEET.md",
    "docs/GATE13-CAUSAL-ACCOUNT.md",
    "docs/GATE13-RELATION-SEPARATION.md",
    "docs/ORGANICA-V2-DESIGN-BRIEF.md",
    "docs/USER-MANUAL.md",
    "docs/V2-CAPACITY-DESIGN-BRIEF.md",
    "docs/FORMATION-UTILIZATION-PREREGISTRATION.md",
    "docs/formation_utilization_results.md",
    "docs/formation_utilization_timing.md",
    PAPER_01,
    "research-journal/phase_g_findings_20261021.md",
]

#: The superseded ceiling. It may appear only where the record says it was
#: corrected -- never as a live claim.
SUPERSEDED_CEILING = "0.3443"
CORRECTION_MARKERS = (
    "corrected",
    "correction",
    "superseded",
    "not 0.3443",
    "was 0.3443",
    "0.3438",
)

#: An adjacent-difference step as the manuscripts quote it: a signed mean
#: followed by a signed 99% interval.
STEP_RE = re.compile(
    r"([+\u2212-]0\.\d{3})\s*\**\s*"
    r"\[([+\u2212-]0\.\d{3})\s*,\s*([+\u2212-]0\.\d{3})\]"
)


def load_doc(rel: str) -> str:
    return io.open(REPO / rel, encoding="utf-8").read()


def load_json(rel: str):
    return json.loads(io.open(REPO / rel, encoding="utf-8").read())


def norm(text: str) -> str:
    """Normalise dash variants so a manuscript's U+2212 compares with -."""
    for dash in ("\u2212", "\u2013", "\u2014"):
        text = text.replace(dash, "-")
    return text


def signed(value: float, places: int = 3) -> str:
    return "%+.*f" % (places, value)


# ---------------------------------------------------------------------------
# Phase L — the curve table and the adjacent-difference intervals
# ---------------------------------------------------------------------------

def phase_l_curve_rows() -> dict[str, str]:
    """The table rows Paper 01 prints, rebuilt from the artifact."""
    curve = load_json("docs/phase_l_results.json")["summaries"]["V1"]["curve"]
    rows: dict[str, str] = {}
    for c in curve:
        latency = ("%.0f" % c["revision_latency_mean_cycles"]
                   if c["revision_latency_mean_cycles"] is not None else "\u2014")
        rows[c["label"]] = norm(
            "| %s | %.3f (%.3f) | %.3f (%.3f) | %s | %s | %d/%d |" % (
                c["label"],
                c["displacement_index_mean"],
                c["displacement_index_stdev"],
                c["preservation_index_mean"],
                c["preservation_index_stdev"],
                signed(c["displacement_score_mean"]),
                latency,
                c["revision_latency_reached_seeds"],
                c["n_seeds"],
            ))
    return rows


def phase_l_step_triples() -> set[tuple[str, str, str]]:
    """Every (mean, lower, upper) the artifact supports, at three decimals."""
    ads = load_json("docs/phase_l_results.json")["summaries"]["V1"][
        "adjacent_differences"]
    triples: set[tuple[str, str, str]] = set()
    for entry in ads:
        for index in ("di", "pi"):
            row = entry[index]
            lo, hi = row["interval"]
            triples.add((signed(row["mean_difference"]),
                         signed(lo), signed(hi)))
    return triples


def check_steps(text: str, allowed: set) -> list[str]:
    """Return the quoted steps that the artifact does not support."""
    problems = []
    for match in STEP_RE.finditer(norm(text)):
        triple = (match.group(1), match.group(2), match.group(3))
        if triple not in allowed:
            problems.append(
                "quotes the step %s [%s, %s], which the artifact does not "
                "support" % triple)
    return problems


# ---------------------------------------------------------------------------
# The Gate 13 numbers
# ---------------------------------------------------------------------------

def gate13_ceiling() -> float:
    """The maximum precision in the Gate 13 allocation-rule artifact."""
    alloc = load_json("docs/gate13_allocation_rule.json")
    best = 0.0
    for seed in alloc:
        for rule in ("global_top_k", "per_source_top_k"):
            for row in seed[rule].values():
                best = max(best, float(row["precision"]))
    return best


def gate13_capacity_ranges() -> dict:
    """Coverage and asserted-edge ranges by cap, from the capacity sweep."""
    sweep = load_json("docs/gate13_capacity_sweep.json")
    by_cap: dict[str, list] = {}
    for caps in sweep.values():
        for cap, row in caps.items():
            by_cap.setdefault(cap, []).append(row)
    out = {}
    for cap, rows in by_cap.items():
        cover = [r["asserted_coverage"] for r in rows]
        edges = [r["total_asserted_edges"] for r in rows]
        out[cap] = {
            "coverage": (min(cover), max(cover)),
            "asserted_edges": (min(edges), max(edges)),
        }
    return out


def gate13_ranking_best_cell() -> tuple[float, float]:
    """The best (coverage, precision) cell in the ranking criterion grid."""
    crit = load_json("docs/gate13_ranking_criterion.json")
    best = None
    for seed in crit:
        for rule in seed["tables"].values():
            for cell in rule.values():
                # each cell holds one scope dict per reading (count, ratio)
                for scope in cell.values():
                    if not isinstance(scope, dict) or "coverage" not in scope:
                        continue
                    key = (float(scope["coverage"]), float(scope["precision"]))
                    if best is None or key[0] > best[0]:
                        best = key
    return best


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPhaseLCurveTable:
    """Paper 01's curve table, row by row, from the artifact."""

    def test_every_artifact_row_appears_in_the_manuscript(self):
        text = norm(load_doc(PAPER_01))
        missing = []
        for label, row in phase_l_curve_rows().items():
            if row not in text:
                missing.append("%s: expected %r" % (label, row))
        assert not missing, (
            "Paper 01's curve table does not match "
            "docs/phase_l_results.json:\n" + "\n".join(missing))

    def test_the_manuscript_has_no_extra_curve_rows(self):
        """A row the artifact does not have is as wrong as a wrong row."""
        text = norm(load_doc(PAPER_01))
        expected = set(phase_l_curve_rows().values())
        labels = set(phase_l_curve_rows())
        pattern = re.compile(
            r"^\| (\d:\d) \| (\d\.\d{3}) \((\d\.\d{3})\) \| "
            r"(\d\.\d{3}) \((\d\.\d{3})\) \| ([+\u2212-]0\.\d{3}) \| "
            r"([\u2014\d]+) \| (\d+/\d+) \|$")
        extra = []
        for line in text.splitlines():
            match = pattern.match(line.strip())
            if match and match.group(1) not in labels:
                extra.append(line.strip())
            elif match and match.group(0) not in expected:
                extra.append(line.strip())
        assert not extra, (
            "Paper 01's curve table states rows the artifact does not "
            "support:\n" + "\n".join(extra))


class TestPhaseLAdjacentDifferences:
    """Every step interval the manuscripts quote, resolved to the artifact."""

    @pytest.mark.parametrize("rel", [PAPER_01, PAPER_02])
    def test_no_unsupported_step_is_quoted(self, rel):
        allowed = phase_l_step_triples()
        problems = check_steps(load_doc(rel), allowed)
        assert not problems, (
            "%s quotes a Phase L step the artifact does not support:\n%s"
            % (rel, "\n".join(problems)))

    def test_the_corrected_intervals_are_the_supported_ones(self):
        """The three intervals corrected on 2026-10-31 must now be allowed."""
        allowed = phase_l_step_triples()
        for triple in (("+0.204", "+0.150", "+0.261"),
                       ("+0.502", "+0.441", "+0.557"),
                       ("-0.039", "-0.061", "-0.020")):
            assert triple in allowed, (
                "%s should be an artifact-supported step" % (triple,))

    def test_the_stale_intervals_are_not_supported(self):
        """And the ones that were wrong must not be."""
        allowed = phase_l_step_triples()
        for triple in (("+0.204", "+0.148", "+0.261"),
                       ("+0.502", "+0.443", "+0.559"),
                       ("-0.039", "-0.059", "-0.020")):
            assert triple not in allowed, (
                "%s is the stale interval and must not be supported" % (triple,))


class TestGate13Ceiling:
    """The precision ceiling, everywhere it is quoted."""

    def test_the_artifact_maximum_is_the_ceiling(self):
        assert gate13_ceiling() == pytest.approx(0.3438, abs=1e-9), (
            "the Gate 13 allocation-rule artifact's maximum precision is not "
            "0.3438; every document that quotes the ceiling must be revisited")

    @pytest.mark.parametrize("rel", CEILING_CARRIERS)
    def test_no_carrier_quotes_the_superseded_ceiling_as_live(self, rel):
        text = load_doc(rel)
        problems = []
        for para in re.split(r"\n\s*\n", norm(text)):
            if SUPERSEDED_CEILING not in para:
                continue
            if not any(marker in para for marker in CORRECTION_MARKERS):
                problems.append(para.strip()[:160])
        assert not problems, (
            "%s quotes the superseded ceiling %s without marking it as "
            "corrected:\n%s" % (rel, SUPERSEDED_CEILING, "\n".join(problems)))

    @pytest.mark.parametrize("rel", CEILING_CARRIERS)
    def test_the_carrier_states_the_measured_ceiling(self, rel):
        assert "0.3438" in load_doc(rel), (
            "%s must state the ceiling the artifact measures" % rel)


class TestGate13CapacitySweep:
    """The capacity-sweep ranges the manuscripts quote."""

    def test_the_quoted_ranges_are_the_artifacts(self):
        ranges = gate13_capacity_ranges()
        text = norm(load_doc(PAPER_01))
        cap20 = ranges["20"]
        uncapped = ranges["None"]
        assert "%.4f" % cap20["coverage"][0] in text
        assert "%.4f" % cap20["coverage"][1] in text
        assert "%.4f" % uncapped["coverage"][0] in text
        assert "%.4f" % uncapped["coverage"][1] in text
        assert "%d" % uncapped["asserted_edges"][0] in text
        assert "%d" % uncapped["asserted_edges"][1] in text

    def test_the_best_ranking_cell_is_the_artifacts(self):
        coverage, precision = gate13_ranking_best_cell()
        assert (round(coverage, 4), round(precision, 4)) == (0.0804, 0.4500)
        text = norm(load_doc(PAPER_01))
        assert "0.0804" in text
        assert "0.4500" in text


class TestAcquisitionCompositionalGate:
    """The benchmark's headroom, as Paper 01 states it."""

    def test_the_quoted_scalars_are_the_artifacts(self):
        gate = load_json("docs/acquisition_compositional_gate.json")
        text = norm(load_doc(PAPER_01))
        expected = [
            "%+.4f" % gate["mean_gap"],
            "%+.4f" % gate["gap_lower_99"],
            "%+.4f" % gate["gap_upper_99"],
            "%+.4f" % gate["gap_on_held_cell"]["mean"],
            "%+.4f" % gate["gap_on_other_cells"]["mean"],
        ]
        missing = [e for e in expected if e not in text]
        assert not missing, (
            "Paper 01 does not state the artifact's compositional-gate "
            "scalars: %s" % missing)

    def test_the_held_cell_ratio_is_the_artifacts(self):
        gate = load_json("docs/acquisition_compositional_gate.json")
        ratio = (gate["gap_on_held_cell"]["mean"]
                 / gate["gap_on_other_cells"]["mean"])
        assert ("%.1f" % ratio) in norm(load_doc(PAPER_01))


class TestCrossDomainTransfer:
    """The one measured cross-domain transfer result."""

    def test_the_quotation_is_the_artifacts(self):
        ablation = load_json("docs/ablation_study.json")
        block = ablation["cross_domain_transfer"]
        text = norm(load_doc(PAPER_01))
        assert ("%.4f" % block["mean_cdt"]) in text
        assert ("%.2f" % block["mean_shared_tags"]) in text
        assert ("%d domain pairs" % len(block["pairs"])) in text


class TestPhaseKFamilies:
    """The three Phase K families' paired differences and verdicts."""

    @pytest.mark.parametrize("family", ["K1", "K2", "K3"])
    def test_the_family_result_is_the_artifacts(self, family):
        summary = load_json("docs/phase_k_results.json")["summaries"][family]
        paired = summary["paired_organica_minus_best_baseline"]
        assert summary["verdict"] == "REVERSED"
        assert paired["n"] == summary["n_seeds"]
        assert paired["interval"][0] <= paired["mean"] <= paired["interval"][1]
        assert paired["mean"] < 0, (
            "positive favours Organica; a negative paired difference is the "
            "reversed outcome")

    def test_every_family_fails_the_same_way(self):
        summaries = load_json("docs/phase_k_results.json")["summaries"]
        verdicts = {f: summaries[f]["verdict"] for f in ("K1", "K2", "K3")}
        assert set(verdicts.values()) == {"REVERSED"}


class TestTheCheckCanFail:
    """A check that cannot disagree with its subject is not a check."""

    def test_the_step_checker_rejects_a_stale_interval(self):
        allowed = phase_l_step_triples()
        assert check_steps("+0.204 [+0.150, +0.261]", allowed) == []
        problems = check_steps("+0.204 [+0.148, +0.261]", allowed)
        assert problems, "the step checker did not notice a stale interval"

    def test_the_step_checker_rejects_a_doctored_mean(self):
        allowed = phase_l_step_triples()
        problems = check_steps("+0.502 [+0.441, +0.559]", allowed)
        assert problems, "the step checker did not notice a doctored mean"

    def test_the_ceiling_checker_rejects_an_uncorrected_quote(self):
        text = ("The precision never exceeds 0.3443 at any budget under "
                "either allocation rule.")
        problems = []
        for para in re.split(r"\n\s*\n", norm(text)):
            if SUPERSEDED_CEILING not in para:
                continue
            if not any(marker in para for marker in CORRECTION_MARKERS):
                problems.append(para)
        assert problems, "the ceiling checker did not notice a live 0.3443"

    def test_the_ceiling_checker_accepts_a_corrected_quote(self):
        text = ("The ceiling was 0.3443; it is 0.3438, corrected from the "
                "artifact.")
        problems = []
        for para in re.split(r"\n\s*\n", norm(text)):
            if SUPERSEDED_CEILING not in para:
                continue
            if not any(marker in para for marker in CORRECTION_MARKERS):
                problems.append(para)
        assert not problems, "the ceiling checker rejected a marked correction"

    def test_the_curve_table_checker_rejects_a_doctored_row(self):
        rows = phase_l_curve_rows()
        expected = rows["3:1"]
        doctored = expected.replace("0.706", "0.707")
        assert doctored != expected
        assert doctored not in rows.values()


class TestTheArtifactsAreReadable:
    """The check needs its artifacts to exist and to hold what it claims."""

    @pytest.mark.parametrize("name", [
        "phase_l_results.json",
        "phase_k_results.json",
        "acquisition_compositional_gate.json",
        "gate13_allocation_rule.json",
        "gate13_capacity_sweep.json",
        "gate13_ranking_criterion.json",
        "ablation_study.json",
    ])
    def test_the_artifact_exists_and_parses(self, name):
        path = REPO / "docs" / name
        assert path.exists(), "%s is missing" % name
        assert load_json("docs/" + name), "%s is empty" % name
