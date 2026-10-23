"""
organica/branch_streams.py
------------------------------------------------------------------
Branch-structured stimuli, designed to satisfy the campaign gates.

WHY THIS EXISTS
---------------
The V1.5 instrumentation audit measured that the current study stream
cannot exercise the retention policy: the Layer-4 belief pool reaches a
maximum of 8 against a cap of 15, so the cap never binds and "alphabetical"
and "salience" select the same beliefs in every cycle (journal §19).

The gate validation then measured *why* (journal §20): Layer 5 forms
exactly one theory per subject holding two or more competing beliefs, so
the organism is **supply-limited, not selection-limited**. The scarce
resource is not vocabulary -- 42 world tags gave 1 theory and 97 gave 0 --
it is **competing expectations about the same subject**.

So the stimulus has to carry *branch structure*: subjects with more than
one competing successor.

THE MECHANISM, READ FROM THE ENGINE
------------------------------------
This is the part that matters, because the first generator (below) was
designed from intuition and produced an intermittent stimulus. The engine
says:

* **Layer 4** builds a belief for every ordered pair of components of a
  workflow, and for every consecutive pair of a process cycle. A subject
  holds >= 2 beliefs *only* if it appears in a workflow, or in more than
  one process.
* **A workflow** is a *process* whose cycle contains >= 2 meta-concept
  anchors. A process is a reciprocal 2-cycle or a directed 3-cycle.
* **A workflow has at most 3 components**, because processes have at most
  3. A 3-component workflow gives each of its 3 subjects exactly 2
  beliefs. A 2-component workflow gives each subject 1 belief and
  therefore creates *no* competition at all.

So the unit of competing expectation is a **triangle**: three tags with
edges a->b, b->c, c->a. Each triangle contributes 6 distinct
(subject, expectation) pairs and 3 competing subjects.

* **Layer 1** takes the top `MAX_PREDICTIONS` temporal edges by count. If
  the stimulus has more distinct edges than that, the window is a
  tie-break lottery: which triangles survive changes cycle to cycle, so
  processes and workflows appear and disappear, so the belief supply
  oscillates between zero and full. That is exactly what the first
  generator did, and it is why it produced gates that passed only
  intermittently.

THE DESIGN RULE, DERIVED FROM THE MECHANISM
--------------------------------------------
1. Emit each triangle as a repeating 3-event cycle of two-tag events
   ("a b", "b c", "c a"). The 3-event temporal lookback then produces
   every directed pair on the triangle, which is what the process
   builder needs.
2. Share tags between triangles so that several triangles land on the
   same subject. A shared tag becomes a subject with many competing
   expectations, and the *number of distinct subjects* stays below
   `MAX_THEORIES = 8` while the *number of beliefs* grows past
   `MAX_HYPOTHESES = 15`.
3. Keep the total number of distinct temporal edges at or below the
   prediction window, so the window stops being a lottery. Each triangle
   costs 9 edges; triangles that share one tag cost 5 more, triangles
   that share two tags cost 5 more as well.

VOCABULARY
----------
The tags are **neutral pseudo-words**. That is deliberate: the question
this stimulus answers is structural ("can the organism hold enough
competing beliefs for selection to matter?"), and a semantic vocabulary
would confound structure with meaning. A semantic variant is also
provided for comparison.

CAVEAT, STATED PLAINLY
-----------------------
This stimulus is **engineered**. Results on it are evidence that the
architecture *can* support the behaviour, not that it does so
unassisted. The unassisted question is a separate experiment with a
separate instrument.
"""

from __future__ import annotations

#: Neutral pseudo-word subjects. Short, distinct, never stopwords.
NEUTRAL_SUBJECTS = (
    "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf",
)

#: Neutral pseudo-word successors, one private pair per subject by default.
NEUTRAL_SUCCESSORS = (
    "hotel", "india", "juliet", "kilo", "lima", "mike", "november",
)

