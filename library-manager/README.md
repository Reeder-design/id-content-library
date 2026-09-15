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
- show a pre-save library-card preview before an item is added locally
- preview the full generated Learning Content Lab locally
- generate a consistent 16:9 card image automatically
- normalize uploaded project images to card dimensions
- create browser screenshots for interactive/document-style content when browser screenshot support is available
- fall back to a generated branded card image instead of failing when browser screenshot support is unavailable
- allow a custom card image to replace the automatic image
- show local unpublished changes as a batch
- validate metadata, slugs, paths, files, thumbnails, generated pages, and preview support
- summarize added, updated, and removed items in plain English
- block unrelated local files from one-click publishing
- require explicit review and public-safe confirmations before publishing
- check GitHub for newer work before publishing
- automate the routine content-only Git add/commit/push workflow from local `main`
- roll a failed push back to a visibly unpublished local state
- open an item folder locally
- archive items
- protect deletion with an exact confirmation phrase
- rebuild generated library output after successful changes
- roll back item-folder mutations when a rebuild fails

The Manager intentionally uses human-facing language. Normal maintenance should not require knowing Git, JSON, repository paths, or the internal preview/source/assets structure.

All smart prefill behavior is deterministic and local. It does not use AI or send uploaded content to an external service. The Manager only analyzes selected file names and relative folder paths before save.

Saving and publishing are intentionally separate. Add/edit/archive/delete actions update the local repository and rebuild the local preview. Nothing is sent to GitHub until **Review & Publish** is used from the local `main` branch.

## Run locally

From the repository root:

1. Create a virtual environment with `python3 -m venv .venv` if one does not already exist.
2. Activate it with `source .venv/bin/activate` on macOS/Linux.
3. Run `python -m pip install -r library-manager/requirements.txt`.
4. Optional but recommended for reliable browser screenshots: run `python -m playwright install chromium` once. If Chromium is not installed, Library Manager still works and generates a branded fallback card image.
5. Run `python library-manager/app.py`.
6. Open the local address shown in the terminal.

The app intentionally binds only to `127.0.0.1`.

## Normal workflow

1. Add or edit an item and **Save Locally**.
2. Preview the item from the Library screen.
3. Use **Preview Library** to inspect the whole generated Lab.
4. Make as many local item changes as needed; they accumulate into one batch.
5. Open **Review & Publish**.
6. Run validation and read the plain-English change summary.
7. Confirm the batch was reviewed and is public-safe.
8. Publish to GitHub.

Publishing intentionally stops instead of guessing when:
- the local branch is not `main`
- unrelated local files are modified
- validation fails
- GitHub has newer commits that need to be synced first
- the local `main` branch already contains separate unpublished Git commits

Anything added through Library Manager belongs in the public Learning Content Lab, so only publish material that is ready for public storage.
