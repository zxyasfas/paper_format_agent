from __future__ import annotations

from pathlib import Path
from typing import Any


OFFICE_OR_RENDERED_SUFFIXES = {".doc", ".docx", ".pdf"}
SECRET_SUFFIXES = {".pem", ".key"}
GENERATED_DIR_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
LOCAL_OUTPUT_DIR_PARTS = {"sample_output", "output", "outputs"}
ALLOWED_BINARY_PREFIXES = ("docs/fixtures/", "tests/fixtures/")


def audit_release_paths(paths: list[str]) -> list[dict[str, Any]]:
    """Return release-blocking repository hygiene findings for tracked paths."""
    findings: list[dict[str, Any]] = []
    for raw_path in sorted(paths):
        normalized = raw_path.replace("\\", "/")
        path = Path(normalized)
        parts = set(path.parts)
        suffix = path.suffix.lower()

        if _is_under_allowed_binary_prefix(normalized):
            continue
        if path.name.startswith("tmp_"):
            findings.append(_finding(normalized, "local_scratch", "Local scratch files should not be tracked."))
            continue
        if parts & GENERATED_DIR_PARTS:
            findings.append(_finding(normalized, "python_cache", "Python/cache artifacts should not be tracked."))
            continue
        if parts & LOCAL_OUTPUT_DIR_PARTS:
            findings.append(_finding(normalized, "local_output", "Generated output folders should not be tracked."))
            continue
        if suffix in OFFICE_OR_RENDERED_SUFFIXES:
            findings.append(
                _finding(
                    normalized,
                    "office_or_rendered_artifact",
                    "DOC/DOCX/PDF files may contain private papers or generated artifacts.",
                )
            )
            continue
        if suffix in SECRET_SUFFIXES or path.name.startswith(".env"):
            findings.append(_finding(normalized, "secret_like_file", "Secret-like files should not be tracked."))
    return findings


def _is_under_allowed_binary_prefix(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in ALLOWED_BINARY_PREFIXES)


def _finding(path: str, category: str, message: str) -> dict[str, Any]:
    return {
        "path": path,
        "category": category,
        "message": message,
    }
