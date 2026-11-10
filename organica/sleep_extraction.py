"""
Sleep Extraction Mixin — Layers 1, 2b, 3b and Graph Analysis.

Handles tag scoring, graph topological metrics, community clustering,
Layer 1 candidate building (Concepts, Phrases, Loops, Predictions, Anomalies),
Layer 2b RoleCandidates, and Layer 3b SchemaCandidates.
"""

import math
from collections import defaultdict
from typing import Optional, Any

from .candidates import (
    _make_id,
    _TagScore,
    ConceptCandidate,
    PhraseCandidate,
    LoopCandidate,
    PredictionCandidate,
    AnomalyCandidate,
    RoleCandidate,
    SchemaCandidate,
)


def _polarity(sent: int, received: int) -> int:
    """+1 if the tag sends more than it receives, -1 if it receives more, 0 if flat."""
    if sent > received:
        return 1
    if received > sent:
        return -1
    return 0


def role_polarity_match(
    out_u: int, in_u: int, out_v: int, in_v: int,
    schema_source_polarity: int, schema_target_polarity: int,
) -> bool:
    """Content-sensitive schema congruence (decision D2).

    A schema may reorder a candidate edge u->v only when the schema's stored
    sender/receiver polarity agrees with the edge's own flow polarity at both ends.
    An unknown polarity (0) never matches, so a flat world cannot borrow a schema.
    """
    if schema_source_polarity == 0 or schema_target_polarity == 0:
        return False
    return (
        _polarity(out_u, in_u) == schema_source_polarity
        and _polarity(in_v, out_v) == schema_target_polarity
    )


