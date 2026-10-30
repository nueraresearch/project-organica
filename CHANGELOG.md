# Changelog

All notable changes to Project Organica are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning 2.0.0](https://semver.org/).

## Versioning in this repository — three separate namespaces

The words "v1" and "v2" appear in this project in three different senses.
They are deliberately distinct, and they are what the version number
*does not* refer to.

| Namespace | Form | Meaning | Current |
|---|---|---|---|
| **Package version** | `0.x.y` (SemVer 2) | the released, installable, citable artifact | **0.9.0** (unreleased) · 0.8.0 is the latest tag |
| **Architecture generation** | *Organica 1*, *Organica 2* | a generation of the eight-layer engine. Organica 1 is frozen; Organica 2 is planned | **Organica 1** |
| **Research campaign** | *Ablation Study 1*, *Ablation Study 2* | the experimental series. Study 1 is the eleven-condition ablation; Study 2 is the six-colony Tier-1 matrix | **Study 2 in flight** |

The package version is **pre-1.0**, which is the honest state: the public
API is not declared stable, and the MINOR/PATCH numbers carry the
meaning instead. `tests/test_versioning.py` asserts that the three
declarations — `organica.__version__`, `pyproject.toml` and `CITATION.cff`
— never drift apart, and that the version describes *this* commit: if a
tag for the version exists, it must point here. A version whose changelog
entry is marked `(unreleased)` is allowed to have no tag yet, because
there is nothing to check out.

---

## [0.10.0] — (unreleased)

### Decided — Phase K H2 remains binding; one bounded Gate 13 diagnostic is authorized (2026-10-30)

Phase K's terminal outcome **H2** ("the search failed; do not design V2") and the Gate 13 causal account had been read as if both were binding on everything, which left the project auditing a defect it had already localized. They scope different things and the decision is now recorded: **H2 binds V2 design** — no architecture redesign, no frozen-file change, no capability claim — and it does **not** bind one **diagnostic** arm, **G13-D**, which removes the two confounds it can remove (**capacity** and **provenance**) on the five seeds already classified diagnostic, in-process, and scored end-to-end against the declared baselines. The readout is held at its calibrated `alpha = 256.0` in both arms; it is a constant, not an intervention. Relation-family separation and a non-frequency ranking are out of scope: building them is design, which D1 forbids. The current 10-cell runner lacks both intervention hooks; a small adapter and dated diagnostic plan are required before execution. See [`docs/DECISION-V2-SCOPE.md`](docs/DECISION-V2-SCOPE.md) and manual decision 14. No preregistration, threshold, verdict, frozen engine, published result, or confirmatory seed is changed.

**Organica 1 is frozen, and Phase L opens as a measurement phase rather than
another benchmark hunt.**

### Added — Paper 01's citations, and the lesson that carries none (2026-10-30)

- **Paper 01's citations are closed.** §4.1's curriculum-sensitivity framing and §5.4's
  four methodological lessons now carry inline `(Author, year)` markers, and the manuscript
  carries a **References** section with **seven** sources, each retrieved and read on
  2026-10-30: Bengio et al. (2009), Wang, Chen & Zhu (2021), Button et al. (2013),
  Simmons et al. (2011), Jacobs & Wallach (2021), Davis & Goadrich (2006), and
  Saito & Rehmsmeier (2015).
- **One lesson carries no citation, by design.** The second methodological lesson —
  compare against the strongest simple baseline and take the headroom from the ceiling —
  is the project's own rule and reports only Organica 1's own numbers, so it is stated as
  such rather than given a borrowed reference. The judgment is recorded in the source notes
  instead of being left silent.
- **The limit on what was read is written down.** Two sources were reachable only as their
  authors' abstracts, because the ACM Digital Library's full text is not retrievable in this
  environment; they are cited only for what those abstracts state.
- **A correction to a cited source was read and disclosed.** An erratum to Button et al.
  was published in *Nature Reviews Neuroscience* 14(6):451 (15 April 2013); it corrects the
  definition of *R* on page 366 and does not affect the power conclusions cited here.

### Corrected — the first world edge was reported without the distribution beside it (2026-10-30)

The owner reviewed the project's own reporting of the Gate 13 ranking failure and found one
claim that was true but incomplete in a way that mattered.

- **The rank of the first world edge is correct** — **31** in the 1-tag stimulus, **30 / 18 /
  53** in the 2-tag seeds, **16 / 8 / 8** after the LIMIT-4 separation — and it was reported on
  its own. A first edge appearing early in a frequency ordering reads as though the world's
  relations were nearly reachable by raising a budget.
- **They are not.** Under the engine's own global count-ranked selection the world's 112 edges
  are **spread through the table, not clustered at its top**: the top 20 recovers **0–1** of
  them, the top 40 **0–2**, the top 80 **8–16**, the top 160 **36–55**, and the top **320** —
  about **16×** the engine's budget — **106–109** (`docs/gate13_allocation_rule.json`, 3
  seeds). The five-seed capacity sweep puts cap 40 at **1–8 of 112** and the frozen cap of 20
  at **0–3 of 112** (`docs/gate13_capacity_sweep.json`).
- **A quoted figure did not survive contact with the artifact.** *"Cap 40 recovers 4–8 of
  112"* was carried in correspondence; the artifact gives **1–8 of 112** (per seed: 4, 7, 1, 2,
  8). The numbers above are read from the artifacts.
- **No measurement changes**, and the conclusion is unchanged — now stated with its
  distribution: **no frequency-based selection can find the world's relations**, because they
  are a third of the rows and are not clustered at the top of any frequency ordering.
- **Law II — the owner's ruling, 2026-10-30.** Keep the discrepancy disclosed and **do not
  amend the law yet**. The amendment waits on the owner's question: *is Law II a design
  requirement, or a description of V1's actual behavior?* Rewriting the law to match the
  frozen engine would erase the distinction that makes the discrepancy meaningful.
  `docs/DESIGN_LAWS.md` is not edited; the disclosure stays where the audit put it.

**A first edge at rank *N* is one edge arriving, not a set arriving.** A threshold, a first case
and a headline statistic are all single points, and the set is the claim.

→ `docs/GATE13-RELATION-SEPARATION.md`; `research-journal/phase_g_findings_20261021.md` §54
and §62; `docs/USER-MANUAL.md` findings 27 and 36; `docs/FACTS-SHEET.md` AD8;
`papers/README.md`

### Corrected — a hand-transcribed table had drifted from its artifact, and the first repair was defective too (2026-10-30)

The publication pass on Papers 01 and 02 turned up a defect in the record itself: the Pilot-0
score matrix in `docs/PILOT-0-INSTRUMENTATION-AUDIT.md` §2 declares
`docs/acquisition_single_seed_pilot.json` as its artifact, but **18 of its 36 values disagreed
with that artifact** in the fourth and fifth decimal of log-loss (largest gap **6.7×10⁻⁵**).

- **The artifact never changed.** The same values are present in both commits that carry it
  (`89b0744`, 2026-10-28; `4ceeab4`, 2026-10-29), verified by extracting them at each revision.
  The drift was in the **transcription**.
- **Six of the drifted values had been inherited** by
  `papers/01_developmental_structure_formation.md` §4.7, and six more each by the five-row
  summaries in `docs/ACQUISITION-ENDPOINT-AUDIT.md`, `docs/ORGANICA-V2-DESIGN-BRIEF.md`,
  `docs/FACTS-SHEET.md` (AC7), `research-journal/phase_g_findings_20261021.md` and
  `research-journal/_journal_entry_51.md`.
- **The first repair made it worse, differently.** The hand-written repair **replaced the two
  reference rows** (Bayes ceiling, base rate) with **duplicate copies of cells 7 and 8**. The
  defect is invisible to review — the table still had the right shape and the right-looking
  numbers — and was caught only by running the table against the artifact mechanically. The table
  is now **regenerated from the artifact** rather than patched.
- **The check is now permanent.** The new `tests/test_readout_tables.py` asserts every document
  that restates this readout against the artifact, and includes four assertions that the checker
  itself can fail.
- **No conclusion changes.** Organica's readout still loses to both baselines, the E-rem floor is
  still **0.403045**, the acquisition gate still fails, and transfer is still *not measurable*.
- **A second, pre-existing defect was caught by the test suite**: journal §59's Law V formula had
  its LaTeX escapes written in as **literal tab characters** rather than as `\t`, so the
  expression rendered as broken text and read as unsubstituted template placeholders. The
  committed record was red on `master` — `tests/test_doc_placeholders.py` failed at `67a7565`.
  The escapes are restored and the repair is noted in place; **no claim changes**.

**A table transcribed from an artifact is a new claim and needs a mechanical check against that
artifact** — and a repair written by hand is another hand transcription, and fails the same way.
The prior verification script reported "0 failures" because it never covered these cells.

### Added — Paper 02's citations, and eight figures that have to be able to fail (2026-10-30)

Papers 01 and 02 were brought to academic grade.

- **Paper 02's §2 now carries inline `(Author, year)` citations and a five-source References
  section**, every source read against a primary source on 2026-10-29: ACM Publications'
  *Artifact Review and Badging* v1.1 (including the Publications Board's 2020 interchange of the
  *Results Reproduced* / *Results Replicated* definitions), Bau, Liu, Wang, Zhu & Torralba's
  *Rewriting a Deep Generative Model* (ECCV 2020, oral), Elhage, Nanda, Olsson et al.'s *A
  Mathematical Framework for Transformer Circuits* (Anthropic, 2021), the W3C *PROV-DM*
  Recommendation (Moreau & Missier, eds., 2013), and Shumailov, Shumaylov, Zhao, Papernot,
  Anderson & Gal (*Nature* 631(8022):755–759, 2024) **with its 2025 Author Correction**
  disclosed — a notation typo, and no change to the cited empirical claim.
- **One candidate citation was dropped**: the Elhage paper's *faithful versus sufficient*
  distinction could not be verified from any readable copy, so it is not cited. **Cite only what
  was read.**
- **Eight dependency-free SVG figures** were added for Papers 01 and 02, generated by the new
  stdlib-only `benchmarks/figure_papers.py`. The generator **asserts every value it draws
  against the committed artifact**, bounds-checks its canvas, checks for text overflow, and
  **parses its own XML before writing** — added because an early build emitted a malformed
  attribute and the renderer silently stopped after the first bar. **A figure is a program that
  draws a claim, so it must be able to fail.**

→ `papers/01_developmental_structure_formation.md`;
`papers/02_persistent_structural_provenance.md`; `benchmarks/figure_papers.py`;
`docs/figure_p*.svg`; `tests/test_readout_tables.py`

### Corrected — the acquisition endpoint, the benchmark that replaced it, and the campaign that stopped at its gate (2026-10-28)

A review of the acquisition experiment found its **endpoint** could not measure
what the study claims. Every one of the five objections was checked against the
code and the frozen generator, and **every one was confirmed**; two further
defects were found that the review did not raise; and a third was found in the
redesign, which changed the study's structure. **No acquisition cell had been
run when the corrections were made.**

- **Seven defects, confirmed against the code.** (a) The task and the readout
  described **different relations** — the frozen generator draws each event's
  cause independently, and the gold relation is a within-event co-occurrence
  that does not predict the next event. (b) **F1@0.5 was degenerate**: the
  Bayes-optimal model scored **0.0000**, exactly like the model that knows
  nothing. (c) The projection was **directional** where the gold relation was
  undirected — 10 of 12 gold pairs appeared in one direction only. (d) The
  "fixed-rule ceiling" was a **relation oracle**, not a prediction ceiling.
  (e) **Retention and transfer were one number with two names.** (f) The
  engine's taxonomy has **no category for a tight group** — `_classify` needs
  clustering ≤ 0.4 and a co-occurrence-defined group has clustering
  **1.000**, so all 12 tags classified `unclassified` and **zero** concepts
  formed. (g) The generator's regime switch is **relation-invariant**.
- **The probe's headroom check was against the wrong comparator.** It compared
  the Bayes ceiling with a **base rate** — the weakest possible comparator.
  Against the **strongest** simple baseline (tuned bigram, decayed bigram,
  cell counter) the headroom was **0.005647** nats against the base rate's
  **0.105032**: the world's law is **first-order Markov**, so a bigram table
  is its natural learner and "understood the law" and "counted transitions"
  are not separable by a next-event score alone. That world was reclassified
  **CALIBRATION / CONTROL**.
- **Added — a compositional task that withholds a *combination* of familiar
  elements.** Four cells in a 2 × 2 grid of two latent factors; the
  tag-to-cell mapping is randomised per world; one held cell per world has its
  transitions removed from the training stream only. Its gate passes on **30
  independent worlds**: gap **+0.1035 nats**, 99 % interval **[+0.0996,
  +0.1074]** against the strongest simple baseline, with the held cell's gap
  **4.6×** the rest so the headroom is *generalization* headroom. Gates G1–G7,
  each with a proof-of-firing.
- **The campaign stopped at the preregistered acquisition gate.** The frozen
  engine asserted **0–3 of 112** world edges while its raw memory held
  **112 / 112 (100 %)**. The cause is one named bound — `MAX_PREDICTIONS = 20`
  — and raising **only** that cap restores **98.2 %–100 %**. Organica's
  readout scored **0.453018** against a replay learner's **0.347521**.
  **Transfer was not measured, and it is not a transfer failure**; the 600-cell
  factorial did not run.
- **Fixed — a gate that could not fire.** The harness and the runner each
  implemented "Gate 13" under one name: the harness on the raw-temporal basis
  (**100 %**, passed) and the runner on the asserted basis (**0.0 %**, failed),
  on the same seed and the same world. The harness now implements the
  pre-registration's dual accounting, gates on the asserted figure, exposes
  the cap-raised treatment so the failure is attributable, and its test asserts
  that Gate 13 **fails** on the frozen engine and **passes** under the
  treatment.
