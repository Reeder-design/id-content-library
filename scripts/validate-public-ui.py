from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def check_html() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    lower = html.lower()

    required_ids = [
        "library-search",
        "content-type-filters",
        "tool-filter",
        "tag-filter",
        "clear-filters",
        "results-count",
        "library-grid",
        "empty-state",
        "load-error",
    ]

    missing = [item_id for item_id in required_ids if f'id="{item_id}"' not in lower]
    if missing:
        fail("Public UI is missing required controls: " + ", ".join(missing))

    if lower.count("<h1") != 1:
        fail("Public homepage must contain exactly one h1")

    if "<noscript>" not in lower:
        fail("Public homepage must include a noscript fallback")

    for token in (
        "css/public-lab-theme.css",
        "js/public-guide.js",
        "data-public-guide-open",
        "data-public-guide",
        "How to use the Lab",
        "What the status means",
        "Lab vs. portfolio",
        "assets/site/favicon.svg",
    ):
        if token not in html:
            fail(f"Public visitor-guide contract is missing: {token}")

    duplicate_ids = sorted({value for value in re.findall(r'id="([^"]+)"', html) if html.count(f'id="{value}"') > 1})
    if duplicate_ids:
        fail("Public homepage contains duplicate IDs: " + ", ".join(duplicate_ids))

    print("PASS: Public library HTML structure and visitor guide are valid")


def check_javascript_contract() -> None:
    js = (ROOT / "js" / "library.js").read_text(encoding="utf-8")
    required_tokens = [
        'loadJson("library-data/items.json")',
        'loadJson("library-data/options.json")',
        "matchesFilters",
        "buildContentTypeFilters",
        "buildSecondaryFilters",
        "createCard",
        "clearFilters",
    ]

    missing = [token for token in required_tokens if token not in js]
    if missing:
        fail("Public library JavaScript contract is incomplete: " + ", ".join(missing))

    if "innerHTML" in js:
        fail("Public library rendering must not inject item metadata with innerHTML")

    guide_js = (ROOT / "js" / "public-guide.js").read_text(encoding="utf-8")
    for token in ("data-public-guide-open", "openGuide", "closeGuide", "Escape"):
        if token not in guide_js:
            fail(f"Public guide JavaScript contract is incomplete: {token}")

    print("PASS: Public library and visitor-guide JavaScript contracts are intact")


def check_css_contract() -> None:
    css = (ROOT / "css" / "styles.css").read_text(encoding="utf-8")
    required_selectors = [
        ".library-grid",
        ".library-card",
        ".filter-pill",
        ".empty-state",
        "@media (max-width: 680px)",
    ]

    missing = [selector for selector in required_selectors if selector not in css]
    if missing:
        fail("Public library CSS is missing required responsive components: " + ", ".join(missing))

    theme = (ROOT / "css" / "public-lab-theme.css").read_text(encoding="utf-8")
    for token in ("--violet:", "--lavender:", "--mint:", ".public-guide-drawer", ".public-guide-button", "min-width: 104px", ".library-card"):
        if token not in theme:
            fail(f"Public Lab theme is missing: {token}")

    item_css = (ROOT / "css" / "item-pages.css").read_text(encoding="utf-8")
    if '@import url("public-lab-theme.css")' not in item_css:
        fail("Generated item pages must inherit the public Lab theme")

    print("PASS: Public library responsive CSS and shared visual theme contracts are intact")


def main() -> int:
    check_html()
    check_javascript_contract()
    check_css_contract()
    print("\nPublic library UI validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
