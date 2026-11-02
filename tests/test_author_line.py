"""The author line of the title page.

The author block is a single hbox, so the name, the ORCID and the address have
to be separated by a real LaTeX break.  Handing pandoc a backslash pair does not
do that: metadata values are parsed as markdown and the pair arrives escaped, so
the title page printed the literal characters (journal §131).  The sentinel is
what makes that testable without rendering a PDF.
"""
from __future__ import annotations

import pytest

from benchmarks import render_papers as rp


def test_prepare_uses_the_sentinel_and_no_backslash_pair():
    body, title, author, plain = rp.prepare(
        "# A Title\n\n**Author:** Ada Lovelace \u2014 https://orcid.org/x \u2014 a@b.c\n\nBody.\n")
    assert rp.AUTHOR_BREAK in author
    assert "\\\\" not in author, "a backslash pair would be escaped by pandoc"
    assert plain == "Ada Lovelace"
    assert title == "A Title"


def test_the_sentinel_becomes_a_real_break(tmp_path):
    tex = tmp_path / "paper.tex"
    tex.write_text("\\author{A " + rp.AUTHOR_BREAK + " B}", encoding="utf-8")
    assert rp.fix_author_breaks(tex) == 1
    out = tex.read_text(encoding="utf-8")
    assert rp.AUTHOR_BREAK not in out
    assert "\\\\" in out


def test_a_surviving_sentinel_is_an_error(tmp_path, monkeypatch):
    tex = tmp_path / "paper.tex"
    tex.write_text("\\author{A " + rp.AUTHOR_BREAK + " B}", encoding="utf-8")
    # A rewrite that cannot remove it must stop the build rather than ship it.
    # Patching the constant would only change what the function looks for, so the
    # write itself is made a no-op instead.
    monkeypatch.setattr(type(tex), "write_text", lambda self, *a, **k: None)
    with pytest.raises(SystemExit):
        rp.fix_author_breaks(tex)
