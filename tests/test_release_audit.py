from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from paper_format_agent.release_audit import audit_release_paths
from tools import release_audit as release_audit_tool


class ReleaseAuditTests(unittest.TestCase):
    def test_audit_flags_generated_and_private_risk_artifacts(self):
        findings = audit_release_paths(
            [
                "paper_format_agent/cli.py",
                "sample_output/run/formatted_paper_v3.docx",
                "paper_format_agent/__pycache__/cli.pyc",
                "tmp_paper_text.txt",
                ".env",
            ]
        )

        categories = {item["category"] for item in findings}
        self.assertIn("local_output", categories)
        self.assertIn("python_cache", categories)
        self.assertIn("local_scratch", categories)
        self.assertIn("secret_like_file", categories)

    def test_audit_allows_code_and_synthetic_fixture_locations(self):
        findings = audit_release_paths(
            [
                "paper_format_agent/cli.py",
                "tests/fixtures/minimal.docx",
                "docs/fixtures/template.docx",
            ]
        )

        self.assertEqual(findings, [])

    def test_local_paths_merges_untracked_and_ignored_paths(self):
        outputs = [
            "notes/private_template.docx\n",
            "sample_output/run/format_report.json\nnotes/private_template.docx\n",
        ]

        def fake_run(*args, **kwargs):
            result = Mock()
            result.stdout = outputs.pop(0)
            return result

        with patch.object(release_audit_tool.subprocess, "run", side_effect=fake_run):
            paths = release_audit_tool.local_paths()

        self.assertEqual(
            paths,
            [
                "notes/private_template.docx",
                "sample_output/run/format_report.json",
            ],
        )


if __name__ == "__main__":
    unittest.main()
