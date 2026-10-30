# Manuscript status

**Inventory: seven manuscript files; zero published.** The manifesto lists four original agenda papers (files 01–04). File 00 is the philosophical framing; files 05–06 are later manuscript concepts. Drafted does not mean peer reviewed, submitted, or publication-ready.

The manifesto's original agenda names four papers. `00` is a philosophical framing; `05` and `06` are later manuscript concepts. The four agenda manuscripts have been revised as evidence-aligned working drafts on 2026-10-27, and the two active manuscripts were brought to academic grade on 2026-10-30: **Paper 01 received its figures and its citations**, and **Paper 02 received both its citations and its figures**. Both citation sets were verified against primary records on 2026-10-30; see each paper's row below.

| Manuscript | Current status | Publication gate |
|---|---|---|
| [01 Developmental structure formation](01_developmental_structure_formation.md) | Empirical working draft — revised to academic grade 2026-10-29; **figures and citations supplied 2026-10-30** | **Narrow core question** ("can developmental structure emerge in Organica 1?") with the negative external-task results included as the boundaries of the answer; methods and results reconciled to the committed record. **Supplied 2026-10-30:** five figures, generated from the committed artifacts by `benchmarks/figure_papers.py`, each asserting its own values against its source; and citations — §4.1's curriculum-sensitivity framing and §5.4's four methodological lessons now carry inline `(Author, year)` markers and a **References** section with **seven** sources, each read against a primary record on 2026-10-30. One of the four lessons is this project's own rule and carries no external citation by design. **Still open:** submission preparation — the manuscript is not submitted. |
| [02 Structural provenance](02_persistent_structural_provenance.md) | Audit working draft — revised to academic grade 2026-10-29; **citations and figures supplied 2026-10-30** | Methods, results, populations and controls added; the stale A5/A6 passage resolved. **Supplied 2026-10-30:** §2 (Positioning) now carries inline citations and a five-source References section, every source read against a primary source and one candidate citation dropped as unverifiable; three figures generated from the committed artifacts. **Still open:** submission preparation — the manuscript is not submitted. |
| [03 Curiosity through contradiction](03_curiosity_through_contradiction.md) | Hypothesis/evidence review | Needs a controlled mechanism intervention; no causal efficacy claim is established. |
| [04 Dream-driven exploration](04_dream_driven_structural_exploration.md) | Descriptive framework | Needs a matched no-dream evaluation with external outcomes and provenance analysis. |
| [00 Intelligence through structural descent](00_intelligence_through_structural_descent.md) | Philosophical framing — **audited against the code 2026-10-29** | **Audit complete:** two of the six architectural laws are contradicted by the implementation, one is untested on its own terms, one is contradicted in direction, and the manuscript's own factual errors are corrected. **Still open:** the recast into a position paper with literature engagement — an owner decision — and the Law II wording question. **Law II, owner ruling 2026-10-30:** keep the discrepancy disclosed and **defer the amendment** until it is settled whether the law is a design requirement or a description of V1's actual behavior; rewriting it to match the frozen engine would erase the distinction that makes the discrepancy meaningful. |
| [05 Cognitive isolation principle](05_cognitive_isolation_principle.md) | Historical hypothesis manuscript | Verify the incident and isolation claims against primary artifacts; remove unproved infinite-horizon guarantees. |
| [06 Ecology of beliefs](06_the_ecology_of_beliefs.md) | Historical hypothesis manuscript | Reconcile lifecycle and decay claims to the frozen engine and results; do not present unverified constants as findings. |

The revised drafts are not submission-ready. They intentionally narrow claims; they do not add new experiments or change preregistrations.

**The next milestone is to make the first two manuscripts submission-ready** — not to publish them as they stand.

## Two maps, kept side by side

**Research-program structure is not publication structure.** The layer map below orients a reader; it does not decide what gets published, and **not every item in the empirical layer is itself a paper**.

**Map 1 — the research program.** What the project contains, regardless of whether it is publishable:

