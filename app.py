# Imports
from flask import Flask, request, jsonify
from flask_cors import CORS
from hashlib import sha512
from random import choice
from string import ascii_letters, digits, punctuation
from datetime import datetime, timedelta
from SQL import SQL

# Creates the flask application 
app = Flask(__name__)
CORS(app, origins="http://localhost:5173", supports_credentials=True)

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

# Check that a field exists in a database
def checkFieldExists():
    pass

# Creates an account with a username and a hashed password
@app.route("/createaccount", methods=["POST"])
def createaccount():
    # Gets their username and check if it already exists in the database
    username = request.json.get("username")
    if len(username) == 0:
        return jsonify({"success":False, "message":"Username field must not be blank"})
    elif len(username) < 4:
        return jsonify({"success":False, "message":"Username must be atleast 4 characters long!"})
    if checkUsername(username):
        return jsonify({"success":False, "message":"Username already exists!"})

    # Gets their password, hashes it and adds it to the database
    password = request.json.get("password")
    if len(password) == 0:
        return jsonify({"success":False, "message":"Password field must not be blank"})
    elif len(password) < 8:
        return jsonify({"success":False, "message":"Password must be atleast 8 characters long!"})
    salt1 = generateRandomString(32)
    hashedPassword = passwordHashing(password, 20, salt1)
    db.manipulateData("INSERT INTO users (username, hashedPassword, salt, roleID) VALUES (%s, %s, %s, %s)", (username, hashedPassword, salt1, 0,))
    
    return jsonify({"success":True, "message":"Account Created!"})

# Checks the username and password against values in database and gives a session id if succesfull
@app.route("/generatesession", methods=["POST"])
def generatesession():
    # Checks their username exists
    username = request.json.get("username")
    if len(username) == 0:
        return jsonify({"success":False, "message":"Username field must not be blank"})
    if not checkUsername(username):
        return jsonify({"success":False, "message":"Incorrect username/password"})
    
    # Checks if their password is correct
    password = request.json.get("password")
    if len(password) == 0:
        return jsonify({"success":False, "message":"Password field must not be blank"})
    if not checkPassword(username, password):
        return jsonify({"success":False, "message":"Incorrect username/password"})

    # Deletes all current sessions 
    db.manipulateData("DELETE FROM sessions WHERE userID = (SELECT userID FROM users WHERE username = %s)", (username,))

    # Generates a new session 
    userID = db.getData("SELECT userID FROM users WHERE username = %s", (username,))[0][0]
    sessionID = generateRandomString(64, False)
    startDate = datetime.now()
    endDate = startDate + timedelta(days=1)
    db.manipulateData("INSERT INTO sessions (sessionID, userID, startDate, endDate) VALUES (%s, %s, %s, %s)", (sessionID, userID, startDate, endDate,))
    
    print(sessionID)
    return jsonify({"success":True, "session":f"{sessionID}"})

@app.route("/validatesession", methods=["POST"])
def validatesession():
    sessionID = request.json.get("sessionID")
    if not checkSession(sessionID):
        return jsonify({"success":False, "message":"invalid session"})
    return jsonify({"success":True})


@app.route("/getusername", methods=["POST"])
def getusername():
    session = request.json.get("sessionID")
    if not checkSession(session):
        return jsonify({"success":False, "message":"invalid session"})
    
    username = db.getData("SELECT username FROM users WHERE userID = (SELECT userID FROM sessions WHERE sessionID = %s)", (session,))[0][0]
    return jsonify({"success":True, "username":username})

@app.route("/getrole", methods=["POST"])
def getrole():
    session = request.json.get("sessionID")
    if not checkSession(session):
        return jsonify({"success":False, "message":"invalid session"})
    
    role = db.getData("SELECT roleName FROM roles WHERE roleID = (SELECT roleID FROM users WHERE userID = (SELECT userID FROM sessions WHERE sessionID = %s))", (session,))[0][0]
    return jsonify({"success":True, "role":role})

# Updates the password within the database
@app.route("/updatepassword", methods=["POST"])
def updatepassword():
    # Gets the current sessionID and checks it against the database
    session = request.json.get("sessionID")
    if not checkSession(session):
        return jsonify({"success":False, "message":"Invalid session"})
    
    # Finds the current username from the sessionID and checks if the user entered password matches their current password
    username = db.getData("SELECT username FROM users WHERE userID = (SELECT userID FROM sessions WHERE sessionID = %s)", (session,))[0][0]
    currentPassword = request.json.get("currentPassword")

    if not checkPassword(username, currentPassword):
        return jsonify({"success":False, "message":"Incorrect current password"})
    
    # Takes the new password from the user and updates it in the database
    newPassword = request.json.get("newPassword")
    if len(newPassword) == 0:
        return jsonify({"success":False, "message":"New password field must not be blank"})
    elif len(newPassword) < 8:
        return jsonify({"success":False, "message":"New password must be atleast 8 characters long!"})
    elif newPassword == currentPassword:
        return jsonify({"success":False, "message":"New password must be different!"})

    salt = db.getData("SELECT salt FROM users WHERE username = %s", (username,))[0][0]
    hashedNewPassword = passwordHashing(newPassword, 20, salt)
    db.manipulateData("UPDATE users SET hashedPassword = %s WHERE username = %s", (hashedNewPassword, username))
    

    userID = db.getData("SELECT userID FROM sessions WHERE sessionID = %s", (session,))[0][0]
    # Deletes all other sessions
    db.manipulateData("DELETE FROM sessions WHERE userID = %s", (userID,))


    # Generates a new session with their new password
    sessionID = generateRandomString(64, False)
    startDate = datetime.now()
    endDate = startDate + timedelta(days=1)
    db.manipulateData("INSERT INTO sessions (sessionID, userID, startDate, endDate) VALUES (%s, %s, %s, %s)", (sessionID, userID, startDate, endDate,))

    return jsonify({"success":True, "message":"Password changed", "session":sessionID})
    

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
        return jsonify({"success":False, "message":"account is not an admin"})
    
    # Checks if the username exists
    if not checkUsername(newAdminUsername):
        return jsonify({"success":False, "message":"username does not exist"})
    db.manipulateData("UPDATE users SET roleID = %s WHERE username = %s", (1, newAdminUsername,))
    
    return jsonify({"success":True, "message":"success"})


