"""
Sleep Selection Mixin — Candidate Persistence, Lineage and Natural Selection (Law VI).

Handles:
  - Database loading for co-occurrences, temporal edges, prior candidates
  - Deep ancestry graph reconstruction
  - Natural selection pass (reinforcement, decay, pruning) across G1–G8
  - Storage of consolidated sleep candidates and cycle metadata
"""

import json
from collections import defaultdict
from dataclasses import asdict
from typing import Optional, Any

from .candidates import SleepReport


class SleepSelectionMixin:
    """Natural selection, ancestry tracing, and persistence methods."""

    def get_ancestry(self, candidate_id: str, max_depth: int = 7) -> dict:
        priors = self._load_prior_candidates()
        by_id = {c["id"]: c for c in priors if "id" in c}

        def build_tree(cid: str, current_depth: int) -> dict:
            if cid not in by_id or current_depth >= max_depth:
                return {"id": cid, "found": cid in by_id}
            node = by_id[cid]
            tree = {
                "id": cid,
                "type": node.get("type"),
                "generation": node.get("generation", 1),
                "confidence": node.get("confidence", node.get("strength")),
                "parents": [build_tree(pid, current_depth + 1) for pid in node.get("parent_ids", [])]
            }
            return tree

        return build_tree(candidate_id, 0)

    # ==================================================================
    # Graph loading
    # ==================================================================

    def _load_cooccurrences(self) -> dict[str, dict[str, int]]:
        graph: dict[str, dict[str, int]] = defaultdict(dict)
        for a, b, count in self.memory.cooccurrences(min_count=1):
            graph[a][b] = count
            graph[b][a] = count
        return graph

    def _load_temporal(self) -> dict[str, dict[str, int]]:
        graph: dict[str, dict[str, int]] = defaultdict(dict)
        for tag_from, tag_to, count in self.memory.temporal_edges(min_count=1):
            graph[tag_from][tag_to] = count
        return graph

    def _load_prior_candidates(self) -> list[dict]:
        if getattr(self, "_prior_cache", None) is not None:
            return self._prior_cache
        events = self.memory.recent(n=4000, event_type="sleep")
        candidates = []
        for e in events:
            if e.source.startswith("sleep:") and e.source != "sleep:meta":
                try:
                    candidates.append(json.loads(e.content))
                except (json.JSONDecodeError, ValueError):
                    pass
        return candidates

    def _count_prior_cycles(self, prior: list[dict]) -> int:
        """Return the highest sleep-cycle number recorded so far."""
        return self.memory.latest_sleep_cycle()

    # ==================================================================
    # Natural Selection: Reinforcement, Decay & Pruning
    # ==================================================================

    def _natural_selection(
        self, prior, concepts, phrases, loops, predictions,
        meta_concepts=None, processes=None, roles=None, workflows=None, schemas=None,
        hypotheses=None, theories=None, questions=None,
        dreams=None, investigations=None, experiments=None,
    ) -> tuple[int, int, int]:
        """Apply natural selection (Law VI) across all generations G1–G8.

        Candidates that re-emerge in the current synthesis cycle are strengthened.
        Those absent decay by DEATH_FACTOR (×0.8). Those below DEATH_THRESHOLD
        are pruned.
        """
        strengthened = 0
        decayed = 0
        pruned = 0

        # Build set of content-identity keys for all current-cycle candidates.
        current_keys: set[str] = set()
        # G1
        for c in concepts:
            current_keys.add(f"concept:{'|'.join(sorted(c.members))}")
        for p in phrases:
            current_keys.add(f"phrase:{'|'.join(sorted(p.members))}")
        for l in loops:
            current_keys.add(f"loop:{'|'.join(l.path)}")
        for p in predictions:
            current_keys.add(f"prediction:{p.source}|{p.target}")
        # G2
        for m in (meta_concepts or []):
            if m.anchor_tag:
                current_keys.add(f"meta_concept:{m.anchor_tag}")
        for p in (processes or []):
            if p.cycle:
                current_keys.add(f"process:{'|'.join(sorted(p.cycle))}")
        for r in (roles or []):
            if r.exemplars:
                current_keys.add(f"role:{'|'.join(sorted(r.exemplars))}")
        # G3
        for w in (workflows or []):
            if w.components:
                current_keys.add(f"workflow:{'|'.join(sorted(w.components))}")
        for s in (schemas or []):
            if s.source_role and s.target_role:
                current_keys.add(f"schema:{s.source_role}->{s.target_role}")
        # G4
        for h in (hypotheses or []):
            if h.subject:
                current_keys.add(f"hypothesis:{h.subject}|{h.expectation}")
        # G5
        for t in (theories or []):
            if t.subject:
                current_keys.add(f"theory:{t.subject}|{'|'.join(sorted(t.hypotheses))}")
        for q in (questions or []):
            if q.subject:
                current_keys.add(f"question:{q.subject}|{'|'.join(sorted(q.competing_expectations))}")
        # G6
        for d in (dreams or []):
            if d.subject:
                path = d.path_or_context
                path_key = "|".join(path) if isinstance(path, list) else str(path)
                current_keys.add(f"dream:{d.dream_category}:{d.subject}:{path_key}")
        # G7
        for inv in (investigations or []):
            if inv.target_id:
                current_keys.add(f"investigation:{inv.target_id}")
        # G8
        for exp in (experiments or []):
            if exp.target_id:
                current_keys.add(f"experiment:{exp.target_id}:{exp.action_type}")

        for prior_c in prior:
            key = self._candidate_key(prior_c)
            if not key:
                continue

            prior_conf = prior_c.get("confidence", prior_c.get("strength", 0))
            prior_gen  = prior_c.get("generation", 1)
            prior_obs  = prior_c.get("evidence", {}).get("observations", 0)

            if key in current_keys:
                strengthened += 1
                self._reinforce_current(
                    key, prior_conf, prior_gen, prior_obs,
                    concepts, phrases, loops, predictions,
                    roles=roles, schemas=schemas,
                )
            else:
                new_conf = prior_conf * 0.8
                if new_conf < self.DEATH_THRESHOLD:
                    pruned += 1
                else:
                    decayed += 1
                    decayed_candidate = dict(prior_c)
                    if "confidence" in decayed_candidate:
                        decayed_candidate["confidence"] = round(new_conf, 4)
                    if "strength" in decayed_candidate:
                        decayed_candidate["strength"] = round(new_conf, 4)
                    decayed_candidate["generation"] = prior_gen + 1
                    evidence = dict(decayed_candidate.get("evidence", {}))
                    evidence["decayed_from"] = round(prior_conf, 4)
                    evidence["decay_cycle"] = True
                    decayed_candidate["evidence"] = evidence
                    self._store_single_candidate(decayed_candidate)

        return strengthened, decayed, pruned

    def _candidate_key(self, c: dict) -> str:
        """Return a stable content-identity key for a candidate, used by natural selection."""
        ctype = c.get("type", "")
        # ---- Layer 1 (G1) ----
        if ctype == "concept_candidate":
            members = c.get("members", [])
            return f"concept:{'|'.join(sorted(members))}" if members else ""
        if ctype == "phrase_candidate":
            members = c.get("members", [])
            return f"phrase:{'|'.join(sorted(members))}" if members else ""
        if ctype == "loop_candidate":
            path = c.get("path", [])
            return f"loop:{'|'.join(path)}" if path else ""
        if ctype == "prediction_candidate":
            return f"prediction:{c.get('source', '')}|{c.get('target', '')}"
        # ---- Layer 2 (G2) ----
        if ctype == "meta_concept":
            anchor = c.get("anchor_tag", "")
            return f"meta_concept:{anchor}" if anchor else ""
        if ctype == "process_candidate":
            cycle = c.get("cycle", [])
            return f"process:{'|'.join(sorted(cycle))}" if cycle else ""
        if ctype == "role_candidate":
            ex = c.get("exemplars", [])
            return f"role:{'|'.join(sorted(ex))}" if ex else ""
        # ---- Layer 3 (G3) ----
        if ctype == "workflow_concept":
            comps = c.get("components", [])
            return f"workflow:{'|'.join(sorted(comps))}" if comps else ""
        if ctype == "schema_candidate":
            s_role = c.get("source_role", "")
            t_role = c.get("target_role", "")
            return f"schema:{s_role}->{t_role}" if (s_role and t_role) else ""
        # ---- Layer 4 (G4) ----
        if ctype == "hypothesis":
            subject = c.get("subject", "")
            expectation = c.get("expectation", "")
            return f"hypothesis:{subject}|{expectation}" if subject else ""
        # ---- Layer 5 (G5) ----
        if ctype == "theory":
            subject = c.get("subject", "")
            hyps = c.get("hypotheses", [])
            return f"theory:{subject}|{'|'.join(sorted(hyps))}" if subject else ""
        if ctype == "question":
            subject = c.get("subject", "")
            exps = c.get("competing_expectations", [])
            return f"question:{subject}|{'|'.join(sorted(exps))}" if subject else ""
        # ---- Layer 6 (G6) ----
        if ctype == "dream":
            cat = c.get("dream_category", "")
            subject = c.get("subject", "")
            path = c.get("path_or_context", [])
            path_key = "|".join(path) if isinstance(path, list) else str(path)
            return f"dream:{cat}:{subject}:{path_key}" if subject else ""
        # ---- Layer 7 (G7) ----
        if ctype == "investigation":
            target_id = c.get("target_id", "")
            return f"investigation:{target_id}" if target_id else ""
        # ---- Layer 8 (G8) ----
        if ctype == "experiment":
            target_id = c.get("target_id", "")
            action = c.get("action_type", "")
            return f"experiment:{target_id}:{action}" if target_id else ""
        return ""

    def _reinforce_current(
        self, key, prior_conf, prior_gen, prior_obs,
        concepts, phrases, loops, predictions,
        roles=None, schemas=None,
    ):
        boost = 0.05
        if key.startswith("concept:"):
            members_key = set(key.split(":", 1)[1].split("|"))
            for c in concepts:
                if set(c.members) == members_key:
                    c.confidence = min(1.0, c.confidence + boost)
                    c.generation = prior_gen + 1
                    c.evidence["prior_confidence"] = round(prior_conf, 4)
                    c.evidence["prior_observations"] = prior_obs
                    c.evidence["strengthened"] = True
                    break

        elif key.startswith("phrase:"):
            members_key = set(key.split(":", 1)[1].split("|"))
            for p in phrases:
                if set(p.members) == members_key:
                    p.confidence = min(1.0, p.confidence + boost)
                    p.generation = prior_gen + 1
                    p.evidence["prior_confidence"] = round(prior_conf, 4)
                    p.evidence["strengthened"] = True
                    break

        elif key.startswith("loop:"):
            path_key = key.split(":", 1)[1].split("|")
            for l in loops:
                if l.path == path_key:
                    l.strength = min(1.0, l.strength + boost)
                    l.generation = prior_gen + 1
                    l.evidence["prior_strength"] = round(prior_conf, 4)
                    l.evidence["strengthened"] = True
                    break

        elif key.startswith("prediction:"):
            parts = key.split(":", 1)[1].split("|")
            if len(parts) == 2:
                src, tgt = parts
                for p in predictions:
                    if p.source == src and p.target == tgt:
                        p.strength = min(1.0, p.strength + boost)
                        p.generation = prior_gen + 1
                        p.evidence["prior_strength"] = round(prior_conf, 4)
                        p.evidence["strengthened"] = True
                        break

        elif key.startswith("role:") and roles:
            ex_key = set(key.split(":", 1)[1].split("|"))
            for r in roles:
                if set(r.exemplars) == ex_key:
                    r.confidence = min(1.0, r.confidence + boost)
                    r.generation = prior_gen + 1
                    r.evidence["prior_confidence"] = round(prior_conf, 4)
                    r.evidence["strengthened"] = True
                    break

        elif key.startswith("schema:") and schemas:
            schema_key = key.split(":", 1)[1]
            for s in schemas:
                if f"{s.source_role}->{s.target_role}" == schema_key:
                    s.confidence = min(1.0, s.confidence + boost)
                    s.generation = prior_gen + 1
                    s.evidence["prior_confidence"] = round(prior_conf, 4)
                    s.evidence["strengthened"] = True
                    break

    # ==================================================================
    # Persistence
    # ==================================================================

    def _store_candidates(self, report: SleepReport):
        self.memory.store(
            json.dumps({"type": "_sleep_meta", "cycle": report.cycle,
                        "ran_at": report.ran_at,
                        "composites_created": report.composites_created}),
            event_type="sleep", source="sleep:meta",
        )
        # Record the cycle number in the authoritative monotonic counter.
        self.memory.record_sleep_cycle(report.cycle, report.ran_at)

        for c in report.concepts:
            self._store_single_candidate(asdict(c))
        for p in report.phrases:
            self._store_single_candidate(asdict(p))
        for l in report.loops:
            self._store_single_candidate(asdict(l))
        for p in report.predictions:
            self._store_single_candidate(asdict(p))
        for a in report.anomalies:
            self._store_single_candidate(asdict(a))
        # Layer 2
        for m in report.meta_concepts:
            self._store_single_candidate(asdict(m))
        for p in report.processes:
            self._store_single_candidate(asdict(p))
        for r in report.roles:
            self._store_single_candidate(asdict(r))
        # Layer 3
        for w in report.workflow_concepts:
            self._store_single_candidate(asdict(w))
        for s in report.schemas:
            self._store_single_candidate(asdict(s))
        # Layer 4
        for h in report.hypotheses:
            self._store_single_candidate(asdict(h))
        # Layer 5
        for t in report.theories:
            self._store_single_candidate(asdict(t))
        for q in report.questions:
            self._store_single_candidate(asdict(q))
        # Layer 6
        for d in report.dreams:
            self._store_single_candidate(asdict(d))
        # Layer 7
        for inv in report.investigations:
            self._store_single_candidate(asdict(inv))
        # Layer 8 (Sleep V6)
        for exp in report.experiments:
            self._store_single_candidate(asdict(exp))

    def _store_single_candidate(self, candidate: dict):
        ctype = candidate.get("type", "unknown")
        self.memory.store(
            json.dumps(candidate),
            event_type="sleep",
            source=f"sleep:{ctype}",
        )
