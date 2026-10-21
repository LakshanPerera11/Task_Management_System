# User Guide
## Task Management System

Welcome to the **Task Management System**, a secure and easy-to-use desktop personal organizer built with Python, Tkinter, and SQLite. This guide provides step-by-step instructions for installation, operation, and database maintenance on Windows.

---

### 1. Prerequisites and Python Verification

The application is built using the standard Python library and requires **no external package installations** via `pip`.

1. Open PowerShell on Windows by pressing `Win + X` and selecting **Terminal** or **Windows PowerShell**.
2. Check your Python installation by running:
   ```powershell
   python --version
   ```
   *(Or using the Python launcher: `py --version`)*
3. Ensure the version displayed is **Python 3.10** or newer (e.g., Python 3.11, 3.12, 3.13).
4. If Python is not installed:
   - Download the installer from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - **Important:** During installation, check the box labeled **"Add python.exe to PATH"** before clicking Install Now.

---

### 2. Opening the Project in Visual Studio Code

1. Launch **Visual Studio Code**.
2. Select **File > Open Folder...** from the top menu.
3. Browse to and select the project directory:
   `TaskManagementSystem`
4. Open the integrated terminal in VS Code:
   - Shortcut: `Ctrl + \`` (backtick) or select **Terminal > New Terminal**.

---

### 3. Launching the Application

In the terminal inside the `TaskManagementSystem` folder, execute:

```powershell
python main.py
```

*(Alternative command using the Windows launcher:)*
```powershell
py main.py
```

The database directory and SQLite database file (`database/task_manager.db`) are created automatically if they do not already exist.

---

### 4. Step-by-Step User Instructions

#### 4.1. Creating an Account (Registration)
1. On the initial startup screen, click the **"Create New Account"** button.
2. Enter your desired **Username**:
   - Must be between 3 and 30 characters long.
   - May contain letters, numbers, and underscores (must start with a letter or number).
3. Enter a secure **Password**:
   - Must be at least 6 characters long.
4. Retype the exact password in the **Confirm Password** field.
5. Click **"Register Account"**.
6. A success dialog will confirm that your account was created with four default categories (**Education**, **Work**, **Personal**, and **Other**). You will be returned to the Sign In screen.

#### 4.2. Logging In
1. On the Sign In screen, enter your registered **Username** and **Password**.
2. Click **"Sign In"** (or press `Enter` on the keyboard).
3. Upon successful verification, your private dashboard opens.

#### 4.3. Understanding the Dashboard
- **Top Header:** Displays the application title and your current username (`Logged in as: <username>`).
- **Summary Metrics Cards:**
  - **Total Tasks:** Cumulative number of tasks created.
  - **Pending Tasks:** Active tasks awaiting completion.
  - **Completed Tasks:** Finished tasks.
  - **Overdue Tasks:** Pending tasks whose due date has passed.
- **Task Table:** Displays task ID, title, category, due date, status, and creation date.
- **Description Pane:** Select any row in the table to read its full description and update timestamp.

#### 4.4. Adding a New Task
1. Click the **"+ New Task"** button on the toolbar.
2. In the modal dialog:
   - **Task Title (Required):** Enter a clear, concise name (e.g., "Complete Algorithms Assignment").
   - **Category (Required):** Select one of your available categories from the dropdown.
   - **Due Date (Optional):** Enter the date in `YYYY-MM-DD` format, or use the quick buttons (**Today**, **Tomorrow**, **+1 Week**) to automatically fill the field.
   - **Description (Optional):** Enter additional notes, reference links, or instructions.
3. Click **"Save Task"**. The new task will immediately appear in the table with `'Pending'` status.

#### 4.5. Marking a Task as Completed
1. In the task list, click once on the task you wish to complete.
2. Click the **"✔ Mark Completed"** button on the bottom toolbar.
3. The status changes to `'Completed'`, the visual badge updates, and the dashboard metrics refresh.

#### 4.6. Editing an Existing Task
1. Select the task in the table and click **"✏ Edit Task"** (or double-click the row).
2. The Edit Task dialog will open, pre-populated with current values.
3. Modify the title, category, due date, status, or description as needed.
4. Click **"Save Changes"**.

#### 4.7. Deleting a Task
1. Select the task you wish to remove.
2. Click the **"🗑 Delete Task"** button.
3. A confirmation dialog will appear: *"Are you sure you want to permanently delete task #...? This action cannot be undone."*
4. Click **"Yes"** to confirm deletion. The task is removed from the database.

#### 4.8. Searching and Filtering Tasks
- **Search by Title:** Type any part of a task title in the Search box and click **"Filter"** (or press `Enter`).
- **Filter by Category:** Select a specific category from the Category dropdown to view only tasks in that category.
- **Filter by Status:** Select **"All Statuses"**, **"Pending"**, or **"Completed"** to focus on active or finished work.
- **Clear Filters:** Click **"Clear"** at any time to reset all filters and display all tasks.

#### 4.9. Managing Categories
1. Click the **"📁 Manage Categories"** button on the toolbar.
2. In the category management window:
   - **Add a Category:** Type the new category name into the input field and click **"Add Category"**.
   - **View Assigned Counts:** The table shows how many tasks are currently assigned to each category.
   - **Safe Deletion:** To delete a category, select it and click **"🗑 Delete Selected"**. If the category has tasks assigned to it, the system will block deletion and explain that tasks must be reassigned or deleted first.

#### 4.10. Logging Out
1. Click the **"Log Out"** button located in the top-right corner of the header.
2. Confirm the prompt. Your session is cleared from memory and you are returned safely to the Sign In screen.

---

### 5. Data Storage and Safe Backup Procedures

#### 5.1. Where Data is Stored
All data (user accounts, salted password hashes, categories, and tasks) is stored in a single, self-contained SQLite database file:
```
TaskManagementSystem/
    database/
        task_manager.db
```

#### 5.2. How to Back Up Your Data
Because SQLite stores all relational data in a single file, backup is simple:
1. Close the Task Management System application.
2. Copy the `database/task_manager.db` file to a secure backup location (e.g., a backup folder, external USB drive, or cloud storage drive).
3. To restore data, simply copy your backup file back to `database/task_manager.db`.
