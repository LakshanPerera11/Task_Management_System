"""Task management business logic: CRUD operations, completion, search, filtering, and metrics."""

from datetime import date, datetime
from pathlib import Path
import sqlite3
from typing import Any

from config import DATETIME_FORMAT, VALID_TASK_STATUSES
from database import get_connection
import validators


def add_task(
    user_id: int,
    title: str,
    category_id: int,
    description: str = "",
    due_date: str | None = None,
    db_path: Path | str | None = None,
) -> tuple[bool, str, int | None]:
    """Validate and insert a new task owned by user_id."""
    # 1. Validation
    valid, msg = validators.validate_task_title(title)
    if not valid:
        return False, msg, None

    valid, msg = validators.validate_task_description(description)
    if not valid:
        return False, msg, None

    valid, msg = validators.validate_due_date(due_date)
    if not valid:
        return False, msg, None

    if not category_id:
        return False, "Please select a valid category.", None

    cleaned_title = title.strip()
    cleaned_desc = (description or "").strip()
    cleaned_due = due_date.strip() if due_date and due_date.strip() else None
    now_str = datetime.now().strftime(DATETIME_FORMAT)

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            
            # Verify category belongs to user_id
            cursor.execute(
                "SELECT id FROM categories WHERE id = ? AND user_id = ?",
                (category_id, user_id),
            )
            if cursor.fetchone() is None:
                return False, "The selected category does not exist or does not belong to you.", None

            cursor.execute(
                """
                INSERT INTO tasks (
                    user_id, category_id, title, description,
                    due_date, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'Pending', ?, ?)
                """,
                (user_id, category_id, cleaned_title, cleaned_desc, cleaned_due, now_str, now_str),
            )
            task_id = cursor.lastrowid
            return True, "Task added successfully.", task_id
    except sqlite3.IntegrityError as e:
        return False, f"Integrity error: {e}", None
    except sqlite3.Error as e:
        return False, f"Database error creating task: {e}", None
    finally:
        conn.close()


def get_task_by_id(
    user_id: int,
    task_id: int,
    db_path: Path | str | None = None,
) -> sqlite3.Row | None:
    """Retrieve a single task ensuring strict user ownership."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT t.id, t.user_id, t.category_id, t.title, t.description,
                   t.due_date, t.status, t.created_at, t.updated_at,
                   c.name AS category_name
            FROM tasks t
            JOIN categories c ON c.id = t.category_id AND c.user_id = t.user_id
            WHERE t.id = ? AND t.user_id = ?
            """,
            (task_id, user_id),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def get_tasks(
    user_id: int,
    status: str = "All",
    category_id: int | None = None,
    search_term: str = "",
    db_path: Path | str | None = None,
) -> list[sqlite3.Row]:
    """Retrieve tasks for the user with optional filters by status, category, and search term.
    
    Always enforces user_id ownership.
    Ordered with Pending tasks first, then sorted by due date ascending (nulls last), then id DESC.
    """
    query = """
        SELECT t.id, t.user_id, t.category_id, t.title, t.description,
               t.due_date, t.status, t.created_at, t.updated_at,
               c.name AS category_name
        FROM tasks t
        JOIN categories c ON c.id = t.category_id AND c.user_id = t.user_id
        WHERE t.user_id = ?
    """
    params: list[Any] = [user_id]

    if status in VALID_TASK_STATUSES:
        query += " AND t.status = ?"
        params.append(status)

    if category_id is not None and category_id > 0:
        query += " AND t.category_id = ?"
        params.append(category_id)

    cleaned_search = (search_term or "").strip()
    if cleaned_search:
        query += " AND t.title LIKE ?"
        params.append(f"%{cleaned_search}%")

    query += """
        ORDER BY 
            CASE WHEN t.status = 'Pending' THEN 0 ELSE 1 END,
            CASE WHEN t.due_date IS NULL OR t.due_date = '' THEN 1 ELSE 0 END,
            t.due_date ASC,
            t.id DESC
    """

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()


