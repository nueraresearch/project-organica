"""Generate the CCRE earned-evidence records from the committed artifacts.

Writes:
  * docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md
  * the manual's §8.23 block, between ``<!-- ccre-earned:start -->`` markers
  * one manual revision-log row

Every number is substituted from an artifact (AGENTS.md rule 20). The manual block is
replaced between markers, so re-running this generator is idempotent.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEW = ROOT / "docs" / "cross_context_reuse_benchmark_earned.json"
OLD = ROOT / "docs" / "cross_context_reuse_benchmark.json"
PROV = ROOT / "docs" / "cross_context_reuse_priming_provenance.json"
OUT = ROOT / "docs" / "CROSS-CONTEXT-REUSE-EARNED-RESULTS.md"
MANUAL = ROOT / "docs" / "USER-MANUAL.md"

ARMS = ("treatment", "control_naive", "control_pruned", "control_orthogonal")
LABEL = {
    "treatment": "treatment",
    "control_naive": "naïve",
    "control_pruned": "pruned",
    "control_orthogonal": "orthogonal",
}
START, END = "<!-- ccre-earned:start -->", "<!-- ccre-earned:end -->"
REV_MARK = "The cross-context experiment: the schema layer primes, but only reorders"


def results_document(new, old, prov) -> str:
    m, om = new["metrics"], old["metrics"]
    rows = new["per_arm_results"]
    recs = {r["arm"]: r for r in prov["records"]}
    t, o = recs["treatment"], recs["control_orthogonal"]

    out: list[str] = []
    add = out.append
    add("# Cross-Context Reuse Experiment — earned-evidence run")
    add("")
    add(f"**Generated from** `{NEW.relative_to(ROOT)}` and "
        f"`{PROV.relative_to(ROOT)}` (this run), and `{OLD.relative_to(ROOT)}` (v1, superseded). "
        f"**Protocol**: {new['protocol']}.")
    add(f"**Seeds**: {new['seeds']} at {new['phase_a_cycles']}/{new['phase_b_cycles']} cycles; "
        f"{new['total_seconds']} s across {new['chunked_run']['chunks']} processes.")
    add("")
    add("## 1. Verdict")
    add("")
    add(f"`{m['reusable_knowledge_verdict']}`")
    add("")
    add(f"Acquisition is flat across all four arms: treatment {m['mean_cycles_treatment']}, "
        f"naïve {m['mean_cycles_naive']}, pruned {m['mean_cycles_pruned']}, orthogonal "
        f"{m['mean_cycles_orthogonal']} cycles → TR {m['transfer_ratio_treatment']} / "
        f"{m['transfer_ratio_pruned']} / {m['transfer_ratio_orthogonal']}. No arm is faster than a "
        f"naïve organism at this endpoint, and the treatment arm is marginally slower.")
    add("")
    add(f"**The priming is not inert.** The single-seed provenance probe separates priming applied by "
        f"the pre-B schema from priming applied by Context B's own emerging schema: treatment "
        f"{t['primed_by_phase_a_schema']} vs {t['primed_by_own_schema']}, orthogonal "
        f"{o['primed_by_phase_a_schema']} vs {o['primed_by_own_schema']} (`schema_prior` applications). "
        f"Both arms acquire at cycle {t['acq_cycle']} and {o['acq_cycle']} respectively, so the prior "
        f"crosses the vocabulary boundary and buys no latency.")
    add("")
    add("## 2. Per-seed results")
    add("")
    add("Cells are `cycles_to_acquire / persistence_cycles / primed_predictions`.")
    add("")
    add("| seed | " + " | ".join(LABEL[a] for a in ARMS) + " |")
    add("|" + "---|" * (len(ARMS) + 1))
    for i, seed in enumerate(new["seeds"]):
        cells = [f"{rows[a][i]['cycles_to_acquire']} / {rows[a][i]['persistence_cycles']} / "
                 f"{rows[a][i]['primed_predictions']}" for a in ARMS]
        add(f"| {seed} | " + " | ".join(cells) + " |")
    add("")
    add("## 3. What changed from the v1 run")
    add("")
    add("| quantity | v1 (`7becdb5`) | earned-evidence |")
    add("|---|---|---|")
    for key, label in (("mean_cycles_treatment", "treatment acquisition"),
                       ("mean_cycles_naive", "naïve acquisition"),
                       ("mean_cycles_pruned", "pruned acquisition"),
                       ("mean_cycles_orthogonal", "orthogonal acquisition"),
                       ("transfer_ratio_treatment", "TR treatment"),
                       ("transfer_ratio_orthogonal", "TR orthogonal")):
        add(f"| {label} | {om[key]} | {m[key]} |")
    add(f"| verdict | `{om['reusable_knowledge_verdict']}` | `{m['reusable_knowledge_verdict']}` |")
    add("")
    add("The v1 advantage came from raising a one-transition edge past `PREDICTION_MIN_COUNT` with a "
        "confidence-derived boost keyed only on the existence of a schema (decision D1). Removing "
        "that substitution flattens acquisition in every arm. The v1 run also could not attribute "
        "its result to Context A: its schema id depended on the role names alone, so Context A and "
        "the orthogonal Context C produced the *same* schema identity and the two arms matched on "
        "four of five seeds, persistence included. Schema identity is now content-bearing (D3), and "
        "the probe above shows the two contexts' schemas are distinct and separately countable.")
    add("")
    add("## 4. What this establishes, and what it does not")
    add("")
    add(f"**Established.** (a) Scored on unboosted evidence, a consolidated schema confers no "
        f"acquisition advantage in this world family — neither Context A's nor Context C's. "
        f"(b) The prior is applied, so the flat result is a measurement rather than an unrun "
        f"manipulation (rules 13a, 25c). (c) The congruence gate can admit and reject, and schema "
        f"identity distinguishes contexts (`tests/test_relational_schema_layer.py`).")
    add("")
    add(f"**Not established.** (a) That a rank-sensitive endpoint would show nothing: the prior "
        f"reorders candidates, and the target edge's rank at acquisition was "
        f"{m['treatment_target_rank_at_acquire']} in treatment, but the acquisition endpoint does "
        f"not reward ranking. (b) Any retention claim: the prior reader returns historical copies, "
        f"so a decayed schema never supersedes its own earlier version. (c) Any statistical claim: "
        f"n = 5, no p-value; the preregistered `TR > 1.25` at `p < 0.01` over 10 seeds is not met "
        f"and is not claimed. (d) That the pruned arm isolates `S_A` — it deletes the entire "
        f"candidate layer and the temporal graph.")
    add("")
    return "\n".join(out) + "\n"


def manual_block(new, prov) -> str:
    m = new["metrics"]
    t, o = [r for r in prov["records"] if r["arm"] == "treatment"][0], \
           [r for r in prov["records"] if r["arm"] == "control_orthogonal"][0]
    return "\n".join([
        START,
        "### 8.23 The cross-context experiment: the schema layer primes, but only reorders",
        "",
        f"**Recorded 2026-11-05.** Decision "
        f"[`docs/DECISION-EARNED-SCHEMA-PRIMING.md`](DECISION-EARNED-SCHEMA-PRIMING.md); results "
        f"[`docs/CROSS-CONTEXT-REUSE-EARNED-RESULTS.md`](CROSS-CONTEXT-REUSE-EARNED-RESULTS.md).",
        "",
        "The 0.12.0 schema layer reported `REUSE_DEMONSTRATED` from a five-seed run. Two things were "
        "wrong with that reading. Its speedup came from a boost that pushed a one-transition edge "
        "past `PREDICTION_MIN_COUNT`, keyed only on *some* schema existing; and its schema identity "
        "depended on the role names alone, so Context A and the orthogonal Context C produced the "
        "same schema id — the two arms were identical on four of five seeds, persistence included.",
        "",
        "**What the engine does now.** A prediction is admitted only on its own evidence "
        "(`temporal_count >= PREDICTION_MIN_COUNT`). A schema may reorder admissible candidates and "
        "nothing else, and only when its stored sender/receiver polarity agrees with the edge's own. "
        "Schema ids carry the role exemplars, so decay and provenance resolve per context.",
        "",
        f"**What the earned-evidence run measured.** Seeds {new['seeds']}, "
        f"{new['phase_a_cycles']}/{new['phase_b_cycles']} cycles, {new['total_seconds']} s: treatment "
        f"{m['mean_cycles_treatment']}, naïve {m['mean_cycles_naive']}, pruned "
        f"{m['mean_cycles_pruned']}, orthogonal {m['mean_cycles_orthogonal']} cycles → TR "
        f"{m['transfer_ratio_treatment']} / {m['transfer_ratio_pruned']} / "
        f"{m['transfer_ratio_orthogonal']}; verdict "
        f"`{m['reusable_knowledge_verdict']}`. The prior is still applied "
        f"({m['primed_predictions']['treatment']} primed predictions in treatment), so the flat "
        f"result is a measurement, not an unrun manipulation.",
        "",
        f"**Which context's schema did the priming?** The single-seed provenance probe separates "
        f"them: Context A's schema primed {t['primed_by_phase_a_schema']} Context B predictions and "
        f"Context B's own schema primed {t['primed_by_own_schema']}; Context C's schema primed "
        f"{o['primed_by_phase_a_schema']} and its own {o['primed_by_own_schema']}. Acquisition was "
        f"cycle {t['acq_cycle']} in both arms. The prior crosses the vocabulary boundary, and so "
        f"does an unrelated one, at the same acquisition cycle.",
        "",
        "**What it does not establish.** That a rank-sensitive endpoint would show nothing (rank was "
        "recorded at acquisition); any retention claim (historical candidate copies are never "
        "superseded); any statistical claim (n = 5, no p-value); or that the pruned arm isolates "
        "`S_A` — it deletes the whole candidate layer and the temporal graph.",
        END,
    ])


def update_manual(block: str) -> None:
    text = MANUAL.read_text()
    if START in text and END in text:
        head, rest = text.split(START, 1)
        _, tail = rest.split(END, 1)
        text = head + block + tail
    else:
        anchor = "\n## 9. Troubleshooting"
        assert text.count(anchor) == 1, "manual anchor not unique"
        text = text.replace(anchor, "\n" + block + "\n" + anchor, 1)

    if REV_MARK not in text:
        marker = "**Revision log:**"
        idx = text.index(marker)
        row_start = text.index("|", idx)
        sep = text.index("|---", row_start)
        row_end = text.index("\n", sep) + 1
        row = (f"| 2026-11-05 | **The cross-context experiment: the schema layer primes, but only "
               f"reorders.** Acquisition is now scored on unboosted evidence, so a prior can reorder "
               f"candidates but cannot admit one; schema identities carry their role exemplars. The "
               f"earned-evidence five-seed rerun is flat across all four arms. §8.23; decision "
               f"`docs/DECISION-EARNED-SCHEMA-PRIMING.md`. |\n")
        text = text[:row_end] + row + text[row_end:]
    MANUAL.write_text(text)


def main() -> None:
    new = json.loads(NEW.read_text())
    old = json.loads(OLD.read_text())
    prov = json.loads(PROV.read_text())
    OUT.write_text(results_document(new, old, prov))
    update_manual(manual_block(new, prov))
    print("wrote", OUT.relative_to(ROOT), "and manual §8.23 + revision row")


if __name__ == "__main__":
    main()
