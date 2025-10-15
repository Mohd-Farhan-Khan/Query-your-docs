from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.config import get_settings

settings = get_settings()

class MongoDB:
    client: AsyncIOMotorClient = None
    
mongodb = MongoDB()

async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(settings.mongodb_uri)
    
async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()

def get_database():
    return mongodb.client[settings.mongodb_db_name]