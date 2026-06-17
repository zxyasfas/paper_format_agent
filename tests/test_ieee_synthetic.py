from __future__ import annotations

import unittest

from paper_format_agent.pipeline import (
    is_chapter,
    is_figure_caption,
    is_section,
    is_subsection,
    is_table_caption,
)


class IEEESyntheticTests(unittest.TestCase):
    def test_ieee_figure_caption_detected(self):
        self.assertTrue(is_figure_caption("Fig. 1"))
        self.assertTrue(is_figure_caption("Fig. 1:"))
        self.assertTrue(is_figure_caption("Fig. 1. System architecture"))
        self.assertTrue(is_figure_caption("Fig. 2: Training loss over epochs"))
        self.assertTrue(is_figure_caption("Fig. 10"))

    def test_ieee_figure_caption_case_insensitive(self):
        self.assertTrue(is_figure_caption("fig. 1"))
        self.assertTrue(is_figure_caption("FIG. 1"))

    def test_ieee_figure_caption_rejects_body_text(self):
        self.assertFalse(is_figure_caption("The system architecture is shown below."))
        self.assertFalse(is_figure_caption("This is not a figure caption."))
        self.assertFalse(is_figure_caption("Figment of imagination"))

    def test_ieee_table_caption_arabic_numerals(self):
        self.assertTrue(is_table_caption("Table 1"))
        self.assertTrue(is_table_caption("TABLE 1"))
        self.assertTrue(is_table_caption("Table 10:"))
        self.assertTrue(is_table_caption("Table 2. Experimental results"))

    def test_ieee_table_caption_roman_numerals(self):
        self.assertTrue(is_table_caption("Table I"))
        self.assertTrue(is_table_caption("TABLE II"))
        self.assertTrue(is_table_caption("Table III"))
        self.assertTrue(is_table_caption("Table IV"))
        self.assertTrue(is_table_caption("Table V"))
        self.assertTrue(is_table_caption("Table X"))

    def test_ieee_table_caption_case_insensitive(self):
        self.assertTrue(is_table_caption("table i"))
        self.assertTrue(is_table_caption("table 1"))

    def test_ieee_table_caption_rejects_body_text(self):
        self.assertFalse(is_table_caption("The results are shown in the table below."))
        self.assertFalse(is_table_caption("Tablecloth is white"))
        self.assertFalse(is_table_caption("Tabernacle"))

    def test_ieee_heading_level1_roman_numerals(self):
        self.assertTrue(is_chapter("I. INTRODUCTION"))
        self.assertTrue(is_chapter("II. BACKGROUND"))
        self.assertTrue(is_chapter("III. METHODOLOGY"))
        self.assertTrue(is_chapter("IV. EXPERIMENTS"))
        self.assertTrue(is_chapter("V. RESULTS"))
        self.assertTrue(is_chapter("VI. CONCLUSION"))
        self.assertTrue(is_chapter("X. RELATED WORK"))

    def test_ieee_heading_level1_rejects_body(self):
        self.assertFalse(is_chapter("Introduction"))
        self.assertFalse(is_chapter("This is a body paragraph."))
        self.assertFalse(is_chapter("I like machine learning"))

    def test_ieee_section_numbered(self):
        self.assertTrue(is_section("1.1"))
        self.assertTrue(is_section("2.3"))
        self.assertTrue(is_section("3.1  Experimental setup"))
        self.assertTrue(is_subsection("1.1.1"))
        self.assertTrue(is_subsection("2.3.4"))


if __name__ == "__main__":
    unittest.main()
