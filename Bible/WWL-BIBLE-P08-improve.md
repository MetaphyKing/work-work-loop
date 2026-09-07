# WWL-BIBLE-P08-improve: Hardened Two-Pass Peer Gating Harness Spec

This specification represents **Version 2.0.0** of the **Two-Pass Peer Gating Harness (`hybrid_gate_harness.py`)**. It hardens the Phase 07 design specification against runtime crashes, state corruption, and the critical "Scoring Death-Loop" identified in BIBLE Phase 03.

---

## 1. Upgraded System Architecture (With Pass 1.5 & Loop-Breaker)

The gating pipeline is reinforced with a pre-flight parser and a loop-breaking mechanism:

```
+------------------------------------+
|       Private Workspace            |
|     (/workspace/scratch/)          |
+-----------------+------------------+
                  |
                  | [Writes Draft]
                  v
+-----------------+------------------+
|    Two-Pass Peer Gating Harness    |
|   (hybrid_gate_harness.py)         |
|                                    |
|   +----------------------------+   |
|   |  Pass 1: Programmatic Gate |   |
|   |  - JSON Schema Check       |   |
|   |  - Metadata & BNP Check    |   |
|   +--------------+-------------+   |
|                  | [Passes]        |
|                  v                 |
|   +--------------+-------------+   |
|   | Pass 1.5: Pre-Flight Gate  |   |
|   |  - Syntactic Compile Check |   |
|   |  - Size & Token Limits Check|  |
|   +--------------+-------------+   |
|                  | [Passes]        |
|                  v                 |
|   +--------------+-------------+   |
|   |  Pass 2: Qualitative Critic |<-- [Check failed_attempts_count < 3]
|   |  - LLM Self-Scoring (S1-S6)|   |
|   +--------------+-------------+   |
|                  |                 |
|                  | [Combined Score |
|                  |  S1-S6 < 99]    |
|                  +-----------------+---> Increment failed_attempts_count
|                                          If count >= 3: Trigger Loop-Breaker
+------------------|-----------------+
                   | [Passes (Score >= 99)]
                   v
+------------------+-----------------+
|         Public Outbox              |
|      (/workspace/out/)             |
+------------------------------------+
```

---

## 2. Hardened State Schema (`wwl_state.json`)

The state schema has been updated to track failure metrics and transaction checkpoints:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WWL_State_v2",
  "type": "object",
  "properties": {
    "version": { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "session_id": { "type": "string" },
    "active_spine": { "type": "string", "enum": ["BIBLE", "BUILD"] },
    "current_phase": { "type": "integer", "minimum": 1, "maximum": 30 },
    "failed_attempts_count": { "type": "integer", "minimum": 0, "default": 0 },
    "rollback_checkpoint_path": { "type": "string" },
    "locks": {
      "type": "array",
      "items": { "type": "string" }
    },
    "history": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "phase": { "type": "integer" },
          "slug": { "type": "string" },
          "timestamp": { "type": "string", "format": "date-time" },
          "artifact_path": { "type": "string" },
          "status": { "type": "string", "enum": ["GATED_COMPLETE", "SPLIT"] }
        },
        "required": ["phase", "slug", "timestamp", "artifact_path", "status"]
      }
    }
  },
  "required": ["version", "session_id", "active_spine", "current_phase", "failed_attempts_count", "rollback_checkpoint_path", "locks", "history"]
}
```

---

## 3. High-Value Hardening Protocols

### A. The Scoring Loop-Breaker (Mitigating Phase 03 Vulnerability)
*   **Trigger:** If the Qualitative Critic (Pass 2) fails to return a score \\( \ge 99 \\) for three consecutive execution cycles, the system increments `failed_attempts_count` to `3`.
*   **Action (Breakout Routine):** The harness immediately locks the outbox and prevents further LLM self-criticism queries. It writes a **Loop Breakout Alert** to the workspace and executes one of two paths:
    1.  **Programmatic Split (Law 5):** Automatically divides the current phase into sub-components (e.g., Phase \\(8a\\), \\(8b\\)), logging the subphase states to `wwl_state.json` to reduce cognitive load.
    2.  **Operator Intervention Gate:** Suspends execution, halts the state-machine, and outputs a structured diagnostics report to the human, requiring a manual override parameter to reset the counter.

### B. Transactional State renascent (Atomic Write Protocol)
To eliminate state corruption during file-write exceptions or process interruptions:
1.  **Write Stage:** State mutations are written strictly to a temporary shadow file: `wwl_state.json.tmp`.
2.  **Verify Stage:** The validator reads `wwl_state.json.tmp` and checks schema compliance.
3.  **Atomic Swap:** If valid, the system executes an atomic OS replacement: `os.replace("wwl_state.json.tmp", "wwl_state.json")`. If the write fails or the schema is invalid, the original `wwl_state.json` remains untouched, preserving the last known stable state.

### C. Pass 1.5: Pre-Flight Syntactic & Token Gating
Before wasting execution tokens on the qualitative LLM evaluation, the programmatic harness executes these local pre-flight checks:
*   **Compile Validator:** For code files, the harness triggers localized compilers (`python -m py_compile <path>` or local JSON/YAML parsers). If a syntax error is present, the file is immediately rejected with a local traceback, bypassing the LLM step entirely.
*   **Token-Limit Guard:** The harness programmatically estimates the token length of the draft. If it exceeds \\( 90\% \\) of the active model window, the harness flags an immediate context warning and forces a Law 5 recursive split.

---

## 4. Structured Error Schema (`scratch/harness_traceback.json`)

To enable automated self-repair during the private WORK phase, errors are logged in a structured JSON format rather than plain-text:

```json
{
  "timestamp": "2026-09-07T14:13:32-07:00",
  "phase": 8,
  "failed_pass": 2,
  "failed_attempts": 2,
  "errors": [
    {
      "criteria": "S3_EVIDENCE",
      "score_assigned": 85,
      "rejection_reason": "Claim in section 3.A regarding 'zero token cost' is ungrounded in knowledge source documents. No source passage mentions zero-cost qualitative validations.",
      "suggested_fix": "Annotate section 3.A with [UNGROUNDED] tag or remove the zero-cost assertion."
    }
  ],
  "remediation_ready": true
}
```
