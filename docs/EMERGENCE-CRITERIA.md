# Emergence Criteria for Project Organica

**Purpose:** a precise, falsifiable definition of emergence for this project — what counts, what does not, and what the codebase can and cannot currently evidence.

**Status:** 2026-10-21. Companion to `docs/ABLATION-PREREGISTRATION.md` (which measures *which mechanisms matter*) and `research-journal/phase_g_findings_20261021.md` (which records what went wrong in the first run).

---

## 1. The definition

> **Emergence is not "the system did something interesting."**
>
> **Emergence is "the system produced a useful structure that was not explicitly encoded by the designer."**

Three clauses, each of which must hold:

1. **Not explicitly encoded.** The structure must not be a restatement of something the programmer wrote down. This is the clause that does the work; everything else is decoration around it.
2. **Useful.** It must change what the system does next. A structure nobody consults is not cognition, however elegant.
3. **Derived.** It must trace back to raw experience. A structure that appears from nowhere is not emergence either — it is noise with lineage.

The operational test used throughout this project:

> A structure the designer did **not** encode, traceable to raw experience, that **changes what the system does next**.

That third clause is why Law II (lineage) is not optional bookkeeping. An emergence claim without provenance is unfalsifiable: you cannot distinguish "it learned this" from "the programmer put this in and it found it again."

---

## 2. The ladder

Each level is strictly harder to fake. A system at Level 2 has not thereby demonstrated Level 3.

### Level 0 — Compression Emergence

*Can the system find recurring regularities that were never declared?*

- **Operational test:** feed events with no declared structure; count the regularities the system extracts on its own.
- **Metric:** number of discovered regularities; prediction accuracy (PA).
- **Organica status: EVIDENCED.** Layer 1 concepts, predictions and loops are built from co-occurrence and temporal edges with no declared pattern list (`organica/sleep.py:870`, `:989`, `:1052`). The cold-start ablation confirms these appear from an unengineered stream with no seeding: `docs/cold_start.json`, condition `real_git_history` — G1 concepts at cycle 5, predictions at cycle 5, loops at cycle 13.
- **What this does not prove:** pattern extraction, not intelligence. This is the weakest form of emergence and it is easy to achieve.

### Level 1 — Transfer Emergence

*Does knowledge learned in one area improve performance in another?*

- **Operational test:** train on domain A, evaluate on domain B; compare against training on B alone.
- **Metric:** CDT (Cross-Domain Transfer).
- **Organica status: MEASURED, NOT SATISFIED.** The four reproduction domains exist and `cross_domain_validation.py` runs, but CDT as a *transfer delta* has now been computed for the first time as part of the ablation study: it is **negative**, and the mean shared vocabulary between domain pairs is **0.17 tags**. The organism's substrate is lexical co-occurrence, so it has no representation that could carry across a vocabulary boundary. A human transfers "an agent acts on an environment" from kitchens to robots; Organica cannot, because "kitchen" and "robot" share no tags and no structure above the tag.
- **Why this matters:** this is the sharpest available evidence that the current architecture is a knowledge-compression engine rather than a general learner. It does not invalidate the project — it locates the gap precisely.

### Level 2 — Novel Concept Emergence

*Does the system create structures whose topology never existed before?*

- **Operational test:** a new node is novel only if its exact canonical topology has never appeared in the graph at any earlier cycle.
- **Metric:** NSR (Novel Structure Rate), plus a lineage proof of derivation from experience.
- **Organica status: MEASURED.** NSR is implemented (`benchmarks/ablation_metrics.py:canonical_signature`) and computed for every ablation condition. The designer-supervision half — a human judging whether a structure is *meaningfully* new, not merely topologically new — is **not yet collected**. Topological novelty is the weaker half: a random generator produces novelty at 100%.

### Level 3 — Surprise Emergence

*Did the system produce something the designer did not anticipate?*

- **Operational test:** the designer records, before a run, what they expect the organism to produce. Afterwards, the outputs are classified as expected / unexpectedly useful / unexpectedly useless.
- **Metric:** DSI = UnexpectedUseful / AllUnexpected; DPF = UnexpectedUseful / ExpectedStructures.
- **Organica status: INSTRUMENT PROVIDED, MEASUREMENT PENDING THE OWNER'S PROTOCOL.** This is the level the owner most cares about, and it is the only fully objective emergence measure in the suite — because "did I anticipate this?" is a question only a human can answer about their own expectations. It **cannot** be automated: an automated surprise-predictor would be the same model that produced the output, so it would predict everything and score zero. The scoring code exists; the predictions have to be written by the owner before a run.
- **Note on the difference from Level 2:** a system can be novel every cycle and still be unsurprising, because randomness is novelty without meaning. Level 3 is what separates the two.

### Level 4 — Autonomous Question Emergence

*Does the system ask questions whose content is unexpected?*

- **Operational test:** questions are not the mechanical result of a threshold rule; their specific content is something the designer did not foresee.
- **Metric:** count of unique investigable questions, plus human novelty ratings.
- **Organica status: PARTIALLY EVIDENCED.** Questions are generated from the measured Shannon entropy of a *genuine* split belief — two competing expectations about one subject, with support and contradiction counts taken from the event stream (`organica/sleep.py:1470-1496`). The entropy is real and not asserted. But the question's *content* is a coalescing of expectations that already existed in the hypothesis layer, so the "unanticipated content" half is **not** evidenced. Level 3 remains the binding constraint on this level.

