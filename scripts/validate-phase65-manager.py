from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
template_dir = ROOT / "library-manager" / "templates"
templates = "\n".join(path.read_text(encoding="utf-8") for path in template_dir.rglob("*.html"))
manager_js = (ROOT / "library-manager" / "static" / "manager.js").read_text(encoding="utf-8")
item_js = (ROOT / "library-manager" / "static" / "item-form.js").read_text(encoding="utf-8")
css = (ROOT / "library-manager" / "static" / "manager.css").read_text(encoding="utf-8")


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


for marker in ("data-guide-open", "data-guide-drawer", "Library Manager, in plain English", "Public-safe reminder"):
    expect(marker in templates, f"Missing guide marker: {marker}")
for marker in ("Add your project", 'name="project_files"', "We’ll do the boring organizing", "What kind of resource is this?", "What did you use to make it?", "How would you search for it later?", "Advanced file options", "Advanced Details", "data-other-label-wrap"):
    expect(marker in templates, f"Missing Phase 6.5 form marker: {marker}")
for marker in ("not related to the “Other” resource category", "Download/source only.", "Replace the current project files.", "Only for unusual file-handling cases"):
    expect(marker in templates, f"Missing Advanced file options explanation: {marker}")
for marker in ("selectedProjectFiles", "source_files", "preview_files", "data-source-only", "syncOtherLabel"):
    expect(marker in item_js, f"Missing Phase 6.5 item JavaScript marker: {marker}")
expect("openGuide" in manager_js, "Missing guide interaction")
expect("assets_files" not in templates, "Normal item form should not expose a supporting-assets uploader")
expect("Preview</h3>" not in templates, "Normal item form should not expose a preview-folder upload card")
expect("Source</h3>" not in templates, "Normal item form should not expose a source-folder upload card")
for marker in ("--violet:", "--lavender:", "--mint:", "--lime:", ".guide-drawer", ".project-upload-card", ".help-popover"):
    expect(marker in css, f"Missing visual-system marker: {marker}")

print("PASS: Phase 6.5 uses one human-centered project upload flow")
print("PASS: Phase 6.5 help guide, contextual help, and simplified labels are present")
print("PASS: Phase 6.5 Advanced file options are clearly separated from the Other resource category")
print("PASS: Phase 6.5 light green/purple visual refresh is present")
