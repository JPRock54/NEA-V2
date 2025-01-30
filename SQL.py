from mysql import connector
from os import getenv
from dotenv import load_dotenv

# SQL Class
class SQL:
    # Initatlises the database connection and creats the database if it doesn't exist
    def __init__(self):
        load_dotenv()
        self.connection = connector.connect(
            host=getenv("DB_HOST"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD")
            )
        self.cursor = self.connection.cursor()
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {getenv("DB")}")
        self.connection.database = getenv("DB_NAME")

    def close(self):
        self.cursor.close()
    
    def create(self, statement : str):
        self.cursor = self.connection.cursor()
        self.cursor.execute(statement)
        self.connection.commit()
        self.close()

    def getData(self, statement : str, values : tuple|list = []):
        self.cursor = self.connection.cursor()
        self.cursor.execute(statement, values)
        data = self.cursor.fetchall()
        self.close()
        return data

    def manipulateData(self, statement : str, values : tuple|list = []):
        self.cursor = self.connection.cursor()
        self.cursor.execute(statement, values)
        self.connection.commit()
        self.close()
