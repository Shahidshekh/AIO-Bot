
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
            return db
        except Exception as e:
            LOGGER.error(e)

    async def add_user(self, user_id, db):
        res = await db.find_one({"_id": user_id})
        LOGGER.info("here")
        if not res:
            await db.insert_one({"_id": user_id})
            LOGGER.info("Added!")
        else:
            LOGGER.info("Exist!")