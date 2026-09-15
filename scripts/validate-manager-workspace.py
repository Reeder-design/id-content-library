from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEMS = ROOT / "items"
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


for directory in sorted(path for path in ITEMS.iterdir() if path.is_dir()):
    metadata_path = directory / "item.json"
    if not metadata_path.is_file():
        fail(f"{directory.name}: missing item.json")
        continue
    try:
        item = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{directory.name}: invalid item.json ({exc})")
        continue

    slug = str(item.get("slug", "")).strip()
    if slug != directory.name:
        fail(f"{directory.name}: folder name does not match slug {slug!r}")

    for required_dir in ("preview", "source", "assets"):
        if not (directory / required_dir).is_dir():
            fail(f"{slug}: missing {required_dir}/ folder")

    generated_page = directory / "index.html"
    if not generated_page.is_file():
        fail(f"{slug}: generated item page is missing")

    thumbnail = str(item.get("thumbnail", "")).strip()
    if thumbnail and not (directory / thumbnail).is_file():
        fail(f"{slug}: thumbnail points to a missing file ({thumbnail})")

    if item.get("preview_type") == "interactive":
        preview = directory / "preview"
        entries = [preview / name for name in ("index.html", "story.html", "index.htm")]
        if not any(path.is_file() for path in entries):
            fail(f"{slug}: interactive preview needs index.html, index.htm, or story.html at the preview root")

    for path in directory.rglob("*"):
        if path.is_file() and path.name.startswith("."):
            fail(f"{slug}: hidden file should not be published ({path.relative_to(directory)})")

if errors:
    print("FAIL: Library Manager workspace validation")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("PASS: item folders, slugs, files, thumbnails, and generated pages are consistent")
