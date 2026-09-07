# Hybrid Gate Harness - Test

---

Python

```
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