### Level 5 — Autonomous Experiment Emergence

*Does the system independently conclude that two theories disagree, decide it needs evidence, and propose a discriminating test?*

- **Operational test:** a probe is executed against the world and the belief's entropy is measured before and after.
- **Metric:** EVS (Experiment Value Score) = H_before − H_after in bits; HDS (Hypothesis Discrimination Score) = Σ |p_after − p_before|.
- **Organica status: NOT EVIDENCED — and not merely unmeasured.** Layer 8 produces well-formed experiment candidates with a real priority ordering (`organica/sleep.py:677-748`), and the candidate's payload names a real discriminating test vector. But **nothing executes a probe and nothing measures a belief delta**, so the claim is unproven in principle: no experiment has ever been run, and therefore no question has ever been closed. The study measures epistemic **tension**, not epistemic **resolution**.
- **This is the single largest gap in the project.** It is also the thing that would close the self-build loop — an organism that can run its own probes would generate its own branch points, and the engineered stream would stop being necessary. See `docs/USER-MANUAL.md` §7.2 decision #7.

### Level 6 — Ontological Emergence

*Does the system invent a category that is not in the ladder?*

- **Operational test:** a structure type that does not correspond to any Generation in the developmental ladder.
- **Metric:** none defined yet.
- **Organica status: NOT EVIDENCED, AND STRUCTURALLY EXCLUDED.** The ladder is fixed at G0–G8 by design, and Generation 9 (self-modeling) is locked until the study concludes. This is a deliberate choice, not an oversight — but it does mean the project cannot currently claim this level even in principle.

### Summary

| Level | Question | Metric | Organica |
|---|---|---|---|
| 0 | Finds undeclared regularities? | PA, regularity count | **Evidenced** |
| 1 | Knowledge transfers across domains? | CDT | **Measured — negative** |
| 2 | Creates never-seen topologies? | NSR | **Measured**; human half pending |
| 3 | Surprises the designer? | DSI / DPF | **Pending owner protocol** |
| 4 | Asks unexpected questions? | question novelty | **Partially evidenced** |
| 5 | Runs its own discriminating tests? | EVS, HDS | **Not evidenced** |
| 6 | Invents a new primitive? | — | **Structurally excluded** |

---

## 3. What is built in, and what emerges

This section exists because the project's vision text can be read as claiming something stronger than the code does, and because the honest version is more defensible than the strong one.

### 3.1 How does the organism recognise language? It does not.

The direct answer to the question *"how does it recognise language, or even know what language is, without being taught?"*:

**It doesn't. It never forms a representation of language as such.** There is no grammar, no lexicon, no parser, no tokeniser with linguistic knowledge, no embedding, and no model of what a word means. What it has is a lexical filter:

```python
# organica/memory.py:443-452
def _extract_tags(content: str) -> list[str]:
    words = re.findall(r"\b[a-zA-Z]{4,}\b", content.lower())
    stopwords = {
        "this", "that", "with", "from", "have", "been", "will", "were",
        "they", "them", "then", "than", "when", "what", "which", "there",
        "their", "would", "could", "should", "about", "some", "more",
        "also", "just", "like", "into", "over", "after", "before",
        "test", "file",  # too generic for a dev env — we'll revisit this
    }
    ...
```

The behaviour this produces, precisely:

- Words are lowercased and matched against `[a-zA-Z]{4,}` — **four or more alphabetic characters**.
- Words shorter than four characters are **invisible**. "cat", "dog", "run", "ok" never become tags. Neither do digits, punctuation, or any non-ASCII character.
- No stemming, lemmatisation, or disambiguation. Two different senses of the same string collapse into one tag.
- The stopword list is **hand-coded**, and includes `"test"` and `"file"` with the in-code comment *"too generic for a dev env — we'll revisit this"* — a domain decision baked into the substrate, and one the cold-start ablation already measured the cost of (`docs/cold_start.json`, condition `no_dev_stopwords`).
- Tags are de-duplicated per event and capped at **8 per event**.

So the organism's atoms are predefined. It is handed a bag of ≥4-character alphabetic tokens and never learns that they are language.

### 3.2 The honest inventory

**Built in (specified by the designer, fixed in code):**

| Built-in | Where |
|---|---|
| The developmental ladder itself (G0–G8) | `docs/developmental-ladder.md` |
| Tag extraction: 4+ char alphabetic tokens, minus a hard-coded stopword list, capped at 8 | `organica/memory.py:443` |
| Co-occurrence edges: every pair of tags in an event | `organica/memory.py:243` |
| Temporal edges: tags within a 3-event lookback | `organica/memory.py:258` |
| Concept-vs-phrase classification thresholds | `organica/sleep.py:322-330` |
| The death threshold (0.15) and the reinforcement/decay schedule | `organica/sleep.py:1506` |
| The confidence formula `support / (support + contradiction)` | `organica/sleep.py:1402` |
| The EIG attention rule `uncertainty × (1 + novelty)` | `organica/sleep.py:609` |
| Four dream categories with fixed novelty values | `organica/sleep.py:488` |
| Per-generation caps (15 hypotheses, 8 theories, 6 questions, 8 dreams, 5 investigations, 5 experiments) | `organica/sleep.py:336-340` |

