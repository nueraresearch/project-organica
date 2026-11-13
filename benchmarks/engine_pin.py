"""Pin the engine: per-file hashes, and a check that fails when it moves.

The v0.9.0 freeze stopped checking the engine above 0.12.0 -- its seven
engine-file checks skip there (``docs/ENGINE-CHANGE-AUDIT.md``, section 3) -- so
nothing compared the live engine to any recorded state. This pin is that
comparison: every module under ``organica/`` with its newline-normalized
SHA-256, the package version they belong to, and the commit that was checked out
when the pin was taken.

``--check`` fails when a file is added, removed or changed, and it separates the
two cases that matter. An engine that moved while the package still claims the
pinned version is the rule this exists to enforce. An engine that moved with a
version bump the pin has not caught up to is not a violation, but the pin no
longer describes the engine, so it fails too and asks to be re-pinned. Neither
case passes silently.

The hash list is the pin. ``head_at_pin`` and ``pinned`` are provenance -- they
say where and when the list was taken, and the check does not compare them,
because a documentation commit must not invalidate a pin that still describes
the engine.

Nothing is written in ``--check`` mode.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = ROOT / "docs" / "engine_pin.json"
ENGINE = ROOT / "organica"
INIT = ENGINE / "__init__.py"


def engine_files():
    """Every engine module, as repository-relative posix paths, in a fixed order."""
    return sorted(path.relative_to(ROOT).as_posix() for path in ENGINE.rglob("*.py"))


def _digest(path: Path) -> str:
    """Hash text after normalizing CRLF and lone CR to LF.

    A Windows checkout with autocrlf must describe the same engine as an LF
    checkout. Binary files, if one is ever added under organica/, keep their raw
    bytes so the fallback cannot silently rewrite them.
    """
    data = Path(path).read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return hashlib.sha256(data).hexdigest()
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def hashes():
    return {name: _digest(ROOT / name) for name in engine_files()}


def package_version():
    """Read __version__ without importing the package.

    Importing to read one string would run the engine's module-level code in
    whatever interpreter asks the question, which is not a thing a check should
    have to do.
    """
    tree = ast.parse(INIT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, "id", None) == "__version__":
                    return ast.literal_eval(node.value)
    raise RuntimeError("organica/__init__.py does not define __version__")


def head_commit():
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def compute():
    return {
        "version": package_version(),
        "head_at_pin": head_commit(),
        "pinned": date.today().isoformat(),
        "files": hashes(),
    }


def load_pin():
    return json.loads(PIN.read_text(encoding="utf-8"))


def _names(names, limit=8):
    names = list(names)
    if len(names) <= limit:
        return ", ".join(names)
    return ", ".join(names[:limit]) + " and %d more" % (len(names) - limit)


def compare(pin, now=None, version=None):
    """Everything that makes the pin no longer describe the engine."""
    now = hashes() if now is None else now
    version = package_version() if version is None else version
    pinned = pin.get("files", {})

    added = sorted(set(now) - set(pinned))
    removed = sorted(set(pinned) - set(now))
    changed = sorted(name for name in set(pinned) & set(now) if pinned[name] != now[name])

    problems = []
    if changed or added or removed:
        parts = []
        if changed:
            parts.append("changed: " + _names(changed))
        if added:
            parts.append("added: " + _names(added))
        if removed:
            parts.append("removed: " + _names(removed))
        detail = "; ".join(parts)
        if version == pin.get("version"):
            problems.append(
                "the engine moved without a version bump (%s) while the package still says %s; "
                "bump the version, then re-run python -m benchmarks.engine_pin"
                % (detail, version)
            )
        else:
            problems.append(
                "the engine moved from version %s to %s (%s); re-run python -m benchmarks.engine_pin"
                % (pin.get("version"), version, detail)
            )
    elif version != pin.get("version"):
        problems.append(
            "the version changed from %s to %s while no engine file did; re-pin or revert the version"
            % (pin.get("version"), version)
        )
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the pin against the engine on disk, without writing",
    )
    args = parser.parse_args(argv)

    if args.check:
        if not PIN.exists():
            print("FAIL: no engine pin recorded; run python -m benchmarks.engine_pin")
            return 1
        pin = load_pin()
        problems = compare(pin)
        if problems:
            for problem in problems:
                print("FAIL:", problem)
            return 1
        print("engine pin: %d files at version %s" % (len(pin["files"]), pin["version"]))
        return 0

    record = compute()
    if PIN.exists():
        for problem in compare(load_pin(), now=record["files"], version=record["version"]):
            print("NOTE:", problem)
    PIN.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("engine pin: %d files at version %s" % (len(record["files"]), record["version"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
