from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "library-manager"))

app_source = (ROOT / "library-manager" / "app.py").read_text(encoding="utf-8")
workspace_source = (ROOT / "library-manager" / "workspace.py").read_text(encoding="utf-8")
thumbnail_source = (ROOT / "library-manager" / "thumbnailer.py").read_text(encoding="utf-8")
item_js = (ROOT / "library-manager" / "static" / "item-form.js").read_text(encoding="utf-8")
manager_css = (ROOT / "library-manager" / "static" / "phase7.css").read_text(encoding="utf-8")
public_js = (ROOT / "js" / "library.js").read_text(encoding="utf-8")
public_css = (ROOT / "css" / "card-thumbnails.css").read_text(encoding="utf-8")
index_html = (ROOT / "index.html").read_text(encoding="utf-8")
templates = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "library-manager" / "templates").rglob("*.html"))
requirements = (ROOT / "library-manager" / "requirements.txt").read_text(encoding="utf-8")


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


for marker in ("/workspace", "validate_workspace", "publish_changes", "regenerate_thumbnail", "finish_item_files", "thumbnail_file", 'summary.get("item_count", 0)'):
    expect(marker in app_source, f"Missing Phase 7 app marker: {marker}")

for marker in ("summarize_changes", "item_count", "run_validation", "git(root, \"fetch\", \"origin\")", "git(root, \"commit\"", "git(root, \"push\", \"origin\", \"main\")", "summary[\"other\"]"):
    expect(marker in workspace_source, f"Missing workspace safety marker: {marker}")

for marker in ("1200, 675", "ImageOps.fit", "sync_playwright", "auto-thumbnail.svg", "custom"):
    expect(marker in thumbnail_source, f"Missing thumbnail marker: {marker}")

for marker in ("Review &amp; Publish", "Preview Full Library", "Publish to GitHub", "I confirm this material is public-safe", "data-draft-preview", "Custom card image", "assets/site/favicon.svg", "summary.item_count"):
    expect(marker in templates, f"Missing Phase 7 UI marker: {marker}")

for marker in ("updateDraftPreview", "data-draft", "Add Locally", "Save Locally"):
    expect(marker in item_js or marker in templates, f"Missing pre-save preview marker: {marker}")

for marker in ("publish-layout", "validation-row", "draft-library-card", "manager-card-image"):
    expect(marker in manager_css, f"Missing Phase 7 Manager style: {marker}")

expect("item.thumbnail" in public_js and "card-thumbnail" in public_js, "Public library must render item thumbnails")
expect("card-thumbnail-link" in public_css, "Public thumbnail sizing styles are missing")
expect("css/card-thumbnails.css" in index_html, "Public thumbnail stylesheet is not loaded")
expect("assets/site/favicon.svg" in index_html, "Public Lab favicon is not loaded")
expect((ROOT / "assets" / "site" / "favicon.svg").is_file(), "Shared favicon asset is missing")
expect("Pillow" in requirements and "playwright" in requirements, "Thumbnail dependencies are missing")
expect("</form>" not in (ROOT / "library-manager" / "templates" / "partials" / "review-step.html").read_text(encoding="utf-8"), "Review partial should not close the parent form")

print("PASS: Phase 7 local preview and automatic thumbnail contracts")
print("PASS: Phase 7 item-first batching and deliberate publishing controls")
print("PASS: Phase 7 public card thumbnails, favicon, and custom image replacement contracts")
