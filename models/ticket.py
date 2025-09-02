# ===============================
# Ticket model
# ===============================
class Ticket:
    def __init__(self, ticket_id, title, description, priority="Normal", status="Open"):
        self.id = ticket_id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status

    def __repr__(self):
        return f"<Ticket {self.id}: {self.title} ({self.status})>"


# ===============================
# Default tickets (constant)
# ===============================
DEFAULT_TICKETS = [
    {
        "id": 1,
        "title": "Cannot log in to portal",
        "description": "User reports invalid credentials error on login.",
        "priority": "High",
        "status": "Open",
    },
    {
        "id": 2,
        "title": "Email not syncing",
        "description": "Outlook inbox not updating since yesterday.",
        "priority": "Normal",
        "status": "Open",
    },
    {
        "id": 3,
        "title": "Request new mouse",
        "description": "Old mouse double-clicks unexpectedly.",
        "priority": "Low",
        "status": "In Progress",
    },
    {
        "id": 4,
        "title": "VPN not connecting",
        "description": "Remote worker cannot connect to VPN.",
        "priority": "High",
        "status": "Open",
    },
    {
        "id": 5,
        "title": "Slow laptop performance",
        "description": "Laptop takes 15 minutes to boot up.",
        "priority": "Normal",
        "status": "Open",
    },
]


# ===============================
# Ticket manager (with defaults)
# ===============================
class TicketManager:
    def __init__(self):
        self.tickets = {}
        self.next_id = 1
        self._load_defaults()

    def _load_defaults(self):
        for data in DEFAULT_TICKETS:
            ticket = Ticket(
                data["id"],
                data["title"],
                data["description"],
                data["priority"],
                data["status"],
            )
            self.tickets[ticket.id] = ticket
        if self.tickets:
            self.next_id = max(self.tickets.keys()) + 1

    # -------------------------------
    # CRUD operations
    # -------------------------------
    def create_ticket(self, title, description, priority="Normal"):
        ticket = Ticket(self.next_id, title, description, priority)
        self.tickets[self.next_id] = ticket
        self.next_id += 1
        return ticket

    def get_ticket(self, ticket_id):
        return self.tickets.get(ticket_id)

    def update_ticket(self, ticket_id, title=None, description=None, priority=None, status=None):
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return None
        if title is not None:
            ticket.title = title
        if description is not None:
            ticket.description = description
        if priority is not None:
            ticket.priority = priority
        if status is not None:
            ticket.status = status
        return ticket

    def delete_ticket(self, ticket_id):
        return self.tickets.pop(ticket_id, None)

    def list_tickets(self):
        return list(self.tickets.values())


# Demo run
if __name__ == "__main__":
    tm = TicketManager()
    print("Loaded tickets:")
    for t in tm.list_tickets():
        print(" ", t)

    print("\nCreating new ticket...")
    new_ticket = tm.create_ticket("Test Feature", "This is a new test ticket.")
    print("Created:", new_ticket)

    print("\nAll tickets now:")
    for t in tm.list_tickets():
        print(" ", t)
