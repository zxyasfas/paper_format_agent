# Template Packs

This directory contains synthetic, privacy-safe template presets for common academic formatting scenarios.

The presets are intentionally stored as JSON so they can be reviewed, copied, and adapted without requiring real school or journal documents. They are examples of the rule shape that the formatter and future template registry should converge on.

## Included Presets

| File | Use Case | Notes |
| --- | --- | --- |
| `chinese-thesis-basic.json` | Chinese undergraduate or graduate thesis | Includes Chinese abstract, keywords, TOC, figure/table captions, headers, and page-number footers. |
| `journal-article-basic.json` | Journal article submission | Uses tighter margins, Times New Roman English text, required English abstract and keywords. |
| `ieee-conference-basic.json` | IEEE-style conference paper | Provides a compact two-column-oriented rule baseline for future layout support. |
| `synthetic-university-thesis-basic.json` | Fictional university thesis (English) | Uses a made-up institution (Northwind University) as a generic, privacy-safe starting point to adapt into a school-specific template. |

## How To Add A Template

1. Copy the closest JSON preset.
2. Change `template_id`, `display_name`, `scenario`, and `rules`.
3. Keep the sample synthetic. Do not copy private school templates or publisher PDFs into the repo.
4. Run:

```bash
python -m unittest tests.test_templates
python tools/release_audit.py --include-local
```

## Current Contract

Each template file should contain:

- `template_id`: stable lowercase identifier.
- `display_name`: user-facing name.
- `locale`: language or region hint.
- `scenario`: thesis, journal, conference, or another academic workflow.
- `rules`: formatter-compatible rule object.

The test suite validates that template files are JSON, contain required metadata, and include the core rule sections needed for scoring and repair.
