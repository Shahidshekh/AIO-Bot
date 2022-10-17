from motor.motor_asyncio import AsyncIOMotorClient

mongodb = AsyncIOMotorClient("mongodb+srv://minato:minato5647@cluster0.mukmldp.mongodb.net/?retryWrites=true&w=majority")
db = mongodb['aio_bot']
user = db['users']

async def add_user(user_id):
    res = await user.find_one({"_id": user_id})
    if not res:
        await user.insert_one({"_id": user_id})