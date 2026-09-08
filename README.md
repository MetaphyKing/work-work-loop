<p align="center">
  <picture>
    <source srcset="https://github.com/MetaphyKing/work-work-loop/blob/main/assets/wwl-hero-q68.webp?raw=true" type="image/webp">
    <img width="1280" height="auto" alt="Work Work Loop" src="https://github.com/MetaphyKing/work-work-loop/blob/main/assets/wwl-hero.jpg?raw=true">
  </picture>
</p>

---

# Work Work Loop v1

Most agents treat a job like a hallway: they start walking and hope they reach the end before they forget why they entered. Work Work Loop treats a job like a **canal lock**. One chamber at a time. The water has to settle, the gates have to close, and the next lock’s instructions have to be written on a card you can hand to whoever shows up tomorrow.

That is the whole product. Not a chatbot personality. A standing kernel any agent can load so that **work, delivery, evidence, and the next prompt** cannot drift apart.

---

## What this is

WWL is a **phase cycle** you wrap around any task, on any agent:

```
score inbound → work this phase → score outbound → deliver in chat
  → write one artifact → emit Best Next Prompt → gate → wait
```

The famous twenty steps (idea through production v1) are a **spine**, not the loop. Mixing those two things is how agents replay “Idea” after the bible is already locked, skip gates when the window is full, or treat “write a Python script that builds the entire thing” as a valid next move.

| Layer | Stays the same | Changes per job |
|-------|----------------|-----------------|
| **Kernel** | Laws, score gate, cycle, CONTINUE/STOP | Never |
| **Spine** | BIBLE 01–20, then BUILD 21–30 | Trim only with `SKIP_REASON` |
| **Locks** | — | Product, stack, tokens, “do not invent a new runtime” |
| **Harness** | — | Gemini Notebook, Grail, IFCH, a coding agent |

---

## Quick start

**1. Load the kernel once** (paste into standing instructions or the first message):

- Machine-parseable: [`docs/WORK_WORK_LOOP_DRAFT_V1.txt`](docs/WORK_WORK_LOOP_DRAFT_V1.txt)
- Human spec: [`docs/WORK_WORK_LOOP_v1.md`](docs/WORK_WORK_LOOP_v1.md)

**2. Start a task** with [`docs/START_ANY_TASK.txt`](docs/START_ANY_TASK.txt). Fill `[IDEA]`. Leave `[SPINE] BIBLE`. Send it.

**3. After each phase** the agent must:

1. Deliver in chat  
2. Attach one artifact  
3. Say exactly: `Phase N of Y. Prompt continue to proceed to the next phase.`  
4. Paste a Best Next Prompt you can send unchanged  
5. **Stop.**

You may reply with only `continue`. That means: run the last Best Next Prompt. After phase 20, do not restart Idea. Start the BUILD spine with product locks in `[LOCKS]`.

---

## How a phase is allowed to finish

All six must hold, or the output is not delivered (score ≥ 99):

1. **Intent** — restates the user’s goal; does not swap the product  
2. **Scope** — this phase only  
3. **Evidence** — paths, ids, sources, or an `UNGROUNDED` tag  
4. **Complete** — work + deliver + artifact + Best Next Prompt + gate line  
5. **Fit** — fits context, or already split into `Na > Nb > Nc`  
6. **Next** — the Best Next Prompt would re-enter this loop  

Human mid-loop authority is **STOP**. Exhaustion is a split, not a complete.

---

## Spines

**BIBLE (think / plan)** — 01 Idea → 02 Break old → 03 Break new → 04 Research hunt → 05 [ShoulderAngels](https://github.com/MetaphyKing/ShoulderAngels) → 06 Brainstorm → 07 Design → 08 Improve → 09 Plan → 10 ShoulderAngels → 11 Hundred guarantee → 12 Spec → 13 Build (plan-level) → 14 Test → 15 Bug hunt → 16 Break → 17 Optimize → 18 Alpha → 19 Beta → **20 Production v1 (lock, do not loop)**.

**BUILD (make)** — only after 20 is gated: 21 Inventory (gaps against the existing system) → 22 Engine → 23 Interface → 24 Surfaces → 25 Tests → 26 Verify → 27 Live bug hunt → 28 Hostile break → 29 Optimize → **30 Production patch** (diff + file list + rollback).

Python is a helper language unless START locks it as the runtime. Do not invent a new stack in BUILD.

Full phase texts live in [`Bible/`](Bible/) and [`build/`](build/).

---

## Repository layout

```
docs/                 Kernel, spec, and START template
Bible/                Gated BIBLE artifacts (P01–P20)
build/                Gated BUILD artifacts (P21–P30)
core/                 Operating kernel PDF and blueprint
engine/               Two-pass gating harness (stdlib Python)
notebook_sources/     Corpus for Gemini Notebook
assets/               Hero still, webp, and motion
```

---

## Engine

A small, zero-dependency two-pass gate: structural checks, then a weighted qualitative score that must clear 99. State and config live under `$WWL_ROOT` or `./.wwl`.

```bash
python engine/hybrid_gate_harness.py --help
python -m unittest engine.test_hybrid_gate_harness engine.test_hostile_break
```

`engine/rollback.sh` reverts to the last gated history entry.

---

## Harnesses

| Host | What “artifact” and “continue” mean |
|------|--------------------------------------|
| Gemini Notebook | Studio file + chat delivery. User pastes BNP or types `continue`. |
| [Grail Kernel](https://github.com/MetaphyKing/grail-kernel) | One `grail next` per phase. Do not read past STOP. |
| IFCH | Optional self-mention of a tokenized BNP, posted as the **last block** of the message, so another seat — or the same one — can re-enter. `wake=<own handle>` re-enters; omit it to park and stop. Never block the gate if IFCH is down. |
| Coding agent | Artifacts are files in the repo. |

---

## Related

- [ShoulderAngels](https://github.com/MetaphyKing/ShoulderAngels) — safe vs bold, forecast, lock a path (phases 05 and 10)
- Team Brain protocols — research, brainstorm, build, bug hunt, optimize

---

## License

Copyright 2026 Logan Smith / Metaphy LLC.

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
