import tkinter as tk # gui library
import random # random joke selection
import os # dynamic file path handling

class AlexaJokeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alexa Joke Teller")
        self.root.geometry("400x320")
        self.punchline = ""
        self.jokes = self.load_jokes()
        self.build_ui()

    def load_jokes(self):
        path = os.path.join(os.path.dirname(__file__), "randomJokes.txt") # finds file regardless of terminal location
        try:
            with open(path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if "?" in line] # loads only valid jokes with a delimiter
        except FileNotFoundError:
            return ["Error?randomJokes.txt not found."] # prevents crash if file is missing

    def build_ui(self):
        self.setup_lbl = tk.Label(self.root, text="Click below for a joke!", wraplength=350, pady=20, font=("Arial", 11))
        self.setup_lbl.pack()

        self.punch_lbl = tk.Label(self.root, text="", wraplength=350, pady=10, font=("Arial", 11, "italic"))
        self.punch_lbl.pack()

        tk.Button(self.root, text="Alexa tell me a Joke", width=20, command=self.tell_joke).pack(pady=4)
        tk.Button(self.root, text="Show Punchline", width=20, command=self.show_punchline).pack(pady=4)
        tk.Button(self.root, text="Next Joke", width=20, command=self.tell_joke).pack(pady=4)
        tk.Button(self.root, text="Quit", width=20, command=self.root.destroy).pack(pady=4)

    def tell_joke(self):
        setup, self.punchline = random.choice(self.jokes).split("?", 1) # splits setup and punchline in one step
        self.setup_lbl.config(text=f"{setup}?")
        self.punch_lbl.config(text="") # clears previous punchline

    def show_punchline(self):
        self.punch_lbl.config(text=self.punchline.strip())

if __name__ == "__main__":
    root = tk.Tk()
    AlexaJokeApp(root)
    root.mainloop()