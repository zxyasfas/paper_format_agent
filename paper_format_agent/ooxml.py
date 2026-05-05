"""OOXML 工具函数"""
from __future__ import annotations


def set_font_east_asia(run, font_name: str):
    """
    设置东亚字体（中文、日文、韩文）
    
    Args:
        run: docx Run 对象
        font_name: 字体名称，如 "宋体"、"黑体" 等
    """
    run.font.name = font_name
    # 设置东亚字体
    r = run._element
    rPr = r.get_or_add_rPr()
    
    # 创建或更新 w:rFonts 元素
    from docx.oxml import OxmlElement
    rFonts = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts')
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    
    # 设置东亚字体
    rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia', font_name)
