from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DATE = "2026-09-15"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def run(root: Path, *args: str) -> None:
    result = subprocess.run(args, cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stdout + "\n" + result.stderr).strip()
        raise SystemExit(f"FAIL: {' '.join(args)}\n{detail}")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def add_reference_fixtures(root: Path) -> None:
    items = root / "items"
    if items.exists():
        shutil.rmtree(items)
    items.mkdir()

    interactive = items / "qa-branching-interaction"
    (interactive / "preview").mkdir(parents=True)
    (interactive / "source").mkdir()
    (interactive / "assets").mkdir()
    write_json(
        interactive / "item.json",
        {
            "title": "QA Branching Interaction",
            "slug": "qa-branching-interaction",
            "summary": "Internal release fixture for an HTML and JavaScript learning interaction.",
            "content_type": "Interactive Learning",
            "format": "HTML/CSS/JavaScript",
            "tools": ["HTML", "CSS", "JavaScript"],
            "tags": ["qa", "branching", "interaction"],
            "library_status": "stable",
            "preview_type": "interactive",
            "created": FIXTURE_DATE,
            "portfolio_status": "library-only",
        },
    )
    interaction_html = """<!doctype html><html><head><meta charset='utf-8'><title>QA interaction</title></head><body><main><h1>Choose a response</h1><button id='choice'>Ask a discovery question</button><p id='feedback'></p></main><script>document.getElementById('choice').addEventListener('click',()=>document.getElementById('feedback').textContent='Good choice: discover the need before proposing a solution.');</script></body></html>"""
    (interactive / "preview" / "index.html").write_text(interaction_html, encoding="utf-8")
    (interactive / "source" / "interaction-source.html").write_text(interaction_html, encoding="utf-8")

    storyline = items / "qa-storyline-package"
    (storyline / "preview" / "story_content").mkdir(parents=True)
    (storyline / "source").mkdir()
    (storyline / "assets").mkdir()
    write_json(
        storyline / "item.json",
        {
            "title": "QA Storyline Package",
            "slug": "qa-storyline-package",
            "summary": "Internal release fixture for Storyline source plus a published browser preview.",
            "content_type": "Interactive Learning",
            "format": "Storyline",
            "tools": ["Articulate Storyline"],
            "tags": ["qa", "storyline", "published-output"],
            "library_status": "stable",
            "preview_type": "interactive",
            "created": FIXTURE_DATE,
            "portfolio_status": "library-only",
        },
    )
    (storyline / "source" / "qa-reference.story").write_text(
        "QA fixture only. This tests .story source packaging; it is not an Articulate-authored binary.",
        encoding="utf-8",
    )
    (storyline / "preview" / "story.html").write_text(
        "<!doctype html><html><head><meta charset='utf-8'><title>Storyline QA preview</title></head><body><h1>Published Storyline preview fixture</h1><p>The Lab detected story.html as the launch page.</p></body></html>",
        encoding="utf-8",
    )
    (storyline / "preview" / "story_content" / "fixture.js").write_text("window.qaStorylineFixture = true;\n", encoding="utf-8")

    prompt = items / "qa-prompt-framework"
    (prompt / "preview").mkdir(parents=True)
    (prompt / "source").mkdir()
    (prompt / "assets").mkdir()
    write_json(
        prompt / "item.json",
        {
            "title": "QA Prompt Framework",
            "slug": "qa-prompt-framework",
            "summary": "Internal release fixture for a reusable text and prompt resource.",
            "content_type": "Prompt Library",
            "format": "Text/Markdown",
            "tools": ["Other"],
            "tags": ["qa", "prompt", "framework"],
            "library_status": "stable",
            "preview_type": "text",
            "created": FIXTURE_DATE,
            "portfolio_status": "library-only",
        },
    )
    prompt_text = "# QA Prompt Framework\n\nUse the supplied goal, audience, constraints, and success criteria to draft a reusable learning asset.\n"
    (prompt / "preview" / "prompt.md").write_text(prompt_text, encoding="utf-8")
    (prompt / "source" / "prompt.md").write_text(prompt_text, encoding="utf-8")


def validate_public_artifact(site: Path) -> None:
    expected = [
        "index.html",
        ".nojekyll",
        "css/styles.css",
        "css/public-lab-theme.css",
        "js/library.js",
        "js/public-guide.js",
        "assets/site/favicon.svg",
        "library-data/items.json",
        "items/qa-branching-interaction/index.html",
        "items/qa-storyline-package/index.html",
        "items/qa-storyline-package/preview/story.html",
        "items/qa-storyline-package/source/qa-reference.story",
        "items/qa-prompt-framework/index.html",
    ]
    for relative in expected:
        expect((site / relative).exists(), f"Public artifact is missing {relative}")

    for forbidden in ("library-manager", "scripts", "docs", "templates", ".github", "README.md"):
        expect(not (site / forbidden).exists(), f"Private/repository-only path was deployed: {forbidden}")

    homepage = (site / "index.html").read_text(encoding="utf-8")
    theme = (site / "css" / "public-lab-theme.css").read_text(encoding="utf-8")
    expect('name="viewport"' in homepage, "Public homepage is missing its mobile viewport")
    expect("data-public-guide-open" in homepage, "Public Guide button is missing")
    expect("assets/site/favicon.svg" in homepage, "Public favicon is missing")
    expect("@media (max-width: 680px)" in theme, "Public Lab theme is missing its mobile breakpoint")
    expect("127.0.0.1" not in homepage and "localhost" not in homepage, "Public homepage contains a local-only address")


def main() -> int:
    workflow = (ROOT / ".github" / "workflows" / "deploy-pages.yml")
    expect(workflow.is_file(), "GitHub Pages deployment workflow is missing")
    workflow_text = workflow.read_text(encoding="utf-8")
    for token in (
        "actions/configure-pages@v5",
        "actions/upload-pages-artifact@v4",
        "actions/deploy-pages@v4",
        "pages: write",
        "id-token: write",
        "github-pages",
        "scripts/build-public-site.py",
    ):
        expect(token in workflow_text, f"Pages deployment workflow is missing {token}")

    with tempfile.TemporaryDirectory(prefix="content-lab-release-") as temp:
        temp_root = Path(temp)
        sandbox = temp_root / "repo"
        shutil.copytree(
            ROOT,
            sandbox,
            ignore=shutil.ignore_patterns(".git", ".venv", "venv", "__pycache__", ".pytest_cache"),
        )
        add_reference_fixtures(sandbox)

        run(sandbox, sys.executable, "scripts/validate-library.py")
        run(sandbox, sys.executable, "scripts/build-library.py")
        run(sandbox, sys.executable, "scripts/build-library.py", "--check")
        run(sandbox, sys.executable, "scripts/validate-item-pages.py")

        site = temp_root / "public-site"
        run(sandbox, sys.executable, "scripts/build-public-site.py", "--output", str(site))
        validate_public_artifact(site)

    print("PASS: Phase 8 Pages workflow contract")
    print("PASS: Phase 8 public artifact excludes Library Manager and repository internals")
    print("PASS: Phase 8 responsive/public Guide/favicon release contract")
    print("PASS: V1 reference fixtures — HTML/JS, Storyline packaging + published preview, and prompt/text")
    print("NOTE: The .story QA fixture validates packaging only; Articulate binary integrity requires a real authored .story file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
