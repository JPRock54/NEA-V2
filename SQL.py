from mysql import connector
from os import getenv
from dotenv import load_dotenv

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
    
    def create(self, statement : str):
        self.cursor.execute(statement)
        self.cursor.commit()
        self.close()

    def getData(self, statement : str, values : tuple|list = []):
        self.cursor.execute(statement, values)
        data = self.cursor.fetchall()
        self.close()
        return data

    def manipulateData(self, statement : str, values : tuple|list = []):
        self.cursor.execute(statement, values)
        self.connection.commit()
        self.close()