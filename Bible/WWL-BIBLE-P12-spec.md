# Technical Specification: Two-Pass Peer Gating Harness Spec (WWL-BIBLE-P12-spec)
**Status:** Implementation-Ready Spec (Locked Ground Truth)  
**Spine:** BIBLE (Strategic Planning & Design)  
**Phase:** 12 SPEC  
**System Target:** Work Work Loop (WWL) Operating Kernel v1.0.0  

---

## 1. Executive Summary & Purpose
This technical specification establishes the absolute, implementation-ready ground truth blueprint for **Approach 3: The Two-Pass Peer Gating Harness (`hybrid_gate_harness.py`)**. 

As audited in Phase 02 and Phase 03, legacy agent systems fail due to attention drift, grading collusion, and state corruption. This spec resolves those flaws by implementing a dual-pass gating engine. **Pass 1 (Programmatic)** enforces absolute schema and structural integrity locally on disk. **Pass 2 (Qualitative)** invokes a stateless LLM reasoning loop to evaluate S1–S6 criteria against strict numeric thresholds. 

This document defines the class interfaces, JSON schemas, state machines, file layouts, and execution rules that the BUILD spine must implement with 100% fidelity.

---

## 2. Directory Layout & System Topology
The harness operates within a strict, air-gapped file-system sandbox, maintaining a physical boundary between volatile drafts and published production deliverables:

```
/workspace/
├── wwl_state.json                    <-- Active, authenticated loop database
├── wwl_config.json                   <-- Configuration dashboard (regexes, weights)
├── rollback.sh                       <-- Recovery script executing rollback procedures
├── artifacts/                        <-- Read-only archive of GATED_COMPLETE assets
│   └── WWL-BIBLE-P11-hundred-guarantee.md
├── scratch/                          <-- Safe sandbox zone for intermediate staging
│   └── stage_draft/                  <-- Dynamic workspace containing pending assets
│       ├── draft_delivery.txt        <-- Generated conversational response
│       └── WWL-BIBLE-P12-spec.md     <-- Generated target file artifact
└── out/                              <-- Write-only, auto-published outbox (flat file)
```

---

## 3. Data Schema Specifications

