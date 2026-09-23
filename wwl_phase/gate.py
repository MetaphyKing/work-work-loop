"""Run the existing hybrid gate and return a structured result."""

import json
import subprocess
import sys
from pathlib import Path

from wwl_phase.classify import classify
from wwl_phase.result import fail
from wwl_phase.scores import validate_scores
from wwl_phase.spine import HARNESS_PATH


def path_inside(root, path):
    if not root or not path:
        return False
    base = Path(root).resolve()
    try:
        target = Path(path).resolve()
    except OSError:
        return False
    return target == base or base in target.parents


def _already_gated(root, phase):
    state_path = Path(root) / "wwl_state.json"
    if not state_path.exists():
        return False
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    for entry in state.get("history") or []:
        if entry.get("phase") == phase and entry.get("status") == "GATED_COMPLETE":
            return True
    return False


def run_gate(root, draft, phase, slug, scores, publish=None, dry_run=False, code=None, harness=None):
    if not path_inside(root, draft):
        return fail(
            "Security Violation: draft resolves outside WWL_ROOT",
            False,
            action="stop",
        )
    if publish and not path_inside(root, publish):
        return fail(
            "Security Violation: publish path resolves outside WWL_ROOT",
            False,
            action="stop",
        )
    if code and not path_inside(root, code):
        return fail(
            "Security Violation: code path resolves outside WWL_ROOT",
            False,
            action="stop",
        )
    if _already_gated(root, phase):
        return fail("phase {0} is already GATED_COMPLETE".format(phase), False, action="stop")

    rejected = validate_scores(scores)
    if rejected:
        return rejected

    harness_path = harness or HARNESS_PATH
    if not Path(harness_path).exists():
        return fail("harness not found at {0}".format(harness_path), False, action="stop")

    root_path = Path(root).resolve()
    command = [
        sys.executable,
        str(harness_path),
        "--draft",
        str(draft),
        "--phase",
        str(phase),
        "--slug",
        slug,
        "--scores",
        json.dumps(scores),
        "--state",
        str(root_path / "wwl_state.json"),
        "--config",
        str(root_path / "wwl_config.json"),
    ]
    if code:
        command.extend(["--code", str(code)])
    if publish:
        command.extend(["--publish", str(publish)])
    if dry_run:
        command.append("--dry-run")

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_env(root_path),
        check=False,
    )
    output = (completed.stdout or "") + "\n" + (completed.stderr or "")
    return classify(completed.returncode, output, dry_run=dry_run)


def _env(root_path):
    import os

    env = os.environ.copy()
    env["WWL_ROOT"] = str(root_path)
    return env
