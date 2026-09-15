# Learning Content Lab + Library Manager — Build Plan

This file is the implementation tracker for v1.

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

## Phase 8 — GitHub Pages + release QA

- [ ] Configure Pages deployment
- [ ] Add automated validation in GitHub Actions
- [ ] Test interactive HTML/JavaScript reference item
- [ ] Test Storyline source + published-preview reference item
- [ ] Test prompt/text/framework reference item
- [ ] Test mobile/responsive behavior
- [ ] Test Library Manager end to end
- [ ] Confirm public-safe boundary
- [ ] Document routine maintenance workflow
- [ ] Declare v1 complete

## V1 acceptance test

The same system must successfully support all three reference content types through:

**upload → minimal metadata → preview → validate → publish → browse**

1. Interactive HTML/JavaScript component
2. Storyline source + published interactive preview
3. Prompt/text/framework resource
