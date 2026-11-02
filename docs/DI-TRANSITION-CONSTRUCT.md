# The transition construct: onset of `DI` as the primary candidate predictor

**Status: exploratory construct record. No engine run, no seed allocated, no confirmatory claim.**
Stage B is not authorised. Every number here is written by `benchmarks/di_transition_construct.py` into
`docs/di_transition_construct.json`, and `tests/test_di_transition_construct.py` asserts this document against
that artifact.

The owner's decision of 2026-11-02 makes a **transition summary** the primary candidate predictor and keeps the
**settled state** as a separate, unresolved construct. This record does the audit that decision requires. It
reads no behavioural endpoint: the choice of summary is made on measurement grounds alone, before any outcome is
examined, because a summary chosen for how well it relates to behaviour would be an outcome in disguise.

---

## 1. The decision, and what it is not

| Element | Decision |
| --- | --- |
| primary candidate | a transition summary, specified in §3 |
| scientific question | does the way internal structure develops predict what the system subsequently does? |
| settled state | retained as a separate construct, **unresolved** — `docs/DI-MEASUREMENT-WINDOW.md` §3.2 shows no settled state exists in the record |
| validation | independent worlds, disjoint seeds, criteria pre-committed (Stage B, §7, **not authorised**) |
| failure | the construct is rejected if it fails validation; the claim is not reduced to fit |

This is not a repair of the settled-state measurement. The settled-state construct asked *what structure exists
at a designated time*, and that question remains open with no window attached to it. The transition construct
asks *how structure emerges*, and it is measured with a different quantity on a different grid.

---

## 2. What the three candidate summaries can actually measure here

Each candidate was computed on all 240 stored records, with no behavioural quantity read. The comparison is of
measurement properties, not of results:

| candidate | defined for | censored | unit | within-config SD (`6:1`) | within-config range (`6:1`) | within-config share of variance | rank stability at cycle 450 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **onset** | 119 / 240 records; 119 / 120 in the four configurations that produce structure | 121 | cycles | 12.4 (median 329) | 289–354 | 7.1 % | 1.000 |
| exposure | 240 / 240 | 0 | pairs | 0.44 (median 6.45) | 5.33–7.33 | 1.4 % | 0.925 |
| slope | 84 / 240 when the run is cut at 450 | 156 | pairs per 100 cycles | 0.55 | — | 65.5 % | **-0.315** |

Three properties decide it, and they are the three the owner named as the questions to ask before Stage B:

1. **Slope is not estimable from a record that may still be running.** Its rank correlation across the 240
   records falls from the full 600-cycle fit to the 450-cycle fit at **-0.315**: the ordering of worlds by rate
   *reverses* when the observation window shortens. A rate fitted over a support that is still growing is a
   function of where you stopped, and this record stops mid-transition (§4). Slope is retained as exploratory
   and is currently unusable; it becomes usable only when a run contains the end of the transition, which is
   exactly what Stage B would have to supply.
2. **Exposure is defined for every record, and depends on the integration interval by construction.** Its
   ranking is fairly stable under truncation (0.925) and it is the natural "dose" reading — how much structure
   had accumulated by the time learning begins. But its value is defined *relative to an interval*, and the
   interval's length is the one design parameter this project has not been able to fix. Keeping it as the
   primary would build the unresolved question into the predictor.
3. **Onset is measured once, at a cycle, and cannot be undone by extending the run.** An event already observed
   does not move when the run continues, so onset is the only candidate whose value is invariant to the run
   length that Stage A found to be the sticking point. It varies within a configuration by far more than its
   own resolution: SD 12.4 cycles over a range of 65 in `6:1`, on a grid of one cycle.

**Primary: onset.** Not because it relates best to behaviour — nothing here has been related to behaviour — but
because it is the only candidate that survives the two things this record has already shown to be broken: the
absent settled state, and the undetermined run length.

