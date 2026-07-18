"""
db.py — SQLite connection helper and database initialisation.

Responsibilities:
  - get_db_connection(): open and return a configured sqlite3 connection.
  - init_db(): create tables if they do not exist; seed one test customer.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# Absolute path to bank.db, always relative to this file so it works
# regardless of the working directory from which `flask run` is invoked.
DB_PATH = os.path.join(os.path.dirname(__file__), "bank.db")


def get_db_connection() -> sqlite3.Connection:
    """Open and return a new SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # columns accessible by name
    conn.execute("PRAGMA journal_mode=WAL")  # safer concurrent reads
    return conn


def init_db() -> None:
    """
    Create the users and accounts tables if they do not exist, then seed
    two demo customers if the database is empty.

    Table layout (planning-level, no SQL exported to the plan doc):
      users    — id, username, password_hash
      accounts — id, user_id (FK → users.id), balance
    """
    conn = get_db_connection()
    try:
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
        conn.commit()

        # Seed demo data only when the users table is empty.
        row = conn.execute("SELECT COUNT(*) AS cnt FROM users").fetchone()
        if row["cnt"] == 0:
            seed_customers = [
                ("alice", "password123", 1500.00),
                ("bob", "securepass", 750.50),
            ]
            for username, password, balance in seed_customers:
                pw_hash = generate_password_hash(password)
                cursor = conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, pw_hash),
                )
                user_id = cursor.lastrowid
                conn.execute(
                    "INSERT INTO accounts (user_id, balance) VALUES (?, ?)",
                    (user_id, balance),
                )
            conn.commit()
    finally:
        conn.close()
