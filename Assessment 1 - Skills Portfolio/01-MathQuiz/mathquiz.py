import tkinter as tk # standard gui library
import random # random numbers, operators, and floating items
import time # tracks live quiz timer
import math # powers smooth sine-wave color throbbing

THEMES = { # pitch black and pitch white palettes
    "dark": {
        "bg": "#000000", "card": "#111111", "border": "#262626", "fg": "#FFFFFF",
        "muted": "#A3A3A3", "btn": "#1F1F1F", "btn_hover": "#333333",
        "entry_bg": "#000000", "good": "#22C55E", "bad": "#EF4444", "bar_bg": "#262626"
    },
    "light": {
        "bg": "#FFFFFF", "card": "#F5F5F5", "border": "#D4D4D4", "fg": "#000000",
        "muted": "#525252", "btn": "#E5E5E5", "btn_hover": "#D4D4D4",
        "entry_bg": "#FFFFFF", "good": "#16A34A", "bad": "#DC2626", "bar_bg": "#E5E5E5"
    }
}

DIFF_META = { # geometry dash inspired colors and labels per difficulty
    1: {"name": "1. Easy", "desc": "Single-Digit (1–9)", "color": "#22C55E"},
    2: {"name": "2. Moderate", "desc": "Double-Digit (10–99)", "color": "#EAB308"},
    3: {"name": "3. Advanced", "desc": "4-Digit (1000–9999)", "color": "#EF4444"},
    4: {"name": "4. DEMON", "desc": "5-Digit (10000–99999)", "color": "#A855F7"}
}

THROB_RGB = { # (light_rgb, dark_rgb) pairs for throbbing equations by tier
    1: ((134, 239, 172), (20, 83, 45)),   # light green -> dark green
    2: ((254, 240, 138), (133, 77, 14)),  # light yellow -> dark yellow
    3: ((252, 165, 165), (127, 29, 29)),  # light red -> dark red
    4: ((216, 180, 254), (88, 28, 135))   # light purple -> dark purple
}

FLOATING_POOL = { # variables and equations grouped by difficulty tier
    1: ["+", "−", "x", "y", "2+3", "9−4", "5+7", "8−2", "1+6", "a+b", "="],
    2: ["×", "÷", "%", "45+19", "82−37", "2x=14", "a²+b²", "64−28", "3y+9", "72+15"],
    3: ["√", "π", "Δ", "∑", "1042−891", "3x²−5", "√144", "4812+2190", "sin(θ)", "log(x)"],
    4: ["∞", "∫", "∇", "∫x²dx", "e^(iπ)+1", "lim x→∞", "98421−45129", "∂y/∂x", "∑1/n²", "∀x∈ℝ"]
}

