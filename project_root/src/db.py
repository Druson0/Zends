# src/db.py
"""Database utilities for the RAG API.

This module establishes a PostgreSQL connection (using ``psycopg2``) and provides
helpers to initialise the schema, manage users, and log query interactions.

In a production deployment you should store all credentials in environment
variables (or a secret manager) rather than hard‑coding them. The ``dotenv``
package is already a dependency, so you can place the values in a ``.env`` file
next to ``project_root`` and load them here.
"""

import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables from .env file
load_dotenv()
from psycopg2 import sql
from psycopg2.extras import DictCursor

# ---------------------------------------------------------------------------
# Configuration – read from environment variables; fall back to safe defaults
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "database": os.getenv("POSTGRES_DB", "rag_db"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "your_password"),
    # Optional: explicit port (default PostgreSQL port is 5432)
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
}


def get_connection():
    """Return a new ``psycopg2`` connection using ``DB_CONFIG``.

    The connection uses a ``DictCursor`` so rows can be accessed by column name.
    """
    return psycopg2.connect(**DB_CONFIG, cursor_factory=DictCursor)


def init_db():
    """Create the required tables if they do not already exist.

    Tables:
        * ``users`` – stores usernames and (hashed) passwords.
        * ``query_logs`` – records each user query and the generated response.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Users table – password should be a hashed value (e.g., bcrypt)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # Query log table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS query_logs (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            query TEXT NOT NULL,
            response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()


def add_user(username: str, password: str) -> bool:
    """Insert a new user.

    Returns ``True`` on success, ``False`` if the username already exists.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password),
        )
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def verify_user(username: str, password: str) -> bool:
    """Check whether the supplied credentials match a record.

    For a real app you would compare a hashed password (e.g., bcrypt) rather
    than storing plaintext passwords.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM users WHERE username = %s AND password = %s",
        (username, password),
    )
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists


def log_query(username: str, query: str, response: str | None = None) -> None:
    """Insert a row into ``query_logs`` for auditing purposes."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO query_logs (username, query, response) VALUES (%s, %s, %s)",
        (username, query, response),
    )
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("PostgreSQL tables initialized.")
