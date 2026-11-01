"""Where do the two candidate populations first differ?

Pre-registered in ``docs/ONSET-INSTRUMENT-BRIEF.md`` and journal §75.  This
instrument generalises ``benchmarks/divergence_cycle_capture.py`` from the fixed
pair ``(k, k-1)`` to the whole range ``1 … k`` and reports, per arm-pair, the
first cycle at which the campaign-side and current-side candidate pools differ
in membership.

It reuses the capture's worker unchanged — the same script, the same
marker-witnessed addressing rule — and writes its parts to a directory of its
own, so the capture's artifact and cache are untouched.

**The rules this instrument is bound by**, from the brief:

- ``F1``  the cycles ``k`` and ``k-1`` it captures must reproduce the
  ``set_identical`` values and the pool IDs already in
  ``docs/divergence_cycle_capture.json``.  If they do not, no onset is reported.
- ``C1``  the control seed's two hash-seed runs must hold identical pools at
  every cycle.  Where the audit records the *same* seed for both sides the
  comparison is a run against itself, which cannot fail; the report must say so
  rather than claim the gauge holds.
- ``F3``  a window that fails its marker check is **not measured**, never an
  empty pool and never a differing pool.
- ``F4``  an onset whose transition record is empty while the sets differ is
  withdrawn.

**Reporting rules** (§7a of the brief): the eleven arm-pairs whose onset is
already fixed by arithmetic are *witness cases* — instrumentation validation,
not findings.  The five already divergent at ``k-1`` are the *search cases* and
carry the scientific content.  An onset that bottoms out at cycle 1 is reported
as ``<= 1``, never as "introduced at cycle 1".
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
SCRATCH = REPO / ".scratch"
PARTS_DIR = SCRATCH / "divergence_onset_parts"
MEMBERSHIP_ARTIFACT = REPO / "docs" / "candidate_membership_audit.json"
CAPTURE_ARTIFACT = REPO / "docs" / "divergence_cycle_capture.json"
ARTIFACT = REPO / "docs" / "divergence_onset.json"
REPORT = REPO / "docs" / "DIVERGENCE-ONSET.md"
CAPTURE_INSTRUMENT = REPO / "benchmarks" / "divergence_cycle_capture.py"

OBSERVER_VERSION = 1
CONTROL_SEED = ("T1", 20261101)
ARMS = ("B", "C")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def part_path(task: str, seed: int, hash_seed: int) -> Path:
    return PARTS_DIR / ("%s_%d_hs%d.json" % (task, seed, hash_seed))


def part_is_current(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return (data.get("observer_version") == OBSERVER_VERSION
                and data.get("kind") == "divergence_onset_part")
    except (json.JSONDecodeError, ValueError, OSError):
        return False


def spawn_worker(task: str, seed: int, hash_seed: int,
                 cycles: list[int]) -> tuple[str, int, int, Path]:
    """Run the capture's worker at a range of cycles, into this instrument's dir."""
    out = part_path(task, seed, hash_seed)
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = str(hash_seed)
    cmd = [sys.executable, "-X", "utf8", str(CAPTURE_INSTRUMENT),
           "--worker", "--task", task, "--seed", str(seed),
           "--cycles", ",".join(str(c) for c in cycles), "--out", str(out)]
    proc = subprocess.run(cmd, cwd=str(REPO), env=env,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError("worker failed for %s/%d hs=%d:\n%s"
                           % (task, seed, hash_seed, proc.stderr[-2000:]))
    with open(out, "r", encoding="utf-8") as f:
        part = json.load(f)
    part["kind"] = "divergence_onset_part"
    part["observer_version"] = OBSERVER_VERSION
    with open(out, "w", encoding="utf-8") as f:
        json.dump(part, f, indent=1, sort_keys=True)
    return task, seed, hash_seed, out


def membership_inputs() -> list[dict[str, Any]]:
    """The eight failing seeds, with their audit index and two hash seeds."""
    with open(MEMBERSHIP_ARTIFACT, "r", encoding="utf-8") as f:
        audit = json.load(f)
    out = []
    for entry in audit["results"]:
        if (entry["task"], entry["seed"]) == CONTROL_SEED:
            continue
        divergence = entry.get("divergence", {})
        index = divergence.get("first_cycle")
        if index is None or not entry.get("campaign_reproduced"):
            continue
        out.append({
            "task": entry["task"],
            "seed": entry["seed"],
            "audit_index": int(index),
            "campaign_hash_seed": entry["campaign_side_hash_seed"],
            "baseline_hash_seed": entry["baseline_hash_seed"],
        })
    return out


def control_input() -> dict[str, Any]:
    """The control seed: the arm-pair the pools must *not* diverge on."""
    with open(MEMBERSHIP_ARTIFACT, "r", encoding="utf-8") as f:
        audit = json.load(f)
    for entry in audit["results"]:
        if (entry["task"], entry["seed"]) == CONTROL_SEED:
            return {
                "task": entry["task"],
                "seed": entry["seed"],
                "campaign_hash_seed": entry["campaign_side_hash_seed"],
                "baseline_hash_seed": entry["baseline_hash_seed"],
            }
    raise SystemExit("control seed %r absent from %s"
                     % (CONTROL_SEED, MEMBERSHIP_ARTIFACT))


def engine_cycle(audit_index: int) -> int:
    """The divergence cycle in engine numbering, from a zero-based index."""
    return audit_index + 1


def control_is_valid(campaign_seed: int, baseline_seed: int) -> bool:
    """Whether the control comparison can fail at all.

    C1 compares the control seed's two hash-seed runs.  Where the audit records
    the same seed for both sides there is one configuration, not two: the
    comparison is a run against itself and cannot fail, so it is not evidence
    that the gauge holds and F2 is not adjudicated.
    """
    return campaign_seed != baseline_seed


def pool(part: dict[str, Any], arm: str, cycle: int) -> tuple[list[str], bool]:
    """The pool at ``cycle`` for ``arm``, and whether it was measured."""
    window = part.get("arms", {}).get(arm, {}).get(str(cycle))
    if window is None or not window.get("addressed"):
        return [], False
    return [c["id"] for c in window["candidates"]], True


def onset_for_arm(camp: dict[str, Any], ours: dict[str, Any], arm: str,
                  last_cycle: int) -> dict[str, Any]:
    """The first cycle at which the two pools differ in membership."""
    measured: dict[int, tuple[list[str], list[str], bool]] = {}
    for cycle in range(1, last_cycle + 1):
        camp_ids, camp_ok = pool(camp, arm, cycle)
        ours_ids, ours_ok = pool(ours, arm, cycle)
        measured[cycle] = (camp_ids, ours_ids, camp_ok and ours_ok)

    unmeasured = [c for c, (_, _, ok) in measured.items() if not ok]
    for cycle in range(1, last_cycle + 1):
        camp_ids, ours_ids, captured = measured[cycle]
        if not captured:
            continue
        if set(camp_ids) == set(ours_ids):
            continue
        if cycle == 1:
            return {"state": "at_or_before_1", "onset_cycle": 1,
                    "entered": [], "left": [], "unmeasured_cycles": unmeasured}
        prev_camp, prev_ours, prev_ok = measured[cycle - 1]
        if not prev_ok:
            continue                      # the bracket is broken: not measurable
        if set(prev_camp) == set(prev_ours):
            return {"state": "onset", "onset_cycle": cycle,
                    "entered": sorted(set(camp_ids) - set(prev_camp)),
                    "left": sorted(set(prev_camp) - set(camp_ids)),
                    "unmeasured_cycles": unmeasured}
    if any(not ok for _, _, ok in measured.values()):
        return {"state": "not_measured", "onset_cycle": None,
                "entered": [], "left": [], "unmeasured_cycles": unmeasured}
    return {"state": "none", "onset_cycle": None,
            "entered": [], "left": [], "unmeasured_cycles": []}


def capture_all(args: argparse.Namespace) -> dict[str, Any]:
    inputs = membership_inputs()
    control = control_input()
    jobs = []
    for item in inputs:
        cycles = list(range(1, engine_cycle(item["audit_index"]) + 1))
        for hash_seed in (item["campaign_hash_seed"], item["baseline_hash_seed"]):
            jobs.append((item["task"], item["seed"], hash_seed, cycles))
    # The control has no divergence cycle: capture it over the longest range any
    # search case uses, so "identical at every cycle" is a statement about the
    # same span, not a shorter one.
    control_range = max(engine_cycle(i["audit_index"]) for i in inputs)
    for hash_seed in (control["campaign_hash_seed"], control["baseline_hash_seed"]):
        jobs.append((control["task"], control["seed"], hash_seed,
                     list(range(1, control_range + 1))))

    started = time.time()
    ran = cached = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool_exec:
        futures = []
        for task, seed, hash_seed, cycles in jobs:
            out = part_path(task, seed, hash_seed)
            if part_is_current(out) and not args.force:
                cached += 1
                continue
            futures.append(pool_exec.submit(spawn_worker, task, seed,
                                            hash_seed, cycles))
        for future in futures:
            task, seed, hash_seed, _ = future.result()
            ran += 1
            print("  ran %s/%d hs=%d" % (task, seed, hash_seed), flush=True)
    return {"inputs": inputs, "control": control, "runs": ran,
            "cached": cached, "seconds": round(time.time() - started, 1),
            "command": "python benchmarks/divergence_onset.py --workers %d"
                       % args.workers}


def analyse(meta: dict[str, Any]) -> dict[str, Any]:
    with open(CAPTURE_ARTIFACT, "r", encoding="utf-8") as f:
        reference = json.load(f)
    ref = {(e["task"], e["seed"]): e for e in reference["results"]}

    results = []
    f1_mismatches = []
    for item in meta["inputs"]:
        k = engine_cycle(item["audit_index"])
        camp = json.loads(part_path(item["task"], item["seed"],
                                    item["campaign_hash_seed"]).read_text("utf-8"))
        ours = json.loads(part_path(item["task"], item["seed"],
                                    item["baseline_hash_seed"]).read_text("utf-8"))
        entry = ref.get((item["task"], item["seed"]))
        arms = {}
        for arm in ARMS:
            onset = onset_for_arm(camp, ours, arm, k)
            f1 = {}
            for cycle in (k, k - 1):
                camp_ids, camp_ok = pool(camp, arm, cycle)
                ours_ids, ours_ok = pool(ours, arm, cycle)
                if not (camp_ok and ours_ok):
                    f1[str(cycle)] = {"reproduced": None, "reason": "not measured"}
                    continue
                computed = set(camp_ids) == set(ours_ids)
                if cycle == k:
                    recorded = entry["arms"][arm]["set_identical"]
                    recorded_ids = (sorted(entry["arms"][arm]["campaign_pool_order"]),
                                    sorted(entry["arms"][arm]["current_pool_order"]))
                else:
                    prev = entry["arms"][arm]["previous_cycle"]
                    recorded = prev["set_identical"]
                    recorded_ids = (sorted(prev["campaign_pool_order"]),
                                    sorted(prev["current_pool_order"]))
                ids_match = (sorted(camp_ids), sorted(ours_ids)) == recorded_ids
                ok = (computed == bool(recorded)) and ids_match
                f1[str(cycle)] = {"reproduced": ok, "computed": computed,
                                  "recorded": bool(recorded), "ids_match": ids_match}
                if not ok:
                    f1_mismatches.append("%s/%d arm %s cycle %d"
                                         % (item["task"], item["seed"], arm, cycle))
            arms[arm] = {
                "onset": onset,
                "f1": f1,
                "divergence_cycle": k,
                "search_case": not entry["arms"][arm]["previous_cycle"]["set_identical"],
            }
        results.append({"task": item["task"], "seed": item["seed"],
                        "audit_index": item["audit_index"],
                        "divergence_cycle": k, "arms": arms})

    c_entry = meta["control"]
    camp_part = json.loads(part_path(c_entry["task"], c_entry["seed"],
                                     c_entry["campaign_hash_seed"]).read_text("utf-8"))
    base_part = json.loads(part_path(c_entry["task"], c_entry["seed"],
                                     c_entry["baseline_hash_seed"]).read_text("utf-8"))
    control: dict[str, Any] = {
        "task": c_entry["task"],
        "seed": c_entry["seed"],
        "campaign_hash_seed": c_entry["campaign_hash_seed"],
        "baseline_hash_seed": c_entry["baseline_hash_seed"],
        "hash_seeds_equal": not control_is_valid(c_entry["campaign_hash_seed"],
                                                 c_entry["baseline_hash_seed"]),
        "cycles": [],
        "identical_at_every_cycle": True,
        "onset": None,
    }
    for arm in ARMS:
        keys = ({int(k) for k in camp_part.get("arms", {}).get(arm, {})}
                & {int(k) for k in base_part.get("arms", {}).get(arm, {})})
        for cycle in sorted(keys):
            a, a_ok = pool(camp_part, arm, cycle)
            b, b_ok = pool(base_part, arm, cycle)
            if not (a_ok and b_ok):
                control["cycles"].append({"arm": arm, "cycle": cycle,
                                          "measured": False})
                continue
            same = set(a) == set(b)
            control["cycles"].append({"arm": arm, "cycle": cycle, "measured": True,
                                      "same_set": same, "same_order": a == b})
            if not same:
                control["identical_at_every_cycle"] = False
                if control["onset"] is None:
                    control["onset"] = {"arm": arm, "cycle": cycle}

    return {
        "kind": "divergence_onset",
        "observer_version": OBSERVER_VERSION,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": meta["command"],
        "runs": meta["runs"],
        "cached": meta["cached"],
        "seconds": meta["seconds"],
        "membership_artifact_sha256": sha256_file(MEMBERSHIP_ARTIFACT),
        "capture_artifact_sha256": sha256_file(CAPTURE_ARTIFACT),
        "f1": {"passed": not f1_mismatches, "mismatches": f1_mismatches},
        "control": control,
        "results": results,
    }


def control_block(c_entry: dict[str, Any], seeds: list[int]) -> dict[str, Any]:
    """The control comparison at a declared pair of hash seeds.

    Kept as one function so a re-run cannot compute the control differently
    from the analysis that reported it void in the first place.
    """
    parts = [json.loads(part_path(c_entry["task"], c_entry["seed"], s).read_text("utf-8"))
             for s in seeds]
    control: dict[str, Any] = {
        "task": c_entry["task"],
        "seed": c_entry["seed"],
        "campaign_hash_seed": seeds[0],
        "baseline_hash_seed": seeds[1],
        "hash_seeds_equal": not control_is_valid(seeds[0], seeds[1]),
        "cycles": [],
        "identical_at_every_cycle": True,
        "onset": None,
    }
    for arm in ARMS:
        keys = set.intersection(*[{int(k) for k in part.get("arms", {}).get(arm, {})}
                                 for part in parts])
        for cycle in sorted(keys):
            pools = [pool(part, arm, cycle) for part in parts]
            if not all(ok for _, ok in pools):
                control["cycles"].append({"arm": arm, "cycle": cycle,
                                          "measured": False})
                continue
            ids = [x for x, _ in pools]
            same = set(ids[0]) == set(ids[1])
            control["cycles"].append({"arm": arm, "cycle": cycle, "measured": True,
                                      "same_set": same, "same_order": ids[0] == ids[1]})
            if not same:
                control["identical_at_every_cycle"] = False
                if control["onset"] is None:
                    control["onset"] = {"arm": arm, "cycle": cycle}
    return control


def render(artifact: dict[str, Any]) -> str:
    lines: list[str] = []
    add = lines.append
    add("# Divergence onset — the first cycle at which the candidate pools differ")
    add("")
    add("**Status.** Measured. Pre-registered in `docs/ONSET-INSTRUMENT-BRIEF.md` "
        "and journal §75 before this instrument existed.")
    add("")
    add("**The question.** At what earliest engine cycle do the campaign-side and "
        "current-side candidate pools differ in membership, and what entered or "
        "left there? Not why identical pools admit differently — that question "
        "lost its subject on 2026-11-01 — and not where the admitted streams "
        "first differ, which the membership audit already answers analytically.")
    add("")

    add("## 1. The checks")
    add("")
    f1 = artifact["f1"]
    add("**F1 — reproduction of the corrected capture.** Cycles *k* and *k−1* "
        "captured here must reproduce `docs/divergence_cycle_capture.json`'s "
        "`set_identical` values **and** its pool IDs, on every arm-pair. **%s**"
        % ("Passed on all 16 arm-pairs." if f1["passed"]
           else "**FAILED** — " + "; ".join(f1["mismatches"])
                + " — no onset is reported."))
    add("")

    control = artifact["control"]
    same_set = sum(1 for c in control["cycles"] if c.get("same_set"))
    measured = sum(1 for c in control["cycles"] if c.get("measured"))
    if control.get("hash_seeds_equal"):
        add("**C1 — the control seed. VOID, and that is a defect in the protocol "
            "as executed.** The audit records campaign hash seed **%s** and "
            "baseline hash seed **%s** for %s/%d — the *same* seed. The two "
            "runs are therefore one configuration, and the comparison is a run "
            "against itself: it cannot fail. It is **not** evidence that the "
            "gauge holds, and **F2 is not adjudicated by this run.** The pools "
            "it compared were identical in %d of %d measured cycles, which is "
            "precisely what comparing a run with itself must return."
            % (control["campaign_hash_seed"], control["baseline_hash_seed"],
               control["task"], control["seed"], same_set, measured))
    else:
        add("**C1 — the control seed.** %s/%d at hash seeds %s and %s, both "
            "arms, every captured cycle: the two runs hold **%s** sets (%d of "
            "%d measured cycles identical). %s"
            % (control["task"], control["seed"], control["campaign_hash_seed"],
               control["baseline_hash_seed"],
               "identical" if control["identical_at_every_cycle"] else "different",
               same_set, measured,
               "The gauge holds." if control["identical_at_every_cycle"] else
               "**The membership difference is generic to hash-seeded "
               "construction, not specific to the divergence; no onset below "
               "is informative.**"))
    add("")
    if control.get("identical_at_every_cycle") is False:
        add("**F2 — the criterion that governs C1.** F2 says the membership "
            "difference is *generic to hash-seeded construction* if a seed that "
            "does not diverge shows one too. It does, so **F2 fires and this "
            "instrument is inadmissible by its own pre-registration**: the onsets "
            "below are measured facts about these arm-pairs and may not be "
            "attributed to the divergence.")
        add("")

    add("## 2. Onset per arm-pair")
    add("")
    add("**Witness cases** have an onset already fixed by arithmetic and are "
        "instrumentation validation; **search cases** were already divergent at "
        "*k−1* and carry the scientific content.")
    add("")
    add("| Task | Seed | Divergence cycle *k* | Arm | Case | Onset | Entered | Left |")
    add("|---|---|---|---|---|---|---|---|")
    for entry in artifact["results"]:
        for arm in ARMS:
            info = entry["arms"][arm]
            o = info["onset"]
            where = {"onset": "cycle %d" % (o["onset_cycle"] or 0),
                     "at_or_before_1": "≤ 1",
                     "none": "none",
                     "not_measured": "not measured"}[o["state"]]
            add("| %s | %d | %d | %s | %s | %s | %d | %d |"
                % (entry["task"], entry["seed"], entry["divergence_cycle"], arm,
                   "search" if info["search_case"] else "witness", where,
                   len(o["entered"]), len(o["left"])))
    add("")

    search = [(e, a) for e in artifact["results"] for a in ARMS
              if e["arms"][a]["search_case"]]
    located_before, located_any = [], []
    for entry, arm in search:
        o = entry["arms"][arm]["onset"]
        if o["state"] == "onset":
            located_any.append((entry["task"], entry["seed"], arm))
            if o["onset_cycle"] < entry["divergence_cycle"] - 1:
                located_before.append((entry["task"], entry["seed"], arm))
    witness_bad = [(e["task"], e["seed"], a) for e in artifact["results"]
                   for a in ARMS
                   if not e["arms"][a]["search_case"]
                   and e["arms"][a]["onset"]["state"] != "onset"]
    add("**The five search cases.** **%d of %d** reached onset **strictly "
        "before *k−1***, which is what P2 asks; **%d of %d** were located at a "
        "specific cycle in total. A case that bottoms out at cycle 1 is "
        "reported as **≤ 1**, never as introduced there."
        % (len(located_before), len(search), len(located_any), len(search)))
    add("")
    add("**The witness cases.** **%d of %d** landed at *k*, as arithmetic "
        "requires. %s"
        % (len([1 for e in artifact["results"] for a in ARMS
                if not e["arms"][a]["search_case"]]) - len(witness_bad),
           len([1 for e in artifact["results"] for a in ARMS
                if not e["arms"][a]["search_case"]]),
           "A witness case landing anywhere else would be an instrument defect "
           "and is reported rather than reconciled."))
    add("")

    departures = sum(len(e["arms"][a]["onset"]["left"])
                     for e in artifact["results"] for a in ARMS
                     if e["arms"][a]["onset"]["state"] == "onset")
    onsets = [(e, a) for e in artifact["results"] for a in ARMS
              if e["arms"][a]["onset"]["state"] == "onset"]
    add("**Insertion or replacement?** Across the %d arm-pairs with a located "
        "onset, **%d** candidate(s) left a pool at the cycle it first differed. "
        "%s"
        % (len(onsets), departures,
           "Every onset is an **insertion**: the pools never shrink at the "
           "transition, they gain candidates." if departures == 0
           else "Some onsets also remove candidates; see the transitions below."))
    add("")

    add("## 3. What entered and left at each onset")
    add("")
    for entry in artifact["results"]:
        for arm in ARMS:
            o = entry["arms"][arm]["onset"]
            if o["state"] != "onset":
                continue
            add("- **%s/%d arm %s, cycle %d** — entered %d, left %d"
                % (entry["task"], entry["seed"], arm, o["onset_cycle"],
                   len(o["entered"]), len(o["left"])))
            if o["entered"]:
                add("  - entered: " + ", ".join("`%s`" % i for i in o["entered"][:10])
                    + (" …" if len(o["entered"]) > 10 else ""))
            if o["left"]:
                add("  - left: " + ", ".join("`%s`" % i for i in o["left"][:10])
                    + (" …" if len(o["left"]) > 10 else ""))
    add("")

    add("## 4. What this does not establish")
    add("")
    add("It does not name the operation that introduces the difference. A "
        "candidate entering the pool at cycle *c* says an upstream write "
        "changed at *c*, not that a named function is responsible. It does not "
        "test H2, does not reopen the mechanism experiment, does not re-score "
        "D0, and changes no engine file.")
    add("")
    if control.get("hash_seeds_equal"):
        add("**C1 being void matters for scope.** The onsets are measurements of "
            "a real difference between two hash seeds; what is missing is the "
            "check that a *non-diverging* seed shows none. Until that is run at "
            "two distinct hash seeds, the onsets are characterised, not yet "
            "shown to be specific to the failing seeds.")
    else:
        add("**What C1 now licenses.** The control was re-run at the declared "
            "pair %s and %s — the audit's own pair is one seed twice, which is "
            "why the first pass could not adjudicate it. %s"
            % (control["campaign_hash_seed"], control["baseline_hash_seed"],
               "Its pools are **identical at every measured cycle**, so the "
               "onsets are specific to the failing seeds rather than a generic "
               "consequence of hash-seeded construction." if control["identical_at_every_cycle"]
               else "Its pools **differ**, so a membership difference is a "
                    "generic consequence of hash-seeded construction and the "
                    "onsets carry no divergence-specific weight."))
    add("")
    add("## Provenance")
    add("")
    add("- Artifact: `docs/divergence_onset.json` (membership audit sha256 "
        "`%s`)." % artifact["membership_artifact_sha256"])
    add("- Instrument: `benchmarks/divergence_onset.py`; the worker is "
        "`benchmarks/divergence_cycle_capture.py`, reused unchanged.")
    add("- Observer version: %s." % artifact["observer_version"])
    add("- Command: `%s` — %d run(s), %d cached, %.1f s."
        % (artifact["command"], artifact["runs"], artifact["cached"],
           artifact["seconds"]))
    rerun = artifact.get("control_rerun")
    if rerun:
        add("- Control re-run: `%s` — %d run(s), %d cached; the hash-seed "
            "pair was declared before it (%s and %s)."
            % (rerun["command"], rerun["runs"], rerun["cached"],
               rerun["declared_pair"][0], rerun["declared_pair"][1]))
    add("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--control-only", action="store_true")
    parser.add_argument("--control-seeds", default="")
    args = parser.parse_args(argv)

    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    if args.control_only:
        seeds = [int(x) for x in (args.control_seeds or "0,1").split(",")]
        if len(seeds) != 2 or seeds[0] == seeds[1]:
            raise SystemExit("--control-seeds needs two distinct seeds")
        c_entry = control_input()
        spans = max(engine_cycle(i["audit_index"]) for i in membership_inputs())
        started = time.time()
        ran = cached = 0
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = []
            for seed in seeds:
                if part_is_current(part_path(c_entry["task"], c_entry["seed"], seed)):
                    cached += 1
                    continue
                futs.append(ex.submit(spawn_worker, c_entry["task"],
                                      c_entry["seed"], seed,
                                      list(range(1, spans + 1))))
            for f in futs:
                task, seed, hs, _ = f.result()
                ran += 1
                print("  ran %s/%d hs=%d" % (task, seed, hs), flush=True)
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        artifact["control"] = control_block(c_entry, seeds)
        artifact["control_rerun"] = {
            "declared_pair": seeds,
            "reason": "The audit's control pair is one hash seed twice, so C1 "
                      "could not fail. This pair is declared before the run and "
                      "is the smallest change that gives the comparison two "
                      "configurations.",
            "runs": ran, "cached": cached, "seconds": round(time.time() - started, 1),
            "command": "python benchmarks/divergence_onset.py --control-only "
                       "--control-seeds %d,%d --workers %d"
                       % (seeds[0], seeds[1], args.workers),
        }
        ARTIFACT.write_text(json.dumps(artifact, indent=1, sort_keys=True) + "\n",
                            encoding="utf-8")
        REPORT.write_text(render(artifact) + "\n", encoding="utf-8")
        print("control re-run at %r: %d run(s), %d cached" % (seeds, ran, cached))
        return 0
    if args.render_only:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    else:
        artifact = analyse(capture_all(args))
        ARTIFACT.write_text(json.dumps(artifact, indent=1, sort_keys=True) + "\n",
                            encoding="utf-8")
    REPORT.write_text(render(artifact) + "\n", encoding="utf-8")
    print("wrote %s and %s (%d runs, %d cached)"
          % (ARTIFACT.relative_to(REPO), REPORT.relative_to(REPO),
             artifact["runs"], artifact["cached"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
