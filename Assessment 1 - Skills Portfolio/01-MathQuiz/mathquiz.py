import tkinter as tk # imports standard gui library
from tkinter import messagebox # imports secondary popup dialog module
import random # imports random module for numbers and operators

class MathsQuizApp: # encapsulates quiz state and ui inside one class
    def __init__(self, root): # runs automatically when app starts
        self.root = root # stores main window reference
        self.root.title("Maths Quiz") # sets top window bar title
        self.root.geometry("400x320") # sets fixed window width and height
        self.displayMenu() # loads difficulty menu on startup

    def clearScreen(self): # helper to wipe current screen before drawing next one
        for widget in self.root.winfo_children(): # loops through every visible element in window
            widget.destroy() # removes element from screen

    def displayMenu(self): # builds initial difficulty selection screen
        self.clearScreen() # clears any previous screen elements
        self.score = 0 # resets user score to zero
        self.question_num = 0 # resets question counter to zero

        tk.Label(self.root, text="DIFFICULTY LEVEL", font=("Arial", 14, "bold")).pack(pady=20) # displays menu title
        tk.Button(self.root, text="1. Easy (1-digit)", width=22, command=lambda: self.startQuiz(1)).pack(pady=5) # button passes level 1 to startQuiz
        tk.Button(self.root, text="2. Moderate (2-digit)", width=22, command=lambda: self.startQuiz(2)).pack(pady=5) # button passes level 2 to startQuiz
        tk.Button(self.root, text="3. Advanced (4-digit)", width=22, command=lambda: self.startQuiz(3)).pack(pady=5) # button passes level 3 to startQuiz

    def startQuiz(self, level): # saves chosen difficulty and begins quiz
        self.difficulty = level # stores selected difficulty level
        self.nextQuestion() # triggers first question

    def randomInt(self, level): # generates random number based on chosen difficulty
        if level == 1: # checks for easy mode
            return random.randint(1, 9) # returns single digit number
        elif level == 2: # checks for moderate mode
            return random.randint(10, 99) # returns double digit number
        return random.randint(1000, 9999) # returns four digit number for advanced mode

    def decideOperation(self): # picks addition or subtraction randomly
        return random.choice(['+', '-']) # returns either plus or minus char

    def nextQuestion(self): # manages 10 question limit and generates new math problem
        if self.question_num >= 10: # checks if all 10 questions are finished
            self.displayResults() # moves to final score screen
            return # stops function from generating another question

        self.question_num += 1 # increments current question count
        self.attempt = 1 # resets attempt counter to first try
        self.num1 = self.randomInt(self.difficulty) # generates first random operand
        self.num2 = self.randomInt(self.difficulty) # generates second random operand
        self.op = self.decideOperation() # generates random operator
        self.correct_ans = self.num1 + self.num2 if self.op == '+' else self.num1 - self.num2 # computes and stores real answer
        self.displayProblem() # draws question onto screen

    def displayProblem(self): # builds active question screen
        self.clearScreen() # wipes previous widgets
        tk.Label(self.root, text=f"Question {self.question_num} of 10 | Score: {self.score}", font=("Arial", 10)).pack(pady=10) # displays progress and live score
        tk.Label(self.root, text=f"{self.num1} {self.op} {self.num2} =", font=("Arial", 20, "bold")).pack(pady=15) # displays actual math problem

        self.answer_entry = tk.Entry(self.root, font=("Arial", 14), justify="center") # creates text box for user answer
        self.answer_entry.pack(pady=10) # places text box on screen
        self.answer_entry.focus() # places typing cursor inside box automatically
        self.answer_entry.bind("<Return>", lambda event: self.checkInput()) # lets user press enter key to submit

        tk.Button(self.root, text="Submit Answer", width=18, command=self.checkInput).pack(pady=5) # button triggers input validation
        self.feedback_lbl = tk.Label(self.root, text="", font=("Arial", 10, "italic")) # creates empty label for inline error text
        self.feedback_lbl.pack(pady=10) # places feedback label below submit button

    def checkInput(self): # validates user input before grading
        try: # starts safety block to catch non numeric text
            user_ans = int(self.answer_entry.get().strip()) # reads text box and converts string to integer
        except ValueError: # catches letters symbols or blank submissions
            self.feedback_lbl.config(text="Please enter a valid whole number.", fg="red") # shows red warning on main window
            return # stops grading so user keeps their attempt
        self.isCorrect(user_ans, self.correct_ans) # passes clean integer to grading function

    def isCorrect(self, user_ans, correct_ans): # grades answer and controls two attempt rule
        if user_ans == correct_ans: # checks if user answer matches real answer
            points = 10 if self.attempt == 1 else 5 # awards 10 points on first try or 5 on second
            self.score += points # adds earned points to total score
            messagebox.showinfo("Correct!", f"Well done! +{points} points.") # launches blue secondary popup window for correct answer
            self.nextQuestion() # moves to next question after popup is closed
        elif self.attempt == 1: # checks if this was their first wrong attempt
            self.attempt = 2 # updates state to second and final attempt
            self.answer_entry.delete(0, tk.END) # clears wrong number from input box
            self.feedback_lbl.config(text="Incorrect! You have 1 more try.", fg="red") # shows inline retry warning on main window
        else: # runs when user fails second attempt
            messagebox.showerror("Incorrect", f"Out of tries! The correct answer was {correct_ans}.") # launches red secondary popup window showing real answer
            self.nextQuestion() # moves to next question after popup is closed

    def displayResults(self): # builds final score and rank screen
        self.clearScreen() # wipes quiz screen widgets
        if self.score > 90: grade = "A+" # assigns A+ for scores above 90
        elif self.score >= 80: grade = "A" # assigns A for 80 to 90
        elif self.score >= 70: grade = "B" # assigns B for 70 to 79
        elif self.score >= 60: grade = "C" # assigns C for 60 to 69
        elif self.score >= 50: grade = "D" # assigns D for 50 to 59
        else: grade = "F" # assigns F for scores under 50

        tk.Label(self.root, text="QUIZ COMPLETE", font=("Arial", 14, "bold")).pack(pady=20) # displays completion header
        tk.Label(self.root, text=f"Final Score: {self.score} / 100", font=("Arial", 13)).pack(pady=5) # displays final score out of 100
        tk.Label(self.root, text=f"Rank / Grade: {grade}", font=("Arial", 16, "bold"), fg="blue").pack(pady=10) # displays letter rank

        tk.Button(self.root, text="Play Again", width=18, command=self.displayMenu).pack(pady=5) # button restarts quiz at difficulty menu
        tk.Button(self.root, text="Quit", width=18, command=self.root.destroy).pack(pady=5) # button closes application safely

if __name__ == "__main__": # ensures script only runs when executed directly
    root = tk.Tk() # creates foundational tkinter window
    MathsQuizApp(root) # injects window into quiz app class
    root.mainloop() # starts main event loop to keep gui open