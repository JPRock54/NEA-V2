# Imports
from SQL import SQL
from hashlib import sha512
from random import choice
from string import ascii_letters, digits, punctuation
from datetime import datetime, timedelta

# Creates the db object based on the SQL class
db = SQL()

# Generates a set of random characters of a set size
def generateRandomString(size, specialCharacters=True):
    # Defines the characters list, with or without special characters
    characters = ascii_letters + digits
    if specialCharacters:
        characters += punctuation
    
    # Appends characters to the randomString list for the set size
    randomString = []
    for i in range(0, size):
        randomString.append(choice(characters))
    
    return ''.join(randomString)

# Hashes the password and the salt in sha512 format, then rehashes it a set number of times
def passwordHashing(password, iterations=1, salt=""):
    # Hashes the password and salt
    hash1 = sha512()
    hash1.update((password+salt).encode('utf-8'))
    
    # Returns the hashed value when all iterations are completed
    if iterations == 0:
        return hash1.hexdigest()
    
    # Rehashed it until the iterations have been complete
    return passwordHashing(hash1.hexdigest(), iterations-1)
    

# Returns true if the session is valid, 0 if otherwise
def checkSession(sessionID):
    # Checks if the session exists
    session = db.getData("SELECT sessionID, endDate FROM sessions WHERE sessionID = %s", (sessionID,))
    if session == [] or session is None:
        return False
    
    # Checks if the session has expired
    sessionID = session[0][0]
    endDate = session[0][1]
    if datetime.now() > endDate:
        db.manipulateData("DELETE FROM sessions WHERE sessionID = %s", (sessionID,))
        return False
    
    return True
    
# Returns True if the username exists, False if otherwise
def checkUsername(username):
    # Gets the username from the database and checks if its empty
    dbUsername = db.getData("SELECT * FROM users WHERE username = %s", (username, ))
    if dbUsername == []:
        return False
    
    return True

# Returns True if the password is correct, False if otherwise
def checkPassword(username, password):
    # Checks if the username exists
    if not checkUsername(username):
        return False

    # Compares the hashedPassword against the one in the database, returns False if they are not the same
    salt = db.getData("SELECT salt FROM users WHERE username = %s", (username,))[0][0]
    hashePassword = passwordHashing(password, 20, salt)
    if hashePassword != db.getData("SELECT hashedPassword FROM users WHERE username = %s", (username,))[0][0]:
        return False
    
    return True
    

# Returns the role of the user
def checkRole(username):
    # Get the role from the database
    role = db.getData("SELECT roleName FROM roles WHERE roleID = (SELECT roleID FROM users WHERE username = %s)", (username,))[0][0]
    return role