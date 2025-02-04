from mysql import connector
from mysql.connector import Error
from os import getenv
from dotenv import load_dotenv

# SQL Class
class SQL:
    # Initatlises the database connection and creats the database if it doesn't exist
    def __init__(self):
        try:
            load_dotenv()
            self.connection = connector.connect(
                host=getenv("DB_HOST"),
                user=getenv("DB_USER"),
                password=getenv("DB_PASSWORD")
                )
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {getenv("DB_NAME")}")
            self.connection.database = getenv("DB_NAME")
            self.cursor.close()
        except Error:
            pass

    def close(self):
        try:
            self.cursor.close()
        except Exception as e:
            print(f"Error closing cursor: {e}")   

    def create(self, statement : str):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(statement)
            self.connection.commit()
            self.close()
        except Error:
            pass

    def getData(self, statement : str, values : tuple|list = []):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(statement, values)
            data = self.cursor.fetchall()
            self.close()
            return data
        except Error:
            return None

    def manipulateData(self, statement : str, values : tuple|list = []):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(statement, values)
            self.connection.commit()
            self.close()
        except Error:
            pass