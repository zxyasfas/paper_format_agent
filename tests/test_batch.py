from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from paper_format_agent.batch import discover_paper_files, make_case_output_dir, summarize_batch


class BatchDiscoveryTests(unittest.TestCase):
    def test_discover_paper_files_skips_temp_hidden_and_generated_docx(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "paper-b.docx").write_bytes(b"")
            (root / "paper-a.docx").write_bytes(b"")
            (root / "~$paper-a.docx").write_bytes(b"")
            (root / "formatted_paper_v3.docx").write_bytes(b"")
            hidden = root / ".hidden"
            hidden.mkdir()
            (hidden / "paper-c.docx").write_bytes(b"")
            nested = root / "nested"
            nested.mkdir()
            (nested / "paper-d.docx").write_bytes(b"")
            (nested / "notes.txt").write_text("not a paper", encoding="utf-8")

            names = [path.relative_to(root).as_posix() for path in discover_paper_files(root)]

            self.assertEqual(names, ["nested/paper-d.docx", "paper-a.docx", "paper-b.docx"])

    def test_make_case_output_dir_is_stable_and_distinguishes_duplicate_names(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            first = root / "a" / "paper.docx"
            second = root / "b" / "paper.docx"
            out = root / "out"

            first_dir = make_case_output_dir(out, first, root)
            second_dir = make_case_output_dir(out, second, root)

            self.assertNotEqual(first_dir, second_dir)
            self.assertTrue(first_dir.name.startswith("a__paper__"))
            self.assertTrue(second_dir.name.startswith("b__paper__"))

    def test_summarize_batch_reports_scores_and_failures(self):
        summary = summarize_batch(
            [
                {"ok": True, "score_before": 70, "score_after": 90, "content_changed": False},
                {"ok": False, "score_before": 80, "score_after": 80, "content_changed": True},
            ]
        )

        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["content_changed_count"], 1)
        self.assertEqual(summary["average_score_improvement"], 10.0)
        json.dumps(summary)


if __name__ == "__main__":
    unittest.main()
