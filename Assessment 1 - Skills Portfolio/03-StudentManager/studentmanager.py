import tkinter as tk # standard gui library
from tkinter import ttk, messagebox # styled table widget and dialogs
import os # dynamic file path handling

THEMES = { # refined pitch black and pitch white monochrome palettes
    "dark": {
        "bg": "#000000", "card": "#0D0D0D", "border": "#262626", "fg": "#FFFFFF",
        "muted": "#A3A3A3", "btn": "#171717", "btn_hover": "#2A2A2A", "btn_fg": "#FFFFFF",
        "primary": "#FFFFFF", "primary_fg": "#000000", "row_even": "#0D0D0D",
        "row_odd": "#141414", "select": "#333333", "entry_bg": "#000000"
    },
    "light": {
        "bg": "#FFFFFF", "card": "#F5F5F5", "border": "#D4D4D4", "fg": "#000000",
        "muted": "#525252", "btn": "#E5E5E5", "btn_hover": "#D4D4D4", "btn_fg": "#000000",
        "primary": "#000000", "primary_fg": "#FFFFFF", "row_even": "#FFFFFF",
        "row_odd": "#F5F5F5", "select": "#D4D4D4", "entry_bg": "#FFFFFF"
    }
}

GRADE_COLORS = {"A": "#22C55E", "B": "#38BDF8", "C": "#818CF8", "D": "#F59E0B", "F": "#EF4444"} # refined chart accents