- **Added** — `docs/ACQUISITION-ENDPOINT-AUDIT.md` (the audit record),
  `docs/ORGANICA-V2-DESIGN-BRIEF.md`, `docs/V2-CAPACITY-DESIGN-BRIEF.md`;
  **updated** — the pre-registration (Revision 3, Amendment 3), the user
  manual (§8.19, finding 25), the facts sheet (§AC), `AGENTS.md` (rule 25),
  the README framing, and journal §51.

### Measured — the relation separation is real, oracle-free, and NOT sufficient (2026-10-29)

The sharpest open question after the causal account was: *can world relations
be separated from engine-generated relations, without modifying the frozen
engine?* It has now been measured. **All seeds are diagnostic
(`20261101`–`20261103`); the confirmatory sample (`20261106`–`20261130`, 25
seeds) is untouched.**

- **The mechanism, located.** `memory.py:261` gates the **trigger** of edge
  recording (`if event_type != "sleep"`), but `memory.py:332` does **not** gate
  the **lookback window** (`SELECT tags FROM events ORDER BY time DESC LIMIT ?`),
  so a world event can take its `tag_from` from a **sleep row**. This is
  **D2** in the audit-trace spec — disclosed, never quantified.
- **The substrate is 99.5 % the engine's own output** — **756–772 world events
  against 152,186–263,533 sleep events** (**201×–341×**). The engine stores one
  sleep event per candidate per cycle, so after 110 cycles it has written two
  to three hundred times as many rows about its own thinking as about the
  world.
- **The separation removes 35.7 %–40.7 % of the relation table, and 100.0 % of
  the removed rows have a sleep-sourced `tag_from`** — the D2 mechanism,
  confirmed exactly. It uses `event_type`, which the engine already records, so
  it is **not an oracle** (unlike the world-vocabulary filter of the previous
  entry).
- **And it is not sufficient.** With every contaminated row removed, coverage
  at the frozen cap of 20 is still **0.0000–0.0446**, and the top 20 is still
  **75–100 % intra-cell**. The separation *does* move the world's edges up
  sharply (first world edge from rank 30 / 18 / 53 to **16 / 8 / 8**), and that
  is still not enough to clear the gate.
- **Two distinct crowding mechanisms were in play.** In the **1-tag** stimulus
  the crowding is the engine's own vocabulary — first world edge at **rank
  31**, the top 30 rows all `internal→world`, verified independently. In the
  **2-tag** stimulus, once that is removed, the crowding is the **world's own
  co-occurrence**: intra-cell pairs out-count the law's transitions by roughly
  an order of magnitude, and a global count-ranked cut of 20 is consumed by
  them entirely.
- **The V2 requirement list is now three, not two:** provenance separation,
  relation-family separation, and **a ranking that is not raw frequency**. The
  third is the hard one, and the capacity sweep showed it cannot be bought
  with budget — precision never exceeds 0.3443 at any budget under either
  allocation rule.
- **Added** — `docs/GATE13-RELATION-SEPARATION.md`,
  `benchmarks/probe_relation_separation.py`,
  `docs/gate13_relation_separation.json`; **updated** —
  `docs/GATE13-CAUSAL-ACCOUNT.md`, `docs/V2-CAPACITY-DESIGN-BRIEF.md` (second
  addendum), `docs/USER-MANUAL.md` (finding 27, revision-log row),
  `docs/FACTS-SHEET.md` AC14, journal §54.
- **No V2 build is authorised.**

### Measured — the ranking requirement: every criterion the engine already stores fails (2026-10-29)

The third of the three V2 requirements — *a ranking that is not raw frequency* —
had been called the hard one, with no precedent in the engine. **It turned out to
have a precedent, and the precedent is the finding.** **All seeds are diagnostic
(`20261101`–`20261103`); the confirmatory sample (`20261106`–`20261130`, 25 seeds)
is untouched.**

- **The engine already computes the criterion.** `sleep.py:1139-1160` computes
  `ratio = count / max(source_freq, 1)`, stores it in every candidate's evidence,
  uses it for **survival**, and then sorts by **raw `temporal_count`** for
  **admission** — so every criterion the probe tested uses fields the engine
  **already stores**.
- **The grid.** 2 tables x 2 frequency scopes x 5 criteria x 3 seeds = **60 cells**,
  over `temporal_count`, `source_frequency`, `target_frequency` and `ratio`. The
  offline reconstruction of the raw table had to match the engine's own table
  exactly or the probe would refuse to report; it did, on every seed.
- **The best cell in the entire grid reaches coverage 0.0804 at precision 0.4500.
  The gate is 0.50** — six times short. Everything else is worse.
- **Neither fix works alone (0.0089). Together** they take coverage from
  **0.0000 to 0.0804** and precision from **0.0000 to 0.4500**, and flip the
  intra/inter balance from 20 / 0 to roughly 8–15 / 5–13 — the world's cross-cell
  relations enter the selection for the first time in meaningful numbers.
- **The engine's own normalized criterion is actively harmful here.** On the raw
  table under the engine's own scope, `ratio`, `cosine` and `pmi` each select
  **20 engine-vocabulary edges and 0 world edges** on every seed.
- **The mechanism is measured, not inferred.** `_record_tag_counts` sits inside the
  `if event_type != "sleep":` block, so **`tag_counts` is world-scoped** and the
  engine's own words have **no frequency entry** — `freqs.get(tag_from, 1)` returns
  1, so `ratio = count / 1 = count`, the maximum possible for that count.
- **A self-inclusive scope flips the failure the other way.** The engine's sleep
  output **names the world's tags** (`sable` 2,601 times, `olive` 7,753, `maple`
  35,986, `cedar` 52,070), so world tags acquire enormous denominators and are
  penalised, and the engine's *rare* metadata words win — best world edge
  `sable` -> `fern` at ratio **0.0177**, against `mutation` -> `cedar` at
  **0.1654**. **The world's vocabulary and the engine's own vocabulary are not
  separable by frequency in either direction**, so the discriminator cannot be a
  per-tag statistic; it must be a **relation-level** property — *which event the
  relation came from*.
- **Added** — `docs/GATE13-RANKING-CRITERION.md`,
  `benchmarks/probe_ranking_criterion.py`, `benchmarks/probe_ranking_mechanism.py`,
  `docs/gate13_ranking_criterion.json`; **updated** — `docs/USER-MANUAL.md`
  (finding 28, revision-log row), `docs/FACTS-SHEET.md` AC15, journal §55,
  `docs/ORGANICA-V2-DESIGN-BRIEF.md` §9.7.
- **No V2 build is authorised.**


### Changed — the historical record normalized to American English, with the change proven (2026-10-29)

The owner confirmed that the frozen records stay right under a spelling normalization — spelling
is not a claim, so no number, verdict, method, seed or decision rule is touched — and authorized
closing that gap.

- **234 words across 25 files** normalized, including the preregistrations
  (`ABLATION-PREREGISTRATION`, `ACQUISITION-EXPERIMENT-PREREGISTRATION`,
  `PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION`, `WORLD-SCALE-PREREGISTRATION`), the audit-trace
  specification, the measurement records and the frozen journal sections.
- **Three proofs, run against `HEAD` for every changed file**: non-target content byte-identical;
  the sequence of numeric literals identical; structure identical (headings, table rows, list
  items, lines). All three pass on all 23 changed files. Inline code spans were never rewritten,
  so **no identifier, file path, tag, test name or constant changed**.
- **A bug worth recording.** The first pass reported *"remaining: 0"* and was wrong by 88
  occurrences: the sweep and its check shared a document-wide code-span regex that mis-aligns on
  unbalanced backticks, so prose was skipped and then not counted. The bug surfaced only because
  a **second, differently implemented** check — a raw-text scan with no span logic — disagreed
  with the first. **A verifier that reuses the writer's parser inherits the writer's bug; a check
  that cannot disagree with its own writer is not a check.**
- **Every number, claim, verdict, date, method, seed and decision rule in the repository is
  unchanged.** The frozen engine is untouched.

### Corrected — Paper 00's audit completed: the constitution, measured against the code (2026-10-29)

The owner asked for the audit of Paper 00's broad claims to be *finished*, not just the two
defects that happened to be noticed. It was finished, by reading the six laws in
`docs/DESIGN_LAWS.md` against the frozen engine and the V1 record.

- **Two of the six architectural laws are contradicted by the implementation.**
  - **Law III (Cognitive Isolation) is violated in exactly the way it was written to prevent.**
    The design law requires that *"temporal precedes matrices are strictly computed on non-sleep
    events"*; `memory.py` gates the **trigger** on `event_type != "sleep"` but not the **lookback
    window**, so sleep output re-enters `precedes` at **201×–341×** the world's own event count
    (D2). **This is the same defect that contradicts Paper 05's "zero self-contamination"
    guarantee.**
  - **Law V (EIG Attention) is wrong twice.** Formally, the engine applies
    `uncertainty * (1.0 + novelty)` to questions and `uncertainty * novelty` to dreams, so the
    law's single expression is not what it computes for half its cases. Empirically, the
    pre-registered prediction that development is EIG-orthogonal came back **REVERSED** —
    selecting the *lowest*-EIG experiment develops **more** than the highest-EIG one.
- **Law IV (Grounded Dreaming) is mixed.** The confidence baseline **holds** (dreams are created
  at **0.04–0.06**, matching the design law), but the law's operative clause — a dream becomes a
  belief only if an external experiment generates the confirming events — is **never exercised**,
  because the engine generates experiments and never executes them, so no question can ever
  close.
- **Law VI holds** (thresholds **0.3** / **0.15**); **Law I was not separately audited** and is
  reported as such rather than assumed.
- **Also corrected:** the abstract's *"unbroken lineage to the raw experience"* is false (D3);
  *"causal predictions"* overstates the engine's own words — `memory.py` calls the temporal edges
  *"the organism's first approximation of causality"* — so the abstract now says **temporal
  predictions**; and the reference list's stale titles and its false *"Associated pre-prints"*
  label (seven manuscript files, **zero published**).
- **D4, a new disclosed defect.** The engine's stored `generation` field agrees with
  `docs/architecture.md` for **G1** and is **one lower for every primitive from G2 upward**
  (meta-concepts and processes `1`, workflows `2`, hypotheses `3`, theories and questions `4`,
  dreams `5`, investigations `6`, experiments `7`), and no document states the field's mapping —
  an undocumented offset, not a violated claim. The audit-trace specification is frozen at
  `audit-trace-v1` and was **not** edited to carry it; the disclosure lives in `docs/FACTS-SHEET.md`
  AD5 and manual finding 33.
- **Added** — manual finding 33 and a revision-log row; `docs/FACTS-SHEET.md` AD5; journal §59.

**A constitution that has never been audited against its implementation is a description of an
unimplemented architecture.** Every one of these was found by *writing the auditor*, not by
arguing — the strongest evidence this program has produced for its own thesis, and invisible to
any review that read the laws and the code side by side without measuring the code's behavior.

**Paper 00 is now accurate and still not ready to circulate**: it is not yet the recast position
paper the project needs, and its literature engagement is absent.

### Corrected — the first audit of Paper 00 and Paper 05 (2026-10-29)

The owner's publication framing put Paper 00 and Paper 05 outside the active submission
queue pending review. The first pass of that review found two verified factual defects and
one contradicted guarantee.

- **Paper 00's generation count was wrong against itself.** It said *"this hierarchy spans
  eight generations"* and then listed **nine** rows (G0–G8). `docs/architecture.md` names
  it correctly: *"The 8 Generational Primitives"*, with **G0: Experience** as the substrate
  and G1–G8 as the primitives. Paper 01's first draft made the same error and was
  corrected in the same pass.
- **Paper 00's Law II is stated without the project's own disclosure.** The manuscript
  calls it inviolable — *"Every structure carries explicit, verified `parent_ids` traceable
  to G0 events"* — but the frozen engine's chain **terminates at Layer 1**, because
  concepts, phrases, loops and predictions are built from tags and the structure→event
  link exists only as counts. This is **D3**, already disclosed in the audit-trace
  specification and left open because the frozen engine's constitution is the owner's
  decision. Corrected in place, with the disclosure carried inline.
- **Paper 00's abstract claims efficacy the record does not support.** The *forms* of
  curiosity, dreaming and inquiry exist (G5–G8); the *efficacy* does not — Phase K's
  matched mechanism ablations all came back empty (`NO_QUESTIONS` −0.0095 [−0.0328,
  +0.0140]; `NO_FALSIFICATION` +0.0241 [−0.0048, +0.0495]; `NO_DREAMS` +0.0000 [0.0000,
  +0.0000], all three intervals containing zero), and **Law IV is never exercised** —
  experiments are generated, every consumer only prints them, and no Question can ever
  close. **Paper 00's remaining broad claims and its literature framing are still
  unaudited**, and the manuscript is **not ready to circulate**.
- **Paper 05's core guarantee is contradicted by the measurement.** Its claim that the
  strict partition *"ensures zero synthetic self-contamination across indefinite life
  cycles"* does not survive contact with the record: **17.9%** of the distinct supporting
  transitions behind reported beliefs (802 of 4,481) are self-sourced, and **43.2%** of all
  distinct transitions recorded (5,436 of 12,583) are the organism's own output, entering
  the temporal substrate through the unfiltered lookback window (D2). The repair is a
  **new thesis** — *the limits of cognitive isolation in Organica V1* — not a revision.
- **Added** — manual finding 31; `docs/FACTS-SHEET.md` AD3; journal §57.

