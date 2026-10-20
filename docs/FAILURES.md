# Project Organica: Chronicle of Failures & Architectural Regressions

*To truly understand why an architecture works, one must understand how it failed. This document chronicles the critical failures encountered during the development of Project Organica and the constitutional rules created to prevent their recurrence.*

---

## 1. The Self-Contamination Crisis (Cycle 3 Feedback Catastrophe)

### The Symptom
By Sleep Cycle 3, when running on developer workflow traces, the top concept candidate emerged as:
`['confidence', 'evidence', 'generation', 'type']` with an edge count exceeding all empirical events combined.

### The Root Cause
When candidates were generated during sleep, the service saved them back to `memory.db` using the standard `store(json.dumps(candidate))` method. The memory service treated these events as raw observations, parsed their word tokens, and updated the `cooccurrences` and `precedes` tables. The organism entered an uncontrollable recursive feedback loop, consolidating patterns on its own JSON schema fields rather than on reality.

### The Fix (Law III: Cognitive Isolation)
We introduced explicit event typing (`event_type="sleep"` vs `event_type="observe"`). The memory engine was modified so that graph edges are calculated strictly on `event_type != "sleep"`. Internal consolidation and dream structures are persisted for ancestry traversal but quarantined from empirical graph mechanics.

---

## 2. The Combinatorial Cycle Explosion

### The Symptom
During early experiments with Process discovery (finding closed cycles $A \rightarrow B \rightarrow A$ and $A \rightarrow B \rightarrow C \rightarrow A$), graph traversal routines attempted to search for arbitrary $N$-length cycles up to depth 6. With a moderately connected graph of 80 tags, the cycle finder hung indefinitely, consuming gigabytes of memory and generating thousands of trivial permutations of the same circular path.

### The Root Cause
Treating cycle detection as generic graph path-finding without topological boundaries or strength thresholds.

### The Fix
We enforced a hard cap on cycle lengths ($L \in \{2, 3\}$) and required that every participating edge satisfy a strict minimum temporal strength threshold (`LOOP_MIN_STRENGTH >= 5`). Furthermore, cycles were canonicalized into sorted tuples before deduplication, collapsing symmetric cycles into a single deterministic candidate ID.

---

## 3. The Broken Lineage Bug

### The Symptom
During an audit of Generation 3 Workflow candidates, several workflow nodes reported parent IDs that did not exist in the candidate registry or pointed to stale candidates that had decayed out of memory.

### The Root Cause
Candidate IDs were initially generated using non-deterministic UUIDs. When a candidate was re-evaluated or decayed across cycles, its ID changed, severing the ancestral graph.

### The Fix (Law II: Deterministic Hashing)
All candidate IDs were converted to deterministic MD5 hashes computed from their semantic components:
$$\text{ID} = \text{MD5}(\text{type} + \text{sorted\_members})$$
Parent IDs became permanent, immutable references that persist reliably across sleep cycles, consolidation passes, and database migrations.

---

## 4. The Majority Class Hallucination (Confidence Stagnation)

### The Symptom
When testing early curiosity systems, the agent was tasked with picking an investigation target. It repeatedly selected hypotheses that had already been observed hundreds of times with 98% confidence (e.g. `test` $\rightarrow$ `run`), completely ignoring rare, contradictory, or fragile hypotheses.

### The Root Cause
Using raw confidence or raw frequency as an importance metric. High-confidence assertions are comfortable, but they provide zero new structural information to an evolving mind.

### The Fix (Law V: Expected Information Gain)
We replaced confidence-based ranking with **Expected Information Gain (EIG)** based on Shannon entropy over competing expectations. A hypothesis with 99% confidence yields an EIG near zero; two co-existing hypotheses in direct 50/50 contradiction yield peak uncertainty ($1.0$) and maximum experimental priority.
