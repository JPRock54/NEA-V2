# Imports
from mysql.connector.errors import ProgrammingError
from SQL import SQL

# Makes database connector based on SQL class
db = SQL()

def checkTableExists(tablename : str):
    try:
        db.getData(f"SELECT * FROM {tablename}")
    except ProgrammingError as e:
        if e.errno == 1146:
            return 0
    else:
        return 1

# Creates a table if if doesn't exist
def createTable(tableName : str, fields : str):
    if checkTableExists(tableName):
        print(f"Table {tableName} already exists")
    else:
        db.create(f"CREATE TABLE IF NOT EXISTS {tableName} ({fields})")
        print(f"Succesfully created table {tableName}")
    

# Main function to run the program
def main():
    createTable("users", "userID INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) NOT NULL, hashedPassword VARCHAR(255) NOT NULL, salt VARCHAR(255) NOT NULL, roleID TINYINT(1) DEFAULT 0 NOT NULL")
    createTable("sessions", "sessionID INT AUTO_INCREMENT PRIMARY KEY, userID INT NOT NULL, startDate DATETIME NOT NULL, endDate DATETIME NOT NULL, FOREIGN KEY (userID) REFERENCES users(userID)")
    createTable("roles", "roleID INT PRIMARY KEY, roleName VARCHAR(255) NOT NULL, FOREIGN KEY (roleID) REFERENCES users(userID)")


# Run program
if __name__ == "__main__":
    main()
    exit(0)
