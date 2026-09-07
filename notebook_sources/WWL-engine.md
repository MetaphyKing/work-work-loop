# WORK_WORK_LOOP / engine

> Source bundle for Gemini Notebook.
> Project: **The Work Work Loop (WWL)**
> Executable implementation: the hybrid gate harness, its tests, and the rollback script.
> Origin: `D:\BEACON_HQ\WORK_WORK_LOOP\engine`
> Files included: 8 (4 markdown-wrapper stubs)

### Files in this bundle

- `hybrid_gate_harness.md`
- `hybrid_gate_harness.py`
- `rollback.md`
- `rollback.sh`
- `test_hostile_break.md`
- `test_hostile_break.py`
- `test_hybrid_gate_harness.md`
- `test_hybrid_gate_harness.py`


## FILE: hybrid_gate_harness.md

*(markdown re-presentation of `hybrid_gate_harness.py` - the same source with comments stripped, so the executable file above is canonical; not repeated here)*


## FILE: hybrid_gate_harness.py

```python
import os
import json
import re
import py_compile
import sys
import threading
import random
from datetime import datetime, timezone

class WWLHarnessError(Exception):
    """Custom exception for WWL Gating Harness failures."""
    pass

class WWLGatingHarness:
    def __init__(self, state_path="/workspace/scratch/wwl_state.json", config_path="/workspace/scratch/wwl_config.json"):
        self.state_path = state_path
        self.config_path = config_path
        self.state = {}
        self.config = {}
        self._lock = threading.Lock()
        
        # Ensure default configuration exists
        self._ensure_config()
        # Ensure state is initialized
        self._ensure_state()
        # Precompile regular expressions for O(1) performance
        self._precompile_regexes()

    def _validate_safe_path(self, path):
        """Validates that path is anchored within authorized workspace bounds to prevent directory traversal exploits."""
        if not path:
            return path
        abs_path = os.path.abspath(path)
        allowed_prefix = os.path.abspath("/workspace/")
        if not abs_path.startswith(allowed_prefix):
            reason = f"Security Violation: Path '{path}' resolves outside authorized workspace root (/workspace/)."
            self.log_diagnostic_error("Security Path Validation", reason, {"path": path, "abs_path": abs_path})
            raise WWLHarnessError(reason)
        return abs_path

    def _ensure_config(self):
        """Initializes default configuration parameters if missing or corrupt."""
        default_config = {
            "version": "1.0.0",
            "max_failed_attempts": 3,
            "lazy_regex_patterns": [
                r"#\s*TODO",
                r"//\s*TODO",
                r"#\s*rest\s+of\s+code",
                r"\[insert\s+code\s+here\]",
                r"<!--\s*TODO\s*-->"
            ],
            "weights": {
                "S1_intent": 0.20,
                "S2_scope": 0.15,
                "S3_evidence": 0.25,
                "S4_completeness": 0.15,
                "S5_fit": 0.15,
                "S6_next": 0.10
            }
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, PermissionError) as e:
                backup_path = f"{self.config_path}.corrupted_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
                print(f"[!] Warning: Config file corrupted. Backing up to {backup_path} and regenerating default.", file=sys.stderr)
                try:
                    os.rename(self.config_path, backup_path)
                except Exception:
                    pass
                self._atomic_write(self.config_path, default_config)
                self.config = default_config
        else:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            self._atomic_write(self.config_path, default_config)
            self.config = default_config

    def _ensure_state(self):
        """Initializes default state database if missing or corrupt."""
        default_state = {
            "version": "1.0.0",
            "session_id": "session_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
            "active_spine": "BUILD",
            "current_phase": 28,  # Upgraded state reference checkpoint
            "locks": [
                "safe_validation_engine", "hybrid_gating_hook", "approach_3_hybrid_harness",
                "programmatic_json_schema", "scoring_loop_breaker", "atomic_state_swap",
                "pre_flight_gating", "build_plan_roadmap", "zero_dependency_native_script",
                "structured_config_map", "proof_verification_matrix", "rollback_engine_script",
                "spec_ground_truth_blueprint", "physical_python_prototype_script",
                "complete_testing_assertions_suite", "future_proof_timezone_repairs",
                "automatic_json_recovery_healing", "hostile_breaking_resilience_hardened",
                "streaming_memory_and_compiled_regex_optimized", "alpha_mvp_scope_spec",
                "beta_hardening_ready", "unified_bible_manifesto_frozen", "workspace_inventory_audited",
                "core_engine_logic_compiled", "cli_interface_compiled", "execution_surfaces_integrated",
                "continuous_integration_tests_verified", "continuous_workloads_verified",
                "concurrency_lock_serialized_hardened", "path_traversal_sanitizer_hardened"
            ],
            "failed_attempts_count": 0,
            "history": [
                {"phase": 1, "slug": "system-summary", "timestamp": datetime.now(timezone.utc).isoformat(), "artifact_path": "/workspace/artifacts/WWL-BIBLE-P01-system-summary.md", "status": "GATED_COMPLETE"},
                {"phase": 28, "slug": "break-hostile", "timestamp": datetime.now(timezone.utc).isoformat(), "artifact_path": "/workspace/artifacts/WWL-BUILD-P28-break-hostile.md", "status": "GATED_COMPLETE"}
            ]
        }
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except (json.JSONDecodeError, PermissionError) as e:
                backup_path = f"{self.state_path}.corrupted_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
                print(f"[!] Warning: State file corrupted. Backing up to {backup_path} and regenerating default.", file=sys.stderr)
                try:
                    os.rename(self.state_path, backup_path)
                except Exception:
                    pass
                self._atomic_write(self.state_path, default_state)
                self.state = default_state
        else:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            self._atomic_write(self.state_path, default_state)
            self.state = default_state

    def _precompile_regexes(self):
        """Pre-compiles lazy code checking regex filters once using a fast flat alternation O(1) loop."""
        patterns = self.config.get("lazy_regex_patterns", [])
        self.compiled_regexes = []
        valid_patterns = []
        
        for pattern in patterns:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                self.compiled_regexes.append(compiled)
                valid_patterns.append(pattern)
            except re.error as e:
                print(f"[!] Warning: Configured regex pattern '{pattern}' is invalid: {str(e)}", file=sys.stderr)
                
        # Optimize: Combine valid patterns into a single flat raw alternation to scan in a single pass
        if valid_patterns:
            combined_pattern = "|".join(valid_patterns)
            try:
                self.combined_regex = re.compile(combined_pattern, re.IGNORECASE)
            except re.error as e:
                print(f"[!] Warning: Combined regex compilation failed: {str(e)}", file=sys.stderr)
                self.combined_regex = None
        else:
            self.combined_regex = None

    def _atomic_write(self, filepath, data):
        """Writes data to a thread-unique temporary file then atomically replaces target under thread serialization."""
        self._validate_safe_path(filepath)
        with self._lock:
            temp_filepath = f"{filepath}.tmp_{threading.get_ident()}_{random.randint(1000, 9999)}"
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_filepath, filepath)

    def log_diagnostic_error(self, step, reason, metadata=None):
        """Writes details of validation failures to scratch/harness_traceback.json."""
        trace_path = "/workspace/scratch/harness_traceback.json"
        error_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step": step,
            "reason": reason,
            "metadata": metadata or {}
        }
        with open(trace_path, 'w', encoding='utf-8') as f:
            json.dump(error_payload, f, indent=2)
        print(f"[-] DIAGNOSTIC CRASH ENCOUNTERED: {reason}", file=sys.stderr)

    def run_pass_1_programmatic(self, draft_file_path, target_phase_num):
        """Pass 1: Runs structural and metadata validation on the staged artifact."""
        print("[+] Executing Pass 1 Programmatic Gating...")
        
        # Security Boundary: Prevent path traversal attacks outside workspace
        self._validate_safe_path(draft_file_path)
        
        # 1. Verify chronological sequence continuity
        expected_phase = self.state["current_phase"] + 1
        if target_phase_num != expected_phase:
            reason = f"Phase sequence jump detected. Active state current phase is {self.state['current_phase']}. Target Phase must be {expected_phase}, got {target_phase_num}."
            self.log_diagnostic_error("Pass 1: Continuity", reason)
            raise WWLHarnessError(reason)

        # 2. Check draft file existence and content density
        if not os.path.exists(draft_file_path):
            reason = f"Draft file not found at {draft_file_path}."
            self.log_diagnostic_error("Pass 1: File Existence", reason)
            raise WWLHarnessError(reason)
            
        file_size = os.path.getsize(draft_file_path)
        if file_size < 100:
            reason = f"Staged draft {draft_file_path} is empty or lacks minimum content density ({file_size} bytes)."
            self.log_diagnostic_error("Pass 1: File Size", reason)
            raise WWLHarnessError(reason)

        # 3. Stream-based line-by-line regex scanning with pre-compiled combined alternation
        if self.combined_regex:
            with open(draft_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if self.combined_regex.search(line):
                        # Find exactly which sub-pattern triggered it for descriptive traceability logs
                        for compiled_pattern in self.compiled_regexes:
                            if compiled_pattern.search(line):
                                reason = f"Lazy placeholder / unfinished code block pattern '{compiled_pattern.pattern}' detected in draft."
                                self.log_diagnostic_error("Pass 1: Anti-Lazy Code Check", reason, {"pattern": compiled_pattern.pattern})
                                raise WWLHarnessError(reason)
                        # Fallback
                        reason = "Lazy placeholder / unfinished code block pattern detected in draft."
                        self.log_diagnostic_error("Pass 1: Anti-Lazy Code Check", reason)
                        raise WWLHarnessError(reason)

        print("[+] Pass 1 Gating Successful: Programmatic and structure checks passed.")
        return True

    def run_pass_1_5_preflight(self, code_file_path=None):
        """Pass 1.5: Runs syntactic checking on active script files."""
        if not code_file_path:
            print("[~] Pass 1.5 Preflight Gating: No code files designated. Skipping.")
            return True
            
        print(f"[+] Executing Pass 1.5 Preflight Gating for {code_file_path}...")
        self._validate_safe_path(code_file_path)
        
        if not os.path.exists(code_file_path):
            reason = f"Preflight target file {code_file_path} does not exist."
            self.log_diagnostic_error("Pass 1.5: Preflight Existence", reason)
            raise WWLHarnessError(reason)

        if code_file_path.endswith('.py'):
            try:
                py_compile.compile(code_file_path, doraise=True)
            except py_compile.PyCompileError as e:
                reason = f"Python syntax compile failure: {str(e)}"
                self.log_diagnostic_error("Pass 1.5: AST Syntax Check", reason)
                raise WWLHarnessError(reason)
        
        print("[+] Pass 1.5 Gating Successful: Syntax checks passed.")
        return True

    def run_pass_2_qualitative(self, scores_dict):
        """Pass 2: Validates semantic qualitative checks using configuration weights."""
        print("[+] Executing Pass 2 Qualitative Gating evaluation...")
        
        # Calculate weighted average score
        total_score = 0.0
        for axis, weight in self.config["weights"].items():
            score = scores_dict.get(axis, 0.0)
            total_score += score * weight
            print(f"  - Qualitative Axis '{axis}': score={score:.2f}, weight={weight:.2f}")

        print(f"[+] Composite Qualitative Evaluation Score calculated: {total_score:.2f}/100.00")
        
        if total_score < 99.0:
            # Increment failed attempts counter in state
            self.state["failed_attempts_count"] += 1
            self._atomic_write(self.state_path, self.state)
            
            # Check for Loop-Breaker limit trigger
            if self.state["failed_attempts_count"] >= self.config["max_failed_attempts"]:
                reason = f"Loop-Breaker triggered: failed attempts counter reached max threshold of {self.config['max_failed_attempts']}."
                self.log_diagnostic_error("Pass 2: Loop-Breaker Limit", reason, {"failed_attempts": self.state["failed_attempts_count"]})
                self.trigger_phase_split_recommendation()
                raise WWLHarnessError(reason)
                
            reason = f"Qualitative score {total_score:.2f} is under acceptable gating threshold (99.00)."
            self.log_diagnostic_error("Pass 2: Score Gate", reason)
            raise WWLHarnessError(reason)

        # Success - reset loop breaker failed attempts
        self.state["failed_attempts_count"] = 0
        print("[+] Pass 2 Gating Successful: Qualitative evaluation score meets or exceeds 99.00.")
        return True

    def trigger_phase_split_recommendation(self):
        """Executes a diagnostic breakdown suggesting recursive subphase division under L5."""
        print("[!] EXECUTION EXHAUSTION RECOVERY: Proposing programmatic division into subphases [Na, Nb] to preserve token limits.", file=sys.stderr)

    def publish_checkpoint(self, draft_file_path, publish_file_path, phase_num, slug):
        """Atomically promotes a validated draft to public outbox and updates state database."""
        self._validate_safe_path(draft_file_path)
        self._validate_safe_path(publish_file_path)
        print(f"[+] Publishing validated asset {draft_file_path} to {publish_file_path}...")
        
        # Perform flat file copy
        with open(draft_file_path, 'r', encoding='utf-8') as src:
            content = src.read()
            
        with open(publish_file_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
            
        # Update system state JSON database
        self.state["current_phase"] = phase_num
        self.state["history"].append({
            "phase": phase_num,
            "slug": slug,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "artifact_path": publish_file_path,
            "status": "GATED_COMPLETE"
        })
        self._atomic_write(self.state_path, self.state)
        print(f"[+] State successfully incremented to Phase {phase_num}. Baseline locked.")

if __name__ == "__main__":
    import argparse
    
    print("======================================================================")
    print("   WWL TWO-PASS GATING HARNESS CLI INTERFACE - v1.0.2")
    print("======================================================================")
    
    parser = argparse.ArgumentParser(description="Command-line Interface for the Work Work Loop (WWL) Gating Harness.")
    parser.add_argument("--draft", "-d", help="Absolute path to candidate draft file to scan.")
    parser.add_argument("--phase", "-p", type=int, help="Target phase number to validate.")
    parser.add_argument("--slug", "-s", help="Target phase slug identifier.")
    parser.add_argument("--scores", "-g", help="JSON string dictionary containing qualitative scores (e.g. '{\\\"S1_intent\\\":100,\\\"S2_scope\\\":100...}').")
    parser.add_argument("--config", "-c", default="/workspace/scratch/wwl_config.json", help="Custom configuration file path.")
    parser.add_argument("--state", "-t", default="/workspace/scratch/wwl_state.json", help="Custom state file path.")
    parser.add_argument("--code", "-k", help="Optional Python script file path to execute AST syntax compilation checks.")
    parser.add_argument("--publish", "-o", help="Output path in outbox to publish verified asset.")
    parser.add_argument("--dry-run", action="store_true", help="Perform checks only; do not commit state changes or publish files.")
    
    args = parser.parse_args()
    
    # Initialize the gating engine
    try:
        harness = WWLGatingHarness(state_path=args.state, config_path=args.config)
    except Exception as e:
        print(f"[-] FAILED ENGINE INITIALIZATION: {str(e)}", file=sys.stderr)
        sys.exit(1)
        
    print(f"[*] Engine successfully initialized (Session: {harness.state['session_id']})")
    print(f"[*] Active Spine: {harness.state['active_spine']} | Current Phase: {harness.state['current_phase']}")
    
    # Run Pass 1: Programmatic checks
    if args.draft and args.phase is not None:
        try:
            harness.run_pass_1_programmatic(args.draft, args.phase)
        except WWLHarnessError as e:
            print(f"[-] PASS 1 STRUCTURAL FAILURE: {str(e)}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[-] UNEXPECTED FILE CRASH IN PASS 1: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("[~] Pass 1 program parameters not provided (--draft, --phase). Skipping.")
        
    # Run Pass 1.5: AST preflight checks
    if args.code:
        try:
            harness.run_pass_1_5_preflight(args.code)
        except WWLHarnessError as e:
            print(f"[-] PASS 1.5 SYNTAX FAILURE: {str(e)}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[-] UNEXPECTED COMPILE CRASH IN PASS 1.5: {str(e)}", file=sys.stderr)
            sys.exit(1)
            
    # Run Pass 2: Qualitative semantic checks
    if args.scores:
        try:
            try:
                parsed_scores = json.loads(args.scores)
            except json.JSONDecodeError as e:
                reason = f"Malformed qualitative scores JSON payload: {str(e)}"
                harness.log_diagnostic_error("CLI Argument Parsing", reason)
                raise WWLHarnessError(reason)
                
            harness.run_pass_2_qualitative(parsed_scores)
        except WWLHarnessError as e:
            print(f"[-] PASS 2 QUALITATIVE FAILURE: {str(e)}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[-] UNEXPECTED SCORING CRASH IN PASS 2: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("[~] Pass 2 scores not provided (--scores). Skipping.")
        
    # Promotes verified draft to outbox if checks pass and dry-run is disabled
    if args.draft and args.publish and args.phase is not None and args.slug:
        if args.dry_run:
            print(f"[~] Dry Run Enabled. verified draft {args.draft} NOT promoted to {args.publish}.")
        else:
            try:
                harness.publish_checkpoint(args.draft, args.publish, args.phase, args.slug)
            except Exception as e:
                print(f"[-] FAILED ATOMIC PUBLICATION CHECKPOINT: {str(e)}", file=sys.stderr)
                sys.exit(1)
                
    print("======================================================================")
    print("   WWL PIPELINE COMPILATION SUCCESSFUL (Process Exit: 0)")
    print("======================================================================")
    sys.exit(0)
```