class SleepExtractionMixin:
    """Extraction and low-level candidate construction methods."""

    # ==================================================================
    # Tag scoring (internal)
    # ==================================================================

    def _score_tags(self, freqs, cooc, temporal) -> list[_TagScore]:
        scores = []
        all_tags = sorted(set(freqs) | set(cooc) | set(temporal))
        for tag in all_tags:
            freq      = freqs.get(tag, 0)
            neighbors = set(cooc.get(tag, {}).keys())
            degree    = len(neighbors)
            clustering = self._clustering_coefficient(tag, neighbors, cooc)
            p_reach   = self._predictive_reach(tag, neighbors, temporal)
            score = _TagScore(
                tag=tag, frequency=freq, degree=degree,
                clustering=clustering, predictive_reach=p_reach,
            )
            score.classification = self._classify(score)
            scores.append(score)
        scores.sort(key=lambda s: (-s.frequency, s.tag))
        return scores

    def _clustering_coefficient(self, tag, neighbors, cooc) -> float:
        k = len(neighbors)
        if k < 2:
            return 0.0
        possible = k * (k - 1) / 2
        actual = 0
        neighbor_list = list(neighbors)
        for i in range(len(neighbor_list)):
            for j in range(i + 1, len(neighbor_list)):
                if neighbor_list[j] in cooc.get(neighbor_list[i], {}):
                    actual += 1
        return actual / possible

    def _predictive_reach(self, tag, cooc_neighbors, temporal) -> int:
        temporal_targets = set(temporal.get(tag, {}).keys())
        outside = temporal_targets - cooc_neighbors - {tag}
        return len(outside)

    def _classify(self, s: _TagScore) -> str:
        if s.frequency <= 1 and s.degree <= 1:
            return "noise"
        if s.clustering >= self.PHRASE_MIN_CLUSTERING and s.predictive_reach <= self.PHRASE_MAX_REACH:
            return "phrase_fragment"
        if (s.degree >= self.CONCEPT_MIN_DEGREE
                and s.clustering <= self.CONCEPT_MAX_CLUSTERING
                and s.predictive_reach >= self.CONCEPT_MIN_REACH):
            return "concept"
        if s.degree >= 5:
            return "hub"
        return "unclassified"

    # ==================================================================
    # Layer 1 Candidate Builders
    # ==================================================================

    def _build_concepts(self, tag_scores, communities, cooc) -> list[ConceptCandidate]:
        concept_tags = {s.tag: s for s in tag_scores if s.classification == "concept"}
        if not concept_tags:
            return []

        tag_to_community: dict[str, int] = {}
        for cid, members, density in communities:
            for t in members:
                tag_to_community[t] = cid

        by_community: dict[int, list[_TagScore]] = defaultdict(list)
        orphans: list[_TagScore] = []
        for tag, score in concept_tags.items():
            cid = tag_to_community.get(tag)
            if cid is not None:
                by_community[cid].append(score)
            else:
                orphans.append(score)

        tag_events = getattr(self, "_current_tag_events", {})
        candidates = []

        for cid, scores in by_community.items():
            members = sorted([s.tag for s in scores])
            edge_count = 0
            for i, m1 in enumerate(members):
                for m2 in members[i+1:]:
                    edge_count += cooc.get(m1, {}).get(m2, 0)

            avg_clust = sum(s.clustering for s in scores) / len(scores)
            avg_reach = sum(s.predictive_reach for s in scores) / len(scores)
            avg_degree = sum(s.degree for s in scores) / len(scores)
            total_obs = sum(s.frequency for s in scores)

            # Grounding Layer 1 Lineage to Events (Defect D3)
            supporting_events: list[str] = []
            for m in members:
                for eid in tag_events.get(m, []):
                    if eid not in supporting_events:
                        supporting_events.append(eid)

            cid_str = _make_id("concept", *members)
            candidates.append(ConceptCandidate(
                id=cid_str,
                parent_ids=supporting_events[:10],
                members=members,
                confidence=min(1.0, (avg_reach / 8) * (1 - avg_clust)),
                evidence={
                    "community_id": cid,
                    "edge_count": edge_count,
                    "observations": total_obs,
                    "avg_clustering": round(avg_clust, 3),
                    "avg_predictive_reach": round(avg_reach, 1),
                    "avg_degree": round(avg_degree, 1),
                },
            ))

        for score in orphans:
            cid_str = _make_id("concept", score.tag)
            orphan_events = tag_events.get(score.tag, [])[:10]
            candidates.append(ConceptCandidate(
                id=cid_str,
                parent_ids=orphan_events,
                members=[score.tag],
                confidence=min(1.0, (score.predictive_reach / 8) * (1 - score.clustering)),
                evidence={
                    "edge_count": sum(cooc.get(score.tag, {}).values()),
                    "observations": score.frequency,
                    "avg_clustering": round(score.clustering, 3),
                    "avg_predictive_reach": score.predictive_reach,
                    "avg_degree": score.degree,
                },
            ))

        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates

    def _build_phrases(self, tag_scores, cooc) -> list[PhraseCandidate]:
        fragments = [s for s in tag_scores if s.classification == "phrase_fragment"]
        if not fragments:
            return []

        frag_set = {s.tag for s in fragments}
        visited: set[str] = set()
        groups: list[list[_TagScore]] = []
        score_map = {s.tag: s for s in fragments}

        for s in fragments:
            if s.tag in visited:
                continue
            group = []
            queue = [s.tag]
            while queue:
                t = queue.pop()
                if t in visited or t not in frag_set:
                    continue
                visited.add(t)
                group.append(score_map[t])
                for neighbor in cooc.get(t, {}):
                    if neighbor in frag_set and neighbor not in visited:
                        queue.append(neighbor)
            if group:
                groups.append(group)

        tag_events = getattr(self, "_current_tag_events", {})
        candidates = []
        for group in groups:
            members = sorted([s.tag for s in group])
            edge_count = 0
            for i, m1 in enumerate(members):
                for m2 in members[i+1:]:
                    edge_count += cooc.get(m1, {}).get(m2, 0)

            avg_clust = sum(s.clustering for s in group) / len(group)
            avg_reach = sum(s.predictive_reach for s in group) / len(group)

            supporting_events: list[str] = []
            for m in members:
                for eid in tag_events.get(m, []):
                    if eid not in supporting_events:
                        supporting_events.append(eid)

            pid = _make_id("phrase", *members)
            candidates.append(PhraseCandidate(
                id=pid,
                parent_ids=supporting_events[:10],
                members=members,
                confidence=min(1.0, avg_clust),
                evidence={
                    "avg_clustering": round(avg_clust, 3),
                    "avg_predictive_reach": round(avg_reach, 1),
                    "edge_count": edge_count,
                },
            ))

        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates

    def _build_loops(self, temporal) -> list[LoopCandidate]:
        tag_events = getattr(self, "_current_tag_events", {})
        loops = []
        seen: set[tuple] = set()
        tags = list(temporal.keys())

        def canonical_cycle(nodes: list[str]) -> list[str]:
            """Return rotation of directed cycle starting with lexicographically minimal node."""
            min_i = min(range(len(nodes)), key=lambda i: nodes[i])
            rotated = nodes[min_i:] + nodes[:min_i]
            return rotated + [rotated[0]]

        # 2-cycles
        for a in tags:
            for b, count_ab in sorted(temporal[a].items()):
                if b <= a:
                    continue
                count_ba = temporal.get(b, {}).get(a, 0)
                strength = min(count_ab, count_ba)
                if strength >= self.LOOP_MIN_STRENGTH:
                    pair = tuple(sorted([a, b]))
                    if pair not in seen:
                        seen.add(pair)
                        lid = _make_id("loop", a, b)
                        supporting_events = [eid for eid in tag_events.get(a, []) if eid in tag_events.get(b, [])][:10]
                        if not supporting_events:
                            supporting_events = (tag_events.get(a, [])[:5] + tag_events.get(b, [])[:5])[:10]
                        loops.append(LoopCandidate(
                            id=lid,
                            parent_ids=supporting_events,
                            path=[a, b, a],
                            strength=strength,
                            evidence={
                                "min_edge_count": strength,
                                "edge_counts": [count_ab, count_ba],
                                "cycle_length": 2,
                            },
                        ))

        # 3-cycles
        for a in tags:
            for b in sorted(temporal.get(a, {}).keys()):
                if b == a:
                    continue
                for c in sorted(temporal.get(b, {}).keys()):
                    if c == a or c == b:
                        continue
                    count_ca = temporal.get(c, {}).get(a, 0)
                    if count_ca >= self.LOOP_MIN_STRENGTH:
                        counts = [
                            temporal[a].get(b, 0),
                            temporal[b].get(c, 0),
                            count_ca,
                        ]
                        strength = min(counts)
                        if strength >= self.LOOP_MIN_STRENGTH:
                            cycle = tuple(sorted([a, b, c]))
                            if cycle not in seen:
                                seen.add(cycle)
                                norm_path = canonical_cycle([a, b, c])
                                lid = _make_id("loop", *norm_path[:-1])
                                supporting_events = (tag_events.get(a, [])[:3] + tag_events.get(b, [])[:3] + tag_events.get(c, [])[:4])[:10]
                                loops.append(LoopCandidate(
                                    id=lid,
                                    parent_ids=supporting_events,
                                    path=norm_path,
                                    strength=strength,
                                    evidence={
                                        "min_edge_count": strength,
                                        "edge_counts": counts,
                                        "cycle_length": 3,
                                    },
                                ))

        # Compute per-tag target entropy for structural ranking
        out_counts: dict[str, int] = {}
        for t in temporal:
            total = sum(temporal[t].values())
            if total > 0:
                out_counts[t] = total

        tag_entropy: dict[str, float] = {}
        for t, total in out_counts.items():
            ent = 0.0
            for cnt in temporal[t].values():
                if cnt > 0:
                    p = cnt / total
                    ent -= p * math.log2(p)
            tag_entropy[t] = round(ent, 4)

        for lc in loops:
            path_tags = [tag for tag in lc.path if tag in tag_entropy]
            min_ent = min((tag_entropy[t] for t in path_tags), default=0.0)
            lc.evidence["path_min_entropy"] = min_ent

        loops.sort(key=lambda l: (
            l.evidence.get("path_min_entropy", 0.0),
            -l.strength,
            l.id,
        ))
        return loops[:self.MAX_LOOPS]

    def _build_predictions(self, temporal, freqs, prior_schemas: list[dict] | None = None) -> list[PredictionCandidate]:
        # Source-frequency decay is promoted engine behavior: the denominator that
        # normalises a temporal edge must decay with the graph it divides.
        freqs = self._prediction_frequencies(freqs)
        if prior_schemas is None:
            prior_schemas = getattr(self, "_current_prior_schemas", None)
        cooc = getattr(self, "_current_cooc", None)
        cooc_pairs = set()
        if cooc:
            for a, targets in cooc.items():
                for b in targets:
                    cooc_pairs.add(tuple(sorted([a, b])))

        tag_events = getattr(self, "_current_tag_events", {})
        # Collect outgoing counts for transition probability P(target | source)
        out_counts: dict[str, int] = defaultdict(int)
        raw_out_counts: dict[str, int] = defaultdict(int)
        raw_in_counts: dict[str, int] = defaultdict(int)
        for tag_from, targets in temporal.items():
            for tag_to, count in targets.items():
                raw_out_counts[tag_from] += count
                raw_in_counts[tag_to] += count
                if count >= self.PREDICTION_MIN_COUNT:
                    out_counts[tag_from] += count

        # Consolidated relational schema, used ONLY as a ranking prior.
        # A schema may reorder candidates that already meet PREDICTION_MIN_COUNT;
        # it may never admit one that does not (earned-evidence contract,
        # docs/DECISION-EARNED-SCHEMA-PRIMING.md D1-D2).
        best_schema = None
        if prior_schemas:
            valid_schemas = [
                s for s in prior_schemas
                if (s.get("confidence") or s.get("strength") or 0) >= self.STABLE_THRESHOLD
            ]
            if valid_schemas:
                best_schema = max(valid_schemas, key=lambda s: (s.get("confidence") or s.get("strength") or 0))

        # Sender/receiver polarity of every tag, used to test whether a schema's
        # role assignment is congruent with a candidate edge (decision D2).
        out_flow: dict[str, int] = {t: sum(v.values()) for t, v in temporal.items()}
        in_flow: dict[str, int] = defaultdict(int)
        for _src, _targets in temporal.items():
            for _tgt, _cnt in _targets.items():
                in_flow[_tgt] += _cnt

        schema_source_polarity = 0
        schema_target_polarity = 0
        if best_schema:
            _ev = best_schema.get("evidence", {}) or {}
            _src_profile = _ev.get("source_role_profile", {}) or {}
            _tgt_profile = _ev.get("target_role_profile", {}) or {}
            schema_source_polarity = _polarity(
                int(_src_profile.get("out_degree", 0) or 0),
                int(_src_profile.get("in_degree", 0) or 0),
            )
            schema_target_polarity = _polarity(
                int(_tgt_profile.get("in_degree", 0) or 0),
                int(_tgt_profile.get("out_degree", 0) or 0),
            )

        # Compute target entropy H(T | source) for each source
        # H(T | u) = - \sum_v P(v|u) * log2 P(v|u)
        source_entropy: dict[str, float] = {}
        for tag_from, total_out in out_counts.items():
            if total_out <= 0:
                continue
            ent = 0.0
            for tag_to, count in temporal[tag_from].items():
                if count >= self.PREDICTION_MIN_COUNT:
                    p = count / total_out
                    if p > 0:
                        ent -= p * math.log2(p)
            source_entropy[tag_from] = round(ent, 4)

        transitions: list[PredictionCandidate] = []
        cooccurrences: list[PredictionCandidate] = []

        for tag_from in sorted(temporal.keys()):
            targets = temporal[tag_from]
            source_freq = freqs.get(tag_from, 1)
            ent = source_entropy.get(tag_from, 0.0)
            for tag_to in sorted(targets.keys()):
                count = targets[tag_to]
                meets_direct = count >= self.PREDICTION_MIN_COUNT
                matching_schema_id = None
                schema_congruent = False

                if meets_direct and best_schema and tag_from != tag_to:
                    # Content-sensitive prior (decision D2): the schema's sender/receiver
                    # polarity must agree with this edge's own flow polarity. Congruence
                    # reorders admissible candidates; it never supplies evidence.
                    if role_polarity_match(
                        out_flow.get(tag_from, 0), in_flow.get(tag_from, 0),
                        out_flow.get(tag_to, 0), in_flow.get(tag_to, 0),
                        schema_source_polarity, schema_target_polarity,
                    ):
                        schema_congruent = True
                        matching_schema_id = best_schema.get("id", "")

                if meets_direct:
                    ratio = count / max(source_freq, 1)
                    trans_prob = count / max(out_counts[tag_from], 1)
                    pid = _make_id("pred", tag_from, tag_to)
                    is_cooc = tuple(sorted([tag_from, tag_to])) in cooc_pairs
                    
                    # Grounding Layer 1 Lineage to Events (Defect D3)
                    supporting_events = [eid for eid in tag_events.get(tag_from, []) if eid in tag_events.get(tag_to, [])][:10]
                    if not supporting_events:
                        supporting_events = (tag_events.get(tag_from, [])[:5] + tag_events.get(tag_to, [])[:5])[:10]

                    parent_ids = list(supporting_events)
                    if schema_congruent and matching_schema_id:
                        parent_ids.insert(0, matching_schema_id)

                    cand_strength = min(1.0, ratio)

                    evidence_dict = {
                        "temporal_count": count,
                        "source_frequency": source_freq,
                        "target_frequency": freqs.get(tag_to, 0),
                        "ratio": round(ratio, 3),
                        "transition_prob": round(trans_prob, 4),
                        "target_entropy": ent,
                        "is_cooccurrence": is_cooc,
                    }
                    if schema_congruent and matching_schema_id:
                        evidence_dict["schema_prior"] = matching_schema_id
                        evidence_dict["schema_confidence"] = best_schema.get("confidence")

                    cand = PredictionCandidate(
                        id=pid,
                        parent_ids=parent_ids,
                        source=tag_from,
                        target=tag_to,
                        strength=cand_strength,
                        evidence=evidence_dict,
                    )
                    if is_cooc:
                        cooccurrences.append(cand)
                    else:
                        transitions.append(cand)

        # Sort transitions by predictive information:
        # 1. Target entropy ascending (lower entropy = more deterministic/unique successor)
        # 2. Transition probability descending P(v|u)
        # 3. Temporal count descending
        transitions.sort(key=lambda p: (
            0 if p.evidence.get("schema_prior") else 1,
            p.evidence.get("target_entropy", 999.0),
            -p.evidence.get("transition_prob", 0.0),
            -p.evidence["temporal_count"],
            p.source,
            p.target
        ))
        # Sort cooccurrences by count
        cooccurrences.sort(key=lambda p: (-p.evidence["temporal_count"], p.source, p.target))

        # Stratified allocation:
        # Guarantee transitions a minimum allocation of half the budget (e.g. 10 of 20),
        # letting transitions expand into any unused cooccurrence quota.
        half_cap = self.MAX_PREDICTIONS // 2
        selected_transitions = transitions[:half_cap]
        remaining_budget = self.MAX_PREDICTIONS - len(selected_transitions)
        selected_cooc = cooccurrences[:remaining_budget]
        
        candidates = selected_transitions + selected_cooc
        # Fill any remainder with more transitions if cooccurrences didn't fill the quota
        if len(candidates) < self.MAX_PREDICTIONS:
            more_trans = [t for t in transitions[half_cap:] if t not in candidates]
            candidates.extend(more_trans[:self.MAX_PREDICTIONS - len(candidates)])

        return candidates[:self.MAX_PREDICTIONS]

    def _build_anomalies(self, temporal, freqs) -> list[AnomalyCandidate]:
        anomalies = []
        for tag_from in sorted(temporal.keys()):
            targets = temporal[tag_from]
            if not targets:
                continue
            sorted_targets = sorted(targets.items(), key=lambda x: (-x[1], x[0]))
            if len(sorted_targets) < 2:
                continue
            top_tag, top_count = sorted_targets[0]
            for other_tag, other_count in sorted_targets[1:]:
                if top_count >= 3 * other_count and other_count >= 2:
                    aid = _make_id("anomaly", tag_from, top_tag, other_tag)
                    anomalies.append(AnomalyCandidate(
                        id=aid,
                        expected=top_tag,
                        observed=other_tag,
                        context=tag_from,
                        evidence={
                            "expected_count": top_count,
                            "observed_count": other_count,
                            "dominance_ratio": round(top_count / max(other_count, 1), 2),
                        },
                    ))

        # Compute target entropy for each anomaly context (source tag)
        for anom in anomalies:
            ctx = anom.context
            ctx_targets = temporal.get(ctx, {})
            total = sum(ctx_targets.values())
            if total > 0:
                ent = 0.0
                for cnt in ctx_targets.values():
                    if cnt > 0:
                        p = cnt / total
                        ent -= p * math.log2(p)
                anom.evidence["source_entropy"] = round(ent, 4)
            else:
                anom.evidence["source_entropy"] = 0.0

        anomalies.sort(key=lambda a: (
            a.evidence.get("source_entropy", 999.0),  # low entropy first (more structural)
            -a.evidence["dominance_ratio"],
            a.id,
        ))
        return anomalies[:self.MAX_ANOMALIES]

    def _extract_structural_roles(
        self, communities, concepts, temporal, freqs, predictions, recent_events
    ) -> list[RoleCandidate]:
        """Layer 2b: Extract evidence-derived structural roles from coherent topological clusters.
        Each role encapsulates empirical structural properties (in/out degree, retention, flow bias).
        """
        roles: list[RoleCandidate] = []
        candidate_groups: list[list[str]] = []
        for _, tags, _ in communities:
            if len(tags) >= 2 and tags not in candidate_groups:
                candidate_groups.append(tags)
        for c in concepts:
            if len(c.members) >= 2 and c.members not in candidate_groups:
                candidate_groups.append(c.members)

        cooc = getattr(self, "_current_cooc", {}) or {}

        for group in candidate_groups:
            within_flow = 0
            for u in group:
                for v in group:
                    if u != v:
                        within_flow += temporal.get(u, {}).get(v, 0)

            out_flow = 0
            for u in group:
                for v, cnt in temporal.get(u, {}).items():
                    if v not in group:
                        out_flow += cnt

            in_flow = 0
            for u, targets in temporal.items():
                if u not in group:
                    for v in group:
                        in_flow += targets.get(v, 0)

            total_ext = out_flow + in_flow
            retention = round(within_flow / max(within_flow + out_flow, 1), 3)
            flow_bias = round((out_flow - in_flow) / max(total_ext, 1), 3)

            k = len(group)
            possible = k * (k - 1) / 2
            actual_edges = 0
            for x in range(len(group)):
                for y in range(x + 1, len(group)):
                    if group[y] in cooc.get(group[x], {}) or group[x] in cooc.get(group[y], {}):
                        actual_edges += 1
            cohesion = round(actual_edges / possible if possible > 0 else 1.0, 3)

            parent_ids = [c.id for c in concepts if set(c.members) == set(group)][:5]
            if not parent_ids:
                parent_ids = [p.id for p in predictions if p.source in group or p.target in group][:5]

            rid = _make_id("role", *sorted(group))
            conf = min(1.0, round(0.4 + 0.3 * cohesion + 0.3 * min(within_flow / 20.0, 1.0), 3))

            profile = {
                "in_degree": in_flow,
                "out_degree": out_flow,
                "retention": retention,
                "cross_flow": total_ext,
                "cohesion": cohesion,
                "flow_bias": flow_bias,
            }

            roles.append(RoleCandidate(
                id=rid,
                generation=2,
                parent_ids=parent_ids,
                exemplars=sorted(group),
                profile=profile,
                confidence=conf,
                evidence={
                    "member_count": len(group),
                    "within_flow": within_flow,
                    "profile": profile,
                }
            ))

        roles.sort(key=lambda r: r.confidence, reverse=True)
        return roles[:self.MAX_ROLES]

    # ==================================================================
    # Layer 3b: Relational Schemas (Structural Abstraction & Reuse)
    # ==================================================================

    def _extract_relational_schemas(
        self, temporal, freqs, communities, concepts, predictions, prior,
        roles: list[RoleCandidate] | None = None,
        recent_events: list[Any] | None = None,
    ) -> list[SchemaCandidate]:
        """Layer 3b: Extract abstract relational schemas connecting structural roles.
        Gated by event-level transition contingency and directional asymmetry:
        - Treatment (structured transitions): high contingency (ratio >= 2.0) -> forms schema
        - Orthogonal (random transitions): flat noise (ratio ~ 1.0) -> rejected (no schema)
        """
        schemas: list[SchemaCandidate] = []

        # 1. Identify candidate roles/clusters
        role_list = list(roles or [])
        if not role_list:
            # Construct ephemeral roles from discovered communities / concepts
            candidate_groups: list[list[str]] = []
            for _, tags, _ in communities:
                if len(tags) >= 2 and tags not in candidate_groups:
                    candidate_groups.append(tags)
            for c in concepts:
                if len(c.members) >= 2 and c.members not in candidate_groups:
                    candidate_groups.append(c.members)
            for g in candidate_groups:
                rid = _make_id("role", *sorted(g))
                role_list.append(RoleCandidate(
                    id=rid,
                    generation=2,
                    exemplars=sorted(g),
                    profile={"cohesion": 1.0},
                    confidence=0.5,
                ))

        # 2. Check transition contingency between role pairs
        for i in range(len(role_list)):
            for j in range(len(role_list)):
                if i == j:
                    continue
                r_a = role_list[i]
                r_b = role_list[j]
                set_a = set(r_a.exemplars)
                set_b = set(r_b.exemplars)
                if set_a & set_b:
                    continue

                # Measure event-level transition contingency from chronological stream
                cross_switches = 0
                self_switches = 0
                if recent_events and len(recent_events) >= 10:
                    events_chrono = list(reversed(recent_events))
                    for idx in range(len(events_chrono) - 1):
                        c_tags = set(events_chrono[idx].tags)
                        n_tags = set(events_chrono[idx + 1].tags)
                        in_a = bool(c_tags & set_a)
                        next_a = bool(n_tags & set_a)
                        next_b = bool(n_tags & set_b)
                        if in_a and next_b:
                            cross_switches += 1
                        elif in_a and next_a:
                            self_switches += 1

                contingency_ratio = cross_switches / max(self_switches, 1)

                # Fallback to temporal graph
                flow_a_to_b = sum(temporal.get(u, {}).get(v, 0) for u in set_a for v in set_b)
                flow_b_to_a = sum(temporal.get(v, {}).get(u, 0) for v in set_b for u in set_a)
                flow_ratio = flow_a_to_b / max(flow_b_to_a, 1)

                # Structural contingency gate:
                # - If chronological events present: requires cross_switches >= 4 and contingency_ratio >= 2.0
                # - If pure temporal graph (unit tests): requires flow_a_to_b >= 4 and flow_ratio >= 1.10
                is_contingent = False
                measured_ratio = 1.0
                if flow_a_to_b > flow_b_to_a:
                    if cross_switches >= 4 and contingency_ratio >= 2.0:
                        is_contingent = True
                        measured_ratio = contingency_ratio
                    elif (not recent_events or len(recent_events) < 10) and flow_a_to_b >= 4 and flow_ratio >= 1.10:
                        is_contingent = True
                        measured_ratio = flow_ratio

                if is_contingent:
                    # Context-bearing identity (decision D3): two worlds never share a
                    # schema id, so decay and provenance are resolvable per context.
                    sid = _make_id(
                        "schema", "antecedent", "consequent",
                        *sorted(r_a.exemplars), *sorted(r_b.exemplars),
                    )
                    conf = min(0.75, round(0.4 + 0.05 * min(measured_ratio, 6.0), 3))

                    parent_ids = [r_a.id, r_b.id]
                    parent_ids.extend([
                        p.id for p in predictions
                        if p.source in set_a and p.target in set_b
                    ][:8])

                    schema = SchemaCandidate(
                        id=sid,
                        generation=3,
                        parent_ids=parent_ids,
                        source_role="antecedent",
                        target_role="consequent",
                        source_role_id=r_a.id,
                        target_role_id=r_b.id,
                        source_exemplars=r_a.exemplars,
                        target_exemplars=r_b.exemplars,
                        confidence=conf,
                        evidence={
                            "forward_flow": flow_a_to_b,
                            "backward_flow": flow_b_to_a,
                            "directional_ratio": round(measured_ratio, 3),
                            "cross_switches": cross_switches,
                            "self_switches": self_switches,
                            "contingency_ratio": round(contingency_ratio, 3),
                            "source_role_profile": r_a.profile,
                            "target_role_profile": r_b.profile,
                        },
                    )
                    schemas.append(schema)

        # Deduplicate and sort schemas by confidence descending
        unique_schemas: dict[str, SchemaCandidate] = {}
        for s in schemas:
            key = f"{s.source_role_id}->{s.target_role_id}"
            if key not in unique_schemas or s.confidence > unique_schemas[key].confidence:
                unique_schemas[key] = s

        sorted_schemas = sorted(unique_schemas.values(), key=lambda s: -s.confidence)
        return sorted_schemas[:self.MAX_SCHEMAS]

    def _find_communities(self, cooc) -> list[tuple[int, list[str], float]]:
        filtered: dict[str, set[str]] = defaultdict(set)
        for tag, neighbors in cooc.items():
            for neighbor, count in neighbors.items():
                if count >= self.COOC_MIN_EDGE:
                    filtered[tag].add(neighbor)
                    filtered[neighbor].add(tag)

        visited: set[str] = set()
        components: list[set[str]] = []
        for start in filtered:
            if start in visited:
                continue
            component: set[str] = set()
            queue = [start]
            while queue:
                node = queue.pop()
                if node in visited:
                    continue
                visited.add(node)
                component.add(node)
                queue.extend(filtered[node] - visited)
            if len(component) >= 2:
                components.append(component)

        results = []
        for i, component in enumerate(components):
            tags = sorted(component)
            k = len(tags)
            possible = k * (k - 1) / 2
            actual = 0
            for x in range(len(tags)):
                for y in range(x + 1, len(tags)):
                    if tags[y] in cooc.get(tags[x], {}):
                        actual += 1
            density = actual / possible if possible > 0 else 0.0
            results.append((i, tags, density))

        results.sort(key=lambda c: c[2], reverse=True)
        return results
