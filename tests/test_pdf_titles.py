"""The PDF's declared title must be the title the manuscript currently has.

The title lives in two places: the manuscript's level-one heading and
``PDF_INFO`` in ``benchmarks/render_papers.py``.  Neither half looks wrong on
its own, so a retitle can leave the deposited PDF claiming a title the paper no
longer has.  The heading is the source of truth, and the project's "Paper N:"
label is not part of the paper's title -- it must not reach the document
properties.
"""
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import importlib.util
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RENDERER = REPO / "benchmarks" / "render_papers.py"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, RENDERER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mod = _load("_render_papers")


def _heading(rel: str) -> str:
    markdown = (REPO / rel).read_text(encoding="utf-8")
    match = mod.TITLE_RE.search(markdown)
    assert match, "%s has no level-one title" % rel
    return match.group("title")


def test_every_paper_has_a_declared_title():
    for rel in mod.PAPERS:
        stem = Path(rel).stem
        assert stem in mod.PDF_INFO, stem
        assert mod.PDF_INFO[stem]["title"].strip(), stem


def test_declared_title_is_the_manuscript_heading_without_the_project_label():
    for rel in mod.PAPERS:
        stem = Path(rel).stem
        heading = _heading(rel)
        assert re.match(r"Paper\s+\d+\s*:", heading), heading
        declared = mod.PDF_INFO[stem]["title"]
        assert declared == mod.manuscript_title(heading), stem
        assert not re.match(r"Paper\s+\d+", declared), declared


def test_manuscript_titles_are_distinct():
    titles = [mod.PDF_INFO[Path(rel).stem]["title"] for rel in mod.PAPERS]
    assert len(set(titles)) == len(titles), titles


def test_the_check_builds_do_carry_passes_for_both_papers():
    for rel in mod.PAPERS:
        mod.verify_title_matches(Path(rel).stem, _heading(rel))


def test_the_check_fires_on_a_stale_title():
    """A check that has only ever passed has not been tested."""
    stem = Path(mod.PAPERS[0]).stem
    heading = _heading(mod.PAPERS[0])
    original = mod.PDF_INFO[stem]["title"]
    mod.PDF_INFO[stem]["title"] = original + " (superseded)"
    try:
        with pytest.raises(SystemExit) as raised:
            mod.verify_title_matches(stem, heading)
    finally:
        mod.PDF_INFO[stem]["title"] = original
    assert "does not match" in str(raised.value)


def test_each_deposit_record_carries_the_documents_own_title():
    """A DOI must not name a paper by a title the paper does not carry.

    The deposit record's title is what a citation generator prints, so a longer
    descriptive variant there cites a title that appears nowhere in the
    document.  The descriptive subtitle belongs in the description.
    """
    for rel in mod.PAPERS:
        stem = Path(rel).stem
        record = REPO / "zenodo" / ("paper-%s-preprint.json" % stem[:2])
        assert record.exists(), record
        record_title = json.loads(record.read_text(encoding="utf-8"))["title"]
        assert record_title == mod.PDF_INFO[stem]["title"], (record.name, record_title)


def test_the_label_rule_handles_the_headings_in_this_repository():
    assert mod.manuscript_title("Paper 1: A Title") == "A Title"
    assert mod.manuscript_title("Paper 2 - A Title") == "A Title"
    assert mod.manuscript_title("A Title") == "A Title"
