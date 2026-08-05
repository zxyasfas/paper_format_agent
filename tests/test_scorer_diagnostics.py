from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document

from paper_format_agent.scorer import save_reports, score_document


class ScorerDiagnosticsTests(unittest.TestCase):
    def test_score_document_returns_actionable_diagnostics(self):
        with TemporaryDirectory() as td:
            docx_path = Path(td) / "paper.docx"
            doc = Document()
            doc.add_paragraph("Body paragraph without required front matter.")
            doc.save(docx_path)

            report = score_document(
                docx_path,
                {
                    "required_sections": {
                        "zh_abstract": True,
                        "zh_keywords": True,
                        "toc": True,
                    },
                    "min_total_chars_no_space": 0,
                },
                enforce_required_sections=True,
            )

            diagnostics = {item["name"]: item for item in report["diagnostics"]}
            self.assertIn("missing_zh_abs", diagnostics)
            self.assertIn("missing_zh_keywords", diagnostics)
            self.assertIn("missing_toc_title", diagnostics)
            self.assertEqual(diagnostics["missing_zh_abs"]["severity"], "high")
            self.assertTrue(diagnostics["missing_zh_abs"]["suggested_fix"])
            self.assertEqual(
                diagnostics["missing_zh_abs"]["penalty"],
                25,
            )

    def test_save_reports_writes_diagnostics_to_json_and_html(self):
        with TemporaryDirectory() as td:
            out_json = Path(td) / "format_report.json"
            out_html = Path(td) / "format_report.html"
            report = {
                "score": 75,
                "raw_quality_score": 75,
                "chars_no_space": 100,
                "features": {},
                "penalties": [{"name": "missing_zh_abs", "value": 25}],
                "diagnostics": [
                    {
                        "name": "missing_zh_abs",
                        "category": "required_sections",
                        "severity": "high",
                        "penalty": 25,
                        "summary": "Chinese abstract section is missing.",
                        "suggested_fix": "Add a standalone Chinese abstract title.",
                        "evidence": {},
                    }
                ],
            }

            save_reports(report, out_json, out_html)

            saved = json.loads(out_json.read_text(encoding="utf-8"))
            html = out_html.read_text(encoding="utf-8")
            self.assertEqual(saved["diagnostics"][0]["name"], "missing_zh_abs")
            self.assertIn("哪个检查没通过、如何修复", html)
            self.assertIn("修复建议", html)
            self.assertIn("缺少中文摘要", html)
            self.assertIn("missing_zh_abs", html)
            self.assertIn("严重", html)

    def test_save_reports_human_readable_check_labels_and_category_hints(self):
        with TemporaryDirectory() as td:
            out_html = Path(td) / "format_report.html"
            report = {
                "score": 60,
                "raw_quality_score": 60,
                "chars_no_space": 100,
                "features": {},
                "penalties": [],
                "diagnostics": [
                    {
                        "name": "char_below_min",
                        "category": "template_rules",
                        "severity": "medium",
                        "penalty": 8,
                        "summary": "Document length is below the minimum.",
                        "suggested_fix": "Verify the character count.",
                        "evidence": {},
                    }
                ],
            }

            save_reports(report, Path(td) / "format_report.json", out_html)

            html = out_html.read_text(encoding="utf-8")
            self.assertIn("字数未达到格式指南下限", html)
            self.assertIn("对照格式指南逐条核对该项规则的要求", html)
            self.assertIn("中等", html)


if __name__ == "__main__":
    unittest.main()
