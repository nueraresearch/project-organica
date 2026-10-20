"""
Phase F: Formal Cross-Domain Validation Script
Runs all 4 reproduction domains, collects structured telemetry, and
writes a machine-readable validation report to docs/validation_report.json.

Measures per domain:
  - Sleep cycles to first G2 composite emergence
  - Peak concept count
  - Peak process count
  - Peak workflow count  
  - Hypothesis count at Cycle 3
  - Peak question uncertainty (entropy)
  - Peak experiment priority
  - Lineage integrity (% of parent links verified)
  - Total sleep runtime (ms)
"""

import json
import time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from organica import MemoryService, SleepService

DOMAINS = [
    {
        "name": "Developer Workflow",
        "description": "Software CI/CD: failure → modified → passed",
        "events": [
            "developer modified auth login session",
            "developer executed test suite",
            "test suite report: failures detected session",
            "failure detected in login module",
            "developer modified auth session handler",
            "developer executed test suite",
            "test suite report: passed validation clean",
            "developer modified api router endpoint",
            "developer executed test suite",
            "test suite report: failures detected router",
            "failure detected in router endpoint",
            "developer modified api router handler",
            "developer executed test suite",
            "test suite report: passed validation clean",
        ] * 4,
    },
    {
        "name": "Bug Tracking Lifecycle",
        "description": "Issue triage → engineer → commit → verify → close",
        "events": [
            "user reported issue ticket assigned",
            "triage assigned issue engineer review",
            "engineer reproduce issue commit patch",
            "pipeline executed tests verified passed",
            "support agent closed issue resolved",
            "user reported issue ticket assigned",
            "triage assigned issue engineer review",
            "engineer reproduce commit patch failed",
            "engineer reproduce commit patch retry",
            "pipeline executed tests verified passed",
            "support agent closed issue resolved",
        ] * 4,
    },
    {
        "name": "Synthetic Ecological Foraging",
        "description": "Organism → forage → consume → replenish cycle",
        "events": [
            "organism search energy level depleted",
            "organism locate resource food available",
            "organism consume food energy restored",
            "biome replenish vegetation growth season",
            "organism rest metabolism stable recovered",
            "organism search energy level depleted",
            "organism locate resource food available",
            "organism consume food energy restored",
            "biome replenish vegetation growth season",
        ] * 5,
    },
    {
        "name": "Autonomous Robot Kinematics",
        "description": "Drive → detect obstacle → turn → clear path",
        "events": [
            "robot drive forward velocity motion",
            "sonar detect obstacle distance near",
            "actuator steer pivot turn left",
            "sonar sense clear corridor open",
            "robot drive forward velocity motion",
            "sonar detect obstacle distance near",
            "actuator steer pivot turn right",
            "sonar sense clear corridor open",
            "robot drive forward velocity motion",
        ] * 5,
    },
]


def run_domain(domain: dict) -> dict:
    db = Path(f"__validation_temp_{domain['name'].replace(' ', '_')}.db")
    if db.exists():
        db.unlink()

    mem = MemoryService(db)
    for e in domain["events"]:
        mem.store(e, event_type="observe", source="validation")

    sleep = SleepService(mem)
    reports = []
    t0 = time.time()
    for _ in range(3):
        reports.append(sleep.run())
    total_ms = round((time.time() - t0) * 1000, 1)

    # Cycles-to-composite: first cycle where processes > 0
    cycles_to_composite = None
    for i, r in enumerate(reports):
        if len(r.processes) > 0 or len(r.meta_concepts) > 0:
            cycles_to_composite = i + 1
            break

    # Peak question uncertainty
    all_questions = reports[-1].questions
    peak_uncertainty = max((q.uncertainty for q in all_questions), default=0.0)

    # Peak experiment priority
    all_experiments = reports[-1].experiments
    peak_priority = max((e.priority for e in all_experiments), default=0.0)

    # Lineage integrity
    priors = sleep._load_prior_candidates()
    id_set = {c.get("id") for c in priors if "id" in c}
    non_g1 = [c for c in priors if c.get("generation", 1) > 1 and "parent_ids" in c]
    total_links = sum(len(c.get("parent_ids", [])) for c in non_g1)
    verified = sum(1 for c in non_g1 for pid in c.get("parent_ids", []) if pid in id_set)
    lineage_pct = round(verified / total_links * 100.0, 2) if total_links > 0 else 100.0

    r3 = reports[-1]
    result = {
        "domain": domain["name"],
        "description": domain["description"],
        "event_count": mem.count(),
        "cycles_to_g2_composite": cycles_to_composite,
        "cycle3": {
            "concepts": len(r3.concepts),
            "processes": len(r3.processes),
            "workflow_concepts": len(r3.workflow_concepts),
            "hypotheses": len(r3.hypotheses),
            "theories": len(r3.theories),
            "questions": len(r3.questions),
            "dreams": len(r3.dreams),
            "investigations": len(r3.investigations),
            "experiments": len(r3.experiments),
        },
        "peak_question_uncertainty": round(peak_uncertainty, 4),
        "peak_experiment_priority": round(peak_priority, 4),
        "lineage_integrity_pct": lineage_pct,
        "total_sleep_runtime_ms": total_ms,
    }

    mem.close()
    if db.exists():
        db.unlink()
    return result


def run_validation():
    print("=" * 65)
    print("PROJECT ORGANICA — PHASE F: CROSS-DOMAIN VALIDATION REPORT")
    print("=" * 65)

    results = []
    for domain in DOMAINS:
        print(f"\n  Running: {domain['name']}...")
        r = run_domain(domain)
        results.append(r)
        print(f"    G2 Composite: Cycle {r['cycles_to_g2_composite']}")
        print(f"    Cycle 3 -> Concepts:{r['cycle3']['concepts']}  "
              f"Procs:{r['cycle3']['processes']}  "
              f"Wfs:{r['cycle3']['workflow_concepts']}  "
              f"Hyps:{r['cycle3']['hypotheses']}  "
              f"Experiments:{r['cycle3']['experiments']}")
        print(f"    Lineage Integrity: {r['lineage_integrity_pct']}%  "
              f"Runtime: {r['total_sleep_runtime_ms']}ms")

    # Summary table
    print("\n" + "=" * 65)
    print("CROSS-DOMAIN EMERGENCE SUMMARY")
    print("=" * 65)
    print(f"{'Domain':<35} {'Wfs':>4} {'Hyps':>5} {'Lineage':>8} {'EXPs':>5}")
    print("-" * 65)
    all_pass = True
    for r in results:
        wfs = r["cycle3"]["workflow_concepts"]
        hyps = r["cycle3"]["hypotheses"]
        lin = r["lineage_integrity_pct"]
        exps = r["cycle3"]["experiments"]
        status = "PASS" if (wfs > 0 or hyps > 0) and lin == 100.0 else "FAIL"
        if status == "✗":
            all_pass = False
        print(f"{status} {r['domain']:<33} {wfs:>4} {hyps:>5} {lin:>7}% {exps:>5}")

    print("=" * 65)
    print("ALL DOMAINS PASSED" if all_pass else "ONE OR MORE DOMAINS FAILED")

    # Write report
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": "F",
        "title": "Cross-Domain Developmental Emergence Validation",
        "result": "PASS" if all_pass else "FAIL",
        "domains": results,
    }
    out = Path(__file__).parent.parent / "docs" / "validation_report.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nFull report written to: {out}")
    return all_pass


if __name__ == "__main__":
    ok = run_validation()
    sys.exit(0 if ok else 1)
