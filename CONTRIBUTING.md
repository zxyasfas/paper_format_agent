# Contributing

Thanks for helping improve Paper Format Agent. The best PRs are narrow,
privacy-safe, test-backed, and easy to review in one sitting.

## Five-Minute Contributor Path

1. Pick an issue labeled `good first issue` or `help wanted`.
2. Read the matching file area in [docs/CONTRIBUTOR_TASKS.md](docs/CONTRIBUTOR_TASKS.md).
3. Create or update only synthetic fixtures, template JSON, docs, or the smallest
   code path needed for the issue.
4. Run the validation commands below.
5. Open a PR with the problem, change, validation output, and privacy checklist.

## Local Validation

Run these before opening a PR:

```bash
python tools/validate_skill.py
python -m unittest discover -s tests -p "test_*.py"
python tools/compile_check.py
```

If your change touches release packaging, examples, or ignored local artifacts, also run:

```bash
python tools/release_audit.py
```

## Privacy Rules

- Do not commit real student papers, reviewer notes, private templates, or generated output documents.
- Do not commit API keys, tokens, account data, screenshots with private data, or local `.env` files.
- Use short synthetic snippets, fake school names, fake article titles, and fake reference entries.
- Keep formatting changes separate from academic content changes.
- Preserve prose by default. A formatter PR should not rewrite academic content.

## High-Value PR Types

### Template Pack PR

Best for first-time contributors.

- Add one JSON template under `templates/`.
- Keep the rule names and values easy to audit.
- Add or update tests in `tests/test_templates.py` when needed.
- Mention whether the template is thesis, journal, conference, or class-paper oriented.

### Rule Extraction PR

Best when a format guide phrase is currently missed.

- Add a failing synthetic snippet or fixture first.
- Keep regex or parser changes narrow.
- Include before/after evidence in the PR body.
- Avoid adding broad language-model behavior for deterministic formatting rules.

### Scoring And Report PR

Best for user-facing quality.

- Add one check or one diagnostic explanation at a time.
- Include a synthetic failing case and the expected report output.
- Make the message actionable: what failed, where it failed, and how the user can fix it.

### Agent Workflow PR

Best for users running this as a skill.

- Improve `SKILL.md`, `agents/openai.yaml`, or local command guidance.
- Keep the workflow local-first and privacy-preserving.
- Validate with `python tools/validate_skill.py`.

## Good First PR Examples

- Add a synthetic APA reference spacing test.
- Add a Chinese thesis abstract and keyword variant test.
- Add a table caption diagnostic in `format_report.json`.
- Add a new template pack for a synthetic university thesis guide.
- Improve failed-check wording in `format_report.html`.
- Add a small regression manifest entry using fake file names and expected scores.

## Pull Request Shape

Include:

- Problem being solved.
- What changed.
- Validation commands and key output.
- Risk or rollback notes.
- Screenshots or report snippets when UI/report behavior changes.
- Privacy statement confirming no real papers, private templates, generated DOCX/PDF, or secrets are included.

## Review Expectations

- Small PRs are easier to merge than broad refactors.
- A rule change should include a test that fails without the change.
- A report change should show the old confusing output or describe the user pain.
- A template change should be synthetic and public-safe.
- Maintainers may ask for scope reduction before reviewing implementation details.

## Style

- Prefer deterministic code over LLM-only behavior.
- Keep regex changes narrow and documented by tests.
- Keep reports explainable.
- Avoid broad refactors in feature PRs.
- Use plain names for fixtures and templates so failures are easy to understand.

## Commit Messages

Examples:

- `fix(rules): parse 1.5x line spacing in thesis guide`
- `test(skill): validate openai metadata`
- `docs: add good first PR examples`
