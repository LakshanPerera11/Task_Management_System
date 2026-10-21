"""Application configuration and constants for the Task Management System."""

from pathlib import Path

# Application Information
APP_NAME = "Task Management System"
APP_SUBTITLE = "Organize, track, and accomplish your personal tasks"
APP_VERSION = "1.0.0"

# Filesystem Paths
BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DEFAULT_DB_PATH = DATABASE_DIR / "task_manager.db"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

# Ensure runtime directories exist
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Date and Timestamp Formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Task Business Rules
VALID_TASK_STATUSES = ("Pending", "Completed")
DEFAULT_TASK_STATUS = "Pending"
DEFAULT_CATEGORIES = ("Education", "Work", "Personal", "Other")

# Validation Constraints & Length Limits
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 128
CATEGORY_MIN_LENGTH = 1
CATEGORY_MAX_LENGTH = 50
TASK_TITLE_MIN_LENGTH = 1
TASK_TITLE_MAX_LENGTH = 120
TASK_DESC_MAX_LENGTH = 1000

# Security Configuration
PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_HASH_ROUNDS = 120_000
PASSWORD_SALT_BYTES = 16

# UI Color Palette (Neutral modern with dark charcoal and deep green accents)
UI_COLORS = {
    "header_bg": "#1E293B",        # Deep slate / charcoal
    "header_fg": "#FFFFFF",        # White text
    "bg_main": "#F8FAFC",          # Soft light background
    "bg_card": "#FFFFFF",          # Clean white container
    "border": "#E2E8F0",           # Subtle light border
    "text_primary": "#0F172A",     # Near black for headings
    "text_secondary": "#475569",   # Slate gray for descriptions
    "text_muted": "#94A3B8",       # Light gray for hints/placeholders
    "accent_green": "#166534",     # Deep forest green (Primary action)
    "accent_green_hover": "#14532D",
    "accent_blue": "#2563EB",      # Blue accent
    "accent_blue_hover": "#1D4ED8",
    "status_pending": "#D97706",   # Amber for pending
    "status_pending_bg": "#FEF3C7",# Light amber badge bg
    "status_completed": "#16A34A", # Fresh green for completed
    "status_completed_bg": "#DCFCE7",# Light green badge bg
    "danger": "#DC2626",           # Crimson red for delete
    "danger_hover": "#B91C1C",
    "btn_secondary": "#64748B",
}

# Window Geometry
DEFAULT_WINDOW_WIDTH = 1080
DEFAULT_WINDOW_HEIGHT = 720
MIN_WINDOW_WIDTH = 960
MIN_WINDOW_HEIGHT = 640
