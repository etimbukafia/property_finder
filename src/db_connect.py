from motor.motor_asyncio import AsyncIOMotorClient
import os
from gridfs import GridFS
from pymongo import MongoClient
import logging
from dotenv import load_dotenv
load_dotenv()

#Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    _client = None
    _db = None
    _collection = None
    _fs = None

    @classmethod
    async def connect(cls):
        if cls._client is None:
            try:
                uri = os.environ.get("MONGO_URI")
                print("Connecting to MongoDB with URI")

                db_name = "listings"
                collection_name = "austin_reduced"

                cls._client = AsyncIOMotorClient(uri,  maxPoolSize=50)
                cls._db = cls._client[db_name]
                cls._collection = cls._db[collection_name]
                cls._fs = GridFS(MongoClient(uri)['listings'])
                logger.info("Connected to MongoDB")
            except ConnectionError as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise
        return cls._collection
    
    @classmethod
    async def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            cls._collection = None
            logger.info("Disconnected from MongoDB")
    
