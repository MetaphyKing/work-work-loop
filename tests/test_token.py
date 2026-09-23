import unittest

from wwl_phase.token import close_phase, normalize_token_count, parse_locks, render_token


class TokenTests(unittest.TestCase):
    def test_lock_profiles(self):
        self.assertEqual(parse_locks("no new runtime, python helper"), ["no new runtime", "python helper"])
        self.assertEqual(parse_locks('["safe", "bold"]'), ["safe", "bold"])
        self.assertEqual(parse_locks("none"), [])
        self.assertEqual(parse_locks(""), [])
        self.assertEqual(parse_locks(None), [])
        self.assertEqual(parse_locks("not-json ["), ["not-json ["])

    def test_valid_token_omits_wake(self):
        result = render_token("BIBLE", 2, 20, ["no new runtime"], 10, 4)
        self.assertTrue(result["success"])
        self.assertIn("tokens_in=10", result["text"])
        self.assertIn("proceed=Proceed Phase 2", result["text"])
        self.assertNotIn("wake=", result["text"])
        self.assertTrue(result["text"].endswith("END_WWL"))

    def test_noisy_count_is_rejected(self):
        result = normalize_token_count("about 12")
        self.assertFalse(result["success"])
        self.assertFalse(result["retryable"])
        self.assertFalse(render_token("BIBLE", 2, 20, [], "1e3", 1)["success"])
        self.assertFalse(normalize_token_count(1.5)["success"])

    def test_empty_count_is_unknown_and_phase_30_unloads(self):
        self.assertEqual(normalize_token_count(None), "UNKNOWN")
        self.assertEqual(normalize_token_count(""), "UNKNOWN")
        closed = close_phase(1, "BIBLE", [], None, None)
        self.assertEqual(
            closed["gate_line"],
            "Phase 1 of 20. Prompt continue to proceed to the next phase.",
        )
        self.assertIn("tokens_in=UNKNOWN", closed["token"])
        done = close_phase(30, "BUILD", [], 3, 3)
        self.assertIn("phase=UNLOAD", done["token"])
        self.assertIn("proceed=UNLOAD", done["token"])
        self.assertEqual(done["next_phase"], "UNLOAD")
