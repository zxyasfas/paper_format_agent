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

Run these before handing work back. Treat a non-zero exit as a blocker — never
return work on a red suite:

```bash
python tools/validate_skill.py
python -m unittest discover -s tests -p "test_*.py"
python tools/compile_check.py
python tools/release_audit.py
```

Reading the output:
- `validate_skill.py` checks the skill contract (paths, section names, example
  commands). On failure, fix the exact section it names.
- `unittest` failures mean a rule, extractor, or regression case broke. Fix the
  code and re-run; never silence a failing test.
- `compile_check.py` compiles every module; failures are syntax or import errors.
- `release_audit.py` gates release safety (no real papers, API keys, or generated
  output committed).

## When Adding Template Support

- Add the smallest representative rule text needed to reproduce the behavior.
- Prefer deterministic rule extraction over LLM-only interpretation.
- Add tests for extracted margins, font size, line spacing, required sections, headings, captions, or references.
- Do not commit real student documents. Use synthetic text or anonymized fixtures.

## Reviewing Output

Work from the artifacts in `--out-dir`. `format_report.json` is the machine-readable
source of truth; `format_report.html` is its human-readable view. Read the JSON
first so you act on exact values, not summaries.

### format_report.json

1. Gate on the content guard: require `content_guard_enforced: true` and
   `content_changed: false`. Anything else means content was touched — do not
   hand back the output.
2. Compare `score_before` vs `score_after` via `score_improvement`. A negative
   improvement means formatting made scoring worse; investigate before returning.
3. Walk `diagnostics` in severity order (`high`, `medium`, `low`). Each entry
   carries `summary`, `suggested_fix`, and `evidence`, so use those to decide
   whether the paper or the rule extractor is at fault.
4. If the score itself is misleading, fix scoring semantics in the scorer and
   add a regression test — do not hand-edit the report.
5. Check `engine_report.success` and `llm_warnings`; a failed post-processing
   engine is a blocker even when the score looks fine.

### Content guard failure

The formatter aborts with `content guard failed` and does not write
`formatted_paper_v3.docx`, so there is usually no output document or
`format_report.json` to inspect. When that happens:

1. Reproduce with `--engine python` so the fingerprint covers the saved DOCX
   (see README for how other engines run a post-processor after the check).
2. Diff `content_fingerprint_before` vs `content_fingerprint_after` when present,
   and read `modify_log.json` for the formatting steps that ran. The fingerprint
   ignores whitespace and stray bullets, so a difference means real text changed.
3. Narrow the offending rule to a minimal synthetic fixture, fix the rule
   extractor or styling step, and re-run.
4. Add a failing-path test that trips the guard on the same input. Do not add
   `--allow-content-change` as a workaround — it only suppresses the check.

### Validation output

A clean Validation run (below) means every guard, test, and release check passed.
If a command fails, act on its message, fix the underlying issue, and re-run the
full suite — never skip the failing command.

## Contribution-Friendly Tasks

Good first PRs usually fit one of these buckets:

- Add a synthetic test for a school, journal, or conference formatting rule.
- Improve a rule extractor with a narrowly scoped regex or parser.
- Improve report clarity without changing scoring semantics.
- Add a regression case to `docs/regression_manifest.sample.json`.
- Improve this skill workflow or `agents/openai.yaml` metadata.
