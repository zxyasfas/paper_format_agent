from __future__ import annotations

import unittest

from paper_format_agent.pipeline import (
    is_abstract_title,
    is_english_abstract_title,
    is_keyword_en,
    is_keyword_zh,
)


class AbstractTitleVariantsTests(unittest.TestCase):
    """Test that common Chinese abstract-title label variants are recognised."""

    def test_bare_label(self):
        self.assertTrue(is_abstract_title("摘要"))  # 摘要

    def test_label_with_colon(self):
        self.assertTrue(is_abstract_title("摘要："))  # 摘要：

    def test_label_with_parens(self):
        self.assertTrue(is_abstract_title("（摘要）"))  # （摘要）

    def test_label_with_brackets(self):
        self.assertTrue(is_abstract_title("【摘要】"))  # 【摘要】

    def test_label_with_chinese_prefix(self):
        self.assertTrue(is_abstract_title("中文摘要"))  # 中文摘要

    def test_label_with_chinese_prefix_and_colon(self):
        self.assertTrue(is_abstract_title("中文摘要："))  # 中文摘要：

    def test_label_with_spaces_between_chars(self):
        self.assertTrue(is_abstract_title("摘 要"))  # 摘 要

    def test_label_with_multiple_spaces(self):
        self.assertTrue(is_abstract_title("  摘  要  "))  # "  摘  要  "

    def test_english_abstract_not_zh_abstract(self):
        self.assertFalse(is_abstract_title("Abstract"))
        self.assertFalse(is_abstract_title("ABSTRACT"))

    def test_english_abstract_not_zh_abstract_with_chinese_env(self):
        self.assertFalse(is_abstract_title("英文摘要"))  # 英文摘要
        self.assertFalse(is_abstract_title("英文摘要："))  # 英文摘要：

    def test_random_text_not_abstract(self):
        self.assertFalse(is_abstract_title("结论"))  # 结论
        self.assertFalse(is_abstract_title("前言"))  # 前言
        self.assertFalse(is_abstract_title(""))


class KeywordZhVariantsTests(unittest.TestCase):
    """Test that common Chinese keyword-label variants are recognised."""

    def test_bare_keyword(self):
        self.assertTrue(is_keyword_zh("关键词："))  # 关键词：

    def test_bare_keyword_alt(self):
        self.assertTrue(is_keyword_zh("关键字："))  # 关键字：

    def test_keyword_with_spaces_before_colon(self):
        self.assertTrue(is_keyword_zh("关键词  ："))  # 关键词  ：

    def test_keyword_with_brackets(self):
        self.assertTrue(is_keyword_zh("【关键词】"))  # 【关键词】

    def test_keyword_with_chinese_prefix(self):
        self.assertTrue(is_keyword_zh("中文关键词："))  # 中文关键词：

    def test_keyword_with_spaces_between_chars(self):
        self.assertTrue(is_keyword_zh("关 键 词："))  # 关 键 词：

    def test_keyword_with_semicolons(self):
        self.assertTrue(is_keyword_zh("关键词：测试；格式"))  # 关键词：测试；格式

    def test_english_keyword_not_zh_keyword(self):
        self.assertFalse(is_keyword_zh("Keywords:"))
        self.assertFalse(is_keyword_zh("Keywords: test"))

    def test_random_text_not_keyword(self):
        self.assertFalse(is_keyword_zh("摘要"))  # 摘要
        self.assertFalse(is_keyword_zh(""))


class EnglishLabelTests(unittest.TestCase):
    """Smoke tests for English label detection."""

    def test_english_abstract(self):
        self.assertTrue(is_english_abstract_title("Abstract"))
        self.assertTrue(is_english_abstract_title("ABSTRACT"))
        self.assertTrue(is_english_abstract_title("  abstract  "))

    def test_english_abstract_rejects_chinese(self):
        self.assertFalse(is_english_abstract_title("摘要"))

    def test_english_keyword(self):
        self.assertTrue(is_keyword_en("Keywords:"))
        self.assertTrue(is_keyword_en("Keywords: test; format"))
        self.assertTrue(is_keyword_en("KEYWORDS:"))

    def test_english_keyword_rejects_chinese(self):
        self.assertFalse(is_keyword_en("关键词："))


if __name__ == "__main__":
    unittest.main()
