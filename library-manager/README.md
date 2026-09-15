# Library Manager

Library Manager is the local-only maintenance utility for the Learning Content Lab.

## Current capabilities

- browse and search existing items
- add items through a Files → Details → Review workflow
- edit metadata
- upload files and folders into preview, source, and assets
- replace an existing file area deliberately
- open an item folder locally
- archive items
- protect deletion with an exact confirmation phrase
- rebuild generated library output after successful changes
- roll back item-folder mutations when a rebuild fails
- detect common file types from selected file names and folder paths
- detect Storyline source files and published Storyline output
- infer format, tool, and preview type when the evidence is clear
- suggest cleaned titles and stable slugs from filenames
- prefill creation date plus default library and portfolio statuses
- surface remembered tool and tag choices as reusable chips
- keep less-common metadata under Advanced Details
- preserve human edits over automatic suggestions

All smart prefill behavior is deterministic and local. It does not use AI or send uploaded content to an external service. The Manager only analyzes the selected file names and relative folder paths before save.

Full generated preview, validation summaries, batching, and deliberate Git publishing remain Phase 7.

## Run locally

From the repository root:

1. Create and activate a Python virtual environment.
2. Run `pip install -r library-manager/requirements.txt`.
3. Run `python library-manager/app.py`.
4. Open the local address shown in the terminal.

The app intentionally binds only to `127.0.0.1`.

Anything added through Library Manager belongs in the public Learning Content Lab, so only add material that is ready for public storage.
