from __future__ import annotations
from copy import deepcopy
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph


def set_cell_text_direction_normal(_cell):
    # placeholder for future vertical-text cleanup
    return


def set_font_east_asia(run, font_name: str) -> None:
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.append(rfonts)
    rfonts.set(qn('w:eastAsia'), font_name)
    rfonts.set(qn('w:ascii'), font_name)
    rfonts.set(qn('w:hAnsi'), font_name)
    rfonts.set(qn('w:cs'), font_name)


def delete_paragraph(paragraph: Paragraph) -> None:
    p = paragraph._element
    parent = p.getparent()
    if parent is not None:
        parent.remove(p)
    paragraph._p = paragraph._element = None


def insert_paragraph_after(paragraph: Paragraph, text: str = "", style=None) -> Paragraph:
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    new_para = Paragraph(new_p, paragraph._parent)
    if text:
        new_para.add_run(text)
    if style:
        new_para.style = style
    return new_para


def add_field_to_paragraph(paragraph: Paragraph, instr: str, placeholder: str = "") -> None:
    run = paragraph.add_run()
    fld_begin = OxmlElement('w:fldChar')
    fld_begin.set(qn('w:fldCharType'), 'begin')
    run._r.append(fld_begin)

    instr_text = OxmlElement('w:instrText')
    instr_text.set(qn('xml:space'), 'preserve')
    instr_text.text = instr
    run._r.append(instr_text)

    fld_sep = OxmlElement('w:fldChar')
    fld_sep.set(qn('w:fldCharType'), 'separate')
    run._r.append(fld_sep)

    if placeholder:
        t = OxmlElement('w:t')
        t.text = placeholder
        run._r.append(t)

    fld_end = OxmlElement('w:fldChar')
    fld_end.set(qn('w:fldCharType'), 'end')
    run._r.append(fld_end)


def add_page_number(paragraph: Paragraph) -> None:
    paragraph.text = ""
    add_field_to_paragraph(paragraph, " PAGE ", "1")


def ensure_update_fields_on_open(doc) -> None:
    settings = doc.settings._element
    existing = settings.find(qn('w:updateFields'))
    if existing is None:
        update = OxmlElement('w:updateFields')
        update.set(qn('w:val'), 'true')
        settings.append(update)
    else:
        existing.set(qn('w:val'), 'true')


def set_page_number_format(sectPr, fmt: str, start: int | None = None) -> None:
    # Remove existing pageNumType then set a new one
    for el in list(sectPr):
        if el.tag == qn('w:pgNumType'):
            sectPr.remove(el)
    pg = OxmlElement('w:pgNumType')
    pg.set(qn('w:fmt'), fmt)
    if start is not None:
        pg.set(qn('w:start'), str(start))
    sectPr.append(pg)


def add_next_page_section_break_after(paragraph: Paragraph, template_sectPr, page_num_fmt: str, page_start: int | None = None) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    # Remove existing sectPr on this paragraph
    for el in list(pPr):
        if el.tag == qn('w:sectPr'):
            pPr.remove(el)
    sect = deepcopy(template_sectPr)
    # section break type: nextPage
    for el in list(sect):
        if el.tag == qn('w:type'):
            sect.remove(el)
    stype = OxmlElement('w:type')
    stype.set(qn('w:val'), 'nextPage')
    sect.insert(0, stype)
    set_page_number_format(sect, page_num_fmt, page_start)
    pPr.append(sect)
