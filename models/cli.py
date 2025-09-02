class TicketCLI:
    """
    Terminal UI skeleton for the Ticketing System.
    Just outlines features. No backend connection yet.
    """

    def __init__(self):
        self.running = True

    def run(self):
        self.print_header()
        while self.running:
            self.show_main_menu()
            choice = input("Select an option: ").strip()
            print()
            self.handle_choice(choice)

    def print_header(self):
        print("=" * 58)
        print("  CLI Ticket Tracker (mini osTicket-style)  ")
        print("=" * 58)

    def show_main_menu(self):
        print("\nMain Menu")
        print("-" * 40)
        # --- Core ---
        print("1) List tickets")
        print("2) View ticket by ID")
        print("3) Create ticket")
        print("4) Update ticket")
        print("5) Delete ticket")
        # --- Intermediate ---
        print("6) Filter tickets (by status/priority/agent)")
        print("7) Assign ticket to agent")
        print("8) Add internal note")
        print("9) SLA check (overdue tickets)")
        # --- Advanced ---
        print("10) Convert to Knowledge Base article")
        print("11) Role simulation (Admin vs Agent)")
        # --- Exit ---
        print("0) Exit")
        print("-" * 40)

    def handle_choice(self, choice: str):
        handlers = {
            "1": self.not_yet,
            "2": self.not_yet,
            "3": self.not_yet,
            "4": self.not_yet,
            "5": self.not_yet,
            "6": self.not_yet,
            "7": self.not_yet,
            "8": self.not_yet,
            "9": self.not_yet,
            "10": self.not_yet,
            "11": self.not_yet,
            "0": self.action_exit,
        }
        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            print("❌ Invalid option. Please try again.")

    # ===============================
    # Placeholder actions
    # ===============================
    def not_yet(self):
        print("🚧 Feature not yet created.\n")

    def action_exit(self):
        print("Goodbye!")
        self.running = False


# -------------------------------
# Run directly for a quick test
# -------------------------------
if __name__ == "__main__":
    app = TicketCLI()
    app.run()
