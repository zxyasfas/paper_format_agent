"""Model Context Protocol (MCP) server for Paper Format Agent.

Exposes the same local, content-guarded formatting pipeline used by the CLI as
MCP tools, so an agent runtime (Claude Code, Codex CLI, or any MCP client) can
format academic DOCX papers directly.

The MCP SDK requires Python >= 3.10, so this module is optional: install it with

    pip install "paper-format-agent[mcp]"

and run the server with

    paper-format-agent-mcp

Every tool runs entirely on the local machine; no document content is uploaded.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - import guard for optional dependency
    raise ImportError(
        "The MCP server requires the 'mcp' package (Python >= 3.10). "
        'Install it with: pip install "paper-format-agent[mcp]"'
    ) from exc

from .rules import extract_rules_from_text
from .scorer import score_document
from .service import format_paper as _format_paper
from .service import read_format_text

mcp = FastMCP("paper-format-agent")


@mcp.tool()
def format_paper(
    format_file: str,
    paper_file: str,
    out_dir: str,
    engine: str = "python",
    strict_required_sections: bool = True,
) -> dict[str, Any]:
    """Reformat an academic paper DOCX to match a format guide, content-guarded.

    Extracts formatting rules from ``format_file`` (a .docx/.doc/.txt guide),
    applies them to ``paper_file`` (a .docx), and writes the formatted document
    plus reports into ``out_dir``. A content fingerprint of the body and table
    text is compared before and after; if that text changed, the run raises
    instead of writing a silently altered document (fail-closed).

    Args:
        format_file: Path to the formatting guide (.docx, .doc, or .txt).
        paper_file: Path to the paper to format (.docx).
        out_dir: Directory to write outputs into (created if missing).
        engine: Post-process engine. "python" is the fully content-guarded path;
            "auto"/"word-com"/"libreoffice" run a post-processor after the guard
            check (e.g. to refresh the table of contents).
        strict_required_sections: Enforce the guide's required sections (abstract,
            keywords, table of contents, etc.).

    Returns:
        A summary dict including score_before, score_after, content_changed,
        content_guard_enforced, both content fingerprints, and the output path.
        The full machine-readable report is written to
        ``<out_dir>/format_report.json``.
    """
    return _format_paper(
        paper_file,
        out_dir,
        format_file=format_file,
        engine=engine,
        strict_required_sections=bool(strict_required_sections),
    )


@mcp.tool()
def extract_format_rules(format_file: str) -> dict[str, Any]:
    """Extract structured formatting rules from a format guide, without changing any file.

    Reads ``format_file`` (a .docx/.doc/.txt guide) and returns the parsed rules
    (margins, fonts, sizes, line spacing, headings, required sections, etc.) as a
    JSON-serializable dict. Useful for previewing what the formatter will enforce.

    Args:
        format_file: Path to the formatting guide (.docx, .doc, or .txt).

    Returns:
        The extracted rules dictionary.
    """
    return extract_rules_from_text(read_format_text(format_file))


@mcp.tool()
def score_paper(
    paper_file: str,
    format_file: str,
    strict_required_sections: bool = True,
) -> dict[str, Any]:
    """Score a paper against a format guide read-only, without modifying it.

    Reads-only: extracts rules from ``format_file`` and scores ``paper_file``
    against them, returning the score, per-check penalties, and actionable
    diagnostics. Does not write or alter any file.

    Args:
        paper_file: Path to the paper to score (.docx).
        format_file: Path to the formatting guide (.docx, .doc, or .txt).
        strict_required_sections: Enforce the guide's required sections.

    Returns:
        The scoring report dict (score, penalties, diagnostics).
    """
    rules = extract_rules_from_text(read_format_text(format_file))
    return score_document(
        Path(paper_file),
        rules,
        baseline_docx=Path(paper_file),
        enforce_required_sections=bool(strict_required_sections),
    )


def main() -> None:
    """Entry point for the ``paper-format-agent-mcp`` console script (stdio transport)."""
    mcp.run()


if __name__ == "__main__":
    main()
