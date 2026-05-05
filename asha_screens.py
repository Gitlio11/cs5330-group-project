"""
asha_screens.py

  - EnterProjectWindow       : Data Entry → Add Project Info
  - EnterAnalysisWindow      : Data Entry → Enter Analysis Results
  - SearchByUsernameWindow   : Search Posts → Search by Username / Platform
  - SearchByNameWindow       : Search Posts → Search by Person Name
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from db_connection import get_connection

BG           = "#1e1e2e"
PANEL        = "#2a2a3e"
ACCENT       = "#7c6af7"
ACCENT_HOVER = "#9a8bff"
TEXT         = "#e0e0f0"
SUBTEXT      = "#a0a0c0"
ENTRY_BG     = "#3a3a52"
FONT_H1      = ("Segoe UI", 20, "bold")
FONT_H2      = ("Segoe UI", 14, "bold")
FONT_BODY    = ("Segoe UI", 11)
FONT_SMALL   = ("Segoe UI", 9)


# Shared helpers 

def make_button(parent, text, command):
    frame = tk.Frame(parent, bg=ACCENT, cursor="hand2")
    lbl = tk.Label(frame, text=text, bg=ACCENT, fg="white",
                   font=FONT_BODY, padx=12, pady=6, anchor="w")
    lbl.pack(fill="both", expand=True)
    def _click(e): command()
    def _enter(e): lbl.configure(bg=ACCENT_HOVER); frame.configure(bg=ACCENT_HOVER)
    def _leave(e): lbl.configure(bg=ACCENT);       frame.configure(bg=ACCENT)
    for w in (frame, lbl):
        w.bind("<Button-1>", _click)
        w.bind("<Enter>",    _enter)
        w.bind("<Leave>",    _leave)
    return frame


def make_label(parent, text, **kw):
    return tk.Label(parent, text=text, bg=kw.pop("bg", BG),
                    fg=kw.pop("fg", TEXT), font=kw.pop("font", FONT_BODY), **kw)


def make_entry(parent, textvariable=None, width=30):
    return tk.Entry(parent, textvariable=textvariable, width=width,
                    bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                    relief="flat", font=FONT_BODY)


def make_tree(parent, columns, height=12):
    col_ids = [c[0] for c in columns]
    tree = ttk.Treeview(parent, columns=col_ids, show="headings", height=height)
    tree.tag_configure("odd",  background="#252538")
    tree.tag_configure("even", background=PANEL)
    for col_id, heading, width in columns:
        tree.heading(col_id, text=heading)
        tree.column(col_id, width=width, minwidth=40)
    sb = ttk.Scrollbar(parent, orient="vertical",   command=tree.yview)
    hb = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=sb.set, xscrollcommand=hb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    sb.grid(row=0, column=1, sticky="ns")
    hb.grid(row=1, column=0, sticky="ew")
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    return tree


def center_window(win, w, h):
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


def validate_date(s):
    try:
        parts = s.split("-")
        if len(parts) != 3:
            return False
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        date(y, m, d)
        return True
    except Exception:
        return False


# Enter Project Info


class EnterProjectWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Project Info")
        self.configure(bg=BG)
        self.resizable(False, False)
        center_window(self, 500, 580)
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Add Research Project", font=FONT_H2,
                 bg=ACCENT, fg="white").pack()

        body = tk.Frame(self, bg=BG, padx=32, pady=20)
        body.pack(fill="both", expand=True)

        self._vars = {}
        fields = [
            ("Project Name *",            "project_name"),
            ("Manager First Name *",      "mgr_first"),
            ("Manager Last Name *",       "mgr_last"),
            ("Institute Name *",          "institute"),
            ("Start Date * (YYYY-MM-DD)", "start_date"),
            ("End Date *   (YYYY-MM-DD)", "end_date"),
        ]
        for i, (label, key) in enumerate(fields):
            make_label(body, label, anchor="w").grid(
                row=i, column=0, sticky="w", pady=6)
            v = tk.StringVar()
            self._vars[key] = v
            make_entry(body, textvariable=v, width=28).grid(
                row=i, column=1, padx=(14, 0), pady=6, sticky="w")

        make_label(body, "Project Fields (one per line, optional):",
                   anchor="w").grid(row=len(fields), column=0,
                                    columnspan=2, sticky="w", pady=(14, 2))

        self._fields_text = tk.Text(body, width=40, height=4,
                                    bg=ENTRY_BG, fg=TEXT,
                                    insertbackground=TEXT, relief="flat",
                                    font=FONT_BODY)
        self._fields_text.grid(row=len(fields)+1, column=0,
                                columnspan=2, sticky="ew", pady=(0, 10))

        make_label(body, "e.g. sentiment\npolitical_leaning",
                   fg=SUBTEXT, font=FONT_SMALL, justify="left").grid(
            row=len(fields)+2, column=0, columnspan=2, sticky="w")

        make_button(self, "  Save Project", self._submit).pack(
            fill="x", padx=32, pady=(0, 20))

    def _submit(self):
        vals = {k: v.get().strip() for k, v in self._vars.items()}
        required = [
            ("Project Name",       "project_name"),
            ("Manager First Name", "mgr_first"),
            ("Manager Last Name",  "mgr_last"),
            ("Institute Name",     "institute"),
            ("Start Date",         "start_date"),
            ("End Date",           "end_date"),
        ]
        for label, key in required:
            if not vals[key]:
                messagebox.showerror("Missing Field", f"{label} is required.", parent=self)
                return
        if not validate_date(vals["start_date"]):
            messagebox.showerror("Invalid Date", "Start date must be YYYY-MM-DD.", parent=self)
            return
        if not validate_date(vals["end_date"]):
            messagebox.showerror("Invalid Date", "End date must be YYYY-MM-DD.", parent=self)
            return
        if vals["end_date"] < vals["start_date"]:
            messagebox.showerror("Invalid Date", "End date cannot be before start date.", parent=self)
            return

        field_names = [
            f.strip() for f in self._fields_text.get("1.0", "end").splitlines()
            if f.strip()
        ]

        try:
            conn = get_connection()
            cur  = conn.cursor()

            cur.execute("INSERT IGNORE INTO Institute (institute_name) VALUES (%s)",
                        (vals["institute"],))

            cur.execute("""
                INSERT INTO ResearchProject
                    (project_name, manager_first_name, manager_last_name,
                     institute_name, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (vals["project_name"], vals["mgr_first"], vals["mgr_last"],
                  vals["institute"], vals["start_date"], vals["end_date"]))

            for fname in field_names:
                cur.execute("""
                    INSERT IGNORE INTO Field (field_name, project_name)
                    VALUES (%s, %s)
                """, (fname, vals["project_name"]))

            conn.commit()
            cur.close(); conn.close()
            messagebox.showinfo("Saved",
                f"Project '{vals['project_name']}' added"
                + (f" with {len(field_names)} field(s)." if field_names else "."),
                parent=self)
            for v in self._vars.values():
                v.set("")
            self._fields_text.delete("1.0", "end")

        except Exception as ex:
            messagebox.showerror("Database Error", str(ex), parent=self)


