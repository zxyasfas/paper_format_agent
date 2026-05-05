# Production Standard (Commercial Readiness)

## Release Gates

1. **Functional Gate**
- Must parse `.doc/.docx/.txt` guideline inputs.
- Must format `.docx` papers without content mutation (content guard pass).
- Must generate `format_report.json` and `modify_log.json`.

2. **Quality Gate**
- On regression dataset, pass rate must be `>= 95%`.
- Average score improvement must be `>= 5`.
- `content_changed` must be `false` for all strict runs.

3. **Safety Gate**
- Default mode must enforce content guard.
- Any content-guard failure must fail fast (non-zero exit).
- Output artifacts must include engine and confidence diagnostics.

4. **Ops Gate**
- CI must run unit tests on every push/PR.
- Regression runner must be executable in staging before release.
- Versioned release notes must record rule changes and score impact.

## Required Commands

```bash
# Unit tests
python -m unittest discover -s tests -p "test_*.py"

# Regression run
python tools/regression_runner.py \
  --manifest docs/regression_manifest.sample.json \
  --out-dir sample_output/regression_ci
```

## Current Scope

- Program is format-focused. It does not rewrite thesis semantics.
- LLM module is advisory by default and should not mutate original content.

