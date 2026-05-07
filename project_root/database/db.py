# database/db.py
"""Simple SQLite helper for user management and document storage.
Provides functions to initialise the database, add users, and retrieve users.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "users.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create the users table if it doesn't exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                api_key TEXT NOT NULL
            );
            """
        )
        conn.commit()

def add_user(username: str, api_key: str):
    """Insert a new user. Raises sqlite3.IntegrityError on duplicate username."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO users (username, api_key) VALUES (?, ?)",
            (username, api_key),
        )
        conn.commit()

def get_user(username: str):
    """Retrieve a user record as a dict or None if not found."""
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        return dict(row) if row else None

if __name__ == "__main__":
    init_db()
    print(f"Database initialised at {DB_PATH}")
