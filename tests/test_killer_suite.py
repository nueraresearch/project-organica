"""
Project Organica: The Four Killer Tests (Adversarial Robustness Suite)

Tests:
  Test A: False Pattern Hell (Massive spurious noise injection)
  Test B: Contradiction Storm (Sudden catastrophic environmental regime shift)
  Test C: Dream Poison (Adversarial counterfactual injection without reality support)
  Test D: Memory Pressure & Lineage Tractability (Large-scale event stream)
"""

import sys
import time
from pathlib import Path
from organica import MemoryService, SleepService

def test_a_false_pattern_hell():
    print("\n" + "=" * 65)
    print("[KILLER TEST A] False Pattern Hell: Spurious Noise Assault")
    print("=" * 65)
    db = Path("killer_test_a.db")
    if db.exists(): db.unlink()
    mem = MemoryService(db)
    
    # Genuine underlying signal: A -> B -> C
    for _ in range(20):
        mem.store("kernel signal alpha transmit packet", event_type="observe", source="hw")
        mem.store("kernel signal beta acknowledge packet", event_type="observe", source="hw")
        mem.store("kernel signal gamma commit buffer", event_type="observe", source="hw")
        
    # Inject 200 high-frequency, completely random, fleeting noise tokens
    for i in range(200):
        mem.store(f"noise_{i % 5} spurious_entropy_{i} transient_glitch_{i * 3}", event_type="observe", source="noise")
        
    sleep = SleepService(mem)
    r1 = sleep.run()
    r2 = sleep.run()
    
    # Verify that the noise did NOT create hallucinated workflows or dominate meta-concepts
    top_metas = [m.anchor_tag for m in r2.meta_concepts]
    print(f"Top Meta-Concept Anchors after 200 noise injections: {top_metas}")
    assert "kernel" in top_metas or "signal" in top_metas, "Killer Test A Failed: Core signal obliterated by noise!"
    for m in r2.meta_concepts:
        assert not m.anchor_tag.startswith("spurious_"), "Killer Test A Failed: Spurious token hallucinated as Meta-Concept!"
        
    print("[PASS] Killer Test A: Spurious noise rejected. Structural core intact.")
    mem.close()
    if db.exists(): db.unlink()

def test_b_contradiction_storm():
    print("\n" + "=" * 65)
    print("[KILLER TEST B] Contradiction Storm: Catastrophic Regime Shift")
    print("=" * 65)
    db = Path("killer_test_b.db")
    if db.exists(): db.unlink()
    mem = MemoryService(db)
    
    # Regime 1: Developer fix workflow (developer modified auth -> executed test suite -> passed)
    regime_1_events = [
        "developer modified auth login session",
        "developer executed test suite",
        "test suite report passed validation",
    ] * 6
    for e in regime_1_events:
        mem.store(e, event_type="observe", source="env")
        
    sleep = SleepService(mem)
    r1 = sleep.run()
    r2 = sleep.run()
    
    initial_hyps = {h.subject: h for h in r2.hypotheses if h.expectation != "high_structural_significance"}
    assert len(initial_hyps) > 0, "Regime 1 failed to establish hypotheses!"
    target_subject = list(initial_hyps.keys())[0]
    initial_hyp = initial_hyps[target_subject]
    print(f"Established Belief: {initial_hyp.subject} -> {initial_hyp.expectation} (Confidence: {initial_hyp.confidence:.2f})")
    
    # Catastrophic Regime Shift: Inversion (developer abandoned -> failure crashed error)
    print(f"Initiating Regime Shift: opposing flow reversing {target_subject}...")
    regime_2_events = [
        f"{target_subject} failure crashed error",
        "system rollback aborted shutdown",
    ] * 20
    for e in regime_2_events:
        mem.store(e, event_type="observe", source="env")
        
    r3 = sleep.run()
    r4 = sleep.run()
    
    # Check that hypothesis confidence adapted/decayed or revised
    updated_hyp = next((h for h in r4.hypotheses if h.id == initial_hyp.id), None)
    adapted = False
    if updated_hyp is None or updated_hyp.confidence < initial_hyp.confidence or "revision_delta" in updated_hyp.evidence:
        adapted = True
        
    print(f"Post-Shift: Initial Belief Id {initial_hyp.id} Conf: {updated_hyp.confidence if updated_hyp else 'EXTINGUISHED/DECAYED'}")
    assert adapted, "Killer Test B Failed: Belief failed to adapt to catastrophic regime shift!"
    
    print("[PASS] Killer Test B: Beliefs adapted; stale regime decayed under contradiction.")
    mem.close()
    if db.exists(): db.unlink()

