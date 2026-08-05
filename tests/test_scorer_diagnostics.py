from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

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

    def test_figure_caption_align_diagnostic_emitted_with_evidence(self):
        with TemporaryDirectory() as td:
            docx_path = Path(td) / "paper.docx"
            doc = Document()
            doc.add_paragraph("Fig. 1. Synthetic system architecture")
            doc.add_paragraph("Body text describing the figure.")
            doc.add_paragraph("Fig. 2: Training loss over epochs")
            doc.save(docx_path)

            report = score_document(
                docx_path,
                {
                    "figure_caption": {"align": "center"},
                    "min_total_chars_no_space": 0,
                },
            )

            diagnostics = {item["name"]: item for item in report["diagnostics"]}
            self.assertIn("figure_caption_align", diagnostics)
            self.assertEqual(diagnostics["figure_caption_align"]["severity"], "medium")
            self.assertGreater(diagnostics["figure_caption_align"]["penalty"], 0)
            self.assertLess(report["raw_quality_score"], 100)
            self.assertTrue(diagnostics["figure_caption_align"]["suggested_fix"])

            evidence = diagnostics["figure_caption_align"]["evidence"]["figure_caption_align"]
            self.assertEqual(len(evidence), 2)
            self.assertEqual(evidence[0]["idx"], 0)
            self.assertIn("Synthetic system architecture", evidence[0]["text"])
            self.assertIn("Fig. 2", evidence[1]["text"])

    def test_centered_figure_caption_is_not_flagged(self):
        with TemporaryDirectory() as td:
            docx_path = Path(td) / "paper.docx"
            doc = Document()
            p = doc.add_paragraph("Fig. 1. Synthetic system architecture")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.save(docx_path)

            report = score_document(
                docx_path,
                {
                    "figure_caption": {"align": "center"},
                    "min_total_chars_no_space": 0,
                },
            )

            diagnostics = {item["name"]: item for item in report["diagnostics"]}
            self.assertNotIn("figure_caption_align", diagnostics)
            self.assertEqual(report["raw_quality_score"], 100)

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
            self.assertIn("Actionable diagnostics", html)
            self.assertIn("Suggested fix", html)
            self.assertIn("missing_zh_abs", html)


if __name__ == "__main__":
    unittest.main()
