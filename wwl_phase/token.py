"""Render the gate line and the TOKENIZED_BNP block. Counts are never estimated."""

import json

from wwl_phase.result import fail, ok
from wwl_phase.spine import of_for


def parse_locks(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(part).strip() for part in value if str(part).strip()]
    text = str(value).strip()
    if text.lower() in ("", "none"):
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [str(part).strip() for part in parsed if str(part).strip()]
    return [
        part.strip()
        for part in text.split(",")
        if part.strip() and part.strip().lower() != "none"
    ]


def normalize_token_count(value):
    if value is None or value == "" or value == "UNKNOWN":
        return "UNKNOWN"
    if isinstance(value, bool):
        return fail("token count must be an integer or UNKNOWN", False, action="stop")
    if isinstance(value, int):
        if value < 0:
            return fail("token count must be an integer or UNKNOWN", False, action="stop")
        return str(value)
    if isinstance(value, float):
        return fail("token count must be an integer or UNKNOWN", False, action="stop")
    if isinstance(value, str):
        text = value.strip()
        if text == "UNKNOWN":
            return "UNKNOWN"
        if text.isdigit():
            return str(int(text))
    return fail("token count must be an integer or UNKNOWN", False, action="stop")


def _locks_text(locks):
    parts = parse_locks(locks)
    return ", ".join(parts) if parts else "none"


def render_token(spine, phase, of, locks, tokens_in, tokens_out, wake=None, proceed=None):
    incoming = normalize_token_count(tokens_in)
    if isinstance(incoming, dict):
        return incoming
    outgoing = normalize_token_count(tokens_out)
    if isinstance(outgoing, dict):
        return outgoing

    spine = (spine or "").upper()
    if spine not in ("BIBLE", "BUILD"):
        return fail("spine must be BIBLE or BUILD", False, action="stop")

    if proceed is None:
        proceed = "Proceed Phase {0}".format(phase)

    lines = [
        "BEGIN_WWL",
        "version=1.1.0",
        "spine={0}".format(spine),
        "phase={0}".format(phase),
        "of={0}".format(of),
        "locks={0}".format(_locks_text(locks)),
        "tokens_in={0}".format(incoming),
        "tokens_out={0}".format(outgoing),
    ]
    if wake is not None and str(wake).strip():
        lines.append("wake={0}".format(str(wake).strip()))
    lines.append("proceed={0}".format(proceed))
    lines.append("END_WWL")
    return ok(action="deliver", text="\n".join(lines), phase=phase)


def close_phase(phase, spine, locks, tokens_in, tokens_out, wake=None):
    try:
        phase = int(phase)
    except (TypeError, ValueError):
        return fail("phase is not an integer", False, action="stop")
    if phase < 1 or phase > 30:
        return fail("phase {0} is outside 1..30".format(phase), False, action="stop")

    gate_line = "Phase {0} of {1}. Prompt continue to proceed to the next phase.".format(
        phase, of_for(phase)
    )
    if phase >= 30:
        rendered = render_token(
            "BUILD", "UNLOAD", 30, locks, tokens_in, tokens_out, wake, proceed="UNLOAD"
        )
        next_phase = "UNLOAD"
        next_spine = "BUILD"
    elif phase == 20:
        rendered = render_token(
            "BUILD", 21, 30, locks, tokens_in, tokens_out, wake, proceed="Proceed Phase 21"
        )
        next_phase = 21
        next_spine = "BUILD"
    else:
        nxt = phase + 1
        rendered = render_token(
            spine,
            nxt,
            of_for(phase),
            locks,
            tokens_in,
            tokens_out,
            wake,
            proceed="Proceed Phase {0}".format(nxt),
        )
        next_phase = nxt
        next_spine = spine

    if not rendered["success"]:
        return rendered
    return ok(
        action="deliver",
        gate_line=gate_line,
        token=rendered["text"],
        next_phase=next_phase,
        next_spine=next_spine,
    )
