from typing import List, Optional


# -----------------------------------------------------------------------------
# Model
# -----------------------------------------------------------------------------
class User:
    """Represents an agent/admin account that can claim tickets and tasks."""

    def __init__(self, user_id: int, name: str, role: str = "Agent", status: str = "Active"):
        self.id = user_id
        self.name = name
        self.role = role      # "Agent" or "Admin"
        self.status = status  # "Active" or "Inactive"

        # Basic tracking (store ids for simplicity)
        self.tickets_claimed: List[int] = []
        self.tasks_claimed: List[int] = []

    # ---------- ticket helpers ----------
    def claim_ticket(self, ticket) -> bool:
        """
        Add a ticket to the user's claimed list.
        Accepts a ticket id or a ticket object with .id; avoids duplicates.
        Returns True if added, False if it was already present.
        """
        tid = ticket.id if hasattr(ticket, "id") else ticket
        if tid not in self.tickets_claimed:
            self.tickets_claimed.append(tid)
            return True
        return False

    def unclaim_ticket(self, ticket) -> bool:
        """
        Remove a ticket from the user's claimed list if present.
        Accepts a ticket id or a ticket object with .id.
        Returns True if removed, False if it wasn't present.
        """
        tid = ticket.id if hasattr(ticket, "id") else ticket
        if tid in self.tickets_claimed:
            self.tickets_claimed.remove(tid)
            return True
        return False

    # ---------- task helpers ----------
    def claim_task(self, task) -> bool:
        """
        Add a task to the user's claimed list.
        Accepts a task id or a task object with .id; avoids duplicates.
        Returns True if added, False if it was already present.
        """
        task_id = task.id if hasattr(task, "id") else task
        if task_id not in self.tasks_claimed:
            self.tasks_claimed.append(task_id)
            return True
        return False

    def unclaim_task(self, task) -> bool:
        """
        Remove a task from the user's claimed list if present.
        Accepts a task id or a task object with .id.
        Returns True if removed, False if it wasn't present.
        """
        task_id = task.id if hasattr(task, "id") else task
        if task_id in self.tasks_claimed:
            self.tasks_claimed.remove(task_id)
            return True
        return False

    def __repr__(self) -> str:
        return "<User {}: {} ({})>".format(self.id, self.name, self.role)


# -----------------------------------------------------------------------------
# Store
# -----------------------------------------------------------------------------
class UserStore:
    """Manages the list of all users in the system (in-memory)."""

    def __init__(self, seed_users: Optional[List[User]] = None):
        # Copy seed list if provided, otherwise start empty
        if seed_users:
            self.users: List[User] = seed_users[:]
        else:
            self.users = []

        # Next id is computed from existing users
        self._next_id = (max([u.id for u in self.users]) + 1) if self.users else 1

    # ---------- creation ----------
    def add_user(self, name: str, role: str = "Agent", status: str = "Active") -> User:
        """Create and append a new User, returning the instance."""
        user = User(self._next_id, name, role, status)
        self.users.append(user)
        self._next_id += 1
        return user

    # ---------- listing ----------
    def list_users(self) -> List[User]:
        """Return all users in insertion order."""
        return self.users

    def list_agents_first(self) -> List[User]:
        """
        Return all users with Agents first, then Admins.
        (Ordering inside each group follows current list order.)
        """
        agents = [u for u in self.users if u.role.lower() == "agent"]
        admins = [u for u in self.users if u.role.lower() == "admin"]
        return agents + admins

    # ---------- lookups ----------
    def get_by_index(self, idx: int, display_list: Optional[List[User]] = None) -> Optional[User]:
        """
        Index-based lookup for UI menus.
        If a display_list is provided, index into that; otherwise index into full list.
        Returns None if index is out of range.
        """
        src = display_list if display_list is not None else self.users
        if 0 <= idx < len(src):
            return src[idx]
        return None

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Find a user by their numeric id, or return None."""
        for u in self.users:
            if u.id == user_id:
                return u
        return None
