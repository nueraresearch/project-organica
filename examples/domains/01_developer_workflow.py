"""
Multi-Domain Reproduction Pack — Domain 1: Developer Workflow
Expected emergence:
  - Meta-Concept: 'failure' as a high-degree structural anchor
  - Process: 'failure' <-> 'modified'
  - Workflow: 'failure' -> 'modified' -> 'passed'
  - Hypothesis: 'suite' -> 'passed' vs 'suite' -> 'failure'
"""

import sys
from pathlib import Path
from organica import MemoryService, SleepService

def run():
    print("=" * 60)
    print("Reproduction Domain 1: Developer Workflow")
    print("=" * 60)
    
    db_path = Path("dev_domain.db")
    if db_path.exists():
        db_path.unlink()
        
    mem = MemoryService(db_path)
    
    events = [
        "developer modified auth/login.py",
        "developer executed test suite",
        "test suite report: 3 failures, 47 passed",
        "failure detected in session validation",
        "developer modified auth/session.py",
        "developer executed test suite",
        "test suite report: 0 failures, 50 passed",
        "developer modified api/router.py",
        "developer executed test suite",
        "test suite report: 1 failures, 49 passed",
        "failure detected in router endpoint",
        "developer modified api/router.py",
        "developer executed test suite",
        "test suite report: 0 failures, 50 passed",
    ] * 4  # Repeat stream to simulate continuous session
    
    for e in events:
        mem.store(e, event_type="observe", source="dev_env")
        
    sleep = SleepService(mem)
    
    # Run 3 consolidation cycles
    print(f"Loaded {mem.count()} events. Running 3 sleep cycles...")
    for cycle in range(1, 4):
        report = sleep.run()
        print(f"Cycle {cycle}: {len(report.concepts)} concepts, {len(report.processes)} processes, "
              f"{len(report.workflow_concepts)} workflows, {len(report.hypotheses)} hypotheses, "
              f"{len(report.experiments)} experiments")
              
    assert len(report.workflow_concepts) > 0, "Failed to emerge developer workflows!"
    top_wf = report.workflow_concepts[0]
    print(f"\n[EMERGENCE SUCCESS] Top Workflow: {top_wf.name} (Confidence: {top_wf.confidence})")
    print(f"Components: {top_wf.components}")
    
    if report.experiments:
        top_exp = report.experiments[0]
        print(f"[EXPERIMENT SELECTED] Action: {top_exp.action_type} (Priority: {top_exp.priority})")
        print(f"Payload: {top_exp.probe_payload}")
        
    mem.close()
    if db_path.exists():
        db_path.unlink()
    print("Domain 1 verified.\n")

if __name__ == "__main__":
    run()
