# Superseded stashes — inventory and disposal, 2026-11-09

This note records what two stashes on the working branch held before they were dropped, so
that the disposal is an accounted-for act rather than a silent one. It adds no evidence and
changes nothing about any result; it is a record of repository housekeeping.

## What was there

Both stashes were created on 2026-11-01, on the same branch, by the pre-merge work that
repaired the release-version check and corrected the documents that described 0.10.0 as
untagged. Both were already labelled as superseded by whoever created them — the messages
say `pre-merge: version-guard fix + release-state corrections (kept for reference)` and
`superseded corrections`.

| stash | stash commit | created (UTC) | base commit (base date) | tracked files changed |
|---|---|---|---|---|
| `stash@{1}` | `99ef5b56af588a325825dabedfbc5a114d7333ab` | 2026-11-01 01:32:36 +0000 | `f3a42a7` (2026-10-31 16:33 −0600) | `AGENTS.md` +1/−1, `CHANGELOG.md` +37/−2, `CITATION.cff` +5/−5, `README.md` +7/−5, `docs/USER-MANUAL.md` +8/−5, `tests/test_versioning.py` +100/−9 |
| `stash@{0}` | `8cdf2b972df8052b2e4fa06a1246b95fef70d86c` | 2026-11-01 03:39:51 +0000 | `7076101` (2026-10-31 19:28 −0600) | `AGENTS.md` +1/−1, `CHANGELOG.md` +28/−2, `CITATION.cff` +5/−5, `README.md` +2/−2, `docs/USER-MANUAL.md` +5/−3, `tests/test_versioning.py` +100/−9 |

Both bases are ancestors of the commit this note is written on. Neither stash had an index
parent carrying untracked files (no `^3` commit), and **neither stash changed any file under
`organica/`** — the count of engine files in each stash is zero. Both trees were purely a
test change plus documentation prose.

## Why they were superseded, and how that was established

The code half landed verbatim. Comparing the two stashes' `tests/test_versioning.py` to the
committed file block by block — parsing both with `ast` and comparing the source segment of
each top-level definition — every added definition is byte-identical to the committed one:
the helpers `_parse_tag_refs` and `_remote_ref`, and the five tests
`test_the_tag_parser_prefers_the_peeled_commit`,
`test_the_tag_parser_accepts_a_lightweight_tag`,
`test_the_tag_parser_returns_none_when_the_tag_is_absent`,
`test_the_bare_query_really_did_return_the_wrong_object`, and
`test_the_release_check_fires_when_the_tag_is_behind_master`. All seven are `SAME`.
So the repair the stashes existed to carry is in the record, and the check that enforces it
still runs.

The prose half was overtaken by later corrections. The hunks describe the 0.10.0 release-state
correction; the changelog and the manual have since moved past them (0.12.0 released, 0.13.0
unreleased), so the stashed wording is an earlier draft of a paragraph that has been rewritten
two or three times since — nothing in it is unpublished text a reader has lost.

The reverse-apply check is worth recording as a negative result: `git apply --check -R` of
either stash patch **fails** on the current tree (`docs/USER-MANUAL.md:87`, `README.md:21`,
`CITATION.cff:12`, `CHANGELOG.md:13`, `AGENTS.md:72`). That does not mean the stash holds
unlanded work; it means the surrounding prose has changed enough that the patch context no
longer matches. The comparison that settles the question is the code-block one above, not the
patch applicability.

## Disposal

Dropped with `git stash drop` on 2026-11-09, older stash first. The working tree was clean
before the drops and clean after them. Nothing was applied, merged, committed from a stash, or
read into the tree at any point.

Dropping a stash removes only the reference. The commits above remain in the object database
as unreachable objects until the repository is pruned (Git's default expiry is 90 days), so
while they are still there they can be inspected or recovered by SHA — `git stash apply
99ef5b56` or `git show 8cdf2b97` — which is why the hashes are written down here rather than
only in a shell history.

## Correction — which artifact carries the older engine file

An earlier pass of this audit, on the same day, said the stashes carried an older
`organica/sleep_selection.py`, before the carried-forward fix. **That attribution was wrong.**
Neither of the two stashes dropped here contains any engine file; they are documentation and
test changes only, as the file counts above show.

The engine snapshot that prompted the warning belongs to a **previously dropped** stash, whose
WIP commit is dangling — `08f3cb1`, dated 2026-11-06 00:37, created on `e6d1bcc`, changing
`organica/sleep_selection.py` among five files. That snapshot contains **no** occurrence of
`carried_forward`, against **11** in the committed file, and the same file's work landed later
in `6c87f63`. So the warning stands — do not apply `08f3cb1` — but it was attached to the wrong
object. It is recorded here because a superseded-artifact warning that names the wrong artifact
is worse than no warning: it sends a future reader to inspect the harmless one.

No engine file, result artifact, protocol or record was changed by this housekeeping.