### 3.1. Physical Loop State Database (`wwl_state.json`)
This read-only file stores system metrics and historical audit logs. It must satisfy this strict JSON Schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WWL_State_Schema",
  "type": "object",
  "properties": {
    "version": { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "session_id": { "type": "string" },
    "active_spine": { "type": "string", "enum": ["BIBLE", "BUILD"] },
    "current_phase": { "type": "integer", "minimum": 1, "maximum": 30 },
    "failed_attempts_count": { "type": "integer", "minimum": 0 },
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
  "required": [
    "version",
    "session_id",
    "active_spine",
    "current_phase",
    "failed_attempts_count",
    "locks",
    "history"
  ]
}
```

### 3.2. Configuration Parameters Control Map (`wwl_config.json`)
Controls regex patterns, metrics weights, and local system parameters to preserve script zero-dependency goals:

```json
{
  "max_allowed_failures": 3,
  "scoring_threshold": 99,
  "required_placeholders_regex": [
    "(?i)#\\s*todo",
    "(?i)#\\s*placeholder",
    "(?i)\\[insert.*code\\]",
    "(?i)//\\s*todo"
  ],
  "weights": {
    "S1_INTENT": 0.20,
    "S2_SCOPE": 0.15,
    "S3_EVIDENCE": 0.25,
    "S4_COMPLETE": 0.15,
    "S5_FIT": 0.15,
    "S6_NEXT": 0.10
  }
}
```

---

## 4. Gating Pipeline State Machine
The core loop execution flow is divided into clear transactional states:

```
                  [ START PHASE RUN ]
                           │
                           ▼
              [ Pass 1: Local Disk Check ]
              - Parse active wwl_state.json
              - Validate staged directory files
              - Scan for placeholder patterns
                           │
                 ├─────────┴─────────┤
              [FAIL]              [PASS]
                 │                   ▼
                 │        [ Pass 1.5: AST Pre-Flight ]
                 │        - Local Python / JSON syntax compilations
                 │        - Compute context size and estimate token weight
                 │                   │
                 │         ├─────────┴─────────┤
                 │      [FAIL]              [PASS]
                 │         │                   ▼
                 │         │      [ Pass 2: LLM qualitative Critic ]
                 │         │      - Invoke stateless scoring loop
                 │         │      - Apply criteria weights to derive total
                 │         │                   │
                 │         │         ├─────────┴─────────┤
                 │         │      [FAIL < 99]       [PASS >= 99]
                 │         │         │                   │
                 ▼         ▼         ▼                   ▼
           [ INC failed_attempts_count ]       [ Reset failure counter ]
           - Write wwl_state.json.tmp          - Write GATED_COMPLETE history
           - Perform Atomic State Swap         - Perform Atomic State Swap
           - Trigger Rollback Engine           - Copy artifact safely to /out/
           - Output traceback JSON             - Clean stage_draft files
                           │                               │
                           ▼                               ▼
                 [ HALT & OVERRIDE ]               [ GATE MET - WAIT ]
```

---

## 5. Harness Class & API Architecture (Python 3. Standard Library Only)

The harness script `hybrid_gate_harness.py` must contain the following core structures and methods:

```python
import os
import re
import json
import sys
from typing import Dict, Any, List

class ProgrammaticGateError(Exception):
    """Custom exception raised during Pass 1 and Pass 1.5 checking."""
    pass

class WWLStateController:
    """Manages transactional disk writes and schemas for state management."""
    def __init__(self, state_path: str = "/workspace/wwl_state.json", config_path: str = "/workspace/wwl_config.json"):
        self.state_path = state_path
        self.config_path = config_path
        self.state: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {}

    def load_files(self) -> None:
        """Loads state and config files, raising errors if schema does not match."""
        pass

    def write_atomic_state(self, new_state: Dict[str, Any]) -> None:
        """Implements Atomic State Swap by writing to .tmp first and replacing."""
        tmp_path = self.state_path + ".tmp"
        with open(tmp_path, 'w') as f:
            json.dump(new_state, f, indent=2)
        os.replace(tmp_path, self.state_path)

class ProgrammaticValidator:
    """Pass 1: Runs local, non-LLM checks against files inside scratch/stage_draft."""
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def verify_files_exist(self, draft_dir: str) -> None:
        """Verifies draft_delivery.txt and target file artifact are non-empty."""
        pass

    def check_for_placeholders(self, filepath: str) -> None:
        """Applies configuration regex maps to prevent fake whole-product comments."""
        pass

    def verify_syntax(self, filepath: str) -> None:
        """Pass 1.5: Locally compiles file content to ensure syntax validity."""
        pass

class QualitativePeerCritic:
    """Pass 2: Invokes a stateless LLM prompt cycle to grade S1-S6."""
    def __init__(self, state: Dict[str, Any], config: Dict[str, Any]):
        self.state = state
        self.config = config

    def generate_evaluation_prompt(self, draft_delivery: str, artifact_content: str) -> str:
        """Generates a highly structured evaluation template for the peer critic."""
        pass

    def parse_critic_scores(self, raw_llm_output: str) -> Dict[str, float]:
        """Parses numeric grades assigned to each category (S1-S6)."""
        pass

    def calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Applies wwl_config.json weights to compute the final aggregate score."""
        pass
```

---

## 6. The Recovery, Breakout, & Rollback Routines

### 6.1. Failed Attempts Counter and Loop-Breaker (L4 & L5)
If `calculate_weighted_score` evaluates to **less than 99**, the harness executes the following recovery actions:
1.  **Read and Increment:** Increments `failed_attempts_count` in memory.
2.  **Diagnostic Dump:** Outputs a complete failure log to `/workspace/scratch/harness_traceback.json` detailing scores and suggested fixes.
3.  **Evaluate Loop Limit:**
    *   If `failed_attempts_count < 3`: The pipeline triggers a warning traceback, letting the agent read the error and self-correct during the next WORK cycle.
    *   If `failed_attempts_count == 3`: The harness **breaks execution**. It automatically initiates a Phase Split (e.g. creating `Na` and `Nb` directories) or freezes compilation, outputting a blocking traceback that requires a manual override file `/workspace/override_flag` to clear.

### 6.2. Rollback Engine Configuration (`rollback.sh`)
An executable shell script is placed in `/workspace/rollback.sh` to revert system state upon critical pipeline crashes:

```bash
#!/usr/bin/env bash
# rollback.sh: Resets system config and purges staging directories on failure

set -euo pipefail

STATE_FILE="/workspace/wwl_state.json"
STATE_TMP="/workspace/wwl_state.json.tmp"
STAGE_DIR="/workspace/scratch/stage_draft"

echo "[ROLLBACK] Initializing pipeline reversion..."

# 1. Clean up volatile staging buffers
if [ -d "$STAGE_DIR" ]; then
    echo "[ROLLBACK] Clearing staging workspace: $STAGE_DIR"
    rm -rf "${STAGE_DIR:?}"/*
fi

if [ -f "$STATE_TMP" ]; then
    echo "[ROLLBACK] Discarding temporary state draft..."
    rm -f "$STATE_TMP"
fi

# 2. Revert active state parameters to the last GATED_COMPLETE index
if [ -f "$STATE_FILE" ]; then
    echo "[ROLLBACK] Reverting active state to last stable configuration..."
    # Extracts the last completed phase from history array using jq
    LAST_STABLE=$(jq '.history[-1]' "$STATE_FILE")
    
    if [ "$LAST_STABLE" != "null" ]; then
        LAST_PHASE=$(echo "$LAST_STABLE" | jq '.phase')
        echo "[ROLLBACK] Restoring loop state to Phase $LAST_PHASE"
        # Update current active phase and reset failed count to zero
        jq --argjson p "$LAST_PHASE" '.current_phase = $p | .failed_attempts_count = 0' "$STATE_FILE" > "$STATE_TMP"
        mv "$STATE_TMP" "$STATE_FILE"
    else
        echo "[ROLLBACK] No completed phase history found. Resetting state to initial default."
        jq '.current_phase = 1 | .failed_attempts_count = 0' "$STATE_FILE" > "$STATE_TMP"
        mv "$STATE_TMP" "$STATE_FILE"
    fi
fi

echo "[ROLLBACK] Reversion complete. Ready for safe execution re-entry."
```

---

## 7. Evidence & Grounding Traceability

Every structural requirement in this spec maps directly to the unbreakable system rules established in the core documentation:
*   **Decoupled Work vs Deliver (L2):** Satisfied by staging drafts strictly within `/workspace/scratch/stage_draft/` and executing verification sweeps before copying files to `/workspace/out/` [8].
*   **Dual-Output Verification (L3):** Enforced programmatically in `ProgrammaticValidator.verify_files_exist()`, requiring both `draft_delivery.txt` and the named file artifact [30].
*   **Anti-Lazy Code Checks (L3 / S4):** The configuration regex array scans for placeholder comments to block partial code generation [31].
*   **Score Integrity Gate (L4 / S1-S6):** Enforced by Pass 2 scoring, requiring weighted aggregate grades to hit \\( \ge 99 \\) [16].
*   **Recursive Split (L5 / L7):** Executed automatically by the loop-breaker when consecutive failed attempts count reaches limit thresholds to protect against token exhaustion [15].
*   **Atomic State Swap (L11):** Satisfied by `WWLStateController.write_atomic_state()` implementing transient buffer transfers to protect against filesystem interrupts [24].

---

## 8. Completion Proof Criteria

For the BUILD spine to successfully gate and compile this harness, the completed engine must satisfy the following verifiable criteria:
*   **Unit Compilation:** Executing `python3 hybrid_gate_harness.py` with malformed inputs must return exit code `1` and raise descriptive `ProgrammaticGateError` stack traces on disk.
*   **State-Corruption Proof:** Running a mock build run and interrupting execution mid-write must leave `wwl_state.json` completely uncorrupted.
*   **Self-Healing Proof:** Running an intentional failed gate must write a parsable `scratch/harness_traceback.json` detailing scores.
*   **Loop-Breaker Proof:** Running three consecutive failed gates must trigger a phase division block or halt compilation, requiring manual overrides to resume.
*   **Rollback Integrity:** Running `bash rollback.sh` must restore `wwl_state.json` to the last completed history index and clean staged folders.
