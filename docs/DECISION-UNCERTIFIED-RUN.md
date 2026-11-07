# When the harness will not certify the run: verdict or void?

**Decided 2026-11-07.** Status: adopted and enforced. No engine change, no version move.

## 1. The question

`benchmarks/decay_falsifier.py` runs a harness whose own reference arm must be alive for the
run to be a test of the decay hypothesis. On the pinned engine that arm is dead: the harness
exits non-zero, records why, and refuses to certify the run. The falsifier can still read its
series — theories reach zero and stay there — which is exactly the scientific bucket the run
would report if the harness had passed it.

So two artifacts are available from one run: a refusal by the harness, and a series that says
`REPRODUCES`. Does the falsifier report that verdict, or record the run as void?

## 2. The decision

**Record the run as void, and report no scientific verdict.** The gate precedes every scientific
bucket. The reading the series still supports is kept as an **observation** under a field that is
not the verdict, because it remains a true statement about the series and a fabricated zero
would be worse than either alternative.

A record carries four quantities, and they are never collapsed:

| field | question it answers | on a void run |
| --- | --- | --- |
| `certified` | did the harness stand behind this run? | `false` |
| `verdict` | which scientific bucket does the hypothesis land in? | the void label, e.g. `VOID_REFERENCE_DEAD` |
| `gate` | why was the run refused? | the harness's own recorded problems |
| `observation` | what does the series say? | the bucket the series would have produced |

The order is the rule: the certificate is read first, the verdict is computed only when it holds,
and the observation is a by-product that cannot be promoted later.

## 3. Why not report the verdict

Three failures, and none of them is about wording.

**(a) The gate's question is not the hypothesis's question.** "Did a theory live in every cycle?"
and "could this run test whether a theory lives in every cycle?" are different questions, and a
run can answer the second with *no*. Reporting the first as the verdict answers the scientific
question with the prerequisite's status, which is precisely the defect Q041 was opened to settle:
*can the decay falsifier be validly interpreted when its reference arm is dead?* — **no**, because
there is no subject whose persistence the hypothesis is about.

**(b) A counted verdict enters claims it never earned.** Any aggregate, registry row or sentence
that counts verdicts would count this run's `REPRODUCES` as a reproduction and its `FALSIFIED`
as a genuine falsification. A void run is a test that did not happen; it belongs in neither
bucket, and rule 13(b) already says an unmeasurable quantity is never a zero. Counting a void as
a result is the same error with the sign reversed.

**(c) The artifact must be readable without the console.** If the headline says `REPRODUCES` and
the refusal lives in a tail field, a reader cannot tell from the record alone whether the engine
died or the instrument did. The refusal is the finding here, so it belongs in the field a reader
reads first.

## 4. Why not discard the reading

Because it is true, and because discarding it would make two different situations look identical.
A void run is not an unrun experiment: the events happened, the series was recorded, and the
death of the reference arm is itself the observation the falsifier was built to make. Deleting it
would erase the only evidence that the pinned engine reproduces the historical death, and it would
make "we could not test this" indistinguishable from "nobody looked".

What the observation may not do, by construction:

- it may not close or answer a research question;
- it may not appear in a claim ledger, a results table or a headline as a verdict;
- it may not be counted by any aggregate — `scientific()` in the policy module is the only
  function an aggregate may use, and it returns certified verdicts only;
- it may not be quoted as "the hypothesis reproduced" without the void attached.

## 5. What a void is not

- **Not a null result.** A null is a measured absence; a void is no test.
- **Not evidence for the hypothesis.** The series agreeing with the prediction does not make the
  run certifiable retroactively.
- **Not evidence against it.** A refusal is not a falsification either.
- **Not zero, and not a failure of the hypothesis.** It is a failure of the run's prerequisites,
  and it is named as such.
- **Not an error to be smoothed over.** A refusal with a recorded reason is a measurement of the
  prerequisite, and on this engine it is the measurement.

## 6. Enforcement

The rule is code, not prose: `benchmarks/verdict_policy.py` holds `certificate`, `decide`,
`check` and `scientific`. `benchmarks/decay_falsifier.py` writes its record through `decide`, so
the void cannot be produced by an overwrite after a verdict was already computed, and its
`--check` runs `check` in **both** directions:

- an uncertified run that carries a scientific verdict is rejected;
- a certified run that carries a void label, or a gate failure, is rejected;
- a void with no recorded reason is rejected;
- an observation that repeats the void label, or appears on a certified run, is rejected;
- a record with no certificate at all is rejected, because certification is a positive record.

`tests/test_verdict_policy.py` builds a passing record for each direction and then mutates it to
prove the checker fires — rule 11's control. `tests/test_decay_falsifier.py` additionally requires
the live artifact's `certified` flag to agree with the harness's own reference-arm flag, so a
record cannot be relabelled without the flag moving.

## 7. What this does not settle

**Certification is a claim about the harness, not about the world.** This rule orders the gate
before the verdict; it does not audit the gate. A harness that certifies a run it should have
refused still yields a verdict, and catching that is rule 13(a)'s job (the audit that the
independent variable varied and the denominator existed), not this rule's. The two are separate
checks and neither substitutes for the other.

**A partial certificate would need a third state.** If a falsifier could certify one segment of a
run and not another, the binary certificate would be too coarse. Nothing in the repository does
that today, and the rule is not extended to cover it by imagination.

## 8. Reopen condition

Reopen only if a falsifier's gate can be decided on part of a run while another part is
certifiable, so that a single void discards a segment that was genuinely measured. Then the
certificate becomes scoped to the segment and the record names the boundary. Until then, one run,
one certificate, one verdict — or none.

## 9. Artifacts

- `benchmarks/verdict_policy.py` — the policy, its checker and the countable-verdict filter.
- `benchmarks/decay_falsifier.py` — the first falsifier routed through it.
- `docs/decay_falsifier.json`, `docs/DECAY-FALSIFIER-RESULT.md` — the live record:
  `certified: false`, `verdict: VOID_REFERENCE_DEAD`, `observation: REPRODUCES`.
- `tests/test_verdict_policy.py`, `tests/test_decay_falsifier.py` — the controls, in both directions.
