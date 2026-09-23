"""Admit one phase and make the run directories the harness will not create."""

import json
from pathlib import Path

from wwl_phase.parse_start import parse_prompt
from wwl_phase.phase_guard import phase_allowed
from wwl_phase.result import fail, ok
from wwl_phase.spine import HARNESS_PATH, KERNEL_PATH
from wwl_phase.token import parse_locks

RUN_CARD = "wwl_run.json"


def _read_json(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fail("{0} is not valid JSON".format(path.name), False, action="stop")


def _fresh_state():
    return {
        "version": "1.0.0",
        "active_spine": "BIBLE",
        "current_phase": 0,
        "locks": [],
        "failed_attempts_count": 0,
        "history": [],
    }


def _ensure_dirs(root):
    (root / "drafts").mkdir(parents=True, exist_ok=True)
    (root / "outbox").mkdir(parents=True, exist_ok=True)


def _write_card(path, card):
    path.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")


def bind(root, action=None, prompt=None, idea=None, locks=None, spine=None, skip_reason=None):
    if not root or not str(root).strip():
        return fail("wwl_root is empty", False, action="stop")

    root_path = Path(root).expanduser().resolve()
    chosen = (action or "").strip().lower()
    parsed = None
    if prompt:
        parsed = parse_prompt(prompt)
        if not parsed["success"]:
            return parsed
        if not chosen:
            chosen = parsed["action"]

    if chosen not in ("start", "continue", "stop"):
        return fail("action must be start, continue, or stop", False, action="stop")
    if chosen == "stop":
        return ok(action="stop", wwl_root=str(root_path))

    card_path = root_path / RUN_CARD
    state_path = root_path / "wwl_state.json"
    existing_card = _read_json(card_path) if card_path.exists() else None
    if isinstance(existing_card, dict) and existing_card.get("success") is False:
        return existing_card
    state = _read_json(state_path) if state_path.exists() else None
    if isinstance(state, dict) and state.get("success") is False:
        return state
    if state is None:
        state = _fresh_state()

    if chosen == "continue":
        if not isinstance(existing_card, dict) or not existing_card.get("idea"):
            return fail("continue requires an existing run card", False, action="stop")
        if not state_path.exists():
            return fail("continue requires wwl_state.json", False, action="stop")
        idea = existing_card["idea"]
        locks = existing_card.get("locks") or []
        spine = existing_card.get("spine") or "BIBLE"
        if state.get("current_phase", 0) >= 30 and _phase_done(state, 30):
            return ok(action="unload", wwl_root=str(root_path), idea=idea, locks=locks, spine="BUILD")
        if _phase_done(state, 20) and state.get("current_phase", 0) == 20:
            spine = "BUILD"
    else:
        if parsed and parsed["action"] == "start" and not idea:
            idea = parsed["idea"]
            locks = parsed["locks"]
            spine = parsed["spine"]
        if not isinstance(idea, str) or not idea.strip():
            return fail("START requires an idea", False, action="stop")
        idea = idea.strip()
        locks = parse_locks(locks)
        spine = (spine or "BIBLE").upper()
        if isinstance(existing_card, dict) and existing_card.get("idea"):
            if state_path.exists() and state.get("current_phase", 0) > 0:
                return fail("run already admitted; send continue", False, action="stop")
            idea = existing_card["idea"]
            locks = existing_card.get("locks") or locks
            spine = existing_card.get("spine") or spine

    target = int(state.get("current_phase", 0)) + 1
    if target > 30:
        return ok(action="unload", wwl_root=str(root_path), idea=idea, locks=locks, spine=spine)

    admitted = phase_allowed(state, target, spine, skip_reason=skip_reason)
    if not admitted["success"]:
        return admitted

    _ensure_dirs(root_path)
    card = {
        "version": "1.1.0",
        "idea": idea,
        "locks": locks,
        "spine": admitted["spine"],
        "kernel_path": KERNEL_PATH,
        "harness_path": HARNESS_PATH,
    }
    if not isinstance(existing_card, dict):
        _write_card(card_path, card)
    elif existing_card.get("spine") != admitted["spine"]:
        existing_card["spine"] = admitted["spine"]
        _write_card(card_path, existing_card)
        card = existing_card

    draft = root_path / "drafts" / admitted["artifact"]
    publish = root_path / "outbox" / admitted["artifact"]
    return ok(
        action=chosen,
        wwl_root=str(root_path),
        idea=card["idea"],
        locks=card.get("locks") or [],
        spine=admitted["spine"],
        phase=admitted["phase"],
        phase_name=admitted["phase_name"],
        slug=admitted["slug"],
        job=admitted["job"],
        of=admitted["of"],
        mode=admitted["mode"],
        skip_reason=admitted["skip_reason"],
        artifact=admitted["artifact"],
        draft_path=str(draft),
        publish_path=str(publish),
        kernel_path=KERNEL_PATH,
        harness_path=HARNESS_PATH,
    )


def _phase_done(state, phase):
    for entry in state.get("history") or []:
        if entry.get("phase") == phase and entry.get("status") == "GATED_COMPLETE":
            return True
    return False
