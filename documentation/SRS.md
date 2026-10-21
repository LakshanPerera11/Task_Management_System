# Software Requirements Specification (SRS)

## Task Management System

---

### 1. Title and Project Overview

- **Project Title:** Task Management System (Desktop Personal Organizer)
- **Course Level:** 3rd Year Undergraduate Information Technology Project
- **Target OS:** Windows 10 / Windows 11
- **Technology Stack:** Python 3 (standard library: Tkinter, ttk, sqlite3, hashlib, datetime, pathlib, unittest)
- **Target Release:** Version 1.0.0
- **Summary:** The Task Management System is an offline, multi-user desktop application designed to provide individual users with secure account authentication, custom category categorization, and full lifecycle management (creation, tracking, updating, filtering, searching, and completion) of personal tasks. Persistent storage is achieved using a normalized SQLite relational database enforcing referential integrity.

---

### 2. Introduction

In modern academic and professional settings, individuals manage multiple responsibilities, assignments, and deadlines concurrently. Without an organized tracking tool, tasks are easily misplaced, deadlines missed, and progress obscured. The Task Management System serves as an intuitive, secure, and robust personal management platform designed specifically for desktop deployment.

---

### 3. Problem Statement

Individuals frequently rely on informal tracking methods such as physical notepads, unstructured text files, or complex cloud-based tools that require continuous internet connectivity, paid subscriptions, or heavy system memory. Informal methods lack structured prioritization, due date validation, and analytical tracking, while over-engineered cloud software introduces privacy concerns and unnecessary complexity. There is a need for a lightweight, secure, locally hosted desktop solution with zero external dependencies.

---

### 4. Project Objectives

1. Provide secure authentication with salted password hashing (PBKDF2-HMAC-SHA256).
2. Isolate user accounts, ensuring complete privacy of personal tasks and custom categories.
3. Facilitate complete CRUD (Create, Read, Update, Delete) task operations.
4. Provide structured categorization with default categories (Education, Work, Personal, Other) and custom user-defined categories.
5. Enforce referential integrity and safe category deletion (preventing deletion of in-use categories).
6. Enable multi-criteria task search and filtering by title, category, and status (Pending/Completed).
7. Deliver real-time visual progress metrics on a dynamic dashboard.
8. Validate all user inputs rigorously before committing changes to SQLite.

---

### 5. Project Scope

- **In Scope:**
  - Local desktop GUI interface implemented with standard Tkinter and ttk.
  - Multi-user authentication on a single local SQLite database.
  - User-scoped category and task management.
  - Dynamic dashboard reporting total tasks, pending tasks, completed tasks, overdue tasks, and completion rate.
  - Due date handling with ISO 8601 validation (`YYYY-MM-DD`).
  - Search and filter queries using parameterized SQL.
  - Automated unit test suite with 100% standard library coverage.
- **Out of Scope:**
  - Cloud server synchronization and remote API integration.
  - Multi-tenant simultaneous concurrent network access over LAN/WAN.
  - Email or SMS external notification services.

---

### 6. Intended Users

- **Primary Users:** University students, researchers, independent professionals, and personal computer users who require an organized, local, distraction-free environment to track personal assignments, projects, and goals.

---

### 7. Functional Requirements

