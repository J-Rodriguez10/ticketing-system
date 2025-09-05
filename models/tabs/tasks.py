# -----------------------------------------------------------------------------
# Seed data (private to this module)
# -----------------------------------------------------------------------------
DEFAULT_TASKS = [
    # Minimal starter tasks; ticket_id can be None
    {"ticket_id": 1, "title": "Verify portal login fix","department": "Support", "description": "Confirm user can log in"},
    {"ticket_id": 2, "title": "Check mailbox sync", "department": "Support", "description": "Validate mail flow"},
    {"ticket_id": 3, "title": "Order new mouse","department": "IT Ops",  "description": "Procure a mouse for Priya"},
]

# -----------------------------------------------------------------------------
# Model
# -----------------------------------------------------------------------------
class Task:
    """Simple internal task with optional link to a ticket."""

    def __init__(self, task_id, title, department="Support",
                 status="Open", assigned_to=None, ticket_id=None, description=""):
        self.id = task_id
        self.title = title
        self.department = department
        # "Open" | "Resolved"
        self.status = status       
        self.assigned_to = assigned_to
        # optional link back to a ticket
        self.ticket_id = ticket_id
        self.description = description

        # list of {"by": name, "text": str}
        self.internal_notes = []    

    def __repr__(self):
        return "<Task {}: {} [{}]>".format(self.id, self.title, self.status)


