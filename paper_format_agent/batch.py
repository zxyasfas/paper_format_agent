from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any


GENERATED_DOCX_NAMES = {
    "formatted_paper_v3.docx",
    "formatted_paper_95plus.docx",
    "paper_llm_enhanced.docx",
}


def discover_paper_files(paper_dir: str | Path, pattern: str = "*.docx") -> list[Path]:
    """Find user paper DOCX files in a stable order for batch processing."""
    root = Path(paper_dir)
    if not root.exists():
        raise FileNotFoundError(f"paper directory does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"paper directory is not a directory: {root}")

    papers: list[Path] = []
    for path in root.rglob(pattern):
        if not path.is_file():
            continue
        if path.suffix.lower() != ".docx":
            continue
        if path.name.startswith("~$") or path.name in GENERATED_DOCX_NAMES:
            continue
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        papers.append(path)
    return sorted(papers, key=lambda item: str(item.relative_to(root)).lower())


def make_case_output_dir(output_root: str | Path, paper_file: str | Path, paper_dir: str | Path) -> Path:
    """Build a deterministic, collision-resistant output folder for a paper."""
    root = Path(paper_dir)
    paper = Path(paper_file)
    try:
        relative = paper.relative_to(root)
    except ValueError:
        relative = Path(paper.name)

    parts = list(relative.parts)
    parts[-1] = Path(parts[-1]).stem
    safe_parts = [_safe_path_part(part) for part in parts]
    digest = hashlib.sha1(str(relative).replace("\\", "/").encode("utf-8")).hexdigest()[:8]
    return Path(output_root) / f"{'__'.join(safe_parts)}__{digest}"


def summarize_batch(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Create a compact machine-readable summary for a batch run."""
    total = len(results)
    failed = [item for item in results if not item.get("ok")]
    score_before = _average(item.get("score_before") for item in results)
    score_after = _average(item.get("score_after") for item in results)
    return {
        "total": total,
        "passed": total - len(failed),
        "failed": len(failed),
        "pass_rate": round(((total - len(failed)) / total) * 100, 2) if total else 0.0,
        "content_changed_count": sum(1 for item in results if item.get("content_changed")),
        "average_score_before": score_before,
        "average_score_after": score_after,
        "average_score_improvement": (
            round(score_after - score_before, 1) if score_before is not None and score_after is not None else None
        ),
        "results": results,
    }


def _safe_path_part(part: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", part).strip("-._")
    return value or "paper"


def _average(values: Iterable[object]) -> float | None:
    numbers: list[float] = []
    for value in values:
        if value is None:
            continue
        try:
            numbers.append(float(value))
        except (TypeError, ValueError):
            continue
    if not numbers:
        return None
    return round(sum(numbers) / len(numbers), 1)
