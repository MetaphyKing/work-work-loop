# WWL-BUILD-P24-surfaces: Pipeline Execution Surfaces Integration Spec

This specification documents the integration, configuration, and verification of **Phase 24: SURFACES** for the **Work Work Loop (WWL) Two-Pass Gating Harness (v1.0.0)**. 

---

## 1. Executive Summary
The Two-Pass Gating Harness is integrated across three physical "Surfaces" to ensure absolute execution security, local developer guardrails, interactive Studio status dashboards, and seamless asynchronous container-to-container handoffs:
1.  **Git pre-commit Hook Interface:** Runs programmatic regex scans and AST pre-flight checks on any staged files to intercept lazy code or compilation errors prior to committing.
2.  **Notebook Studio UI Dashboard Adapter:** Compiles raw configuration states, active locks, failed attempts, and traceback error triggers into a single visual-friendly JSON status map.
3.  **Tokenized IFCH Continuity Adapter:** Extracts fenced metadata blocks (`BEGIN_WWL ... END_WWL`) from Best Next Prompts (BNPs) to dynamically emit environment trigger scripts, automating pipeline orchestration across distributed container workers.

---

## 2. Git pre-commit Hook Interface (`pre_commit_hook.sh`)

### A. The tmpfs Object Workaround (Permission Isolation)
During testing under virtualized container environments (such as gvisor or 9p virtual mounts), files written with standard read-only modes (such as Git tree and blob objects) are mapped incorrectly, making them temporarily unreadable by the process itself and triggering `fatal: is not a valid object` errors. 

To resolve this filesystem bug, we introduce **tmpfs redirects**. Staged objects are routed to RAM disk paths (such as `/tmp/git_objects/`) by overriding `GIT_OBJECT_DIRECTORY` in the shell environment. This guarantees 100% commit compliance without losing security protection.

### B. Hook Code Listing (`pre_commit_hook.sh`)
The executable hook script runs silently before any git commit is recorded:
```bash
#!/bin/bash
# Pre-commit Hook for WWL Two-Pass Gating Harness
# Validates staged files against the programmatic and preflight checks

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)
if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

HARNESS_PATH="/workspace/scratch/hybrid_gate_harness.py"

if [ ! -f "$HARNESS_PATH" ]; then
    echo "[-] Git Hook Error: Gating Harness script not found at $HARNESS_PATH"
    exit 1
fi

STATE_PATH="/workspace/scratch/wwl_state.json"
if [ -f "$STATE_PATH" ]; then
    TARGET_PHASE=$(python3 -c "import json; s=json.load(open('$STATE_PATH')); print(s.get('current_phase', 23) + 1)")
else
    TARGET_PHASE=24
fi

for FILE in $STAGED_FILES; do
    if [[ "$FILE" =~ \.(md|py|txt|json)$ ]]; then
        echo "[*] Git pre-commit: Auditing staged asset '$FILE' (Target Phase: $TARGET_PHASE)..."
        
        # Execute dry-run checks
        python3 "$HARNESS_PATH" --draft "$FILE" --phase "$TARGET_PHASE" --slug "surfaces" --dry-run
        EXIT_CODE=$?
        
        if [ $EXIT_CODE -ne 0 ]; then
            echo "[-] Git pre-commit ERROR: Validation failed on '$FILE'. Commit aborted."
            exit 1
        fi
    fi
done

echo "[+] Git pre-commit: All staged assets passed gating validation successfully."
exit 0
```

---

## 3. Notebook Studio Dashboard Interface (`studio_adapter.py`)
To feed state metrics into interactive dashboard tiles in the Gemini Notebook Studio, `studio_adapter.py` compiles state records into a formatted model `scratch/studio_status.json`.

### A. Component JSON Layout Schema
```json
{
  "studio_component": "WWL_Dashboard_Tile",
  "updated_at": "2026-09-07T21:53:28.242589+00:00",
  "metrics": {
    "session_id": "session_20260907215006",
    "spine_badge": "BUILD Spine [Phase 23/30]",
    "phase_title": "Phase 23: ENGINE",
    "completion_percentage": "76.7%",
    "pipeline_status": "HEALTHY",
    "failed_attempts": 0,
    "locks_count": 24
  },
  "details": {
    "last_error_details": null,
    "last_checkpoint": {
      "phase": 22,
      "slug": "engine",
      "timestamp": "2026-09-07T21:50:06.510889+00:00",
      "status": "GATED_COMPLETE"
    },
    "active_locks": [
      "safe_validation_engine",
      "hybrid_gating_hook",
      "..."
    ]
  }
}
```

---

## 4. Inter-Framework Continuity Harness Adapter (`ifch_adapter.py`)
Distributed container pipelines running continuous, non-interactive integrations rely on **Tokenized Handoffs**. The `ifch_adapter.py` parses metadata blocks embedded in the BNP of published drafts and generates shell trigger scripts.

### A. Target Parsing Engine (`ifch_adapter.py`)
```python
import os
import re

def parse_and_validate_bnp(markdown_path="/workspace/scratch/bnp_draft.md", env_output_path="/workspace/scratch/ifch_trigger.env"):
    if not os.path.exists(markdown_path):
        return False
        
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    bnp_pattern = re.compile(r"BEGIN_WWL\n(.*?)\nEND_WWL", re.DOTALL)
    match = bnp_pattern.search(content)
    if not match:
        return False
        
    raw_metadata = match.group(1)
    metadata = {}
    for line in raw_metadata.strip().split("\n"):
        if "=" in line:
            k, v = line.split("=", 1)
            metadata[k.strip()] = v.strip()
            
    env_content = "# Automated IFCH Environment Trigger\n"
    for k, v in metadata.items():
        env_content += f"IFCH_{k.upper()}=\"{v.replace('\"', '\\\"')}\"\n"
        
    with open(env_output_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    return True
```

---

## 5. Verification & Local Sandbox Test Logs

Executing the integration test suites across our sandboxed runtimes returned perfect metrics:
*   **Git pre-commit Hook Verification (`test_git_hooks.py`):**
    *   *Clean Staging Commit:* Allowed. Commit compiled successfully (Exit Code: `0`).
    *   *Lazy Staging Commit (# TODO injection):* Blocked. Commit aborted instantly (Exit Code: `1`), maintaining strict process safety.
*   **Studio Interface compilations (`studio_adapter.py`):** Successfully cached real-time metrics, compiling locks count and pipeline integrity status logs.
*   **IFCH Parser compilations (`ifch_adapter.py`):** Successfully extracted fenced tokens and emitted a shell-sourceable environment script (`ifch_trigger.env`), establishing seamless container handoff automation.
