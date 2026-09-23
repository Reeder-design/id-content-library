# Learning Content Lab

A reusable public library for instructional-design templates, interactions, prompts, code, resources, experiments, and other learning-content assets.

**V1 released:** 2026-09-15

**Public Learning Content Lab:** `https://reeder-design.github.io/id-content-library/`

[![Learning Content Lab preview](assets/site/social-preview.png)](https://reeder-design.github.io/id-content-library/)

The repository has two deliberately separate surfaces:

- **Learning Content Lab** — the public-facing static site that visitors browse. This is the only surface deployed through GitHub Pages.
- **Library Manager** — the private maintenance utility used locally on the owner's computer for adding, editing, previewing, validating, batching, and publishing library items. It is not a public website and is not deployed.

The public Lab and local Manager share the same visual identity so maintaining the library and browsing it feel like parts of one system, but they serve different audiences and remain technically separate.

The shared color and type tokens live in `css/studio-tokens.css`. The public catalog uses `css/studio-public.css`; the local editing workspace uses `library-manager/static/manager-studio.css`. They use separate book and controls favicons so browser tabs are easy to distinguish. The learning, ideas, and tools illustrations in `assets/site/illustrations/`, along with the wizard mascot in `assets/site/mascot-wave.png`, come from Haley's custom portfolio assets.

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

In General Details, the Manager offers three card thumbnail sources: a frame from the project, an uploaded image, or an image from Haley's curated icon library. You can also add connected URLs for supporting assets and related repositories. The Manager generates the public item page and card from those choices.

The Manager requires a locally configured password before it shows library content. Setup, login, lock, and password change instructions are in [`library-manager/README.md`](library-manager/README.md).

## Public deployment

GitHub Pages is deployed from `.github/workflows/deploy-pages.yml` after changes reach `main`.

The deployment does **not** upload the repository root. `scripts/build-public-site.py` creates an allow-listed static artifact containing only:

- `index.html`
- `css/`
- `js/`
- `assets/site/`
- `items/`
- `library-data/`

Library Manager, scripts, docs, templates, workflows, and local/repository internals are deliberately excluded from the public artifact.

Live project-site URL:

`https://reeder-design.github.io/id-content-library/`

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

## Maintenance

See [`docs/maintenance.md`](docs/maintenance.md) for the routine content workflow.

See [`docs/release-qa.md`](docs/release-qa.md) for v1 release acceptance and deployment gates.

See [`docs/build-plan.md`](docs/build-plan.md) for the phased implementation tracker.
