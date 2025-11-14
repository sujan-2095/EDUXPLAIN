"""User authentication and management."""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path
from typing import Optional, Tuple

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "eduxplain.db"


def _hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_auth_db() -> None:
    """Initialize users table."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def register_user(username: str, email: str, password: str) -> Tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    init_auth_db()
    
    if not username or not email or not password:
        return False, "All fields are required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    password_hash = _hash_password(password)
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (username.strip(), email.strip().lower(), password_hash),
            )
            conn.commit()
        return True, "Registration successful"
    except sqlite3.IntegrityError:
        return False, "Username or email already exists"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user. Returns user dict if successful, None otherwise."""
    init_auth_db()
    password_hash = _hash_password(password)
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT id, username, email, created_at
            FROM users
            WHERE (username = ? OR email = ?) AND password_hash = ?
            """,
            (username.strip(), username.strip().lower(), password_hash),
        )
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "created_at": row["created_at"],
            }
    return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID."""
    init_auth_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "created_at": row["created_at"],
            }
    return None

