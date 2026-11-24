import tkinter as tk # standard gui library
from tkinter import messagebox # favorites popup dialog
import random # shuffles jokes and balloon physics
import os # dynamic file path handling
import math # powers jester bell bounce and equalizer waves
import threading # plays sound effects without freezing gui

try:
    import winsound # built-in windows audio for circus chimes and balloon pops
except ImportError:
    winsound = None # safely disables audio on non-windows systems

THEMES = { # vibrant midnight circus and big top day palettes
    "dark": {
        "bg": "#120624", "card": "#230B42", "stage": "#15052B", "border": "#FACC15",
        "fg": "#FFFFFF", "muted": "#E9D5FF", "accent": "#FF2E63", "gold": "#FACC15",
        "teal": "#00F5D4", "purple": "#9B5DE5", "lime": "#A3E635", "top_btn": "#3B156B"
    },
    "light": {
        "bg": "#FFFBEB", "card": "#FFFFFF", "stage": "#FEF3C7", "border": "#DC2626",
        "fg": "#1E1B4B", "muted": "#6B21A8", "accent": "#EF4444", "gold": "#F59E0B",
        "teal": "#0D9488", "purple": "#7C3AED", "lime": "#65A30D", "top_btn": "#FDE68A"
    }
}

BALLOON_COLORS = ["#FF2E63", "#FACC15", "#00F5D4", "#9B5DE5", "#FF7B00", "#38BDF8", "#A3E635"] # vibrant circus balloon colors