#: A semantic variant, for comparison against the neutral one. Same
#: structure, meaningful words.
SEMANTIC_SUBJECTS = (
    "developer", "engineer", "reporter", "operator", "auditor", "planner",
)

SEMANTIC_SUCCESSORS = (
    "login", "router", "ticket", "patch", "report", "session", "endpoint",
)

#: Neutral tags for the lattice design. One hub plus eight petals gives
#: enough distinct tags for every lattice design below.
NEUTRAL_HUB = ("alpha",)
NEUTRAL_PETALS = (
    "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india",
)

SEMANTIC_HUB = ("developer",)
SEMANTIC_PETALS = (
    "engineer", "reporter", "operator", "auditor", "planner", "login",
    "router", "ticket",
)


def _scene(subject: str, successors: tuple[str, ...]) -> list[str]:
    """One branch: a subject and its competing successors.

    Each pair is emitted as a duplicated two-tag event, which is what
    makes the pair reciprocal in the temporal graph.
    """
    events: list[str] = []
    for succ in successors:
        events.append(f"{subject} {succ}")
        events.append(f"{subject} {succ}")
    return events


def branch_stream(
    n_subjects: int = 6,
    successors_per_subject: int = 2,
    repeats: int = 6,
    subjects: tuple[str, ...] = NEUTRAL_SUBJECTS,
    successors: tuple[str, ...] = NEUTRAL_SUCCESSORS,
    shared_successors: bool = False,
) -> list[str]:
    """Build a branch-structured stimulus.

    Parameters
    ----------
    n_subjects
        How many branch subjects. The campaign target is 5-7 (see the
        pre-registration): at least 3 for a meaningful theory ecology, and
        below ``MAX_THEORIES = 8`` so the theory layer stays unsaturated.
    successors_per_subject
        How many competing successors each subject has. 2 gives a theory;
        3 gives a question with real entropy.
    repeats
        How many times the whole scene set repeats. Every edge's count
        scales with this, and edges below ``PREDICTION_MIN_COUNT = 5`` are
        invisible, so this is the knob that sets the floor.
    shared_successors
        If True every subject draws from the same successor pool; if False
        (the default) each subject gets its own private successors, which
        keeps the number of *competing* subjects close to
        ``n_subjects`` instead of spreading competition onto the
        successors too.

    .. note::
       This is the **first** generator. It was measured and it produced
       an *intermittent* stimulus -- the belief supply oscillated between
       zero and full because the prediction window could not hold the
       branch structure. It is kept because it is the control that
       ``lattice_stream`` was measured against.
    """
    if not 1 <= n_subjects <= len(subjects):
        raise ValueError("n_subjects out of range")
    if not 1 <= successors_per_subject <= len(successors):
        raise ValueError("successors_per_subject out of range")

    scene_set: list[str] = []
    for i in range(n_subjects):
        subj = subjects[i]
        if shared_successors:
            succs = tuple(successors[(i + k) % len(successors)]
                          for k in range(successors_per_subject))
        else:
            start = (i * successors_per_subject) % len(successors)
            succs = tuple(successors[(start + k) % len(successors)]
                          for k in range(successors_per_subject))
        scene_set += _scene(subj, succs)

    return scene_set * repeats


# ==================================================================
# The lattice design
# ==================================================================

