# 00 - Corpus Overview: The Work Work Loop (WWL)

> **What this is.** Gemini Notebook sources built from the Drive folder
> `WORK_WORK_LOOP`
> (https://drive.google.com/drive/folders/16hI23NswuDlPyft5_7eAqV6cgNBqBv-9),
> via its byte-identical local mirror at `D:\BEACON_HQ\WORK_WORK_LOOP`.
> Text files are flattened into one markdown source **per subfolder**; PDFs and
> audio are carried over untouched because Gemini Notebook ingests those
> formats natively.

## Corpus at a glance

| | |
|---|---|
| Drive folder | `WORK_WORK_LOOP` (52 files) |
| Local mirror | `D:\BEACON_HQ\WORK_WORK_LOOP` |
| Uploadable sources produced | 9 |
| Text files bundled | 43 |
| Files copied in native format | 3 |
| Files that cannot be notebook sources | 6 |
| Total upload payload | 55.6 MB |

## What the WWL is

The **Work Work Loop** is a phased operating system for taking any task from
idea to production. It runs in two halves:

- **BIBLE (Think / Plan)** - phases **P01-P20**, from system summary and
  breaking the old approach, through precedent hunting, shoulder-angel
  critique, brainstorm, design, spec and prototype, to test, bug hunt,
  optimize, alpha, beta and production v1.
- **BUILD (Make)** - phases **P21-P30** plus **PUNLOAD**, from inventory and
  engine through interface, surfaces, tests, verification, live bug hunt,
  hostile break, optimize, production patch and archive.

The `engine/` folder holds the executable core: a **hybrid gate harness** that
enforces the phase gates, its test suites (including a hostile-break suite),
and a rollback script.

## Text source bundles

| Source file | Subfolder | Files inside | Size |
|---|---|---|---|
| `Bible.md` | Bible | 20 | 154.2 KB |
| `build.md` | build | 11 | 73.6 KB |
| `core.md` | core | 1 | 12.4 KB |
| `docs.md` | docs | 3 | 14.3 KB |
| `engine.md` | engine | 8 | 35.8 KB |

## Native-format sources (upload as-is)

| File | Subfolder | Size | Handling |
|---|---|---|---|
| `How_Work_Work_Loop_Ends_AI_Chaos.m4a` | assets | 41.3 MB | copied verbatim |
| `WWL_Operating_Kernel.pdf` | core | 14.0 MB | copied verbatim |
| `Work Work Loop (WWL) Core System and Phase Specifications - Table 1.pdf` | core | 0.0 MB | copied verbatim |

`WWL_Operating_Kernel.pdf` is a **scanned, image-only PDF** - it carries no text
layer (text extraction yields 15 characters). It is therefore copied rather
than converted; Gemini Notebook runs OCR on upload.

## Not uploadable as notebook sources

These are media files. Gemini Notebook does not accept video or raw images as
sources, so they are catalogued here rather than converted. They remain in
`D:\BEACON_HQ\WORK_WORK_LOOP\assets`.

| File | Subfolder | Size |
|---|---|---|
| `NotebookLM Mind Map (8).png` | assets | 1.9 MB |
| `The_Work_Work_Loop.mp4` | assets | 47.2 MB |
| `The_Work_Work_Loop_Framework.png` | assets | 4.2 MB |
| `wwl-hero-q68.webp` | assets | 13.3 MB |
| `wwl-hero.jpg` | assets | 0.7 MB |
| `wwl-hero.mp4` | assets | 17.0 MB |

The audio narration (`How_Work_Work_Loop_Ends_AI_Chaos.m4a`) *is* accepted and
has been copied above. `wwl-hero-q68.webp` is the animated WebP rendered from
`wwl-hero.mp4` earlier in this project.

## A note on duplicates

`engine/` contains four `.md` files that are markdown re-presentations of the
matching `.py` / `.sh` sources: verified to be the same code with whole-line
comments stripped. The commented executable file is therefore strictly richer
and is treated as canonical; each `.md` appears as a stub, so the notebook is
not fed the same code twice (once with its explanations removed).

## Suggested questions for this notebook

- What exactly does each phase gate require before the loop may advance?
- How does the hybrid gate harness enforce a gate in code, and what happens on
  failure?
- Where do the BIBLE and BUILD halves hand off to each other?
- What does the hostile-break suite try to do, and what did it find?
- What is the rollback procedure, and which phases can it unwind?
