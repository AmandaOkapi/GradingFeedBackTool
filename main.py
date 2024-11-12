import curses
import pyperclip

#Customizeable attributes
#headers
name = "Your Name"
email = "youremail@email.com"
officeHours = "Your office hours"
#footnotes
wellDone = "Well done" #if applied

#technicals
maxGrade = 60;
wellDoneAmount = int( (maxGrade *0.9))
OVERALL =0; #beware, global variable
##Sections
class Section:
    # Constructor to initialize attributes
    def __init__(self, name : str, weight: int, weightApplicable: bool = True):
        self.name = name  
        self.weight = weight
        self.score = weight      
        self.weightApplicable = weightApplicable 
        self.weightText =  "" if weightApplicable else f"({self.score} / {self.weight})"    
        self.deductionsBank =[]
        self.deductionsToStudent = []
    
class Deduction:
    # Constructor to initialize attributes
    def __init__(self, amount : int, reason : str):
        self.amount = amount  
        self.reason = reason


s0 = Section("Submission", 0, False)
s1 = Section("Part I", 20)
s2 = Section("Part II", 40)

sectionsList = [s0,s1,s2]



def calculateOverall():
    score = maxGrade
    for section in sectionsList:
        for d in section.deductionsToStudent:
            score += d.amount
    return score

def sectionScoreString(section):
    if(not section.weightApplicable):
        return ""
    score = section.weight
    for d in section.deductionsToStudent:
        score += d.amount
    return f"({score}/{section.weight})"

def Template():
    sectionsText = ""

    for section in sectionsList:
        sectionsText += f"{section.name} {sectionScoreString(section)}\n"  # Add section name and score
        for d in section.deductionsToStudent:
            sectionsText += f"\t({d.amount}) {d.reason}\n"  # Add deductions

    # Construct the full template
    template = f"""
Grading TA: {name}
Email: {email}
OH: {officeHours}
Grading Details: ({calculateOverall()}/{maxGrade})
{sectionsText}
{wellDone if calculateOverall() > maxGrade * 0.9 else ""}
    """
    return template

def confirmationMenu(stdscr, text : str, lineNum :int):
    #initial confirmation menu
    stdscr.addstr(lineNum, 0, text)
    # Highlight 'YES' by deafult
    stdscr.addstr("YES", curses.A_REVERSE)  
    stdscr.addstr(" or CANCEL ")        
    yes = True
    #show confirmation menu
    while True:
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_LEFT:
            stdscr.addstr(lineNum, 0, text)
            stdscr.addstr("YES", curses.A_REVERSE)  
            stdscr.addstr(" or CANCEL ")        
            yes = True
        elif key == curses.KEY_RIGHT:
            stdscr.addstr(lineNum, 0, text)
            stdscr.addstr("YES or ")  
            stdscr.addstr("CANCEL", curses.A_REVERSE)
            yes = False    
        elif key == ord("\n"):  # Enter key
            return yes    
        

#build the main menu
def main(stdscr):
    curses.curs_set(0)
    
    # Define main menu items
    mainMenu = ["Grade", "Settings", "Load Deductions", "Exit"]
    
    #track user scrolling
    selected_idx = 0
    
    while True:
        stdscr.clear()
        
        # Display menu
        for i, item in enumerate(mainMenu):
            if i == selected_idx:
                stdscr.addstr(i, 0, item, curses.A_REVERSE)  # Highlight selected item
            else:
                stdscr.addstr(i, 0, item)
        
        # Get user input
        key = stdscr.getch()
        
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(mainMenu) - 1:
            selected_idx += 1
        elif key == ord("\n"):  # Enter key
            #exit the loop and end the program if exit selected
            if(mainMenu[selected_idx] == "Exit"):
                break
            #otherwise handle the selection accordingly
            handleMainMenu(mainMenu[selected_idx], stdscr)
            #else:
             #   stdscr.addstr(len(menu) + 1, 0, f"You selected '{menu[selected_idx]}'")
           # stdscr.refresh()
           # stdscr.getch()  # Wait for another key press before returning to the menu

        stdscr.refresh()

