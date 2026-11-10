"""The D3 result writers must refuse a degenerate seed axis in a child process.

The in-process tests replace ``build`` and call ``finish`` directly. This test runs each
module's own ``main(["--finish"])`` in a child process, injects only the synthetic artifact,
and checks the process exit and the absence of both output files.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from benchmarks import d3_persistence_run as R
from benchmarks import d3_persistence_seed_varying as S

ROOT = Path(__file__).resolve().parent.parent

_CHILD = r"""
import importlib
import json
import sys
from pathlib import Path

M = importlib.import_module("{module}")
artifact = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
M.ARTIFACT = Path(sys.argv[2])
M.{page_attr} = Path(sys.argv[3])
M.build = lambda: artifact
raise SystemExit(M.main(["--finish"]))
"""


def _identical_artifact(module_name: str) -> dict:
    """A fully seed-degenerate copy of the historical run, written only under tmp_path."""
    if module_name == "benchmarks.d3_persistence_run":
        artifact = json.loads(
            (ROOT / "docs" / "d3_persistence_run.json").read_text(encoding="utf-8")
        )
    else:
        artifact = json.loads(
            (ROOT / "docs" / "d3_persistence_seed_varying_run.json").read_text(
                encoding="utf-8"
            )
        )
        for stage in R.STAGES:
            for arm in R.ARMS:
                first = next(
                    cell for cell in artifact["cells"]
                    if cell["stage"] == stage and cell["arm"] == arm
                )
                for cell in artifact["cells"]:
                    if cell["stage"] == stage and cell["arm"] == arm:
                        for field in ("theory_counts", "first_zero_cycle", "recall_early",
                                      "predictions_early", "world_digest"):
                            cell[field] = copy.deepcopy(first[field])
    artifact["seed_axis"] = (R.seed_axis(artifact["cells"])
                             if module_name == "benchmarks.d3_persistence_run"
                             else S.seed_axis(artifact["cells"]))
    return artifact


@pytest.mark.parametrize(
    ("module_name", "page_attr", "artifact_name"),
    [
        ("benchmarks.d3_persistence_run", "DOC", "d3_persistence_run.json"),
        ("benchmarks.d3_persistence_seed_varying", "RESULT",
         "d3_persistence_seed_varying_run.json"),
    ],
    ids=["D3-1", "D3-2"],
)
def test_finish_refuses_a_degenerate_artifact_in_a_subprocess(
        tmp_path, module_name, page_attr, artifact_name):
    artifact = _identical_artifact(module_name)
    synthetic = tmp_path / artifact_name
    synthetic.write_text(json.dumps(artifact), encoding="utf-8")
    out = tmp_path / "artifact.json"
    page = tmp_path / "page.md"

    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    proc = subprocess.run(
        [sys.executable, "-c", _CHILD.format(module=module_name, page_attr=page_attr),
         str(synthetic), str(out), str(page)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )

    combined = proc.stdout + proc.stderr
    assert proc.returncode != 0, combined
    assert "single-world pass cannot be reported" in combined, combined
    assert not out.exists(), "the artifact was written before the guard fired"
    assert not page.exists(), "the result page was written before the guard fired"
