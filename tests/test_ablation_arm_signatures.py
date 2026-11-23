"""Every ablation arm override must accept the engine's full call signature.

`benchmarks/ablation_study.py` applies its ablations by overriding
`SleepService` / `MemoryService` methods. An override that spells its
parameters out is a contract with the engine, and the engine is free to
add a keyword: `_natural_selection` moved to G1-G8 selection and began
passing `meta_concepts`, which the D arm's narrow signature did not
accept. The failure surfaced at cycle 300, after four conditions had run,
and wrote no results artifact.

This module reads the engine's own call sites out of `organica/*.py` and
checks every arm override two ways.

**Binding** is the cheap check: `inspect.Signature.bind` against the
arguments a call site passes reproduces a signature mismatch exactly,
without needing a live substrate. An override that accepts `**kwargs`
binds anything and passes by design; one that names its parameters must
name the engine's.

**Calling** is the stronger check, and it catches what binding cannot: an
override that accepts the call and then forwards a stale argument set to
`super()` or to another engine method. Each override is invoked with the
*union* of the arguments the engine passes at all of its call sites,
against a probe instance that answers any missing attribute and whose
engine methods are replaced by recorders that still bind against the real
engine signature. A body that needs real data may raise while running;
only an argument-shape `TypeError` counts as a failure, because that is
the defect this guards.

Both checks are proved able to fail: a deliberately narrow override
reproduces the pre-repair D-arm signature, and a canary asserts the full
argument set still carries the `meta_concepts` keyword that broke it.
"""

from __future__ import annotations
LAYER = "synthetic"  # benchmarks/test_layers.py: the module's execution layer

import ast
import contextlib
import inspect
from pathlib import Path

from organica import MemoryService, SleepService

from benchmarks import ablation_study as ablation

ENGINE_ROOT = Path(__file__).resolve().parents[1] / "organica"
ENGINE_CLASSES = (SleepService, MemoryService)
SENTINEL = object()

# The phrases CPython uses when a call and a signature disagree. A body
# that fails for any other reason is running against stand-in data, which
# is expected and is not the defect being guarded.
CALL_SHAPE_ERRORS = (
    "unexpected keyword argument",
    # CPython's own call check says "required positional argument";
    # `Signature.bind` says "missing a required argument". Both are the
    # same defect, and a recorder reports the second.
    "required positional argument",
    "missing a required argument",
    "positional arguments but",
    "positional argument but",
    "multiple values for argument",
    "takes no keyword arguments",
    "too many positional arguments",
)


class _Any:
    """A stand-in value: answers any attribute, call, iteration or arithmetic.

    Ablation bodies read candidate fields, iterate predecessors and index
    into results. They need an object that tolerates all of that without
    a database behind it. Iteration is empty and truthiness is false, so a
    body takes its "nothing available" path rather than a fabricated one.
    """

    def __getattr__(self, _name):
        return self

    def __call__(self, *_args, **_kwargs):
        return self

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

    def __getitem__(self, _key):
        return self

    def __setitem__(self, _key, _value):
        return None

    def __contains__(self, _item):
        return False

    def __bool__(self):
        return False

    def __int__(self):
        return 0

    def __index__(self):
        return 0

    def __float__(self):
        return 0.0

    def __add__(self, _other):
        return self

    __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = __add__

    def __lt__(self, _other):
        return False

    __le__ = __gt__ = __ge__ = __lt__

    def __eq__(self, _other):
        return False

    def __ne__(self, _other):
        return True

    __hash__ = object.__hash__

    def __repr__(self):
        return "<any>"


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


def _engine_classes() -> list[type]:
    """The engine classes and their mixins, in lookup order, minus object."""
    classes: list[type] = []
    for base in ENGINE_CLASSES:
        for klass in base.__mro__:
            if klass is object or klass in classes:
                continue
            classes.append(klass)
    return classes


def _engine_method(name: str):
    for klass in _engine_classes():
        if name in vars(klass):
            return vars(klass)[name]
    raise AssertionError(f"{name} is not defined on the engine")


def _full_argument_set(name: str) -> dict[str, object]:
    """Every parameter the engine supplies at any of its call sites.

    Each call is resolved against the engine's own signature, so an
    argument passed positionally at one site and by keyword at another
    becomes one entry under its declared name. A site that hides its
    arguments behind `*` or `**` would make the set invisible, which is a
    failure of the checker rather than a pass.
    """
    signature = inspect.signature(_engine_method(name))
    supplied: dict[str, object] = {}
    for path, lineno, call in _call_sites(name):
        args, kwargs, unknown = _sample(call)
        if unknown:
            raise AssertionError(
                f"{path}:{lineno} passes * or ** to {name}, so the checker "
                "cannot see the engine's full argument set")
        bound = signature.bind(SENTINEL, *args, **kwargs)
        for key, value in bound.arguments.items():
            if key == "self":
                continue
            if signature.parameters[key].kind is inspect.Parameter.VAR_KEYWORD:
                for extra in value:
                    supplied[extra] = _Any()
            else:
                supplied[key] = _Any()
    return supplied


