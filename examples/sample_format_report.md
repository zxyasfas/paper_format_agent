# Sample Format Report

This is a human-readable companion to `sample_format_report.json`.

## Summary

- Score before: 72
- Score after: 91
- Content changed: false
- Content guard enforced: true
- Fixed items: 8
- Remaining items: 3

## Diagnostics

| Severity | Category | Problem | Suggested Fix |
| --- | --- | --- | --- |
| warning | required_sections | English keywords section is missing. | Add an English keywords paragraph after the English abstract. |
| info | caption | Two figure captions were not centered before repair. | Review figure captions after formatting and confirm numbering order. |
| pass | content_guard | Content fingerprint is unchanged. | No action required. |

The goal is to make report output readable for students and reviewers while keeping the JSON shape stable for agents and CI.
