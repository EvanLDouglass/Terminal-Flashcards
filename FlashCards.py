"""
A simple flash cards program for the terminal. Current implementation is not 
secure and will not maintain data between machines unless files are saved and 
transferred. Assumes operation on a Windows machine. Currently, new users will 
have to create a directory with name = username before using the program.
Author: Evan L. Douglass
Version 1: Storage using dictionaries and .txt files
"""
import random  # Used for test function

# Path to folder constant
PATH = "C:\\Users\\Evan\\PythonProjects\\FlashCards\\"

# Global variables for current user, current deck and active dictionary
User = ""
Deck = ""
ActiveDict = {}
firstRun = True

def main():
    """
    Driver function.
    """
    # Welcome message
    print('Welcome to "Terminal Flashcards"!')

    # Initial setup
    selectUser()
    
    # Display all commands and process response. Repeat as necessary.
    displayMenu()


def selectUser():
    """
    Gives a welcome message and gets info needed to run the program on start.
    """
    global Deck
    global User

    # Get user
    User = input("\tEnter User: ")

    # Use old deck or create new deck?
    prompt = "Load old deck (-l) or create new deck (-n)? "
    answer = getValidResponse(["-l", "-n"], prompt)

    # Old deck
    if answer == "-l":
        Deck = input("\tEnter deck name: ")
        loadDeck(Deck, User)
    # New deck
    elif answer == "-n":
        Deck = input("Enter new deck name: ")
        loadDeck(Deck, User, new=True)


def displayMenu():
    """
    Displays a menu with command options then processes user response.
    """
    print("Select a command below:")
    print("\t-t Test yourself")
    print("\t-a Add a card")
    print("\t-d Delete a card")
    print("\t-p Print full deck")
    print("\t-s Save current deck")
    print("\t-n Create a new deck")
    print("\t-l Load a saved deck")
    print("\t-u Select user")
    print("\t-m Display menu")
    print("\t-q Quit program")

    processCommand()


def processCommand():
    """
    Directs given command to appropriate function. Assumes command is valid.
    """
    global Deck
    global User

    command = displayPrompt()

    if command == "-t":
        test()

    elif command == "-a":
        addCard()

    elif command == "-d":
        deleteCard()

    elif command == "-p":
        printDeck()

    elif command == "-s":
        saveDeck()

    elif command == "-n":
        Deck = input("Enter new deck name: ")
        loadDeck(Deck, User, new=True)

    elif command == "-l":
        Deck = input("Ender deck name: ")
        loadDeck(Deck, User)

    elif command == "-u":
        User = input("User: ")
        Deck = input("Deck: ")
        selectUser()

    elif command == "-m":
        displayMenu()

    elif command == "-q":
        save = input("'-s to save changes: ")
        if save == "-s":
            saveDeck()
        exit()

    # command has been validated already, don't need final else


def displayPrompt():
    """
    Displays a prompt symbol at which commands are entered.
    Returns the validated command as a string.
    """
    validCommands = ["-t", "-a", "-d", "-p", "-s", "-n", "-l", "-u", "-m", "-q"]
    prompt = "--> "
    # Show prompt and validate response
    command = getValidResponse(validCommands, prompt)
    
    return command


def test():
    """
    The core function of the program. Tests your knowledge of the trivia entered into the deck via a flashcards.
    """
    # get keys and randomize
    keys = list(ActiveDict.keys())
    random.shuffle(keys)

    # instructions
    print("Press Enter to flip cards and move to next card. Enter '-q' at any time to return to the menu.")
    print("====================")  # top division
    
    # for each key
    for key in keys:
        print(key)
        flip = input("-----")  # front and back division
        if flip == "-q":
            break
        print(ActiveDict[key])
        next = input("====================")  # bottom division
        if next == "-q":
            break

    print("End of Test")

    processCommand()


def addCard():
    """
    Adds a card to the current deck using prompts.
    """
    global ActiveDict

    # Prompt for front of card text
    key = input("Enter front text: ")
    # Prompt for back of card text
    value = input("Enter back text: ")

    # input values to activeDict
    ActiveDict[key] = value
    print(key, "added to deck")

    processCommand()


def deleteCard():
    """
    Deletes a card based on the key
    key is a string
    """
    global ActiveDict

    # get card
    key = input("Enter front text of card to be deleted or '-c' to empty deck:\n... ")

    # clear all
    if key == "-c":
        ActiveDict.clear()
        print("All cards deleted.")
    # delete single card
    elif key in ActiveDict.keys():
        del ActiveDict[key]
        print("Card", key, "deleted from", Deck)
    # card not found
    else:
        print("Card not found:", key)

    processCommand()


def printDeck():
    """
    Prints the full current deck.
    """
    num = 1
    for key, value in ActiveDict.items():
        print("Card", str(num) + ":")
        print("\tFront:", key)
        print("\tBack:", value)
        num += 1

    processCommand()


def saveDeck():
    """
    Uses a .txt file to store the current deck long term
    """
    global User
    global Deck
    global ActiveDict

    path = PATH + "Users\\" + User + "\\" + Deck + ".txt"
    deck = open(path, "w")

    # for each key in dict
    for key, value in ActiveDict.items():
        # write key to file
        deck.write(key + "\n")
        # write value to file
        deck.write(value + "\n")

    processCommand()


def loadDeck(deckName, username, new=False):
    """
    Loads an existing deck by default, creates a new deck if new == True.
    deckName is a string, the name of the deck.
    username is a string, the current user
    new is Boolean => load an existing deck or create a new one.
    """
    global Deck
    global User
    global ActiveDict
    global firstRun

    # Message to user
    print("Loading deck", Deck + "...")

    # Path can be same for new and existing decks. 
    path = PATH + "Users\\" + User + "\\" + Deck + ".txt"

    # New deck
    if new == True:
        try:
            # Open a new .txt file
            newDeck = open(path, "w+")
            # No reason to keep open, only creating file
            newDeck.close()
        except FileNotFoundError:
            print("File not found. Does user have directory in Users directory?")
            selectUser()
    
    # Existing deck
    else:
        # clear current dict
        ActiveDict.clear()
        try:
            # Open existing file
            oldDeck = open(path, "r")

            # Until end of file
            key = oldDeck.readline().strip()
            while key:
                # odd lines = key
                # even lines = value
                value = oldDeck.readline().strip()
                # load key, value into activeDict
                ActiveDict[key] = value

                # next key
                key = oldDeck.readline().strip()
                
        except FileNotFoundError:
            response = input("File not found. Try again or type -q to exit: ")
            if response != "-q":
                loadDeck(response, User)

    print("Ready")

    if not firstRun:
        processCommand()
    else: # is first run
        firstRun = False


def getValidResponse(validResponses, prompt):
    """
    Ensures a valid response string is obtained from a given prompt.
    validResponses is a list of valid response strings.
    prompt is a string for the input function.
    """
    while True:
        response = input(prompt)
        if (response in validResponses):
            break
        else:
            print("Invalid response", response)
    
    return response


if __name__ == "__main__":
    main()
