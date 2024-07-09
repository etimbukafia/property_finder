from motor.motor_asyncio import AsyncIOMotorClient
import os

class Database:
    _client = None
    _db = None
    _collection = None

    @classmethod
    async def connect(cls):
        if cls._client is None:
            password = os.environ.get('PASSWORD')
            username = os.environ.get('USERNAME')
            try:
                uri = f"mongodb+srv://{username}:{password}@realestatecluster.kypuqxb.mongodb.net/?retryWrites=true&w=majority&appName=realEstateCluster"
                db_name = "listings"
                collection_name = "austin_reduced"
                cls._client = AsyncIOMotorClient(uri)
                cls._db = cls._client[db_name]
                cls._collection = cls._db[collection_name]
            except Exception as e:
                raise ConnectionError(f"Failed to connect to MongoDB: {e}")
        return cls._collection
    
    @classmethod
    async def close(cls):
        if cls._client:
            cls._client.close()
    
