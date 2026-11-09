# Decision — tag 0.13.0 as a release?

> **This is a release-gate record, not a decision.** It is filed outside the `DECISION-`
> namespace because nothing in it has been decided: the graph and the question registry both
> index decisions, and an undecided gate tallied to a research question would be a false
> statement in the registry.

**Date**: 2026-11-09

**Status**: **OPEN — owner decision pending. Nothing in this record has been done**: no tag was
created, no changelog heading was changed, no version was bumped, no artifact was regenerated,
no deposit reference was moved.
**Question**: what must be true before `v0.13.0` can be tagged, and which of those things only the
owner can decide?
**Answer**: the engine side is already ready; the release side is not. Six gates are open, and four
of them are decisions rather than edits.

---

## 1. What is already true

| Fact | Evidence |
|---|---|
| The three declarations agree on **0.13.0** | `organica/__init__.py`, `pyproject.toml:9`, `CITATION.cff:14` |
| The engine pin is 0.13.0, over 14 modules, taken at `6e0ff24` (2026-11-07) | `docs/engine_pin.json`; `engine_pin --check` reports 14 files at 0.13.0 |
| The engine has **not moved** since the pin | 64 commits after `6e0ff24`, **0** of them touching `organica/` |
| A changelog entry exists, so `test_versioning` passes today | `CHANGELOG.md:31` `## [0.13.0] — (unreleased)` |
| No `v0.13.0` tag exists locally or on the remote | `git tag -l`, `git ls-remote --tags origin` |

That is why nothing is broken right now: rule 10 allows an `(unreleased)` version to have no tag.
Tagging changes that permission into an obligation, which is the whole point of the gate.

## 2. What tagging means mechanically

Once the heading stops saying `(unreleased)`, `tests/test_versioning.py::test_a_released_version_is_checkable`
requires the tag to exist, to point at the local `HEAD`, and to match the tip of `origin/master`.
Three consequences follow, and they are easy to get wrong:

- **The tag must be the last act on master.** A commit after the tag makes the version name a
  release that master is not, and the test fails. The next commit after a release must bump the
  version.
- **The tag and master must be pushed together**, and `origin/master` must already be at the
  release commit when the tag lands, because the remote comparison is against the remote master tip.
- **`CITATION.cff` must be redated.** It currently says `date-released: "2026-11-06"`, which is the
  `v0.12.0` cut date, not 0.13.0's.

## 3. The gates — gate 4 repaired, five open

| # | Gate | State today | Who decides |
|---|---|---|---|
| 1 | **`v0.12.0` must be checkable** | **Blocked: the 2026-11-09 push did not land.** `origin` still has only `v0.6.0`–`v0.10.0` + `audit-trace-v1`, and no ref contains `0.12`; a push from this workspace fails authentication (`could not read Username`, exit 128); `clone_check` is **7/8** (`1 failed, 1615 passed, 7 skipped, 13 errors`, `2026-11-09T02:49:24Z`). Evidence and the check that clears it: section 3a | Owner, on a machine with push access; or the deposit decision that makes the tag unnecessary |
| 2 | **The changelog must cover the release range** | `v0.12.0..HEAD` is **123 commits**; the 0.13.0 section has **28** subsections, **all dated 2026-11-07**. The **29 commits from 2026-11-08/09** (test-count recorder, artifact stamping, engine-version audit, Q052/Q053 work, stash inventory, version sweep) are unrepresented | Owner: complete the section, or declare the release's scope to be the 2026-11-07 state |
| 3 | **The deposit reference** | `benchmarks/deposit_bundle.py` pins `SOFTWARE_REF = "v0.12.0"`, described as "the release a reader can cite today". After 0.13.0 that sentence is false unless the deposit moves or states that it deliberately pins 0.12.0 | Owner: move to `v0.13.0` and re-archive, or keep and disclose |
| 4 | **The ablation suite** | **Repaired 2026-11-09.** `NoFalsificationService._natural_selection()` now accepts the engine's full G1-G8 keyword set, and all **eleven** conditions ran at 300 cycles, writing `docs/ablation_study_0.13.0.json` (engine 0.13.0, `6e0ff24d84d3`, `2026-11-09T03:01:52Z`, 266.6 s). The pre-repair crash is preserved in `docs/VERIFICATION-SWEEP-2026-11-09.md` | Owner: whether the 0.13.0 re-run supersedes or is reported beside the pre-0.13.0 artifact |
| 5 | **Stale committed artifacts** | `docs/cold_start.json` and `docs/g5_gap_diagnostic.json` were generated 2026-10-30, before the 2026-11-06 engine changes; re-running moves 22 and 1,132 leaf values respectively, while `cold_start`'s generation outcomes are unchanged | Owner direction recorded in §5: the experiments are **re-run** on 0.13.0 as new runs, and these two artifacts stay as labelled records of the pre-0.13.0 engine — not regenerated to look current |
| 6 | **Documents that will flip at tag time** | `CHANGELOG.md:16` and `docs/ENGINE-CHANGE-AUDIT.md:26` say 0.13.0 is `(unreleased)`; `README.md:475` says "the latest cut version is 0.12.0"; `docs/ZENODO-DEPOSIT.md:105` says v0.9.0 is the latest published release; `docs/FACTS-SHEET.md` A3 and `docs/GATE-BOARD.md` claim a fresh clone passes 8/8 with "17 pytest" while the check reports 7/8 | Agent work, but it must land in the same commit as the tag, or the record contradicts itself |

