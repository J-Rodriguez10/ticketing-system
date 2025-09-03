# models/users.py

class User:
    def __init__(self, user_id, name, role="Agent", status="Active"):
        self.id = user_id
        self.name = name
        self.role = role # "Agent" or "Admin"
        self.status = status # "Active" or "Inactive"

        # basic tracking (store ids for simplicity)
        self.tickets_claimed = []
        self.tasks_claimed = []

    # ---------- ticket helpers ----------
    def claim_ticket(self, ticket):
        """Accepts a ticket id or a ticket object with .id; avoids duplicates."""
        tid = ticket.id if hasattr(ticket, "id") else ticket
        if tid not in self.tickets_claimed:
            self.tickets_claimed.append(tid)
            return True
        return False

    def unclaim_ticket(self, ticket):
        """Remove a ticket id (or object) if present."""
        tid = ticket.id if hasattr(ticket, "id") else ticket
        if tid in self.tickets_claimed:
            self.tickets_claimed.remove(tid)
            return True
        return False

    # ---------- task helpers ----------
    def claim_task(self, task):
        """Accepts a task id or a task object with .id; avoids duplicates."""
        task_id = task.id if hasattr(task, "id") else task
        if task_id not in self.tasks_claimed:
            self.tasks_claimed.append(task_id)
            return True
        return False

    def unclaim_task(self, task):
        """Remove a task id (or object) if present."""
        task_id = task.id if hasattr(task, "id") else task
        if task_id in self.tasks_claimed:
            self.tasks_claimed.remove(task_id)
            return True
        return False

    def __repr__(self):
        return "<User {}: {} ({})>".format(self.id, self.name, self.role)


class UserStore:
    """Manages the list of all users in the system."""

    def __init__(self, seed_users=None):
        if seed_users:
            self.users = seed_users[:]
        else:
            self.users = []
        self._next_id = (max([u.id for u in self.users]) + 1) if self.users else 1

    def add_user(self, name, role="Agent", status="Active"):
        user = User(self._next_id, name, role, status)
        self.users.append(user)
        self._next_id += 1
        return user

    def list_users(self):
        return self.users

    def list_agents_first(self):
        agents = [u for u in self.users if u.role.lower() == "agent"]
        admins = [u for u in self.users if u.role.lower() == "admin"]
        return agents + admins

    def get_by_index(self, idx, display_list=None):
        """ for the UI menu. If display_list is given, use that as the source list; otherwise use full list."""
        src = display_list if display_list is not None else self.users
        if 0 <= idx < len(src):
            return src[idx]
        return None

    def get_by_id(self, user_id):
        """ for internal use (like the actual user id) """
        for u in self.users:
            if u.id == user_id:
                return u
        return None
