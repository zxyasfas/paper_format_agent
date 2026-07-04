---
name: Good first contributor task
about: A small, privacy-safe task that is suitable for a first PR
title: ""
labels: "good first issue, help wanted"
assignees: ""
---

## User Pain

What real formatting problem does this help users solve?

## Expected PR

- [ ] Keep the change narrow.
- [ ] Use only synthetic examples or fixtures.
- [ ] Add or update tests when behavior changes.
- [ ] Update docs or samples only when user-facing behavior changes.

## Suggested Files

- `tests/`
- `templates/`
- `paper_format_agent/`
- `docs/`

## Acceptance Criteria

- [ ] `python tools/validate_skill.py`
- [ ] `python -m unittest discover -s tests -p "test_*.py"`
- [ ] `python tools/compile_check.py`

## Privacy Checklist

- [ ] No real student papers.
- [ ] No private templates.
- [ ] No generated DOCX/PDF files.
- [ ] No API keys, tokens, or local output folders.
