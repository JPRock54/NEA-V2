# Imports
from flask import Flask, request, jsonify
from hashlib import sha512
from random import choice
from string import ascii_letters, digits, punctuation
from datetime import datetime, timedelta
from SQL import SQL

# Creates the flask application 
app = Flask(__name__)

# Creates the db object based on the SQL class
db = SQL()

# Generates a set of random characters of a set size
def generateRandomString(size, specialCharacters=True):
    characters = ascii_letters + digits
    if specialCharacters:
        characters += punctuation
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
def verifySession(sessionID):
    # Checks if the session exists
    session = db.getData("SELECT sessionID, endDate FROM sessions WHERE sessionID = %s", (sessionID,))
    if session == []:
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
    username = db.getData("SELECT * FROM users WHERE username = %s", (username, ))
    if username == []:
        return False
    return True

# Returns True if the password is correct, False if otherwise
def checkPassword(username, password):
    if not checkUsername(username):
        return False

    salt = db.getData("SELECT salt FROM users WHERE username = %s", (username,))[0][0]
    hashed_password = passwordHashing(password, 20, salt)
    if hashed_password != db.getData("SELECT hashedPassword FROM users WHERE username = %s", (username,))[0][0]:
        return False
    
    return True
    

# Returns the role of the user
def checkRole(username):
    # Get the role from the database
    role = db.getData("SELECT roleName FROM roles WHERE roleID = (SELECT roleID FROM users WHERE username = %s)", (username,))[0][0]
    return role

# Check that a field exists in a database
def checkFieldExists():
    pass

# Creates an account with a username and a hashed password
@app.route("/createaccount", methods=["POST"])
def createaccount():
    # Gets their username and check if it already exists in the database
    username = request.json.get("username")
    if checkUsername(username):
        return jsonify({"success":False, "message":"username already exists"})

    # Gets their password, hashes it and adds it to the database
    password = request.json.get("password")
    salt1 = generateRandomString(32)
    hashedPassword = passwordHashing(password, 20, salt1)
    print(passwordHashing(password, 20, salt1))
    db.manipulateData("INSERT INTO users (username, hashedPassword, salt, roleID) VALUES (%s, %s, %s, %s)", (username, hashedPassword, salt1, 0,))
    
    return jsonify({"success":True, "message":"account created"})

# Checks the username and password against values in database and gives a session id if succesfull
@app.route("/generatesession", methods=["POST"])
def generatesession():
    # Checks their username exists
    username = request.json.get("username")
    if not checkUsername(username):
        return jsonify({"success":False, "message":"username does not exist"})
    
    # Checks if their password is correct
    password = request.json.get("password")
    if not checkPassword(username, password):
        return jsonify({"success":False, "message":"incorrect password"})

    # Deletes all current sessions 
    db.manipulateData("DELETE FROM sessions WHERE userID = (SELECT userID FROM users WHERE username = %s)", (username,))

    # Generates a new session 
    userID = db.getData("SELECT userID FROM users WHERE username = %s", (username,))[0][0]
    sessionID = generateRandomString(64, False)
    startDate = datetime.now()
    endDate = startDate + timedelta(days=1)
    db.manipulateData("INSERT INTO sessions (sessionID, userID, startDate, endDate) VALUES (%s, %s, %s, %s)", (sessionID, userID, startDate, endDate,))
    
    return jsonify({"success":True, "message":"success"})


# Updates the password within the database
@app.route("/updatepassword", methods=["POST"])
def updatepassword():
    # Gets the current sessionID and checks it against the database
    session = request.json.get("sessionID")
    if not verifySession(session):
        return jsonify({"success":False, "message":"invalid session"})
    
    # Finds the current username from the sessionID and checks if the user entered password matches their current password
    username = db.getData("SELECT username FROM users WHERE userID = (SELECT userID FROM sessions WHERE sessionID = %s)", (session,))[0][0]
    currentPassword = request.json.get("currentPassword")
    if not checkPassword(username, currentPassword):
        return jsonify({"success":False, "message":"incorrect current password"})
    
    # Takes the new password from the user and updates it in the database
    newPassword = request.json.get("newPassword")
    salt = db.getData("SELECT salt FROM users WHERE username = %s", (username,))[0][0]
    hashedNewPassword = passwordHashing(newPassword, 20, salt)
    db.manipulateData("UPDATE users SET hashedPassword = %s WHERE username = %s", (hashedNewPassword, username))
    
    return jsonify({"success":True, "message":"password changed"})
    

# Allows an admin to assign another user as an admin
@app.route("/admin/assignadmin", methods=["POST"])
def assignadmin():
    # Gets the users username based on their current sessionID
    session = request.json.get("sessionID")
    adminUsername = db.getData("SELECT username FROM users WHERE userID = (SELECT userID FROM sessions WHERE sessionID = %s)", (session,))[0][0]
    newAdminUsername = request.json.get("username")


    # Checks if the current users role is an admin
    role = checkRole(adminUsername)
    if role != "Admin":
        print(role)
        return jsonify({"success":False, "message":"account is not an admin"})
    
    # Checks if the username exists
    if not checkUsername(newAdminUsername):
        return jsonify({"success":False, "message":"username does not exist"})
    db.manipulateData("UPDATE users SET roleID = %s WHERE username = %s", (1, newAdminUsername,))
    
    return jsonify({"success":True, "message":"success"})

# Main function to run the program
def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()