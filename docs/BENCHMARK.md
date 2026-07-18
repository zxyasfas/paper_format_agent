# Text survival benchmark

`tools/benchmark_text_survival.py` builds four small synthetic DOCX files,
formats them with the pipeline, and checks that every authored string still
exists in the output document. It reports by category instead of one overall
number, and it lists known gaps instead of implying full coverage.

The pipeline runs with the content guard disabled here, so that a lost string
shows up as a `LOST` line in the table instead of aborting the run. The
guard's own changed flag is printed per document. Strict success is an exact
match; a `guard-equivalent` result means the string only matches after the
same whitespace and bullet normalization the guard itself uses. That fallback
shares code with the guard, so it is a warning, not an independent check.

The script exits 1 if any string is lost.

Run it:

```bash
python tools/benchmark_text_survival.py
```

Output from a run on 2026-07-18 (Python 3.9.19, python-docx 1.2.0, the tree
that introduced this file):

```text
zh_thesis  (guard changed flag: False)
  front matter: 3/3 exact
  headings: 3/3 exact
  body: 2/2 exact
  captions: 2/2 exact
  table cells: 4/4 exact
  references: 2/2 exact

en_paper  (guard changed flag: False)
  front matter: 3/3 exact
  headings: 2/2 exact
  body: 2/2 exact
  captions: 1/1 exact
  table cells: 4/4 exact
  references: 2/2 exact

toc_doc  (guard changed flag: False)
  manual toc: 3/3 exact
  headings: 2/2 exact
  body: 2/2 exact

bullet_doc  (guard changed flag: False)
  bullet-prefixed plain paragraphs: 3/3 exact
  body: 1/1 exact

4 documents, 17 category rows, 41 authored strings

known gaps, not a complete list (not generated, not verified):
  real Word lists (w:numPr numbering)
  field-based tables of contents
  merged or nested tables
  footnotes
  equations (OMML)
  text boxes
  tracked changes
  embedded objects

headers and footers are written by the formatter on purpose and are
outside the content guard, so they are not part of this benchmark.
```

## Scope and limitations

The four fixtures are small and synthetic. They cover what the harness can
build with python-docx: plain paragraphs, Chinese and English headings,
captions, unmerged 2x2 table cells, reference entries, a manual TOC block and
paragraphs with literal bullet characters. The bullet fixture is plain
paragraphs, not real Word lists, so the formatter's numbering cleanup path is
not exercised here.

The known-gaps list above is what we know is missing, not a promise that
everything else is covered. Files that rely on those objects should be
checked by hand until the harness grows.

If a run prints a `LOST` line on your machine, that is a bug. Please open an
issue and paste the output.
