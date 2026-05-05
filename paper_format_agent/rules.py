from __future__ import annotations

import re
from copy import deepcopy


# Unicode escapes are used intentionally to avoid host-encoding drift.
ZH_SONGTI = "\u5b8b\u4f53"  # 宋体
ZH_HEITI = "\u9ed1\u4f53"  # 黑体
ZH_FANGSONG = "\u4eff\u5b8b"  # 仿宋

KW_BODY = "\u6b63\u6587"  # 正文
KW_TOC = "\u76ee\u5f55"  # 目录
KW_TOC_ALT = "\u76ee\u6b21"  # 目次
KW_ZH_ABS = "\u6458\u8981"  # 摘要
KW_ZH_KW = "\u5173\u952e\u8bcd"  # 关键词
KW_ZH_KW_ALT = "\u5173\u952e\u5b57"  # 关键字
KW_EN_ABS = "\u82f1\u6587\u6458\u8981"  # 英文摘要
KW_FOREIGN_ABS = "\u5916\u6587\u6458\u8981"  # 外文摘要
KW_EN_KW = "\u82f1\u6587\u5173\u952e\u8bcd"  # 英文关键词
KW_FOREIGN_KW = "\u5916\u6587\u5173\u952e\u8bcd"  # 外文关键词

KW_TOP = "\u4e0a"
KW_BOTTOM = "\u4e0b"
KW_LEFT = "\u5de6"
KW_RIGHT = "\u53f3"
KW_CM = "\u5398\u7c73"
KW_MARGIN = "\u9875\u8fb9\u8ddd"
KW_TOP_BOTTOM = "\u4e0a\u4e0b"
KW_LEFT_RIGHT = "\u5de6\u53f3"

KW_LV1 = "\u4e00\u7ea7\u6807\u9898"  # 一级标题
KW_LV2 = "\u4e8c\u7ea7\u6807\u9898"  # 二级标题
KW_LV3 = "\u4e09\u7ea7\u6807\u9898"  # 三级标题
KW_CENTER = "\u5c45\u4e2d"  # 居中
KW_LEFT_ALIGN = "\u5de6\u5bf9\u9f50"  # 左对齐
KW_JUSTIFY = "\u4e24\u7aef\u5bf9\u9f50"  # 两端对齐

KW_LS_15 = "1.5\u500d\u884c\u8ddd"
KW_LS_125 = "1.25\u500d\u884c\u8ddd"
KW_LS_SINGLE = "\u5355\u500d\u884c\u8ddd"

KW_NOT_LESS_THAN = "\u4e0d\u5c11\u4e8e"
KW_NOT_LOWER_THAN = "\u4e0d\u4f4e\u4e8e"
KW_WAN_ZI = "\u4e07\u5b57"
KW_ZI = "\u5b57"


DEFAULT_RULES = {
    "name": "\u672c\u79d1\u8bba\u6587\u683c\u5f0f\u89c4\u5219(V3)",
    "paper_size": "A4",
    "margins_cm": {"top": 2.54, "bottom": 2.54, "left": 3.17, "right": 2.54},
    "body": {
        "font": ZH_SONGTI,
        "size_pt": 12,
        "line_spacing": 1.25,
        "first_line_indent_chars": 2,
        "alignment": "justify",
    },
    "english": {"font": "Times New Roman", "size_pt": 12, "line_spacing": 1.25},
    "toc": {"title": KW_TOC, "font": ZH_SONGTI, "title_size_pt": 18, "body_size_pt": 12},
    "abstract_title": {"text": KW_ZH_ABS, "font": ZH_SONGTI, "size_pt": 18},
    "heading_1": {"font": ZH_HEITI, "size_pt": 16, "bold": True, "align": "center", "page_break_before": False},
    "heading_2": {"font": ZH_HEITI, "size_pt": 14, "bold": True, "align": "left"},
    "heading_3": {"font": ZH_HEITI, "size_pt": 12, "bold": True, "align": "left"},
    "figure_caption": {"font": ZH_SONGTI, "size_pt": 10.5, "bold": False, "align": "center"},
    "table_caption": {"font": ZH_SONGTI, "size_pt": 10.5, "bold": False, "align": "center"},
    "table_body": {"font": ZH_SONGTI, "size_pt": 12, "line_spacing": 1.25, "align": "left"},
    "header": {"text": "\u672c\u79d1\u6bd5\u4e1a\u8bba\u6587", "font": ZH_SONGTI, "size_pt": 9},
    "min_total_chars_no_space": 10000,
    "required_sections": {
        "zh_abstract": True,
        "zh_keywords": True,
        "en_abstract": False,
        "en_keywords": False,
        "toc": False,
    },
}


def _cn_numeral_size_to_pt(clean: str) -> float | None:
    mapping = {
        "\u5c0f\u56db": 12.0,  # 小四
        "\u56db\u53f7": 14.0,  # 四号
        "\u5c0f\u4e09": 15.0,  # 小三
        "\u4e09\u53f7": 16.0,  # 三号
        "\u5c0f\u4e8c": 18.0,  # 小二
        "\u4e8c\u53f7": 22.0,  # 二号
        "\u4e94\u53f7": 10.5,  # 五号
        "\u5c0f\u4e94": 9.0,  # 小五
    }
    for k, v in mapping.items():
        if k in clean:
            return v
    return None


