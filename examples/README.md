# Examples

This directory contains synthetic examples that show what Paper Format Agent expects and produces. The examples are text and JSON only; no real papers, generated DOCX files, or private templates are stored here.

## Files

| File | Purpose |
| --- | --- |
| `synthetic_format_guide.md` | A small synthetic formatting guide that can be converted into rules during demos. |
| `sample_format_report.json` | A representative machine-readable report shape with score, diagnostics, and content guard fields. |
| `sample_format_report.md` | A human-readable version of the same report for README links and quick review. |

## Demo Flow

Use these examples to explain the workflow without exposing private academic material:

1. Start from a synthetic rule guide.
2. Run the formatter against a synthetic DOCX fixture created locally.
3. Inspect `format_report.json` for score, diagnostics, and content safety.
4. Share only the report shape and synthetic fixtures in issues or PRs.

Real `.docx`, `.doc`, `.pdf`, screenshots, and local output folders are intentionally ignored by the repository release audit.
