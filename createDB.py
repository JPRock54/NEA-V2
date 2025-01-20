# Imports
from SQL import SQL

# Makes database connector based on SQL class
db = SQL()

# Creates a database if it doesn't exist
#def createDatabase(databaseName : str):
    #db.create(f"CREATE DATABASE IF NOT EXISTS {databaseName}")

# Creates a table if if doesn't exist
def createTable(tableName : str, fields : str):
    db.create(f"CREATE TABLE IF NOT EXISTS {tableName} ({fields})")

# Main function to run the program
def main():
    createTable("users", "userID INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) NOT NULL, hashedPassword VARCHAR(255) NOT NULL, salt VARCHAR(255) NOT NULL")

# Run program
if __name__ == "__main__":
    main()
