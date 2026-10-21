"""Category management service for user-owned task categories."""

from datetime import datetime
from pathlib import Path
import sqlite3

from config import DATETIME_FORMAT
from database import get_connection
import validators


def create_category(
    user_id: int,
    name: str,
    db_path: Path | str | None = None,
) -> tuple[bool, str, int | None]:
    """Create a new category for the authenticated user after validating uniqueness and format.
    
    Returns:
        tuple[bool, str, int | None]: (success_flag, user_message, new_category_id)
    """
    valid, msg = validators.validate_category_name(name)
    if not valid:
        return False, msg, None

    cleaned_name = name.strip()
    now_str = datetime.now().strftime(DATETIME_FORMAT)

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            
            # Case-insensitive duplicate check for this user
            cursor.execute(
                "SELECT id FROM categories WHERE user_id = ? AND name = ?",
                (user_id, cleaned_name),
            )
            if cursor.fetchone() is not None:
                return False, f"You already have a category named '{cleaned_name}'.", None
            
            cursor.execute(
                """
                INSERT INTO categories (user_id, name, created_at)
                VALUES (?, ?, ?)
                """,
                (user_id, cleaned_name, now_str),
            )
            cat_id = cursor.lastrowid
            return True, f"Category '{cleaned_name}' created successfully.", cat_id
    except sqlite3.IntegrityError:
        return False, f"A category named '{cleaned_name}' already exists for your account.", None
    except sqlite3.Error as e:
        return False, f"Database error creating category: {e}", None
    finally:
        conn.close()


def get_categories(
    user_id: int,
    db_path: Path | str | None = None,
) -> list[sqlite3.Row]:
    """Retrieve all categories belonging to the authenticated user, ordered alphabetically."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, name, created_at
            FROM categories
            WHERE user_id = ?
            ORDER BY name COLLATE NOCASE ASC
            """,
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_category_by_id(
    user_id: int,
    category_id: int,
    db_path: Path | str | None = None,
) -> sqlite3.Row | None:
    """Retrieve a single category, strictly checking ownership by user_id."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, name, created_at
            FROM categories
            WHERE id = ? AND user_id = ?
            """,
            (category_id, user_id),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def get_category_task_count(
    user_id: int,
    category_id: int,
    db_path: Path | str | None = None,
) -> int:
    """Return the number of tasks assigned to a specific category for this user."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM tasks
            WHERE category_id = ? AND user_id = ?
            """,
            (category_id, user_id),
        )
        row = cursor.fetchone()
        return row["count"] if row else 0
    finally:
        conn.close()


def delete_category(
    user_id: int,
    category_id: int,
    db_path: Path | str | None = None,
) -> tuple[bool, str]:
    """Safely delete a category if it belongs to the user and is NOT currently assigned to any tasks.
    
    Returns:
        tuple[bool, str]: (success_flag, user_message)
    """
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            
            # Check ownership and existence
            cursor.execute(
                "SELECT id, name FROM categories WHERE id = ? AND user_id = ?",
                (category_id, user_id),
            )
            cat_row = cursor.fetchone()
            if cat_row is None:
                return False, "Category not found or you do not have permission to delete it."
            
            cat_name = cat_row["name"]
            
            # Check if any tasks are assigned to this category
            cursor.execute(
                "SELECT COUNT(*) AS count FROM tasks WHERE category_id = ? AND user_id = ?",
                (category_id, user_id),
            )
            task_count_row = cursor.fetchone()
            task_count = task_count_row["count"] if task_count_row else 0
            
            if task_count > 0:
                return (
                    False,
                    f"Cannot delete category '{cat_name}'. It is currently assigned to {task_count} task(s). "
                    f"Please reassign or delete those tasks first.",
                )
            
            # Proceed with safe deletion
            cursor.execute(
                "DELETE FROM categories WHERE id = ? AND user_id = ?",
                (category_id, user_id),
            )
            return True, f"Category '{cat_name}' was deleted successfully."
    except sqlite3.IntegrityError:
        return False, "Cannot delete category due to active database foreign-key constraints."
    except sqlite3.Error as e:
        return False, f"Database error deleting category: {e}"
    finally:
        conn.close()
