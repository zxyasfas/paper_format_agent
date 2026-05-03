# Architecture (V3)

## Pipeline

1. Parse source `.docx`
2. Detect structural anchors (`摘要`, `目录`, heading patterns)
3. Assign internal type tags (`PFA3_MARK_*`)
4. Optional block reorder (high-confidence only)
5. Apply final styles from tags
6. Cleanup numbering metadata (`w:numPr`) and temporary styles
7. Score and emit report

## Why Type-Tag First

Direct regex-format often damages paragraph order. V3 separates:
- recognition
- formatting
- cleanup

This makes behavior auditable and easier to debug.

## Scoring Modes

- `strict`: enforce required sections from school template
- `loose`: baseline-aware (do not force missing sections absent in original)

## Engine Strategy

`auto` mode:
1. `word-com`
2. `libreoffice`
3. fallback `python`

This improves compatibility across different Windows environments.
