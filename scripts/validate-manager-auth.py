"""Exercise the local Manager password gate without touching a real password file."""

from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "library-manager"))


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


with tempfile.TemporaryDirectory(prefix="manager-auth-check-") as temporary:
    auth_file = Path(temporary) / "auth.json"
    os.environ["LIBRARY_MANAGER_AUTH_FILE"] = str(auth_file)

    import app as manager
    from auth import ManagerAuth

    client = manager.app.test_client()
    expect("/setup" in client.get("/add").location, "Manager must require password setup on first launch")
    expect("/setup" in client.get("/repo/index.html").location, "Manager must protect repository files")
    expect(client.get("/static/auth.css").status_code == 200, "Password form stylesheet must be available")
    expect(client.get("/repo/assets/site/manager-favicon.svg").status_code == 200, "Password form icon must be available")
    expect(client.post("/setup", data={"password": "too short"}).status_code == 400, "Password setup must require a form token")
    client.get("/setup")
    with client.session_transaction() as browser_session:
        token = browser_session["csrf_token"]
    first_password = "manager-test-password-123"
    setup = client.post("/setup", data={"csrf_token": token, "password": first_password, "confirm_password": first_password, "next": "/add"})
    expect(setup.status_code == 302 and setup.location.endswith("/add"), "Password setup must unlock the requested page")
    expect(client.get("/add").status_code == 200, "Authenticated owner must access the Manager")
    expect(client.get("/repo/index.html").status_code == 200, "Authenticated owner must preview repository files")
    expect(stat.S_IMODE(auth_file.stat().st_mode) == 0o600, "Local password file must be private")
    saved = json.loads(auth_file.read_text(encoding="utf-8"))
    expect(first_password not in auth_file.read_text(encoding="utf-8") and saved["password_hash"].startswith("pbkdf2:sha256:"), "Store a slow password hash, never the password")
    expect(ManagerAuth(auth_file).secret_key == manager.AUTH.secret_key, "Session signing key must survive a restart")

    other = manager.app.test_client()
    expect("/login" in other.get("/library").location, "New browser must sign in")
    other.get("/login")
    with other.session_transaction() as browser_session:
        other_token = browser_session["csrf_token"]
    for _ in range(5):
        expect(other.post("/login", data={"csrf_token": other_token, "password": "wrong"}).status_code == 401, "Wrong password must fail")
    expect(other.post("/login", data={"csrf_token": other_token, "password": first_password}).status_code == 429, "Repeated guesses must be throttled")
    manager.AUTH.successful_login()
    signed_in = other.post("/login", data={"csrf_token": other_token, "password": first_password, "next": "//example.com"})
    expect(signed_in.status_code == 302 and signed_in.location.endswith("/library"), "Sign-in must reject external redirect targets")

    with client.session_transaction() as browser_session:
        token = browser_session["csrf_token"]
    second_password = "manager-new-password-456"
    changed = client.post("/password", data={"csrf_token": token, "current_password": first_password, "password": second_password, "confirm_password": second_password})
    expect(changed.status_code == 302 and manager.AUTH.verify(second_password) and not manager.AUTH.verify(first_password), "Password change must replace the old password")
    expect("/login" in other.get("/library").location, "Password change must invalidate other sessions")
    with client.session_transaction() as browser_session:
        token = browser_session["csrf_token"]
    expect(client.post("/logout", data={"csrf_token": token}).status_code == 302, "Lock action must sign out")
    expect("/login" in client.get("/library").location, "Locked session must require sign-in")

print("PASS: Manager password setup, private routes, slow hash, CSRF, throttling, password change, and lock")
