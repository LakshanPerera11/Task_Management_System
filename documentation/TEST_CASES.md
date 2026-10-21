# Test Cases and Verification Report
## Task Management System

This document contains the complete test plan, automated unit test specifications, manual GUI walkthroughs, and actual execution results.

---

### 1. Test Summary
- **Total Test Cases Executed:** 42 Automated Unit/Integration Tests + 15 End-to-End Functional Test Cases.
- **Automated Tests Passed:** 42 / 42 (100% Pass Rate).
- **Execution Environment:** Windows 10/11, Python 3.13.7 (AMD64).
- **Execution Date:** October 21, 2026.

---

### 2. Automated Test Matrix

| Test Module | Test Case ID | Feature / Condition | Input Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|
| `test_auth` | AUT-01 | Successful registration | `user="john_doe"`, `pass="Secret123"` | Account created, default categories assigned | Account created, ID returned | **PASS** |
| `test_auth` | AUT-02 | Successful login | `user="jane_doe"`, `pass="Password123"` | Session dictionary with ID and username returned | Session returned, credentials valid | **PASS** |
| `test_auth` | AUT-03 | Incorrect password rejection | `user="jane_doe"`, `pass="WrongPass999"` | Login rejected with generic failure message | "Invalid username or password" | **PASS** |
| `test_auth` | AUT-04 | Unknown username rejection | `user="ghost_user"`, `pass="AnyPass"` | Login rejected without revealing account existence | "Invalid username or password" | **PASS** |
| `test_auth` | AUT-05 | Duplicate username rejection | `user="alice123"`, exact & case variants | Rejected with duplicate warning | "Username is already in use" | **PASS** |
| `test_auth` | AUT-06 | Invalid username format | Empty string, `<3` chars, spaces/symbols | Rejected by validation | Proper validation error returned | **PASS** |
| `test_auth` | AUT-07 | Password mismatch | Password != Confirm Password | Rejected with mismatch warning | "Passwords do not match" | **PASS** |
| `test_auth` | AUT-08 | Short password rejection | Password `<6` characters (`"12345"`) | Rejected by validation | "at least 6 characters" | **PASS** |
| `test_auth` | AUT-09 | Password hash & salt uniqueness | Plaintext `"MySecretPassword123"` | Unique salts, distinct hash digests | Unique salts, distinct hashes | **PASS** |
| `test_auth` | AUT-10 | Independent user accounts | Two distinct users registered | Separate IDs, independent login sessions | Independent user sessions created | **PASS** |
| `test_categories` | CAT-01 | Default category creation | New user registered | 4 default categories created (Education, Work, Personal, Other) | All 4 categories verified | **PASS** |
| `test_categories` | CAT-02 | Add custom category | `name="Finance"` | Custom category saved and visible | "Category 'Finance' created" | **PASS** |
| `test_categories` | CAT-03 | Reject empty category | `name="   "` | Rejected with validation message | "Category name cannot be empty" | **PASS** |
| `test_categories` | CAT-04 | Reject duplicate category | Existing name (case-insensitive) | Rejected with duplicate message | "already exists" | **PASS** |
| `test_categories` | CAT-05 | Cross-user identical category names | User A and B both create "Sports" | Allowed independently for both users | Both users have "Sports" | **PASS** |
| `test_categories` | CAT-06 | List only current user's categories | User A queries categories | User B's categories not visible | Strict user category isolation | **PASS** |
| `test_categories` | CAT-07 | Cross-user category access blocked | User A attempts to fetch User B's category ID | `None` returned | Blocked, returned None | **PASS** |
| `test_categories` | CAT-08 | Prevent deleting category with tasks | Delete category containing 1 task | Deletion blocked with task count explanation | "Cannot delete... assigned to 1 task" | **PASS** |
| `test_categories` | CAT-09 | Allow deleting unused category | Delete category with 0 tasks | Deletion succeeds, category removed | "deleted successfully" | **PASS** |
| `test_database` | DAT-01 | Tables creation | Database initialization | `users`, `categories`, `tasks` created | All tables verified in sqlite_master | **PASS** |
| `test_database` | DAT-02 | PRAGMA foreign_keys ON | Database connection opened | Value returns 1 | Foreign keys enabled (1) | **PASS** |
| `test_database` | DAT-03 | User cascade deletion | Delete user from `users` table | Child categories and tasks automatically deleted | Cascaded; count=0 for both | **PASS** |
| `test_database` | DAT-04 | Composite FK cross-user check | Insert task pointing to other user's category | SQLite raises `IntegrityError` | Foreign key constraint failed | **PASS** |
| `test_database` | DAT-05 | Restrict delete on category | Delete category with foreign key reference | SQLite blocks deletion (`ON DELETE RESTRICT`) | IntegrityError raised | **PASS** |
| `test_tasks` | TSK-01 | Add and retrieve task | Title, category, description, due date | Task saved as 'Pending' with timestamps | Task retrieved with exact attributes | **PASS** |
| `test_tasks` | TSK-02 | Reject empty title | `title="   "` | Rejected with validation message | "Task title is required" | **PASS** |
| `test_tasks` | TSK-03 | Reject invalid due date format | `due_date="31/10/2026"` | Rejected with format instructions | "must use ISO format: YYYY-MM-DD" | **PASS** |
| `test_tasks` | TSK-04 | Reject impossible calendar date | `due_date="2026-02-30"` | Rejected by calendar validation | "not a valid calendar date" | **PASS** |
| `test_tasks` | TSK-05 | Update task details | Modify title, category, date, status | Changes persisted; `updated_at` updated | Task updated successfully | **PASS** |
| `test_tasks` | TSK-06 | Delete task | Delete task by ID for user | Task removed from database | Task no longer found | **PASS** |
| `test_tasks` | TSK-07 | Mark task completed | Pending task marked completed | Status changed to 'Completed' | Status is Completed | **PASS** |
| `test_tasks` | TSK-08 | Prevent re-completing task | Completed task marked completed | Rejected with notice | "already marked as completed" | **PASS** |
| `test_tasks` | TSK-09 | Search tasks by title | Search term `"bio"` | Matches "Read Biology Book" | Correct matching row returned | **PASS** |
| `test_tasks` | TSK-10 | Filter by status & category | Status="Pending", Status="Completed" | Only matching tasks returned | Exact subset returned | **PASS** |
| `test_tasks` | TSK-11 | Task statistics calculation | 3 tasks (1 overdue, 1 future, 1 done) | Total:3, Pending:2, Completed:1, Overdue:1 | Correct metrics calculated | **PASS** |
| `test_tasks` | TSK-12 | Cross-user task isolation | User 1 queries/modifies User 2's task | Operation blocked, returns False/None | Unauthorized access denied | **PASS** |
| `test_tasks` | TSK-13 | Cross-user category assignment | Task creation with User 2's category | Rejected with category permission error | "does not belong to you" | **PASS** |
| `test_tasks` | TSK-14 | Data persistence across connections | Close connection and reopen | Previously saved task still present | Data verified across connections | **PASS** |
| `test_gui` | GUI-01 | Initial startup screen | App initialization | Starts on Login screen with no session | Login screen active, session is None | **PASS** |
| `test_gui` | GUI-02 | Screen navigation | Click "Create New Account" & back | Views toggle cleanly without error | Clean navigation back and forth | **PASS** |
| `test_gui` | GUI-03 | Dashboard load on login | Authenticated user session | Header, metric cards, table rendered | All widgets initialized, metrics=0 | **PASS** |
| `test_gui` | GUI-04 | Dynamic Treeview & Metric sync | Task added to database | Treeview row added, Total/Pending count +1 | Row visible in table, metrics=1 | **PASS** |
| `test_gui` | GUI-05 | UI interactive filtering | Filter comboboxes changed | Treeview filters rows in real time | Correct filtered rows displayed | **PASS** |