def handleMainMenu(x, stdscr):
    match x:
        case "Grade":
            gradeMenu(stdscr)
            return
        case "Settings":
            stdscr.clear()
            stdscr.addstr(0,0,"Coming soon")
            stdscr.refresh()
            stdscr.getch()
            return
        case "Load Deductions":
            stdscr.clear()
            stdscr.addstr(0,0,"Loaded")
            #loading deductions
            sectionIndex =0;
            with open("deductions.txt", "r") as file:
                while True:
                    line = file.readline()
                    if not line:
                        break  # Exit the loop if there are no more lines to read
                    if(line == "BREAK\n"):
                        sectionIndex+=1
                        continue
                    sectionsList[sectionIndex].deductionsBank.append(Deduction(int(line), file.readline()))
            stdscr.refresh()
            stdscr.getch()
            return
        case "Exit":
            return ""
        case _:
            return

def gradeMenu(stdscr):
    #clean up global variables from previous student
    for item in sectionsList:
        item.deductionsToStudent = []

    # Define main menu items
    gradeMenuList = []
    sectionCnt=1;
    for item in sectionsList:
        gradeMenuList.append(f"Section {sectionCnt}: {item.name}")
        sectionCnt+=1
    gradeMenuList.append("View applied deductions")
    gradeMenuList.append("Finish")
    gradeMenuList.append("Cancel")

    #track user scrolling
    selected_idx = 0

    #Start the grade menu Displaying 
    while True:
        stdscr.clear()
        
        # Display grade menu
        stdscr.addstr(0, 0, f"Current Grade {calculateOverall()}/{maxGrade}")
        for i, item in enumerate(gradeMenuList):
            if i == selected_idx:
                stdscr.addstr(i+1, 0, item, curses.A_REVERSE)  # Highlight selected item
            else:
                stdscr.addstr(i+1, 0, item)
        
        # Get user input
        key = stdscr.getch()
        
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(gradeMenuList) - 1:
            selected_idx += 1
        elif key == ord("\n"):  # Enter key
            #exit the loop and end the program if exit selected
            if(gradeMenuList[selected_idx] == "Cancel"):
                if(confirmationMenu(stdscr, "Are you sure you would like to quit? ", len(gradeMenuList)+1)):
                    break
                else:
                    continue
            if(gradeMenuList[selected_idx] == "View applied deductions"):
                AppliedDeductionMenu(stdscr)
                continue
            if(gradeMenuList[selected_idx] == "Finish"):
                if(GenerateFeedback(stdscr)):
                    gradeMenu(stdscr)
                    break
                continue
            #otherwise handle the selection accordingly
            DeductionMenu(stdscr, selected_idx)
    

        stdscr.refresh()

def GenerateFeedback(stdscr):
    stdscr.clear()
    template = Template()
    #copy to clipboard
    pyperclip.copy(template)
    #append to a file
    with open('feedback.txt', 'a') as file:
        file.write(template)

    try:
        stdscr.addstr(0, 0, template)  # Print the entire template
    except curses.error:
        stdscr.addstr(0,0, "!Increase screen your size!")
        stdscr.refresh()
        stdscr.getch()
        return False
    
    if(confirmationMenu(stdscr, "Copied to clipboard and saved. Grade Another Student? ", len(template.splitlines()))):
        return True
    return False

def AppliedDeductionMenu(stdscr):
    stdscr.clear()
    i =0
    for section in sectionsList:
        stdscr.addstr(i, 0, section.name +":")
        i+=1
        for d in section.deductionsToStudent:
            stdscr.addstr(i, 0, f"({d.amount}) {d.reason}")
            i+=1
    stdscr.getch()

