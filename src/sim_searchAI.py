from dotenv import load_dotenv
from db_connect import Database
import logging
load_dotenv()
from typing import List
#from mistralai.client import MistralClient
from sentence_transformers import SentenceTransformer, util
from config import Configs
import torch

# Define the loggers
app_logger = logging.getLogger('app_logger')
debug_logger = logging.getLogger('debug_logger')

configs = Configs()

async def similiarity_search(query: str, fields: List[str] = ["city", "streetAddress", "latestPrice"]) -> List[dict]:
    """
    Perform a similarity search on the real estate listings based on the provided query.
    
    Args:
        query (str): The search query describing desired property features.
        fields (List[str], optional): List of fields to be included in the result. Defaults to ["city", "streetAddress", "latestPrice"].
    
    Returns:
        List[dict]: A list of dictionaries representing the top similar documents."""
    
    # Connect to the database
    collection = await Database.connect()
    # Check if the database connection was successful
    if collection is None:
        logging.error("Can't connect to database")
        return []
    # Retrieve all documents and their embeddings
    await configs.initialize()
    model = configs.get_embeddings_model()

    #Encode the query into an embedding vector
    query_embedding = model.encode(query).tolist()
    app_logger.info("query embedded")

    
    try:
        """ docs_with_embeddings = [] Initialize a list to hold documents with their embeddings. 
        As the code iterates over documents retrieved from the database, it appends each document that contains an embedding to this list."""
        docs_with_embeddings = []

        # Create a projection dictionary to specify which fields to retrieve
        # Ensure that the 'embedding' field is included for similarity comparison
        projection = {field: 1 for field in fields} #for field in fields iterates over each item in the fields list. {field: 1} creates a key-value pair where the key is the current item from fields, and the value is 1
        projection['embedding'] = 1  # Ensure embedding field is included for similarity comparison

        # Retrieve all documents that have an 'embedding' field
        async for doc in collection.find({"embedding": {"$exists": True}}, projection):
            docs_with_embeddings.append(doc)
        
        # Check if any documents with embeddings were found
        if not docs_with_embeddings:
            app_logger.warning("No documents with embeddings found")
            return []

        # Extract the embeddings from the retrieved documents
        doc_embeddings = [doc['embedding'] for doc in docs_with_embeddings]

        similarities = util.cos_sim(query_embedding, doc_embeddings).tolist()[0]

        # Retrieve top-k documents based on relevance scores
        sorted_docs = sorted(zip(docs_with_embeddings, similarities), key=lambda x: x[1], reverse=True)

        top_n = 5
        #iterates over each of these top top_n tuples and extracts only the doc (document) part from each tuple.
        similar_docs = [doc for doc, sim in sorted_docs[:top_n]] 

        return similar_docs
    
    except Exception as e:
        app_logger.error(f"Error while finding similar listings: {e}")
        return []