## 3a. Open blocker — the `v0.12.0` publish attempt did not reach `origin` (2026-11-09)

**State.** The owner reported on 2026-11-09 that `v0.12.0` had been pushed. The canonical remote does
not have it, so gate 1 is not cleared and the fresh-clone check is unchanged.

**The attempt made from this workspace**

```
$ git push origin refs/tags/v0.12.0
fatal: could not read Username for 'https://github.com': terminal prompts disabled
exit 128
```

No credential helper is configured and neither `GITHUB_TOKEN` nor `GH_TOKEN` is set, so a tag push
cannot be made from here at all. The failure is authentication, not a rejected update.

**What `origin` reports** (`https://github.com/nueraresearch/project-organica.git`, read live)

| query | result |
|---|---|
| `git ls-remote --tags origin` | `v0.6.0`, `v0.7.0`, `v0.8.0`, `v0.9.0`, `v0.10.0`, `audit-trace-v1` — no `v0.12.0` |
| `git ls-remote origin` filtered for `0.12` | nothing: no tag, branch or other ref containing `0.12` |
| `git ls-remote --heads origin` | `master` at `1f9f7130e3695c49b73ba46c6fb2ab9a7e94ce06`; `evaluation-pilots-2026-10-23` |

*Master has since moved: section 3c records the new tip. The tag rows above stand as read.*

The tag exists here and is intact: annotated object `df56bc20c38153c1518b5916c931bd04cf99a98e`,
peeled commit `5804e609e5978bb6437da79827f14002b006457a`.

**Consequence, as measured.** `benchmarks/clone_check.py` reports **7/8** at
`2026-11-09T02:49:24Z` (`docs/clone_check.json`), with the `pytest` step failing
`1 failed, 1615 passed, 7 skipped, 13 errors`. The failing step is the deposit's `git archive v0.12.0`,
which is the consequence gate 1 already records, not a new defect.

**Deliberately not done while the check is red.** `docs/FACTS-SHEET.md` A3 and the
`docs/GATE-BOARD.md` row keep the 2026-10-22 numbers (**"17 pytest"**). Their correction is written
only when the artifact reports 8/8, because the edit is guarded on a zero exit; writing it now would
describe a state the repository is not in.

**Two explanations remain, and this record does not choose between them:** the push came from a
checkout whose `origin` is a fork rather than `nueraresearch/project-organica`, or it was rejected or
never ran and its output was not seen. The check that distinguishes them, run in the checkout the push
was made from, is `git remote -v` followed by `git ls-remote --tags origin v0.12.0`, which must print
the tag object and the peeled commit above.

**What clears it.** The tag appears on the canonical remote, `clone_check.py` then returns 8/8, and its
artifact supplies the numbers A3 and the gate board need. Until then gate 1 stays open and gate 3
cannot be settled either, because the reference it names is not checkable. Section 3b records the measured cause of the failed
attempt and the exact commands that publish the tag.

## 3b. Why the push failed, and the exact steps that publish it (2026-11-09, measured here)

**The remote state, read live from this workspace.** `git ls-remote --tags origin` returns
`v0.6.0`, `v0.7.0`, `v0.8.0`, `v0.9.0`, `v0.10.0` and `audit-trace-v1`; nothing matching `0.12`
appears in any ref, and `refs/heads/master` is `1f9f7130e3695c49b73ba46c6fb2ab9a7e94ce06`. The absence is confirmed, not
inferred.

**The tag is intact here and needs no new commit.** `v0.12.0` is an annotated tag, object
`df56bc20c38153c1518b5916c931bd04cf99a98e`, peeling to commit `5804e609e5978bb6437da79827f14002b006457a` (*Cut v0.12.0 and make the deposit descriptions true of it*, tagged 2026-11-06T21:49:42+00:00).
It is already an ancestor of `origin/master`, so the remote's history already contains it. What is missing from the remote is the **tag ref**, not a branch: publishing it
needs no new commit and no branch push.