def _recorder(engine_fn):
    """Stand in for an engine method, still enforcing its signature."""
    signature = inspect.signature(engine_fn)

    def recorded(_self, *args, **kwargs):
        signature.bind(_self, *args, **kwargs)
        return _Any()

    recorded.__name__ = getattr(engine_fn, "__name__", "recorded")
    return recorded


@contextlib.contextmanager
def _engine_methods_recorded():
    """Replace every engine method so a forwarded call is checked, not run."""
    originals: dict[tuple[type, str], object] = {}
    try:
        for klass in _engine_classes():
            for attr, value in vars(klass).items():
                if attr.startswith("__") or not inspect.isfunction(value):
                    continue
                originals[(klass, attr)] = value
                setattr(klass, attr, _recorder(value))
        yield
    finally:
        for (base, attr), value in originals.items():
            setattr(base, attr, value)


def _probe(cls: type, name: str) -> object:
    """An instance of the arm that needs no substrate and answers anything."""
    probe_cls = type(f"Probe_{cls.__name__}_{name}", (cls,),
                     {"__getattr__": lambda _self, _attr: _Any()})
    return object.__new__(probe_cls)


def _is_call_shape_error(exc: TypeError) -> bool:
    text = str(exc)
    return any(marker in text for marker in CALL_SHAPE_ERRORS)


def _invoke(cls: type, name: str, member, params: dict[str, object] | None = None) -> str:
    """Call one override with the engine's full argument set.

    `params` is passed in when the caller has already read the engine's
    signatures; while methods are recorded the live signature belongs to
    the recorder, so the set must be taken before the substitution.

    Returns `"ran"` when the body completed and `"raised"` when it stopped
    on stand-in data. An argument-shape `TypeError` -- at the call or at
    any forward inside the body -- is raised as an assertion failure.
    """
    if params is None:
        params = _full_argument_set(name)
    probe = _probe(cls, name)
    try:
        member(probe, **params)
    except TypeError as exc:
        if _is_call_shape_error(exc):
            raise AssertionError(
                f"{cls.__name__}.{name} cannot accept the engine's argument "
                f"set {sorted(params)}: {exc}") from exc
        return "raised"
    except Exception:
        return "raised"
    return "ran"


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


def test_every_ablation_override_runs_with_the_engines_full_argument_set():
    arms = _arm_classes()
    assert len(arms) >= 10, f"discovered only {len(arms)} arms: {arms}"
    overrides = [(cls, name, member) for cls in arms for name, member in _overrides(cls)]
    assert len(overrides) >= 40, f"discovered only {len(overrides)} overrides"

    # Read every signature before the recorders replace them: while the
    # substitution is live, `inspect.signature` would describe the recorder.
    params = {name: _full_argument_set(name) for _cls, name, _member in overrides}

    errors = []
    with _engine_methods_recorded():
        for cls, name, member in overrides:
            try:
                _invoke(cls, name, member, params[name])
            except AssertionError as exc:
                errors.append(str(exc))
    assert not errors, "ablation overrides reject the engine's argument set:\n" + "\n".join(errors)


def test_the_argument_set_carries_the_keyword_that_broke_the_d_arm():
    """The canary: the set is not merely non-empty, it holds the real defect."""
    params = _full_argument_set("_natural_selection")
    assert "meta_concepts" in params, sorted(params)
    assert "prior" in params and "predictions" in params, sorted(params)


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


def test_the_invocation_check_fires_on_a_narrow_override():
    class NarrowService(ablation.NoFalsificationService):
        def _natural_selection(self, prior, concepts, phrases, loops, predictions):
            return (0, 0, 0)

    params = _full_argument_set("_natural_selection")
    with _engine_methods_recorded():
        try:
            _invoke(NarrowService, "_natural_selection",
                    NarrowService._natural_selection, params)
        except AssertionError as exc:
            assert "meta_concepts" in str(exc), str(exc)
        else:
            raise AssertionError("the invocation check accepted a narrow override")

def test_the_invocation_check_fires_on_a_stale_forward():
    """The case binding cannot see: `*a, **k` accepts, then drops arguments.

    A body that spells `**kwargs` binds any signature the engine grows, so
    `_binding_errors` is silent. It still fails at runtime if it forwards
    only part of what it accepted, which is why the override is called and
    its `super()` call is bound against the real engine signature.
    """
    class StaleForwardService(SleepService):
        # Subclass the engine, not an arm: the arm's own stub would answer
        # the `super()` call and the stale forward would go unmeasured.
        def _build_concepts(self, *a, **k):
            return super()._build_concepts(*a[:1])

    assert _binding_errors(StaleForwardService) == []

    params = _full_argument_set("_build_concepts")
    with _engine_methods_recorded():
        try:
            _invoke(StaleForwardService, "_build_concepts",
                    StaleForwardService._build_concepts, params)
        except AssertionError as exc:
            assert "_build_concepts" in str(exc), str(exc)
        else:
            raise AssertionError("the invocation check accepted a stale forward")
