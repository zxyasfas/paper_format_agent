# User Pain Analysis

Snapshot date: 2026-05-06

This project prioritizes local DOCX formatting fixes that are deterministic,
content-preserving, and easy to review. A quick scan of public GitHub issues in
DOCX, Word automation, and academic/report generation projects surfaced a
repeated pattern: users do not only need a generated document; they need to know
what changed, what is still wrong, and how to fix it without losing formatting.

## Public Signals

- Word/DOCX editing tools receive repeated reports about preserving formatting,
  including style-preserving paragraph replacement and inserts that do not keep
  formatting: [Office-Word-MCP-Server #83](https://github.com/GongRzhe/Office-Word-MCP-Server/issues/83),
  [#84](https://github.com/GongRzhe/Office-Word-MCP-Server/issues/84).
- Users report unreliable anchors, range replacement, and cross-run search in
  DOCX XML, which makes automated fixes hard to trust:
  [Office-Word-MCP-Server #80](https://github.com/GongRzhe/Office-Word-MCP-Server/issues/80),
  [#81](https://github.com/GongRzhe/Office-Word-MCP-Server/issues/81),
  [#82](https://github.com/GongRzhe/Office-Word-MCP-Server/issues/82).
- Table editing and "format is messy" reports show that users need targeted
  diagnostics rather than a generic failure:
  [Office-Word-MCP-Server #78](https://github.com/GongRzhe/Office-Word-MCP-Server/issues/78),
  [#79](https://github.com/GongRzhe/Office-Word-MCP-Server/issues/79).
- Other DOCX/report projects show the same preservation theme:
  [react-quill #1048](https://github.com/zenoamaro/react-quill/issues/1048),
  [glossa #82](https://github.com/nikazzio/glossa/issues/82),
  [docwow #59](https://github.com/py-prit/docwow/issues/59),
  [docx-editor #380](https://github.com/eigenpal/docx-editor/issues/380).

## Implementation Choice

The first open-source improvement from this analysis is an actionable diagnostic
layer in `format_report.json` and `format_report.html`.

Before this change, reports exposed raw penalty names and scores. That was useful
for machines but weak for users and agents. The new `diagnostics` array maps each
failed check to:

- category
- severity
- penalty
- human-readable problem summary
- suggested fix
- evidence fields when available

This keeps the formatter local-first and deterministic while making failures
actionable for students, supervisors, and CI systems.
