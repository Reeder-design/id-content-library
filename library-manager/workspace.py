from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass
class CheckResult:
    label: str
    ok: bool
    detail: str


def _run(root: Path, args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=root,
        capture_output=True,
        text=True,
        check=check,
    )


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return _run(root, ["git", *args])


def current_branch(root: Path) -> str:
    result = git(root, "branch", "--show-current")
    return result.stdout.strip() if result.returncode == 0 else ""


def changed_paths(root: Path) -> list[dict[str, str]]:
    result = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if result.returncode != 0:
        return []
    changes: list[dict[str, str]] = []
    for raw in result.stdout.splitlines():
        if len(raw) < 4:
            continue
        status = raw[:2]
        path = raw[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changes.append({"status": status, "path": path})
    return changes


def _kind(status: str) -> str:
    if status == "??" or "A" in status:
        return "added"
    if "D" in status:
        return "removed"
    return "updated"


def summarize_changes(root: Path) -> dict:
    changes = changed_paths(root)
    buckets: dict[str, set[str]] = {"added": set(), "updated": set(), "removed": set()}
    other: list[str] = []
    generated = False

    for change in changes:
        path = change["path"]
        if path.startswith("items/"):
            parts = Path(path).parts
            if len(parts) >= 2:
                buckets[_kind(change["status"])].add(parts[1])
            continue
        if path == "library-data/items.json":
            generated = True
            continue
        other.append(path)

    return {
        "branch": current_branch(root),
        "count": len(changes),
        "has_changes": bool(changes),
        "added": sorted(buckets["added"]),
        "updated": sorted(buckets["updated"] - buckets["added"] - buckets["removed"]),
        "removed": sorted(buckets["removed"]),
        "generated": generated,
        "other": sorted(other),
        "raw": changes,
    }


def run_validation(root: Path) -> list[CheckResult]:
    checks = [
        ("Library metadata", [sys.executable, "scripts/validate-library.py"]),
        ("Item files and generated pages", [sys.executable, "scripts/validate-manager-workspace.py"]),
        ("Generated site is current", [sys.executable, "scripts/build-library.py", "--check"]),
        ("Preview support", [sys.executable, "scripts/validate-item-pages.py"]),
    ]
    results: list[CheckResult] = []
    for label, command in checks:
        result = _run(root, command)
        output = (result.stdout or result.stderr or "").strip()
        if result.returncode == 0:
            last_line = output.splitlines()[-1] if output else "Passed"
            results.append(CheckResult(label, True, last_line))
        else:
            detail = output.splitlines()[-1] if output else "Validation failed."
            results.append(CheckResult(label, False, detail))
    return results


def validation_ok(results: list[CheckResult]) -> bool:
    return bool(results) and all(result.ok for result in results)


def _remote_position(root: Path) -> tuple[int, int] | None:
    result = git(root, "rev-list", "--left-right", "--count", "HEAD...origin/main")
    if result.returncode != 0:
        return None
    parts = result.stdout.strip().split()
    if len(parts) != 2:
        return None
    return int(parts[0]), int(parts[1])


def publish(root: Path) -> dict:
    summary = summarize_changes(root)
    if summary["branch"] != "main":
        return {"ok": False, "message": "Publishing is only available from the local main branch. Switch to main and pull the latest version first."}
    if not summary["has_changes"]:
        return {"ok": False, "message": "There are no local library changes to publish."}
    if summary["other"]:
        return {
            "ok": False,
            "message": "There are local changes outside Library Manager content. Nothing was published so those files cannot be committed by accident.",
            "other": summary["other"],
        }

    checks = run_validation(root)
    if not validation_ok(checks):
        return {"ok": False, "message": "Validation found something that needs attention. Nothing was published.", "checks": checks}

    fetch = git(root, "fetch", "origin")
    if fetch.returncode != 0:
        return {"ok": False, "message": "Could not check GitHub for newer changes. Nothing was published."}

    position = _remote_position(root)
    if position is None:
        return {"ok": False, "message": "Could not compare your local copy with GitHub. Nothing was published."}
    ahead, behind = position
    if ahead or behind:
        if behind:
            message = "GitHub has newer changes than this local copy. Pull/sync main first, then reopen Review & Publish."
        else:
            message = "This local main branch already has unpublished Git commits. Publish them or reconcile them before using Library Manager publishing."
        return {"ok": False, "message": message, "ahead": ahead, "behind": behind}

    add = git(root, "add", "--", "items", "library-data/items.json")
    if add.returncode != 0:
        return {"ok": False, "message": "Could not prepare the library changes for publishing."}

    staged = git(root, "diff", "--cached", "--quiet")
    if staged.returncode == 0:
        return {"ok": False, "message": "No Library Manager content changes were ready to publish."}

    message = f"Publish Learning Content Lab updates ({date.today().isoformat()})"
    commit = git(root, "commit", "-m", message)
    if commit.returncode != 0:
        return {"ok": False, "message": "Git could not create the publish commit. Nothing was pushed to GitHub.", "detail": (commit.stderr or commit.stdout).strip()}

    push = git(root, "push", "origin", "main")
    if push.returncode != 0:
        return {
            "ok": False,
            "message": "The local publish commit was created, but GitHub rejected the push. Your work is still safe locally.",
            "detail": (push.stderr or push.stdout).strip(),
        }

    sha = git(root, "rev-parse", "--short", "HEAD").stdout.strip()
    return {"ok": True, "message": "Published to GitHub successfully.", "sha": sha, "checks": checks}
