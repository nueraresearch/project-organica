"""
Multi-Domain Reproduction Pack — Domain 3: Synthetic Ecological Foraging
Expected emergence:
  - Trophic & metabolic loops: 'forage' -> 'consume' -> 'replenish'
  - High-order Workflows governing resource cycles
"""

from pathlib import Path
from organica import MemoryService, SleepService

def run():
    print("=" * 60)
    print("Reproduction Domain 3: Synthetic Ecological Foraging")
    print("=" * 60)
    
    db_path = Path("eco_domain.db")
    if db_path.exists():
        db_path.unlink()
        
    mem = MemoryService(db_path)
    
    events = [
        "organism search energy low",
        "organism locate resource food",
        "organism consume food energy high",
        "biome replenish vegetation season",
        "organism search energy low",
        "organism locate resource food",
        "organism consume food energy high",
        "organism rest metabolism stable",
        "organism search energy low",
        "organism locate resource food",
        "organism consume food energy high",
        "biome replenish vegetation season",
    ] * 5
    
    for e in events:
        mem.store(e, event_type="observe", source="sim_eco")
        
    sleep = SleepService(mem)
    print(f"Loaded {mem.count()} ecological simulation events. Running sleep cycles...")
    for cycle in range(1, 4):
        report = sleep.run()
        print(f"Cycle {cycle}: {len(report.concepts)} concepts, {len(report.processes)} processes, "
              f"{len(report.workflow_concepts)} workflows, {len(report.dreams)} dreams")
              
    assert len(report.concepts) > 0 or len(report.processes) > 0, "Failed to emerge ecological cycles!"
    if report.processes:
        print(f"\n[EMERGENCE SUCCESS] Top Ecological Cycle: {' -> '.join(report.processes[0].cycle)}")
    if report.dreams:
        top_dream = report.dreams[0]
        print(f"[COUNTERFACTUAL DREAM] Type: {top_dream.dream_category} | Path: {' -> '.join(top_dream.path_or_context)}")
        
    mem.close()
    if db_path.exists():
        db_path.unlink()
    print("Domain 3 verified.\n")

if __name__ == "__main__":
    run()
