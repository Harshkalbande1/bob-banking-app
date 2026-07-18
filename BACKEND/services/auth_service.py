"""
auth_service.py — Authentication business logic.

Responsible for verifying a username/password pair against the database.
Has no Flask dependency — purely Python so it can be unit-tested in isolation.
"""

from werkzeug.security import check_password_hash

from db import get_db_connection


def verify_credentials(username: str, password: str):
    """
    Check whether the given username and password are valid.

    Returns:
        The integer user_id if credentials are correct.
        None if the username does not exist or the password is wrong.

    Security note: we return the same None in both failure cases so callers
    cannot distinguish "no such user" from "wrong password", preventing
    username enumeration.
    """
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None  # username not found

    if not check_password_hash(row["password_hash"], password):
        return None  # wrong password

    return row["id"]  # success — return the user's primary key


def get_username(user_id: int) -> str | None:
    """
    Look up and return the username for a given user_id.
    Returns None if the user_id does not exist (should not happen in normal
    operation, but guarded against for safety).
    """
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT username FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()

    return row["username"] if row else None
