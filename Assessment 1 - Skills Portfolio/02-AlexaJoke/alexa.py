import tkinter as tk # imports the gui library
import random # imports random module

jokes_list = [] # global list to hold jokes
current_punchline = "" # global string to hold the hidden punchline

file = open("Assessment 1 - Skills Portfolio/02-AlexaJoke/randomJokes.txt", "r", encoding="utf-8") # opens file with the specific explicit path
jokes_list = file.readlines() # reads all lines into the list
file.close() # closes the file to free system resources

def tell_joke(): # defines function to get a new joke
    global current_punchline # allows changing the global variable inside this function
    selected_joke = random.choice(jokes_list).strip() # picks a random joke and removes hidden spaces
    
    parts = selected_joke.split('?', 1) # cuts the joke into two pieces at the first question mark
    setup = parts[0] + "?" # adds the question mark back to the first piece
    current_punchline = parts[1].strip() # saves the second piece as the punchline globally
    
    setup_label.config(text=setup) # updates the frontend text to show the setup
    punchline_label.config(text="") # erases any old punchline from the frontend

def show_punchline(): # defines function to reveal the punchline
    punchline_label.config(text=current_punchline) # changes frontend label to show the hidden punchline

root = tk.Tk() # creates the main application window
root.title("Alexa Joke Teller") # sets the window title
root.geometry("400x350") # sets the window size

setup_label = tk.Label(root, text="ready for a joke?", wraplength=350, pady=20, font=("arial", 11)) # creates the setup text label
setup_label.pack() # places the setup label on screen

punchline_label = tk.Label(root, text="", wraplength=350, pady=10, font=("arial", 11, "italic")) # creates the punchline text label
punchline_label.pack() # places the punchline label on screen

joke_btn = tk.Button(root, text="Alexa tell me a Joke", width=20, command=tell_joke) # creates main joke button
joke_btn.pack(pady=5) # places main joke button on screen

punchline_btn = tk.Button(root, text="Show Punchline", width=20, command=show_punchline) # creates punchline reveal button
punchline_btn.pack(pady=5) # places punchline button on screen

next_btn = tk.Button(root, text="Next Joke", width=20, command=tell_joke) # creates next joke button
next_btn.pack(pady=5) # places next joke button on screen

quit_btn = tk.Button(root, text="Quit", width=20, command=root.destroy) # creates quit button
quit_btn.pack(pady=5) # places quit button on screen

root.mainloop() # keeps the window open and running