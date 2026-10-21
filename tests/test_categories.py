import gc
from pathlib import Path
import tempfile
import unittest

import auth
import category_manager
from database import initialize_database
import task_manager


class TestCategories(unittest.TestCase):
    """Test category creation, listing, uniqueness, and safe deletion rules."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = Path(self.temp_dir.name) / "test_cat.db"
        initialize_database(self.db_path)

        # Register two test users
        _, _, self.user1_id = auth.register_user("user_one", "Password123", "Password123", db_path=self.db_path)
        _, _, self.user2_id = auth.register_user("user_two", "Password123", "Password123", db_path=self.db_path)

    def tearDown(self) -> None:
        gc.collect()
        self.temp_dir.cleanup()

    def test_default_categories_created_on_registration(self) -> None:
        """Every registered user automatically receives the 4 default categories."""
        cats = category_manager.get_categories(self.user1_id, db_path=self.db_path)
        cat_names = [c["name"] for c in cats]
        for expected in ("Education", "Work", "Personal", "Other"):
            self.assertIn(expected, cat_names)

    def test_add_custom_category(self) -> None:
        """User can create custom categories."""
        ok, msg, cat_id = category_manager.create_category(self.user1_id, "Finance", db_path=self.db_path)
        self.assertTrue(ok)
        self.assertIsNotNone(cat_id)
        
        cats = category_manager.get_categories(self.user1_id, db_path=self.db_path)
        self.assertIn("Finance", [c["name"] for c in cats])

    def test_reject_empty_category_name(self) -> None:
        """Empty or whitespace-only category names are rejected."""
        ok, msg, _ = category_manager.create_category(self.user1_id, "   ", db_path=self.db_path)
        self.assertFalse(ok)
        self.assertIn("cannot be empty", msg)

    def test_reject_duplicate_category_for_same_user(self) -> None:
        """A user cannot create duplicate categories (case-insensitive)."""
        ok1, _, _ = category_manager.create_category(self.user1_id, "Health", db_path=self.db_path)
        self.assertTrue(ok1)

        # Duplicate same case
        ok2, msg2, _ = category_manager.create_category(self.user1_id, "Health", db_path=self.db_path)
        self.assertFalse(ok2)
        self.assertIn("already", msg2)

        # Duplicate different case
        ok3, msg3, _ = category_manager.create_category(self.user1_id, "HEALTH", db_path=self.db_path)
        self.assertFalse(ok3)

    def test_different_users_can_have_same_category_name(self) -> None:
        """Different users can each have a category with the same name."""
        ok1, _, _ = category_manager.create_category(self.user1_id, "Sports", db_path=self.db_path)
        ok2, _, _ = category_manager.create_category(self.user2_id, "Sports", db_path=self.db_path)
        self.assertTrue(ok1)
        self.assertTrue(ok2)

    def test_list_only_current_users_categories(self) -> None:
        """Users can only view their own categories."""
        category_manager.create_category(self.user1_id, "User1_Only", db_path=self.db_path)
        category_manager.create_category(self.user2_id, "User2_Only", db_path=self.db_path)

        cats1 = category_manager.get_categories(self.user1_id, db_path=self.db_path)
        cats2 = category_manager.get_categories(self.user2_id, db_path=self.db_path)

        names1 = [c["name"] for c in cats1]
        names2 = [c["name"] for c in cats2]

        self.assertIn("User1_Only", names1)
        self.assertNotIn("User2_Only", names1)

        self.assertIn("User2_Only", names2)
        self.assertNotIn("User1_Only", names2)

    def test_reject_cross_user_category_access(self) -> None:
        """User cannot access another user's category by ID."""
        _, _, cat_id = category_manager.create_category(self.user2_id, "User2_Secret", db_path=self.db_path)
        
        # User 1 attempts to fetch User 2's category
        cat = category_manager.get_category_by_id(self.user1_id, cat_id, db_path=self.db_path)
        self.assertIsNone(cat)

    def test_prevent_unsafe_category_deletion_with_tasks(self) -> None:
        """Category cannot be deleted if active tasks reference it."""
        _, _, cat_id = category_manager.create_category(self.user1_id, "ProjectX", db_path=self.db_path)
        
        # Assign a task to ProjectX
        task_manager.add_task(self.user1_id, "Write Report", cat_id, db_path=self.db_path)

        # Attempt to delete category
        ok, msg = category_manager.delete_category(self.user1_id, cat_id, db_path=self.db_path)
        self.assertFalse(ok)
        self.assertIn("assigned to 1 task", msg)

    def test_allow_deletion_of_unused_category(self) -> None:
        """Category can be deleted cleanly if no tasks are assigned to it."""
        _, _, cat_id = category_manager.create_category(self.user1_id, "TempCat", db_path=self.db_path)
        
        ok, msg = category_manager.delete_category(self.user1_id, cat_id, db_path=self.db_path)
        self.assertTrue(ok)
        self.assertIn("deleted successfully", msg)

        # Ensure it is gone
        cat = category_manager.get_category_by_id(self.user1_id, cat_id, db_path=self.db_path)
        self.assertIsNone(cat)


if __name__ == "__main__":
    unittest.main()
