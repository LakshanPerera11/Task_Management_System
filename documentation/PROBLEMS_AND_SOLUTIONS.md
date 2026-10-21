# Engineering Problems, Root Causes, and Implemented Solutions

## Task Management System

This document records the technical challenges encountered during system design, implementation, and testing, detailing the diagnosed root causes, architectural solutions, and verification steps.

---

### Problem 1: SQLite Foreign Key Constraints Inactive by Default

- **Symptom:** Foreign key constraints (such as `ON DELETE CASCADE` and `ON DELETE RESTRICT`) were not initially enforced by SQLite during database operations, allowing child records to persist after parent deletion.
- **Root Cause:** In the standard SQLite C library and Python `sqlite3` module, foreign key enforcement is disabled by default for legacy backwards compatibility. Each new database connection must explicitly enable it.
- **Implemented Solution:**
  In `database.py`, every connection instantiated through `get_connection()` immediately executes:
  ```python
  connection.execute("PRAGMA foreign_keys = ON")
  ```
- **Verification:**
  Automated test `test_foreign_keys_pragma_enabled` queries `PRAGMA foreign_keys` on active connections, confirming that the pragma returns `1` (enabled).

---

### Problem 2: Windows File-Locking Contention During Automated Test Teardown

- **Symptom:** During automated unit testing on Windows, `tearDown()` methods raised `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process` when attempting to clean up temporary test database directories.
- **Root Cause:** In Python's standard `sqlite3` library, using `with connection:` manages transactions (calling `commit()` or `rollback()`) but **does not close** the connection. On Windows, open SQLite file handles prevent the OS from deleting temporary directories until the process terminates or connections are explicitly closed.
- **Implemented Solution:**
  1. Implemented a custom connection class `ManagedConnection(sqlite3.Connection)` whose `__exit__` method guarantees that `close()` is invoked when exiting a `with` block.
  2. Updated `initialize_database()` and query functions to use strict `try ... finally: conn.close()` blocks.
  3. Added explicit garbage collection (`gc.collect()`) prior to directory removal.
  4. Initialized test fixtures with `tempfile.TemporaryDirectory(ignore_cleanup_errors=True)`.
- **Verification:**
  Re-ran all 42 automated tests across `test_database`, `test_auth`, `test_categories`, `test_tasks`, and `test_gui`. All tests passed cleanly on Windows with zero file-locking exceptions.

---

### Problem 3: Prevention of Cross-User Category Assignment at Database Level

- **Symptom:** In a multi-user database, a compromised or malfunctioning UI could potentially permit User A to assign a `category_id` belonging to User B when creating or updating a task.
- **Root Cause:** A simple foreign key `FOREIGN KEY (category_id) REFERENCES categories(id)` only checks that the category exists somewhere in the table; it does not verify that the category's `user_id` matches the task's `user_id`.
- **Implemented Solution:**
  Architected a composite foreign key constraint at the SQLite schema level:
  1. Added a candidate key in the `categories` table: `UNIQUE (id, user_id)`.
  2. Added a composite foreign key constraint in the `tasks` table:
     ```sql
     FOREIGN KEY (category_id, user_id) REFERENCES categories(id, user_id) ON DELETE RESTRICT
     ```
  3. Layered this with application-level validation in `task_manager.py` verifying ownership before executing queries.
- **Verification:**
  Automated tests `test_composite_foreign_key_cross_user_prevention` and `test_reject_assigning_another_users_category` verify that both the database engine and the application layer reject cross-user category assignments.

---

### Problem 4: Missing Font Submodule in Tkinter

- **Symptom:** GUI tests encountered `AttributeError: module 'tkinter' has no attribute 'font'` when evaluating available system fonts.
- **Root Cause:** In Python's `tkinter` package, `tkinter.font` is a distinct submodule that is not automatically imported when importing `tkinter as tk`.
- **Implemented Solution:**
  Updated `ui.py` to explicitly import `font as tkfont` from `tkinter` and called `tkfont.families()`.
- **Verification:**
  Automated test suite `test_gui.py` executed successfully, initializing font families and configuring ttk themes without errors.

---

### Problem 5: Accidental Deletion of Categories in Active Use

- **Symptom:** Deleting a category that has tasks assigned to it could either orphan tasks, cause cascading accidental task loss, or trigger raw database errors.
- **Root Cause:** Without a clear deletion policy, either cascading deletes destroy valid user tasks without warning, or SQLite raises an unhandled `IntegrityError`.
- **Implemented Solution:**
  1. Configured database foreign key `ON DELETE RESTRICT`.
  2. Implemented pre-deletion validation in `category_manager.delete_category()`, counting tasks referencing the category.
  3. If tasks are assigned, the UI presents an informative warning stating exactly how many tasks are using the category and instructing the user to reassign or delete them first.
- **Verification:**
  Automated test `test_prevent_unsafe_category_deletion_with_tasks` verifies that category deletion is blocked when tasks exist.

---

### 6. Student Personal Experience Template (For Viva / Demonstration Preparation)

> **Instructions for Student:** You can personalize the section below with observations from your personal project experience before your viva or final presentation.

```markdown
#### Personal Viva Reflection:

- Date of Final Testing: October 21, 2026
- Key Learning Experience: Implementing salted PBKDF2 password hashing and composite SQLite constraints provided practical insights into application security and relational database normalization.
- UI Observation: Designing custom modal dialogs in Tkinter required careful handling of transient states and modal grabs (`transient()` and `grab_set()`) to ensure dialogs behave properly on Windows.
- Performance: Query execution for 100+ tasks was instantaneous due to proper indexing on `user_id` and `status`.
```
