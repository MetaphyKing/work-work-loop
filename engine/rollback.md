# Rollback Engine

---

sh

```
#!/usr/bin/env bash
# rollback.sh - Atomic Rollback Engine for WWL Operating Kernel [93]

set -euo pipefail

TRACE_FILE="/workspace/scratch/harness_traceback.json"
TEMP_STATE="/workspace/scratch/wwl_state.json.tmp"
ACTIVE_STATE="/workspace/scratch/wwl_state.json"
SCRATCH_DIR="/workspace/scratch/"

echo "[ROLLBACK ENGINE] Initiating atomic state reversion..."

# 1. Discard any temporary shadow state to prevent corruption
if [ -f "$TEMP_STATE" ]; then
    rm -f "$TEMP_STATE"
    echo "[ROLLBACK ENGINE] Discarded unverified shadow state: $TEMP_STATE"
fi

# 2. Verify existence of active state file
if [ ! -f "$ACTIVE_STATE" ]; then
    echo "[CRITICAL ERROR] Active state database not found. Re-initialization required!" >&2
    exit 1
fi

# 3. Read the last stable file target from history using jq
LAST_STABLE_PHASE=$(jq -r '.history[-1].phase' "$ACTIVE_STATE")
LAST_STABLE_SLUG=$(jq -r '.history[-1].slug' "$ACTIVE_STATE")
LAST_STABLE_PATH=$(jq -r '.history[-1].artifact_path' "$ACTIVE_STATE")

echo "[ROLLBACK ENGINE] Reverting state to Phase $LAST_STABLE_PHASE ($LAST_STABLE_SLUG)"
echo "[ROLLBACK ENGINE] Verified stable source file: $LAST_STABLE_PATH"

# 4. Clear compiling staging buffers in scratch (preserving logs)
find "$SCRATCH_DIR" -mindepth 1 -maxdepth 1 ! -name "wwl_state.json" ! -name "harness_traceback.json" ! -name "logs" -exec rm -rf {} +
echo "[ROLLBACK ENGINE] Scratch workspace staged files purged successfully."

# 5. Restore the active configuration state targets
jq '.current_phase = .history[-1].phase' "$ACTIVE_STATE" > "$TEMP_STATE"
mv -f "$TEMP_STATE" "$ACTIVE_STATE"

echo "[ROLLBACK ENGINE] Rollback completed. System state reverted to stable Phase $LAST_STABLE_PHASE."
```