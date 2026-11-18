import tkinter as tk
from tkinter import messagebox
import random

class MathsQuizApp:
    def __init__(self, root):
        # initialize main window and default quiz state
        self.root = root
        self.root.title("Maths Quiz")
        self.root.geometry("400x320")
        self.displayMenu()

    def clearScreen(self):
        # removes all current widgets so the next screen can be drawn cleanly
        for widget in self.root.winfo_children():
            widget.destroy()

    def displayMenu(self):
        # resets quiz variables and builds the difficulty selection screen
        self.clearScreen()
        self.score = 0
        self.question_num = 0

        tk.Label(self.root, text="DIFFICULTY LEVEL", font=("Arial", 14, "bold")).pack(pady=20)
        tk.Button(self.root, text="1. Easy (1-digit)", width=22, command=lambda: self.startQuiz(1)).pack(pady=5)
        tk.Button(self.root, text="2. Moderate (2-digit)", width=22, command=lambda: self.startQuiz(2)).pack(pady=5)
        tk.Button(self.root, text="3. Advanced (4-digit)", width=22, command=lambda: self.startQuiz(3)).pack(pady=5)

    def startQuiz(self, level):
        # saves chosen difficulty and launches the first question
        self.difficulty = level
        self.nextQuestion()

    def randomInt(self, level):
        # returns a random integer matching the digit length of the chosen difficulty
        if level == 1:
            return random.randint(1, 9)
        elif level == 2:
            return random.randint(10, 99)
        return random.randint(1000, 9999)

    def decideOperation(self):
        # randomly selects and returns either addition or subtraction as a char
        return random.choice(['+', '-'])

    def nextQuestion(self):
        # checks if 10 questions are done; otherwise generates a new problem
        if self.question_num >= 10:
            self.displayResults()
            return

        self.question_num += 1
        self.attempt = 1
        self.num1 = self.randomInt(self.difficulty)
        self.num2 = self.randomInt(self.difficulty)
        self.op = self.decideOperation()
        self.correct_ans = self.num1 + self.num2 if self.op == '+' else self.num1 - self.num2
        self.displayProblem()

    def displayProblem(self):
        # renders the current arithmetic question, input box, and submit button
        self.clearScreen()
        tk.Label(self.root, text=f"Question {self.question_num} of 10 | Score: {self.score}", font=("Arial", 10)).pack(pady=10)
        tk.Label(self.root, text=f"{self.num1} {self.op} {self.num2} =", font=("Arial", 20, "bold")).pack(pady=15)

        self.answer_entry = tk.Entry(self.root, font=("Arial", 14), justify="center")
        self.answer_entry.pack(pady=10)
        self.answer_entry.focus() # automatically places cursor in the input box
        self.answer_entry.bind("<Return>", lambda event: self.checkInput()) # allows pressing Enter to submit

        tk.Button(self.root, text="Submit Answer", width=18, command=self.checkInput).pack(pady=5)
        self.feedback_lbl = tk.Label(self.root, text="", font=("Arial", 10, "italic"))
        self.feedback_lbl.pack(pady=10)

    def checkInput(self):
        # defensive validation: ensures user entered a valid integer before grading
        try:
            user_ans = int(self.answer_entry.get().strip())
        except ValueError:
            self.feedback_lbl.config(text="Please enter a valid whole number.", fg="red")
            return
        self.isCorrect(user_ans, self.correct_ans)

    def isCorrect(self, user_ans, correct_ans):
        # evaluates answer, awards 10 or 5 points, and manages the 2-attempt rule
        if user_ans == correct_ans:
            points = 10 if self.attempt == 1 else 5
            self.score += points
            messagebox.showinfo("Correct!", f"Well done! +{points} points.")
            self.nextQuestion()
        elif self.attempt == 1:
            self.attempt = 2
            self.answer_entry.delete(0, tk.END) # clears wrong answer for retry
            self.feedback_lbl.config(text="Incorrect! You have 1 more try.", fg="red")
        else:
            messagebox.showerror("Incorrect", f"Out of tries! The correct answer was {correct_ans}.")
            self.nextQuestion()

    def displayResults(self):
        # calculates final grade out of 100 and prompts the user to play again
        self.clearScreen()
        if self.score > 90: grade = "A+"
        elif self.score >= 80: grade = "A"
        elif self.score >= 70: grade = "B"
        elif self.score >= 60: grade = "C"
        elif self.score >= 50: grade = "D"
        else: grade = "F"

        tk.Label(self.root, text="QUIZ COMPLETE", font=("Arial", 14, "bold")).pack(pady=20)
        tk.Label(self.root, text=f"Final Score: {self.score} / 100", font=("Arial", 13)).pack(pady=5)
        tk.Label(self.root, text=f"Rank / Grade: {grade}", font=("Arial", 16, "bold"), fg="blue").pack(pady=10)

        tk.Button(self.root, text="Play Again", width=18, command=self.displayMenu).pack(pady=5)
        tk.Button(self.root, text="Quit", width=18, command=self.root.destroy).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    MathsQuizApp(root)
    root.mainloop()