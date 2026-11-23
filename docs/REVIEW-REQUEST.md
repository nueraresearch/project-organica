# Independent methods review — request letter

**Status: written, not sent. Five bracketed fields must be filled by the sender before it goes anywhere;
no request has been sent, and no reviewer has been approached.** The h4 text below is the letter as it
should arrive, minus those fields.

## Why this is not a paper submission

The review this project needs happens **before** the experiment, by someone outside it, and asks one
question: should this be run at all. Journal peer review asks whether a finished contribution deserves
publication, arrives after the data exist, and typically takes months. Sending a protocol to a journal to
obtain a pre-experiment verdict would answer a different question, later, from a different direction of
travel. The record of that reasoning is `docs/INDEPENDENT-METHODS-REVIEW.md` §1 and §6.

## The letter

#### Subject: request for a methodological review of an experiment that has not been run

Dear [name],

I am asking you to review an experiment I have not yet run, and I would rather you told me not to run it
than told me it looks promising.

**What the project is.** Project Organica is an independent research codebase that grows cognitive
structures from a raw event stream through repeated sleep and consolidation, rather than loading pretrained
weights. The repository is public: https://github.com/nueraresearch/project-organica. Everything I would
otherwise attach is readable there, at a fixed commit, so you can check any number against the artifact
that owns it rather than against my summary.

**What I am asking for.** Two to four hours, within [three weeks from the date you accept], and a written
assessment against the rubric in `docs/INDEPENDENT-METHODS-REVIEW.md` §5: five questions marked PASS,
CONDITIONAL or DEFECT, each with a pointer to the artifact that supports the judgement, and one overall
outcome — approved, approved with conditions, or rejected. The report form is §7 of the same document and
is deliberately empty.

**What you would receive.** The protocol (`docs/STRUCTURE-BEHAVIOR-DESIGN.md`), a cover sheet with the
prior-evidence summary and the reading order (`docs/REVIEW-PACKAGE.md`), and an artifact list with the
underlying evidence. Nothing is a summary of anything else: where a document restates a result, the
artifact that owns it is in the list. If you are not in this field, or are short of time, `docs/REVIEW-PRIMER.md` gets you the whole thing in five minutes and does not soften the two hard parts.

**What I am not asking for.** Co-authorship, a letter of support, or a verdict on conclusions — there are
none. I am also not asking you to fix the design; a defect you can name is more useful to me than a
repair you perform.

**Two facts I want you to see before forming a view, because they are the inconvenient ones.** First, the
block the design proposes needs **48 worlds per configuration** to resolve the smallest relation it would
call predictive (rank 0.50) at a 0.90 bar, and **that number is a floor, not a target**: measurement error
in the predictor attenuates the observed relation, and at reliability 0.80 the requirement rises to 79
worlds per configuration. The computation is `docs/sign_resolution_structure_behavior.json` and it runs no
engine and spends no seed. Second, the predictor and the outcome are produced by the **same readout**, so a
positive result would be one instrument predicting its own later output; the protocol bounds that
explanation with a size baseline and a permutation control and discloses the limit in §7 rather than
removing it. If either of those makes the experiment not worth running, "rejected" is a useful answer and
I will record it verbatim.

**Eligibility, stated so you can rule yourself out.** The reviewer must not have designed the architecture
or its instruments, must not have selected the historical results that motivate the hypothesis, must have
no stake in a positive result, and is not me. Declaring a conflict does not disqualify you; leaving one
undeclared does.

**Compensation.** [state: no payment is offered / the rate offered]

**What I will record.** Your affiliation and contact, any conflicts you declare, the dates received and
reported, your five item verdicts, the outcome, and what you say you did not review. A rejection is
recorded verbatim and is not edited later, and no seed can be allocated until the report is in the record.

If you would rather decline, that is a useful answer too and needs no explanation.

Yours,

[sender name]
[affiliation and contact]

## Before sending

1. Fill the five bracketed fields: name, deadline, compensation, sender name, affiliation and contact.
2. Replace nothing else. The two numbers in the letter are the ones the artifact computes; if they change,
   the letter is wrong and the artifact is right.
3. Send to one candidate at a time and keep the other names in reserve, so that two reviewers cannot
   compare notes on a design neither has yet assessed.
4. Do not send until `python -m pytest tests/test_review_package.py tests/test_independent_methods_review.py -q`
   passes, because that command is what makes the package's own claims checkable.
5. When a reviewer accepts, record the date in `docs/INDEPENDENT-METHODS-REVIEW.md` §7 immediately. An
   unrecorded acceptance is how a review quietly becomes an opinion.