class MathsQuizApp: # encapsulates arcade quiz state, throbbing background, and ui
    def __init__(self, root):
        self.root = root
        self.root.title("Maths Quiz Arcade")
        self.root.geometry("680x620")
        self.root.minsize(540, 560) # allows resizing and full-screen cleanly
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", lambda e: self.set_fullscreen(False))

        self.theme_mode = "dark"
        self.screen = "menu"
        self.difficulty = 1
        self.timer_job = None
        self.start_time = 0.0
        self.elapsed_sec = 0

        # persistent full-window canvas for bouncing & throbbing equations
        self.bg_canvas = tk.Canvas(self.root, bg=self.c("bg"), highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.symbols = []
        self.init_floating_symbols()
        self.animate_symbols()

        # responsive topbar and centered card container floating above canvas
        self.topbar = tk.Frame(self.root, bg=self.c("bg"))
        self.topbar.place(x=0, y=0, relwidth=1, height=54)
        self.ui_frame = tk.Frame(self.root, bg=self.c("card"), padx=28, pady=24, highlightthickness=2, highlightbackground=self.c("border"))
        self.ui_frame.place(relx=0.5, rely=0.53, anchor="center", width=480)

        self.displayMenu()

    def c(self, key): # fetches active theme color
        return THEMES[self.theme_mode][key]

    def lerp_hex(self, rgb1, rgb2, t): # blends two rgb colors based on t (0.0 to 1.0)
        r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * t)
        g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * t)
        b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def toggle_fullscreen(self, event=None): # toggles true fullscreen with F11
        self.set_fullscreen(not self.is_fullscreen)

    def set_fullscreen(self, state): # sets fullscreen state safely
        self.is_fullscreen = state
        self.root.attributes("-fullscreen", state)

    def init_floating_symbols(self): # spawns 44 color-tiered variables and equations
        for tier in (1, 2, 3, 4):
            for _ in range(11): # 11 items per difficulty tier = 44 total
                x, y = random.randint(40, 640), random.randint(65, 580)
                dx = random.choice([-2.2, -1.6, -1.1, 1.1, 1.6, 2.2])
                dy = random.choice([-2.2, -1.6, -1.1, 1.1, 1.6, 2.2])
                text = random.choice(FLOATING_POOL[tier])
                size = random.randint(12, 20) if len(text) > 2 else random.randint(18, 28)
                phase = random.uniform(0, 6.28) # offsets throbbing so items pulse organically
                item = self.bg_canvas.create_text(x, y, text=text, font=("Segoe UI", size, "bold"))
                self.symbols.append([item, x, y, dx, dy, tier, phase])

    def animate_symbols(self): # bounces items off window edges and throbs their tier color
        w = max(self.bg_canvas.winfo_width(), 640)
        h = max(self.bg_canvas.winfo_height(), 580)
        for s in self.symbols:
            s[1] += s[3]
            s[2] += s[4]
            if s[1] <= 30 or s[1] >= w - 30: s[3] *= -1
            if s[2] <= 65 or s[2] >= h - 25: s[4] *= -1
            self.bg_canvas.coords(s[0], s[1], s[2])

            s[6] += 0.08 # advances sine wave phase
            t = (math.sin(s[6]) + 1) / 2 # oscillates smoothly between 0 and 1
            light_rgb, dark_rgb = THROB_RGB[s[5]]
            self.bg_canvas.itemconfig(s[0], fill=self.lerp_hex(light_rgb, dark_rgb, t))
        self.root.after(30, self.animate_symbols)

    def toggle_theme(self): # switches pitch black/white mode and redraws current screen
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.bg_canvas.configure(bg=self.c("bg"))
        if self.screen == "menu": self.displayMenu()
        elif self.screen == "problem": self.displayProblem()
        elif self.screen == "results": self.displayResults()

    def clearScreen(self): # clears foreground card and topbar without stopping animation
        for w in self.ui_frame.winfo_children(): w.destroy()
        for w in self.topbar.winfo_children(): w.destroy()
        self.topbar.configure(bg=self.c("bg"))
        self.ui_frame.configure(bg=self.c("card"), highlightbackground=self.c("border"))

    def make_btn(self, parent, text, cmd, bg=None, fg=None, width=22): # creates flat button
        b_bg = bg or self.c("btn")
        b_fg = fg or self.c("fg")
        return tk.Button(parent, text=text, width=width, command=cmd, bg=b_bg, fg=b_fg,
                         activebackground=self.c("btn_hover"), activeforeground=b_fg,
                         relief="flat", font=("Segoe UI", 10, "bold"), pady=7, cursor="hand2", bd=0)

    def build_topbar(self, title_text): # renders header bar with fullscreen and day/night toggles
        tk.Label(self.topbar, text=title_text, font=("Segoe UI", 12, "bold"), bg=self.c("bg"), fg=self.c("fg")).pack(side="left", padx=20, pady=12)
        toggle_lbl = "☀ Pitch White" if self.theme_mode == "dark" else "🌙 Pitch Black"
        self.make_btn(self.topbar, toggle_lbl, self.toggle_theme, width=13).pack(side="right", padx=(6, 16), pady=10)
        self.make_btn(self.topbar, "⛶ F11", self.toggle_fullscreen, width=7).pack(side="right", pady=10)

    def draw_gd_face(self, parent, level, size=44): # draws geometry dash inspired difficulty face
        color = DIFF_META[level]["color"]
        cv = tk.Canvas(parent, width=size, height=size, bg=self.c("card"), highlightthickness=0)
        pad = 6
        if level == 4: # demon horns
            cv.create_polygon(10, 14, 4, 2, 18, 8, fill="#7E22CE", outline="#000000", width=1.5)
            cv.create_polygon(size-10, 14, size-4, 2, size-18, 8, fill="#7E22CE", outline="#000000", width=1.5)
        cv.create_oval(pad, pad, size-pad, size-pad, fill=color, outline="#000000", width=2)

        if level == 1: # easy: happy green face
            cv.create_oval(14, 15, 19, 20, fill="#000000")
            cv.create_oval(25, 15, 30, 20, fill="#000000")
            cv.create_arc(13, 18, 31, 33, start=200, extent=140, style="arc", width=2.5, outline="#000000")
        elif level == 2: # moderate: focused yellow face
            cv.create_oval(14, 16, 19, 21, fill="#000000")
            cv.create_oval(25, 16, 30, 21, fill="#000000")
            cv.create_line(15, 29, 29, 28, width=2.5, fill="#000000")
        elif level == 3: # advanced: angry red face
            cv.create_line(12, 14, 20, 18, width=2.5, fill="#000000")
            cv.create_line(32, 14, 24, 18, width=2.5, fill="#000000")
            cv.create_oval(14, 18, 19, 23, fill="#000000")
            cv.create_oval(25, 18, 30, 23, fill="#000000")
            cv.create_arc(14, 26, 30, 36, start=20, extent=140, style="arc", width=2.5, outline="#000000")
        else: # demon: glowing red eyes and fangs
            cv.create_line(11, 13, 20, 18, width=2.5, fill="#000000")
            cv.create_line(33, 13, 24, 18, width=2.5, fill="#000000")
            cv.create_oval(13, 17, 19, 22, fill="#EF4444", outline="#000000")
            cv.create_oval(25, 17, 31, 22, fill="#EF4444", outline="#000000")
            cv.create_polygon(13, 29, 17, 25, 22, 30, 27, 25, 31, 29, 27, 33, 17, 33, fill="#FFFFFF", outline="#000000")
        return cv

    def displayMenu(self): # builds difficulty selection menu with geometry dash faces
        self.screen = "menu"
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self.clearScreen()
        self.score = 0
        self.question_num = 0
        self.streak = 0
        self.best_streak = 0
        self.correct_count = 0

        self.build_topbar("MATHS QUIZ ARCADE")
        tk.Label(self.ui_frame, text="DIFFICULTY LEVEL", font=("Segoe UI", 16, "bold"), bg=self.c("card"), fg=self.c("fg")).pack(pady=(0, 2))
        tk.Label(self.ui_frame, text="10 Questions  •  10 pts (1st try)  •  5 pts (2nd try)", font=("Segoe UI", 9), bg=self.c("card"), fg=self.c("muted")).pack(pady=(0, 16))

        for lvl in (1, 2, 3, 4):
            row = tk.Frame(self.ui_frame, bg=self.c("card"))
            row.pack(fill="x", pady=5)
            self.draw_gd_face(row, lvl).pack(side="left", padx=(4, 12))
            meta = DIFF_META[lvl]
            txt = f"{meta['name']}  —  {meta['desc']}"
            btn_fg = "#000000" if lvl in (1, 2) else "#FFFFFF"
            self.make_btn(row, txt, lambda l=lvl: self.startQuiz(l), bg=meta["color"], fg=btn_fg, width=32).pack(side="left", fill="x", expand=True)

    def startQuiz(self, level): # starts quiz session and live timer
        self.difficulty = level
        self.start_time = time.time()
        self.elapsed_sec = 0
        self.nextQuestion()

    def randomInt(self, level): # returns random integer matching chosen difficulty
        if level == 1: return random.randint(1, 9)
        if level == 2: return random.randint(10, 99)
        if level == 3: return random.randint(1000, 9999)
        return random.randint(10000, 99999) # demon 5-digit range

    def decideOperation(self): # randomly returns '+' or '-' char
        return random.choice(['+', '-'])

    def update_timer(self): # refreshes elapsed timer every 500ms
        if self.screen != "problem": return
        self.elapsed_sec = int(time.time() - self.start_time)
        if hasattr(self, "timer_lbl") and self.timer_lbl.winfo_exists():
            self.timer_lbl.config(text=f"⏱ {self.elapsed_sec}s")
        self.timer_job = self.root.after(500, self.update_timer)

    def nextQuestion(self): # advances question counter or ends quiz after 10
        if self.question_num >= 10:
            self.displayResults()
            return
        self.question_num += 1
        self.attempt = 1
        self.num1 = self.randomInt(self.difficulty)
        self.num2 = self.randomInt(self.difficulty)
        self.op = self.decideOperation()
        self.correct_ans = self.num1 + self.num2 if self.op == '+' else self.num1 - self.num2
        self.displayProblem()

    def displayProblem(self): # renders active question card, face badge, and progress bar
        self.screen = "problem"
        self.clearScreen()
        diff_color = DIFF_META[self.difficulty]["color"]
        self.ui_frame.configure(highlightbackground=diff_color)
        self.build_topbar(f"QUESTION {self.question_num} OF 10  •  {DIFF_META[self.difficulty]['name'].upper()}")

        hud = tk.Frame(self.ui_frame, bg=self.c("card"))
        hud.pack(fill="x", pady=(0, 8))
        self.draw_gd_face(hud, self.difficulty, size=38).pack(side="left")
        tk.Label(hud, text=f"Score: {self.score}   |   🔥 {self.streak}x", font=("Segoe UI", 10, "bold"), bg=self.c("card"), fg=self.c("fg")).pack(side="left", padx=12)
        self.timer_lbl = tk.Label(hud, text=f"⏱ {self.elapsed_sec}s", font=("Segoe UI", 10, "bold"), bg=self.c("card"), fg=self.c("muted"))
        self.timer_lbl.pack(side="right")

        prog = tk.Canvas(self.ui_frame, height=8, bg=self.c("bar_bg"), highlightthickness=0)
        prog.pack(fill="x", pady=(0, 18))
        prog.create_rectangle(0, 0, int(420 * (self.question_num / 10)), 8, fill=diff_color, width=0)

        tk.Label(self.ui_frame, text=f"{self.num1}  {self.op}  {self.num2}  =", font=("Segoe UI", 26, "bold"), bg=self.c("card"), fg=self.c("fg")).pack(pady=(10, 16))

        self.answer_entry = tk.Entry(self.ui_frame, font=("Segoe UI", 16, "bold"), justify="center",
                                     bg=self.c("entry_bg"), fg=self.c("fg"), insertbackground=self.c("fg"),
                                     relief="flat", highlightthickness=1, highlightbackground=self.c("border"))
        self.answer_entry.pack(pady=8, ipady=6, fill="x", padx=40)
        self.answer_entry.focus()
        self.answer_entry.bind("<Return>", lambda e: self.checkInput())

        btn_fg = "#000000" if self.difficulty in (1, 2) else "#FFFFFF"
        self.submit_btn = self.make_btn(self.ui_frame, "Submit Answer", self.checkInput, bg=diff_color, fg=btn_fg, width=20)
        self.submit_btn.pack(pady=12)

        self.feedback_lbl = tk.Label(self.ui_frame, text="", font=("Segoe UI", 10, "bold"), bg=self.c("card"), fg=self.c("muted"))
        self.feedback_lbl.pack(pady=4)

        if self.timer_job: self.root.after_cancel(self.timer_job)
        self.update_timer()

    def checkInput(self): # validates integer input before grading
        try:
            user_ans = int(self.answer_entry.get().strip())
        except ValueError:
            self.feedback_lbl.config(text="Enter a valid whole number.", fg=self.c("bad"))
            return
        self.isCorrect(user_ans, self.correct_ans)

    def isCorrect(self, user_ans, correct_ans): # grades answer, flashes border, manages 2 attempts
        if user_ans == correct_ans:
            points = 10 if self.attempt == 1 else 5
            self.score += points
            self.correct_count += 1
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
            self.ui_frame.config(highlightbackground=self.c("good"))
            self.feedback_lbl.config(text=f"✔ Correct! +{points} points", fg=self.c("good"))
            self.submit_btn.config(state="disabled")
            self.root.after(750, self.nextQuestion)
        elif self.attempt == 1:
            self.attempt = 2
            self.streak = 0
            self.ui_frame.config(highlightbackground=self.c("bad"))
            self.answer_entry.delete(0, tk.END)
            self.feedback_lbl.config(text="✘ Incorrect! One more try for 5 points.", fg=self.c("bad"))
        else:
            self.streak = 0
            self.ui_frame.config(highlightbackground=self.c("bad"))
            self.feedback_lbl.config(text=f"✘ Out of tries! Answer was {correct_ans}.", fg=self.c("bad"))
            self.submit_btn.config(state="disabled")
            self.root.after(1050, self.nextQuestion)

    def displayResults(self): # renders final score, grade, stats, and replay button
        self.screen = "results"
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self.clearScreen()

        if self.score > 90: grade = "A+"
        elif self.score >= 80: grade = "A"
        elif self.score >= 70: grade = "B"
        elif self.score >= 60: grade = "C"
        elif self.score >= 50: grade = "D"
        else: grade = "F"

        diff_color = DIFF_META[self.difficulty]["color"]
        self.ui_frame.configure(highlightbackground=diff_color)
        self.build_topbar("QUIZ COMPLETE")

        self.draw_gd_face(self.ui_frame, self.difficulty, size=52).pack(pady=(0, 6))
        tk.Label(self.ui_frame, text=f"RANK: {grade}", font=("Segoe UI", 26, "bold"), bg=self.c("card"), fg=diff_color).pack()
        tk.Label(self.ui_frame, text=f"Final Score: {self.score} / 100", font=("Segoe UI", 14, "bold"), bg=self.c("card"), fg=self.c("fg")).pack(pady=4)
        tk.Label(self.ui_frame, text=f"Accuracy: {self.correct_count}/10   •   Best Streak: {self.best_streak}x   •   Time: {self.elapsed_sec}s",
                 font=("Segoe UI", 9), bg=self.c("card"), fg=self.c("muted")).pack(pady=(4, 18))

        btn_fg = "#000000" if self.difficulty in (1, 2) else "#FFFFFF"
        self.make_btn(self.ui_frame, "Play Again", self.displayMenu, bg=diff_color, fg=btn_fg, width=22).pack(pady=5)
        self.make_btn(self.ui_frame, "Quit", self.root.destroy, width=22).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    MathsQuizApp(root)
    root.mainloop()