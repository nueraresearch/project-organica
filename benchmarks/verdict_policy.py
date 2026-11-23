"""The verdict hierarchy for a run the harness will not certify.

A falsifier answers a question about the organism only if the run's own
prerequisites held. When the harness refuses to certify the run -- its reference
arm is dead, its control failed, its gate fired -- the falsifier records the run
as **void** and reports no scientific verdict. The gate precedes every scientific
bucket, and the reading the run can still produce is kept as an *observation*
under a field that is not the verdict, because a true statement about a series is
not a verdict about the hypothesis.

The rule and its rejected alternatives are recorded in
``docs/DECISION-UNCERTIFIED-RUN.md``. This module is where the rule is enforced:
``decide`` writes the record and ``check`` rejects a contradiction in either
direction, so an artifact that reports a verdict on an uncertified run fails the
falsifier's own ``--check`` instead of travelling.

Three quantities are deliberately kept apart:

* the **certificate** -- did the harness stand behind this run at all?
* the **verdict** -- the scientific bucket, present only on a certified run;
* the **observation** -- what the series says, kept beside a void and never
  counted as a verdict (``scientific`` is the only function an aggregate may use).
"""

from __future__ import annotations

SCIENTIFIC_VERDICTS = ("FALSIFIED", "REPRODUCES", "INTERMITTENT", "INCONCLUSIVE")


def certificate(failed: bool, problems) -> dict:
    """The harness's certificate: did the run's own prerequisites hold?

    A refusal is a recorded reason, not a missing field. ``failed`` is the
    harness's own flag; ``problems`` is the attribution it wrote next to it.
    """
    problems = [str(p) for p in (problems or [])]
    return {"certified": not failed and not problems, "problems": problems}


def is_void(verdict) -> bool:
    """A void label says the run could not test the hypothesis; it is not a bucket."""
    return isinstance(verdict, str) and verdict.startswith("VOID")


def decide(scientific: str, cert: dict, void_label: str) -> dict:
    """Return the recorded verdict fields, with the gate evaluated first.

    ``scientific`` is the bucket the series would produce if the run were
    certifiable. It is the verdict only when the certificate holds; otherwise it
    is returned as the observation and the verdict is the void label.
    """
    if cert["certified"]:
        return {"certified": True, "verdict": scientific, "observation": None, "gate": None}
    return {
        "certified": False,
        "verdict": void_label,
        "observation": scientific,
        "gate": {
            "certified": False,
            "problems": list(cert["problems"]),
            "reason": "the harness refused to certify the run, so no scientific verdict "
                      "is reported",
        },
    }


def check(record: dict, void_label: str = "VOID_UNCERTIFIED") -> list[str]:
    """Contradictions between the certificate, the verdict and the observation.

    Both directions are checked: an uncertified run may not carry a scientific
    verdict, and a certified run may not carry a void label or a gate failure.
    """
    found: list[str] = []
    verdict = record.get("verdict")
    certified = record.get("certified")
    gate = record.get("gate")

    if certified is None:
        found.append("the run records no certificate, so its verdict cannot be read")
    if certified is False and not is_void(verdict):
        found.append("the harness refused to certify the run but the verdict is %r, not %s"
                     % (verdict, void_label))
    if certified is True and is_void(verdict):
        found.append("the run is certified but the verdict is void")
    if is_void(verdict) and not (gate and (gate.get("problems") or gate.get("reason"))):
        found.append("the verdict is void but no reason is recorded beside it")
    if certified is True and gate:
        found.append("the run is certified but carries a gate failure")
    if not is_void(verdict) and verdict not in SCIENTIFIC_VERDICTS:
        found.append("unknown scientific verdict %r" % (verdict,))

    observation = record.get("observation")
    if observation is not None:
        if not is_void(verdict):
            found.append("an observation is kept on a certified run; it would read as a verdict")
        elif observation == verdict:
            found.append("the kept observation repeats the void label instead of the reading")
        elif observation not in SCIENTIFIC_VERDICTS:
            found.append("the kept observation %r is not a scientific reading" % (observation,))
    return found


def scientific(records) -> list[str]:
    """The verdicts an aggregate may count.

    A void run is **excluded**, not counted as a failure and not counted as a
    null result: it was not a test of the hypothesis, so putting it in either
    bucket would be a fabrication.
    """
    return [r["verdict"] for r in records if r.get("certified") is True]