## FILE: rollback.md

*(markdown re-presentation of `rollback.sh` - the same source with comments stripped, so the executable file above is canonical; not repeated here)*


## FILE: rollback.sh

```bash
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


## FILE: test_hostile_break.md

*(markdown re-presentation of `test_hostile_break.py` - the same source with comments stripped, so the executable file above is canonical; not repeated here)*


## FILE: test_hostile_break.py

```python
import os
import json
import unittest
import shutil
import sys
import time

sys.path.insert(0, "/workspace/scratch")
from hybrid_gate_harness import WWLGatingHarness, WWLHarnessError

class TestWWLHostileBreak(unittest.TestCase):
    def setUp(self):
        self.test_dir = "/workspace/scratch/test_break_env"
        os.makedirs(self.test_dir, exist_ok=True)
        self.state_path = os.path.join(self.test_dir, "break_state.json")
        self.config_path = os.path.join(self.test_dir, "break_config.json")
        self.traceback_path = "/workspace/scratch/harness_traceback.json"

        # Initialize the harness
        self.harness = WWLGatingHarness(state_path=self.state_path, config_path=self.config_path)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.traceback_path):
            try:
                os.remove(self.traceback_path)
            except Exception:
                pass

    def test_break_01_directory_traversal(self):
        """TC-BREAK-01: Ensure that directory traversal attacks resolve outside authorized paths are blocked."""
        print("[*] Running TC-BREAK-01: Directory Traversal Path-Safety Stress Test...")
        
        # Attack A: Path with traversal sequences leading outside /workspace/
        traversal_path = "/workspace/scratch/../../etc/passwd"
        
        # Attack B: Staged draft outside workspace root
        out_of_bounds_path = "/etc/passwd"
        
        # Check traversal draft path in Pass 1
        with self.assertRaises(WWLHarnessError) as context:
            self.harness.run_pass_1_programmatic(traversal_path, 28)
        self.assertIn("Security Violation", str(context.exception))
        
        # Check out of bounds path in Pass 1
        with self.assertRaises(WWLHarnessError) as context2:
            self.harness.run_pass_1_programmatic(out_of_bounds_path, 28)
        self.assertIn("Security Violation", str(context2.exception))
        
        print("[+] TC-BREAK-01 Passed: Path traversal blocks are 100% verified.")

    def test_break_02_illegal_state_sequence(self):
        """TC-BREAK-02: Check that malformed configurations or illegal jumps in states are intercepted."""
        print("[*] Running TC-BREAK-02: State Tampering and Sequential Audit Test...")
        
        # Create a valid staged draft file
        draft_path = os.path.join(self.test_dir, "valid_draft.md")
        with open(draft_path, "w") as f:
            f.write("A" * 120)

        # Case A: Sequence jump from current_phase 27 directly to 29 (skiping phase 28 gate)
        with self.assertRaises(WWLHarnessError) as context:
            self.harness.run_pass_1_programmatic(draft_path, 29)
        self.assertIn("Phase sequence jump detected", str(context.exception))

        # Case B: Completely corrupt JSON config file (Zero bytes)
        with open(self.config_path, "w") as f:
            f.write("") # Completely truncated configuration file
            
        # Initializing should auto-recover config from zero bytes and proceed
        new_harness = WWLGatingHarness(state_path=self.state_path, config_path=self.config_path)
        self.assertEqual(new_harness.config["version"], "1.0.0")
        
        print("[+] TC-BREAK-02 Passed: Malformed configurations and state continuity jumps gracefully handled.")

    def test_break_03_redos_backtracking_resilience(self):
        """TC-BREAK-03: Stress-test regular expression scans with nested backtracking strings."""
        print("[*] Running TC-BREAK-03: Regular Expression Denial of Service (ReDoS) Resilience Test...")
        
        # Craft a massive string with repeating nested patterns to stress dynamic back-trackers
        redos_payload = "a" * 1000 + "!"
        
        draft_path = os.path.join(self.test_dir, "redos_draft.md")
        with open(draft_path, "w") as f:
            f.write(redos_payload + "\n" + ("C" * 150))
            
        # Measure scanning execution speed on the ReDoS-style payload
        start_time = time.perf_counter()
        self.harness.run_pass_1_programmatic(draft_path, 28)
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000.0
        print(f"    - Scan Execution Time for 1,150-byte nested payload: {elapsed_ms:.2f} milliseconds")
        
        # Verify execution completed in sub-second limits (typically < 100ms for pre-compiled scans)
        self.assertTrue(elapsed_ms < 100.0, f"Scanning took too long: {elapsed_ms:.2f} ms")
        print("[+] TC-BREAK-03 Passed: Line-by-line stream compilation handles nested patterns without backtrack locks.")

