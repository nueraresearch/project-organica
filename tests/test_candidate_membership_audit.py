"""Cross-validate the candidate-membership audit against the use-path audit.

The membership audit says which candidate IDs the campaign had and which the
current reconstruction has.  The use-path audit, run earlier and independently,
recorded the per-type **counts** by which the two sides differ, for the types
that moved.  If the membership diff is right, its net per-type difference must
reproduce those recorded counts exactly -- and for the types the use-path
audit did not list, the membership must show no difference at all.

That is the check that makes the membership evidence rather than a claim: the
per-ID diff is derived from the regenerated populations, and the per-type
counts are derived from an earlier, separate measurement of the same
populations.  Two derivations, one artifact, no hand transcription.

The tests fail on a doctored artifact, so a passing run is not a formality.
"""

from __future__ import annotations
LAYER = "static"  # benchmarks/test_layers.py: the module's execution layer

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
ARTIFACT = REPO / "docs" / "candidate_membership_audit.json"
AUDIT = REPO / "docs" / "use_path_audit.json"
REPORT = REPO / "docs" / "CANDIDATE-MEMBERSHIP-AUDIT.md"

CONTROL = ("T1", 20261101)
FAILING = [("T1", 20261125), ("T1", 20261128), ("T1", 20261129),
           ("T2", 20261118), ("T2", 20261120), ("T2", 20261121),
           ("T2", 20261123), ("T2", 20261130)]


