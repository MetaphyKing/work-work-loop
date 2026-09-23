import json
import tempfile
import unittest
from pathlib import Path

from wwl_phase.bind import bind


class BindTests(unittest.TestCase):
    def test_valid_start_creates_dirs_and_keeps_idea(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = bind(tmp, action="start", idea="Name the caller.", locks=["no new runtime"], spine="BIBLE")
            self.assertTrue(first["success"])
            self.assertEqual(first["phase"], 1)
            self.assertTrue((Path(tmp) / "drafts").is_dir())
            self.assertTrue((Path(tmp) / "outbox").is_dir())
            again = bind(tmp, action="start", idea="A different product.")
            self.assertEqual(again["idea"], "Name the caller.")
            card = json.loads((Path(tmp) / "wwl_run.json").read_text(encoding="utf-8"))
            self.assertEqual(card["idea"], "Name the caller.")

    def test_malformed_prompt_does_not_create_a_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = bind(tmp, prompt="WWL/1.1.0\n[SPINE] MAYBE\n")
            self.assertFalse(result["success"])
            self.assertFalse((Path(tmp) / "wwl_run.json").exists())

    def test_empty_root_and_continue_without_card(self):
        self.assertFalse(bind("  ", action="start", idea="x")["success"])
        with tempfile.TemporaryDirectory() as tmp:
            missing = bind(tmp, action="continue")
            self.assertFalse(missing["success"])
            self.assertIn("run card", missing["error"])
