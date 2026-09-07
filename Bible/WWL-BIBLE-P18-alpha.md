# WWL-BIBLE-P18-alpha: Minimum Viable Product (MVP) Specification & Plan

This document establishes the formal **Minimum Viable Product (MVP)** scope and release boundary for the **Two-Pass Peer Gating Harness (`hybrid_gate_harness.py`)**, serving as the definitive plan to lock execution parameters prior to completing the BIBLE spine.

---

## 1. Executive Vision & The Smallest Shippable Unit
The core mission of this MVP is to deliver a bulletproof, zero-dependency, local gating pipeline that guarantees chronological execution and syntactic precision without platform locking or context exhaustion.

The MVP is defined by four core assets:
1.  **`hybrid_gate_harness.py` (Core Engine):** Zero-dependency execution utility implementing Pass 1 (Programmatic sequencing), Pass 1.5 (AST Syntax Validation), and Pass 2 (Qualitative Weighted Scoring Evaluator).
2.  **`wwl_config.json` (Configuration Map):** Static parameters mapping validation rules, regex expressions, attempt thresholds, and scoring weights.
3.  **`wwl_state.json` (Active State Database):** Atomic-written, schema-validated append-only transaction registry tracking phase transitions.
4.  **CLI Command Boundary Wrapper:** Explicit CLI execution interface supporting standardized standard exit codes (`0` for success, `1` for error) and structured error traces (`harness_traceback.json`).

---

## 2. API Interface & CLI Boundary Specs
The harness defines a rigid command-line boundary to ensure interoperability with continuous integration (CI) runtimes and external hooks:

### CLI Invocation Scheme
```bash
python3 hybrid_gate_harness.py --draft <path_to_draft> --phase <phase_num> --slug <phase_slug> [--scores <json_scores>]
```

### Parameter Specification
*   `--draft`: Absolute path to the candidate markdown or code file staged inside `/workspace/scratch/`.
*   `--phase`: Chronological integer representation of the target phase (must equal `current_phase + 1`).
*   `--slug`: Lowercase string identifier for the target phase.
*   `--scores`: Optional JSON dictionary mapping qualitative score axes (S1–S6) to evaluate in Pass 2. If omitted, Pass 2 evaluates default passing baselines to support automated pre-flight workflows.

### Process Exit Codes
*   `0`: Check passes successfully. Candidate draft promoted to `/workspace/out/` and system state safely incremented.
*   `1`: Critical validation failure, sequence jump, lazy code discovery, syntax compile error, or qualitative rejection under the 99.00 limit. Traceback written to disk and rollback executed.

---

## 3. High-Fidelity Gating Pipeline
```
[Candidate Draft Staged]
        │
        ▼
┌─────────────────────────────────┐
│ Pass 1: Programmatic Gate       │ ──(Fail)──► [Exit Code 1 / Write traceback.json]
└─────────────────────────────────┘
        │ (Success)
        ▼
┌─────────────────────────────────┐
│ Pass 1.5: Pre-Flight AST Gate   │ ──(Fail)──► [Exit Code 1 / Write traceback.json]
└─────────────────────────────────┘
        │ (Success)
        ▼
┌─────────────────────────────────┐
│ Pass 2: Qualitative Score Gate  │ ──(Fail)──► [Increment Failed Attempt Counter]
└─────────────────────────────────┘                   │
        │ (Score >= 99.00)                            ▼
        │                              ┌─────────────────────────────────────┐
        │                              │ Failed attempts >= 3?               │
        │                              └─────────────────────────────────────┘
        │                                      │ (Yes)
        │                                      ▼
        │                              ┌─────────────────────────────────────┐
        │                              │ Trigger Loop-Breaker Recovery        │
        │                              │ Propose Recursive Subphase Split     │
        │                              └─────────────────────────────────────┘
        ▼
┌─────────────────────────────────┐
│ Atomic State Database Swap      │
└─────────────────────────────────┘
        │ (Verified)
        ▼
┌─────────────────────────────────┐
│ Move Asset to /workspace/out/   │ ──► [Exit Code 0 / Release Synchronized]
└─────────────────────────────────┘
```

---

## 4. MVP Quality Gates & Assertion Coverage
To declare the Alpha milestone complete and proceed toward production, the shippable code must execute cleanly against our automated testing assertions:
*   **A01 (Determinism):** Zero dynamic package imports. Runs comfortably inside strict air-gapped runtimes using native standard libraries.
*   **A02 (Anti-Cheat):** Direct regex discovery blocks placeholder files from being promoted.
*   **A03 (Crash-Recovery):** Malformed, corrupted configuration or state databases are backed up and self-healed on initialization.
*   **A04 (Memory-Safety):** Streaming line generators maintain a flat, constant RAM overhead, securing execution during large file parsing.
*   **A05 (Loop-Breaking):** Rejection thresholds successfully break loops to recommend recursive phase divisions.
