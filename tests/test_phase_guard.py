import unittest

from wwl_phase.phase_guard import phase_allowed


def history(*phases):
    return [{"phase": phase, "status": "GATED_COMPLETE", "slug": "x"} for phase in phases]


class PhaseGuardTests(unittest.TestCase):
    def test_valid_first_phase(self):
        result = phase_allowed({"current_phase": 0, "history": []}, 1, "BIBLE")
        self.assertTrue(result["success"])
        self.assertEqual(result["slug"], "system-summary")
        self.assertEqual(result["artifact"], "WWL-BIBLE-P01-system-summary.md")
        self.assertEqual(result["mode"], "work")

    def test_malformed_skip_and_jump(self):
        noisy = phase_allowed({"current_phase": 0, "history": []}, "next", "BIBLE")
        self.assertFalse(noisy["success"])
        self.assertFalse(noisy["retryable"])
        jump = phase_allowed({"current_phase": 1, "history": history(1)}, 3, "BIBLE")
        self.assertIn("sequence jump", jump["error"])
        self.assertEqual(jump["action"], "stop")
        blank = phase_allowed({"current_phase": 4, "history": history(1, 2, 3, 4)}, 5, "BIBLE", skip_reason="  ")
        self.assertIn("SKIP_REASON", blank["error"])

    def test_empty_state_and_locked_bible(self):
        fresh = phase_allowed(None, 1, "BIBLE")
        self.assertTrue(fresh["success"])
        locked = phase_allowed(
            {"current_phase": 20, "active_spine": "BIBLE", "history": history(20)},
            1,
            "BIBLE",
        )
        self.assertIn("L9", locked["error"])
        build = phase_allowed(
            {"current_phase": 20, "history": history(20)},
            21,
            "BUILD",
        )
        self.assertTrue(build["success"])
        self.assertEqual(build["slug"], "inventory")
        early = phase_allowed({"current_phase": 4, "history": history(1, 2, 3, 4)}, 5, "BUILD")
        self.assertFalse(early["success"])
