import tkinter as tk # imports standard gui library
from tkinter import messagebox, simpledialog, scrolledtext # imports popups input dialogs and scrollable text box
import os # imports os module for dynamic file path handling

class StudentManagerApp: # encapsulates student data and gui inside one class
    def __init__(self, root): # runs automatically when app starts
        self.root = root # stores main window reference
        self.root.title("Student Manager") # sets top window bar title
        self.root.geometry("620x520") # sets fixed window width and height
        self.file_path = os.path.join(os.path.dirname(__file__), "studentMarks.txt") # builds dynamic path to data file
        self.students = [] # initializes empty list to hold student dictionaries
        self.load_data() # loads student records from text file on startup
        self.build_ui() # draws buttons and output area onto screen

    def load_data(self): # reads studentMarks.txt into memory safely
        self.students = [] # resets list before loading
        try: # starts safety block to catch missing file errors
            with open(self.file_path, "r", encoding="utf-8") as f: # opens text file securely in read mode
                lines = [line.strip() for line in f if line.strip()] # reads non empty lines and strips spaces
                for line in lines[1:]: # skips first line count and loops through student records
                    parts = line.split(",") # splits comma separated values into list
                    self.students.append({ # stores each student as a clean dictionary
                        "code": int(parts[0]), "name": parts[1],
                        "cw": [int(parts[2]), int(parts[3]), int(parts[4])], "exam": int(parts[5])
                    })
        except FileNotFoundError: # catches crash if text file is missing
            messagebox.showerror("Error", "studentMarks.txt not found.") # shows red popup warning

    def save_data(self): # writes updated student list back to studentMarks.txt
        with open(self.file_path, "w", encoding="utf-8") as f: # opens file in write mode to overwrite cleanly
            f.write(f"{len(self.students)}\n") # writes updated total student count on line 1
            for s in self.students: # loops through every student dictionary
                f.write(f"{s['code']},{s['name']},{s['cw'][0]},{s['cw'][1]},{s['cw'][2]},{s['exam']}\n") # writes csv line

    def calc_stats(self, s): # calculates coursework total overall percentage and letter grade
        cw_total = sum(s["cw"]) # adds the three coursework marks out of 60
        pct = ((cw_total + s["exam"]) / 160) * 100 # computes overall percentage out of 160 total marks
        if pct >= 70: grade = "A" # assigns A for 70 percent and above
        elif pct >= 60: grade = "B" # assigns B for 60 to 69 percent
        elif pct >= 50: grade = "C" # assigns C for 50 to 59 percent
        elif pct >= 40: grade = "D" # assigns D for 40 to 49 percent
        else: grade = "F" # assigns F for under 40 percent
        return cw_total, pct, grade # returns all three calculated values

    def format_student(self, s): # formats one student dictionary into readable text block
        cw_total, pct, grade = self.calc_stats(s) # fetches calculated stats
        return (f"Name: {s['name']} | Number: {s['code']}\n" # formats name and id line
                f"Coursework: {cw_total}/60 | Exam: {s['exam']}/100 | " # formats marks line
                f"Overall: {pct:.2f}% | Grade: {grade}\n" + "-"*55 + "\n") # formats percentage grade and divider

    def show_output(self, text): # replaces content inside the scrollable output box
        self.output.config(state="normal") # temporarily unlocks text box for editing
        self.output.delete("1.0", tk.END) # clears all previous text
        self.output.insert(tk.END, text) # inserts new formatted text
        self.output.config(state="disabled") # locks text box so user cannot accidentally type in it

    def find_student(self): # prompts user for name or code and returns matching student
        query = simpledialog.askstring("Find Student", "Enter Student Name or Number:") # opens text input popup
        if not query: return None # exits safely if user clicks cancel
        q = query.strip().lower() # normalizes input for case insensitive matching
        for s in self.students: # searches through all students
            if str(s["code"]) == q or s["name"].lower() == q: # checks exact code or name match
                return s # returns matching student dictionary
        messagebox.showinfo("Not Found", "No matching student record found.") # informs user if no match exists
        return None # returns nothing when not found

    def build_ui(self): # constructs frontend menu buttons and scrollable display
        tk.Label(self.root, text="STUDENT MANAGER", font=("Arial", 14, "bold")).pack(pady=10) # displays app header
        btn_frame = tk.Frame(self.root) # creates container frame to align buttons in a grid
        btn_frame.pack(pady=5) # mounts button frame below header

        buttons = [ # defines all 8 menu options and their linked methods
            ("1. View All", self.view_all), ("2. View Individual", self.view_one),
            ("3. Highest Score", self.view_highest), ("4. Lowest Score", self.view_lowest),
            ("5. Sort Records", self.sort_records), ("6. Add Student", self.add_student),
            ("7. Delete Student", self.delete_student), ("8. Update Student", self.update_student)
        ]
        for i, (label, cmd) in enumerate(buttons): # loops through button list to place them cleanly
            tk.Button(btn_frame, text=label, width=18, command=cmd).grid(row=i//4, column=i%4, padx=4, pady=4) # arranges 2 rows of 4 buttons

        self.output = scrolledtext.ScrolledText(self.root, width=70, height=22, font=("Consolas", 10), state="disabled") # creates read only scrollable display box
        self.output.pack(pady=10, padx=10) # mounts display box onto main window

    def view_all(self, data=None): # option 1 displays all records plus class summary
        records = data if data is not None else self.students # uses custom sorted list if provided else full list
        if not records: # checks if dataset is empty
            self.show_output("No student records available.") # displays empty message
            return # exits function early
        text = "".join(self.format_student(s) for s in records) # combines all formatted student blocks
        avg = sum(self.calc_stats(s)[1] for s in records) / len(records) # calculates class average percentage
        text += f"\nSUMMARY: {len(records)} Students | Average Percentage: {avg:.2f}%" # appends required summary line
        self.show_output(text) # pushes final output to screen

    def view_one(self): # option 2 displays single chosen student
        s = self.find_student() # asks user to pick a student
        if s: self.show_output(self.format_student(s)) # displays formatted record if found

    def view_highest(self): # option 3 finds and displays highest scoring student
        if not self.students: return # exits safely if list is empty
        top = max(self.students, key=lambda s: sum(s["cw"]) + s["exam"]) # finds student with max total marks
        self.show_output("HIGHEST OVERALL SCORE:\n\n" + self.format_student(top)) # displays top student

    def view_lowest(self): # option 4 finds and displays lowest scoring student
        if not self.students: return # exits safely if list is empty
        low = min(self.students, key=lambda s: sum(s["cw"]) + s["exam"]) # finds student with min total marks
        self.show_output("LOWEST OVERALL SCORE:\n\n" + self.format_student(low)) # displays lowest student

    def sort_records(self): # option 5 sorts records ascending or descending by total score
        order = simpledialog.askstring("Sort", "Enter 'asc' for ascending or 'desc' for descending:") # asks sort direction
        if not order or order.strip().lower() not in ("asc", "desc"): return # exits if cancelled or invalid
        rev = order.strip().lower() == "desc" # sets reverse flag true for descending
        sorted_list = sorted(self.students, key=lambda s: sum(s["cw"]) + s["exam"], reverse=rev) # sorts students by total score
        self.view_all(sorted_list) # reuses view_all to display sorted list and summary

    def add_student(self): # option 6 adds new student and saves to file
        code = simpledialog.askinteger("Add Student", "Student Code (1000-9999):", minvalue=1000, maxvalue=9999) # validates 4 digit code
        if code is None: return # exits if cancelled
        name = simpledialog.askstring("Add Student", "Student Full Name:") # asks for student name
        if not name: return # exits if cancelled or blank
        cw = [simpledialog.askinteger("Add Student", f"Coursework {i+1} (0-20):", minvalue=0, maxvalue=20) for i in range(3)] # validates 3 cw marks
        if None in cw: return # exits if any mark cancelled
        exam = simpledialog.askinteger("Add Student", "Exam Mark (0-100):", minvalue=0, maxvalue=100) # validates exam mark
        if exam is None: return # exits if cancelled
        self.students.append({"code": code, "name": name.strip(), "cw": cw, "exam": exam}) # adds new record to memory
        self.save_data() # saves updated list back to studentMarks.txt
        messagebox.showinfo("Added", f"{name.strip()} added and saved.") # confirms save via popup
        self.view_all() # refreshes display

    def delete_student(self): # option 7 deletes chosen student and updates file
        s = self.find_student() # asks user which student to delete
        if not s: return # exits if not found
        self.students.remove(s) # removes student from memory list
        self.save_data() # saves updated list back to studentMarks.txt
        messagebox.showinfo("Deleted", f"{s['name']} deleted from records.") # confirms deletion via popup
        self.view_all() # refreshes display

    def update_student(self): # option 8 updates specific field of a chosen student
        s = self.find_student() # asks user which student to update
        if not s: return # exits if not found
        field = simpledialog.askstring("Update", "Field to update (name, cw1, cw2, cw3, exam):") # asks which field to edit
        if not field: return # exits if cancelled
        f = field.strip().lower() # normalizes field choice
        if f == "name": # handles name update
            val = simpledialog.askstring("Update", "New Name:") # prompts for new name
            if val: s["name"] = val.strip() # saves new name
        elif f in ("cw1", "cw2", "cw3"): # handles coursework mark update
            val = simpledialog.askinteger("Update", f"New {f.upper()} (0-20):", minvalue=0, maxvalue=20) # validates new cw mark
            if val is not None: s["cw"][int(f[2]) - 1] = val # updates specific cw index
        elif f == "exam": # handles exam mark update
            val = simpledialog.askinteger("Update", "New Exam Mark (0-100):", minvalue=0, maxvalue=100) # validates new exam mark
            if val is not None: s["exam"] = val # updates exam mark
        else: # handles unrecognized field input
            messagebox.showerror("Invalid", "Use: name, cw1, cw2, cw3, or exam.") # warns user
            return # exits without saving
        self.save_data() # saves updated record back to studentMarks.txt
        messagebox.showinfo("Updated", f"{s['name']}'s record updated.") # confirms update via popup
        self.view_all() # refreshes display

if __name__ == "__main__": # ensures script only runs when executed directly
    root = tk.Tk() # creates foundational tkinter window
    StudentManagerApp(root) # injects window into student manager class
    root.mainloop() # starts main event loop to keep gui open