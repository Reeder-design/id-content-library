from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "library-manager"))
from smart_prefill import infer_from_files  # noqa: E402


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


storyline = infer_from_files([
    {"area": "source", "path": "branching-sales-v2.story"},
    {"area": "preview", "path": "branching-sales/story.html"},
    {"area": "preview", "path": "branching-sales/story_content/data.js"},
])
expect(storyline["title"] == "Branching Sales", "Storyline title cleanup")
expect(storyline["slug"] == "branching-sales", "Storyline slug generation")
expect(storyline["format"] == "Storyline", "Storyline format detection")
expect(storyline["tools"] == ["Articulate Storyline"], "Storyline tool detection")
expect(storyline["preview_type"] == "interactive", "Storyline published preview detection")

web = infer_from_files([
    {"area": "preview", "path": "scenario-v3/index.html"},
    {"area": "preview", "path": "scenario-v3/styles.css"},
    {"area": "preview", "path": "scenario-v3/app.js"},
])
expect(web["format"] == "HTML/CSS/JavaScript", "Web format detection")
expect(web["tools"] == ["HTML", "CSS", "JavaScript"], "Web tool detection")
expect(web["preview_type"] == "interactive", "Web preview detection")

pdf = infer_from_files([{"area": "preview", "path": "job-aid-final.pdf"}])
expect(pdf["title"] == "Job Aid", "Filename cleanup")
expect(pdf["format"] == "PDF" and pdf["preview_type"] == "document", "PDF detection")

word = infer_from_files([{"area": "source", "path": "facilitator-guide.docx"}])
expect(word["format"] == "Word", "Word detection")
expect(word["tools"] == ["Microsoft Word"], "Word tool inference")
expect(word["preview_type"] == "download", "Source-only download behavior")

text = infer_from_files([{"area": "preview", "path": "scenario-writing-framework.md"}])
expect(text["format"] == "Text/Markdown" and text["preview_type"] == "text", "Markdown detection")

python_item = infer_from_files([{"area": "preview", "path": "report-cleanup.py"}])
expect(python_item["format"] == "Python", "Python detection")
expect(python_item["tools"] == ["Python"] and python_item["preview_type"] == "code", "Python tool and preview inference")

app_source = (ROOT / "library-manager" / "app.py").read_text(encoding="utf-8")
template_dir = ROOT / "library-manager" / "templates"
templates = "\n".join(path.read_text(encoding="utf-8") for path in template_dir.rglob("*.html"))
static_dir = ROOT / "library-manager" / "static"
javascript = "\n".join(path.read_text(encoding="utf-8") for path in static_dir.glob("*.js"))
options = json.loads((ROOT / "library-data" / "options.json").read_text(encoding="utf-8"))

for marker in ("/api/prefill", "new_item_defaults", "suggestion_catalog", "127.0.0.1"):
    expect(marker in app_source, f"Missing app marker: {marker}")
for marker in ("data-smart-field", "data-chip-target", "Advanced Details", "data-advanced-details"):
    expect(marker in templates, f"Missing form marker: {marker}")
for marker in ("runSmartPrefill", "dataset.autoFilled", "syncChips", "/api/prefill"):
    expect(marker in javascript, f"Missing JavaScript marker: {marker}")

expect(options["defaults"]["library_status"] == "stable", "Stable library default")
expect(options["defaults"]["portfolio_status"] == "library-only", "Library-only portfolio default")
expect("Microsoft Word" in options["tool_suggestions"], "Word suggestion")
expect("Microsoft Excel" in options["tool_suggestions"], "Excel suggestion")

print("PASS: Phase 6 smart upload inference scenarios")
print("PASS: Phase 6 defaults, chips, remembered suggestions, and Advanced Details contracts")
