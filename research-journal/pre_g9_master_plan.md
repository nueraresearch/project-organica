# Project Organica: Pre-G9 Master Execution Plan

> **Strategic Directive**: Freeze Generations 0–8 at v1.0. Do not implement Generation 9 (Self-Modeling) until the architecture is documented, reproduced across diverse external worlds, benchmarked on growth metrics, battle-tested for long-term endurance, and published to the scientific community.

---

```
                              ┌──────────────────────────────────────────────┐
                              │      PHASE A: Architecture Freeze (v1.0)     │
                              │   Freeze G0-G8 • Spec Invariants • Proofs   │
                              └──────────────────────┬───────────────────────┘
                                                     │
                      ┌──────────────────────────────┴──────────────────────────────┐
                      │                                                             │
         ┌────────────┴─────────────┐                                  ┌────────────┴─────────────┐
         │ PHASE B: Reproduction Pack│                                  │  PHASE C: Benchmark Suite │
         │ 4 Domain Real-World Packs│                                  │  5 Growth-Based Metrics  │
         └────────────┬─────────────┘                                  └────────────┬─────────────┘
                      │                                                             │
                      └──────────────────────────────┬──────────────────────────────┘
                                                     │
                                      ┌──────────────┴──────────────┐
                                      │  PHASE D: Research Papers   │
                                      │  5 Canonical Pre-prints     │
                                      └──────────────┬──────────────┘
                                                     │
                      ┌──────────────────────────────┴──────────────────────────────┐
                      │                                                             │
         ┌────────────┴─────────────┐                                  ┌────────────┴─────────────┐
         │  PHASE E: Community & OSS │                                  │  PHASE F: External Worlds │
         │  FAILURES.md • Roadmap   │                                  │  Robotics, FS, Web, Code │
         └────────────┬─────────────┘                                  └────────────┬─────────────┘
                      │                                                             │
                      └──────────────────────────────┬──────────────────────────────┘
                                                     │
                                      ┌──────────────┴──────────────┐
                                      │  PHASE G: Long-Term Soak    │
                                      │  Endurance (24h / 7d / 30d) │
                                      └──────────────┬──────────────┘
                                                     │
                                                     ▼
                                      ┌─────────────────────────────┐
                                      │    GENERATION 9: INTROSPECT │
                                      │       (Self-Modeling)       │
                                      └─────────────────────────────┘
```

---

## 1. Phase Breakdown & Deliverables

### Phase A: Architecture Freeze (v1.0)
- **Goal**: Lock cognitive primitives. Ensure no ad-hoc additions.
- **Deliverables**:
  - `docs/ARCHITECTURE.md` (Formal invariants, topological thresholds, data contracts).
  - Detailed per-generation specifications (`docs/generations/GEN_0.md` through `GEN_8.md`).
  - `docs/DESIGN_LAWS.md` (The 6 inviolable laws: induction, lineage, isolation, dreaming, EIG, selection).

### Phase B: Reproduction Pack (`examples/domains/`)
- **Goal**: Empower independent researchers to reproduce emergent phenomena in < 60 seconds without deep learning hardware.
- **Worlds Provided**:
  1. `01_developer_workflow.py` (`failure` $\rightarrow$ `modified` $\rightarrow$ `passed`).
  2. `02_bug_tracking.py` (`issue` $\rightarrow$ `reproduce` $\rightarrow$ `commit` $\rightarrow$ `resolved`).
  3. `03_synthetic_ecology.py` (Resource trophic levels and metabolic foraging loops).
  4. `04_robot_simulation.py` (Sensor-action-kinematic loops and collision avoidance).

### Phase C: Growth Benchmark Suite (`benchmarks/`)
- Standard ML benchmarks measure *static accuracy*. Organica benchmarks measure *developmental growth*:
  - **BM1: Signal Extraction**: Precision of graph topology vs. frequency baselines on noisy streams.
  - **BM2: Lineage Preservation**: Percentage of candidates tracing unbroken ancestry back to G0 (Target: 100.0%).
  - **BM3: Belief Adaptation**: Rate of hypothesis revision and confidence shifts during regime changes.
  - **BM4: Curiosity Resolution**: EIG predictive utility (does high EIG lead to maximum uncertainty reduction?).
  - **BM5: Dream Realization**: Percentage of counterfactual dreams validated by subsequent environmental experiments.

### Phase D: Research Papers (`papers/`)
- Draft 5 academic manuscripts:
  1. *Developmental Cognitive Architectures Through Structural Descent*
  2. *Persistent Structural Provenance in Continual Learning Systems*
  3. *Curiosity Through Contradiction: EIG-Driven Self-Supervised Inquiries*
  4. *Dream-Driven Structural Exploration: Counterfactual Search Without Delusion*
  5. *The Cognitive Isolation Principle: Preventing Runaway Feedback in Introspective Architectures*

### Phase E: Community & Open Source Infrastructure
- Public GitHub release files:
  - `CONTRIBUTING.md`, `ROADMAP.md`, `CITATION.cff`, `LICENSE` (Apache 2.0).
  - `FAILURES.md`: Frank chronicle of real failures (the self-contamination bug, combinatorial loop explosion, decaying confidence collapses).

### Phase F: Multi-Domain Validation & Phase G: Endurance Soak
- Continuous daemon testing: verifying stability, memory boundness, and candidate survival across extended runs.
