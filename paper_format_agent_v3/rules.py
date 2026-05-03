from __future__ import annotations

import re
from copy import deepcopy


DEFAULT_RULES = {
    "name": "本科论文格式规则（V3）",
    "paper_size": "A4",
    "margins_cm": {"top": 2.54, "bottom": 2.54, "left": 2.54, "right": 2.17},
    "body": {"font": "宋体", "size_pt": 12, "line_spacing": 1.25, "first_line_indent_chars": 2, "alignment": "justify"},
    "english": {"font": "Times New Roman", "size_pt": 12, "line_spacing": 1.25},
    "toc": {"title": "目  录", "font": "宋体", "title_size_pt": 18, "body_size_pt": 12},
    "abstract_title": {"text": "摘  要", "font": "宋体", "size_pt": 18},
    "heading_1": {"font": "黑体", "size_pt": 16, "bold": True, "page_break_before": False},
    "heading_2": {"font": "黑体", "size_pt": 14, "bold": True},
    "heading_3": {"font": "宋体", "size_pt": 12, "bold": True},
    "header": {"text": "本科毕业论文", "font": "宋体", "size_pt": 9},
    "min_total_chars_no_space": 10000,
    "required_sections": {
        "zh_abstract": True,
        "zh_keywords": True,
        "en_abstract": False,
        "en_keywords": False,
        "toc": False,
    },
}


def _extract_min_chars(clean: str) -> int | None:
    m = re.search(r"(不少于|不低于)([0-9.]+)万字", clean)
    if m:
        return int(float(m.group(2)) * 10000)
    m = re.search(r"(不少于|不低于)(\d{4,6})字", clean)
    if m:
        return int(m.group(2))
    m = re.search(r"(\d{4,6})字(以上|及以上)", clean)
    if m:
        return int(m.group(1))
    return None


def extract_rules_from_text(text: str | None = None) -> dict:
    rules = deepcopy(DEFAULT_RULES)
    if not text:
        return rules

    clean = re.sub(r"\s+", "", text)
    lower = clean.lower()
    m = re.search(
        r"上[、,，]?下页边距(?:均为|为)?([0-9.]+)(?:厘米|cm).*?左页边距([0-9.]+)(?:厘米|cm).*?右页边距([0-9.]+)(?:厘米|cm)",
        clean,
        flags=re.IGNORECASE,
    )
    if m:
        rules["margins_cm"].update(
            {
                "top": float(m.group(1)),
                "bottom": float(m.group(1)),
                "left": float(m.group(2)),
                "right": float(m.group(3)),
            }
        )
    else:
        m = re.search(
            r"上[、,，]?下[、,，]?右页边距([0-9.]+)(?:厘米|cm).*?左页边距([0-9.]+)(?:厘米|cm)",
            clean,
            flags=re.IGNORECASE,
        )
        if m:
            rules["margins_cm"].update(
                {
                    "top": float(m.group(1)),
                    "bottom": float(m.group(1)),
                    "right": float(m.group(1)),
                    "left": float(m.group(2)),
                }
            )

    if "小四号宋体" in clean:
        rules["body"]["font"] = "宋体"
        rules["body"]["size_pt"] = 12
    if "1.25倍行距" in clean:
        rules["body"]["line_spacing"] = 1.25

    min_chars = _extract_min_chars(clean)
    if min_chars:
        rules["min_total_chars_no_space"] = min_chars

    if "目录" in clean or "目錄" in clean or "目次" in clean:
        rules["required_sections"]["toc"] = True
    if "关键词" in clean or "关键字" in clean:
        rules["required_sections"]["zh_keywords"] = True
    if ("英文摘要" in clean) or ("外文摘要" in clean) or ("abstract" in lower):
        rules["required_sections"]["en_abstract"] = True
    if ("英文关键词" in clean) or ("外文关键词" in clean) or ("keywords" in lower):
        rules["required_sections"]["en_keywords"] = True

    return rules
