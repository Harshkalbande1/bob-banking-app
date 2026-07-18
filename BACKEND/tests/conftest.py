"""
conftest.py — Shared pytest fixtures for the SecureBank test suite.

Provides:
  - an isolated in-memory SQLite database for each test session
  - a Flask test client pre-configured to use that database
"""

import os
import sqlite3
import sys

import pytest
from werkzeug.security import generate_password_hash

# Make BACKEND/ importable so tests can import db, services, routes, etc.
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, os.path.join(BACKEND_DIR, "services"))


# ---------------------------------------------------------------------------
# In-memory database helpers
# ---------------------------------------------------------------------------

def _create_test_db(path: str) -> None:
    """Create tables and seed one test user in the database at *path*."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS accounts (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
            balance REAL    NOT NULL DEFAULT 0.0
        );
        """
    )
    pw = generate_password_hash("testpass")
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        ("testuser", pw),
    )
    uid = cursor.lastrowid
    conn.execute(
        "INSERT INTO accounts (user_id, balance) VALUES (?, ?)", (uid, 500.0)
    )
    conn.commit()
    conn.close()


@pytest.fixture(scope="function")
def test_db_path(tmp_path):
    """Create a fresh temporary database file for each test function."""
    db_file = str(tmp_path / "test_bank.db")
    _create_test_db(db_file)
    return db_file


@pytest.fixture(scope="function")
def flask_app(test_db_path, monkeypatch):
    """
    Return a Flask test application wired to the temporary database.

    monkeypatch replaces DB_PATH in the db module so all service calls
    hit the test database instead of the real bank.db.
    """
    import db as db_module

    monkeypatch.setattr(db_module, "DB_PATH", test_db_path)

    # Also patch the copy of DB_PATH imported into services before app import.
    import services.auth_service as auth_svc
    import services.account_service as acct_svc

    monkeypatch.setattr(auth_svc, "get_db_connection", db_module.get_db_connection)
    monkeypatch.setattr(acct_svc, "get_db_connection", db_module.get_db_connection)

    import app as app_module

    app_module.app.config["TESTING"] = True
    app_module.app.config["WTF_CSRF_ENABLED"] = False
    app_module.app.secret_key = "test-secret"

    return app_module.app


@pytest.fixture(scope="function")
def client(flask_app):
    """Return a Flask test client."""
    with flask_app.test_client() as c:
        yield c


@pytest.fixture(scope="function")
def auth_client(flask_app, test_db_path, monkeypatch):
    """
    Return a Flask test client with an active 'testuser' session.
    Uses the test client context to simulate a logged-in user.
    """
    import db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", test_db_path)

    with flask_app.test_client() as c:
        # Log in via the real POST /login route to establish a session.
        c.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=False,
        )
        yield c
