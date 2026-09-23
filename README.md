<p align="center">
  <picture>
    <source srcset="https://github.com/MetaphyKing/work-work-loop/blob/main/assets/wwl-hero-q68.webp?raw=true" type="image/webp">
    <img width="1280" height="auto" alt="Work Work Loop" src="https://github.com/MetaphyKing/work-work-loop/blob/main/assets/wwl-hero.jpg?raw=true">
  </picture>
</p>

---

# Work Work Loop

Most agents treat a job like a hallway: they start walking and hope they reach the end before they forget why they entered. Work Work Loop treats a job like a **canal lock**. One chamber at a time. The water has to settle, the gates have to close and the next lock's instructions have to be written on a card you can hand to whoever shows up tomorrow.

That is the whole product. A standing kernel any agent can load so that **work, delivery, evidence and the next prompt** cannot drift apart.

## Install

Clone this repository. Python 3.9 or newer. The phase tools use the standard library only.

```bash
git clone https://github.com/MetaphyKing/work-work-loop.git
cd work-work-loop
python -m wwl_phase --help
python -m unittest discover -s tests -t .
```

Optional, from the clone: `pip install -e .` registers the `wwl-phase` command. You do not need that install to run `python -m wwl_phase`.

## Quick start

**1. Load the kernel once** (paste into standing instructions or the first message):

- Machine-parseable: [`docs/WORK_WORK_LOOP_DRAFT_V1.txt`](docs/WORK_WORK_LOOP_DRAFT_V1.txt)
- Human spec: [`docs/WORK_WORK_LOOP_v1.md`](docs/WORK_WORK_LOOP_v1.md)

**2. Start a task** with [`docs/START_ANY_TASK.txt`](docs/START_ANY_TASK.txt). Fill `[IDEA]`. Leave `[SPINE] BIBLE`. Send it.

On Grok, use [`docs/grok-start-prompt.md`](docs/grok-start-prompt.md) or `/workflow work-work-loop`.

**3. After each phase** the agent must:

1. Deliver in chat
2. Attach one artifact
3. Say exactly: `Phase N of Y. Prompt continue to proceed to the next phase.`
4. Paste a Best Next Prompt you can send unchanged
5. **Stop.**

You may reply with only `continue`. That means: run the last Best Next Prompt. After phase 20, do not restart Idea. Start the BUILD spine with product locks in `[LOCKS]`.

One phase looks like this:

```
score inbound → work this phase → score outbound → deliver in chat
  → write one artifact → emit Best Next Prompt → gate → wait
```

## Package map

| Path | What a partner opens it for |
|------|------------------------------|
| [`docs/`](docs/) | Kernel, human spec, START card, Grok start prompt |
| [`Bible/`](Bible/) | Gated BIBLE records, phases 01 through 20 |
| [`build/`](build/) | Gated BUILD records, phases 21 through 30 |
| [`core/`](core/) | Operating kernel PDF and blueprint |
| [`engine/`](engine/) | Two-pass gating harness |
| [`wwl_phase/`](wwl_phase/) | Phase CLI: `parse`, `bind`, `gate`, `close` |
| [`tests/`](tests/) | Tests for that CLI |
| [`.grok/skills/work-work-loop/SKILL.md`](.grok/skills/work-work-loop/SKILL.md) | Grok skill. One phase, then stop |
| [`.grok/workflows/work-work-loop.rhai`](.grok/workflows/work-work-loop.rhai) | Grok workflow of the same name |
| [`notebook_sources/`](notebook_sources/) | Corpus for Gemini Notebook |
| [`assets/`](assets/) | Title hero, social still, motion and audio |

Paths from a clone of this repo:

- Kernel: `docs/WORK_WORK_LOOP_DRAFT_V1.txt`
- Harness: `engine/hybrid_gate_harness.py`
- Package root: this directory

`WWL_KERNEL_PATH` and `WWL_HARNESS_PATH` override the kernel file and the harness file. `WWL_PACKAGE_ROOT` is the working directory when a Grok seat is not already in the clone. The gate is called only through `python -m wwl_phase`.

## How a phase is allowed to finish

All six must hold, or the output is not delivered (score at least 99):

1. **Intent.** Restates the user's goal. Does not swap the product.
2. **Scope.** This phase only.
3. **Evidence.** Paths, ids, sources or an `UNGROUNDED` tag.
4. **Complete.** Work, deliver, artifact, Best Next Prompt and gate line.
5. **Fit.** Fits context, or already split into `Na > Nb > Nc`.
6. **Next.** The Best Next Prompt would re-enter this loop.

