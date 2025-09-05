from datetime import datetime

# Seed articles
DEFAULT_ARTICLES = [
    {
        "title": "How to reset your password",
        "content": (
            "1) Go to the login portal\n"
            "2) Click 'Forgot Password'\n"
            "3) Check your email and follow the link\n"
            "4) Choose a new password and confirm"
        ),
    },
    {
        "title": "How to set up VPN",
        "content": (
            "1) Open the VPN client\n"
            "2) Enter your company email\n"
            "3) Use your SSO credentials to authenticate\n"
            "4) Click Connect"
        ),
    },
]


# -----------------------------------------------------------------------------
# Model
# -----------------------------------------------------------------------------
class Article:
    """A single FAQ entry."""

    def __init__(self, article_id, title, content, created_at=None):
        self.id = article_id
        self.title = title
        self.content = content
        self.created_at = created_at or datetime.now()

    def __repr__(self):
        return f"<Article {self.id}: {self.title[:24]!r}>"


# -----------------------------------------------------------------------------
# Manager / UI
# -----------------------------------------------------------------------------
class KnowledgeBase:
    """Stores and manages FAQ-style articles."""

    def __init__(self):
        self.articles = {}
        for i, a in enumerate(DEFAULT_ARTICLES, start=1):
            self.articles[i] = Article(i, a["title"], a["content"])
        self._next_id = (max(self.articles.keys()) + 1) if self.articles else 1

    # --- helpers ---
    def _next(self):
        nid = self._next_id
        self._next_id += 1
        return nid

    def get_article(self, article_id):
        return self.articles.get(article_id)

    def _print_titles(self):
        print("{:<4} {:<40} {:<12}".format("ID", "Title", "Created"))
        print("-" * 64)
        if not self.articles:
            print("(no articles yet)")
            return
        for a in self.articles.values():
            created = a.created_at.strftime("%Y-%m-%d")
            print("{:<4} {:<40} {:<12}".format(a.id, a.title[:40], created))

    # --- UI entrypoint ---
    def run_ui(self):
        print("\n=== Knowledge Base (Titles / FAQ) ===\n")
        running = True
        while running:
            self._print_titles()
            print("\nActions:")
            print("1) Create article")
            print("2) Read article by ID")
            print("3) Delete article by ID")
            print("0) Back to tabs\n")

            choice = input("Enter a number: ").strip()
            if choice == "0":
                print("\nReturning to tabs...\n")
                running = False
            elif choice == "1":
                self._create_article_ui()
            elif choice == "2":
                self._read_article_ui()
            elif choice == "3":
                self._delete_article_ui()
            else:
                print("\n❌ Invalid option. Try again.\n")

    # --- create/read/delete ---
    def _create_article_ui(self):
        print("\n=== Create Article (enter 0 at any prompt to cancel) ===")
        title = input("Title: ").strip()
        if title == "0":
            print("Cancelled.\n")
            return
        if not title:
            print("❌ Title is required.\n")
            return

        print("Enter content. Finish with a single '.' on a line.")
        lines = []
        while True:
            line = input()
            if line == "0":
                print("Cancelled.\n")
                return
            if line.strip() == ".":
                break
            lines.append(line)
        content = "\n".join(lines).strip()
        if not content:
            print("❌ Content is required.\n")
            return

        nid = self._next()
        self.articles[nid] = Article(nid, title, content)
        print(f"✅ Article {nid} ('{title}') created.\n")

    def _read_article_ui(self):
        s = input("\nEnter Article ID to read (or 0 to cancel): ").strip()
        if s == "0":
            print("Cancelled.\n")
            return
        if not s.isdigit():
            print("❌ Invalid input. Please enter a number.\n")
            return

        aid = int(s)
        a = self.get_article(aid)
        if not a:
            print("❌ Article not found.\n")
            return

        print("\n=== Article {} — {} ===".format(a.id, a.title))
        print(a.content)
        print("")
        input("Press Enter to return...")

    def _delete_article_ui(self):
        s = input("\nEnter Article ID to delete (or 0 to cancel): ").strip()
        if s == "0":
            print("Cancelled.\n")
            return
        if not s.isdigit():
            print("❌ Invalid input. Please enter a number.\n")
            return

        aid = int(s)
        a = self.get_article(aid)
        if not a:
            print("❌ Article not found.\n")
            return

        confirm = input(f"Type DELETE to confirm removal of '{a.title}': ").strip()
        if confirm == "DELETE":
            del self.articles[aid]
            print(f"✅ Article {aid} deleted.\n")
        else:
            print("Cancelled.\n")
