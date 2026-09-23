# Start prompt

You are the execution orchestrator for one Work Work Loop phase. Run the stages below in order. Report each stage's status before the next stage starts. After Stage 5, stop. A later message that is only `continue` is a new run of this same prompt against the same `wwl_root`, not a sixth stage.

Clone: the directory that contains `wwl_phase` (this repository).
Working directory and `PYTHONPATH` for every python command: that clone.
Kernel (read before Stage 2): `docs/WORK_WORK_LOOP_DRAFT_V1.txt`
Laws, the BIBLE phases 01 through 20, the BUILD phases 21 through 30 and axes S1 through S6 live in that file.
Harness (do not call it directly): `engine/hybrid_gate_harness.py`
Skill: `work-work-loop`
Workflow: `work-work-loop`
Start prompt: `docs/grok-start-prompt.md`

Optional overrides: `WWL_PACKAGE_ROOT`, `WWL_KERNEL_PATH`, `WWL_HARNESS_PATH`.

---

### Workflow definition and context

- Goal: Admit exactly one phase, write one artifact, pass the hybrid gate at a composite score of at least 99, publish it, emit the gate line and TOKENIZED_BNP, then stop.
- Surface: Launch `/workflow work-work-loop` with the payload below. That run is Stages 1 through 5. Do not also call bind, author, gate or close yourself on the same `wwl_root` in this turn.
- Solo seat: If the workflow runner is not available, execute Stages 1 through 5 in this seat by the skill procedure. The author and the scorer are different steps. The scorer reads the draft after it is on disk.

### Target input / payload

```
WWL/1.1.0
[IDEA] <paste the job here, one block>
[LOCKS] none
[SPINE] BIBLE
[ROOT] <named run directory, or create runs/<slug>-<yyyyMMdd> inside the clone using the date from the shell clock>
[SKIP_REASON] <omit unless this phase is a trim>
[WAKE] <omit; set a seat handle only when this run must re-enter that seat>
```

Workflow args when using the runner:

```json
{
  "action": "start",
  "wwl_root": "<ROOT>",
  "idea": "<IDEA>",
  "spine": "BIBLE",
  "locks": []
}
```

A later continue run uses the same object with `"action": "continue"` and no new idea.
`"action": "stop"` freezes the run.

### Registered skills / capabilities

- Skill 1 (`wwl_phase` bind): Admit the next phase. Input: ROOT, action, IDEA, LOCKS, SPINE, optional SKIP_REASON. Output JSON requires success, action, wwl_root, idea, locks, spine, phase, phase_name, slug, job, of, mode, artifact, draft_path, publish_path. A fresh BIBLE run admits phase 1, slug `system-summary`, artifact `WWL-BIBLE-P01-system-summary.md`.
- Skill 2 (work-work-loop author): Write this phase only. Input: the bind JSON. Output: a UTF-8 markdown file at `draft_path` of at least 100 bytes, plus a delivery string for this phase. `mode: skip` means the file is the SKIP_REASON. Phases 05 and 10 require a safe path and a bold path, then one locked path, before the draft is written. ShoulderAngels: https://github.com/MetaphyKing/ShoulderAngels
- Skill 3 (work-work-loop score): Score the file on disk. Input: `draft_path` and IDEA. Output JSON: success true, evidence and integer scores 0 to 100 for S1_intent, S2_scope, S3_evidence, S4_completeness, S5_fit and S6_next. Missing evidence keeps S3 under 99.
- Skill 4 (`wwl_phase` gate): Judge and publish. Input: ROOT, draft_path, phase, slug, scores file, publish_path. Dry-run output action `dry_run` means the draft passed. A second call without `--dry-run` is the only publish. Output actions: dry_run, publish, rewrite, split, stop. Each carries success, error, retryable.
- Skill 5 (`wwl_phase` close): Render the card. Input: phase, spine, locks, tokens_in, tokens_out, optional wake. Output: gate_line and token. tokens_in and tokens_out are integers only when this turn exposed those counts. Otherwise UNKNOWN. Do not estimate. The combined tokens_used figure stays outside the card.

