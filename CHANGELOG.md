# Changelog

## 1.1.1 — 2026-09-12

- Mini Fix Loop addendum: `docs/WWL_MFL.md`. Names L4 `failed_attempts` as MFL-A (cap 3, this-chamber only) vs MFL-B (file bugs, human CONTINUE). Harness counters unchanged.

## 1.1.0 — 2026-09-08

- `TOKENIZED_BNP` gains `tokens_in=` and `tokens_out=` (required; `UNKNOWN` if the runtime does not expose them, never an estimate). The agent is the only place a per-phase token count exists — no harness can recover it after the turn ends — so cost per phase is now readable straight off the card.
- `TOKENIZED_BNP` gains an optional `wake=<seat handle>`. On a waking harness, present means re-enter that seat for the next phase; absent means park the card and stop. Omitting it is how a run ENDS; there is no separate stop token.
- The token block must be the LAST thing in the message, nothing after `END_WWL`. A waker arms only on a block that terminates the post, so a token quoted mid-message — in a receipt, an artifact, or the kernel itself — cannot wake anyone by accident. This replaces per-harness wake keys, which drifted out of sync with the kernel the moment a loop changed spine.
- Kernel version string 1.0.0 → 1.1.0. Both new fields are additive; a 1.0.0 card still parses.

## 1.0.1 — 2026-09-08

- Relicensed from MIT to Apache License 2.0. Commits through `7f56080` remain available under MIT as originally published.

## 1.0.0 — 2026-09-07

- Public package of Work Work Loop: kernel, BIBLE spine (01–20), BUILD spine (21–30), hybrid gating harness, and notebook corpus.
- Machine-paste kernel (`docs/WORK_WORK_LOOP_DRAFT_V1.txt`) and production spec (`docs/WORK_WORK_LOOP_v1.md`).
- Engine defaults to `$WWL_ROOT` or `./.wwl` (no hardcoded `/workspace` paths). Fresh state starts at BIBLE phase 0.
