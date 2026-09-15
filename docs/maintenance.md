# Routine maintenance workflow

The Learning Content Lab has two separate surfaces:

- **Library Manager** runs only on the owner's computer and is the normal way to maintain content.
- **Learning Content Lab** is the public static site deployed through GitHub Pages.

Normal content maintenance should not require editing JSON, HTML, repository paths, or Git commands beyond updating the local copy before starting.

## Start a maintenance session

From the repository root:

```bash
git switch main
git pull origin main
source .venv/bin/activate
python -m pip install -r library-manager/requirements.txt
python library-manager/app.py
```

Open the local address shown in the terminal, normally `http://127.0.0.1:5000`.

## Add or update content

1. Use **Add Item** or open an existing item in Library Manager.
2. Choose one project file or project folder.
3. Review the smart suggestions and add the human context the Manager cannot infer.
4. Save locally.
5. Preview the item and the full library.
6. Repeat as needed. Multiple item changes can wait locally as one batch.

Nothing is public at this point.

## Publish a batch

1. Open **Review & Publish**.
2. Review the item-level change summary.
3. Run validation.
4. Confirm the batch is reviewed and public-safe.
5. Choose **Publish to GitHub**.

Library Manager only publishes from local `main`. It checks GitHub for newer work, blocks unrelated local edits, validates the library, and commits only library content.

After a successful push to `main`, the GitHub Pages workflow validates and deploys the public-only site artifact automatically.

## What is deployed publicly

The Pages artifact uses an explicit allow-list. It includes only:

- `index.html`
- `css/`
- `js/`
- `assets/site/`
- `items/`
- `library-data/`

It does **not** deploy:

- `library-manager/`
- `scripts/`
- `docs/`
- `templates/`
- `.github/`
- local environments or repository internals

## Public-safe rule

Anything inside a library item can ultimately be published. Do not add confidential company material, proprietary customer information, credentials, private notes, or unsanitized source files.

Sanitize first, then add the public-safe version to Library Manager.

## Changing the software itself

Routine content updates happen through Library Manager on `main`.

Changes to Library Manager, the public Lab design, validation scripts, schemas, or deployment behavior should still use a feature branch and pull request. This keeps application-code changes reviewable without adding Git complexity to normal content maintenance.

## If publishing stops

Library Manager is designed to stop instead of guessing. Common causes include:

- local `main` is behind GitHub
- unrelated files are modified locally
- validation fails
- the current branch is not `main`
- a GitHub push is rejected

The content remains safe locally. Resolve the reported condition, return to **Review & Publish**, and try again.
