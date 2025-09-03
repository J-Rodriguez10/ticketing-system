from models.users import UserStore


class AuthSelector:
    """Standalone login/switch-user UI for the terminal."""

    def __init__(self, user_store):
        self.users = user_store

    def run(self):
        self._print_header()
        while True:
            display = self.users.list_agents_first()
            self._show_user_list(display)
            choice = input("Select a user by number (or 0 to exit): ").strip()

            if choice == "0":
                print("Exiting to system… (session will reset to defaults)")
                return None

            if choice.isdigit():
                idx = int(choice) - 1
                selected = self.users.get_by_index(idx, display)
                if selected:
                    print("\n✅ Operating as: {} ({})\n".format(selected.name, selected.role))
                    return selected

            print("❌ Invalid selection. Please try again.\n")

    def _print_header(self):
        print("=" * 58)
        print("  Login / Switch User  ")
        print("=" * 58)
        print("Pick an Agent/Admin to operate as. No password required.\n")

    def _show_user_list(self, display):
        print("Users:")
        print("-" * 58)
        for i, u in enumerate(display, start=1):
            print("{}) {:<20} | {:<5} | {}".format(i, u.name, u.role, u.status))
        print("-" * 58)