def _extract_min_chars(clean: str) -> int | None:
    m = re.search(rf"({KW_NOT_LESS_THAN}|{KW_NOT_LOWER_THAN})\s*([0-9.]+)\s*{KW_WAN_ZI}", clean)
    if m:
        return int(float(m.group(2)) * 10000)
    m = re.search(rf"({KW_NOT_LESS_THAN}|{KW_NOT_LOWER_THAN})\s*(\d{{4,6}})\s*{KW_ZI}", clean)
    if m:
        return int(m.group(2))
    m = re.search(rf"(\d{{4,6}})\s*{KW_ZI}(?:\u4ee5\u4e0a|\u53ca\u4ee5\u4e0a)?", clean)
    if m:
        return int(m.group(1))
    return None


def _extract_margins(clean: str) -> dict[str, float] | None:
    m = re.search(
        rf"{KW_TOP}\s*([0-9.]+)\s*(?:cm|{KW_CM}).*?"
        rf"{KW_BOTTOM}\s*([0-9.]+)\s*(?:cm|{KW_CM}).*?"
        rf"{KW_LEFT}\s*([0-9.]+)\s*(?:cm|{KW_CM}).*?"
        rf"{KW_RIGHT}\s*([0-9.]+)\s*(?:cm|{KW_CM})",
        clean,
        flags=re.IGNORECASE,
    )
    if m:
        return {"top": float(m.group(1)), "bottom": float(m.group(2)), "left": float(m.group(3)), "right": float(m.group(4))}

    m = re.search(
        rf"{KW_TOP_BOTTOM}\s*([0-9.]+)\s*(?:cm|{KW_CM}).*?{KW_LEFT_RIGHT}\s*([0-9.]+)\s*(?:cm|{KW_CM})",
        clean,
        flags=re.IGNORECASE,
    )
    if m:
        tb = float(m.group(1))
        lr = float(m.group(2))
        return {"top": tb, "bottom": tb, "left": lr, "right": lr}
    return None


def _parse_heading_align(clean: str, level_label: str) -> str | None:
    # Keep this strict to avoid false matches from nearby unrelated wording.
    m = re.search(level_label + rf".{{0,24}}(?:\u5bf9\u9f50|\u6392\u7248|\u683c\u5f0f).{{0,12}}({KW_CENTER}|{KW_LEFT_ALIGN}|{KW_JUSTIFY})", clean)
    if not m:
        m = re.search(level_label + rf".{{0,16}}({KW_CENTER}|{KW_LEFT_ALIGN}|{KW_JUSTIFY})", clean)
    if not m:
        return None
    token = m.group(1)
    if token == KW_CENTER:
        return "center"
    if token == KW_LEFT_ALIGN:
        return "left"
    return "justify"


def extract_rules_from_text(text: str | None = None) -> dict:
    rules = deepcopy(DEFAULT_RULES)
    if not text:
        return rules

    clean = re.sub(r"\s+", "", text)
    lower = clean.lower()

    margins = _extract_margins(clean)
    if margins:
        rules["margins_cm"].update(margins)

    if KW_BODY in clean:
        if ZH_SONGTI in clean:
            rules["body"]["font"] = ZH_SONGTI
        elif ZH_FANGSONG in clean:
            rules["body"]["font"] = ZH_FANGSONG

    sz = _cn_numeral_size_to_pt(clean)
    if sz is not None and ((KW_BODY in clean) or ("\u5c0f\u56db" in clean)):
        rules["body"]["size_pt"] = sz

    if KW_LS_15 in clean:
        rules["body"]["line_spacing"] = 1.5
        rules["english"]["line_spacing"] = 1.5
    elif KW_LS_125 in clean:
        rules["body"]["line_spacing"] = 1.25
        rules["english"]["line_spacing"] = 1.25
    elif KW_LS_SINGLE in clean:
        rules["body"]["line_spacing"] = 1.0
        rules["english"]["line_spacing"] = 1.0

    h1_align = _parse_heading_align(clean, KW_LV1)
    # Keep H2/H3 stable unless explicitly stated. Many school guides only define H1 alignment.
    h2_align = None
    h3_align = None
    if h1_align:
        rules["heading_1"]["align"] = h1_align
    if h2_align:
        rules["heading_2"]["align"] = h2_align
    if h3_align:
        rules["heading_3"]["align"] = h3_align

    if (KW_TOC in clean) or (KW_TOC_ALT in clean):
        rules["required_sections"]["toc"] = True
    if (KW_ZH_KW in clean) or (KW_ZH_KW_ALT in clean):
        rules["required_sections"]["zh_keywords"] = True
    if (KW_EN_ABS in clean) or (KW_FOREIGN_ABS in clean) or ("abstract" in lower):
        rules["required_sections"]["en_abstract"] = True
    if (KW_EN_KW in clean) or (KW_FOREIGN_KW in clean) or ("keywords" in lower):
        rules["required_sections"]["en_keywords"] = True

    min_chars = _extract_min_chars(clean)
    if min_chars:
        rules["min_total_chars_no_space"] = min_chars

    return rules
