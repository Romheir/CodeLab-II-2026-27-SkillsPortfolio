import tkinter as tk # standard gui library
import random # shuffles joke queue
import os # dynamic file path handling

THEMES = { # dark and light smart assistant palettes
    "dark": {
        "bg": "#0B1120", "card": "#162032", "fg": "#F8FAFC", "muted": "#94A3B8",
        "accent": "#06B6D4", "ring_glow": "#22D3EE", "btn": "#1E293B", "btn_hover": "#334155"
    },
    "light": {
        "bg": "#F0F9FF", "card": "#FFFFFF", "fg": "#0F172A", "muted": "#475569",
        "accent": "#0891B2", "ring_glow": "#06B6D4", "btn": "#E2E8F0", "btn_hover": "#CBD5E1"
    }
}

class AlexaJokeApp: # encapsulates assistant gui and joke state
    def __init__(self, root):
        self.root = root
        self.root.title("Alexa Joke Assistant")
        self.root.geometry("480x500")
        self.root.resizable(False, False)
        self.theme_mode = "dark"
        self.jokes = self.load_jokes()
        self.queue = [] # non-repeating shuffled queue
        self.punchline = ""
        self.jokes_told = 0
        self.laughs = 0
        self.type_job = None # tracks active typewriter animation
        self.pulse_job = None # tracks active ring animation
        self.pulse_step = 0
        self.build_ui()
        self.apply_theme()

    def c(self, key): # helper for active theme color
        return THEMES[self.theme_mode][key]

    def load_jokes(self): # safely loads valid jokes from randomJokes.txt
        path = os.path.join(os.path.dirname(__file__), "randomJokes.txt")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = [line.strip() for line in f if "?" in line]
                return data if data else ["Error?No valid jokes found."]
        except FileNotFoundError:
            return ["Error?randomJokes.txt not found."]

    def build_ui(self): # builds assistant layout, canvas ring, and required buttons
        self.topbar = tk.Frame(self.root)
        self.topbar.pack(fill="x", padx=20, pady=(12, 0))
        self.counter_lbl = tk.Label(self.topbar, text="Jokes Heard: 0", font=("Segoe UI", 9, "bold"))
        self.counter_lbl.pack(side="left")
        self.theme_btn = tk.Button(self.topbar, text="☀ Day", command=self.toggle_theme, relief="flat", font=("Segoe UI", 9, "bold"), padx=10, pady=3, cursor="hand2")
        self.theme_btn.pack(side="right")

        self.ring_canvas = tk.Canvas(self.root, width=110, height=110, highlightthickness=0) # animated alexa echo ring
        self.ring_canvas.pack(pady=(6, 4))
        self.draw_ring(0)

        self.card = tk.Frame(self.root, padx=20, pady=18) # speech bubble card
        self.card.pack(fill="x", padx=24, pady=8)
        self.setup_lbl = tk.Label(self.card, text="Say the word — click below for a joke!", wraplength=390, font=("Segoe UI", 12, "bold"), height=3)
        self.setup_lbl.pack()
        self.punch_lbl = tk.Label(self.card, text="", wraplength=390, font=("Segoe UI", 11, "italic"), height=2)
        self.punch_lbl.pack(pady=(6, 0))

        self.btn_frame = tk.Frame(self.root) # holds the 4 required buttons + laugh reaction
        self.btn_frame.pack(pady=10)
        self.joke_btn = tk.Button(self.btn_frame, text="Alexa tell me a Joke", width=24, command=self.tell_joke, relief="flat", font=("Segoe UI", 10, "bold"), pady=7, cursor="hand2")
        self.joke_btn.pack(pady=4)
        self.punch_btn = tk.Button(self.btn_frame, text="Show Punchline", width=24, command=self.show_punchline, relief="flat", font=("Segoe UI", 10, "bold"), pady=6, cursor="hand2")
        self.punch_btn.pack(pady=4)

        row = tk.Frame(self.btn_frame)
        row.pack(pady=4)
        self.row_frame = row
        self.next_btn = tk.Button(row, text="Next Joke", width=11, command=self.tell_joke, relief="flat", font=("Segoe UI", 10, "bold"), pady=6, cursor="hand2")
        self.next_btn.pack(side="left", padx=4)
        self.laugh_btn = tk.Button(row, text="😂 Laugh (0)", width=11, command=self.add_laugh, relief="flat", font=("Segoe UI", 10, "bold"), pady=6, cursor="hand2")
        self.laugh_btn.pack(side="left", padx=4)

        self.quit_btn = tk.Button(self.btn_frame, text="Quit", width=24, command=self.root.destroy, relief="flat", font=("Segoe UI", 9, "bold"), pady=5, cursor="hand2")
        self.quit_btn.pack(pady=(6, 0))

    def apply_theme(self): # updates all widget colors cleanly without resetting active joke
        self.root.configure(bg=self.c("bg"))
        for f in (self.topbar, self.btn_frame, self.row_frame): f.configure(bg=self.c("bg"))
        self.ring_canvas.configure(bg=self.c("bg"))
        self.card.configure(bg=self.c("card"))
        self.counter_lbl.configure(bg=self.c("bg"), fg=self.c("muted"))
        self.setup_lbl.configure(bg=self.c("card"), fg=self.c("fg"))
        self.punch_lbl.configure(bg=self.c("card"), fg=self.c("accent"))
        self.theme_btn.configure(text="☀ Day" if self.theme_mode == "dark" else "🌙 Night", bg=self.c("btn"), fg=self.c("fg"))

        primary_fg = "#0B1120" if self.theme_mode == "dark" else "#FFFFFF"
        self.joke_btn.configure(bg=self.c("accent"), fg=primary_fg, activebackground=self.c("ring_glow"))
        for b in (self.punch_btn, self.next_btn, self.laugh_btn, self.quit_btn):
            b.configure(bg=self.c("btn"), fg=self.c("fg"), activebackground=self.c("btn_hover"), activeforeground=self.c("fg"))
        self.draw_ring(0)

    def toggle_theme(self): # switches between day and night mode
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.apply_theme()

    def draw_ring(self, expand): # draws glowing echo ring on canvas
        self.ring_canvas.delete("all")
        self.ring_canvas.create_oval(18-expand, 18-expand, 92+expand, 92+expand, outline=self.c("ring_glow"), width=3)
        self.ring_canvas.create_oval(26, 26, 84, 84, fill=self.c("card"), outline=self.c("accent"), width=4)
        self.ring_canvas.create_text(55, 55, text="ALEXA", font=("Segoe UI", 9, "bold"), fill=self.c("accent"))

    def animate_ring(self, frames=14): # pulses ring while assistant speaks
        if frames <= 0:
            self.draw_ring(0)
            return
        expand = 6 if frames % 2 == 0 else 2
        self.draw_ring(expand)
        self.pulse_job = self.root.after(90, lambda: self.animate_ring(frames - 1))

    def type_text(self, label, full_text, idx=0): # smooth typewriter reveal animation
        if idx <= len(full_text):
            label.config(text=full_text[:idx])
            self.type_job = self.root.after(18, lambda: self.type_text(label, full_text, idx + 1))

    def tell_joke(self): # pulls next non-repeating joke and animates setup
        if self.type_job: self.root.after_cancel(self.type_job)
        if self.pulse_job: self.root.after_cancel(self.pulse_job)
        if not self.queue: # refills and shuffles queue when exhausted
            self.queue = self.jokes.copy()
            random.shuffle(self.queue)

        setup, self.punchline = self.queue.pop().split("?", 1)
        self.jokes_told += 1
        self.counter_lbl.config(text=f"Jokes Heard: {self.jokes_told}  •  Queue Left: {len(self.queue)}")
        self.punch_lbl.config(text="")
        self.animate_ring(16)
        self.type_text(self.setup_lbl, f"{setup}?")

    def show_punchline(self): # animates punchline reveal
        if not self.punchline: return
        if self.type_job: self.root.after_cancel(self.type_job)
        if self.pulse_job: self.root.after_cancel(self.pulse_job)
        self.animate_ring(12)
        self.type_text(self.punch_lbl, self.punchline.strip())

    def add_laugh(self): # increments interactive laugh counter
        self.laughs += 1
        self.laugh_btn.config(text=f"😂 Laugh ({self.laughs})")

if __name__ == "__main__":
    root = tk.Tk()
    AlexaJokeApp(root)
    root.mainloop()