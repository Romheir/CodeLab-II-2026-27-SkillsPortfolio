import tkinter as tk # imports tkinter library for the gui
import random # imports random module to select jokes

def tell_joke(): # defines function to fetch and display the joke setup
    pass # placeholder for file reading and random selection logic

def show_punchline(): # defines function to display the joke punchline
    pass # placeholder for punchline reveal logic

root = tk.Tk() # initializes the main application window
root.title("Alexa Joke Teller") # sets the text in the window title bar
root.geometry("400x300") # sets the default width and height of the window

setup_label = tk.Label(root, text="Click below to hear a joke!", wraplength=350, pady=20) # creates text label for the joke setup
setup_label.pack() # places the setup label into the window

punchline_label = tk.Label(root, text="", wraplength=350, pady=10) # creates empty text label for the punchline
punchline_label.pack() # places the punchline label into the window

joke_btn = tk.Button(root, text="Alexa tell me a Joke", command=tell_joke) # creates button that runs tell_joke function
joke_btn.pack(pady=5) # places the joke button into the window with vertical padding

punchline_btn = tk.Button(root, text="Show Punchline", command=show_punchline) # creates button that runs show_punchline function
punchline_btn.pack(pady=5) # places the punchline button into the window with vertical padding

quit_btn = tk.Button(root, text="Quit", command=root.destroy) # creates button that closes the application
quit_btn.pack(pady=5) # places the quit button into the window with vertical padding

root.mainloop() # runs the main event loop to keep the window open