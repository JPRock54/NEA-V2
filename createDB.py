# Imports
from mysql.connector.errors import ProgrammingError
from SQL import SQL

# Makes database connector based on SQL class
db = SQL()

def checkTableExists(tablename : str):
    try:
        table = db.getData(f"SELECT * FROM {tablename}")
    except ProgrammingError as e:
        if e.errno == 1146:
            return 0
    else:
        if table is None:
            return 0
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
    createTable("roles", "roleID INT PRIMARY KEY, roleName VARCHAR(255) NOT NULL")
    createTable("users", "userID INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) NOT NULL, hashedPassword VARCHAR(255) NOT NULL, salt VARCHAR(255) NOT NULL, roleID INT NOT NULL, FOREIGN KEY (roleID) REFERENCES roles(roleID)")
    createTable("sessions", "sessionID VARCHAR(255) PRIMARY KEY, userID INT NOT NULL, startDate DATETIME NOT NULL, endDate DATETIME NOT NULL, FOREIGN KEY (userID) REFERENCES users(userID)")
    createTable("classes", "classID INT PRIMARY KEY, classRoom INT NOT NULL, classSubject VARCHAR(255) NOT NULL, requiredRoleID INT NOT NULL, FOREIGN KEY (requiredRoleID) REFERENCES roles(roleID)")
    createTable("suppliers", "supplierID INT PRIMARY KEY, supplierName VARCHAR(255) NOT NULL, supplierEmail VARCHAR(255) NOT NULL, supplierPhone VARCHAR(255) NOT NULL, supplierAddress VARCHAR(255) NOT NULL, requiredRoleID INT NOT NULL, FOREIGN KEY (requiredRoleID) REFERENCES roles(roleID)")
    createTable("categories", "categoryID INT PRIMARY KEY, categoryName VARCHAR(255) NOT NULL, categoryDescription VARCHAR(255) NOT NULL, requiredRoleID INT NOT NULL, FOREIGN KEY (requiredRoleID) REFERENCES roles(roleID)")
    createTable("items", "itemID INT PRIMARY KEY, itemName VARCHAR(255) NOT NULL, categoryID INT NOT NULL, stockAmount INT NOT NULL, itemPrice FLOAT NOT NULL, classID INT NOT NULL, supplierID INT NOT NULL, requiredRoleID INT NOT NULL, FOREIGN KEY (categoryID) REFERENCES categories(categoryID), FOREIGN KEY (classID) REFERENCES classes(classID), FOREIGN KEY (supplierID) REFERENCES suppliers(supplierID), FOREIGN KEY (requiredRoleID) REFERENCES roles(roleID)")
    db.manipulateData("INSERT INTO roles (roleID, roleName) VALUES (%s, %s)", (0, "User"))
    db.manipulateData("INSERT INTO roles (roleID, roleName) VALUES (%s, %s)", (1, "Admin"))

# Run program
if __name__ == "__main__":
    main()
    exit(0)
