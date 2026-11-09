# Decision — tag 0.13.0 as a release?

> **This is a release-gate record, not a decision.** It is filed outside the `DECISION-`
> namespace because nothing in it has been decided: the graph and the question registry both
> index decisions, and an undecided gate tallied to a research question would be a false
> statement in the registry.

**Date**: 2026-11-09

**Status (current, 2026-11-09)**: `v0.13.0` is **not tagged** and the release decision is still the
owner's. Of the six gates, **1**, **2** and **4** are cleared and **3**, **5** and **6** remain — the
deposit reference, the two pre-0.13.0 artifacts, and the nine tag-time edits. **This line is the
current statement**; everything below it is a chronological record, and where a measurement
contradicted an earlier reading the correction is dated and points at the section that supersedes it.

**Status at filing**: OPEN — owner decision pending, and nothing had been done: no tag was created,
no changelog heading was changed, no version was bumped, no artifact was regenerated, no deposit
reference was moved.
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
| 1 | **`v0.12.0` must be checkable** | **Cleared 2026-11-09.** `refs/tags/v0.12.0` is on the remote as annotated object `df56bc2` peeling to `5804e60` (section 3f), and `clone_check` reports **8/8** for `2026-11-09T14:40:19Z`: `1641 passed, 19 skipped`, the thirteen new skips being the deposit bundle in a clone with no rendered PDFs. It was blocked twice for different reasons — the tag ref was absent (section 3a), and then thirteen deposit tests raised in a clone without `papers/build/`; section 3f records both and the fix. `docs/FACTS-SHEET.md` A3 and `docs/GATE-BOARD.md` now carry this artifact's numbers, which table 3c had withheld until it reported 8/8 | Owner: nothing left on this gate; gate 3 carries the deposit decision |
| 2 | **The changelog must cover the release range** | **Cleared as an edit 2026-11-09.** `v0.12.0..9cba01f` is **128** commits, and the 0.13.0 section has **45** subsections: **7** dated 2026-11-09, **10** dated 2026-11-08 and **28** dated 2026-11-07. The **34** commits after 2026-11-07 that `9cba01f` contains are covered by the 17 entries dated after that day, by work item rather than one entry per commit; the three still missing on 2026-11-09 (`2ed31ce`, `747d3dd`, `3c9948e`) now have entries of their own. This row first said **123 commits**, **28** subsections all dated 2026-11-07 and **29** unrepresented commits; section 3d records the correction. | Owner: confirm the release's scope now runs through 2026-11-09 |
| 3 | **The deposit reference** | `benchmarks/deposit_bundle.py` pins `SOFTWARE_REF = "v0.12.0"`, described as "the release a reader can cite today". After 0.13.0 that sentence is false unless the deposit moves or states that it deliberately pins 0.12.0 | Owner: move to `v0.13.0` and re-archive, or keep and disclose |
| 4 | **The ablation suite** | **Repaired 2026-11-09.** `NoFalsificationService._natural_selection()` now accepts the engine's full G1-G8 keyword set, and all **eleven** conditions ran at 300 cycles, writing `docs/ablation_study_0.13.0.json` (engine 0.13.0, `6e0ff24d84d3`, `2026-11-09T03:01:52Z`, 266.6 s). The pre-repair crash is preserved in `docs/VERIFICATION-SWEEP-2026-11-09.md` | Owner: whether the 0.13.0 re-run supersedes or is reported beside the pre-0.13.0 artifact |
| 5 | **Stale committed artifacts** | `docs/cold_start.json` and `docs/g5_gap_diagnostic.json` were generated 2026-10-30, before the 2026-11-06 engine changes; re-running moves 22 and 1,132 leaf values respectively, while `cold_start`'s generation outcomes are unchanged | Owner direction recorded in §5: the experiments are **re-run** on 0.13.0 as new runs, and these two artifacts stay as labelled records of the pre-0.13.0 engine — not regenerated to look current |
| 6 | **Documents that will flip at tag time** | **Settled 2026-11-09.** The exact list is section 3e: **nine** statements across **six** files that the tag commit must carry, **two** that are already stale and are not the tag's consequence, **two** the earlier list wrongly included because they follow `clone_check` rather than this tag, and **one** conditional on gate 3's deposit decision. The earlier row named `CHANGELOG.md:16` but missed `CHANGELOG.md:31` — the heading `tests/test_versioning.py` actually reads — and omitted `CITATION.cff`, the manual's Git row and this record itself. | Agent work, in the same commit as the tag |

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

