---
name: Report or scoring improvement
about: Improve score coverage, diagnostics, or human-readable reports
title: ""
labels: "reporting, help wanted"
assignees: ""
---

## Problem

Which failed check, score, or report message is hard for users to understand?

## Desired Behavior

Describe the output users should see in `format_report.json` or
`format_report.html`.

## Synthetic Example

Paste a short fake snippet or describe the synthetic fixture needed. Do not use
real papers or private templates.

## Acceptance Criteria

- [ ] The report explains what failed.
- [ ] The report includes evidence or location when available.
- [ ] The report gives an actionable fix.
- [ ] Tests cover the new or changed behavior.

## Validation

- [ ] `python tools/validate_skill.py`
- [ ] `python -m unittest discover -s tests -p "test_*.py"`
- [ ] `python tools/compile_check.py`
