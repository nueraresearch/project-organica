# Findings ledger — current claims, caveats and open constraints

**Status:** durable synthesis, **not a result**. Last updated 2026-11-11.

**Authority.** The cited artifacts and the research registry are authoritative. If this page
disagrees with either, the artifact/registry wins. This page exists so the current claim
scope does not depend on chat history, a context window or memory.

## 1. Persistence: established effect, localized failure, unresolved cause

**Established.** T1b established that removing carried temporal support reduces served and
asserted world edges under the tested conditions: shipped `S_ever` was 101, 95, 100, 103,
98 and 99 against persistence-off 0, 1, 0, 3, 0 and 3 (mean paired difference **98.167**,
95% interval **[96, 100]**), with all seven gates passing.

**Localized.** On the five zero-S_ever cells (T1 `20612204`, `20612205`; T1b `20612208`,
`20612210`, `20612212`), the failure occurs at **candidate formation**:

```text
reset
  -> within-cycle world-edge counts remain 1-4
  -> no world edge reaches floor 5
  -> no world-edge candidate exists
  -> S_ever = 0
```

The zero is created before ranking, admission or assertion can operate. On these cells those
downstream stages never receive a world-edge candidate. The diagnostic verdict is
**LOCALIZED**, not "mechanism solved."

**Boundary caveat.** `PersistenceOff` is **no carried support conditional on cycle
completion**, not a perfect no-memory condition. The reset fires when a processed event
completes an 8-event block; a withheld block-end event can suppress the reset. Positive
off-arm cells are therefore not necessarily a contradiction.

**Floor distribution — measured 2026-11-11.** The zero-cell maxima **4, 3, 4, 3, 4** and
control maxima **6, 6, 5, 6, 5, 6, 5** are maxima of a population, not its support. Across
the zero cells' **600** processed reset groups (all 4-8 events), the **14,279** edge-cycle
rows are **12,278** at count 1 (86.0%), **1,861** at 2 (13.0%), **136** at 3 (1.0%) and
**4** at 4 (0.03%); no row reaches 5. The same-group count, which excludes the engine's
lookback into the previous group, is also 1-4; cross-group lookback supplies **2,508**
pair observations (15.3%) and on seed `20612208` is what lifts the group maximum from 3
to 4. In the controls, **149** of **609** groups are longer than 8 events because a
withheld block-end event suppressed the reset; all **30** count-5+ rows occur in those
merged groups. Across the **1,060** groups of at most 8 events in both roles, the maximum
is **4**. The 1-4 concentration is therefore the support of short groups, not a separate
floor regime: floor 5 sits above that support, and counts 5-6 require the extra repetition
of a merged group, which no zero cell has.

**Window sweep is a counterfactual.** At window 6 the zero cells reach 8-9 on their best
edge and 61-69 edges at floor 5; 1,000 fixed-seed within-cycle permutations put the observed
maxima below the null p95 (5-6). That makes the ceiling **window-sensitive**, but it does
not establish a clean horizon treatment: an engine-lookback extension keeps persistent event
rows and reintroduces cross-cycle context. It is a different treatment family and needs its
own preregistration.

**Not established.** The group-length contribution is measured; the exact contribution of
the read floor, lookback horizon and world structure remains unresolved, as does any
mixture of them.

**Evidence.** `docs/t1b_persistence_off_run.json`, `docs/T1B-PERSISTENCE-OFF-RESULT.md`,
`docs/persistence_zero_served_diagnostic.json`, `docs/PERSISTENCE-ZERO-SERVED-NOTE.md`,
`docs/ceiling_diagnostic.json`, `docs/CEILING-DIAGNOSTIC.md`,
`docs/within_cycle_distribution.json`, `docs/WITHIN-CYCLE-DISTRIBUTION.md`, Q055 in
`docs/RESEARCH-FINDINGS.md`.

## 2. Assertion anomaly: the 26 asserted-but-never-served edges

Of **247** asserted world edges, **221** were served at least once and **26** never entered
a served window (10.5%). All 26 are transitions. Their best recorded rank runs **22-127**;
**10** sit inside the cap, but **0** sat inside the transitions actually served in the cycle
that ranked them, and the closest in-cap miss is **2** ranks short. By band: 1-20: 0;
21-40: 10; 41-80: 10; 81-112: 4; 113+: 2.

This is a **location, not a cause**. It rules out "the assertion step loses nothing" and
"inside the cap means served," but it does not identify an admission rule or an assertion
mechanism. It is also not a claim that serving those edges would have changed `A_W`.

**Provenance traced (2026-11-11).** A behaviour-neutral replay on the same six Q4 seeds,
120 cycles and cap 40 reproduces every seed's asserted-world fingerprint and committed
served-world set. It assigns the 26 rows in `docs/assertion_provenance.json`:

- **0 recording gaps.** The replay's served-world set equals the committed N3 set on every
  seed, and every direct edge has zero direct service in both records.
