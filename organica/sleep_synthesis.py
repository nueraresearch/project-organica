"""
Sleep Synthesis Mixin — Layers 2a, 3a, 4, 5.

Handles high-order composition, hypothesis retention, and dialectic tension:
  Layer 2a: MetaConcepts, Processes
  Layer 3a: WorkflowConcepts
  Layer 4:  Hypotheses & Falsification (with retention policies: salience, tension, etc.)
  Layer 5:  Theories & Questions (Dialectic Tension & Uncertainty)
"""

import math
from collections import defaultdict

from .candidates import (
    _make_id,
    MetaConceptCandidate,
    ProcessCandidate,
    WorkflowConceptCandidate,
    HypothesisCandidate,
    TheoryCandidate,
    QuestionCandidate,
)


class SleepSynthesisMixin:
    """Higher-level composition, dialectic, and belief evaluation methods."""

    # ==================================================================
    # Layer 2: Structural Composition (V1)
    # ==================================================================

    def _compose_meta_concepts(self, stable_prior: list[dict]) -> list[MetaConceptCandidate]:
        tag_refs: dict[str, list[tuple[str, str]]] = defaultdict(list)

        for c in stable_prior:
            cid = c.get("id", "")
            ctype = c.get("type", "")
            if not cid:
                continue

            tags = set()
            if "members" in c:
                tags.update(c["members"])
            if "source" in c and c["source"]:
                tags.add(c["source"])
            if "target" in c and c["target"]:
                tags.add(c["target"])
            if "path" in c and isinstance(c["path"], list):
                tags.update(c["path"])
            if "anchor_tag" in c and c["anchor_tag"]:
                tags.add(c["anchor_tag"])
            if "cycle" in c and isinstance(c["cycle"], list):
                tags.update(c["cycle"])
            if "components" in c and isinstance(c["components"], list):
                tags.update(c["components"])

            for tag in sorted(tags):
                tag_refs[tag].append((cid, ctype))

        candidates = []
        for tag in sorted(tag_refs.keys()):
            refs = tag_refs[tag]
            distinct_types = sorted(set(ctype for _, ctype in refs))
            distinct_ids = sorted(set(cid for cid, _ in refs))

            if len(distinct_types) >= 2 and len(distinct_ids) >= self.META_CONCEPT_MIN_REFS:
                mid = _make_id("meta", tag)
                avg_conf = 0.0
                conf_count = 0
                for c in stable_prior:
                    if c.get("id") in distinct_ids:
                        conf = c.get("confidence", c.get("strength", 0))
                        if conf:
                            avg_conf += conf
                            conf_count += 1
                if conf_count:
                    avg_conf /= conf_count

                candidates.append(MetaConceptCandidate(
                    id=mid,
                    generation=2,
                    parent_ids=distinct_ids[:10],
                    anchor_tag=tag,
                    related_candidates=len(distinct_ids),
                    confidence=round(min(1.0, avg_conf), 4),
                    evidence={
                        "distinct_candidate_types": distinct_types,
                        "candidate_count": len(distinct_ids),
                        "type_count": len(distinct_types),
                    },
                ))

        candidates.sort(key=lambda m: (-m.related_candidates, m.id))
        return candidates[:self.MAX_META_CONCEPTS]

    def _compose_processes(self, stable_prior: list[dict]) -> list[ProcessCandidate]:
        preds: dict[str, dict[str, dict]] = {}
        for c in stable_prior:
            if c.get("type") != "prediction_candidate":
                continue
            src = c.get("source", "")
            tgt = c.get("target", "")
            if src and tgt:
                if src not in preds:
                    preds[src] = {}
                existing = preds[src].get(tgt)
                c_strength = c.get("strength", 0)
                if not existing or c_strength > existing.get("strength", 0):
                    preds[src][tgt] = c

        if not preds:
            return []

        candidates = []
        seen_cycles: set[tuple] = set()
        sources = list(preds.keys())

        # 2-cycles
        for a in sources:
            for b in preds.get(a, {}):
                if b <= a:
                    continue
                if a in preds.get(b, {}):
                    cycle_key = tuple(sorted([a, b]))
                    if cycle_key not in seen_cycles:
                        seen_cycles.add(cycle_key)
                        pred_ab = preds[a][b]
                        pred_ba = preds[b][a]
                        strength = min(pred_ab.get("strength", 0), pred_ba.get("strength", 0))
                        parent_ids = [pred_ab.get("id", ""), pred_ba.get("id", "")]
                        parent_ids = [p for p in parent_ids if p]

                        pid = _make_id("process", a, b)
                        candidates.append(ProcessCandidate(
                            id=pid,
                            generation=2,
                            parent_ids=parent_ids,
                            cycle=[a, b],
                            strength=round(strength, 4),
                            evidence={
                                "cycle_length": 2,
                                "prediction_strengths": [
                                    round(pred_ab.get("strength", 0), 4),
                                    round(pred_ba.get("strength", 0), 4),
                                ],
                                "min_strength": round(strength, 4),
                            },
                        ))

        # 3-cycles
        for a in sources:
            for b in preds.get(a, {}):
                if b == a:
                    continue
                for c in preds.get(b, {}):
                    if c == a or c == b:
                        continue
                    if a in preds.get(c, {}):
                        cycle_key = tuple(sorted([a, b, c]))
                        if cycle_key not in seen_cycles:
                            seen_cycles.add(cycle_key)
                            pred_ab = preds[a][b]
                            pred_bc = preds[b][c]
                            pred_ca = preds[c][a]
                            strength = min(
                                pred_ab.get("strength", 0),
                                pred_bc.get("strength", 0),
                                pred_ca.get("strength", 0),
                            )
                            parent_ids = [
                                pred_ab.get("id", ""),
                                pred_bc.get("id", ""),
                                pred_ca.get("id", ""),
                            ]
                            parent_ids = [p for p in parent_ids if p]

                            pid = _make_id("process", a, b, c)
                            candidates.append(ProcessCandidate(
                                id=pid,
                                generation=2,
                                parent_ids=parent_ids,
                                cycle=[a, b, c],
                                strength=round(strength, 4),
                                evidence={
                                    "cycle_length": 3,
                                    "prediction_strengths": [
                                        round(pred_ab.get("strength", 0), 4),
                                        round(pred_bc.get("strength", 0), 4),
                                        round(pred_ca.get("strength", 0), 4),
                                    ],
                                    "min_strength": round(strength, 4),
                                },
                            ))

        candidates.sort(key=lambda p: (-p.strength, p.id))
        return candidates[:self.MAX_PROCESSES]

    # ==================================================================
    # Layer 3: High-Order Synthesis (Sleep V2)
    # ==================================================================

    def _compose_workflows(
        self,
        meta_concepts: list[MetaConceptCandidate],
        processes: list[ProcessCandidate],
        stable_prior: list[dict],
    ) -> list[WorkflowConceptCandidate]:
        if not processes or not meta_concepts:
            return []

        meta_by_anchor = {m.anchor_tag: m for m in meta_concepts}
        workflows = []

        for proc in processes:
            matched_metas = [meta_by_anchor[t] for t in proc.cycle if t in meta_by_anchor]

            if len(matched_metas) >= self.WORKFLOW_MIN_MATCHED_METAS:
                parent_ids = [proc.id] + [m.id for m in matched_metas]
                cycle_str = "_".join(proc.cycle)
                name = f"workflow_{cycle_str}"
                wid = _make_id("workflow", *sorted(proc.cycle))

                avg_conf = (proc.strength + sum(m.confidence for m in matched_metas)) / (1 + len(matched_metas))

                workflows.append(WorkflowConceptCandidate(
                    id=wid,
                    generation=3,
                    parent_ids=parent_ids,
                    name=name,
                    components=sorted(proc.cycle),
                    confidence=round(min(1.0, avg_conf), 4),
                    evidence={
                        "process_id": proc.id,
                        "process_strength": proc.strength,
                        "meta_concept_anchors": [m.anchor_tag for m in matched_metas],
                        "ancestor_count": len(parent_ids),
                    },
                ))

        workflows.sort(key=lambda w: w.confidence, reverse=True)
        return workflows[:self.MAX_WORKFLOWS]

    # ==================================================================
    # Layer 4: Falsifiable Hypotheses (Sleep V3)
    # ==================================================================

    def _form_and_test_hypotheses(
        self,
        temporal: dict[str, dict[str, int]],
        freqs: dict[str, int],
        workflows: list[WorkflowConceptCandidate],
        processes: list[ProcessCandidate],
        meta_concepts: list[MetaConceptCandidate],
        prior: list[dict],
    ) -> list[HypothesisCandidate]:
        prior_hyps = {h.get("id"): h for h in prior if h.get("type") == "hypothesis"}
        candidates: dict[str, HypothesisCandidate] = {}

        for w in workflows:
            comps = w.components
            for i in range(len(comps)):
                sub = comps[i]
                for j in range(len(comps)):
                    if i != j:
                        exp = comps[j]
                        hid = _make_id("hyp", sub, exp)
                        if hid not in candidates:
                            candidates[hid] = HypothesisCandidate(
                                id=hid,
                                generation=4,
                                subject=sub,
                                expectation=exp,
                                parent_ids=[w.id],
                            )
                        else:
                            if w.id not in candidates[hid].parent_ids:
                                candidates[hid].parent_ids.append(w.id)

        for p in processes:
            cycle = p.cycle
            for i in range(len(cycle)):
                sub = cycle[i]
                exp = cycle[(i + 1) % len(cycle)]
                hid = _make_id("hyp", sub, exp)
                if hid not in candidates:
                    candidates[hid] = HypothesisCandidate(
                        id=hid,
                        generation=4,
                        subject=sub,
                        expectation=exp,
                        parent_ids=[p.id],
                    )
                else:
                    if p.id not in candidates[hid].parent_ids:
                        candidates[hid].parent_ids.append(p.id)

        for m in meta_concepts:
            if m.related_candidates >= 5:
                hid = _make_id("hyp", m.anchor_tag, "high_structural_significance")
                candidates[hid] = HypothesisCandidate(
                    id=hid,
                    generation=4,
                    subject=m.anchor_tag,
                    expectation="high_structural_significance",
                    confidence=m.confidence,
                    support_count=m.related_candidates,
                    contradiction_count=0,
                    parent_ids=[m.id],
                    evidence={"type": "meta_centrality", "related_candidates": m.related_candidates},
                )

        results = []
        for hid, hyp in candidates.items():
            if hyp.expectation == "high_structural_significance":
                results.append(hyp)
                continue

            sub = hyp.subject
            exp = hyp.expectation

            targets = temporal.get(sub, {})
            support = targets.get(exp, 0)
            total_flow = sum(targets.values())
            raw_contradiction = max(0, total_flow - support)
            contradiction = raw_contradiction * self.CONTRADICTION_SCALE

            prior_h = prior_hyps.get(hid)
            prior_conf = prior_h.get("confidence") if prior_h else None

            if (support + contradiction) > 0:
                conf = round(support / (support + contradiction), 4)
            else:
                conf = 0.0

            if conf < self.DEATH_THRESHOLD and (support + contradiction) >= 3:
                continue

            hyp.confidence = conf
            hyp.support_count = support
            hyp.contradiction_count = contradiction
            hyp.evidence = {
                "support_count": support,
                "contradiction_count": contradiction,
                "raw_contradiction_count": raw_contradiction,
                "total_flow": total_flow,
                "prior_confidence": prior_conf,
                "revision_delta": round(conf - prior_conf, 4) if prior_conf is not None else 0.0,
            }
            results.append(hyp)

        markers = [h for h in results
                   if h.expectation == "high_structural_significance"]
        beliefs = [h for h in results
                   if h.expectation != "high_structural_significance"]

        info = self._belief_info(beliefs, prior_hyps, temporal)
        kept = self._retain_hypotheses(beliefs, info, temporal)
        kept_markers = self._retain_markers(markers, info)
        return kept + kept_markers

    # ==================================================================
    # Hypothesis retention
    # ==================================================================

    def _belief_info(self, beliefs, prior_hyps, temporal) -> dict:
        info = {}
        for h in beliefs:
            raw = h.evidence.get("raw_contradiction_count",
                                 h.contradiction_count)
            total = h.support_count + raw
            tension = (raw / total) if total > 0 else 0.0
            prior_h = prior_hyps.get(h.id)
            prior_conf = prior_h.get("confidence") if prior_h else None
            revision = abs(h.confidence - prior_conf) if prior_conf is not None else 0.0
            info[h.id] = {
                "support": h.support_count,
                "raw_contradiction": raw,
                "tension": tension,
                "novelty": 0.0 if prior_h else 1.0,
                "revision": revision,
            }
        return info

    def _subject_entropy(self, subject: str, temporal) -> float:
        counts = [c for c in temporal.get(subject, {}).values() if c > 0]
        if len(counts) < 2:
            return 0.0
        total = sum(counts)
        h = 0.0
        for c in counts:
            q = c / total
            h -= q * math.log2(q)
        return h / math.log2(len(counts))

    def _salience(self, beliefs, info, temporal) -> dict:
        w_tension, w_curiosity, w_novelty, w_revision = self.SALIENCE_WEIGHTS
        scores = {}
        for h in beliefs:
            i = info[h.id]
            scores[h.id] = (
                w_tension * i["tension"]
                + w_curiosity * self._subject_entropy(h.subject, temporal)
                + w_novelty * i["novelty"]
                + w_revision * i["revision"]
            )
        return scores

    def _retain_markers(self, markers, info) -> list:
        markers = sorted(markers, key=lambda h: (-h.confidence, h.subject))
        return markers[:self.MAX_STRUCTURAL_MARKERS]

    def _retain_hypotheses(self, beliefs, info, temporal) -> list:
        policy = self.HYPOTHESIS_RETENTION
        if policy not in self.VALID_RETENTION_POLICIES:
            raise ValueError(f"unknown HYPOTHESIS_RETENTION policy: {policy!r}")

        if not beliefs:
            return []

        if policy == "alphabetical":
            ranked = sorted(beliefs, key=lambda h: (h.subject, -h.confidence))
            return ranked[:self.MAX_HYPOTHESES]
        if policy == "confidence":
            ranked = sorted(beliefs, key=lambda h: (-h.confidence, h.subject))
            return ranked[:self.MAX_HYPOTHESES]
        if policy == "contradiction":
            ranked = sorted(beliefs, key=lambda h: (-h.contradiction_count, h.subject))
            return ranked[:self.MAX_HYPOTHESES]
        if policy == "tension":
            ranked = sorted(beliefs, key=lambda h: (-info[h.id]["tension"], h.subject))
            return ranked[:self.MAX_HYPOTHESES]
        if policy == "shannon_entropy":
            ranked = sorted(
                beliefs,
                key=lambda h: (-self._subject_entropy(h.subject, temporal), h.subject),
            )
            return ranked[:self.MAX_HYPOTHESES]

        scores = self._salience(beliefs, info, temporal)

        if policy == "salience":
            ranked = sorted(beliefs, key=lambda h: (-scores[h.id], h.subject))
            return ranked[:self.MAX_HYPOTHESES]
        if policy == "stochastic":
            return self._stochastic_retain(beliefs, scores)

        raise ValueError(f"unknown HYPOTHESIS_RETENTION policy: {policy!r}")

