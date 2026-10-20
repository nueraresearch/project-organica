"""
Multi-Domain Reproduction Pack — Domain 2: Bug Tracking System
Expected emergence:
  - Process: 'issue' -> 'commit' -> 'verified' -> 'closed'
  - Curiosity / Question: Competing expectations on issue resolution (e.g. 'reopened' vs 'closed')
"""

from pathlib import Path
from organica import MemoryService, SleepService

def run():
    print("=" * 60)
    print("Reproduction Domain 2: Bug Tracking System")
    print("=" * 60)
    
    db_path = Path("bug_domain.db")
    if db_path.exists():
        db_path.unlink()
        
    mem = MemoryService(db_path)
    
    events = [
        "user reported issue BUG-101",
        "triage assigned issue to engineer",
        "engineer committed patch commit-a1",
        "ci executed pipeline verified",
        "support agent closed issue BUG-101",
        "user reported issue BUG-102",
        "triage assigned issue to engineer",
        "engineer committed patch commit-b2",
        "ci executed pipeline failed",
        "engineer committed patch commit-b3",
        "ci executed pipeline verified",
        "support agent closed issue BUG-102",
        "user reported issue BUG-103",
        "triage assigned issue to engineer",
        "ci executed pipeline verified",
        "support agent closed issue BUG-103",
    ] * 4
    
    for e in events:
        mem.store(e, event_type="observe", source="jira")
        
    sleep = SleepService(mem)
    print(f"Loaded {mem.count()} bug lifecycle events. Running sleep cycles...")
    for cycle in range(1, 4):
        report = sleep.run()
        print(f"Cycle {cycle}: {len(report.meta_concepts)} metas, {len(report.processes)} processes, "
              f"{len(report.theories)} theories, {len(report.questions)} questions")
              
    assert len(report.meta_concepts) > 0 or len(report.processes) > 0, "Failed to emerge bug tracking primitives!"
    if report.meta_concepts:
        print(f"\n[EMERGENCE SUCCESS] Top Anchor: '{report.meta_concepts[0].anchor_tag}' with {report.meta_concepts[0].related_candidates} connections")
    if report.questions:
        print(f"[CURIOUS TENSION] Question: {report.questions[0].subject} -> {report.questions[0].competing_expectations}")
        
    mem.close()
    if db_path.exists():
        db_path.unlink()
    print("Domain 2 verified.\n")

if __name__ == "__main__":
    run()