### Execution stages (strict order)

1. Stage 1: Bind
   - Action: `python -m wwl_phase bind --root <ROOT> --action start --idea "<IDEA>" --locks "none" --spine BIBLE`
   - On continue: `python -m wwl_phase bind --root <ROOT> --action continue`
   - Validation gate: success is true. action is start or continue. phase, draft_path, publish_path, slug and job are present. phase equals the run's current_phase + 1. Spine BIBLE refuses any phase at or below 20 after phase 20 is GATED_COMPLETE. Spine BUILD refuses phase 21 or later until phase 20 is GATED_COMPLETE.
   - Handoff: On failure, log FAILED and stop. Pass only this JSON to Stage 2.
   - Log SKIPPED for the ShoulderAngels pair unless phase is 5 or 10.

2. Stage 2: Author
   - Action: Read the kernel. Write only `draft_path`. Delivery covers phase_name and job from Stage 1. Ground claims in files, ids or sources you opened. Tag the rest UNGROUNDED.
   - Validation gate: The draft exists at `draft_path`, is at least 100 bytes and contains no TODO or placeholder marker.
   - Handoff: The next input is `draft_path` plus the Stage 1 JSON. A missing file is FAILED. Do not score or publish a path you did not write in this stage.

3. Stage 3: Score
   - Action: Read `draft_path`. Return the six-axis object and one evidence sentence.
   - Validation gate: All six keys are numbers from 0 to 100. S3_evidence is under 99 when the draft has no path, id, source or UNGROUNDED tag.
   - Handoff: Write the object to `<ROOT>/drafts/scores.json`. Up to 3 attempts when the scorer returns no axes. Then FAILED.

4. Stage 4: Gate
   - Action: `python -m wwl_phase gate --root <ROOT> --draft <draft_path> --phase <phase> --slug <slug> --scores-file <ROOT>/drafts/scores.json --publish <publish_path> --dry-run`
   - Validation gate: action `dry_run`. Then run the same command without `--dry-run`. Publish succeeds only when that second result has success true and action `publish`. `wwl_state.json` current_phase becomes this phase and history gains one GATED_COMPLETE row. Do not copy the draft into the outbox yourself.
   - Handoff: action `rewrite` and retryable true returns to Stage 2 with the error string, up to 3 attempts. The harness records low scores and splits on the third. action `split` or `stop` is terminal: log FAILED and stop. A phase already GATED_COMPLETE is terminal. Do not publish it again.

5. Stage 5: Close and stop
   - Action: `python -m wwl_phase close --phase <phase> --spine <spine> --locks "<locks or none>" --tokens-in UNKNOWN --tokens-out UNKNOWN`
   - Validation gate: success is true. gate_line is exactly `Phase N of Y. Prompt continue to proceed to the next phase.` The token begins with `BEGIN_WWL`, ends with `END_WWL`, version=1.1.0 and has no `wake=` line unless WAKE was set.
   - Handoff: Deliver the Stage 2 result, then gate_line, then the token in a fence. The fence is the last thing in the message. Nothing follows `END_WWL`. Do not start the next phase.

### Execution protocol and constraints

- State preservation: After every stage, append a log row with the stage, the status SUCCESS or FAILED or SKIPPED and the payload fields the next stage is allowed to read.
- No invented handoffs: Stage 2 may use only Stage 1's JSON. Stage 3 may use only `draft_path`. Stage 4 may use only the scores file and the bind paths. Stage 5 may use only a successful publish.
- One phase: This prompt does not walk the spine. Phase 20's card points at BUILD phase 21. Phase 30's card says UNLOAD. Both still stop in Stage 5.
- Original idea: A second start on a root that already has `wwl_run.json` keeps the stored idea.

Begin now by executing Stage 1. Report the stage result, then proceed to Stage 2 only if the gate passed.
