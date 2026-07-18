<!-- mcp-name: io.github.zxyasfas/paper-format-agent -->

# Paper Format Agent

[中文说明](README.zh-CN.md) | English

![CI](https://github.com/zxyasfas/paper_format_agent/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

A local DOCX formatter for theses and papers.

It changes fonts, spacing, indents, headings and captions to match a format
guide. It does not rewrite the paper. Before saving, it compares a fingerprint
of the body and table text from before and after the run. If the text changed,
it aborts instead of writing the formatted file.

Everything runs on your machine. Nothing is uploaded.

## the content check

Report fields from a real run (`--engine python`):

```json
{
  "content_fingerprint_before": "793e6533fd670418141d11fdcf014be19750408129ecff8b1b78a2641a3786db",
  "content_fingerprint_after":  "793e6533fd670418141d11fdcf014be19750408129ecff8b1b78a2641a3786db",
  "content_changed": false,
  "content_guard_enforced": true
}
```

The two hashes should match. If they don't, the formatter exits with
`content guard failed` and the formatted DOCX is not written.

What the check covers: body paragraphs and tables, with whitespace and stray
bullet characters normalized before comparing. Headers and footers are out of
scope because the formatter sets those on purpose. Use `--engine python` when
the fingerprint must cover the final saved DOCX; the other engines run a local
post-processor after the check, e.g. to refresh the table of contents.

To watch the guard trip, run `python tools/demo_content_guard.py`. It formats
a synthetic paper, then repeats the run with the styling step patched to edit
one sentence of the in-memory document. The second run aborts without writing
the DOCX.

[docs/BENCHMARK.md](docs/BENCHMARK.md) tracks which authored strings survive
a run in small synthetic fixtures, and lists the known gaps.

## install and run

```bash
pip install -r requirements.txt

python -m paper_format_agent.cli \
  --format-file "format_guide.docx" \
  --paper-file "paper.docx" \
  --out-dir "./output" \
  --engine python
```

There is also a GUI (`python run_gui.py`), a batch mode, and JSON template
packs for Chinese thesis, journal and IEEE-style formats. See
[docs/USAGE.md](docs/USAGE.md).

## limits

Early project. Ordinary paragraphs, headings and tables work better than
equations, footnotes and complex layouts. With `--strict-required-sections`,
checks may include `char_below_min` or `blank_page_risk`. Do not use it as the
only check before a real submission. Keep your original file.

## why I made this

I did not want to upload an unfinished thesis to a formatting website, and I
wanted a way to check that formatting did not touch the text. So the default
engine runs locally and refuses to save if the text changed.

## agents

The repo doubles as an installable agent skill ([SKILL.md](SKILL.md)), and the
same pipeline is available as an optional MCP server (Python 3.10+):

```bash
pip install "paper-format-agent[mcp]"
paper-format-agent-mcp
```

Tools: `format_paper`, `extract_format_rules`, `score_paper`. Client config in
[docs/MCP.md](docs/MCP.md).

## contributing

Small PRs are welcome. Adding a synthetic test for a school or journal
formatting rule is a good place to start:
[docs/CONTRIBUTOR_TASKS.md](docs/CONTRIBUTOR_TASKS.md),
[CONTRIBUTING.md](CONTRIBUTING.md). Notes on the pipeline are in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

Do not commit real papers, private school templates, reviewer comments, API
keys or generated output. Synthetic fixtures only.

## license

MIT. See [LICENSE](LICENSE).
