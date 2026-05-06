from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document

from paper_format_agent.pipeline import run_pipeline
from paper_format_agent.rules import extract_rules_from_text


class PipelineContentGuardTests(unittest.TestCase):
    def test_pipeline_keeps_content_fingerprint(self):
        with TemporaryDirectory() as td:
            td_path = Path(td)
            src = td_path / "input.docx"
            out = td_path / "out.docx"

            doc = Document()
            doc.add_paragraph("摘要")
            doc.add_paragraph("这是摘要内容。")
            doc.add_paragraph("关键词：测试；格式化")
            doc.add_paragraph("一、绪论")
            doc.add_paragraph("这是正文第一段。")
            table = doc.add_table(rows=1, cols=2)
            table.cell(0, 0).text = "列1"
            table.cell(0, 1).text = "列2"
            doc.save(src)

            rules = extract_rules_from_text("正文宋体小四，1.25倍行距。")
            result = run_pipeline(src, out, rules, enforce_content_guard=True)
            self.assertFalse(result.content_changed)
            self.assertTrue(out.exists())

    def test_pipeline_writes_header_and_page_number_footer(self):
        with TemporaryDirectory() as td:
            td_path = Path(td)
            src = td_path / "input.docx"
            out = td_path / "out.docx"

            doc = Document()
            doc.add_paragraph("Abstract")
            doc.add_paragraph("Body paragraph.")
            doc.save(src)

            rules = extract_rules_from_text("")
            rules["header"]["text"] = "Journal Draft"
            result = run_pipeline(src, out, rules, enforce_content_guard=True)

            formatted = Document(str(out))
            section = formatted.sections[0]
            self.assertEqual(section.header.paragraphs[0].text, "Journal Draft")
            self.assertIn("PAGE", section.footer._element.xml)
            self.assertFalse(result.content_changed)
            self.assertEqual(result.logs[0]["action"], "setup_document_base")
            self.assertEqual(result.logs[0]["headers_written"], 1)
            self.assertEqual(result.logs[0]["footers_written"], 1)


if __name__ == "__main__":
    unittest.main()
