# Paper Format Agent

Local-first academic paper formatting for DOCX files, packaged as both a Python tool and an agent skill.

Paper Format Agent extracts formatting rules from a guide, applies deterministic DOCX repairs, and produces machine-readable plus human-readable reports. It is built for thesis, journal, and conference formatting workflows where privacy and content preservation matter.

## Why This Exists

Academic formatting is tedious, repetitive, and hard to review manually. This project focuses on formatting-only automation:

- margins, fonts, line spacing, headings, captions, tables, and references
- required section checks such as abstracts, keywords, and table of contents
- content fingerprint guards to detect accidental academic content changes
- local execution for private papers and school templates
- reports that can be used by students, supervisors, reviewers, and CI

## Agent Skill

This repository includes a top-level [SKILL.md](SKILL.md) and [agents/openai.yaml](agents/openai.yaml), so agent users can treat the repo as an installable skill.

The skill teaches an agent how to:

- inspect input files safely
- run the formatter in content-preserving mode
- review `format_report.json`
- validate changes before returning results
- add new template rules with tests

## Quick Start

```bash
pip install -r requirements.txt

python -m paper_format_agent.cli \
  --format-file "format_guide.docx" \
  --paper-file "paper.docx" \
  --out-dir "./output" \
  --engine auto \
  --strict-required-sections
```

Optional GUI:

```bash
python run_gui.py
```

## Outputs

| File | Purpose |
| --- | --- |
| `formatted_paper_v3.docx` | repaired DOCX document |
| `format_rules.json` | extracted formatting rules |
| `format_report.json` | machine-readable score and checks |
| `format_report.html` | human-readable report |
| `modify_log.json` | formatting operation log |
| `engine_report.json` | Word COM / LibreOffice / Python post-process result |
| `marker_dump.json` | optional paragraph classification dump |

## Safety Model

By default, the pipeline enforces a content guard. Reports include:

- `content_changed`
- `content_guard_enforced`
- `content_fingerprint_before`
- `content_fingerprint_after`

For normal academic formatting, `content_changed` should be `false`.

## Validation

```bash
python tools/validate_skill.py
python -m unittest discover -s tests -p "test_*.py"
python tools/compile_check.py
```

## Good First PRs

We want many small, reviewable PRs. Good contribution areas:

- Add a synthetic test for a school, journal, or conference formatting rule.
- Improve a narrowly scoped rule extractor.
- Add scoring coverage for tables, figures, references, equations, headers, or footers.
- Improve report wording or diagnostics.
- Add local-first integrations such as MCP, GitHub Actions, or batch processing.
- Improve this repo's `SKILL.md` workflow for agent users.

See [CONTRIBUTING.md](CONTRIBUTING.md), [ROADMAP.md](ROADMAP.md), and [AGENTS.md](AGENTS.md).

## Architecture

```text
format guide + paper.docx
  -> rule extraction
  -> paragraph type tagging
  -> style application
  -> numbering cleanup
  -> optional engine post-process
  -> scoring and reports
```

Detailed notes:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/PRODUCTION_STANDARD.md](docs/PRODUCTION_STANDARD.md)
- [README_V3.md](README_V3.md)

## Privacy

Do not commit real papers, private school templates, reviewer comments, API keys, or generated documents. Use synthetic fixtures or anonymized snippets in tests.

## License

MIT. See [LICENSE](LICENSE).
