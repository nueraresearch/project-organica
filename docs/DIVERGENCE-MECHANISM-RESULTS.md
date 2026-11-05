# Divergence mechanism — where the two sides first construct differently

**Status.** Measured, and it does **not** confirm the pre-registered hypothesis. Arm A and Arm B of the experiment pre-registered in `docs/DIVERGENCE-MECHANISM-BRIEF.md` and journal §73, run against the frozen engine at `711f04dde00e`.

No engine file was modified: the observer and the intervention are subclasses in `benchmarks/divergence_mechanism.py`.

## 1. What was run

| | |
|---|---|
| Baseline commit | `711f04dde00ed0d0d293a1f425e63342b53823ab` |
| Command | `python benchmarks/divergence_mechanism.py --arm BOTH --workers 4` |
| Seeds | 8 failing seeds plus the control seed T1/20261101 |
| Parts | 36, each with its sha256 in the artifact |
| Analysis pass | 0.1 s over the cached parts |
| Pre-registration | `docs/DIVERGENCE-MECHANISM-BRIEF.md` |

## 2. Two resolutions, and they answer different questions

The brief asks which builder first differs. That question has two readings, and the instrument measures both:

- **the builders' own sequences** — the tag scores before and after their sort, the graph as read, and each candidate list in order. These are what the engine assembles.
- **the admitted stream** — the predictions the harness admits each cycle, which is what the membership audit digested.

## 3. Arm A: order enters at `_score_tags`, on every seed, at cycle 1

| Task | Seed | First differing builder (arm C) | Cycle found | Kind |
|---|---|---|---|---|
| T1 | 20261125 | tag scores (`_score_tags`) | 1 | order |
| T1 | 20261128 | tag scores (`_score_tags`) | 1 | order |
| T1 | 20261129 | tag scores (`_score_tags`) | 1 | order |
| T2 | 20261118 | tag scores (`_score_tags`) | 1 | order |
| T2 | 20261120 | tag scores (`_score_tags`) | 1 | order |
| T2 | 20261121 | tag scores (`_score_tags`) | 1 | order |
| T2 | 20261123 | tag scores (`_score_tags`) | 1 | order |
| T2 | 20261130 | tag scores (`_score_tags`) | 1 | order |

**8 of 8 seeds** report `_score_tags` as the first builder whose sequence differs, and every one of them differs at **cycle 1**.

**This does not locate the divergence.** `_score_tags` iterates `set(freqs) | set(cooc) | set(temporal)` — a set of strings — and then stable-sorts on `frequency`, an integer that ties constantly, so its position order is the hash seed's. That is true on the first cycle of every run, and it is true of the **control seed** as well. The earliest order-sensitive site is therefore answered, and the question the brief wanted answered — which difference makes the two sides part company — is downstream of it.

## 4. The admitted streams reproduce the audit’s cycle, and there is no offset

| Task | Seed | Audit index | Engine cycle | Admitted streams first differ at | Reproduced | Types differing at that cycle |
|---|---|---|---|---|---|---|
| T1 | 20261125 | 11 | 12 | 12 | yes | anomalies, loops, meta, predictions, score_tags, temporal_read |
| T1 | 20261128 | 3 | 4 | 4 | yes | loops, meta, predictions, score_tags, temporal_read |
| T1 | 20261129 | 2 | 3 | 3 | yes | anomalies, loops, meta, predictions, score_tags, temporal_read |
| T2 | 20261118 | 5 | 6 | 6 | yes | anomalies, predictions, score_tags, temporal_read |
| T2 | 20261120 | 5 | 6 | 6 | yes | anomalies, loops, meta, predictions, score_tags, temporal_read |
| T2 | 20261121 | 5 | 6 | 6 | yes | anomalies, predictions, score_tags, temporal_read |
| T2 | 20261123 | 5 | 6 | 6 | yes | predictions, score_tags, temporal_read |
| T2 | 20261130 | 5 | 6 | 6 | yes | anomalies, loops, meta, predictions, score_tags, temporal_read |

