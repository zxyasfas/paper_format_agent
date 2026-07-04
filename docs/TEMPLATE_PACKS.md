# Template Packs

Template packs are the main path for turning Paper Format Agent from a local demo into a useful academic formatting project. They make the project searchable, easy to fork, and easy for contributors to extend without sharing private papers.

## Goals

- Keep real papers and private school templates out of the repository.
- Store synthetic template rules in a simple reviewable format.
- Make school, journal, and conference support incremental.
- Give users a starting point for local customization.
- Give contributors small PRs that can be validated in CI.

## Repository Layout

```text
templates/
  README.md
  chinese-thesis-basic.json
  journal-article-basic.json
  ieee-conference-basic.json

examples/
  README.md
  synthetic_format_guide.md
  sample_format_report.json
  sample_format_report.md
```

## Template Shape

Each template JSON file contains metadata and a formatter-compatible `rules` object:

```json
{
  "template_id": "chinese-thesis-basic",
  "display_name": "Chinese Thesis Basic",
  "locale": "zh-CN",
  "scenario": "thesis",
  "rules": {
    "paper_size": "A4",
    "margins_cm": {
      "top": 2.54,
      "bottom": 2.54,
      "left": 3.17,
      "right": 2.54
    }
  }
}
```

## Contribution Checklist

When adding a template:

- Use synthetic wording and values, or values that are common public formatting requirements.
- Do not copy a private school guide, journal PDF, or real submission checklist.
- Include core sections: `margins_cm`, `body`, `english`, headings, captions, `header`, `footer`, and `required_sections`.
- Add or update tests if the template relies on a new rule shape.
- Run:

```bash
python -m unittest tests.test_templates
python tools/release_audit.py --include-local
```

## Roadmap

Near-term template work should focus on:

- More Chinese thesis variants: undergraduate, professional master, academic master.
- Journal submission variants: double-spaced review manuscript, camera-ready manuscript.
- Conference variants: IEEE-style and ACM-style synthetic baselines.
- Rule coverage for references, equations, footnotes, table bodies, and figure placement.
- A CLI flag to load a template pack directly, for example `--template chinese-thesis-basic`.
