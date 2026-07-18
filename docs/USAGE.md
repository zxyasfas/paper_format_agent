# Usage

## What it covers

Margins, fonts, line spacing, alignment, first-line indents, headings,
captions, tables, references, required-section checks (abstract, keywords,
table of contents), running headers and centered page-number footers.

## GUI

```bash
python run_gui.py
```

## Batch mode

```bash
python -m paper_format_agent.cli \
  --format-file "format_guide.docx" \
  --paper-dir "./papers" \
  --out-dir "./batch_output" \
  --engine python \
  --strict-required-sections
```

Writes one output folder per paper plus `batch_summary.json` with pass rate,
score averages, content-change count and per-paper report locations.

By default the scorer only checks sections that exist in the original paper.
With `--strict-required-sections`, missing required sections (abstract,
keywords, table of contents) count as failures.

## Engines

The main formatting pass always runs on python-docx. `--engine` picks an
optional post-processor on top of that: `auto` tries
`word-com -> libreoffice -> python` in that order. `word-com` needs Windows
with desktop Word installed, `libreoffice` needs `soffice` or `libreoffice`
on PATH, and `python` means keeping the python-docx result with no external
post-processing. Only the `python` path leaves the file untouched after the
fingerprint check.

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

Reports include `content_changed`, `content_guard_enforced`, both content
fingerprints, and `diagnostics` with severity and evidence for failed checks.

## Templates and examples

[../templates/](../templates/) has JSON presets for Chinese thesis, journal
article and IEEE-style conference formats. [../examples/](../examples/) has a
synthetic format guide and sample reports. The template contract is in
[TEMPLATE_PACKS.md](TEMPLATE_PACKS.md).

## Checks before a PR

```bash
python tools/validate_skill.py
python -m unittest discover -s tests -p "test_*.py"
python tools/compile_check.py
python tools/release_audit.py
```

`release_audit.py --include-local` also scans untracked and ignored local
artifacts such as generated outputs and caches.
