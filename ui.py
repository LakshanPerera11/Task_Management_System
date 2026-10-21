"""Modern desktop GUI for the Task Management System using Tkinter and ttk."""

from datetime import date, datetime, timedelta
import tkinter as tk
from tkinter import font as tkfont, messagebox, ttk
from typing import Any

import auth
import category_manager
from config import (
    APP_NAME,
    APP_SUBTITLE,
    DATE_FORMAT,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    UI_COLORS,
)
import task_manager
import validators


class TaskApp(tk.Tk):
    """Main application window managing authentication, session state, and screens."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.configure(bg=UI_COLORS["bg_main"])

        # Authenticated user session dictionary: {'id': int, 'username': str, 'created_at': str}
        self.current_user: dict[str, Any] | None = None

        self._configure_styles()
        self.show_login()

    def _configure_styles(self) -> None:
        """Configure ttk styles for a modern, neutral look with dark green and charcoal accents."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Global font definitions
        font_family = "Segoe UI" if "Segoe UI" in tkfont.families() else "Helvetica"

        style.configure(".", background=UI_COLORS["bg_main"], font=(font_family, 10))
        
        # Frame styles
        style.configure("TFrame", background=UI_COLORS["bg_main"])
        style.configure("Card.TFrame", background=UI_COLORS["bg_card"], relief="solid", borderwidth=1)
        style.configure("Header.TFrame", background=UI_COLORS["header_bg"])

        # Label styles
        style.configure("TLabel", background=UI_COLORS["bg_main"], foreground=UI_COLORS["text_primary"])
        style.configure("Card.TLabel", background=UI_COLORS["bg_card"], foreground=UI_COLORS["text_primary"])
        style.configure("HeaderTitle.TLabel", background=UI_COLORS["header_bg"], foreground=UI_COLORS["header_fg"], font=(font_family, 16, "bold"))
        style.configure("HeaderSubtitle.TLabel", background=UI_COLORS["header_bg"], foreground="#94A3B8", font=(font_family, 9))
        style.configure("HeaderUser.TLabel", background=UI_COLORS["header_bg"], foreground="#E2E8F0", font=(font_family, 10))

        # Metrics Card Labels
        style.configure("MetricValue.TLabel", background=UI_COLORS["bg_card"], font=(font_family, 20, "bold"), foreground=UI_COLORS["text_primary"])
        style.configure("MetricTitle.TLabel", background=UI_COLORS["bg_card"], font=(font_family, 9), foreground=UI_COLORS["text_secondary"])

        # Buttons
        style.configure("TButton", padding=(10, 6), font=(font_family, 10))
        
        # Primary Action Button (Forest Green)
        style.configure(
            "Primary.TButton",
            background=UI_COLORS["accent_green"],
            foreground="white",
            font=(font_family, 10, "bold"),
            padding=(12, 6),
        )
        style.map(
            "Primary.TButton",
            background=[("active", UI_COLORS["accent_green_hover"]), ("pressed", UI_COLORS["accent_green_hover"])],
            foreground=[("active", "white")],
        )

        # Danger Button (Red)
        style.configure(
            "Danger.TButton",
            background=UI_COLORS["danger"],
            foreground="white",
            font=(font_family, 10),
            padding=(10, 6),
        )
        style.map(
            "Danger.TButton",
            background=[("active", UI_COLORS["danger_hover"]), ("pressed", UI_COLORS["danger_hover"])],
            foreground=[("active", "white")],
        )

        # Treeview (Table)
        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground=UI_COLORS["text_primary"],
            rowheight=30,
            font=(font_family, 10),
            borderwidth=1,
        )
        style.configure(
            "Treeview.Heading",
            background="#F1F5F9",
            foreground=UI_COLORS["text_primary"],
            font=(font_family, 10, "bold"),
            padding=(6, 6),
        )
        style.map("Treeview", background=[("selected", "#E2E8F0")], foreground=[("selected", UI_COLORS["text_primary"])])

    def clear_screen(self) -> None:
        """Destroy all current child widgets before switching views."""
        for child in self.winfo_children():
            child.destroy()

    # =========================================================================
    # LOGIN SCREEN
    # =========================================================================
    def show_login(self) -> None:
        """Render the login screen."""
        self.current_user = None
        self.clear_screen()

        container = ttk.Frame(self, padding=40)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Card container
        card = tk.Frame(container, bg=UI_COLORS["bg_card"], bd=1, relief="solid", padx=35, pady=30)
        card.pack()

        # Branding
        title_label = tk.Label(
            card,
            text=f"✔ {APP_NAME}",
            font=("Segoe UI", 22, "bold"),
            fg=UI_COLORS["header_bg"],
            bg=UI_COLORS["bg_card"],
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 4))

        subtitle_label = tk.Label(
            card,
            text=APP_SUBTITLE,
            font=("Segoe UI", 10),
            fg=UI_COLORS["text_secondary"],
            bg=UI_COLORS["bg_card"],
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 24))

        # Username
        tk.Label(card, text="Username", font=("Segoe UI", 10, "bold"), bg=UI_COLORS["bg_card"]).grid(row=2, column=0, sticky="w", pady=(6, 2))
        username_entry = ttk.Entry(card, width=32, font=("Segoe UI", 10))
        username_entry.grid(row=3, column=0, columnspan=2, pady=(0, 12), sticky="ew")

        # Password
        tk.Label(card, text="Password", font=("Segoe UI", 10, "bold"), bg=UI_COLORS["bg_card"]).grid(row=4, column=0, sticky="w", pady=(6, 2))
        password_entry = ttk.Entry(card, width=32, show="•", font=("Segoe UI", 10))
        password_entry.grid(row=5, column=0, columnspan=2, pady=(0, 20), sticky="ew")

        def handle_login() -> None:
            username = username_entry.get()
            password = password_entry.get()
            ok, msg, user = auth.login_user(username, password)
            if ok and user:
                self.current_user = user
                self.show_dashboard()
            else:
                messagebox.showerror("Login Failed", msg)

        login_btn = ttk.Button(card, text="Sign In", style="Primary.TButton", command=handle_login)
        login_btn.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        register_btn = ttk.Button(card, text="Create New Account", command=self.show_registration)
        register_btn.grid(row=7, column=0, columnspan=2, sticky="ew")

        username_entry.focus_set()
        username_entry.bind("<Return>", lambda _: password_entry.focus_set())
        password_entry.bind("<Return>", lambda _: handle_login())

    # =========================================================================
    # REGISTRATION SCREEN
    # =========================================================================
    def show_registration(self) -> None:
        """Render the registration screen."""
        self.clear_screen()

        container = ttk.Frame(self, padding=40)
        container.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(container, bg=UI_COLORS["bg_card"], bd=1, relief="solid", padx=35, pady=30)
        card.pack()

        # Header
        title_label = tk.Label(
            card,
            text="Create an Account",
            font=("Segoe UI", 20, "bold"),
            fg=UI_COLORS["header_bg"],
            bg=UI_COLORS["bg_card"],
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 4))

        info_label = tk.Label(
            card,
            text="Register to start organizing your personal tasks",
            font=("Segoe UI", 9),
            fg=UI_COLORS["text_secondary"],
            bg=UI_COLORS["bg_card"],
        )
        info_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Username
        tk.Label(card, text="Username (3-30 alphanumeric characters)", font=("Segoe UI", 9, "bold"), bg=UI_COLORS["bg_card"]).grid(row=2, column=0, sticky="w", pady=(4, 2))
        username_entry = ttk.Entry(card, width=34, font=("Segoe UI", 10))
        username_entry.grid(row=3, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        # Password
        tk.Label(card, text="Password (at least 6 characters)", font=("Segoe UI", 9, "bold"), bg=UI_COLORS["bg_card"]).grid(row=4, column=0, sticky="w", pady=(4, 2))
        password_entry = ttk.Entry(card, width=34, show="•", font=("Segoe UI", 10))
        password_entry.grid(row=5, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        # Confirm Password
        tk.Label(card, text="Confirm Password", font=("Segoe UI", 9, "bold"), bg=UI_COLORS["bg_card"]).grid(row=6, column=0, sticky="w", pady=(4, 2))
        confirm_entry = ttk.Entry(card, width=34, show="•", font=("Segoe UI", 10))
        confirm_entry.grid(row=7, column=0, columnspan=2, pady=(0, 20), sticky="ew")

        def handle_register() -> None:
            username = username_entry.get()
            password = password_entry.get()
            confirm = confirm_entry.get()

            ok, msg, _ = auth.register_user(username, password, confirm)
            if ok:
                messagebox.showinfo("Registration Successful", msg)
                self.show_login()
            else:
                messagebox.showerror("Registration Error", msg)

        reg_btn = ttk.Button(card, text="Register Account", style="Primary.TButton", command=handle_register)
        reg_btn.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        back_btn = ttk.Button(card, text="Back to Sign In", command=self.show_login)
        back_btn.grid(row=9, column=0, columnspan=2, sticky="ew")

        username_entry.focus_set()
        username_entry.bind("<Return>", lambda _: password_entry.focus_set())
        password_entry.bind("<Return>", lambda _: confirm_entry.focus_set())
        confirm_entry.bind("<Return>", lambda _: handle_register())

    # =========================================================================
    # MAIN DASHBOARD SCREEN
    # =========================================================================
    def show_dashboard(self) -> None:
        """Render the authenticated user dashboard."""
        if not self.current_user:
            self.show_login()
            return

        self.clear_screen()

        # 1. Top Header Bar
        header = ttk.Frame(self, style="Header.TFrame", padding=(20, 12))
        header.pack(fill="x")

        # Title & Subtitle
        title_box = ttk.Frame(header, style="Header.TFrame")
        title_box.pack(side="left")
        ttk.Label(title_box, text=f"✔ {APP_NAME}", style="HeaderTitle.TLabel").pack(anchor="w")
        ttk.Label(title_box, text=f"Logged in as: {self.current_user['username']}", style="HeaderSubtitle.TLabel").pack(anchor="w")

        # Logout button
        def handle_logout() -> None:
            if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?"):
                self.current_user = None
                self.show_login()

        logout_btn = ttk.Button(header, text="Log Out", command=handle_logout)
        logout_btn.pack(side="right", padx=(10, 0))

        # Main Body Frame
        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)

        # 2. Metrics / Statistics Bar
        self._build_metrics_banner(body)

        # 3. Search and Filter Toolbar
        self._build_filter_toolbar(body)

        # 4. Task Table with Scrollbar
        self._build_task_table(body)

        # 5. Task Detail / Preview Card
        self._build_detail_pane(body)

        # 6. Bottom Action Bar
        self._build_bottom_actions(body)

        # Initial data load
        self.refresh_dashboard()

    def _build_metrics_banner(self, parent: ttk.Frame) -> None:
        """Construct the 4 summary statistics cards."""
        metrics_frame = ttk.Frame(parent)
        metrics_frame.pack(fill="x", pady=(0, 12))
        metrics_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="metric")

        self.metric_cards = {}
        metric_configs = [
            ("total", "Total Tasks", "#0F172A"),
            ("pending", "Pending Tasks", UI_COLORS["status_pending"]),
            ("completed", "Completed Tasks", UI_COLORS["status_completed"]),
            ("overdue", "Overdue Tasks", UI_COLORS["danger"]),
        ]

        for idx, (key, title, color) in enumerate(metric_configs):
            card = tk.Frame(metrics_frame, bg=UI_COLORS["bg_card"], bd=1, relief="solid", padx=14, pady=8)
            card.grid(row=0, column=idx, padx=4, sticky="nsew")

            val_label = tk.Label(card, text="0", font=("Segoe UI", 18, "bold"), fg=color, bg=UI_COLORS["bg_card"])
            val_label.pack(anchor="w")

            title_label = tk.Label(card, text=title, font=("Segoe UI", 9), fg=UI_COLORS["text_secondary"], bg=UI_COLORS["bg_card"])
            title_label.pack(anchor="w")

            self.metric_cards[key] = val_label

    def _build_filter_toolbar(self, parent: ttk.Frame) -> None:
        """Construct search box, category dropdown, status dropdown, and action triggers."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", pady=(0, 10))

        # Search box
        ttk.Label(toolbar, text="Search:").pack(side="left", padx=(0, 4))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=22)
        search_entry.pack(side="left", padx=(0, 12))
        search_entry.bind("<Return>", lambda _: self.refresh_dashboard())

        # Category filter
        ttk.Label(toolbar, text="Category:").pack(side="left", padx=(0, 4))
        self.category_filter_var = tk.StringVar(value="All Categories")
        self.category_filter_combo = ttk.Combobox(
            toolbar,
            textvariable=self.category_filter_var,
            state="readonly",
            width=16,
        )
        self.category_filter_combo.pack(side="left", padx=(0, 12))
        self.category_filter_combo.bind("<<ComboboxSelected>>", lambda _: self.refresh_dashboard())

        # Status filter
        ttk.Label(toolbar, text="Status:").pack(side="left", padx=(0, 4))
        self.status_filter_var = tk.StringVar(value="All Statuses")
        status_combo = ttk.Combobox(
            toolbar,
            textvariable=self.status_filter_var,
            values=["All Statuses", "Pending", "Completed"],
            state="readonly",
            width=14,
        )
        status_combo.pack(side="left", padx=(0, 12))
        status_combo.bind("<<ComboboxSelected>>", lambda _: self.refresh_dashboard())

        # Apply and Clear buttons
        ttk.Button(toolbar, text="Filter", command=self.refresh_dashboard).pack(side="left", padx=2)
        
        def handle_clear_filters() -> None:
            self.search_var.set("")
            self.category_filter_var.set("All Categories")
            self.status_filter_var.set("All Statuses")
            self.refresh_dashboard()

        ttk.Button(toolbar, text="Clear", command=handle_clear_filters).pack(side="left", padx=2)

        # Right-aligned Management buttons
        manage_cat_btn = ttk.Button(toolbar, text="📁 Manage Categories", command=self.open_category_manager)
        manage_cat_btn.pack(side="right", padx=(6, 0))

        new_task_btn = ttk.Button(toolbar, text="+ New Task", style="Primary.TButton", command=self.open_add_task_dialog)
        new_task_btn.pack(side="right", padx=(0, 6))

    def _build_task_table(self, parent: ttk.Frame) -> None:
        """Construct the ttk.Treeview table displaying user tasks."""
        table_container = ttk.Frame(parent)
        table_container.pack(fill="both", expand=True)

        columns = ("id", "title", "category", "due_date", "status", "created_at")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        # Define column headings and widths
        column_configs = [
            ("id", "ID", 50, "center"),
            ("title", "Task Title", 340, "w"),
            ("category", "Category", 140, "w"),
            ("due_date", "Due Date", 110, "center"),
            ("status", "Status", 110, "center"),
            ("created_at", "Created At", 150, "center"),
        ]

        for col_id, title, width, align in column_configs:
            self.tree.heading(col_id, text=title, command=lambda c=col_id: self._sort_by_column(c, False))
            self.tree.column(col_id, width=width, anchor=align)

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        # Row tag colors
        self.tree.tag_configure("pending", foreground="#B45309")
        self.tree.tag_configure("completed", foreground="#15803D")
        self.tree.tag_configure("overdue", foreground="#DC2626")

        # Event bindings
        self.tree.bind("<<TreeviewSelect>>", self._on_task_selected)
        self.tree.bind("<Double-1>", lambda _: self.open_edit_task_dialog())

    def _build_detail_pane(self, parent: ttk.Frame) -> None:
        """Construct a bottom preview pane showing description and details of selected task."""
        self.detail_frame = tk.LabelFrame(
            parent,
            text="Selected Task Description",
            font=("Segoe UI", 9, "bold"),
            bg=UI_COLORS["bg_card"],
            fg=UI_COLORS["text_secondary"],
            padx=10,
            pady=6,
        )
        self.detail_frame.pack(fill="x", pady=(8, 0))

        self.detail_text = tk.Label(
            self.detail_frame,
            text="Select a task from the list to view its full description and details.",
            font=("Segoe UI", 9),
            fg=UI_COLORS["text_secondary"],
            bg=UI_COLORS["bg_card"],
            justify="left",
            anchor="w",
            wraplength=920,
        )
        self.detail_text.pack(fill="x")

    def _build_bottom_actions(self, parent: ttk.Frame) -> None:
        """Construct the bottom action toolbar."""
        actions = ttk.Frame(parent)
        actions.pack(fill="x", pady=(10, 0))

        ttk.Button(actions, text="✏ Edit Task", command=self.open_edit_task_dialog).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="✔ Mark Completed", style="Primary.TButton", command=self.handle_mark_completed).pack(side="left", padx=6)
        ttk.Button(actions, text="🗑 Delete Task", style="Danger.TButton", command=self.handle_delete_task).pack(side="left", padx=6)
        ttk.Button(actions, text="🔄 Refresh", command=self.refresh_dashboard).pack(side="left", padx=6)

        self.status_bar_label = ttk.Label(actions, text="", font=("Segoe UI", 9))
        self.status_bar_label.pack(side="right")

    # =========================================================================
    # EVENT HANDLERS & REFRESH LOGIC
    # =========================================================================
    def _on_task_selected(self, _event: Any = None) -> None:
        """Update detail pane when user selects a row in the treeview."""
        selected = self.tree.selection()
        if not selected:
            self.detail_text.config(text="Select a task from the list to view its full description and details.")
            return

        task_id = int(self.tree.item(selected[0], "values")[0])
        row = task_manager.get_task_by_id(self.current_user["id"], task_id)
        if row:
            desc = row["description"] if row["description"] else "(No description provided)"
            updated_info = f"Last updated: {row['updated_at']}"
            self.detail_text.config(
                text=f"Title: {row['title']}\nDescription: {desc}\nStatus: {row['status']} | Due Date: {row['due_date'] or 'None'} | {updated_info}"
            )

    def _sort_by_column(self, col: str, reverse: bool) -> None:
        """Sort treeview rows when clicking a column heading."""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        # Numeric sort for ID
        if col == "id":
            items.sort(key=lambda t: int(t[0]), reverse=reverse)
        else:
            items.sort(key=lambda t: t[0].lower(), reverse=reverse)

        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)

        self.tree.heading(col, command=lambda: self._sort_by_column(col, not reverse))

    def refresh_dashboard(self) -> None:
        """Refresh statistics cards, category filter values, and task table rows from SQLite."""
        if not self.current_user:
            return

        user_id = self.current_user["id"]

        # 1. Update Metrics
        stats = task_manager.get_task_statistics(user_id)
        self.metric_cards["total"].config(text=str(stats["total"]))
        self.metric_cards["pending"].config(text=str(stats["pending"]))
        self.metric_cards["completed"].config(text=str(stats["completed"]))
        self.metric_cards["overdue"].config(text=str(stats["overdue"]))

        # 2. Update Categories list & mapping
        categories = category_manager.get_categories(user_id)
        self.category_id_map = {cat["name"]: cat["id"] for cat in categories}
        self.category_name_map = {cat["id"]: cat["name"] for cat in categories}
        
        filter_options = ["All Categories"] + list(self.category_id_map.keys())
        self.category_filter_combo["values"] = filter_options
        if self.category_filter_var.get() not in filter_options:
            self.category_filter_var.set("All Categories")

        # 3. Apply Filters and Load Tasks
        raw_status = self.status_filter_var.get()
        status_param = "All" if raw_status == "All Statuses" else raw_status

        selected_cat_name = self.category_filter_var.get()
        cat_id_param = None
        if selected_cat_name != "All Categories":
            cat_id_param = self.category_id_map.get(selected_cat_name)

        search_query = self.search_var.get()

        tasks = task_manager.get_tasks(
            user_id=user_id,
            status=status_param,
            category_id=cat_id_param,
            search_term=search_query,
        )

        # Clear existing table items
        for item in self.tree.get_children():
            self.tree.delete(item)

        today_str = date.today().isoformat()

        # Insert fresh rows
        for row in tasks:
            status_display = "⏳ Pending" if row["status"] == "Pending" else "✅ Completed"
            due_display = row["due_date"] or "-"
            
            # Determine visual tag
            row_tag = "pending"
            if row["status"] == "Completed":
                row_tag = "completed"
            elif row["due_date"] and row["due_date"] < today_str:
                row_tag = "overdue"
                status_display = "⚠ Overdue"

            self.tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["title"],
                    row["category_name"],
                    due_display,
                    status_display,
                    row["created_at"],
                ),
                tags=(row_tag,),
            )

        self.status_bar_label.config(text=f"Showing {len(tasks)} of {stats['total']} tasks | Completion Rate: {stats['completion_rate']}%")
        self.detail_text.config(text="Select a task from the list to view its full description and details.")

    def _get_selected_task_id(self) -> int | None:
        """Return the selected task ID or display a warning."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a task from the table first.")
            return None
        return int(self.tree.item(selected[0], "values")[0])

    # =========================================================================
    # TASK ACTIONS & MODALS
    # =========================================================================
    def open_add_task_dialog(self) -> None:
        """Display modal dialog to add a new task."""
        if not self.current_user:
            return

        categories = category_manager.get_categories(self.current_user["id"])
        if not categories:
            messagebox.showerror("No Categories", "You do not have any categories available. Please add a category first.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Add New Task")
        dialog.geometry("520x460")
        dialog.minsize(480, 420)
        dialog.transient(self)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(frame, text="Task Title *", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        title_entry = ttk.Entry(frame, width=45)
        title_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        # Category
        ttk.Label(frame, text="Category *", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(0, 4))
        category_names = [cat["name"] for cat in categories]
        category_combo = ttk.Combobox(frame, values=category_names, state="readonly", width=30)
        category_combo.grid(row=3, column=0, sticky="w", pady=(0, 12))
        category_combo.set(category_names[0])

        # Due Date
        ttk.Label(frame, text="Due Date (Optional, YYYY-MM-DD)", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="w", pady=(0, 4))
        due_frame = ttk.Frame(frame)
        due_frame.grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 12))
        
        due_entry = ttk.Entry(due_frame, width=18)
        due_entry.pack(side="left", padx=(0, 8))

        def set_due(days_offset: int) -> None:
            target = date.today() + timedelta(days=days_offset)
            due_entry.delete(0, "end")
            due_entry.insert(0, target.strftime(DATE_FORMAT))

        ttk.Button(due_frame, text="Today", command=lambda: set_due(0)).pack(side="left", padx=2)
        ttk.Button(due_frame, text="Tomorrow", command=lambda: set_due(1)).pack(side="left", padx=2)
        ttk.Button(due_frame, text="+1 Week", command=lambda: set_due(7)).pack(side="left", padx=2)

        # Description
        ttk.Label(frame, text="Description (Optional)", font=("Segoe UI", 10, "bold")).grid(row=6, column=0, sticky="w", pady=(0, 4))
        desc_text = tk.Text(frame, height=5, width=45, font=("Segoe UI", 10))
        desc_text.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 18))

        # Buttons
        btn_box = ttk.Frame(frame)
        btn_box.grid(row=8, column=0, columnspan=2, sticky="e")

        def handle_save() -> None:
            cat_name = category_combo.get()
            cat_id = self.category_id_map.get(cat_name)
            title = title_entry.get()
            desc = desc_text.get("1.0", "end")
            due = due_entry.get()

            ok, msg, _ = task_manager.add_task(
                user_id=self.current_user["id"],
                title=title,
                category_id=cat_id,
                description=desc,
                due_date=due,
            )
            if ok:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self.refresh_dashboard()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        ttk.Button(btn_box, text="Cancel", command=dialog.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(btn_box, text="Save Task", style="Primary.TButton", command=handle_save).pack(side="right")

        title_entry.focus_set()

    def open_edit_task_dialog(self) -> None:
        """Display modal dialog to edit the selected task."""
        task_id = self._get_selected_task_id()
        if task_id is None:
            return

        task = task_manager.get_task_by_id(self.current_user["id"], task_id)
        if not task:
            messagebox.showerror("Error", "The selected task could not be retrieved from the database.")
            return

        categories = category_manager.get_categories(self.current_user["id"])
        category_names = [cat["name"] for cat in categories]

        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Task #{task_id}")
        dialog.geometry("520x510")
        dialog.minsize(480, 460)
        dialog.transient(self)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(frame, text="Task Title *", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        title_entry = ttk.Entry(frame, width=45)
        title_entry.insert(0, task["title"])
        title_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Category
        ttk.Label(frame, text="Category *", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(0, 4))
        category_combo = ttk.Combobox(frame, values=category_names, state="readonly", width=30)
        category_combo.grid(row=3, column=0, sticky="w", pady=(0, 10))
        current_cat_name = self.category_name_map.get(task["category_id"], category_names[0])
        category_combo.set(current_cat_name)

        # Status
        ttk.Label(frame, text="Status *", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="w", pady=(0, 4))
        status_combo = ttk.Combobox(frame, values=["Pending", "Completed"], state="readonly", width=18)
        status_combo.grid(row=5, column=0, sticky="w", pady=(0, 10))
        status_combo.set(task["status"])

        # Due Date
        ttk.Label(frame, text="Due Date (Optional, YYYY-MM-DD)", font=("Segoe UI", 10, "bold")).grid(row=6, column=0, sticky="w", pady=(0, 4))
        due_frame = ttk.Frame(frame)
        due_frame.grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 10))
        due_entry = ttk.Entry(due_frame, width=18)
        if task["due_date"]:
            due_entry.insert(0, task["due_date"])
        due_entry.pack(side="left", padx=(0, 8))

        def set_due(days_offset: int) -> None:
            target = date.today() + timedelta(days=days_offset)
            due_entry.delete(0, "end")
            due_entry.insert(0, target.strftime(DATE_FORMAT))

        ttk.Button(due_frame, text="Today", command=lambda: set_due(0)).pack(side="left", padx=2)
        ttk.Button(due_frame, text="Tomorrow", command=lambda: set_due(1)).pack(side="left", padx=2)
        ttk.Button(due_frame, text="Clear", command=lambda: due_entry.delete(0, "end")).pack(side="left", padx=2)

        # Description
        ttk.Label(frame, text="Description (Optional)", font=("Segoe UI", 10, "bold")).grid(row=8, column=0, sticky="w", pady=(0, 4))
        desc_text = tk.Text(frame, height=4, width=45, font=("Segoe UI", 10))
        if task["description"]:
            desc_text.insert("1.0", task["description"])
        desc_text.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        # Buttons
        btn_box = ttk.Frame(frame)
        btn_box.grid(row=10, column=0, columnspan=2, sticky="e")

        def handle_save_changes() -> None:
            cat_name = category_combo.get()
            cat_id = self.category_id_map.get(cat_name)
            title = title_entry.get()
            desc = desc_text.get("1.0", "end")
            due = due_entry.get()
            stat = status_combo.get()

            ok, msg = task_manager.update_task(
                user_id=self.current_user["id"],
                task_id=task_id,
                title=title,
                category_id=cat_id,
                description=desc,
                due_date=due,
                status=stat,
            )
            if ok:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self.refresh_dashboard()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        ttk.Button(btn_box, text="Cancel", command=dialog.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(btn_box, text="Save Changes", style="Primary.TButton", command=handle_save_changes).pack(side="right")

    def handle_mark_completed(self) -> None:
        """Mark the selected task as completed."""
        task_id = self._get_selected_task_id()
        if task_id is None:
            return

        ok, msg = task_manager.mark_task_completed(self.current_user["id"], task_id)
        if ok:
            messagebox.showinfo("Task Completed", msg)
            self.refresh_dashboard()
        else:
            messagebox.showwarning("Notice", msg)

    def handle_delete_task(self) -> None:
        """Prompt confirmation and delete the selected task."""
        task_id = self._get_selected_task_id()
        if task_id is None:
            return

        task = task_manager.get_task_by_id(self.current_user["id"], task_id)
        if not task:
            messagebox.showerror("Error", "The task was not found or has already been deleted.")
            self.refresh_dashboard()
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete task #{task_id}?\n\nTitle: \"{task['title']}\"\n\nThis action cannot be undone.",
            icon="warning",
        )
        if not confirm:
            return

        ok, msg = task_manager.delete_task(self.current_user["id"], task_id)
        if ok:
            messagebox.showinfo("Deleted", msg)
            self.refresh_dashboard()
        else:
            messagebox.showerror("Delete Failed", msg)

    # =========================================================================
    # CATEGORY MANAGEMENT DIALOG
    # =========================================================================
    def open_category_manager(self) -> None:
        """Display dialog allowing user to view, create, and safely delete categories."""
        if not self.current_user:
            return

        user_id = self.current_user["id"]

        dialog = tk.Toplevel(self)
        dialog.title("Manage Categories")
        dialog.geometry("480x440")
        dialog.minsize(440, 400)
        dialog.transient(self)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=16)
        frame.pack(fill="both", expand=True)

        # Add New Category section
        add_frame = tk.LabelFrame(frame, text="Add New Category", font=("Segoe UI", 9, "bold"), padx=10, pady=8)
        add_frame.pack(fill="x", pady=(0, 12))

        cat_entry = ttk.Entry(add_frame, width=28)
        cat_entry.pack(side="left", padx=(0, 8))

        # Categories Table
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))

        cat_tree = ttk.Treeview(table_frame, columns=("id", "name", "count"), show="headings", selectmode="browse")
        cat_tree.heading("id", text="ID")
        cat_tree.heading("name", text="Category Name")
        cat_tree.heading("count", text="Assigned Tasks")
        cat_tree.column("id", width=50, anchor="center")
        cat_tree.column("name", width=220, anchor="w")
        cat_tree.column("count", width=120, anchor="center")

        cat_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=cat_tree.yview)
        cat_tree.configure(yscrollcommand=cat_scroll.set)
        cat_tree.pack(side="left", fill="both", expand=True)
        cat_scroll.pack(side="right", fill="y")

        def refresh_categories() -> None:
            for item in cat_tree.get_children():
                cat_tree.delete(item)
            cats = category_manager.get_categories(user_id)
            for c in cats:
                task_count = category_manager.get_category_task_count(user_id, c["id"])
                cat_tree.insert("", "end", values=(c["id"], c["name"], task_count))

        def handle_add_category() -> None:
            name = cat_entry.get()
            ok, msg, _ = category_manager.create_category(user_id, name)
            if ok:
                cat_entry.delete(0, "end")
                refresh_categories()
                self.refresh_dashboard()
                messagebox.showinfo("Category Created", msg, parent=dialog)
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        ttk.Button(add_frame, text="Add Category", style="Primary.TButton", command=handle_add_category).pack(side="left")
        cat_entry.bind("<Return>", lambda _: handle_add_category())

        # Category Actions
        cat_actions = ttk.Frame(frame)
        cat_actions.pack(fill="x")

        def handle_delete_category() -> None:
            selected = cat_tree.selection()
            if not selected:
                messagebox.showwarning("Select Category", "Please select a category to delete.", parent=dialog)
                return

            cat_id = int(cat_tree.item(selected[0], "values")[0])
            cat_name = cat_tree.item(selected[0], "values")[1]
            task_count = int(cat_tree.item(selected[0], "values")[2])

            if task_count > 0:
                messagebox.showwarning(
                    "Cannot Delete Category",
                    f"Category '{cat_name}' is currently assigned to {task_count} task(s).\n\n"
                    f"To protect data integrity, please delete or reassign those tasks before deleting this category.",
                    parent=dialog,
                )
                return

            if not messagebox.askyesno("Confirm Delete", f"Delete category '{cat_name}'?", parent=dialog):
                return

            ok, msg = category_manager.delete_category(user_id, cat_id)
            if ok:
                refresh_categories()
                self.refresh_dashboard()
                messagebox.showinfo("Deleted", msg, parent=dialog)
            else:
                messagebox.showerror("Delete Error", msg, parent=dialog)

        ttk.Button(cat_actions, text="🗑 Delete Selected", style="Danger.TButton", command=handle_delete_category).pack(side="left")
        ttk.Button(cat_actions, text="Close", command=dialog.destroy).pack(side="right")

        refresh_categories()
        cat_entry.focus_set()
