"""
tests.test_reset
Unit tests for the reset_workspace utility.
"""

from pathlib import Path
import tempfile
import unittest

from agent_helper.reset import reset_workspace


class TestResetWorkspace(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.test_dir.name)

        # Create mock project structure
        (self.root / "input" / "beamer").mkdir(parents=True)
        (self.root / "input" / "beamer" / "slides.tex").write_text(r"\documentclass{beamer}")
        (self.root / "digestion").mkdir(parents=True)
        (self.root / "digestion" / "cache.json").write_text("{}")
        (self.root / "output").mkdir(parents=True)
        (self.root / "output" / "deck.pdf").write_text("dummy pdf")
        (self.root / "template_override").mkdir(parents=True)
        (self.root / "template_override" / "tpl.tex").write_text("% template")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_dry_run_does_not_delete(self):
        report = reset_workspace(root_dir=self.root, dry_run=True)
        self.assertTrue(report["dry_run"])
        self.assertTrue((self.root / "input" / "beamer" / "slides.tex").exists())
        self.assertTrue((self.root / "output" / "deck.pdf").exists())

    def test_reset_creates_backup_and_cleans(self):
        report = reset_workspace(root_dir=self.root, backup=True, keep_templates=True)
        self.assertEqual(report["status"], "success")
        self.assertIsNotNone(report["backup_created"])
        self.assertTrue(Path(report["backup_created"]).exists())

        # Check that old output was removed
        self.assertFalse((self.root / "output" / "deck.pdf").exists())
        # Check that new clean subdirectories were initialized
        self.assertTrue((self.root / "input" / "beamer").exists())
        self.assertTrue((self.root / "input" / "thesis").exists())
        self.assertTrue((self.root / "input" / "assets").exists())
        self.assertTrue((self.root / "input" / "README.md").exists())
        self.assertTrue((self.root / "output").exists())
        self.assertTrue((self.root / "digestion").exists())

        # Check template_override was preserved
        self.assertTrue((self.root / "template_override" / "tpl.tex").exists())


if __name__ == "__main__":
    unittest.main()
