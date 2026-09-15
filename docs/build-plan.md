# Learning Content Lab + Library Manager — Build Plan

This file is the implementation tracker for v1.

**V1 status: COMPLETE — released 2026-09-15**

## Phase 1 — Repository foundation

- [x] Create `id-content-library`
- [x] Create agreed repository skeleton
- [x] Add architecture README
- [x] Add `.gitignore`
- [x] Add build tracker
- [x] Clone repository locally
- [x] Configure repo-local Git author with GitHub noreply identity
- [x] Confirm clean local `main` after the foundation PR is merged

## Phase 2 — Data model + item template

- [x] Implement minimum `item.json` schema
- [x] Define controlled values and `Other` behavior
- [x] Create reusable item-folder template
- [x] Define preview/source/assets conventions
- [x] Add test item data

## Phase 3 — Static Learning Content Lab

- [x] Build public homepage/layout
- [x] Generate item cards from library data
- [x] Add search
- [x] Add content-type filtering
- [x] Add tool/tag filtering
- [x] Add status display
- [x] Make site responsive

## Phase 4 — Item pages + previews

- [x] Generate permanent item pages
- [x] Support HTML/JavaScript previews
- [x] Support Storyline published output
- [x] Support PDF/document previews
- [x] Support images and video
- [x] Support text, prompts, and code
- [x] Support download-only/unknown assets
- [x] Add graceful preview fallback

## Phase 5 — Library Manager

- [x] Build local-only app
- [x] Add Library browser
- [x] Add Item wizard
- [x] Edit existing items
- [x] Archive items
- [x] Upload files/folders
- [x] Add deliberate delete protection

## Phase 6 — Smart upload + prefill

- [x] Detect common file types
- [x] Detect Storyline source/output
- [x] Infer format/tool/preview type
- [x] Generate title/slug suggestions from filenames
- [x] Prefill dates/default statuses
- [x] Add dropdowns and tag/tool chips
- [x] Remember commonly used tags/tools
- [x] Move uncommon fields under Advanced Details

## Phase 6.5 — Manager UX refinement

- [x] Replace preview/source/assets upload cards with one Add Your Project flow
- [x] Keep repository folder mechanics hidden during normal use
- [x] Add source-only and replace-project advanced controls
- [x] Simplify normal metadata to human-language questions
- [x] Keep technical metadata under Advanced Details
- [x] Show Other label only when an Other option is actually selected
- [x] Add a plain-language user guide drawer
- [x] Add contextual help bubbles and option descriptions
- [x] Refresh the Manager with a light green/purple futuristic-whimsical visual system
- [x] Preserve smart prefill and human-overrides-win behavior

## Phase 7 — Preview + validation + publishing

- [x] Preview new item before adding
- [x] Preview full library locally
- [x] Generate automatic screenshots/thumbnails for supported interactive, document, and image content
- [x] Normalize/crop generated card imagery to consistent display sizes
- [x] Allow a generated thumbnail to be replaced manually when desired
- [x] Validate metadata, paths, slugs, files, thumbnails, and generated pages
- [x] Show human-readable change summary
- [x] Batch multiple local item changes before publishing
- [x] Add deliberate Publish to GitHub action
- [x] Automate routine Git fetch/check/commit/push work with safe sync guards

## Phase 7.5 — Public Lab experience refresh

- [x] Keep Library Manager local-only and the Learning Content Lab public-facing
- [x] Align the public Lab with the Manager's mint/lavender/violet visual identity
- [x] Preserve a visitor-facing design instead of exposing admin/maintenance controls
- [x] Add a public Guide button and plain-language visitor guide
- [x] Explain browsing, item pages, and library statuses in the public guide
- [x] Apply the refreshed visual system to generated item pages
- [x] Add regression checks for the public guide and shared visual theme

## Phase 8 — GitHub Pages + release QA

- [x] Add GitHub Pages deployment workflow
- [x] Build an explicit public-only deployment artifact that excludes Library Manager
- [x] Add automated Phase 8 validation to GitHub Actions
- [x] Test interactive HTML/JavaScript reference fixture
- [x] Test Storyline source packaging + published-preview reference fixture
- [x] Test prompt/text/framework reference fixture
- [x] Add responsive/mobile release contracts
- [x] Test Library Manager end to end manually
- [x] Confirm public-safe deployment boundary
- [x] Document routine maintenance workflow
- [x] Merge Phase 8 release PR to `main`
- [x] Enable repository Pages source as GitHub Actions
- [x] Verify successful Pages build/deployment
- [x] Browser-check the exact deployed artifact for homepage/Guide/search/filter behavior
- [x] Browser-check the exact deployed artifact at phone width with no horizontal overflow
- [x] Record the first-real-item live page check as a post-v1 operational follow-up instead of publishing fake QA content
- [x] Declare v1 complete

## V1 acceptance test

The system successfully supports all three reference content types through:

**upload → minimal metadata → preview → validate → publish → browse**

1. Interactive HTML/JavaScript component
2. Storyline source + published interactive preview
3. Prompt/text/framework resource

Phase 8 CI uses temporary internal QA fixtures for these three content families so release validation does not require fake test items to remain in the public Lab.

## Post-v1 operating state

Normal content maintenance now happens through Library Manager on local `main`. Successful publishing pushes the library content to GitHub, and GitHub Pages automatically rebuilds the public Lab.

The next platform work should be driven by real usage rather than adding speculative complexity.
