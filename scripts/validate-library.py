from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPTIONS_PATH = ROOT / "library-data" / "options.json"
AGGREGATE_PATH = ROOT / "library-data" / "items.json"
FIXTURES = [
    ROOT / "tests" / "fixtures" / "valid-item" / "item.json",
    ROOT / "tests" / "fixtures" / "other-item" / "item.json",
]

REQUIRED_FIELDS = {
    "title",
    "slug",
    "summary",
    "content_type",
    "format",
    "tools",
    "tags",
    "library_status",
    "preview_type",
    "created",
}
OPTIONAL_FIELDS = {"updated", "portfolio_status", "thumbnail", "other_label", "usage_notes"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Missing required file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")


def nonempty_string(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_date(value, field: str, source: str) -> None:
    if not nonempty_string(value):
        fail(f"{source}: {field} must be a non-empty YYYY-MM-DD string")
    try:
        date.fromisoformat(value)
    except ValueError:
        fail(f"{source}: {field} must use YYYY-MM-DD")


def validate_item(item: dict, source: str, options: dict) -> None:
    if not isinstance(item, dict):
        fail(f"{source}: item must be a JSON object")

    missing = REQUIRED_FIELDS - item.keys()
    if missing:
        fail(f"{source}: missing required fields: {', '.join(sorted(missing))}")

    unknown = item.keys() - REQUIRED_FIELDS - OPTIONAL_FIELDS
    if unknown:
        fail(f"{source}: unknown fields: {', '.join(sorted(unknown))}")

    for field in ("title", "summary", "format"):
        if not nonempty_string(item[field]):
            fail(f"{source}: {field} must be a non-empty string")

    if not nonempty_string(item["slug"]) or not SLUG_RE.fullmatch(item["slug"]):
        fail(f"{source}: slug must use lowercase letters, numbers, and single hyphens")

    for field in ("tools", "tags"):
        values = item[field]
        if not isinstance(values, list) or not values or not all(nonempty_string(v) for v in values):
            fail(f"{source}: {field} must be a non-empty list of non-empty strings")
        if len(values) != len(set(values)):
            fail(f"{source}: {field} cannot contain duplicates")

    controlled = {
        "content_type": options["content_types"],
        "library_status": options["library_statuses"],
        "preview_type": options["preview_types"],
    }
    if "portfolio_status" in item:
        controlled["portfolio_status"] = options["portfolio_statuses"]

    for field, allowed in controlled.items():
        if item[field] not in allowed:
            fail(f"{source}: {field} has unsupported value {item[field]!r}")

    uses_other = (
        item["content_type"] == "Other"
        or item["library_status"] == "other"
        or item["preview_type"] == "other"
        or item.get("portfolio_status") == "other"
    )
    if uses_other and not nonempty_string(item.get("other_label")):
        fail(f"{source}: other_label is required when a controlled field uses Other/other")

    check_date(item["created"], "created", source)
    if "updated" in item:
        check_date(item["updated"], "updated", source)

    for field in ("thumbnail", "other_label", "usage_notes"):
        if field in item and not nonempty_string(item[field]):
            fail(f"{source}: {field} must be a non-empty string when present")


def main() -> int:
    options = load_json(OPTIONS_PATH)
    required_option_keys = {
        "content_types",
        "library_statuses",
        "preview_types",
        "portfolio_statuses",
        "format_suggestions",
        "tool_suggestions",
        "defaults",
    }
    missing_options = required_option_keys - options.keys()
    if missing_options:
        fail("options.json is missing keys: " + ", ".join(sorted(missing_options)))

    for fixture in FIXTURES:
        validate_item(load_json(fixture), str(fixture.relative_to(ROOT)), options)

    aggregate = load_json(AGGREGATE_PATH)
    if not isinstance(aggregate, list):
        fail("library-data/items.json must contain a JSON array")

    slugs: list[str] = []
    for index, item in enumerate(aggregate):
        source = f"library-data/items.json[{index}]"
        validate_item(item, source, options)
        slugs.append(item["slug"])

    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        fail("Duplicate slugs in library-data/items.json: " + ", ".join(duplicates))

    print("PASS: Item schema conventions and fixtures are valid")
    print(f"PASS: Aggregated library data contains {len(aggregate)} item(s) with unique slugs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