- **FR-01: User Registration:** The system shall allow new users to register by providing a unique username, password, and password confirmation.
- **FR-02: Default Categories Provisioning:** Upon successful registration, the system shall automatically create the default categories ("Education", "Work", "Personal", "Other") within the same transaction.
- **FR-03: User Login:** The system shall authenticate users against salted PBKDF2-HMAC-SHA256 hashes without storing or exposing plaintext passwords.
- **FR-04: User Logout & Session Management:** The system shall manage an in-memory session and safely clear it upon logout, returning to the login screen.
- **FR-05: Category Creation:** Authenticated users shall be able to create custom categories with unique names per user (case-insensitive).
- **FR-06: Category Deletion Protection:** The system shall prevent deletion of any category currently assigned to one or more tasks.
- **FR-07: Task Creation:** Users shall be able to create tasks with a title (required), category (required), due date (optional, ISO format), and description (optional).
- **FR-08: Task Retrieval & List View:** Users shall view their tasks in a tabular view with columns: ID, Title, Category, Due Date, Status, and Created Date.
- **FR-09: Task Updating:** Users shall be able to modify the title, description, category, due date, and status of existing tasks owned by them.
- **FR-10: Task Deletion:** Users shall be able to delete an owned task after explicit confirmation dialog approval.
- **FR-11: Mark Completed:** Users shall be able to mark pending tasks as completed with a single action, updating timestamps and metrics.
- **FR-12: Search Functionality:** Users shall be able to search tasks by case-insensitive substring matching against task titles.
- **FR-13: Status & Category Filtering:** Users shall be able to filter tasks by status (All, Pending, Completed) and category simultaneously.
- **FR-14: Dashboard Analytics:** The system shall display live calculated counts of Total Tasks, Pending Tasks, Completed Tasks, Overdue Tasks, and Completion Rate (%).

---

### 8. Non-Functional Requirements

- **NFR-01: Performance:** Queries and screen transitions shall complete in under 100 milliseconds for standard local databases.
- **NFR-02: Security:** Passwords must be hashed using PBKDF2-HMAC-SHA256 with 120,000 iterations and a unique 16-byte random salt. All database statements must use parameterized placeholders (`?`) to prevent SQL injection.
- **NFR-03: Data Integrity:** Foreign key enforcement (`PRAGMA foreign_keys = ON`) must be enabled on every SQLite connection. Tasks are linked to categories and users via composite foreign keys.
- **NFR-04: Usability:** The user interface must employ a neutral, modern visual hierarchy with clear typography, intuitive button placements, and informational error dialogs.
- **NFR-05: Portability:** The software must run on standard Windows systems equipped with Python 3.10+ without installing external pip packages.
- **NFR-06: Reliability:** System errors must be intercepted and reported to the user gracefully without application crashes or data corruption.

---

### 9. Hardware Requirements

- **Processor:** Intel Core i3 or equivalent AMD processor (1.5 GHz or higher).
- **RAM:** Minimum 2 GB (4 GB recommended).
- **Disk Space:** Minimum 50 MB of available storage.
- **Display:** Minimum screen resolution of 1024 x 768 pixels.

---

### 10. Software Requirements

- **Operating System:** Microsoft Windows 10 or Windows 11 (64-bit).
- **Runtime:** Python 3.10, 3.11, 3.12, or 3.13.
- **Standard Libraries:** Tkinter, ttk, sqlite3, hashlib, datetime, pathlib, unittest.
- **Development Environment:** Visual Studio Code.

---

### 11. Use Cases

1. `UC-01`: Register Account
2. `UC-02`: Log In User
3. `UC-03`: Log Out User
4. `UC-04`: View Dashboard & Metrics
5. `UC-05`: Add Task
6. `UC-06`: Edit Task
7. `UC-07`: Mark Task Completed
8. `UC-08`: Delete Task
9. `UC-09`: Search and Filter Tasks
10. `UC-10`: Create Category
11. `UC-11`: Delete Category

---

### 12. Use-Case Descriptions

#### UC-05: Add Task

- **Primary Actor:** Authenticated User
- **Preconditions:** User is logged in and possesses at least one category.
- **Main Flow:**
  1. User clicks the "+ New Task" button on the dashboard.
  2. System displays the "Add New Task" modal dialog.
  3. User enters task title, selects a category, optionally specifies due date and description.
  4. User clicks "Save Task".
  5. System validates field constraints (non-empty title, ISO date check).
  6. System saves task with 'Pending' status, current timestamps, and closes modal.
  7. Dashboard table and statistics refresh immediately.
- **Alternative Flow:**
  - If title is blank or due date is invalid (e.g., February 30), system presents a descriptive warning dialog and preserves entered data for correction.

#### UC-07: Mark Task Completed