| Layer | Content | Nature |
|---|---|---|
| **Theory** | the structural-descent framing and its alternative to the oracle metaphor (Paper 00); the engine's six architectural laws | position paper — not an empirical contribution |
| **Proposed mechanisms** | curiosity through contradiction (03), dream-driven exploration (04), the Gate 13 failure characterization (capacity, provenance separation, relation-level ranking) | hypotheses and analyses whose external efficacy is **not** established |
| **Empirical record** | Paper 01, Paper 02 — and, as **evidence sources rather than manuscripts**, the longitudinal study, Phase L, the audit-trace artifacts, the acquisition audits and the mechanism probes | the strongest evidence currently lives here |

**Map 2 — the publication map.** Which specific manuscript can make a coherent, evidence-backed contribution now:

1. **Paper 01**, revised as the empirical V1 account. **Core question: can developmental structure emerge in Organica 1?** Include the negative findings, the failed expectations and the boundaries. **Do not** fit the audit trace, Phase L, the capacity probes, the acquisition audits and every historical idea into one manuscript — give readers one question and answer it rigorously.
2. **Paper 02**, as a separate auditability paper. **Core question: can developmental decisions be reconstructed externally?** The answer is *partially, yes* — surviving state, **not** complete history and **not** unrestricted reconstruction. That nuance is what gives the paper its credibility.
3. **A theory/position paper from 00**, if one is wanted, after recasting it: original theory → predictions → what V1 supported → what V1 did not support → open questions. That version is much stronger than the original form.
4. **Keep 03 and 04 as hypotheses or reviews** until controlled mechanism-specific experiments test whether those mechanisms improve an external outcome. The current repository state does not support publishing them as empirical claims.
5. **Keep 05 and 06 out of the active submission queue** until they are substantially rewritten against the current engine and findings. **No claim in either is currently strengthened by recent work, and none should be described as if it were.** Specifically: **Paper 05's** strong isolation claim conflicts with the measured sleep-sourced relations in the temporal substrate (disclosed as D2; quantified in `docs/GATE13-RELATION-SEPARATION.md`), and **Paper 06's** major lifecycle, stability and lineage claims remain unverified against the current evidence. Paper 05 might instead become a paper about the **limits or failure** of cognitive isolation in Organica V1 — but that would be a **different paper**, not a revision.

## Claim-status vocabulary

Every claim is placed in one of **four** categories, not two. A claim that was **not established** is not a claim that was **refuted**, and **reversed** is a stronger statement than merely unsupported. **The scope is part of the status**: where the evidence splits, a compound status is required rather than a single word.

| Status | Meaning |
|---|---|
| **Supported within the tested scope** | evidence exists for the conditions tested |
| **Mixed / context-limited** | evidence varies by condition or interpretation; the restriction is part of the finding |
| **Reversed** | evidence points opposite the original prediction — and this does not establish that the opposite phenomenon never occurs |
| **Not established / not measured** | no valid conclusion yet; **this is not evidence of absence** |

Worked examples, in the wording the project uses:

| Claim | Status |
|---|---|
| Developmental structure forms and varies with experience | **Supported within the tested scope** |
| Phase L structural displacement occurs | **Measured; the protocol verdict `H3-L` remains inconclusive** |
| Organica performs belief revision better than simple baselines | **Reversed in Phase K's tested task**; this does not establish that no updating occurs |
| A continuous coherence–plasticity tradeoff | **Not established**; the preregistered Phase L verdict was inconclusive |
| Transfer | **No positive transfer demonstrated**; one measured cross-domain result was negative, while other forms remain untested |
| Human-like learning | **Not established** |
| Complete historical reconstruction | **Not demonstrated**; the trace is bounded to surviving state |

## What is *not* a manuscript here

The Phase L characterization, the V1 synthesis, the audit-trace artifacts and the Gate 13 investigation are **research records**. They may support future manuscripts, but they are not manuscripts in this directory, and the inventory above stays **seven files, zero published**.

Two facts constrain what those records can be made to say:

- The Phase L preregistered verdict remains **`H3-L — INCONCLUSIVE`**. The Phase L *characterization* is a separate artifact and does not re-score the verdict.
- The acquisition study **stopped before measuring transfer**. Transfer was reported as *not measurable*; it is **not** a transfer failure, and it is **not** a transfer success.

## House style

- **American English** (`behavior`, `program`, `analyze`, `center`).
- Claims are never wider than the check behind them, every rate is reported against a named population, and every claim carries one of the four statuses above with its scope named.
- "Independently auditable" means independently **reconstructed from the engine's state**, never independently **replicated** by another laboratory.
