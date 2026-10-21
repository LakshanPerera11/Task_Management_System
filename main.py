"""Application entry point for the Task Management System."""

import sys
from database import initialize_database
from ui import TaskApp


def main() -> None:
    """Initialize database schema and start the desktop Tkinter application."""
    # Ensure database tables and indexes exist
    initialize_database()

    # Launch desktop application main loop
    app = TaskApp()
    app.mainloop()


if __name__ == "__main__":
    main()
