# app.py
from models.users import UserStore
from models.auth_selector import AuthSelector

def seed_users():
    store = UserStore()
    store.add_user("Admin", role="Admin", status="Active")
    store.add_user("Sam Patel", role="Agent", status="Active")
    store.add_user("Dana Kim", role="Agent", status="Active")
    return store

class App:
    def __init__(self):
        self.user_store = seed_users()
        self.current_user = None
        self.running = True

    def run(self):
        while self.running:
            selector = AuthSelector(self.user_store)
            self.current_user = selector.run()
            if not self.current_user:
                break
            self._tabs_menu_loop()
        print("Goodbye! (session reset)")

    def _tabs_menu_loop(self):
        while True:
            self._print_tabs_header()
            self._print_tabs_menu()
            choice = input("Enter a number: ").strip()

            if choice == "0":
                self.running = False
                return
            if choice == "9":
                print("\nSwitching user...\n")
                return

            if choice == "1":
                self._run_tickets_tab()
            elif choice == "2":
                self._run_tasks_tab()
            elif choice == "3":
                self._run_users_tab()
            elif choice == "4":
                self._run_kb_tab()
            elif choice == "5":
                self._run_dashboard_tab()
            else:
                print("\n❌ Invalid option. Try again.\n")

    def _print_tabs_header(self):
        print("=" * 58)
        print("  Main Tabs — Operating as: {} ({})".format(
            self.current_user.name, self.current_user.role))
        print("=" * 58)

    def _print_tabs_menu(self):
        print("\nTabs:")
        print("1) Tickets")
        print("2) Tasks")
        print("3) Users")
        print("4) Knowledge Base")
        print("5) Dashboard")
        print("9) Switch user")
        print("0) Exit\n")

    # Placeholders
    def _run_tickets_tab(self):
        print("\n=== Tickets Tab === (not implemented yet)")
        input("Press Enter to return...")

    def _run_tasks_tab(self):
        print("\n=== Tasks Tab === (not implemented yet)")
        input("Press Enter to return...")

    def _run_users_tab(self):
        print("\n=== Users Tab === (not implemented yet)")
        input("Press Enter to return...")

    def _run_kb_tab(self):
        print("\n=== Knowledge Base === (not implemented yet)")
        input("Press Enter to return...")

    def _run_dashboard_tab(self):
        print("\n=== Dashboard === (not implemented yet)")
        input("Press Enter to return...")

if __name__ == "__main__":
    app = App()
    app.run()
