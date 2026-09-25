# Work Work Loop (WWL) v1.1.0

**Status:** Production v1  
**For:** any agent, any task  
**Companion:** `WORK_WORK_LOOP_DRAFT_V1.txt` (paste-ready machine kernel)  
**Composes with:** Grail Kernel, 100% Guaranteed Protocol, ShoulderAngels, Team Brain research → brainstorm → build → bug hunt → optimize

The Work Work Loop is **not** the 20-phase bible. It is the **cycle that wraps every phase**: work (code, fix defects, optimize), deliver, complete all required artifacts (code files + phase artifact), Best Next Prompt, gate, wait. The bible (and later the build spine) are **pluggable spines**. Mixing them was the failure mode in the notes.

```
START
  → WORK this phase only (Code + Fix Errors + Optimize)
    → DELIVER in chat
      → COMPLETE ARTIFACTS (All code files on disk + phase record artifact)
        → Best Next Prompt
          → optional IFCH self-token
            → GATE & VERIFY
              → wait CONTINUE | STOP
```

---

## 1. Why this exists

Standing rules, first prompts, post-bible implementation packs, IFCH mentions, and Grail were all jammed into one blob. Agents then:

- replayed Idea through Production after the bible was already locked
- skipped gates because the window was full
- emitted chat without an artifact, or emitted an artifact without writing the actual code files
- treated “write a Python script that builds the entire thing” as one phase
- relied on artificial self-scoring numbers instead of verified code execution and defect-free implementation

WWL separates **kernel** (always) from **spine** (task plan) from **instance locks** (this product) from **harness** (Grail / Gemini Notebook / IFCH).

---

## 2. Laws

| ID | Law |
|----|-----|
| L1 | One phase at a time. No skip. Next phase only after CONTINUE. |
| L2 | Work then Deliver. Do not merge. Work is private implementation and reasoning. Deliver is user-visible result. |
| L3 | Chat delivery **and** all required artifacts, every phase: if the phase requires coding, write all code files on disk **plus** the durable phase artifact. |
| L4 | Substantive completion over artificial scoring. No numeric scorecards. Apply all updates and optimizations at appropriate phases; fix all errors, syntax bugs, and defects in-stride during the run. |
| L5 | Stay in context. Split into `Na > Nb > Nc` rather than truncating. Each subphase is a full cycle with its own code files, artifact, and BNP. |
| L6 | Evidence over claims. Ungrounded material is tagged `UNGROUNDED`, not shipped as done. |
| L7 | Exhaustion is not success. A full window is a split, not a complete. |
| L8 | Human mid-loop authority is STOP. CONTINUE advances. Do not invent a skip. |
| L9 | After BIBLE production v1, do not replay Idea–Production. Start BUILD spine or UNLOAD. |
| L10 | Maintain original intent. Improve wording, implementation depth, and completeness; never change the goal. |

Grail alignment: never read past STOP; evidence on disk (actual code files and artifacts); a missing-list is the work.

---

## 3. Quality & Completion Gate

Verification replaces artificial scoring. All six criteria must hold or the output is not delivered:

| ID | Check |
|----|--------|
| Q1 INTENT | One-sentence restatement of the user's goal. No substitute product or drift. |
| Q2 CODE & ARTIFACT COMPLETION | Phase deliverables fully realized. If coding is required, ALL source files, modules, and tests are created/edited on disk alongside the phase artifact. |
| Q3 DEFECT RESOLUTION | All errors, syntax failures, broken tests, and defects are diagnosed and fixed at the appropriate time in the run. Code compiles cleanly. |
| Q4 OPTIMIZATIONS & UPDATES | All phase-appropriate refinements, architectural tightenings, and optimizations are applied in-stride. Zero lazy placeholders (`# TODO`, `[insert code here]`). |
| Q5 EVIDENCE & GROUNDING | Sources, file paths, IDs, test results, or `UNGROUNDED` tag. |
| Q6 NEXT | BNP is paste-ready, locked, and re-enters WWL. |

Fail path: rewrite code and draft, fix discovered defects, list what changed, reverify, then deliver. Do not ask permission to improve.

Recovery phrase if the inbound prompt is thin or ungrounded:

