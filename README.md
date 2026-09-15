# Learning Content Lab

A reusable public library for instructional-design templates, interactions, prompts, code, resources, experiments, and other learning-content assets.

The repository has two deliberately separate surfaces:

- **Learning Content Lab** — the public-facing static site that visitors browse. This is the part that will be hosted with GitHub Pages.
- **Library Manager** — the private maintenance utility used locally on the owner's computer for adding, editing, previewing, validating, batching, and publishing library items. It is not a public website and is not intended to be deployed.

The public Lab and local Manager share the same visual identity so maintaining the library and browsing it feel like parts of one system, but they serve different audiences and remain technically separate.

This project is also intentionally separate from the official portfolio. The portfolio contains selected spotlight projects; the Lab can contain the broader body of reusable work.

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

Each library item owns a folder under `items/<slug>/` containing its metadata and, when relevant, `preview/`, `source/`, and `assets/` content. Library Manager hides those repository mechanics during normal use.

## Design principles

- Keep the public site static, approachable, and easy to browse.
- Keep Library Manager local-only and maintenance-focused.
- Use one shared visual identity across both surfaces without turning the public Lab into an admin interface.
- Make adding content low-friction.
- Infer technical metadata locally whenever practical.
- Require human input only for context the system cannot reliably determine.
- Preview and validate before publishing.
- Use Git history instead of inventing a separate versioning system.
- Add complexity only after real usage proves it is needed.

## Build status

See [`docs/build-plan.md`](docs/build-plan.md) for the phased implementation tracker.
