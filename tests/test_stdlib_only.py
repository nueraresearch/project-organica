"""Enforce AGENTS.md rule 7: the core is standard library only.

Rule 7 has been a claim and not a check.  Nothing stopped a third-party import
from entering ``organica/`` or ``benchmarks/``, and the deposit's software
record is published as *zero external dependencies* — a claim a reader is
entitled to have verified rather than asserted.  This module makes it
mechanical in the two places it can break:

1. **What the code imports.**  Every absolute import in ``organica/`` must
   resolve to the standard library, or to ``organica`` itself.  Every absolute
   import in ``benchmarks/`` must resolve to the standard library, to
   ``organica``, or to a module or package directory that actually exists in
   this repository.  A name that is none of those is a dependency the project
   did not declare.

2. **What the package declares.**  ``pyproject.toml`` must declare an empty
   ``dependencies`` list.  A dependency added there is the same defect arriving
   by a different door, and the two are checked separately because they fail
   independently.

The checker is exercised against sources it **must** reject, so a passing run is
not a formality — the same discipline as the rest of this project's guards,
where a check that cannot fail is decoration.

**What this does not cover.**  It reads absolute imports only, so a relative
import inside ``organica/`` is assumed to stay inside the package, and it does
not resolve ``sys.path`` manipulation or imports built at runtime from strings.
The engine has neither; a future one should arrive with its own check rather
than an exemption here.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
STDLIB = set(sys.stdlib_module_names)

#: The frozen engine modules (AGENTS.md rule 12).  They must be in the scan: a
#: rename or a move would otherwise shrink what this check covers without
#: failing anything, which is how a coverage claim quietly becomes false.
FROZEN = (
    "sleep.py",
    "memory.py",
    "paths.py",
    "streams.py",
    "branch_streams.py",
    "scale_streams.py",
    "ground_truth_worlds.py",
)


def absolute_imports(source: str) -> set[str]:
    """The top-level names the absolute imports in ``source`` refer to."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def reachable_modules(directory: Path) -> set[str]:
    """Module names importable from ``directory`` without leaving the repository."""
    names = {path.stem for path in directory.glob("*.py")}
    names |= {path.name for path in directory.iterdir()
              if path.is_dir() and (path / "__init__.py").exists()}
    return names


def unexpected(source: str, *, allowed: set[str]) -> set[str]:
    """Names imported by ``source`` that are neither the standard library nor ``allowed``."""
    return {name for name in absolute_imports(source)
            if name not in STDLIB and name not in allowed}


def offenders(directory: Path, *, allowed: set[str]) -> dict[str, list[str]]:
    """Every file under ``directory`` that imports a name it is not allowed to."""
    found: dict[str, list[str]] = {}
    for path in sorted(directory.rglob("*.py")):
        extra = unexpected(path.read_text(encoding="utf-8"), allowed=allowed)
        if extra:
            try:
                label = str(path.relative_to(REPO))
            except ValueError:
                label = str(path)
            found[label] = sorted(extra)
    return found


@pytest.mark.parametrize("name", FROZEN)
def test_the_scan_reaches_the_frozen_engine(name):
    assert (REPO / "organica" / name).is_file(), (
        "%s is missing from organica/, so this check would pass over a smaller "
        "package than rule 7 governs" % name)


def test_the_engine_imports_only_the_standard_library():
    found = offenders(REPO / "organica", allowed={"organica"})
    assert found == {}, (
        "third-party import in the engine, which rule 7 forbids: %r. If the "
        "dependency is intended, that is a decision, not a test change." % found)


def test_the_benchmarks_import_only_the_library_and_this_repository():
    # Benchmark scripts deliberately import their siblings and the repo-root
    # helpers (``metrics``), so a resolvable local module is allowed; a name
    # that is neither stdlib nor a file in this tree is not.  ``benchmarks``
    # itself is a namespace package -- it has no ``__init__.py`` -- so scripts
    # import each other as ``from benchmarks.acquisition_runner import ...``
    # and the package name is local even though no module is named it.
    allowed = ({"organica", "benchmarks"}
               | reachable_modules(REPO / "benchmarks")
               | reachable_modules(REPO))
    found = offenders(REPO / "benchmarks", allowed=allowed)
    assert found == {}, (
        "an import in benchmarks/ resolves to no file in this repository: %r. "
        "Either the module is missing or a dependency is being introduced." % found)


def test_pyproject_declares_no_runtime_dependencies():
    import tomllib
    data = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"].get("dependencies") == [], (
        "pyproject declares runtime dependencies; rule 7 allows none")


def test_local_imports_resolve_to_files_in_this_repository():
    root_modules = reachable_modules(REPO)
    assert "metrics" in root_modules
    assert "organica" in root_modules
    assert "numpy" not in root_modules


@pytest.mark.parametrize("source,expected", [
    ("import numpy\n", {"numpy"}),
    ("from requests import get\n", {"requests"}),
    ("import json\nimport pandas as pd\n", {"pandas"}),
    ("def f():\n    import scipy\n", {"scipy"}),
    ("from django.db import models\n", {"django"}),
])
def test_the_checker_rejects_a_third_party_import(source, expected):
    assert unexpected(source, allowed=set()) == expected


@pytest.mark.parametrize("source", [
    "import json\n",
    "from pathlib import Path\n",
    "from __future__ import annotations\n",
    "from typing import Any\n",
    "from . import sibling\n",
    "from .sub import thing\n",
    "import organica\n",
    "from organica import sleep\n",
    "import os, sys\n",
])
def test_the_checker_accepts_the_library_and_local_imports(source):
    assert unexpected(source, allowed={"organica"}) == set()
