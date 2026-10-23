"""
Compare the V1 ablation study before and after the substrate scope fix.

The question this answers is the one the owner asked: *did the fix change
the scientific meaning of V1?*

Method. Every V1 conclusion is a COMPARISON between conditions, and all
eleven conditions ran on the same substrate. So the thing to compare is
not the absolute metrics -- those legitimately moved -- but each
condition's DELTA against the O_FULL reference arm, computed on the
pre-fix substrate and again on the post-fix substrate.

  Survived          the delta kept its sign and its size (within 25%)
  Changed magnitude the delta kept its sign but moved (more than 25%)
  Reversed          the delta changed sign
  New / Gone        a delta that did not exist before, or no longer exists

Usage:
    python benchmarks/v1_impact.py
Writes docs/v1_impact.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Metrics that are scalars at the top level of a condition's metrics dict.
SCALARS = ["pa", "pa_substrate", "ip", "scr", "coverage_ratio", "ss", "lc",
           "cd", "cd_duty_cycle", "cdt", "nsr", "es"]

POPULATIONS = ["G1 concepts", "G1 loops", "G1 predictions", "G1 anomalies",
               "G2 meta-concepts", "G2 processes", "G3 workflows",
               "G4 hypotheses", "G5 theories", "G5 questions", "G6 dreams",
               "G7 investigations", "G8 experiments"]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_census(pre_census: dict, post_census: dict) -> list[dict]:
    """The belief-level before/after, condition by condition."""
    fields = ["subjects_mean", "subjects_ge2_mean", "subjects_ge2_max",
              "mbsd_density", "belief_pool_mean", "belief_pool_max",
              "retention_pressure_mean"]
    rows = []
    for name in sorted(set(pre_census) | set(post_census)):
        p, q = pre_census.get(name, {}), post_census.get(name, {})
        if not p or not q:
            continue
        if p.get("hypothesis_layer_engaged") is False:
            rows.append({"condition": name, "note": "Layer 4 bypassed by design",
                         "pre": None, "post": None, "verdict": "UNCHANGED (bypassed)"})
            continue
        pre_vals = {f: p.get(f) for f in fields}
        post_vals = {f: q.get(f) for f in fields}
        # The headline judgement is on competing subjects, the quantity the
        # gate is defined on.
        p_ge2 = p.get("subjects_ge2_max")
        q_ge2 = q.get("subjects_ge2_max")
        if p_ge2 == 0 and q_ge2 and q_ge2 > 0:
            verdict = "REVERSED (was zero, now non-zero)"
        elif (p_ge2 or 0) == 0 and (q_ge2 or 0) == 0:
            verdict = "UNCHANGED (both zero)"
        elif p_ge2 is None or q_ge2 is None:
            verdict = "n/a"
        elif q_ge2 == 0:
            verdict = "REVERSED (was non-zero, now zero)"
        else:
            verdict = "CHANGED MAGNITUDE"
        rows.append({
            "condition": name,
            "pre": pre_vals,
            "post": post_vals,
            "pre_gate": {"G_MBD_abs_ge3": p.get("passes_mbsd_absolute_ge3"),
                         "G_MBD_density_ge050": p.get("passes_mbsd_density_ge050"),
                         "G_P1": p.get("passes_g_p1")},
            "post_gate": {"G_MBD_abs_ge3": q.get("passes_mbsd_absolute_ge3"),
                          "G_MBD_density_ge050": q.get("passes_mbsd_density_ge050"),
                          "G_P1": q.get("passes_g_p1")},
            "verdict": verdict,
        })
    return rows


def by_condition(doc: dict) -> dict:
    return {c["condition"]: c for c in doc["conditions"]}


def census_rows(path: Path) -> dict:
    if not path.exists():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    return {r["condition"]: r for r in doc.get("rows", [])}


# ==================================================================
# The interpretations. Measurements move; interpretations are what the
# project BELIEVED because of them. These are audited separately, and
# a change here is a change of scientific meaning.
# ==================================================================

def audit_interpretations(pre: dict, post: dict, pre_census: dict, post_census: dict) -> list[dict]:
    pc, qc = by_condition(pre), by_condition(post)

    def pops(cond: dict, key: str, default=None):
        return cond.get("final_populations", {}).get(key, default)

    def met(cond: dict, key: str, default=None):
        return cond.get("metrics", {}).get(key, default)

    def cen(name: dict, key: str, default=None):
        return name.get(key, default)

    out = []

    out.append({
        "id": "I1",
        "interpretation": "No Sleep is foundational: without sleep every developmental structure goes to zero.",
        "verdict": "SURVIVED",
        "post_evidence": (
            f"A post-fix: theories={pops(qc['A'], 'G5 theories')}, "
            f"questions={pops(qc['A'], 'G5 questions')}, "
            f"hypotheses={pops(qc['A'], 'G4 hypotheses')}, "
            f"dreams={pops(qc['A'], 'G6 dreams')}"),
        "reason": "Sleep bypasses every downstream layer by construction; no change in the frequency estimate can resurrect them.",
    })

    out.append({
        "id": "I2",
        "interpretation": "Memory Without Structure is foundational: without a structured substrate nothing develops.",
        "verdict": "SURVIVED",
        "post_evidence": (
            f"J post-fix: theories={pops(qc['J'], 'G5 theories')}, "
            f"hypotheses={pops(qc['J'], 'G4 hypotheses')}, "
            f"dreams={pops(qc['J'], 'G6 dreams')}"),
        "reason": "The substrate is removed outright; the scope fix cannot affect a condition that never builds a graph.",
    })

    out.append({
        "id": "I3",
        "interpretation": "No Lineage is the control: populations are identical to the reference arm and only the lineage metric moves.",
        "verdict": "SURVIVED",
        "post_evidence": (
            f"B post-fix populations equal O_FULL post-fix: "
            f"beliefs={cen(post_census.get('B', {}), 'belief_pool_max')} vs "
            f"{cen(post_census.get('O_FULL', {}), 'belief_pool_max')}, "
            f"subjects>=2 max={cen(post_census.get('B', {}), 'subjects_ge2_max')} vs "
            f"{cen(post_census.get('O_FULL', {}), 'subjects_ge2_max')}"),
        "reason": "Lineage removal strips parent_ids and cannot change which beliefs are produced.",
    })

    out.append({
        "id": "I4",
        "interpretation": "No Falsification FREEZES the organism rather than bloating it: contradiction duty collapses and it produces almost nothing.",
        "verdict": "RETRACTED",
        "post_evidence": (
            f"D post-fix: belief pool {cen(post_census.get('D', {}), 'belief_pool_mean')}"
            f"/{cen(post_census.get('D', {}), 'belief_pool_max')}, "
            f"subjects>=2 mean/max "
            f"{cen(post_census.get('D', {}), 'subjects_ge2_mean')}/"
            f"{cen(post_census.get('D', {}), 'subjects_ge2_max')}, "
            f"MBSD={cen(post_census.get('D', {}), 'mbsd_density')}, "
            f"retention pressure={cen(post_census.get('D', {}), 'retention_pressure_mean')} "
            f"(pre-fix: all zeros)"),
        "reason": (
            "The pre-fix zeros were produced by the scope defect, not by removing "
            "falsification. Post-fix, No Falsification is the BEST-SUPPLIED condition "
            "in the entire study -- 18 beliefs, every subject competing, MBSD 1.000 -- "
            "and it is the only V1 condition that passes the launch gates on the study "
            "stream. The interpretation 'falsification prevents freeze' is withdrawn; "
            "the pre-fix evidence for it was an instrumentation artifact."),
    })

    out.append({
        "id": "I5",
        "interpretation": "Dreams carry the upper ladder: removing them collapses processes and workflows to zero.",
        "verdict": "SURVIVED (direction), RECALIBRATED (magnitude)",
        "post_evidence": (
            f"E post-fix: subjects {cen(post_census.get('E', {}), 'subjects_mean')}, "
            f"subjects>=2 {cen(post_census.get('E', {}), 'subjects_ge2_mean')}/"
            f"{cen(post_census.get('E', {}), 'subjects_ge2_max')}, "
            f"MBSD {cen(post_census.get('E', {}), 'mbsd_density')} "
            f"(pre-fix: {cen(pre_census.get('E', {}), 'subjects_ge2_mean')}/"
            f"{cen(pre_census.get('E', {}), 'subjects_ge2_max')}, "
            f"MBSD {cen(pre_census.get('E', {}), 'mbsd_density')})"),
        "reason": (
            "E still has almost no subject competition post-fix, so the qualitative "
            "claim holds. But the pre-fix magnitude (0.07 subjects with >=2 beliefs) "
            "was itself inflated by the defect, and the post-fix figure is higher, so "
            "the claim is stated with a different number."),
    })

    out.append({
        "id": "I6",
        "interpretation": "EIG is the only producer of investigations and experiments, and removing it RAISES theories, hypotheses and questions while the two output layers go to zero -- it passes G4, but in the wrong direction.",
        "verdict": "SURVIVED",
        "post_evidence": (
            f"C post-fix: theories={pops(qc['C'], 'G5 theories')}, "
            f"questions={pops(qc['C'], 'G5 questions')}, "
            f"hypotheses={pops(qc['C'], 'G4 hypotheses')}, "
            f"investigations={pops(qc['C'], 'G7 investigations')}, "
            f"experiments={pops(qc['C'], 'G8 experiments')}"),
        "reason": "The intervention removes layers 7 and 8 outright; the direction of the effect is structural.",
    })

    out.append({
        "id": "I7",
        "interpretation": "Questions are not the gateway -- dreams are: removing questions leaves investigations and experiments alive.",
        "verdict": "SURVIVED",
        "post_evidence": (
            f"G post-fix: questions={pops(qc['G'], 'G5 questions')}, "
            f"investigations={pops(qc['G'], 'G7 investigations')}, "
            f"experiments={pops(qc['G'], 'G8 experiments')}"),
        "reason": "The layer ordering is unchanged by the frequency scope.",
    })

    out.append({
        "id": "I8",
        "interpretation": "Random curiosity is genuinely different selection (Jaccard 0.111 vs EIG) and still buys no developmental gain -- EIG is a perfect ranker that buys nothing measurable.",
        "verdict": "SURVIVED (as a V1 finding); the question it poses is now OPEN",
        "post_evidence": (
            "The selection-side facts (Jaccard overlap, top-k precision) are properties "
            "of the ranking code, not of the frequency estimate, so they are unaffected. "
            "Whether the *developmental* outcome is still flat is exactly what the V2 "
            "campaign measures, on a substrate where the belief cap binds."),
        "reason": (
            "A perfect selector over a starved candidate pool cannot matter. Post-fix "
            "the pool is no longer starved on the branch stimulus, so the V1 conclusion "
            "is not evidence against EIG; it is evidence that the pool was empty."),
    })

    out.append({
        "id": "I9",
        "interpretation": "The organism is SUPPLY-limited, not selection-limited: the scarce resource is competing expectations about the same subject, not vocabulary.",
        "verdict": "RETRACTED AS A GENERAL STATEMENT",
        "post_evidence": (
            "On the branch stimulus the pool is 18 beliefs over 7 competing subjects "
            "against a cap of 15, and the retention policy changes the retained "
            "competing-subject count (7 pre-retention, 5-6 post-retention). "
            "Selection is now measurable and the cap binds."),
        "reason": (
            "The claim was true of the study stream on the pre-fix substrate and is "
            "the reason the branch stimulus was built. It is not a property of the "
            "architecture, and stating it as one would have been the same mistake as "
            "the r=4 boundary: reading a property of the instrument as a property of "
            "the system."),
    })

    out.append({
        "id": "I10",
        "interpretation": "MAX_HYPOTHESES is INERT: the belief cap never binds, so the retention policy cannot matter.",
        "verdict": "RETRACTED AS A GENERAL STATEMENT (still true of the study stream)",
        "post_evidence": (
            "Study stream post-fix: belief pool max "
            f"{cen(post_census.get('O_FULL', {}), 'belief_pool_max')} against a cap of 15 "
            "-- still under, so still inert THERE. Branch stimulus: 18 beliefs against a "
            "cap of 15 -- the cap binds and the policy changes the retained population."),
        "reason": "An instrument property, scoped to a stimulus, reported as an architecture property.",
    })

    out.append({
        "id": "I11",
        "interpretation": "More vocabulary makes it worse: 42 world tags gave 1 theory and 97 gave 0.",
        "verdict": "SURVIVED",
        "post_evidence": (
            "The stimulus sweep is a comparison between two stimuli on one substrate, "
            "so its differential is unaffected by a change to the frequency estimate; "
            "the absolute theory counts move, the ordering does not."),
        "reason": "A within-substrate comparison, which is the kind that survives a substrate change.",
    })

    return out


def flat_metrics(cond: dict) -> dict:
    out = {}
    for key in SCALARS:
        if key in cond.get("metrics", {}):
            out[key] = cond["metrics"][key]
    return out


def compare(pre: dict, post: dict) -> dict:
    pre_c, post_c = by_condition(pre), by_condition(post)
    ref_pre = flat_metrics(pre_c.get("O_FULL", {}))
    ref_post = flat_metrics(post_c.get("O_FULL", {}))

    rows = []
    for name in sorted(set(pre_c) & set(post_c)):
        if name == "O_FULL":
            continue
        pm, qm = flat_metrics(pre_c[name]), flat_metrics(post_c[name])
        per_metric = {}
        for key in sorted(set(pm) & set(qm) & set(ref_pre) & set(ref_post)):
            d_pre = pm[key] - ref_pre[key]
            d_post = qm[key] - ref_post[key]
            if abs(d_pre) < 1e-12 and abs(d_post) < 1e-12:
                verdict = "unchanged (both zero)"
            elif abs(d_pre) < 1e-12:
                verdict = "NEW (was zero, now not)"
            elif abs(d_post) < 1e-12:
                verdict = "GONE (was not, now zero)"
            elif (d_pre > 0) != (d_post > 0):
                verdict = "REVERSED"
            else:
                scale = max(abs(d_pre), 1e-12)
                if abs(d_post - d_pre) / scale <= 0.25:
                    verdict = "SURVIVED"
                else:
                    verdict = "CHANGED MAGNITUDE"
            per_metric[key] = {
                "pre_delta": round(d_pre, 6),
                "post_delta": round(d_post, 6),
                "pre_value": pm[key],
                "post_value": qm[key],
                "verdict": verdict,
            }
        rows.append({
            "condition": name,
            "name": pre_c[name]["name"],
            "metrics": per_metric,
        })

    # The reference arm's own absolute values: the substrate changed, so
    # these are expected to move. Reported separately from the deltas.
    ref_rows = []
    for key in sorted(set(ref_pre) & set(ref_post)):
        p, q = ref_pre[key], ref_post[key]
        if abs(p - q) <= 1e-9:
            verdict = "unchanged"
        elif p == 0:
            verdict = "NEW"
        else:
            verdict = ("CHANGED MAGNITUDE"
                       if abs(q - p) / abs(p) > 0.25 else "SURVIVED")
        ref_rows.append({"metric": key, "pre": p, "post": q, "verdict": verdict})

    pops = []
    for key in POPULATIONS:
        pv = pre_c.get("O_FULL", {}).get("final_populations", {}).get(key)
        qv = post_c.get("O_FULL", {}).get("final_populations", {}).get(key)
        if pv is not None and qv is not None:
            pops.append({"population": key, "pre": pv, "post": qv,
                         "verdict": "unchanged" if pv == qv else "CHANGED MAGNITUDE"})

    return {"deltas": rows, "reference_arm": ref_rows, "reference_populations": pops}


def tally(result: dict) -> dict:
    counts = {}
    for row in result["deltas"]:
        for m in row["metrics"].values():
            counts[m["verdict"]] = counts.get(m["verdict"], 0) + 1
    return counts


def main() -> None:
    pre_path = REPO / "docs" / "ablation_study.json"
    post_path = REPO / "docs" / "ablation_study_postfix.json"
    if not post_path.exists():
        print("post-fix artifact not present yet:", post_path)
        sys.exit(1)

    pre, post = load(pre_path), load(post_path)
    result = compare(pre, post)
    counts = tally(result)

    pre_census = census_rows(REPO / "docs" / "mbsd_census.json")
    post_census = census_rows(REPO / "docs" / "mbsd_census_postfix.json")
    census_rows_out = compare_census(pre_census, post_census)
    interpretations = audit_interpretations(pre, post, pre_census, post_census)

    print("=" * 78)
    print("V1 BEFORE vs AFTER THE SCOPE FIX -- delta-vs-O_FULL verdicts")
    print("=" * 78)
    for verdict, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {verdict:<28} {n}")

    print()
    print("BELIEF-LEVEL BEFORE/AFTER (the quantity the gate is defined on):")
    print(f"  {'cond':<4} {'ge2 max pre':>12} {'ge2 max post':>13} "
          f"{'pool max pre':>13} {'pool max post':>14}  verdict")
    for r in census_rows_out:
        if r.get("pre") is None:
            print(f"  {r['condition']:<4} {'-':>12} {'-':>13} {'-':>13} {'-':>14}  {r['verdict']}")
            continue
        print(f"  {r['condition']:<4} {r['pre']['subjects_ge2_max']:>12} "
              f"{r['post']['subjects_ge2_max']:>13} "
              f"{r['pre']['belief_pool_max']:>13} "
              f"{r['post']['belief_pool_max']:>14}  {r['verdict']}")

    print()
    print("REVERSED or NEW/GONE deltas (these are the ones that change meaning):")
    any_special = False
    for row in result["deltas"]:
        for key, m in row["metrics"].items():
            if m["verdict"] in ("REVERSED", "NEW (was zero, now not)",
                                "GONE (was not, now zero)"):
                any_special = True
                print(f"  {row['condition']:<3} {key:<14} "
                      f"pre_delta={m['pre_delta']:>10} post_delta={m['post_delta']:>10}  "
                      f"{m['verdict']}")
    if not any_special:
        print("  (none)")

    print()
    print("INTERPRETATION AUDIT -- what the project BELIEVED, and what it")
    print("believes now. A change here is a change of scientific meaning.")
    for i in interpretations:
        print()
        print(f"  [{i['id']}] {i['verdict']}")
        print(f"       claim   : {i['interpretation']}")
        print(f"       evidence: {i['post_evidence']}")
        print(f"       reason  : {i['reason']}")

    print()
    print("REFERENCE ARM (O_FULL) absolute metrics:")
    for r in result["reference_arm"]:
        print(f"  {r['metric']:<16} pre={r['pre']:>12} post={r['post']:>12}  {r['verdict']}")

    print()
    print("REFERENCE ARM final populations:")
    for p in result["reference_populations"]:
        print(f"  {p['population']:<18} pre={p['pre']:>4} post={p['post']:>4}  {p['verdict']}")

    out = REPO / "docs" / "v1_impact.json"
    out.write_text(json.dumps({
        "pre_artifact": str(pre_path.relative_to(REPO)),
        "post_artifact": str(post_path.relative_to(REPO)),
        "tally": counts,
        "census_comparison": census_rows_out,
        "interpretations": interpretations,
        **result,
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
