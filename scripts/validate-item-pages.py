from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build-library.py"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_builder():
    spec = importlib.util.spec_from_file_location("build_library", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        fail("Could not load scripts/build-library.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def base_item(preview_type: str, slug: str) -> dict:
    return {
        "title": f"Fixture {preview_type.title()}",
        "slug": slug,
        "summary": "Generated preview fixture.",
        "content_type": "Design Patterns",
        "format": "Fixture",
        "tools": ["HTML"],
        "tags": ["fixture"],
        "library_status": "stable",
        "preview_type": preview_type,
        "created": "2026-09-15",
        "portfolio_status": "library-only",
    }


def write(path: Path, content: str = "fixture") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def assert_contains(page: str, *tokens: str) -> None:
    missing = [token for token in tokens if token not in page]
    if missing:
        fail("Generated item page is missing expected token(s): " + ", ".join(missing))


def main() -> int:
    builder = load_builder()

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)

        scenarios = [
            ("interactive", "interactive-fixture", "preview/index.html", "<html><body>interactive</body></html>", ["Interactive preview", "Launch preview"]),
            ("document", "document-fixture", "preview/guide.pdf", "%PDF fixture", ["Document preview", "Open preview"]),
            ("image", "image-fixture", "preview/example.png", "image placeholder", ["media-preview", "Open preview"]),
            ("video", "video-fixture", "preview/demo.mp4", "video placeholder", ["video-preview", "Open preview"]),
            ("code", "code-fixture", "preview/example.js", "<script>alert('x')</script>", ["text-preview", "&lt;script&gt;"]),
            ("text", "text-fixture", "preview/prompt.md", "# Prompt\nUse this safely.", ["text-preview", "# Prompt"]),
            ("download", "download-fixture", "source/template.story", "source placeholder", ["Download source", "reusable download"]),
            ("none", "none-fixture", None, None, ["informational", "Permanent URL"]),
        ]

        for preview_type, slug, relative_path, content, expected in scenarios:
            item_dir = root / slug
            item_dir.mkdir(parents=True, exist_ok=True)
            item = base_item(preview_type, slug)
            if relative_path:
                write(item_dir / relative_path, content or "fixture")
            page = builder.render_item_page(item, item_dir)
            assert_contains(page, builder.GENERATED_MARKER, f"/items/{slug}/", *expected)

        fallback_dir = root / "fallback-fixture"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        write(fallback_dir / "preview" / "mystery.bin", "binary-ish fixture")
        fallback_item = base_item("other", "fallback-fixture")
        fallback_item["other_label"] = "Custom Preview"
        fallback_page = builder.render_item_page(fallback_item, fallback_dir)
        assert_contains(fallback_page, "browser preview is not available", "Open preview")

        source_dir = root / "multi-source-fixture"
        source_dir.mkdir(parents=True, exist_ok=True)
        write(source_dir / "source" / "one.txt", "one")
        write(source_dir / "source" / "two.txt", "two")
        source_item = base_item("none", "multi-source-fixture")
        source_page = builder.render_item_page(source_item, source_dir)
        assert_contains(source_page, "Source files", "Source downloads", "one.txt", "two.txt")

    print("PASS: Permanent item page rendering supports interactive, document, image, video, code, text, download, none, and fallback modes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
