import tkinter as tk # imports the standard gui toolkit
import random # imports random module for unpredictable joke selection
import os # imports operating system module for dynamic file path handling

class AlexaJokeApp: # encapsulates everything into a class to avoid global variables
    def __init__(self, root): # initializes the object when created
        self.root = root # saves the main window reference
        self.root.title("Alexa Joke Teller") # sets the window title text
        self.root.geometry("400x350") # sets the physical dimensions of the window
        
        self.jokes_list = [] # creates an empty instance list for jokes
        self.current_punchline = "" # creates an empty instance string for the punchline
        
        self.load_jokes() # triggers the file reading method
        self.build_ui() # triggers the frontend construction method

    def load_jokes(self): # defines the secure file reading logic
        current_dir = os.path.dirname(__file__) # finds exactly where this python script lives on the hard drive
        file_path = os.path.join(current_dir, "randomJokes.txt") # builds a foolproof dynamic path to the text file
        
        try: # starts a safety block to catch missing files
            with open(file_path, "r", encoding="utf-8") as file: # opens file securely and closes it automatically after
                self.jokes_list = file.readlines() # loads all lines into the instance list
        except FileNotFoundError: # catches the error if the text file is missing
            self.jokes_list = ["error?joke database not found"] # sets fallback data to prevent app crash

    def build_ui(self): # defines the method that places all frontend visual elements
        self.setup_label = tk.Label(self.root, text="ready for a joke?", wraplength=350, pady=20, font=("arial", 11)) # creates setup label with word wrap
        self.setup_label.pack() # places setup label on the screen

        self.punchline_label = tk.Label(self.root, text="", wraplength=350, pady=10, font=("arial", 11, "italic")) # creates punchline label
        self.punchline_label.pack() # places punchline label on the screen

        tk.Button(self.root, text="Alexa tell me a Joke", width=20, command=self.tell_joke).pack(pady=5) # creates and places first joke button
        tk.Button(self.root, text="Show Punchline", width=20, command=self.show_punchline).pack(pady=5) # creates and places punchline button
        tk.Button(self.root, text="Next Joke", width=20, command=self.tell_joke).pack(pady=5) # creates and places next joke button
        tk.Button(self.root, text="Quit", width=20, command=self.root.destroy).pack(pady=5) # creates and places quit button

    def tell_joke(self): # defines the logic for selecting and splitting a joke
        selected_joke = random.choice(self.jokes_list).strip() # picks one random joke and strips trailing spaces
        
        if '?' in selected_joke: # verifies the delimiter exists before splitting
            parts = selected_joke.split('?', 1) # splits string at the first question mark
            self.setup_label.config(text=parts[0] + "?") # updates frontend setup label
            self.current_punchline = parts[1].strip() # securely stores punchline in instance variable
        else: # handles poorly formatted jokes missing a question mark
            self.setup_label.config(text=selected_joke) # shows raw text
            self.current_punchline = "" # clears punchline memory
            
        self.punchline_label.config(text="") # erases the visible punchline from the frontend

    def show_punchline(self): # defines logic for revealing the punchline
        self.punchline_label.config(text=self.current_punchline) # updates frontend label with the stored punchline string


if __name__ == "__main__": # execution guard ensures script only runs when directly executed
    root = tk.Tk() # builds the main tkinter window framework
    app = AlexaJokeApp(root) # links the window to the object oriented application class
    root.mainloop() # runs the continuous event loop