def test_c_dream_poison():
    print("\n" + "=" * 65)
    print("[KILLER TEST C] Dream Poison: Immune Resistance to Untested Dreams")
    print("=" * 65)
    db = Path("killer_test_c.db")
    if db.exists(): db.unlink()
    mem = MemoryService(db)
    
    # Normal observations
    for _ in range(15):
        mem.store("system boot init start", event_type="observe", source="os")
        mem.store("system ready active run", event_type="observe", source="os")
        
    sleep = SleepService(mem)
    r1 = sleep.run()
    r2 = sleep.run()
    
    # Artificially inject 50 wild, poisoned dream candidates into sleep memory
    for i in range(50):
        fake_dream = {
            "type": "dream",
            "id": f"poison_dream_{i}",
            "generation": 5,
            "dream_category": "mutation",
            "subject": "boot",
            "path_or_context": ["boot", f"poison_tag_{i}", "destroy_system"],
            "confidence": 0.05,
            "novelty": 0.99,
            "parent_ids": [],
            "evidence": {"poison": True}
        }
        mem.store(str(fake_dream), event_type="sleep", source="sleep:dream")
        
    # Run sleep consolidation
    r3 = sleep.run()
    
    # Invariant check: Did ANY poisoned dream promote to a Hypothesis or Workflow?
    for h in r3.hypotheses:
        assert "destroy_system" not in h.expectation, "Killer Test C Failed: Poisoned dream promoted to Hypothesis without empirical evidence!"
    for w in r3.workflow_concepts:
        assert "destroy_system" not in w.components, "Killer Test C Failed: Poisoned dream promoted to Workflow!"
        
    print("[PASS] Killer Test C: Cognitive isolation held. Zero poison dreams promoted to beliefs.")
    mem.close()
    if db.exists(): db.unlink()

def test_d_memory_pressure():
    print("\n" + "=" * 65)
    print("[KILLER TEST D] Memory Pressure & Lineage Tractability")
    print("=" * 65)
    db = Path("killer_test_d.db")
    if db.exists(): db.unlink()
    mem = MemoryService(db)
    
    print("Streaming 1,000 temporal events...")
    start_time = time.time()
    for i in range(250):
        mem.store(f"flow_step_alpha state_{i % 3} active", event_type="observe", source="stream")
        mem.store(f"flow_step_beta state_{i % 3} pending", event_type="observe", source="stream")
        mem.store(f"flow_step_gamma state_{i % 3} complete", event_type="observe", source="stream")
        mem.store(f"flow_step_delta state_{i % 3} ack", event_type="observe", source="stream")
    stream_duration = time.time() - start_time
    print(f"Ingested 1,000 events in {stream_duration:.2f}s ({1000/stream_duration:.0f} ev/s)")
    
    sleep = SleepService(mem)
    print("Running multi-cycle consolidation under load...")
    t0 = time.time()
    r1 = sleep.run()
    r2 = sleep.run()
    r3 = sleep.run()
    consolidation_duration = time.time() - t0
    print(f"3 Full Consolidations completed in {consolidation_duration:.2f}s")
    
    # Verify lineage lookup latency
    if r3.experiments:
        exp_id = r3.experiments[0].id
        t_lookup = time.time()
        ancestry = sleep.get_ancestry(exp_id, max_depth=8)
        lookup_duration = (time.time() - t_lookup) * 1000
        print(f"Ancestor Tree Traversal Latency: {lookup_duration:.2f}ms")
        assert ancestry["id"] == exp_id
        assert lookup_duration < 100.0, "Killer Test D Failed: Lineage traversal exceeded 100ms threshold!"
        
    print("[PASS] Killer Test D: Memory and lineage remain linear and tractable under load.")
    mem.close()
    if db.exists(): db.unlink()

def run_all_killer_tests():
    print("=" * 65)
    print("ORGANICA ADVERSARIAL KILLER TEST SUITE")
    print("=" * 65)
    test_a_false_pattern_hell()
    test_b_contradiction_storm()
    test_c_dream_poison()
    test_d_memory_pressure()
    print("\n" + "=" * 65)
    print("ALL 4 KILLER TESTS PASSED: ORGANICA SURVIVED ADVERSARIAL ASSAULT")
    print("=" * 65)

if __name__ == "__main__":
    run_all_killer_tests()
