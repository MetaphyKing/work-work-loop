---
name: work-work-loop
description: Run one Work Work Loop phase from MetaphyKing/work-work-loop: score, work, deliver, write one artifact, emit a Best Next Prompt and gate it with the local hybrid harness. Stops after the gate line and a fenced BEGIN_WWL block. Use when the user runs /work-work-loop, says WWL, Work Work Loop, continue the loop, Proceed Phase or pastes a WWL/1.1.0 START card.
---

# Work Work Loop

Run one phase, then stop. The kernel is `docs/WORK_WORK_LOOP_DRAFT_V1.txt` in this clone. Read that file before the phase. Laws, spines and the six score axes live there. This skill is the Grok procedure around that file.

The gate is `engine/hybrid_gate_harness.py`. Call it only through `python -m wwl_phase` with `PYTHONPATH` and the working directory set to the clone (the directory that contains `wwl_phase`). Every command prints one JSON object. `success: false` ends the turn. Deliver `error` and stop.

Optional local overrides: `WWL_PACKAGE_ROOT` for the working directory, `WWL_KERNEL_PATH` for the kernel file, `WWL_HARNESS_PATH` for the harness file. The start prompt is `docs/grok-start-prompt.md`.

## Admit

Use the run root the user names. When they do not name one, create `runs/<slug>-<yyyyMMdd>` inside the clone and take the date from the shell clock.

- A new job: `python -m wwl_phase bind --root <root> --action start --idea "<idea>" --locks "<comma list or none>" --spine BIBLE`
- A message that is only `continue`: `python -m wwl_phase bind --root <root> --action continue`
- A message that is only `stop`: `python -m wwl_phase bind --root <root> --action stop`

`action: unload` means the spine is finished. Deliver that and stop. A trim requires `--skip-reason`. Phases 05, 10 and 11 are not trimmed without one.

## Work, then deliver

Take `phase`, `phase_name`, `job`, `idea`, `locks`, `mode`, `draft_path` and `publish_path` from the bind JSON.

Work stays private. The chat delivery is this phase only. Write one UTF-8 markdown file at `draft_path`. It must be at least 100 bytes and must not contain a TODO or other placeholder marker. `mode: skip` means the file states the SKIP_REASON and does not do the phase's other job.

Ground every claim in a file, an id or a source. Tag anything you cannot ground as `UNGROUNDED`.

Phases 05 and 10 lock one path from a safe option and a bold option before the draft is written. The method is ShoulderAngels: `https://github.com/MetaphyKing/ShoulderAngels`.

## Gate

Score `S1_intent`, `S2_scope`, `S3_evidence`, `S4_completeness`, `S5_fit` and `S6_next` as integers from 0 to 100. Missing evidence stays under 99 on S3. Write that object to a JSON file inside the run root.

```
python -m wwl_phase gate --root <root> --draft <draft_path> --phase <n> --slug <slug> --scores-file <scores.json> --publish <publish_path> --dry-run
```

`action: rewrite` means fix the draft and score again. Stop when `action` is `split` or `stop`. The harness itself stops the score loop at three failures.

When the dry run returns `action: dry_run`, run the same command without `--dry-run`. That publish is what advances `wwl_state.json`. Do not copy the draft into the outbox yourself.

## Close and stop

```
python -m wwl_phase close --phase <n> --spine <spine> --locks "<locks>" --tokens-in <integer or UNKNOWN> --tokens-out <integer or UNKNOWN>
```

Pass the token counts this turn actually exposed. Use `UNKNOWN` when they were not exposed. Do not estimate. Add `--wake <handle>` only when the user names a seat to re-enter.

Deliver the phase result, then `gate_line` exactly as printed, then `token` in a fence. That fence is the last thing in the message. Nothing follows `END_WWL`. Do not start the next phase. The next `continue` is a new turn.

## Tests

From the clone: `python -m unittest discover -s tests -t .`

The workflow of the same name runs this phase with a separate author and a separate scorer: `/workflow work-work-loop`.
