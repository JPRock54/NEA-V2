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
def generateSalt(size):
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
def checkAdmin():
    pass

# Check that a field exists in a database
def checkFieldExists():
    pass

# Checks if the user of a specific username exists
def checkUserExists():
    pass

# Creates an account with a username and a hashed password
@app.route("/createaccount", methods=["POST"])
def createaccount():
    username = request.json.get("username")

    if checkUsername(username):
        return jsonify({"message":"username already exists"})

    password = request.json.get("password")
    salt1 = generateSalt(32)
    hashedPassword = passwordHashing(password, salt1)
    db.manipulateData("INSERT INTO users (username, hashedPassword, salt) VALUES (%s, %s, %s)", (username, hashedPassword, salt1,))
    return jsonify({"message":"success"})

# Checks the username and password against values in database and gives a session id if succesfull
@app.route("/generatesession", methods=["POST"])
def generatesession():
    username = request.json.get("username")
    password = request.json.get("password")

    return jsonify({"message":db.getData("SELECT salt FROM users WHERE username=(%s)", (username,))})


# Updates the password within the database
@app.route("/updatepassword", methods=["POST"])
def updatepassword():
    pass

# Allows an admin to assign another user as an admin
@app.route("/admin/assignadmin", methods=["POST"])
def assignadmin():
    pass

# Main function to run the program
def main():
    print(passwordHashing("sdfsdfsdf", "sdfsdf"))
    app.run(debug=True)


if __name__ == "__main__":
    main()