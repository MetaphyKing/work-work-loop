# WWL-BIBLE-P07-design: Two-Pass Peer Gating Harness Spec

This specification defines the formal system architecture and data schemas for **Approach 3: The Two-Pass Peer Gating Harness (`hybrid_gate_harness.py`)**. 

---

## 1. System Overview
The Two-Pass Peer Gating Harness acts as the defensive enforcement layer of the **Work Work Loop (WWL) Operating Kernel**. It sits directly between the private reasoning space (`/workspace/scratch/`) and the public publishing outbox (`/workspace/out/`).

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
|   |  Pass 2: Qualitative Critic |   |
|   |  - LLM Self-Scoring (S1-S6)|   |
|   +--------------+-------------+   |
+------------------|-----------------+
                   | [Passes (Score >= 99)]
                   v
+------------------+-----------------+
|         Public Outbox              |
|      (/workspace/out/)             |
+------------------------------------+
```

---

## 2. Pass 1: Programmatic Schema (`wwl_state.json`)
Every project governed by the WWL maintains a physical state file. The harness programmatically parses and validates this schema.

### JSON Schema Specification
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WWL_State",
  "type": "object",
  "properties": {
    "version": { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "session_id": { "type": "string" },
    "active_spine": { "type": "string", "enum": ["BIBLE", "BUILD"] },
    "current_phase": { "type": "integer", "minimum": 1, "maximum": 30 },
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
  "required": ["version", "session_id", "active_spine", "current_phase", "locks", "history"]
}
```

---

## 3. Pass 2: Qualitative Peer Critic Rules (S1-S6)
If Pass 1 succeeds, the harness invokes the Peer Critic execution prompt to run semantic evaluation.

### Core Scoring Protocol
*   **S1 INTENT [Weight: 20%]:** Semantic alignment check. The critic extracts the target intent from the current turn and runs a Cosine Similarity match against the base user intent stored in the state.
*   **S2 SCOPE [Weight: 15%]:** Out-of-bounds leakage check. Detects whether the current delivery contains code or markdown destined for future phases.
*   **S3 EVIDENCE [Weight: 25%]:** Citation and grounding audit.
    *   Every factual assertion must map to a `[i]` tag pointing back to active workspace knowledge.
    *   No external factual claims are permitted unless tagged explicitly as `[UNGROUNDED]`.
*   **S4 COMPLETENESS [Weight: 15%]:** Elements verification. Validates presence of the `Best Next Prompt` (BNP) in markdown format.
*   **S5 FIT [Weight: 15%]:** Size and structural density check. Emits warning if token ceiling is approaching \\(\ge 90\%\\), forcing a split planning cycle.
*   **S6 NEXT [Weight: 10%]:** Target phase parsing check. Verifies that the next target phase has the correct chronological index (e.g., Phase \\(N + 1\\)).

---

## 4. Operational Boundaries & Transaction Control
The harness enforces transactional file security to prevent corrupted or half-baked outputs:

1.  **Draft Staging:** The compiling agent must output its workspace deliverables strictly inside `/workspace/scratch/WWL-BIBLE-P07-design/`.
2.  **Structural Execution:** `hybrid_gate_harness.py` is invoked.
3.  **Rejection Loop (L4):** If the combined evaluation score is less than 99, the harness writes a highly descriptive trace file (`scratch/harness_traceback.log`) describing the exact criteria failure and blocks the publish sequence.
4.  **Atomic Move (Publishing):** Only when the combined score is \\( \ge 99 \\) does the harness copy the final verified artifact into the flat write-only directory `/workspace/out/`.
