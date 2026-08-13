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
4. Check the content guard fields in `format_report.json`:
   - `content_changed` should normally be `false`.
   - `content_guard_enforced` should normally be `true`.
5. If a rule is wrong, update rule extraction or scoring logic and add a minimal test case.

## Validation

Run these before handing work back:

```bash
python tools/validate_skill.py
python -m unittest discover -s tests -p "test_*.py"
python tools/compile_check.py
python tools/release_audit.py
```

## When Adding Template Support

- Add the smallest representative rule text needed to reproduce the behavior.
- Prefer deterministic rule extraction over LLM-only interpretation.
- Add tests for extracted margins, font size, line spacing, required sections, headings, captions, or references.
- Do not commit real student documents. Use synthetic text or anonymized fixtures.

## When Reviewing Output

Read `format_report.json` first, then inspect `format_report.html` if the user needs a human-readable summary. Prioritize issues in this order:

1. **Content guard**: Check `content_changed` and `content_guard_enforced` in `format_report.json`. If `content_changed` is `true` and the user did not opt in, investigate immediately — this is the highest priority failure.
2. **Required sections**: Verify `penalties` for missing or misclassified sections. Cross-check with the format guide's section list.
3. **Page setup**: Inspect margins, font size, and line spacing values in the `features` dict. Compare against extracted rules in `format_rules.json`.
4. **Captions and references**: Look for penalty entries related to captions, tables, or numbering. Check `diagnostics` for suggested fixes.
5. **Score clarity**: If the score explanation is unclear, check `raw_quality_score` vs `score` to understand penalty impact.

For each failure found, follow the `suggested_fix` in the `diagnostics` table before re-running the formatter.

## Contribution-Friendly Tasks

Good first PRs usually fit one of these buckets:

- Add a synthetic test for a school, journal, or conference formatting rule.
- Improve a rule extractor with a narrowly scoped regex or parser.
- Improve report clarity without changing scoring semantics.
- Add a regression case to `docs/regression_manifest.sample.json`.
- Improve this skill workflow or `agents/openai.yaml` metadata.