**The redundancy is measured, not hidden.** Among the 119 moving runs, onset and exposure rank-correlate at
**-0.932** across configurations: earlier emergence and greater accumulated stock are nearly the same ordering.
So choosing onset does not discard the dose information — it chooses the *measurable* of two nearly equivalent
orderings, and it leaves exposure available as a co-reported exploratory quantity whose interval must be declared
in advance.

---

## 3. Onset: the event, the conventions, and the scope

### 3.1 The event, and the conventions that define it

**The event is the first cycle of the qualifying sustained run** — not the first cycle on which `DI` is
non-zero, and not the first cycle at which the emergence was visible. The anchor is assigned retrospectively:
only once the tenth consecutive non-zero reading has been recorded is the earlier cycle confirmed as onset. The
quantity is therefore a cycle index whose *availability* comes nine cycles later, and §6's boundary is written
against that availability rather than against the anchor.

| question | convention | what it does in this record |
| --- | --- | --- |
| which cycle is onset? | the first cycle of the qualifying run | 99 of 119 onsets are also the record's first non-zero cycle; **20 are later**, one by as much as 279 cycles |
| when is it known? | at the tenth consecutive reading | latest confirmation cycle **598** of 600 |
| is it assigned retrospectively? | yes — the anchor is back-dated once the run qualifies | all 119 |
| a run interrupted before the tenth reading? | does not qualify, does not move the anchor; the search resumes at the cycle after the zero | **2353** such attempts across 24 records |
| an interruption after confirmation? | does not move a confirmed onset | — |
| a missing reading? | counts as not qualifying, so it breaks the run; never read as non-zero | 0 records contain one, so the convention is declared for future runs and is vacuous here |
| too few cycles left to confirm? | censored, never an onset at the boundary | **0** censored this way; **4** censored with an interrupted attempt; **117** have no non-zero reading at all |

The last row fixes the denominator: 240 = **119** onsets + **4** interrupted short runs + **117** with no
reading to qualify. The four in the middle are the one-cycle arrival blips in the `1:x` arms, and they are why
a single non-zero reading is not an onset: without the sustention rule they would each become one, at the
arrival cycle, in a world where nothing then persists.

### 3.2 The sustention rule is part of the measure, so it is swept

Ten cycles is a declared constant, not a natural boundary. Its effect is bounded here rather than asserted:

| sustention rule | onsets defined | median | SD | worst single-record shift | records whose onset moves |
| --- | --- | --- | --- | --- | --- |
| 5 | 119 | 376 | 81.6 | 25 | 3 |
| **10 (declared)** | **119** | **376** | **82.0** | — | — |
| 20 | 117 | 374 | 79.3 | 13 | 1 |

The medians and SDs in that table pool all four configurations, which is why the SD is 82 cycles and why no
pooled figure may be reported as a finding (§3.5, limit 2); the per-configuration distributions are in §3.4.
What the sweep shows is that the rule does not manufacture the ordering: halving or doubling it moves three of
119 onsets, by at most 25 cycles. Stage B must still freeze the rule and report it beside every onset value,
because a constant that is part of the measure is part of the claim.

### 3.3 Measurement eligibility is not scientific scope

Eligibility is decided by measurement, for every configuration, and reported whether or not the construct claims
it. A configuration is **eligible** when at least 90 % of its runs produce a sustained onset — the same threshold
Stage B's first criterion uses, applied here to the record already in hand.

| configuration | records | runs that ever move | sustained onsets | defined share | classification | in the claim |
| --- | --- | --- | --- | --- | --- | --- |
| `1:1` | 30 | 1 | 0 | 0.000 | without sustained emergence | no |
| `1:2` | 30 | 1 | 0 | 0.000 | without sustained emergence | no |
| `1:3` | 30 | 1 | 0 | 0.000 | without sustained emergence | no |
| `1:4` | 30 | 1 | 0 | 0.000 | without sustained emergence | no |
| `2:1` | 30 | 29 | 29 | 0.967 | with sustained emergence | yes |
| `3:1` | 30 | 30 | 30 | 1.000 | with sustained emergence | yes |
| `4:1` | 30 | 30 | 30 | 1.000 | with sustained emergence | yes |
| `6:1` | 30 | 30 | 30 | 1.000 | with sustained emergence | yes |

