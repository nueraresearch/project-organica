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

**Floor distribution.** Within-cycle maxima on the five zero cells are **4, 3, 4, 3, 4**;
the seven non-zero off controls reproduce **6, 6, 5, 6, 5, 6, 5**. The population occupies
1-4 and floor 5 slices through it. The next distributional question is why the counts
concentrate there, not simply whether to lower the floor.

**Window sweep is a counterfactual.** At window 6 the zero cells reach 8-9 on their best
edge and 61-69 edges at floor 5; 1,000 fixed-seed within-cycle permutations put the observed
maxima below the null p95 (5-6). That makes the ceiling **window-sensitive**, but it does
not establish a clean horizon treatment: an engine-lookback extension keeps persistent event
rows and reintroduces cross-cycle context. It is a different treatment family and needs its
own preregistration.

**Not established.** The exact contribution of the read floor, lookback horizon,
cycle-boundary reset behavior and world structure remains unresolved, as does any mixture
of them.

**Evidence.** `docs/t1b_persistence_off_run.json`, `docs/T1B-PERSISTENCE-OFF-RESULT.md`,
`docs/persistence_zero_served_diagnostic.json`, `docs/PERSISTENCE-ZERO-SERVED-NOTE.md`,
`docs/ceiling_diagnostic.json`, `docs/CEILING-DIAGNOSTIC.md`, Q055 in
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

The anomaly is the main current constraint on the emerging pipeline because it suggests one
of three different things: a parallel assertion path, an incomplete served-window record, or
an identity/attribution mismatch. Those need to be separated before treating the 26 edges as
a single mechanism. See `docs/UNEXPLAINED-EDGES-NOTE.md`.

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

The first links have evidence, but this is not a necessary single path. The 26 edges are the
conspicuous gap: assertion appears able to occur without a served window, or the served
record is incomplete. The map is a way to place claims, not a claim that a unified theory
already exists.

## 5. Priority for information gain — judgment, not evidence

1. **Assertion provenance**: trace the 26 edges per edge. Separate recording gaps, alternate
   assertion paths, identity mismatches and genuine assertion without service.
2. **The 1-4 count distribution**: explain why the population sits there before testing
   another floor or a longer engine lookback.
3. **BAND-2**: keep the governance block live, but it is less likely than the first two to
   produce a large jump in understanding.

This ordering is an owner/agent prioritization. It changes no verdict, gate, seed or status.

## How to update this page

Append a dated entry when a claim's scope changes; do not rewrite an older scope. Cite the
authoritative artifact or registry row. Do not add a cell, seed or result here. A new
measurement belongs in its own artifact and registry question; this ledger only preserves
the current reading.