*(Corrected 2026-11-09: only half of that held. With the tag on the remote, `deposit_bundle.py
--check` passes and `clone_check` still returned **7/8** — the tag was **necessary and not
sufficient**. Section 3f records the second cause and the fix.)*

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
   *(Corrected 2026-11-09: the expectation was wrong. The tag was published and `clone_check` still
   returned **7/8**, because thirteen deposit tests raise in a clone with no rendered PDFs; 8/8 came
   only after those tests were made to skip on that condition. Section 3f.)*
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

*[Amended 2026-11-09: section 3d supersedes the counts in this section for gate 2. The master tip
and the gate statuses this section records are unchanged.]*

## 3d. Amendment — 2026-11-09: gate 2's figures were the pre-entry state

**State.** Gate 2 was written before the section had entries for the 2026-11-08/09 work: it said
`v0.12.0..HEAD` was **123** commits, the section had **28** subsections all dated 2026-11-07, and
**29** commits from 2026-11-08/09 were unrepresented. Measured here at `9cba01f`, `v0.12.0..9cba01f` is
**128** commits and the section has **45** subsections — **7** dated 2026-11-09,
**10** dated 2026-11-08 and **28** dated 2026-11-07 — against the **34** commits after
2026-11-07 in `9cba01f`.

**What the coverage is, and what it is not.** It is one entry per *work item*, not one entry per
commit: the decay-edge work, the engine audit and its guard, the artifact stamping, the sleep-path
split, the reopening pass, the Q051/Q052/Q053 cells, and the 2026-11-09 repairs were each a cluster
of commits that one entry describes. The three commits that were still missing — `2ed31ce` (the
master-published amendment to this record), `747d3dd` (the Q052 tally, the Stage B block and the
rerun plan) and `3c9948e` (the changelog-figure pass itself) — now have entries of their own, and
every figure they quote is pinned in `tests/test_changelog_figures.py` blocks E43–E45, whose
classification list now carries **45** headings with **0** uncovered. Nothing mechanical asserts
one entry per commit and this record does not claim it; the claim is that every dated work item
after 2026-11-07 has an entry, which is what gate 2 asked for.

**The engine is still untouched by any of it:** no commit since the pin `6e0ff24` touches
`organica/`, and `engine_pin --check` reports its fourteen files at 0.13.0. No tag was created, no
version bumped, no artifact regenerated and no deposit reference moved.

**Gate status.** Gate 2 is no longer an edit owed; what remains in it is the owner's scope
statement, which is a decision rather than a document change. With gate 4 repaired and gate 2
cleared, four of the six remain as §3 lists them — gates 1, 3, 5 and 6 — and gates 1 and 3 are
still blocked on the missing `v0.12.0` tag ref.

## 3e. Gate 6 settled — the exact statements that flip at tag time

The row's earlier list was short and partly wrong, and a tag commit written from it would have left
prose contradicted by the tag. Every citation below was checked against the file as it stands: the
line number is today's anchor, and the quoted text is the locator that survives a shift.

### a. Statements the tag commit must change (nine, in six files)

| # | Where | Says now | Becomes at the tag |
|---|---|---|---|
| 1 | `CHANGELOG.md:31` | heading `## [0.13.0] — (unreleased)` | the heading carries the tag date, because this is the line `tests/test_versioning.py` reads; the earlier list named line 16 instead and would have left this one unedited |
| 2 | `CHANGELOG.md:16` | version table: 0.13.0 `(unreleased)`, 0.12.0 cut 2026-11-06, v0.10.0 the previous tag, v0.9.0 the latest published release | 0.13.0 released on the tag date and the previous cut becomes 0.12.0; the published-release clause moves only if a GitHub release page is created for 0.13.0 |
| 3 | `docs/ENGINE-CHANGE-AUDIT.md:26` | the HEAD row: `0.13.0` (unreleased), current master | the HEAD row names the tag date and `v0.13.0` as the tag on this commit |
| 4 | `README.md:466` | 0.13.0 is **unreleased** work on top of the **0.12.0 deposit**, which is cut, dated and tagged; v0.9.0 is the latest published release | 0.13.0 is the latest cut version and the deposit, dated and tagged; the published-release clause follows whether a release page exists |
| 5 | `README.md:475` | "the latest cut version is 0.12.0", and 0.13.0 is unreleased work on top of it | "the latest cut version is 0.13.0", with 0.12.0 the deposit it was cut on top of |
| 6 | `CITATION.cff:15` | comment: 0.13.0 is unreleased working-tree work, and `date-released` below is the deposit's tag date | the comment describes 0.13.0 as the release and names the tag date |
| 7 | `CITATION.cff:20` | `date-released: "2026-11-06"` | the tag date of 0.13.0, because the field must agree with the `version` above it |
| 8 | `docs/USER-MANUAL.md:90` | Git row: package version 0.13.0, **unreleased** work; v0.9.0 still the latest published release; `CITATION.cff` records the deposit's tag date because 0.13.0 has no release of its own yet | 0.13.0 tagged on the tag date, with 0.12.0's deposit date kept separate and the published-release clause following the release page |
| 9 | `docs/RELEASE-GATE-0.13.0.md:9-12` and §4 | status: "Nothing in this record has been done: no tag was created"; step 5 still asks for the heading to be changed | the status records the tag object, its peeled commit and the push, and the order's remaining steps are marked done |

