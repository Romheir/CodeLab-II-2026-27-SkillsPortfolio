import random
import os

class JokeBackend:
    def __init__(self):
        self.jokes_list = []
        self.current_punchline = ""
        self.load_jokes()

    def load_jokes(self):
        try: # prevents app crash if the text file is renamed or missing
            with open("randomJokes.txt", "r", encoding="utf-8") as file: # auto closes file after reading
                self.jokes_list = file.readlines()
        except FileNotFoundError:
            self.jokes_list = ["error?joke database not found"] # fallback data

    def get_new_joke(self):
        selected_joke = random.choice(self.jokes_list).strip() # strip removes invisible whitespace and newline characters
        
        if '?' in selected_joke: # safe split only if delimiter exists
            parts = selected_joke.split('?', 1) 
            setup = parts[0] + "?"
            self.current_punchline = parts[1].strip()
            return setup
        else:
            self.current_punchline = ""
            return selected_joke

    def get_punchline(self):
        return self.current_punchline