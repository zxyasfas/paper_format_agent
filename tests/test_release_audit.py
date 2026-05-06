from __future__ import annotations

import unittest

from paper_format_agent.release_audit import audit_release_paths


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


if __name__ == "__main__":
    unittest.main()
