# Agent Instructions

This repository contains a local-first academic paper formatting agent. Keep changes narrow, deterministic, and test-backed.

## Commands

```bash
python tools/validate_skill.py
python -m unittest discover -s tests -p "test_*.py"
python tools/compile_check.py
```

## Guardrails

- Do not commit real papers, private templates, API keys, generated DOCX/PDF files, or local output folders.
- Preserve content by default. Formatting changes must not rewrite academic prose unless a user explicitly opts in.
- Prefer synthetic fixtures and short rule snippets in tests.
- When adding a new format rule, include a test that fails without the change.

## High-Value PR Areas

- Template rules for more schools, journals, and conferences.
- DOCX inspection and scoring coverage for tables, figures, equations, references, headers, and footers.
- Better reports that explain what failed and how to fix it.
- Local-only integrations such as MCP, GitHub Actions, and batch processing.
