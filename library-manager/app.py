from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path, PurePosixPath

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, send_from_directory, session, url_for

from smart_prefill import infer_from_files
from thumbnailer import AUTO_NAMES, generate_thumbnail
from workspace import publish as publish_workspace
from workspace import run_validation, summarize_changes, validation_ok

ROOT = Path(__file__).resolve().parents[1]
ITEMS_DIR = ROOT / "items"
OPTIONS_PATH = ROOT / "library-data" / "options.json"
BUILD_SCRIPT = ROOT / "scripts" / "build-library.py"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
UPLOAD_AREAS = ("preview", "source", "assets")
THUMBNAIL_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config.update(MAX_CONTENT_LENGTH=1024 * 1024 * 1024)
app.jinja_env.variable_start_string = "[["
app.jinja_env.variable_end_string = "]]"
app.jinja_env.block_start_string = "<%"
app.jinja_env.block_end_string = "%>"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_options() -> dict:
    return load_json(OPTIONS_PATH)


def clean(value) -> str:
    return str(value or "").strip()


def split_values(value: str) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for raw in re.split(r"[,\n]", value or ""):
        item = raw.strip()
        if item and item not in seen:
            seen.add(item)
            values.append(item)
    return values


def csrf_token() -> str:
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


app.jinja_env.globals["csrf_token"] = csrf_token


def require_csrf() -> None:
    expected = session.get("csrf_token")
    supplied = request.form.get("csrf_token")
    if not expected or not supplied or not secrets.compare_digest(expected, supplied):
        abort(400, "Invalid form token. Refresh the page and try again.")


def item_dir(slug: str) -> Path:
    if not SLUG_RE.fullmatch(slug):
        abort(404)
    return ITEMS_DIR / slug


def load_item(slug: str) -> dict:
    path = item_dir(slug) / "item.json"
    if not path.is_file():
        abort(404)
    return load_json(path)


def raw_items() -> list[dict]:
    items: list[dict] = []
    if not ITEMS_DIR.is_dir():
        return items
    for directory in sorted((path for path in ITEMS_DIR.iterdir() if path.is_dir()), key=lambda path: path.name):
        metadata = directory / "item.json"
        if metadata.is_file():
            items.append(load_json(metadata))
    return items


def load_items() -> list[dict]:
    items: list[dict] = []
    for item in raw_items():
        item = dict(item)
        slug = clean(item.get("slug"))
        item["_folder"] = str(ITEMS_DIR / slug)
        item["_preview_url"] = url_for("repo_file", filepath=f"items/{slug}/index.html")
        thumb = clean(item.get("thumbnail"))
        item["_thumbnail_url"] = url_for("repo_file", filepath=f"items/{slug}/{thumb}") if thumb else ""
        items.append(item)
    return sorted(items, key=lambda item: clean(item.get("title")).lower())


def suggestion_catalog(options: dict | None = None) -> dict[str, list[str]]:
    options = options or load_options()
    tool_counts: Counter[str] = Counter()
    tag_counts: Counter[str] = Counter()
    for item in raw_items():
        tool_counts.update(clean(value) for value in item.get("tools", []) if clean(value))
        tag_counts.update(clean(value) for value in item.get("tags", []) if clean(value))

    def ranked(counter: Counter[str], seeds=(), limit: int = 14) -> list[str]:
        ordered = [value for value, _ in sorted(counter.items(), key=lambda pair: (-pair[1], pair[0].lower()))]
        for seed in seeds:
            if seed not in ordered:
                ordered.append(seed)
        return ordered[:limit]

    return {
        "tools": ranked(tool_counts, options.get("tool_suggestions", [])),
        "tags": ranked(tag_counts, limit=16),
    }


def new_item_defaults(options: dict) -> dict:
    defaults = options.get("defaults", {})
    return {
        "created": date.today().isoformat(),
        "library_status": defaults.get("library_status", "stable"),
        "portfolio_status": defaults.get("portfolio_status", "library-only"),
    }


