from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    ROOT / "README.md",
    ROOT / "index.html",
    ROOT / "css" / "styles.css",
    ROOT / "js" / "library.js",
    ROOT / "library-data" / "items.json",
    ROOT / "docs" / "build-plan.md",
    ROOT / "library-manager" / "README.md",
    ROOT / "templates" / "library-item" / "README.md",
    ROOT / "scripts" / "README.md",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def check_required_paths() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_PATHS if not path.exists()]
    if missing:
        fail("Missing required foundation paths: " + ", ".join(missing))
    print("PASS: Required foundation paths exist")


def check_library_data() -> None:
    path = ROOT / "library-data" / "items.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"library-data/items.json is not valid JSON: {exc}")

    if not isinstance(data, list):
        fail("library-data/items.json must contain a JSON array")

    print("PASS: library-data/items.json is valid")


def check_public_page() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8").lower()

    required_tokens = [
        "<!doctype html>",
        "<html",
        "<head",
        "<title>",
        "<meta name=\"viewport\"",
        "<body",
        "css/styles.css",
        "js/library.js",
    ]

    missing = [token for token in required_tokens if token not in html]
    if missing:
        fail("index.html is missing required page elements: " + ", ".join(missing))

    print("PASS: Public index.html foundation is intact")


def check_public_safe_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    if "public-safe" not in readme and "public safe" not in readme:
        fail("README.md must state the repository's public-safe boundary")
    print("PASS: Public-safe repository boundary is documented")


def main() -> int:
    check_required_paths()
    check_library_data()
    check_public_page()
    check_public_safe_boundary()
    print("\nFoundation validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
