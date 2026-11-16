import tkinter as tk # imports the standard python gui toolkit for visual elements
import random # imports random module to pick jokes unpredictably

class AlexaJokeApp: # creates a class to encapsulate gui state and avoid global variables
    def __init__(self, root): # initializes the application when the class is instantiated
        self.root = root # stores the main window object within the class for persistent access
        self.root.title("Alexa Joke Teller") # sets the text displayed in the top window bar
        self.root.geometry("400x350") # sets the physical pixel width and height of the window
        
        self.jokes_list = [] # creates an empty list to store jokes loaded from the text file
        self.current_punchline = "" # creates an empty string variable to hold the hidden punchline in memory
        
        self.load_jokes() # calls the method to read the text file immediately on startup
        self.build_ui() # calls the method to construct the buttons and labels on the screen

    def load_jokes(self): # defines the method responsible for data extraction
        try: # starts a safety block to handle potential file reading errors
            with open("randomJokes.txt", "r", encoding="utf-8") as file: # opens the text file securely in read mode
                self.jokes_list = file.readlines() # reads every line in the file and saves them as a list
        except FileNotFoundError: # catches the specific error if the text file is missing
            self.jokes_list = ["error?joke database not found"] # provides a fallback joke format to prevent gui crash

    def build_ui(self): # defines the method that places visual elements on the front end
        self.setup_label = tk.Label(self.root, text="ready for a joke?", wraplength=350, pady=20, font=("arial", 11)) # creates a text label for the setup with word wrap to prevent horizontal cutoff
        self.setup_label.pack() # mounts the setup label onto the main window vertically

        self.punchline_label = tk.Label(self.root, text="", wraplength=350, pady=10, font=("arial", 11, "italic")) # creates an initially blank text label reserved for the punchline
        self.punchline_label.pack() # mounts the punchline label directly below the setup label

        tk.Button(self.root, text="Alexa tell me a Joke", width=20, command=self.tell_joke).pack(pady=5) # creates and mounts the main joke trigger button mapped to the tell_joke function
        tk.Button(self.root, text="Show Punchline", width=20, command=self.show_punchline).pack(pady=5) # creates and mounts the reveal button mapped to the show_punchline function
        tk.Button(self.root, text="Next Joke", width=20, command=self.tell_joke).pack(pady=5) # creates and mounts a button to fetch a new joke using the same logic as the first button
        tk.Button(self.root, text="Quit", width=20, command=self.root.destroy).pack(pady=5) # creates and mounts a button that safely destroys the gui window and stops the program

    def tell_joke(self): # defines the logic executed when the joke buttons are clicked
        selected_joke = random.choice(self.jokes_list).strip() # picks one random line from the list and removes invisible trailing spaces
        
        if '?' in selected_joke: # checks if the required question mark delimiter exists in the string before splitting
            parts = selected_joke.split('?', 1) # splits the string into exactly two halves at the first question mark
            self.setup_label.config(text=parts[0] + "?") # updates the front end setup label with the first half and restores the question mark visibly
            self.current_punchline = parts[1].strip() # saves the second half securely in memory without displaying it on the gui yet
        else: # handles edge cases where the text file line is formatted incorrectly without a question mark
            self.setup_label.config(text=selected_joke) # displays the raw string as a fallback on the front end
            self.current_punchline = "" # empties the stored punchline to prevent mismatching with previous jokes
            
        self.punchline_label.config(text="") # erases the visible punchline on the front end when a new joke is loaded

    def show_punchline(self): # defines the logic executed when the punchline button is clicked
        self.punchline_label.config(text=self.current_punchline) # updates the front end punchline label to display the previously hidden string


if __name__ == "__main__": # ensures the app only runs if the script is executed directly
    root = tk.Tk() # creates the foundational gui window framework
    app = AlexaJokeApp(root) # injects the window framework into our custom object oriented class
    root.mainloop() # starts the continuous loop that keeps the graphical interface visible and interactive

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