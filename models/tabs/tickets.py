from typing import Optional
from models.users import User

# -----------------------------------------------------------------------------
# Seed data (private to this module)
# -----------------------------------------------------------------------------
DEFAULT_TICKETS = [
    {"subject": "Cannot log in to portal", "from_name": "Taylor", "priority": "High",   "email": "taylor@example.com"},
    {"subject": "Email not syncing",       "from_name": "Chris",  "priority": "Normal", "email": "chris@example.com"},
    {"subject": "Request new mouse",       "from_name": "Priya",  "priority": "Low",    "email": "priya@example.com"},
    {"subject": "VPN not connecting",      "from_name": "Jordan", "priority": "High",   "email": "jordan@example.com"},
    {"subject": "Slow laptop performance", "from_name": "Morgan", "priority": "Normal", "email": "morgan@example.com"},
]

# -----------------------------------------------------------------------------
# Model
# -----------------------------------------------------------------------------
class Ticket:
    """Simple ticket record with minimal fields and internal notes."""

    def __init__(
        self,
        ticket_id: int,
        subject: str,
        from_name: str,
        priority: str = "Normal",
        status: str = "Open",
        assigned_to: Optional[str] = None,
        # optional fields with defaults
        department: str = "Support",
        sla_plan: str = "Standard",
        help_topic: str = "General Inquiry",
        printing: bool = False,
        email: Optional[str] = None,
    ):
        # core
        self.id = ticket_id
        self.subject = subject
        self.from_name = from_name
        self.priority = priority
        self.status = status
        self.assigned_to = assigned_to

        # additional metadata
        self.department = department
        self.sla_plan = sla_plan
        self.help_topic = help_topic
        self.printing = printing
        self.email = email

        # notes: [{"by": <str>, "text": <str>}]
        self.internal_notes = []

    def __repr__(self):
        return "<Ticket {}: {} [{}]>".format(self.id, self.subject, self.status)


