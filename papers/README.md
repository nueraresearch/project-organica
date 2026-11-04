# Manuscript status

**Inventory: seven manuscript files; zero published.** The manifesto lists four original agenda papers (files 01–04). File 00 is the philosophical framing; files 05–06 are later manuscript concepts. Drafted does not mean peer reviewed, submitted, or publication-ready.

The manifesto's original agenda names four papers. `00` is a philosophical framing; `05` and `06` are later manuscript concepts. The four agenda manuscripts have been revised as evidence-aligned working drafts on 2026-10-27, and the two active manuscripts were brought to academic grade on 2026-10-30: **Paper 01 received its figures and its citations**, and **Paper 02 received both its citations and its figures**. Both citation sets were verified against primary records on 2026-10-30; see each paper's row below.

| Manuscript | Current status | Publication gate |
|---|---|---|
| [01 Developmental structure formation](01_developmental_structure_formation.md) | Empirical working draft — revised to academic grade 2026-10-29; **figures and citations supplied 2026-10-30** | **Narrow core question** ("can developmental structure emerge in Organica 1?") with the negative external-task results included as the boundaries of the answer; methods and results reconciled to the committed record. **Supplied 2026-10-30:** five figures, generated from the committed artifacts by `benchmarks/figure_papers.py`, each asserting its own values against its source; and citations — §4.1's curriculum-sensitivity framing and §5.4's four methodological lessons now carry inline `(Author, year)` markers and a **References** section with **seven** sources, each read against a primary record on 2026-10-30. One of the four lessons is this project's own rule and carries no external citation by design. **Result added 2026-11-02:** §4.10 reports the confirmed capacity-1,000 test — no improvement detected on held-out prediction (98.33% interval crossing zero), a withheld-relation advantage that the preregistered measure cannot attribute, and no transfer claim in either direction; figures read from `docs/functional_structure_confirmatory.json`. **Submission package built and checked 2026-11-02:** the manuscript renders to a **25-page PDF** with **0** LaTeX errors and **0** overfull boxes, all five figures are vector PDF, every number is checked by `tests/test_paper_numbers.py`, and every artifact it cites is present in the archived software tree — `python benchmarks/deposit_bundle.py --check` prints the count and fails on a missing artifact, which is why no count is repeated by hand here. Its checksums, manifests and reproduction bundle (archived commit, environment, commands, both PDFs) are **generated** into `.scratch/deposit/`, a gitignored scratch directory, so a reader confirms the package by rebuilding it rather than by looking for it: `python benchmarks/render_papers.py` (prerequisites are pandoc and a LaTeX toolchain, and it exits non-zero when pandoc is absent rather than writing nothing) then `python benchmarks/deposit_bundle.py`, and `pytest tests/test_deposit_bundle.py` rebuilds all four bundles from the rendered PDFs and verifies every manifest, checksum and cited artifact. **Revised again 2026-11-02 after a reviewer's report** (journal §129): §4.10 now describes the tuning split as the code implements it — fits for selection exclude it, the winning configuration is then refit on all 110 cycles, and the preregistration's §3 wording is disclosed as superseded by its §11.1; §4.4 states that the 3:1 crossing is a grid-level location (3:1 is the first sampled point above parity, the crossing lies between 2:1 and 3:1); §3.5 records Phase L's pre-outcome amendment to a 99% interval and labels the seed-exchangeability audit as post-outcome; §4.1 and §4.6 carry the compact study tables the review asked for; and all eight figure PDFs were regenerated, because Figure 1's went to press with six of its eight sweep points and three labels were clipped at the right edge. **Still open:** the upload itself — a Zenodo deposit mints a public DOI and is the owner's action. |
| [02 Structural provenance](02_persistent_structural_provenance.md) | Audit working draft — revised to academic grade 2026-10-29; **citations and figures supplied 2026-10-30** | Methods, results, populations and controls added; the stale A5/A6 passage resolved. **Supplied 2026-10-30:** §2 (Positioning) now carries inline citations and a five-source References section, every source read against a primary source and one candidate citation dropped as unverifiable; three figures generated from the committed artifacts. **Submission package built and checked 2026-11-02:** it renders to a **14-page PDF** with **0** LaTeX errors and **0** overfull boxes — the wide audit tables are set a size down in portrait rather than rotated onto landscape pages, which had cost an orphaned heading and two almost blank sheets — and it is bundled with its three vector figures, checksums and manifest. **Still open:** the upload. |
| [03 Curiosity through contradiction](03_curiosity_through_contradiction.md) | Hypothesis/evidence review | Needs a controlled mechanism intervention; no causal efficacy claim is established. |
| [04 Dream-driven exploration](04_dream_driven_structural_exploration.md) | Descriptive framework | Needs a matched no-dream evaluation with external outcomes and provenance analysis. |
| [00 Intelligence through structural descent](00_intelligence_through_structural_descent.md) | Philosophical framing — **audited against the code 2026-10-29** | **Audit complete:** two of the six architectural laws are contradicted by the implementation, one is untested on its own terms, one is contradicted in direction, and the manuscript's own factual errors are corrected. **Still open:** the recast into a position paper with literature engagement — an owner decision — and the Law II wording question. **Law II, owner ruling 2026-10-30:** keep the discrepancy disclosed and **defer the amendment** until it is settled whether the law is a design requirement or a description of V1's actual behavior; rewriting it to match the frozen engine would erase the distinction that makes the discrepancy meaningful. |
| [05 Cognitive isolation principle](05_cognitive_isolation_principle.md) | Historical hypothesis manuscript | Verify the incident and isolation claims against primary artifacts; remove unproved infinite-horizon guarantees. |
| [06 Ecology of beliefs](06_the_ecology_of_beliefs.md) | Historical hypothesis manuscript | Reconcile lifecycle and decay claims to the frozen engine and results; do not present unverified constants as findings. |

**Papers 01 and 02 have completed submission packages; the other five drafts do not.** Every draft intentionally narrows its claims; none adds experiments or changes a preregistration. For 01 and 02 the package is built and checked — rendered, numbers guarded, every cited artifact present — and the only open item is the owner's upload. Papers 00, 03, 04, 05 and 06 still stand behind the gates in the table above.

**The next milestone is the deposit of Papers 01 and 02** — the upload, which mints a public DOI and is the owner's action alone. The inventory still reads seven manuscript files and zero published, and it will keep reading that until a DOI exists: *ready to deposit* is a property of a package, not of the inventory.

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
| An advantage on held-out prediction at capacity 1,000 | **Not established**; the pooled margin crossed zero (no improvement detected), 15 confirmatory seeds, one run (Paper 01 §4.10) |
| Transfer on relations withheld from formation | **Not established**; the score improved and the preregistered provenance measure returned *not attributable*, so no transfer claim is made either way (Paper 01 §4.10) |
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
