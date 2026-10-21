"""Input validation functions for user accounts, categories, and tasks."""

from datetime import datetime
import re

from config import (
    CATEGORY_MAX_LENGTH,
    CATEGORY_MIN_LENGTH,
    DATE_FORMAT,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    TASK_DESC_MAX_LENGTH,
    TASK_TITLE_MAX_LENGTH,
    TASK_TITLE_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    VALID_TASK_STATUSES,
)

# Allowed characters: alphanumeric and underscores; must start with alphanumeric
_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_]*$")


def validate_username(username: str) -> tuple[bool, str]:
    """Validate username length, presence, and allowed characters."""
    cleaned = (username or "").strip()
    if not cleaned:
        return False, "Username is required and cannot be blank."
    if len(cleaned) < USERNAME_MIN_LENGTH:
        return False, f"Username must be at least {USERNAME_MIN_LENGTH} characters long."
    if len(cleaned) > USERNAME_MAX_LENGTH:
        return False, f"Username cannot exceed {USERNAME_MAX_LENGTH} characters."
    if not _USERNAME_PATTERN.match(cleaned):
        return (
            False,
            "Username may only contain letters, numbers, and underscores, and must start with a letter or number.",
        )
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password presence, length, and content."""
    if not password:
        return False, "Password is required."
    if len(password.strip()) == 0:
        return False, "Password cannot consist solely of whitespace."
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must contain at least {PASSWORD_MIN_LENGTH} characters."
    if len(password) > PASSWORD_MAX_LENGTH:
        return False, f"Password cannot exceed {PASSWORD_MAX_LENGTH} characters."
    return True, ""


def validate_password_confirmation(password: str, confirm_password: str) -> tuple[bool, str]:
    """Ensure password and password confirmation match exactly."""
    if password != confirm_password:
        return False, "Passwords do not match."
    return True, ""


def validate_category_name(name: str) -> tuple[bool, str]:
    """Validate category name presence and length."""
    cleaned = (name or "").strip()
    if not cleaned:
        return False, "Category name is required and cannot be empty."
    if len(cleaned) < CATEGORY_MIN_LENGTH:
        return False, f"Category name must have at least {CATEGORY_MIN_LENGTH} character."
    if len(cleaned) > CATEGORY_MAX_LENGTH:
        return False, f"Category name cannot exceed {CATEGORY_MAX_LENGTH} characters."
    return True, ""


def validate_task_title(title: str) -> tuple[bool, str]:
    """Validate task title presence and length."""
    cleaned = (title or "").strip()
    if not cleaned:
        return False, "Task title is required."
    if len(cleaned) < TASK_TITLE_MIN_LENGTH:
        return False, f"Task title must have at least {TASK_TITLE_MIN_LENGTH} character."
    if len(cleaned) > TASK_TITLE_MAX_LENGTH:
        return False, f"Task title cannot exceed {TASK_TITLE_MAX_LENGTH} characters."
    return True, ""


def validate_task_description(description: str | None) -> tuple[bool, str]:
    """Validate task description length (optional field)."""
    cleaned = (description or "").strip()
    if len(cleaned) > TASK_DESC_MAX_LENGTH:
        return False, f"Description cannot exceed {TASK_DESC_MAX_LENGTH} characters (currently {len(cleaned)})."
    return True, ""


def validate_due_date(due_date_str: str | None) -> tuple[bool, str]:
    """Validate due date format (YYYY-MM-DD) and calendar validity.
    
    Returns (True, '') if empty/None because due date is optional.
    """
    if due_date_str is None:
        return True, ""
    cleaned = due_date_str.strip()
    if not cleaned:
        return True, ""
        
    if len(cleaned) != 10 or cleaned[4] != "-" or cleaned[7] != "-":
        return False, "Due date must use ISO format: YYYY-MM-DD (e.g., 2026-10-31)."
        
    try:
        parsed_date = datetime.strptime(cleaned, DATE_FORMAT)
        # Sanity check for reasonable calendar year range
        if parsed_date.year < 1900 or parsed_date.year > 2100:
            return False, "Due date year must be between 1900 and 2100."
        return True, ""
    except ValueError:
        return False, f"'{cleaned}' is not a valid calendar date. Please check the month and day (e.g., February 30 does not exist)."


def validate_task_status(status: str) -> tuple[bool, str]:
    """Ensure task status is one of the allowed business values ('Pending' or 'Completed')."""
    if status not in VALID_TASK_STATUSES:
        return False, f"Invalid task status '{status}'. Allowed statuses: {', '.join(VALID_TASK_STATUSES)}."
    return True, ""
