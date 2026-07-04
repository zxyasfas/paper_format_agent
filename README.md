# Paper Format Agent

[中文说明](README.zh-CN.md) | English

![Local-first](https://img.shields.io/badge/local--first-DOCX-blue)
![Content Guard](https://img.shields.io/badge/content--guard-enabled-green)
![Python](https://img.shields.io/badge/python-3.9%2B-3776AB)
![CI](https://github.com/zxyasfas/paper_format_agent/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**An open-source DOCX formatter for academic papers that can prove it didn't rewrite your text.**

Paper Format Agent reformats a thesis or paper — fonts, indents, alignment, spacing, headings, captions — to match a target format guide, and it ships with a verifiable content fingerprint so you can confirm the wording of your paper came out unchanged. It compares a fingerprint of your body and table text (with whitespace and stray bullet characters normalized out) before and after formatting; the run is **fail-closed**, so if that text changed it aborts instead of writing a file. Everything runs locally on your machine. It's also packaged as an installable agent skill ([SKILL.md](SKILL.md) + [agents/openai.yaml](agents/openai.yaml)), so tools like Claude Code or Codex CLI can invoke it directly instead of a human clicking through a GUI.

## Proof, not a promise

Real fields from an actual run (`--engine python`, the fully-guarded path), taken from the produced `format_report.json`:

```json
{
  "content_fingerprint_before": "793e6533fd670418141d11fdcf014be19750408129ecff8b1b78a2641a3786db",
  "content_fingerprint_after":  "793e6533fd670418141d11fdcf014be19750408129ecff8b1b78a2641a3786db",
  "content_changed": false,
  "content_guard_enforced": true
}
```

The before/after fingerprints match, and a paragraph-by-paragraph `.text` comparison I ran across the whole document confirms every word survived. What *did* change on that same file: body text went from unset font/indent/alignment to SimSun (宋体) 12pt, a 2-character first-line indent, and justified alignment; the abstract title became SimSun 18pt centered; the Chinese keywords line became SimSun 12pt left-aligned. The same run also reported the real problems it found — `char_below_min` (document under the guide's minimum length) and `blank_page_risk` — rather than silently claiming a perfect score.

## Why This Exists

Every closed-source formatting service (论文无忧, WPS 论文排版, 大以论文, AIPoliDoc, and similar) asks you to *trust* that your content survives the reformatting pass — none of them let you verify it.

- The content guard is the smallest honest promise: change the formatting, but not the wording of your body and table text — and if that can't be confirmed, the run aborts with an error (`content guard failed`) instead of shipping a silently-altered document. It's fail-closed and enforced by default. (Scope: it normalizes whitespace and stray bullet characters before comparing, and covers body paragraphs and tables; headers and footers, which the formatter sets on purpose, are out of scope. The fully-guarded path is `--engine python`; other engines run a local post-processor, e.g. to refresh the table of contents, after the check.)
- Open-source and auditable: read the code, or just diff the fingerprint yourself.
- Formatting-only automation across margins, fonts, line spacing, headings, captions, tables, and references, plus required-section checks (abstracts, keywords, table of contents) and running headers / centered page-number footers.
- Reports are usable by students, supervisors, reviewers, and CI.

## Status

This project is a practical open-source MVP. It is suitable for demos, internal pilots, agent workflows, and synthetic benchmark development. Before relying on it for high-stakes submissions, expand the regression corpus, template coverage, and object-level scoring for tables, figures, equations, footnotes, headers, and footers.

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

Batch processing:

```bash
python -m paper_format_agent.cli \
  --format-file "format_guide.docx" \
  --paper-dir "./papers" \
  --out-dir "./batch_output" \
  --engine python \
  --strict-required-sections
```

Batch mode writes one output folder per paper plus `batch_summary.json`, including pass rate, score averages, content-change count, and per-paper report locations.

## Template Packs And Synthetic Examples

The repository includes privacy-safe template packs and synthetic examples so users can try the workflow without uploading real papers:

- [templates/](templates/) contains JSON presets for Chinese thesis, journal article, and IEEE-style conference formatting.
- [examples/](examples/) contains a synthetic format guide and sample reports for demos, issues, and PRs.
- [docs/TEMPLATE_PACKS.md](docs/TEMPLATE_PACKS.md) explains the template contract and contribution checklist.

Template files are intentionally plain JSON. They are easy to review, easy to customize locally, and safe to extend through small PRs.

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
- `diagnostics` with severity, evidence, and suggested fixes for failed checks

For normal academic formatting, `content_changed` should be `false`.

## Validation

```bash
python tools/validate_skill.py
python -m unittest discover -s tests -p "test_*.py"
python tools/compile_check.py
python tools/release_audit.py
```

Before publishing from a local workspace, also run:

```bash
python tools/release_audit.py --include-local
```

This optional check includes untracked and ignored local artifacts, such as generated outputs, scratch files, caches, and private document formats.

## Good First PRs

We want many small, reviewable PRs. Good contribution areas:

- Add a synthetic test for a school, journal, or conference formatting rule.
- Add a new synthetic template pack in `templates/`.
- Improve a narrowly scoped rule extractor.
- Add scoring coverage for tables, figures, references, equations, headers, or footers.
- Improve report wording or diagnostics.
- Add local-first integrations such as MCP, GitHub Actions, or batch processing.
- Improve this repo's `SKILL.md` workflow for agent users.

New contributors can start from the task-ready board in
[docs/CONTRIBUTOR_TASKS.md](docs/CONTRIBUTOR_TASKS.md). Each task lists user
pain, expected PR shape, and suggested labels.

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
