from __future__ import annotations

import hashlib
import re

from docx import Document


_BULLET_CHARS = "▪•●■◆◇◦·"


def normalize_for_content_guard(text: str) -> str:
    s = text or ""
    if not s:
        return ""
    # Ignore whitespace and common artifact bullets introduced by broken list metadata.
    s = re.sub(r"\s+", "", s)
    s = s.translate({ord(ch): None for ch in _BULLET_CHARS})
    return s


def build_content_fingerprint(doc: Document) -> str:
    parts: list[str] = []
    for p in doc.paragraphs:
        if p.text:
            parts.append(normalize_for_content_guard(p.text))
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                if cell.text:
                    parts.append(normalize_for_content_guard(cell.text))
    joined = "\n".join(parts)
    return hashlib.sha256(joined.encode("utf-8", errors="ignore")).hexdigest()