- **Primary Actor:** Authenticated User
- **Preconditions:** User has selected a task row from the table.
- **Main Flow:**
  1. User clicks "✔ Mark Completed".
  2. System checks if task status is currently 'Pending'.
  3. System updates status to 'Completed' and sets `updated_at` timestamp.
  4. System refreshes dashboard metrics and updates task row visual indicator.
- **Alternative Flow:**
  - If task is already completed, system alerts the user that no update is required.

---

### 13. System Architecture

The application adopts a clean, layered architectural design:

- **Presentation Layer (`ui.py`):** Tkinter frames, dialogs, widgets, theme definitions, and event handlers.
- **Business Logic Layer (`auth.py`, `task_manager.py`, `category_manager.py`):** User session management, validation coordination, analytics calculation, and authorization enforcement.
- **Validation Layer (`validators.py`):** Reusable, stateless validation rules enforcing field constraints and formats.
- **Configuration Layer (`config.py`):** Centralized constants, limits, paths, and color codes.
- **Data Access Layer (`database.py`):** Connection pooling, foreign key enablement, transactional context managers, and schema DDL.
- **Storage Layer (SQLite `database/task_manager.db`):** Relational tables, composite constraints, and indexes.

---

### 14. Database Design Summary

The database contains three normalized relational tables:

1. `users` (id, username, password_hash, password_salt, created_at)
2. `categories` (id, user_id, name, created_at)
3. `tasks` (id, user_id, category_id, title, description, due_date, status, created_at, updated_at)

_Detailed schema, indexes, and ER diagrams are provided in `DATABASE_DESIGN.md`._

---

### 15. User Interface Design

- **Color Palette:** Charcoal header (`#1E293B`), deep forest green primary accents (`#166534`), soft light slate backgrounds (`#F8FAFC`), white card panels (`#FFFFFF`), amber pending tags (`#D97706`), and emerald completion tags (`#16A34A`).
- **Typography:** Segoe UI (standard Windows system font) with clear size hierarchy (22pt branding, 18pt metrics, 10pt labels, 9pt subtitles).
- **Layouts:** Centered login/registration cards; multi-pane dashboard featuring top metrics cards, filter toolbar, main treeview table, detail preview pane, and bottom action bar.

---

### 16. Validation Rules

- **Username:** 3 to 30 characters; alphanumeric and underscores; must start with a letter or digit.
- **Password:** Minimum 6 characters, maximum 128 characters; cannot be purely whitespace.
- **Category Name:** 1 to 50 characters; unique per user (case-insensitive).
- **Task Title:** 1 to 120 characters; non-empty.
- **Task Description:** Optional; maximum 1,000 characters.
- **Due Date:** Optional; must match ISO 8601 `YYYY-MM-DD` and represent a valid calendar day.
- **Status:** Restricted strictly to `'Pending'` and `'Completed'`.

---

### 17. Security Considerations

1. **Password Protection:** PBKDF2-HMAC-SHA256 with 120,000 iterations and per-user cryptographic random salts (`os.urandom(16)`). Plaintext passwords are never stored or logged.
2. **Timing Attack Mitigation:** Constant-time verification using `hmac.compare_digest`.
3. **SQL Injection Prevention:** 100% parameterized SQL statements with `?` parameter markers.
4. **Ownership Verification:** All business operations explicitly check `WHERE user_id = ?` and foreign keys enforce cross-user isolation.
5. **Session Safety:** Credentials and sessions are held strictly in process memory and purged upon logout.

---

### 18. Constraints and Limitations

- **Local Single-Node Deployment:** The SQLite database is intended for local single-machine desktop use and does not provide multi-user network concurrency across distinct computers.
- **Client-Side Encryption:** SQLite data files on disk are unencrypted at rest; file security relies on standard Windows NTFS user permissions.

---

### 19. Conclusion

The Task Management System delivers a complete, secure, highly maintainable, and professionally structured desktop personal organizer. Adhering strictly to academic and industry best practices, it provides students and professionals with a reliable tool for organizing their daily workflows without external dependencies.