**Why the earlier attempt failed.** It was authentication, and the cause is now measurable in the
workspace rather than guessed. The remote is HTTPS
(`https://github.com/nueraresearch/project-organica.git`) and the environment holds no credential
material at all: `credential.helper` is unset, and `GITHUB_TOKEN`, `GH_TOKEN`, `GIT_ASKPASS` and
`SSH_AUTH_SOCK` are all unset. Git therefore falls back to prompting for a username, the shell is
non-interactive, and the attempt dies with `could not read Username for 'https://github.com':
terminal prompts disabled` (exit 128). The asymmetry is the whole diagnosis: **read access works
without credentials because the repository is public, write access never does** -- which is why
`ls-remote` could prove the tag was missing while `push` could not put it there. The authenticated
push available to an agent in this workspace is branch-scoped (it sends HEAD to a branch), so it
cannot publish a tag either.

**The exact steps, in a checkout that has push rights.**

1. `git remote -v` -- confirm the push URL is `nueraresearch/project-organica`. A fork's `origin` is
   the one failure mode that looks exactly like this one.
2. `git cat-file -t v0.12.0` -> `tag`, and `git rev-parse v0.12.0^{}` -> `5804e609e5978bb6437da79827f14002b006457a`. If the
   checkout lacks the tag, fetch it first: `git fetch origin tag v0.12.0`.
3. `git push origin refs/tags/v0.12.0` -- one ref, no `--force`, and **no branch push**: master is
   already ahead of the release commit, so the tag is the only missing object.
4. If step 3 prompts for a username, authenticate in that checkout (a personal access token through
   `gh auth login` or a credential helper, or an SSH remote with a loaded key). Never paste the token
   into a file, a command line or this chat.
5. Verify from outside the checkout: `git ls-remote --tags origin v0.12.0` must print **both** the
   tag object `df56bc20c38153c1518b5916c931bd04cf99a98e` and the peeled commit `5804e609e5978bb6437da79827f14002b006457a^{}`. A single line means a
   lightweight tag was created instead, which does not match this record.
6. Verify a stranger can use it: `git clone <remote> /tmp/pc`, then `git -C /tmp/pc checkout v0.12.0`
   and `git -C /tmp/pc log -1 --format=%H` -> `5804e609e5978bb6437da79827f14002b006457a`.
7. Re-run `python benchmarks/clone_check.py` and expect **8/8**. Only then correct the fresh-clone
   numbers in `docs/FACTS-SHEET.md` A3 and `docs/GATE-BOARD.md`, which are deliberately withheld
   while the artifact reports 7/8.
8. Gate 3 (the deposit reference) can then be settled, because the tag it names becomes checkable.

**If the owner has no push access from any checkout.** Create the tag at commit `5804e609e5978bb6437da79827f14002b006457a` through
GitHub's UI or API instead. Prefer recreating the annotated object so the object id stays
`df56bc20c38153c1518b5916c931bd04cf99a98e`; a lightweight tag created in the UI carries no tagger or message and will not
match this record, which must then be disclosed rather than quietly edited.

**Not done here:** no push was attempted from this workspace. It is not authorised, and with the
credential environment measured above it could not have succeeded.

*(Amended 2026-11-09: a **branch** push was made from this workspace through the
branch-scoped authenticated path, and `master` is now at `747d3dd` — section 3c. No **tag**
push was made, and none can be made from here.)*

## 3c. Amendment — 2026-11-09: `master` is published at `747d3dd`

**State.** `refs/heads/master` on the canonical remote moved from `1f9f713` to `747d3dd`
(`747d3dd1083368753970bc41840d33f21cd34db5`). Three commits, all dated 2026-11-09, were pushed from
this workspace through the environment's authenticated, branch-scoped push path — the path §3b
describes, which sends HEAD to a branch and cannot publish a tag. The push reported
`1f9f713..747d3dd  HEAD -> master`; `git ls-remote --heads origin master` returns the new tip, and a
fresh fetch returns the same commit as `FETCH_HEAD` and as local `HEAD`.

| Commit | Subject | Files |
|---|---|---|
| `6ad8735` | Repair the ablation harness and record its 0.13.0 run | ablation harness, artifacts, records |
| `3c9948e` | Bind the changelog figures and the ablation overrides with tests | `tests/test_changelog_figures.py`, `tests/test_ablation_arm_signatures.py`, manual |
| `747d3dd` | Close the Q052 tally and commit the rerun plan's guards | registry, Stage B block, release-gate rename, rerun plan and its tests |

