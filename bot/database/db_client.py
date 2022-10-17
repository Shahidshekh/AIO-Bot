from motor.motor_asyncio import AsyncIOMotorClient
from bot.modules.logger import LOGGER

mongodb = AsyncIOMotorClient("mongodb+srv://minato:minato5647@cluster0.mukmldp.mongodb.net/?retryWrites=true&w=majority")
db = mongodb['aio_bot']
user = db['users']

async def add_user(user_id):
    res = await user.find_one({"_id": user_id})
    LOGGER.info("exist")
    if not res:
        await user.insert_one({"_id": user_id})
        LOGGER.info("Added!")