**A position paper is audited against the code, not against the prose.** The two documents
most likely to be circulated are the two least checked against the engine, because neither
is a measurement record and so neither is covered by the harness.

### Changed — the publication framing moved into the rule file; living guidance set to American English (2026-10-29)

The publication map was settled in conversation and recorded in `papers/README.md`, but a
framing that lives in one document is a preference rather than a constraint. It now also
lives in the rule file.

- **`AGENTS.md` rule 26** states two disciplines: **research-program structure is not
  publication structure** (the corpus is organized as a research-program map and a
  publication map kept side by side, so the layer map orients a reader without pressing
  every old manuscript or lab artifact into a paper), and **a claim's status names its
  scope** (four statuses — *supported within the tested scope*, *mixed / context-limited*,
  *reversed*, *not established / not measured* — with **not established is not refuted**,
  and a compound status required where the evidence splits).
- **`AGENTS.md`, `README.md` and `ROADMAP.md` set to American English.** Code spans and
  identifiers were protected, so no file path, tag, test name or constant was altered;
  the diff is prose only.
- **The historical research record was deliberately not rewritten.** Preregistrations,
  measurement records and the frozen journal sections are committed records whose value
  depends on having been written as they were; normalizing them is the owner's decision,
  not a cleanup.
- Manual revision-log row added, per the standing obligation that any change the manual
  describes is recorded in the same turn.

No measurement changed. The frozen engine is untouched — the only difference from `v0.9.0`
is the version string in `organica/__init__.py`, which is not in the frozen file set — and
the live study remains paused at 5,396 sleep cycles with no `organica.log`.

### Corrected — the audit build's closure was recorded in six places, and two documents still said the opposite (2026-10-29)

The owner read the paper directory and the V2 design brief and found two documents
still asserting that the audit build was unfinished, after it had closed, frozen and
been tagged on 2026-10-28.

- **Paper 02 contradicted itself.** Its abstract ended *"A5 field honesty and A6
  separation of trace from counterfactual remain pending; the audit instrumentation is
  not yet frozen"* and its §3 was titled *"Remaining acceptance work"* — while its own
  draft-status line said *"A5/A6 closed and the audit layer frozen at `audit-trace-v1`
  on 2026-10-28"* and its conclusion said the same.
- **The V2 design brief's §4.3 was headed *"The audit build is nearly, but not fully
  closed"*** and listed A5 and A6 as *"Still open"*. Five further passages carried the
  same state: build gate 4 was unmarked, the gate-5 annotation said *"gates 4 (A5/A6)
  and the study itself remain open"*, the §10 corrections table said A5/A6 *"remain
  open"*, the §11 table treated their closure as a future event, and the superseded
  banners in `ROADMAP.md` and `docs/V1-SYNTHESIS.md` described the audit build as
  unfinished and the pre-registration as Revision 2.
- **Eleven passages across four documents** corrected. The closure had been recorded in
  **six** places; six agreeing places do not compensate for two disagreeing ones, and a
  self-contradicting document is worse than a merely out-of-date one, because it
  teaches the reader that its own sentences cannot be relied on. The sweep criterion
  was **one status, stated in every document that states it**.

### Changed — the papers are the publication surface (2026-10-29)

The repository is a research program whose codebase is one component, and the
owner set the near-term publication sequence. It is now recorded in
[`papers/README.md`](../papers/README.md) so it is not re-derived. **The accurate
next milestone is making the first two manuscripts submission-ready — not publishing
them as they stand.**

- **Paper 01** — rewritten at academic grade as the honest empirical V1 account:
  methods and results reconciled to the committed record, with the negative
  external-task findings and the acquisition campaign retained rather than smoothed.
  Renamed to `01_developmental_structure_formation.md` to match its revised title
  (nothing referenced the old filename).
- **Paper 02** — revised at academic grade: Introduction, Positioning, Methods
  (observer, the two graphs, the three arms, every measured quantity **with its
  population**, the acceptance criteria with their proof-of-firing tests, and
  reproduction), Results (selection reconstruction, event-level attribution, ancestry
  honesty, behavioral invariance and the 1.7-cycle window boundary), Discussion,
  expanded Limitations, and data/code availability. The non-vacuity argument is now
  explicit: the default arm's candidate cap never bound, so the stress arm — in which
  403 candidates lost on rank — carries the selection test.
- **Paper 01's headline finding kept in its own words**: the **+0.1035 nats** is the
  *benchmark's headroom*, not a margin any learner achieved, and the transfer question
  is **not measurable** rather than answered.
- **House style set to American English** (`behavior`, `program`, `analyze`, `center`).
- **Two maps, kept side by side.** The corpus is organized as a **research-program
  map** (theory / proposed mechanisms / empirical findings) and a **publication map**
  (which manuscript can make a coherent, evidence-backed contribution now), so the
  three-layer view orients a reader without pressing every old manuscript or lab
  artifact into a paper.
- **Claims now carry one of four statuses**: *supported within this scope*, *mixed /
  context-limited*, *reversed*, and *not established / not measured*. **Not
  established is not refuted**, and *reversed* is a stronger statement than merely
  unsupported. Paper 01's central question was narrowed to match and no longer covers
  every probe.
- **Paper 05 might instead become a paper about the limits or failure of cognitive
  isolation** — a new thesis, not a revision of the existing one.
- **Held or reclassified**: Paper 00 is a separate position paper, to be developed only
  after its broad claims and literature framing are audited; Papers 03 and 04 are
  mechanism *proposals*, not demonstrated-efficacy results; Papers 05 and 06 stay
  historical until their claims are rechecked, and **no claim in either is currently
  strengthened by recent work — neither should be described as if it were**: Paper 05
  **cannot** be presented as evidence that the system prevents self-contamination, because
  its strict-firewall claim conflicts with the measured sleep-sourced relations, and
  Paper 06's major lifecycle, stability and lineage claims remain unverified against the
  current evidence.
- **The Phase L characterization, the V1 synthesis and the audit artifacts are research
  records, not manuscripts.** They are not additional papers in `papers/`, and the
  inventory stays **seven manuscript files, zero published**.

**No measurement changed.** The six negative task families, the Phase L verdict
`H3-L — INCONCLUSIVE`, the acquisition gate failure and the transfer result of *not
measurable* all stand as recorded; every seed used in the mechanism probes remains
diagnostic; the frozen engine is untouched.

### The audit build is CLOSED, TAGGED and FROZEN (2026-10-28)

The audit build's stop condition is met and has been executed. **A1–A7 are all
met**, the three probe arms (default, stress, forced-tie) are regenerated, and
the instrumentation is **tagged `audit-trace-v1`**.

- **A5 closed** — field honesty enforced; records verified to contain zero
  mislabelled count fields, and proved to fail if competing flow is mislabelled
  as contradictory observations.
- **A6 closed** — counterfactual separation enforced; trace records and schema
  verified to contain zero counterfactual claims, and proved to fail on
  counterfactual injection.

**From that tag, no feature may be added to the instrumentation.** It may still
be *fixed* if it is found to be wrong, but not *extended*; a new requirement
goes to the study's wish-list instead.

**The package version stays untagged.** `audit-trace-v1` marks the
*instrumentation*, not a release of the package — which keeps the three version
namespaces (package version, architecture generation, research campaign) separate
as this changelog requires.

Verification at the freeze: **128 tests pass** · 83 anchors / 0 broken · 1,142
document paths all exist · the live study untouched at **5,396** sleep cycles
with no `organica.log`.

### Corrected — "bottleneck" is not "deepest cause": the acquisition failure is a PRECISION limit, not a capacity limit (2026-10-28)

The parallel session's Gate 13 write-up named **`MAX_PREDICTIONS = 20`** as the
cause of the acquisition failure, on the evidence that raising the cap to
1,000 restored coverage to 98.2 %–100 %. That was sound on its own evidence,
but it left **three probes written and uncommitted** that ask whether there is
a better fix than a bigger budget. Running them, and adding a fourth, changes
the answer. **All seeds used are diagnostic (`20261100`–`20261105`); the
confirmatory sample (`20261106`–`20261130`, 25 seeds) is untouched.**

- **The world's relations are in memory.** Raw temporal coverage is
  **0.97–1.00** on every seed and both stimulus shapes (**1.0000** on all six
  2-tag seeds) — the same figure the pilot recorded.
- **But they are a minority of the candidate space, and they are not the
  high-count rows.** The `precedes` table has **366–518 rows** for a 16-tag
  world; only **232–240** are world-tag pairs; the world's 112 edges are about
  a third of what any selection must retain. **Precision never exceeds
  0.3443** at any budget under either allocation rule.
- **A 1-tag stimulus does not rescue it** — it removes the within-cell pairs by
  construction, quintuples coverage to **0.1719–0.1953**, and still fails
  **0 of 6** seeds. The top of the table is internal vocabulary
  (`type -> olive`, `generation -> olive`).
- **The capacity sweep is a steep monotone dose-response**: **0.0000–0.0268**
  at cap 20, **0.0089–0.0714** at 40, **0.0893–0.1786** at 80,
  **0.9911–1.0000** uncapped — needing **240–244** asserted edges, about
  **12×** the budget. At the frozen cap the law-bearing **inter-cell** edges
  are **0–3** while intra-cell edges are **28–39**: the engine formed the
  world's partition and none of its transitions.
- **A per-source allocation rule is NOT the fix** — this refutes the
  hypothesis the observation-protocol probe suggested. Per-source K=10 retains
  **258–286** edges for coverage **0.72–0.77**, where the global rule reaches
  **0.95–0.97** at 320.
- **So the deepest cause is PRECISION.** In a candidate space where the signal
  is a third of the rows and is not clustered at the top of any frequency
  ordering, **no frequency-based selection can find it**. The specific
  pollution is **internal vocabulary**: **27–34** distinct sources for a
  16-tag world.
- **Three things are called "Gate 13"** and they disagree — the protocol's
  (asserted structure, global top-20: FAIL), the capacity sweep's (global
  top-K: dose-response), and the observation probe's (`precedes` table,
  per-source top-20: PASS). The third is a different *selection rule over the
  same table*, and the whole FAIL/PASS difference is that rule. The filter in
  that probe selects on the world's own tag list and is therefore an
  **oracle**, not an organism-side fix.
- **Added** — `docs/GATE13-CAUSAL-ACCOUNT.md`,
  `benchmarks/probe_allocation_rule.py`, `docs/gate13_capacity_sweep.json`,
  `docs/gate13_allocation_rule.json`; **updated** —
  `docs/V2-CAPACITY-DESIGN-BRIEF.md` (the brief's premise was measured and it
  does not hold; two of its design objectives are refuted),
  `docs/ORGANICA-V2-DESIGN-BRIEF.md` §9.7, `docs/ACQUISITION-ENDPOINT-AUDIT.md`
  §8.3, `docs/USER-MANUAL.md` §8.19, `docs/FACTS-SHEET.md` AC11–AC13,
  `AGENTS.md` rule 25(d), journal §52.
- **No V2 build is authorised.** The V2 question is narrower and sharper: can
  the organism identify which of its vocabulary items are its own, and can it
  rank candidates by something other than raw frequency?

### Corrected — five claims in the project's own summary, narrowed (2026-10-26)

A review of the project's *summary* — not of its measurements — found five
sentences that were wider than the checks behind them. All five were
corrected, and the corrections were made **before the acquisition experiment
ran**, so the next study does not inherit an overstatement from the previous
one. **No number was recomputed, no artifact re-read, and no criterion
reinterpreted.** The protocol verdict `H3-L — INCONCLUSIVE` stands, the Phase L
characterization stands, and the six negative task families stand.

1. **"Revision exists" → "structural displacement exists."** Phase L's
   `DI`/`PI` are structure-retention indices — they measure whether later
   *structure* displaces earlier *structure*, not whether a *belief* was
   corrected against ground truth. Belief revision is a separate capability
   question, and the one head-to-head measurement of it was a clean loss:
   Organica **0.4111** vs the best simple baseline **0.9846**, difference
   **−0.5735**, 98.33% interval **[−0.6162, −0.5309]**, **REVERSED**.
2. **The 3:1 crossing is robust *within this defined experiment* — this
   engine, this world family, this support-ratio axis.** The eight alternative
   bootstrap seeds test **resampling stability, not new worlds**; they re-draw
   from the same measured seeds. **3:1 is not a general threshold for
   Organica.**
3. **Path dependence is supported; strict order dependence is not tested.** The
   curriculum and history comparisons vary the event **multiset and the order
   together**, so they cannot separate "order matters" from "content matters".
   Isolating order requires the multiset held fixed — that comparison has not
   been run.
4. **Transfer: no positive transfer has been demonstrated, and the measured
   cross-domain result was negative** — **−0.4863** across **12 domain pairs**,
   mean shared vocabulary **0.17 tags**. Other forms of transfer remain
   untested.
5. **"Independently auditable" means independently *reconstructed from the
   engine's state*, not independently *replicated by another lab*.** The trace
   also covers the organism's **surviving, current** structures rather than
   their full past, and the audit layer is **now complete** — A1–A7 all met,
   tagged and frozen at `audit-trace-v1` (2026-10-28).

The project now leads with the compressed state: *Organica demonstrably
changes its internal structure as experience and curriculum change. Under one
tested pressure axis, later structures can abruptly displace earlier ones. The
project has built a strong instrument for auditing surviving state and
implemented decisions. It has not yet shown that these structures yield useful
knowledge or positive transfer; the acquisition experiment could address that,
and its metric and memory-removal conditions are now pinned — it is
pre-registered and not yet run.*

