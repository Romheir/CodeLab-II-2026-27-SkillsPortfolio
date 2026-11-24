import tkinter as tk # imports standard gui library
import random # imports random module to pick jokes unpredictably
import os # imports os module for dynamic file path handling

class AlexaJokeApp: # encapsulates app state and ui inside one class
    def __init__(self, root): # runs automatically when app starts
        self.root = root # stores main window reference
        self.root.title("Alexa Joke Teller") # sets top window bar title
        self.root.geometry("400x320") # sets fixed window width and height
        self.punchline = "" # initializes empty string to hold hidden punchline
        self.jokes = self.load_jokes() # loads valid jokes list from text file on startup
        self.build_ui() # draws all labels and buttons onto screen

    def load_jokes(self): # reads and filters jokes from external text file
        path = os.path.join(os.path.dirname(__file__), "randomJokes.txt") # builds dynamic file path next to this script
        try: # starts safety block to catch missing file errors
            with open(path, "r", encoding="utf-8") as f: # opens text file securely and auto closes after
                return [line.strip() for line in f if "?" in line] # returns cleaned list of lines containing question mark
        except FileNotFoundError: # catches crash if text file is missing
            return ["Error?randomJokes.txt not found."] # returns fallback string so app stays open

    def build_ui(self): # constructs all frontend visual elements
        self.setup_lbl = tk.Label(self.root, text="Click below for a joke!", wraplength=350, pady=20, font=("Arial", 11)) # creates setup text label with word wrap
        self.setup_lbl.pack() # mounts setup label onto main window

        self.punch_lbl = tk.Label(self.root, text="", wraplength=350, pady=10, font=("Arial", 11, "italic")) # creates empty italic label for punchline
        self.punch_lbl.pack() # mounts punchline label below setup label

        tk.Button(self.root, text="Alexa tell me a Joke", width=20, command=self.tell_joke).pack(pady=4) # creates and mounts main joke trigger button
        tk.Button(self.root, text="Show Punchline", width=20, command=self.show_punchline).pack(pady=4) # creates and mounts punchline reveal button
        tk.Button(self.root, text="Next Joke", width=20, command=self.tell_joke).pack(pady=4) # creates and mounts next joke button reusing tell_joke
        tk.Button(self.root, text="Quit", width=20, command=self.root.destroy).pack(pady=4) # creates and mounts button that closes window safely

    def tell_joke(self): # picks random joke and separates setup from punchline
        setup, self.punchline = random.choice(self.jokes).split("?", 1) # splits random joke at first question mark into two variables
        self.setup_lbl.config(text=f"{setup}?") # updates frontend setup label and restores question mark
        self.punch_lbl.config(text="") # clears previous punchline from screen

    def show_punchline(self): # reveals stored punchline on frontend
        self.punch_lbl.config(text=self.punchline.strip()) # updates punchline label with cleaned punchline text

if __name__ == "__main__": # ensures script only runs when executed directly
    root = tk.Tk() # creates foundational tkinter window
    AlexaJokeApp(root) # injects window into joke app class
    root.mainloop() # starts main event loop to keep gui open