# 2. Enter Analysis Results
# Fixed: dropdown of posts linked to project

class EnterAnalysisWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Enter Analysis Results")
        self.configure(bg=BG)
        self.resizable(False, True)
        center_window(self, 580, 600)
        self._field_entries = {}
        self._post_map = {}   # display string -> post_id
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Enter Analysis Results", font=FONT_H2,
                 bg=ACCENT, fg="white").pack()

        top = tk.Frame(self, bg=BG, padx=28, pady=14)
        top.pack(fill="x")

        # Step 1: project name + load posts button
        make_label(top, "Project Name *", anchor="w").grid(
            row=0, column=0, sticky="w", pady=5)
        self._proj_var = tk.StringVar()
        make_entry(top, textvariable=self._proj_var, width=26).grid(
            row=0, column=1, padx=12, pady=5, sticky="w")
        make_button(top, "  Load Posts", self._load_posts).grid(
            row=0, column=2, padx=8, pady=5)

        # Step 2: dropdown of posts linked to this project
        make_label(top, "Select Post *", anchor="w").grid(
            row=1, column=0, sticky="w", pady=5)
        self._post_var = tk.StringVar()
        self._post_combo = ttk.Combobox(top, textvariable=self._post_var,
                                        width=40, state="readonly",
                                        font=FONT_BODY)
        self._post_combo.grid(row=1, column=1, columnspan=2,
                              padx=12, pady=5, sticky="w")
        self._post_combo.bind("<<ComboboxSelected>>", lambda e: self._load_fields())

        make_label(self, "Fields — leave blank to skip:", anchor="w",
                   fg=SUBTEXT, font=FONT_SMALL).pack(fill="x", padx=28, pady=(4, 0))

        # Scrollable fields area
        outer = tk.Frame(self, bg=ENTRY_BG, bd=0)
        outer.pack(fill="both", expand=True, padx=28, pady=6)

        canvas = tk.Canvas(outer, bg=ENTRY_BG, highlightthickness=0)
        sb     = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self._fields_frame = tk.Frame(canvas, bg=ENTRY_BG)
        self._fields_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self._fields_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        make_button(self, "  Save Results", self._submit).pack(
            fill="x", padx=28, pady=(4, 20))

    def _load_posts(self):
        """Load all posts associated with this project into the dropdown."""
        project = self._proj_var.get().strip()
        if not project:
            messagebox.showerror("Missing Info", "Enter a Project Name first.", parent=self)
            return
        try:
            conn = get_connection()
            cur  = conn.cursor()

            cur.execute("SELECT 1 FROM ResearchProject WHERE project_name = %s", (project,))
            if not cur.fetchone():
                messagebox.showerror("Not Found",
                    f"Project '{project}' not found.", parent=self)
                cur.close(); conn.close()
                return

            cur.execute("""
                SELECT p.post_id, p.username, p.media_name,
                       LEFT(p.content, 50) AS preview
                FROM ProjectPost pp
                JOIN Post p ON pp.post_id = p.post_id
                WHERE pp.project_name = %s
                ORDER BY p.post_id
            """, (project,))
            rows = cur.fetchall()
            cur.close(); conn.close()

            self._post_map.clear()
            for widget in self._fields_frame.winfo_children():
                widget.destroy()
            self._field_entries.clear()

            if not rows:
                messagebox.showinfo("No Posts",
                    f"No posts are linked to '{project}' yet.\n"
                    "Use 'Add Posts to a Project' first.", parent=self)
                self._post_combo["values"] = []
                self._post_var.set("")
                return

            options = []
            for post_id, uname, media, preview in rows:
                label = f"ID {post_id} | {uname}@{media} — {preview}"
                self._post_map[label] = post_id
                options.append(label)

            self._post_combo["values"] = options
            self._post_var.set(options[0])
            self._load_fields()

        except Exception as ex:
            messagebox.showerror("Database Error", str(ex), parent=self)

    def _load_fields(self):
        """Load fields for the selected post and pre-fill any existing values."""
        project  = self._proj_var.get().strip()
        selected = self._post_var.get()
        post_id  = self._post_map.get(selected)
        if not post_id:
            return

        try:
            conn = get_connection()
            cur  = conn.cursor()

            cur.execute(
                "SELECT field_name FROM Field WHERE project_name = %s ORDER BY field_name",
                (project,))
            fields = [r[0] for r in cur.fetchall()]

            cur.execute("""
                SELECT field_name, result_value FROM AnalysisResult
                WHERE project_name = %s AND post_id = %s
            """, (project, post_id))
            existing = {r[0]: r[1] for r in cur.fetchall()}
            cur.close(); conn.close()

            for w in self._fields_frame.winfo_children():
                w.destroy()
            self._field_entries.clear()

            if not fields:
                make_label(self._fields_frame,
                    "No fields defined for this project.\n"
                    "Add fields in 'Add Project Info' first.",
                    fg=SUBTEXT, bg=ENTRY_BG).pack(pady=12)
                return

            for i, fname in enumerate(fields):
                make_label(self._fields_frame, fname, width=22,
                    anchor="w", bg=ENTRY_BG).grid(
                    row=i, column=0, padx=10, pady=4, sticky="w")
                e = make_entry(self._fields_frame, width=28)
                e.grid(row=i, column=1, padx=10, pady=4)
                if fname in existing:
                    e.insert(0, existing[fname])
                self._field_entries[fname] = e

        except Exception as ex:
            messagebox.showerror("Database Error", str(ex), parent=self)

    def _submit(self):
        project  = self._proj_var.get().strip()
        selected = self._post_var.get()
        post_id  = self._post_map.get(selected)

        if not project:
            messagebox.showerror("Missing Info", "Enter a Project Name.", parent=self)
            return
        if not post_id:
            messagebox.showerror("Missing Info",
                "Load posts and select one first.", parent=self)
            return
        if not self._field_entries:
            messagebox.showerror("No Fields",
                "No fields to save. This project has no fields defined.", parent=self)
            return

        filled = {f: e.get().strip()
                  for f, e in self._field_entries.items() if e.get().strip()}
        if not filled:
            messagebox.showwarning("Nothing to Save",
                "No field values were entered.", parent=self)
            return

        try:
            conn = get_connection()
            cur  = conn.cursor()

            cur.execute("""
                INSERT IGNORE INTO ProjectPost (project_name, post_id)
                VALUES (%s, %s)
            """, (project, post_id))

            for fname, val in filled.items():
                cur.execute("""
                    INSERT INTO AnalysisResult
                        (project_name, post_id, field_name, result_value)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE result_value = VALUES(result_value)
                """, (project, post_id, fname, val))

            conn.commit()
            cur.close(); conn.close()
            messagebox.showinfo("Saved", f"{len(filled)} result(s) saved.", parent=self)

        except Exception as ex:
            messagebox.showerror("Database Error", str(ex), parent=self)



