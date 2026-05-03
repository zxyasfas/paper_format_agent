from __future__ import annotations

import json
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

from .formatter import count_total_chars
from .rules import DEFAULT_RULES


def _cm_close(value, target, tol=0.08):
    return abs(value.cm - target) <= tol


def _norm(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def _iter_texts(doc: Document) -> list[str]:
    return [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]


def _has_toc_field(doc: Document) -> bool:
    xml = doc._element.xml
    return (" TOC " in xml or "TOC" in xml) and ("\\o" in xml or "w:instrText" in xml)


def _is_abstract_title(t: str) -> bool:
    return bool(re.fullmatch(r"摘\s*要", (t or "").strip()))


def _is_keyword_zh(t: str) -> bool:
    return bool(re.match(r"^(关键词|关键字)\s*[:：]", (t or "").strip()))


def _is_abstract_en(t: str) -> bool:
    return (t or "").strip().upper() == "ABSTRACT"


def _is_keyword_en(t: str) -> bool:
    return bool(re.match(r"^Keywords?\s*[:：]", (t or "").strip(), flags=re.IGNORECASE))


def _is_toc_title(t: str) -> bool:
    return _norm(t) in {"目录", "目錄", "目次"}


def _is_intro_title(t: str) -> bool:
    s = (t or "").strip()
    n = _norm(s)
    return ("绪论" in n) or ("引言" in n) or bool(re.match(r"^[一二三四五六七八九十]+、", s))


def _is_conclusion_title(t: str) -> bool:
    n = _norm(t)
    return ("结论" in n) or ("结语" in n)


def _is_references_title(t: str) -> bool:
    return "参考文献" in _norm(t)


def _is_author_bio_title(t: str) -> bool:
    n = _norm(t)
    return ("作者简介" in n) or ("作者簡介" in n)


def _is_ack_title(t: str) -> bool:
    n = _norm(t)
    return ("致谢" in n) or ("致謝" in n)


def _find_first_index(doc: Document, predicate) -> int | None:
    for i, p in enumerate(doc.paragraphs):
        if predicate((p.text or "").strip()):
            return i
    return None


def detect_sections(doc: Document):
    texts = _iter_texts(doc)
    return {
        "abstract": any(_is_abstract_title(t) for t in texts),
        "keyword": any(_is_keyword_zh(t) for t in texts),
        "english_abstract": any(_is_abstract_en(t) for t in texts),
        "english_keyword": any(_is_keyword_en(t) for t in texts),
        "toc": _has_toc_field(doc) or any(_is_toc_title(t) for t in texts),
        "intro": any(_is_intro_title(t) for t in texts),
        "conclusion": any(_is_conclusion_title(t) for t in texts),
        "references": any(_is_references_title(t) for t in texts),
        "author_bio": any(_is_author_bio_title(t) for t in texts),
        "ack": any(_is_ack_title(t) for t in texts),
    }


def _check_front_matter_order(doc: Document, rules: dict) -> tuple[bool, str]:
    idx_zh_abs = _find_first_index(doc, _is_abstract_title)
    idx_kw_zh = _find_first_index(doc, _is_keyword_zh)
    idx_en_abs = _find_first_index(doc, _is_abstract_en)
    idx_kw_en = _find_first_index(doc, _is_keyword_en)
    idx_toc = _find_first_index(doc, _is_toc_title)
    idx_body = _find_first_index(doc, _is_intro_title)

    # Missing front-matter items are handled by dedicated checks, so here only
    # enforce ordering when at least two items are present.
    present = [(name, idx) for name, idx in [
        ("zh_abs", idx_zh_abs),
        ("kw_zh", idx_kw_zh),
        ("en_abs", idx_en_abs),
        ("kw_en", idx_kw_en),
        ("toc", idx_toc),
    ] if idx is not None]
    if len(present) < 2:
        return True, "front-matter items not enough to validate order"

    front_order = rules.get("front_matter_order") or ["abstract", "keyword", "english_abstract", "english_keyword", "toc", "intro"]
    alias = {
        "abstract": "zh_abs",
        "keyword": "kw_zh",
        "english_abstract": "en_abs",
        "english_keyword": "kw_en",
        "toc": "toc",
    }
    expected_seq = [alias[x] for x in front_order if x in alias]
    if not expected_seq:
        expected_seq = ["zh_abs", "kw_zh", "en_abs", "kw_en", "toc"]
    expected_rank = {name: i + 1 for i, name in enumerate(expected_seq)}
    seq = sorted(present, key=lambda x: x[1])
    ranks = [expected_rank.get(name, 10_000) for name, _ in seq]
    in_order = all(ranks[i] <= ranks[i + 1] for i in range(len(ranks) - 1))
    if not in_order:
        return False, f"front-matter order invalid: {seq}, expected={expected_seq}"

    if idx_zh_abs is not None and idx_body is not None and idx_zh_abs > idx_body:
        return False, "中文摘要出现在正文之后"
    if idx_toc is not None and idx_body is not None and idx_toc > idx_body:
        return False, "目录出现在正文之后"

    return True, "front-matter order looks valid"


def _check_toc_residue_in_body(doc: Document) -> tuple[bool, str]:
    idx_body = _find_first_index(doc, _is_intro_title)
    if idx_body is None:
        return True, "body start not detected"

    residue = 0
    for p in doc.paragraphs[idx_body + 1 :]:
        t = (p.text or "").strip()
        if not t:
            continue
        # Typical manual TOC dot leaders leaking into body.
        if re.search(r"[\.·•…]{3,}\s*\d+\s*$", t):
            residue += 1
        elif re.match(r"^[一二三四五六七八九十]+、.+[\.·•…]{3,}\s*\d+\s*$", t):
            residue += 1
        elif re.match(r"^\d+(\.\d+)*\s+.+[\.·•…]{3,}\s*\d+\s*$", t):
            residue += 1

    return residue == 0, f"toc-like residue lines in body: {residue}"


def _check_forced_page_break_anomaly(doc: Document) -> tuple[bool, str]:
    allowed_title = lambda t: (
        _is_abstract_title(t)
        or _is_abstract_en(t)
        or _is_toc_title(t)
        or _is_references_title(t)
        or _is_author_bio_title(t)
        or _is_ack_title(t)
    )
    all_forced = 0
    unexpected = []
    for i, p in enumerate(doc.paragraphs):
        if p.paragraph_format.page_break_before:
            all_forced += 1
            if not allowed_title((p.text or "").strip()):
                unexpected.append(i)
    # Too many forced breaks usually means style inheritance bug.
    passed = (len(unexpected) <= 1) and (all_forced <= 12)
    detail = f"forced={all_forced}, unexpected={len(unexpected)}, idx={unexpected[:8]}"
    return passed, detail


def score_document(docx_path: str | Path, rules: dict | None = None) -> dict:
    rules = rules or DEFAULT_RULES
    doc = Document(docx_path)
    checks: list[dict] = []

    def add(name: str, weight: float, passed: bool, detail: str = ""):
        checks.append({"name": name, "weight": weight, "passed": bool(passed), "detail": detail})

    # 1) 页面设置 10
    sec = doc.sections[0]
    add(
        "A4纸张",
        2,
        abs(sec.page_width.cm - 21.0) < 0.2 and abs(sec.page_height.cm - 29.7) < 0.2,
        f"{sec.page_width.cm:.2f} x {sec.page_height.cm:.2f} cm",
    )
    m = rules.get("margins_cm", {})
    add(
        "页边距符合规范",
        8,
        _cm_close(sec.top_margin, m.get("top", 2.54))
        and _cm_close(sec.bottom_margin, m.get("bottom", 2.54))
        and _cm_close(sec.left_margin, m.get("left", 2.54))
        and _cm_close(sec.right_margin, m.get("right", 2.17)),
        f"top={sec.top_margin.cm:.2f}, bottom={sec.bottom_margin.cm:.2f}, left={sec.left_margin.cm:.2f}, right={sec.right_margin.cm:.2f}",
    )

    # 2) 组成部分 15
    sections = detect_sections(doc)
    section_labels = [
        ("abstract", "中文摘要"),
        ("keyword", "关键词"),
        ("english_abstract", "英文摘要"),
        ("english_keyword", "英文关键词"),
        ("toc", "目录"),
        ("intro", "绪论/引言"),
        ("conclusion", "结论/结语"),
        ("references", "参考文献"),
        ("author_bio", "作者简介"),
        ("ack", "致谢"),
    ]
    for key, label in section_labels:
        add(f"组成部分：{label}", 1.5, sections[key])

    # 3) 字数 10
    chars = count_total_chars(doc)
    min_chars = int(rules.get("min_total_chars_no_space", 20000))
    add(f"字数不少于{min_chars}", 10, chars >= min_chars, f"{chars} 字符")

    # 4) 样式 25
    body_ok = 0
    body_total = 0
    for p in doc.paragraphs:
        t = (p.text or "").strip()
        if not t or len(t) < 15:
            continue
        if p.style and p.style.name.startswith("Heading"):
            continue
        if _is_abstract_title(t) or _is_abstract_en(t) or _is_toc_title(t):
            continue
        body_total += 1
        spacing = p.paragraph_format.line_spacing
        if isinstance(spacing, (int, float)) and abs(spacing - 1.25) < 0.05:
            body_ok += 1
    add("正文行距大部分为1.25倍", 8, body_total == 0 or body_ok / body_total >= 0.8, f"{body_ok}/{body_total}")

    heading1 = [p for p in doc.paragraphs if p.style and p.style.name == "Heading 1"]
    heading2 = [p for p in doc.paragraphs if p.style and p.style.name == "Heading 2"]
    heading3 = [p for p in doc.paragraphs if p.style and p.style.name == "Heading 3"]
    add("一级标题应用Heading 1", 5, len(heading1) >= 5, f"{len(heading1)} 个")
    add("二级标题应用Heading 2", 5, len(heading2) >= 4, f"{len(heading2)} 个")
    add("三级标题应用Heading 3", 4, len(heading3) >= 8, f"{len(heading3)} 个")

    abstract_para = next((p for p in doc.paragraphs if _is_abstract_title((p.text or "").strip())), None)
    add(
        "摘要标题居中",
        3,
        abstract_para is not None and abstract_para.alignment == WD_ALIGN_PARAGRAPH.CENTER,
        "检测摘要标题对齐",
    )

    # 5) 目录域 8
    add("目录为自动目录域", 8, _has_toc_field(doc))

    # 6) 页眉页脚与页码元数据 12
    header_text = "\n".join((p.text or "") for s in doc.sections for p in s.header.paragraphs)
    footer_xml = "\n".join(s.footer._element.xml for s in doc.sections)
    add("页眉已设置", 4, bool(header_text.strip()), header_text[:80])
    add("页脚页码字段已设置", 4, "PAGE" in footer_xml, "检测PAGE域")
    add("页码格式元数据存在", 4, "pgNumType" in doc._element.xml, "检测pgNumType")

    # 7) 表格/参考文献/关键词 10
    add("表格存在", 3, len(doc.tables) >= 1, f"{len(doc.tables)} 个表格")
    full_text = "\n".join(_iter_texts(doc))
    refs = re.findall(r"\[\s*\d+\s*\]", full_text)
    add("参考文献条目可识别", 4, len(refs) >= 5, f"{len(refs)} 条")

    kw_line = next((t for t in _iter_texts(doc) if _is_keyword_zh(t)), "")
    kw_count = 0
    has_semicolon = False
    if kw_line:
        parts = re.split(r"[:：]", kw_line, maxsplit=1)
        body = parts[1] if len(parts) > 1 else ""
        has_semicolon = ("；" in body) or (";" in body)
        items = [x.strip() for x in re.split(r"[；;，,、]", body) if x.strip()]
        kw_count = len(items)
    add("中文关键词不少于5个且使用分号", 3, kw_count >= 5 and has_semicolon, f"{kw_count} 个")

    # 8) 结构异常防护 10（新增）
    order_ok, order_detail = _check_front_matter_order(doc, rules)
    add("结构顺序合理（前置部分不应跑到正文后）", 4, order_ok, order_detail)

    toc_residue_ok, toc_residue_detail = _check_toc_residue_in_body(doc)
    add("正文中无目录残留点线", 3, toc_residue_ok, toc_residue_detail)

    pb_ok, pb_detail = _check_forced_page_break_anomaly(doc)
    add("无异常强制分页（避免大面积空白）", 3, pb_ok, pb_detail)

    total_weight = sum(c["weight"] for c in checks)
    passed_weight = sum(c["weight"] for c in checks if c["passed"])
    score = round(passed_weight / total_weight * 100, 1) if total_weight else 0
    return {"score": score, "checks": checks, "chars_no_space": chars, "sections": sections}


def save_reports(report: dict, out_json: str | Path, out_html: str | Path):
    out_json = Path(out_json)
    out_html = Path(out_html)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = []
    for c in report["checks"]:
        mark = "✓" if c["passed"] else "✗"
        rows.append(
            f"<tr><td>{mark}</td><td>{c['name']}</td><td>{c['weight']}</td><td>{c.get('detail', '')}</td></tr>"
        )
    html = (
        "<!doctype html><html><head><meta charset='utf-8'><title>格式检测报告</title>"
        "<style>body{font-family:Arial,'Microsoft YaHei',sans-serif;max-width:1000px;margin:32px auto;line-height:1.6}"
        "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:8px}"
        "th{background:#f5f5f5}.score{font-size:30px;font-weight:bold}</style></head><body>"
        f"<h1>论文格式检测报告</h1><p class='score'>综合评分：{report['score']} / 100</p>"
        f"<p>不含空白字符数：{report['chars_no_space']}</p>"
        f"<h2>检测明细</h2><table><tr><th>结果</th><th>检测项</th><th>权重</th><th>说明</th></tr>{''.join(rows)}</table>"
        "<h2>说明</h2><p>评分为程序化检测结果，不等同于学校最终人工审核结论。</p>"
        "</body></html>"
    )
    out_html.write_text(html, encoding="utf-8")
