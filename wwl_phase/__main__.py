"""CLI: one JSON object on stdout, exit 0 only when success is true."""

import argparse
import json
import sys
from pathlib import Path

from wwl_phase.bind import bind
from wwl_phase.gate import run_gate
from wwl_phase.parse_start import parse_prompt
from wwl_phase.result import fail
from wwl_phase.token import close_phase, parse_locks


def _load_scores(raw, path):
    if not raw and not path:
        return None
    if path:
        try:
            raw = Path(path).read_text(encoding="utf-8")
        except OSError as exc:
            return fail("scores file unreadable: {0}".format(exc), True, action="rewrite")
    if raw is None or not str(raw).strip():
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        return fail("malformed scores JSON: {0}".format(exc), True, action="rewrite")


def _locks(text):
    if text is None:
        return None
    return parse_locks(text)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="wwl_phase")
    sub = parser.add_subparsers(dest="command", required=True)

    parse_cmd = sub.add_parser("parse")
    parse_cmd.add_argument("--prompt-file")
    parse_cmd.add_argument("--prompt")

    bind_cmd = sub.add_parser("bind")
    bind_cmd.add_argument("--root", required=True)
    bind_cmd.add_argument("--action", default="")
    bind_cmd.add_argument("--prompt-file")
    bind_cmd.add_argument("--prompt")
    bind_cmd.add_argument("--idea")
    bind_cmd.add_argument("--locks")
    bind_cmd.add_argument("--spine")
    bind_cmd.add_argument("--skip-reason")

    gate_cmd = sub.add_parser("gate")
    gate_cmd.add_argument("--root", required=True)
    gate_cmd.add_argument("--draft", required=True)
    gate_cmd.add_argument("--phase", required=True, type=int)
    gate_cmd.add_argument("--slug", required=True)
    gate_cmd.add_argument("--scores")
    gate_cmd.add_argument("--scores-file")
    gate_cmd.add_argument("--publish")
    gate_cmd.add_argument("--dry-run", action="store_true")
    gate_cmd.add_argument("--code")

    close_cmd = sub.add_parser("close")
    close_cmd.add_argument("--phase", required=True, type=int)
    close_cmd.add_argument("--spine", required=True)
    close_cmd.add_argument("--locks", default="none")
    close_cmd.add_argument("--tokens-in", default="UNKNOWN")
    close_cmd.add_argument("--tokens-out", default="UNKNOWN")
    close_cmd.add_argument("--wake", default="")

    args = parser.parse_args(argv)
    if args.command == "parse":
        result = _prompt_result(args.prompt, args.prompt_file)
    elif args.command == "bind":
        prompt = _prompt_text(args.prompt, args.prompt_file)
        if isinstance(prompt, dict):
            result = prompt
        else:
            skip = args.skip_reason if args.skip_reason is not None else None
            result = bind(
                args.root,
                action=args.action,
                prompt=prompt,
                idea=args.idea,
                locks=_locks(args.locks) if args.locks is not None else None,
                spine=args.spine,
                skip_reason=skip,
            )
    elif args.command == "gate":
        scores = _load_scores(args.scores, args.scores_file)
        if isinstance(scores, dict) and scores.get("success") is False:
            result = scores
        else:
            result = run_gate(
                args.root,
                args.draft,
                args.phase,
                args.slug,
                scores,
                publish=args.publish,
                dry_run=args.dry_run,
                code=args.code,
            )
    else:
        result = close_phase(
            args.phase,
            args.spine,
            _locks(args.locks),
            args.tokens_in,
            args.tokens_out,
            wake=args.wake or None,
        )

    sys.stdout.write(json.dumps(result))
    sys.stdout.write("\n")
    return 0 if result.get("success") else 1


def _prompt_text(prompt, prompt_file):
    if prompt_file:
        try:
            return Path(prompt_file).read_text(encoding="utf-8")
        except OSError as exc:
            return fail("prompt file unreadable: {0}".format(exc), False, action="stop")
    return prompt


def _prompt_result(prompt, prompt_file):
    text = _prompt_text(prompt, prompt_file)
    if isinstance(text, dict):
        return text
    return parse_prompt(text if text is not None else "")


if __name__ == "__main__":
    sys.exit(main())