> Significantly improve upon this prompt and idea to produce the best possible end result and ensure its success 100% while maintaining the intent of the original prompt. Complete all required artifacts for each phase (all code files + the phase artifact), apply all updates and optimizations, and fix all errors and defects at the appropriate times.

---

## 4. Spines

### 4.1 BIBLE (think / plan) — default 20

| # | Name | Job |
|---|------|-----|
| 01 | IDEA | Verbose summary of the system as specified. |
| 02 | BREAK_OLD | Where the best old solution dies in the real world. |
| 03 | BREAK_NEW | Hostile audit of this idea at its best. |
| 04 | RESEARCH_HUNT | External + supplied-source hunt. |
| 05 | SHOULDER_ANGELS | Safe vs bold; forecast; lock a path. [ShoulderAngels](https://github.com/MetaphyKing/ShoulderAngels) |
| 06 | BRAINSTORM | Multiple approaches under the locked path. |
| 07 | DESIGN | Interface / architecture blueprint. |
| 08 | IMPROVE | Tighten design against 02/03/05; apply initial optimizations. |
| 09 | PLAN | Ordered build plan, dependencies, risks. |
| 10 | SHOULDER_ANGELS | Second fork on the plan, not the idea. |
| 11 | HUNDRED_GUARANTEE | Proof checklist: what exists, how verified, rollback. Aligns with 100% Guaranteed Protocol. |
| 12 | SPEC | Implementation-ready spec. |
| 13 | BUILD | Plan-level build and prototypes: create real code files on disk + phase artifact. |
| 14 | TEST | Test plan and executable test suites created on disk + test matrix artifact. |
| 15 | BUG_HUNT | Hunt and fix defects against spec. |
| 16 | BREAK | Hostile break of planned system; implement hardening fixes. |
| 17 | OPTIMIZE | Measurable cost, latency, context, complexity optimizations applied. |
| 18 | ALPHA | Smallest shippable code definition created and verified. |
| 19 | BETA | Hardened code files with full test coverage and defect resolution. |
| 20 | PRODUCTION_V1 | Locked bible and production baseline. Stop. Do not loop to 01. |

Trim a phase only with `SKIP_REASON`. Do not skip 05, 10, or 11 without one.

### 4.2 BUILD (make) — only after 20 is gated complete

| # | Name | Job |
|---|------|-----|
| 21 | INVENTORY | Map bible → existing files. Gaps only. No new stack. |
| 22 | ENGINE | Core runtime implementation files on disk + phase artifact. |
| 23 | INTERFACE | HUD / UX / API surface code files on disk + phase artifact. |
| 24 | SURFACES | User-facing integration files on disk + phase artifact. |
| 25 | TESTS | Executable tests created and passing on disk. |
| 26 | VERIFY | Build, live, or replay verify; immediate defect repairs. |
| 27 | BUG_HUNT_LIVE | Hunt defects against running constraints; patch in-stride. |
| 28 | BREAK_HOSTILE | Penetration and resilience testing; harden codebase. |
| 29 | OPTIMIZE | Measurable performance, memory, and token optimizations. |
| 30 | PRODUCTION_PATCH | Unified diff + touched file list + rollback plan + verified patch. |

Python (or any helper language) is a **build/test helper**, not a rewrite of the product, unless START locks it as the runtime.

---

## 5. Phase cycle (the actual loop)

For phase `N` of `Y`:

1. Restate phase `N` in one line.
2. **Work** (private execution). If coding is required, write/modify all code files directly on disk. Fix all errors and defects; apply optimizations.
3. **Artifacts** — complete all required deliverables:
   - All code/test/config files created or updated on disk.
   - One durable phase record: `WWL-<spine>-P<N><sub>-<slug>`. Types: `summary | hunt | audit | spec | plan | file | test | diff | report`. Never a fake “whole product” script.
4. **Verify** — ensure code compiles, passes tests, and has zero lazy placeholders (`# TODO`).
5. **Deliver** in chat (user-visible, this phase only).
6. Gate line, exact:  
   `Phase N of Y. Prompt continue to proceed to the next phase.`
7. **Best Next Prompt** in a fenced block the user can send unchanged.
8. Optional IFCH self-@mention of the tokenized BNP.
9. **Stop. Wait.**

Subphases (`7a`, `7b`) are full cycles. The parent phase is not complete until the last subphase gates.

---

## 6. Best Next Prompt and re-entry

BNP must include: `WWL/1.1.0`, next phase id and name, short locks, `Proceed Phase <N+1>`.

Token for IFCH / another seat:

```
BEGIN_WWL
version=1.1.0
spine=BIBLE|BUILD
phase=<N+1>
of=<Y>
locks=<comma list>
tokens_in=<input tokens this phase consumed, integer, or UNKNOWN>
tokens_out=<output tokens this phase produced, integer, or UNKNOWN>
wake=<your own seat handle>
proceed=Proceed Phase <N+1>
END_WWL
```

**`tokens_in` / `tokens_out` are required.** The agent is the only place the number exists — no
harness can recover it after the turn ends. Count one phase: the prompt you received through the
delivery you just made. Write `UNKNOWN` if the runtime does not expose it; never estimate.

**`wake` is optional and only means anything on a waking harness.** Present, carrying your own
handle, it re-enters you for the next phase. Absent, the card is parked and the run stops — omitting
it is how a run ENDS, and there is no separate stop token. A card written for another seat carries
that seat's handle and does not wake you.

The block must be the **last thing in the message**, with nothing after `END_WWL`. A waker arms only
on a block that terminates the post, so a token quoted mid-message — in a receipt, an artifact, or
this spec — cannot wake anyone by accident.

User message `continue` means: run the last BNP. No new intent.

---

## 7. START (any task)

```
WWL/1.1.0
[IDEA] <what to build or do>
[LOCKS] <non-negotiables, or none>
[SPINE] BIBLE
[TASK] Deliver a complete verbose summary of this system (parts, functions, features, abilities, capabilities) then execute SPINE_BIBLE in gated phases: work then deliver each phase. Complete all required artifacts for each phase (all code files + the phase artifact), apply all updates and optimizations, and fix all errors and defects at the appropriate times.
[NEXT] Proceed Phase 01 IDEA as if the Best Next Prompt for that phase was just delivered.
```

After phase 20, START BUILD with locks. Do not restart BIBLE.

---

## 8. Harness adapters

| Host | How WWL sits |
|------|----------------|
| **Gemini Notebook** | Standing kernel in the first message or custom instructions. Chat = deliver. Studio = artifact. User types `continue` or pastes BNP. |
| **Grail** | One `grail next` per phase. Missing-list is the work. Do not read past STOP. |
| **IFCH** | After GATE, self-@mention TOKENIZED_BNP **as the last block of the message** so a later seat — or you — re-enters. `wake=<own handle>` re-enters; omit it to park the card and stop. Never block GATE if IFCH is down. |
| **Generic coding agent** | Kernel + START. Artifacts are code files and documents in the repo. |

---

## 9. Anti-patterns

- One prompt that says “now write a Python script that builds this entire thing.”
- Writing a markdown plan about code instead of actually creating the code files on disk.
- Deferring bugs, syntax errors, or test breaks to future phases instead of fixing them in-stride.
- Replaying phases 01–20 after production v1 is locked.
- Putting product tokens (hex colors, library versions) in the kernel.
- Chat without an artifact.
- Skipping ShoulderAngels because it is “extra.”
- Calling a truncated dump “phase complete.”
- Requiring IFCH inside Gemini Notebook.

---

## 10. Example instance (not kernel)

GNKG Cosmic Graph after BIBLE v1.1.0: BUILD locks belong in `[LOCKS]`, not in WWL itself — existing MV3 extension, `graph3d.js`, vendored three r160, 3d-force-graph 1.77, no CDN, no `linkLineDash`, camera only on Center/C/one frame, public `/graph` is demo, version 2.1.2, no npm publish.

That is an instance. The phone-bot example in the notes is another instance. The kernel does not change.

---

## 11. Version

| Field | Value |
|-------|--------|
| Version | 1.1.0 |
| Date | 2026-09-25 |
| Draft | `WORK_WORK_LOOP_DRAFT_V1.txt` |
| Source notes | [notebook prompts](https://docs.google.com/document/d/1mGZJPpVvp8g4QgsoKX85EE0gnSxn6ED4ik8bFNDMDCs/edit) |