The lesson is recorded as `AGENTS.md` rule 24: **a claim must be no wider than
the check behind it, and the summary is where the widening happens.** The
measurements were right and the *headlines* were wrong, and a wrong headline is
invisible in a diff — it looks exactly like a right one. Propagated to the
README, the Phase L synthesis (§2.2, §2.3a, §3.3, §8), the V1 synthesis
(§2.2, §3, §5, §9), the audit-trace specification (§10, §11), the emergence
criteria (§4), the manual (§2, §8.18, finding 24, six common misreadings), the
facts sheet (§AB1–§AB7) and the journal (§50).

### Result — Phase L primary axis (V1): a reproducible crossing, and a criterion that did not pass

The Phase L campaign ran its primary axis to completion: **80 of 80 cells**,
8,057.8 s wall clock, 10 seeds per sweep point, `PYTHONHASHSEED=0` pinned and
recorded as the *actual* value, 99.00% decision interval, 10,000 bootstrap
replicates, against the frozen `v0.9.0` engine (verified unchanged by the
freeze test). **All four instrument audits passed on the live run**, and **no
cell was unmeasurable** — nothing was excluded and nothing was zeroed.

**Verdict: `H3-L — INCONCLUSIVE`.** The protocol's remedy for that verdict is
*raise n; conclude nothing*, and **no Phase L outcome authorises a V2** — the
secondary arms V2–V5 were deliberately not run.

| Label | DI (sd) | PI (sd) | DS | Latency | Seeds reaching DI > 0.5 |
|---|---|---|---|---|---|
| 1:4 | 0.000 (0.000) | 0.789 (0.078) | −0.789 | — | 0/10 |
| 1:3 | 0.000 (0.000) | 0.794 (0.070) | −0.794 | — | 0/10 |
| 1:2 | 0.000 (0.000) | 0.783 (0.096) | −0.783 | — | 0/10 |
| 1:1 | 0.000 (0.000) | 0.728 (0.055) | −0.728 | — | 0/10 |
| 2:1 | 0.283 (0.124) | 0.600 (0.122) | −0.317 | — | 0/10 |
| 3:1 | 0.722 (0.037) | 0.022 (0.039) | +0.700 | 347 | 10/10 |
| 4:1 | 0.739 (0.064) | 0.000 (0.000) | +0.739 | 285 | 10/10 |
| 6:1 | 0.750 (0.029) | 0.000 (0.000) | +0.750 | 236 | 10/10 |

**Three of the four pre-committed criteria are met.** DI is monotone increasing
with range 0.750; the curves cross at **3:1**, interior to the sweep; and the
crossing is reproducible under a paired bootstrap over seeds — interval
**[5.0, 5.0]**, **10,000 of 10,000** replicates finding a crossing, eight
alternative bootstrap seeds all `INTERIOR`, leave-one-seed-out 3:1 in **10 of
10** folds.

**Criterion 2 — *PI is monotone decreasing* — was not met.** Mean PI rises
0.789 → 0.794 between 1:4 and 1:3 (+0.005, against a per-point standard
deviation of 0.070) before falling monotonically through the rest of the
sweep. The criterion has no noise clause: it is evaluated on the mean curve,
and the mean curve rises. It was evaluated once by the committed code and it
failed; it was **not** re-read, relaxed, or reinterpreted afterwards, and the
stable RT was not allowed to stand in for the criterion that failed.

**A wording defect in the protocol is recorded rather than exploited.** The
`H3-L` bucket is described as *"intervals too wide to place RT"*, which is not
what happened — the RT interval is the narrowest possible and criterion 4
passed comfortably. The verdict is INCONCLUSIVE because criterion 2 failed, not
because the threshold could not be located. The next phase must say what
"inconclusive" means when the interval is narrow and a different criterion
failed.

**Established:** the instrument works and the pilot's flat line was an
artifact; the organism sits at the preservation pole (DI exactly 0.000, PI ≈
0.79) under low displacement pressure; on this axis DI and PI cross at 3:1 and
the crossing is highly reproducible. **Not established:** a boundary in the
`H2-L` sense, PI's monotone decrease, anything about capability, and anything
about the support ratio being *the* operative variable beyond this axis on
this engine.

Added `docs/phase_l_results.md` and the artifacts `docs/phase_l_results.json`
and `docs/phase_l_results.ndjson`. Journal §38, facts sheet §X, manual §8.10
and finding 15.

### Result — Phase L raise-n (n=30): the verdict stands, and the reason is now visible

The raise-n campaign finished: **240 of 240 cells**, 30 seeds per point,
12,738.1 s, `PYTHONHASHSEED=0` pinned and recorded as the actual value,
99.00% decision interval, against the frozen `v0.9.0` engine. All four
instrument audits passed on the live run and **no cell was unmeasurable**. It
is a strict **superset** of the n=10 run — the original ten seeds are the
first ten of the new list, so the 80 original cells were **reused, not
recomputed** — and the reuse was verified: all 80 are byte-identical in the
merged file.

**Verdict: `H3-L — INCONCLUSIVE`, unchanged — and now with TWO of the four
criteria unmet.**

| Criterion | n = 10 | n = 30 |
|---|---|---|
| 1. DI monotone increasing | **met** | **not met** |
| 2. PI monotone decreasing | not met | not met |
| 3. DI range ≥ 0.25, crossing interior | met | met |
| 4. RT interval excludes both endpoints | met | met |

**The Revision Threshold did not move:** still 3:1, interval **[5.0, 5.0]**,
**10,000 of 10,000** replicates finding a crossing, eight alternative
bootstrap seeds all `INTERIOR`, leave-one-seed-out at 3:1 in **30 of 30**
folds. Tripling n did not move the one quantity the phase set out to locate.

**The curve is a step function, not a ramp.** DI is **exactly 0.000** at
1:4–1:1 for all 30 seeds; **PI is exactly 0.000** at 4:1 and 6:1; DI ≈ 0.71
across the top; two sharp transitions in between. Revision latency goes from
**0/30** seeds reaching DI > 0.5 at 2:1 to **30/30** at 3:1 (mean 356 cycles,
median 351).

**Both failing criteria fail on steps whose 99% paired interval contains
zero** — +0.011 [−0.026, +0.044] at 1:4 → 1:3, and −0.007 [−0.037, +0.022] at
4:1 → 6:1 — while every step whose interval excludes zero is a real
transition. **A criterion that flips when n changes is measuring the draw,
not the organism:** resampling the 30 measured seeds, criteria 3 and 3b hold
in **100%** of random subsets, criterion 1 in 19.3% / 16.1% / 0%, criterion 2
in 12.0% / 6.6% / 0%, and **all four together in 2.9% / 1.2% / 0%**. Strict
monotonicity is not a property this organism's displacement curve has at any
practical n, and more seeds cannot turn a plateau into a ramp — so "raise n"
is exhausted as a route to satisfying criteria 1 and 2. **This does not
re-score the protocol:** the verdict stands, no boundary is claimed, and the
four criteria stand as written.

**The added seeds moved the curve more than resampling should allow** — DI at
6:1 0.750 → 0.697 (p = 0.0022) and DI at 2:1 0.283 → 0.164 (p = 0.0103)
against random 10-vs-20 splits — so a **seed-exchangeability audit** with 30
fresh, non-consecutive, pre-declared seeds was run to tell non-exchangeability
from an unlucky draw. It is an instrument audit and produces no experimental
claim. **The seeds are exchangeable**: the fresh scattered set gave DI 0.7241
at 6:1 against the campaign's own 0.7148 (30 seeds) and 0.7500 (its original
ten) — a difference of +0.0093, **p = 0.60** against random 30/30 splits of
all 60 measured values — and its own arbitrary half-split gap of **−0.0407**
has the opposite sign to the campaign's +0.0528 at similar magnitude. **The
original ten seeds were an unlucky high draw, not a seed-block artifact**, so
the paired bootstrap over seeds is sound.

`docs/phase_l_results.md` is rewritten for the raise-n result; journal §39,
facts sheet §Y, manual §8.11 and finding 16.

### Result — Phase L characterization: regime behavior, and a verdict that did not move

The raise-n result has been read and **published as a characterization**:
[`docs/PHASE-L-SYNTHESIS.md`](docs/PHASE-L-SYNTHESIS.md). The protocol verdict
is **unchanged** — `H3-L — INCONCLUSIVE` — and the two are deliberately kept
as separate artifacts, the measurement record and the synthesis, neither
re-scoring the other.

> *Organica 1 does not appear to exhibit a continuous coherence–plasticity
> trade-off. It appears to exhibit regime behavior separated by a
> reproducible transition region.*

**What survived increasing n:** the preservation plateau (**DI exactly 0.000**
for all 30 seeds across 1:4–1:1), the transition region, the crossing at
**3:1**, the reproducible RT (**[5.0, 5.0]**, 10,000/10,000 replicates,
leave-one-seed-out 3:1 in **30 of 30**), and the abrupt latency shift
(**0/30 → 30/30** seeds reaching DI > 0.5 between 2:1 and 3:1). **What did not
survive:** strict monotonicity, which got *weaker* as n grew — exactly as
expected if it was never a property of the organism.

**Raising n is exhausted on this axis and will not be repeated.** The reason to
raise n was to distinguish *the tiny PI reversal is noise around an otherwise
monotone curve* from *the curve is genuinely step-shaped* — worlds that predict
differently. n=30 distinguished them: the low-end steps are each consistent
with zero, the plateaus are exact across all 30 seeds, and the monotonicity
criteria fail *more* firmly. The campaign was not failing for want of
precision; it was failing because the curve is not the curve the protocol
expected.

**The dangerous question, answered.** *A stable, reproducible threshold at 3:1
— that is a boundary, isn't it?* **It is not.** A threshold divides a continuum
only if the trade-off is a continuum; here the curve is flat on both sides of
the crossing, and the crossing is stable because the organism **switches
regimes**. That is a real property of the measured system, and it is not the
property the protocol asked for.

**What comes next.** **V2–V5 remain unrun** — no Phase L outcome authorises a
V2. The secondary axes are now a more specific question than the one Phase L
was written to ask: not *which variable moves a smooth boundary*, but **why is
the curve step-shaped** — what sets the width and location of the transition
region.

Added `docs/PHASE-L-SYNTHESIS.md`; manual §8.12 and finding 17; facts sheet
§Z; journal §40.

### Added — the development audit trace specification (Phase M groundwork)

The specification for a **developmental auditability** record: the artifact
that would let an investigator reconstruct *why* a structure survived — what
evidence was used, how the claim was formed, what the competing candidates were
— **without asking the system**. Written against the frozen engine's **actual**
report fields and persistence limits, source-read on 2026-10-25.

**Level 1 (provenance) is available.** `get_ancestry()` reads parent links that
are already stored; the limits are depth 7 and the 4,000-event window, and a
parent outside the window means *not found in window*, never *no parent*.

