from motor.motor_asyncio import AsyncIOMotorClient
from bot.modules.logger import LOGGER

mongodb = AsyncIOMotorClient(
    "mongodb+srv://minato:minato0987@cluster2.6w89fyn.mongodb.net/?retryWrites=true&w=majority")
db = mongodb['aio_bot']
user = db['users']


async def add_user(user_id):
    res = check_user(user_id)
    if not res:
        await user.insert_one({"_id": user_id, "vid": False})


async def check_user(user_id):
    res = await user.find_one({"_id": user_id})
    return True if res else False


async def total_users():
    return await user.count_documents({})


async def users_list():
    return (user["user_id"] async for user in user_db.find({}))


async def up_mode(user_id, mode):
    res = await user.find_one({"_id": user_id})
    if res:
        await user.update_one({"_id": user_id}, {"$set": {"vid": mode}})
    else:
        await user.insert_one({"_id": user_id, "vid": mode})


async def get_up_mode(user_id):
    res = await user.find_one({"_id": user_id})
    if res:
        return res['vid']
    else:
        return False
