import json
import tempfile
import unittest
from pathlib import Path

from wwl_phase.gate import path_inside, run_gate

HARNESS = Path(r"C:\dev\wwl\engine\hybrid_gate_harness.py")
SCORES = {
    "S1_intent": 100,
    "S2_scope": 100,
    "S3_evidence": 100,
    "S4_completeness": 100,
    "S5_fit": 100,
    "S6_next": 100,
}
LOW = dict(SCORES, S3_evidence=0)


def draft(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


BODY = (
    "The doorbell names the caller from the supplied lock and writes one artifact. "
    "Evidence is this sentence, the phase is IDEA, and the next card re-enters the loop.\n"
)


class GateTests(unittest.TestCase):
    def test_path_profiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inside = root / "drafts" / "a.md"
            self.assertTrue(path_inside(root, inside))
            self.assertFalse(path_inside(root, root.parent / "outside.md"))
            self.assertFalse(path_inside(root, ""))
            self.assertFalse(path_inside("", inside))

    @unittest.skipUnless(HARNESS.exists(), "local harness missing")
    def test_valid_dry_run_then_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file_path = root / "drafts" / "WWL-BIBLE-P01-system-summary.md"
            draft(file_path, BODY)
            outbox = root / "outbox"
            published = outbox / file_path.name
            dry = run_gate(root, file_path, 1, "system-summary", SCORES, publish=published, dry_run=True)
            self.assertTrue(dry["success"], dry)
            self.assertEqual(dry["action"], "dry_run")
            self.assertFalse(published.exists())
            missing_parent = run_gate(root, file_path, 1, "system-summary", SCORES, publish=published)
            self.assertFalse(missing_parent["success"])
            self.assertTrue(missing_parent["retryable"])
            self.assertEqual(missing_parent["action"], "publish")
            outbox.mkdir()
            published_ok = run_gate(root, file_path, 1, "system-summary", SCORES, publish=published)
            self.assertTrue(published_ok["success"], published_ok)
            state = json.loads((root / "wwl_state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["current_phase"], 1)
            again = run_gate(root, file_path, 1, "system-summary", SCORES, publish=published, dry_run=True)
            self.assertEqual(again["action"], "stop")

    @unittest.skipUnless(HARNESS.exists(), "local harness missing")
    def test_malformed_scores_do_not_create_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file_path = root / "drafts" / "a.md"
            draft(file_path, BODY)
            result = run_gate(root, file_path, 1, "system-summary", {"S1_intent": "high"})
            self.assertTrue(result["retryable"])
            self.assertFalse((root / "wwl_state.json").exists())

    @unittest.skipUnless(HARNESS.exists(), "local harness missing")
    def test_empty_skip_and_outside(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tiny = root / "drafts" / "tiny.md"
            draft(tiny, "too short")
            empty = run_gate(root, tiny, 1, "system-summary", SCORES, dry_run=True)
            self.assertEqual(empty["action"], "rewrite")
            self.assertTrue(empty["retryable"])

            jumped = run_gate(root, tiny, 3, "break-new", SCORES, dry_run=True)
            # density fails first inside the harness when the file is tiny; use a dense draft
            dense = root / "drafts" / "dense.md"
            draft(dense, BODY)
            jumped = run_gate(root, dense, 3, "break-new", SCORES, dry_run=True)
            self.assertEqual(jumped["action"], "stop")
            self.assertIn("sequence", jumped["error"].lower())

            outside = Path(tempfile.gettempdir()) / "wwl-outside-draft.md"
            outside.write_text(BODY, encoding="utf-8")
            try:
                escaped = run_gate(root, outside, 1, "system-summary", SCORES, dry_run=True)
            finally:
                outside.unlink(missing_ok=True)
            self.assertEqual(escaped["action"], "stop")
            self.assertIn("Security", escaped["error"])

            lazy = root / "drafts" / "lazy.md"
            draft(lazy, BODY + "\n# TODO leave this unfinished\n")
            flagged = run_gate(root, lazy, 1, "system-summary", SCORES, dry_run=True)
            self.assertEqual(flagged["action"], "rewrite")

    @unittest.skipUnless(HARNESS.exists(), "local harness missing")
    def test_third_low_score_splits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file_path = root / "drafts" / "a.md"
            draft(file_path, BODY)
            actions = []
            for _ in range(3):
                result = run_gate(root, file_path, 1, "system-summary", LOW, dry_run=True)
                actions.append(result["action"])
            self.assertEqual(actions, ["rewrite", "rewrite", "split"])
            self.assertFalse(run_gate(root, file_path, 1, "system-summary", LOW, dry_run=True)["retryable"])