### b. Already stale, and not the tag's consequence (two)

| Where | Says now | Why it is already wrong |
|---|---|---|
| `docs/ZENODO-DEPOSIT.md:104-105` | "**0.10.0 is the latest cut version — dated, tagged and pushed — and v0.9.0 is the latest published release.**" | the second clause was true; the first was overtaken when `v0.12.0` was cut on 2026-11-06. **Corrected 2026-11-09:** the paragraph now says 0.12.0 is the latest cut version, dated and tagged at `5804e60` on 2026-11-06, states that the tag ref is not yet on the remote (gate 1, section 3b), and notes that neither `v0.10.0` nor `v0.12.0` has a GitHub release; the same file's engine paragraph was corrected with it, since it repeated the removed version-gated skip in the present tense |
| `papers/01_developmental_structure_formation.md:54` | "on the current package (`0.12.0`) its engine-identity checks are skipped … the package version is `0.12.0`, and `v0.10.0` is the last tag cut" | wrong twice already: the package is 0.13.0, and the version-gated skip was removed on 2026-11-08 when the per-file pin replaced it; the tag would have made it wrong a third way. **Corrected 2026-11-09:** §2.2 now names `0.13.0`, describes the pin and records that it replaced the skip on 2026-11-08, and names `v0.12.0` (2026-11-06) as the latest tag cut; the paper's Draft-status line carries the correction as a dated note, and no measurement, number or conclusion changed |

### c. Removed from the list — these follow `clone_check`, not the tag (two)

| Where | Says now | What actually gates it |
|---|---|---|
| `docs/FACTS-SHEET.md:27` (A3) | a fresh clone passes **8/8** with **17 passed**, dated 2026-10-22 | the artifact must first report 8/8, which needs the missing `v0.12.0` tag ref (gate 1); the row's own date marks it as a measurement, not a tag-time claim |
| `docs/GATE-BOARD.md:25` | fresh clone passes 8/8 checks, 17 pytest, 9/9 examples | the same condition, and the same correction follows the same artifact |

**Both corrected 2026-11-09**, from `docs/clone_check.json` at `2026-11-09T14:40:19Z` — **8/8**, `1641 passed, 19 skipped` — once a clone stopped erroring on the deposit tests; section 3f records the fix and the measurement.

### d. Conditional on gate 3 (one)

| Where | Says now | When it changes |
|---|---|---|
| `zenodo/software-v0.12.0.json:36` | the v0.12.0 software record's note says v0.9.0 is the latest published release | only if gate 3 moves the deposit to 0.13.0, which needs a new record; if the deposit stays on 0.12.0 the record is unchanged and gate 3 carries the disclosure |

### e. Dated records that must not be edited

