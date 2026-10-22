"""
benchmarks/clone_check.py
------------------------------------------------------------------
Can a stranger actually run this?

The unit tests prove the code works on *this* machine, where the package
may be importable for reasons a fresh clone would not have. This script
answers the question that actually matters for a public repository:

    clone it somewhere clean, and see whether it works there.

It clones the repository into a temporary directory, then runs the
stranger-facing entry points from inside that clone:

    1. `import organica` works with no install
    2. `python -m pytest tests -q` passes
    3. `python build.py` grows an organism from nothing
    4. every example script exits 0
    5. the core has no third-party runtime dependencies
    6. `python benchmarks/study_health.py` runs

Nothing here touches the live study: the clone gets its own scratch
directory, and the live `memory.db` is not on the path.

Usage:
    python benchmarks/clone_check.py
    python benchmarks/clone_check.py --keep          # leave the clone behind
    python benchmarks/clone_check.py --remote https://github.com/nueraresearch/project-organica.git
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REMOTE = "https://github.com/nueraresearch/project-organica.git"


def run(cmd: list[str], cwd: Path, timeout: int = 900) -> tuple[int, str]:
    proc = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
        shell=False,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def live_row_count(db: Path) -> int:
    """Number of rows in the live substrate, or -1 if it cannot be read."""
    if not db.exists():
        return -1
    try:
        import sqlite3
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        try:
            return int(conn.execute("SELECT COUNT(*) FROM events").fetchone()[0])
        finally:
            conn.close()
    except Exception:
        return -1


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify a fresh clone works end to end.")
    ap.add_argument("--remote", default=DEFAULT_REMOTE)
    ap.add_argument("--branch", default="master")
    ap.add_argument("--keep", action="store_true", help="leave the clone on disk")
    ap.add_argument("--out", default="docs/clone_check.json")
    args = ap.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="organica_clone_"))
    clone = workdir / "project-organica"
    results: list[dict] = []

    # Captured before anything runs, so the live substrate can be compared
    # against its own earlier state rather than against a snapshot.
    live_db = REPO_ROOT / "memory.db"
    live_before = live_row_count(live_db)

    print("=" * 92)
    print("FRESH CLONE CHECK -- can a stranger run this?")
    print("=" * 92)
    print(f"  remote : {args.remote} ({args.branch})")
    print(f"  clone  : {clone}")
    print()

    # ---- 1. clone ----------------------------------------------------
    t0 = time.time()
    code, out = run(["git", "clone", "--depth", "1", "--branch", args.branch,
                     args.remote, str(clone)], cwd=workdir, timeout=600)
    ok = code == 0 and clone.exists()
    results.append({"step": "clone", "ok": ok, "seconds": round(time.time() - t0, 1),
                    "detail": out.strip()[-400:] if not ok else ""})
    print(f"  [{'ok' if ok else 'FAIL'}] clone")
    if not ok:
        print(out[-1500:])
        return 1

    # ---- 2. import without install ------------------------------------
    code, out = run([sys.executable, "-c",
                     "import organica; print('organica import OK', organica.__file__)"],
                    cwd=clone)
    ok = code == 0
    results.append({"step": "import_organica", "ok": ok,
                    "detail": out.strip()[-300:]})
    print(f"  [{'ok' if ok else 'FAIL'}] import organica (no install)")

    # ---- 3. core has no third-party runtime dependencies -------------
    req = clone / "requirements.txt"
    core_deps = []
    if req.exists():
        for line in req.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                core_deps.append(line)
    results.append({"step": "core_dependencies", "ok": not core_deps,
                    "detail": f"requirements.txt lists: {core_deps or 'nothing'}"})
    print(f"  [{'ok' if not core_deps else 'FAIL'}] core dependencies (stdlib only)")

    # ---- 4. test suite ------------------------------------------------
    t0 = time.time()
    code, out = run([sys.executable, "-m", "pytest", "tests", "-q"], cwd=clone, timeout=900)
    ok = code == 0
    tail = [ln for ln in out.strip().splitlines() if ln.strip()][-1:] if out.strip() else []
    results.append({"step": "pytest", "ok": ok, "seconds": round(time.time() - t0, 1),
                    "detail": tail[0] if tail else out.strip()[-300:]})
    print(f"  [{'ok' if ok else 'FAIL'}] pytest  ({tail[0] if tail else 'see log'})")

    # ---- 5. build an organism from nothing -----------------------------
    t0 = time.time()
    code, out = run([sys.executable, "build.py"], cwd=clone, timeout=900)
    ok = code == 0
    interesting = [ln for ln in out.splitlines()
                   if any(k in ln for k in ("G5", "lineage", "Lineage", "uncertaint",
                                            "priority", "events"))]
    results.append({"step": "build_py", "ok": ok, "seconds": round(time.time() - t0, 1),
                    "detail": " | ".join(interesting[-6:]) if interesting else out.strip()[-300:]})
    print(f"  [{'ok' if ok else 'FAIL'}] build.py")

    # ---- 6. every example runs ----------------------------------------
    examples = sorted((clone / "examples").glob("*.py"))
    domain_examples = sorted((clone / "examples" / "domains").glob("*.py"))
    example_results = []
    for ex in examples + domain_examples:
        # Run from the clone root with the path relative to it: the
        # examples locate the repository by walking up to pyproject.toml,
        # so they work from either directory, but running from the root
        # is what a stranger is most likely to do.
        code, out = run([sys.executable, str(ex.relative_to(clone))],
                        cwd=clone, timeout=600)
        example_results.append({"script": str(ex.relative_to(clone)),
                                "ok": code == 0,
                                "detail": "" if code == 0 else out.strip()[-300:]})
    ok = all(r["ok"] for r in example_results)
    results.append({"step": "examples", "ok": ok,
                    "detail": f"{sum(r['ok'] for r in example_results)}/"
                              f"{len(example_results)} examples exited 0"})
    print(f"  [{'ok' if ok else 'FAIL'}] examples "
          f"({sum(r['ok'] for r in example_results)}/{len(example_results)} exited 0)")

    # ---- 7. health tool runs -------------------------------------------
    # A fresh clone has no organica.log, so "NO CYCLES PARSED" is the
    # correct answer, not a failure. What matters is that the tool runs
    # and reports rather than crashing.
    code, out = run([sys.executable, "benchmarks/study_health.py"], cwd=clone, timeout=300)
    ran = ("Traceback" not in out) and (
        "ORGANICA STUDY" in out or "NO CYCLES PARSED" in out)
    results.append({"step": "study_health", "ok": ran,
                    "detail": out.strip()[-200:]})
    print(f"  [{'ok' if ran else 'FAIL'}] study_health.py"
          f"{'  (no log yet in a fresh clone -- expected)' if 'NO CYCLES' in out else ''}")

    # ---- 8. the live study was not damaged -----------------------------
    # The clone cannot reach the live substrate by construction: paths.py
    # derives REPO_ROOT from __file__, so a clone's scratch directory is
    # inside the clone. What we verify is the catastrophic case -- the
    # live substrate shrinking, which is what the old examples did.
    live_db = REPO_ROOT / "memory.db"
    live_after = live_row_count(live_db)
    untouched = (live_before < 0 or live_after < 0 or live_after >= live_before)
    results.append({"step": "live_study_untouched", "ok": untouched,
                    "detail": f"live substrate rows {live_before} -> {live_after} "
                              f"(must not shrink); the clone's scratch dir is inside the clone"})
    print(f"  [{'ok' if untouched else 'FAIL'}] live study untouched")

    passed = sum(1 for r in results if r["ok"])
    print()
    print("=" * 92)
    print(f"  {passed}/{len(results)} checks passed")
    print("=" * 92)

    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "remote": args.remote,
        "branch": args.branch,
        "checks": results,
        "examples": example_results,
        "passed": passed,
        "total": len(results),
    }, indent=2), encoding="utf-8")
    print(f"  Report written to: {out_path}")

    if args.keep:
        print(f"  Clone left at: {clone}")
    else:
        shutil.rmtree(workdir, ignore_errors=True)
        print("  Clone removed.")

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