# -----------------------------------------------------------------------------
# Manager
# -----------------------------------------------------------------------------
class TicketManager:
    """
    Owns the collection of tickets and exposes:
      - Core helpers (create, lookup, stats)
      - Tickets tab UI (agent workflow)
      - Client submission UI (public form)
    """

    # -------------------------------------------------------------------------
    # Construction & Core Helpers
    # -------------------------------------------------------------------------
    def __init__(self, user_store=None):
        self.user_store = user_store              # reference so we can assign/escalate
        self.tickets = {}                         # {id: Ticket}

        # Seed initial tickets
        for i, d in enumerate(DEFAULT_TICKETS, start=1):
            self.tickets[i] = Ticket(ticket_id=i, status="Open", **d)

        # Stats for dashboard
        self.totals_created = len(self.tickets)
        self.totals_resolved = 0
        self.totals_deleted = 0  # maintained if you add deletion later

        # Next ID after seeding
        self._next_id = (max(self.tickets.keys()) + 1) if self.tickets else 1

    def _next_ticket_id(self) -> int:
        """Return the next incremental ticket id and advance the counter."""
        nid = self._next_id
        self._next_id += 1
        return nid

    def create_ticket(
        self,
        subject: str,
        from_name: str,
        priority: str = "Normal",
        email: Optional[str] = None,
        department: str = "Support",
        sla_plan: str = "Standard",
        help_topic: str = "General Inquiry",
        printing: bool = False,
    ) -> Ticket:
        """
        Programmatic creation (used by client form and tests).
        Returns the created Ticket.
        """
        tid = self._next_ticket_id()
        t = Ticket(
            ticket_id=tid,
            subject=subject,
            from_name=from_name,
            priority=priority,
            status="Open",
            assigned_to=None,
            department=department,
            sla_plan=sla_plan,
            help_topic=help_topic,
            printing=printing,
            email=email,
        )
        self.tickets[tid] = t
        self.totals_created += 1
        return t

    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        """Lookup a ticket by id or return None."""
        return self.tickets.get(ticket_id)

    def print_stats(self):
        """Small stats dump used by the Dashboard."""
        print("==== Ticket Stats (Totals) ====")
        print(f"Created:  {self.totals_created}")
        print(f"Resolved: {self.totals_resolved}")
        print(f"Deleted:  {self.totals_deleted}")
        print("===============================")

    # -------------------------------------------------------------------------
    # Tickets Tab UI (agent workflow)
    # -------------------------------------------------------------------------
    def run_ui(self, current_user: User):
        """Entry point for the Tickets tab loop."""
        print(f"\n=== {current_user.name} is now in the Tickets Tab ===\n")
        running = True
        while running:
            self._print_ticket_list()

            print("\nActions:")
            print("1) Claim a ticket")
            print("2) See my tickets")
            print("3) Access / work on a ticket")
            print("0) Back to tabs\n")

            choice = input("Enter a number: ").strip()
            if choice == "0":
                print("\nReturning to tabs...\n")
                running = False
            elif choice == "1":
                self._claim_ticket_ui(current_user)
            elif choice == "2":
                self._show_my_tickets(current_user)
            elif choice == "3":
                self._access_ticket_ui(current_user)
            else:
                print("\n❌ Invalid option. Try again.\n")

    def _print_ticket_list(self):
        """Render the current (open) tickets table."""
        if not self.tickets:
            print("(no tickets)")
            return

        print(f"{'ID':<4} {'Subject':<38} {'From':<12} {'Priority':<8} {'Status':<12} {'Assigned To':<15}")
        print("-" * 100)
        for t in self.tickets.values():
            assigned = t.assigned_to if t.assigned_to else "Unassigned"
            print(f"{t.id:<4} {t.subject[:28]:<38} {t.from_name:<12} {t.priority:<8} {t.status:<12} {assigned:<15}")

    def _claim_ticket_ui(self, user: User):
        """Claim a ticket: assigns it to the current agent and records on the User."""
        print(f"\nClaim Ticket (as {user.name})")
        ticket_id = input("Enter the ID of the ticket you want to claim (or 0 to cancel): ").strip()

        if ticket_id == "0":
            print("Cancelled claiming.\n")
            return
        if not ticket_id.isdigit():
            print("❌ Invalid input. Please enter a number.\n")
            return

        tid = int(ticket_id)
        ticket = self.get_ticket(tid)
        if ticket is None:
            print("❌ Ticket not found.\n")
            return

        # Update both sides: ticket + user
        ticket.assigned_to = user.name
        user.claim_ticket(ticket)

        print(f"✅ Ticket {tid} ('{ticket.subject}') is now assigned to {user.name}.\n")

    def _show_my_tickets(self, user: User):
        """Submenu that lists tickets claimed by the given user, with a quick access flow."""
        claimed_ids = user.tickets_claimed

        while True:
            print("\n=== My Tickets (for {}) ===".format(user.name))
            if not claimed_ids:
                print("(You have not claimed any tickets yet.)\n")
                return

            # Header
            print("{:<4} {:<30} {:<12} {:<8} {:<12} {:<15}".format(
                "ID", "Subject", "From", "Priority", "Status", "Assigned To"))
            print("-" * 90)

            for tid in claimed_ids:
                t = self.get_ticket(tid)
                if not t:
                    continue
                assigned = t.assigned_to if t.assigned_to else "Unassigned"
                print("{:<4} {:<30} {:<12} {:<8} {:<12} {:<15}".format(
                    t.id, t.subject[:28], t.from_name, t.priority, t.status, assigned))
            print("")

            # Submenu actions
            print("Actions:")
            print("1) Access / work on a ticket")
            print("0) Back to all tickets\n")

            choice = input("Enter a number: ").strip()
            if choice == "0":
                return
            elif choice == "1":
                self._access_ticket_ui(user)
            else:
                print("\n❌ Invalid option. Try again.\n")

    def _access_ticket_ui(self, user: User):
        """Open a specific ticket by id and provide per-ticket actions."""
        ticket_id = input("Enter the ID of the ticket to access (or 0 to cancel): ").strip()
        if ticket_id == "0":
            print("Cancelled.\n")
            return
        if not ticket_id.isdigit():
            print("❌ Invalid input. Please enter a number.\n")
            return

        tid = int(ticket_id)
        t = self.get_ticket(tid)
        if not t:
            print("❌ Ticket not found.\n")
            return

        while True:
            self._print_ticket_details(t)
            print("Actions:")
            print("1) Internal notes (view/add)")
            print("2) Update status (Open/Resolved)")
            print("3) Assign/Escalate to another agent")
            print("0) Back\n")

            choice = input("Enter a number: ").strip()
            if choice == "0":
                return
            elif choice == "1":
                self._internal_notes_ui(t, user)
            elif choice == "2":
                self._update_status_ui(t, user)
                # If resolved, the ticket is removed from the dict; bounce back.
                if self.get_ticket(t.id) is None:
                    return
            elif choice == "3":
                self._assign_ticket_ui(t, user)
            else:
                print("\n❌ Invalid option. Try again.\n")

    def _print_ticket_details(self, t: Ticket):
        """Pretty-print ticket fields and metadata."""
        print("\n=== Ticket {} — {} ===".format(t.id, t.subject))
        print("Status:      {}".format(t.status))
        print("Priority:    {}".format(t.priority))
        print("Department:  {}".format(t.department))
        print("Assigned To: {}".format(t.assigned_to if t.assigned_to else "Unassigned"))
        print("SLA Plan:    {}".format(t.sla_plan))
        print("Help Topic:  {}".format(t.help_topic))
        print("Printing:    {}".format("Enabled" if t.printing else "Disabled"))
        print("Email:       {}".format(t.email if t.email else "(unknown)"))
        print("")

    def _internal_notes_ui(self, t: Ticket, user: User):
        """View and append internal notes for the given ticket."""
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

    def _update_status_ui(self, t: Ticket, user: User):
        """Toggle status between Open and Resolved. Resolved tickets are removed."""
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
            if t.id in self.tickets:
                del self.tickets[t.id]
            self.totals_resolved += 1
            # best-effort: remove from current user's claimed list if present
            try:
                user.unclaim_ticket(t.id)
            except Exception:
                pass
            print("✅ Ticket {} resolved and removed.\n".format(t.id))
        else:
            print("❌ Invalid option.\n")

    def _assign_ticket_ui(self, t: Ticket, current_user: User):
        """
        Assign/Escalate a ticket to another active user (Agent or Admin).
        Excludes the current user from the candidate list.
        """
        # Must have a user store to list candidates
        if not hasattr(self, "user_store") or self.user_store is None:
            print("❌ Cannot assign: user store not available.\n")
            return

        # 1) Build candidate list: ALL ACTIVE USERS (Agents + Admins)
        all_users = self.user_store.list_users()
        candidates = []
        for u in all_users:
            if isinstance(u.status, str) and u.status.lower() == "active":
                candidates.append(u)

        # Exclude the current user (so you can't assign to yourself)
        display = []
        for u in candidates:
            if current_user is None or u.id != current_user.id:
                display.append(u)

        # Fallback: if we somehow filtered out everyone, show candidates anyway
        if not display:
            display = candidates[:]

        if not display:
            print("❌ No eligible users found.\n")
            return

        # 2) Show the table (note the header says USER ID)
        print("\n--- Assign/Escalate Ticket {} ---".format(t.id))
        print("{:<4} {:<20} {:<8} {:<8}".format("ID", "Name", "Role", "Status"))
        print("-" * 48)
        for u in display:
            print("{:<4} {:<20} {:<8} {:<8}".format(u.id, u.name, u.role, u.status))
        print("-" * 48)

        # 3) Prompt for USER ID (NOT menu index)
        s = input("Enter USER ID to assign to (or 0 to cancel): ").strip()
        if s == "0":
            print("Cancelled.\n")
            return
        if not s.isdigit():
            print("❌ Invalid input. Please enter a number.\n")
            return

        target_id = int(s)

        # Ensure the chosen ID is actually in our displayed list
        target = None
        for u in display:
            if u.id == target_id:
                target = u
                break

        if target is None:
            print("❌ That USER ID was not in the list above.\n")
            return

        # 4) Do the reassignment: unclaim from all, then assign to target
        for u in self.user_store.list_users():
            try:
                u.unclaim_ticket(t.id)
            except Exception:
                pass

        t.assigned_to = target.name
        target.claim_ticket(t)

        print("✅ Ticket {} assigned to {}.\n".format(t.id, target.name))

    # -------------------------------------------------------------------------
    # Client Submission UI (public form)
    # -------------------------------------------------------------------------
    def submit_ticket_ui(self):
        """
        Simple terminal form for an end-user to submit a ticket.
        No login required; adds an Open ticket to the queue.
        """
        print("\n" + "=" * 60)
        print("   Submit a Ticket (enter 0 at any prompt to cancel)")
        print("=" * 60 + "\n")

        # Subject
        subject = input("Subject: ").strip()
        if subject == "0":
            print("\nCancelled.\n")
            return
        if not subject:
            print("\n❌ Subject is required.\n")
            return

        # Requester name
        from_name = input("\nYour Name: ").strip()
        if from_name == "0":
            print("\nCancelled.\n")
            return
        if not from_name:
            from_name = "Guest"

        # Email (optional)
        email = input("\nEmail (optional): ").strip()
        if email == "0":
            print("\nCancelled.\n")
            return
        if not email:
            email = None

        # Priority
        print("\nPriority options:")
        print("  1) High")
        print("  2) Normal")
        print("  3) Low")
        p = input("Choose priority (1/2/3, default 2): ").strip()
        if p == "0":
            print("\nCancelled.\n")
            return
        priority_map = {"1": "High", "2": "Normal", "3": "Low"}
        priority = priority_map.get(p, "Normal")

        # Department
        department = input("\nDepartment (e.g., Support, IT, HR): ").strip()
        if department == "0":
            print("\nCancelled.\n")
            return
        if not department:
            department = "Support"

        # Help topic
        help_topic = input("\nHelp Topic (e.g., Login Issue, Hardware Request): ").strip()
        if help_topic == "0":
            print("\nCancelled.\n")
            return
        if not help_topic:
            help_topic = "General Inquiry"

        # SLA Plan
        print("\nSLA options:")
        print("  1) Standard")
        print("  2) Expedited")
        s = input("Choose SLA plan (1/2, default 1): ").strip()
        if s == "0":
            print("\nCancelled.\n")
            return
        sla_map = {"1": "Standard", "2": "Expedited"}
        sla_plan = sla_map.get(s, "Standard")

        printing = False  # kept hidden for now

        # Create
        t = self.create_ticket(
            subject=subject,
            from_name=from_name,
            priority=priority,
            email=email,
            department=department,
            sla_plan=sla_plan,
            help_topic=help_topic,
            printing=printing,
        )

        # Receipt
        print("\n" + "-" * 60)
        print(f"✅ Ticket {t.id} submitted by {from_name} ({email or 'no email'}).")
        print("   Subject:    ", t.subject)
        print("   Priority:   ", t.priority)
        print("   Department: ", department)
        print("   Help Topic: ", help_topic)
        print("   SLA Plan:   ", sla_plan)
        print("-" * 60 + "\n")

        input("Press Enter to return...")
