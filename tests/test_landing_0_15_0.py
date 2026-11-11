"""The landing record must quote both builds and must not survive a further move."""
LAYER = "static"

import copy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from benchmarks import landing_0_15_0 as landing  # noqa: E402


def test_the_record_matches_the_landed_state():
    assert landing.problems() == []


def test_a_record_missing_a_step_is_rejected():
    text = landing.DOC.read_text(encoding="utf-8").replace("## 3. Re-pin the engine", "")

    assert landing.problems(text), "a record without the re-pin step must fail"


def test_a_pre_landing_build_is_rejected():
    live = copy.deepcopy(landing.state())
    live["version"] = "0.14.0"
    live["cap"] = 40

    assert landing.problems(live=live), "this record describes 0.15.0 and must fail on 0.14.0"


def test_a_record_that_drops_a_pre_landing_digest_is_rejected():
    text = landing.DOC.read_text(encoding="utf-8").replace(
        landing.PRE_LANDING["PRESENCE-CONSTRUCT-1"], "0" * 64)

    assert landing.problems(text), "the 0.14.0 digests are the departure record and must stay"
