from __future__ import annotations

import re
from copy import deepcopy

DEFAULT_RULES = {
    "name": "本科毕业论文格式规则（MVP）",
    "paper_size": "A4",
    "margins_cm": {"top": 2.54, "bottom": 2.54, "left": 2.54, "right": 2.17},
    "body": {"font": "宋体", "size_pt": 12, "line_spacing": 1.25, "first_line_indent_chars": 2, "alignment": "justify"},
    "abstract_title": {"font": "宋体", "size_pt": 18, "bold": True, "alignment": "center", "text": "摘  要"},
    "abstract_body": {"font": "宋体", "size_pt": 12, "line_spacing": 1.25, "first_line_indent_chars": 2},
    "keyword": {"font": "宋体", "size_pt": 12, "label_bold": True, "separator": "；", "min_count": 5},
    "english": {"font": "Times New Roman", "size_pt": 12, "line_spacing": 1.25},
    "toc": {"title": "目  录", "font": "宋体", "title_size_pt": 18, "body_size_pt": 12, "auto": True},
    "heading_1": {"font": "黑体", "size_pt": 16, "bold": True, "alignment": "center", "page_break_before": False},
    "heading_2": {"font": "黑体", "size_pt": 14, "bold": True, "alignment": "left"},
    "heading_3": {"font": "宋体", "size_pt": 12, "bold": True, "alignment": "left"},
    "heading_4": {"font": "宋体", "size_pt": 12, "bold": True, "alignment": "left", "first_line_indent": False},
    "references": {"title_font": "黑体", "title_size_pt": 16, "item_font": "宋体", "item_size_pt": 10.5},
    "appendix": {"title_font": "黑体", "title_size_pt": 14, "body_font": "宋体", "body_size_pt": 10.5},
    "author_bio": {"title_font": "黑体", "title_size_pt": 16, "body_font": "宋体", "body_size_pt": 12},
    "acknowledgement": {"title_font": "黑体", "title_size_pt": 16, "body_font": "宋体", "body_size_pt": 12},
    "caption": {"figure_font": "宋体", "table_font": "宋体", "size_pt": 10.5, "alignment": "center"},
    "table": {"font": "宋体", "size_pt": 10.5, "alignment": "center"},
    "footnote": {"font": "宋体", "size_pt": 9, "numbering": "circled_per_page"},
    "pagination": {"front": "upperRoman", "body": "decimal", "body_start": 1, "position": "footer_center"},
    "header": {"even": "本科毕业论文", "odd": "本科毕业论文", "font": "宋体", "size_pt": 9, "different_odd_even": True},
    # Dynamic, school-specific front-matter order; can be overridden by extract_rules_from_text().
    "front_matter_order": ["abstract", "keyword", "english_abstract", "english_keyword", "toc", "intro"],
    "required_sections": ["摘要", "关键词", "ABSTRACT", "Keywords", "目录", "引言", "结论", "参考文献", "作者简介", "致谢"],
    "min_total_chars_no_space": 20000,
}

_SIZE_MAP = {
    "小初": 36,
    "初号": 42,
    "小一": 24,
    "一号": 26,
    "小二": 18,
    "二号": 22,
    "小三": 15,
    "三号": 16,
    "小四": 12,
    "四号": 14,
    "五号": 10.5,
    "小五": 9,
}


def _size_to_pt(label: str, fallback: float) -> float:
    return _SIZE_MAP.get(label, fallback)


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


