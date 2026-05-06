# Contributing

Thanks for helping improve Paper Format Agent. The best PRs are small, test-backed, and easy to review.

## Before You Open a PR

```bash
python tools/validate_skill.py
python -m unittest discover -s tests -p "test_*.py"
python tools/compile_check.py
```

## Privacy Rules

- Do not commit real student papers, reviewer notes, private templates, or generated output documents.
- Do not commit API keys, tokens, account data, or local `.env` files.
- Use synthetic snippets or anonymized fixtures.
- Keep formatting changes separate from academic content changes.

## Good First PRs

- Add a synthetic test for a school, journal, or conference rule.
- Improve one rule extractor, with before/after tests.
- Add a report explanation for an existing scoring check.
- Improve `SKILL.md` for agent workflows.
- Add a small regression manifest entry using fake files and documented expectations.

## Pull Request Shape

Include:

- Problem being solved.
- What changed.
- Validation commands and key output.
- Risk or rollback notes.
- Screenshots or report snippets when UI/report behavior changes.

## Style

- Prefer deterministic code over LLM-only behavior.
- Keep regex changes narrow and documented by tests.
- Keep reports explainable.
- Avoid broad refactors in feature PRs.

## Commit Messages

Examples:

- `fix(rules): parse 1.5x line spacing in thesis guide`
- `test(skill): validate openai metadata`
- `docs: add good first PR examples`
