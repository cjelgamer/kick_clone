from mysql.connector import connect
from pymongo import MongoClient

class DatabaseConnector:
    def __init__(self):
        # Conexión MySQL
        self.mysql_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  
            'database': 'kick_db'
        }
        
        # Conexión MongoDB
        self.mongo_uri = 'mongodb://localhost:27017'
        self.mongo_db = 'kick_realtime_db'

    def get_mysql_connection(self):
        return connect(**self.mysql_config)

    def get_mongo_db(self):
        client = MongoClient(self.mongo_uri)
        return client[self.mongo_db]