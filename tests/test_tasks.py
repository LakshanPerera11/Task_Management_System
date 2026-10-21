import gc
from datetime import date, timedelta
from pathlib import Path
import tempfile
import unittest

import auth
import category_manager
from database import initialize_database
import task_manager


class TestTasks(unittest.TestCase):
    """Test task operations, security isolation, validation, and analytics."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = Path(self.temp_dir.name) / "test_tasks.db"
        initialize_database(self.db_path)

        # Register User 1
        _, _, self.user1_id = auth.register_user("task_user_one", "Password123", "Password123", db_path=self.db_path)
        cats1 = category_manager.get_categories(self.user1_id, db_path=self.db_path)
        self.u1_cat_work = [c for c in cats1 if c["name"] == "Work"][0]["id"]
        self.u1_cat_edu = [c for c in cats1 if c["name"] == "Education"][0]["id"]

        # Register User 2
        _, _, self.user2_id = auth.register_user("task_user_two", "Password123", "Password123", db_path=self.db_path)
        cats2 = category_manager.get_categories(self.user2_id, db_path=self.db_path)
        self.u2_cat_work = [c for c in cats2 if c["name"] == "Work"][0]["id"]

    def tearDown(self) -> None:
        gc.collect()
        self.temp_dir.cleanup()

    def test_add_and_retrieve_task(self) -> None:
        """A user can add a task with title, description, category, and due date."""
        ok, msg, task_id = task_manager.add_task(
            user_id=self.user1_id,
            title="Complete Coursework",
            category_id=self.u1_cat_edu,
            description="Write 2000 words on software design.",
            due_date="2026-10-31",
            db_path=self.db_path,
        )
        self.assertTrue(ok)
        self.assertIsNotNone(task_id)

        task = task_manager.get_task_by_id(self.user1_id, task_id, db_path=self.db_path)
        self.assertIsNotNone(task)
        self.assertEqual(task["title"], "Complete Coursework")
        self.assertEqual(task["description"], "Write 2000 words on software design.")
        self.assertEqual(task["due_date"], "2026-10-31")
        self.assertEqual(task["status"], "Pending")
        self.assertEqual(task["category_name"], "Education")

    def test_reject_empty_task_title(self) -> None:
        """Tasks with empty titles are rejected."""
        ok, msg, _ = task_manager.add_task(
            user_id=self.user1_id,
            title="   ",
            category_id=self.u1_cat_work,
            db_path=self.db_path,
        )
        self.assertFalse(ok)
        self.assertIn("title is required", msg.lower())

    def test_reject_invalid_due_date_format(self) -> None:
        """Non-ISO dates or bad formats are rejected."""
        ok, msg, _ = task_manager.add_task(
            user_id=self.user1_id,
            title="Task with bad date",
            category_id=self.u1_cat_work,
            due_date="31/10/2026",
            db_path=self.db_path,
        )
        self.assertFalse(ok)
        self.assertIn("ISO format", msg)

    def test_reject_impossible_calendar_date(self) -> None:
        """Dates that do not exist on the calendar (like 2026-02-30) are rejected."""
        ok, msg, _ = task_manager.add_task(
            user_id=self.user1_id,
            title="Impossible date task",
            category_id=self.u1_cat_work,
            due_date="2026-02-30",
            db_path=self.db_path,
        )
        self.assertFalse(ok)
        self.assertIn("not a valid calendar date", msg)

    def test_update_task(self) -> None:
        """User can update an existing task title, description, category, due date, and status."""
        _, _, task_id = task_manager.add_task(
            user_id=self.user1_id,
            title="Original Title",
            category_id=self.u1_cat_work,
            description="Original desc",
            db_path=self.db_path,
        )

        ok, msg = task_manager.update_task(
            user_id=self.user1_id,
            task_id=task_id,
            title="Updated Title",
            category_id=self.u1_cat_edu,
            description="Updated desc",
            due_date="2026-11-15",
            status="Completed",
            db_path=self.db_path,
        )
        self.assertTrue(ok)

        task = task_manager.get_task_by_id(self.user1_id, task_id, db_path=self.db_path)
        self.assertEqual(task["title"], "Updated Title")
        self.assertEqual(task["description"], "Updated desc")
        self.assertEqual(task["category_id"], self.u1_cat_edu)
        self.assertEqual(task["due_date"], "2026-11-15")
        self.assertEqual(task["status"], "Completed")

    def test_delete_task(self) -> None:
        """User can delete an owned task."""
        _, _, task_id = task_manager.add_task(
            user_id=self.user1_id,
            title="To be deleted",
            category_id=self.u1_cat_work,
            db_path=self.db_path,
        )

        ok, msg = task_manager.delete_task(self.user1_id, task_id, db_path=self.db_path)
        self.assertTrue(ok)

        # Ensure task no longer exists
        task = task_manager.get_task_by_id(self.user1_id, task_id, db_path=self.db_path)
        self.assertIsNone(task)

    def test_mark_task_completed(self) -> None:
        """Marking a pending task as completed sets status to Completed."""
        _, _, task_id = task_manager.add_task(
            user_id=self.user1_id,
            title="Pending Task",
            category_id=self.u1_cat_work,
            db_path=self.db_path,
        )

        ok, msg = task_manager.mark_task_completed(self.user1_id, task_id, db_path=self.db_path)
        self.assertTrue(ok)

        task = task_manager.get_task_by_id(self.user1_id, task_id, db_path=self.db_path)
        self.assertEqual(task["status"], "Completed")

        # Second attempt should notify that it is already completed
        ok2, msg2 = task_manager.mark_task_completed(self.user1_id, task_id, db_path=self.db_path)
        self.assertFalse(ok2)
        self.assertIn("already", msg2)

    def test_search_tasks_by_title(self) -> None:
        """Search matches tasks with case-insensitive substring in title."""
        task_manager.add_task(self.user1_id, "Buy Groceries", self.u1_cat_work, db_path=self.db_path)
        task_manager.add_task(self.user1_id, "Read Biology Book", self.u1_cat_edu, db_path=self.db_path)
        task_manager.add_task(self.user1_id, "Call Doctor", self.u1_cat_work, db_path=self.db_path)

        results = task_manager.search_tasks(self.user1_id, "bio", db_path=self.db_path)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Read Biology Book")

    def test_filter_tasks_by_status_and_category(self) -> None:
        """Filter tasks by status and category combinations."""
        _, _, t1 = task_manager.add_task(self.user1_id, "Task 1", self.u1_cat_work, db_path=self.db_path)
        _, _, t2 = task_manager.add_task(self.user1_id, "Task 2", self.u1_cat_edu, db_path=self.db_path)
        task_manager.mark_task_completed(self.user1_id, t1, db_path=self.db_path)

        # Filter by Pending
        pending = task_manager.get_tasks(self.user1_id, status="Pending", db_path=self.db_path)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["id"], t2)

        # Filter by Completed
        completed = task_manager.get_tasks(self.user1_id, status="Completed", db_path=self.db_path)
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0]["id"], t1)

        # Filter by Category
        work_tasks = task_manager.get_tasks(self.user1_id, category_id=self.u1_cat_work, db_path=self.db_path)
        self.assertEqual(len(work_tasks), 1)
        self.assertEqual(work_tasks[0]["id"], t1)

    def test_task_statistics_calculation(self) -> None:
        """Task statistics accurately reflect total, pending, completed, overdue, and rate."""
        yesterday_str = (date.today() - timedelta(days=1)).isoformat()
        tomorrow_str = (date.today() + timedelta(days=1)).isoformat()

        # 1 Overdue task (Pending, due yesterday)
        task_manager.add_task(self.user1_id, "Overdue Task", self.u1_cat_work, due_date=yesterday_str, db_path=self.db_path)
        # 1 Pending task (due tomorrow)
        task_manager.add_task(self.user1_id, "Future Task", self.u1_cat_edu, due_date=tomorrow_str, db_path=self.db_path)
        # 1 Completed task
        _, _, t3 = task_manager.add_task(self.user1_id, "Done Task", self.u1_cat_work, db_path=self.db_path)
        task_manager.mark_task_completed(self.user1_id, t3, db_path=self.db_path)

        stats = task_manager.get_task_statistics(self.user1_id, db_path=self.db_path)
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["pending"], 2)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["overdue"], 1)
        self.assertEqual(stats["completion_rate"], 33.3)

    def test_cross_user_isolation(self) -> None:
        """User 1 cannot view, edit, complete, or delete User 2's tasks."""
        _, _, u2_task_id = task_manager.add_task(
            user_id=self.user2_id,
            title="User 2 Secret Task",
            category_id=self.u2_cat_work,
            db_path=self.db_path,
        )

        # User 1 tries to view User 2's task
        task = task_manager.get_task_by_id(self.user1_id, u2_task_id, db_path=self.db_path)
        self.assertIsNone(task)

        # User 1 tries to update User 2's task
        ok, msg = task_manager.update_task(self.user1_id, u2_task_id, "Hacked", self.u1_cat_work, db_path=self.db_path)
        self.assertFalse(ok)

        # User 1 tries to complete User 2's task
        ok, msg = task_manager.mark_task_completed(self.user1_id, u2_task_id, db_path=self.db_path)
        self.assertFalse(ok)

        # User 1 tries to delete User 2's task
        ok, msg = task_manager.delete_task(self.user1_id, u2_task_id, db_path=self.db_path)
        self.assertFalse(ok)

    def test_reject_assigning_another_users_category(self) -> None:
        """User 1 cannot create a task using User 2's category."""
        ok, msg, _ = task_manager.add_task(
            user_id=self.user1_id,
            title="Invalid Category Task",
            category_id=self.u2_cat_work,  # Belongs to User 2!
            db_path=self.db_path,
        )
        self.assertFalse(ok)
        self.assertIn("does not belong to you", msg)

    def test_persistence_across_connections(self) -> None:
        """Data persists reliably and can be read by fresh database connections."""
        _, _, task_id = task_manager.add_task(
            user_id=self.user1_id,
            title="Persistent Task",
            category_id=self.u1_cat_work,
            db_path=self.db_path,
        )

        # Fresh query with new connection
        task = task_manager.get_task_by_id(self.user1_id, task_id, db_path=self.db_path)
        self.assertIsNotNone(task)
        self.assertEqual(task["title"], "Persistent Task")


if __name__ == "__main__":
    unittest.main()
