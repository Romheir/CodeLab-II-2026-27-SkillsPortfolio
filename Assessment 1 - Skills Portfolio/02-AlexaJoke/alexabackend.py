import random

jokes_list = [] # global list to hold jokes
current_punchline = "" # global string for the hidden punchline

# basic file read without error handling
file = open("randomJokes.txt", "r") 
jokes_list = file.readlines()
file.close()

def tell_joke_logic():
    global current_punchline # forces python to use the global variable
    selected_joke = random.choice(jokes_list)
    
    # basic split assuming every line has a question mark
    parts = selected_joke.split('?')
    setup = parts[0] + "?"
    current_punchline = parts[1]
    
    return setup

def show_punchline_logic():
    return current_punchline