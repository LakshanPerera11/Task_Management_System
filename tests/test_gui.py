"""Automated GUI integration tests for Tkinter windows and user workflows."""

import gc
from pathlib import Path
import tempfile
import unittest

import auth
import category_manager
from database import initialize_database
import task_manager
from ui import TaskApp


class TestGUIIntegration(unittest.TestCase):
    """Programmatic end-to-end tests for the Tkinter desktop user interface."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.test_db = Path(self.temp_dir.name) / "test_gui.db"
        initialize_database(self.test_db)

        # Set default DB path in database module for UI usage
        import database
        database.set_database_path(self.test_db)

        # Create Tk app without blocking mainloop
        self.app = TaskApp()
        self.app.withdraw()  # Keep hidden during automated test execution
        self.app.update()

    def tearDown(self) -> None:
        try:
            self.app.destroy()
        except Exception:
            pass
        gc.collect()
        self.temp_dir.cleanup()

    def test_app_starts_on_login_screen(self) -> None:
        """App starts on the login screen with no active session."""
        self.assertIsNone(self.app.current_user)
        self.app.update()

    def test_navigation_to_registration_and_back(self) -> None:
        """User can navigate from login to registration screen and back."""
        self.app.show_registration()
        self.app.update()
        self.app.show_login()
        self.app.update()
        self.assertIsNone(self.app.current_user)

    def test_dashboard_loads_after_login(self) -> None:
        """When an authenticated user logs in, the dashboard and metrics are initialized."""
        # Create a test account
        auth.register_user("gui_test_user", "Password123", "Password123", db_path=self.test_db)
        ok, _, session = auth.login_user("gui_test_user", "Password123", db_path=self.test_db)
        self.assertTrue(ok)

        # Set active user and load dashboard
        self.app.current_user = session
        self.app.show_dashboard()
        self.app.update()

        # Verify metric cards exist and initial values are 0
        self.assertEqual(self.app.metric_cards["total"].cget("text"), "0")
        self.assertEqual(self.app.metric_cards["pending"].cget("text"), "0")
        self.assertEqual(self.app.metric_cards["completed"].cget("text"), "0")
        self.assertEqual(self.app.metric_cards["overdue"].cget("text"), "0")

    def test_adding_task_updates_dashboard_and_treeview(self) -> None:
        """Adding a task refreshes metrics and displays the task in the Treeview."""
        auth.register_user("gui_user2", "Password123", "Password123", db_path=self.test_db)
        _, _, session = auth.login_user("gui_user2", "Password123", db_path=self.test_db)
        self.app.current_user = session
        self.app.show_dashboard()

        # Add a task via task_manager
        cats = category_manager.get_categories(session["id"], db_path=self.test_db)
        work_cat_id = [c["id"] for c in cats if c["name"] == "Work"][0]

        task_manager.add_task(
            user_id=session["id"],
            title="Prepare Sprint Backlog",
            category_id=work_cat_id,
            description="Review requirements and prioritize user stories.",
            due_date="2026-11-01",
            db_path=self.test_db,
        )

        self.app.refresh_dashboard()
        self.app.update()

        # Verify metric card updated
        self.assertEqual(self.app.metric_cards["total"].cget("text"), "1")
        self.assertEqual(self.app.metric_cards["pending"].cget("text"), "1")

        # Verify row in Treeview table
        items = self.app.tree.get_children()
        self.assertEqual(len(items), 1)
        row_values = self.app.tree.item(items[0], "values")
        self.assertEqual(row_values[1], "Prepare Sprint Backlog")
        self.assertEqual(row_values[2], "Work")
        self.assertEqual(row_values[3], "2026-11-01")
        self.assertEqual(row_values[4], "⏳ Pending")

    def test_filter_functionality_in_ui(self) -> None:
        """Selecting different filter options filters treeview items correctly."""
        auth.register_user("gui_user3", "Password123", "Password123", db_path=self.test_db)
        _, _, session = auth.login_user("gui_user3", "Password123", db_path=self.test_db)
        self.app.current_user = session
        self.app.show_dashboard()

        cats = category_manager.get_categories(session["id"], db_path=self.test_db)
        work_id = [c["id"] for c in cats if c["name"] == "Work"][0]
        edu_id = [c["id"] for c in cats if c["name"] == "Education"][0]

        _, _, t1 = task_manager.add_task(session["id"], "Task Alpha", work_id, db_path=self.test_db)
        _, _, t2 = task_manager.add_task(session["id"], "Task Beta", edu_id, db_path=self.test_db)
        task_manager.mark_task_completed(session["id"], t1, db_path=self.test_db)

        # Test Status filter = Completed
        self.app.status_filter_var.set("Completed")
        self.app.refresh_dashboard()
        items = self.app.tree.get_children()
        self.assertEqual(len(items), 1)
        self.assertEqual(self.app.tree.item(items[0], "values")[1], "Task Alpha")

        # Test Status filter = Pending
        self.app.status_filter_var.set("Pending")
        self.app.refresh_dashboard()
        items = self.app.tree.get_children()
        self.assertEqual(len(items), 1)
        self.assertEqual(self.app.tree.item(items[0], "values")[1], "Task Beta")

        # Test Search filter = "Alpha"
        self.app.status_filter_var.set("All Statuses")
        self.app.search_var.set("Alpha")
        self.app.refresh_dashboard()
        items = self.app.tree.get_children()
        self.assertEqual(len(items), 1)
        self.assertEqual(self.app.tree.item(items[0], "values")[1], "Task Alpha")


if __name__ == "__main__":
    unittest.main()
