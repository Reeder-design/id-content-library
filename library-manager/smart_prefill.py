from __future__ import annotations

import re
import unicodedata
from pathlib import PurePosixPath

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v"}
DOCUMENT_TYPES = {
    ".pdf": ("PDF", None),
    ".doc": ("Word", "Microsoft Word"),
    ".docx": ("Word", "Microsoft Word"),
    ".ppt": ("PowerPoint", "Microsoft PowerPoint"),
    ".pptx": ("PowerPoint", "Microsoft PowerPoint"),
    ".xls": ("Excel", "Microsoft Excel"),
    ".xlsx": ("Excel", "Microsoft Excel"),
}
TEXT_EXTENSIONS = {".txt", ".md", ".markdown"}
CODE_EXTENSIONS = {".json", ".xml", ".yaml", ".yml", ".sql", ".sh"}
WEB_EXTENSIONS = {".html", ".htm", ".css", ".js"}
ARCHIVE_EXTENSIONS = {".zip", ".7z", ".rar"}
GENERIC_ROOTS = {"preview", "source", "assets", "output", "published", "publish", "export", "dist", "build"}

ACRONYMS = {
    "ai": "AI",
    "api": "API",
    "css": "CSS",
    "html": "HTML",
    "id": "ID",
    "js": "JS",
    "lms": "LMS",
    "pdf": "PDF",
    "scorm": "SCORM",
    "xapi": "xAPI",
}


def clean_path(value: str) -> str:
    return str(value or "").strip().replace("\\", "/")


def suffix(path: str) -> str:
    return PurePosixPath(clean_path(path)).suffix.lower()


def basename(path: str) -> str:
    return PurePosixPath(clean_path(path)).name


def pretty_title(seed: str) -> str:
    name = PurePosixPath(clean_path(seed)).name
    stem = PurePosixPath(name).stem if PurePosixPath(name).suffix else name
    stem = re.sub(
        r"(?i)(?:[-_. ]+(?:v(?:ersion)?[-_. ]?\d+(?:\.\d+)*|final|draft|copy|published|publish|output))+$",
        "",
        stem,
    )
    stem = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", stem)
    words = [word for word in re.split(r"[-_.\s]+", stem) if word]
    rendered = []
    for word in words:
        lowered = word.lower()
        if lowered in ACRONYMS:
            rendered.append(ACRONYMS[lowered])
        elif re.fullmatch(r"\d+g", lowered):
            rendered.append(lowered.upper())
        else:
            rendered.append(word[:1].upper() + word[1:])
    return " ".join(rendered).strip()


def slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def choose_title_seed(entries: list[dict]) -> str:
    for entry in entries:
        path = clean_path(entry.get("path", ""))
        if suffix(path) == ".story":
            return basename(path)

    roots = []
    for entry in entries:
        path = clean_path(entry.get("path", ""))
        parts = PurePosixPath(path).parts
        if len(parts) > 1:
            roots.append(parts[0])
    if roots:
        counts = {root: roots.count(root) for root in set(roots)}
        root = max(counts, key=lambda candidate: (counts[candidate], -len(candidate)))
        if root.lower() not in GENERIC_ROOTS:
            return root

    preferred = [
        entry for entry in entries
        if basename(clean_path(entry.get("path", ""))).lower()
        not in {"index.html", "index.htm", "story.html"}
    ]
    candidate = preferred[0] if preferred else (entries[0] if entries else {})
    return basename(clean_path(candidate.get("path", "")))


def infer_from_files(entries: list[dict]) -> dict:
    normalized = []
    for raw in entries:
        path = clean_path(raw.get("path", ""))
        if not path:
            continue
        normalized.append({"area": str(raw.get("area", "")).strip().lower(), "path": path})

    if not normalized:
        return {}

    all_exts = {suffix(entry["path"]) for entry in normalized}
    preview = [entry for entry in normalized if entry["area"] == "preview"]
    preview_exts = {suffix(entry["path"]) for entry in preview}
    preview_names = {basename(entry["path"]).lower() for entry in preview}
    preview_paths = {entry["path"].lower() for entry in preview}

    title = pretty_title(choose_title_seed(normalized))
    result = {"title": title, "slug": slugify(title)} if title else {}

    storyline_source = ".story" in all_exts
    storyline_output = (
        "story.html" in preview_names
        or any("story_content/" in path for path in preview_paths)
        or any("story_html5.html" in path for path in preview_paths)
    )
    if storyline_source or storyline_output:
        result.update(
            {
                "format": "Storyline",
                "tools": ["Articulate Storyline"],
                "preview_type": "interactive" if storyline_output else "download",
            }
        )
        return result

    if preview_exts & {".html", ".htm"}:
        tools = []
        if all_exts & {".html", ".htm"}:
            tools.append("HTML")
        if ".css" in all_exts:
            tools.append("CSS")
        if ".js" in all_exts:
            tools.append("JavaScript")
        result.update(
            {
                "format": "HTML/CSS/JavaScript",
                "tools": tools or ["HTML"],
                "preview_type": "interactive",
            }
        )
        return result

    def first_extension(candidates, pool: set[str]) -> str | None:
        return next((ext for ext in candidates if ext in pool), None)

    doc_ext = first_extension(DOCUMENT_TYPES.keys(), preview_exts or all_exts)
    if doc_ext:
        file_format, tool = DOCUMENT_TYPES[doc_ext]
        result["format"] = file_format
        result["preview_type"] = "document" if doc_ext in preview_exts else "download"
        if tool:
            result["tools"] = [tool]
        return result

    if preview_exts & VIDEO_EXTENSIONS or (not preview and all_exts & VIDEO_EXTENSIONS):
        result["format"] = "Video"
        result["preview_type"] = "video" if preview_exts & VIDEO_EXTENSIONS else "download"
        return result

    if preview_exts & IMAGE_EXTENSIONS or (not preview and all_exts & IMAGE_EXTENSIONS):
        result["format"] = "Image"
        result["preview_type"] = "image" if preview_exts & IMAGE_EXTENSIONS else "download"
        return result

    if ".py" in all_exts:
        result.update(
            {
                "format": "Python",
                "tools": ["Python"],
                "preview_type": "code" if ".py" in preview_exts else "download",
            }
        )
        return result

    if preview_exts & TEXT_EXTENSIONS or (not preview and all_exts & TEXT_EXTENSIONS):
        result["format"] = "Text/Markdown"
        result["preview_type"] = "text" if preview_exts & TEXT_EXTENSIONS else "download"
        return result

    if preview_exts & CODE_EXTENSIONS or (not preview and all_exts & CODE_EXTENSIONS):
        result["format"] = "Code"
        result["preview_type"] = "code" if preview_exts & CODE_EXTENSIONS else "download"
        return result

    if all_exts & ARCHIVE_EXTENSIONS:
        result["format"] = "Archive"
        result["preview_type"] = "download"
        return result

    result["preview_type"] = "download"
    return result
