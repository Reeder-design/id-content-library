# V1 release QA record

Date: 2026-09-15

This document records the release checks for Learning Content Lab + Library Manager v1.

## Architecture boundary

- Library Manager is local-only and binds to `127.0.0.1`.
- The public Learning Content Lab is a static site.
- GitHub Pages is built from an explicit public allow-list rather than from the repository root.
- Manager code, scripts, docs, templates, workflows, and local environments are excluded from the Pages artifact.

## Manual UX checks completed

The owner manually tested and approved the Phase 7/7.5 experience before Phase 8:

- Add Item workflow
- smart prefill and human override behavior
- local save behavior
- generated thumbnails/card imagery
- item preview
- full-library preview
- Review & Publish workspace
- validation presentation
- public Lab visual refresh
- public Guide drawer
- publish badge behavior
- custom favicon

## Automated v1 acceptance fixtures

`scripts/validate-phase8-release.py` creates temporary, non-public QA fixtures and runs them through the library build/validation pipeline.

### 1. HTML/JavaScript interaction

Checks:

- valid item metadata
- interactive `preview/index.html`
- source download
- generated permanent item page
- inclusion in public artifact

### 2. Storyline packaging + published preview

Checks:

- Storyline metadata and tool labeling
- `.story` source-file packaging path
- published `story.html` launch-page detection
- nested `story_content/` preservation
- generated permanent item page
- inclusion in public artifact

The `.story` file used by CI is intentionally a packaging fixture, not an Articulate-authored binary. CI validates the library workflow around Storyline source files; opening/editing a real `.story` binary remains an Articulate-specific manual check when a real public-safe source is available.

### 3. Prompt/text framework

Checks:

- prompt-library metadata
- Markdown text preview
- source download
- generated permanent item page
- inclusion in public artifact

## Responsive/public experience checks

Automated release validation confirms:

- mobile viewport metadata is present
- public responsive breakpoints are present
- public Guide assets are present
- favicon is present
- no localhost/127.0.0.1 address leaks into the public homepage
- Manager/repository-only directories are absent from the deployed artifact

The public Lab and Manager have also been visually reviewed in-browser during development. A final live-site phone/tablet spot check should be performed after GitHub Pages is enabled.

## Deployment checks

The Pages workflow:

1. runs on pushes to `main` and manual dispatch
2. validates metadata and generated output
3. validates the public UI and preview matrix
4. builds a public-only artifact
5. configures Pages
6. uploads the Pages artifact
7. deploys through the `github-pages` environment

## Final release gates

Before declaring v1 complete:

- [ ] Phase 8 PR merged to `main`
- [ ] repository Pages source set to **GitHub Actions** if it is not already enabled
- [ ] Pages deployment completes successfully
- [ ] live public URL opens successfully
- [ ] live homepage Guide/search/filter behavior spot-checked
- [ ] one live item page spot-checked after real content is published
- [ ] live mobile/phone layout spot-checked

Once those gates pass, the v1 workflow is:

**upload → minimal metadata → preview → validate → publish → browse**