def safe_upload_path(filename: str) -> Path:
    normalized = clean(filename).replace("\\", "/")
    path = PurePosixPath(normalized)
    if not normalized or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Unsafe upload path: {filename!r}")
    if any(part.startswith(".") for part in path.parts):
        raise ValueError(f"Hidden files and folders are not supported: {filename!r}")
    return Path(*path.parts)


def form_metadata(existing: dict | None = None) -> dict:
    options = load_options()
    slug = clean(request.form.get("slug"))
    if existing:
        slug = clean(existing.get("slug"))

    item = {
        "title": clean(request.form.get("title")),
        "slug": slug,
        "summary": clean(request.form.get("summary")),
        "content_type": clean(request.form.get("content_type")),
        "format": clean(request.form.get("format")),
        "tools": split_values(request.form.get("tools", "")),
        "tags": split_values(request.form.get("tags", "")),
        "library_status": clean(request.form.get("library_status")),
        "preview_type": clean(request.form.get("preview_type")),
        "created": clean(request.form.get("created")),
    }

    optional_strings = ("updated", "portfolio_status", "thumbnail", "other_label", "usage_notes")
    for field in optional_strings:
        value = clean(request.form.get(field))
        if value:
            item[field] = value

    errors: list[str] = []
    for field in ("title", "slug", "summary", "content_type", "format", "library_status", "preview_type", "created"):
        if not clean(item.get(field)):
            errors.append(f"{field.replace('_', ' ').title()} is required.")
    if not SLUG_RE.fullmatch(slug):
        errors.append("Slug must use lowercase letters, numbers, and single hyphens.")
    if not item["tools"]:
        errors.append("Add at least one tool.")
    if not item["tags"]:
        errors.append("Add at least one tag.")

    controlled = {
        "content_type": options["content_types"],
        "library_status": options["library_statuses"],
        "preview_type": options["preview_types"],
    }
    if item.get("portfolio_status"):
        controlled["portfolio_status"] = options["portfolio_statuses"]
    for field, allowed in controlled.items():
        if item.get(field) not in allowed:
            errors.append(f"{field.replace('_', ' ').title()} has an unsupported value.")

    uses_other = any(
        item.get(field) in {"Other", "other"}
        for field in ("content_type", "library_status", "preview_type", "portfolio_status")
    )
    if uses_other and not item.get("other_label"):
        errors.append("Other label is required when a controlled field uses Other.")

    for field in ("created", "updated"):
        if item.get(field):
            try:
                date.fromisoformat(item[field])
            except ValueError:
                errors.append(f"{field.title()} must use YYYY-MM-DD.")

    if errors:
        raise ValueError(" ".join(errors))
    return item


def save_uploads(destination: Path, field_name: str) -> int:
    saved = 0
    for upload in request.files.getlist(field_name):
        if not upload or not clean(upload.filename):
            continue
        relative = safe_upload_path(upload.filename)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        upload.save(target)
        saved += 1
    return saved


def apply_uploads(directory: Path) -> int:
    saved = 0
    for area in UPLOAD_AREAS:
        if request.form.get(f"replace_{area}") == "1":
            shutil.rmtree(directory / area, ignore_errors=True)
        target = directory / area
        target.mkdir(parents=True, exist_ok=True)
        saved += save_uploads(target, f"{area}_files")
    return saved


def apply_custom_thumbnail(directory: Path, item: dict) -> bool:
    upload = request.files.get("thumbnail_file")
    if not upload or not clean(upload.filename):
        return False
    suffix = Path(clean(upload.filename)).suffix.lower()
    if suffix not in THUMBNAIL_SUFFIXES:
        raise ValueError("Custom preview image must be PNG, JPG, JPEG, WEBP, GIF, or SVG.")
    assets = directory / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for path in assets.glob("custom-thumbnail.*"):
        path.unlink()
    for name in AUTO_NAMES:
        path = assets / name
        if path.exists():
            path.unlink()
    target = assets / f"custom-thumbnail{suffix}"
    upload.save(target)
    item["thumbnail"] = f"assets/{target.name}"
    return True


