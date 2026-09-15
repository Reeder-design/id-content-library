# Scripts

Deterministic build and validation utilities live here. No AI, external API, or database is required for the core library architecture.

## Build the library

```bash
python scripts/build-library.py
```

This scans `items/<slug>/item.json` as the canonical published-item metadata, regenerates `library-data/items.json`, and creates/updates each permanent `items/<slug>/index.html` page.

Use check mode when you want to confirm generated files are already current without changing anything:

```bash
python scripts/build-library.py --check
```

## Validation

- `validate-foundation.py` checks the repository foundation and public-safe boundary.
- `validate-library.py` checks metadata and controlled-value conventions.
- `validate-public-ui.py` checks the searchable/filterable homepage contract.
- `validate-item-pages.py` exercises the preview matrix, including web/Storyline interactive launches, PDF/documents, images, video, text/code, source downloads, and graceful fallback behavior.
- `validate-phase4-ui.py` checks permanent card links, item-page styling, and generator contracts.

GitHub Actions runs these checks on pull requests and pushes to `main`.