@app.route("/tables", methods=["GET"])
def getTables():
    tables = db.getTables()
    excluded_tables = ['sessions', 'users', 'roles']
    return jsonify([table[0] for table in tables if table[0] not in excluded_tables])

# Route to get data from a specific table
@app.route('/gettabledata', methods=['POST'])
def getTableData():
    data = request.get_json()
    sessionID = data.get('sessionID')  
    if not checkSession(sessionID):
        return jsonify({"success":False, "message":"invalid session"})

    tableName = data.get('tableName')  
    tables = db.getTables()
    excluded_tables = ['sessions', 'users', 'roles']
    tableNames = [table[0] for table in tables if table[0] not in excluded_tables]
    if tableName not in tableNames:
        print("RAPE")
        return jsonify("")
    
    query = db.getData(f"SELECT * FROM {tableName}", returnColumnNames=True)
    rowCount = db.getData(f"SELECT COUNT(*) FROM {tableName}")
    return jsonify({"data":query, "rowCount":rowCount})

@app.route('/updatetables', methods=['POST'])
def update_table_data():
    primaryKeyMapping = {
    "categories" : "categoryID",
    "classes" : "classID",
    "items" : "itemID",
    "roles" : "roleID",
    "suppliers" : "supplierID"
    }

    data = request.get_json()  
    session = data['sessionID']
    primaryKeyValue = data['primaryKey']
    column = data['column']
    newValue = data['value']
    tableName = data['tableName']
    primaryKey = primaryKeyMapping[tableName]

    if not checkSession(session):
        return jsonify({"success":False, "message":"invalid session"})
    
    tables = db.getTables()
    excluded_tables = ['sessions', 'users', 'roles']
    tableNames = [table[0] for table in tables if table[0] not in excluded_tables]
    if tableName not in tableNames:
        return jsonify({"success":False})

    requiredRoleID = db.getData(f"SELECT requiredRoleID FROM {tableName} WHERE {primaryKey} = %s", (primaryKeyValue,))[0][0]
    currentRoleID = db.getData("SELECT roleID FROM users WHERE userID = (SELECT userID FROM sessions WHERE sessionID = %s)", (session,))[0][0]

    if newValue == "":
        return jsonify({"success":False})

    if column == primaryKey:
        return jsonify({"success": False, "message":"Cannot change this field"})
    
    if column == "requiredRoleID" and currentRoleID != 1:
        return jsonify({"success": False, "message":"Cannot change this field"})

    if currentRoleID is not None and int(currentRoleID) < int(requiredRoleID):
        return jsonify({"success": False, "message":"Invalid permissions"})

    db.manipulateData(f"UPDATE {tableName} SET {column} = %s WHERE {primaryKey} = %s", (newValue, primaryKeyValue))
    return jsonify({"success": True, "message": "Tables updated successfully"}), 200
    
@app.route('/addrow', methods=['POST'])
def add_row():
    data = request.get_json()
    sessionID = data.get('sessionID')
    tableName = data.get('tableName')

    tables = db.getTables()
    excluded_tables = ['sessions', 'users', 'roles']
    tableNames = [table[0] for table in tables if table[0] not in excluded_tables]
    if tableName not in tableNames:
        return jsonify({"success":False})

    # Validate session here (you may have a function for this)
    if not checkSession(sessionID):
        return jsonify({"success": False, "message": "Invalid session"})


    db.manipulateData(f"INSERT INTO {tableName} (requiredRoleID) VALUES (0)")
    return jsonify({"success": True, "message": "success"})

@app.route('/deleterow', methods=['POST'])
def deleterow():
    primaryKeyMapping = {
    "categories" : "categoryID",
    "classes" : "classID",
    "items" : "itemID",
    "roles" : "roleID",
    "suppliers" : "supplierID"
    }

    data = request.get_json()
    sessionID = data.get('sessionID')
    tableName = data.get('tableName')
    primaryKeyValue = data.get('primaryKey')
    primaryKey = primaryKeyMapping[tableName]

    if not checkSession(sessionID):
        return jsonify({"success": False, "message": "Invalid session"})
    

    requiredRoleID = db.getData(f"SELECT requiredRoleID FROM {tableName} WHERE {primaryKey} = %s", (primaryKeyValue,))[0][0]
    currentRoleID = db.getData("SELECT roleID FROM users WHERE userID = (SELECT userID FROM sessions WHERE sessionID = %s)", (sessionID,))[0][0]

    if currentRoleID is not None and int(currentRoleID) < int(requiredRoleID):
        return jsonify({"success": False, "message":"Invalid permissions"})

    db.manipulateData(f"DELETE FROM {tableName} WHERE {primaryKey} = %s", (primaryKeyValue,))
    return jsonify({"success": True, "message": "success"})

    


# Main function to run the program
def main():
    app.run(debug=True)

# Runs the program
if __name__ == "__main__":
    main()
