---
name: paper-format-agent
description: Use this skill when a user needs to inspect, score, repair, or regression-test academic paper formatting in DOCX files, especially thesis, journal, or conference documents with a separate format specification. The skill guides Codex through local-first document handling, rule extraction, formatting repair, report review, and contribution-safe validation.
---

# Paper Format Agent

Use this skill for local-first academic document formatting work. It is designed for `.docx` papers and a separate format specification in `.docx`, `.doc`, or `.txt`.

## Safety Defaults

- Never upload private papers or format guides to external services unless the user explicitly asks for it.
- Treat student papers, manuscripts, reviewer comments, and school templates as sensitive data.
- Do not change academic content unless the user explicitly opts in. Default to formatting-only changes.
- Keep reports and generated documents in a user-provided output directory.

## Standard Workflow

1. Confirm the input files:
   - `--format-file`: format guide or template text.
   - `--paper-file`: source paper, currently `.docx`.
   - `--out-dir`: output directory for reports and generated documents.
2. Run the CLI in formatting-only mode:

```bash
python -m paper_format_agent.cli \
  --format-file "format_guide.docx" \
  --paper-file "paper.docx" \
  --out-dir "./output" \
  --engine auto \
  --strict-required-sections
```

3. Inspect generated artifacts:
   - `formatted_paper_v3.docx`: repaired document.
   - `format_rules.json`: extracted rules.
   - `format_report.json`: machine-readable score and checks.
   - `format_report.html`: human-readable report.
   - `modify_log.json`: formatting operations.
   - `engine_report.json`: post-processing engine result.

## Reviewing Format Reports

### Reading `format_report.json`

Open `format_report.json` first after every run. The key fields to examine:

- **`score`** (0–100): overall formatting compliance. Lower scores mean more issues to investigate.
- **`checks`**: array of per-check results. Each check has:
  - `check`: check name (e.g. `margins`, `line_spacing`, `required_sections`).
  - `status`: `pass` or `fail`. A single `fail` lowers the score.
  - `details`: human-readable explanation of what was found versus what was expected.
  - `expected` / `actual`: values for the checked property, when applicable.
- **`content_guard`**: object with two boolean fields:
  - `content_changed`: `true` only if the tool modified actual academic text (not just formatting).
  - `content_guard_enforced`: `true` when the guard was active during the run.
- **`engine`**: which engine ran (e.g. `auto`, `python-docx`).
- **`errors`**: array of runtime errors. Any entries here need investigation before delivering results.

**Review workflow:** Scan checks with `status: "fail"` first. Read their `details` to understand what did not match. Cross-reference with the priority list below to decide what to fix.

### Handling Content Guard Failures

If `content_guard.content_changed` is `true`:

1. **Stop and confirm with the user.** A content guard failure means the tool may have altered paper text, equations, or reference text. Do not deliver the repaired document until this is resolved.
2. **Check `modify_log.json`** for the specific operations that triggered the change. The `modify_log.json` contains a timestamped list of every modification, including a `type` field and a `reason` field.
3. **Compare the original and repaired documents** side by side if the user provides both. Look for changed words, removed content, or relocated sections.
4. **If the change was intentional and safe** (e.g. the user explicitly asked for content replacement), confirm with the user and note the exception in your summary.
5. **If the change was unintentional**, revert by rerunning with `--preserve-content` (if supported) or by applying only formatting operations manually. Report the false positive as a GitHub issue with the smallest reproducing input.

### Review Priority

When reviewing output, prioritize issues in this order:

1. Content changed unexpectedly (see content guard handling above).
2. Required sections or headings were misclassified.
3. Page setup, margins, fonts, or line spacing are wrong.
5. Captions, references, tables, or numbering look wrong.
6. Report wording or score explanation is unclear.

## Validation

Run these before handing work back:

```bash
python tools/validate_skill.py
python -m unittest discover -s tests -p "test_*.py"
python tools/compile_check.py
python tools/release_audit.py
```

### What Each Validation Step Checks

- **`tools/validate_skill.py`**: Verifies that `SKILL.md` front matter, section structure, and required code blocks follow the expected format for agent consumption. Fix any warnings this script reports before proceeding.
- **`python -m unittest discover -s tests`**: Runs the project test suite. All tests should pass. If any fail, read the test name and error message to determine whether the failure is in your change or in a pre-existing test.
- **`tools/compile_check.py`**: Ensures the Python package can be imported and all modules compile without errors. A failed import or syntax error here blocks delivery.
- **`tools/release_audit.py`**: Audits the repository for release-readiness: version consistency, changelog entries, and required metadata files. Non-fatal warnings should be noted; errors should be fixed.

If any validation step fails, investigate the output before proceeding. Do not deliver results while validation is red.

## When Adding Template Support

- Add the smallest representative rule text needed to reproduce the behavior.
- Prefer deterministic rule extraction over LLM-only interpretation.
- Add tests for extracted margins, font size, line spacing, required sections, headings, captions, or references.
- Do not commit real student documents. Use synthetic text or anonymized fixtures.

## Contribution-Friendly Tasks

Good first PRs usually fit one of these buckets:

- Add a synthetic test for a school, journal, or conference formatting rule.
- Improve a rule extractor with a narrowly scoped regex or parser.
- Improve report clarity without changing scoring semantics.
- Add a regression case to `docs/regression_manifest.sample.json`.
- Improve this skill workflow or `agents/openai.yaml` metadata.
