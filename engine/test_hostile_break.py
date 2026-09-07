import os
import json
import unittest
import shutil
import sys
import time
import tempfile

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ENGINE_DIR)
from hybrid_gate_harness import WWLGatingHarness, WWLHarnessError

class TestWWLHostileBreak(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="wwl_break_")
        os.environ["WWL_ROOT"] = self.test_dir
        self.state_path = os.path.join(self.test_dir, "break_state.json")
        self.config_path = os.path.join(self.test_dir, "break_config.json")
        self.traceback_path = os.path.join(self.test_dir, "harness_traceback.json")
        self.harness = WWLGatingHarness(state_path=self.state_path, config_path=self.config_path)
        self.harness.state["current_phase"] = 27
        self.harness._atomic_write(self.state_path, self.harness.state)

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
        
        traversal_path = os.path.join(self.test_dir, os.pardir, os.pardir, "etc", "passwd")
        
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
        self.harness.run_pass_1_programmatic(draft_path, 28)  # current_phase 27 → expected 28
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000.0
        print(f"    - Scan Execution Time for 1,150-byte nested payload: {elapsed_ms:.2f} milliseconds")
        
        # Verify execution completed in sub-second limits (typically < 100ms for pre-compiled scans)
        self.assertTrue(elapsed_ms < 100.0, f"Scanning took too long: {elapsed_ms:.2f} ms")
        print("[+] TC-BREAK-03 Passed: Line-by-line stream compilation handles nested patterns without backtrack locks.")

if __name__ == "__main__":
    unittest.main()
