"""Reject a qualitative score card before it can touch harness state."""

from wwl_phase.result import fail
from wwl_phase.spine import AXES


def validate_scores(scores):
    if scores is None:
        return None
    if not isinstance(scores, dict) or not scores:
        return fail("scores must be a non-empty object with all six axes", True, action="rewrite")
    missing = [axis for axis in AXES if axis not in scores]
    if missing:
        return fail("scores missing {0}".format(", ".join(missing)), True, action="rewrite")
    for axis in AXES:
        value = scores[axis]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return fail("{0} is not a number".format(axis), True, action="rewrite")
        if value < 0 or value > 100:
            return fail("{0} out of range".format(axis), True, action="rewrite")
    return None
