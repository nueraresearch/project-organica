"""Every ablation arm override must accept the engine's full call signature.

`benchmarks/ablation_study.py` applies its ablations by overriding
`SleepService` / `MemoryService` methods. An override that spells its
parameters out is a contract with the engine, and the engine is free to
add a keyword: `_natural_selection` moved to G1-G8 selection and began
passing `meta_concepts`, which the D arm's narrow signature did not
accept. The failure surfaced at cycle 300, after four conditions had run,
and wrote no results artifact.

This module reads the engine's own call sites out of `organica/*.py` and
binds every arm override against the arguments those calls pass. Binding,
not invoking, is the check: the overrides need a live substrate and a
real `SleepReport`, while the defect being guarded is a signature
mismatch, which `inspect.Signature.bind` reproduces exactly. An override
that accepts `**kwargs` binds anything and passes by design; one that
names its parameters must name the engine's.

A deliberately narrow override is bound too, and the test asserts the
check reports it -- a check that cannot fire is not a check.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

from organica import MemoryService, SleepService

from benchmarks import ablation_study as ablation

ENGINE_ROOT = Path(__file__).resolve().parents[1] / "organica"
ENGINE_CLASSES = (SleepService, MemoryService)
SENTINEL = object()


def _arm_classes() -> list[type]:
    """The ablation arms defined by the harness, not the engine classes."""
    arms = []
    for _name, obj in inspect.getmembers(ablation, inspect.isclass):
        if obj in ENGINE_CLASSES or obj.__module__ != ablation.__name__:
            continue
        if issubclass(obj, ENGINE_CLASSES):
            arms.append(obj)
    return sorted(arms, key=lambda cls: cls.__name__)


def _overrides(cls: type) -> list[tuple[str, object]]:
    """Methods this arm overrides on the engine, ignoring its own helpers."""
    out = []
    for name, member in vars(cls).items():
        if name.startswith("__") or not inspect.isfunction(member):
            continue
        if any(hasattr(base, name) for base in ENGINE_CLASSES):
            out.append((name, member))
    return sorted(out, key=lambda item: item[0])


def _call_sites(name: str) -> list[tuple[str, int, ast.Call]]:
    """Every `self.<name>(...)` call in the engine, with its source location."""
    sites = []
    for path in sorted(ENGINE_ROOT.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not isinstance(func, ast.Attribute) or func.attr != name:
                continue
            if not isinstance(func.value, ast.Name) or func.value.id != "self":
                continue
            sites.append((path.relative_to(ENGINE_ROOT.parent).as_posix(),
                          node.lineno, node))
    return sites


def _sample(call: ast.Call) -> tuple[list[object], dict[str, object], bool]:
    """One sentinel per argument the engine passes; `unknown` marks * / **."""
    args = []
    unknown = False
    for arg in call.args:
        if isinstance(arg, ast.Starred):
            unknown = True
        else:
            args.append(SENTINEL)
    kwargs = {}
    for keyword in call.keywords:
        if keyword.arg is None:
            unknown = True
        else:
            kwargs[keyword.arg] = SENTINEL
    return args, kwargs, unknown


def _binding_errors(cls: type) -> list[str]:
    errors = []
    for name, member in _overrides(cls):
        sites = _call_sites(name)
        if not sites:
            errors.append(f"{cls.__name__}.{name}: the engine never calls this method, "
                          "so the test cannot check it")
            continue
        for path, lineno, call in sites:
            args, kwargs, unknown = _sample(call)
            location = f"{path}:{lineno}"
            if unknown:
                errors.append(f"{cls.__name__}.{name}: {location} passes * or **, so the "
                              "checker cannot see the engine's full argument set")
                continue
            try:
                inspect.signature(member).bind(SENTINEL, *args, **kwargs)
            except TypeError as exc:
                errors.append(f"{cls.__name__}.{name} cannot accept {location}: {exc}")
    return errors


def test_every_ablation_override_accepts_the_engines_call_signature():
    arms = _arm_classes()
    assert len(arms) >= 10, f"discovered only {len(arms)} arms: {arms}"
    errors = [error for cls in arms for error in _binding_errors(cls)]
    assert not errors, "ablation overrides no longer match the engine:\n" + "\n".join(errors)


def test_the_signature_check_fires_on_a_narrow_override():
    class NarrowService(ablation.NoFalsificationService):
        # The D arm's signature before the 2026-11-08 repair: it does not
        # accept the G2-G8 keywords the engine now passes.
        def _natural_selection(self, prior, concepts, phrases, loops, predictions):
            return (0, 0, 0)

    errors = _binding_errors(NarrowService)
    assert len(errors) == 1, errors
    assert "_natural_selection" in errors[0]
    assert "meta_concepts" in errors[0], errors[0]
