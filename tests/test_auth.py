import gc
from pathlib import Path
import tempfile
import unittest

import auth
from database import initialize_database


class TestAuth(unittest.TestCase):
    """Test user registration and authentication workflows."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = Path(self.temp_dir.name) / "test_auth.db"
        initialize_database(self.db_path)

    def tearDown(self) -> None:
        gc.collect()
        self.temp_dir.cleanup()

    def test_successful_registration(self) -> None:
        """A user with valid credentials can register successfully."""
        ok, msg, user_id = auth.register_user("john_doe", "Secret123", "Secret123", db_path=self.db_path)
        self.assertTrue(ok)
        self.assertIsNotNone(user_id)
        self.assertIn("Account created successfully", msg)

    def test_successful_login(self) -> None:
        """A registered user can log in with correct credentials."""
        auth.register_user("jane_doe", "Password123", "Password123", db_path=self.db_path)
        ok, msg, session = auth.login_user("jane_doe", "Password123", db_path=self.db_path)
        self.assertTrue(ok)
        self.assertEqual(session["username"], "jane_doe")
        self.assertIsNotNone(session["id"])

    def test_incorrect_password_rejected(self) -> None:
        """Login fails when an incorrect password is provided."""
        auth.register_user("jane_doe", "Password123", "Password123", db_path=self.db_path)
        ok, msg, session = auth.login_user("jane_doe", "WrongPass999", db_path=self.db_path)
        self.assertFalse(ok)
        self.assertIsNone(session)
        self.assertEqual(msg, "Invalid username or password.")

    def test_unknown_username_rejected(self) -> None:
        """Login fails for non-existent users with a generic message."""
        ok, msg, session = auth.login_user("ghost_user", "AnyPassword123", db_path=self.db_path)
        self.assertFalse(ok)
        self.assertIsNone(session)
        self.assertEqual(msg, "Invalid username or password.")

    def test_duplicate_username_rejected(self) -> None:
        """Duplicate usernames (including case-insensitive matches) are rejected."""
        ok1, _, _ = auth.register_user("alice123", "Password123", "Password123", db_path=self.db_path)
        self.assertTrue(ok1)
        
        # Exact duplicate
        ok2, msg2, _ = auth.register_user("alice123", "AnotherPass456", "AnotherPass456", db_path=self.db_path)
        self.assertFalse(ok2)
        self.assertIn("already", msg2.lower())

        # Case-insensitive duplicate ("ALICE123")
        ok3, msg3, _ = auth.register_user("ALICE123", "AnotherPass456", "AnotherPass456", db_path=self.db_path)
        self.assertFalse(ok3)

    def test_invalid_username_rejected(self) -> None:
        """Usernames with invalid characters, too short, or empty are rejected."""
        # Empty
        ok, msg, _ = auth.register_user("", "Password123", "Password123", db_path=self.db_path)
        self.assertFalse(ok)

        # Too short (< 3 chars)
        ok, msg, _ = auth.register_user("ab", "Password123", "Password123", db_path=self.db_path)
        self.assertFalse(ok)

        # Invalid characters (e.g., spaces or symbols)
        ok, msg, _ = auth.register_user("bad user!", "Password123", "Password123", db_path=self.db_path)
        self.assertFalse(ok)

    def test_password_mismatch_rejected(self) -> None:
        """Registration fails if password and confirmation do not match."""
        ok, msg, _ = auth.register_user("valid_user", "Password123", "DifferentPass", db_path=self.db_path)
        self.assertFalse(ok)
        self.assertIn("do not match", msg)

    def test_short_password_rejected(self) -> None:
        """Passwords shorter than 6 characters are rejected."""
        ok, msg, _ = auth.register_user("valid_user", "12345", "12345", db_path=self.db_path)
        self.assertFalse(ok)
        self.assertIn("at least 6 characters", msg)

    def test_password_hash_and_salt_uniqueness(self) -> None:
        """Plaintext is never stored, and unique random salts yield distinct hashes for identical passwords."""
        plain = "MySecretPassword123"
        hash1, salt1 = auth.hash_password(plain)
        hash2, salt2 = auth.hash_password(plain)

        self.assertNotEqual(plain, hash1)
        self.assertNotEqual(salt1, salt2)
        self.assertNotEqual(hash1, hash2)

    def test_independent_user_accounts(self) -> None:
        """Two different users can independently register and log in."""
        auth.register_user("user_alpha", "PasswordA1", "PasswordA1", db_path=self.db_path)
        auth.register_user("user_beta", "PasswordB2", "PasswordB2", db_path=self.db_path)

        ok_a, _, s_a = auth.login_user("user_alpha", "PasswordA1", db_path=self.db_path)
        ok_b, _, s_b = auth.login_user("user_beta", "PasswordB2", db_path=self.db_path)

        self.assertTrue(ok_a)
        self.assertTrue(ok_b)
        self.assertNotEqual(s_a["id"], s_b["id"])


if __name__ == "__main__":
    unittest.main()
