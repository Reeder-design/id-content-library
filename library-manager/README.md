# Library Manager

Library Manager is the **local-only** maintenance utility for the public Learning Content Lab. It is intentionally not deployed as part of the public site.

The two surfaces share a visual identity, but their roles stay separate:

- **Library Manager** = private/local maintenance workspace.
- **Learning Content Lab** = public visitor-facing library.

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
- preview the library-card presentation before saving
- generate consistent 16:9 card images automatically
- use browser screenshots when Playwright/Chromium is available
- crop/normalize image projects and use a branded fallback when screenshots are unavailable
- allow a custom card image to replace the automatic one
- preview the full generated Learning Content Lab locally
- batch multiple local item changes before publishing
- show a plain-English Review & Publish change summary
- validate metadata, slugs, paths, files, thumbnails, generated pages, and preview support
- publish library content deliberately from local `main`
- stop publishing when unrelated local edits, stale remote history, divergent commits, or validation failures are detected
- open an item folder locally
- archive items
- protect deletion with an exact confirmation phrase
- rebuild generated library output after successful changes
- roll back item-folder mutations when a rebuild fails

The Manager intentionally uses human-facing language. Normal maintenance should not require knowing Git, JSON, repository paths, or the internal preview/source/assets structure.

All smart prefill behavior is deterministic and local. It does not use AI or send uploaded content to an external service. The Manager only analyzes the selected file names and relative folder paths before save.

## Run locally

From the repository root:

1. Create a virtual environment with `python3 -m venv .venv` if one does not already exist.
2. Activate it with `source .venv/bin/activate` on macOS/Linux.
3. Run `python -m pip install -r library-manager/requirements.txt`.
4. Optional but recommended for reliable browser screenshots: run `python -m playwright install chromium` once.
5. Run `python library-manager/app.py`.
6. Open the local address shown in the terminal.

On first launch, the Manager asks you to set a password of at least 12 characters. Later visits require that password. Use **Lock** in the header to end a session, and **Change Manager password** in the Guide to update it. Sessions expire after eight hours of inactivity.

Only a password hash and signing key are stored in `~/.config/learning-content-lab/manager-auth.json` on your computer, outside this repository and the public site. If you forget the password, stop the Manager, remove that local file, and start it again to set a new one. The app still binds only to `127.0.0.1`.

The app intentionally binds only to `127.0.0.1`.

Anything added through Library Manager belongs in the public Learning Content Lab, so only add material that is ready for public storage.
