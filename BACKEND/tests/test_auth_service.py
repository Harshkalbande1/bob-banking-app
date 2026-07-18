"""
test_auth_service.py — Unit tests for services/auth_service.py.

Tests the credential-verification logic in total isolation from Flask.
Each test uses its own temporary database via the test_db_path fixture.
"""

import sqlite3
import sys
import os

import pytest
from werkzeug.security import generate_password_hash

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, os.path.join(BACKEND_DIR, "services"))


# ---------------------------------------------------------------------------
# verify_credentials
# ---------------------------------------------------------------------------

class TestVerifyCredentials:
    def test_valid_credentials_returns_user_id(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.auth_service import verify_credentials

        result = verify_credentials("testuser", "testpass")
        assert result is not None
        assert isinstance(result, int)
        assert result > 0

    def test_wrong_password_returns_none(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.auth_service import verify_credentials

        result = verify_credentials("testuser", "wrongpassword")
        assert result is None

    def test_nonexistent_user_returns_none(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.auth_service import verify_credentials

        result = verify_credentials("nobody", "anypassword")
        assert result is None

    def test_empty_username_returns_none(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.auth_service import verify_credentials

        result = verify_credentials("", "testpass")
        assert result is None

    def test_empty_password_returns_none(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.auth_service import verify_credentials

        result = verify_credentials("testuser", "")
        assert result is None

    def test_password_not_stored_as_plaintext(self, test_db_path, monkeypatch):
        """Confirm the database stores a hash, not the raw password string."""
        conn = sqlite3.connect(test_db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = 'testuser'"
        ).fetchone()
        conn.close()

        assert row is not None
        # The hash should not equal the plaintext password.
        assert row["password_hash"] != "testpass"
        # Werkzeug hashes begin with 'pbkdf2:', 'scrypt:', or 'bcrypt:'.
        assert row["password_hash"].startswith(("pbkdf2:", "scrypt:", "bcrypt:"))


# ---------------------------------------------------------------------------
# get_username
# ---------------------------------------------------------------------------

class TestGetUsername:
    def test_returns_username_for_valid_id(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.auth_service import verify_credentials, get_username

        user_id = verify_credentials("testuser", "testpass")
        assert get_username(user_id) == "testuser"

    def test_returns_none_for_invalid_id(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.auth_service import get_username

        assert get_username(99999) is None
