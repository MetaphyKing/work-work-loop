"""Admit exactly one next phase. Sequence and L9 are enforced here."""

from wwl_phase.result import fail, ok
from wwl_phase.spine import PHASES, artifact_name, of_for, spine_for


def _gated(history, phase):
    for entry in history or []:
        if entry.get("phase") == phase and entry.get("status") == "GATED_COMPLETE":
            return True
    return False


def phase_allowed(state, target_phase, spine, skip_reason=None):
    state = state or {}
    history = state.get("history") or []
    try:
        current = int(state.get("current_phase", 0))
        target = int(target_phase)
    except (TypeError, ValueError):
        return fail("phase is not an integer", False, action="stop")

    spine = (spine or state.get("active_spine") or "BIBLE").upper()
    if spine not in ("BIBLE", "BUILD"):
        return fail("spine must be BIBLE or BUILD", False, action="stop")

    if skip_reason is not None and not str(skip_reason).strip():
        return fail("trim requires SKIP_REASON", False, action="stop")

    if _gated(history, target):
        return fail(
            "phase {0} is already GATED_COMPLETE".format(target),
            False,
            action="stop",
        )

    if _gated(history, 20) and spine == "BIBLE" and target <= 20:
        return fail(
            "L9: BIBLE production v1 is locked. Start BUILD or UNLOAD.",
            False,
            action="stop",
        )

    if target >= 21 and not _gated(history, 20):
        return fail("BUILD requires phase 20 GATED_COMPLETE", False, action="stop")

    if target >= 21 and spine != "BUILD":
        return fail("phase 21+ requires spine BUILD", False, action="stop")

    if target > 30 or target < 1:
        return fail("phase {0} is outside 1..30".format(target), False, action="stop")

    expected = current + 1
    if target != expected:
        return fail(
            "Phase sequence jump detected. Active state current phase is {0}. "
            "Target Phase must be {1}, got {2}.".format(current, expected, target),
            False,
            action="stop",
        )

    legal_spine = spine_for(target)
    if spine != legal_spine:
        return fail(
            "phase {0} belongs to spine {1}".format(target, legal_spine),
            False,
            action="stop",
        )

    name, slug, job = PHASES[target]
    mode = "skip" if skip_reason is not None else "work"
    return ok(
        action="admit",
        phase=target,
        phase_name=name,
        slug=slug,
        job=job,
        spine=spine,
        of=of_for(target),
        mode=mode,
        artifact=artifact_name(spine, target, slug),
        skip_reason=str(skip_reason).strip() if skip_reason is not None else "",
    )
