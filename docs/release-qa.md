# V1 release QA record

Date: 2026-09-15

Status: **V1 released**

Public site: `https://reeder-design.github.io/id-content-library/`

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

The exact artifact uploaded to GitHub Pages was also browser-tested after deployment:

- desktop Guide opens/closes correctly
- mobile Guide opens/closes correctly
- search and filter controls initialize without JavaScript errors
- 390 px phone viewport has no horizontal overflow
- mobile Guide fits the full phone width cleanly
- deployed artifact contains the expected public theme, Guide JavaScript, favicon, and library data
- deployed artifact contains no Library Manager routes, localhost references, scripts, docs, templates, workflows, or repository README

## Deployment checks

The Pages workflow:

1. runs on pushes to `main` and manual dispatch
2. validates metadata and generated output
3. validates the public UI and preview matrix
4. builds a public-only artifact
5. configures Pages
6. uploads the Pages artifact
7. deploys through the `github-pages` environment

The first deployment attempt correctly stopped because Pages had not yet been enabled at the repository level. After the repository owner selected **Settings → Pages → Source → GitHub Actions**, the failed workflow was rerun.

The rerun completed successfully. GitHub Pages reported a successful deployment for commit `90e0a6f625c811db0ca2f0e1f2454ff54245bc1a` and published the environment URL:

`https://reeder-design.github.io/id-content-library/`

## Final release gates

- [x] Phase 8 PR merged to `main`
- [x] repository Pages source set to **GitHub Actions**
- [x] Pages build and deployment completed successfully
- [x] exact deployed public artifact passed homepage/Guide/search/filter browser checks
- [x] exact deployed public artifact passed mobile/phone browser checks
- [x] deployed artifact verified to exclude Library Manager and repository-only files
- [x] v1 acceptance fixtures passed for interactive HTML/JavaScript, Storyline packaging/published preview, and prompt/text/framework content
- [x] routine maintenance workflow documented
- [x] v1 declared complete

## First real-content follow-up

The public Lab intentionally launched without fake QA items. When the first real public-safe library item is published, perform one live item-page spot check for its preview/download behavior. This is an operational follow-up, not a blocker for the v1 platform release, because item-page behavior is already covered by the Phase 4 preview matrix and Phase 8 acceptance fixtures.

## V1 workflow

**upload → minimal metadata → preview → validate → publish → browse**
