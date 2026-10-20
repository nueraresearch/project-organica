# Project Organica Architecture

```
                    ┌──────────────────────────┐
                    │  Wake Experience Stream │ (Events)
                    └─────────────┬────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │      Memory Service      │
                    │  - Co-occurrence Graph   │
                    │  - Precedes Graph        │
                    └─────────────┬────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │      Sleep Service       │
                    │  (Transform & Select)    │
                    └─────────────┬────────────┘
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      ▼                           ▼                           ▼
┌─────────────┐             ┌─────────────┐             ┌─────────────┐
│ Generation 1│             │ Generation 2│             │ Generation 3│
│ Concepts    │             │ Processes   │             │ Workflows   │
│ Predictions │ ──────────> │ MetaConcepts│ ──────────> │             │
│ Loops       │             │             │             │             │
└─────────────┘             └─────────────┘             └──────┬──────┘
                                                               │
                                                               ▼
┌─────────────┐             ┌─────────────┐             ┌─────────────┐
│ Generation 6│             │ Generation 5│             │ Generation 4│
│ Dreams      │ <────────── │ Theories    │ <────────── │ Hypotheses  │
│ (Synthetic) │             │ Questions   │             │             │
└──────┬──────┘             └──────┬──────┘             └─────────────┘
       │                           │
       └─────────────┬─────────────┘
                     ▼
       ┌──────────────────────────┐
       │       Generation 7       │
       │  Investigation Agenda    │
       │    (Attention by EIG)    │
       └─────────────┬────────────┘
                     ▼
       ┌──────────────────────────┐
       │       Generation 8       │
       │   Active Experiments     │
       │ (Probing & Intervention) │
       └──────────────────────────┘
```

---

## Candidate Representation & Deterministic Identity
All nodes in Organica are pure Python dataclasses serializable to JSON. Every candidate carries:
- `id`: Deterministic hash derived from type prefix and sorted component keys.
- `generation`: Depth in the developmental ladder.
- `parent_ids`: Immutable lineage links to ancestor nodes.
- `confidence` / `uncertainty` / `strength`: Floating-point status metrics.
- `evidence`: Dictionary of verifiable counts, ratios, and observation timestamps.

## Natural Selection & Extinction Engine
During every sleep cycle:
1. **Reinforcement**: Rediscovered candidates receive an additive boost ($+0.05$).
2. **Decay**: Unconfirmed candidates decay exponentially ($\times 0.8$ per sleep cycle).
3. **Extinction**: Candidates falling below `DEATH_THRESHOLD` ($0.15$) are pruned permanently from the active memory graph.