def lattice_stream(
    triangles: list[tuple[str, str, str]],
    block_repeat: int = 4,
    repeats: int = 6,
) -> list[str]:
    """Build a lattice stimulus out of directed triangles.

    Each triangle ``(a, b, c)`` is emitted as the repeating event cycle
    ``"a b"``, ``"b c"``, ``"c a"``. The 3-event temporal lookback turns
    that into every directed pair on the triangle, which is what the
    Layer-2 process builder needs to find a 3-cycle.

    Triangles are concatenated into blocks and the whole block sequence is
    repeated. Triangles that share tags share subjects, so a shared tag
    accumulates competing expectations from several triangles while the
    number of *distinct* subjects stays small.

    Parameters
    ----------
    triangles
        Each entry is a 3-tuple of distinct tags.
    block_repeat
        How many times each triangle's 3-event cycle is repeated inside
        its own block. This sets the edge-count floor: an edge needs
        ``PREDICTION_MIN_COUNT = 5`` observations to exist at all, and the
        block boundary between two triangles leaks a few low-count edges.
    repeats
        How many times the whole triangle sequence repeats.
    """
    if block_repeat < 1:
        raise ValueError("block_repeat must be >= 1")
    if repeats < 1:
        raise ValueError("repeats must be >= 1")

    blocks: list[str] = []
    for tri in triangles:
        if len(set(tri)) != 3:
            raise ValueError(f"a triangle needs 3 distinct tags, got {tri!r}")
        a, b, c = tri
        blocks += [f"{a} {b}", f"{b} {c}", f"{c} {a}"] * block_repeat

    return blocks * repeats


def lattice_designs(
    hub: tuple[str, ...] = NEUTRAL_HUB,
    petals: tuple[str, ...] = NEUTRAL_PETALS,
) -> dict[str, dict]:
    """The lattice designs under test, with their *predicted* structure.

    The predictions here are arithmetic consequences of the mechanism, not
    measurements. The sweep measures them; where the measurement
    disagrees with the prediction, the measurement wins and the prediction
    is corrected in place.

    Each triangle contributes 9 directed edges (every ordered pair on its
    3 tags) and 6 ordered (subject, expectation) pairs. Triangles that
    share one tag share exactly one edge (the shared tag's self-loop).
    """
    x = hub[0]
    p = list(petals)
    designs = {
        # 1 hub, 3 disjoint petals-pairs: 7 subjects, 27 edges, 18 beliefs.
        "L1_hub1_t3_disjoint": {
            "triangles": [(x, p[0], p[1]), (x, p[2], p[3]), (x, p[4], p[5])],
            "predict": {"subjects": 7, "edges": 27, "beliefs": 18},
        },
        # 1 hub, 3 petals-pairs all sharing the second petal: 5 subjects,
        # 19 edges, 14 beliefs.
        "L2_hub1_t3_shared": {
            "triangles": [(x, p[0], p[1]), (x, p[0], p[2]), (x, p[0], p[3])],
            "predict": {"subjects": 5, "edges": 19, "beliefs": 14},
        },
        # 1 hub, 3 triangles, one shared petal: 6 subjects, 24 edges.
        "L3_hub1_t3_mixed": {
            "triangles": [(x, p[0], p[1]), (x, p[2], p[3]), (x, p[0], p[4])],
            "predict": {"subjects": 6, "edges": 24, "beliefs": 16},
        },
        # 2 hubs, 3 petals: 5 subjects, 19 edges.
        "L4_hub2_t3": {
            "triangles": [(x, p[0], p[1]), (x, p[0], p[2]), (x, p[0], p[3])],
            "predict": {"subjects": 5, "edges": 19, "beliefs": 14},
        },
    }
    return designs


def describe(stream: list[str]) -> dict:
    """Summary of a generated stream, for the sweep report."""
    words = set()
    for ev in stream:
        words.update(w for w in ev.split() if len(w) >= 4)
    return {
        "events": len(stream),
        "distinct_tags": len(words),
        "tags": sorted(words),
    }


__all__ = [
    "NEUTRAL_SUBJECTS",
    "NEUTRAL_SUCCESSORS",
    "SEMANTIC_SUBJECTS",
    "SEMANTIC_SUCCESSORS",
    "NEUTRAL_HUB",
    "NEUTRAL_PETALS",
    "SEMANTIC_HUB",
    "SEMANTIC_PETALS",
    "branch_stream",
    "lattice_stream",
    "lattice_designs",
    "describe",
]
