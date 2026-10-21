"""
Multi-Domain Reproduction Pack — Domain 3: Synthetic Ecological Foraging
Expected emergence:
  - Trophic & metabolic loops: 'forage' -> 'consume' -> 'replenish'
  - High-order Workflows governing resource cycles
"""

from pathlib import Path
import sys
from pathlib import Path

# Allow running this file directly from a fresh clone, with no install:
# walk up until we find the repository root, then make it importable.
_REPO_ROOT = Path(__file__).resolve()
while not (_REPO_ROOT / "pyproject.toml").exists() and _REPO_ROOT != _REPO_ROOT.parent:
    _REPO_ROOT = _REPO_ROOT.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from organica.paths import scratch_db
from organica import MemoryService, SleepService

def run():
    print("=" * 60)
    print("Reproduction Domain 3: Synthetic Ecological Foraging")
    print("=" * 60)
    
    db_path = scratch_db("eco_domain.db")
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
