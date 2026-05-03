"""
Entry point for the Social Media Analysis app.
Displays the main menu and hosts the Experiment Query screen
"app" to run the whole thing

Run with:
    python main_menu.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import get_connection
from emilio_screens import (
    AddPostsWindow, LinkAccountsWindow,
    SearchByPlatformWindow, SearchByDateRangeWindow,
)
from asha_screens import (
    EnterProjectWindow, EnterAnalysisWindow,
    SearchByUsernameWindow, SearchByNameWindow,
)

#  STYLE CONSTANTS
BG           = "#1e1e2e"
PANEL        = "#2a2a3e"
ACCENT       = "#7c6af7"
ACCENT_HOVER = "#9a8bff"
TEXT         = "#e0e0f0"
SUBTEXT      = "#a0a0c0"
ENTRY_BG     = "#3a3a52"

FONT_H1   = ("Segoe UI", 20, "bold")
FONT_H2   = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_SMALL= ("Segoe UI", 9)


def make_button(parent, text, command):
    frame = tk.Frame(parent, bg=ACCENT, cursor="hand2")
    lbl = tk.Label(frame, text=text, bg=ACCENT, fg="white",
                   font=FONT_BODY, padx=12, pady=6, anchor="w")
    lbl.pack(fill="both", expand=True)
    def _click(e): command()
    def _enter(e): lbl.configure(bg=ACCENT_HOVER); frame.configure(bg=ACCENT_HOVER)
    def _leave(e): lbl.configure(bg=ACCENT); frame.configure(bg=ACCENT)
    for w in (frame, lbl):
        w.bind("<Button-1>", _click)
        w.bind("<Enter>", _enter)
        w.bind("<Leave>", _leave)
    return frame


def apply_treeview_style():
    """Apply dark theme to all Treeview widgets."""
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("Treeview",
                background=PANEL, foreground=TEXT,
                fieldbackground=PANEL, rowheight=24, font=FONT_BODY)
    s.configure("Treeview.Heading",
                background=ENTRY_BG, foreground=ACCENT,
                font=("Segoe UI", 10, "bold"), relief="flat")
    s.map("Treeview", background=[("selected", ACCENT)])



#  MAIN MENU
class MainMenuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Social Media Analysis — CS 5330")
        self.configure(bg=BG)
        self.resizable(False, False)
        apply_treeview_style()
        self._center(500, 590)
        self._build()

    def _center(self, w, h):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build(self):
        #Header 
        hdr = tk.Frame(self, bg=ACCENT, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Social Media Analysis DB",
                 font=FONT_H1, bg=ACCENT, fg="white").pack()
        tk.Label(hdr, text="CS 5330  •  Spring 2026",
                 font=FONT_SMALL, bg=ACCENT, fg="#ddd").pack()

        #Button sections
        body = tk.Frame(self, bg=BG, padx=40, pady=24)
        body.pack(fill="both", expand=True)

        sections = [
            ("Data Entry", [
                ("Add Project Info", lambda: EnterProjectWindow(self)),
                ("Enter Analysis Results", lambda: EnterAnalysisWindow(self)),
                ("Enter Analysis Results",        self._stub("Enter Analysis Results")),
                ("Link Accounts to Same Person",  self._open_link_accounts),
            ]),
            ("Search Posts", [
                ("Search by Platform",            self._open_search_by_platform),
                ("Search by Date Range",          self._open_search_by_date_range),
                ("Search by Username / Platform", lambda: SearchByUsernameWindow(self)),
                ("Search by Person Name", lambda: SearchByNameWindow(self)),
            ]),
            ("Experiments", [
                ("Query Experiment Results",      self._open_experiment_query),
            ]),
        ]

        for title, buttons in sections:
            tk.Label(body, text=title, font=FONT_H2,
                     bg=BG, fg=ACCENT).pack(anchor="w", pady=(14, 4))
            f = tk.Frame(body, bg=BG)
            f.pack(fill="x")
            for label, cmd in buttons:
                b = make_button(f, label, cmd)
                b.pack(pady=2, fill="x")

        tk.Label(self, text="Credentials loaded from db_config.txt",
                 font=FONT_SMALL, bg=BG, fg=SUBTEXT).pack(pady=(0, 10))

    # Stubs for teammates' screens 
    @staticmethod
    def _stub(name):
        def _inner():
            messagebox.showinfo("Coming Soon",
                                f"'{name}' is being built by another team member.")
        return _inner

    def _open_experiment_query(self):
        ExperimentQueryWindow(self)

    def _open_add_posts(self):
        AddPostsWindow(self)

    def _open_link_accounts(self):
        LinkAccountsWindow(self)

    def _open_search_by_platform(self):
        SearchByPlatformWindow(self)

    def _open_search_by_date_range(self):
        SearchByDateRangeWindow(self)



#  EXPERIMENT QUERY WINDOW 
class ExperimentQueryWindow(tk.Toplevel):
    """
    User enters a project name → displays:
      1. All posts associated with that project
      2. Click a post → see its analysis results (all fields shown,
         '(not entered)' for any field without a recorded value)
      3. Field completion table: % of posts that have a value for
         each field
    
    Schema used  (Vikas design):
        ResearchProject(project_name PK, manager_first_name,
                        manager_last_name, institute_name FK,
                        start_date, end_date)
        Field(field_name, project_name)  composite PK
        ProjectPost(project_name, post_id)
        Post(post_id PK, username, media_name, content, post_time, ...)
        UserAccount(username, media_name)  composite PK
        AnalysisResult(project_name, post_id, field_name, result_value)
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Query Experiment Results")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._center(900, 680)
        self._project_name = None   # currently loaded project
        self._post_id_map  = {}     # tree row iid → post_id
        self._build()

    def _center(self, w, h):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    # Layout 
    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Query Experiment Results",
                 font=FONT_H2, bg=ACCENT, fg="white").pack()

        # Search bar
        sf = tk.Frame(self, bg=PANEL, pady=12, padx=20)
        sf.pack(fill="x")
        tk.Label(sf, text="Project name:", font=FONT_BODY,
                 bg=PANEL, fg=TEXT).pack(side="left")
        self._project_var = tk.StringVar()
        entry = tk.Entry(sf, textvariable=self._project_var,
                         font=FONT_BODY, bg=ENTRY_BG, fg=TEXT,
                         insertbackground=TEXT, relief="flat", width=38)
        entry.pack(side="left", padx=(8, 12), ipady=4)
        entry.bind("<Return>", lambda _e: self._search())
        b = make_button(sf, "Search", self._search)
        b.pack(side="left")

        # Status bar
        self._status = tk.StringVar(value="Enter a project name and press Search.")
        tk.Label(self, textvariable=self._status, font=FONT_SMALL,
                 bg=BG, fg=SUBTEXT, anchor="w").pack(fill="x", padx=16, pady=(6, 0))

        #Vertical panes
        paned = tk.PanedWindow(self, orient="vertical", bg=BG,
                               sashrelief="flat", sashwidth=6)
        paned.pack(fill="both", expand=True, padx=12, pady=8)

        # Top pane — posts table
        top = tk.Frame(paned, bg=BG)
        paned.add(top, minsize=180)
        tk.Label(top, text="Posts in this experiment",
                 font=FONT_H2, bg=BG, fg=ACCENT).pack(anchor="w", pady=(4, 4))
        self._posts_tree = self._make_tree(
            top,
            columns=[
                ("post_id",      "ID",           55),
                ("username",     "Username",     140),
                ("media_name",   "Platform",     110),
                ("post_time",    "Posted At",    145),
                ("preview",      "Post Content (preview)", 360),
            ],
            height=8,
        )
        self._posts_tree.bind("<<TreeviewSelect>>", self._on_post_select)

        # Bottom pane — results (left) + field completion (right)
        bot = tk.Frame(paned, bg=BG)
        paned.add(bot, minsize=180)

        left  = tk.Frame(bot, bg=BG)
        right = tk.Frame(bot, bg=BG)
        left.pack(side="left",  fill="both", expand=True)
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(left, text="Analysis results for selected post",
                 font=FONT_H2, bg=BG, fg=ACCENT).pack(anchor="w", pady=(4, 4))
        self._results_tree = self._make_tree(
            left,
            columns=[
                ("field_name",   "Field",  180),
                ("result_value", "Value",  240),
            ],
            height=7,
        )

        tk.Label(right, text="Field completion (%)",
                 font=FONT_H2, bg=BG, fg=ACCENT).pack(anchor="w", pady=(4, 4))
        self._pct_tree = self._make_tree(
            right,
            columns=[
                ("field_name", "Field",    170),
                ("pct",        "% Filled",  80),
                ("filled",     "Filled",    55),
                ("total",      "Total",     55),
            ],
            height=7,
        )

    # Tree helper
    @staticmethod
    def _make_tree(parent, columns, height):
        col_ids = [c[0] for c in columns]
        tree = ttk.Treeview(parent, columns=col_ids,
                             show="headings", height=height)
        tree.tag_configure("odd",  background="#252538")
        tree.tag_configure("even", background=PANEL)
        for col_id, heading, width in columns:
            tree.heading(col_id, text=heading)
            tree.column(col_id, width=width, minwidth=40)
        sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return tree

    # Search 
    def _search(self):
        name = self._project_var.get().strip()
        if not name:
            messagebox.showwarning("Input needed", "Please enter a project name.")
            return

        # Clear all panes
        for t in (self._posts_tree, self._results_tree, self._pct_tree):
            t.delete(*t.get_children())
        self._post_id_map.clear()
        self._project_name = None

        try:
            conn = get_connection()
            cur  = conn.cursor(dictionary=True)

            # 1. Look up the project
            cur.execute("""
                SELECT rp.project_name,
                       rp.manager_first_name,
                       rp.manager_last_name,
                       rp.institute_name,
                       rp.start_date,
                       rp.end_date
                FROM   ResearchProject rp
                WHERE  rp.project_name = %s
            """, (name,))
            project = cur.fetchone()

            if not project:
                self._status.set(f"No project found with name: '{name}'")
                conn.close()
                return

            self._project_name = project["project_name"]

            #  2. Load all posts for the project
            cur.execute("""
                SELECT p.post_id,
                       p.username,
                       p.media_name,
                       p.post_time,
                       LEFT(p.content, 80) AS preview
                FROM   ProjectPost  pp
                JOIN   Post         p  ON pp.post_id    = p.post_id
                WHERE  pp.project_name = %s
                ORDER BY p.post_time DESC
            """, (self._project_name,))
            posts = cur.fetchall()

            for i, row in enumerate(posts):
                tag     = "odd" if i % 2 else "even"
                preview = (row["preview"] + "…") if row["preview"] else ""
                iid = self._posts_tree.insert("", "end", tags=(tag,), values=(
                    row["post_id"],
                    row["username"],
                    row["media_name"],
                    str(row["post_time"]),
                    preview,
                ))
                self._post_id_map[iid] = row["post_id"]

            # 3. Field completion percentages 
            self._load_completion(cur)

            conn.close()

            total = len(posts)
            self._status.set(
                f"Project: {project['project_name']}  •  "
                f"Manager: {project['manager_first_name']} {project['manager_last_name']}  •  "
                f"Institute: {project['institute_name']}  •  "
                f"{total} post(s).   Click a post to see its results."
            )

        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    # Field completion table 
    def _load_completion(self, cur):
        self._pct_tree.delete(*self._pct_tree.get_children())
        if not self._project_name:
            return

        # Count how many posts the project has
        cur.execute("""
            SELECT COUNT(*) AS total
            FROM   ProjectPost
            WHERE  project_name = %s
        """, (self._project_name,))
        total = cur.fetchone()["total"]

        # For each field, count how many posts have a recorded value
        cur.execute("""
            SELECT f.field_name,
                   COUNT(ar.post_id) AS filled
            FROM   Field f
            LEFT JOIN AnalysisResult ar
                   ON  ar.field_name   = f.field_name
                   AND ar.project_name = f.project_name
            WHERE  f.project_name = %s
            GROUP BY f.field_name
            ORDER BY f.field_name
        """, (self._project_name,))

        for i, row in enumerate(cur.fetchall()):
            filled = row["filled"] or 0
            pct    = f"{100 * filled / total:.1f}%" if total > 0 else "—"
            tag    = "odd" if i % 2 else "even"
            self._pct_tree.insert("", "end", tags=(tag,), values=(
                row["field_name"], pct, filled, total
            ))

    # Per-post results
    def _on_post_select(self, _event):
        sel = self._posts_tree.selection()
        if not sel:
            return
        post_id = self._post_id_map.get(sel[0])
        if post_id is None or not self._project_name:
            return

        self._results_tree.delete(*self._results_tree.get_children())
        try:
            conn = get_connection()
            cur  = conn.cursor(dictionary=True)

            # Show ALL fields for the project; LEFT JOIN means fields
            # without a recorded value appear as '(not entered)'
            cur.execute("""
                SELECT f.field_name,
                       COALESCE(ar.result_value, '(not entered)') AS result_value
                FROM   Field f
                LEFT JOIN AnalysisResult ar
                       ON  ar.field_name   = f.field_name
                       AND ar.project_name = f.project_name
                       AND ar.post_id      = %s
                WHERE  f.project_name = %s
                ORDER BY f.field_name
            """, (post_id, self._project_name))

            for i, row in enumerate(cur.fetchall()):
                tag = "odd" if i % 2 else "even"
                self._results_tree.insert("", "end", tags=(tag,), values=(
                    row["field_name"], row["result_value"]
                ))
            conn.close()

        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))


#  Entry point
if __name__ == "__main__":
    app = MainMenuApp()
    app.mainloop()
