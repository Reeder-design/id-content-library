# Library Manager

Library Manager is the local-only maintenance utility for the Learning Content Lab.

## Current capabilities

- browse and search existing items
- add or edit an item through a Project → Details → Review workflow
- upload one project file or one complete project folder through the normal workflow
- reuse that project automatically for source/download and preview behavior when appropriate
- keep repository concepts such as `preview/`, `source/`, and `assets/` out of the normal user workflow
- use an advanced source-only option for projects that should not be treated as browser previews
- detect common file types from selected file names and folder paths
- detect Storyline source files and published Storyline output
- infer format, tool, and preview type when the evidence is clear
- suggest cleaned titles and stable slugs from filenames
- prefill creation date plus default library and portfolio statuses
- surface remembered tool and tag choices as reusable chips
- keep less-common metadata under Advanced Details
- preserve human edits over automatic suggestions
- provide a plain-language user guide plus contextual help bubbles
- open an item folder locally
- archive items
- protect deletion with an exact confirmation phrase
- rebuild generated library output after successful changes
- roll back item-folder mutations when a rebuild fails

The Manager intentionally uses human-facing language. Normal maintenance should not require knowing Git, JSON, repository paths, or the internal preview/source/assets structure.

All smart prefill behavior is deterministic and local. It does not use AI or send uploaded content to an external service. The Manager only analyzes the selected file names and relative folder paths before save.

Generated pre-publish previews, automatic screenshots/thumbnails, validation summaries, batching, and deliberate Git publishing remain Phase 7.

## Run locally

From the repository root:

1. Create a virtual environment with `python3 -m venv .venv` if one does not already exist.
2. Activate it with `source .venv/bin/activate` on macOS/Linux.
3. Run `python -m pip install -r library-manager/requirements.txt`.
4. Run `python library-manager/app.py`.
5. Open the local address shown in the terminal.

The app intentionally binds only to `127.0.0.1`.

Anything added through Library Manager belongs in the public Learning Content Lab, so only add material that is ready for public storage.
