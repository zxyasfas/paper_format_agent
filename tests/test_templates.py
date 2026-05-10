from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates"


class TemplatePackTests(unittest.TestCase):
    def test_template_files_are_valid_and_complete(self) -> None:
        templates = sorted(TEMPLATE_DIR.glob("*.json"))
        self.assertGreaterEqual(len(templates), 3)

        for path in templates:
            with self.subTest(path=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                self._assert_template_metadata(data)
                self._assert_core_rules(data["rules"])

    def _assert_template_metadata(self, data: dict[str, Any]) -> None:
        for key in ("template_id", "display_name", "locale", "scenario", "rules"):
            self.assertIn(key, data)
        self.assertRegex(data["template_id"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertIsInstance(data["rules"], dict)

    def _assert_core_rules(self, rules: dict[str, Any]) -> None:
        for key in (
            "paper_size",
            "margins_cm",
            "body",
            "english",
            "heading_1",
            "heading_2",
            "heading_3",
            "figure_caption",
            "table_caption",
            "header",
            "footer",
            "required_sections",
        ):
            self.assertIn(key, rules)

        for side in ("top", "bottom", "left", "right"):
            self.assertIn(side, rules["margins_cm"])
            self.assertGreater(float(rules["margins_cm"][side]), 0)

        for section in ("zh_abstract", "zh_keywords", "en_abstract", "en_keywords", "toc"):
            self.assertIn(section, rules["required_sections"])
            self.assertIsInstance(rules["required_sections"][section], bool)


if __name__ == "__main__":
    unittest.main()