- **18 identity mismatches.** The direct edge was never served, but the same endpoint pair
  was served in the reverse orientation. The reverse is itself a world edge, and the
  loop/dream readout is symmetric, so this is an orientation mismatch in the direct record,
  not proof that the directed edge was served.
- **8 alternate assertion paths.** Neither orientation was served; loop/dream structures
  carry the edge independently of the prediction window.
- **0 genuine assertions without service.** No edge is carried only by a prediction
  candidate, so the prediction path supplies no assertion that service failed to provide.

All 26 rows have a non-prediction structural carrier. This is a **provenance classification
of the readout**, not a mechanism: it does not show why loop/dream structures carry those
pairs, whether serving them would change `A_W`, or whether the split holds on another world
family. See `docs/ASSERTION-PROVENANCE.md` and Q054.

**Carrier traced (2026-11-11).** A second replay on the same six Q4 seeds starts at the
carrier's candidate formation. All 26 rows have a loop carrier: **61** loop-candidate
occurrences, **58** 3-cycles and **3** 2-cycles. One row also has a dream co-carrier; no row
is dream-only. Every loop path contains the pair and `structure_edges` adds both directions,
so the 18 reverse-served rows and the 8 alternate rows reach the assertion by the same
symmetric loop readout. The direct edge is present in the temporal graph in every row at
count **23-47**, above the prediction floor, although **0** rows have a final prediction
source; the trace does not decompose the intervening rank/cap selection. First carrier
formations span cycles **37-117** (median **78.5**), and the loop builder requires a
minimum temporal edge count of **5**. This explains the loop/dream carrier path, not whether
serving the direct edge would change `A_W` or whether the split holds on another world
family. See `docs/ASSERTION-CARRIER-TRACE.md` and Q054.

**Fresh-block replication (2026-11-11).** A pre-registered six-seed block
(`20613101-20613106`) found **26** asserted-but-never-served edges: **24 identity
mismatches** and **2 alternate paths**, with **0** prediction residuals. The fresh
identity share **0.923** (95% Wilson **[0.759, 0.979]**) excludes the original
**0.692**, so the pre-specified verdict is **`DIRECTIONAL ONLY`**: the reverse
orientation remains the dominant path, but the **18/8** magnitude did not replicate.
Both alternate paths occur on one seed (`20613106`); five of six seeds have none.
The original 18/8 classification remains correct for its block. This does not show
whether service would change `A_W`. See `docs/ASSERTION-PROVENANCE-REPLICATION.md`.

## 3. Presence band: class-level result, separate named-edge ledger

**BAND-5 is `CONFIRMED` at class level.** Six fresh seeds (20612601-20612606), twelve cells
at 40 and 112, and one determinism rerun produced `docs/presence_band_rank_5_run.json`.
All **89 of 89** measured rank-21-40 edges are served at 112 and **0** at 40; B1-B8 pass,
with 64-68 transitions and 48 cooccurrences on every full cap-112 window.

This does **not** re-score or validate BAND-1's **62 named Q4 edges**. BAND-1 remains
**VOID**; its named-edge condition remains **unadjudicated**. The admission decision remains
**PENDING**. The exact 62 edges and the class-level allocation law are separate claims.

## 4. Working mechanism map — navigation, not a unified theory

```text
carry / decay
  -> eligibility (candidate formation)
  -> admission
  -> service
  -> assertion
```

The first links have evidence, but this is not a necessary single path. The 26 edges now have
a provenance separation: none is a recording gap, 18 are reverse-orientation mismatches and
8 are alternate loop/dream paths. The map is a way to place claims, not a claim that a
unified theory already exists; the remaining question is why loop/dream structures assert
those pairs.

## 5. Priority for information gain — judgment, not evidence

1. **Top information-gain priority — assertion provenance — carrier traced 2026-11-11.** The 26 edges are separated into 0 recording
   gaps, 18 reverse-orientation identity mismatches, 8 alternate loop/dream paths and 0
   prediction-only residuals. The carrier trace now shows the loop/dream formation path:
   61 loop candidates and one dream co-carrier, with all direct temporal counts above the
   prediction floor. The fresh-block replication is **directional only** (24 identity /
   2 alternate, original 18/8 magnitude outside the fresh interval). The next question
   is whether serving the direct edge would change `A_W`.
2. **The 1-4 count distribution — measured 2026-11-11.** It is the support of 5-8-event
   groups; 5-6 requires a merged group longer than 8. The next question is whether a
   nominal 8-event cycle can be made to carry more repetition, not another floor.
3. **BAND-2**: keep the governance block live, but it is less likely than the first two to
   produce a large jump in understanding.

This ordering is an owner/agent prioritization. It changes no verdict, gate, seed or status.

## How to update this page

Append a dated entry when a claim's scope changes; do not rewrite an older scope. Cite the
authoritative artifact or registry row. Do not add a cell, seed or result here. A new
measurement belongs in its own artifact and registry question; this ledger only preserves
the current reading.