**Accounting: 240 records — 120 in the four configurations with sustained emergence, 120 in the four without,
0 dropped.** The ineligible four are not missing data and are not silently removed: they are counted here, their
runs appear in every aggregate in §2, and their classification is a property of those worlds under this rule
(the AGENTS 13a condition in its exact form). They are **out of scope for this construct**, and a run of one is a
statement about the world, never a null about the organism.

The construct's claim is therefore stated as **evaluated among configurations in which sustained structure
emerges** — narrower than a universal claim, and the only form the measurement supports. A relation found inside
one of these four configurations does not extend to the others by itself, and no relation is claimed across
them.

### 3.4 Distribution per configuration, and the resolution criterion it feeds

| configuration | runs with an onset | median onset | SD | range | exposure, mean ± SD (pairs) |
| --- | --- | --- | --- | --- | --- |
| `6:1` | 30 | 329 | 12.4 | 289–354 | 6.45 ± 0.44 |
| `4:1` | 30 | 362 | 19.3 | 310–391 | 5.29 ± 0.40 |
| `3:1` | 30 | 404 | 25.1 | 342–445 | 3.65 ± 0.57 |
| `2:1` | 29 | 539 | 27.3 | 475–589 | 0.31 ± 0.25 |
| `1:1`–`1:4` | 0 | — | — | — | 0.00 ± 0.00 |

A standard deviation over 30 values can be carried by a handful of unusual worlds, so the distribution behind it
is reported beside it:

| configuration | defined share | median | SD | IQR | range | distinct onsets | share within ±3 cycles of the median |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `6:1` | 1.000 | 329 | 12.4 | 14.00 | 289–354 | 18 | 0.17 |
| `4:1` | 1.000 | 362 | 19.3 | 17.25 | 310–391 | 27 | 0.27 |
| `3:1` | 1.000 | 404 | 25.1 | 26.00 | 342–445 | 23 | 0.27 |
| `2:1` | 0.967 | 539 | 27.3 | 37.00 | 475–589 | 22 | 0.21 |

The resolution criterion is evaluated **within each configuration**, at a floor of 3 cycles, alongside the 90 %
defined-share criterion — never on the pooled set, where the arm differences would dominate:

| configuration | defined share ≥ 0.90 | SD ≥ 3 cycles | pass |
| --- | --- | --- | --- |
| `6:1` | yes (1.000) | yes (12.4) | yes |
| `4:1` | yes (1.000) | yes (19.3) | yes |
| `3:1` | yes (1.000) | yes (25.1) | yes |
| `2:1` | yes (0.967) | yes (27.3) | yes |

All four pass, and not narrowly: the smallest within-configuration SD is 12.4 cycles against a 3-cycle floor,
and the tightest defined share is 0.967 against 0.90. The clump column is what keeps that from being a false
pass in the other direction — only 17–27 % of onsets sit within ±3 cycles of their own configuration's median,
and 18–27 of each 30 onsets are distinct values, so the spread is broad rather than a floor plus a few outliers.
The one quantity that sits at all near its threshold is `6:1`'s SD: it is the configuration with the least onset
spread, it would be the first to fail if a future run tightened the rule, and its value is reported above with
the IQR and range rather than on its own.

### 3.5 Limits, stated before any use

1. **The sustention rule is part of the measure.** Ten cycles is a declared constant, not a natural boundary.
   §3.2 bounds its effect in this record — halving it moves three onsets by at most 25 cycles — but Stage B must
   still freeze it, report it beside every onset value, and treat a world whose confirmation cycle falls outside
   the record as unresolved rather than as a precise number.
