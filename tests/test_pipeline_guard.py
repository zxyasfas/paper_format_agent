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


if __name__ == "__main__":
    unittest.main()