**Level 2 (evidence) is available, with one correction.** `support_count` counts
**temporal transitions**, and `contradiction_count` is the subject's **competing
flow** — not a count of observations that contradicted the claim. The record
format as first proposed ("12 supporting observations, 4 contradictory
observations") would have put a false claim at the center of the audit and is
corrected in the spec.

**Level 3 (selection) is available without instrumenting the engine.** The
report contains only survivors, but under the default `salience` policy the
whole contest — including candidates culled by the confidence rule and
candidates that lost on rank — is reconstructible from the report's own Layer-2/3
outputs plus the persisted priors. The plan is therefore **assembly, not
instrumentation**; a labeled observer build is the fallback, and it must prove
that recording the trace leaves the engine's outputs unchanged.

**Counterfactuals live behind a wall.** *"Candidate B would have survived
without A"* is a **replay**, not a trace: a separate run, a separate artifact,
its own label.

**Six acceptance criteria** for the eventual build, each able to fail:
evidence-replay exactness, selection-reconstruction exactness, ancestry honesty,
behavior invariance, field-honesty, and trace/counterfactual separation.

**Two defects disclosed, neither patched** (Organica 1 is frozen):
`contradiction_count` is easy to misread, and the temporal graph's lookback
window has **no `event_type` filter**, so a supporting transition can originate
from the organism's own previous sleep payload while co-occurrence and
tag-frequency edges are world-scoped.

Added `docs/AUDIT-TRACE-SPEC.md`; manual §8.13 and finding 18; facts sheet §AA;
journal §41; AGENTS.md rule 17.

**And the specification's load-bearing claim was tested.** `benchmarks/audit_trace_probe.py`
is an **instrument probe, not an experiment about the organism**: it runs the frozen engine on
the frozen cause-world generator and, at every cycle, rebuilds the selection contest from
the report and the substrate and compares. **Default arm** (the engine's own belief cap of
15): **120 cycles, 1,412 beliefs checked, A1 evidence replay 0 failures, A2 selection
reconstruction 120/120 cycles.** **Stress arm** (cap 5, so the cap binds): **60 cycles, 290
beliefs checked, A1 0 failures, A2 60/60 cycles, 403 candidates lost on rank.** The default
arm alone was a weak test — its pool peaked at 12 against a cap of 15, so the
*lost-on-rank* branch never fired — which is why the stress arm exists and why the write-up
says so. **The checks can fail:** `tests/test_audit_trace_probe.py` breaks the auditor on
purpose and requires A1 and A2 to go red, and they do. **So the selection contest needs no
hook inside the engine** — assembly, not instrumentation. What is *not* established:
generality, the `stochastic` policy, the four remaining acceptance criteria, or anything
about learning.

Added `benchmarks/audit_trace_probe.py`, `tests/test_audit_trace_probe.py`, and the artifacts
`docs/audit_trace_probe.json` and `docs/audit_trace_probe_stress.json`; spec §10; facts sheet
§AA8.

### Added — the rule that keeps the audit trace from becoming a second inventory

An audit layer is attractive, and attractive things become projects. The trace
could have been built, extended and admired without ever adjudicating a question
the project wanted answered — which would make it a *second* inventory
("how many events resolve?"), and would swap one measurement habit for another.

**So the rule is pre-committed, not aspirational:** the next protocol's success
criteria must contain at least one **trace-derived diagnostic**, and a result
that fails it **fails the protocol even if the headline behavior is correct.**

**The first instance is a disqualifier: *a predicted-correct result whose
supporting evidence is self-sourced is not a transfer result.*** The trace
reports the world/self split of every belief's support, because the temporal
graph's lookback window has no `event_type` filter and a supporting transition
can originate from the organism's own previous sleep payload (D2). That is
D2's first concrete use, and it turns a disclosed defect into a **live
scientific instrument** — a defect that can defeat a claim is worth more than a
defect that is merely recorded.

**Second guard:** the trace's own metrics — evidence-trace completeness,
lineage completeness, selection reproducibility — are **diagnostics of the
instrument**: reported, never criteria. An audit layer earns its keep by
adjudicating a live question, not by accumulating completeness.

Added spec §11; AGENTS.md rule 18; manual §8.14 and finding 19; facts sheet
§AA9; journal §42.

### Corrected — the audit-trace probe's headline, and three errors in the specification

The probe's first version reconciled the **aggregate** `precedes` table against
the engine's reported support counts. That demonstrates the auditor reproduces
Organica's *counts* and its *selection decisions*; it does **not** demonstrate
that it can identify the individual experiences behind a count. The
specification claimed the stronger thing, and is now corrected to say exactly
what was measured: **aggregate evidence reconciliation and selection
reconstruction passed.** Event-level attribution is now its own acceptance
criterion (**A7**), measured with a passive store-time observer.

**Three corrections to the specification, each verified against the source
before being written down:**

1. A cycle returns **14** candidate lists, not 13.
2. The engine's lookback window **includes the event being stored** —
   `store()` inserts the row before recording edges — so the window is the
   event itself plus two others, and **within-event tag pairs also become
   temporal edges**. The first replay rule was wrong.
3. **A post-hoc replay from the final log cannot reconstruct the window**: the
   engine's query has no `rowid` tiebreak, and sleep-candidate rows are
   pruned. Event-level attribution therefore **requires** a passive
   store-time observer, whose guard must mirror the engine's own
   `event_type != "sleep"` rule.

**Results.** Default arm: A1 1,412 beliefs / 0 failures, A2
120/120 cycles, A7 1,412 beliefs / 0 failures with 244 aggregate
edges reconciling exactly. Stress arm: A1 290, A2 60/60, A7 290, **403 candidates lost on rank**. A4
behavior invariance passes — observer on and off produce byte-identical
reports apart from `ran_at`.

**D2 is now measured: 53,980 of 307,857 attributed support transitions (17.5%) are
self-sourced** — the prior event was the organism's own sleep payload. Roughly
one belief-support transition in six rests on the organism's own output. That
is the baseline the pre-committed disqualifier is read against.

**The probe found two defects in itself** — an observer that attributed
sleep-event transitions the engine never makes, and an invariance check that
compared a wall-clock timestamp — both caught by the checks rather than by
inspection. The generalisable lesson is now **AGENTS.md rule 17(d): an
aggregate is not an attribution; name the resolution of every check.**

### Corrected — the self-sourced figure's denominator, and the forced-tie arm

The probe's most quoted number — the share of self-sourced support — was
measured against the wrong denominator. It pooled the support of every reported
belief across every cycle in which that belief was reported; because a belief's
support count is **cumulative**, a transition that occurred early is counted
again in every later cycle where the belief survives. That pooled number counts
**support references**, not distinct evidence.

**Three views, kept apart** (default arm): **distinct evidence behind reported
beliefs** 802/4,481 = **17.9%** self-sourced — the disqualifier's figure;
**pooled support references** 53,980/307,857 = 17.5%; **all distinct transitions recorded**
5,436/12,583 = **43.2%**, including edges no reported belief ever rested on. Correcting
the denominator moved the headline only slightly (17.5% → 17.9%), and that agreement is worth
stating — but it surfaced a separate and much larger number: **43.2% of the organism's entire
distinct transition surface is its own sleep output**, against 17.9% of the evidence actually behind its
claims.

**The forced-tie arm is now run.** The engine's lookback query has no
tie-breaker, so the schema does not determine which rows a tied window selects.
The clock is patched so every four consecutive stores share a timestamp,
producing **479 stores with a genuinely tied window**; the observer reproduces the engine's
choice anyway and **A7 stays exact**. The honest statement: the *implementation*
is deterministic for identical queries over identical data, while the *schema*
still does not determine the window under a tie — the observer is the reason,
not a proof about the engine.

Added `docs/audit_trace_probe_tie.json`; the probe gained a `--force-tie` arm
and a distinct-evidence view; a seventh test requires the two views to stay
apart. Recorded in spec §3.3, §6, §10, §11; facts sheet §AA11; journal §44.

### Changed — the figure's population, and the disqualifier as a per-claim rule

**The 17.9% is a share of the union of the unique evidence transitions behind beliefs reported during
the run** — deduplicated, restricted to the edges those beliefs rested on. It is **not** a per-claim
share, and it is **not** evidence that self-sourced support caused an incorrect prediction.

**A run-level share cannot carry a per-claim claim**, so the disqualifier is now written against the
claim itself, in four conditions fixed in advance: report the world/self split for the **claim's own**
support; a **majority** of it must be world-derived; its self-sourced share must be **no higher than the
run's baseline rate** for beliefs; and the comparison is against the claim, never the organism in
general, with a failed condition **failing the protocol even if the prediction was correct**.

**The rule is conservative, and says so.** The contamination is **measured, not shown to be
consequential** — nothing yet shows that a self-sourced transition caused a wrong answer — so the
disqualifier is a statement about *what counts as evidence of transfer*, not a claim that the organism
is damaged by its own output. That is also why it is pre-committed: a criterion that only bites once
the harm is demonstrated would never bite at all. **Whether self-sourced support *hurts* is now a
measurable question**, and the trace is the first instrument that can ask it.

**The observer's window match is an implementation match, not a schema guarantee.** The engine runs
`SELECT tags FROM events ORDER BY time DESC LIMIT 3`; the observer runs the same ordering clause with a
wider projection, so the two are not byte-identical SQL. The match is empirical on the tested SQLite
implementation, and the evidence for it is **A7's exactness** — a window mismatch on any store would
have broken the reconciliation. The 60-cycle forced-tie artifact is committed as
`docs/audit_trace_probe_tie.json` (60 cycles, 479 tied windows, 0 mismatches).

Recorded in spec §3.3, §10, §11; facts sheet §AA12, §AA13; journal §45.

### Fixed — the acquisition pre-registration, after a review found five defects

**The pre-registration is now Revision 2**, committed before any cell is run. Five
defects in Revision 1 were found and corrected:

1. **The endpoint was the wrong metric.** Task support was scored with Phase L's
   `DI` — `late_structure_retained / late_structure_available` — which measures
   **structural displacement, not prediction**. Now a **ground-truth prediction
   score** on a fixed label set, with the exact predictions named, F1 at 0.5
   primary and balanced accuracy and Brier co-reported.
2. **"Source experiences removed" did not say what derived memory survived.**
   Ingest also accumulates `cooccurrences` and `tag_counts` (`memory.py:282`,
   `306`), which outlive the event rows. The condition is now named **"episode
   removal with learned graph retained"**, the retained set is listed, and **the
   same rows are removed from every learner's store** — which is what makes the
   comparison about reconstruction versus replay rather than about unequal
   access to evidence.
3. **The cell matrix was not specified.** Now **one complete table with the
   exact number of runs — 10 per seed, 30 seeds, 180 engine runs** — and a
   prediction for every cell, with `P-none × E-pres` stated as the untreated
   baseline rather than an extra cell on top of six.
4. **It was not an executable plan.** Now pinned: the generator and its
   parameters, the target relation, the phase boundaries (the regime switch lands
   exactly on the follow-up boundary), the seeds and sample size, the
   quantitative decision rule, and both baselines' algorithms, tuning grids,
   memory accounting and test-time procedures. **"Same memory budget", defined:**
   identical raw rows and identical removal for every learner, with derived
   state deliberately *not* equalised because derived state **is** the mechanism
   under test — and in the `E-pres` cells the comparison learners have strictly
   *more* usable access than Organica, so a win for Organica is conservative.
5. **The audit build had no stop condition.** Now explicit: **close A5 and A6
   only** (A1, A2, A3, A4 and A7 are closed and are not reopened), then **tag,
   freeze and stop** — no feature may be added to the instrumentation afterwards.

**Drift fixed in the same pass.** The README claimed every abstract structure
keeps parent links *"down to raw experience events"* — **the engine has never
done that**: the `parent_ids` chain terminates at Layer 1, and the
structure→event link is a count, not a pointer. The README's restatement was
corrected; **Law II of `docs/DESIGN_LAWS.md` is left as written** with the
discrepancy disclosed in the audit-trace specification as **D3**, because the
frozen engine's constitution is the owner's decision. Also fixed: the
specification's *"all six"* acceptance criteria where the table lists seven; the
manual's status table dated 2026-10-23 while the file recorded 2026-10-26 work;
and the missing **dated supersessions** in the README, `ROADMAP.md` and the V1
synthesis.

**The owner's standing decisions are recorded:** V2 **not cut**, live study **not
restarted**, V2–V5 **not run**, no further open-ended audit work. Sequence:
**finish the audit build → freeze it → run the acquisition experiment → compare
against the replay learner → publish whatever happens → only then discuss V2.**

### Added — the acquisition experiment pre-registration, and two diagnostics that changed its questions

The blank-slate question is now **can experience create a structure that
remains useful after the originating experience is gone?** — and **does the
organism carry structure forward, reconstruct it from evidence, or do both
under different conditions?**

**Two read-only diagnostics, run before the design was written, and
quarantined in the pre-registration as design inputs rather than
predictions:**

- A surviving structure's parent set is identical in **94.5%** of 3,883 structure-cycles.
- **But 87.2% of all 8,416 lineage links point at structures re-derived in that same
  cycle** (12.8% carried) — so the lineage is **re-derived, not carried**. This corrects
  an earlier reading of mine that called the identical sets "carried forward"; the
  link-state measurement is the discriminating evidence.

**The engine's survival rule is asymmetric across layers**, and this is the fact the
design rests on: `_natural_selection` (`sleep.py:1752-1802`) decays and prunes **Layer 1
only** — `_candidate_key` returns `""` for every other type — so Layer 1 survives only
if current experience keeps producing its content key, while Layers 2–4 are never
decayed and persist as rows with re-derived edges. **"Persistent reconstruction" is
accurate for Layer 1 and misleading for the rest.**

**The trace shows the present lineage, not the historical one**: a candidate's identity
is a content hash that does **not** include the parent set, and parents are recomputed
each cycle, so the same content identity can carry a different lineage later.

**The design:** six cells (parent {removed, not} × source experiences {removed, not} ×
removal applied to the **observer** or the **organism**, because removing a parent from
the auditor's reconstruction tests the trace and removing it from the organism's state
tests the maintenance mechanism). **Q1 (internal persistence) and Q2 (external
provenance) scored separately.** Three outcomes tracked separately and per cycle, so a
crossover is detectable. **The sharpest prediction is computed from the source, not
fitted**: pruning after `⌈log(0.15/c)/log(0.8)⌉` cycles — 4 from c=0.3, 6 from c=0.5. And
the decisive control is a **replay learner** that stores episodes verbatim and
regenerates nothing: if continuity is reconstruction rather than recall, perfect recall
is the *harder* baseline.

Added `docs/ACQUISITION-EXPERIMENT-PREREGISTRATION.md`; manual §8.16 and finding 22;
facts sheet §AA20–§AA22; journal §48; AGENTS.md rule 22.

### Added — A3: the ancestry measurement, and a correction it forced on the specification

**A3 is met.** An ancestry auditor walks each cycle's reported structures' parent
chains against the engine's own cognition window and classifies every branch
that fails to resolve. **Lineage reachability 1.000** (8,061 of 8,061
structures resolve back to Layer 1 within depth 7), **evidence linkage 1.000**
(1,412 of 1,412 claims resolve to event ids with a world/self split), **zero
honesty errors**, and an empty structure-level truncation split — while the
branch-level count shows **105 aged-out branches**, because every structure
resolves through at least one branch still inside the window. The stress arm
(3,240 structures) and the forced-tie arm (3,988 structures) both return 1.000.

**The correction.** Spec §12 said the window was "the more likely binding
constraint", because it spans only 1.7 cycles. **That was wrong.** Surviving
candidates are re-stored every cycle, so a live ancestor stays in the window
however old it is — **a lineage's depth is bounded by the death of an ancestor,
not by the window's recency.** Measured: the window holds 3,998 candidates, the
oldest last stored 1 cycle ago, content spanning 2 cycles. The correction is
recorded in place, not quietly fixed.

**The answer to A3's key question.** The observer's limit and the architecture's
limit are the same limit: **the engine's cognition window IS its memory.** An
investigator cannot recover more developmental history than Organica retains,
because there is no more to recover. That is good news for the trace and a hard
ceiling on the project's distinguishing property.

**Two sweeps prove the truncation categories are reachable rather than inert:**
the window sweep falls from 1.000 at the engine's window to 0.000 at 25–50
candidates (68 aged out); the depth sweep falls from 1.000 at depth 7 to 0.221
at depth 1 (53 depth-truncated) — so **the engine's depth limit of 7 is not
binding; the chains are shorter than it.**

**Two defects the build caught in itself**, both found by the checks rather than
by inspection: the observer matched `sleep:meta_concept` with a prefix test
that excluded every meta candidate (the engine uses an exact comparison), which
produced spurious "missing record" verdicts; and the window sweep sliced the
wrong end of a newest-first list. Both fixed, and the ordering is now pinned by
a test.

Added `A3_ancestry_honesty` to the probe's artifact; spec §13 and the §12
correction; manual §8.15 and finding 21; facts sheet §AA18–§AA19; journal §47;
AGENTS.md rule 21; `tests/test_audit_ancestry.py` (7 tests, four of them
proof-of-firing).

### Fixed — a threshold that judged its own data, and a window span that was wrong by an order of magnitude

**The transfer rule's reference rate is now frozen.** The third condition read
*"no higher than the run's baseline rate"* — circular, because a threshold
computed on the same data it judges relaxes whenever that run's beliefs happen
to be unusually self-sourced. The reference rate is now **17.9%**, fixed from
the calibration probe, **not recomputed on the evaluated run**, re-calibratable
only on data that is not being judged, and labeled a **provisional calibration
value, not a precise universal cutoff** (one run, one world, one policy).

**The window span was wrong by more than an order of magnitude, and is now
measured.** This project asserted the 4,000-event cognition window spanned
"roughly 40–130 cycles". That was a guess. **Measured: the engine stores 2,374.68 sleep events per
cycle, so the window spans 1.7 cycles.** The correction is recorded rather than quietly fixed. A lineage that keeps
being produced stays inside the window (candidates are re-stored every cycle);
one that stopped being produced is gone within about 1.7 cycles.

**A3's definition is fixed in advance**, reporting three things separately:
*lineage reachability* (extant structures resolving back to Layer 1 within
depth 7), *evidence linkage* (extant claims whose support resolves to event
ids with a world/self split), and a *truncation split* — **aged out** (a
persistence problem) / **depth-truncated** (a representation problem) / *no
parent* / **missing record** (a data defect). Level 1 (developmental lineage)
and Level 2 (evidential linkage) stay separate: **success in one cannot stand
in for success in the other.**

**And the boundary A3 cannot cross: fidelity is not sufficiency.** Reproducing
the implemented rule — exactly, and under a binding cap — does not establish
that the reconstruction is a uniquely correct account of *why* a belief arose.

Added spec §12; facts sheet §AA14–§AA16; journal §46; AGENTS.md rule 19; the
probe now reports `A7_event_level_attribution.cognition_window`.

**Fixed — seven literal template placeholders in the specification.** `{ties}`,
`{t_dist:,}`, `{t_edges}`, `{t_cycles}`, `{t_a1:,}`, `{t_a2}` (committed in the second
and third review rounds) and `{share:.1f}` (introduced by this round's script and
caught before commit) had shipped inside sentences that assert results. Corrected
in place from the artifacts: 479 tied windows, 2,589 distinct transitions, 241
aggregate edges, 60 cycles, 692 A1 beliefs, 60 A2 cycles, 692 A7 beliefs, 17.9%
reference rate. A placeholder is **silent** — it reads as a sentence in a diff —
so it is now caught by a standing guard — `tests/test_doc_placeholders.py` — rather
than by another careful read. Facts sheet §AA17; journal §46; AGENTS.md rule 20.

### Amendment 3 — the raise-n campaign on the primary axis

The n=10 run produced `H3-L — INCONCLUSIVE`, whose protocol-specified remedy
is *"raise n; conclude nothing"*. The owner took that remedy literally and on
the primary axis: **same sweep, same protocol, same criteria, no edits.**
Seeds per point go **10 → 30** (the original 10 plus 20 new), so the campaign
is a strict **superset** — the 80 original cells are reused, not recomputed,
and 160 new cells are added. Sweep points, independent variable, metrics,
decision interval, the four success criteria, the four terminal outcomes and
the frozen engine are **unchanged**; the secondary arms V2–V5 remain unrun.

**A real defect was found while preparing the run.** The preregistration says
criterion 4 is a *paired* bootstrap over seeds, but the implementation paired
by **position in the records list** — and the records arrive in completion
order, which differs from label to label. Position-pairing therefore paired
unrelated seeds across labels: an unpaired resample wearing the word
"paired" on it. Each label now contributes a `{seed: value}` map and every
label is evaluated on the same drawn set of seeds. **The fix does not change
the n=10 result** — RT 3:1, interval `[5.0, 5.0]`, 10,000/10,000 replicates,
eight alternative bootstrap seeds `INTERIOR`, leave-one-seed-out 3:1 in
10/10, the same four criteria, the same verdict — so the n=10 record is kept
as `docs/phase_l_results_n10.json` / `.ndjson`.

**A new diagnostic: the adjacent paired differences.** The monotone criteria
are evaluated on the **mean** curve and therefore test the **sign** of an
adjacent difference; if the underlying curve is flat at one end of the sweep,
that sign is a coin flip at any n. More seeds settle the **effect size**. So
each adjacent pair now reports its paired difference with a 99% paired
interval. It is a diagnostic only — not a metric, not a criterion, in no
verdict.

**The analysis is committed code.** `benchmarks/phase_l_analyze.py` replaces
the uncommitted scratch script that produced the reported numbers.

Amendment 3 was committed **before the raise-n run existed**. 69 tests pass;
the four instrument audits pass.

### The freeze

**Organica 1 is frozen as of the `v0.9.0` tag.** Not abandoned, and not
"no more commits" — **no more architectural modifications to the engine.**
The engine becomes a fixed reference object: everything afterwards *measures*
it, and nothing afterwards *quietly changes* it.

Frozen: `organica/sleep.py`, `memory.py`, `paths.py`, `streams.py`,
`branch_streams.py`, `scale_streams.py`, `ground_truth_worlds.py`, and the
published result artifacts. Still free: benchmarks, harnesses, all
documentation, the action list, and tests for new instrumentation. The one
boundary rule: nothing may change the **behavior** of the frozen engine.

**The freeze is enforced, not declared.** `tests/test_v1_freeze.py` reads the
frozen files out of the `v0.9.0` tag and compares them against the working
tree, failing and naming the difference if one differs, and skipping honestly
when the tag is not reachable. It was proved to fire by temporarily modifying
a frozen file and watching it fail. See `docs/V1-FREEZE.md`.

### Added — Phase L: Plasticity–Coherence Measurement

Phase L is not a benchmark hunt. Every previous phase asked *"can Organica do
X?"*; this one asks **how much pressure is required for new structure to
displace old structure?**

The protocol is frozen in
[`docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md`](docs/PHASE-L-PLASTICITY-COHERENCE-PREREGISTRATION.md)
and was committed **before any Phase L outcome was generated**.

| | |
|---|---|
| **Hypothesis** | Organica 1 exhibits a measurable coherence–plasticity boundary; revision occurs only after a displacement threshold |
| **Primary axis** | support ratio (late : early), 8 points — the axis the K3 2×2 already located |
| **Secondary axes** | arrival timing, novelty density, belief-cap pressure, contradiction pressure — each swept **one at a time** |
| **Displacement Index** | `late_structure_retained / late_structure_available` |
| **Preservation Index** | `early_structure_retained / early_structure_original` |
| **Revision Threshold** | the pressure at which DI crosses PI — the headline quantity |
| **Success criterion** | a **reproducible displacement curve**, not a win: DI monotone up, PI monotone down, an interior crossing, and a bootstrap interval excluding both endpoints |
| **Terminal outcomes** | four, pre-committed — **none of them authorises a V2** |

The instrument audits are permanent and required. A **discrimination control**
must show that first-seen-wins scores DI ≈ 0 / PI ≈ 1 and last-seen-wins
scores DI ≈ 1 / PI ≈ 0, so the metric can tell "never revises" from
"always revises". An **endpoint ceiling check** must show a perfect model
scoring 1.0 on both indices. A **degeneracy audit** must show the design
itself is live: that every cell has a denominator to measure against, that
the support ratio actually changes the early/late event mix, that the
contradiction arm produces a different world from the plain arm, and that the
density arm actually changes the event count. The campaign does not run if any
of them fails.

**Launch is not run.** The protocol is written, the harness is built and
validated, and the protocol is reviewed before the campaign executes.

### Fixed — four harness defects found by the Phase L pilot

The reduced-scale pilot returned `DI = 0.000` at **every** point of the
support-ratio sweep — a clean-looking negative result that was in fact an
artifact. The support ratio was not varying anything. Four defects, all in
the harness's implementation of the protocol as written:

1. **The late group arrived after the run ended.** The arrival cycle was
   absolute rather than a fraction of the run, so at reduced scale the late
   group never became active and the late structure was never available to
   measure. Arrival is now proportional.
2. **An unmeasurable index was reported as `0.0`.** A ratio with a zero
   denominator was reported as "nothing was retained" for conditions in which
   nothing was available to retain. Undefined ratios are now `None`,
   excluded from the curve, and counted — never zeroed.
3. **The contradiction arm was a no-op.** It shared a feature of the late
   group with itself, producing a byte-identical world with the arm on and
   off. The shared feature now comes from the early group, so the two groups
   actually compete for the same subject.
4. **The density arm fed the engine only part of the world.** The event
   stream was chunked at a fixed rate while the density arm varies it, so at
   density 4.0 the engine saw 7,200 of 28,800 events while the harness
   reported a complete run. The world's own event rate is now used.

Also corrected: the Revision Threshold bootstrap was resampling the DI−PI gap
rather than the **crossing location** that criterion 4 is about, and was
reporting a min/max rather than the preregistered percentile interval. Seeds
are now resampled paired across labels, and "excludes both endpoints" is
tested directly against the sweep.

Recorded as **Amendment 1** in the preregistration, made before any Phase L
outcome existed. No hypothesis, variable, metric, baseline, success criterion
or terminal outcome was changed, and no gate was relaxed — one audit was
added.

### Changed — the Phase L decision interval is 99%, not 98.33%

The Phase L protocol stated a **98.33%** decision interval and glossed it as
"Bonferroni across the arms". Those disagree: across five arms Bonferroni
gives 0.05/5 = 0.01, i.e. a **99%** interval, while 98.33% corresponds to
0.05/3 — Phase K's correction factor, carried over by accident.

**The owner's ruling, made before any Phase L outcome existed: the intent
governs and the stray percentage is the accidental constant.** The procedure
is preserved and the number is corrected to 99%. Phase K's own 98.33%
figures are unaffected — that protocol had three families and 0.05/3 was
correct there. Recorded as **Amendment 2**.

Amendment 2 also adds a plain statement of what success and failure look
like (preregistration §6.1): success is a stable displacement curve with an
interior, reproducible crossing; failure is a flat DI, a flat PI and no
crossing — a characterization, and a publishable one. **The campaign must be
able to fail.**

### Added — the two preregistered secondary outcomes the harness was missing

The protocol declares three secondary outcomes. The harness computed only
"absolute late incorporation"; **revision latency** and the **knowledge
preservation trajectory** are now computed from a per-cycle DI/PI trace taken
as the engine runs. The trace is per-cycle rather than cumulative, so it
answers *when did the organism start asserting the late structure*; the final
indices are still computed from the last report alone and the trace does not
change them.

### Fixed — a false record in the results file

The results file recorded `"python_hash_seed": "0"` unconditionally, asserting
the pinned value whether or not it was set. It now records the **actual**
value, records whether the pin was met, and warns loudly when it was not.

---

## [0.9.0] — 2026-10-24

**The project question changed: from *can we make a developmental
architecture?* to *what class of problems benefits from one?* Phase K opens
the search for that task.**

### The reasoning

Phases H, I and J were three preregistered attempts to show an external
advantage and all three were negative. That is not the same statement as
*V1 failed*:

> V1 develops interesting internal structure. We do not yet know what
> problem that structure solves.

Three tasks were negative; an infinite number of tasks were not tested. So
**no V2** — the design of a successor architecture cannot be justified while
the advantage it would provide is unknown. Designing V2 first would make V2
guesswork.

### Added — Phase K: Comparative Advantage Search

A **search**, not a test. The question is *what is Organica uniquely good
at?* Three candidate task families, each derived from a mechanism the
project has actually measured, each scored against the strongest simple
baseline that could plausibly solve it.

| Family | Mechanism it targets | The baseline that could beat it |
|---|---|---|
| **K1 — Incremental world modeling** | question generation drives novelty assimilation | online co-occurrence, which won Phase H at 0.8000 vs 0.7041 |
| **K2 — Belief revision** | falsification and contradiction drive revision | change-point detection plus wholesale relearning, with a forgetting window |
| **K3 — Longitudinal knowledge integration** | dreams integrate beliefs into coherent structure (P4, SUPPORTED) | sliding-window co-occurrence, which must trade retention against acquisition |

The protocol is frozen in [`docs/PHASE-K-PREREGISTRATION.md`](docs/PHASE-K-PREREGISTRATION.md)
and was committed **before any Phase K outcome was generated**. Three things
in it keep the phase honest:

1. **The baselines get the tuning advantage.** Every simple baseline is swept
   over a declared grid and its *best* score is the number used. A strawman
   baseline is the most likely way to manufacture a false positive, and it is
   impossible by construction.
2. **The harness is validated before the campaign runs.** The Phase H
   held-out task is rerun through the same code, where Organica's loss is
   already known (0.412605 vs 0.504039). If the harness reports a win
   there, the campaign does not run.
3. **"No family confirmed" is a pre-committed terminal outcome.** Three more
   families ruled out is a publishable result, and it does not authorise a
   V2.

Decision rule: paired percentile bootstrap over ten seeds, **98.33%**
interval (Bonferroni across the three families), SUPPORTED only when the
interval for Organica − best simple baseline lies wholly above zero.
Attribution — whether the hypothesised mechanism is actually implicated — is
reported from a matched within-architecture ablation and is kept separate
from the success criterion.

**The pilot, disclosed.** The harness was run once at one seed and one tenth
of every cycle count before the protocol was frozen. Organica was behind the
baseline in all three families. That is one seed at ten per cent of the
protocol and it is **not evidence**; it is recorded in the preregistration
so it cannot later be mistaken for a result.

### The result — the search failed, and that was pre-committed

The campaign ran to completion: **ten seeds per family**, thirty in total. All
three families came back **REVERSED**.

| Family | Organica | Best simple baseline | Paired difference | 98.33% interval | Verdict |
|---|---|---|---|---|---|
| K1 — incremental world modeling | 0.5923 | 0.9360 | −0.3437 | [−0.3773, −0.3123] | **REVERSED** |
| K2 — belief revision | 0.4111 | 0.9846 | −0.5735 | [−0.6162, −0.5309] | **REVERSED** |
| K3 — longitudinal integration | 0.0000 | 0.8578 | −0.8578 | [−0.8598, −0.8571] | **REVERSED** |

No family is SUPPORTED and none is INCONCLUSIVE: every decision interval lies
wholly below zero, so these are clean losses rather than ambiguous ones. Every
verdict survives eight different bootstrap seeds and both leave-one-out
checks. The **H2** terminal outcome fired exactly as written down before the
run: three more task families are ruled out, the negative-results map grows,
and **no V2 is designed**.

**The ablations came back empty — a negative attribution.** `NO_QUESTIONS`
(K1) −0.0095 [−0.0328, +0.0140]; `NO_FALSIFICATION` (K2) +0.0241 [−0.0048,
+0.0495]; `NO_DREAMS` (K3) +0.0000 [0.0000, 0.0000]. All three intervals
contain zero, so the three mechanisms the families were built around are not
load-bearing for the tasks they were meant to carry. This is within one
implementation on synthetic worlds, and it does not say the mechanisms are
inert in general.

**The K3 zero was root-caused, not assumed.** Organica scored exactly 0.000
on late incorporation on all ten seeds while a trivial co-occurrence counter
reached 0.857, so three artifacts were checked — each capable of failing.
The late structure appears in **zero of 150 cycles**, so it is not an artifact
of reading only the final cycle. Every candidate type except `anomaly` mentions
**zero of 12** late tags, so no late structure was left unread by the edge
extractor. And a 2×2 control across five seeds shows the late group is
incorporated **only when it is strictly stronger** than the group that arrived
first — so the exclusion is a salience/priority competition under a bounded
belief pool, not a blanket inability to learn late structure. This is the risk
§6 of the preregistration named before the run.

### Added

- `docs/V1-SYNTHESIS.md` — **the formal synthesis of V1.** What the project established, what it did not, the distinction between the two goals it could serve, the danger of reading six negative task families as a verdict rather than a map, and the question the evidence leaves open: *what properties must a developmental intelligence have to remain adaptable without losing coherence?* It adds no new evidence — it is a reading of the record, and every claim in it cites a committed artifact.
- `docs/phase_k_results.md` — the Phase K write-up: results, robustness, the
  K3 root cause, and what it changes.
- `docs/phase_k_results.json` — the campaign artifact: protocol block, the K0
  control, the ceiling check, all thirty per-seed records with every model's
  score and configuration, and the per-family summaries.
- `docs/phase_k_results.ndjson` — the live recording, one line per completed
  seed, appended and flushed.
- `benchmarks/phase_k_diagnose.py` — the K3 root-cause diagnostics: the
  per-cycle check, the under-read check, and the arrival-order × strength 2×2
  control.

### Changed

- The package version is **0.9.0**, cut on master; **0.8.0 is the latest
  release**. 0.8.0 was a research-integrity release: corrected clone
  verification, corrected version/tag semantics, the missing campaign
  artifacts regenerated, the cycle-1 fixation claim corrected (journal
  §31), the negative external-validity results recorded, and the
  documentation synchronised with the measurements.
- Journal §32 records the strategic shift and the negative-results map;
  **§33 records the Phase K result**, its robustness, and the K3 root cause.
- Facts sheet **§T** records the result in the one-fact-per-line form.
- The manual's status row for Phase K, its command list, its file map and its
  revision log are updated in the same turn as the change they describe.

---

## [0.8.0] — 2026-10-24

**The external-validity arc: three preregistered campaigns asking whether
Organica's structure buys anything over trivial baselines. The honest
answer recorded here is negative.**

Full detail in research journal §24–§30 and in
`docs/PHASE-H-PREREGISTRATION.md`, `docs/REGIME-SHIFT-PREREGISTRATION.md`,
`docs/PHASE-J-ADAPTATION-PREREGISTRATION.md`.

### Corrected — the structural plateau is dominant, not perfect

**0.7.0 said "the structure is decided on cycle 1" and that every colony
"holds that configuration for 2,999 cycles". The first half is right; the
second was an overstatement, and it is corrected here.**

Regenerating the Tier-1 artifact to produce `docs/discovery.json` meant
checking every published claim against the regenerated file. Measured cycle by
cycle:

| Colony | cycles at 18 beliefs / 7 subjects | of the tail half | last excursion |
|---|---:|---:|---:|
| FULL | 2,964 / 2,999 (98.8%) | 100% | cycle 212 |
| SALIENCE | 2,984 / 2,999 (99.5%) | 100% | cycle 221 |
| NO_CONTRADICTIONS | 2,957 / 2,999 (98.6%) | 100% | cycle 163 |
| **NO_QUESTIONS** | **2,277 / 2,999 (75.9%)** | **95.1%** | **cycle 2,738** |
| NO_DREAMS | 2,984 / 2,999 (99.5%) | 100% | cycle 185 |
| ANTI_EIG | 2,943 / 2,999 (98.1%) | 100% | cycle 539 |

The **retained** belief count is exactly 15 in every one of the 2,999 cycles of
every colony. The **pre-retention pool** is modal, not constant: it dips to 16
beliefs over 6 competing subjects and returns. The excursions are brief — 1–17
cycles in five arms, all over by cycle 539 — and they are real substrate
states, not a recording artifact.

**No launch gate is affected.** G-CS, G-P1, G-SUP and G-EXP hold in 100% of
cycles in all six colonies and G-SUS is 100% in every tail half, re-verified
from the regenerated artifact. G-P1/G-SUP need the pool to *exceed* 15, and 16
does. The verdicts, the noise floor, the inventory totals and the +10,776%
support growth stand as published.

The exception is the interesting part: **`NO_QUESTIONS` is also the arm that
discovers the most** (112 items; 95% of them by cycle 977, 99% by cycle 2,167)
and the only arm still finding new items deep into the run. The five arms
whose structure stops moving are the five that stop discovering; the one arm
that kept discovering kept moving. One arm in one run — a correlation, not a
cause — but it points the same way as H24.

Full record: journal §31, facts sheet §S, `docs/FORCE-MATRIX-RESULTS.md` §2.

### The position this leaves

**No external-validity task tested has produced a win for Organica.** Being
precise about what that means:

- **Held-out prediction** — beaten by both baselines (0.4126 against 0.5040
  and 0.4851).
- **Structure recovery** — beats the temporal-transition-graph baseline in
  the clean and overlapping worlds, **loses to it in the stress world**, and
  loses to plain same-event co-occurrence in all three.
- **Regime-shift detection** — no family met its preregistered success rule;
  the cause-mixture comparison was inconclusive.
- **Post-shift adaptation** — both gates failed in both families, against
  baselines with far lower predictive loss.

That is not the same statement as *the architecture has been shown useless*.
These tasks score next-event prediction, detection delay, structure recovery
and adaptation cost, and none of them is what the eight-layer engine was
designed to win. But it is the honest reading of the evidence so far, and it
is recorded **before** any redesign rather than after one.

### Added — Phase H: external validity (preregistered)

Held-out next-event prediction, F1 on known training tags:

| Model | F1 |
|---|---|
| Organica (Generation-1 prediction candidates) | **0.4126** |
| First-order Markov | **0.5040** |
| Decayed temporal association | **0.4851** |

**Disclosure:** the prediction curriculum is deterministic and identical across
seeds, so Organica's F1 is exactly 0.4126 and the Markov baseline's exactly
0.5040 in all ten seeds. The intervals there are degenerate, and they are
reported as degenerate rather than smoothed into significance.

Structure recovery against hidden cause-pair ground truth, mean F1 over the
ten seeds (range in brackets):

| World | Organica | Same-event co-occurrence | Temporal transition graph |
|---|---|---|---|
| clean | **0.7041** [0.667–0.750] | 0.8000 | 0.1482 |
| overlapping | **0.5469** [0.449–0.628] | 0.7642 | 0.2199 |
| stress | **0.1091** [0.097–0.159] | 0.7959 | 0.2803 |

Organica beats the temporal-graph baseline in the clean and overlapping
worlds and **loses to it in the stress world** — 0.1091 against 0.2803. It
loses to plain same-event co-occurrence in all three. The league is a
three-level stress test, and Organica degrades faster than either baseline
does.

### Added — Phase I: preregistered regime-shift detection

No primary success rule was met in either generator family.

- **cause-mix** — Organica's mean detection delay was **2.55** cycles,
  against **2.80** for the Markov baseline and **4.25** for decayed
  association. The paired advantage for the Markov baseline is 0.25
  cycles, 97.5% CI **[−0.25, 0.75]** — inconclusive. Organica's
  false-alarm rate is **0.0**.
- **mapping-swap** — the baselines are **faster** (Markov **1.25**,
  decayed **1.20**, against Organica **2.65**), and their **15%**
  false-alarm rate breaks the 10% gate while Organica's is **0%**. The
  benchmark is flagged invalid for this family, and the comparison is
  reported with that caveat attached.

### Added — Phase J: gradual post-shift adaptation

Both gates failed in both families.

| Family | Organica adaptation cost | Markov | Decayed |
|---|---|---|---|
| cause-mix | **2.497** | 0.178 | 0.122 |
| mapping-mix | **2.727** | 0.442 | 0.276 |

Final-stable NLL gap: **+4.478** / **+4.500** (cause-mix) and **+3.617** /
**+3.796** (mapping-mix). A clean negative result.

### Added — extended burst horizons, and the scaffold ladder

The burst curriculum was carried to longer horizons:

| Horizon | Baseline inventory | Burst inventory | Bursts delivered | Assimilation efficiency |
|---|---|---|---|---|
| 600 cycles | 91 | **119** | 19 | 1.474 |
| 1,200 cycles | 91 | **128** | 39 | 0.949 |

**Assimilation efficiency decays** — 2.44 → 1.474 → 0.949 items per burst —
so the mechanism's yield falls as the run lengthens even while the
cumulative total still climbs. At 1,200 cycles the burst arm added 8 items
between cycles 601 and 1200 and 2 in its final 100 cycles, reaching 128
against a preregistered 140+ progressive-expansion band. Neither unbounded
expansion nor a stable attractor is established; the reading is recorded as
*intermediate*.

The 300-cycle scaffold ladder, at 91 for the repeating baseline, gives 94 /
93 / 95 for the slow / medium / fast scaffold variants over 24 / 51 / 186
distinct event strings — scaffolding holds the inventory roughly flat
where uniform scaling collapses it.

### Changed

- **The live study is PAUSED** at the owner's direction, after continuous-run
  cycle 1032 (global `sleep_cycle` 5396). The pause marker is in the
  append-only log, the `INTERVAL` override was removed, and there is no
  scheduled restart. The organism did not experience the missing wall-clock
  time, and the write-up says so.
- The package version is **0.8.0**, and this release is the one that
  carries it. Master had drifted past the `v0.7.0` tag while still
  declaring 0.7.0, so the version number was naming a release that master
  was not.

### Fixed

- `tests/test_versioning.py` failed in a **fresh clone**. `clone_check.py`
  clones with `--depth 1`, which fetches only the tags pointing at the
  commit it fetched, so a release tag on an ancestor commit was absent
  locally and the test asserted against an empty tag list. The check now
  consults the remote when the checkout is shallow, and a full checkout
  with no tag still fails exactly as before.
- The version test now also fails when the version describes a commit the
  tag does not cover, which is the drift that let master sit past
  `v0.7.0` while still claiming 0.7.0.
- The local `master` branch had not actually been advanced past the
  overnight merges: a fast-forward had landed on a since-deleted PR branch
  instead, leaving `master` 13 commits behind its remote while the working
  tree still looked current. `master` is fast-forwarded and the three
  orphaned branches are gone.

### Known limitations

- Phase H's **prediction** scores are identical across all ten seeds, because
  the curriculum is deterministic; those intervals carry no information about
  seed variance. The **recovery** task does vary across seeds, and Organica's
  recovery F1 falls to 0.1091 in the stress world, below the temporal-graph
  baseline's 0.2803.
- Phase I and Phase J generalize only to their two predefined synthetic
  generator families, and Phase J's settling time is self-referenced to
  each model's own final stable loss, so it is descriptive, not
  confirmatory.
- Phase I's mapping-swap family has an **invalid benchmark** — the
  baselines' false-alarm rate is above the gate.
- The live study is paused and no restart is scheduled.

---

## [0.7.0] — 2026-10-23

**Ablation Study 2 — the Tier-1 matrix ran, and what it actually measured.**

18,000 colony-cycles: six colonies × 3,000 cycles, on the fixed substrate,
under a protocol whose metrics, gates, noise floor and sensitivity were all
fixed and committed *before* the run. The results are a scientific finding in
their own right and are published in `docs/FORCE-MATRIX-RESULTS.md` and
journal §23.

### The headline

**The structure is decided on cycle 1.** Every colony reaches 18
pre-retention beliefs, 7 competing subjects and 15 retained beliefs on the
first cycle and holds that configuration for 2,999 cycles, while mean support
grows **+10,776%**. All six arms converge to the *same* attractor despite
six different interventions. Structure flat, evidence growing by three orders
of magnitude.

> *Corrected in 0.8.0 — journal §31. "Holds that configuration for 2,999
> cycles" was an overstatement: the retained belief count is exactly 15 in
> every cycle, but the pre-retention pool is modal rather than constant
> (98.1–99.5% of cycles for five arms, 75.9% for `NO_QUESTIONS`). No launch
> gate, verdict, inventory total or noise-floor number changes.*

### The verdicts

**2 SUPPORTED · 3 REVERSED · 0 UNSUPPORTED · 0 NOT INTERPRETABLE**

| # | Prediction | Verdict |
|---|---|---|
| P1 | Retention policy affects development | **SUPPORTED** (M7: 212 vs 2,990 cycles) |
| P2 | Contradiction is developmental fuel | **REVERSED** — removing it *raises* development |
| P3 | Curiosity needs explicit questions | **REVERSED** — removing questions *raises* development |
| P4 | Dreams contribute to trajectory | **SUPPORTED** — removing them lowers it |
| P5 | EIG is orthogonal to development | **REVERSED** — lowest-EIG develops *more* than highest-EIG |

The verdicts are **direction-aware**. A naive "did the metric move?" test
would have scored all five as confirmed.

### A metric that was not a metric

M5 ("development velocity") is `new items ÷ run length`. The reference arm
discovered **74** items over 300 cycles and **74** over 3,000; the rate fell
from 24.667 to 2.467 because the numerator stopped growing. Every colony
discovered **zero** new items in its final 100 cycles. The inventory, broken
down by category, is the interpretable number: FULL 74 (16 beliefs, 11
questions, 36 dreams, 11 experiments) · SALIENCE 78 · NO_CONTRADICTIONS 79 ·
NO_QUESTIONS 112 · NO_DREAMS 44 · ANTI_EIG 85.

### A confound, disclosed

The stimulus **repeats every 9 cycles** — 9 distinct events over 7 distinct
words, seen 333 times. A repertoire cannot grow in a world that does not
change, so the plateau is consistent with *the organism exhausted the
environment*, which is not the same statement as *the organism cannot
develop*. The campaign cannot separate the two.

### The hypothesis this produced

**H24: Organica's apparent developmental plateau is primarily constrained by
environmental information content rather than by architectural inability to
reorganise.** Stated with the evidence on both sides and its falsification
criteria before the experiment that tests it. The next experiment is a
**world-complexity ladder** — a stimulus change, not an architecture change.

### The World-Scale Ladder & Burst Assimilation Findings (2026-10-23)

Immediate experimental testing of H24 during the 0.7.0 cycle revealed three
successive mechanistic insights that redefined the developmental narrative:

1. **Uniform scaling causes dilution collapse**: Multiplying distinct world
   triangles by 16× (3 → 12 → 48) collapsed inventory (91 → 66 → 56) and
   theories (10 → 4) due to frequency dilution in the `MAX_PREDICTIONS = 20`
   window.
2. **Scaffolding prevents collapse**: Maintaining a 3-triangle core scaffold
   prevented multi-layer degradation, preserving theories at 13–14 and
   stabilizing beliefs at 18.
3. **Burst reinforcement enables developmental assimilation**: Novelty requires
   local reinforcement to survive early-stage filters (`PREDICTION_MIN_COUNT = 5`,
   `STABLE_THRESHOLD = 0.3`). Introducing novelty in concentrated bursts
   drove cumulative inventory to **113 items (+24.2%)** across 300 cycles, with
   active discoveries continuing through epochs 2–5 (88, 10, 7, 2, 6, 0).
4. **Conclusion frozen**: *Organica's developmental capacity is not a fixed
   architectural constant. It is strongly dependent on the structure and
   presentation schedule of novelty.* Prior candidate ceilings (74, 91) were
   constrained measurements of environmental bottlenecks rather than hard
   architectural limits.

### Added

- `docs/FORCE-MATRIX-RESULTS.md` — the results, the verdicts, what the
  campaign can and cannot answer, and H24.
- `benchmarks/run_matrix.py` — the campaign launcher. Runs the G1
  verification once, launches the six colonies in parallel with the **same**
  `PYTHONHASHSEED=0`, and records the hash seed, git commit and wall clock
  in the artifact.
- `benchmarks/verdicts.py` — every pre-registered prediction forced into
  SUPPORTED / UNSUPPORTED / REVERSED / NOT INTERPRETABLE, direction-aware.
- `benchmarks/discovery_report.py` — the inventory breakdown and the
  cumulative discovery curves, plus the stimulus's own measured periodicity.
- `benchmarks/process_noise.py` — the process-level noise floor, with a
  parallel sweep and the scale-invariant item-count form.
- `organica/scale_streams.py` — worlds of increasing information content for
  the H24 ladder.
- `benchmarks/scale_ladder.py` — the ladder runner.
- `benchmarks/hub_degree_probe.py` — measures the Layer-1 survival threshold
  against hub degree.
- `docs/force_matrix.json`, `docs/discovery.json`, `docs/verdicts.json`,
  `docs/process_noise_3000.json`, `docs/figure_tier1_matrix.svg`,
  `docs/figure_discovery.svg`.
- Facts sheet §I (matrix results) and §J (H24).
- `docs/ORGANICA-V2-DESIGN-NOTES.md` §7–§10 rewritten with the matrix's
  answers and the new stimulus requirement.

### Changed

- `benchmarks/force_matrix.py` now records the per-cycle **discovery
  history** — new items and cumulative distinct items per category — so the
  inventory can be measured directly rather than inferred from a rate.
- `benchmarks/metric_sensitivity.py` gains the per-metric most-sensitive-
  colony ranking and a **downstream** deviation ranking that excludes each
  colony's own intervention metric.
- `benchmarks/v1_impact.py` excludes `None` metrics rather than zeroing
  them. The harness reports "n/a" for lineage completeness when a condition
  has no lineage; that is *not measurable*, not zero, and zeroing it would
  have been the same class of error as the scope defect the tool documents.
- The README now carries the research findings, the verdicts, and H24.

### Fixed

- `benchmarks/seed_noise.py` overclaimed: it measures the **within-process**
  seed floor (exactly 0.00), not the floor that binds. Disclosed in place.
- `benchmarks/figure_campaign.py` failed with a raw `KeyError` on an
  artifact predating the per-cycle series capture; it now says so.
- `benchmarks/run_matrix.py` and `force_matrix.py` print the G1 header even
  when verification is skipped.
- `organica/scale_streams.py` numbered its leaf tags (`ta0`), and the engine
  only extracts words of **four or more letters** — every leaf was silently
  invisible and the ladder measured nothing. The leaves are now spelled in
  letters.

### Known limitations

- The stimulus's 9-cycle period means the campaign cannot separate
  "exhausted the environment" from "cannot reorganise". H24 is untested.
- M7's spread rests on very few observations: the reference arm's
  212-cycle mean is the mean of **one** belief death. Reported as such.
- `NO_CONTRADICTIONS` removes contradiction's **weight in the confidence
  formula**, not contradictions. M3 is near-invariant for it by
  construction. The colony's name overstates the intervention; disclosed in
  the results document and the facts sheet.

---

## [0.6.0] — 2026-10-23

> **0.6.0 is the first release of this repository to carry a git tag.**
> The versions below were published to this repository without tags, so they
> are recorded here as history but cannot be checked out as named commits.
> The tag convention starts here: releases are tagged `v<version>`, and
> `tests/test_versioning.py` fails the build if the version has no tag.

**Milestone M0.5 — mechanism closure, and a substrate correction.**

This release changes the organism's behavior. It is a pre-1.0 release
because the public API is not stable, but the behavioral change is
real and is disclosed in full in `research-journal/phase_g_findings_20261021.md`
§21.8 and `docs/USER-MANUAL.md` §8.4.

### Changed — substrate

- **The tag-frequency counter is now scoped to world events.** It was
  maintained over every stored event, including the organism's own sleep
  payloads, while the co-occurrence and temporal graphs it normalises are
  built from world events only. The counter is the *denominator* of the
  Layer-1 edge strength (`ratio = count / source_freq`), so the two sides
  of the ratio measured different populations and the survival filter
  discarded the world's own structure. Measured: 4 surviving edges, 0
  processes, 0 workflows, 0 beliefs.
- A `meta` table records the scope the counters were built with, so a
  database written by an older build rebuilds its counter exactly once
  instead of mixing two populations in one table.

### Added

- `docs/FORCE-MATRIX-PREREGISTRATION.md` — M1–M9 frozen, plus the launch
  gates G-CS, G-P1, G-SUP, G-EXP and G-SUS.
- `docs/ORGANICA-V2-DESIGN-NOTES.md` — planning only: what survived
  scrutiny, what failed, what turned out inert, what turned out essential,
  what became a bottleneck, and the open questions.
- `docs/gate_validation.json`, `docs/mbsd_census.json`,
  `docs/mbsd_census_postfix.json`, `docs/gate_check.json`,
  `docs/freq_scope_probe.json`, `docs/metric_sensitivity.json`,
  `docs/force_matrix_pilot.json`.
- `organica/branch_streams.py` — branch-structured stimuli built from
  triangles, derived from the measured mechanism.
- Benchmarks: `gate_validation.py`, `mbsd_census.py`, `branch_sweep.py`,
  `branch_sweep2.py`, `branch_diag.py`, `branch_diag2.py`,
  `freq_scope_probe.py`, `gate_check.py`, `force_matrix.py`,
  `metric_sensitivity.py`, `seed_noise.py`, `v1_impact.py`,
  `figure_campaign.py`.
- `tests/test_substrate_equivalence.py` — a scope-consistency regression
  test: a sleep payload must change neither the temporal graph nor the
  frequency counter that normalises it.
- `tests/test_versioning.py` — the version declarations must agree, must
  be SemVer 2, must be pre-1.0, and must have a git tag and a changelog
  entry.
- `run_continuous.py` writes `freq_scope=world` in its build marker, so
  the append-only log says which substrate produced which cycles.

### Changed — research findings

- **The proposed Multi-Belief Subject Density gate is structural, not
  predictive.** Layer 5 forms exactly one theory per subject holding ≥ 2
  beliefs; the identity `theories == min(competing_subjects, MAX_THEORIES)`
  holds in 100% of cycles in 9 of the 11 conditions. The gate is restated
  as an absolute count.
- **The `r=4 / r=6 / r=10` "phase transition" was an instrumentation
  artifact.** With the counter scoped correctly, all three repeat counts
  behave identically: a full prediction window, a belief pool of 18, seven
  competing subjects, and 100% of tail cycles passing every gate.
- **"No Falsification freezes the organism" is withdrawn.** Post-fix it is
  the best-supplied condition in the study: 18 beliefs, 6 of 6 subjects
  competing, MBSD 1.000.
- **"The organism is supply-limited, not selection-limited" is withdrawn as
  a general statement.** It was true of the study stream on the old
  substrate; on a branch-structured stimulus the cap binds and the
  retention policy changes the population.
- Facts sheet D8b is **corrected in place**; D8c–D8e are added.

### Fixed

- The G1–G4 perturbation ladder caught a measurement reading the wrong
  report attribute and reporting a working layer as dead (previously
  corrected, recorded here for the release history).
- The campaign runner instantiated the instrument instead of the colony
  subclass, which made every colony run the default service and produced
  a byte-identical FULL and SALIENCE. The runner now asserts G1 — that
  each colony's intervention is in the code path — before running a
  colony.

### Known limitations

- The ablation study in `docs/ablation_study.json` was produced on the
  **pre-fix** substrate. Every condition ran on the same substrate, so
  the comparisons stand, but the absolute densities are not comparable to
  post-fix numbers. `benchmarks/v1_impact.py` produces the before/after
  audit (`docs/v1_impact.json`).
- One seed per colony. Deltas smaller than the measured seed-noise floor
  are reported as *not interpretable*. The floor is measured by
  `benchmarks/seed_noise.py`.

---

## 0.5.0 — 2026-10-21

- Phase G endurance work: monotonic sleep-cycle counter in the database,
  bounded candidate retention, the tag-frequency counter moved from a
  full-table scan to an incremental counter.
- `docs/USER-MANUAL.md` rewritten with 18 sections.
- `docs/FACTS-SHEET.md` — facts with provenance, separated from assumptions.
- `docs/GATE-BOARD.md` — what is demonstrated versus assumed.
- `benchmarks/clone_check.py` and a passing fresh-clone check.

## 0.4.0 — 2026-10-20

- Observation pipeline repaired; `MemoryService.batch()` added after
  profiling found one fsync per candidate dominated the cycle
  (1,023 commits = 3.0 s of a 4.5 s cycle).
- `benchmarks/cold_start.py` — the eight assistance levels.

## 0.3.0 — 2026-10-20

- The eight-layer engine, the four reproduction domains, the reproduction
  pack and the growth benchmarks.

## 0.2.0 — 2026-10-19

- The study daemon, the append-only log format, and the snapshot writers.

## 0.1.0 — 2026-10-19

- First public release of the substrate and the sleep pipeline.

[0.10.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.10.0
[0.9.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.9.0
[0.8.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.8.0
[0.7.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.7.0
[0.6.0]: https://github.com/nueraresearch/project-organica/releases/tag/v0.6.0
