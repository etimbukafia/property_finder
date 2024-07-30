from motor.motor_asyncio import AsyncIOMotorClient
import os
from gridfs import GridFS
from pymongo import MongoClient
import logging

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
            password = os.environ.get('PASSWORD')
            username = os.environ.get('USERNAME')
            try:
                uri = f"mongodb+srv://ghostbandit02:dontlogmein@realestatecluster.kypuqxb.mongodb.net/?retryWrites=true&w=majority&appName=realEstateCluster"
                print(f"Connecting to MongoDB with URI: {uri}")
                db_name = "listings"
                collection_name = "austin_reduced"
                cls._client = AsyncIOMotorClient(uri)
                cls._db = cls._client[db_name]
                cls._collection = cls._db[collection_name]
                cls._fs = GridFS(MongoClient(uri)['listings'])
                logger.info("Connected to MongoDB")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise ConnectionError(f"Failed to connect to MongoDB: {e}")
        return cls._collection
    
    @classmethod
    async def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            cls._collection = None
            logger.info("Disconnected from MongoDB")
    
