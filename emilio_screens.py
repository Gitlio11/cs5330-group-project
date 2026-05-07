import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import get_connection

BG           = "#1e1e2e"
PANEL        = "#2a2a3e"
ACCENT       = "#7c6af7"
ACCENT_HOVER = "#9a8bff"
TEXT         = "#e0e0f0"
SUBTEXT      = "#a0a0c0"
ENTRY_BG     = "#3a3a52"
FONT_H2      = ("Segoe UI", 14, "bold")
FONT_BODY    = ("Segoe UI", 11)
FONT_SMALL   = ("Segoe UI", 9)


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


def make_tree(parent, columns, height=10):
    col_ids = [c[0] for c in columns]
    tree = ttk.Treeview(parent, columns=col_ids, show="headings", height=height)
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


def labeled_entry(parent, label, row, var):
    tk.Label(parent, text=label, font=FONT_BODY, bg=PANEL, fg=TEXT).grid(
        row=row, column=0, sticky="e", padx=(12, 6), pady=4)
    e = tk.Entry(parent, textvariable=var, font=FONT_BODY,
                 bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                 relief="flat", width=34)
    e.grid(row=row, column=1, sticky="w", padx=(0, 12), pady=4, ipady=3)
    return e


def center_window(win, w, h):
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


class AddPostsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Link Posts and Projects")
        self.configure(bg=BG)
        self.resizable(False, False)
        center_window(self, 560, 280)  # CHANGED: smaller window, just 2 fields
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Link Posts and Projects",
                 font=FONT_H2, bg=ACCENT, fg="white").pack()

        form = tk.Frame(self, bg=PANEL, padx=16, pady=16)
        form.pack(fill="x", padx=20, pady=16)

        self._project = tk.StringVar()
        self._post_id_link = tk.StringVar()

        labeled_entry(form, "Project name *", 0, self._project)
        labeled_entry(form, "Post ID *",       1, self._post_id_link)

        self._status = tk.StringVar(value="Enter a project name and post ID to link.")
        tk.Label(self, textvariable=self._status, font=FONT_SMALL,
                 bg=BG, fg=SUBTEXT, wraplength=520, anchor="w").pack(
            fill="x", padx=20, pady=(0, 4))

        make_button(self, "Submit", self._submit).pack(pady=(0, 16), padx=20, fill="x")

    def _submit(self):
        project = self._project.get().strip()
        raw_id  = self._post_id_link.get().strip()

        if not project or not raw_id:
            messagebox.showwarning("Missing fields",
                                   "Both Project name and Post ID are required.")
            return
        if not raw_id.isdigit():
            messagebox.showwarning("Invalid", "Post ID must be a number.")
            return

        post_id = int(raw_id)
        try:
            conn = get_connection()
            cur  = conn.cursor(dictionary=True)

            cur.execute("SELECT 1 FROM ResearchProject WHERE project_name = %s", (project,))
            if not cur.fetchone():
                messagebox.showerror("Not found", f"Project '{project}' does not exist.")
                conn.close()
                return

            cur.execute("SELECT 1 FROM Post WHERE post_id = %s", (post_id,))
            if not cur.fetchone():
                messagebox.showerror("Not found", f"No post with ID {post_id}.")
                conn.close()
                return

            cur.execute("INSERT IGNORE INTO ProjectPost (project_name, post_id) VALUES (%s, %s)",
                        (project, post_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Post (id={post_id}) linked to '{project}'.")
            self._clear()

        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    def _clear(self):
        self._project.set("")
        self._post_id_link.set("")


class LinkAccountsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Link Accounts to Same Person")
        self.configure(bg=BG)
        self.resizable(False, False)
        center_window(self, 620, 500)
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Link Accounts to Same Person",
                 font=FONT_H2, bg=ACCENT, fg="white").pack()

        form = tk.Frame(self, bg=PANEL, padx=16, pady=16)
        form.pack(fill="x", padx=20, pady=16)

        self._new_person = tk.BooleanVar(value=True)
        self._person_id = tk.StringVar()
        self._username = tk.StringVar()
        self._media = tk.StringVar()

        tk.Label(form, text="Person:", font=FONT_BODY,
                 bg=PANEL, fg=TEXT).grid(row=0, column=0, sticky="e", padx=(12, 6), pady=4)
        rb_frame = tk.Frame(form, bg=PANEL)
        rb_frame.grid(row=0, column=1, sticky="w")
        tk.Radiobutton(rb_frame, text="Create new person",
                       variable=self._new_person, value=True,
                       bg=PANEL, fg=TEXT, selectcolor=ENTRY_BG,
                       activebackground=PANEL,
                       command=self._toggle).pack(side="left")
        tk.Radiobutton(rb_frame, text="Use existing ID",
                       variable=self._new_person, value=False,
                       bg=PANEL, fg=TEXT, selectcolor=ENTRY_BG,
                       activebackground=PANEL,
                       command=self._toggle).pack(side="left", padx=(12, 0))

        tk.Label(form, text="Person ID", font=FONT_BODY,
                 bg=PANEL, fg=TEXT).grid(row=1, column=0, sticky="e", padx=(12, 6), pady=4)
        self._id_entry = tk.Entry(form, textvariable=self._person_id,
                                   font=FONT_BODY, bg=ENTRY_BG, fg=TEXT,
                                   insertbackground=TEXT, relief="flat",
                                   width=16, state="disabled")
        self._id_entry.grid(row=1, column=1, sticky="w", padx=(0, 12), pady=4, ipady=3)

        labeled_entry(form, "Username *",         2, self._username)
        labeled_entry(form, "Platform (media) *", 3, self._media)

        self._status = tk.StringVar(
            value="Create a new person or enter an existing ID, then link an account.")
        tk.Label(self, textvariable=self._status, font=FONT_SMALL,
                 bg=BG, fg=SUBTEXT, wraplength=580, anchor="w").pack(
            fill="x", padx=20, pady=(0, 4))

        btn = make_button(self, "Link Account", self._submit)
        btn.pack(pady=(0, 10), padx=20, fill="x")

        tk.Label(self, text="Existing links", font=FONT_SMALL,
                 bg=BG, fg=SUBTEXT).pack(anchor="w", padx=20)
        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self._link_tree = make_tree(tree_frame, [
            ("person_id",  "Person ID",  80),
            ("first_name", "First Name", 110),
            ("last_name",  "Last Name",  110),
            ("username",   "Username",   130),
            ("media_name", "Platform",   110),
        ], height=5)
        self._load_links()

    def _toggle(self):
        if self._new_person.get():
            self._id_entry.configure(state="disabled")
        else:
            self._id_entry.configure(state="normal")

    def _load_links(self):
        self._link_tree.delete(*self._link_tree.get_children())
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT ao.person_id, p.first_name, p.last_name,
                       ao.username, ao.media_name
                FROM AccountOwnership ao
                JOIN Person p ON p.person_id = ao.person_id
                ORDER BY ao.person_id, ao.username
            """)
            for i, row in enumerate(cur.fetchall()):
                tag = "odd" if i % 2 else "even"
                self._link_tree.insert("", "end", tags=(tag,),
                    values=(row["person_id"],
                            row["first_name"] or "(none)",
                            row["last_name"]  or "(none)",
                            row["username"],
                            row["media_name"]))
            conn.close()
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    def _submit(self):
        username = self._username.get().strip()
        media = self._media.get().strip()
        if not username or not media:
            messagebox.showwarning("Missing fields", "Username and Platform are required.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)

            cur.execute("SELECT 1 FROM UserAccount WHERE username = %s AND media_name = %s",
                        (username, media))
            if not cur.fetchone():
                messagebox.showerror("Not found",
                    f"No account '{username}' on '{media}' found in the database.")
                conn.close()
                return

            if self._new_person.get():
                cur.execute("INSERT INTO Person (first_name, last_name) VALUES (NULL, NULL)")
                person_id = cur.lastrowid
            else:
                raw = self._person_id.get().strip()
                if not raw.isdigit():
                    messagebox.showwarning("Invalid ID", "Person ID must be a number.")
                    conn.close()
                    return
                person_id = int(raw)
                cur.execute("SELECT 1 FROM Person WHERE person_id = %s", (person_id,))
                if not cur.fetchone():
                    messagebox.showerror("Not found", f"No person with ID {person_id}.")
                    conn.close()
                    return

            cur.execute("INSERT IGNORE INTO AccountOwnership (person_id, username, media_name) VALUES (%s, %s, %s)",
                        (person_id, username, media))

            conn.commit()
            conn.close()
            messagebox.showinfo("Success",
                f"'{username}' on '{media}' linked to person ID {person_id}.")
            self._username.set("")
            self._media.set("")
            self._load_links()

        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))


class SearchByPlatformWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Search Posts by Platform")
        self.configure(bg=BG)
        self.resizable(True, True)
        center_window(self, 900, 540)
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Search Posts by Platform",
                 font=FONT_H2, bg=ACCENT, fg="white").pack()

        sf = tk.Frame(self, bg=PANEL, pady=12, padx=20)
        sf.pack(fill="x")
        tk.Label(sf, text="Platform:", font=FONT_BODY, bg=PANEL, fg=TEXT).pack(side="left")
        self._platform_var = tk.StringVar()
        entry = tk.Entry(sf, textvariable=self._platform_var,
                         font=FONT_BODY, bg=ENTRY_BG, fg=TEXT,
                         insertbackground=TEXT, relief="flat", width=30)
        entry.pack(side="left", padx=(8, 12), ipady=4)
        entry.bind("<Return>", lambda _e: self._search())
        make_button(sf, "Search", self._search).pack(side="left")

        self._status = tk.StringVar(value="Enter a platform name (e.g. Facebook).")
        tk.Label(self, textvariable=self._status, font=FONT_SMALL,
                 bg=BG, fg=SUBTEXT, anchor="w").pack(fill="x", padx=16, pady=(4, 0))

        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=12, pady=8)
        self._tree = make_tree(tree_frame, [
            ("post_id",     "ID",              55),
            ("username",    "Username",        140),
            ("media_name",  "Platform",        110),
            ("post_time",   "Posted At",       145),
            ("experiments", "Projects",        200),
            ("preview",     "Content preview", 280),
        ])

    def _search(self):
        platform = self._platform_var.get().strip()
        if not platform:
            messagebox.showwarning("Input needed", "Please enter a platform name.")
            return

        self._tree.delete(*self._tree.get_children())
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT p.post_id, p.username, p.media_name, p.post_time,
                       LEFT(p.content, 80) AS preview,
                       GROUP_CONCAT(pp.project_name ORDER BY pp.project_name SEPARATOR ', ') AS experiments
                FROM Post p
                LEFT JOIN ProjectPost pp ON pp.post_id = p.post_id
                WHERE p.media_name = %s
                GROUP BY p.post_id
                ORDER BY p.post_time DESC
            """, (platform,))
            rows = cur.fetchall()
            conn.close()

            for i, row in enumerate(rows):
                tag = "odd" if i % 2 else "even"
                preview = (row["preview"] + "…") if row["preview"] else ""
                self._tree.insert("", "end", tags=(tag,), values=(
                    row["post_id"], row["username"], row["media_name"],
                    str(row["post_time"]), row["experiments"] or "—", preview,
                ))
            self._status.set(f"{len(rows)} post(s) found on '{platform}'.")

        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))


class SearchByDateRangeWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Search Posts by Date Range")
        self.configure(bg=BG)
        self.resizable(True, True)
        center_window(self, 900, 540)
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Search Posts by Date Range",
                 font=FONT_H2, bg=ACCENT, fg="white").pack()

        sf = tk.Frame(self, bg=PANEL, pady=12, padx=20)
        sf.pack(fill="x")

        tk.Label(sf, text="From:", font=FONT_BODY, bg=PANEL, fg=TEXT).pack(side="left")
        self._start_var = tk.StringVar()
        tk.Entry(sf, textvariable=self._start_var, font=FONT_BODY,
                 bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                 relief="flat", width=20).pack(side="left", padx=(8, 16), ipady=4)

        tk.Label(sf, text="To:", font=FONT_BODY, bg=PANEL, fg=TEXT).pack(side="left")
        self._end_var = tk.StringVar()
        tk.Entry(sf, textvariable=self._end_var, font=FONT_BODY,
                 bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                 relief="flat", width=20).pack(side="left", padx=(8, 16), ipady=4)

        make_button(sf, "Search", self._search).pack(side="left")

        self._status = tk.StringVar(value="Enter dates as YYYY-MM-DD or YYYY-MM-DD HH:MM.")
        tk.Label(self, textvariable=self._status, font=FONT_SMALL,
                 bg=BG, fg=SUBTEXT, anchor="w").pack(fill="x", padx=16, pady=(4, 0))

        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=12, pady=8)
        self._tree = make_tree(tree_frame, [
            ("post_id",     "ID",              55),
            ("username",    "Username",        140),
            ("media_name",  "Platform",        110),
            ("post_time",   "Posted At",       145),
            ("experiments", "Projects",        200),
            ("preview",     "Content preview", 280),
        ])

    def _search(self):
        start = self._start_var.get().strip()
        end = self._end_var.get().strip()
        if not start or not end:
            messagebox.showwarning("Input needed", "Please enter both a start and end date.")
            return

        self._tree.delete(*self._tree.get_children())
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT p.post_id, p.username, p.media_name, p.post_time,
                       LEFT(p.content, 80) AS preview,
                       GROUP_CONCAT(pp.project_name ORDER BY pp.project_name SEPARATOR ', ') AS experiments
                FROM Post p
                LEFT JOIN ProjectPost pp ON pp.post_id = p.post_id
                WHERE p.post_time BETWEEN %s AND %s
                GROUP BY p.post_id
                ORDER BY p.post_time DESC
            """, (start, end))
            rows = cur.fetchall()
            conn.close()

            for i, row in enumerate(rows):
                tag = "odd" if i % 2 else "even"
                preview = (row["preview"] + "…") if row["preview"] else ""
                self._tree.insert("", "end", tags=(tag,), values=(
                    row["post_id"], row["username"], row["media_name"],
                    str(row["post_time"]), row["experiments"] or "—", preview,
                ))
            self._status.set(f"{len(rows)} post(s) found between '{start}' and '{end}'.")

        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))