def DeductionMenu(stdscr, index):

    #display the deduction bank 


    #track user scrolling
    selected_idx = 0

    #Start the grade menu Displaying 
    while True:
        stdscr.clear()
        
        # Define main menu items
        deductionMenu = []
        deductionsToDisplay = sectionsList[index].deductionsBank
        for item in deductionsToDisplay:
            deductionMenu.append(f"({item.amount})  {item.reason}")
        deductionMenu.append("[Add new deduction to section]")
        deductionMenu.append("[Remove deduction from section]")
        deductionMenu.append("Back")

        # Display grade menu
        stdscr.addstr(0, 0, f"Section: {sectionsList[index].name}. Press <- to go back quickly!")
        for i, item in enumerate(deductionMenu):
            if i == selected_idx:
                stdscr.addstr(i+1, 0, item, curses.A_REVERSE)  # Highlight selected item
            else:
                stdscr.addstr(i+1, 0, item)
        
        # Get user input
        key = stdscr.getch()
        
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(deductionMenu) - 1:
            selected_idx += 1
        elif key == curses.KEY_LEFT:
            break
        elif key == ord("\n"):  # Enter key
            #exit the loop and end the program if exit selected
            if(deductionMenu[selected_idx] == "[Add new deduction to section]"):
                AddDeductionMenu(stdscr, index)
                stdscr.refresh()
                break
            if(deductionMenu[selected_idx] == "[Remove deduction from section]"):
                stdscr.clear()
                stdscr.addstr(0,0,"Coming soon")
                stdscr.refresh()
                stdscr.getch()
                #not yet implemented
                break
            if(deductionMenu[selected_idx] == "Back"):
                break
            #otherwise handle the selection accordingly

            #avoid duplicates
            if sectionsList[index].deductionsBank[selected_idx] in sectionsList[index].deductionsToStudent:
                stdscr.addstr(len(deductionMenu) + 1, 0, f"Error: deduction already applied to student")
                stdscr.addstr(len(deductionMenu) + 2, 0, f"Press any key to continue")
                stdscr.refresh()
                stdscr.getch()  # Wait for another key press before returning to the menu
                continue
            sectionsList[index].deductionsToStudent.append(sectionsList[index].deductionsBank[selected_idx])
            stdscr.addstr(len(deductionMenu) + 1, 0, f"Deduction: '{sectionsList[index].deductionsToStudent[-1].reason}' added")
            stdscr.addstr(len(deductionMenu) + 2, 0, f"Press any key to continue")
            stdscr.refresh()
            stdscr.getch()  # Wait for another key press before returning to the menu
            
        stdscr.refresh()

def AddDeductionMenu(stdscr, index):
    #loop to ensure valid inputs
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter 'q' to quit to cancel at anytime. ")

        stdscr.addstr(1, 0, "Enter a deduction amount: ")
        stdscr.refresh()
        # Get user input using curses
        curses.echo()  # Enable echoing of characters typed by the user
        user_input = stdscr.getstr(2, 0).decode('utf-8')  # Get input from the user as a string
        if(user_input =='q'):
            return
        try:
            number = int(user_input)  # Attempt to convert string to integer
        except ValueError:
            continue

        stdscr.addstr(3, 0, "Enter a deduction reason: ")
        stdscr.refresh()

        curses.echo()  # Enable echoing of characters typed by the user
        user_input = stdscr.getstr(4, 0).decode('utf-8')  # Get input from the user as a string

        stdscr.addstr(5, 0, f"Deduction: ({number}) {user_input}")

        if(confirmationMenu(stdscr,"Add deduction to student and section bank: ", 6)):
            d = Deduction(number, user_input)
            sectionsList[index].deductionsBank.append(d)
            sectionsList[index].deductionsToStudent.append(d)
            with open("deductions.txt", "w") as file:
                pass #clear the file
            with open("deductions.txt", "a") as file:
                for s in sectionsList:
                    for d in s.deductionsBank:
                        file.write(str(d.amount) + '\n')
                        file.write(d.reason+ '\n')
                    file.write("BREAK"+ '\n')
        return



curses.wrapper(main)