2. **Onset is a timing, so it is confounded with the pace of the arm.** It can only be interpreted *within* a
   configuration, where the pace is held fixed. A pooled relation between onset and behaviour would restate the
   fact that the arms differ, which is why §5's fourth falsifier exists.
3. **Onset says nothing about how much structure is present.** A world can emerge early and plateau low. That
   is exposure's question, and it is why exposure is retained as exploratory rather than dropped.
4. **The within-configuration share of variance is 7.1 %** — the remaining 92.9 % is between configurations. That
   is not disqualifying for a within-configuration test: the arm is held constant by design, and the within-arm
   spread is 65 cycles wide. It does mean that no pooled coefficient should ever be reported as the finding.

---

## 4. Settling, separated into the three criteria it had been conflating

The project had been using a single statistic — "the last cycle at which the run's value differs from its own
final value by a whole pair" — and reading it as evidence that the state had settled. Those are three different
criteria, and only the third speaks to whether the trajectory would keep moving. Among the 119 runs with a
sustained onset:

| criterion | statistic | result |
| --- | --- | --- |
| (a) entry into a one-pair band around the final value | median entry cycle | **587** of 600 (max 599) |
| (b) remaining in that band for a stated duration | median persistence | **13 cycles**; 37 runs ≥ 30, 17 ≥ 50, **4 ≥ 100** |
| (c) no meaningful remaining trend | change over the last 100 cycles | median **2.0 pairs**, range -4.0 to +9.0; **23** runs below half a pair, **96** at two pairs or more |

**Nothing in this record is a settled state.** Criterion (a) is retrospective — it uses the run's own final
value, which is simply where the observation stopped — and its median of 13 cycles of persistence is a quiet
patch, not a plateau. Criterion (c) is the one that could support an asymptote claim, and it fails for 96 of the
119 runs: they moved by at least two pairs over the final 100 cycles, and none moved by a quantity between half
a pair and two pairs. Only **4 of 119** runs satisfy (b) at 50 cycles and (c) together.

**Consequences, applied:**

- No asymptote is claimed for this record. The word **asymptote** is retired from the design documents. A
  future run may claim one only if (b) and (c) are both declared before it runs and both met afterwards, with
  their parameters stated.
- A stopping criterion is now a **pair** of conditions — persistence in a one-pair band over a stated number of
  cycles, and no remaining trend over a stated span — not a single last-change cycle.
- The Stage A figure of **586** and this record's **587** measure the same statistic on different populations:
  586 pools all 123 runs that ever move, including the four one-cycle arrival blips; 587 uses the 119 runs with
  a sustained onset. The difference is one cycle, and it changes none of the conclusions above.

---

## 5. What the construct claims, and what would falsify it

**Claim, in the form Stage B would test:** *within a generating configuration, worlds whose internal structure
emerges earlier behave differently afterwards from worlds whose structure emerges later — in the direction that
structure available earlier supports later revision.*

The claim is **evaluated among configurations in which sustained structure emerges** (§3.3). It is not a claim
about the `1:x` worlds, where the quantity is not produced, and it is not a claim across configurations.

Pre-committed falsifiers, written before any behavioural endpoint is read:

1. **Absence.** A within-configuration interval for the relation that contains zero → the construct is not
   supported. It is not "weakly supported", and it is not rescued by the pooled relation.
2. **Reversal.** A relation of the opposite sign → recorded as reversed, which is a stronger statement than
   unsupported and must be reported as such.
3. **Dead configuration.** A configuration in which onset is undefined in most runs → out of scope for the
   construct, reported as a world property, never as a null.
4. **Pooled only.** A relation that appears across configurations but not inside one → the construct is not
   supported for the protocol's question, because the protocol's question is within a configuration.

---

## 6. The temporal boundary

The ordering the owner required — structural measurement, then held-out behavioural observation — is preserved
by construction here, and the boundary is stricter than a window's:

- Onset is a **cycle index assigned retrospectively**, so the predictor does not exist at the anchor cycle: it
  becomes available at the confirmation cycle, nine cycles later, and the latest confirmation in this record is
  cycle **598** of 600 (§3.1). The behavioural limb may not begin before the confirmation cycle, and a Stage B run
  must then extend through the protocol's 50-cycle learning and 50-cycle test. The run length is therefore set by
  the organism's own emergence plus a fixed margin, not by a window chosen for the measurement — which is the
  property the settled-state window lacked.
- **No behavioural cycle may contribute to onset.** Onset is derived from the structural trajectory up to its
  own event; the behavioural limb begins afterwards and its test set is withheld.
- If exposure is co-reported, its integration interval **must be declared in advance and must end before
  learning begins.** An interval chosen after seeing the behaviour would make the dose a function of the
  outcome.
- The late-pair overlap measured for the settled-state window is not the binding overlap for onset — onset is
  not computed from a pair set — but any pair contributing to *any* predictor in the run must be withheld from
  the behavioural test set, and that requirement is unchanged.

---

## 7. Stage B: what validating this construct would require, and why it is not authorised

Fresh methodology worlds from the frozen engine, on seeds disjoint from every Phase L seed and from every
confirmatory block; the sustention rule, the stopping criterion and the integration interval declared before any
world is generated; the relation estimated **within** configuration with the predictor's spread reported beside
it.

The four Stage B criteria carry over, with the resolution criterion restated for a cycle-valued predictor:

1. **Non-degenerate.** Onset is defined in at least 90 % of the runs of **each** configuration the construct
   claims — evaluated configuration by configuration, never on the pooled set.
2. **Resolution.** Within-configuration SD of onset is at least 3 cycles **in each claimed configuration**,
   reported beside that configuration's IQR, range and distinct-value count so that a concentrated distribution
   cannot pass on a few unusual worlds.
3. **Consistency.** The stopping criterion of §4 — persistence plus no remaining trend — is met in every
   configuration claimed, with its parameters declared in advance.
4. **Ordering.** Onset and the sustention window complete strictly before revision learning begins, and no
   behavioural cycle contributes to any predictor.

Both measurement criteria are evaluated per configuration because a pooled SD would be dominated by the arm
differences — the pooled SD of 82.0 cycles in §3.2 is between-configuration spread, not resolution. On the record
in hand all four claimed configurations pass both (§3.4), so no criterion is being met by the pool while failing
inside a configuration.

**Failure rule unchanged:** if any criterion fails, the construct is rejected and no confirmatory seed is
allocated. A rejection is the design's result and is not renegotiated into a smaller claim, and a configuration
that fails criterion 1 or 2 is dropped from the claim rather than from the accounting (§3.3).

**Cost.** Stage B spends methodology seeds, so it is **not authorised here**: no seed is allocated, no world is
generated, and the owner decides whether and when to run it. Nothing in this document commits the project to it.

---

## 8. What is preserved

- The 240 Phase L records, untouched: same file, same seeds, same values.
- The protocol's window (110–150), still written and still flagged as contested and unresolved.
- The construct audit's verdict on `DI` as a state at a designated time, untouched. This record adds a second
  construct beside it rather than reinterpreting it.
- V1 and its results, untouched. The sample-size discussion remains paused, and the attenuation curve will need
  re-deriving for whatever predictor is finally validated.

---

## 9. Verification

```bash
./.venv/bin/python -m benchmarks.di_transition_construct        # writes docs/di_transition_construct.json
./.venv/bin/python -m pytest tests/test_di_transition_construct.py -q
```

The test recomputes the artifact, asserts every number quoted here against it, asserts that onset is the named
primary with exposure and slope labelled exploratory, and asserts that the artifact records no behavioural
correlation — the guarantee that the construct was not chosen on an outcome. It also asserts that the onset
convention quoted in §3.1 is the convention the code applies, that eligibility is reported for all eight
configurations with no record dropped, and that the resolution criterion is evaluated per configuration with the
distribution beside it.