**Claimed to emerge (and what the evidence actually supports):**

| Emergent | Evidence | Status |
|---|---|---|
| Co-occurrence and temporal graph | built at ingest, not declared | Emerges trivially |
| Concepts, phrases, loops, predictions | from the graph, no declared pattern list | **Evidenced** (Level 0) |
| Meta-concepts, processes, workflows | from stable Layer-1 candidates | Emerges; quality unclear |
| Hypotheses | from workflow/process components, tested against the temporal graph | Emerges |
| Theories and Questions | from ≥2 competing hypotheses about one subject | Emerges **only when the stream is engineered to branch** (cold-start finding) |
| Dreams | four categories generated from questions and workflows | Emerges; NSR contribution measured |
| Investigations and Experiments | EIG-ranked from questions and dreams | Emerges as **candidates**; nothing executes them (Level 5 gap) |

### 3.3 The defensible claim

The project's vision text says the organism contains *"zero pre-trained neural networks and zero hard-coded natural language rules."* That is true — but it is weaker than it sounds, and it can be misread as "nothing cognitive is hard-coded." It is not.

The accurate position:

> **We hard-code developmental mechanisms and no domain-specific cognitive content.** There is no pretrained knowledge and no grammar, vocabulary, or parsing rules. What emerges is the *knowledge structure* — which concepts, which sequences, which expectations, which questions — within mechanisms that were specified in advance.

This is the same position modern developmental psychology takes about human infants: an infant arrives with an enormous amount of built-in machinery (pattern detection, object permanence tendencies, attention systems, curiosity drives, reward systems) and learns essentially all *content*. A baby does not know English; it is equipped to make English learnable. Organica is equipped to make structure learnable from events, and it does not know anything until events tell it.

**It is important to be clear that the built-in machinery above is not "nothing".** The developmental ladder is a substantial architectural bet. It encodes a theory of what cognitive development looks like — memory first, then structure, then hypotheses, then tension, then inquiry. If that theory is wrong, the organism will still produce a graph, and the graph will not be intelligence. That is exactly what the ablation study is designed to test.

---

## 4. Falsification checklist

Any claim of emergence in this project must survive all five checks. The current column states where the project stands.

| # | Check | Fails if | Status |
|---|---|---|---|
| 1 | **Lineage** — the structure's ancestry resolves to a Generation 0 experience event | LC < 1.0 for surviving structures | **Passing** (LC = 1.0 in the live run) |
| 2 | **Ablation** — the structure still appears when the mechanism supposedly responsible is removed | a layer contributes nothing to it | **Being measured** now; see `docs/ABLATION-PREREGISTRATION.md` |
| 3 | **Non-anticipation** — the designer did not predict the structure beforehand | DPF / DSI shows no unexpected-useful output | **Pending owner protocol** |
| 4 | **Unengineered stimulus** — the structure appears without a hand-designed branch point | it only appears when the stream is engineered | **Partially failing**: G5 requires an engineered branch point (cold-start finding) |
| 5 | **Held-out measurement** — the metric is computed on data the structure was not built from | the metric is computed on the training events | **Passing** for PA in the ablation study (16 of 48 events never ingested) |

Check 4 is the one that currently fails, and it fails in an informative way: it is not that the organism cannot hold two beliefs, it is that the *confidence formula* makes a minority belief impossible to hold (`organica/sleep.py:1402`). The remedy is a Laplace/Beta-smoothed posterior instead of a share — simpler, and it makes the lookback width irrelevant. That is a proposal under the Phase A freeze, not an applied change.

---

## 5. How to falsify this document

This document makes falsifiable claims. These would show it wrong:

- **If NSR collapses toward zero** across a long run, the organism is a pure compressor with no structural novelty, and Level 2 fails.
- **If CDT is exactly zero across many domain pairs** (rather than negative), there is no transfer mechanism at all and no reusable abstraction — worse than the negative result, which at least means the transfer attempt cost something.
- **If an ablation produces no measurable change in any metric** for a layer the architecture treats as foundational — sleep, falsification, curiosity — then that layer is ornament, and the developmental ladder is decorative.
- **If Random Curiosity performs like EIG curiosity** (ablation H), then the attention economy — one of the project's six design laws — is not pulling its weight, and Law V is a slogan.
- **If the Designer Surprise Index stays near zero** across a genuine protocol, then the organism is reflecting the designer's assumptions back, and the project's central claim does not survive contact with its own author.
- **If the built-in machinery list in §3.2 is wrong** — that is, if any item listed there is in fact emergent, or any item omitted is in fact hard-coded — then the claim in §3.3 is miscalibrated and the vision text's wording needs correcting further.

The point of writing these down is that they are the outcomes worth finding. A project that cannot be shown to be wrong has not been tested.
