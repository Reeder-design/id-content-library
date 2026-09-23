"""Local password storage and login throttling for Library Manager."""

from __future__ import annotations

import json
import os
import secrets
import tempfile
import threading
import time
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash


class ManagerAuth:
    def __init__(self, path: Path):
        self.path = path.expanduser()
        self._record = self._load()
        self._failures: list[float] = []
        self._blocked_until = 0.0
        self._lock = threading.Lock()

    @classmethod
    def from_environment(cls) -> "ManagerAuth":
        configured = os.environ.get("LIBRARY_MANAGER_AUTH_FILE")
        path = Path(configured) if configured else Path.home() / ".config" / "learning-content-lab" / "manager-auth.json"
        return cls(path)

    def _load(self) -> dict | None:
        if not self.path.exists():
            return None
        try:
            record = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Manager password file could not be read: {self.path}") from exc
        if not isinstance(record, dict) or record.get("version") != 1 or any(
            not isinstance(record.get(key), str) or not record[key]
            for key in ("password_hash", "secret_key", "revision")
        ):
            raise RuntimeError(f"Manager password file is invalid: {self.path}")
        return record

    @property
    def configured(self) -> bool:
        return self._record is not None

    @property
    def secret_key(self) -> str | None:
        return self._record["secret_key"] if self._record else None

    @property
    def revision(self) -> str | None:
        return self._record["revision"] if self._record else None

    def verify(self, password: str) -> bool:
        if not self._record or len(password) > 1024:
            return False
        try:
            return check_password_hash(self._record["password_hash"], password)
        except ValueError:
            return False

    def _write(self, record: dict, *, first_setup: bool) -> None:
        created_directory = not self.path.parent.exists()
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if created_directory:
            os.chmod(self.path.parent, 0o700)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent, prefix=".manager-auth-", delete=False) as output:
                temporary = Path(output.name)
                os.chmod(temporary, 0o600)
                json.dump(record, output)
                output.write("\n")
            if first_setup:
                os.link(temporary, self.path)
            else:
                os.replace(temporary, self.path)
                temporary = None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        self._record = record

    def create(self, password: str) -> None:
        if self.configured or self.path.exists():
            raise ValueError("The Manager password has already been set.")
        record = {
            "version": 1,
            "password_hash": generate_password_hash(password, method="pbkdf2:sha256:1000000"),
            "secret_key": secrets.token_hex(32),
            "revision": secrets.token_urlsafe(24),
        }
        self._write(record, first_setup=True)

    def change(self, password: str) -> None:
        if not self._record:
            raise ValueError("Set a Manager password first.")
        record = dict(self._record)
        record["password_hash"] = generate_password_hash(password, method="pbkdf2:sha256:1000000")
        record["revision"] = secrets.token_urlsafe(24)
        self._write(record, first_setup=False)

    def retry_after(self) -> int:
        with self._lock:
            if self._blocked_until and time.monotonic() >= self._blocked_until:
                self._blocked_until = 0.0
                self._failures.clear()
            return max(0, int(self._blocked_until - time.monotonic() + 0.999))

    def failed_login(self) -> None:
        now = time.monotonic()
        with self._lock:
            self._failures = [stamp for stamp in self._failures if now - stamp < 300]
            self._failures.append(now)
            if len(self._failures) >= 5:
                self._blocked_until = now + 60

    def successful_login(self) -> None:
        with self._lock:
            self._failures.clear()
            self._blocked_until = 0.0