def update_task(
    user_id: int,
    task_id: int,
    title: str,
    category_id: int,
    description: str = "",
    due_date: str | None = None,
    status: str | None = None,
    db_path: Path | str | None = None,
) -> tuple[bool, str]:
    """Update an existing task owned by user_id."""
    # 1. Validation
    valid, msg = validators.validate_task_title(title)
    if not valid:
        return False, msg

    valid, msg = validators.validate_task_description(description)
    if not valid:
        return False, msg

    valid, msg = validators.validate_due_date(due_date)
    if not valid:
        return False, msg

    if status is not None:
        valid, msg = validators.validate_task_status(status)
        if not valid:
            return False, msg

    cleaned_title = title.strip()
    cleaned_desc = (description or "").strip()
    cleaned_due = due_date.strip() if due_date and due_date.strip() else None
    now_str = datetime.now().strftime(DATETIME_FORMAT)

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            
            # Ensure task exists and belongs to user
            cursor.execute(
                "SELECT id, status FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, user_id),
            )
            existing_task = cursor.fetchone()
            if existing_task is None:
                return False, "Task not found or you do not have permission to modify it."

            # Ensure category belongs to user
            cursor.execute(
                "SELECT id FROM categories WHERE id = ? AND user_id = ?",
                (category_id, user_id),
            )
            if cursor.fetchone() is None:
                return False, "The selected category does not exist or does not belong to you."

            target_status = status if status is not None else existing_task["status"]

            cursor.execute(
                """
                UPDATE tasks
                SET title = ?,
                    description = ?,
                    category_id = ?,
                    due_date = ?,
                    status = ?,
                    updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (cleaned_title, cleaned_desc, category_id, cleaned_due, target_status, now_str, task_id, user_id),
            )
            return True, "Task updated successfully."
    except sqlite3.Error as e:
        return False, f"Database error updating task: {e}"
    finally:
        conn.close()


def delete_task(
    user_id: int,
    task_id: int,
    db_path: Path | str | None = None,
) -> tuple[bool, str]:
    """Delete a task owned by user_id."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, user_id),
            )
            if cursor.rowcount == 0:
                return False, "Task not found or you do not have permission to delete it."
            return True, "Task deleted successfully."
    except sqlite3.Error as e:
        return False, f"Database error deleting task: {e}"
    finally:
        conn.close()


def mark_task_completed(
    user_id: int,
    task_id: int,
    db_path: Path | str | None = None,
) -> tuple[bool, str]:
    """Mark a pending task as completed."""
    now_str = datetime.now().strftime(DATETIME_FORMAT)
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT status FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, user_id),
            )
            row = cursor.fetchone()
            if row is None:
                return False, "Task not found or you do not have permission to modify it."
            
            if row["status"] == "Completed":
                return False, "This task is already marked as completed."

            cursor.execute(
                """
                UPDATE tasks
                SET status = 'Completed',
                    updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (now_str, task_id, user_id),
            )
            return True, "Task marked as completed!"
    except sqlite3.Error as e:
        return False, f"Database error completing task: {e}"
    finally:
        conn.close()


def get_task_statistics(
    user_id: int,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Calculate task metrics: total, pending, completed, overdue, and completion rate."""
    today_str = date.today().isoformat()
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        
        # Total count
        cursor.execute("SELECT COUNT(*) AS total FROM tasks WHERE user_id = ?", (user_id,))
        total = cursor.fetchone()["total"]

        # Pending count
        cursor.execute(
            "SELECT COUNT(*) AS pending FROM tasks WHERE user_id = ? AND status = 'Pending'",
            (user_id,),
        )
        pending = cursor.fetchone()["pending"]

        # Completed count
        cursor.execute(
            "SELECT COUNT(*) AS completed FROM tasks WHERE user_id = ? AND status = 'Completed'",
            (user_id,),
        )
        completed = cursor.fetchone()["completed"]

        # Overdue count (due_date is set and < today and status is Pending)
        cursor.execute(
            """
            SELECT COUNT(*) AS overdue FROM tasks
            WHERE user_id = ? AND status = 'Pending' AND due_date IS NOT NULL AND due_date != '' AND due_date < ?
            """,
            (user_id, today_str),
        )
        overdue = cursor.fetchone()["overdue"]

        # Due today count
        cursor.execute(
            """
            SELECT COUNT(*) AS due_today FROM tasks
            WHERE user_id = ? AND status = 'Pending' AND due_date = ?
            """,
            (user_id, today_str),
        )
        due_today = cursor.fetchone()["due_today"]

        rate = round((completed / total * 100), 1) if total > 0 else 0.0

        return {
            "total": total,
            "pending": pending,
            "completed": completed,
            "overdue": overdue,
            "due_today": due_today,
            "completion_rate": rate,
        }
    finally:
        conn.close()


def search_tasks(
    user_id: int,
    search_term: str,
    db_path: Path | str | None = None,
) -> list[sqlite3.Row]:
    """Convenience function to search tasks by title."""
    return get_tasks(user_id=user_id, search_term=search_term, db_path=db_path)


def filter_tasks(
    user_id: int,
    status: str = "All",
    category_id: int | None = None,
    db_path: Path | str | None = None,
) -> list[sqlite3.Row]:
    """Convenience function to filter tasks by status and/or category."""
    return get_tasks(user_id=user_id, status=status, category_id=category_id, db_path=db_path)
