import unittest

from wwl_phase.parse_start import parse_prompt

VALID = """WWL/1.1.0
[IDEA] Build a doorbell that names the caller.
[LOCKS] no new runtime
[SPINE] BIBLE
[TASK] Execute the spine one phase at a time.
[NEXT] Proceed Phase 01 IDEA
"""

NOISY = """please start this when you can
WWL/1.1.0
[IDEA] Build a doorbell that names the caller.
random aside that stays inside the idea
[LOCKS] none
[SPINE] BIBLE
thanks!
"""


class ParseStartTests(unittest.TestCase):
    def test_valid_card(self):
        result = parse_prompt(VALID)
        self.assertTrue(result["success"])
        self.assertEqual(result["action"], "start")
        self.assertEqual(result["idea"], "Build a doorbell that names the caller.")
        self.assertEqual(result["locks"], ["no new runtime"])
        self.assertEqual(result["spine"], "BIBLE")
        self.assertEqual(result["version"], "1.1.0")

    def test_noisy_card_keeps_idea(self):
        result = parse_prompt(NOISY)
        self.assertTrue(result["success"])
        self.assertIn("random aside", result["idea"])
        self.assertEqual(result["locks"], [])

    def test_malformed_spine(self):
        result = parse_prompt("WWL/1.1.0\n[IDEA] A thing\n[SPINE] MAYBE\n")
        self.assertFalse(result["success"])
        self.assertFalse(result["retryable"])
        self.assertIn("spine", result["error"])

    def test_empty_and_bare_tokens(self):
        empty = parse_prompt("   ")
        self.assertFalse(empty["success"])
        self.assertEqual(empty["error"], "empty prompt")
        self.assertEqual(parse_prompt("continue")["action"], "continue")
        self.assertEqual(parse_prompt("STOP")["action"], "stop")
        self.assertFalse(parse_prompt("continue please")["success"])
        self.assertFalse(parse_prompt(None)["success"])
