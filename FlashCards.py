"""
A simple flash cards program for the terminal. This version removes the
option of different users and improves data storage, moving from txt file
storage to a local database via SQLite.
Author: Evan L. Douglass
Version 2.0
"""
import sqlite3

# Establish global database connection
con = sqlite3.connect("flashcards.db")
cur = con.cursor()

# global variables
deck = ""
deckID = None
prompt = "--> "

def main():
    # Welcome message
    print('Welcome to Terminal Flashcards!')

    # Set up tables
    initTables()

    # Init active deck, create new or quit
    print("Do you want to load an existing deck (-l) or start a new deck (-n)?",
          "\nType -pd to print available decks, -q to quit.")
    while True:
        choice = getValidResponse(("-l", "-n", "-pd", "-q"), prompt)
        if choice == "-l":
            deckName = input("Ender deck name: ")
            loadDeck(deckName)
            break
        elif choice == "-n":
            deckName = input("Enter new deck name: ")
            newDeck(deckName)
            break
        elif choice == "-pd":
            printDecks()
        elif choice == "-q":
            exit()
        else:
            print("Invalid command:", choice)

    # Display menu of commands and process responses
    displayMenu()
    processCommand()


def initTables():
    """Sets up tables needed for flashcards."""

    makeDecks = '''
        CREATE TABLE IF NOT EXISTS Decks (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
    '''
    makeCards = '''
        CREATE TABLE IF NOT EXISTS Cards (
            id INTEGER PRIMARY KEY,
            deckID INTEGER NOT NULL,
            front TEXT NOT NULL,
            back TEXT,
            FOREIGN KEY(deckID) REFERENCES Decks(id)
        );
    '''
    cur.execute(makeDecks)
    cur.execute(makeCards)
    con.commit()


def displayMenu():
    """Displays a menu with command options then processes user response."""

    print("Select a command below:")
    print("\t-t Test yourself")
    print("\t-a Add a card")
    print("\t-dc Delete a card")
    print("\t-dd Delete a deck")
    print("\t-pc Print all cards in deck")
    print("\t-pd Print available decks")
    print("\t-n Create a new deck")
    print("\t-l Load a saved deck")
    print("\t-m Display menu")
    print("\t-q Quit program")


def processCommand():
    """Directs given command to appropriate function. Assumes command is valid."""
    
    validResponses = ("-t", "-a", "-dc", "-dd", "-pc", "-pd", "-n", "-l", "-m", "-q")
    command = getValidResponse(validResponses, prompt)

    while command != "-q":
        if command == "-t":
            test()

        elif command == "-a":
            addCard()

        elif command == "-dc":
            deleteCard()

        elif command == "-dd":
            deleteDeck()

        elif command == "-pc":
            printCards()

        elif command == "-pd":
            printDecks()

        elif command == "-n":
            deckName = input("Enter new deck name: ")
            newDeck(deckName)

        elif command == "-l":
            deckName = input("Ender deck name: ")
            loadDeck(deckName)

        elif command == "-m":
            displayMenu()
        
        command = getValidResponse(validResponses, prompt)

    # Quit the program and close database connection
    con.close()


def getValidResponse(responses, prompt):
    """
    Ensures a valid response string is obtained from a given prompt.
    obj responses -- An iterable of valid responses
    str prompt -- A prompt to display before getting a response.
    Returns a string in responses.
    """
    while True:
        response = input(prompt).lower()
        if (response in responses):
            break
        else:
            print("Invalid response", response)
    
    return response


def test():
    """
    Tests user's knowledge of the trivia entered into the deck via a flashcards.
    """
    sqlShuffled = '''
        SELECT front, back FROM Cards
        WHERE deckID=?
        ORDER BY RANDOM();
    '''
    shuffled = cur.execute(sqlShuffled, (deckID,))

    # instructions
    print("Press Enter to flip cards and move to next card. Enter '-q' at any time to return to the menu.")
    print("====================")  # top division

    # for each key
    for front, back in shuffled:
        print(front)  # Card prompt
        flip = input("----- ")  # front and back division. Space is for -q readability.
        if flip == "-q":
            con.close()
            break
        print(back)  # Card answer if user does not quit
        next = input("==================== ")  # bottom division
        if next == "-q":
            con.close()
            break

    print("End of Test")


def addCard():
    """Adds a card to the current deck."""
    
    # Get front and back of card
    print("Enter the card prompt below:")
    front = input()
    print("Enter the answer below:")
    back = input()

    try:
        sqlInsert = '''
            INSERT INTO Cards(deckID, front, back)
            VALUES(?, ?, ?);
        '''
        cur.execute(sqlInsert, (deckID, front, back))
        con.commit()

        print(front, "added to", deck)
    except sqlite3.IntegrityError:
        print("No deck initialized, please load an existing deck or create a new one")


def deleteCard():
    """Deletes a card from the active deck."""

    print("Select a card to delete or press Enter to cancel:")
    card = input()
    if card != "":
        delete = 'DELETE FROM Cards WHERE deckID=? AND front=?'
        cur.execute(delete, (deckID, card))
        con.commit()
        print(card, "removed from", deck)


def deleteDeck():
    """Deletes a deck from the collection of decks."""

    global deck, deckID

    print("This will delete a deck and all cards in it. Continue? (y/n)")
    response = getValidResponse(("y", "n"), prompt)

    if response == "y":
        # First remove all cards in the deck, then remove the deck
        deckName = input("Choose the deck to delete: ")
        fromCards = '''
            DELETE FROM Cards WHERE deckID=(
                SELECT id FROM Decks
                WHERE name=?
            );
        '''
        fromDecks = 'DELETE FROM Decks WHERE name=?;'
        cur.execute(fromCards, (deckName,))
        cur.execute(fromDecks, (deckName,))
        con.commit()

        # If deleting the active deck, reset deck variable
        if deckName == deck:
            deck = ""
            deckID = None
    else:
        # Abandon delete
        pass


def printCards():
    """Prints the full current deck in order of creation"""

    sqlGetCards = '''
        SELECT front, back FROM Cards
        WHERE deckID=?;
    '''
    print("Cards in", deck + ": ")
    print()
    activeDeck = cur.execute(sqlGetCards, (deckID,))
    for front, back in activeDeck:
        print("Front:", front)
        print("Back:", back)
        print("====================")


def printDecks():
    """Prints the available decks."""
    print("Available decks:")
    for deck in cur.execute("SELECT name FROM Decks;"):
        print("\t" + deck[0])  # Results returned as a single element tuple


def newDeck(deckName):
    """
    Adds a new deck to the database and sets the active deck.
    str deckName -- The name of the new deck.
    """
    try:
        command = "INSERT INTO Decks(name) VALUES(?);"
        cur.execute(command, (deckName,))
        con.commit()
        loadDeck(deckName)

    except sqlite3.IntegrityError:
        print("The", deckName, "deck already exists.")


def loadDeck(deckName):
    """
    Loads a deck as the active deck.
    str deckName -- the name of an existing deck.
    """
    global deck, deckID
    sqlGetIDAndDeck = '''
        SELECT id, name FROM Decks
        WHERE name=?;
    '''
    try:
        deckID, deck = cur.execute(sqlGetIDAndDeck, (deckName,)).fetchone()
    except TypeError:
        print(deckName, "deck not found.")


if __name__ == "__main__":
    main()
