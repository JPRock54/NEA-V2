# Imports
from flask import Flask, request, jsonify
from hashlib import sha512
from random import choice
from string import ascii_letters, digits, punctuation
from datetime import date, datetime, timedelta
from SQL import SQL

# Creates 
app = Flask(__name__)
db = SQL()

# Generates a set of random characters of a set size
def generateRandomString(size):
    characters = ascii_letters + digits + punctuation
    salt = []
    for i in range(0, size):
        salt.append(choice(characters))
    return ''.join(salt)

# Hashes the password and the salt in sha512 format
def passwordHashing(password, salt):
    hash1 = sha512()
    hash1.update((password+salt).encode('utf-8'))
    return hash1.hexdigest()

# Checks is the session is valid
def verifySession():
    pass

# Returns 1 if the username exists, 0 if otherwise
def checkUsername(username):
    username = db.getData("SELECT * FROM users WHERE username = %s", (username, ))
    if username == []:
        return 0
    return 1

# Returns 1 if the user is an admin, 0 if otherwise
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
        return jsonify({"message":"username already exists"})

    password = request.json.get("password")
    salt1 = generateRandomString(32)
    hashedPassword = passwordHashing(password, salt1)
    db.manipulateData("INSERT INTO users (username, hashedPassword, salt, roleID) VALUES (%s, %s, %s, %s)", (username, hashedPassword, salt1, 0,))
    return jsonify({"message":"success"})

# Checks the username and password against values in database and gives a session id if succesfull
@app.route("/generatesession", methods=["POST"])
def generatesession():
    username = request.json.get("username")
    if not checkUsername(username):
        return jsonify({"success":False, "message":"username does not exist"})
    
    password = request.json.get("password")
    salt = db.getData("SELECT salt FROM users WHERE username=(%s)", (username,))[0][0]
    hash1 = passwordHashing(password, salt)
    if hash1 != db.getData("SELECT hashedPassword FROM users where username=(%s)", (username, ))[0][0]:
        return jsonify({"success": False, "message":"incorrect password"})

    userID = db.getData("SELECT userID FROM users WHERE username = %s", (username,))[0][0]
    sessionID = generateRandomString(64)
    startDate = datetime.now()
    endDate = startDate + timedelta(days=1)
    db.manipulateData("INSERT INTO sessions (sessionID, userID, startDate, endDate) VALUES (%s, %s, %s, %s)", (sessionID, userID, startDate, endDate,))
    
    return jsonify({"success":True, "message":"success"})


# Updates the password within the database
@app.route("/updatepassword", methods=["POST"])
def updatepassword():
    username = request.json.get("username")
    role = checkRole(username)
    print(role)
    return jsonify({"message":role})

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
    print(passwordHashing("sdfsdfsdf", "sdfsdf"))
    app.run(debug=True)


if __name__ == "__main__":
    main()