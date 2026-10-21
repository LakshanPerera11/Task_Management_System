# Application Screenshots Guide
## Task Management System

This directory holds screenshots of the running desktop application for inclusion in project submission reports, presentations, and viva documentation.

---

### Recommended Screenshots to Capture

| Number | Suggested Filename | Screen Description | How to Capture |
|---|---|---|---|
| **01** | `01_login_screen.png` | Centered Login screen with application title, subtitle, and input fields. | Launch `python main.py`. |
| **02** | `02_registration_screen.png` | Registration screen with username, password, and confirm password fields. | Click "Create New Account" on the login screen. |
| **03** | `03_main_dashboard.png` | Main Dashboard showing username, 4 metrics cards, search/filter toolbar, and populated task table. | Sign in using `demo_student` / `DemoPassword123`. |
| **04** | `04_add_task_dialog.png` | Modal dialog for adding a new task with title, category dropdown, date shortcuts, and description. | Click "+ New Task" on the toolbar. |
| **05** | `05_edit_task_dialog.png` | Modal dialog for editing an existing task with pre-populated fields and status dropdown. | Select a task and click "✏ Edit Task". |
| **06** | `06_manage_categories.png` | Category management modal listing categories, task counts, and safe delete protection. | Click "📁 Manage Categories" on the toolbar. |
| **07** | `07_filtered_completed_tasks.png` | Dashboard with Status dropdown filtered to "Completed". | Set Status filter to "Completed" and click "Filter". |
| **08** | `08_search_results.png` | Dashboard showing filtered tasks matching a search keyword. | Type a search keyword (e.g. "SRS") and press Enter. |

---

### Quick Screenshot Capture on Windows

1. Run the application:
   ```powershell
   python main.py
   ```
2. To capture any active window:
   - Press **`Alt + PrtScn`** (captures only the currently active window to clipboard).
   - Or press **`Win + Shift + S`** to open the Windows Snipping Tool and select the window.
3. Paste the image into Microsoft Paint or open Snipping Tool and save the file into this `screenshots/` directory (e.g. `screenshots/01_login_screen.png`).
4. Alternatively, run:
   ```powershell
   python seed_demo_data.py
   ```
   to automatically populate sample tasks and categories for clean presentation screenshots.
