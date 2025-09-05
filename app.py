from models.users import UserStore
from models.auth_selector import AuthSelector
from models.tabs.tickets import TicketManager
from models.tabs.tasks import TaskManager
from models.tabs.knowledge_base import KnowledgeBase
from models.tabs.dashboard import Dashboard

# -----------------------------------------------------------------------------
# Seed Users
# -----------------------------------------------------------------------------
def seed_users():
    """Initialize system with default users."""
    store = UserStore()
    store.add_user("Admin", role="Admin", status="Active")
    store.add_user("Sam Patel", role="Agent", status="Active")
    store.add_user("Dana Kim", role="Agent", status="Active")
    return store


# -----------------------------------------------------------------------------
# App
# -----------------------------------------------------------------------------
class App:
    """Main app controller: login + tabs menu."""

    def __init__(self):
        # Core state
        self.user_store = seed_users()
        self.current_user = None
        self.running = True

        # Managers (pass user_store where needed)
        self.ticket_manager = TicketManager(self.user_store)
        self.task_manager = TaskManager(self.user_store)
        self.kb = KnowledgeBase()
        self.dashboard = Dashboard(self.ticket_manager, self.task_manager)

    # --- main loop ---
    def run(self):
        while self.running:
            selector = AuthSelector(self.user_store)
            self.current_user = selector.run()
            if not self.current_user:
                break
            self._tabs_menu_loop()
        print("Goodbye! (session reset)")

    # --- tabs navigation ---
    def _tabs_menu_loop(self):
        while True:
            self._print_tabs_header()
            self._print_tabs_menu()
            choice = input("Enter a number: ").strip()

            if choice == "0":   # Exit
                self.running = False
                return
            if choice == "9":   # Switch user
                print("\nSwitching user...\n")
                return

            if choice == "1":
                self._run_tickets_tab()
            elif choice == "2":
                self._run_tasks_tab()
            elif choice == "3":
                self._run_kb_tab()
            elif choice == "4":
                self._run_dashboard_tab()
            elif choice == "8":   # client-facing ticket submission
                self._run_client_submit_ticket()
            else:
                print("\n❌ Invalid option. Try again.\n")

    # --- print helpers ---
    def _print_tabs_header(self):
        print("=" * 58)
        print("  Main Tabs — Operating as: {} ({})".format(
            self.current_user.name, self.current_user.role))
        print("=" * 58)

    def _print_tabs_menu(self):
        print("\nTabs:")
        print("1) Tickets")
        print("2) Tasks")
        print("3) Knowledge Base")
        print("4) Dashboard")
        print("")
        print("Extra Options:")
        print("8) Submit a ticket (as a client)")
        print("9) Switch Agents")
        print("0) Exit\n")

    # --- tab launchers ---
    def _run_tickets_tab(self):
        self.ticket_manager.run_ui(self.current_user)

    def _run_tasks_tab(self):
        self.task_manager.run_ui(self.current_user)

    def _run_kb_tab(self):
        self.kb.run_ui()

    def _run_dashboard_tab(self):
        self.dashboard.run_ui()

    def _run_client_submit_ticket(self):
        self.ticket_manager.submit_ticket_ui()


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = App()
    app.run()