Human mid-loop authority is **STOP**. Exhaustion is a split, not a complete.

## Spines

The twenty steps are a **spine**, not the loop. Mixing those two things is how agents replay "Idea" after the bible is already locked, skip gates when the window is full, or treat "write a Python script that builds the entire thing" as a valid next move.

| Layer | Stays the same | Changes per job |
|-------|----------------|-----------------|
| **Kernel** | Laws, score gate, cycle, CONTINUE/STOP | Never |
| **Spine** | BIBLE 01 through 20, then BUILD 21 through 30 | Trim only with `SKIP_REASON` |
| **Locks** | | Product, stack, tokens, "do not invent a new runtime" |
| **Harness** | | Gemini Notebook, Grail, IFCH, a coding agent |

**BIBLE (think and plan).** 01 Idea, 02 Break old, 03 Break new, 04 Research hunt, 05 [ShoulderAngels](https://github.com/MetaphyKing/ShoulderAngels), 06 Brainstorm, 07 Design, 08 Improve, 09 Plan, 10 ShoulderAngels, 11 Hundred guarantee, 12 Spec, 13 Build (plan-level), 14 Test, 15 Bug hunt, 16 Break, 17 Optimize, 18 Alpha, 19 Beta, **20 Production v1 (lock, do not loop)**.

**BUILD (make).** Only after 20 is gated: 21 Inventory, 22 Engine, 23 Interface, 24 Surfaces, 25 Tests, 26 Verify, 27 Live bug hunt, 28 Hostile break, 29 Optimize, **30 Production patch** (diff, file list and rollback).

Python is a helper language unless START locks it as the runtime. Do not invent a new stack in BUILD.

Full phase texts live in [`Bible/`](Bible/) and [`build/`](build/).

## Grok package

The skill, the workflow and `wwl_phase` are one package. They run a single phase and stop.

- Skill: [`.grok/skills/work-work-loop/SKILL.md`](.grok/skills/work-work-loop/SKILL.md)
- Workflow: [`.grok/workflows/work-work-loop.rhai`](.grok/workflows/work-work-loop.rhai). Bind, author, score, gate, then close.
- Start prompt: [`docs/grok-start-prompt.md`](docs/grok-start-prompt.md). Five stages. A later `continue` is a new run on the same root.
- CLI version `1.1.0`: `python -m wwl_phase` with subcommands `parse`, `bind`, `gate` and `close`.

## Engine

A small two-pass gate: structural checks, then a weighted qualitative score that must clear 99. Run state lives in the directory you pass as `--root`. The CLI sets `WWL_ROOT` to that directory before it calls the harness.

```bash
python -m wwl_phase gate --help
python -m unittest engine.test_hybrid_gate_harness engine.test_hostile_break
```

`engine/rollback.sh` reverts to the last gated history entry. The harness file is [`engine/hybrid_gate_harness.py`](engine/hybrid_gate_harness.py).

## Harnesses

| Host | What "artifact" and "continue" mean |
|------|--------------------------------------|
| Gemini Notebook | Studio file plus chat delivery. The user pastes the Best Next Prompt or types `continue`. |
| [Grail Kernel](https://github.com/MetaphyKing/grail-kernel) | One `grail next` per phase. Do not read past STOP. |
| IFCH | Optional self-mention of a tokenized Best Next Prompt, posted as the **last block** of the message, so another seat or the same one can re-enter. `wake=<own handle>` re-enters. Omit it to park and stop. Never block the gate if IFCH is down. |
| Coding agent | Artifacts are files in the repo. |
| Grok | Skill `work-work-loop` or `/workflow work-work-loop`. |

## Non-goals

- This is not a chatbot personality and not a new runtime.
- `Bible/` and `build/` are gated phase records. They are not a second kernel.
- One phase per turn. The package does not walk the spine by itself.
- Token counts on the card are the counts the turn exposed, or `UNKNOWN`. They are not estimates.

## Related

- [ShoulderAngels](https://github.com/MetaphyKing/ShoulderAngels): safe versus bold, forecast, lock a path (phases 05 and 10)
- Team Brain protocols: research, brainstorm, build, bug hunt, optimize
- [CONTRIBUTING.md](CONTRIBUTING.md)

## License

Copyright 2026 Logan Smith / Metaphy LLC.

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
