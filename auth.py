"""Authentication service handling registration, password hashing, and user sessions."""

from datetime import datetime
import hashlib
import hmac
import os
from pathlib import Path
import sqlite3
from typing import Any

from config import (
    DATETIME_FORMAT,
    DEFAULT_CATEGORIES,
    PASSWORD_HASH_ROUNDS,
    PASSWORD_SALT_BYTES,
)
from database import get_connection
import validators


def hash_password(password: str, salt_bytes: bytes | None = None) -> tuple[str, str]:
    """Generate a PBKDF2-HMAC-SHA256 password hash using a secure random salt.
    
    Returns:
        tuple[str, str]: (hex-encoded hash digest, hex-encoded salt)
    """
    if salt_bytes is None:
        salt_bytes = os.urandom(PASSWORD_SALT_BYTES)
        
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        PASSWORD_HASH_ROUNDS,
    )
    return digest.hex(), salt_bytes.hex()


def verify_password(password: str, stored_hash_hex: str, salt_hex: str) -> bool:
    """Verify password against the stored PBKDF2-HMAC-SHA256 hash using constant-time comparison."""
    try:
        salt_bytes = bytes.fromhex(salt_hex)
        candidate_digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt_bytes,
            PASSWORD_HASH_ROUNDS,
        )
        return hmac.compare_digest(candidate_digest.hex(), stored_hash_hex)
    except Exception:
        return False


def register_user(
    username: str,
    password: str,
    confirm_password: str,
    db_path: Path | str | None = None,
) -> tuple[bool, str, int | None]:
    """Validate registration input and register a new user with default categories.
    
    All operations occur inside a single database transaction.
    
    Returns:
        tuple[bool, str, int | None]: (success_flag, user_message, new_user_id)
    """
    normalized_username = (username or "").strip()
    
    # 1. Validation checks
    valid, msg = validators.validate_username(normalized_username)
    if not valid:
        return False, msg, None

    valid, msg = validators.validate_password(password)
    if not valid:
        return False, msg, None

    valid, msg = validators.validate_password_confirmation(password, confirm_password)
    if not valid:
        return False, msg, None

    # 2. Database registration transaction
    hash_hex, salt_hex = hash_password(password)
    now_str = datetime.now().strftime(DATETIME_FORMAT)

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            
            # Check for existing user (case-insensitive)
            cursor.execute("SELECT id FROM users WHERE username = ?", (normalized_username,))
            if cursor.fetchone() is not None:
                return False, f"Username '{normalized_username}' is already taken. Please choose another.", None
            
            # Insert new user record
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, password_salt, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (normalized_username, hash_hex, salt_hex, now_str),
            )
            user_id = cursor.lastrowid
            
            # Insert standard default categories for this user
            for cat_name in DEFAULT_CATEGORIES:
                cursor.execute(
                    """
                    INSERT INTO categories (user_id, name, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (user_id, cat_name, now_str),
                )
                
        return True, "Account created successfully! You can now log in.", user_id
    except sqlite3.IntegrityError:
        return False, f"Username '{normalized_username}' is already in use.", None
    except sqlite3.Error as e:
        return False, f"Database error during registration: {e}", None
    finally:
        conn.close()


def login_user(
    username: str,
    password: str,
    db_path: Path | str | None = None,
) -> tuple[bool, str, dict[str, Any] | None]:
    """Authenticate user credentials.
    
    Returns a generic error message upon failure to prevent username enumeration.
    
    Returns:
        tuple[bool, str, dict | None]: (success_flag, user_message, user_session_dict)
    """
    normalized_username = (username or "").strip()
    if not normalized_username or not password:
        return False, "Please enter both username and password.", None

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, password_hash, password_salt, created_at
            FROM users
            WHERE username = ?
            """,
            (normalized_username,),
        )
        row = cursor.fetchone()
        
        if row is not None:
            if verify_password(password, row["password_hash"], row["password_salt"]):
                user_session = {
                    "id": row["id"],
                    "username": row["username"],
                    "created_at": row["created_at"],
                }
                return True, "Login successful.", user_session
        
        # Generic message regardless of whether user exists or password was wrong
        return False, "Invalid username or password.", None
    except sqlite3.Error as e:
        return False, f"Database error during login: {e}", None
    finally:
        conn.close()
