from sentence_transformers import SentenceTransformer
from db_connect import Database
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
import asyncio
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
import os
from config import Configs

configs = Configs()
def remove_embedding_field():
    # Replace these with your MongoDB connection details
    mongo_uri = os.environ.get("MONGO_URI")
    database_name = "listings"
    collection_name = "austin_reduced"

    # Create a MongoClient
    client = MongoClient(mongo_uri)

    # Access the database and collection
    db = client[database_name]
    collection = db[collection_name]

    # Use the $unset operator to remove the 'embedding' field from all documents
    result = collection.update_many(
        {},  # An empty query to match all documents
        {"$unset": {"embedding": ""}}  # Unset the 'embedding' field
    )

    print(f"Modified {result.modified_count} documents.")


async def generate_embeddings():
    await configs.initialize()
    db_collection = await Database.connect()
    model = configs.get_embeddings_model()
    #model = SentenceTransformer('all-MiniLM-L6-v2')
   

    if db_collection is None:
        logging.error("Can't connect to database")
        return
    
    #Generate embeddings in atlas vector store
    try:
        async for doc in db_collection.find():
            if 'description' in doc:
                description = doc['description']
                embedding = model.encode(description, normalize_embeddings=True).tolist()

                # Update the corresponding listing with the image ID
                await db_collection.update_one(
                    {'_id': doc['_id']},
                    {'$set': {'embedding': embedding}}
                )
                logging.info(f"created embedding and updated collection of doc: {doc}")
            else:
                 logging.warning(f"No description found for doc: {doc['_id']}")
    except Exception as e:
            # Print a message if no listing is found for the zpid
        logging.error(f"Error while generating embeddings: {e}")

if __name__ == "__main__":
    asyncio.run(generate_embeddings())