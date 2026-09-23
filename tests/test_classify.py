import unittest

from wwl_phase.classify import classify
from wwl_phase.scores import validate_scores

VALID_SCORES = {
    "S1_intent": 100,
    "S2_scope": 100,
    "S3_evidence": 100,
    "S4_completeness": 100,
    "S5_fit": 100,
    "S6_next": 100,
}


class ClassifyTests(unittest.TestCase):
    def test_valid_exit(self):
        dry = classify(0, "Dry Run Enabled\nPIPELINE COMPILATION SUCCESSFUL", dry_run=True)
        self.assertTrue(dry["success"])
        self.assertEqual(dry["action"], "dry_run")
        published = classify(0, "PIPELINE COMPILATION SUCCESSFUL", dry_run=False)
        self.assertEqual(published["action"], "publish")

    def test_malformed_harness_text(self):
        sequence = classify(1, "Phase sequence jump detected. got 3.")
        self.assertEqual(sequence["action"], "stop")
        self.assertFalse(sequence["retryable"])
        score = classify(1, "Qualitative score 40.00 is under acceptable gating threshold (99.00).")
        self.assertEqual(score["action"], "rewrite")
        self.assertTrue(score["retryable"])
        lazy = classify(1, "Lazy placeholder / unfinished code block pattern detected")
        self.assertEqual(lazy["action"], "rewrite")
        split = classify(1, "Loop-Breaker triggered: failed attempts counter reached max threshold of 3.")
        self.assertEqual(split["action"], "split")
        self.assertFalse(split["retryable"])

    def test_empty_and_security(self):
        empty = classify(1, "")
        self.assertFalse(empty["success"])
        self.assertEqual(empty["action"], "stop")
        outside = classify(1, "Security Violation: Path 'C:\\tmp\\x' resolves outside authorized workspace root.")
        self.assertEqual(outside["action"], "stop")
        missing = validate_scores({})
        self.assertTrue(missing["retryable"])
        noisy = validate_scores({"S1_intent": "high"})
        self.assertIn("missing", noisy["error"])
        self.assertIsNone(validate_scores(VALID_SCORES))
