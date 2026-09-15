# Learning Content Lab

A reusable public library for instructional-design templates, interactions, prompts, code, resources, experiments, and other learning-content assets.

The repository has two parts:

- **Learning Content Lab** — the static public library that will be hosted with GitHub Pages.
- **Library Manager** — a lightweight local-only utility for adding, editing, previewing, validating, and publishing library items.

This is intentionally separate from the official portfolio. The portfolio contains selected spotlight projects; this library can contain the broader body of reusable work.

## Core rule

**Anything committed to this repository must already be public-safe.** Do not add confidential company material, proprietary customer information, private notes, credentials, API keys, or unsanitized source content.

## Repository structure

```text
id-content-library/
├── index.html
├── css/
├── js/
├── assets/site/
├── items/
├── library-data/
├── templates/library-item/
├── library-manager/
├── scripts/
└── docs/
```

Each future library item will own a folder under `items/<slug>/` containing its metadata and, when relevant, `preview/`, `source/`, and `assets/` content.

## Design principles

- Keep the public site static and simple.
- Make adding content low-friction.
- Infer technical metadata locally whenever practical.
- Require human input only for context the system cannot reliably determine.
- Preview and validate before publishing.
- Use Git history instead of inventing a separate versioning system.
- Add complexity only after real usage proves it is needed.

## Build status

See [`docs/build-plan.md`](docs/build-plan.md) for the phased implementation tracker.