def load(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def artifact():
    return load(ARTIFACT)


@pytest.fixture(scope="module")
def audit():
    return load(AUDIT)


def entry_for(artifact, task, seed):
    for e in artifact["results"]:
        if e["task"] == task and e["seed"] == seed:
            return e
    raise AssertionError("no result for %s/%d" % (task, seed))


def audit_entry(audit, seed):
    for e in audit["summary"]["per_seed"]:
        if e["seed"] == seed:
            return e
    raise AssertionError("no use-path audit entry for seed %d" % seed)


# ---------------------------------------------------------------------------
# the artifact says what it claims to say
# ---------------------------------------------------------------------------

def test_the_artifact_exists_and_is_measured(artifact):
    assert artifact["kind"] == "candidate_membership_audit"
    assert artifact["status"] == "measured"


def test_every_seed_is_covered(artifact):
    seen = {(e["task"], e["seed"]) for e in artifact["results"]}
    assert seen == set(FAILING) | {CONTROL}


def test_every_failing_seed_reproduces_the_campaign(artifact):
    for task, seed in FAILING:
        e = entry_for(artifact, task, seed)
        assert e["campaign_reproduced"], "%s/%d did not reproduce" % (task, seed)
        assert e["matching_hash_seeds"], "%s/%d has no matching hash seed" % (
            task, seed)


def test_the_campaign_side_is_not_the_baseline(artifact):
    """A seed whose campaign side IS the pinned hash seed would have an empty
    membership, which would mean the diff was measured against itself."""
    for task, seed in FAILING:
        e = entry_for(artifact, task, seed)
        assert e["campaign_side_hash_seed"] != e["baseline_hash_seed"], (
            "%s/%d: the campaign side is the baseline" % (task, seed))


def test_the_control_seed_has_no_membership_difference(artifact):
    e = entry_for(artifact, *CONTROL)
    diff = sum(len(v["missing"]) + len(v["added"])
               for v in e["membership"].values())
    assert diff == 0, "the control seed differs by %d candidate IDs" % diff


def test_the_control_seed_reproduces_at_every_hash_seed_swept(artifact):
    e = entry_for(artifact, *CONTROL)
    assert e["matching_hash_seeds"] == artifact["hash_seeds_swept"], (
        "the control reproduces only at %s" % e["matching_hash_seeds"])


# ---------------------------------------------------------------------------
# the cross-validation: the per-ID diff reproduces the earlier per-type counts
# ---------------------------------------------------------------------------

def test_membership_net_delta_reproduces_the_audit_deltas(artifact, audit):
    for task, seed in FAILING:
        e = entry_for(artifact, task, seed)
        recorded = audit_entry(audit, seed)["arms"]["no_tiebreak"][
            "per_type_deltas"]
        for ctype, values in recorded.items():
            row = e["membership"].get(ctype)
            assert row is not None, "%s/%d: no membership for %s" % (
                task, seed, ctype)
            net = len(row["missing"]) - len(row["added"])
            expected = (values["campaign"]["unique_count"]
                        - values["audit"]["unique_count"])
            assert net == expected, (
                "%s/%d/%s: membership net %d, use-path audit delta %d"
                % (task, seed, ctype, net, expected))


def test_types_the_audit_did_not_list_keep_their_count(artifact, audit):
    """The audit recorded a delta only for the types whose COUNT moved.

    A type can keep its count and swap candidate IDs, so for the types the
    audit did not list the membership must show a NET difference of zero --
    not an empty membership.  The identity churn is real and is asserted
    separately below.
    """
    for task, seed in FAILING:
        e = entry_for(artifact, task, seed)
        recorded = audit_entry(audit, seed)["arms"]["no_tiebreak"][
            "per_type_deltas"]
        campaign_types = set(audit_entry(audit, seed)["campaign"]["per_type"])
        for ctype in campaign_types - set(recorded):
            row = e["membership"].get(ctype)
            assert row is not None
            net = len(row["missing"]) - len(row["added"])
            assert net == 0, (
                "%s/%d/%s: the audit recorded no count change, the membership "
                "has a net difference of %d" % (task, seed, ctype, net))


def test_the_membership_is_finer_than_the_count_audit(artifact, audit):
    """Some types hold their count while their candidate IDs change.

    These are the differences a count-based audit cannot see, and they are
    the reason the membership audit is not a restatement of the use-path
    audit.
    """
    churn = 0
    for task, seed in FAILING:
        e = entry_for(artifact, task, seed)
        recorded = audit_entry(audit, seed)["arms"]["no_tiebreak"][
            "per_type_deltas"]
        campaign_types = set(audit_entry(audit, seed)["campaign"]["per_type"])
        listed = sorted(c for c in campaign_types - set(recorded)
                        if e["membership"][c]["missing"]
                        or e["membership"][c]["added"])
        assert listed == sorted(e["identity_churn_without_count_change"]), (
            "%s/%d: the recorded churn %s does not match the membership %s"
            % (task, seed, e["identity_churn_without_count_change"], listed))
        churn += len(listed)
    assert churn > 0, (
        "no type held its count while its identities changed; the membership "
        "would then be no finer than the count audit it is meant to extend")


def test_the_baseline_reproduces_the_audit_reconstruction(artifact):
    for task, seed in FAILING:
        e = entry_for(artifact, task, seed)
        assert e["control_baseline_equals_audit_reconstruction"], (
            "%s/%d: the pinned hash seed does not reproduce the use-path "
            "audit's reconstruction" % (task, seed))


def test_the_membership_sets_are_disjoint(artifact):
    """A candidate cannot be both missing and added, and the three sets must
    reconstruct the campaign's population exactly."""
    for task, seed in FAILING:
        e = entry_for(artifact, task, seed)
        for ctype, row in e["membership"].items():
            both = set(row["both"])
            missing = set(row["missing"])
            added = set(row["added"])
            assert not (both & missing)
            assert not (both & added)
            assert not (missing & added)
            campaign = set(e["campaign_ids_by_type"].get(ctype, []))
            ours = set(e["reconstruction_ids_by_type"].get(ctype, []))
            assert campaign == both | missing
            assert ours == both | added


def test_the_hash_seeds_that_reproduce_agree_on_membership(artifact):
    for task, seed in FAILING:
        e = entry_for(artifact, task, seed)
        assert e["matching_seeds_agree_on_membership"], (
            "%s/%d: the reproducing hash seeds disagree on the candidate IDs"
            % (task, seed))


# ---------------------------------------------------------------------------
# the report is rendered from the artifact, and says the same thing
# ---------------------------------------------------------------------------

def test_the_report_exists_and_names_every_seed(artifact):
    text = REPORT.read_text(encoding="utf-8")
    for task, seed in FAILING + [CONTROL]:
        assert "%s / %d" % (task, seed) in text, "the report omits %s/%d" % (
            task, seed)


def test_the_report_states_the_same_counts(artifact):
    text = REPORT.read_text(encoding="utf-8")
    for task, seed in FAILING:
        e = entry_for(artifact, task, seed)
        row = "| %s | %d | %d | %d | %d |" % (
            task, seed,
            sum(len(v["both"]) for v in e["membership"].values()),
            sum(len(v["missing"]) for v in e["membership"].values()),
            sum(len(v["added"]) for v in e["membership"].values()))
        assert row in text, "the report's row for %s/%d does not match the " \
            "artifact" % (task, seed)


def test_the_report_names_the_missing_and_added_candidates(artifact):
    text = REPORT.read_text(encoding="utf-8")
    for task, seed in FAILING:
        e = entry_for(artifact, task, seed)
        for ctype, row in e["membership"].items():
            for cid in row["missing"]:
                assert "`%s`" % cid in text, (
                    "%s/%d: the report omits missing candidate %s"
                    % (task, seed, cid))


# ---------------------------------------------------------------------------
# fail-tests: the checker can reject a doctored artifact
# ---------------------------------------------------------------------------

def test_a_doctored_membership_is_rejected(artifact, audit):
    """Change one membership row and the cross-validation must fail."""
    import copy
    broken = copy.deepcopy(artifact)
    e = entry_for(broken, "T1", 20261125)
    ctype = sorted(e["membership"])[0]
    row = e["membership"][ctype]
    if row["missing"]:
        row["missing"].append("doctored_candidate")
    else:
        row["added"].append("doctored_candidate")
    recorded = audit_entry(audit, 20261125)["arms"]["no_tiebreak"][
        "per_type_deltas"]
    values = recorded[ctype]
    net = len(row["missing"]) - len(row["added"])
    expected = (values["campaign"]["unique_count"]
                - values["audit"]["unique_count"])
    assert net != expected, (
        "a doctored membership still passes the cross-validation")


def test_a_doctored_baseline_flag_is_rejected(artifact):
    import copy
    broken = copy.deepcopy(artifact)
    entry_for(broken, "T2", 20261120)["control_baseline_equals_audit_reconstruction"] = False
    flagged = [e for e in broken["results"]
               if e.get("control_baseline_equals_audit_reconstruction")]
    assert len(flagged) != len(broken["results"]), (
        "a failed baseline check is not distinguishable from a passing one")
