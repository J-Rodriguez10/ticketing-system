class Dashboard:
    """
    Simple overview tab.
    Pulls stats from TicketManager and TaskManager.
    No actions — just a summary + return to tabs.
    """

    def __init__(self, ticket_manager, task_manager):
        self.ticket_manager = ticket_manager
        self.task_manager = task_manager

    def run_ui(self):
        print("\n=== Dashboard Overview ===\n")

        # --- Tickets ---
        tm = self.ticket_manager
        print("Tickets:")
        print("  Created:  {}".format(tm.totals_created))
        print("  Resolved: {}".format(tm.totals_resolved))
        print("  Deleted:  {}".format(tm.totals_deleted))
        print("  Open:     {}".format(len(tm.tickets)))
        print("")

        # --- Tasks ---
        ta = self.task_manager
        print("Tasks:")
        print("  Created:  {}".format(ta.totals_created))
        print("  Resolved: {}".format(ta.totals_resolved))
        print("  Deleted:  {}".format(ta.totals_deleted))
        print("  Open:     {}".format(len(ta.tasks)))
        print("")

        input("Press Enter to return...")