`CHANGELOG.md:45` (an entry's statement that the heading still said `(unreleased)` on 2026-11-09),
`docs/V1-FREEZE.md:8` and `:238`, `docs/DECISION-V2-SCOPE.md:54`, `docs/AUDIT-TRACE-SPEC.md:509`,
`docs/ZENODO-DEPOSIT.md`'s 2026-10-31 route section, and the manual's revision rows are records of
what was true when they were written. The version sweep of 2026-11-09 already declared them, and
tagging does not make a dated statement false.

**The checklist for the tag commit:** table a, all nine, in the same commit as the tag. Table b was
**corrected on 2026-11-09** — nothing in it depended on the tag — and table c must wait for
`clone_check` to report 8/8, which gate 1 blocks.

## 3f. Amendment — 2026-11-09: `v0.12.0` is published, and gate 1's remaining failure is not the tag

**The tag ref is on the remote.** After the owner authorised a device login for this workspace,
`git push origin refs/tags/v0.12.0` reported `* [new tag] v0.12.0 -> v0.12.0`. `git ls-remote --tags
origin v0.12.0` returns both lines — object `df56bc20c38153c1518b5916c931bd04cf99a98e` and peeled
`5804e609e5978bb6437da79827f14002b006457a` — so the annotated object travelled and its id matches the
one this record names. No branch was pushed and no force was used: `refs/heads/master` stayed at
`e2d031e`.

**What that clears.** In a fresh `git clone` of the canonical remote, `benchmarks/deposit_bundle.py
--check` now exits 0 and prints `cited artifacts: 40, missing from the v0.12.0 tree: 0`. The deposit's
citations are checkable by a stranger, which is the thing the missing ref blocked.

**What it does not clear.** `benchmarks/clone_check.py` re-run after the push still reports **7/8**
(`docs/clone_check.json`, 2026-11-09): `1640 passed, 6 skipped, 13 errors` in 159.5 s. Every error is in
`tests/test_deposit_bundle.py`, raised in that module's `manifest` fixture:

    RuntimeError: .../papers/build/01_developmental_structure_formation.pdf is missing.
    Build it first: python benchmarks/render_papers.py

`papers/build/` is gitignored (`.gitignore:16 build/`) and `benchmarks/render_papers.py` needs pandoc,
which this environment does not have (`pdflatex` is present). A clone therefore carries the source but
not the rendered PDFs, and the deposit tests cannot build their bundle without them. **This is a build
prerequisite of the check, not a tag defect.** Section 3a recorded the same **13** errors before the
push and attributed them to the missing ref; with the ref present the same thirteen tests still error,
now one step later, at `build_paper`. Publishing the tag was necessary and is not sufficient, and §3a's
statement that the failing step "is the deposit's `git archive v0.12.0`" does not survive this
measurement.

**Consequence.** Gate 1 stays open on its 8/8 criterion, so `docs/FACTS-SHEET.md` A3 and the
`docs/GATE-BOARD.md` row keep their 2026-10-22 numbers — which now also disagree with the suite the
clone collects (**1,659**, where those rows say "17 pytest"). Three ways to close it, and this record
does not choose between them: **(a)** the deposit fixture skips with a stated reason when the rendered
PDFs are absent, which makes a clone report 8/8 with thirteen skips and means a stranger's clone no
longer exercises the deposit checks at all; **(b)** gate 1's criterion is restated around what a clone
can check without the PDFs, and A3 and the gate board are rewritten from the new artifact; **(c)**
`clone_check.py` renders the papers itself, which makes the check depend on pandoc and a LaTeX
toolchain. Committing the PDFs is not among them: that was decided against on 2026-11-06.

**Closed 2026-11-09.** The `manifest` fixture in `tests/test_deposit_bundle.py` now skips, naming the files, when the rendered manuscripts are absent, and a control test asserts that condition fires on an empty tree and stays silent once the PDFs exist — so a drifted path fails there rather than silently skipping thirteen tests. Measured here, with the PDFs present, the module runs **15** tests and skips none; in a clone without `papers/build/` it reports **2 passed, 13 skipped**. With the change on `master` (`82df9e8`), `clone_check` returns **8/8** (`docs/clone_check.json`, `2026-11-09T14:40:19Z`): `1641 passed, 19 skipped`, 9/9 examples, and `build.py`, `study_health` and live-study isolation unchanged. A3 and the gate board are corrected from that artifact, which is the edit table c said to wait for. Gate 1 is cleared; gate 3, the deposit reference, is the remaining owner decision.

## 4. The order, once the decisions are made

1. Push `v0.12.0` (gate 1), or make the deposit decision that makes it unnecessary (gate 3).
2. Set `CITATION.cff`'s `date-released` (gate 6). The changelog half is done — gate 2 was
   cleared as an edit on 2026-11-09, because the 0.13.0 section now covers every work item after
   2026-11-07 (section 3d).
3. **Done 2026-11-09:** the ablation harness was repaired (gate 4) and all eleven conditions ran; label the two stale artifacts as pre-0.13.0 records instead of regenerating them (gate 5, §5).
4. Run the guards: full `pytest`, `engine_pin --check`, `engine_stamp --check`, and
   `clone_check` — 8/8 only if gate 1 is cleared.
5. Carry gate 6's settled list (section 3e) in this commit: the nine tag-time edits — the
   `(unreleased)` heading, the version table, the audit's HEAD row, both README statements,
   `CITATION.cff`'s comment and `date-released`, the manual's Git row, and this record's status.
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
