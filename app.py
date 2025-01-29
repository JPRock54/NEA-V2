# Imports
from flask import Flask, request, jsonify
from hashlib import sha512
from random import choice
from string import ascii_letters, digits, punctuation
from datetime import datetime, timedelta
from SQL import SQL

# Creates 
app = Flask(__name__)
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

# Hashes the password and the salt in sha512 format
def passwordHashing(password, salt):
    hash1 = sha512()
    hash1.update((password+salt).encode('utf-8'))
    return hash1.hexdigest()

# Checks is the session is valid
def verifySession(sessionID):
    session = db.getData("SELECT sessionID, endDate FROM sessions WHERE sessionID = %s", (sessionID,))
    if session == []:
        return False
    sessionID = session[0][0]
    endDate = session[0][1]
    if datetime.now() > endDate:
        db.manipulateData("DELETE FROM sessions WHERE sessionID = %s", (sessionID,))
        return False
    return True
    
# Returns 1 if the username exists, 0 if otherwise
def checkUsername(username):
    username = db.getData("SELECT * FROM users WHERE username = %s", (username, ))
    if username == []:
        return 0
    return 1

# Returns the role of the user
def checkRole(username):
    role = db.getData("SELECT roleName FROM roles WHERE roleID = (SELECT roleID FROM users WHERE username = %s)", (username,))
    return role

# Check that a field exists in a database
def checkFieldExists():
    pass

# Creates an account with a username and a hashed password
@app.route("/createaccount", methods=["POST"])
def createaccount():
    username = request.json.get("username")
    if checkUsername(username):
        return jsonify({"success":False, "message":"username already exists"})

    password = request.json.get("password")
    salt1 = generateRandomString(32)
    hashedPassword = passwordHashing(password, salt1)
    db.manipulateData("INSERT INTO users (username, hashedPassword, salt, roleID) VALUES (%s, %s, %s, %s)", (username, hashedPassword, salt1, 0,))
    return jsonify({"success":True, "message":"account created"})

# Checks the username and password against values in database and gives a session id if succesfull
@app.route("/generatesession", methods=["POST"])
def generatesession():
    username = request.json.get("username")
    if not checkUsername(username):
        return jsonify({"success":False, "message":"username does not exist"})
    
    db.manipulateData("DELETE FROM sessions WHERE userID = (SELECT userID FROM users WHERE username = %s)", (username,))

    password = request.json.get("password")
    salt = db.getData("SELECT salt FROM users WHERE username=(%s)", (username,))[0][0]
    hash1 = passwordHashing(password, salt)
    if hash1 != db.getData("SELECT hashedPassword FROM users where username=(%s)", (username, ))[0][0]:
        return jsonify({"success": False, "message":"incorrect password"})

    userID = db.getData("SELECT userID FROM users WHERE username = %s", (username,))[0][0]
    sessionID = generateRandomString(64, False)
    startDate = datetime.now()
    endDate = startDate + timedelta(days=1)
    db.manipulateData("INSERT INTO sessions (sessionID, userID, startDate, endDate) VALUES (%s, %s, %s, %s)", (sessionID, userID, startDate, endDate,))
    
    return jsonify({"success":True, "message":"success"})


# Updates the password within the database
@app.route("/updatepassword", methods=["POST"])
def updatepassword():
    """
    username = request.json.get("username")
    role = checkRole(username)
    print(role)
    return jsonify({"message":role})
    """
    session = request.json.get("sessionID")
    print(verifySession(session))
    

# Allows an admin to assign another user as an admin
@app.route("/admin/assignadmin", methods=["POST"])
def assignadmin(username):
    role = checkRole(username)
    if role != "Admin":
        return jsonify({"success":False, "message":"account is not an admin"})
    if not checkUsername(username):
        return jsonify({"success":False, "message":"username does not exist"})
    db.manipulateData("UPDATE users SET roleID = %s WHERE username = %s", (1, username,))
    return jsonify({"success":True, "message":"success"})

# Main function to run the program
def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()