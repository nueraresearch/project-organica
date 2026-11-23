"""Every test module declares one execution layer, and the authorised count stays zero.

The layers are about what a module *does*, not what it is about:

- ``static``              reads committed artifacts, records and documents; runs no engine and no harness.
- ``dry-run``             invokes a harness's non-cell paths (validators, refusals, ``--dry-run``).
- ``synthetic``           executes the engine on a synthetic world, which is what the canaries and the
                          presence cells do at 120 cycles.
- ``authorized``          would execute a cell under an owner grant. **No test module may be tagged
                          ``authorized``**: the owner's grants authorise campaigns, not the suite, and a
                          suite that runs granted cells turns a deliberate run into a side effect.

The tags live in the modules themselves (``LAYER = "static"``) so they travel with a rename. The tag
is the declaration; the source checks below are deliberately narrow guards against the dangerous
mistakes -- an engine call hidden under a static tag, or a cell entry point with no refusal test.
They do not try to infer or replace the declaration.

    python -m benchmarks.test_layers --check     # exit 1 on any problem, report the split
    python -m benchmarks.test_layers --report    # the split only
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"

LAYERS = ("static", "dry-run", "synthetic", "authorized")
AUTHORIZED = "authorized"

# Functions whose call (or subclassing) means the module itself executes the engine. Read from the
# AST: a test that merely *mentions* ``SleepService(memory)`` in a string is not executing it.
ENGINE_CALLS = frozenset({
    "SleepService", "MemoryService", "run_sleep_cycle", "run_cell",
    "_make_scratch_db", "generate_compositional_world",
})
# Calls and flags that would execute or finish a real block.
CELL_CALLS = frozenset({"measure", "finish", "run_cell"})
CELL_FLAGS = ("--measure", "--finish")
# Phrases that show a cell-token occurrence is a refusal test, not a run.
REFUSAL_MARKERS = ("REFUSED", "refused", "not authorised", "unauthorised", "not granted",
                   "SystemExit", "pytest.raises")


def modules() -> list[Path]:
    return sorted(TESTS.glob("test_*.py"))


def _tree(source: str) -> ast.Module | None:
    try:
        return ast.parse(source)
    except SyntaxError:
        return None


def declared(path: Path) -> list[str]:
    """Every module-level string assigned to LAYER, in source order."""
    source = path.read_text(encoding="utf-8")
    tree = _tree(source)
    if tree is None:
        return []
    found: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "LAYER":
                    value = node.value
                    if isinstance(value, ast.Constant) and isinstance(value.value, str):
                        found.append(value.value)
                    else:
                        found.append("<not a literal>")
    return found


def _names(tree: ast.Module) -> set[str]:
    """Every called function name and every subclassed base, by attribute as well as by name."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                found.add(func.id)
            elif isinstance(func, ast.Attribute):
                found.add(func.attr)
        elif isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name):
                    found.add(base.id)
                elif isinstance(base, ast.Attribute):
                    found.add(base.attr)
    return found


def evidence(path: Path) -> dict:
    source = path.read_text(encoding="utf-8")
    tree = _tree(source) or ast.Module(body=[], type_ignores=[])
    names = _names(tree)
    flags = sorted({node.value for node in ast.walk(tree)
                    if isinstance(node, ast.Constant) and node.value in CELL_FLAGS})
    return {
        "engine": sorted(names & ENGINE_CALLS),
        "cell": sorted((names & CELL_CALLS) | set(flags)),
        "refusal": [marker for marker in REFUSAL_MARKERS if marker in source],
    }


def problems() -> list[str]:
    found: list[str] = []
    for path in modules():
        tags = declared(path)
        name = path.relative_to(ROOT).as_posix()
        if not tags:
            found.append("%s: no LAYER declared" % name)
            continue
        if len(tags) > 1:
            found.append("%s: %d LAYER declarations (%r)" % (name, len(tags), tags))
            continue
        tag = tags[0]
        if tag not in LAYERS:
            found.append("%s: unknown layer %r (one of %s)" % (name, tag, ", ".join(LAYERS)))
            continue
        if tag == AUTHORIZED:
            found.append("%s: tagged authorized; no test module may run a granted cell" % name)
        seen = evidence(path)
        if tag in ("static", "dry-run") and seen["engine"]:
            found.append("%s: tagged %s but executes the engine (%s)"
                         % (name, tag, ", ".join(seen["engine"])))
        if tag != AUTHORIZED and seen["cell"] and not seen["refusal"]:
            found.append("%s: tagged %s but names a cell-running entry point with no refusal marker"
                         % (name, tag))
    return found


def split() -> dict[str, int]:
    counts = {layer: 0 for layer in LAYERS}
    for path in modules():
        tags = declared(path)
        tag = tags[0] if len(tags) == 1 else "<untagged>"
        counts[tag] = counts.get(tag, 0) + 1
    counts["modules"] = len(modules())
    return counts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate and report the split")
    parser.add_argument("--report", action="store_true", help="report the split only")
    args = parser.parse_args(argv)
    counts = split()
    print("test layers: " + "  ".join("%s=%d" % (layer, counts[layer]) for layer in LAYERS)
          + "  of %d modules" % counts["modules"])
    if args.report:
        return 0
    found = problems()
    for problem in found:
        print("FAIL:", problem)
    if counts[AUTHORIZED] != 0:
        print("FAIL: the authorized count is %d, and it must be zero" % counts[AUTHORIZED])
        found = found + ["authorized count is not zero"]
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
