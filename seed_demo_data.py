"""Helper script to seed realistic demo data for testing, screenshots, and presentations."""

from datetime import date, timedelta
import auth
import category_manager
from database import initialize_database
import task_manager


def seed_demo_data() -> None:
    """Populate database with sample student user, custom categories, and tasks."""
    initialize_database()

    username = "demo_student"
    password = "DemoPassword123"

    print(f"Creating demo account: '{username}'...")
    ok, msg, user_id = auth.register_user(username, password, password)
    if not ok:
        # Check if already registered
        ok_login, _, session = auth.login_user(username, password)
        if ok_login and session:
            user_id = session["id"]
            print("Demo account already exists. Using existing account.")
        else:
            print(f"Could not register or log in demo user: {msg}")
            return
    else:
        print(f"Demo account registered with ID: {user_id}")

    # Add custom category
    print("Creating custom category: 'Capstone Project'...")
    category_manager.create_category(user_id, "Capstone Project")

    # Fetch user categories
    cats = category_manager.get_categories(user_id)
    cat_map = {c["name"]: c["id"] for c in cats}

    today = date.today()
    yesterday = (today - timedelta(days=2)).isoformat()
    today_str = today.isoformat()
    tomorrow = (today + timedelta(days=1)).isoformat()
    next_week = (today + timedelta(days=7)).isoformat()

    sample_tasks = [
        (
            "Finalize Software Requirements Specification (SRS)",
            cat_map.get("Education"),
            "Complete all 19 sections of the academic SRS document for final submission.",
            today_str,
            False,
        ),
        (
            "Implement SQLite Schema with Composite Constraints",
            cat_map.get("Capstone Project"),
            "Create users, categories, and tasks tables with PRAGMA foreign_keys enabled.",
            yesterday,
            True,  # Completed
        ),
        (
            "Prepare Slides for Final Project Presentation",
            cat_map.get("Education"),
            "Organize presentation outline covering architecture, database, and live demo flow.",
            next_week,
            False,
        ),
        (
            "Submit Weekly Internship Progress Report",
            cat_map.get("Work"),
            "Summarize task management system development achievements and unit test outcomes.",
            tomorrow,
            False,
        ),
        (
            "Conduct Code Review and Security Audit",
            cat_map.get("Capstone Project"),
            "Verify PBKDF2 password hashing rounds and parameterized SQL queries.",
            yesterday,
            True,  # Completed
        ),
        (
            "Schedule Annual Medical Checkup",
            cat_map.get("Personal"),
            "Call university health clinic to book routine checkup appointment.",
            next_week,
            False,
        ),
    ]

    print("Inserting sample tasks...")
    for title, cat_id, desc, due, is_completed in sample_tasks:
        if not cat_id:
            continue
        ok_t, _, task_id = task_manager.add_task(
            user_id=user_id,
            title=title,
            category_id=cat_id,
            description=desc,
            due_date=due,
        )
        if ok_t and task_id and is_completed:
            task_manager.mark_task_completed(user_id, task_id)

    print("\nDemo data seeding complete!")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("You can now launch 'python main.py' and log in with these credentials to capture screenshots or demo.")


if __name__ == "__main__":
    seed_demo_data()
