from __future__ import annotations

import html
from pathlib import Path

ICON_CHOICES = {
    "content": "Content",
    "ideas": "Ideas",
    "visuals": "Visuals",
    "multimedia": "Multimedia",
    "design": "Design",
    "strategy": "Strategy",
    "code": "Code",
    "repository": "Repository",
}
ICON_NAME = "icon-thumbnail.png"

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


def generate_icon_thumbnail(item_dir: Path, item: dict, icon_id: str, icon_root: Path) -> dict:
    if icon_id not in ICON_CHOICES:
        raise ValueError("Choose an icon from the library.")
    from PIL import Image, ImageDraw, ImageFont

    source = icon_root / f"{icon_id}.webp"
    if not source.is_file():
        raise ValueError("That library icon is unavailable.")
    assets = item_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    target = assets / ICON_NAME
    canvas = Image.new("RGB", (1200, 675), "#153842")
    draw = ImageDraw.Draw(canvas)
    for x in range(0, 1200, 42):
        draw.line((x, 0, x, 675), fill="#1c444d", width=1)
    for y in range(0, 675, 42):
        draw.line((0, y, 1200, y), fill="#1c444d", width=1)
    draw.rounded_rectangle((50, 54, 1150, 621), radius=40, fill="#edf9f1")
    draw.rounded_rectangle((88, 102, 500, 573), radius=34, fill="#d9f2df")
    with Image.open(source) as original:
        icon = original.convert("RGBA")
        icon.thumbnail((345, 345), Image.Resampling.LANCZOS)
        canvas.paste(icon, (294 - icon.width // 2, 337 - icon.height // 2), icon)
    font_candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    font_path = next((path for path in font_candidates if Path(path).is_file()), None)
    title_font = ImageFont.truetype(font_path, 58) if font_path else ImageFont.load_default()
    label_font = ImageFont.truetype(font_path, 23) if font_path else ImageFont.load_default()
    draw.text((550, 160), "LEARNING CONTENT LAB", font=label_font, fill="#24766d")
    title = str(item.get("title", "Untitled item"))
    words, lines, line = title.split(), [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if line and draw.textlength(candidate, font=title_font) > 550:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    for index, text_line in enumerate(lines[:4]):
        draw.text((550, 230 + index * 72), text_line, font=title_font, fill="#173a43")
    draw.rounded_rectangle((550, 525, 777, 558), radius=16, fill="#c8ed7c")
    draw.text((565, 530), ICON_CHOICES[icon_id].upper(), font=label_font, fill="#173a43")
    canvas.save(target, format="PNG", optimize=True)
    return {"path": f"assets/{ICON_NAME}", "kind": "icon", "message": f"Using the {ICON_CHOICES[icon_id]} icon from your library."}


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
