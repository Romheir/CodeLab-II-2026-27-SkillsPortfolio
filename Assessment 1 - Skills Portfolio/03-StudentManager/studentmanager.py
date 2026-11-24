import tkinter as tk # standard gui library
from tkinter import ttk, messagebox # styled table widget and dialogs
import os # dynamic file path handling

THEMES = { # professional obsidian dark and alabaster light palettes
    "dark": {
        "bg": "#0B0F19", "card": "#111827", "surface": "#1E293B", "surface_hover": "#334155",
        "border": "#1F2937", "fg": "#F9FAFB", "muted": "#9CA3AF",
        "accent": "#3B82F6", "accent_hover": "#2563EB", "accent_fg": "#FFFFFF",
        "row_even": "#111827", "row_odd": "#161F30", "select": "#1D4ED8", "select_fg": "#FFFFFF",
        "entry_bg": "#0F172A"
    },
    "light": {
        "bg": "#F8FAFC", "card": "#FFFFFF", "surface": "#F1F5F9", "surface_hover": "#E2E8F0",
        "border": "#E2E8F0", "fg": "#0F172A", "muted": "#64748B",
        "accent": "#2563EB", "accent_hover": "#1D4ED8", "accent_fg": "#FFFFFF",
        "row_even": "#FFFFFF", "row_odd": "#F8FAFC", "select": "#DBEAFE", "select_fg": "#0F172A",
        "entry_bg": "#FFFFFF"
    }
}

GRADE_COLORS = {"A": "#10B981", "B": "#3B82F6", "C": "#6366F1", "D": "#F59E0B", "F": "#EF4444"} # refined chart accents