def _extract_front_matter_order(text: str) -> list[str]:
    """
    Infer section order from school format text when possible.
    Falls back to default canonical order when extraction is ambiguous.
    """
    default_order = ["abstract", "keyword", "english_abstract", "english_keyword", "toc", "intro"]
    if not text:
        return default_order

    compact = re.sub(r"\s+", "", text)
    compact_lower = compact.lower()

    # Prefer stable aliases that commonly appear in Chinese thesis specs.
    patterns: dict[str, list[str]] = {
        "abstract": ["中文摘要", "摘要"],
        "keyword": ["关键词", "关键字"],
        "english_abstract": ["英文摘要", "abstract"],
        "english_keyword": ["英文关键词", "keywords", "keyword"],
        "toc": ["目录", "目次", "目錄"],
        "intro": ["绪论", "引言"],
    }

    pos: dict[str, int] = {}
    for key, aliases in patterns.items():
        hit_idx = None
        for alias in aliases:
            idx = compact_lower.find(alias.lower())
            if idx >= 0 and (hit_idx is None or idx < hit_idx):
                hit_idx = idx
        if hit_idx is not None:
            pos[key] = hit_idx

    # Not enough evidence -> keep defaults.
    if len(pos) < 2:
        return default_order

    ordered = [k for k, _ in sorted(pos.items(), key=lambda kv: kv[1])]
    # Append missing default items to keep downstream logic stable.
    for item in default_order:
        if item not in ordered:
            ordered.append(item)
    return ordered


def extract_rules_from_text(text: str | None = None) -> dict:
    rules = deepcopy(DEFAULT_RULES)
    if not text:
        return rules

    clean = re.sub(r"\s+", "", text)

    # Margins:
    # - 上、下、右页边距2厘米，左页边距2.7厘米
    # - 上、下页边距2.54cm，左页边距2.54cm，右页边距2.17cm
    m = re.search(
        r"上[、,，]?下[、,，]?右页边距([0-9.]+)(?:厘米|cm).*?左页边距([0-9.]+)(?:厘米|cm)",
        clean,
        flags=re.IGNORECASE,
    )
    if m:
        right_val = float(m.group(1))
        left_val = float(m.group(2))
        rules["margins_cm"].update({
            "top": right_val,
            "bottom": right_val,
            "right": right_val,
            "left": left_val,
        })
    else:
        m = re.search(
            r"上[、,，]?下页边距(?:均为|为)?([0-9.]+)(?:厘米|cm).*?"
            r"左页边距([0-9.]+)(?:厘米|cm).*?"
            r"右页边距([0-9.]+)(?:厘米|cm)",
            clean,
            flags=re.IGNORECASE,
        )
        if m:
            tb = float(m.group(1))
            rules["margins_cm"].update({
                "top": tb,
                "bottom": tb,
                "left": float(m.group(2)),
                "right": float(m.group(3)),
            })

    if "1.25倍行距" in clean:
        rules["body"]["line_spacing"] = 1.25
    if "行间距23磅" in clean or "行间距：23磅" in clean:
        # Keep a practical default multiplier for python-docx rendering.
        rules["body"]["line_spacing"] = 1.25
    if "小四号宋体" in clean:
        rules["body"]["font"] = "宋体"
        rules["body"]["size_pt"] = 12

    m = re.search(r"摘要.*?(小[一二三四五]|[一二三四五]号).*?宋体.*?加粗", clean)
    if m:
        rules["abstract_title"]["size_pt"] = _size_to_pt(m.group(1), rules["abstract_title"]["size_pt"])
        rules["abstract_title"]["font"] = "宋体"
        rules["abstract_title"]["bold"] = True

    if "关键词" in clean and "分号" in clean:
        rules["keyword"]["separator"] = "；"

    if "三级标题" in clean and "小四号宋体加粗" in clean:
        rules["heading_3"].update({"font": "宋体", "size_pt": 12, "bold": True, "alignment": "left"})

    if "大写罗马数字" in clean:
        rules["pagination"]["front"] = "upperRoman"
    if "阿拉伯数字" in clean:
        rules["pagination"]["body"] = "decimal"
    if "页脚居中" in clean:
        rules["pagination"]["position"] = "footer_center"
    if "奇偶页不同" in clean:
        rules["header"]["different_odd_even"] = True

    m = re.search(r"([一-龥]{2,20})学位论文", clean)
    if m:
        rules["header"]["even"] = f"{m.group(1)}学位论文"
        rules["header"]["odd"] = f"{m.group(1)}学位论文"

    min_chars = _extract_min_chars(clean)
    if min_chars:
        rules["min_total_chars_no_space"] = min_chars

    # School-specific structure order (front-matter/body anchor).
    rules["front_matter_order"] = _extract_front_matter_order(text)

    return rules