The admitted streams first differ at the audit’s cycle itself on **8 of 8** seeds. There is no offset: the membership audit stores `first_cycle` as a **zero-based index** into its cycle digests, and this instrument numbers cycles from one, so the two numbers differ by that base alone. The earlier version of this report read the index as a cycle, took every "at the divergence cycle" comparison one cycle early, and described the resulting +1 as a systematic difference of convention; it was neither behavioural nor a convention. The agreement is **reproduction of the audit’s cycle on a fresh capture**, not an interval: the audit defines its divergence cycle *as* the first cycle whose admitted streams differ, so a second instrument cannot find the difference anywhere else without contradicting it. **No delay between construction order and admission is measured here, in either direction.**

The replacement field is falsifiable and it fired: the fresh capture does **not** part company at the audit’s cycle for T2/20261120 arm B. Arm C is the arm the D0 verdict was scored on; arm B is reported because arm C reads arm B’s recorded temporal graphs.

## 5. Arm B: the pre-registered intervention was not admissible

| | Result |
|---|---|
| **P1** | 8 types located |
| **P2** | **NOT MET** — the control’s *builders* do not agree across hash seeds
| **P3** | **NOT MET** — 0 of 8 seeds became invariant
| **F1** | **FIRED**
| **F2** | **FIRED**

**F2 fired, so by the pre-registration no conclusion may be drawn from Arm B.** The canonicalisation changes the control seed’s builder sequences at a fixed hash seed, which is the confound the control exists to catch.

F1 fired as well, and Arm A explains why it had to: the intervention canonicalises the **temporal graph** and the **composites**, while the figure above shows the earliest order-sensitive builder is `_score_tags`, which the intervention deliberately leaves untouched (`§5.2` of the brief chose the two smallest changes, not every sort). An intervention that starts downstream of the first order channel cannot remove it, so F1’s firing is evidence about the **intervention’s scope**, not about H2.

## 6. The controls

| | Control | Result |
|---|---|---|
| **C1** | the control seed (T1/20261101) across hash seeds | **FAILED as pre-registered**: C1 required the control's *assembled lists* to be identical at every hash seed (P2), and P2 is **NOT MET** |
| **C3** | determinism: one part rewritten by a second process | **identical**, field for field |

**A narrower observation, recorded post hoc and not as a held control.** The control seed's *admitted stream* is identical at every cycle across hash seeds while its builder sequences differ. That is a real, artifact-backed fact: the artifact carries `P2.admitted_stream_identical: true` beside `P2.met: false`. It is a **different quantity from the one C1 pre-registered**, and it was read after P2 had already failed, so the admissible statement is: on this one seed, at one hash-seed pair, the build was observed to be order-invariant in what it decides and order-dependent in how it constructs. An observation, not a passed control, and not a general law (on the eight failing seeds the two coincided).

**The defect in this section, disclosed rather than overwritten.** An earlier version reported C1 as *invariant* and called it the sharpest positive result. C1's name was kept while the quantity behind it was changed to one that passes. A control re-specified after it fails has measured nothing.

## 7. What this establishes, and what it does not

**Establishes.** Order enters candidate construction at `_score_tags` on the first cycle of every seed, including the seed the campaign calls stable; a fresh capture reproduces the audit’s divergence cycle on all eight seeds; and the pre-registered intervention is confounded by its own control; and the control the brief named for that invariance did not hold (P2 failed).

**Does not establish.** That the order channel is or is not sufficient — H2 is **untested in an admissible form**, because F2 fired before Arm B could speak. It does not re-score D0, modify the engine, or say anything about the campaign’s own numbers.

**What the next instrument needs.** An intervention at the **first** order-sensitive site — a total order on the tag scores, or a canonical iteration order for `set(freqs) | set(cooc) | set(temporal)` — and a control that holds. The brief’s choice of the two downstream sites is the defect this run found.

## Provenance

- Artifact: `docs/divergence_mechanism.json`.
- Instrument: `benchmarks/divergence_mechanism.py`.
- Membership reference: `docs/candidate_membership_audit.json` (sha256 `544ebd87bf86a7b38e98815449cd86e66a9ed75dbc3ffb1431cae34c76365e17`).
- Observer version: 1; 36 part files, each with its sha256 in the artifact.
- Re-render: `python benchmarks/divergence_mechanism.py --render-only`.