def write_metadata(directory: Path, item: dict) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for area in UPLOAD_AREAS:
        (directory / area).mkdir(exist_ok=True)
    (directory / "item.json").write_text(json.dumps(item, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def rebuild_library() -> None:
    result = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "Unknown build failure").strip()
        raise RuntimeError(detail)


def finish_item_files(directory: Path, item: dict) -> dict:
    custom = apply_custom_thumbnail(directory, item)
    write_metadata(directory, item)
    rebuild_library()
    if custom:
        return {"kind": "custom", "message": "Using your custom preview image."}
    result = generate_thumbnail(directory, item, request.host_url.rstrip("/"))
    item["thumbnail"] = result["path"]
    write_metadata(directory, item)
    return result


def mutate_existing(slug: str, mutation) -> None:
    directory = item_dir(slug)
    if not directory.is_dir():
        abort(404)
    with tempfile.TemporaryDirectory(prefix="library-manager-") as temp:
        backup = Path(temp) / slug
        shutil.copytree(directory, backup)
        try:
            mutation(directory)
            rebuild_library()
        except Exception:
            shutil.rmtree(directory, ignore_errors=True)
            shutil.copytree(backup, directory)
            rebuild_library()
            raise


def open_folder(path: Path) -> None:
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    elif os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", str(path)])


def render_item_form(mode: str, item, options: dict, *, status: int = 200):
    return (
        render_template(
            "item-form.html",
            mode=mode,
            item=item,
            options=options,
            suggestions=suggestion_catalog(options),
        ),
        status,
    )


@app.context_processor
def manager_context():
    try:
        summary = summarize_changes(ROOT)
        count = summary.get("item_count", 0)
    except Exception:
        count = 0
    return {"workspace_change_count": count}


@app.get("/")
def home():
    return redirect(url_for("library"))


@app.get("/library")
def library():
    return render_template("library.html", items=load_items())


@app.get("/workspace")
def workspace_page():
    return render_template("workspace.html", summary=summarize_changes(ROOT), checks=None, publish_result=None)


@app.post("/workspace/validate")
def validate_workspace():
    require_csrf()
    checks = run_validation(ROOT)
    return render_template(
        "workspace.html",
        summary=summarize_changes(ROOT),
        checks=checks,
        validation_passed=validation_ok(checks),
        publish_result=None,
    )


@app.post("/workspace/publish")
def publish_changes():
    require_csrf()
    if request.form.get("reviewed") != "1" or request.form.get("public_safe") != "1":
        result = {"ok": False, "message": "Confirm both review checks before publishing."}
        return render_template("workspace.html", summary=summarize_changes(ROOT), checks=None, publish_result=result), 400
    result = publish_workspace(ROOT)
    return render_template(
        "workspace.html",
        summary=summarize_changes(ROOT),
        checks=result.get("checks"),
        validation_passed=result.get("ok", False),
        publish_result=result,
    ), (200 if result.get("ok") else 400)


@app.post("/api/prefill")
def prefill():
    payload = request.get_json(silent=True) or {}
    files = payload.get("files", [])
    if not isinstance(files, list) or len(files) > 10000:
        abort(400, "files must be a JSON list with at most 10,000 entries")
    if any(not isinstance(entry, dict) for entry in files):
        abort(400, "each file entry must be an object")
    return jsonify(infer_from_files(files))


@app.route("/add", methods=["GET", "POST"])
def add_item():
    options = load_options()
    if request.method == "GET":
        return render_item_form("add", new_item_defaults(options), options)

    require_csrf()
    try:
        item = form_metadata()
        directory = item_dir(item["slug"])
        if directory.exists():
            raise ValueError("That slug already exists. Choose a different slug.")
        directory.mkdir(parents=True)
        try:
            apply_uploads(directory)
            thumbnail_result = finish_item_files(directory, item)
            rebuild_library()
        except Exception:
            shutil.rmtree(directory, ignore_errors=True)
            rebuild_library()
            raise
    except (ValueError, RuntimeError) as exc:
        flash(str(exc), "error")
        return render_item_form("add", request.form, options, status=400)

    flash(f"Added {item['title']} locally. {thumbnail_result['message']} Review it before publishing.", "success")
    return redirect(url_for("library"))


@app.route("/items/<slug>/edit", methods=["GET", "POST"])
def edit_item(slug: str):
    existing = load_item(slug)
    options = load_options()
    if request.method == "GET":
        return render_item_form("edit", existing, options)

    require_csrf()
    thumbnail_result: dict = {"message": "Preview image kept."}
    try:
        updated = form_metadata(existing=existing)
        updated["updated"] = date.today().isoformat()

        def mutation(directory: Path) -> None:
            nonlocal thumbnail_result
            apply_uploads(directory)
            thumbnail_result = finish_item_files(directory, updated)

        mutate_existing(slug, mutation)
    except (ValueError, RuntimeError) as exc:
        flash(str(exc), "error")
        return render_item_form("edit", request.form, options, status=400)

    flash(f"Saved changes to {updated['title']} locally. {thumbnail_result['message']}", "success")
    return redirect(url_for("library"))


@app.post("/items/<slug>/thumbnail/regenerate")
def regenerate_thumbnail(slug: str):
    require_csrf()
    item = load_item(slug)
    current = clean(item.get("thumbnail"))
    if current and Path(current).name not in AUTO_NAMES:
        flash("This item uses a custom preview image. Edit the item to replace it.", "error")
        return redirect(url_for("library"))

    result: dict = {}

    def mutation(directory: Path) -> None:
        nonlocal result
        rebuild_library()
        result = generate_thumbnail(directory, item, request.host_url.rstrip("/"))
        item["thumbnail"] = result["path"]
        item["updated"] = date.today().isoformat()
        write_metadata(directory, item)

    try:
        mutate_existing(slug, mutation)
    except RuntimeError as exc:
        flash(f"Could not refresh the preview image: {exc}", "error")
    else:
        flash(result.get("message", "Preview image refreshed."), "success")
    return redirect(url_for("library"))


@app.post("/items/<slug>/archive")
def archive_item(slug: str):
    require_csrf()
    item = load_item(slug)

    def mutation(directory: Path) -> None:
        item["library_status"] = "archived"
        item["updated"] = date.today().isoformat()
        write_metadata(directory, item)

    try:
        mutate_existing(slug, mutation)
    except RuntimeError as exc:
        flash(f"Archive failed: {exc}", "error")
    else:
        flash(f"Archived {item['title']}. You can still edit or restore it later.", "success")
    return redirect(url_for("library"))


@app.post("/items/<slug>/open-files")
def open_files(slug: str):
    require_csrf()
    directory = item_dir(slug)
    if not directory.is_dir():
        abort(404)
    try:
        open_folder(directory)
    except OSError as exc:
        flash(f"Could not open the item folder: {exc}", "error")
    else:
        flash(f"Opened {directory}.", "success")
    return redirect(url_for("library"))


@app.route("/items/<slug>/delete", methods=["GET", "POST"])
def delete_item(slug: str):
    item = load_item(slug)
    required_phrase = f"DELETE {slug}"
    if request.method == "GET":
        return render_template("delete.html", item=item, required_phrase=required_phrase)

    require_csrf()
    if request.form.get("confirm_phrase") != required_phrase or request.form.get("understand") != "1":
        flash("Delete protection did not pass. Type the exact phrase and confirm the checkbox.", "error")
        return render_template("delete.html", item=item, required_phrase=required_phrase), 400

    directory = item_dir(slug)
    with tempfile.TemporaryDirectory(prefix="library-manager-delete-") as temp:
        backup = Path(temp) / slug
        shutil.copytree(directory, backup)
        try:
            shutil.rmtree(directory)
            rebuild_library()
        except Exception as exc:
            shutil.copytree(backup, directory)
            rebuild_library()
            flash(f"Delete failed and was rolled back: {exc}", "error")
            return redirect(url_for("library"))

    flash(f"Deleted {item['title']} locally. Review the removal before publishing.", "success")
    return redirect(url_for("library"))


@app.get("/repo/<path:filepath>")
def repo_file(filepath: str):
    requested = (ROOT / filepath).resolve()
    try:
        requested.relative_to(ROOT.resolve())
    except ValueError:
        abort(404)
    if not requested.is_file():
        abort(404)
    return send_from_directory(ROOT, filepath)


@app.get("/health")
def health():
    return {"status": "ok", "scope": "local-only"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
