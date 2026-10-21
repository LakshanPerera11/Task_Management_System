# Task Management System

A complete, robust, offline desktop personal productivity application built for Windows using Python 3, Tkinter/ttk, and SQLite.

Developed as an individual undergraduate IT software engineering project demonstrating relational database design, secure salted authentication, layered architecture, and responsive GUI development without external dependencies.

---

## Features

- **Secure Authentication:** User registration, password verification, and session management using PBKDF2-HMAC-SHA256 with 120,000 iterations and unique 16-byte cryptographic salts.
- **Strict User Isolation:** Multi-user support on a shared local database with strict user ownership enforcement across all queries and composite database constraints.
- **Full Task Lifecycle (CRUD):** Add, view, edit, and delete personal tasks with optional descriptions and ISO 8601 due dates (`YYYY-MM-DD`).
- **One-Click Task Completion:** Instantly mark pending tasks as completed with real-time status and metric synchronization.
- **Categorization & Safe Deletion:** Automatic provisioning of 4 default categories (`Education`, `Work`, `Personal`, `Other`), creation of custom categories, and foreign-key protected category deletion.
- **Search & Multi-Filter Toolbar:** Case-insensitive search by task title, category filtering, and status filtering (`All`, `Pending`, `Completed`).
- **Dashboard Metrics:** Real-time summary cards displaying Total Tasks, Pending Tasks, Completed Tasks, Overdue Tasks, and completion percentage.
- **Persistent Local Database:** Automatic runtime initialization of SQLite database schema, indexes, and foreign keys.

---

## Technology Stack

- **Operating System:** Windows 10 / Windows 11
- **Programming Language:** Python 3 (Python 3.10, 3.11, 3.12, or 3.13)
- **GUI Framework:** `tkinter` and `tkinter.ttk` (standard library)
- **Relational Database:** `sqlite3` (standard library with `PRAGMA foreign_keys = ON`)
- **Security & Cryptography:** `hashlib.pbkdf2_hmac` and `hmac.compare_digest`
- **Testing Framework:** `unittest` (standard library)
- **Dependencies:** **None** (100% Python Standard Library)

---

## Project Structure

```
TaskManagementSystem/
│
├── main.py                     # Application entry point
├── database.py                 # SQLite connection lifecycle & schema DDL
├── auth.py                     # Authentication & salted password hashing
├── task_manager.py             # Task CRUD, completion, and statistics
├── category_manager.py         # Category CRUD & safe deletion logic
├── validators.py               # Reusable input validation rules
├── config.py                   # Global constants, paths, and UI palette
├── ui.py                       # Tkinter presentation layer & dashboard
│
├── requirements.txt            # Environment & standard library documentation
├── README.md                   # Project overview & instructions
├── .gitignore                  # Git exclusions for caches and runtime databases
│
├── database/
│   ├── .gitkeep
│   └── task_manager.db         # Runtime-generated SQLite database
│
├── tests/
│   ├── __init__.py
│   ├── test_database.py        # Database schema & composite constraint tests
│   ├── test_auth.py            # User registration & authentication tests
│   ├── test_categories.py      # Category rules & safe deletion tests
│   ├── test_tasks.py           # Task CRUD, date validation & isolation tests
│   └── test_gui.py             # Tkinter programmatic GUI integration tests
│
├── screenshots/
│   ├── .gitkeep
│   └── README.md               # Screenshot capture guide & UI descriptions
│
└── documentation/
    ├── SRS.md                  # Comprehensive 19-section Software Requirements Specification
    ├── DATABASE_DESIGN.md      # Detailed ER diagrams, table schemas & DDL
    ├── TEST_CASES.md           # Automated test matrix & manual walkthrough results
    ├── USER_GUIDE.md           # Step-by-step user manual & database backup guide
    ├── PROBLEMS_AND_SOLUTIONS.md # Diagnosed issues, root causes & engineering fixes
    └── PRESENTATION_OUTLINE.md # Viva slides, talking points & 5-minute demo script
```

---

## Installation and Setup

### 1. Check Python Installation
Open PowerShell and verify that Python 3.10+ is installed:

```powershell
python --version
```

If not installed, download Python from [python.org](https://www.python.org/downloads/) and ensure **"Add python.exe to PATH"** is selected during installation.

### 2. Verify Zero External Dependencies
This project uses only the Python standard library. No packages need to be installed via `pip`:

```powershell
pip list
```

---

## Running the Application

Navigate to the project root directory in PowerShell or VS Code terminal:

```powershell
python main.py
```

*(Or using the Windows Python launcher:)*
```powershell
py main.py
```

On first launch, the `database/` directory and `task_manager.db` SQLite file are created automatically.

---

## Running the Automated Test Suite

Run all 42 automated tests covering authentication, database schema, categories, tasks, and GUI workflows:

```powershell
python -m unittest discover -s tests -v
```

Expected output:
```
Ran 42 tests in ~7s
OK
```

To run individual test modules:
```powershell
python -m unittest tests.test_auth -v
python -m unittest tests.test_categories -v
python -m unittest tests.test_tasks -v
python -m unittest tests.test_database -v
python -m unittest tests.test_gui -v
```

---

## Database Location & Persistence

- **Database File:** `database/task_manager.db`
- **Schema Management:** Initialized automatically by `database.initialize_database()`.
- **Integrity Guarantee:** Never resets or drops existing user data upon application restarts.
- **Backup:** Copy `database/task_manager.db` to a backup directory while the app is closed.

---

## Security Architecture

1. **Salted PBKDF2 Hashing:** Passwords are never stored in plaintext. Passwords are hashed with `hashlib.pbkdf2_hmac("sha256", password, salt, 120_000)` where `salt` is 16 random bytes from `os.urandom(16)`.
2. **Timing-Attack Resistance:** Password hashes are evaluated using `hmac.compare_digest`.
3. **SQL Injection Defense:** All queries use parameterized SQL markers (`?`), never string concatenation.
4. **Relational Isolation:** Composite foreign key `FOREIGN KEY (category_id, user_id) REFERENCES categories(id, user_id)` guarantees at the database level that tasks cannot reference another user's category.
5. **Session Safety:** Credentials and active session dictionaries exist solely in memory during the execution lifecycle.

---

## Troubleshooting

- **Tkinter Missing:** On standard Windows Python installations, Tkinter is included by default. If missing, re-run the official Python installer and ensure the "tcl/tk and IDLE" feature is checked.
- **Portability Notice:** Database paths use `pathlib.Path` relative to the project directory, so the application functions regardless of where the project folder is stored on Windows.

---

## Documentation Links

- [Software Requirements Specification](documentation/SRS.md)
- [Database Design Specification](documentation/DATABASE_DESIGN.md)
- [Test Cases & Execution Report](documentation/TEST_CASES.md)
- [User Guide & Backup Manual](documentation/USER_GUIDE.md)
- [Problems, Causes, and Solutions](documentation/PROBLEMS_AND_SOLUTIONS.md)
- [Viva & Presentation Demonstration Outline](documentation/PRESENTATION_OUTLINE.md)
