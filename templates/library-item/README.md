# Library Item Template

Each library item owns one folder at `items/<slug>/`.

```text
items/<slug>/
├── item.json
├── preview/   # optional browser-viewable or launchable output
├── source/    # optional reusable/downloadable source files
└── assets/    # optional thumbnail, screenshots, or supporting media
```

Only `item.json` is required. The other folders are created only when the item needs them.

## Required metadata

`title`, `slug`, `summary`, `content_type`, `format`, `tools`, `tags`, `library_status`, `preview_type`, and `created`.

## Optional metadata

`updated`, `portfolio_status`, `thumbnail`, `other_label`, and `usage_notes`.

The canonical schema is `library-data/item-schema.json`. Controlled choices and future Library Manager dropdown values live in `library-data/options.json`.

## Other behavior

When `content_type`, `library_status`, `preview_type`, or `portfolio_status` is set to its `Other`/`other` choice, `other_label` is required and should briefly describe the custom value.

## Folder conventions

- `preview/` contains files intended to be viewed or launched from the public Lab. For HTML/Storyline-style output, the entry point should ultimately be `preview/index.html` when possible.
- `source/` contains reusable source files that may be offered for download.
- `assets/` contains thumbnails, screenshots, and supporting media used by the item page or card.
- Folder presence can inform the UI, but an empty folder should never be treated as a usable preview or download.

Do not place confidential, proprietary, credential-bearing, or otherwise non-public-safe material in any item folder.
