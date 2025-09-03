
"""
THIS FILE DOES NOT WORK
TODO: Refractor this to work with the new app.py structure.
and import the User class to all the necessary places.
"""


# models/tickets.py
from typing import Dict, List, Optional

# --- Seed data kept private to this module ---
DEFAULT_TICKETS: List[dict] = [
    {"subject": "Cannot log in to portal", "from_name": "Taylor", "priority": "High"},
    {"subject": "Email not syncing",       "from_name": "Chris",  "priority": "Normal"},
    {"subject": "Request new mouse",       "from_name": "Priya",  "priority": "Low"},
    {"subject": "VPN not connecting",      "from_name": "Jordan", "priority": "High"},
    {"subject": "Slow laptop performance", "from_name": "Morgan", "priority": "Normal"},
]


class Ticket:
    def __init__(
        self,
        ticket_id: int,
        subject: str,
        from_name: str,
        priority: str = "Normal",
        status: str = "Open",
        assigned_to: Optional[str] = None,
    ):
        self.id = ticket_id
        self.subject = subject
        self.from_name = from_name
        self.priority = priority
        self.status = status
        self.assigned_to = assigned_to

    def __repr__(self):
        return f"<Ticket {self.id}: {self.subject} [{self.status}]>"



class TicketManager:
    def __init__(self):
        self.tickets: Dict[int, Ticket] = {}

        # Seed from local defaults automatically (no args needed)
        for i, d in enumerate(DEFAULT_TICKETS, start=1):
            self.tickets[i] = Ticket(ticket_id=i, status="Open", **d)

        # simple totals for dashboard
        self.totals_created = len(self.tickets)
        self.totals_resolved = 0
        self.totals_deleted = 0

    # ----------------- basic helper -----------------
    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        return self.tickets.get(ticket_id)

    # ----------------- stats -----------------
    def print_stats(self):
        print("==== Ticket Stats (Totals) ====")
        print(f"Created:  {self.totals_created}")
        print(f"Resolved: {self.totals_resolved}")
        print(f"Deleted:  {self.totals_deleted}")
        print("===============================")

    # ----------------- Tickets Tab UI -----------------
    def run_ui(self, current_user: User):
        print("\n=== You are now in the Tickets Tab ===\n")
        running = True
        while running:
            # list tickets first
            self._print_ticket_list()

            # then show actions
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
            elif choice in {"2", "3"}:
                print(f"\nYou selected option {choice}. (Not implemented yet)\n")
            else:
                print("\nInvalid option. Try again.\n")

    def _print_ticket_list(self):
        if not self.tickets:
            print("(no tickets)")
            return

        print(f"{'ID':<4} {'Subject':<30} {'From':<12} {'Priority':<8} {'Status':<12} {'Assigned To':<15}")
        print("-" * 90)
        for t in self.tickets.values():
            assigned = t.assigned_to if t.assigned_to else "Unassigned"
            print(f"{t.id:<4} {t.subject[:28]:<30} {t.from_name:<12} {t.priority:<8} {t.status:<12} {assigned:<15}")

    # -------- Claim Ticket UI (updates user + ticket) --------
    def _claim_ticket_ui(self, user: User):
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
        user.add_ticket(ticket)

        print(f"✅ Ticket {tid} ('{ticket.subject}') is now assigned to {user.name}.\n")


# --- quick test (optional) ---
if __name__ == "__main__":
    tm = TicketManager()
    tm.print_stats()

    dummy = User(user_id=1, name="Dummy User", email="dummy@example.com")
    tm.run_ui(dummy)

    if dummy.tickets_claimed:
        print("Tickets claimed by user:")
        for t in dummy.tickets_claimed:
            print(" -", t)
