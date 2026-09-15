#!/usr/bin/env bash
# rollback.sh - Atomic Rollback Engine for WWL Operating Kernel [93]

set -euo pipefail

ROOT="${WWL_ROOT:-$PWD/.wwl}"
TRACE_FILE="$ROOT/harness_traceback.json"
TEMP_STATE="$ROOT/wwl_state.json.tmp"
ACTIVE_STATE="$ROOT/wwl_state.json"
SCRATCH_DIR="$ROOT/"

echo "[ROLLBACK ENGINE] Initiating atomic state reversion..."

# S2 Protection: Require .wwl-scratch marker file
if [ ! -f "$ROOT/.wwl-scratch" ]; then
    echo "[CRITICAL ERROR] Target directory $ROOT lacks the .wwl-scratch marker file." >&2
    echo "Refusing to execute purge. Ensure this is a scratch environment and not a repository root." >&2
    exit 1
fi

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
LAST_STABLE_PHASE=$(jq -r '.history[-1].phase' "$ACTIVE_STATE" 2>/dev/null || echo "UNKNOWN")
LAST_STABLE_SLUG=$(jq -r '.history[-1].slug' "$ACTIVE_STATE" 2>/dev/null || echo "UNKNOWN")
LAST_STABLE_PATH=$(jq -r '.history[-1].artifact_path' "$ACTIVE_STATE" 2>/dev/null || echo "UNKNOWN")

echo "[ROLLBACK ENGINE] Reverting state to Phase $LAST_STABLE_PHASE ($LAST_STABLE_SLUG)"
if [ "$LAST_STABLE_PATH" != "UNKNOWN" ] && [ -f "$LAST_STABLE_PATH" ]; then
    echo "[ROLLBACK ENGINE] Verified stable source file exists: $LAST_STABLE_PATH"
fi

# 4. Clear compiling staging buffers in scratch (preserving logs, state, config, templates, and journals)
echo "[ROLLBACK ENGINE] Files targeted for deletion in $SCRATCH_DIR:"
find "$SCRATCH_DIR" -mindepth 1 -maxdepth 1 \
    ! -name "wwl_state.json" \
    ! -name "wwl_config.json" \
    ! -name "harness_traceback.json" \
    ! -name "logs" \
    ! -name ".wwl-scratch" \
    ! -name "eao.journal.sqlite3" \
    ! -name "eao.journal.sqlite3-wal" \
    ! -name "eao.journal.sqlite3-shm" \
    ! -name "ML-REPORT-TEMPLATE.md" \
    ! -path "$LAST_STABLE_PATH"

find "$SCRATCH_DIR" -mindepth 1 -maxdepth 1 \
    ! -name "wwl_state.json" \
    ! -name "wwl_config.json" \
    ! -name "harness_traceback.json" \
    ! -name "logs" \
    ! -name ".wwl-scratch" \
    ! -name "eao.journal.sqlite3" \
    ! -name "eao.journal.sqlite3-wal" \
    ! -name "eao.journal.sqlite3-shm" \
    ! -name "ML-REPORT-TEMPLATE.md" \
    ! -path "$LAST_STABLE_PATH" \
    -exec rm -rf {} +
echo "[ROLLBACK ENGINE] Scratch workspace staged files purged successfully."

# 5. Restore the active configuration state targets
if jq '.current_phase = .history[-1].phase' "$ACTIVE_STATE" > "$TEMP_STATE" 2>/dev/null; then
    mv -f "$TEMP_STATE" "$ACTIVE_STATE"
fi

echo "[ROLLBACK ENGINE] Rollback completed. System state reverted to stable Phase $LAST_STABLE_PHASE."
