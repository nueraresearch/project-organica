"""
Sleep Inquiry Mixin — Layers 6, 7, 8 (Sleep V5 / V6 / Path B).

Handles active inquiry, curiosity simulation, and empirical experimentation:
  Layer 6: Categorized Dreams (Completion, Analogy, Mutation, Conditional)
  Layer 7: Investigation Candidates & Ranking (Expected Information Gain)
  Layer 8: Active Experiment Probes & Execution (Law IV verification)
"""

import json
import time
from typing import Optional, Any, Callable

from .candidates import (
    _make_id,
    WorkflowConceptCandidate,
    ProcessCandidate,
    MetaConceptCandidate,
    QuestionCandidate,
    DreamCandidate,
    InvestigationCandidate,
    ExperimentCandidate,
    HypothesisCandidate,
)


class SleepInquiryMixin:
    """Active inquiry, dream generation, and empirical experiment methods."""

    # ==================================================================
    # Layer 6: Categorized Dreams (V5)
    # ==================================================================

    def _generate_categorized_dreams(
        self,
        workflows: list[WorkflowConceptCandidate],
        processes: list[ProcessCandidate],
        meta_concepts: list[MetaConceptCandidate],
        questions: list[QuestionCandidate],
        cooc: dict[str, dict[str, int]],
        temporal: dict[str, dict[str, int]],
    ) -> list[DreamCandidate]:
        """Generate structured dreams across 4 distinct categories:
        1. Completion: transitive closure of observed edges (A->B, B->C => dream A->C).
        2. Analogy: substitute tag with co-occurrence synonym (A->C, A ~ B => dream B->C).
        3. Mutation: structural path extension/variation.
        4. Conditional: search for hidden context tags separating conflicting outcomes in Questions.
        """
        dreams = []
        seen = set()

        # Category 1: Completion Dreams (Transitive Closure)
        for p in processes:
            cycle = p.cycle
            if len(cycle) >= 3:
                for i in range(len(cycle)):
                    a = cycle[i]
                    c = cycle[(i + 2) % len(cycle)]
                    if c not in temporal.get(a, {}):
                        did = _make_id("dream_comp", a, c)
                        if did not in seen:
                            seen.add(did)
                            dreams.append(DreamCandidate(
                                id=did,
                                generation=6,
                                dream_category="completion",
                                subject=a,
                                path_or_context=[a, c],
                                confidence=0.08,
                                novelty=0.65,
                                parent_ids=[p.id],
                                evidence={"reason": "transitive_shortcut", "via_process": p.id},
                            ))

        # Category 2: Analogy Dreams (Knowledge Transfer via Co-occurrence Neighbors)
        for m in meta_concepts[:3]:
            anchor = m.anchor_tag
            neighbors = sorted(cooc.get(anchor, {}).items(), key=lambda x: -x[1])
            for neighbor, count in neighbors[:2]:
                for target, edge_cnt in temporal.get(anchor, {}).items():
                    if edge_cnt >= 3 and target not in temporal.get(neighbor, {}):
                        did = _make_id("dream_analogy", neighbor, target)
                        if did not in seen:
                            seen.add(did)
                            dreams.append(DreamCandidate(
                                id=did,
                                generation=6,
                                dream_category="analogy",
                                subject=neighbor,
                                path_or_context=[neighbor, target],
                                confidence=0.05,
                                novelty=0.75,
                                parent_ids=[m.id],
                                evidence={"reason": "analogy_substitution", "analog_source": anchor, "shared_cooc": count},
                            ))

        # Category 3: Mutation Dreams (Structural Path Extension)
        for w in workflows[:2]:
            comps = list(w.components)
            if len(comps) >= 2:
                for m in meta_concepts:
                    if m.anchor_tag not in comps:
                        mutated = comps + [m.anchor_tag]
                        did = _make_id("dream_mut", w.id, m.anchor_tag)
                        if did not in seen:
                            seen.add(did)
                            dreams.append(DreamCandidate(
                                id=did,
                                generation=6,
                                dream_category="mutation",
                                subject=comps[0],
                                path_or_context=mutated,
                                confidence=0.04,
                                novelty=0.85,
                                parent_ids=[w.id, m.id],
                                evidence={"reason": "path_extension", "extended_tag": m.anchor_tag},
                            ))
                        break

        # Category 4: Conditional Dreams (Resolving Questions)
        for q in questions[:3]:
            sub = q.subject
            candidate_contexts = [t for t, _ in sorted(cooc.get(sub, {}).items(), key=lambda x: -x[1])
                                  if t not in q.competing_expectations]
            for ctx in candidate_contexts[:2]:
                did = _make_id("dream_cond", sub, ctx)
                if did not in seen:
                    seen.add(did)
                    dreams.append(DreamCandidate(
                        id=did,
                        generation=6,
                        dream_category="conditional",
                        subject=sub,
                        path_or_context=[ctx, sub] + q.competing_expectations,
                        confidence=0.06,
                        novelty=0.90,
                        parent_ids=[q.id],
                        evidence={"reason": "hidden_fork_context", "context_tag": ctx, "question_id": q.id},
                    ))

        dreams.sort(key=lambda d: d.novelty, reverse=True)
        return dreams[:self.MAX_DREAMS]

    # ==================================================================
    # Layer 7: Investigation Ranking / Attention Economy (V5)
    # ==================================================================

    def _rank_investigations(
        self,
        questions: list[QuestionCandidate],
        dreams: list[DreamCandidate],
    ) -> list[InvestigationCandidate]:
        """Rank investigations based on Expected Information Gain (EIG).
        
        Currency of Epistemic Choice:
          EIG = Uncertainty * (1.0 + Novelty)
        High EIG targets promise maximum knowledge reorganization or conflict elimination.
        """
        investigations = []

        # 1. Evaluate Questions
        for q in questions:
            if q.evidence.get("closed") or q.evidence.get("resolved_by"):
                continue
            novelty = 0.50
            eig = round(q.uncertainty * (1.0 + novelty), 4)
            iid = _make_id("inv", q.id)
            investigations.append(InvestigationCandidate(
                id=iid,
                generation=7,
                target_id=q.id,
                target_type="question",
                subject=q.subject,
                novelty=novelty,
                uncertainty=q.uncertainty,
                expected_information_gain=eig,
                parent_ids=[q.id],
                evidence={
                    "formula": "uncertainty * (1.0 + novelty)",
                    "competing_outcomes": q.competing_expectations,
                },
            ))

        # 2. Evaluate Dreams
        for d in dreams:
            uncertainty = round(1.0 - d.confidence, 4)
            eig = round(uncertainty * (1.0 + d.novelty), 4)
            iid = _make_id("inv", d.id)
            investigations.append(InvestigationCandidate(
                id=iid,
                generation=7,
                target_id=d.id,
                target_type="dream",
                subject=d.subject,
                novelty=d.novelty,
                uncertainty=uncertainty,
                expected_information_gain=eig,
                parent_ids=[d.id],
                evidence={
                    "formula": "uncertainty * (1.0 + novelty)",
                    "dream_category": d.dream_category,
                    "path_or_context": d.path_or_context,
                },
            ))

        investigations.sort(key=lambda inv: inv.expected_information_gain, reverse=True)
        return investigations[:self.MAX_INVESTIGATIONS]

    # ==================================================================
    # Layer 8: Active Experiment Selection (Sleep V6 / Path B)
    # ==================================================================

    def _select_experiments(
        self,
        investigations: list[InvestigationCandidate],
        questions: list[QuestionCandidate],
        dreams: list[DreamCandidate],
    ) -> list[ExperimentCandidate]:
        """Convert top investigations into concrete, executable experiment interventions."""
        questions_by_id = {q.id: q for q in questions}
        dreams_by_id = {d.id: d for d in dreams}
        experiments = []

        for inv in investigations:
            if inv.target_type == "question":
                q = questions_by_id.get(inv.target_id)
                if not q:
                    continue
                action_type = "discriminating_probe"
                payload = {
                    "subject": q.subject,
                    "target_question_id": q.id,
                    "competing_outcomes": q.competing_expectations,
                    "test_vector": f"probe:{q.subject} -> ? ({' vs '.join(q.competing_expectations)})",
                }
                expected_outcomes = q.competing_expectations
                cost = 1.0
            elif inv.target_type == "dream":
                d = dreams_by_id.get(inv.target_id)
                if not d:
                    continue
                action_type = f"verify_{d.dream_category}_dream"
                payload = {
                    "subject": d.subject,
                    "target_dream_id": d.id,
                    "dream_category": d.dream_category,
                    "path_or_context": d.path_or_context,
                    "test_vector": f"probe_path:{' -> '.join(d.path_or_context)}",
                }
                expected_outcomes = ["validated", "refuted"]
                cost = 1.2 if d.dream_category in ("mutation", "conditional") else 0.8
            else:
                continue

            priority = round(inv.expected_information_gain / max(0.1, cost), 4)
            eid = _make_id("exp", inv.id, action_type)

            experiments.append(ExperimentCandidate(
                id=eid,
                generation=8,
                investigation_id=inv.id,
                target_id=inv.target_id,
                target_type=inv.target_type,
                action_type=action_type,
                probe_payload=payload,
                expected_outcomes=expected_outcomes,
                cost=cost,
                priority=priority,
                status="proposed",
                parent_ids=[inv.id],
                evidence={
                    "investigation_eig": inv.expected_information_gain,
                    "cost": cost,
                    "formula": "EIG / cost",
                },
            ))

        experiments.sort(key=lambda exp: exp.priority, reverse=True)
        return experiments[:self.MAX_EXPERIMENTS]

    def execute_experiments(
        self,
        experiments: Optional[list[ExperimentCandidate]] = None,
        executor_fn: Optional[Callable] = None,
    ) -> list[dict]:
        """Execute proposed experiments against empirical reality (Law IV)."""
        all_prior = self._load_prior_candidates()
        if experiments is None:
            experiments = [
                ExperimentCandidate(**{k: v for k, v in c.items() if k != "type"})
                for c in all_prior if c.get("type") == "experiment" and c.get("status") == "proposed"
            ]

        recent_obs = self.memory.recent(n=50, event_type="observe") if not executor_fn else []
        results = []
        with self.memory.batch():
            for exp in experiments:
                if executor_fn:
                    outcome = executor_fn(exp)
                else:
                    payload = exp.probe_payload
                    subject = payload.get("subject", "")
                    outcomes = exp.expected_outcomes
                    found_match = False
                    for obs in recent_obs:
                        if subject in obs.tags:
                            for out in outcomes:
                                if out in obs.tags:
                                    found_match = True
                                    break
                        if found_match:
                            break

                    outcome = "validated" if found_match else "refuted"

                exp.status = outcome
                result_record = {
                    "experiment_id": exp.id,
                    "target_id": exp.target_id,
                    "target_type": exp.target_type,
                    "status": outcome,
                    "executed_at": time.time(),
                }
                results.append(result_record)

                # Record experiment intervention event in memory
                self.memory.store(
                    json.dumps(result_record),
                    event_type="experiment_result",
                    source=f"experiment:{exp.id}",
                )

                # Hypothesis Promotion / Refutation Loop (Law IV completion)
                if exp.target_type in ("question", "dream"):
                    updated_ids: set[str] = set()
                    for pc in all_prior:
                        if pc.get("type") == "hypothesis":
                            pc_subject = pc.get("subject", "")
                            pc_exp = pc.get("expectation", "")
                            payload_subject = exp.probe_payload.get("subject", "")
                            if pc_subject == payload_subject or pc_exp in exp.expected_outcomes:
                                if pc["id"] in updated_ids:
                                    continue
                                updated_ids.add(pc["id"])
                                updated = dict(pc)
                                if outcome == "validated":
                                    updated["support_count"] = pc.get("support_count", 0) + 1
                                    prev_conf = pc.get("confidence", 0.5)
                                    updated["confidence"] = round(min(1.0, prev_conf + 0.05), 4)
                                    ev = dict(updated.get("evidence", {}))
                                    ev["experiment_validated"] = exp.id
                                    updated["evidence"] = ev
                                else:  # refuted
                                    updated["contradiction_count"] = pc.get("contradiction_count", 0) + 1
                                    prev_conf = pc.get("confidence", 0.5)
                                    updated["confidence"] = round(max(0.0, prev_conf - 0.05), 4)
                                    ev = dict(updated.get("evidence", {}))
                                    ev["experiment_refuted"] = exp.id
                                    updated["evidence"] = ev
                                self._store_single_candidate(updated)

                # Mark targeted question as resolved if experiment validated
                if outcome == "validated" and exp.target_type == "question":
                    for pc in all_prior:
                        if pc.get("type") == "question" and pc.get("id") == exp.target_id:
                            updated_q = dict(pc)
                            ev = dict(updated_q.get("evidence", {}))
                            ev["resolved_by"] = exp.id
                            ev["resolved_at"] = time.time()
                            ev["closed"] = True
                            updated_q["evidence"] = ev
                            updated_q["closed"] = True
                            self._store_single_candidate(updated_q)
                            break

                # Promote a validated dream into a grounded hypothesis
                if outcome == "validated" and exp.target_type == "dream":
                    dream_prior = next(
                        (pc for pc in all_prior if pc.get("id") == exp.target_id), None
                    )
                    if dream_prior:
                        path = dream_prior.get("path_or_context", [])
                        expectation = path[1] if isinstance(path, list) and len(path) > 1 else "confirmed"
                        new_hyp_id = _make_id("hyp", dream_prior.get("subject", ""), expectation)
                        new_hyp = HypothesisCandidate(
                            id=new_hyp_id,
                            generation=4,
                            subject=dream_prior.get("subject", ""),
                            expectation=expectation,
                            confidence=round(1.0 - dream_prior.get("confidence", 0.5), 4),
                            support_count=1,
                            contradiction_count=0,
                            parent_ids=[dream_prior.get("id", ""), exp.id],
                            evidence={
                                "promoted_from_dream": exp.target_id,
                                "experiment_validated": exp.id,
                            },
                        )
                        self._store_single_candidate(vars(new_hyp))

        return results
