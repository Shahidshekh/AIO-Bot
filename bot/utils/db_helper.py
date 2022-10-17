
from motor.motor_asyncio import AsyncIOMotorClient
from bot.modules.logger import LOGGER


class Database:
    def __init__(self):
        self.err=False

    def connect(self):
        try:
            client = AsyncIOMotorClient("mongodb+srv://minato:minato5647@cluster0.mukmldp.mongodb.net/?retryWrites=true&w=majority")
            LOGGER.info("Connected!")
            db = client["aio_bot_users"]
            collection = db['users']
            return collection
        except Exception as e:
            LOGGER.error(e)

    async def add_user(self, user_id, coll):
        LOGGER.info("here")
        res = await coll.find_one({"_id": user_id})
        if not res:
            await coll.insert_one({"_id": user_id})
            LOGGER.info("Added!")
        else:
            LOGGER.info("Exist!")