# -----------------------------------------------------------------------------
# Manager
# -----------------------------------------------------------------------------
class TaskManager:
    """
    Owns the collection of tasks and exposes:
      - Core helpers (lookup, id generation, stats)
      - Tasks tab UI (agent workflow)
    """

    # -------------------------------------------------------------------------
    # Construction & Core Helpers
    # -------------------------------------------------------------------------
    def __init__(self, user_store=None):
        self.user_store = user_store
        self.tasks = {}

        # Seed defaults
        for i, d in enumerate(DEFAULT_TASKS, start=1):
            self.tasks[i] = Task(
                task_id=i,
                title=d.get("title", "Untitled Task"),
                department=d.get("department", "Support"),
                status="Open",
                assigned_to=d.get("assigned_to"),
                ticket_id=d.get("ticket_id"),
                description=d.get("description", ""),
            )

        # Stats (for dashboard)
        self.totals_created = len(self.tasks)
        self.totals_resolved = 0
        self.totals_deleted = 0

    def get_task(self, task_id):
        """Lookup a task by id or return None."""
        return self.tasks.get(task_id)

    def _next_id(self):
        """Return the next incremental task id (computed from current keys)."""
        return (max(self.tasks.keys()) + 1) if self.tasks else 1

    # -------------------------------------------------------------------------
    # List Rendering
    # -------------------------------------------------------------------------
    def _print_task_list(self):
        """Render the current (open) tasks table."""
        if not self.tasks:
            print("(no tasks)")
            return

        print("{:<4} {:<8} {:<30} {:<14} {:<12} {:<15}".format(
            "ID", "Ticket", "Title", "Department", "Status", "Assigned To"))
        print("-" * 100)
        for t in self.tasks.values():
            ticket_str = str(t.ticket_id) if t.ticket_id is not None else "-"
            assigned = t.assigned_to if t.assigned_to else "Unassigned"
            print("{:<4} {:<8} {:<30} {:<14} {:<12} {:<15}".format(
                t.id, ticket_str, t.title[:28], t.department, t.status, assigned))

    # -------------------------------------------------------------------------
    # Tasks Tab UI (agent workflow)
    # -------------------------------------------------------------------------
    def run_ui(self, current_user):
        """Entry point for the Tasks tab loop."""
        print(f"\n=== {getattr(current_user, 'name', 'You')} is now in the Tasks Tab ===\n")
        running = True
        while running:
            self._print_task_list()

            print("\nActions:")
            print("1) Claim a task")
            print("2) See my tasks")
            print("3) Access / work on a task")
            print("4) Create a task")
            print("0) Back to tabs\n")

            choice = input("Enter a number: ").strip()
            if choice == "0":
                print("\nReturning to tabs...\n")
                running = False
            elif choice == "1":
                self._claim_task_ui(current_user)
            elif choice == "2":
                self._show_my_tasks(current_user)
            elif choice == "3":
                self._access_task_ui(current_user)
            elif choice == "4":
                self._create_task_ui(current_user)
            else:
                print("\n❌ Invalid option. Try again.\n")

    # -------------------------------------------------------------------------
    # Actions: Claim / My Tasks / Access
    # -------------------------------------------------------------------------
    def _claim_task_ui(self, user):
        """Claim a task: assigns it to the current agent and records on the User."""
        print("\nClaim Task (as {})".format(user.name))
        task_id = input("Enter the ID of the task you want to claim (or 0 to cancel): ").strip()

        if task_id == "0":
            print("Cancelled claiming.\n")
            return

        if not task_id.isdigit():
            print("❌ Invalid input. Please enter a number.\n")
            return

        tid = int(task_id)
        task = self.get_task(tid)
        if task is None:
            print("❌ Task not found.\n")
            return

        # Update both sides
        task.assigned_to = user.name
        user.claim_task(task)

        print("✅ Task {} ('{}') is now assigned to {}.\n".format(tid, task.title, user.name))

    def _show_my_tasks(self, user):
        """Submenu that lists tasks claimed by the given user, with a quick access flow."""
        while True:
            claimed_ids = user.tasks_claimed
            print("\n=== My Tasks (for {}) ===".format(user.name))
            if not claimed_ids:
                print("(You have not claimed any tasks yet.)\n")
                return

            print("{:<4} {:<8} {:<30} {:<14} {:<12} {:<15}".format(
                "ID", "Ticket", "Title", "Department", "Status", "Assigned To"))
            print("-" * 100)
            for tid in claimed_ids:
                t = self.get_task(tid)
                if not t:
                    continue
                ticket_str = str(t.ticket_id) if t.ticket_id is not None else "-"
                assigned = t.assigned_to if t.assigned_to else "Unassigned"
                print("{:<4} {:<8} {:<30} {:<14} {:<12} {:<15}".format(
                    t.id, ticket_str, t.title[:28], t.department, t.status, assigned))
            print("")

            print("Actions:")
            print("1) Access / work on a task")
            print("0) Back to all tasks\n")

            choice = input("Enter a number: ").strip()
            if choice == "0":
                return
            elif choice == "1":
                self._access_task_ui(user)
            else:
                print("\n❌ Invalid option. Try again.\n")

    def _access_task_ui(self, user):
        """Open a specific task by id and provide per-task actions."""
        task_id = input("Enter the ID of the task to access (or 0 to cancel): ").strip()
        if task_id == "0":
            print("Cancelled.\n")
            return
        if not task_id.isdigit():
            print("❌ Invalid input. Please enter a number.\n")
            return

        tid = int(task_id)
        t = self.get_task(tid)
        if not t:
            print("❌ Task not found.\n")
            return

        while True:
            self._print_task_details(t)
            print("Actions:")
            print("1) Internal notes (view/add)")
            print("2) Update status (Open/Resolved)")
            print("0) Back\n")

            choice = input("Enter a number: ").strip()
            if choice == "0":
                return
            elif choice == "1":
                self._internal_notes_ui(t, user)
            elif choice == "2":
                self._update_status_ui(t, user)
                # If resolved, the task is removed from the dict; bounce back.
                if self.get_task(t.id) is None:
                    return
            else:
                print("\n❌ Invalid option. Try again.\n")

    # -------------------------------------------------------------------------
    # Rendering & Notes
    # -------------------------------------------------------------------------
    def _print_task_details(self, t):
        """Pretty-print task fields and metadata."""
        print("\n=== Task {} — {} ===".format(t.id, t.title))
        print("Status:        {}".format(t.status))
        print("Department:    {}".format(t.department))
        print("Assigned To:   {}".format(t.assigned_to if t.assigned_to else "Unassigned"))
        print("Linked Ticket: {}".format(t.ticket_id if t.ticket_id is not None else "-"))
        print("Description:   {}".format(t.description if t.description else "(none)"))
        print("")

    def _internal_notes_ui(self, t, user):
        """View and append internal notes for the given task."""
        print("\n--- Internal Notes ---")
        if not t.internal_notes:
            print("(no internal notes yet)")
        else:
            for i, n in enumerate(t.internal_notes, start=1):
                print("{}: [{}] {}".format(i, n.get("by", "Unknown"), n.get("text", "")))
        print("")
        add = input("Add a new note? (y/n): ").strip().lower()
        if add == "y":
            text = input("Note text (blank to cancel): ").strip()
            if text:
                t.internal_notes.append({"by": user.name, "text": text})
                print("✅ Note added.\n")
            else:
                print("Cancelled.\n")

    # -------------------------------------------------------------------------
    # Status Updates
    # -------------------------------------------------------------------------
    # ChatGPT was used to write this function and debug it.
    def _update_status_ui(self, t, user):
        """Toggle status between Open and Resolved. Resolved tasks are removed."""
        print("\n--- Update Status ---")
        print("Current status:", t.status)
        print("1) Open")
        print("2) Resolved")
        choice = input("Choose status (1/2) or 0 to cancel: ").strip()

        if choice == "0":
            print("Cancelled.\n")
            return
        elif choice == "1":
            t.status = "Open"
            print("✅ Status set to Open.\n")
        elif choice == "2":
            t.status = "Resolved"
            # remove from store so it disappears from lists
            if t.id in self.tasks:
                del self.tasks[t.id]
            self.totals_resolved += 1
            # best-effort: remove from current user's claimed list if present
            try:
                user.unclaim_task(t.id)
            except Exception:
                pass
            print("✅ Task {} resolved and removed.\n".format(t.id))
        else:
            print("❌ Invalid option.\n")

    # -------------------------------------------------------------------------
    # Creation
    # -------------------------------------------------------------------------
    def _create_task_ui(self, user):
        """Interactive form to create a new task (optionally assigning to a user)."""
        print("\n=== Create a Task (enter 0 at any prompt to cancel) ===")

        # Title
        title = input("Title: ").strip()
        if title == "0":
            print("Cancelled.\n")
            return
        if not title:
            print("❌ Title is required.\n")
            return

        # Description
        print("")
        description = input("Description (optional): ").strip()
        if description == "0":
            print("Cancelled.\n")
            return

        # Department
        print("")
        department = input("Department (e.g., Support, IT Ops): ").strip()
        if department == "0":
            print("Cancelled.\n")
            return
        if not department:
            department = "Support"

        # Linked Ticket ID (optional)
        print("")
        ticket_input = input("Linked Ticket ID (blank for none): ").strip()
        if ticket_input == "0":
            print("Cancelled.\n")
            return
        ticket_id = None
        if ticket_input:
            if ticket_input.isdigit():
                ticket_id = int(ticket_input)
            else:
                print("❌ Invalid ticket id; leaving blank.")
                ticket_id = None

        # Optional Assignee (by USER ID) — show active users if we can
        assignee_name = None
        if self.user_store:
            users = [u for u in self.user_store.list_users()
                     if isinstance(u.status, str) and u.status.lower() == "active"]
            if users:
                print("\nActive users:")
                print("{:<4} {:<20} {:<8} {:<8}".format("ID", "Name", "Role", "Status"))
                print("-" * 48)
                for u in users:
                    print("{:<4} {:<20} {:<8} {:<8}".format(u.id, u.name, u.role, u.status))
                print("-" * 48)
                s = input("Assign to USER ID (blank for none): ").strip()
                if s == "0":
                    print("Cancelled.\n")
                    return
                if s:
                    if s.isdigit():
                        target = self.user_store.get_by_id(int(s))
                        if target and isinstance(target.status, str) and target.status.lower() == "active":
                            assignee_name = target.name
                        else:
                            print("❌ Invalid or inactive user id; leaving unassigned.")
                    else:
                        print("❌ Invalid input; leaving unassigned.")

        # Create the task
        new_id = self._next_id()
        t = Task(
            task_id=new_id,
            title=title,
            department=department,
            status="Open",
            assigned_to=assignee_name,
            ticket_id=ticket_id,
            description=description,
        )
        self.tasks[new_id] = t
        self.totals_created += 1

        # If assigned to someone, add to their claimed list
        if assignee_name and self.user_store:
            for u in self.user_store.list_users():
                if u.name == assignee_name:
                    try:
                        u.claim_task(t)
                    except Exception:
                        pass
                    break

        print("✅ Task {} ('{}') created{}.\n".format(
            new_id, title, " and assigned to {}".format(assignee_name) if assignee_name else ""))
