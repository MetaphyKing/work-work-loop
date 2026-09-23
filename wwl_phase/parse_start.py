"""Parse a START card, a bare continue, or a bare stop."""

import re

from wwl_phase.result import fail, ok

_HEADER = re.compile(r"WWL/(\d+\.\d+\.\d+)", re.IGNORECASE)
_TAG = re.compile(r"^\[(IDEA|LOCKS|SPINE|TASK|NEXT)\]\s*(.*)$", re.IGNORECASE)


def parse_prompt(text):
    if not isinstance(text, str) or not text.strip():
        return fail("empty prompt", False, action="stop")

    stripped = text.strip()
    if "\n" not in stripped:
        token = stripped.lower().rstrip(".")
        if token == "continue":
            return ok(action="continue", idea="", locks=[], spine="", version="")
        if token == "stop":
            return ok(action="stop", idea="", locks=[], spine="", version="")

    lines = stripped.splitlines()
    start_at = 0
    version = ""
    for i, line in enumerate(lines):
        match = _HEADER.search(line.strip())
        if match:
            version = match.group(1)
            start_at = i
            break

    fields = {}
    current = None
    for line in lines[start_at:]:
        tag = _TAG.match(line.strip())
        if tag:
            current = tag.group(1).upper()
            fields[current] = tag.group(2).strip()
            continue
        if current == "IDEA" and line.strip() and not line.strip().upper().startswith("WWL/"):
            fields[current] = (fields.get(current, "") + "\n" + line.strip()).strip()

    idea = fields.get("IDEA", "").strip()
    if not idea:
        return fail("START card missing [IDEA]", False, action="stop")

    spine = fields.get("SPINE", "BIBLE").strip().upper() or "BIBLE"
    if spine not in ("BIBLE", "BUILD"):
        return fail("spine must be BIBLE or BUILD, got {0}".format(spine), False, action="stop")

    locks_raw = fields.get("LOCKS", "none").strip()
    if not locks_raw or locks_raw.lower() == "none":
        locks = []
    else:
        locks = [
            part.strip()
            for part in locks_raw.split(",")
            if part.strip() and part.strip().lower() != "none"
        ]

    return ok(
        action="start",
        idea=idea,
        locks=locks,
        spine=spine,
        version=version or "1.1.0",
        task=fields.get("TASK", ""),
        next_line=fields.get("NEXT", ""),
    )
