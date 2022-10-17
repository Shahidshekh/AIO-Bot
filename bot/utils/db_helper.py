from pymongo import MongoClient
from bot.modules.logger import LOGGER


class Database:
    def __init__(self):
        self.err=False
        self.coll = self.connect()

    def connect(self):
        try:
            client = MongoClient("mongodb+srv://minato:minato5647@cluster0.mukmldp.mongodb.net/?retryWrites=true&w=majority")
            db = client["aio_bot_users"]
            collection = db['users']
            return collection
        except Exception as e:
            LOGGER.error(e)