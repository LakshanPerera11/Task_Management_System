"""Unit tests for database initialization, schema integrity, and SQLite constraints."""

import gc
from pathlib import Path
import sqlite3
import tempfile
import unittest

from database import get_connection, initialize_database


class TestDatabase(unittest.TestCase):
    """Test SQLite schema constraints, foreign key pragmas, and composite rules."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = Path(self.temp_dir.name) / "test_db.db"
        initialize_database(self.db_path)

    def tearDown(self) -> None:
        gc.collect()
        self.temp_dir.cleanup()

    def test_tables_created(self) -> None:
        """Verify that users, categories, and tasks tables exist."""
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row["name"] for row in cursor.fetchall()}
            self.assertIn("users", tables)
            self.assertIn("categories", tables)
            self.assertIn("tasks", tables)

    def test_foreign_keys_pragma_enabled(self) -> None:
        """Verify PRAGMA foreign_keys is set to ON on connections."""
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys")
            val = cursor.fetchone()[0]
            self.assertEqual(val, 1)

    def test_user_deletion_cascades_categories_and_tasks(self) -> None:
        """Deleting a user cascades and removes their categories and tasks."""
        with get_connection(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash, password_salt, created_at) VALUES (?, ?, ?, ?)",
                ("alice", "hash1", "salt1", "2026-10-20 10:00:00"),
            )
            user_id = cur.lastrowid
            cur.execute(
                "INSERT INTO categories (user_id, name, created_at) VALUES (?, ?, ?)",
                (user_id, "Work", "2026-10-20 10:00:00"),
            )
            cat_id = cur.lastrowid
            cur.execute(
                """
                INSERT INTO tasks (user_id, category_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, cat_id, "Test Task", "2026-10-20 10:00:00", "2026-10-20 10:00:00"),
            )

            # Now delete the user
            cur.execute("DELETE FROM users WHERE id = ?", (user_id,))

            # Verify categories and tasks are gone
            cur.execute("SELECT COUNT(*) FROM categories WHERE user_id = ?", (user_id,))
            self.assertEqual(cur.fetchone()[0], 0)
            cur.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,))
            self.assertEqual(cur.fetchone()[0], 0)

    def test_composite_foreign_key_cross_user_prevention(self) -> None:
        """A user cannot create a task referencing another user's category at the DB level."""
        with get_connection(self.db_path) as conn:
            cur = conn.cursor()
            # User 1
            cur.execute("INSERT INTO users (username, password_hash, password_salt, created_at) VALUES ('u1', 'h1', 's1', 'now')")
            u1 = cur.lastrowid
            cur.execute("INSERT INTO categories (user_id, name, created_at) VALUES (?, 'Cat1', 'now')", (u1,))
            cat_u1 = cur.lastrowid

            # User 2
            cur.execute("INSERT INTO users (username, password_hash, password_salt, created_at) VALUES ('u2', 'h2', 's2', 'now')")
            u2 = cur.lastrowid

            # User 2 tries to insert task pointing to User 1's category
            with self.assertRaises(sqlite3.IntegrityError):
                cur.execute(
                    """
                    INSERT INTO tasks (user_id, category_id, title, created_at, updated_at)
                    VALUES (?, ?, 'Illegal Task', 'now', 'now')
                    """,
                    (u2, cat_u1),
                )

    def test_category_restrict_delete_with_tasks(self) -> None:
        """Categories cannot be deleted directly while tasks reference them (RESTRICT)."""
        with get_connection(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password_hash, password_salt, created_at) VALUES ('u1', 'h1', 's1', 'now')")
            u1 = cur.lastrowid
            cur.execute("INSERT INTO categories (user_id, name, created_at) VALUES (?, 'Study', 'now')", (u1,))
            cat_id = cur.lastrowid
            cur.execute(
                "INSERT INTO tasks (user_id, category_id, title, created_at, updated_at) VALUES (?, ?, 'Read', 'now', 'now')",
                (u1, cat_id),
            )

            # Attempt to delete the category directly in SQL
            with self.assertRaises(sqlite3.IntegrityError):
                cur.execute("DELETE FROM categories WHERE id = ?", (cat_id,))


if __name__ == "__main__":
    unittest.main()
