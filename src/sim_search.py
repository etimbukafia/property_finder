from sentence_transformers import SentenceTransformer
from db_connect import Database
from langchain.vectorstores import MongoDBAtlasVectorSearch
import asyncio
import logging

async def generate_embeddings():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    db_collection = await Database.connect()
    logging.error("Can't connect to database")

    vector_search = MongoDBAtlasVectorSearch.from_documents(
            collection = db_collection,
            embedding=model,
            index_name = "real_vector_index"
        )
    
    #Generate embeddings in atlas vector store
    async for doc in db_collection.find():
        if 'description' in doc:
            description = doc['description']
            embedding = model.encode(description).tolist()
        

        # Update the corresponding listing with the image ID
        db_collection.update_one(
            {'_id': doc['_id']},
            {'$set': {'embedding': embedding}}
        )
        logging.info(f"created embedding and updated collection of doc: {doc}")
    else:
            # Print a message if no listing is found for the zpid
        logging.error(f"No collection found for doc: {doc}. embedding not created.")

if __name__ == "__main__":
    asyncio.run(generate_embeddings())


