import tkinter as tk # standard gui library
import random # random numbers, operators, and floating items
import time # tracks live quiz timer
import math # powers smooth sine-wave color throbbing

THEMES = { # pitch black and pitch white mathematical palettes
    "dark": {
        "bg": "#000000", "grid": "#121212", "axis": "#1F2937", "card": "#0D0D0D",
        "border": "#262626", "fg": "#FFFFFF", "muted": "#A3A3A3", "accent": "#38BDF8",
        "btn": "#1F1F1F", "btn_hover": "#333333", "entry_bg": "#000000",
        "good": "#22C55E", "bad": "#EF4444", "bar_bg": "#262626"
    },
    "light": {
        "bg": "#FFFFFF", "grid": "#EFEFEF", "axis": "#D4D4D4", "card": "#F8FAFC",
        "border": "#CBD5E1", "fg": "#000000", "muted": "#525252", "accent": "#0284C7",
        "btn": "#E5E5E5", "btn_hover": "#D4D4D4", "entry_bg": "#FFFFFF",
        "good": "#16A34A", "bad": "#DC2626", "bar_bg": "#E5E5E5"
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

class MathsQuizApp: # encapsulates arcade quiz state, graph grid, throbbing equations, and ui
    def __init__(self, root):
        self.root = root
        self.root.title("Maths Quiz Arcade")
        self.root.geometry("680x620")
        self.root.minsize(540, 560) # allows resizing and full-screen cleanly
        self.set_math_icon() # applies custom generated pi window icon
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", lambda e: self.set_fullscreen(False))

        self.theme_mode = "dark"
        self.screen = "menu"
        self.difficulty = 1
        self.timer_job = None
        self.start_time = 0.0
        self.elapsed_sec = 0
        self.last_w = 680 # tracks canvas width for instant fullscreen rescaling
        self.last_h = 620 # tracks canvas height for instant fullscreen rescaling
        self.current_title = "∑  MATHS QUIZ ARCADE  π"

        # persistent full-window canvas for coordinate grid and throbbing equations
        self.bg_canvas = tk.Canvas(self.root, bg=self.c("bg"), highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_canvas.bind("<Configure>", self.on_resize) # rescales equations and title on resize

        self.symbols = []
        self.draw_grid(680, 620)
        self.init_floating_symbols()
        self.animate_symbols()

        # responsive topbar, fullscreen hero banner, and centered card
        self.topbar = tk.Frame(self.root, bg=self.c("bg"))
        self.topbar.place(x=0, y=0, relwidth=1, height=54)

        self.hero_frame = tk.Frame(self.root, bg=self.c("bg")) # shown centered above box only in fullscreen/wide mode
        self.hero_title = tk.Label(self.hero_frame, text=self.current_title, font=("Cambria Math", 26, "bold"), bg=self.c("bg"), fg=self.c("fg"))
        self.hero_title.pack()
        self.hero_sub = tk.Label(self.hero_frame, text="f(x) = a ± b   •   ARITHMETIC CHALLENGE ENGINE", font=("Consolas", 10, "bold"), bg=self.c("bg"), fg=self.c("accent"))
        self.hero_sub.pack()

        self.ui_frame = tk.Frame(self.root, bg=self.c("card"), padx=28, pady=24, highlightthickness=2, highlightbackground=self.c("border"))
        self.ui_frame.place(relx=0.5, rely=0.55, anchor="center", width=490)

        self.displayMenu()

    def set_math_icon(self): # generates a crisp 32x32 mathematical pi icon with zero external files
        icon = tk.PhotoImage(width=32, height=32)
        icon.put("#0F172A", to=(0, 0, 32, 32)) # dark navy background
        icon.put("#38BDF8", to=(0, 0, 32, 2)) # cyan top border
        icon.put("#38BDF8", to=(0, 30, 32, 32)) # cyan bottom border
        icon.put("#38BDF8", to=(0, 0, 2, 32)) # cyan left border
        icon.put("#38BDF8", to=(30, 0, 32, 32)) # cyan right border
        icon.put("#FFFFFF", to=(6, 8, 26, 11)) # pi top bar
        icon.put("#FFFFFF", to=(10, 11, 13, 25)) # pi left leg
        icon.put("#FFFFFF", to=(19, 11, 22, 24)) # pi right leg
        icon.put("#FFFFFF", to=(22, 22, 25, 25)) # pi right foot curve
        self.icon_ref = icon # keeps reference so tkinter does not garbage collect icon
        self.root.iconphoto(True, self.icon_ref)

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
        self.update_title_layout(self.bg_canvas.winfo_width())

    def draw_grid(self, w, h): # draws subtle cartesian graph paper grid behind floating equations
        self.bg_canvas.delete("grid")
        step = 45
        for x in range(0, w, step):
            self.bg_canvas.create_line(x, 0, x, h, fill=self.c("grid"), tags="grid")
        for y in range(0, h, step):
            self.bg_canvas.create_line(0, y, w, y, fill=self.c("grid"), tags="grid")
        self.bg_canvas.create_line(w // 2, 0, w // 2, h, fill=self.c("axis"), width=1.5, tags="grid") # y-axis
        self.bg_canvas.create_line(0, h // 2, w, h // 2, fill=self.c("axis"), width=1.5, tags="grid") # x-axis
        self.bg_canvas.tag_lower("grid") # keeps grid strictly behind floating equations

    def on_resize(self, event): # rescales floating equations across full screen and updates title layout
        w, h = max(event.width, 540), max(event.height, 560)
        if abs(w - self.last_w) > 40 or abs(h - self.last_h) > 40:
            sx = w / max(self.last_w, 1)
            sy = h / max(self.last_h, 1)
            for s in self.symbols: # spreads equations proportionally across entire new screen
                s[1] = min(max(s[1] * sx, 35), w - 35)
                s[2] = min(max(s[2] * sy, 65), h - 25)
            self.last_w, self.last_h = w, h
            self.draw_grid(w, h)
        self.update_title_layout(w)

    def update_title_layout(self, w): # puts title in corner when windowed or centered above box in fullscreen/wide
        is_wide = self.is_fullscreen or w >= 950
        if hasattr(self, "corner_title") and self.corner_title.winfo_exists():
            if is_wide:
                self.corner_title.pack_forget() # hides corner title in fullscreen
                self.hero_frame.configure(bg=self.c("bg"))
                self.hero_title.configure(text=self.current_title, bg=self.c("bg"), fg=self.c("fg"))
                self.hero_sub.configure(bg=self.c("bg"), fg=self.c("accent"))
                self.hero_frame.place(relx=0.5, rely=0.14, anchor="center") # places title centered above box
                self.ui_frame.place(relx=0.5, rely=0.56, anchor="center", width=500)
            else:
                self.hero_frame.place_forget() # hides hero title when windowed
                if not self.corner_title.winfo_ismapped():
                    self.corner_title.pack(side="left", padx=20, pady=12)
                self.ui_frame.place(relx=0.5, rely=0.54, anchor="center", width=480)

    def init_floating_symbols(self): # spawns 44 color-tiered variables and equations
        for tier in (1, 2, 3, 4):
            for _ in range(11): # 11 items per difficulty tier = 44 total
                x, y = random.randint(40, 640), random.randint(65, 580)
                dx = random.choice([-2.2, -1.6, -1.1, 1.1, 1.6, 2.2])
                dy = random.choice([-2.2, -1.6, -1.1, 1.1, 1.6, 2.2])
                text = random.choice(FLOATING_POOL[tier])
                size = random.randint(12, 20) if len(text) > 2 else random.randint(18, 28)
                phase = random.uniform(0, 6.28)
                item = self.bg_canvas.create_text(x, y, text=text, font=("Cambria Math", size, "bold"))
                self.symbols.append([item, x, y, dx, dy, tier, phase])

    def animate_symbols(self): # bounces items off current window edges and throbs their tier color
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

    def toggle_theme(self): # switches pitch black/white mode and redraws grid + current screen
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.bg_canvas.configure(bg=self.c("bg"))
        self.draw_grid(max(self.bg_canvas.winfo_width(), 640), max(self.bg_canvas.winfo_height(), 580))
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
        self.current_title = title_text
        self.corner_title = tk.Label(self.topbar, text=title_text, font=("Cambria Math", 13, "bold"), bg=self.c("bg"), fg=self.c("fg"))
        self.corner_title.pack(side="left", padx=20, pady=12)
        toggle_lbl = "☀ Pitch White" if self.theme_mode == "dark" else "🌙 Pitch Black"
        self.make_btn(self.topbar, toggle_lbl, self.toggle_theme, width=13).pack(side="right", padx=(6, 16), pady=10)
        self.make_btn(self.topbar, "⛶ F11", self.toggle_fullscreen, width=7).pack(side="right", pady=10)
        self.update_title_layout(self.bg_canvas.winfo_width())

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

        self.build_topbar("∑  MATHS QUIZ ARCADE  π")
        tk.Label(self.ui_frame, text="DIFFICULTY LEVEL", font=("Cambria Math", 18, "bold"), bg=self.c("card"), fg=self.c("fg")).pack(pady=(0, 2))
        tk.Label(self.ui_frame, text="10 Questions  •  10 pts (1st try)  •  5 pts (2nd try)", font=("Consolas", 9), bg=self.c("card"), fg=self.c("muted")).pack(pady=(0, 16))

        for lvl in (1, 2, 3, 4):
            row = tk.Frame(self.ui_frame, bg=self.c("card"))
            row.pack(fill="x", pady=5)
            self.draw_gd_face(row, lvl).pack(side="left", padx=(4, 12))
            meta = DIFF_META[lvl]
            txt = f"{meta['name']}  —  {meta['desc']}"
            btn_fg = "#000000" if lvl in (1, 2) else "#FFFFFF"
            self.make_btn(row, txt, lambda l=lvl: self.startQuiz(l), bg=meta["color"], fg=btn_fg, width=32).