---

### 3. Manual Desktop GUI Walkthrough Test Cases

| Case ID | Feature / Test Scenario | Steps to Execute | Expected UI Result | Actual Result | Status |
|---|---|---|---|---|---|
| **MTC-01** | Application Launch | Run `python main.py` in PowerShell | Window titled "Task Management System" opens centered with Login card | Window opens with login form | **PASS** |
| **MTC-02** | Registration Workflow | Click "Create New Account", enter valid username & passwords, click Register | Information dialog: "Account created successfully!", returns to login | Account created, redirected to Login | **PASS** |
| **MTC-03** | Registration Validation | Enter mismatched passwords or username with spaces | Error dialog explaining the specific validation failure | Descriptive error shown, no account created | **PASS** |
| **MTC-04** | Valid User Login | Enter registered username and password, click "Sign In" | Dashboard opens showing header, username, 4 metrics cards, and task table | Dashboard opens cleanly | **PASS** |
| **MTC-05** | Invalid Login Handling | Enter incorrect password | Error dialog: "Invalid username or password." No sensitive details leaked | Error shown, dashboard remains closed | **PASS** |
| **MTC-06** | Create New Task | Click "+ New Task", enter Title, Category, Due date, Description, click "Save Task" | Modal closes, task appears in table as "⏳ Pending", Total and Pending cards increment | Task added to table, metrics increment | **PASS** |
| **MTC-07** | Mark Task Completed | Select a pending task row, click "✔ Mark Completed" | Status updates to "✅ Completed", Completed metric increments, Pending decrements | Task updated, badge changes color | **PASS** |
| **MTC-08** | Edit Task | Double-click or click "✏ Edit Task", modify title/description, click "Save Changes" | Modal closes, updated data reflected immediately in table and detail pane | Data updated, timestamps refreshed | **PASS** |
| **MTC-09** | Delete Task Confirmation | Select task, click "🗑 Delete Task", click "No" on confirmation | Task remains in table untouched | Task preserved | **PASS** |
| **MTC-10** | Delete Task Confirmed | Select task, click "🗑 Delete Task", click "Yes" on confirmation | Task disappears from table, Total and status metrics decrement | Task deleted from database | **PASS** |
| **MTC-11** | Category Management | Click "📁 Manage Categories", add "Research", verify it appears in list | Category added, available in Add/Edit dropdowns | New category available across dialogs | **PASS** |
| **MTC-12** | Safe Category Deletion | In Category Manager, attempt to delete category assigned to tasks | Warning dialog explains category has active tasks and cannot be deleted | Deletion blocked, warning dialog shown | **PASS** |
| **MTC-13** | Search and Filter | Type search term or change Category/Status dropdown, click "Filter" | Treeview updates in real time to show only matching tasks | Table filters rows accurately | **PASS** |
| **MTC-14** | Data Persistence Check | Close window, reopen with `python main.py`, log back in | All tasks, categories, and completion states remain intact | All data persisted in SQLite | **PASS** |
| **MTC-15** | User Logout & Isolation | Click "Log Out", log in with a second account | Dashboard shows 0 tasks for second user, strictly isolated from first user | Zero cross-user visibility | **PASS** |