# 3. Search Posts by Username & Platform
# Fixed: projects from ProjectPost, full content popup on row click


class SearchByUsernameWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Search Posts by Username & Platform")
        self.configure(bg=BG)
        self.resizable(True, True)
        center_window(self, 920, 520)
        self._rows = []
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Search by Username & Platform", font=FONT_H2,
                 bg=ACCENT, fg="white").pack()

        sf = tk.Frame(self, bg=PANEL, pady=12, padx=20)
        sf.pack(fill="x")

        make_label(sf, "Username *", bg=PANEL).grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        self._user_var = tk.StringVar()
        make_entry(sf, textvariable=self._user_var, width=22).grid(
            row=0, column=1, padx=(0, 20))

        make_label(sf, "Platform *", bg=PANEL).grid(
            row=0, column=2, sticky="w", padx=(0, 8))
        self._plat_var = tk.StringVar()
        make_entry(sf, textvariable=self._plat_var, width=22).grid(
            row=0, column=3, padx=(0, 16))

        make_button(sf, "  Search", self._search).grid(row=0, column=4)

        make_label(sf, "Click a row to view full post content.",
                   bg=PANEL, fg=SUBTEXT, font=FONT_SMALL).grid(
            row=1, column=0, columnspan=5, sticky="w", pady=(4, 0))

        self._status_var = tk.StringVar(
            value="Enter username and platform, then press Search.")
        tk.Label(self, textvariable=self._status_var, font=FONT_SMALL,
                 bg=BG, fg=SUBTEXT, anchor="w").pack(fill="x", padx=16, pady=(6, 0))

        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self._tree = make_tree(tree_frame, [
            ("post_id",  "Post ID",         70),
            ("platform", "Platform",        120),
            ("username", "Username",        130),
            ("post_time","Posted At",       150),
            ("projects", "Projects",        180),
            ("content",  "Content Preview", 240),
        ])
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

    def _search(self):
        username = self._user_var.get().strip()
        platform = self._plat_var.get().strip()
        if not username or not platform:
            messagebox.showerror("Missing Fields",
                "Both Username and Platform are required.", parent=self)
            return
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT p.post_id, p.media_name, p.username, p.post_time,
                       GROUP_CONCAT(DISTINCT pp.project_name
                                    ORDER BY pp.project_name SEPARATOR ', ') AS projects,
                       p.content
                FROM Post p
                LEFT JOIN ProjectPost pp ON pp.post_id = p.post_id
                WHERE p.username = %s AND p.media_name = %s
                GROUP BY p.post_id
                ORDER BY p.post_time DESC
            """, (username, platform))
            self._rows = cur.fetchall()
            cur.close(); conn.close()

            self._tree.delete(*self._tree.get_children())
            for i, (pid, media, uname, ptime, projs, content) in enumerate(self._rows):
                tag = "odd" if i % 2 else "even"
                preview = (content[:80] + "…") if content and len(content) > 80 else (content or "")
                self._tree.insert("", "end", tags=(tag,), values=(
                    pid, media, uname,
                    str(ptime) if ptime else "",
                    projs or "(none)",
                    preview
                ))
            self._status_var.set(f"{len(self._rows)} post(s) found.")
        except Exception as ex:
            messagebox.showerror("Database Error", str(ex), parent=self)

    def _on_select(self, _event):
        sel = self._tree.selection()
        if not sel:
            return
        idx = self._tree.index(sel[0])
        if idx >= len(self._rows):
            return
        pid, media, uname, ptime, projs, content = self._rows[idx]
        popup = tk.Toplevel(self)
        popup.title(f"Post {pid} — Full Content")
        popup.configure(bg=BG)
        center_window(popup, 500, 340)
        tk.Label(popup, text=f"Post ID {pid} | {uname}@{media} | {ptime}",
                 bg=ACCENT, fg="white", font=FONT_BODY, pady=8).pack(fill="x")
        tk.Label(popup, text=f"Projects: {projs or '(none)'}",
                 bg=PANEL, fg=SUBTEXT, font=FONT_SMALL, pady=4).pack(fill="x")
        txt = tk.Text(popup, bg=ENTRY_BG, fg=TEXT, font=FONT_BODY,
                      wrap="word", padx=12, pady=8, relief="flat")
        txt.insert("1.0", content or "")
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=12, pady=8)


# 4. Search Posts by Person's First / Last Name
# Fixed: ProjectPost for projects, NULL name handling, full content popup

class SearchByNameWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Search Posts by Person Name")
        self.configure(bg=BG)
        self.resizable(True, True)
        center_window(self, 960, 520)
        self._rows = []
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=ACCENT, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Search by Poster's First / Last Name", font=FONT_H2,
                 bg=ACCENT, fg="white").pack()

        sf = tk.Frame(self, bg=PANEL, pady=12, padx=20)
        sf.pack(fill="x")

        make_label(sf, "First Name", bg=PANEL).grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        self._first_var = tk.StringVar()
        make_entry(sf, textvariable=self._first_var, width=20).grid(
            row=0, column=1, padx=(0, 20))

        make_label(sf, "Last Name", bg=PANEL).grid(
            row=0, column=2, sticky="w", padx=(0, 8))
        self._last_var = tk.StringVar()
        make_entry(sf, textvariable=self._last_var, width=20).grid(
            row=0, column=3, padx=(0, 16))

        make_button(sf, "  Search", self._search).grid(row=0, column=4)

        make_label(sf,
            "(at least one name required) — Click a row to view full content.",
            bg=PANEL, fg=SUBTEXT, font=FONT_SMALL).grid(
            row=1, column=0, columnspan=5, sticky="w", pady=(4, 0))

        self._status_var = tk.StringVar(value="Enter a first name, last name, or both.")
        tk.Label(self, textvariable=self._status_var, font=FONT_SMALL,
                 bg=BG, fg=SUBTEXT, anchor="w").pack(fill="x", padx=16, pady=(6, 0))

        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self._tree = make_tree(tree_frame, [
            ("post_id",     "Post ID",       65),
            ("platform",    "Platform",      110),
            ("username",    "Username",      120),
            ("poster_name", "Poster Name",   130),
            ("post_time",   "Posted At",     140),
            ("projects",    "Projects",      150),
            ("content",     "Content Preview", 200),
        ])
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

    def _search(self):
        first = self._first_var.get().strip()
        last  = self._last_var.get().strip()
        if not first and not last:
            messagebox.showerror("Missing Fields",
                "Enter at least a first or last name.", parent=self)
            return

        conditions, params = [], []
        if first:
            conditions.append("ua.first_name LIKE %s")
            params.append(f"%{first}%")
        if last:
            conditions.append("ua.last_name LIKE %s")
            params.append(f"%{last}%")
        where = " AND ".join(conditions)

        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute(f"""
                SELECT p.post_id, p.media_name, p.username,
                       TRIM(CONCAT(COALESCE(ua.first_name, ''), ' ',
                                   COALESCE(ua.last_name,  ''))) AS poster_name,
                       p.post_time,
                       GROUP_CONCAT(DISTINCT pp.project_name
                                    ORDER BY pp.project_name SEPARATOR ', ') AS projects,
                       p.content
                FROM Post p
                JOIN UserAccount ua
                  ON ua.username = p.username AND ua.media_name = p.media_name
                LEFT JOIN ProjectPost pp ON pp.post_id = p.post_id
                WHERE {where}
                GROUP BY p.post_id
                ORDER BY p.post_time DESC
            """, params)
            self._rows = cur.fetchall()
            cur.close(); conn.close()

            self._tree.delete(*self._tree.get_children())
            for i, (pid, media, uname, pname, ptime, projs, content) in enumerate(self._rows):
                tag = "odd" if i % 2 else "even"
                preview = (content[:75] + "…") if content and len(content) > 75 else (content or "")
                self._tree.insert("", "end", tags=(tag,), values=(
                    pid, media, uname,
                    pname or "(no name)",
                    str(ptime) if ptime else "",
                    projs or "(none)",
                    preview
                ))
            self._status_var.set(f"{len(self._rows)} post(s) found.")
        except Exception as ex:
            messagebox.showerror("Database Error", str(ex), parent=self)

    def _on_select(self, _event):
        sel = self._tree.selection()
        if not sel:
            return
        idx = self._tree.index(sel[0])
        if idx >= len(self._rows):
            return
        pid, media, uname, pname, ptime, projs, content = self._rows[idx]
        popup = tk.Toplevel(self)
        popup.title(f"Post {pid} — Full Content")
        popup.configure(bg=BG)
        center_window(popup, 500, 340)
        tk.Label(popup, text=f"Post ID {pid} | {uname}@{media} | {ptime}",
                 bg=ACCENT, fg="white", font=FONT_BODY, pady=8).pack(fill="x")
        tk.Label(popup,
                 text=f"Poster: {pname or '(no name)'} | Projects: {projs or '(none)'}",
                 bg=PANEL, fg=SUBTEXT, font=FONT_SMALL, pady=4).pack(fill="x")
        txt = tk.Text(popup, bg=ENTRY_BG, fg=TEXT, font=FONT_BODY,
                      wrap="word", padx=12, pady=8, relief="flat")
        txt.insert("1.0", content or "")
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=12, pady=8)

