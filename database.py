"""Database connection management, schema initialization, and transactional helpers."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Generator

from config import DEFAULT_DB_PATH

# Module-level default path, can be overridden for testing
_current_db_path: Path = DEFAULT_DB_PATH


class ManagedConnection(sqlite3.Connection):
    """Connection that automatically manages transactions and closes upon exiting a with block."""

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def set_database_path(path: Path | str) -> None:
    """Set the database path to be used across the application or test suite."""
    global _current_db_path
    _current_db_path = Path(path)


def get_database_path() -> Path:
    """Return the currently configured database path."""
    return _current_db_path


def get_connection(db_path: Path | str | None = None) -> ManagedConnection:
    """Create and return a new SQLite database connection with row factory and foreign keys enabled."""
    target_path = Path(db_path) if db_path is not None else _current_db_path

    # Ensure parent directory exists for file-based databases
    if str(target_path) != ":memory:":
        target_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(target_path), factory=ManagedConnection)
    connection.row_factory = sqlite3.Row
    # Foreign key enforcement is disabled by default in SQLite; must enable per connection
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def get_db_cursor(db_path: Path | str | None = None) -> Generator[sqlite3.Cursor, None, None]:
    """Context manager providing an active cursor with automatic commit/rollback and connection cleanup."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database(db_path: Path | str | None = None) -> None:
    """Safely initialize the database schema, creating tables and indexes if they do not exist.

    Never drops or resets existing user data.
    """
    target_path = Path(db_path) if db_path is not None else _current_db_path
    if str(target_path) != ":memory:":
        target_path.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection(target_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")

        # 1. Users Table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )

        # 2. Categories Table
        # Note: UNIQUE(id, user_id) allows composite foreign key reference from tasks
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL COLLATE NOCASE,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, name COLLATE NOCASE),
                UNIQUE (id, user_id)
            );
            """
        )

        # 3. Tasks Table
        # Composite foreign key ensures task's category_id and user_id must belong together
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                due_date TEXT,
                status TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Completed')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id, user_id) REFERENCES categories(id, user_id) ON DELETE RESTRICT
            );
            """
        )

        # Indexes for fast lookup and filtering
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks(user_id, status);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user_category ON tasks(user_id, category_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(user_id, due_date);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_categories_user ON categories(user_id);")

        conn.commit()
    finally:
        conn.close()
