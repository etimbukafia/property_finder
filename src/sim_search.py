from sentence_transformers import SentenceTransformer
from db_connect import Database
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
import asyncio
import logging

async def generate_embeddings():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    db_collection = await Database.connect()

    if db_collection is None:
        logging.error("Can't connect to database")
        return
    
    #Generate embeddings in atlas vector store
    try:
        async for doc in db_collection.find():
            if 'description' in doc:
                description = doc['description']
                embedding = model.encode(description).tolist()

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