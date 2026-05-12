# Contributor Task Board

This board turns the roadmap into small PRs that are useful to users and easy to
review. Every task below can be completed with synthetic data only.

## Before You Start

Run the standard checks before opening a PR:

```bash
python tools/validate_skill.py
python -m unittest discover -s tests -p "test_*.py"
python tools/compile_check.py
```

Do not use real student papers, private school templates, generated DOCX/PDF
files, screenshots with private data, API keys, or local output folders.

## Good First Issues

### Add APA Reference Spacing Coverage

User pain: reference formatting is one of the most common rejection reasons for
course papers and journal submissions.

Expected PR:

- Add a short synthetic APA-style reference snippet.
- Add or update a test that checks spacing, indentation, or paragraph style.
- Keep the rule focused on references only.

Suggested labels: `good first issue`, `tests`, `references`.

### Add Chinese Thesis Abstract Keyword Variants

User pain: Chinese thesis templates often use slightly different labels such as
`关键词`, `关键字`, `Keywords`, or mixed Chinese/English abstract sections.

Expected PR:

- Add synthetic format-guide text covering two or three label variants.
- Add a test proving the required section check recognizes them.
- Do not add real school template text.

Suggested labels: `good first issue`, `rule-request`, `tests`.

### Add Figure Caption Diagnostics

User pain: users need to know which figure caption failed and what to change,
not only that the score dropped.

Expected PR:

- Add or improve one diagnostic for figure captions.
- Include evidence fields in the report when available.
- Add a synthetic failing case.

Suggested labels: `help wanted`, `scoring`, `reporting`.

### Add Table Caption Diagnostics

User pain: table captions are often required to appear above tables with a
specific numbering style.

Expected PR:

- Add one focused table-caption check or improve an existing message.
- Include an actionable suggested fix.
- Add a synthetic failing case.

Suggested labels: `help wanted`, `scoring`, `reporting`.

### Add A Synthetic University Thesis Template Pack

User pain: users want a ready-to-edit template pack before adapting the tool to
their own school.

Expected PR:

- Add `templates/synthetic-university-thesis-basic.json`.
- Keep values generic and public-safe.
- Update `templates/README.md` if the template list changes.
- Ensure template tests still pass.

Suggested labels: `good first issue`, `templates`.

### Improve Failed-Check Wording In HTML Reports

User pain: a failed formatting check should explain what failed, where it was
found, and what the user can do next.

Expected PR:

- Improve one report phrase or diagnostic section.
- Keep the HTML output simple and local.
- Update the sample report only if it is generated from safe synthetic data.

Suggested labels: `good first issue`, `reporting`, `docs`.

### Add GitHub Actions Example For Format Checks

User pain: labs and classes may want formatting checks in CI without uploading
papers to a third-party service.

Expected PR:

- Add a small documented workflow example that uses synthetic input paths.
- Make clear that real papers should not be committed to the repo.
- Keep the example optional and local-first.

Suggested labels: `help wanted`, `ci`, `docs`.

## Larger Follow-Up Areas

- Object-level scoring for equations, footnotes, headers, and footers.
- Versioned template packs for schools, journals, and conferences.
- PDF render-and-compare visual QA.
- Minimal MCP wrapper for local agent integration.
- Batch-mode benchmark reports using synthetic documents.
