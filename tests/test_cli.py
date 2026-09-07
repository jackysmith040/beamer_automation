"""
tests.test_cli
Comprehensive unit tests for the Typer CLI interface (beamer).
"""

import json
import unittest
from typer.testing import CliRunner

from agent_helper.cli import app

runner = CliRunner()


class TestCLI(unittest.TestCase):
    def test_cli_help(self):
        result = runner.invoke(app, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("build", result.output)
        self.assertIn("compile", result.output)
        self.assertIn("review", result.output)
        self.assertIn("reset", result.output)
        self.assertIn("demo", result.output)
        self.assertIn("init", result.output)

    def test_cli_review_sample(self):
        result = runner.invoke(app, ["review", "samples/beamer/sample_presentation.md"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Pre-flight Review", result.output)
        self.assertIn("PASS", result.output)

    def test_cli_review_json(self):
        result = runner.invoke(app, ["review", "samples/beamer/sample_presentation.md", "--json"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertTrue(data.get("valid"))
        self.assertIn("metrics", data)
        self.assertEqual(len(data.get("errors", [])), 0)

    def test_cli_reset_dry_run(self):
        result = runner.invoke(app, ["reset", "--dry-run"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("DRY-RUN", result.output)

    def test_cli_init_help(self):
        result = runner.invoke(app, ["init", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--type", result.output)


if __name__ == "__main__":
    unittest.main()
