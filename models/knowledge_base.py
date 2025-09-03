# auth_selector.py

from typing import Optional, TypedDict, List

class User(TypedDict):
    id: int
    name: str
    role: str  # "Agent" | "Admin"
    status: str  # "Active" etc.

# Seed a tiny roster; expand later if you want.
DEFAULT_USERS: List[User] = [
    {"id": 1, "name": "Alex Johnson", "role": "Agent", "status": "Active"},
    {"id": 2, "name": "Sam Patel",    "role": "Agent", "status": "Active"},
    {"id": 3, "name": "Dana Kim",     "role": "Admin", "status": "Active"},
]

class AuthSelector:
    """
    Standalone login/switch-user UI for the terminal.
    No passwords; user picks a persona from a list.
    Returns the chosen user dict or None if the user exits.
    """

    def __init__(self, users: List[User] | None = None):
        self.users = users[:] if users else DEFAULT_USERS[:]

    def run(self) -> Optional[User]:
        """Main entry. Loops until a valid user is chosen or the user exits."""
        self._print_header()
        while True:
            self._show_user_list()
            choice = input("Select a user by number (or 0 to exit): ").strip()
            if choice == "0":
                print("Exiting to system… (session will reset to defaults)")
                return None
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(self.users):
                    selected = self.users[idx]
                    print(f"\n✅ Operating as: {selected['name']} ({selected['role']})\n")
                    return selected
            print("❌ Invalid selection. Please try again.\n")

    # -------------------------------
    # Rendering helpers
    # -------------------------------
    def _print_header(self):
        print("=" * 58)
        print("  Login / Switch User  ")
        print("=" * 58)
        print("Pick an Agent/Admin to operate as. No password required.\n")

    def _show_user_list(self):
        print("Users:")
        print("-" * 58)
        # Group by role for clarity
        agents = [u for u in self.users if u["role"].lower() == "agent"]
        admins = [u for u in self.users if u["role"].lower() == "admin"]

        # Keep a stable numbering across the full list
        flat = agents + admins
        for i, u in enumerate(flat, start=1):
            print(f"{i}) {u['name']:<20}  | {u['role']:<5} | {u['status']}")
        print("-" * 58)

# Quick manual test
if __name__ == "__main__":
    auth = AuthSelector()
    current_user = auth.run()
    if current_user:
        print(f"Selected: {current_user}")