class StudentManagerApp: # encapsulates professional dashboard ui and student crud logic
    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager Dashboard")
        self.root.geometry("1000x680")
        self.root.minsize(880, 620) # prevents widget crowding on small screens
        self.set_ledger_icon() # applies custom generated executive window icon
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", lambda e: self.set_fullscreen(False))

        self.theme_mode = "dark" # defaults to obsidian dark mode
        self.sort_desc = True # toggles ascending/descending sort
        self.file_path = os.path.join(os.path.dirname(__file__), "studentMarks.txt") # dynamic data path
        self.students = []
        self.current_view = [] # tracks currently displayed subset for column sorting
        self.style = ttk.Style()
        self.style.theme_use("clam") # enables full cross-platform treeview styling

        self.load_data()
        self.build_ui()
        self.apply_theme()
        self.view_all()

    def set_ledger_icon(self): # generates a crisp 32x32 executive ledger icon with zero external files
        icon = tk.PhotoImage(width=32, height=32)
        icon.put("#0B0F19", to=(0, 0, 32, 32)) # obsidian base
        icon.put("#3B82F6", to=(0, 0, 32, 3)) # executive blue top accent
        icon.put("#1E293B", to=(2, 5, 30, 30)) # slate inner panel
        icon.put("#F9FAFB", to=(6, 9, 26, 12)) # header bar
        icon.put("#9CA3AF", to=(6, 15, 20, 17)) # row line 1
        icon.put("#9CA3AF", to=(6, 20, 26, 22)) # row line 2
        icon.put("#9CA3AF", to=(6, 25, 17, 27)) # row line 3
        self.icon_ref = icon # keeps reference so tkinter does not garbage collect icon
        self.root.iconphoto(True, self.icon_ref)

    def c(self, key): # helper for active theme color
        return THEMES[self.theme_mode][key]

    def toggle_fullscreen(self, event=None): # toggles true fullscreen with F11
        self.set_fullscreen(not self.is_fullscreen)

    def set_fullscreen(self, state): # sets fullscreen state safely
        self.is_fullscreen = state
        self.root.attributes("-fullscreen", state)

    def load_data(self): # parses studentMarks.txt into list of dictionaries
        self.students = []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                for line in lines[1:]: # skips line 1 student count
                    p = line.split(",")
                    self.students.append({
                        "code": int(p[0]), "name": p[1],
                        "cw": [int(p[2]), int(p[3]), int(p[4])], "exam": int(p[5])
                    })
        except FileNotFoundError:
            messagebox.showerror("Error", "studentMarks.txt not found.")

    def save_data(self): # persists changes and updated count back to studentMarks.txt
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(f"{len(self.students)}\n") # updates line 1 count
            for s in self.students:
                f.write(f"{s['code']},{s['name']},{s['cw'][0]},{s['cw'][1]},{s['cw'][2]},{s['exam']}\n")

    def calc_stats(self, s): # computes coursework total, percentage out of 160, and grade
        cw_total = sum(s["cw"])
        pct = ((cw_total + s["exam"]) / 160) * 100
        if pct >= 70: grade = "A"
        elif pct >= 60: grade = "B"
        elif pct >= 50: grade = "C"
        elif pct >= 40: grade = "D"
        else: grade = "F"
        return cw_total, pct, grade

    def set_status(self, text): # updates bottom status bar message
        if hasattr(self, "status_lbl"):
            self.status_lbl.config(text=text)

    def bind_hover(self, btn, is_primary=False): # attaches smooth theme-aware hover transitions
        def on_enter(e):
            btn.config(bg=self.c("accent_hover") if is_primary else self.c("surface_hover"))
        def on_leave(e):
            btn.config(bg=self.c("accent") if is_primary else self.c("surface"))
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def build_ui(self): # constructs responsive grid-based dashboard layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1) # allows table section to expand cleanly on resize

        # row 0: header bar
        self.header = tk.Frame(self.root)
        self.header.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 10))
        self.title_lbl = tk.Label(self.header, text="STUDENT MANAGER", font=("Segoe UI", 15, "bold"))
        self.title_lbl.pack(side="left")

        self.theme_btn = tk.Button(self.header, text="☀ Light Mode", command=self.toggle_theme, relief="flat", font=("Segoe UI", 9, "bold"), padx=12, pady=5, cursor="hand2", bd=0)
        self.theme_btn.pack(side="right", padx=(8, 0))
        self.bind_hover(self.theme_btn, False)

        self.fs_btn = tk.Button(self.header, text="⛶ F11", command=self.toggle_fullscreen, relief="flat", font=("Segoe UI", 9, "bold"), padx=10, pady=5, cursor="hand2", bd=0)
        self.fs_btn.pack(side="right", padx=(8, 0))
        self.bind_hover(self.fs_btn, False)

        self.search_var = tk.StringVar() # live search filter
        self.search_var.trace_add("write", lambda *args: self.filter_search())
        self.search_entry = tk.Entry(self.header, textvariable=self.search_var, font=("Segoe UI", 10), width=24, relief="flat", highlightthickness=1)
        self.search_entry.pack(side="right", padx=(8, 4), ipady=4)
        self.search_lbl = tk.Label(self.header, text="SEARCH", font=("Segoe UI", 8, "bold"))
        self.search_lbl.pack(side="right")

        # row 1: 4 live kpi summary cards using equal-weight grid columns
        self.kpi_frame = tk.Frame(self.root)
        self.kpi_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=4)
        self.kpi_cards, self.kpi_vals, self.kpi_titles = [], {}, []
        kpi_defs = [("total", "TOTAL STUDENTS"), ("avg", "CLASS AVERAGE"), ("high", "HIGHEST SCORE"), ("pass", "PASS RATE (40%+)")]
        for idx, (key, label) in enumerate(kpi_defs):
            self.kpi_frame.columnconfigure(idx, weight=1, uniform="kpi") # locks equal card widths at all aspect ratios
            card = tk.Frame(self.kpi_frame, padx=16, pady=12, highlightthickness=1)
            card.grid(row=0, column=idx, sticky="ew", padx=4)
            t = tk.Label(card, text=label, font=("Segoe UI", 8, "bold"))
            t.pack(anchor="w")
            v = tk.Label(card, text="--", font=("Segoe UI", 17, "bold"))
            v.pack(anchor="w", pady=(2, 0))
            self.kpi_cards.append(card)
            self.kpi_titles.append(t)
            self.kpi_vals[key] = v

        # row 2: all 8 menu options in 2 equal-width rows
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        actions = [
            ("1. View All", self.view_all, True), ("2. View Individual", self.view_one, False),
            ("3. Highest Score", self.view_highest, False), ("4. Lowest Score", self.view_lowest, False),
            ("5. Sort Asc/Desc", self.sort_records, False), ("6. Add Student", self.add_student, True),
            ("7. Delete Selected", self.delete_student, False), ("8. Update Selected", self.update_student, False)
        ]
        self.action_btns = []
        for i, (txt, cmd, is_primary) in enumerate(actions):
            self.btn_frame.columnconfigure(i % 4, weight=1, uniform="btn") # equal button widths at all aspect ratios
            b = tk.Button(self.btn_frame, text=txt, command=cmd, relief="flat", font=("Segoe UI", 9, "bold"), pady=8, cursor="hand2", bd=0)
            b.is_primary = is_primary
            self.bind_hover(b, is_primary)
            b.grid(row=i // 4, column=i % 4, sticky="ew", padx=4, pady=3)
            self.action_btns.append(b)

        # row 3: responsive student records table
        self.table_frame = tk.Frame(self.root, highlightthickness=1)
        self.table_frame.grid(row=3, column=0, sticky="nsew", padx=24, pady=(2, 10))
        cols = ("code", "name", "cw", "exam", "pct", "grade")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings")
        headings = [
            ("code", "Student #", 95, 80), ("name", "Student Name", 240, 160),
            ("cw", "Coursework (/60)", 130, 100), ("exam", "Exam (/100)", 110, 90),
            ("pct", "Overall %", 110, 90), ("grade", "Grade", 85, 70)
        ]
        for col, text, w, mw in headings:
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_by_column(c)) # clickable column sort
            self.tree.column(col, width=w, minwidth=mw, stretch=True, anchor="center" if col != "name" else "w")
        self.tree.bind("<Double-1>", lambda e: self.view_one()) # double-click row to inspect record
        scroll = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # row 4: responsive grade distribution chart
        self.chart_frame = tk.Frame(self.root, padx=16, pady=10, highlightthickness=1)
        self.chart_frame.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 8))
        self.chart_lbl = tk.Label(self.chart_frame, text="GRADE DISTRIBUTION (A – F)", font=("Segoe UI", 8, "bold"))
        self.chart_lbl.pack(anchor="w")
        self.chart_canvas = tk.Canvas(self.chart_frame, height=96, highlightthickness=0)
        self.chart_canvas.pack(fill="x", pady=(4, 0))
        self.chart_canvas.bind("<Configure>", lambda e: self.draw_chart()) # rescales bars cleanly on any resize

        # row 5: status bar
        self.status_lbl = tk.Label(self.root, text="Ready  •  Double-click any row to view full record", font=("Segoe UI", 8), anchor="w")
        self.status_lbl.grid(row=5, column=0, sticky="ew", padx=26, pady=(0, 12))

    def apply_theme(self): # styles all widgets, treeview, and zebra rows for active mode
        self.root.configure(bg=self.c("bg"))
        for f in (self.header, self.kpi_frame, self.btn_frame): f.configure(bg=self.c("bg"))
        self.title_lbl.configure(bg=self.c("bg"), fg=self.c("fg"))
        self.search_lbl.configure(bg=self.c("bg"), fg=self.c("muted"))
        self.search_entry.configure(bg=self.c("entry_bg"), fg=self.c("fg"), insertbackground=self.c("fg"), highlightbackground=self.c("border"), highlightcolor=self.c("accent"))
        self.theme_btn.configure(text="☀ Light Mode" if self.theme_mode == "dark" else "🌙 Dark Mode", bg=self.c("surface"), fg=self.c("fg"), activebackground=self.c("surface_hover"), activeforeground=self.c("fg"))
        self.fs_btn.configure(bg=self.c("surface"), fg=self.c("fg"), activebackground=self.c("surface_hover"), activeforeground=self.c("fg"))
        self.status_lbl.configure(bg=self.c("bg"), fg=self.c("muted"))

        for card in self.kpi_cards: card.configure(bg=self.c("card"), highlightbackground=self.c("border"))
        for t in self.kpi_titles: t.configure(bg=self.c("card"), fg=self.c("muted"))
        for v in self.kpi_vals.values(): v.configure(bg=self.c("card"), fg=self.c("fg"))

        for b in self.action_btns:
            if b.is_primary:
                b.configure(bg=self.c("accent"), fg=self.c("accent_fg"), activebackground=self.c("accent_hover"), activeforeground=self.c("accent_fg"))
            else:
                b.configure(bg=self.c("surface"), fg=self.c("fg"), activebackground=self.c("surface_hover"), activeforeground=self.c("fg"))

        self.table_frame.configure(bg=self.c("card"), highlightbackground=self.c("border"))
        self.chart_frame.configure(bg=self.c("card"), highlightbackground=self.c("border"))
        self.chart_lbl.configure(bg=self.c("card"), fg=self.c("muted"))
        self.chart_canvas.configure(bg=self.c("card"))

        self.style.configure("Treeview", background=self.c("card"), foreground=self.c("fg"), fieldbackground=self.c("card"), rowheight=28, font=("Segoe UI", 10), borderwidth=0)
        self.style.configure("Treeview.Heading", background=self.c("surface"), foreground=self.c("fg"), font=("Segoe UI", 9, "bold"), relief="flat", padding=(6, 6))
        self.style.map("Treeview", background=[("selected", self.c("select"))], foreground=[("selected", self.c("select_fg"))])
        self.style.map("Treeview.Heading", background=[("active", self.c("surface_hover"))])
        self.tree.tag_configure("even", background=self.c("row_even"))
        self.tree.tag_configure("odd", background=self.c("row_odd"))
        self.draw_chart()

    def toggle_theme(self): # switches between obsidian dark and alabaster light modes
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.apply_theme()

    def refresh_table(self, records): # populates treeview with zebra striping, updates kpis and chart
        self.current_view = list(records)
        for row in self.tree.get_children(): self.tree.delete(row)
        for idx, s in enumerate(records):
            cw, pct, grade = self.calc_stats(s)
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert("", "end", iid=str(s["code"]), tags=(tag,),
                             values=(s["code"], s["name"], f"{cw} / 60", f"{s['exam']} / 100", f"{pct:.2f}%", grade))
        self.update_kpis()
        self.draw_chart()

    def update_kpis(self): # refreshes top 4 summary cards
        if not self.students:
            for v in self.kpi_vals.values(): v.config(text="0")
            return
        pcts = [self.calc_stats(s)[1] for s in self.students]
        passed = sum(1 for p in pcts if p >= 40)
        self.kpi_vals["total"].config(text=str(len(self.students)))
        self.kpi_vals["avg"].config(text=f"{sum(pcts)/len(pcts):.1f}%")
        self.kpi_vals["high"].config(text=f"{max(pcts):.1f}%")
        self.kpi_vals["pass"].config(text=f"{(passed/len(self.students))*100:.0f}%")

    def draw_chart(self): # draws responsive grade distribution bars scaled to current canvas dimensions
        self.chart_canvas.delete("all")
        w = max(self.chart_canvas.winfo_width(), 600)
        h = max(self.chart_canvas.winfo_height(), 96)
        base_y = h - 22 # baseline for bars
        max_bar_h = max(h - 46, 20) # leaves room for count labels above and grade labels below

        counts = {g: 0 for g in ("A", "B", "C", "D", "F")}
        for s in self.students: counts[self.calc_stats(s)[2]] += 1
        max_c = max(counts.values()) if counts.values() and max(counts.values()) > 0 else 1

        self.chart_canvas.create_line(16, base_y, w - 16, base_y, fill=self.c("border"), width=1) # baseline rule
        slot_w = (w - 32) / 5
        bar_w = min(slot_w * 0.5, 120)
        for i, g in enumerate(("A", "B", "C", "D", "F")):
            cx = 16 + slot_w * i + slot_w / 2
            x0, x1 = cx - bar_w / 2, cx + bar_w / 2
            bar_h = int((counts[g] / max_c) * max_bar_h)
            if bar_h > 0:
                self.chart_canvas.create_rectangle(x0, base_y - bar_h, x1, base_y, fill=GRADE_COLORS[g], width=0)
            self.chart_canvas.create_text(cx, base_y - bar_h - 10, text=str(counts[g]), fill=self.c("fg"), font=("Segoe UI", 9, "bold"))
            self.chart_canvas.create_text(cx, h - 10, text=f"Grade {g}", fill=self.c("muted"), font=("Segoe UI", 9))

    def filter_search(self): # filters table live as user types
        q = self.search_var.get().strip().lower()
        if not q:
            self.refresh_table(self.students)
            self.set_status(f"Showing all {len(self.students)} student records  •  Double-click any row for details")
            return
        filtered = [s for s in self.students if q in s["name"].lower() or q in str(s["code"])]
        self.refresh_table(filtered)
        self.set_status(f"Filter '{q}': {len(filtered)} matching record(s)")

    def sort_by_column(self, col): # sorts current table view when clicking a column header
        self.sort_desc = not self.sort_desc
        key_map = {
            "code": lambda s: s["code"], "name": lambda s: s["name"].lower(),
            "cw": lambda s: sum(s["cw"]), "exam": lambda s: s["exam"],
            "pct": lambda s: sum(s["cw"]) + s["exam"], "grade": lambda s: sum(s["cw"]) + s["exam"]
        }
        ordered = sorted(self.current_view, key=key_map[col], reverse=self.sort_desc)
        self.refresh_table(ordered)
        self.set_status(f"Sorted by {col.upper()} ({'Descending' if self.sort_desc else 'Ascending'})")

    def get_selected_student(self): # returns student dict for clicked table row
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select a Student", "Click a student row in the table first.")
            return None
        code = int(sel[0])
        return next((s for s in self.students if s["code"] == code), None)

    def view_all(self): # option 1 shows all records
        self.search_var.set("")
        self.refresh_table(self.students)
        self.set_status(f"Loaded {len(self.students)} records from studentMarks.txt  •  Double-click any row for details")

    def view_one(self): # option 2 shows detailed card for selected student
        s = self.get_selected_student()
        if not s: return
        cw, pct, grade = self.calc_stats(s)
        msg = (f"Name: {s['name']}\nStudent Number: {s['code']}\n"
               f"Coursework Marks: {s['cw']}  (Total: {cw}/60)\n"
               f"Exam Mark: {s['exam']}/100\nOverall Percentage: {pct:.2f}%\nGrade: {grade}")
        messagebox.showinfo("Individual Student Record", msg)

    def view_highest(self): # option 3 isolates highest scoring student
        if not self.students: return
        top = max(self.students, key=lambda s: sum(s["cw"]) + s["exam"])
        self.refresh_table([top])
        self.set_status(f"Highest overall mark: {top['name']} ({top['code']})")

    def view_lowest(self): # option 4 isolates lowest scoring student
        if not self.students: return
        low = min(self.students, key=lambda s: sum(s["cw"]) + s["exam"])
        self.refresh_table([low])
        self.set_status(f"Lowest overall mark: {low['name']} ({low['code']})")

    def sort_records(self): # option 5 toggles ascending / descending sort by total score
        self.sort_desc = not self.sort_desc
        ordered = sorted(self.students, key=lambda s: sum(s["cw"]) + s["exam"], reverse=self.sort_desc)
        self.refresh_table(ordered)
        self.set_status(f"Sorted all records by Overall Score ({'Descending' if self.sort_desc else 'Ascending'})")

    def open_student_form(self, student=None): # unified modal form centered over main window for add (6) and update (8)
        win = tk.Toplevel(self.root)
        win.title("Update Student" if student else "Add Student")
        win.resizable(False, False)
        win.configure(bg=self.c("card"))
        win.transient(self.root)
        win.grab_set() # locks focus to modal form

        w, h = 360, 345
        rx = self.root.winfo_rootx() + (self.root.winfo_width() - w) // 2
        ry = self.root.winfo_rooty() + (self.root.winfo_height() - h) // 2
        win.geometry(f"{w}x{h}+{max(rx, 0)}+{max(ry, 0)}") # centers modal cleanly on any monitor ratio

        fields = [("Student Code (1000-9999):", str(student["code"]) if student else ""),
                  ("Full Name:", student["name"] if student else ""),
                  ("Coursework 1 (0-20):", str(student["cw"][0]) if student else ""),
                  ("Coursework 2 (0-20):", str(student["cw"][1]) if student else ""),
                  ("Coursework 3 (0-20):", str(student["cw"][2]) if student else ""),
                  ("Exam Mark (0-100):", str(student["exam"]) if student else "")]
        entries = []
        for lbl, default in fields:
            row = tk.Frame(win, bg=self.c("card"))
            row.pack(fill="x", padx=24, pady=7)
            tk.Label(row, text=lbl, font=("Segoe UI", 9), bg=self.c("card"), fg=self.c("fg")).pack(side="left")
            e = tk.Entry(row, width=17, bg=self.c("entry_bg"), fg=self.c("fg"), insertbackground=self.c("fg"),
                         relief="flat", highlightthickness=1, highlightbackground=self.c("border"), highlightcolor=self.c("accent"))
            e.insert(0, default)
            e.pack(side="right", ipady=3)
            entries.append(e)

        def submit(): # validates ranges and saves record
            try:
                code = int(entries[0].get().strip())
                name = entries[1].get().strip()
                cw = [int(entries[2].get().strip()), int(entries[3].get().strip()), int(entries[4].get().strip())]
                exam = int(entries[5].get().strip())
                if not (1000 <= code <= 9999) or not name or any(not (0 <= m <= 20) for m in cw) or not (0 <= exam <= 100):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Input", "Check ranges: Code 1000-9999, CW 0-20, Exam 0-100, non-empty Name.", parent=win)
                return

            if student:
                student.update({"code": code, "name": name, "cw": cw, "exam": exam})
                action = f"Updated {name} ({code}) and saved to studentMarks.txt"
            else:
                if any(s["code"] == code for s in self.students):
                    messagebox.showerror("Duplicate", "That student code already exists.", parent=win)
                    return
                self.students.append({"code": code, "name": name, "cw": cw, "exam": exam})
                action = f"Added {name} ({code}) and saved to studentMarks.txt"
            self.save_data()
            self.view_all()
            self.set_status(action)
            win.destroy()

        save_btn = tk.Button(win, text="Save Record", command=submit, bg=self.c("accent"), fg=self.c("accent_fg"),
                             activebackground=self.c("accent_hover"), activeforeground=self.c("accent_fg"),
                             relief="flat", font=("Segoe UI", 10, "bold"), pady=8, width=18, cursor="hand2", bd=0)
        self.bind_hover(save_btn, True)
        save_btn.pack(pady=16)

    def add_student(self): # option 6 launches empty add modal
        self.open_student_form(None)

    def delete_student(self): # option 7 deletes selected row after confirmation
        s = self.get_selected_student()
        if not s: return
        if messagebox.askyesno("Confirm Delete", f"Delete {s['name']} ({s['code']})?"):
            self.students.remove(s)
            self.save_data()
            self.view_all()
            self.set_status(f"Deleted {s['name']} ({s['code']}) and updated studentMarks.txt")

    def update_student(self): # option 8 launches pre-filled update modal
        s = self.get_selected_student()
        if s: self.open_student_form(s)

if __name__ == "__main__":
    root = tk.Tk()
    StudentManagerApp(root)
    root.mainloop()