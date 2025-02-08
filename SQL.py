from mysql.connector import Error, pooling
from os import getenv
from dotenv import load_dotenv

# SQL Class
class SQL:
    # Initatlises the database connection and creats the database if it doesn't exist
    def __init__(self):
        try:
            load_dotenv()
            self.pool = pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=32,  
                host=getenv("DB_HOST"),
                user=getenv("DB_USER"),
                password=getenv("DB_PASSWORD"),
                database=getenv("DB_NAME")
            )
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {getenv('DB_NAME')}")
            connection.database = getenv("DB_NAME")
            cursor.close()
            connection.close() 

        except Error as e:
            print(f"Error initializing connection pool: {e}")
    
    def create(self, statement : str):
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(statement)
            connection.commit()
            cursor.close()
            connection.close()
        except Error:
            pass

    def getData(self, statement : str, values : tuple|list = [], returnColumnNames = False):
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(statement, values)
            rows = cursor.fetchall()
            
            if returnColumnNames:
                columnNames = [desc[0] for desc in cursor.description]
                result = []
                for row in rows:
                    result.append(dict(zip(columnNames, row))) 
                cursor.close()
                connection.close()
                return result
            
            cursor.close()
            connection.close()
            return rows
        except Error:
            return None

    def manipulateData(self, statement : str, values : tuple|list = []):
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute(statement, values)
            connection.commit()
            cursor.close()
            connection.close()
        except Error:
            pass
    
    def getTables(self):
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            cursor.close()
            connection.close()
            return tables
        except:
            pass