class StudentManagerApp: # encapsulates monochrome dashboard ui and student crud logic
    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager Dashboard")
        self.root.geometry("960x660")
        self.root.minsize(820, 600) # allows resizing and fullscreen cleanly
        self.set_ledger_icon() # applies custom generated monochrome window icon
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", lambda e: self.set_fullscreen(False))

        self.theme_mode = "dark" # defaults to pitch black mode
        self.sort_desc = True # toggles ascending/descending sort
        self.file_path = os.path.join(os.path.dirname(__file__), "studentMarks.txt") # dynamic data path
        self.students = []
        self.current_view = [] # tracks currently displayed subset for column sorting
        self.style = ttk.Style()
        self.style.theme_use("clam") # enables full monochrome treeview styling

        self.load_data()
        self.build_ui()
        self.apply_theme()
        self.view_all()

    def set_ledger_icon(self): # generates a crisp 32x32 monochrome ledger icon with zero external files
        icon = tk.PhotoImage(width=32, height=32)
        icon.put("#000000", to=(0, 0, 32, 32)) # pitch black base
        icon.put("#FFFFFF", to=(2, 2, 30, 4)) # top white frame
        icon.put("#FFFFFF", to=(2, 28, 30, 30)) # bottom white frame
        icon.put("#FFFFFF", to=(2, 2, 4, 30)) # left white frame
        icon.put("#FFFFFF", to=(28, 2, 30, 30)) # right white frame
        icon.put("#FFFFFF", to=(7, 8, 25, 11)) # header bar
        icon.put("#A3A3A3", to=(7, 14, 21, 16)) # row line 1
        icon.put("#A3A3A3", to=(7, 19, 25, 21)) # row line 2
        icon.put("#A3A3A3", to=(7, 24, 18, 26)) # row line 3
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

    def build_ui(self): # constructs header, kpi cards, action bar, table, chart, and status bar
        self.header = tk.Frame(self.root)
        self.header.pack(fill="x", padx=22, pady=(16, 10))
        self.title_lbl = tk.Label(self.header, text="STUDENT MANAGER", font=("Segoe UI", 15, "bold"))
        self.title_lbl.pack(side="left")

        self.theme_btn = tk.Button(self.header, text="☀ Pitch White", command=self.toggle_theme, relief="flat", font=("Segoe UI", 9, "bold"), padx=12, pady=5, cursor="hand2")
        self.theme_btn.pack(side="right", padx=(6, 0))
        self.fs_btn = tk.Button(self.header, text="⛶ F11", command=self.toggle_fullscreen, relief="flat", font=("Segoe UI", 9, "bold"), padx=10, pady=5, cursor="hand2")
        self.fs_btn.pack(side="right", padx=(6, 0))

        self.search_var = tk.StringVar() # live search filter
        self.search_var.trace_add("write", lambda *args: self.filter_search())
        self.search_entry = tk.Entry(self.header, textvariable=self.search_var, font=("Segoe UI", 10), width=24, relief="flat", highlightthickness=1)
        self.search_entry.pack(side="right", padx=10, ipady=3)
        self.search_lbl = tk.Label(self.header, text="SEARCH:", font=("Segoe UI", 8, "bold"))
        self.search_lbl.pack(side="right")

        self.kpi_frame = tk.Frame(self.root) # 4 live monochrome kpi cards
        self.kpi_frame.pack(fill="x", padx=22, pady=4)
        self.kpi_cards, self.kpi_vals, self.kpi_titles = [], {}, []
        for key, label in [("total", "TOTAL STUDENTS"), ("avg", "CLASS AVERAGE"), ("high", "HIGHEST SCORE"), ("pass", "PASS RATE (40%+)")]:
            card = tk.Frame(self.kpi_frame, padx=16, pady=12, highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=4)
            t = tk.Label(card, text=label, font=("Segoe UI", 8, "bold"))
            t.pack(anchor="w")
            v = tk.Label(card, text="--", font=("Segoe UI", 17, "bold"))
            v.pack(anchor="w", pady=(2, 0))
            self.kpi_cards.append(card)
            self.kpi_titles.append(t)
            self.kpi_vals[key] = v

        self.btn_frame = tk.Frame(self.root) # all 8 menu options in 2 clean rows
        self.btn_frame.pack(fill="x", padx=22, pady=10)
        actions = [
            ("1. View All", self.view_all, True), ("2. View Individual", self.view_one, False),
            ("3. Highest Score", self.view_highest, False), ("4. Lowest Score", self.view_lowest, False),
            ("5. Sort Asc/Desc", self.sort_records, False), ("6. Add Student", self.add_student, True),
            ("7. Delete Selected", self.delete_student, False), ("8. Update Selected", self.update_student, False)
        ]
        self.action_btns = []
        for i, (txt, cmd, is_primary) in enumerate(actions):
            b = tk.Button(self.btn_frame, text=txt, command=cmd, relief="flat", font=("Segoe UI", 9, "bold"), pady=7, cursor="hand2")
            b.is_primary = is_primary # highlights primary actions in inverted monochrome
            b.grid(row=i//4, column=i%4, sticky="ew", padx=4, pady=3)
            self.btn_frame.columnconfigure(i%4, weight=1)
            self.action_btns.append(b)

        self.table_frame = tk.Frame(self.root, highlightthickness=1) # interactive student records table
        self.table_frame.pack(fill="both", expand=True, padx=22, pady=(2, 8))
        cols = ("code", "name", "cw", "exam", "pct", "grade")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings", height=10)
        headings = [("code", "Student #", 95), ("name", "Student Name", 240), ("cw", "Coursework (/60)", 130),
                    ("exam", "Exam (/100)", 110), ("pct", "Overall %", 110), ("grade", "Grade", 85)]
        for col, text, w in headings:
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_by_column(c)) # clickable column sort
            self.tree.column(col, width=w, anchor="center" if col != "name" else "w")
        self.tree.bind("<Double-1>", lambda e: self.view_one()) # double-click row to inspect record
        scroll = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.chart_frame = tk.Frame(self.root, padx=14, pady=10, highlightthickness=1) # responsive grade chart
        self.chart_frame.pack(fill="x", padx=22, pady=(0, 8))
        self.chart_lbl = tk.Label(self.chart_frame, text="GRADE DISTRIBUTION (A – F)", font=("Segoe UI", 8, "bold"))
        self.chart_lbl.pack(anchor="w")
        self.chart_canvas = tk.Canvas(self.chart_frame, height=86, highlightthickness=0)
        self.chart_canvas.pack(fill="x", pady=(4, 0))
        self.chart_canvas.bind("<Configure>", lambda e: self.draw_chart()) # rescales bars on fullscreen

        self.status_lbl = tk.Label(self.root, text="Ready  •  Double-click any row to view full record", font=("Segoe UI", 8), anchor="w")
        self.status_lbl.pack(fill="x", padx=24, pady=(0, 10))

    def apply_theme(self): # styles all widgets, treeview, and zebra rows for pitch black/white mode
        self.root.configure(bg=self.c("bg"))
        for f in (self.header, self.kpi_frame, self.btn_frame): f.configure(bg=self.c("bg"))
        self.title_lbl.configure(bg=self.c("bg"), fg=self.c("fg"))
        self.search_lbl.configure(bg=self.c("bg"), fg=self.c("muted"))
        self.search_entry.configure(bg=self.c("entry_bg"), fg=self.c("fg"), insertbackground=self.c("fg"), highlightbackground=self.c("border"), highlightcolor=self.c("fg"))
        self.theme_btn.configure(text="☀ Pitch White" if self.theme_mode == "dark" else "🌙 Pitch Black", bg=self.c("btn"), fg=self.c("btn_fg"), activebackground=self.c("btn_hover"))
        self.fs_btn.configure(bg=self.c("btn"), fg=self.c("btn_fg"), activebackground=self.c("btn_hover"))
        self.status_lbl.configure(bg=self.c("bg"), fg=self.c("muted"))

        for card in self.kpi_cards: card.configure(bg=self.c("card"), highlightbackground=self.c("border"))
        for t in self.kpi_titles: t.configure(bg=self.c("card"), fg=self.c("muted"))
        for v in self.kpi_vals.values(): v.configure(bg=self.c("card"), fg=self.c("fg"))

        for b in self.action_btns:
            if b.is_primary:
                b.configure(bg=self.c("primary"), fg=self.c("primary_fg"), activebackground=self.c("btn_hover"), activeforeground=self.c("fg"))
            else:
                b.configure(bg=self.c("btn"), fg=self.c("btn_fg"), activebackground=self.c("btn_hover"), activeforeground=self.c("fg"))

        self.table_frame.configure(bg=self.c("card"), highlightbackground=self.c("border"))
        self.chart_frame.configure(bg=self.c("card"), highlightbackground=self.c("border"))
        self.chart_lbl.configure(bg=self.c("card"), fg=self.c("muted"))
        self.chart_canvas.configure(bg=self.c("card"))

        self.style.configure("Treeview", background=self.c("card"), foreground=self.c("fg"), fieldbackground=self.c("card"), rowheight=27, font=("Segoe UI", 10), borderwidth=0)
        self.style.configure("Treeview.Heading", background=self.c("btn"), foreground=self.c("fg"), font=("Segoe UI", 9, "bold"), relief="flat")
        self.style.map("Treeview", background=[("selected", self.c("select"))], foreground=[("selected", self.c("fg"))])
        self.tree.tag_configure("even", background=self.c("row_even"))
        self.tree.tag_configure("odd", background=self.c("row_odd"))
        self.draw_chart()

    def toggle_theme(self): # switches between pitch black and pitch white modes
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

    def draw_chart(self): # draws responsive grade distribution bars centered across current canvas width
        self.chart_canvas.delete("all")
        w = max(self.chart_canvas.winfo_width(), 600)
        counts = {g: 0 for g in ("A", "B", "C", "D", "F")}
        for s in self.students: counts[self.calc_stats(s)[2]] += 1
        max_c = max(counts.values()) if counts.values() and max(counts.values()) > 0 else 1

        slot_w = w / 5 # divides canvas evenly into 5 responsive columns
        bar_w = min(slot_w * 0.55, 130)
        for i, g in enumerate(("A", "B", "C", "D", "F")):
            cx = slot_w * i + slot_w / 2
            x0, x1 = cx - bar_w / 2, cx + bar_w / 2
            bar_h = int((counts[g] / max_c) * 48)
            self.chart_canvas.create_rectangle(x0, 64 - bar_h, x1, 64, fill=GRADE_COLORS[g], width=0)
            self.chart_canvas.create_text(cx, 53 - bar_h, text=str(counts[g]), fill=self.c("fg"), font=("Segoe UI", 9, "bold"))
            self.chart_canvas.create_text(cx, 76, text=f"Grade {g}", fill=self.c("muted"), font=("Segoe UI", 9))

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

    def open_student_form(self, student=None): # unified monochrome modal form for add (6) and update (8)
        win = tk.Toplevel(self.root)
        win.title("Update Student" if student else "Add Student")
        win.geometry("350x340")
        win.configure(bg=self.c("card"))
        win.grab_set() # locks focus to modal form

        fields = [("Student Code (1000-9999):", str(student["code"]) if student else ""),
                  ("Full Name:", student["name"] if student else ""),
                  ("Coursework 1 (0-20):", str(student["cw"][0]) if student else ""),
                  ("Coursework 2 (0-20):", str(student["cw"][1]) if student else ""),
                  ("Coursework 3 (0-20):", str(student["cw"][2]) if student else ""),
                  ("Exam Mark (0-100):", str(student["exam"]) if student else "")]
        entries = []
        for lbl, default in fields:
            row = tk.Frame(win, bg=self.c("card"))
            row.pack(fill="x", padx=22, pady=7)
            tk.Label(row, text=lbl, font=("Segoe UI", 9), bg=self.c("card"), fg=self.c("fg")).pack(side="left")
            e = tk.Entry(row, width=16, bg=self.c("entry_bg"), fg=self.c("fg"), insertbackground=self.c("fg"),
                         relief="flat", highlightthickness=1, highlightbackground=self.c("border"))
            e.insert(0, default)
            e.pack(side="right", ipady=2)
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

        tk.Button(win, text="Save Record", command=submit, bg=self.c("primary"), fg=self.c("primary_fg"),
                  relief="flat", font=("Segoe UI", 10, "bold"), pady=7, width=18, cursor="hand2").pack(pady=16)

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