class AlexaJokeApp: # encapsulates circus jester assistant, poppable balloons, and joke logic
    def __init__(self, root):
        self.root = root
        self.root.title("Alexa's Circus Joke Tent")
        self.root.geometry("720x660")
        self.root.minsize(560, 600) # fully resizable and fullscreen compatible
        self.set_clown_icon() # applies custom generated clown window icon
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", lambda e: self.set_fullscreen(False))
        self.root.bind("<space>", lambda e: self.tell_joke())
        self.root.bind("<Return>", lambda e: self.show_punchline())

        self.theme_mode = "dark"
        self.muted = False
        self.jokes = self.load_jokes()
        self.queue = [] # non-repeating shuffled queue
        self.favorites = []
        self.current_full_joke = ""
        self.punchline = ""
        self.punchline_revealed = False # tracks if current punchline is already shown
        self.jokes_told = 0
        self.laughs = 0
        self.popped_count = 0 # tracks popped balloons
        self.is_speaking = False
        self.phase = 0.0
        self.type_job = None
        self.last_w = 720 # tracks window width for fullscreen redistribution

        # full-window interactive canvas for floating balloons
        self.bg_canvas = tk.Canvas(self.root, bg=self.c("bg"), highlightthickness=0, cursor="crosshair")
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_canvas.bind("<Button-1>", self.on_canvas_click) # detects clicks on balloons
        self.bg_canvas.bind("<Configure>", self.on_resize) # spreads balloons when entering fullscreen

        self.balloons = [] # active floating balloons
        self.bursts = [] # pop confetti and text animations

        # topbar and centered circus stage card floating above canvas
        self.topbar = tk.Frame(self.root, bg=self.c("bg"))
        self.topbar.place(x=0, y=0, relwidth=1, height=52)
        self.ui_frame = tk.Frame(self.root, bg=self.c("card"), padx=26, pady=20, highlightthickness=3, highlightbackground=self.c("border"))
        self.ui_frame.place(relx=0.5, rely=0.53, anchor="center", width=520)

        self.build_ui()
        self.apply_theme()
        for _ in range(14): self.spawn_balloon(from_edge=False) # spawns 14 initial balloons
        self.animate_loop()

    def set_clown_icon(self): # generates a crisp 32x32 circus clown icon with zero external files
        icon = tk.PhotoImage(width=32, height=32)
        icon.put("#120624", to=(0, 0, 32, 32)) # midnight circus background
        icon.put("#FF2E63", to=(4, 4, 11, 13)) # left red jester puff
        icon.put("#00F5D4", to=(21, 4, 28, 13)) # right teal jester puff
        icon.put("#9B5DE5", to=(12, 2, 20, 10)) # center purple jester hat
        icon.put("#FACC15", to=(14, 1, 18, 4)) # golden bell on top
        icon.put("#FFFFFF", to=(7, 9, 25, 28)) # white clown face
        icon.put("#000000", to=(10, 14, 13, 17)) # left eye
        icon.put("#000000", to=(19, 14, 22, 17)) # right eye
        icon.put("#FF2E63", to=(14, 17, 18, 21)) # red clown nose
        icon.put("#FF2E63", to=(10, 23, 22, 25)) # clown smile
        self.icon_ref = icon # keeps reference so tkinter does not garbage collect icon
        self.root.iconphoto(True, self.icon_ref)

    def c(self, key): # fetches active theme color
        return THEMES[self.theme_mode][key]

    def toggle_fullscreen(self, event=None): # toggles true fullscreen with F11
        self.set_fullscreen(not self.is_fullscreen)

    def set_fullscreen(self, state): # sets fullscreen state safely
        self.is_fullscreen = state
        self.root.attributes("-fullscreen", state)

    def play_sound(self, notes): # plays non-blocking circus chime or pop sound
        if self.muted or not winsound: return
        def _beep():
            for freq, dur in notes:
                winsound.Beep(freq, dur)
        threading.Thread(target=_beep, daemon=True).start()

    def load_jokes(self): # safely loads valid jokes from randomJokes.txt
        path = os.path.join(os.path.dirname(__file__), "randomJokes.txt")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = [line.strip() for line in f if "?" in line]
                return data if data else ["Error?No valid jokes found."]
        except FileNotFoundError:
            return ["Error?randomJokes.txt not found."]

    def on_resize(self, event): # spreads balloons across full width when maximized or fullscreened
        if abs(event.width - self.last_w) > 120:
            scale = event.width / max(self.last_w, 1)
            for b in self.balloons:
                b["x"] = min(max(b["x"] * scale, 40), event.width - 40)
            self.last_w = event.width

    def spawn_balloon(self, from_edge=True): # creates a clickable circus balloon with string
        w = max(self.bg_canvas.winfo_width(), 700)
        h = max(self.bg_canvas.winfo_height(), 640)
        x = random.randint(45, w - 45)
        y = h + 40 if from_edge else random.randint(80, h - 60)
        dx = random.uniform(-1.2, 1.2)
        dy = random.uniform(-2.0, -0.9)
        color = random.choice(BALLOON_COLORS)
        r = random.randint(20, 28)

        string_id = self.bg_canvas.create_line(x, y+r+4, x, y+r+34, fill=self.c("muted"), width=2)
        body_id = self.bg_canvas.create_oval(x-r, y-r-4, x+r, y+r+4, fill=color, outline="#FFFFFF", width=2)
        shine_id = self.bg_canvas.create_oval(x-r+6, y-r+2, x-r+12, y-r+10, fill="#FFFFFF", outline="")
        self.balloons.append({"x": x, "y": y, "dx": dx, "dy": dy, "r": r, "color": color, "items": [string_id, body_id, shine_id]})

    def on_canvas_click(self, event): # pops clicked balloon, reveals punchline if waiting, and respawns in 5s
        for b in self.balloons[:]:
            dist = math.hypot(event.x - b["x"], event.y - b["y"])
            if dist <= b["r"] + 10:
                for item in b["items"]: self.bg_canvas.delete(item)
                self.balloons.remove(b)
                self.popped_count += 1
                self.update_counter()
                self.spawn_burst(b["x"], b["y"], b["color"], "POP!")
                self.play_sound([(900, 35), (450, 45)]) # quick pop sound
                if self.punchline and not self.punchline_revealed: # reveals punchline on balloon pop
                    self.show_punchline()
                self.root.after(5000, lambda: self.spawn_balloon(from_edge=True)) # regenerates 5 seconds later
                break

    def spawn_burst(self, x, y, color, label=None): # spawns colorful confetti particles and optional pop text
        if label:
            txt = self.bg_canvas.create_text(x, y, text=label, font=("Segoe UI", 14, "bold"), fill=color)
            self.bursts.append([txt, x, y, 0, -1.8, 22])
        for _ in range(10):
            dx, dy = random.uniform(-4.0, 4.0), random.uniform(-4.0, 2.0)
            c = random.choice(BALLOON_COLORS)
            dot = self.bg_canvas.create_oval(x-4, y-4, x+4, y+4, fill=c, outline="")
            self.bursts.append([dot, x, y, dx, dy, 26])

    def make_fun_btn(self, parent, text, cmd, bg_key, fg="#FFFFFF", width=18, pady=7): # chunky circus button with hover pop
        btn = tk.Button(parent, text=text, width=width, command=cmd, bg=self.c(bg_key), fg=fg,
                        activebackground=self.c("gold"), activeforeground="#000000",
                        relief="raised", bd=3, font=("Segoe UI", 10, "bold"), pady=pady, cursor="hand2")
        btn.bg_key = bg_key
        btn.orig_fg = fg
        btn.bind("<Enter>", lambda e: btn.config(bg=self.c("gold"), fg="#000000"))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.c(btn.bg_key), fg=btn.orig_fg))
        return btn

    def build_ui(self): # constructs topbar, jester canvas, speech stage, and playful buttons
        self.counter_lbl = tk.Label(self.topbar, text="🤡 Jokes: 0  •  🎈 Popped: 0", font=("Segoe UI", 10, "bold"))
        self.counter_lbl.pack(side="left", padx=18, pady=12)

        self.theme_btn = tk.Button(self.topbar, text="☀ Big Top Day", command=self.toggle_theme, relief="raised", bd=2, font=("Segoe UI", 9, "bold"), padx=10, pady=3, cursor="hand2")
        self.theme_btn.pack(side="right", padx=(6, 16), pady=10)
        self.fs_btn = tk.Button(self.topbar, text="⛶ F11", command=self.toggle_fullscreen, relief="raised", bd=2, font=("Segoe UI", 9, "bold"), padx=8, pady=3, cursor="hand2")
        self.fs_btn.pack(side="right", padx=4, pady=10)
        self.mute_btn = tk.Button(self.topbar, text="🔊 Sound", command=self.toggle_mute, relief="raised", bd=2, font=("Segoe UI", 9, "bold"), padx=8, pady=3, cursor="hand2")
        self.mute_btn.pack(side="right", padx=4, pady=10)

        # jester alexa mascot + rainbow equalizer canvas
        self.jester_canvas = tk.Canvas(self.ui_frame, width=460, height=130, highlightthickness=0)
        self.jester_canvas.pack(pady=(0, 4))

        self.status_lbl = tk.Label(self.ui_frame, text="🎪 STEP RIGHT UP! POP A BALLOON TO REVEAL THE PUNCHLINE!", font=("Segoe UI", 8, "bold"))
        self.status_lbl.pack(pady=(0, 8))

        # speech stage
        self.stage = tk.Frame(self.ui_frame, padx=16, pady=14, highlightthickness=2)
        self.stage.pack(fill="x", pady=(0, 14))
        self.setup_lbl = tk.Label(self.stage, text="Honk the button below for a joke!", wraplength=420, font=("Segoe UI", 12, "bold"), height=3)
        self.setup_lbl.pack()
        self.punch_lbl = tk.Label(self.stage, text="", wraplength=420, font=("Segoe UI", 11, "italic"), height=2)
        self.punch_lbl.pack(pady=(4, 0))

        # primary required buttons
        self.joke_btn = self.make_fun_btn(self.ui_frame, "🤡 Alexa tell me a Joke", self.tell_joke, "accent", "#FFFFFF", width=28, pady=8)
        self.joke_btn.pack(pady=4)
        self.punch_btn = self.make_fun_btn(self.ui_frame, "🎉 Show Punchline", self.show_punchline, "purple", "#FFFFFF", width=28, pady=7)
        self.punch_btn.pack(pady=4)

        # secondary playful row
        self.row1 = tk.Frame(self.ui_frame)
        self.row1.pack(pady=5)
        self.next_btn = self.make_fun_btn(self.row1, "🎪 Next Joke", self.tell_joke, "teal", "#000000", width=12, pady=5)
        self.next_btn.pack(side="left", padx=4)
        self.laugh_btn = self.make_fun_btn(self.row1, "😂 Laugh (0)", self.add_laugh, "lime", "#000000", width=12, pady=5)
        self.laugh_btn.pack(side="left", padx=4)
        self.fav_btn = self.make_fun_btn(self.row1, "⭐ Save (0)", self.save_favorite, "gold", "#000000", width=12, pady=5)
        self.fav_btn.pack(side="left", padx=4)

        # bottom row: view favorites + required quit button
        self.row2 = tk.Frame(self.ui_frame)
        self.row2.pack(pady=(4, 0))
        self.view_fav_btn = self.make_fun_btn(self.row2, "📜 Favorites", self.view_favorites, "top_btn", self.c("fg"), width=13, pady=4)
        self.view_fav_btn.pack(side="left", padx=4)
        self.quit_btn = self.make_fun_btn(self.row2, "🚪 Quit", self.root.destroy, "top_btn", self.c("fg"), width=13, pady=4)
        self.quit_btn.pack(side="left", padx=4)

    def apply_theme(self): # updates all circus colors cleanly for day/night toggle
        self.bg_canvas.configure(bg=self.c("bg"))
        self.topbar.configure(bg=self.c("bg"))
        self.ui_frame.configure(bg=self.c("card"), highlightbackground=self.c("border"))
        self.jester_canvas.configure(bg=self.c("card"))
        self.stage.configure(bg=self.c("stage"), highlightbackground=self.c("teal"))
        self.row1.configure(bg=self.c("card"))
        self.row2.configure(bg=self.c("card"))

        self.counter_lbl.configure(bg=self.c("bg"), fg=self.c("gold"))
        self.status_lbl.configure(bg=self.c("card"), fg=self.c("teal"))
        self.setup_lbl.configure(bg=self.c("stage"), fg=self.c("fg"))
        self.punch_lbl.configure(bg=self.c("stage"), fg=self.c("accent"))

        self.theme_btn.configure(text="☀ Big Top Day" if self.theme_mode == "dark" else "🌙 Midnight Circus", bg=self.c("top_btn"), fg=self.c("fg"))
        self.fs_btn.configure(bg=self.c("top_btn"), fg=self.c("fg"))
        self.mute_btn.configure(bg=self.c("top_btn"), fg=self.c("fg"))

        for b in (self.joke_btn, self.punch_btn, self.next_btn, self.laugh_btn, self.fav_btn):
            b.configure(bg=self.c(b.bg_key), fg=b.orig_fg)
        for b in (self.view_fav_btn, self.quit_btn):
            b.orig_fg = self.c("fg")
            b.configure(bg=self.c("top_btn"), fg=self.c("fg"))
        for b in self.balloons:
            self.bg_canvas.itemconfig(b["items"][0], fill=self.c("muted"))

    def toggle_theme(self): # switches between midnight circus and big top day
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.apply_theme()

    def toggle_mute(self): # toggles sound effects on/off
        self.muted = not self.muted
        self.mute_btn.config(text="🔇 Muted" if self.muted else "🔊 Sound")

    def update_counter(self): # refreshes topbar jokes & popped stats
        self.counter_lbl.config(text=f"🤡 Jokes: {self.jokes_told}  •  🎈 Popped: {self.popped_count}")

    def draw_jester_and_eq(self): # draws bouncing jester alexa mascot and rainbow equalizer
        cv = self.jester_canvas
        cv.delete("all")
        self.phase += 0.25 if self.is_speaking else 0.08
        bob = math.sin(self.phase) * (5 if self.is_speaking else 2.5)

        # rainbow circus equalizer bars on both sides
        for side in (-1, 1):
            for i in range(6):
                x = 230 + side * (70 + i * 24)
                amp = random.randint(14, 42) if self.is_speaking else int(7 + 5 * math.sin(self.phase + i))
                col = BALLOON_COLORS[i % len(BALLOON_COLORS)]
                cv.create_line(x, 72 - amp, x, 72 + amp, fill=col, width=6, capstyle="round")

        # 3-point jester hat with bouncing golden bells
        cx, cy = 230, 74 + bob
        cv.create_polygon(cx-30, cy-16, cx-54, cy-46, cx-10, cy-26, fill="#FF2E63", outline="#FFFFFF", width=2)
        cv.create_polygon(cx+30, cy-16, cx+54, cy-46, cx+10, cy-26, fill="#00F5D4", outline="#FFFFFF", width=2)
        cv.create_polygon(cx-16, cy-22, cx, cy-58, cx+16, cy-22, fill="#9B5DE5", outline="#FFFFFF", width=2)
        for bx, by in ((cx-54, cy-46), (cx+54, cy-46), (cx, cy-58)):
            cv.create_oval(bx-6, by-6, bx+6, by+6, fill="#FACC15", outline="#000000", width=1.5)

        # smiling clown face with red nose
        cv.create_oval(cx-32, cy-26, cx+32, cy+36, fill="#FFFFFF", outline="#FACC15", width=3)
        cv.create_oval(cx-14, cy-10, cx-6, cy-2, fill="#000000") # left eye
        cv.create_oval(cx+6, cy-10, cx+14, cy-2, fill="#000000") # right eye
        cv.create_oval(cx-7, cy+1, cx+7, cy+15, fill="#FF2E63", outline="#000000") # clown nose
        cv.create_arc(cx-16, cy+6, cx+16, cy+26, start=200, extent=140, style="arc", width=3, outline="#FF2E63")

    def animate_loop(self): # unified animation loop for balloons, bursts, and jester mascot
        w = max(self.bg_canvas.winfo_width(), 700)
        h = max(self.bg_canvas.winfo_height(), 640)

        for b in self.balloons: # moves balloons smoothly across full screen
            b["x"] += b["dx"]
            b["y"] += b["dy"]
            if b["x"] < 30 or b["x"] > w - 30: b["dx"] *= -1
            if b["y"] < -50: # wraps back to bottom at a fresh random full-width x
                b["y"] = h + 45
                b["x"] = random.randint(45, w - 45)

            x, y, r = b["x"], b["y"], b["r"]
            self.bg_canvas.coords(b["items"][0], x, y+r+4, x, y+r+34)
            self.bg_canvas.coords(b["items"][1], x-r, y-r-4, x+r, y+r+4)
            self.bg_canvas.coords(b["items"][2], x-r+6, y-r+2, x-r+12, y-r+10)

        for b in self.bursts[:]: # animates and cleans up pop confetti
            b[1] += b[3]
            b[2] += b[4]
            b[5] -= 1
            if self.bg_canvas.type(b[0]) == "text":
                self.bg_canvas.coords(b[0], b[1], b[2])
            else:
                self.bg_canvas.coords(b[0], b[1]-4, b[2]-4, b[1]+4, b[2]+4)
            if b[5] <= 0:
                self.bg_canvas.delete(b[0])
                self.bursts.remove(b)

        self.draw_jester_and_eq()
        self.root.after(32, self.animate_loop)

    def type_text(self, label, full_text, idx=0): # smooth typewriter reveal synced to jester animation
        if idx <= len(full_text):
            label.config(text=full_text[:idx])
            self.type_job = self.root.after(18, lambda: self.type_text(label, full_text, idx + 1))
        else:
            self.is_speaking = False
            if not self.punchline_revealed:
                self.status_lbl.config(text="🎪 READY! PRESS ENTER OR POP A BALLOON FOR THE PUNCHLINE!")

    def tell_joke(self): # pulls non-repeating joke, plays circus chime, and animates setup
        if self.type_job: self.root.after_cancel(self.type_job)
        if not self.queue:
            self.queue = self.jokes.copy()
            random.shuffle(self.queue)

        self.current_full_joke = self.queue.pop()
        setup, self.punchline = self.current_full_joke.split("?", 1)
        self.punchline_revealed = False # resets flag so popping a balloon reveals punchline
        self.jokes_told += 1
        self.update_counter()
        self.punch_lbl.config(text="")
        self.is_speaking = True
        self.status_lbl.config(text="🤡 TELLING JOKE...")
        self.play_sound([(523, 60), (659, 60), (784, 80)]) # upbeat circus fanfare
        self.type_text(self.setup_lbl, f"{setup}?")

    def show_punchline(self): # reveals punchline with celebratory sound
        if not self.punchline: return
        if self.type_job: self.root.after_cancel(self.type_job)
        self.punchline_revealed = True
        self.is_speaking = True
        self.status_lbl.config(text="🎉 BA-DUM-TSS!")
        self.play_sound([(784, 55), (1046, 110)])
        self.type_text(self.punch_lbl, self.punchline.strip())

    def add_laugh(self): # increments laugh counter and launches confetti burst
        self.laughs += 1
        self.laugh_btn.config(text=f"😂 Laugh ({self.laughs})")
        w = max(self.bg_canvas.winfo_width(), 700)
        self.spawn_burst(random.randint(100, w-100), 120, self.c("gold"), "HAHA!")

    def save_favorite(self): # bookmarks current joke without duplicates
        if self.current_full_joke and self.current_full_joke not in self.favorites:
            self.favorites.append(self.current_full_joke)
            self.fav_btn.config(text=f"⭐ Save ({len(self.favorites)})")

    def view_favorites(self): # opens popup listing all saved jokes
        if not self.favorites:
            messagebox.showinfo("Favorites", "No favorite jokes saved yet! Click ⭐ Save on a joke you like.")
            return
        formatted = "\n\n".join(f"• {j.replace('?', '?\n  ')}" for j in self.favorites)
        messagebox.showinfo(f"Saved Favorites ({len(self.favorites)})", formatted)

if __name__ == "__main__":
    root = tk.Tk()
    AlexaJokeApp(root)
    root.mainloop()