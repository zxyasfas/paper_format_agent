# Roadmap

This roadmap is organized to create many small PR opportunities.

## Good First PRs

- [ ] Add synthetic tests for IEEE-style heading and caption rules.
- [ ] Add synthetic tests for APA-style reference spacing rules.
- [ ] Add synthetic tests for Chinese thesis abstract and keyword variants.
- [ ] Improve `format_report.html` wording for failed checks.
- [ ] Add examples to `docs/regression_manifest.sample.json`.
- [ ] Improve `SKILL.md` with more precise agent review steps.

See [docs/CONTRIBUTOR_TASKS.md](docs/CONTRIBUTOR_TASKS.md) for task-ready issue
descriptions, acceptance criteria, and suggested labels.

## Contributor Starter Board

These are intentionally small and useful PRs:

- [ ] `tests`: APA reference spacing synthetic coverage.
- [ ] `tests`: Chinese thesis abstract and keyword label variants.
- [ ] `scoring`: figure caption diagnostics with actionable fixes.
- [ ] `scoring`: table caption diagnostics with evidence fields.
- [ ] `templates`: synthetic university thesis template pack.
- [ ] `reporting`: clearer failed-check wording in HTML reports.
- [ ] `ci`: optional GitHub Actions example for local format checks.

## Recently Added

- [x] Batch CLI for folders of papers.
- [x] Release audit for tracked generated files, local scratch files, caches, and secret-like files.
- [x] Privacy-safe template packs for Chinese thesis, journal article, and IEEE-style conference workflows.
- [x] Synthetic examples for demo guides and report output shapes.
- [x] GitHub Actions CI for skill validation, unit tests, compile checks, and release audit.

## Near Term

- [ ] CLI flag to load a template pack directly, for example `--template chinese-thesis-basic`.
- [ ] Stronger template extraction for section order and numbering systems.
- [ ] More granular scoring explanations.
- [ ] Table, figure, equation, footnote, header, and footer checks.
- [ ] Minimal MCP server wrapper for local agent integration.
- [ ] GitHub Action example for formatting checks in PRs.

## Mid Term

- [ ] Public synthetic benchmark corpus.
- [ ] Expanded template packs for more schools, journals, and conferences.
- [ ] Rule plugin interface.
- [ ] Render-and-compare PDF visual QA.
- [ ] Better cross-platform post-processing with LibreOffice.

## Long Term

- [ ] Multi-language paper formatting support.
- [ ] Web/Desktop review UI.
- [ ] Enterprise audit dashboard.
- [ ] Marketplace-style template registry.

## Growth Plan

- Keep the first-run path under five minutes.
- Make every template rule request easy to turn into a PR.
- Publish reproducible demos using synthetic documents.
- Prefer many small contributor-friendly issues over large opaque milestones.
- Keep public issues specific enough that a contributor can finish one in one evening.
