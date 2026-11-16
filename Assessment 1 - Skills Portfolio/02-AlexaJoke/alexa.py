import tkinter as tk # imports the gui library
import random # imports random module

# global variables to store state
jokes_list = [] 
current_punchline = "" 

# read the file immediately before building the gui
# since you moved randomJokes.txt to the same folder, this will now work perfectly
file = open("Assessment 1 - Skills Portfolio/02-AlexaJoke/randomJokes.txt", "r", encoding="utf-8")
jokes_list = file.readlines()
file.close()

def tell_joke(): # function triggered by the joke buttons
    global current_punchline # allows modification of the global variable
    selected_joke = random.choice(jokes_list).strip() # picks a random joke and cleans invisible spaces
    
    parts = selected_joke.split('?', 1) # splits the text at the first question mark
    setup = parts[0] + "?" # restores the question mark for the setup string
    current_punchline = parts[1].strip() # saves the punchline globally for later use
    
    setup_label.config(text=setup) # updates the frontend setup label text
    punchline_label.config(text="") # clears any previous punchline from the frontend

def show_punchline(): # function triggered by the punchline button
    punchline_label.config(text=current_punchline) # updates the frontend punchline label with the hidden text

# set up the main window
root = tk.Tk()
root.title("Alexa Joke Teller")
root.geometry("400x350")

# create and pack frontend labels
setup_label = tk.Label(root, text="ready for a joke?", wraplength=350, pady=20, font=("arial", 11))
setup_label.pack()

punchline_label = tk.Label(root, text="", wraplength=350, pady=10, font=("arial", 11, "italic"))
punchline_label.pack()

# create and pack frontend buttons mapping to the functions above
joke_btn = tk.Button(root, text="Alexa tell me a Joke", width=20, command=tell_joke)
joke_btn.pack(pady=5)

punchline_btn = tk.Button(root, text="Show Punchline", width=20, command=show_punchline)
punchline_btn.pack(pady=5)

next_btn = tk.Button(root, text="Next Joke", width=20, command=tell_joke)
next_btn.pack(pady=5)

quit_btn = tk.Button(root, text="Quit", width=20, command=root.destroy)
quit_btn.pack(pady=5)

# start the gui event loop at the very end of the script
root.mainloop()