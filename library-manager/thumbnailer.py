from __future__ import annotations

import html
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
AUTO_NAMES = {"auto-thumbnail.png", "auto-thumbnail.jpg", "auto-thumbnail.svg"}


def _preview_files(item_dir: Path) -> list[Path]:
    preview = item_dir / "preview"
    if not preview.is_dir():
        return []
    return sorted(path for path in preview.rglob("*") if path.is_file())


def _first_preview_image(item_dir: Path) -> Path | None:
    return next((path for path in _preview_files(item_dir) if path.suffix.lower() in IMAGE_SUFFIXES), None)


def _fallback_svg(item: dict, target: Path) -> None:
    title = html.escape(str(item.get("title", "Learning Content Lab")))
    fmt = html.escape(str(item.get("format", "Reusable resource")))
    content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#102e37"/>
    <stop offset="1" stop-color="#235963"/>
  </linearGradient>
</defs>
<rect width="1200" height="675" rx="44" fill="url(#bg)"/>
<circle cx="1020" cy="120" r="180" fill="#81d5b1" opacity="0.14"/>
<circle cx="160" cy="560" r="210" fill="#c8ed7c" opacity="0.12"/>
<text x="84" y="118" fill="#c8ed7c" font-family="Arial, Helvetica, sans-serif" font-size="26" font-weight="700">LEARNING CONTENT LAB</text>
<text x="84" y="302" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="66" font-weight="800">{title}</text>
<text x="84" y="374" fill="#d7e9e5" font-family="Arial, Helvetica, sans-serif" font-size="30">{fmt}</text>
<path d="M84 532h40c9 0 15 3 20 9v50c-5-6-11-9-20-9H84zm120 0h-40c-9 0-15 3-20 9v50c5-6 11-9 20-9h40z" fill="#c8ed7c"/>
</svg>'''
    target.write_text(content, encoding="utf-8")


def _normalize_image(source: Path, target: Path) -> bool:
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return False
    try:
        with Image.open(source) as image:
            image = image.convert("RGB")
            fitted = ImageOps.fit(image, (1200, 675), method=Image.Resampling.LANCZOS)
            fitted.save(target, quality=90)
        return True
    except Exception:
        return False


def _browser_screenshot(url: str, target: Path) -> tuple[bool, str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False, "Playwright is not installed; used a generated fallback image instead."

    try:
        with sync_playwright() as playwright:
            browser = None
            try:
                browser = playwright.chromium.launch(channel="chrome", headless=True)
            except Exception:
                browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1200, "height": 675}, device_scale_factor=1)
            page.goto(url, wait_until="networkidle", timeout=15000)
            page.screenshot(path=str(target), full_page=False)
            browser.close()
        return True, "Generated a fresh browser screenshot."
    except Exception:
        return False, "Browser screenshot support is not ready; used a generated fallback image instead."


def generate_thumbnail(item_dir: Path, item: dict, base_url: str) -> dict:
    assets = item_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    existing = str(item.get("thumbnail", "")).strip()
    if existing and Path(existing).name not in AUTO_NAMES:
        return {"path": existing, "kind": "custom", "message": "Kept the custom thumbnail."}

    for name in AUTO_NAMES:
        path = assets / name
        if path.exists():
            path.unlink()

    image = _first_preview_image(item_dir)
    if image:
        target = assets / "auto-thumbnail.jpg"
        if _normalize_image(image, target):
            return {"path": "assets/auto-thumbnail.jpg", "kind": "image", "message": "Created a consistently sized thumbnail from the project image."}

    screenshot = assets / "auto-thumbnail.png"
    item_url = f"{base_url.rstrip('/')}/repo/items/{item['slug']}/index.html"
    ok, message = _browser_screenshot(item_url, screenshot)
    if ok:
        return {"path": "assets/auto-thumbnail.png", "kind": "screenshot", "message": message}

    fallback = assets / "auto-thumbnail.svg"
    _fallback_svg(item, fallback)
    return {"path": "assets/auto-thumbnail.svg", "kind": "fallback", "message": message}
