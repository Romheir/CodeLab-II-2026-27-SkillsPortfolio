import tkinter as tk # standard gui library
from tkinter import ttk, messagebox # styled table widget and dialogs
import os # dynamic file path handling

THEMES = { # dark and light dashboard palettes
    "dark": {
        "bg": "#0F172A", "card": "#1E293B", "fg": "#F8FAFC", "muted": "#94A3B8",
        "accent": "#38BDF8", "btn": "#334155", "row_alt": "#162032", "select": "#0284C7",
        "entry_bg": "#0F172A", "good": "#22C55E", "warn": "#F59E0B", "bad": "#EF4444"
    },
    "light": {
        "bg": "#F1F5F9", "card": "#FFFFFF", "fg": "#0F172A", "muted": "#475569",
        "accent": "#0284C7", "btn": "#E2E8F0", "row_alt": "#F8FAFC", "select": "#BAE6FD",
        "entry_bg": "#FFFFFF", "good": "#16A34A", "warn": "#D97706", "bad": "#DC2626"
    }
}

class StudentManagerApp: # encapsulates dashboard ui and student crud logic
    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager Dashboard")
        self.root.geometry("920x640")
        self.theme_mode = "dark"
        self.sort_desc = True # toggles ascending/descending sort
        self.file_path = os.path.join(os.path.dirname(__file__), "studentMarks.txt")
        self.students = []
        self.style = ttk.Style()
        self.style.theme_use("clam") # enables full dark/light styling on windows
        self.load_data()
        self.build_ui()
        self.apply_theme()
        self.view_all()

    def c(self, key): # helper for active theme color
        return THEMES[self.theme_mode][key]

    def load_data(self): # parses studentMarks.txt into list of dictionaries
        self.students = []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                for line in lines[1:]:
                    p = line.split(",")
                    self.students.append({
                        "code": int(p[0]), "name": p[1],
                        "cw": [int(p[2]), int(p[3]), int(p[4])], "exam": int(p[5])
                    })
        except FileNotFoundError:
            messagebox.showerror("Error", "studentMarks.txt not found.")

    def save_data(self): # persists changes and updated count back to studentMarks.txt
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(f"{len(self.students)}\n")
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

    def build_ui(self): # constructs header, kpi cards, action bar, table, and chart
        self.header = tk.Frame(self.root)
        self.header.pack(fill="x", padx=20, pady=(14, 8))
        self.title_lbl = tk.Label(self.header, text="STUDENT MANAGER DASHBOARD", font=("Segoe UI", 14, "bold"))
        self.title_lbl.pack(side="left")

        self.theme_btn = tk.Button(self.header, text="☀ Day", command=self.toggle_theme, relief="flat", font=("Segoe UI", 9, "bold"), padx=12, pady=4, cursor="hand2")
        self.theme_btn.pack(side="right")

        self.search_var = tk.StringVar() # live search filter
        self.search_var.trace_add("write", lambda *args: self.filter_search())
        self.search_entry = tk.Entry(self.header, textvariable=self.search_var, font=("Segoe UI", 10), width=24, relief="flat", bd=5)
        self.search_entry.pack(side="right", padx=12)
        self.search_lbl = tk.Label(self.header, text="🔍 Search:", font=("Segoe UI", 9, "bold"))
        self.search_lbl.pack(side="right")

        self.kpi_frame = tk.Frame(self.root) # 4 live summary cards
        self.kpi_frame.pack(fill="x", padx=20, pady=6)
        self.kpi_cards, self.kpi_vals, self.kpi_titles = [], {}, []
        for key, label in [("total", "Total Students"), ("avg", "Class Average"), ("high", "Highest Score"), ("pass", "Pass Rate (40%+)")]:
            card = tk.Frame(self.kpi_frame, padx=14, pady=10)
            card.pack(side="left", fill="x", expand=True, padx=4)
            t = tk.Label(card, text=label, font=("Segoe UI", 9))
            t.pack(anchor="w")
            v = tk.Label(card, text="--", font=("Segoe UI", 16, "bold"))
            v.pack(anchor="w")
            self.kpi_cards.append(card)
            self.kpi_titles.append(t)
            self.kpi_vals[key] = v

        self.btn_frame = tk.Frame(self.root) # all 8 menu options in 2 clean rows
        self.btn_frame.pack(fill="x", padx=20, pady=8)
        actions = [
            ("1. View All", self.view_all), ("2. View Individual", self.view_one),
            ("3. Highest Score", self.view_highest), ("4. Lowest Score", self.view_lowest),
            ("5. Sort Asc/Desc", self.sort_records), ("6. Add Student", self.add_student),
            ("7. Delete Selected", self.delete_student), ("8. Update Selected", self.update_student)
        ]
        self.action_btns = []
        for i, (txt, cmd) in enumerate(actions):
            b = tk.Button(self.btn_frame, text=txt, command=cmd, relief="flat", font=("Segoe UI", 9, "bold"), pady=6, cursor="hand2")
            b.grid(row=i//4, column=i%4, sticky="ew", padx=4, pady=3)
            self.btn_frame.columnconfigure(i%4, weight=1)
            self.action_btns.append(b)

        self.table_frame = tk.Frame(self.root) # interactive student records table
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(4, 8))
        cols = ("code", "name", "cw", "exam", "pct", "grade")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings", height=11)
        headings = [("code", "Student #", 90), ("name", "Student Name", 220), ("cw", "Coursework (/60)", 130),
                    ("exam", "Exam (/100)", 110), ("pct", "Overall %", 110), ("grade", "Grade", 80)]
        for col, text, w in headings:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center" if col != "name" else "w")
        scroll = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.chart_frame = tk.Frame(self.root, padx=12, pady=8) # live grade distribution bar chart
        self.chart_frame.pack(fill="x", padx=20, pady=(0, 14))
        self.chart_lbl = tk.Label(self.chart_frame, text="GRADE DISTRIBUTION (A – F)", font=("Segoe UI", 9, "bold"))
        self.chart_lbl.pack(anchor="w")
        self.chart_canvas = tk.Canvas(self.chart_frame, height=85, highlightthickness=0)
        self.chart_canvas.pack(fill="x", pady=(4, 0))

    def apply_theme(self): # styles all widgets and ttk treeview for day/night mode
        self.root.configure(bg=self.c("bg"))
        for f in (self.header, self.kpi_frame, self.btn_frame, self.table_frame): f.configure(bg=self.c("bg"))
        self.title_lbl.configure(bg=self.c("bg"), fg=self.c("accent"))
        self.search_lbl.configure(bg=self.c("bg"), fg=self.c("muted"))
        self.search_entry.configure(bg=self.c("entry_bg"), fg=self.c("fg"), insertbackground=self.c("fg"))
        self.theme_btn.configure(text="☀ Day" if self.theme_mode == "dark" else "🌙 Night", bg=self.c("btn"), fg=self.c("fg"))

        for card in self.kpi_cards: card.configure(bg=self.c("card"))
        for t in self.kpi_titles: t.configure(bg=self.c("card"), fg=self.c("muted"))
        for v in self.kpi_vals.values(): v.configure(bg=self.c("card"), fg=self.c("fg"))

        for b in self.action_btns: b.configure(bg=self.c("btn"), fg=self.c("fg"), activebackground=self.c("accent"))
        self.chart_frame.configure(bg=self.c("card"))
        self.chart_lbl.configure(bg=self.c("card"), fg=self.c("muted"))
        self.chart_canvas.configure(bg=self.c("card"))

        self.style.configure("Treeview", background=self.c("card"), foreground=self.c("fg"), fieldbackground=self.c("card"), rowheight=26, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", background=self.c("btn"), foreground=self.c("fg"), font=("Segoe UI", 9, "bold"), relief="flat")
        self.style.map("Treeview", background=[("selected", self.c("select"))])
        self.draw_chart()

    def toggle_theme(self): # switches between day and night mode
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.apply_theme()

    def refresh_table(self, records): # populates treeview, kpis, and chart
        for row in self.tree.get_children(): self.tree.delete(row)
        for s in records:
            cw, pct, grade = self.calc_stats(s)
            self.tree.insert("", "end", iid=str(s["code"]), values=(s["code"], s["name"], f"{cw} / 60", f"{s['exam']} / 100", f"{pct:.2f}%", grade))
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

    def draw_chart(self): # draws grade distribution bars on canvas
        self.chart_canvas.delete("all")
        counts = {g: 0 for g in ("A", "B", "C", "D", "F")}
        for s in self.students: counts[self.calc_stats(s)[2]] += 1
        max_c = max(counts.values()) if counts.values() and max(counts.values()) > 0 else 1
        colors = {"A": self.c("good"), "B": self.c("accent"), "C": "#818CF8", "D": self.c("warn"), "F": self.c("bad")}
        for i, g in enumerate(("A", "B", "C", "D", "F")):
            x0, x1 = 40 + i * 165, 145 + i * 165
            bar_h = int((counts[g] / max_c) * 48)
            self.chart_canvas.create_rectangle(x0, 62 - bar_h, x1, 62, fill=colors[g], width=0)
            self.chart_canvas.create_text((x0+x1)//2, 52 - bar_h, text=str(counts[g]), fill=self.c("fg"), font=("Segoe UI", 9, "bold"))
            self.chart_canvas.create_text((x0+x1)//2, 74, text=f"Grade {g}", fill=self.c("muted"), font=("Segoe UI", 9))

    def filter_search(self): # filters table live as user types
        q = self.search_var.get().strip().lower()
        if not q:
            self.refresh_table(self.students)
            return
        filtered = [s for s in self.students if q in s["name"].lower() or q in str(s["code"])]
        self.refresh_table(filtered)

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

    def view_lowest(self): # option 4 isolates lowest scoring student
        if not self.students: return
        low = min(self.students, key=lambda s: sum(s["cw"]) + s["exam"])
        self.refresh_table([low])

    def sort_records(self): # option 5 toggles ascending / descending sort
        self.sort_desc = not self.sort_desc
        ordered = sorted(self.students, key=lambda s: sum(s["cw"]) + s["exam"], reverse=self.sort_desc)
        self.refresh_table(ordered)

    def open_student_form(self, student=None): # unified modal form for add (6) and update (8)
        win = tk.Toplevel(self.root)
        win.title("Update Student" if student else "Add Student")
        win.geometry("340x330")
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
            row.pack(fill="x", padx=20, pady=6)
            tk.Label(row, text=lbl, font=("Segoe UI", 9), bg=self.c("card"), fg=self.c("fg")).pack(side="left")
            e = tk.Entry(row, width=16, bg=self.c("entry_bg"), fg=self.c("fg"), insertbackground=self.c("fg"), relief="flat", bd=4)
            e.insert(0, default)
            e.pack(side="right")
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
            else:
                if any(s["code"] == code for s in self.students):
                    messagebox.showerror("Duplicate", "That student code already exists.", parent=win)
                    return
                self.students.append({"code": code, "name": name, "cw": cw, "exam": exam})
            self.save_data()
            self.view_all()
            win.destroy()

        tk.Button(win, text="Save Record", command=submit, bg=self.c("accent"), fg="#0F172A" if self.theme_mode == "dark" else "#FFFFFF",
                  relief="flat", font=("Segoe UI", 10, "bold"), pady=6, width=18, cursor="hand2").pack(pady=16)

    def add_student(self): # option 6 launches empty add modal
        self.open_student_form(None)

    def delete_student(self): # option 7 deletes selected row after confirmation
        s = self.get_selected_student()
        if not s: return
        if messagebox.askyesno("Confirm Delete", f"Delete {s['name']} ({s['code']})?"):
            self.students.remove(s)
            self.save_data()
            self.view_all()

    def update_student(self): # option 8 launches pre-filled update modal
        s = self.get_selected_student()
        if s: self.open_student_form(s)

if __name__ == "__main__":
    root = tk.Tk()
    StudentManagerApp(root)
    root.mainloop()