**What this does not change.** Gate 1 is still open. `git ls-remote --tags origin` returns
`v0.6.0`–`v0.10.0` and `audit-trace-v1` and no `v0.12.0`, so the missing ref is still the tag alone;
the tag object `df56bc20c38153c1518b5916c931bd04cf99a98e` and its peeled commit
`5804e609e5978bb6437da79827f14002b006457a` are unchanged. `clone_check` has not been re-run: the
**7/8** in §3a at `2026-11-09T02:49:24Z` is that measurement, and nothing here clears it. Gate 3
stays unsettled for the same reason. No tag was created, no version bumped, no pin changed, no
artifact regenerated and no deposit reference moved; the 0.13.0 heading still says `(unreleased)`.

**Counts that moved, because a branch push moves every count taken from HEAD.** Measured with
`git rev-list --count` here:

| Quantity | At `1f9f713` | At `747d3dd` |
|---|---|---|
| Commits after the pin `6e0ff24` | 64 | **67** |
| Of those touching `organica/` | 0 | **0** |
| Commits after `v0.12.0` | 123 | **126** |

The engine is untouched: `python -m benchmarks.engine_pin --check` reports 14 files at 0.13.0, and
still 0 commits since the pin touch `organica/`. Gate 2's figures are the measurement at `1f9f713`;
the gap it records widens by three, all dated 2026-11-09, so the changelog's 0.13.0 section — which
still ends at 2026-11-07 — is three commits further behind than it was.

**Supersession.** §3a and §3b describe `refs/heads/master` as `1f9f713`; that was true when read and
is superseded **for master only** by this section. Their other observations — the missing tag ref,
the authentication cause, and the branch-scoped push path — stand.

## 4. The order, once the decisions are made

1. Push `v0.12.0` (gate 1), or make the deposit decision that makes it unnecessary (gate 3).
2. Complete the changelog for the release range and set `CITATION.cff`'s `date-released` (gates 2, 6).
3. **Done 2026-11-09:** the ablation harness was repaired (gate 4) and all eleven conditions ran; label the two stale artifacts as pre-0.13.0 records instead of regenerating them (gate 5, §5).
4. Run the guards: full `pytest`, `engine_pin --check`, `engine_stamp --check`, and
   `clone_check` — 8/8 only if gate 1 is cleared.
5. Remove `(unreleased)` from the 0.13.0 heading and record the release date.
6. Confirm `origin/master` is at the release commit, create the annotated tag `v0.13.0` there, and
   push master and the tag.
7. Verify from outside: `git ls-remote --tags origin` peels `v0.13.0` to the same commit as
   `refs/heads/master`, and a fresh clone reports ahead 0 / behind 0.
8. The next commit must bump the version; nothing may follow the tag except a bump.

## 5. Direction recorded with this gate (owner, 2026-11-09)

The purpose of the re-runs is to **reproduce the experiments on the new engine, not to reproduce the
recorded results**. Ideally the new engine does better; that is the reason to run them, not a
criterion applied to them afterwards.

What follows from that:

- **Old artifacts stay old.** `docs/cold_start.json` and `docs/g5_gap_diagnostic.json` (generated
  2026-10-30) record the pre-0.13.0 engine. They are labelled as such, not regenerated to look
  current, and their numbers are not the target of a re-run.
- **New runs are new artifacts.** Each re-run writes its own artifact, engine-stamped, and is
  reported beside the old one rather than over it. The two re-runs already made on 2026-11-09 are in
  `docs/VERIFICATION-SWEEP-2026-11-09.md`: `cold_start`'s generation outcomes were unchanged while
  its counts moved, which is the shape a new-engine re-run is expected to have.
- **A new engine makes a new experiment.** A cell that is to be *judged* — an ablation arm, a
  campaign, a confirmatory block — needs its criteria fixed before it runs. It cannot inherit the old
  verdict, and "better" cannot become the criterion after the fact. Descriptive re-runs (the
  cold-start ladder, the G5 diagnostic) need no criterion; judged ones do.
- **The enabling step was the harness, and it is done.** The mismatch was repaired on 2026-11-09,
  so `ablation_study.py` runs all eleven conditions on 0.13.0 and writes
  `docs/ablation_study_0.13.0.json`. The re-run is reported beside the pre-0.13.0 artifact, not over
  it; gate 4 is cleared, and what remains is the release decision itself.

## 6. What this record deliberately does not do

It does not tag, date, publish, bump, re-pin, regenerate an artifact, or move the deposit. Every
gate above is a decision the owner has reserved, and four of the six need one before any edit is
safe to make.
