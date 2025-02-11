# Imports
from mysql.connector import Error, pooling
from os import getenv
from dotenv import load_dotenv

# SQL Class
class SQL:
    # Initatlises the database connection and creats the database if it doesn't exist
    def __init__(self):
        # Attempts to create a cursor pool 
        try:
            # Makes a cursor pool connecting to the database based on information in the .env file
            load_dotenv()
            self.pool = pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=32,  
                host=getenv("DB_HOST"),
                user=getenv("DB_USER"),
                password=getenv("DB_PASSWORD"),
                database=getenv("DB_NAME")
            )
            
            # Creates the database if it doesn't already exist
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {getenv('DB_NAME')}")
            connection.database = getenv("DB_NAME")
            
            # Closes the connection
            cursor.close()
            connection.close() 

        # Logs error 
        except Error as e:
            print(f"Error initializing connection pool: {e}")
    
    # Creates a table in the database
    def create(self, statement : str):
        # Attempts to create a table based on the statement
        try:
            # Established connection from connection pool and makes cursor
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(statement)
            
            # Commites changes to database
            connection.commit()
            
            # Closes the connection
            cursor.close()
            connection.close()
        
        # Passes if an error occures to prevent crashing
        except Error:
            pass
    
    # Gets the data from the database
    def getData(self, statement : str, values : tuple|list = [], returnColumnNames = False):
        # Tries to get the data from the database based on the statement
        try:
            # Established connection from connection pool and makes cursor
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(statement, values)

            # Gets all the rows from the cursor for the table/s
            rows = cursor.fetchall()
            
            # Gets column names if required
            if returnColumnNames:
                columnNames = [desc[0] for desc in cursor.description]
                result = []
                for row in rows:
                    result.append(dict(zip(columnNames, row))) 
                
                # Closes the connection and returns the data
                cursor.close()
                connection.close()
                return result
            
            # Closes the connection and returns the data
            cursor.close()
            connection.close()
            return rows
        
        # Passes if an error occures to prevent crashing
        except Error:
            return None

    # Manipulates data in the database
    def manipulateData(self, statement : str, values : tuple|list = []):
        # Tries to connect to the database and commit changes based on statement
        try:
            # Established connection from connection pool, makes cursor and executes the statement
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(statement, values)
           
            # Commites changes to database          
            connection.commit()
            
            # Closes the connection
            cursor.close()
            connection.close()
        
        # Passes if an error occures to prevent crashing
        except Error:
            pass
    
    # Gets all the tables from the database
    def getTables(self):
        # Tries to connect to database to get tables
        try:
            # Established connection from connection pool, makes cursor and executes the statement
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            
            # Gets all the tables from the cursor
            tables = cursor.fetchall()
            
            # Closes the connection and returns the tables
            cursor.close()
            connection.close()
            return tables
        
        # Passes if an error occures to prevent crashing
        except Error:
            pass