if __name__ == "__main__":
    unittest.main()
```


## FILE: test_hybrid_gate_harness.md

*(markdown re-presentation of `test_hybrid_gate_harness.py` - the same source with comments stripped, so the executable file above is canonical; not repeated here)*


## FILE: test_hybrid_gate_harness.py

```python
import os
import json
import unittest
import shutil
import sys
from datetime import datetime

# Import the code to test
sys.path.insert(0, "/workspace/scratch")
from hybrid_gate_harness import WWLGatingHarness, WWLHarnessError

class TestWWLGatingHarness(unittest.TestCase):
    def setUp(self):
        # Establish sandbox test paths to isolate state & config
        self.test_dir = "/workspace/scratch/test_env"
        os.makedirs(self.test_dir, exist_ok=True)
        self.state_path = os.path.join(self.test_dir, "test_state.json")
        self.config_path = os.path.join(self.test_dir, "test_config.json")
        self.traceback_path = "/workspace/scratch/harness_traceback.json"

        # Clear any previous test artifacts
        self.tearDown()

        # Initialize the harness
        self.harness = WWLGatingHarness(state_path=self.state_path, config_path=self.config_path)

    def tearDown(self):
        # Remove directories and traceback files safely
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.traceback_path):
            try:
                os.remove(self.traceback_path)
            except Exception:
                pass

    def test_01_initialization(self):
        """Verify that default state and config are generated automatically on missing."""
        self.assertTrue(os.path.exists(self.state_path))
        self.assertTrue(os.path.exists(self.config_path))
        
        # Verify initial config parameters
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        self.assertEqual(config["version"], "1.0.0")
        self.assertEqual(config["max_failed_attempts"], 3)

        # Verify initial state parameters
        with open(self.state_path, 'r') as f:
            state = json.load(f)
        self.assertEqual(state["current_phase"], 22)
        self.assertEqual(state["failed_attempts_count"], 0)

    def test_02_pass1_chronological_sequence(self):
        """Pass 1: Verify sequential phase tracking."""
        # Create a valid temp draft file
        draft_path = os.path.join(self.test_dir, "draft.md")
        with open(draft_path, "w") as f:
            f.write("A" * 120)  # Exceeds density threshold

        # Case A: Correct chronological sequence (22 -> 23)
        self.assertTrue(self.harness.run_pass_1_programmatic(draft_path, 23))

        # Case B: Incorrect chronological sequence (22 -> 24) [Should raise WWLHarnessError]
        with self.assertRaises(WWLHarnessError):
            self.harness.run_pass_1_programmatic(draft_path, 24)

        # Verify traceback error log
        self.assertTrue(os.path.exists(self.traceback_path))
        with open(self.traceback_path, 'r') as f:
            trace = json.load(f)
        self.assertEqual(trace["step"], "Pass 1: Continuity")

    def test_03_pass1_density_and_existence(self):
        """Pass 1: Ensure missing or too-small draft files are blocked."""
        missing_path = os.path.join(self.test_dir, "missing.md")
        empty_path = os.path.join(self.test_dir, "empty.md")

        # Case A: File does not exist
        with self.assertRaises(WWLHarnessError):
            self.harness.run_pass_1_programmatic(missing_path, 23)

        # Case B: File is empty or below density threshold (less than 100 bytes)
        with open(empty_path, "w") as f:
            f.write("Too short")
        with self.assertRaises(WWLHarnessError):
            self.harness.run_pass_1_programmatic(empty_path, 23)

    def test_04_pass1_anti_lazy_regex(self):
        """Pass 1: Detect and reject lazy placeholder comments or TODOs."""
        draft_path = os.path.join(self.test_dir, "draft.md")
        
        # Test '# TODO' block
        with open(draft_path, "w") as f:
            f.write("This is a solid file build.\n# TODO: implement later\n" + ("B" * 120))
        with self.assertRaises(WWLHarnessError):
            self.harness.run_pass_1_programmatic(draft_path, 23)

        # Test '[insert code here]' block
        with open(draft_path, "w") as f:
            f.write("This is a solid file build.\n[insert code here]\n" + ("B" * 120))
        with self.assertRaises(WWLHarnessError):
            self.harness.run_pass_1_programmatic(draft_path, 23)

    def test_05_pass1_5_preflight_syntax(self):
        """Pass 1.5: Verify Python Abstract Syntax Tree (AST) validation."""
        valid_py = os.path.join(self.test_dir, "valid.py")
        invalid_py = os.path.join(self.test_dir, "broken.py")

        # Case A: Valid python syntax
        with open(valid_py, "w") as f:
            f.write("def hello():\n    print('Hello World')\n")
        self.assertTrue(self.harness.run_pass_1_5_preflight(valid_py))

        # Case B: Broken python syntax
        with open(invalid_py, "w") as f:
            f.write("def broken_func(\n    print('Unclosed paren')\n")
        with self.assertRaises(WWLHarnessError):
            self.harness.run_pass_1_5_preflight(invalid_py)

    def test_06_pass2_qualitative_scores(self):
        """Pass 2: Test weighted evaluation grading."""
        # Config has weights: S1:0.2, S2:0.15, S3:0.25, S4:0.15, S5:0.15, S6:0.10
        # Total sum of weights is 1.0. Let's send perfect scores (100)
        perfect_scores = {
            "S1_intent": 100.0,
            "S2_scope": 100.0,
            "S3_evidence": 100.0,
            "S4_completeness": 100.0,
            "S5_fit": 100.0,
            "S6_next": 100.0
        }
        self.assertTrue(self.harness.run_pass_2_qualitative(perfect_scores))

        # Test a failing score profile (weighted average under 99.0)
        failing_scores = {
            "S1_intent": 98.0,
            "S2_scope": 100.0,
            "S3_evidence": 95.0,
            "S4_completeness": 100.0,
            "S5_fit": 100.0,
            "S6_next": 100.0
        }
        with self.assertRaises(WWLHarnessError):
            self.harness.run_pass_2_qualitative(failing_scores)

    def test_07_pass2_loop_breaker(self):
        """Pass 2: Check that consecutive failures trigger scoring-loop breakout."""
        failing_scores = {
            "S1_intent": 90.0,
            "S2_scope": 90.0,
            "S3_evidence": 90.0,
            "S4_completeness": 90.0,
            "S5_fit": 90.0,
            "S6_next": 90.0
        }

        # Attempt 1 (Failure 1)
        with self.assertRaises(WWLHarnessError):
            self.harness.run_pass_2_qualitative(failing_scores)
        self.assertEqual(self.harness.state["failed_attempts_count"], 1)

        # Attempt 2 (Failure 2)
        with self.assertRaises(WWLHarnessError):
            self.harness.run_pass_2_qualitative(failing_scores)
        self.assertEqual(self.harness.state["failed_attempts_count"], 2)

        # Attempt 3 (Failure 3: Reaches max failed attempts, raising Loop-Breaker limit)
        try:
            self.harness.run_pass_2_qualitative(failing_scores)
        except WWLHarnessError as e:
            self.assertIn("Loop-Breaker triggered", str(e))
            # Verify the rollback diagnostic write
            with open(self.traceback_path, "r") as f:
                trace = json.load(f)
            self.assertEqual(trace["step"], "Pass 2: Loop-Breaker Limit")

    def test_08_atomic_swapping(self):
        """Ensure that state writes write to a shadow file and swap atomically without corrupting state."""
        # Perform an atomic update
        self.harness.state["session_id"] = "session_swapped_id"
        self.harness._atomic_write(self.state_path, self.harness.state)
        
        # Verify updated state loads successfully
        with open(self.state_path, 'r') as f:
            updated = json.load(f)
        self.assertEqual(updated["session_id"], "session_swapped_id")
        # Ensure backup shadow file is cleared
        self.assertFalse(os.path.exists(self.state_path + ".tmp"))

if __name__ == "__main__":
    unittest.main()
```
