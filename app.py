# Imports
from flask import Flask
from hashlib import sha512
from random import choice
from string import ascii_letters, digits, punctuation
from mysql import connector
from dotenv import load_dotenv
from os import getenv

# SQL Class
class SQL:
    def __init__(self):
        load_dotenv()
        self.connector = connector.connect(
            host=getenv("HOST"),
            user=getenv("USER"),
            password=getenv("PASSWORD"),
            database=getenv("DB")
            )
        self.cursor = self.connection.cursor()
    
    def close(self):
        if self.connector:
            self.connector.close()
    
    def insert(self, statement : str, values : tuple|list = []):
        self.cursor.execute(statement, values)
        data = self.cursor.fetchall()
        self.close()
        return data

    def manipulateData(self, statement : str, values : tuple|list = []):
        self.cursor.execute(statement, values)
        self.connection.commit()
        self.close()

# Creates 
app = Flask(__name__)

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

def verifySession():
    pass

def checkAdmin():
    pass

def checkFieldExists():
    pass

@app.route("/createaccount", methods=["POST"])
def createaccount():
    pass

@app.route("/generatesession", methods=["POST"])
def generatesession():
    pass

@app.route("/updatepassword", methods=["POST"])
def updatepassword():
    pass

@app.route("/admin/assignadmin", methods=["POST"])
def assignadmin():
    pass



# Main
def main():
    print(passwordHashing("sdfsdfsdf", "sdfsdf"))
    app.run(debug=True)

# Run program
if __name__ == "__main__":
    main()