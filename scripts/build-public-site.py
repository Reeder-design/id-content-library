from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_FILES = ("index.html",)
OPTIONAL_PUBLIC_FILES = ("CNAME", "robots.txt")
PUBLIC_DIRS = (
    "css",
    "js",
    "assets/site",
    "items",
    "library-data",
)
FORBIDDEN_TOP_LEVEL = {
    ".git",
    ".github",
    ".venv",
    "docs",
    "library-manager",
    "scripts",
    "templates",
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def copy_directory(source: Path, destination: Path) -> None:
    if not source.is_dir():
        fail(f"Missing required public directory: {source.relative_to(ROOT)}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, dirs_exist_ok=True)


def build(output: Path) -> Path:
    output = output.resolve()
    root = ROOT.resolve()
    if output == root or root in output.parents:
        fail("Public-site output must live outside the repository so generated deployment files never become source files.")

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    for relative in PUBLIC_FILES:
        source = ROOT / relative
        if not source.is_file():
            fail(f"Missing required public file: {relative}")
        shutil.copy2(source, output / relative)

    for relative in OPTIONAL_PUBLIC_FILES:
        source = ROOT / relative
        if source.is_file():
            shutil.copy2(source, output / relative)

    for relative in PUBLIC_DIRS:
        copy_directory(ROOT / relative, output / relative)

    (output / ".nojekyll").write_text("", encoding="utf-8")

    forbidden = sorted(name for name in FORBIDDEN_TOP_LEVEL if (output / name).exists())
    if forbidden:
        fail("Private/repository-only paths leaked into the public artifact: " + ", ".join(forbidden))

    print(f"PUBLIC BUILD: {output}")
    print("Included: index.html, css, js, assets/site, items, library-data")
    print("Excluded: Library Manager, scripts, docs, templates, workflows, and repository internals")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the static public Learning Content Lab artifact.")
    parser.add_argument("--output", required=True, help="Output directory outside the repository.")
    args = parser.parse_args()
    build(Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
